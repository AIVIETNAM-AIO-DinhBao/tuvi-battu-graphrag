from __future__ import annotations

import csv
import json
import os
import re
import sys
import time
import zipfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from .common import (
    JUDGE_SCHEMA_VERSION,
    append_jsonl,
    atomic_write_json,
    canonical_json,
    iter_json_records,
    load_jsonl_map,
    resolve_directory,
    sha256_file,
    sha256_text,
    stable_pair_id,
    write_jsonl_atomic,
)
from .reporting import build_legacy_config_results, write_legacy_artifacts


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def prediction_key(record: dict[str, Any]) -> str:
    model_id = str(record.get("model_id") or "")
    pair_id = str(record.get("pair_id") or "")
    if not model_id or not pair_id:
        raise ValueError("Every prediction must contain model_id and pair_id")
    return f"{model_id}::{pair_id}"


def discover_prediction_files(roots: Iterable[str | Path], extraction_dir: Path) -> list[Path]:
    files: list[Path] = []
    extraction_dir.mkdir(parents=True, exist_ok=True)
    for root in roots:
        path = Path(root)
        if not path.exists():
            continue
        if path.is_file() and path.name.startswith("predictions_shard_") and path.suffix == ".jsonl":
            files.append(path)
            continue
        if path.is_file() and path.suffix == ".zip":
            # Keep the extraction path short. The full experiment/archive names
            # can otherwise exceed the legacy Windows MAX_PATH limit.
            archive_tag = sha256_text(str(path.resolve()))[:12]
            target = extraction_dir / archive_tag
            target.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(path) as archive:
                for name in archive.namelist():
                    member = Path(name)
                    if not member.name.startswith("predictions_shard_") or member.suffix != ".jsonl":
                        continue
                    destination = target / member.name
                    with archive.open(name) as source, destination.open("wb") as sink:
                        sink.write(source.read())
                    files.append(destination)
            continue
        if path.is_dir():
            files.extend(path.rglob("predictions_shard_*.jsonl"))
            for archive_path in path.rglob("local_llm_predictions_*.zip"):
                files.extend(discover_prediction_files([archive_path], extraction_dir))
    return sorted(set(file.resolve() for file in files))


