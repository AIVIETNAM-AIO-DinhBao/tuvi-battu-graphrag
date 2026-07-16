"""Run W6-EVAL-02 config-aware evaluation against TuViQA release data.

Official W6 metric runs use Gemini as the judge for RAGAS-like metrics.
Use ``--offline-smoke`` only to verify runner/report plumbing without Neo4j,
Gemini generation, or Gemini judging.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.rag.evaluation import (  # noqa: E402
    DEFAULT_JUDGE_MODEL,
    EvaluationRunner,
    NullExperimentRunStore,
    SupabaseExperimentRunStore,
    build_single_config_manifest,
    load_ablation_manifest,
    make_evaluation_judge,
    make_evaluation_rag_runner,
    write_evaluation_reports,
)
from app.rag.ablation import load_ablation_dataset  # noqa: E402
from app.rag.config import config_hash  # noqa: E402
from app.rag.evaluation_checkpoint import (  # noqa: E402
    CheckpointError,
    EvaluationCheckpointStore,
    build_run_identity,
    sha256_file,
    sha256_json,
)


DEFAULT_DATASET_PATH = Path("benchmark/tuvi_golden_dataset/release/tuviqa_v1_release.jsonl")
DEFAULT_CONFIG_PATH = Path("configs/default_production.yaml")
DEFAULT_OUTPUT_DIR = Path("benchmark/tuvi_golden_dataset/reports/w6_eval_02")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run W6-EVAL-02 config-aware RAG evaluation.")
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument("--manifest", type=Path, default=None, help="Evaluation manifest YAML path.")
    input_group.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Single ExperimentConfig YAML path. Used with --dataset.",
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=DEFAULT_DATASET_PATH,
        help="TuViQA release dataset path for single-config mode.",
    )
    parser.add_argument("--output-dir", type=Path, default=None, help="Override report output directory.")
    parser.add_argument("--limit", type=int, default=None, help="Limit dataset items for smoke/debug runs.")
    parser.add_argument(
        "--judge-backend",
        choices=["gemini", "static"],
        default="gemini",
        help="Judge backend for W6 metrics. Official runs must use gemini.",
    )
    parser.add_argument(
        "--judge-model",
        default=DEFAULT_JUDGE_MODEL,
        help="Gemini judge model used when --judge-backend gemini.",
    )
    parser.add_argument(
        "--offline-smoke",
        action="store_true",
        help="Use deterministic RAG dependencies and static judge. Not an official W6 metric run.",
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
        "--checkpoint-dir",
        type=Path,
        default=None,
        help="Directory containing the atomic evaluation checkpoint and progress summary.",
    )
    parser.add_argument("--resume", action="store_true", help="Resume matching config-item pairs from checkpoint.")
    parser.add_argument(
        "--retry-failed",
        action="store_true",
        help="With --resume, execute failed checkpoint pairs again instead of preserving them.",
    )
    parser.add_argument(
        "--max-item-attempts",
        type=int,
        default=1,
        help="Maximum attempts per config-item pair, including the first attempt.",
    )
    parser.add_argument(
        "--retry-base-seconds",
        type=float,
        default=0.0,
        help="Base exponential-backoff delay between item attempts.",
    )
    parser.add_argument(
        "--no-report-files",
        action="store_true",
        help="Run and print summary JSON without writing report files.",
    )
    args = parser.parse_args()
    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be a positive integer when provided.")
    if args.max_item_attempts < 1:
        parser.error("--max-item-attempts must be at least 1.")
    if args.retry_base_seconds < 0:
        parser.error("--retry-base-seconds must be non-negative.")
    if args.resume and args.checkpoint_dir is None:
        parser.error("--resume requires --checkpoint-dir.")
    if args.retry_failed and not args.resume:
        parser.error("--retry-failed requires --resume.")
    if args.skip_persistence and args.persist_supabase:
        parser.error("Use either --skip-persistence or --persist-supabase, not both.")
    if args.offline_smoke and args.judge_backend != "static":
        args.judge_backend = "static"
    if args.judge_backend == "static" and not args.offline_smoke:
        parser.error("--judge-backend static is only allowed with --offline-smoke.")
    return args


def build_manifest(args: argparse.Namespace):
    if args.manifest:
        return load_ablation_manifest(args.manifest)
    return build_single_config_manifest(
        dataset_path=args.dataset,
        config_path=args.config or DEFAULT_CONFIG_PATH,
        output_dir=args.output_dir or DEFAULT_OUTPUT_DIR,
    )


def git_identity() -> tuple[str | None, bool | None]:
    try:
        sha = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT_DIR,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        dirty = bool(
            subprocess.run(
                ["git", "status", "--porcelain", "--untracked-files=no"],
                cwd=ROOT_DIR,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
        )
        return sha or None, dirty
    except (OSError, subprocess.SubprocessError):
        return None, None


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


def build_checkpoint_store(args: argparse.Namespace, manifest) -> EvaluationCheckpointStore | None:
    if args.checkpoint_dir is None:
        return None
    checkpoint_path = args.checkpoint_dir / "evaluation_checkpoint.json"
    if checkpoint_path.exists() and not args.resume:
        raise CheckpointError(
            f"Checkpoint already exists: {checkpoint_path}. Use --resume or choose a new --checkpoint-dir."
        )
    items = load_ablation_dataset(manifest.dataset_path, limit=args.limit)
    configs = {spec.name: spec.build_config() for spec in manifest.configs}
    git_sha, git_dirty = git_identity()
    identity = build_run_identity(
        manifest_name=manifest.name,
        dataset_path=manifest.dataset_path,
        config_hashes={name: config_hash(config) for name, config in configs.items()},
        judge_backend="static-smoke" if args.offline_smoke else args.judge_backend,
        judge_model="static-smoke" if args.offline_smoke else args.judge_model,
        generation_models={name: config.generation_model for name, config in configs.items()},
        manifest_sha256=manifest_fingerprint(manifest),
        git_sha=git_sha,
        git_dirty=git_dirty,
        evaluator_sha256=evaluator_fingerprint(),
        selected_item_ids=[item.id for item in items],
    )
    store = EvaluationCheckpointStore(checkpoint_path, identity)
    store.load()
    return store


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = parse_args()
    manifest = build_manifest(args)
    output_dir = args.output_dir
    try:
        checkpoint_store = build_checkpoint_store(args, manifest)
    except (CheckpointError, OSError, ValueError) as exc:
        print(f"Checkpoint error: {exc}", file=sys.stderr)
        return 2
    run_store = SupabaseExperimentRunStore() if args.persist_supabase and not args.skip_persistence else NullExperimentRunStore()
    judge = make_evaluation_judge(backend=args.judge_backend, model=args.judge_model)
    runner = EvaluationRunner(
        run_store=run_store,
        rag_runner=make_evaluation_rag_runner(offline_smoke=args.offline_smoke),
        judge=judge,
        fail_fast=args.fail_fast,
        write_reports=not args.no_report_files,
        max_item_attempts=args.max_item_attempts,
        retry_base_seconds=args.retry_base_seconds,
        checkpoint_store=checkpoint_store,
        retry_failed=args.retry_failed,
    )
    report = runner.run(manifest, limit=args.limit, output_dir=output_dir)
    report["command"] = " ".join(sys.argv)
    if not args.no_report_files:
        write_evaluation_reports(report, Path(report["output_dir"]))
    summary = {
        "manifest_name": report["manifest_name"],
        "dataset_item_count": report["dataset_item_count"],
        "config_count": report["config_count"],
        "judge_backend": report["judge_backend"],
        "output_dir": report["output_dir"],
        "statuses": {config["config_name"]: config["status"] for config in report["configs"]},
        "metrics": {config["config_name"]: config["metrics"] for config in report["configs"]},
        "status": report.get("status"),
        "execution_summary": report.get("execution_summary") or {},
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report.get("status") == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())