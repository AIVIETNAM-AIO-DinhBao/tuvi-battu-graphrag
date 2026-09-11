"""Merge two completed A/B reports into canonical manifest order."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.rag.ablation import load_ablation_manifest  # noqa: E402
from app.rag.config import config_hash  # noqa: E402
from app.rag.evaluation import write_evaluation_reports  # noqa: E402
from app.rag.evaluation_checkpoint import atomic_write_json, sha256_file  # noqa: E402

from run_retrieval_eval import RETRIEVAL_BACKEND, render_markdown  # noqa: E402


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT_DIR / path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Merge two completed sequential ablation shards.")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--report-a", type=Path, required=True)
    parser.add_argument("--report-b", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest_path = resolve(args.manifest)
    reports = [json.loads(resolve(path).read_text(encoding="utf-8")) for path in (args.report_a, args.report_b)]
    for label, report in zip(("A", "B"), reports, strict=True):
        if report.get("status") != "completed":
            raise SystemExit(f"Shard {label} is not completed.")
        if int((report.get("execution_summary") or {}).get("failed_pair_count") or 0) != 0:
            raise SystemExit(f"Shard {label} contains failed pairs.")
        if report.get("dataset_item_count") != 100:
            raise SystemExit(f"Shard {label} does not contain 100 dataset items.")
    if reports[0].get("judge_backend") != reports[1].get("judge_backend"):
        raise SystemExit("Shard backends differ.")
    if reports[0].get("judge_protocol") != reports[1].get("judge_protocol"):
        raise SystemExit("Shard judge protocols differ.")
    if reports[0].get("dataset_path") != reports[1].get("dataset_path"):
        raise SystemExit("Shard dataset paths differ.")
    if reports[0].get("anchor_summary") != reports[1].get("anchor_summary"):
        raise SystemExit("Shard gold-anchor summaries differ.")
    report_bundle_hashes = {
        report.get("bundle_manifest_sha256")
        or report.get("frozen_retrieval_bundle_sha256")
        or next(
            (
                item.get("frozen_retrieval_bundle_sha256")
                for config in report.get("configs") or []
                for item in config.get("items") or []
                if item.get("frozen_retrieval_bundle_sha256")
            ),
            None,
        )
        for report in reports
    }
    if len(report_bundle_hashes) != 1:
        raise SystemExit(f"Shard frozen bundle hashes differ: {sorted(map(str, report_bundle_hashes))}")
    identities = [report.get("run_identity") or {} for report in reports]
    for key in ("dataset_sha256", "evaluator_sha256", "git_sha", "judge_model"):
        values = {identity.get(key) for identity in identities}
        if len(values) != 1:
            raise SystemExit(f"Shard run identities differ for {key}: {sorted(map(str, values))}")
    if any(identity.get("git_dirty") is True for identity in identities):
        raise SystemExit("At least one shard was run from a dirty tracked worktree.")
    timeout_values = {report.get("reranker_timeout_seconds") for report in reports}
    if len(timeout_values) != 1:
        raise SystemExit("Shard offline reranker deadlines differ.")
    manifest = load_ablation_manifest(manifest_path)
    expected_names = [spec.name for spec in manifest.configs]
    by_name: dict[str, dict] = {}
    for report in reports:
        for config in report.get("configs") or []:
            name = str(config.get("config_name"))
            if name in by_name:
                raise SystemExit(f"Duplicate config across shards: {name}")
            by_name[name] = config
    if set(by_name) != set(expected_names):
        raise SystemExit(f"Config mismatch. Missing={sorted(set(expected_names)-set(by_name))}; extra={sorted(set(by_name)-set(expected_names))}")
    expected_hashes = {spec.name: config_hash(spec.build_config()) for spec in manifest.configs}
    for name, expected_hash in expected_hashes.items():
        if by_name[name].get("config_hash") != expected_hash:
            raise SystemExit(f"Config hash mismatch for {name}.")
    merged = dict(reports[0])
    merged.update(
        {
            "manifest_name": manifest.name,
            "notes": manifest.notes,
            "output_dir": str(resolve(args.output_dir)),
            "started_at": min(str(report.get("started_at")) for report in reports),
            "completed_at": datetime.now(UTC).isoformat(),
            "config_count": len(expected_names),
            "configs": [by_name[name] for name in expected_names],
            "status": "completed",
            "shard_run_identities": [report.get("run_identity") for report in reports],
        }
    )
    merged.pop("run_identity", None)
    summaries = [report.get("execution_summary") or {} for report in reports]
    merged["execution_summary"] = {
        key: sum(int(summary.get(key) or 0) for summary in summaries)
        for key in (
            "expected_pair_count",
            "completed_pair_count",
            "failed_pair_count",
            "executed_pair_count",
            "resumed_pair_count",
        )
    }
    expected_pairs = len(expected_names) * 100
    if merged["execution_summary"]["completed_pair_count"] != expected_pairs:
        raise SystemExit(f"Merged completed count is not {expected_pairs}.")
    output_dir = resolve(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "evaluation_report.json"
    atomic_write_json(report_path, merged)
    if merged.get("judge_backend") == RETRIEVAL_BACKEND:
        markdown_path = output_dir / "evaluation_report.md"
        markdown_path.write_text(render_markdown(merged), encoding="utf-8", newline="\n")
    else:
        write_evaluation_reports(merged, output_dir)
        markdown_path = output_dir / "evaluation_report.md"
    atomic_write_json(
        output_dir / "artifact_manifest_sha256.json",
        {
            "evaluation_report.json": sha256_file(report_path),
            "evaluation_report.md": sha256_file(markdown_path),
            "source_report_a": sha256_file(resolve(args.report_a)),
            "source_report_b": sha256_file(resolve(args.report_b)),
            "manifest": sha256_file(manifest_path),
        },
    )
    print(f"PASS: merged {len(expected_names)} configs / {expected_pairs} pairs into {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
