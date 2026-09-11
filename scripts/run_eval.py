"""Run W6-EVAL-02 config-aware evaluation against TuViQA release data.

Official W6 metric runs use Gemini as the judge for RAGAS-like metrics.
Use ``--offline-smoke`` only to verify runner/report plumbing without Neo4j,
Gemini generation, or Gemini judging.
"""

from __future__ import annotations

import argparse
import copy
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
    JUDGE_PROTOCOL_BLIND_V2,
    JUDGE_PROTOCOL_LEGACY_V1,
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
from app.rag.gold_evidence import load_gold_span_anchors  # noqa: E402
from app.rag.nodes import build_node_map  # noqa: E402
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
    parser.add_argument(
        "--frozen-retrieval-bundle",
        type=Path,
        default=None,
        help="P3 bundle: reuse its exact context and execute only generation + citation mapping.",
    )
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
        "--judge-protocol",
        choices=[JUDGE_PROTOCOL_LEGACY_V1, JUDGE_PROTOCOL_BLIND_V2],
        default=JUDGE_PROTOCOL_LEGACY_V1,
        help="blind-v2 hides experiment identities and judges only faithfulness/relevancy.",
    )
    parser.add_argument(
        "--gold-anchors",
        type=Path,
        default=None,
        help="Validated provenance anchors used for Citation Evidence F1.",
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
    if args.judge_protocol == JUDGE_PROTOCOL_BLIND_V2 and not args.offline_smoke and args.gold_anchors is None:
        parser.error("--judge-protocol blind-v2 requires --gold-anchors for Citation Evidence F1.")
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
    git_prefix = ["git", "-c", f"safe.directory={ROOT_DIR.as_posix()}"]
    try:
        sha = subprocess.run(
            [*git_prefix, "rev-parse", "HEAD"],
            cwd=ROOT_DIR,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        dirty = bool(
            subprocess.run(
                [*git_prefix, "status", "--porcelain", "--untracked-files=no"],
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
                BACKEND_DIR / "app" / "rag" / "gold_evidence.py",
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
    judge_protocol = getattr(args, "judge_protocol", JUDGE_PROTOCOL_LEGACY_V1)
    gold_anchors = getattr(args, "gold_anchors", None)
    frozen_bundle = getattr(args, "frozen_retrieval_bundle", None)
    git_sha, git_dirty = git_identity()
    identity = build_run_identity(
        manifest_name=manifest.name,
        dataset_path=manifest.dataset_path,
        config_hashes={name: config_hash(config) for name, config in configs.items()},
        judge_backend=(
            "static-smoke"
            if args.offline_smoke
            else f"{args.judge_backend}:{judge_protocol}"
        ),
        judge_model="static-smoke" if args.offline_smoke else args.judge_model,
        generation_models={name: config.generation_model for name, config in configs.items()},
        manifest_sha256=sha256_json(
            {
                "manifest": manifest_fingerprint(manifest),
                "gold_anchors": (
                    sha256_file(gold_anchors if gold_anchors.is_absolute() else ROOT_DIR / gold_anchors)
                    if gold_anchors is not None
                    else None
                ),
                "frozen_retrieval_bundle": (
                    sha256_file(
                        (
                            frozen_bundle
                            if frozen_bundle.is_absolute()
                            else ROOT_DIR / frozen_bundle
                        )
                        / "bundle_manifest.json"
                    )
                    if frozen_bundle is not None
                    else None
                ),
            }
        ),
        git_sha=git_sha,
        git_dirty=git_dirty,
        evaluator_sha256=evaluator_fingerprint(),
        selected_item_ids=[item.id for item in items],
    )
    store = EvaluationCheckpointStore(checkpoint_path, identity)
    store.load()
    return store


def _jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _retrieval_signature(payload: dict) -> dict:
    keys = (
        "chunk_strategy_id",
        "graph_retrieval_enabled",
        "dense_retrieval_enabled",
        "sparse_retrieval_enabled",
        "fusion_method",
        "retrieval_top_k",
        "reranker_enabled",
        "reranker_config",
        "document_grading_enabled",
        "context_assembly_strategy",
        "query_rewrite_enabled",
        "cache_disabled",
    )
    return {key: payload.get(key) for key in keys}


def make_frozen_retrieval_runner(bundle_path: Path, manifest):
    bundle_dir = bundle_path if bundle_path.is_absolute() else ROOT_DIR / bundle_path
    bundle_manifest = json.loads((bundle_dir / "bundle_manifest.json").read_text(encoding="utf-8"))
    if not bundle_manifest.get("is_complete") or int(bundle_manifest.get("completed_pair_count") or 0) != 100:
        raise ValueError("Frozen P3 bundle must contain 100 completed retrieval cases.")
    cases = _jsonl(bundle_dir / "cases.jsonl")
    cases_by_item = {str(case["item_id"]): case for case in cases if case.get("status") == "completed"}
    if len(cases_by_item) != 100:
        raise ValueError("Frozen P3 bundle must map exactly one context state to each of 100 items.")
    bundle_configs = _jsonl(bundle_dir / "configs.jsonl")
    if len(bundle_configs) != 1:
        raise ValueError("Frozen P3 bundle must have exactly one retrieval configuration.")
    baseline_signature = _retrieval_signature(bundle_configs[0]["config"])
    for spec in manifest.configs:
        signature = _retrieval_signature(spec.build_config().model_dump(mode="json"))
        if signature != baseline_signature:
            raise ValueError(f"P3 config {spec.name!r} changes a frozen retrieval/context field.")
    bundle_digest = sha256_file(bundle_dir / "bundle_manifest.json")

    def run_item(item, config):
        case = cases_by_item.get(item.id)
        if case is None:
            raise KeyError(f"Frozen retrieval state missing for {item.id}")
        state = copy.deepcopy(case["state"])
        state["experiment_config"] = config
        nodes = build_node_map(experiment_config=config, retrieval_fallback_on_error=False)
        state = nodes["generation"](state)
        state = nodes["citation_map"](state)
        state["frozen_retrieval_pair_id"] = case["pair_id"]
        state["frozen_retrieval_bundle_sha256"] = bundle_digest
        return state

    return run_item


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
    judge = make_evaluation_judge(
        backend=args.judge_backend,
        model=args.judge_model,
        protocol=args.judge_protocol,
    )
    anchors_by_item = (
        load_gold_span_anchors(
            args.gold_anchors if args.gold_anchors.is_absolute() else ROOT_DIR / args.gold_anchors
        )
        if args.gold_anchors is not None
        else {}
    )
    rag_runner = (
        make_frozen_retrieval_runner(args.frozen_retrieval_bundle, manifest)
        if args.frozen_retrieval_bundle is not None
        else make_evaluation_rag_runner(offline_smoke=args.offline_smoke)
    )
    runner = EvaluationRunner(
        run_store=run_store,
        rag_runner=rag_runner,
        judge=judge,
        fail_fast=args.fail_fast,
        write_reports=not args.no_report_files,
        max_item_attempts=args.max_item_attempts,
        retry_base_seconds=args.retry_base_seconds,
        checkpoint_store=checkpoint_store,
        retry_failed=args.retry_failed,
        gold_anchors_by_item=anchors_by_item,
    )
    report = runner.run(manifest, limit=args.limit, output_dir=output_dir)
    report["command"] = " ".join(sys.argv)
    if args.frozen_retrieval_bundle is not None:
        bundle_dir = (
            args.frozen_retrieval_bundle
            if args.frozen_retrieval_bundle.is_absolute()
            else ROOT_DIR / args.frozen_retrieval_bundle
        )
        report["frozen_retrieval_bundle_sha256"] = sha256_file(bundle_dir / "bundle_manifest.json")
        report["retrieval_executed_in_phase"] = False
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
