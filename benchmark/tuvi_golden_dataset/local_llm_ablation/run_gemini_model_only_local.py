from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the Gemini model-only TuViQA baseline locally. The model receives only "
            "the question and raw chart data; no retrieval or corpus context is used."
        )
    )
    parser.add_argument("--mode", choices=("smoke", "official"), default="smoke")
    parser.add_argument("--model", default="gemini-3.1-flash-lite-preview")
    parser.add_argument("--minimum-key-count", type=int, default=1)
    parser.add_argument("--initial-key-offset", type=int, default=0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    kit_root = Path(__file__).resolve().parent
    repo_root = kit_root.parents[2]
    bundle_dir = kit_root / "artifacts" / "model_only_bundle_v1"
    if not (repo_root / "backend" / "app").exists():
        raise FileNotFoundError(f"Cannot locate repository root: {repo_root}")
    if not (bundle_dir / "bundle_manifest.json").exists():
        raise FileNotFoundError("Run notebook 01 official to create model_only_bundle_v1 first")

    sys.path.insert(0, str(kit_root))
    from local_tools.run_gemini_model_only import run_gemini_model_only

    output_name = "gemini_model_only_smoke" if args.mode == "smoke" else "gemini_model_only_official"
    config = {
        "repo_root": str(repo_root),
        "bundle_dir": str(bundle_dir),
        "output_root": str(kit_root / "artifacts" / output_name),
        "model_id": args.model,
        "model_key": "gemini31_flash_lite",
        "limit": 2 if args.mode == "smoke" else None,
        "temperature": 0.0,
        "max_output_tokens": 1024,
        "request_timeout_seconds": 20,
        "retry_attempts": 3,
        "retry_base_seconds": 2.0,
        "retry_errors": True,
        "initial_key_offset": args.initial_key_offset,
        "minimum_key_count": args.minimum_key_count,
    }
    summary = run_gemini_model_only(config)
    expected = 2 if args.mode == "smoke" else 100
    if summary["assigned_pair_count"] != expected:
        raise RuntimeError(f"Expected {expected} assigned pairs: {summary}")
    if not summary["is_complete"] or summary["completed_pair_count"] != expected:
        raise RuntimeError(f"Gemini model-only run is incomplete: {summary}")
    print("\nPASS")
    print(json.dumps({
        "mode": args.mode,
        "completed": summary["completed_pair_count"],
        "failed": summary["failed_pair_count"],
        "model": summary["model_id"],
        "key_rotation": summary["key_rotation"],
        "archive_path": summary["archive_path"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
