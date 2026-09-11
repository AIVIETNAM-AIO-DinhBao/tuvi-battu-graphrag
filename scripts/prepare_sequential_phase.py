"""Generate the next one-factor manifest from the previous locked config."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml


ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.rag.config import load_experiment_config  # noqa: E402


DATASET = "benchmark/tuvi_golden_dataset/release/tuviqa_v1_release.jsonl"
TWO_PERSON_ASSIGNMENTS = {
    "p2": {
        "A": {"p2_graph", "p2_dense", "p2_graph_dense"},
        "B": {"p2_sparse", "p2_graph_sparse", "p2_dense_sparse", "p2_graph_dense_sparse"},
    },
    "p3": {
        "A": {"p3_v1", "p3_structured_v3"},
        "B": {"p3_grounded_v2", "p3_answer_first_v4"},
    },
    "p4": {"A": {"p4_rerank_off"}, "B": {"p4_rerank_on"}},
    "p5": {"A": {"p5_top_k_10"}, "B": {"p5_top_k_20", "p5_top_k_40"}},
}


def repo_relative(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT_DIR).as_posix()
    except ValueError:
        return resolved.as_posix()


def candidate(name: str, base: str, experiment_id: str, label: str, overrides: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": name,
        "base_config_path": base,
        "overrides": {"experiment_id": experiment_id, "name": label, **overrides},
    }


def phase_specs(phase: str, base: str) -> tuple[str, str, list[dict[str, Any]]]:
    if phase == "p2":
        variants = [
            ("graph", True, False, False),
            ("sparse", False, False, True),
            ("dense", False, True, False),
            ("graph_sparse", True, False, True),
            ("graph_dense", True, True, False),
            ("dense_sparse", False, True, True),
            ("graph_dense_sparse", True, True, True),
        ]
        specs = [
            candidate(
                f"p2_{name}",
                base,
                f"sequential_p2_{name}",
                f"Sequential P2 - {name.replace('_', '+')}",
                {
                    "graph_retrieval_enabled": graph,
                    "dense_retrieval_enabled": dense,
                    "sparse_retrieval_enabled": sparse,
                },
            )
            for name, graph, dense, sparse in variants
        ]
        return "sequential_p2_retrieval", "Only the categorical retrieval strategy changes.", specs
    if phase == "p3":
        prompts = [
            ("v1", "tuvi_generation_v1"),
            ("grounded_v2", "tuvi_generation_grounded_v2"),
            ("structured_v3", "tuvi_generation_structured_v3"),
            ("answer_first_v4", "tuvi_generation_answer_first_v4"),
        ]
        specs = [
            candidate(
                f"p3_{name}",
                base,
                f"sequential_p3_{name}",
                f"Sequential P3 - {name}",
                {"prompt_template_id": prompt_id},
            )
            for name, prompt_id in prompts
        ]
        return "sequential_p3_prompt", "Only prompt_template_id changes; run with Gemini generation and judge.", specs
    if phase == "p4":
        specs = [
            candidate(
                "p4_rerank_off",
                base,
                "sequential_p4_rerank_off",
                "Sequential P4 - reranker off",
                {"reranker_config": {"enabled": False, "top_k": 20}},
            ),
            candidate(
                "p4_rerank_on",
                base,
                "sequential_p4_rerank_on",
                "Sequential P4 - reranker on",
                {"reranker_config": {"enabled": True, "top_k": 20}},
            ),
        ]
        return "sequential_p4_reranker", "Only reranker.enabled changes; top_k is fixed at 20.", specs
    if phase == "p5":
        specs = [
            candidate(
                f"p5_top_k_{top_k}",
                base,
                f"sequential_p5_top_k_{top_k}",
                f"Sequential P5 - reranker top-k {top_k}",
                {"reranker_config": {"top_k": top_k}},
            )
            for top_k in (10, 20, 40)
        ]
        return "sequential_p5_reranker_depth", "Only reranker.top_k changes; base must have reranker enabled.", specs
    if phase == "p6-context":
        specs = [
            candidate(
                "p6_frozen_context",
                base,
                "sequential_p6_frozen_context",
                "Sequential P6 - frozen final retrieval context",
                {},
            )
        ]
        return "sequential_p6_frozen_context", "One locked retrieval config used to build the model-neutral P6 bundle.", specs
    raise ValueError(f"Unsupported phase: {phase}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare a sequential one-factor ablation manifest.")
    parser.add_argument("--phase", choices=["p2", "p3", "p4", "p5", "p6-context"], required=True)
    parser.add_argument("--base", type=Path, required=True, help="Locked config from the previous phase.")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--output-dir", type=str, required=True, help="Repo-relative result directory written into manifest.")
    parser.add_argument("--two-person-shard-dir", type=Path, default=None)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    base_path = args.base if args.base.is_absolute() else ROOT_DIR / args.base
    output_path = args.output if args.output.is_absolute() else ROOT_DIR / args.output
    if output_path.exists() and not args.force:
        raise SystemExit(f"Refusing to overwrite {output_path}; pass --force only after auditing the existing file.")
    base_config = load_experiment_config(base_path)
    if args.phase in {"p2", "p3", "p4"} and base_config.reranker_enabled:
        raise SystemExit(f"{args.phase} requires a reranker-off locked base.")
    if args.phase == "p5" and not base_config.reranker_enabled:
        raise SystemExit("p5 is valid only when P4 locked reranker on.")
    name, notes, specs = phase_specs(args.phase, repo_relative(base_path))
    payload = {
        "name": name,
        "notes": notes,
        "dataset_path": DATASET,
        "output_dir": args.output_dir,
        "configs": specs,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(yaml.safe_dump(payload, allow_unicode=True, sort_keys=False), encoding="utf-8", newline="\n")
    print(output_path)
    print(f"phase={args.phase} configs={len(specs)} base={repo_relative(base_path)}")
    if args.two_person_shard_dir is not None:
        if args.phase not in TWO_PERSON_ASSIGNMENTS:
            raise SystemExit(f"Two-person shards are not defined for {args.phase}.")
        shard_dir = args.two_person_shard_dir if args.two_person_shard_dir.is_absolute() else ROOT_DIR / args.two_person_shard_dir
        shard_dir.mkdir(parents=True, exist_ok=True)
        for member, selected_names in TWO_PERSON_ASSIGNMENTS[args.phase].items():
            selected = [spec for spec in specs if spec["name"] in selected_names]
            if {spec["name"] for spec in selected} != selected_names:
                raise RuntimeError(f"Invalid {args.phase} shard assignment for {member}.")
            shard_payload = {
                **payload,
                "name": f"{name}_shard_{member.lower()}",
                "notes": f"{notes} Two-person official shard assigned to {member}.",
                "output_dir": f"{args.output_dir.rstrip('/')}/shards/{member}",
                "configs": selected,
            }
            shard_path = shard_dir / f"{args.phase}_shard_{member.lower()}.yaml"
            shard_path.write_text(
                yaml.safe_dump(shard_payload, allow_unicode=True, sort_keys=False), encoding="utf-8", newline="\n"
            )
            print(f"shard {member}: {shard_path} configs={len(selected)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
