"""Prepare a one-config P6 bundle plan and preconfigured official Kaggle notebooks."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
KIT_ROOT = ROOT_DIR / "benchmark" / "tuvi_golden_dataset" / "local_llm_ablation"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.rag.ablation import load_ablation_manifest  # noqa: E402


MODELS = {
    "qwen25_7b": {
        "model_id": "Qwen/Qwen2.5-7B-Instruct",
        "loader": "causal_lm",
        "gated": False,
        "default_quantization": "4bit",
    },
    "gemma3_4b": {
        "model_id": "google/gemma-3-4b-it",
        "loader": "gemma3_conditional",
        "gated": True,
        "default_quantization": "4bit",
    },
}


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT_DIR / path


def repo_relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT_DIR).as_posix()


def notebook_config(model_key: str, config_key: str) -> list[str]:
    model_id = MODELS[model_key]["model_id"]
    return [
        "# ===== FROZEN BY scripts/prepare_p6_kaggle.py =====\n",
        "RUNNER = 'S'\n",
        f"MODEL_KEY = {model_key!r}\n",
        "RUN_MODE = 'official'\n",
        "\n",
        "RUNNER_CONFIGS = {\n",
        f"    'S': {{'suite': 'sequential_final_1', 'config_key': {config_key!r}}},\n",
        "}\n",
        "MODEL_REGISTRY = {\n",
        f"    {model_key!r}: {model_id!r},\n",
        "}\n",
        "\n",
        "BUNDLE_INPUT = None\n",
        "MODEL_ASSET_DIR = None\n",
        "\n",
        "assert RUNNER in RUNNER_CONFIGS\n",
        "assert MODEL_KEY in MODEL_REGISTRY\n",
        "assert RUN_MODE == 'official'\n",
        "RUN_SPEC = RUNNER_CONFIGS[RUNNER]\n",
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare P6 context plan and official Kaggle notebooks.")
    parser.add_argument("--manifest", type=Path, required=True, help="One-config p6_frozen_context manifest.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("benchmark/tuvi_golden_dataset/sequential_ablation/p6_kaggle"),
    )
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest_path = resolve(args.manifest).resolve()
    output_dir = resolve(args.output_dir).resolve()
    manifest = load_ablation_manifest(manifest_path)
    if len(manifest.configs) != 1:
        raise SystemExit("P6 frozen-context manifest must contain exactly one config.")
    config_name = manifest.configs[0].name
    config_key = f"sequential_final_1::{config_name}"
    if output_dir.exists() and any(output_dir.iterdir()) and not args.force:
        raise SystemExit(f"Refusing to overwrite non-empty {output_dir}; use --force after audit.")
    output_dir.mkdir(parents=True, exist_ok=True)
    plan = {
        "schema_version": "local-llm-ablation-plan-v2",
        "study_id": "sequential_final_generator_ablation",
        "default_suites": ["sequential_final_1"],
        "models": MODELS,
        "suites": {
            "sequential_final_1": {
                "description": "One locked retrieval/context configuration shared by all P6 generators.",
                "selection_rationale": "P1-P5 winner; only generation model changes in P6.",
                "manifest_selections": [
                    {"path": repo_relative(manifest_path), "include_configs": [config_name]}
                ],
                "expected_config_count": 1,
                "expected_item_count": 100,
                "expected_retrieval_pair_count": 100,
            }
        },
        "official_matrix": {
            "retrieval_pair_count": 100,
            "generation_model_count": 3,
            "generation_pair_count": 300,
            "gemini_judge_pair_count": 300,
        },
        "team": {
            "A": ["build frozen bundle locally", "run Gemini API candidate", "run Qwen Kaggle", "judge/merge"],
            "B": ["run the preconfigured Gemma Kaggle notebook", "return prediction ZIP"],
        },
    }
    (output_dir / "experiment_plan.json").write_text(
        json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    template = json.loads((KIT_ROOT / "notebooks" / "02_generate_offline_kaggle.ipynb").read_text(encoding="utf-8"))
    for model_key in MODELS:
        notebook = copy.deepcopy(template)
        notebook["cells"][1]["source"] = notebook_config(model_key, config_key)
        target = output_dir / f"P6_{model_key}_official_kaggle.ipynb"
        target.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    handoff = {
        "suite": "sequential_final_1",
        "config_name": config_name,
        "config_key": config_key,
        "manifest": repo_relative(manifest_path),
        "notebooks": {
            "A": "P6_qwen25_7b_official_kaggle.ipynb",
            "B": "P6_gemma3_4b_official_kaggle.ipynb",
        },
    }
    (output_dir / "handoff.json").write_text(
        json.dumps(handoff, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(handoff, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
