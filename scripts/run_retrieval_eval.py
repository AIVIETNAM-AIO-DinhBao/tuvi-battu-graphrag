"""Run live retrieval/context ablations without generation or an AI judge."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.rag.ablation import load_ablation_dataset, load_ablation_manifest  # noqa: E402
from app.rag.config import config_hash  # noqa: E402
from app.rag.evaluation import retrieval_latency_ms  # noqa: E402
from app.rag.evaluation_checkpoint import (  # noqa: E402
    CheckpointError,
    EvaluationCheckpointStore,
    atomic_write_json,
    build_run_identity,
    sha256_file,
    sha256_json,
)
from app.rag.gold_evidence import (  # noqa: E402
    aggregate_gold_evidence,
    load_gold_span_anchors,
    score_gold_evidence,
)
from app.rag.token_overlap import aggregate_token_overlap, score_token_overlap  # noqa: E402
from app.rag import nodes as rag_nodes  # noqa: E402
from app.rag.nodes import DRY_RUN_NODE_ORDER, build_node_map  # noqa: E402


DEFAULT_ANCHORS = Path("benchmark/tuvi_golden_dataset/sequential_ablation/gold_span_anchors.jsonl")
RETRIEVAL_BACKEND = "rule-based-token-overlap-v2"
SKIPPED_NODES = {"generation", "citation_map"}


def utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def resolve_repo_path(path: Path) -> Path:
    return path if path.is_absolute() else ROOT_DIR / path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run official live retrieval-only ablation.")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--anchors", type=Path, default=DEFAULT_ANCHORS)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--checkpoint-dir", type=Path, required=True)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--retry-failed", action="store_true")
    parser.add_argument("--max-item-attempts", type=int, default=2)
    parser.add_argument("--retry-base-seconds", type=float, default=2.0)
    parser.add_argument(
        "--reranker-timeout-seconds",
        type=float,
        default=600.0,
        help="Offline-only reranker deadline. The interactive API keeps its 8-second default.",
    )
    parser.add_argument("--fail-fast", action="store_true")
    args = parser.parse_args()
    if args.max_item_attempts < 1:
        parser.error("--max-item-attempts must be at least 1.")
    if args.retry_base_seconds < 0:
        parser.error("--retry-base-seconds must be non-negative.")
    if args.reranker_timeout_seconds <= 0:
        parser.error("--reranker-timeout-seconds must be positive.")
    if args.retry_failed and not args.resume:
        parser.error("--retry-failed requires --resume.")
    return args


def git_identity() -> tuple[str | None, bool | None]:
    git_prefix = ["git", "-c", f"safe.directory={ROOT_DIR.as_posix()}"]
    try:
        sha = subprocess.run(
            [*git_prefix, "rev-parse", "HEAD"], cwd=ROOT_DIR, check=True, capture_output=True, text=True
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


def run_live_retrieval(item: Any, config: Any) -> dict[str, Any]:
    initial_state: dict[str, Any] = {"chart_id": item.chart_id, "query": item.query}
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
        chart_loader = lambda chart_id, user_id=None: {  # noqa: E731
            "id": chart_id,
            "user_id": user_id,
            "chart_system": "TUVI",
            "chart_data": chart_payload,
        }
    nodes = build_node_map(
        experiment_config=config,
        chart_loader=chart_loader,
        retrieval_fallback_on_error=False,
    )
    state = dict(initial_state)
    for node_name in DRY_RUN_NODE_ORDER:
        if node_name in SKIPPED_NODES:
            continue
        state = nodes[node_name](state)
    return state


def run_item(item: Any, config: Any, anchors: list[dict[str, Any]]) -> dict[str, Any]:
    started = time.perf_counter()
    state = run_live_retrieval(item, config)
    elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
    if state.get("retrieval_backend_unavailable"):
        raise RuntimeError("retrieval backend unavailable")
    diagnostics = dict(state.get("retrieval_diagnostics") or {})
    fallbacks = list(diagnostics.get("fallbacks") or [])
    if fallbacks:
        raise RuntimeError(f"retrieval fallback detected: {fallbacks}")
    context_chunks = list(state.get("context_chunks") or [])
    final_scores = score_gold_evidence(context_chunks, anchors)
    token_scores = score_token_overlap(context_chunks, list(item.gold_context_spans))
    if anchors and final_scores["mapped_corpus_chunk_count"] != final_scores["corpus_chunk_count"]:
        raise RuntimeError(
            "selected corpus context is missing doc/section/character provenance: "
            f"mapped={final_scores['mapped_corpus_chunk_count']} total={final_scores['corpus_chunk_count']}"
        )
    fused_scores = score_gold_evidence(list(state.get("fused_candidates") or []), anchors)
    chart_only = not bool(item.gold_context_spans)
    return {
        "status": "completed",
        "item_id": item.id,
        "query": item.query,
        "question_complexity": item.question_complexity,
        "question_family": (item.labels or {}).get("question_family"),
        "chart_only": chart_only,
        "rule_metric_eligible": bool(anchors),
        "gold_annotation_span_count": len(item.gold_context_spans),
        "token_overlap_threshold": token_scores["token_overlap_threshold"],
        "recall_at_8": token_scores["recall_at_8"],
        "precision_at_8": token_scores["precision_at_8"],
        "f1_at_8": token_scores["f1_at_8"],
        "token_overlap_span_details": token_scores["token_overlap_span_details"],
        "token_overlap_chunk_details": token_scores["token_overlap_chunk_details"],
        **{key: value for key, value in final_scores.items() if key not in {"gold_span_details", "chunk_details"}},
        "fused_gold_span_recall": fused_scores["gold_span_recall"],
        "gold_span_details": final_scores["gold_span_details"],
        "chunk_details": final_scores["chunk_details"],
        "context_chunks": context_chunks,
        "retrieval_diagnostics": diagnostics,
        "retrieval_trace": state.get("retrieval_trace") or {},
        "retrieval_latency_ms": retrieval_latency_ms(state) or elapsed_ms,
        "total_latency_ms": elapsed_ms,
        "fallbacks": fallbacks,
        "error": None,
    }


def run_item_with_retries(
    item: Any,
    config: Any,
    anchors: list[dict[str, Any]],
    *,
    attempts: int,
    retry_base_seconds: float,
) -> dict[str, Any]:
    errors: list[str] = []
    for attempt in range(1, attempts + 1):
        started = time.perf_counter()
        try:
            result = run_item(item, config, anchors)
            result["attempt_count"] = attempt
            result["attempt_errors"] = errors
            result["result_source"] = "executed"
            return result
        except Exception as exc:
            errors.append(f"{type(exc).__name__}: {exc}")
            if attempt < attempts and retry_base_seconds:
                time.sleep(retry_base_seconds * (2 ** (attempt - 1)))
            last_latency = round((time.perf_counter() - started) * 1000, 2)
    return {
        "status": "failed",
        "item_id": item.id,
        "query": item.query,
        "question_complexity": item.question_complexity,
        "question_family": (item.labels or {}).get("question_family"),
        "chart_only": not bool(item.gold_context_spans),
        "rule_metric_eligible": bool(anchors),
        "attempt_count": attempts,
        "attempt_errors": errors,
        "retrieval_latency_ms": None,
        "total_latency_ms": last_latency,
        "error": errors[-1],
        "result_source": "executed",
    }


def percentile(values: list[float], quantile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * quantile
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return round(ordered[lower] * (1 - fraction) + ordered[upper] * fraction, 2)


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        f"# Retrieval-only report — {report['manifest_name']}",
        "",
        f"- Status: `{report['status']}`",
        f"- Dataset items: `{report['dataset_item_count']}`",
        f"- Anchor mapping coverage: `{report['anchor_summary'].get('mapping_coverage')}`",
        f"- Backend: `{RETRIEVAL_BACKEND}`",
        "",
        "| Config | Status | Recall@8 | Precision@8 | F1@8 | Retrieval p95 ms | Failed |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for config in report["configs"]:
        metrics = config["metrics"]
        lines.append(
            "| {name} | {status} | {recall} | {precision} | {f1} | {p95} | {failed} |".format(
                name=config["config_name"],
                status=config["status"],
                recall=metrics.get("recall_at_8"),
                precision=metrics.get("precision_at_8"),
                f1=metrics.get("f1_at_8"),
                p95=metrics.get("retrieval_p95_ms"),
                failed=metrics.get("failed_count"),
            )
        )
    lines.extend(
        [
            "",
            "Recall@8 and Precision@8 use source-aligned multiset token overlap at tau=0.25. All annotated gold spans enter the recall denominator.",
            "Exact-coordinate gold metrics remain in JSON as provenance diagnostics only.",
            "Generation and AI judging were not executed in this report.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = parse_args()
    # Official ablation is an offline batch job. Give the real cross-encoder time
    # to finish instead of accepting the interactive API's bounded fallback.
    rag_nodes.RERANK_TIMEOUT_SECONDS = args.reranker_timeout_seconds
    manifest_path = resolve_repo_path(args.manifest).resolve()
    anchors_path = resolve_repo_path(args.anchors).resolve()
    checkpoint_dir = resolve_repo_path(args.checkpoint_dir).resolve()
    manifest = load_ablation_manifest(manifest_path)
    items = load_ablation_dataset(manifest.dataset_path)
    anchors_by_item = load_gold_span_anchors(anchors_path)
    configs = {spec.name: spec.build_config() for spec in manifest.configs}
    output_dir = resolve_repo_path(args.output_dir).resolve() if args.output_dir else manifest.output_dir
    checkpoint_path = checkpoint_dir / "evaluation_checkpoint.json"
    if checkpoint_path.exists() and not args.resume:
        print(f"Checkpoint exists: {checkpoint_path}. Use --resume or a new directory.", file=sys.stderr)
        return 2

    anchor_summary_path = anchors_path.with_name("gold_span_anchor_summary.json")
    anchor_summary = json.loads(anchor_summary_path.read_text(encoding="utf-8"))
    git_sha, git_dirty = git_identity()
    identity = build_run_identity(
        manifest_name=manifest.name,
        dataset_path=manifest.dataset_path,
        config_hashes={name: config_hash(config) for name, config in configs.items()},
        judge_backend=RETRIEVAL_BACKEND,
        manifest_sha256=sha256_json(
            {
                "manifest_sha256": sha256_file(manifest_path),
                "anchors_sha256": sha256_file(anchors_path),
                "reranker_timeout_seconds": args.reranker_timeout_seconds,
            }
        ),
        git_sha=git_sha,
        git_dirty=git_dirty,
        evaluator_sha256=sha256_json(
            {
                "runner": sha256_file(Path(__file__)),
                "scorer": sha256_file(BACKEND_DIR / "app" / "rag" / "gold_evidence.py"),
                "token_overlap_scorer": sha256_file(BACKEND_DIR / "app" / "rag" / "token_overlap.py"),
            }
        ),
        selected_item_ids=[item.id for item in items],
    )
    try:
        store = EvaluationCheckpointStore(checkpoint_path, identity)
        store.load()
    except CheckpointError as exc:
        print(f"Checkpoint error: {exc}", file=sys.stderr)
        return 2

    started_at = utc_now()
    config_reports: list[dict[str, Any]] = []
    executed = resumed = 0
    for spec in manifest.configs:
        config = configs[spec.name]
        item_results: list[dict[str, Any]] = []
        config_started = utc_now()
        for item in items:
            cached = store.item_results(spec.name, item_ids=[item.id])
            cached_result = cached[0] if cached else None
            if cached_result is not None and (cached_result.get("status") == "completed" or not args.retry_failed):
                result = dict(cached_result)
                result["result_source"] = "checkpoint"
                resumed += 1
            else:
                result = run_item_with_retries(
                    item,
                    config,
                    anchors_by_item.get(item.id, []),
                    attempts=args.max_item_attempts,
                    retry_base_seconds=args.retry_base_seconds,
                )
                store.record_item(spec.name, item.id, result)
                executed += 1
            item_results.append(result)
            processed = executed + resumed
            failed_so_far = sum(
                1
                for config_name in configs
                for row in store.item_results(config_name)
                if row.get("status") != "completed"
            )
            atomic_write_json(
                checkpoint_dir / "checkpoint_summary.json",
                {
                    "expected_pair_count": len(items) * len(configs),
                    "processed_pair_count": processed,
                    "executed_pair_count": executed,
                    "resumed_pair_count": resumed,
                    "failed_pair_count": failed_so_far,
                    "remaining_pair_count": len(items) * len(configs) - processed,
                    "current_config": spec.name,
                    "current_item": item.id,
                    "updated_at": utc_now(),
                },
            )
            if args.fail_fast and result.get("status") != "completed":
                raise RuntimeError(result.get("error") or f"Retrieval failed for {item.id}")
        metrics = aggregate_gold_evidence(item_results)
        metrics.update(aggregate_token_overlap(item_results))
        metrics["fused_gold_span_recall"] = (
            round(
                sum(float(row["fused_gold_span_recall"]) for row in item_results if row.get("fused_gold_span_recall") is not None)
                / max(1, sum(1 for row in item_results if row.get("fused_gold_span_recall") is not None)),
                6,
            )
        )
        latency_values = [float(row["retrieval_latency_ms"]) for row in item_results if row.get("retrieval_latency_ms") is not None]
        metrics["retrieval_p50_ms"] = percentile(latency_values, 0.50)
        metrics["retrieval_p95_ms"] = percentile(latency_values, 0.95)
        status = "completed" if metrics["failed_count"] == 0 else "failed"
        config_reports.append(
            {
                "config_name": spec.name,
                "experiment_id": config.experiment_id,
                "config_hash": config_hash(config),
                "chunk_strategy_id": config.chunk_strategy_id,
                "graph_retrieval_enabled": config.graph_retrieval_enabled,
                "dense_retrieval_enabled": config.dense_retrieval_enabled,
                "sparse_retrieval_enabled": config.sparse_retrieval_enabled,
                "fusion_method": config.fusion_method,
                "reranker_enabled": config.reranker_enabled,
                "reranker_top_k": config.reranker_config.top_k,
                "status": status,
                "started_at": config_started,
                "completed_at": utc_now(),
                "metrics": metrics,
                "items": item_results,
            }
        )

    failed_pairs = sum(config["metrics"]["failed_count"] for config in config_reports)
    expected_pairs = len(items) * len(configs)
    report = {
        "schema_version": "sequential-retrieval-ablation-v1",
        "manifest_name": manifest.name,
        "dataset_path": str(manifest.dataset_path),
        "dataset_item_count": len(items),
        "config_count": len(configs),
        "judge_backend": RETRIEVAL_BACKEND,
        "generation_executed": False,
        "reranker_timeout_seconds": args.reranker_timeout_seconds,
        "anchor_summary": anchor_summary,
        "metric_definitions": {
            "recall_at_8": "Gold-span hit rate using same-source multiset token coverage >= 0.25; all annotated spans are included.",
            "precision_at_8": "Fraction of selected corpus chunks matching >= 0.25 of at least one same-source gold span's tokens.",
            "f1_at_8": "Harmonic mean of aggregate Recall@8 and Precision@8.",
        },
        "started_at": started_at,
        "completed_at": utc_now(),
        "status": "completed" if failed_pairs == 0 else "partial",
        "execution_summary": {
            "expected_pair_count": expected_pairs,
            "completed_pair_count": expected_pairs - failed_pairs,
            "failed_pair_count": failed_pairs,
            "executed_pair_count": executed,
            "resumed_pair_count": resumed,
        },
        "run_identity": identity,
        "configs": config_reports,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "evaluation_report.json"
    markdown_path = output_dir / "evaluation_report.md"
    atomic_write_json(report_path, report)
    markdown_path.write_text(render_markdown(report), encoding="utf-8", newline="\n")
    atomic_write_json(
        output_dir / "artifact_manifest_sha256.json",
        {
            "evaluation_report.json": sha256_file(report_path),
            "evaluation_report.md": sha256_file(markdown_path),
            "evaluation_checkpoint.json": sha256_file(checkpoint_path),
            "anchors": sha256_file(anchors_path),
            "dataset": sha256_file(manifest.dataset_path),
        },
    )
    print(json.dumps({"status": report["status"], **report["execution_summary"], "output_dir": str(output_dir)}, indent=2))
    return 0 if failed_pairs == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
