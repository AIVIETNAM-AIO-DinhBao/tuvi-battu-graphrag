"""Run the Gemini candidate on the same frozen P6 prompt bundle as Kaggle models."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
KIT_ROOT = ROOT_DIR / "benchmark" / "tuvi_golden_dataset" / "local_llm_ablation"
if str(KIT_ROOT) not in sys.path:
    sys.path.insert(0, str(KIT_ROOT))

from local_tools.run_gemini_model_only import run_gemini_model_only  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run official sequential P6 Gemini generation.")
    parser.add_argument(
        "--p6-dir", type=Path, default=Path("benchmark/tuvi_golden_dataset/sequential_ablation/p6_kaggle")
    )
    parser.add_argument("--minimum-key-count", type=int, default=1)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    p6_dir = args.p6_dir if args.p6_dir.is_absolute() else ROOT_DIR / args.p6_dir
    handoff = json.loads((p6_dir / "handoff.json").read_text(encoding="utf-8"))
    summary = run_gemini_model_only(
        {
            "repo_root": str(ROOT_DIR),
            "bundle_dir": str(p6_dir / "context_bundle"),
            "output_root": str(p6_dir / "gemini_predictions"),
            "model_id": "gemini-3.1-flash-lite-preview",
            "model_key": "gemini31_flash_lite",
            "suite": handoff["suite"],
            "config_key": handoff["config_key"],
            "output_label": handoff["config_name"],
            "temperature": 0.0,
            "max_output_tokens": 1024,
            "request_timeout_seconds": 20,
            "retry_attempts": 3,
            "retry_base_seconds": 2.0,
            "retry_errors": True,
            "minimum_key_count": args.minimum_key_count,
        }
    )
    if not summary.get("is_complete") or summary.get("completed_pair_count") != 100:
        raise RuntimeError(f"P6 Gemini generation incomplete: {summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
