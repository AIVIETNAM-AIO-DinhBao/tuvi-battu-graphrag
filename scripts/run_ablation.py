"""Run W4/W6 ablation manifests against the RAG pipeline.

W4-ABL-01 focuses on a small smoke matrix and report/persistence plumbing.
Use ``--offline-smoke --skip-persistence`` for deterministic local checks.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.rag.ablation import (  # noqa: E402
    AblationRunner,
    NullExperimentRunStore,
    SupabaseExperimentRunStore,
    load_ablation_manifest,
    make_default_rag_runner,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a config-aware RAG ablation manifest.")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("configs/w4_ablation_smoke.yaml"),
        help="Path to an ablation manifest YAML file.",
    )
    parser.add_argument("--output-dir", type=Path, default=None, help="Override the report output directory.")
    parser.add_argument("--limit", type=int, default=None, help="Limit dataset items for smoke/debug runs.")
    parser.add_argument(
        "--offline-smoke",
        action="store_true",
        help="Use deterministic generation and fake retrieval dependencies; dataset items must include chart_data.",
    )
    parser.add_argument(
        "--skip-persistence",
        action="store_true",
        help="Do not write rows to Supabase experiment_runs.",
    )
    parser.add_argument(
        "--persist-supabase",
        action="store_true",
        help="Persist one experiment_runs row per config to Supabase.",
    )
    parser.add_argument("--fail-fast", action="store_true", help="Stop on first item/config failure.")
    parser.add_argument(
        "--no-report-files",
        action="store_true",
        help="Run and print summary JSON without writing report files.",
    )
    args = parser.parse_args()
    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be a positive integer when provided.")
    if args.skip_persistence and args.persist_supabase:
        parser.error("Use either --skip-persistence or --persist-supabase, not both.")
    return args


def main() -> int:
    args = parse_args()
    manifest = load_ablation_manifest(args.manifest)
    run_store = SupabaseExperimentRunStore() if args.persist_supabase and not args.skip_persistence else NullExperimentRunStore()
    runner = AblationRunner(
        run_store=run_store,
        rag_runner=make_default_rag_runner(offline_smoke=args.offline_smoke),
        fail_fast=args.fail_fast,
        write_reports=not args.no_report_files,
    )
    report = runner.run(manifest, limit=args.limit, output_dir=args.output_dir)
    summary = {
        "manifest_name": report["manifest_name"],
        "dataset_item_count": report["dataset_item_count"],
        "config_count": report["config_count"],
        "output_dir": report["output_dir"],
        "statuses": {config["config_name"]: config["status"] for config in report["configs"]},
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())