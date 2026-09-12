"""Freeze the P4-selected k=20 context for the final P5 prompt comparison."""

from __future__ import annotations

import argparse
import copy
import json
import sys
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
from app.rag.nodes import build_node_map  # noqa: E402
from local_tools.common import load_jsonl_map, write_jsonl_atomic  # noqa: E402


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT_DIR / path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--p4-bundle", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    manifest_path = resolve(args.manifest).resolve()
    p4_bundle = resolve(args.p4_bundle).resolve()
    output_dir = resolve(args.output_dir).resolve()
    manifest = load_ablation_manifest(manifest_path)
    if len(manifest.configs) != 3:
        raise SystemExit("P5 final prompt manifest must contain exactly three candidates.")
    control = next((spec for spec in manifest.configs if spec.name == "p5_prompt_2"), manifest.configs[0])
    config = control.build_config()
    if not config.reranker_enabled or int(config.reranker_config.top_k) != 20:
        raise SystemExit("P5 final prompt bundle requires the P4-locked reranker-on, retention-20 config.")
    source_meta = json.loads((p4_bundle / "bundle_manifest.json").read_text(encoding="utf-8"))
    if not source_meta.get("is_complete") or int(source_meta.get("reranker_execution_count") or 0) != 100:
        raise SystemExit("P4 max-rerank bundle must prove exactly 100 completed reranker executions.")
    if int(source_meta.get("max_k") or 0) < 20:
        raise SystemExit("P4 max-rerank bundle does not retain enough candidates for k=20.")
    items = load_ablation_dataset(manifest.dataset_path)
    if len(items) != 100:
        raise SystemExit(f"Official P5 prompt bundle requires 100 items; found {len(items)}.")
    source_cases = load_jsonl_map(p4_bundle / "cases.jsonl", "item_id")
    if set(source_cases) != {item.id for item in items}:
        raise SystemExit("P4 bundle item IDs do not exactly match the evaluation dataset.")
    output_dir.mkdir(parents=True, exist_ok=True)
    cases: list[dict] = []
    for item in items:
        state = copy.deepcopy(source_cases[item.id]["state"])
        state["experiment_config"] = config
        state["reranked_candidates"] = list(state.get("reranked_candidates") or [])[:20]
        nodes = build_node_map(experiment_config=config, retrieval_fallback_on_error=False)
        state = nodes["document_grading"](state)
        state = nodes["context_assembly"](state)
        state = nodes["retrieval_diagnostics"](state)
        state.pop("experiment_config", None)
        cases.append({"schema_version": "p5-final-prompt-context-v1", "status": "completed", "pair_id": f"p5-final-prompt::{control.name}::{item.id}", "suite": "p5_final_prompt", "config_key": f"p5_final_prompt::{control.name}", "item_id": item.id, "state": state})
    config_record = {"config_key": f"p5_final_prompt::{control.name}", "suite": "p5_final_prompt", "manifest_name": manifest.name, "manifest_path": manifest_path.relative_to(ROOT_DIR).as_posix(), "config_name": control.name, "source_config_hash": config_hash(config), "bundle_config_hash": config_hash(config), "config": config.model_dump(mode="json")}
    write_jsonl_atomic(output_dir / "cases.jsonl", cases)
    write_jsonl_atomic(output_dir / "configs.jsonl", [config_record])
    write_jsonl_atomic(output_dir / "items.jsonl", [{"item_id": item.id} for item in items])
    bundle_manifest = {"schema_version": "p5-final-prompt-context-v1", "is_complete": True, "planned_pair_count": 100, "completed_pair_count": 100, "failed_pair_count": 0, "selected_suites": ["p5_final_prompt"], "source_p4_bundle": p4_bundle.relative_to(ROOT_DIR).as_posix(), "source_p4_bundle_sha256": sha256_file(p4_bundle / "bundle_manifest.json"), "source_manifest": manifest_path.relative_to(ROOT_DIR).as_posix(), "source_manifest_sha256": sha256_file(manifest_path), "context_config": control.name, "context_config_hash": config_hash(config), "reranker_execution_count": 0, "files": {"cases": {"name": "cases.jsonl", "sha256": sha256_file(output_dir / "cases.jsonl")}, "configs": {"name": "configs.jsonl", "sha256": sha256_file(output_dir / "configs.jsonl")}, "items": {"name": "items.jsonl", "sha256": sha256_file(output_dir / "items.jsonl")}}}
    atomic_write_json(output_dir / "bundle_manifest.json", bundle_manifest)
    print(json.dumps(bundle_manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
