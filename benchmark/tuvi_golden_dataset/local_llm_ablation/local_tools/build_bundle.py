from __future__ import annotations

import json
import os
import sys
import time
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .common import (
    BUNDLE_SCHEMA_VERSION,
    append_jsonl,
    assert_no_secret_keys,
    atomic_write_json,
    canonical_json,
    load_jsonl_map,
    sha256_file,
    sha256_text,
    stable_pair_id,
    write_jsonl_atomic,
)


STATE_KEYS = (
    "query",
    "rewritten_query",
    "normalized_query",
    "question_complexity",
    "question_family",
    "chart_id",
    "chart_data",
    "chart_facts",
    "entities",
    "query_entities",
    "context_chunks",
    "context_summary",
    "final_context",
    "retrieval_trace",
    "retrieval_plan",
    "retrieval_diagnostics",
    "retrieval_backend_unavailable",
    "retrieval_backend_error_type",
)
CANDIDATE_STAGES = (
    "graph_candidates",
    "dense_candidates",
    "sparse_candidates",
    "fused_candidates",
    "reranked_candidates",
    "graded_candidates",
    "ranked_candidates",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def item_payload(item: Any) -> dict[str, Any]:
    return {
        "id": item.id,
        "query": item.query,
        "chart_id": item.chart_id,
        "user_id": item.user_id,
        "chart_data": item.chart_data,
        "gold_answer": item.gold_answer,
        "expected_answer_summary": item.expected_answer_summary,
        "gold_context_spans": item.gold_context_spans,
        "labels": item.labels,
        "question_complexity": item.question_complexity,
        "birth_info": item.birth_info,
        "metadata": item.metadata,
    }


def compact_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    provenance = candidate.get("provenance") if isinstance(candidate.get("provenance"), dict) else {}
    return {
        "rank": candidate.get("rank"),
        "chunk_id": candidate.get("chunk_id"),
        "chunk_hash": candidate.get("chunk_hash"),
        "source_id": candidate.get("source_id") or provenance.get("source_id") or provenance.get("doc_id"),
        "source_page": candidate.get("source_page") or candidate.get("page_book") or candidate.get("page_pdf"),
        "retrieval_path": candidate.get("retrieval_path"),
        "retrieval_paths": candidate.get("retrieval_paths") or [],
        "score": candidate.get("score"),
        "fusion_score": candidate.get("fusion_score"),
        "rerank_score": candidate.get("rerank_score"),
        "grade_score": candidate.get("grade_score"),
    }


def snapshot_state(state: dict[str, Any], *, candidate_log_k: int) -> dict[str, Any]:
    snapshot = {key: state.get(key) for key in STATE_KEYS if key in state}
    snapshot["candidate_snapshots"] = {
        stage: [compact_candidate(candidate) for candidate in (state.get(stage) or [])[:candidate_log_k]]
        for stage in CANDIDATE_STAGES
    }
    return snapshot


def build_context_bundle(config: dict[str, Any]) -> dict[str, Any]:
    """Run retrieval/context assembly once and export model-agnostic prompts."""
    repo_root = Path(config["repo_root"]).expanduser().resolve()
    kit_root = Path(config.get("kit_root") or Path(__file__).resolve().parents[1]).resolve()
    plan_path = Path(config.get("plan_path") or kit_root / "experiment_plan.json").resolve()
    output_dir = Path(config.get("output_dir") or kit_root / "artifacts" / "context_bundle").resolve()
    selected_suites = list(config.get("suites") or [])
    item_limit = config.get("item_limit")
    candidate_log_k = int(config.get("candidate_log_k") or 100)
    retry_failed = bool(config.get("retry_failed", True))

    if not (repo_root / "backend" / "app").exists():
        raise FileNotFoundError(f"Invalid repo_root: {repo_root}")
    if not plan_path.exists():
        raise FileNotFoundError(plan_path)

    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    if not selected_suites:
        selected_suites = list(plan["default_suites"])
    unknown = sorted(set(selected_suites) - set(plan["suites"]))
    if unknown:
        raise ValueError(f"Unknown suites: {unknown}")

    try:
        from dotenv import load_dotenv

        load_dotenv(repo_root / ".env", override=False)
    except Exception:
        pass
    os.chdir(repo_root)
    backend_dir = repo_root / "backend"
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))

    from app.rag.ablation import load_ablation_dataset, load_ablation_manifest
    from app.rag.config import ExperimentConfig, config_hash
    from app.rag.generation import GenerationResult
    from app.rag.graph import run_rag_dry_run

    class CaptureGenerationClient:
        def __init__(self) -> None:
            self.prompt: str | None = None

        def generate(self, prompt: str, *, config: Any, state: dict[str, Any]) -> Any:
            self.prompt = prompt
            return GenerationResult(answer="[BUNDLE_CAPTURE]", model="bundle-capture", raw_response=None)

    output_dir.mkdir(parents=True, exist_ok=True)
    cases_path = output_dir / "cases.jsonl"
    errors_path = output_dir / "bundle_errors.jsonl"
    existing_cases = load_jsonl_map(cases_path, "pair_id")
    completed_ids = {
        pair_id for pair_id, record in existing_cases.items() if record.get("status") == "completed"
    }
    failed_ids: set[str] = set()
    if errors_path.exists():
        from .common import iter_json_records

        failed_ids = {str(record.get("pair_id")) for record in iter_json_records(errors_path) if record.get("pair_id")}

    item_records: dict[str, dict[str, Any]] = {}
    config_records: dict[str, dict[str, Any]] = {}
    planned_pairs: set[str] = set()
    executed = 0
    skipped = 0
    failures = 0
    started_at = utc_now()

    for suite_name in selected_suites:
        suite = plan["suites"][suite_name]
        observed_config_count = 0
        for selection in suite["manifest_selections"]:
            manifest_rel = str(selection["path"])
            include_configs = {str(name) for name in selection.get("include_configs") or []}
            manifest_path = repo_root / manifest_rel
            manifest = load_ablation_manifest(manifest_path)
            available_names = {str(spec.name) for spec in manifest.configs}
            missing_names = sorted(include_configs - available_names)
            if missing_names:
                raise ValueError(f"{manifest_rel} does not contain selected configs: {missing_names}")
            items = load_ablation_dataset(manifest.dataset_path, limit=item_limit)
            for item in items:
                payload = item_payload(item)
                previous = item_records.get(item.id)
                if previous is not None and canonical_json(previous) != canonical_json(payload):
                    raise ValueError(f"Conflicting dataset record for item {item.id}")
                item_records[item.id] = payload

            for spec in manifest.configs:
                if include_configs and spec.name not in include_configs:
                    continue
                observed_config_count += 1
                source_config = spec.build_config()
                source_config_hash = config_hash(source_config)
                config_payload = source_config.model_dump(mode="json")
                config_payload.update(
                    {
                        "branch": "local-kaggle",
                        "generation_model": "offline-local-llm",
                        "experiment_id": f"{source_config.experiment_id}_frozen_retrieval",
                        # Keep the human-readable config name model-blind because the
                        # repository judge prompt includes config.name.
                        "name": source_config.name,
                        "cache_disabled": True,
                    }
                )
                bundle_config = ExperimentConfig.model_validate(config_payload)
                config_key = f"{suite_name}::{spec.name}"
                config_record = {
                    "config_key": config_key,
                    "suite": suite_name,
                    "manifest_name": manifest.name,
                    "manifest_path": manifest_rel,
                    "config_name": spec.name,
                    "source_config_hash": source_config_hash,
                    "bundle_config_hash": config_hash(bundle_config),
                    "config": bundle_config.model_dump(mode="json"),
                }
                previous_config = config_records.get(config_key)
                if previous_config is not None and canonical_json(previous_config) != canonical_json(config_record):
                    raise ValueError(f"Conflicting config_key {config_key}")
                config_records[config_key] = config_record

                for item in items:
                    pair_id = stable_pair_id(suite_name, spec.name, item.id, config_record["bundle_config_hash"])
                    planned_pairs.add(pair_id)
                    if pair_id in completed_ids or (pair_id in failed_ids and not retry_failed):
                        skipped += 1
                        continue
                    initial_state: dict[str, Any] = {
                        "chart_id": item.chart_id,
                        "query": item.query,
                    }
                    if item.user_id:
                        initial_state["user_id"] = item.user_id
                    if item.question_complexity:
                        initial_state["question_complexity"] = item.question_complexity
                    question_family = (item.labels or {}).get("question_family")
                    if question_family:
                        initial_state["question_family"] = question_family
                    chart_loader = None
                    if item.chart_data is not None:
                        chart_payload = item.chart_data
                        chart_loader = lambda chart_id, user_id=None, chart_payload=chart_payload: {
                            "id": chart_id,
                            "user_id": user_id,
                            "chart_system": "TUVI",
                            "chart_data": chart_payload,
                        }
                    capture = CaptureGenerationClient()
                    pair_started = time.perf_counter()
                    try:
                        state = dict(
                            run_rag_dry_run(
                                initial_state,
                                experiment_config=bundle_config,
                                chart_loader=chart_loader,
                                generation_client=capture,
                                retrieval_fallback_on_error=False,
                            )
                        )
                        if not capture.prompt:
                            raise RuntimeError("Generation prompt was not captured")
                        record = {
                            "schema_version": BUNDLE_SCHEMA_VERSION,
                            "status": "completed",
                            "pair_id": pair_id,
                            "suite": suite_name,
                            "config_key": config_key,
                            "item_id": item.id,
                            "prompt": capture.prompt,
                            "prompt_sha256": sha256_text(capture.prompt),
                            "bundle_build_latency_ms": round((time.perf_counter() - pair_started) * 1000, 2),
                            "state": snapshot_state(state, candidate_log_k=candidate_log_k),
                        }
                        assert_no_secret_keys(record)
                        append_jsonl(cases_path, record)
                        existing_cases[pair_id] = record
                        completed_ids.add(pair_id)
                        executed += 1
                    except Exception as exc:
                        failure = {
                            "schema_version": BUNDLE_SCHEMA_VERSION,
                            "status": "failed",
                            "pair_id": pair_id,
                            "suite": suite_name,
                            "config_key": config_key,
                            "item_id": item.id,
                            "error_type": type(exc).__name__,
                            "error": str(exc)[:2000],
                            "failed_at": utc_now(),
                        }
                        assert_no_secret_keys(failure)
                        append_jsonl(errors_path, failure)
                        failures += 1
        expected = int(suite.get("expected_config_count") or observed_config_count)
        if observed_config_count != expected:
            raise RuntimeError(
                f"Suite {suite_name}: expected {expected} configs but loaded {observed_config_count}"
            )

    # Rewrite dimension tables deterministically and compact completed cases after a resume.
    write_jsonl_atomic(output_dir / "items.jsonl", [item_records[key] for key in sorted(item_records)])
    write_jsonl_atomic(output_dir / "configs.jsonl", [config_records[key] for key in sorted(config_records)])
    completed_case_records = [
        existing_cases[pair_id] for pair_id in sorted(planned_pairs) if pair_id in existing_cases
    ]
    write_jsonl_atomic(cases_path, completed_case_records)

    failed_pair_count = len(planned_pairs) - len(completed_case_records)
    manifest_payload = {
        "schema_version": BUNDLE_SCHEMA_VERSION,
        "created_at": utc_now(),
        "started_at": started_at,
        "repo_root_name": repo_root.name,
        "generation_targets": plan.get("models") or {},
        "selected_suites": selected_suites,
        "item_limit": item_limit,
        "candidate_log_k": candidate_log_k,
        "item_count": len(item_records),
        "config_count": len(config_records),
        "planned_pair_count": len(planned_pairs),
        "completed_pair_count": len(completed_case_records),
        "failed_pair_count": failed_pair_count,
        "is_complete": failed_pair_count == 0,
        "executed_this_run": executed,
        "skipped_this_run": skipped,
        "failed_this_run": failures,
        "files": {
            "items": {"name": "items.jsonl", "sha256": sha256_file(output_dir / "items.jsonl")},
            "configs": {"name": "configs.jsonl", "sha256": sha256_file(output_dir / "configs.jsonl")},
            "cases": {"name": "cases.jsonl", "sha256": sha256_file(cases_path)},
        },
        "exact_chunk_metric_note": (
            "The release dataset has no gold_chunk_ids. Candidate IDs are logged for audit, but exact chunk hit "
            "cannot be reported until gold spans are mapped separately for every chunking strategy."
        ),
    }
    assert_no_secret_keys(manifest_payload)
    atomic_write_json(output_dir / "bundle_manifest.json", manifest_payload)
    if manifest_payload["completed_pair_count"] != manifest_payload["planned_pair_count"]:
        raise RuntimeError(
            "Context bundle is incomplete. Inspect bundle_errors.jsonl, fix the cause, and rerun with retry_failed=true."
        )
    return manifest_payload


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python -m src.build_bundle CONFIG.json")
    config = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    print(json.dumps(build_context_bundle(config), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
