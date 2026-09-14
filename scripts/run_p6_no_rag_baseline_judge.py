"""Re-score the existing three-model chart-only baseline with the current P6 judge."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
KIT_ROOT = ROOT_DIR / "benchmark" / "tuvi_golden_dataset" / "local_llm_ablation"
if str(KIT_ROOT) not in sys.path:
    sys.path.insert(0, str(KIT_ROOT))

from local_tools.run_judge import run_gemini_judge  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Judge the immutable Qwen/Gemma/Gemini chart-only baseline with current blind-v2."
    )
    parser.add_argument(
        "--p6-dir", type=Path, default=Path("benchmark/tuvi_golden_dataset/sequential_ablation/p6_kaggle")
    )
    parser.add_argument("--minimum-key-count", type=int, default=1)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    p6_dir = args.p6_dir if args.p6_dir.is_absolute() else ROOT_DIR / args.p6_dir
    artifacts = KIT_ROOT / "artifacts"
    summary = run_gemini_judge(
        {
            "repo_root": str(ROOT_DIR),
            "bundle_dir": str(artifacts / "model_only_bundle_v1"),
            "prediction_roots": [
                str(artifacts / "gemini_model_only_official"),
                str(artifacts / "prediction_archives" / "M"),
            ],
            "output_dir": str(p6_dir / "no_rag_baseline"),
            "suites": ["model_only"],
            "selected_config_keys": ["model_only::question_chart_direct"],
            "expected_model_ids": [
                "gemini-3.1-flash-lite-preview",
                "Qwen/Qwen2.5-7B-Instruct",
                "google/gemma-3-4b-it",
            ],
            "judge_model": "gemini-3.1-flash-lite-preview",
            "judge_protocol": "blind-v2",
            "blind_seed": 42,
            "gold_anchors": str(
                ROOT_DIR / "benchmark" / "tuvi_golden_dataset" / "sequential_ablation" / "gold_span_anchors.jsonl"
            ),
            "retry_attempts": 3,
            "retry_base_seconds": 2.0,
            "retry_failed": True,
            "minimum_key_count": args.minimum_key_count,
            "shard_name": "sequential-p6-no-rag-baseline",
        }
    )
    if not summary.get("is_complete") or summary.get("judged_completed_count") != 300:
        raise RuntimeError(f"P6 no-RAG baseline judge incomplete: {summary}")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
