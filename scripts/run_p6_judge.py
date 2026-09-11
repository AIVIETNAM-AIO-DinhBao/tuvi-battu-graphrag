"""Judge all three P6 generators centrally against the frozen context bundle."""

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
    parser = argparse.ArgumentParser(description="Run the centralized official P6 Gemini judge.")
    parser.add_argument(
        "--p6-dir", type=Path, default=Path("benchmark/tuvi_golden_dataset/sequential_ablation/p6_kaggle")
    )
    parser.add_argument("--minimum-key-count", type=int, default=1)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    p6_dir = args.p6_dir if args.p6_dir.is_absolute() else ROOT_DIR / args.p6_dir
    handoff = json.loads((p6_dir / "handoff.json").read_text(encoding="utf-8"))
    inbox = p6_dir / "predictions_inbox"
    inbox.mkdir(parents=True, exist_ok=True)
    summary = run_gemini_judge(
        {
            "repo_root": str(ROOT_DIR),
            "bundle_dir": str(p6_dir / "context_bundle"),
            "prediction_roots": [str(p6_dir / "gemini_predictions"), str(inbox)],
            "output_dir": str(p6_dir / "judge_final"),
            "suites": [handoff["suite"]],
            "selected_config_keys": [handoff["config_key"]],
            "expected_model_ids": [
                "gemini-3.1-flash-lite-preview",
                "Qwen/Qwen2.5-7B-Instruct",
                "google/gemma-3-4b-it",
            ],
            "judge_model": "gemini-3.1-flash-lite-preview",
            "judge_protocol": "blind-v2",
            "blind_seed": 42,
            "gold_anchors": str(
                ROOT_DIR
                / "benchmark"
                / "tuvi_golden_dataset"
                / "sequential_ablation"
                / "gold_span_anchors.jsonl"
            ),
            "retry_attempts": 3,
            "retry_base_seconds": 2.0,
            "retry_failed": True,
            "minimum_key_count": args.minimum_key_count,
            "shard_name": "sequential-p6-final",
        }
    )
    if not summary.get("is_complete") or summary.get("judged_completed_count") != 300:
        raise RuntimeError(f"P6 judge incomplete: {summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
