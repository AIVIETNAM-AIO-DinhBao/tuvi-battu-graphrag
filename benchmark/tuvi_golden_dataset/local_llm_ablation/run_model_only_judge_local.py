from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


EXPECTED_MODELS = {
    "Qwen/Qwen2.5-7B-Instruct",
    "google/gemma-3-4b-it",
    "gemini-3.1-flash-lite-preview",
}
SUITE = "model_only"
CONFIG_KEY = "model_only::question_chart_direct"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Preflight or judge all three model-only TuViQA runs.")
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--minimum-key-count", type=int, default=2)
    parser.add_argument("--initial-key-offset", type=int, default=0)
    return parser.parse_args()


def paths() -> tuple[Path, Path, list[Path], Path]:
    kit_root = Path(__file__).resolve().parent
    repo_root = kit_root.parents[2]
    bundle_dir = kit_root / "artifacts" / "model_only_bundle_v1"
    kaggle_archives = kit_root / "artifacts" / "prediction_archives" / "M"
    gemini_archive = (
        kit_root
        / "artifacts"
        / "gemini_model_only_official"
        / "local_llm_predictions_gemini31_flash_lite_question-chart-direct_00_of_01.zip"
    )
    output_dir = kit_root / "artifacts" / "gemini_judge_model_only_3models"
    return repo_root, bundle_dir, [kaggle_archives, gemini_archive], output_dir


def run_preflight(bundle_dir: Path, prediction_roots: list[Path], output_dir: Path) -> dict[str, object]:
    from local_tools.common import load_jsonl_map
    from local_tools.run_judge import discover_prediction_files, merge_predictions

    cases = {
        pair_id: row
        for pair_id, row in load_jsonl_map(bundle_dir / "cases.jsonl", "pair_id").items()
        if row.get("suite") == SUITE and row.get("config_key") == CONFIG_KEY
    }
    files = discover_prediction_files(prediction_roots, output_dir / "_preflight_extracted_predictions")
    predictions = merge_predictions(files)
    expected_keys = {f"{model_id}::{pair_id}" for model_id in EXPECTED_MODELS for pair_id in cases}
    completed = {
        key: row
        for key, row in predictions.items()
        if key in expected_keys and row.get("status") == "completed"
    }
    missing = sorted(expected_keys - set(completed))
    unexpected = sorted(set(predictions) - expected_keys)
    prompt_mismatches = sorted(
        key
        for key, row in completed.items()
        if str(row.get("prompt_sha256") or "")
        != str(cases[str(row["pair_id"])].get("prompt_sha256") or "")
    )
    model_counts = {
        model_id: sum(key.startswith(f"{model_id}::") for key in completed)
        for model_id in sorted(EXPECTED_MODELS)
    }
    result: dict[str, object] = {
        "prediction_files": [str(path) for path in files],
        "case_count": len(cases),
        "expected_prediction_count": len(expected_keys),
        "completed_prediction_count": len(completed),
        "model_counts": model_counts,
        "missing_count": len(missing),
        "unexpected_count": len(unexpected),
        "prompt_mismatch_count": len(prompt_mismatches),
        "ok": (
            len(cases) == 100
            and len(completed) == 300
            and not missing
            and not unexpected
            and not prompt_mismatches
            and all(count == 100 for count in model_counts.values())
        ),
    }
    if not result["ok"]:
        result.update(
            {
                "missing_examples": missing[:3],
                "unexpected_examples": unexpected[:3],
                "prompt_mismatch_examples": prompt_mismatches[:3],
            }
        )
    return result


def main() -> None:
    args = parse_args()
    repo_root, bundle_dir, prediction_roots, output_dir = paths()
    if not (repo_root / "backend" / "app").exists():
        raise FileNotFoundError(f"Cannot locate repository root: {repo_root}")
    if not (bundle_dir / "bundle_manifest.json").exists():
        raise FileNotFoundError(bundle_dir)
    for path in prediction_roots:
        if not path.exists():
            raise FileNotFoundError(path)

    kit_root = Path(__file__).resolve().parent
    sys.path.insert(0, str(kit_root))
    preflight = run_preflight(bundle_dir, prediction_roots, output_dir)
    print("PREFLIGHT")
    print(json.dumps(preflight, ensure_ascii=False, indent=2))
    if not preflight["ok"]:
        raise RuntimeError("Model-only judge preflight failed; Gemini API was not called")
    if args.preflight_only:
        return

    print(
        "Preflight đạt 300/300. Đang nạp backend và Gemini judge; lần đầu có thể mất 30–60 giây. "
        "Đừng bấm Ctrl+C. Log tiến độ sẽ hiện sau mỗi 10 câu.",
        flush=True,
    )
    from local_tools.run_judge import run_gemini_judge

    print("Bắt đầu Gemini judge 300 câu trả lời...", flush=True)
    report = run_gemini_judge(
        {
            "repo_root": str(repo_root),
            "bundle_dir": str(bundle_dir),
            "prediction_roots": [str(path) for path in prediction_roots],
            "suites": [SUITE],
            "selected_config_keys": [CONFIG_KEY],
            "expected_model_ids": sorted(EXPECTED_MODELS),
            "judge_model": "gemini-3.1-flash-lite-preview",
            "initial_key_offset": args.initial_key_offset,
            "minimum_key_count": args.minimum_key_count,
            "retry_attempts": 3,
            "retry_base_seconds": 2.0,
            "retry_failed": True,
            "allow_incomplete": False,
            "shard_name": "model-only-3models",
            "output_dir": str(output_dir),
        }
    )
    if report["expected_prediction_count"] != 300:
        raise RuntimeError(f"Expected 300 judge pairs: {report}")
    if report["judged_completed_count"] != 300 or not report["is_complete"]:
        raise RuntimeError(f"Model-only judging is incomplete: {report}")
    print("\nPASS")
    print(
        json.dumps(
            {
                "judged_completed_count": report["judged_completed_count"],
                "judged_failed_count": report["judged_failed_count"],
                "config_result_count": len(report["config_results"]),
                "archive_path": report["archive_path"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
