"""Materialize one audited winning candidate as the immutable base for the next phase."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import yaml


ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.rag.ablation import load_ablation_manifest  # noqa: E402
from app.rag.config import config_hash  # noqa: E402
from app.rag.evaluation_checkpoint import atomic_write_json, sha256_file  # noqa: E402


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT_DIR / path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Lock one completed sequential ablation candidate.")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--winner", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest_path, report_path, output_path = map(resolve, (args.manifest, args.report, args.output))
    if output_path.exists() and not args.force:
        raise SystemExit(f"Refusing to overwrite locked config: {output_path}")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    if report.get("status") != "completed":
        raise SystemExit(f"Report is not completed: {report.get('status')}")
    execution = report.get("execution_summary") or {}
    if int(execution.get("failed_pair_count") or 0) != 0:
        raise SystemExit("Report contains failed pairs.")
    manifest = load_ablation_manifest(manifest_path)
    specs = {spec.name: spec for spec in manifest.configs}
    if report.get("dataset_item_count") != 100:
        raise SystemExit("Official lock requires exactly 100 dataset items.")
    if int(execution.get("completed_pair_count") or 0) != len(specs) * 100:
        raise SystemExit("Completed pair count does not match full manifest × 100 items.")
    if args.winner not in specs:
        raise SystemExit(f"Winner {args.winner!r} is not in manifest.")
    report_configs = {str(row.get("config_name")): row for row in report.get("configs") or []}
    if set(report_configs) != set(specs):
        raise SystemExit("Report config set does not match the canonical manifest.")
    for name, spec in specs.items():
        row = report_configs[name]
        if row.get("status") != "completed":
            raise SystemExit(f"Config {name!r} is incomplete.")
        if row.get("config_hash") != config_hash(spec.build_config()):
            raise SystemExit(f"Config hash mismatch for {name!r}.")
        metrics = row.get("metrics") or {}
        for key in (
            "retrieval_backend_fallback_count",
            "generation_backend_fallback_count",
            "judge_failure_count",
            "failed_count",
            "invalid_citation_marker_count",
        ):
            if key in metrics and int(metrics.get(key) or 0) != 0:
                raise SystemExit(f"Config {name!r} has non-zero {key}.")
    identity = report.get("run_identity") or {}
    if identity.get("git_dirty") is True:
        raise SystemExit("Refusing to lock a report produced from a dirty tracked worktree.")
    if args.winner not in report_configs or report_configs[args.winner].get("status") != "completed":
        raise SystemExit(f"Winner {args.winner!r} is missing or incomplete in report.")
    config = specs[args.winner].build_config()
    digest = config_hash(config)
    if report_configs[args.winner].get("config_hash") != digest:
        raise SystemExit("Winner config hash does not match the manifest-built config.")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        yaml.safe_dump(config.model_dump(mode="json"), allow_unicode=True, sort_keys=False),
        encoding="utf-8",
        newline="\n",
    )
    metadata_path = output_path.with_suffix(".lock.json")
    atomic_write_json(
        metadata_path,
        {
            "locked_at": datetime.now(UTC).isoformat(),
            "manifest": manifest_path.as_posix(),
            "manifest_sha256": sha256_file(manifest_path),
            "report": report_path.as_posix(),
            "report_sha256": sha256_file(report_path),
            "winner": args.winner,
            "config_hash": digest,
            "locked_config": output_path.as_posix(),
            "locked_config_sha256": sha256_file(output_path),
        },
    )
    print(f"locked winner={args.winner} config_hash={digest}")
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
