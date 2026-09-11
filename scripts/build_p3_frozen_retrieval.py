"""Build the one-retrieval-per-item bundle used by sequential P3."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
KIT_ROOT = ROOT_DIR / "benchmark" / "tuvi_golden_dataset" / "local_llm_ablation"
for path in (BACKEND_DIR, KIT_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from app.rag.ablation import load_ablation_manifest  # noqa: E402
from app.rag.evaluation_checkpoint import atomic_write_json, sha256_file  # noqa: E402
from local_tools.build_bundle import build_context_bundle  # noqa: E402


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT_DIR / path


def main() -> int:
    parser = argparse.ArgumentParser(description="Freeze P2-locked retrieval once for all P3 prompt arms.")
    parser.add_argument("--manifest", type=Path, required=True, help="Full P3 prompt manifest.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("benchmark/tuvi_golden_dataset/sequential_ablation/results/P3_prompt/frozen_retrieval"),
    )
    parser.add_argument("--reranker-timeout-seconds", type=float, default=600.0)
    args = parser.parse_args()
    manifest_path = resolve(args.manifest).resolve()
    output_dir = resolve(args.output_dir).resolve()
    manifest = load_ablation_manifest(manifest_path)
    if len(manifest.configs) < 2:
        raise SystemExit("P3 manifest must contain multiple prompt candidates.")
    control = next((spec for spec in manifest.configs if spec.name == "p3_structured_v3"), manifest.configs[0])
    plan_path = output_dir.parent / "p3_frozen_retrieval_plan.json"
    manifest_rel = manifest_path.relative_to(ROOT_DIR).as_posix()
    plan = {
        "schema_version": "p3-frozen-retrieval-plan-v1",
        "default_suites": ["p3_frozen_retrieval"],
        "models": {},
        "suites": {
            "p3_frozen_retrieval": {
                "description": "One P2-locked retrieval/context state shared by every P3 prompt arm.",
                "manifest_selections": [
                    {"path": manifest_rel, "include_configs": [control.name]}
                ],
                "expected_config_count": 1,
                "expected_item_count": 100,
                "expected_retrieval_pair_count": 100,
            }
        },
    }
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_json(plan_path, plan)
    summary = build_context_bundle(
        {
            "repo_root": str(ROOT_DIR),
            "kit_root": str(KIT_ROOT),
            "plan_path": str(plan_path),
            "output_dir": str(output_dir),
            "suites": ["p3_frozen_retrieval"],
            "candidate_log_k": 100,
            "retry_failed": True,
            "strict_no_fallback": True,
            "reranker_timeout_seconds": args.reranker_timeout_seconds,
        }
    )
    if summary.get("completed_pair_count") != 100 or summary.get("failed_pair_count") != 0:
        raise RuntimeError(f"P3 frozen retrieval bundle is incomplete: {summary}")
    audit = {
        "protocol": "p3-frozen-retrieval-v1",
        "source_manifest": manifest_rel,
        "source_manifest_sha256": sha256_file(manifest_path),
        "control_used_to_build_retrieval": control.name,
        "retrieval_execution_count": 100,
        "prompt_candidate_count": len(manifest.configs),
        "bundle_manifest_sha256": sha256_file(output_dir / "bundle_manifest.json"),
    }
    atomic_write_json(output_dir / "p3_freeze_audit.json", audit)
    print(json.dumps({"summary": summary, "audit": audit}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
