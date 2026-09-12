"""Replay P4 retention 10/20/40 from one frozen max-depth reranker output."""

from __future__ import annotations

import argparse
import copy
import json
import sys
import time
from datetime import UTC, datetime
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
KIT_ROOT = ROOT_DIR / "benchmark" / "tuvi_golden_dataset" / "local_llm_ablation"
for path in (BACKEND_DIR, KIT_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from app.rag.ablation import load_ablation_dataset, load_ablation_manifest  # noqa: E402
from app.rag.config import config_hash  # noqa: E402
from app.rag.evaluation_checkpoint import atomic_write_json, sha256_file  # noqa: E402
from app.rag.gold_evidence import aggregate_gold_evidence, load_gold_span_anchors, score_gold_evidence  # noqa: E402
from app.rag.nodes import build_node_map  # noqa: E402
from app.rag.token_overlap import aggregate_token_overlap, score_token_overlap  # noqa: E402
from local_tools.common import load_jsonl_map  # noqa: E402


def utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT_DIR / path


def percentile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    values = sorted(values)
    position = (len(values) - 1) * q
    lower = int(position)
    upper = min(lower + 1, len(values) - 1)
    fraction = position - lower
    return round(values[lower] * (1 - fraction) + values[upper] * fraction, 2)


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministically replay P4 retention arms without rerunning reranker.")
    parser.add_argument("--manifest", type=Path, required=True, help="Full or A/B-sharded P4 manifest.")
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--anchors", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    manifest_path = resolve(args.manifest).resolve()
    bundle_dir = resolve(args.bundle).resolve()
    anchors_path = resolve(args.anchors).resolve()
    output_dir = resolve(args.output_dir).resolve()
    manifest = load_ablation_manifest(manifest_path)
    items = load_ablation_dataset(manifest.dataset_path)
    anchors = load_gold_span_anchors(anchors_path)
    bundle_meta = json.loads((bundle_dir / "bundle_manifest.json").read_text(encoding="utf-8"))
    if not bundle_meta.get("is_complete") or int(bundle_meta.get("reranker_execution_count") or 0) != 100:
        raise SystemExit("P4 bundle must prove exactly 100 successful reranker executions.")
    cases = load_jsonl_map(bundle_dir / "cases.jsonl", "item_id")
    if set(cases) != {item.id for item in items}:
        raise SystemExit("P4 bundle item IDs do not exactly match the evaluation dataset.")
    config_reports = []
    started_at = utc_now()
    for spec in manifest.configs:
        config = spec.build_config()
        if not config.reranker_enabled:
            raise SystemExit(f"{spec.name}: reranker must stay enabled in P5.")
        top_k = int(config.reranker_config.top_k)
        if top_k > int(bundle_meta["max_k"]):
            raise SystemExit(f"{spec.name}: top_k={top_k} exceeds frozen max_k={bundle_meta['max_k']}.")
        results = []
        for item in items:
            case = cases[item.id]
            state = copy.deepcopy(case["state"])
            state["experiment_config"] = config
            full_reranked = list(state.get("reranked_candidates") or [])
            state["reranked_candidates"] = full_reranked[:top_k]
            replay_started = time.perf_counter()
            nodes = build_node_map(experiment_config=config, retrieval_fallback_on_error=False)
            state = nodes["document_grading"](state)
            state = nodes["context_assembly"](state)
            state = nodes["retrieval_diagnostics"](state)
            replay_ms = round((time.perf_counter() - replay_started) * 1000, 2)
            context_chunks = list(state.get("context_chunks") or [])
            scores = score_gold_evidence(context_chunks, anchors.get(item.id, []))
            token_scores = score_token_overlap(context_chunks, list(item.gold_context_spans))
            if anchors.get(item.id) and scores["mapped_corpus_chunk_count"] != scores["corpus_chunk_count"]:
                raise RuntimeError(f"{spec.name}/{item.id}: missing provenance after replay")
            results.append(
                {
                    "status": "completed",
                    "item_id": item.id,
                    "chart_only": not bool(item.gold_context_spans),
                    "rule_metric_eligible": bool(anchors.get(item.id)),
                    "gold_annotation_span_count": len(item.gold_context_spans),
                    "token_overlap_threshold": token_scores["token_overlap_threshold"],
                    "recall_at_8": token_scores["recall_at_8"],
                    "precision_at_8": token_scores["precision_at_8"],
                    "f1_at_8": token_scores["f1_at_8"],
                    "token_overlap_span_details": token_scores["token_overlap_span_details"],
                    "token_overlap_chunk_details": token_scores["token_overlap_chunk_details"],
                    **{key: value for key, value in scores.items() if key not in {"gold_span_details", "chunk_details"}},
                    "gold_span_details": scores["gold_span_details"],
                    "chunk_details": scores["chunk_details"],
                    "full_reranked_count": len(full_reranked),
                    "replayed_top_k": top_k,
                    "replay_latency_ms": replay_ms,
                    "rerank_bundle_build_latency_ms": case.get("build_latency_ms"),
                    "retrieval_latency_ms": round(float(case.get("build_latency_ms") or 0) + replay_ms, 2),
                    "result_source": "deterministic-replay",
                }
            )
        metrics = aggregate_gold_evidence(results)
        metrics.update(aggregate_token_overlap(results))
        latencies = [float(row["retrieval_latency_ms"]) for row in results]
        metrics["retrieval_p50_ms"] = percentile(latencies, 0.50)
        metrics["retrieval_p95_ms"] = percentile(latencies, 0.95)
        metrics["reranker_execution_count"] = 0
        metrics["replay_count"] = len(results)
        config_reports.append(
            {
                "config_name": spec.name,
                "experiment_id": config.experiment_id,
                "config_hash": config_hash(config),
                "reranker_enabled": True,
                "reranker_top_k": top_k,
                "status": "completed",
                "metrics": metrics,
                "items": results,
            }
        )
    report = {
        "schema_version": "sequential-p5-replay-v1",
        "manifest_name": manifest.name,
        "dataset_path": str(manifest.dataset_path),
        "dataset_item_count": len(items),
        "config_count": len(config_reports),
        "judge_backend": "rule-based-token-overlap-v2",
        "metric_definitions": {
            "normalization": "Unicode NFD + casefold + remove combining marks/punctuation + Unicode word tokens",
            "matching": "same source family and gold-token multiset coverage >= 0.25",
            "recall_at_8": "Evidence Recall: hit gold spans / all gold spans in the final selected context",
            "precision_at_8": "Evidence Precision: relevant corpus context chunks / all corpus context chunks in the final selected context",
            "f1_at_8": "Evidence F1: harmonic mean of aggregate Evidence Recall and Evidence Precision",
            "gold_span_policy": "include every raw gold span regardless of anchor mapping status",
        },
        "generation_executed": False,
        "reranker_execution_mode": "one-max-depth-build-then-deterministic-truncation",
        "bundle_manifest_sha256": sha256_file(bundle_dir / "bundle_manifest.json"),
        "started_at": started_at,
        "completed_at": utc_now(),
        "status": "completed",
        "execution_summary": {
            "expected_pair_count": len(items) * len(config_reports),
            "completed_pair_count": len(items) * len(config_reports),
            "failed_pair_count": 0,
            "reranker_execution_count": 0,
            "replay_pair_count": len(items) * len(config_reports),
        },
        "configs": config_reports,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    atomic_write_json(output_dir / "evaluation_report.json", report)
    lines = [
        f"# P5 deterministic replay — {manifest.name}",
        "",
        f"- Frozen max-depth reranker executions: `{bundle_meta['reranker_execution_count']}`",
        f"- Bundle SHA-256: `{report['bundle_manifest_sha256']}`",
        "",
        "| Config | Evidence Recall | Evidence Precision | Evidence F1 | Retrieval p95 ms | Replays |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in config_reports:
        metric = row["metrics"]
        lines.append(
            f"| {row['config_name']} | {metric['recall_at_8']} | "
            f"{metric['precision_at_8']} | {metric['f1_at_8']} | "
            f"{metric['retrieval_p95_ms']} | {metric['replay_count']} |"
        )
    markdown_path = output_dir / "evaluation_report.md"
    markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    atomic_write_json(
        output_dir / "artifact_manifest_sha256.json",
        {
            "evaluation_report.json": sha256_file(output_dir / "evaluation_report.json"),
            "evaluation_report.md": sha256_file(markdown_path),
            "source_manifest": sha256_file(manifest_path),
            "bundle_manifest.json": sha256_file(bundle_dir / "bundle_manifest.json"),
            "gold_anchors.jsonl": sha256_file(anchors_path),
        },
    )
    print(json.dumps({"output_dir": str(output_dir), "configs": len(config_reports)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
