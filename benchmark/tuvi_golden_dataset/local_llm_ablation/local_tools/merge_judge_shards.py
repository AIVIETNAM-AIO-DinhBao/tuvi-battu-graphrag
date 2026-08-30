from __future__ import annotations

import csv
import json
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from .common import (
    JUDGE_SCHEMA_VERSION,
    atomic_write_json,
    canonical_json,
    iter_json_records,
    load_jsonl_map,
    resolve_directory,
    sha256_file,
    write_jsonl_atomic,
)
from .reporting import build_legacy_config_results, write_legacy_artifacts


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_extract_judge_zip(path: Path, destination: Path) -> Path:
    target = destination / path.stem
    target.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path) as archive:
        for member in archive.infolist():
            resolved = (target / member.filename).resolve()
            if target.resolve() not in resolved.parents and resolved != target.resolve():
                raise RuntimeError(f"Unsafe ZIP member in {path}: {member.filename}")
        archive.extractall(target)
    if not (target / "judge_shard_manifest.json").exists():
        raise RuntimeError(f"{path} does not contain judge_shard_manifest.json")
    return target


def discover_judge_shards(roots: Iterable[str | Path], extraction_dir: Path) -> list[Path]:
    found: list[Path] = []
    extraction_dir.mkdir(parents=True, exist_ok=True)
    for raw in roots:
        path = Path(raw)
        if not path.exists():
            continue
        if path.is_file() and path.suffix.lower() == ".zip":
            found.append(_safe_extract_judge_zip(path, extraction_dir))
        elif path.is_dir() and (path / "judge_shard_manifest.json").exists():
            found.append(path.resolve())
        elif path.is_dir():
            found.extend(marker.parent.resolve() for marker in path.rglob("judge_shard_manifest.json"))
            for archive in path.rglob("gemini_judge_shard_*.zip"):
                found.append(_safe_extract_judge_zip(archive, extraction_dir))
    return sorted(set(found))


def _validate_shard(root: Path) -> dict[str, Any]:
    manifest = json.loads((root / "judge_shard_manifest.json").read_text(encoding="utf-8"))
    for relative, expected in (manifest.get("files") or {}).items():
        path = root / relative
        if not path.exists():
            raise FileNotFoundError(f"Shard {root} is missing {relative}")
        if sha256_file(path) != expected:
            raise RuntimeError(f"Checksum mismatch in shard {root}: {relative}")
    if not manifest.get("is_complete"):
        raise RuntimeError(f"Judge shard is incomplete: {root}")
    return manifest


