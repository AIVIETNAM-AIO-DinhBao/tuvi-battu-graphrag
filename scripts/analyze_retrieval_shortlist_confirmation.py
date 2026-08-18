"""Create a paired analysis for the isolated W8 retrieval shortlist confirmation.

The script reads a completed Phase 50 evaluation report and writes only derived
JSON/Markdown artifacts next to that report.  It never edits the canonical W8
matrix or the final ablation report.
"""

from __future__ import annotations

import argparse
import json
import math
import random
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REPORT = ROOT / "benchmark" / "tuvi_golden_dataset" / "reports_final" / "50_retrieval_shortlist_confirmation" / "evaluation_report.json"
DEFAULT_OUTPUT_DIR = DEFAULT_REPORT.parent
METRICS = ("faithfulness", "answer_relevancy", "context_recall", "citation_coverage")
CONFIGS = {
    "control": "semantic_gs_rrf_rerank_on_control",
    "rerank_off": "semantic_gs_rrf_rerank_off_candidate",
    "quality": "semantic_gd_rrf_rerank_on_quality",
}


def percentile(values: list[float], fraction: float) -> float:
    if not values:
        raise ValueError("cannot calculate percentile of an empty list")
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def bootstrap_mean_ci(values: list[float], *, samples: int = 5_000, seed: int = 20260812) -> list[float] | None:
    if not values:
        return None
    rng = random.Random(seed)
    count = len(values)
    means = [sum(rng.choice(values) for _ in range(count)) / count for _ in range(samples)]
    return [round(percentile(means, 0.025), 6), round(percentile(means, 0.975), 6)]


