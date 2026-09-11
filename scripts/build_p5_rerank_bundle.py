"""Run retrieval and the cross-encoder once at max depth for sequential P5."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
KIT_ROOT = ROOT_DIR / "benchmark" / "tuvi_golden_dataset" / "local_llm_ablation"
for path in (BACKEND_DIR, KIT_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from app.rag import nodes as rag_nodes  # noqa: E402
from app.rag.ablation import load_ablation_dataset, load_ablation_manifest  # noqa: E402
from app.rag.config import config_hash  # noqa: E402
from app.rag.evaluation_checkpoint import atomic_write_json, sha256_file  # noqa: E402
from app.rag.nodes import DRY_RUN_NODE_ORDER, build_node_map  # noqa: E402
from local_tools.common import load_jsonl_map, write_jsonl_atomic  # noqa: E402


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT_DIR / path


def initial_state(item):
    state = {"chart_id": item.chart_id, "query": item.query}
    if item.user_id:
        state["user_id"] = item.user_id
    if item.question_complexity:
        state["question_complexity"] = item.question_complexity
    family = (item.labels or {}).get("question_family")
    if family:
        state["question_family"] = family
    return state


def main() -> int:
    parser = argparse.ArgumentParser(description="Build one max-depth rerank bundle for deterministic P5 replay.")
    parser.add_argument("--manifest", type=Path, required=True, help="Full P5 manifest containing k10/k20/k40.")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--reranker-timeout-seconds", type=float, default=600.0)
    args = parser.parse_args()
    manifest_path = resolve(args.manifest).resolve()
    output_dir = resolve(args.output_dir).resolve()
    manifest = load_ablation_manifest(manifest_path)
    max_spec = max(manifest.configs, key=lambda spec: spec.build_config().reranker_config.top_k)
    config = max_spec.build_config()
    if not config.reranker_enabled:
        raise SystemExit("P5 replay is valid only after P4 locks reranker on.")
    max_k = int(config.reranker_config.top_k)
    items = load_ablation_dataset(manifest.dataset_path)
    if len(items) != 100:
        raise SystemExit(f"Official P5 bundle requires 100 items; found {len(items)}.")
    rag_nodes.RERANK_TIMEOUT_SECONDS = args.reranker_timeout_seconds
    output_dir.mkdir(parents=True, exist_ok=True)
    cases_path = output_dir / "cases.jsonl"
    existing = load_jsonl_map(cases_path, "item_id") if cases_path.exists() else {}
    for item in items:
        if str(item.id) in existing and existing[str(item.id)].get("status") == "completed":
            continue
        chart_loader = None
        if item.chart_data is not None:
            chart_payload = item.chart_data
            chart_loader = lambda chart_id, user_id=None, chart_payload=chart_payload: {
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
        state = initial_state(item)
        started = time.perf_counter()
        for node_name in DRY_RUN_NODE_ORDER:
            state = nodes[node_name](state)
            if node_name == "rerank":
                break
        trace_nodes = list((state.get("retrieval_trace") or {}).get("nodes") or [])
        trace_detail = next((row for row in reversed(trace_nodes) if row.get("node") == "rerank"), {})
        if state.get("retrieval_backend_unavailable") or trace_detail.get("status") != "completed":
            raise RuntimeError(f"P5 bundle fallback for {item.id}: {trace_detail}")
        if not state.get("reranked_candidates"):
            raise RuntimeError(f"P5 bundle has no reranked candidates for {item.id}: {trace_detail}")
        state.pop("experiment_config", None)
        record = {
            "status": "completed",
            "item_id": item.id,
            "max_k": max_k,
            "build_latency_ms": round((time.perf_counter() - started) * 1000, 2),
            "state": state,
        }
        json.dumps(record, ensure_ascii=False)
        existing[str(item.id)] = record
        write_jsonl_atomic(cases_path, [existing[key] for key in sorted(existing)])
    bundle_manifest = {
        "schema_version": "p5-max-rerank-bundle-v1",
        "source_manifest": manifest_path.relative_to(ROOT_DIR).as_posix(),
        "source_manifest_sha256": sha256_file(manifest_path),
        "builder_config": max_spec.name,
        "builder_config_hash": config_hash(config),
        "max_k": max_k,
        "item_count": len(existing),
        "reranker_execution_count": len(existing),
        "is_complete": len(existing) == 100,
        "cases_sha256": sha256_file(cases_path),
    }
    atomic_write_json(output_dir / "bundle_manifest.json", bundle_manifest)
    if not bundle_manifest["is_complete"]:
        raise RuntimeError(f"Incomplete P5 bundle: {len(existing)}/100")
    print(json.dumps(bundle_manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
