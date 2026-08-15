"""Create paired analysis artifacts for the isolated Phase 52 reranker top-k sweep."""

from __future__ import annotations

import argparse
import json
import math
import random
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = ROOT / "benchmark" / "tuvi_golden_dataset" / "reports_final" / "52_reranker_top_k_sweep"
METRICS = ("faithfulness", "answer_relevancy", "context_recall", "citation_coverage")
CONFIGS = {
    "k10": "semantic_gs_rrf_rerank_k10_control",
    "k20": "semantic_gs_rrf_rerank_k20",
    "k40": "semantic_gs_rrf_rerank_k40",
    "no_rerank": "semantic_gs_rrf_no_rerank_reference",
}


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower, upper = math.floor(position), math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def bootstrap_ci(values: list[float], *, seed: int) -> list[float] | None:
    if not values:
        return None
    rng = random.Random(seed)
    count = len(values)
    means = [sum(rng.choice(values) for _ in range(count)) / count for _ in range(5_000)]
    return [round(percentile(means, 0.025), 6), round(percentile(means, 0.975), 6)]


def paired(configs: dict[str, dict[str, Any]], left: str, right: str, label: str, *, seed: int) -> dict[str, Any]:
    left_items = {item.get("item_id"): item for item in configs[left].get("items") or []}
    right_items = {item.get("item_id"): item for item in configs[right].get("items") or []}
    shared_ids = sorted(set(left_items) & set(right_items))
    metrics: dict[str, Any] = {}
    for metric in METRICS:
        values: list[float] = []
        better = same = worse = 0
        for item_id in shared_ids:
            before, after = left_items[item_id].get(metric), right_items[item_id].get(metric)
            if not isinstance(before, (int, float)) or not isinstance(after, (int, float)):
                continue
            delta = float(after) - float(before)
            values.append(delta)
            if delta > 0:
                better += 1
            elif delta < 0:
                worse += 1
            else:
                same += 1
        metrics[metric] = {
            "n": len(values),
            "mean_delta_right_minus_left": round(sum(values) / len(values), 6) if values else None,
            "bootstrap_95_ci": bootstrap_ci(values, seed=seed),
            "right_better_count": better,
            "same_count": same,
            "right_worse_count": worse,
        }
    return {"label": label, "left_config": left, "right_config": right, "shared_item_count": len(shared_ids), "metrics": metrics}


def summary(config: dict[str, Any]) -> dict[str, Any]:
    metrics = config.get("metrics") or {}
    items = [item for item in config.get("items") or [] if not item.get("chart_only")]

    def mean_count(name: str) -> float:
        values = [float(((item.get("diagnostic_candidate_counts") or {}).get(name) or 0)) for item in items]
        return round(sum(values) / len(values), 4) if values else 0.0

    return {
        "config_name": config.get("config_name"),
        "reranker_enabled": config.get("reranker_enabled"),
        "faithfulness_avg": metrics.get("faithfulness_avg"),
        "answer_relevancy_avg": metrics.get("answer_relevancy_avg"),
        "context_recall_avg": metrics.get("context_recall_avg"),
        "citation_coverage_rate": metrics.get("citation_coverage_rate"),
        "graph_hit_rate": metrics.get("graph_hit_rate"),
        "retrieval_p95_ms": metrics.get("retrieval_p95_ms"),
        "p95_latency_ms": metrics.get("p95_latency_ms"),
        "mean_fused_candidates": mean_count("fused"),
        "mean_reranked_candidates": mean_count("reranked"),
        "mean_graded_candidates": mean_count("graded"),
        "mean_context_selected": mean_count("context_selected"),
    }


def fmt(value: Any) -> str:
    return "n/a" if value is None else f"{float(value):.3f}" if isinstance(value, (int, float)) else str(value)


def write_markdown(analysis: dict[str, Any], destination: Path) -> None:
    lines = [
        "# Phase 52 — Reranker Top-k Sweep",
        "",
        "This analysis is separate from the canonical W8 matrix and Phase 50 shortlist confirmation.",
        "",
        f"- Generated UTC: `{analysis['generated_at']}`",
        "- Pairwise deltas are `right - left`; positive values favor the right-hand configuration.",
        "- Bootstrap CIs use 5,000 seeded resamples and are descriptive.",
        "",
        "## Aggregate quality, latency, and candidate flow",
        "",
        "| Role | Config | Faith | Relevancy | Context recall | Citation | Retr p95 ms | Fused | Reranked | Graded | Context selected |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for role, row in analysis["configs"].items():
        lines.append(
            f"| {role} | {row['config_name']} | {fmt(row['faithfulness_avg'])} | {fmt(row['answer_relevancy_avg'])} | "
            f"{fmt(row['context_recall_avg'])} | {fmt(row['citation_coverage_rate'])} | {fmt(row['retrieval_p95_ms'])} | "
            f"{fmt(row['mean_fused_candidates'])} | {fmt(row['mean_reranked_candidates'])} | {fmt(row['mean_graded_candidates'])} | {fmt(row['mean_context_selected'])} |"
        )
    for comparison in analysis["paired_comparisons"]:
        lines += ["", f"## {comparison['label']}", "", f"`{comparison['right_config']}` minus `{comparison['left_config']}`; shared items: `{comparison['shared_item_count']}`.", "", "| Metric | N | Mean delta | Bootstrap 95% CI | Right better / same / worse |", "|---|---:|---:|---|---:|"]
        for metric, result in comparison["metrics"].items():
            ci = result["bootstrap_95_ci"]
            ci_text = "n/a" if ci is None else f"[{ci[0]:.3f}, {ci[1]:.3f}]"
            lines.append(f"| {metric} | {result['n']} | {fmt(result['mean_delta_right_minus_left'])} | {ci_text} | {result['right_better_count']} / {result['same_count']} / {result['right_worse_count']} |")
    destination.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    output_dir = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    report_path = output_dir / "evaluation_report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    execution = report.get("execution_summary") or {}
    if report.get("status") != "completed" or report.get("judge_backend") != "gemini" or execution.get("completed_pair_count") != 400 or execution.get("failed_pair_count") != 0:
        raise ValueError("Phase 52 report must be a completed 400-pair Gemini run with zero failures.")
    rows = {row.get("config_name"): row for row in report.get("configs") or []}
    missing = [name for name in CONFIGS.values() if name not in rows]
    if missing:
        raise ValueError(f"Missing configs: {missing}")
    named = {role: summary(rows[name]) for role, name in CONFIGS.items()}
    analysis = {
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "report_path": report_path.relative_to(ROOT).as_posix(),
        "execution_summary": execution,
        "configs": named,
        "paired_comparisons": [
            paired(rows, CONFIGS["k10"], CONFIGS["k20"], "Top-k 20 vs top-k 10", seed=52_020),
            paired(rows, CONFIGS["k10"], CONFIGS["k40"], "Top-k 40 vs top-k 10", seed=52_040),
            paired(rows, CONFIGS["no_rerank"], CONFIGS["k20"], "Top-k 20 vs no-rerank reference", seed=52_120),
            paired(rows, CONFIGS["no_rerank"], CONFIGS["k40"], "Top-k 40 vs no-rerank reference", seed=52_140),
        ],
    }
    (output_dir / "top_k_sweep_comparison.json").write_text(json.dumps(analysis, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(analysis, output_dir / "top_k_sweep_comparison.md")
    print(json.dumps({"output_dir": str(output_dir), "comparisons": 4}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())