def load_report(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing evaluation report: {path}")
    report = json.loads(path.read_text(encoding="utf-8"))
    if report.get("status") != "completed":
        raise ValueError(f"Report must be completed, got {report.get('status')!r}")
    if report.get("judge_backend") != "gemini":
        raise ValueError(f"Report must use Gemini judging, got {report.get('judge_backend')!r}")
    if report.get("dataset_item_count") != 100:
        raise ValueError(f"Expected 100 dataset items, got {report.get('dataset_item_count')!r}")
    if (report.get("execution_summary") or {}).get("failed_pair_count") != 0:
        raise ValueError("Report has failed pairs")
    return report


def paired_comparison(
    configs: dict[str, dict[str, Any]],
    *,
    left_key: str,
    right_key: str,
    label: str,
) -> dict[str, Any]:
    left = configs[left_key]
    right = configs[right_key]
    left_items = {item.get("item_id"): item for item in left.get("items") or []}
    right_items = {item.get("item_id"): item for item in right.get("items") or []}
    shared_ids = sorted(set(left_items) & set(right_items))
    results: dict[str, Any] = {}
    for metric in METRICS:
        deltas: list[float] = []
        better = same = worse = 0
        for item_id in shared_ids:
            left_value = left_items[item_id].get(metric)
            right_value = right_items[item_id].get(metric)
            if not isinstance(left_value, (int, float)) or not isinstance(right_value, (int, float)):
                continue
            delta = float(right_value) - float(left_value)
            deltas.append(delta)
            if delta > 0:
                better += 1
            elif delta < 0:
                worse += 1
            else:
                same += 1
        results[metric] = {
            "n": len(deltas),
            "mean_delta_right_minus_left": round(sum(deltas) / len(deltas), 6) if deltas else None,
            "bootstrap_95_ci": bootstrap_mean_ci(deltas),
            "right_better_count": better,
            "same_count": same,
            "right_worse_count": worse,
        }
    return {
        "label": label,
        "left_config": left.get("config_name"),
        "right_config": right.get("config_name"),
        "shared_item_count": len(shared_ids),
        "metrics": results,
    }


def compact_config(config: dict[str, Any]) -> dict[str, Any]:
    metrics = config.get("metrics") or {}
    return {
        "config_name": config.get("config_name"),
        "reranker_enabled": config.get("reranker_enabled"),
        "graph_retrieval_enabled": config.get("graph_retrieval_enabled"),
        "dense_retrieval_enabled": config.get("dense_retrieval_enabled"),
        "sparse_retrieval_enabled": config.get("sparse_retrieval_enabled"),
        "fusion_method": config.get("fusion_method"),
        "faithfulness_avg": metrics.get("faithfulness_avg"),
        "answer_relevancy_avg": metrics.get("answer_relevancy_avg"),
        "context_recall_avg": metrics.get("context_recall_avg"),
        "citation_coverage_rate": metrics.get("citation_coverage_rate"),
        "graph_hit_rate": metrics.get("graph_hit_rate"),
        "p95_latency_ms": metrics.get("p95_latency_ms"),
        "retrieval_p95_ms": metrics.get("retrieval_p95_ms"),
        "generation_p95_ms": metrics.get("generation_p95_ms"),
    }


def write_markdown(analysis: dict[str, Any], path: Path) -> None:
    configs = analysis["configs"]
    lines = [
        "# W8 Retrieval Shortlist Confirmation",
        "",
        "This is a Phase 50 isolated confirmation run. It is separate from the canonical W8 matrix and does not replace its artifacts.",
        "",
        f"- Generated UTC: `{analysis['generated_at']}`",
        f"- Dataset items: `{analysis['dataset_item_count']}`",
        f"- Judge backend: `{analysis['judge_backend']}`",
        "- Pairwise deltas are `right - left`; positive values favor the right-hand configuration.",
        "- Bootstrap CIs use 5,000 seeded resamples and are descriptive, not a replacement for a preregistered significance test.",
        "",
        "## Aggregate metrics",
        "",
        "| Config | Faith | Relevancy | Context recall | Citation | Graph hit | RAG p95 ms | Retrieval p95 ms |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for config in configs.values():
        lines.append(
            "| {config_name} | {faithfulness_avg:.3f} | {answer_relevancy_avg:.3f} | {context_recall_avg:.3f} | "
            "{citation_coverage_rate:.3f} | {graph_hit_rate:.3f} | {p95_latency_ms:.1f} | {retrieval_p95_ms:.1f} |".format(
                **{key: 0.0 if value is None else value for key, value in config.items()}
            )
        )
    for comparison in analysis["paired_comparisons"]:
        lines.extend(
            [
                "",
                f"## {comparison['label']}",
                "",
                f"`{comparison['right_config']}` minus `{comparison['left_config']}`; shared items: `{comparison['shared_item_count']}`.",
                "",
                "| Metric | N | Mean delta | Bootstrap 95% CI | Right better / same / worse |",
                "|---|---:|---:|---|---:|",
            ]
        )
        for metric, result in comparison["metrics"].items():
            ci = result["bootstrap_95_ci"]
            ci_text = "n/a" if ci is None else f"[{ci[0]:.3f}, {ci[1]:.3f}]"
            delta = result["mean_delta_right_minus_left"]
            delta_text = "n/a" if delta is None else f"{delta:.3f}"
            lines.append(
                f"| {metric} | {result['n']} | {delta_text} | {ci_text} | "
                f"{result['right_better_count']} / {result['same_count']} / {result['right_worse_count']} |"
            )
    lines.extend(
        [
            "",
            "## Decision rule",
            "",
            "Promote reranker-off only if it is non-inferior on the three quality metrics versus the matched Graph+Sparse control and its operational latency is acceptable. Promote Graph+Dense only if its quality gain over reranker-off justifies the measured latency/cost trade-off in this same-machine run.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    report_path = args.report if args.report.is_absolute() else ROOT / args.report
    output_dir = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    report = load_report(report_path)
    by_name = {config.get("config_name"): config for config in report.get("configs") or []}
    missing = [name for name in CONFIGS.values() if name not in by_name]
    if missing:
        raise ValueError(f"Missing shortlist configs: {missing}")
    configs = {key: compact_config(by_name[name]) for key, name in CONFIGS.items()}
    analysis = {
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "report_path": str(report_path.relative_to(ROOT)).replace("\\", "/"),
        "dataset_item_count": report.get("dataset_item_count"),
        "judge_backend": report.get("judge_backend"),
        "execution_summary": report.get("execution_summary"),
        "configs": configs,
        "paired_comparisons": [
            paired_comparison(configs=by_name, left_key=CONFIGS["control"], right_key=CONFIGS["rerank_off"], label="Reranker on vs off: matched Graph + Sparse + RRF"),
            paired_comparison(configs=by_name, left_key=CONFIGS["rerank_off"], right_key=CONFIGS["quality"], label="Production candidate vs quality challenger: Graph + Sparse no-rerank vs Graph + Dense rerank"),
        ],
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "shortlist_comparison.json").write_text(json.dumps(analysis, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(analysis, output_dir / "shortlist_comparison.md")
    print(json.dumps({"output_dir": str(output_dir), "comparisons": len(analysis["paired_comparisons"])}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())