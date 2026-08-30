from __future__ import annotations

import json
import re
import subprocess
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from .common import atomic_write_json, canonical_json, sha256_file, sha256_text


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_") or "model"


def build_legacy_config_results(
    item_results: list[dict[str, Any]],
    configs: dict[str, dict[str, Any]],
    *,
    aggregate_evaluation_metrics: Callable[..., dict[str, Any]],
    aggregate_grouped_metrics: Callable[..., dict[str, Any]],
    started_at: str,
    completed_at: str,
) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in item_results:
        grouped[(str(row["model_id"]), str(row["config_key"]))].append(row)

    output: list[dict[str, Any]] = []
    for model_id, config_key in sorted(grouped):
        metadata = configs[config_key]
        payload = metadata["config"]
        rows = sorted(grouped[(model_id, config_key)], key=lambda row: str(row["item_id"]))
        model_key = str(rows[0].get("model_key") or safe_slug(model_id.rsplit("/", 1)[-1]))
        base_name = str(metadata["config_name"])
        report_config_name = f"{model_key}__{base_name}"
        config_hash = sha256_text(
            canonical_json(
                {
                    "bundle_config_hash": metadata["bundle_config_hash"],
                    "model_id": model_id,
                    "model_revision": rows[0].get("model_revision"),
                    "quantization": rows[0].get("quantization"),
                }
            )
        )
        reranker = payload.get("reranker_config") or {}
        output.append(
            {
                "chunk_strategy_id": payload.get("chunk_strategy_id"),
                "completed_at": completed_at,
                "config_hash": config_hash,
                "config_name": report_config_name,
                "base_config_name": base_name,
                "config_key": config_key,
                "context_assembly_strategy": payload.get("context_assembly_strategy"),
                "dense_retrieval_enabled": payload.get("dense_retrieval_enabled"),
                "document_grading_enabled": payload.get("document_grading_enabled"),
                "error": None,
                "experiment_id": f"{payload.get('experiment_id')}__{model_key}",
                "fusion_method": payload.get("fusion_method"),
                "generation_model": model_id,
                "model_revision": rows[0].get("model_revision"),
                "quantization": rows[0].get("quantization"),
                "graph_retrieval_enabled": payload.get("graph_retrieval_enabled"),
                "grouped_metrics": aggregate_grouped_metrics(rows),
                "items": rows,
                "metrics": aggregate_evaluation_metrics(rows, expected_item_count=len(rows)),
                "prompt_template_id": payload.get("prompt_template_id"),
                "reranker_enabled": bool(reranker.get("enabled")),
                "reranker_top_k": reranker.get("top_k"),
                "run_id": sha256_text(f"{report_config_name}:{config_hash}")[:24],
                "sparse_retrieval_enabled": payload.get("sparse_retrieval_enabled"),
                "started_at": started_at,
                "status": "completed" if all(row.get("status") == "completed" for row in rows) else "failed",
            }
        )
    return output