def merge_gemini_judge_shards(config: dict[str, Any]) -> dict[str, Any]:
    repo_root = Path(config["repo_root"]).expanduser().resolve()
    kit_root = Path(config.get("kit_root") or Path(__file__).resolve().parents[1]).resolve()
    bundle_dir = resolve_directory(config.get("bundle_dir"), marker="bundle_manifest.json")
    output_dir = Path(config.get("output_dir") or kit_root / "artifacts" / "gemini_judge_final").resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    selected_suites = {str(value) for value in config.get("suites") or []}
    expected_model_ids = {str(value) for value in config.get("expected_model_ids") or []}
    shard_roots = discover_judge_shards(
        config.get("judge_shard_roots") or [], output_dir / "_extracted_judge_shards"
    )
    if not shard_roots:
        raise FileNotFoundError("No judge_shard_manifest.json or gemini_judge_shard_*.zip found")
    shard_manifests = [_validate_shard(root) for root in shard_roots]
    judge_models = {str(row.get("judge_model") or "") for row in shard_manifests}
    if len(judge_models) != 1 or not next(iter(judge_models)):
        raise RuntimeError(f"Judge shards use inconsistent judge models: {sorted(judge_models)}")
    judge_model = next(iter(judge_models))

    cases = load_jsonl_map(bundle_dir / "cases.jsonl", "pair_id")
    configs = load_jsonl_map(bundle_dir / "configs.jsonl", "config_key")
    if selected_suites:
        cases = {key: row for key, row in cases.items() if str(row.get("suite")) in selected_suites}
    if not expected_model_ids:
        expected_model_ids = {
            str(model_id)
            for manifest in shard_manifests
            for model_id in manifest.get("expected_model_ids") or []
        }
    expected_keys = {f"{model_id}::{pair_id}" for model_id in expected_model_ids for pair_id in cases}

    merged: dict[str, dict[str, Any]] = {}
    source_reports: list[dict[str, Any]] = []
    for root in shard_roots:
        source_report_path = root / "evaluation_report.json"
        source_report = json.loads(source_report_path.read_text(encoding="utf-8"))
        source_reports.append(
            {
                "path": str(source_report_path),
                "manifest_name": source_report.get("manifest_name"),
                "output_dir": source_report.get("output_dir"),
                "config_count": source_report.get("config_count"),
                "execution_summary": source_report.get("execution_summary"),
                "status": source_report.get("status"),
            }
        )
        for row in iter_json_records(root / "judged_items.jsonl"):
            key = f"{row.get('model_id')}::{row.get('pair_id')}"
            previous = merged.get(key)
            if previous is not None and canonical_json(previous) != canonical_json(row):
                raise RuntimeError(f"Conflicting judged result for {key}")
            merged[key] = row

    missing = sorted(expected_keys - set(merged))
    unexpected = sorted(set(merged) - expected_keys)
    failed = [row for key, row in merged.items() if key in expected_keys and row.get("status") != "completed"]
    if missing or failed:
        raise RuntimeError(
            f"Cannot merge official report: missing={len(missing)}, failed={len(failed)}, "
            f"unexpected={len(unexpected)}"
        )
    completed_results = [merged[key] for key in sorted(expected_keys)]
    started_at = min(
        str(row.get("created_at") or row.get("started_at") or utc_now()) for row in shard_manifests
    )
    completed_at = utc_now()

    backend_dir = repo_root / "backend"
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))
    from app.rag.evaluation import (
        aggregate_evaluation_metrics,
        aggregate_grouped_metrics,
        metric_definitions,
        render_markdown_report,
    )

    legacy_configs = build_legacy_config_results(
        completed_results,
        configs,
        aggregate_evaluation_metrics=aggregate_evaluation_metrics,
        aggregate_grouped_metrics=aggregate_grouped_metrics,
        started_at=started_at,
        completed_at=completed_at,
    )
    if len(legacy_configs) != len(expected_model_ids) * len(configs):
        raise RuntimeError(
            f"Expected {len(expected_model_ids) * len(configs)} model-config rows, got {len(legacy_configs)}"
        )

    judged_path = output_dir / "judged_items.jsonl"
    write_jsonl_atomic(judged_path, completed_results)
    metrics_path = output_dir / "local_llm_metrics.csv"
    columns = [
        "generation_model",
        "model_revision",
        "quantization",
        "config_key",
        "base_config_name",
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
        for row in legacy_configs:
            metrics = row["metrics"]
            writer.writerow(
                {
                    **{key: row.get(key) for key in columns if key in row},
                    **{key: metrics.get(key) for key in columns if key in metrics},
                }
            )

    legacy_report = write_legacy_artifacts(
        output_dir=output_dir,
        repo_root=repo_root,
        kit_root=kit_root,
        bundle_dir=bundle_dir,
        legacy_configs=legacy_configs,
        judge_model=judge_model,
        manifest_name="local_llm_gemini_judge_final_2x3",
        started_at=started_at,
        completed_at=completed_at,
        expected_pair_count=len(expected_keys),
        failed_pair_count=0,
        executed_pair_count=0,
        resumed_pair_count=len(expected_keys),
        metric_definitions=metric_definitions("gemini"),
        render_markdown_report=render_markdown_report,
        notes=(
            "Merged three complete B/C/D judge shards. No Gemini API calls occur during merge; "
            "all per-item records were produced by the canonical repository evaluator."
        ),
        source_shard_reports=source_reports,
        merge_policy={
            "strategy": "model_config_shard_concatenation",
            "require_completed": True,
            "unique_key": "model_id + pair_id",
            "require_identical_judge_model": True,
            "require_complete_expected_matrix": True,
            "expected_models": sorted(expected_model_ids),
            "expected_config_count": len(configs),
        },
    )
    summary = {
        "schema_version": JUDGE_SCHEMA_VERSION,
        "artifact_type": "merged_gemini_judge_report",
        "judge_model": judge_model,
        "source_shard_count": len(shard_roots),
        "expected_pair_count": len(expected_keys),
        "completed_pair_count": len(completed_results),
        "failed_pair_count": 0,
        "config_result_count": len(legacy_configs),
        "is_complete": len(completed_results) == len(expected_keys),
        "key_rotation_by_shard": {
            str(row.get("shard_name")): row.get("key_rotation") for row in shard_manifests
        },
        "files": {
            "evaluation_report.json": sha256_file(output_dir / "evaluation_report.json"),
            "evaluation_report.md": sha256_file(output_dir / "evaluation_report.md"),
            "checkpoints/evaluation_checkpoint.json": sha256_file(
                output_dir / "checkpoints" / "evaluation_checkpoint.json"
            ),
            "checkpoints/checkpoint_summary.json": sha256_file(
                output_dir / "checkpoints" / "checkpoint_summary.json"
            ),
            "judged_items.jsonl": sha256_file(judged_path),
            "local_llm_metrics.csv": sha256_file(metrics_path),
        },
        "legacy_report_status": legacy_report["status"],
    }
    atomic_write_json(output_dir / "merge_summary.json", summary)
    return summary
