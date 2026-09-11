"""Build and archive the single frozen-context bundle for sequential P6."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
KIT_ROOT = ROOT_DIR / "benchmark" / "tuvi_golden_dataset" / "local_llm_ablation"
if str(KIT_ROOT) not in sys.path:
    sys.path.insert(0, str(KIT_ROOT))

from local_tools.build_bundle import build_context_bundle  # noqa: E402


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT_DIR / path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the official P6 frozen context bundle locally.")
    parser.add_argument(
        "--p6-dir", type=Path, default=Path("benchmark/tuvi_golden_dataset/sequential_ablation/p6_kaggle")
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    p6_dir = resolve(args.p6_dir).resolve()
    output_dir = p6_dir / "context_bundle"
    summary = build_context_bundle(
        {
            "repo_root": str(ROOT_DIR),
            "kit_root": str(KIT_ROOT),
            "plan_path": str(p6_dir / "experiment_plan.json"),
            "output_dir": str(output_dir),
            "suites": ["sequential_final_1"],
            "candidate_log_k": 100,
            "retry_failed": True,
            "strict_no_fallback": True,
            "reranker_timeout_seconds": 600.0,
        }
    )
    if summary.get("completed_pair_count") != 100 or summary.get("failed_pair_count") != 0:
        raise RuntimeError(f"P6 bundle is incomplete: {summary}")
    archive = Path(shutil.make_archive(str(p6_dir / "p6_frozen_context_bundle"), "zip", root_dir=output_dir))
    print(json.dumps({"summary": summary, "archive": str(archive)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
