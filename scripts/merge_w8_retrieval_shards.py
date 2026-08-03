"""Merge W8 retrieval/fusion/reranker shard reports into the canonical report.

The official W8 retrieval matrix is split by config so multiple teammates can run
independent full-100 shards without writing to the same checkpoint/report files.
This script validates completed shard artifacts and writes the canonical
10-config report expected by ``scripts/build_final_ablation_report.py``.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.rag.ablation import load_ablation_dataset, load_ablation_manifest  # noqa: E402
from app.rag.config import config_hash  # noqa: E402
from app.rag.evaluation import build_ablation_analysis, write_evaluation_reports  # noqa: E402
from app.rag.evaluation_checkpoint import atomic_write_json, sha256_file, sha256_json  # noqa: E402


CANONICAL_MANIFEST = ROOT / "configs" / "w8_abl_01_retrieval_matrix_v2.yaml"
CANONICAL_OUTPUT_DIR = ROOT / "benchmark" / "tuvi_golden_dataset" / "reports_final" / "20_retrieval_fusion_reranker_matrix"
SHARD_REPORTS = [
    CANONICAL_OUTPUT_DIR / "shards" / "shard_a_controls" / "evaluation_report.json",
    CANONICAL_OUTPUT_DIR / "shards" / "shard_b_single_paths" / "evaluation_report.json",
    CANONICAL_OUTPUT_DIR / "shards" / "shard_c_dense_combos" / "evaluation_report.json",
]
EXPECTED_JUDGE_BACKEND = "gemini"


def posix(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing shard report: {posix(path)}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Report must contain a JSON object: {posix(path)}")
    return payload


def normalize_path(raw_path: Any) -> Path:
    path = Path(str(raw_path or ""))
    if path.is_absolute():
        return path.resolve()
    return (ROOT / path).resolve()


def manifest_fingerprint(manifest) -> str:
    return sha256_json(
        {
            "name": manifest.name,
            "notes": manifest.notes,
            "dataset_path": str(manifest.dataset_path),
            "configs": [
                {
                    "name": spec.name,
                    "base_config_path": str(spec.base_config_path),
                    "overrides": spec.overrides,
                }
                for spec in manifest.configs
            ],
        }
    )


def evaluator_fingerprint() -> str:
    return sha256_json(
        {
            path.name: sha256_file(path)
            for path in [
                BACKEND_DIR / "app" / "rag" / "evaluation.py",
                BACKEND_DIR / "app" / "rag" / "nodes.py",
                BACKEND_DIR / "app" / "rag" / "evaluation_checkpoint.py",
            ]
        }
    )


def git_output(*args: str) -> str | None:
    try:
        return subprocess.run(
            ["git", *args],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None


def git_dirty() -> bool | None:
    try:
        status = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=no"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        ).stdout.strip()
        return bool(status)
    except (OSError, subprocess.SubprocessError):
        return None


def validate_shard_report(
    *,
    report: dict[str, Any],
    path: Path,
    dataset_path: Path,
    expected_item_count: int,
    expected_hashes: dict[str, str],
    require_completed: bool,
) -> list[dict[str, Any]]:
    errors: list[str] = []
    if report.get("judge_backend") != EXPECTED_JUDGE_BACKEND:
        errors.append(f"judge_backend must be {EXPECTED_JUDGE_BACKEND!r}, got {report.get('judge_backend')!r}")
    if normalize_path(report.get("dataset_path")) != dataset_path.resolve():
        errors.append(f"dataset_path mismatch: {report.get('dataset_path')!r} != {posix(dataset_path)!r}")
    if report.get("dataset_item_count") != expected_item_count:
        errors.append(f"dataset_item_count must be {expected_item_count}, got {report.get('dataset_item_count')!r}")
    if require_completed and report.get("status") != "completed":
        errors.append(f"report status must be completed, got {report.get('status')!r}")
    execution = report.get("execution_summary") or {}
    if require_completed and execution.get("failed_pair_count") != 0:
        errors.append(f"execution_summary.failed_pair_count must be 0, got {execution.get('failed_pair_count')!r}")

    configs = report.get("configs") or []
    if not isinstance(configs, list) or not configs:
        errors.append("configs must be a non-empty array")
        configs = []
    expected_pair_count = len(configs) * expected_item_count
    if execution and execution.get("expected_pair_count") != expected_pair_count:
        errors.append(
            "execution_summary.expected_pair_count must be "
            f"{expected_pair_count}, got {execution.get('expected_pair_count')!r}"
        )
    if require_completed and execution.get("completed_pair_count") != expected_pair_count:
        errors.append(
            "execution_summary.completed_pair_count must be "
            f"{expected_pair_count}, got {execution.get('completed_pair_count')!r}"
        )
    for row in configs:
        if not isinstance(row, dict):
            errors.append("each config row must be an object")
            continue
        name = row.get("config_name")
        if name not in expected_hashes:
            errors.append(f"unexpected config_name {name!r}")
            continue
        if row.get("config_hash") != expected_hashes[name]:
            errors.append(f"config_hash mismatch for {name}: {row.get('config_hash')!r} != {expected_hashes[name]!r}")
        if require_completed and row.get("status") != "completed":
            errors.append(f"config {name} status must be completed, got {row.get('status')!r}")
        metrics = row.get("metrics") or {}
        if metrics.get("item_count") != expected_item_count:
            errors.append(f"config {name} metrics.item_count must be {expected_item_count}, got {metrics.get('item_count')!r}")
        if require_completed and metrics.get("failed_count") != 0:
            errors.append(f"config {name} metrics.failed_count must be 0, got {metrics.get('failed_count')!r}")
        items = row.get("items") or []
        if len(items) != expected_item_count:
            errors.append(f"config {name} must contain {expected_item_count} item results, got {len(items)}")
        if require_completed:
            failed_items = [item.get("item_id") for item in items if isinstance(item, dict) and item.get("status") != "completed"]
            if failed_items:
                errors.append(f"config {name} has non-completed items: {failed_items[:5]}")

    if errors:
        bullet_list = "\n".join(f"  - {message}" for message in errors)
        raise ValueError(f"Invalid shard report {posix(path)}:\n{bullet_list}")
    return configs


def merge_reports(args: argparse.Namespace) -> dict[str, Any]:
    manifest = load_ablation_manifest(args.canonical_manifest)
    items = load_ablation_dataset(manifest.dataset_path)
    expected_names = [spec.name for spec in manifest.configs]
    expected_hashes = {spec.name: config_hash(spec.build_config()) for spec in manifest.configs}
    dataset_path = Path(manifest.dataset_path)
    expected_item_count = len(items)

    all_configs: list[dict[str, Any]] = []
    source_reports: list[dict[str, Any]] = []
    for report_path in args.shard_reports:
        report = load_json(report_path)
        configs = validate_shard_report(
            report=report,
            path=report_path,
            dataset_path=dataset_path,
            expected_item_count=expected_item_count,
            expected_hashes=expected_hashes,
            require_completed=not args.allow_incomplete,
        )
        all_configs.extend(configs)
        source_reports.append(
            {
                "path": posix(report_path),
                "manifest_name": report.get("manifest_name"),
                "output_dir": report.get("output_dir"),
                "status": report.get("status"),
                "config_count": report.get("config_count"),
                "execution_summary": report.get("execution_summary"),
            }
        )

    counts = Counter(row.get("config_name") for row in all_configs)
    duplicates = sorted(name for name, count in counts.items() if count > 1)
    missing = [name for name in expected_names if counts.get(name, 0) == 0]
    unexpected = sorted(name for name in counts if name not in expected_hashes)
    if duplicates or missing or unexpected:
        raise ValueError(
            "Shard config coverage is invalid: "
            f"duplicates={duplicates}, missing={missing}, unexpected={unexpected}"
        )

    configs_by_name = {row["config_name"]: row for row in all_configs}
    ordered_configs = [configs_by_name[name] for name in expected_names]
    failed_pair_count = sum(int((row.get("metrics") or {}).get("failed_count") or 0) for row in ordered_configs)
    expected_pair_count = len(expected_names) * expected_item_count
    completed_pair_count = expected_pair_count - failed_pair_count
    status = "completed" if failed_pair_count == 0 else ("partial" if completed_pair_count > 0 else "failed")
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")

    started_values = [str(row.get("started_at")) for row in ordered_configs if row.get("started_at")]
    completed_values = [str(row.get("completed_at")) for row in ordered_configs if row.get("completed_at")]
    run_identity = {
        "manifest_name": manifest.name,
        "dataset_path": posix(dataset_path),
        "dataset_sha256": sha256_file(dataset_path),
        "config_hashes": expected_hashes,
        "judge_backend": EXPECTED_JUDGE_BACKEND,
        "judge_model": args.judge_model,
        "generation_models": {spec.name: spec.build_config().generation_model for spec in manifest.configs},
        "manifest_sha256": manifest_fingerprint(manifest),
        "git_sha": git_output("rev-parse", "HEAD"),
        "git_dirty": git_dirty(),
        "evaluator_sha256": evaluator_fingerprint(),
        "selected_item_ids": [item.id for item in items],
    }
    run_identity["identity_sha256"] = sha256_json(run_identity)

    report = {
        "manifest_name": manifest.name,
        "notes": manifest.notes,
        "dataset_path": posix(dataset_path),
        "output_dir": posix(args.output_dir),
        "started_at": min(started_values) if started_values else now,
        "completed_at": max(completed_values) if completed_values else now,
        "dataset_item_count": expected_item_count,
        "config_count": len(ordered_configs),
        "judge_backend": EXPECTED_JUDGE_BACKEND,
        "metric_definitions": (source_reports and load_json(args.shard_reports[0]).get("metric_definitions")) or {},
        "configs": ordered_configs,
        "status": status,
        "execution_summary": {
            "expected_pair_count": expected_pair_count,
            "completed_pair_count": completed_pair_count,
            "failed_pair_count": failed_pair_count,
            "executed_pair_count": sum(
                int(((source.get("execution_summary") or {}).get("executed_pair_count") or 0))
                for source in source_reports
            ),
            "resumed_pair_count": sum(
                int(((source.get("execution_summary") or {}).get("resumed_pair_count") or 0))
                for source in source_reports
            ),
        },
        "command": " ".join(sys.argv),
        "checkpoint_path": posix(args.output_dir / "checkpoints" / "checkpoint_summary.json"),
        "run_identity": run_identity,
        "source_shard_reports": source_reports,
        "merge_policy": {
            "strategy": "config_shard_concatenation",
            "canonical_config_order": expected_names,
            "require_completed": not args.allow_incomplete,
        },
    }
    report["ablation_analysis"] = build_ablation_analysis(report)
    return report


def write_merged_artifacts(report: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    write_evaluation_reports(report, output_dir)
    checkpoint_dir = output_dir / "checkpoints"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    execution = report.get("execution_summary") or {}
    current_config = None
    current_item = None
    configs = report.get("configs") or []
    if configs:
        current_config = configs[-1].get("config_name")
        items = configs[-1].get("items") or []
        if items:
            current_item = items[-1].get("item_id")
    atomic_write_json(
        checkpoint_dir / "checkpoint_summary.json",
        {
            "expected_pair_count": execution.get("expected_pair_count"),
            "processed_pair_count": execution.get("completed_pair_count"),
            "executed_pair_count": execution.get("executed_pair_count"),
            "resumed_pair_count": execution.get("resumed_pair_count"),
            "failed_pair_count": execution.get("failed_pair_count"),
            "remaining_pair_count": max(
                int(execution.get("expected_pair_count") or 0) - int(execution.get("completed_pair_count") or 0),
                0,
            ),
            "current_config": current_config,
            "current_item": current_item,
            "updated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "source_shard_reports": report.get("source_shard_reports") or [],
            "merge_policy": report.get("merge_policy") or {},
        },
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--canonical-manifest", type=Path, default=CANONICAL_MANIFEST)
    parser.add_argument("--output-dir", type=Path, default=CANONICAL_OUTPUT_DIR)
    parser.add_argument("--shard-report", dest="shard_reports", action="append", type=Path)
    parser.add_argument("--judge-model", default="gemini-3.1-flash-lite-preview")
    parser.add_argument("--allow-incomplete", action="store_true", help="Merge partial shards for debugging; do not use for final evidence.")
    parser.add_argument("--dry-run", action="store_true", help="Validate and print summary without writing canonical artifacts.")
    args = parser.parse_args()
    if not args.canonical_manifest.is_absolute():
        args.canonical_manifest = ROOT / args.canonical_manifest
    if not args.output_dir.is_absolute():
        args.output_dir = ROOT / args.output_dir
    if args.shard_reports:
        args.shard_reports = [path if path.is_absolute() else ROOT / path for path in args.shard_reports]
    else:
        args.shard_reports = SHARD_REPORTS
    return args


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = parse_args()
    try:
        report = merge_reports(args)
        if not args.dry_run:
            write_merged_artifacts(report, args.output_dir)
    except Exception as exc:
        print(f"Merge failed: {exc}", file=sys.stderr)
        return 2

    execution = report.get("execution_summary") or {}
    print(
        json.dumps(
            {
                "status": report.get("status"),
                "output_dir": report.get("output_dir"),
                "config_count": report.get("config_count"),
                "expected_pair_count": execution.get("expected_pair_count"),
                "completed_pair_count": execution.get("completed_pair_count"),
                "failed_pair_count": execution.get("failed_pair_count"),
                "dry_run": args.dry_run,
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if report.get("status") == "completed" or args.allow_incomplete else 1


if __name__ == "__main__":
    raise SystemExit(main())