def merge_predictions(paths: Iterable[Path]) -> dict[str, dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for path in paths:
        for record in iter_json_records(path):
            key = prediction_key(record)
            previous = merged.get(key)
            if previous is not None and canonical_json(previous) != canonical_json(record):
                if previous.get("status") == "completed" and record.get("status") != "completed":
                    continue
                if record.get("status") == "completed" and previous.get("status") != "completed":
                    merged[key] = record
                    continue
                raise ValueError(f"Conflicting predictions for {key}")
            merged[key] = record
    return merged


def _latest_records(path: Path) -> dict[str, dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    if not path.exists():
        return latest
    for record in iter_json_records(path):
        evaluation_id = str(record.get("evaluation_id") or "")
        if evaluation_id:
            latest[evaluation_id] = record
    return latest


class RotatingGeminiJudge:
    """Round-robin starting keys per request, then fail over without exposing secrets."""

    backend = "gemini"

    def __init__(self, judge_factory: Any, api_keys: list[str], *, initial_offset: int = 0) -> None:
        if not api_keys:
            raise ValueError("RotatingGeminiJudge requires at least one API key")
        self._judges = [judge_factory(key) for key in api_keys]
        self._initial_offset = initial_offset % len(self._judges)
        self._request_count = 0
        self.usage_counts = {f"key_{index + 1}": 0 for index in range(len(self._judges))}
        self.success_counts = {f"key_{index + 1}": 0 for index in range(len(self._judges))}
        self.failure_counts = {f"key_{index + 1}": 0 for index in range(len(self._judges))}
        self.last_error_types: dict[str, str] = {}

    def evaluate(self, *, item: Any, state: dict[str, Any], config: Any) -> Any:
        start = (self._initial_offset + self._request_count) % len(self._judges)
        self._request_count += 1
        attempted_labels: list[str] = []
        for step in range(len(self._judges)):
            index = (start + step) % len(self._judges)
            label = f"key_{index + 1}"
            attempted_labels.append(label)
            self.usage_counts[label] += 1
            try:
                result = self._judges[index].evaluate(item=item, state=state, config=config)
                self.success_counts[label] += 1
                return result
            except Exception as exc:
                self.failure_counts[label] += 1
                self.last_error_types[label] = type(exc).__name__
        error_types = {label: self.last_error_types.get(label, "unknown") for label in attempted_labels}
        raise RuntimeError(f"All {len(self._judges)} Gemini keys failed; error_types={error_types}")

    def diagnostics(self) -> dict[str, Any]:
        return {
            "key_count": len(self._judges),
            "initial_offset": self._initial_offset,
            "request_count": self._request_count,
            "usage_counts": dict(self.usage_counts),
            "success_counts": dict(self.success_counts),
            "failure_counts": dict(self.failure_counts),
            "last_error_types": dict(self.last_error_types),
        }


def safe_slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "judge-shard"


def run_gemini_judge(config: dict[str, Any]) -> dict[str, Any]:
    bundle_dir = resolve_directory(config.get("bundle_dir"), marker="bundle_manifest.json")
    bundle_manifest = json.loads((bundle_dir / "bundle_manifest.json").read_text(encoding="utf-8"))
    repo_root = Path(config["repo_root"]).expanduser().resolve()
    output_dir = Path(config.get("output_dir") or "./local_llm_gemini_judge").resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    selected_suites = {str(value) for value in config.get("suites") or []}
    selected_config_keys = {str(value) for value in config.get("selected_config_keys") or []}
    expected_model_ids = {str(value) for value in config.get("expected_model_ids") or []}
    allow_incomplete = bool(config.get("allow_incomplete", False))
    retry_failed = bool(config.get("retry_failed", True))
    judge_model = str(config.get("judge_model") or "gemini-3.1-flash-lite-preview")
    retry_attempts = int(config.get("retry_attempts", 3))
    retry_base_seconds = float(config.get("retry_base_seconds", 2.0))
    initial_key_offset = int(config.get("initial_key_offset", 0))
    minimum_key_count = int(config.get("minimum_key_count", 1))
    shard_name = safe_slug(str(config.get("shard_name") or "judge-shard"))

    if not (repo_root / "backend" / "app").exists():
        raise FileNotFoundError(f"Invalid repo_root: {repo_root}")
    backend_dir = repo_root / "backend"
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))
    try:
        from dotenv import load_dotenv

        load_dotenv(repo_root / ".env", override=False)
    except Exception:
        pass

    prediction_roots = list(config.get("prediction_roots") or ["."])
    prediction_files = discover_prediction_files(prediction_roots, output_dir / "_extracted_predictions")
    if not prediction_files:
        raise FileNotFoundError(f"No predictions_shard_*.jsonl found under {prediction_roots}")
    predictions = merge_predictions(prediction_files)
    cases = load_jsonl_map(bundle_dir / "cases.jsonl", "pair_id")
    items = load_jsonl_map(bundle_dir / "items.jsonl", "id")
    configs = load_jsonl_map(bundle_dir / "configs.jsonl", "config_key")
    if selected_suites:
        cases = {key: case for key, case in cases.items() if str(case.get("suite")) in selected_suites}
    if selected_config_keys:
        unknown_configs = sorted(selected_config_keys - set(configs))
        if unknown_configs:
            raise ValueError(f"Unknown selected_config_keys: {unknown_configs}")
        cases = {
            key: case for key, case in cases.items() if str(case.get("config_key")) in selected_config_keys
        }
    if not expected_model_ids:
        expected_model_ids = {str(record["model_id"]) for record in predictions.values()}
    expected_keys = {f"{model_id}::{pair_id}" for model_id in expected_model_ids for pair_id in cases}
    completed_predictions = {
        key: record
        for key, record in predictions.items()
        if key in expected_keys and record.get("status") == "completed"
    }
    prompt_mismatches = sorted(
        key
        for key, prediction in completed_predictions.items()
        if str(prediction.get("prompt_sha256") or "")
        != str(cases[str(prediction["pair_id"])].get("prompt_sha256") or "")
    )
    if prompt_mismatches:
        raise RuntimeError(
            f"Prediction prompt checksum mismatch for {len(prompt_mismatches)} pair(s); "
            f"examples={prompt_mismatches[:3]}"
        )
    missing_keys = sorted(expected_keys - set(completed_predictions))
    unexpected_keys = sorted(set(predictions) - expected_keys)
    if missing_keys and not allow_incomplete:
        by_model = {
            model_id: sum(key.startswith(f"{model_id}::") for key in missing_keys)
            for model_id in sorted(expected_model_ids)
        }
        raise RuntimeError(
            f"Predictions incomplete: missing {len(missing_keys)} of {len(expected_keys)}; by model={by_model}. "
            "Do not start official judging until both models cover the same frozen cases."
        )

    from app.rag.ablation import AblationDatasetItem
    from app.rag.citations import map_citations
    from app.rag.config import ExperimentConfig
    from app.rag.evaluation import (
        GeminiEvaluationJudge,
        aggregate_evaluation_metrics,
        aggregate_grouped_metrics,
        metric_definitions,
        render_markdown_report,
        retrieval_latency_ms,
        summarize_evaluation_item,
    )
    from app.rag.gemini_keys import load_runtime_gemini_api_keys

    explicit_api_key = str(config.get("api_key") or "").strip()
    api_keys = [explicit_api_key] if explicit_api_key else load_runtime_gemini_api_keys()
    if len(api_keys) < minimum_key_count:
        raise RuntimeError(
            f"Found {len(api_keys)} Gemini key(s), but minimum_key_count={minimum_key_count}. "
            "Set GEMINI_API_KEYS (comma-separated), GEMINI_API_KEY, or numbered GEMINI_API_KEY_N variables."
        )
    judge = RotatingGeminiJudge(
        lambda key: GeminiEvaluationJudge(model=judge_model, api_key=key, temperature=0.0),
        api_keys,
        initial_offset=initial_key_offset,
    )
    judged_path = output_dir / "judged_items.jsonl"
    latest = _latest_records(judged_path)
    started_at = utc_now()
    executed_pair_count = 0
    resumed_pair_count = 0

    ordered_predictions = sorted(
        completed_predictions.values(), key=lambda row: (str(row["model_id"]), str(row["pair_id"]))
    )
    for index, prediction in enumerate(ordered_predictions, start=1):
        pair_id = str(prediction["pair_id"])
        model_id = str(prediction["model_id"])
        evaluation_id = stable_pair_id(
            pair_id,
            model_id,
            str(prediction["model_revision"]),
            str(prediction["quantization"]),
            judge_model,
        )
        previous = latest.get(evaluation_id)
        if previous and (previous.get("status") == "completed" or not retry_failed):
            resumed_pair_count += 1
            continue
        case = cases[pair_id]
        item_record = items[str(case["item_id"])]
        config_record = configs[str(case["config_key"])]
        item = AblationDatasetItem.from_payload(item_record, line_number=index)
        experiment_config = ExperimentConfig.model_validate(config_record["config"])
        state = dict(case.get("state") or {})
        state["answer"] = str(prediction.get("answer") or "")
        state["sources"], state["citation_metadata"] = map_citations(state, experiment_config)
        judge_started = time.perf_counter()
        try:
            judge_result = None
            last_exc: Exception | None = None
            attempt_errors: list[str] = []
            attempt_used = 0
            for attempt in range(1, retry_attempts + 1):
                attempt_used = attempt
                try:
                    judge_result = judge.evaluate(item=item, state=state, config=experiment_config)
                    break
                except Exception as exc:
                    last_exc = exc
                    attempt_errors.append(type(exc).__name__)
                    if attempt < retry_attempts:
                        time.sleep(retry_base_seconds * (2 ** (attempt - 1)))
            if judge_result is None:
                assert last_exc is not None
                raise last_exc
            judge_latency_ms = round((time.perf_counter() - judge_started) * 1000, 2)
            retrieval_ms = float(retrieval_latency_ms(state) or 0.0)
            generation_ms = float(prediction.get("generation_latency_ms") or 0.0)
            rag_latency_ms = round(retrieval_ms + generation_ms, 2)
            result = summarize_evaluation_item(
                item,
                state,
                judge_result,
                latency_ms=rag_latency_ms,
                judge_latency_ms=judge_latency_ms,
            )
            result.update(
                {
                    "schema_version": JUDGE_SCHEMA_VERSION,
                    "attempt_count": attempt_used,
                    "attempt_errors": attempt_errors,
                    "result_source": "executed",
                    "evaluation_id": evaluation_id,
                    "prediction_id": prediction.get("prediction_id"),
                    "pair_id": pair_id,
                    "suite": case["suite"],
                    "config_key": case["config_key"],
                    "prompt_sha256": case["prompt_sha256"],
                    "answer_sha256": sha256_text(str(prediction["answer"])),
                    "model_key": prediction.get("model_key"),
                    "model_id": model_id,
                    "model_revision": prediction["model_revision"],
                    "quantization": prediction["quantization"],
                    "input_tokens": prediction.get("input_tokens"),
                    "output_tokens": prediction.get("output_tokens"),
                    "generation_latency_ms": generation_ms,
                    "retrieval_context_build_latency_ms": retrieval_ms,
                    "rag_latency_ms": rag_latency_ms,
                    "latency_ms": rag_latency_ms,
                    "judge_latency_ms": judge_latency_ms,
                    "evaluation_total_latency_ms": round(rag_latency_ms + judge_latency_ms, 2),
                    "completed_at": utc_now(),
                }
            )
        except Exception as exc:
            result = {
                "schema_version": JUDGE_SCHEMA_VERSION,
                "status": "failed",
                "attempt_count": attempt_used,
                "attempt_errors": attempt_errors or [type(exc).__name__],
                "result_source": "executed",
                "evaluation_id": evaluation_id,
                "pair_id": pair_id,
                "suite": case["suite"],
                "config_key": case["config_key"],
                "item_id": case["item_id"],
                "model_id": model_id,
                "model_revision": prediction.get("model_revision"),
                "quantization": prediction.get("quantization"),
                "error_type": type(exc).__name__,
                "error": str(exc)[:2000],
                "failed_at": utc_now(),
            }
        append_jsonl(judged_path, result)
        executed_pair_count += 1
        latest[evaluation_id] = result
        if index % 10 == 0 or index == len(ordered_predictions):
            print(
                f"judged={index}/{len(ordered_predictions)} model={model_id} status={result['status']}",
                flush=True,
            )

    expected_evaluation_ids = {
        stable_pair_id(
            str(prediction["pair_id"]),
            str(prediction["model_id"]),
            str(prediction["model_revision"]),
            str(prediction["quantization"]),
            judge_model,
        )
        for prediction in ordered_predictions
    }
    compacted = [latest[key] for key in sorted(expected_evaluation_ids) if key in latest]
    write_jsonl_atomic(judged_path, compacted)
    completed_results = [record for record in compacted if record.get("status") == "completed"]
    failed_results = [record for record in compacted if record.get("status") == "failed"]

    by_model_config: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for record in completed_results:
        by_model_config[(str(record["model_id"]), str(record["config_key"]))].append(record)
    config_results: list[dict[str, Any]] = []
    for model_id, config_key in sorted(by_model_config):
        metadata = configs[config_key]
        rows = by_model_config[(model_id, config_key)]
        config_results.append(
            {
                "model_id": model_id,
                "model_revision": rows[0]["model_revision"],
                "quantization": rows[0]["quantization"],
                "config_key": config_key,
                "suite": metadata["suite"],
                "config_name": metadata["config_name"],
                "bundle_config_hash": metadata["bundle_config_hash"],
                "chunk_strategy_id": metadata["config"]["chunk_strategy_id"],
                "prompt_template_id": metadata["config"]["prompt_template_id"],
                "metrics": aggregate_evaluation_metrics(rows),
                "grouped_metrics": aggregate_grouped_metrics(rows),
            }
        )

    limitations = [
        "Gemini is an LLM judge and may have model-family bias; model identity is excluded from the judge prompt.",
        "Generation latency is comparable only when runtime settings and hardware/API conditions are held constant.",
    ]
    if bundle_manifest.get("bundle_type") == "model_only_question_plus_raw_chart":
        limitations.append(
            "This model-only bundle has no retrieved corpus context or citations; retrieval and citation metrics are not applicable."
        )
    else:
        limitations.append(
            "Exact chunk hit is unavailable because the release dataset contains no gold_chunk_ids."
        )
    if any(str(record.get("quantization")) == "4bit" for record in completed_predictions.values()):
        limitations.append("Qwen and Gemma use 4-bit quantized inference, not full precision.")

    report = {
        "schema_version": JUDGE_SCHEMA_VERSION,
        "started_at": started_at,
        "completed_at": utc_now(),
        "judge_backend": "gemini",
        "judge_model": judge_model,
        "shard_name": shard_name,
        "selected_suites": sorted(selected_suites),
        "selected_config_keys": sorted(selected_config_keys),
        "expected_model_ids": sorted(expected_model_ids),
        "bundle_type": bundle_manifest.get("bundle_type"),
        "retrieval_executed": bundle_manifest.get("retrieval_executed"),
        "evaluation_case_count": len(cases),
        "retrieval_pair_count": len(cases),
        "expected_prediction_count": len(expected_keys),
        "completed_prediction_count": len(completed_predictions),
        "missing_prediction_count": len(missing_keys),
        "unexpected_prediction_count": len(unexpected_keys),
        "judged_completed_count": len(completed_results),
        "judged_failed_count": len(failed_results),
        "is_complete": not missing_keys and not failed_results and len(completed_results) == len(expected_keys),
        "prediction_files": [str(path) for path in prediction_files],
        "key_rotation": judge.diagnostics(),
        "config_results": config_results,
        "limitations": limitations,
    }
    report_path = output_dir / "local_llm_evaluation_report.json"
    metrics_path = output_dir / "local_llm_metrics.csv"
    atomic_write_json(report_path, report)
    columns = [
        "model_id",
        "model_revision",
        "quantization",
        "suite",
        "config_key",
        "config_name",
        "chunk_strategy_id",
        "prompt_template_id",
        "item_count",
        "faithfulness_avg",
        "answer_relevancy_avg",
        "context_recall_avg",
        "citation_coverage_rate",
        "graph_hit_rate",
        "avg_gold_doc_coverage_rate",
        "avg_gold_page_hit_rate",
        "avg_gold_quote_overlap",
        "generation_p95_ms",
        "p95_latency_ms",
    ]
    with metrics_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in config_results:
            metrics = row["metrics"]
            writer.writerow(
                {
                    **{key: row.get(key) for key in columns if key in row},
                    **{key: metrics.get(key) for key in columns if key in metrics},
                }
            )
    report["judged_items_sha256"] = sha256_file(judged_path)
    report["metrics_csv_sha256"] = sha256_file(metrics_path)
    atomic_write_json(report_path, report)
    completed_at = str(report["completed_at"])
    legacy_configs = build_legacy_config_results(
        completed_results,
        configs,
        aggregate_evaluation_metrics=aggregate_evaluation_metrics,
        aggregate_grouped_metrics=aggregate_grouped_metrics,
        started_at=started_at,
        completed_at=completed_at,
    )
    legacy_report = write_legacy_artifacts(
        output_dir=output_dir,
        repo_root=repo_root,
        kit_root=Path(__file__).resolve().parents[1],
        bundle_dir=bundle_dir,
        legacy_configs=legacy_configs,
        judge_model=judge_model,
        manifest_name=f"local_llm_gemini_judge_{shard_name}",
        started_at=started_at,
        completed_at=completed_at,
        expected_pair_count=len(expected_keys),
        failed_pair_count=len(failed_results),
        executed_pair_count=executed_pair_count,
        resumed_pair_count=resumed_pair_count,
        metric_definitions=metric_definitions("gemini"),
        render_markdown_report=render_markdown_report,
        notes=(
            "Local-LLM generation answers judged with the canonical GeminiEvaluationJudge, "
            "build_gemini_judge_prompt, summarize_evaluation_item, and aggregate metric functions."
        ),
    )
    handoff_manifest = {
        "schema_version": JUDGE_SCHEMA_VERSION,
        "artifact_type": "gemini_judge_shard",
        "created_at": completed_at,
        "shard_name": shard_name,
        "judge_model": judge_model,
        "selected_config_keys": sorted(selected_config_keys),
        "expected_model_ids": sorted(expected_model_ids),
        "judged_completed_count": len(completed_results),
        "judged_failed_count": len(failed_results),
        "is_complete": report["is_complete"],
        "key_rotation": judge.diagnostics(),
        "files": {
            "judged_items.jsonl": sha256_file(judged_path),
            "local_llm_metrics.csv": sha256_file(metrics_path),
            "local_llm_evaluation_report.json": sha256_file(report_path),
            "evaluation_report.json": sha256_file(output_dir / "evaluation_report.json"),
            "evaluation_report.md": sha256_file(output_dir / "evaluation_report.md"),
            "checkpoints/evaluation_checkpoint.json": sha256_file(
                output_dir / "checkpoints" / "evaluation_checkpoint.json"
            ),
            "checkpoints/checkpoint_summary.json": sha256_file(
                output_dir / "checkpoints" / "checkpoint_summary.json"
            ),
        },
    }
    handoff_path = output_dir / "judge_shard_manifest.json"
    atomic_write_json(handoff_path, handoff_manifest)
    archive_path = output_dir.parent / f"gemini_judge_shard_{shard_name}.zip"
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in (
            judged_path,
            metrics_path,
            report_path,
            output_dir / "evaluation_report.json",
            output_dir / "evaluation_report.md",
            handoff_path,
        ):
            archive.write(path, arcname=path.name)
        archive.write(
            output_dir / "checkpoints" / "evaluation_checkpoint.json",
            arcname="checkpoints/evaluation_checkpoint.json",
        )
        archive.write(
            output_dir / "checkpoints" / "checkpoint_summary.json",
            arcname="checkpoints/checkpoint_summary.json",
        )
    report["archive_path"] = str(archive_path)
    report["legacy_report_status"] = legacy_report["status"]
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return report


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python -m local_tools.run_judge CONFIG.json")
    config = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    run_gemini_judge(config)


if __name__ == "__main__":
    main()