def git_identity(repo_root: Path) -> tuple[str | None, bool | None]:
    try:
        sha = subprocess.run(
            ["git", "-c", f"safe.directory={repo_root.as_posix()}", "rev-parse", "HEAD"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        dirty = bool(
            subprocess.run(
                ["git", "-c", f"safe.directory={repo_root.as_posix()}", "status", "--porcelain"],
                cwd=repo_root,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
        )
        return sha or None, dirty
    except Exception:
        return None, None


def build_run_identity(
    *,
    repo_root: Path,
    kit_root: Path,
    bundle_dir: Path,
    legacy_configs: list[dict[str, Any]],
    judge_model: str,
    manifest_name: str,
) -> dict[str, Any]:
    dataset_path = repo_root / "benchmark" / "tuvi_golden_dataset" / "release" / "tuviqa_v1_release.jsonl"
    evaluator_path = repo_root / "backend" / "app" / "rag" / "evaluation.py"
    plan_path = kit_root / "experiment_plan.json"
    git_sha, git_dirty = git_identity(repo_root)
    identity = {
        "schema_version": 1,
        "manifest_name": manifest_name,
        "dataset_sha256": sha256_file(dataset_path),
        "manifest_sha256": sha256_file(plan_path),
        "bundle_cases_sha256": sha256_file(bundle_dir / "cases.jsonl"),
        "evaluator_sha256": sha256_file(evaluator_path),
        "config_hashes": {row["config_name"]: row["config_hash"] for row in legacy_configs},
        "generation_models": {row["config_name"]: row["generation_model"] for row in legacy_configs},
        "judge_backend": "gemini",
        "judge_model": judge_model,
        "selected_item_ids": sorted(
            {str(item["item_id"]) for row in legacy_configs for item in row.get("items") or []}
        ),
        "git_sha": git_sha,
        "git_dirty": git_dirty,
    }
    identity["identity_sha256"] = sha256_text(canonical_json(identity))
    return identity


def write_legacy_artifacts(
    *,
    output_dir: Path,
    repo_root: Path,
    kit_root: Path,
    bundle_dir: Path,
    legacy_configs: list[dict[str, Any]],
    judge_model: str,
    manifest_name: str,
    started_at: str,
    completed_at: str,
    expected_pair_count: int,
    failed_pair_count: int,
    executed_pair_count: int,
    resumed_pair_count: int,
    metric_definitions: dict[str, Any],
    render_markdown_report: Callable[[dict[str, Any]], str],
    notes: str,
    source_shard_reports: list[dict[str, Any]] | None = None,
    merge_policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    checkpoints = output_dir / "checkpoints"
    checkpoints.mkdir(parents=True, exist_ok=True)
    run_identity = build_run_identity(
        repo_root=repo_root,
        kit_root=kit_root,
        bundle_dir=bundle_dir,
        legacy_configs=legacy_configs,
        judge_model=judge_model,
        manifest_name=manifest_name,
    )
    completed_pair_count = expected_pair_count - failed_pair_count
    dataset_item_count = len(
        {str(item["item_id"]) for row in legacy_configs for item in row.get("items") or []}
    )
    report: dict[str, Any] = {
        "manifest_name": manifest_name,
        "dataset_path": "benchmark/tuvi_golden_dataset/release/tuviqa_v1_release.jsonl",
        "output_dir": str(output_dir),
        "config_count": len(legacy_configs),
        "dataset_item_count": dataset_item_count,
        "judge_backend": "gemini",
        "started_at": started_at,
        "completed_at": completed_at,
        "notes": notes,
        "configs": legacy_configs,
        "execution_summary": {
            "expected_pair_count": expected_pair_count,
            "completed_pair_count": completed_pair_count,
            "failed_pair_count": failed_pair_count,
            "executed_pair_count": executed_pair_count,
            "resumed_pair_count": resumed_pair_count,
        },
        "status": "completed" if failed_pair_count == 0 and completed_pair_count == expected_pair_count else "failed",
        "run_identity": run_identity,
        "metric_definitions": metric_definitions,
        "checkpoint_path": str(checkpoints / "evaluation_checkpoint.json"),
        "command": "notebooks/03_gemini_judge_local.ipynb",
        "ablation_analysis": {},
    }
    if source_shard_reports is not None:
        report["source_shard_reports"] = source_shard_reports
    if merge_policy is not None:
        report["merge_policy"] = merge_policy

    report_path = output_dir / "evaluation_report.json"
    markdown_path = output_dir / "evaluation_report.md"
    atomic_write_json(report_path, report)
    markdown_path.write_text(render_markdown_report(report), encoding="utf-8")

    config_items = {
        row["config_name"]: {"items": {str(item["item_id"]): item for item in row.get("items") or []}}
        for row in legacy_configs
    }
    checkpoint = {
        "schema_version": 1,
        "created_at": started_at,
        "updated_at": completed_at,
        "run_identity": run_identity,
        "configs": config_items,
    }
    atomic_write_json(checkpoints / "evaluation_checkpoint.json", checkpoint)
    last_config = legacy_configs[-1]["config_name"] if legacy_configs else None
    last_items = (legacy_configs[-1].get("items") or []) if legacy_configs else []
    checkpoint_summary = {
        "current_config": last_config,
        "current_item": last_items[-1].get("item_id") if last_items else None,
        "expected_pair_count": expected_pair_count,
        "processed_pair_count": completed_pair_count + failed_pair_count,
        "remaining_pair_count": max(0, expected_pair_count - completed_pair_count - failed_pair_count),
        "executed_pair_count": executed_pair_count,
        "resumed_pair_count": resumed_pair_count,
        "failed_pair_count": failed_pair_count,
        "updated_at": completed_at,
    }
    atomic_write_json(checkpoints / "checkpoint_summary.json", checkpoint_summary)
    return report
