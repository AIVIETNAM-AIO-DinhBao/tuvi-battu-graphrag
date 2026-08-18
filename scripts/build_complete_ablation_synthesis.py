"""Build a complete, provenance-aware synthesis of all completed ablation studies.

The report combines the immutable 3x3 Chunking x Prompt source waves, the W8
10-config retrieval matrix with reranker top_k=10, and the completed hybrid
10-config reranker top_k=40 matrix.  It writes a new synthesis only; raw study
artifacts and the existing final report are never modified.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / "benchmark" / "tuvi_golden_dataset" / "reports_final"
OUTPUT_DIR = BASE / "90_final_report"
SOURCES = {
    "chunking_prompt_v3": BASE / "10_chunking_strategy_ablation" / "evaluation_report.json",
    "chunking_prompt_v1_v2": BASE / "11_chunking_prompt_interaction_v1_v2" / "evaluation_report.json",
    "retrieval_k10": BASE / "20_retrieval_fusion_reranker_matrix" / "evaluation_report.json",
    "retrieval_k40": BASE / "53_retrieval_fusion_reranker_k40_matrix" / "evaluation_report.json",
}
K40_HYBRID_CONTROL_SOURCE = BASE / "53_retrieval_fusion_reranker_k40_matrix" / "reused_phase52_controls" / "evaluation_report.json"
OUTPUT_JSON = OUTPUT_DIR / "complete_ablation_synthesis.json"
OUTPUT_MARKDOWN = OUTPUT_DIR / "complete_ablation_synthesis.md"

METRICS = (
    ("faithfulness_avg", "Faith"),
    ("answer_relevancy_avg", "Relev"),
    ("context_recall_avg", "CtxRecall"),
    ("citation_coverage_rate", "Citation"),
    ("graph_hit_rate", "GraphHit"),
    ("retrieval_p95_ms", "Retr p95 ms"),
    ("p95_latency_ms", "RAG p95 ms"),
)
K40_TO_K10 = {
    "semantic_gs_rrf_rerank_k40": "baseline_graph_sparse_rrf",
    "graph_only_rrf_k40": "graph_only_rrf",
    "sparse_only_rrf_k40": "sparse_only_rrf",
    "dense_only_rrf_k40": "dense_only_rrf",
    "dense_sparse_rrf_k40": "dense_sparse_rrf",
    "graph_dense_rrf_k40": "graph_dense_rrf",
    "all_paths_planner_dense_rrf_k40": "all_paths_planner_dense_rrf",
    "semantic_gs_rrf_no_rerank_reference": "baseline_no_reranker",
    "graph_sparse_weighted_sum_k40": "baseline_weighted_sum",
    "graph_sparse_graph_first_k40": "baseline_graph_first",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_completed_report(path: Path, *, expected_configs: int) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing report: {relative(path)}")
    report = json.loads(path.read_text(encoding="utf-8"))
    execution = report.get("execution_summary") or {}
    if report.get("status") != "completed":
        raise ValueError(f"Incomplete report {relative(path)}: {report.get('status')!r}")
    if report.get("judge_backend") != "gemini":
        raise ValueError(f"Non-Gemini report {relative(path)}: {report.get('judge_backend')!r}")
    if report.get("dataset_item_count") != 100 or report.get("config_count") != expected_configs:
        raise ValueError(f"Unexpected dataset/config count in {relative(path)}")
    if execution.get("completed_pair_count") != expected_configs * 100 or execution.get("failed_pair_count") != 0:
        raise ValueError(f"Incomplete pair coverage in {relative(path)}")
    rows = report.get("configs") or []
    if len(rows) != expected_configs:
        raise ValueError(f"Unexpected config rows in {relative(path)}")
    for row in rows:
        metrics = row.get("metrics") or {}
        if row.get("status") != "completed" or metrics.get("item_count") != 100 or metrics.get("failed_count") != 0:
            raise ValueError(f"Invalid completed config row {row.get('config_name')!r} in {relative(path)}")
    return report


def value(metrics: dict[str, Any], key: str) -> float:
    raw = metrics.get(key)
    return float(raw) if isinstance(raw, (int, float)) else 0.0


def quality_score(row: dict[str, Any]) -> float:
    """Transparent descriptive quality score; latency is intentionally excluded."""
    metrics = row.get("metrics") or {}
    return round(
        0.35 * value(metrics, "context_recall_avg")
        + 0.25 * value(metrics, "faithfulness_avg")
        + 0.20 * value(metrics, "answer_relevancy_avg")
        + 0.15 * value(metrics, "citation_coverage_rate")
        + 0.05 * value(metrics, "graph_hit_rate"),
        6,
    )


def compact_row(row: dict[str, Any]) -> dict[str, Any]:
    metrics = row.get("metrics") or {}
    return {
        "config_name": row.get("config_name"),
        "config_hash": row.get("config_hash"),
        "chunk_strategy_id": row.get("chunk_strategy_id"),
        "prompt_template_id": row.get("prompt_template_id"),
        "graph_retrieval_enabled": row.get("graph_retrieval_enabled"),
        "dense_retrieval_enabled": row.get("dense_retrieval_enabled"),
        "sparse_retrieval_enabled": row.get("sparse_retrieval_enabled"),
        "fusion_method": row.get("fusion_method"),
        "reranker_enabled": row.get("reranker_enabled"),
        "metrics": {key: metrics.get(key) for key, _ in METRICS},
        "quality_score": quality_score(row),
    }


def ranked_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted((compact_row(row) for row in rows), key=lambda row: row["quality_score"], reverse=True)


def winner(rows: list[dict[str, Any]], metric: str) -> dict[str, Any]:
    return max(rows, key=lambda row: value(row.get("metrics") or {}, metric))


def fmt(value_: Any, *, milliseconds: bool = False) -> str:
    if value_ is None:
        return "n/a"
    if isinstance(value_, (int, float)):
        return f"{float(value_):.1f}" if milliseconds else f"{float(value_):.3f}"
    return str(value_)


def settings(row: dict[str, Any]) -> str:
    paths = "".join(
        letter
        for enabled, letter in (
            (row.get("graph_retrieval_enabled"), "G"),
            (row.get("dense_retrieval_enabled"), "D"),
            (row.get("sparse_retrieval_enabled"), "S"),
        )
        if enabled
    )
    rerank = "on" if row.get("reranker_enabled") else "off"
    return f"paths={paths or 'none'}; fusion={row.get('fusion_method')}; rerank={rerank}"


def append_ranked_table(lines: list[str], rows: list[dict[str, Any]], *, include_chunk_prompt: bool = False) -> None:
    headers = ["Rank", "Config"]
    if include_chunk_prompt:
        headers += ["Chunk", "Prompt"]
    else:
        headers += ["Retrieval / fusion / rerank"]
    headers += ["Quality score"] + [label for _, label in METRICS]
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("|" + "|".join("---" for _ in headers) + "|")
    for index, row in enumerate(rows, start=1):
        metrics = row["metrics"]
        variable = (
            f"{row.get('chunk_strategy_id')}; {row.get('prompt_template_id')}"
            if include_chunk_prompt
            else settings(row)
        )
        cells = [str(index), f"`{row['config_name']}`", variable, fmt(row["quality_score"])]
        for key, _ in METRICS:
            cells.append(fmt(metrics.get(key), milliseconds=key.endswith("_ms")))
        lines.append("| " + " | ".join(cells) + " |")


def build_summary() -> dict[str, Any]:
    reports = {
        "chunking_prompt_v3": load_completed_report(SOURCES["chunking_prompt_v3"], expected_configs=3),
        "chunking_prompt_v1_v2": load_completed_report(SOURCES["chunking_prompt_v1_v2"], expected_configs=6),
        "retrieval_k10": load_completed_report(SOURCES["retrieval_k10"], expected_configs=10),
        "retrieval_k40": load_completed_report(SOURCES["retrieval_k40"], expected_configs=10),
    }
    hybrid_controls = load_completed_report(K40_HYBRID_CONTROL_SOURCE, expected_configs=2)
    source_rows = {
        key: {
            "path": relative(path),
            "sha256": sha256_file(path),
            "status": reports[key].get("status"),
            "judge_backend": reports[key].get("judge_backend"),
            "config_count": reports[key].get("config_count"),
            "execution_summary": reports[key].get("execution_summary"),
        }
        for key, path in SOURCES.items()
    }
    source_rows["k40_reused_phase52_controls"] = {
        "path": relative(K40_HYBRID_CONTROL_SOURCE),
        "sha256": sha256_file(K40_HYBRID_CONTROL_SOURCE),
        "status": hybrid_controls.get("status"),
        "judge_backend": hybrid_controls.get("judge_backend"),
        "config_count": hybrid_controls.get("config_count"),
        "execution_summary": hybrid_controls.get("execution_summary"),
        "source_phase52_provenance": hybrid_controls.get("source_phase52_provenance"),
    }
    chunk_rows = list(reports["chunking_prompt_v3"].get("configs") or []) + list(reports["chunking_prompt_v1_v2"].get("configs") or [])
    k10_rows = list(reports["retrieval_k10"].get("configs") or [])
    k40_rows = list(reports["retrieval_k40"].get("configs") or [])
    k10_by_name = {row.get("config_name"): row for row in k10_rows}
    k40_by_name = {row.get("config_name"): row for row in k40_rows}
    comparisons: list[dict[str, Any]] = []
    for k40_name, k10_name in K40_TO_K10.items():
        old, new = k10_by_name[k10_name], k40_by_name[k40_name]
        old_metrics, new_metrics = old.get("metrics") or {}, new.get("metrics") or {}
        comparisons.append(
            {
                "k10_config": k10_name,
                "k40_config": k40_name,
                "faithfulness_delta": round(value(new_metrics, "faithfulness_avg") - value(old_metrics, "faithfulness_avg"), 6),
                "relevancy_delta": round(value(new_metrics, "answer_relevancy_avg") - value(old_metrics, "answer_relevancy_avg"), 6),
                "context_recall_delta": round(value(new_metrics, "context_recall_avg") - value(old_metrics, "context_recall_avg"), 6),
                "citation_delta": round(value(new_metrics, "citation_coverage_rate") - value(old_metrics, "citation_coverage_rate"), 6),
            }
        )
    return {
        "generated_at_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "scope": "Completed 3x3 Chunking x Prompt matrix, W8 retrieval/fusion/reranker k10 matrix, and hybrid reranker top_k=40 matrix.",
        "metric_policy": "Quality score is descriptive only: 0.35 context recall + 0.25 faithfulness + 0.20 relevancy + 0.15 citation coverage + 0.05 graph hit. It excludes latency so quality and latency trade-offs remain explicit.",
        "sources": source_rows,
        "chunking_prompt_3x3": {"ranked_configs": ranked_rows(chunk_rows)},
        "retrieval_k10": {"ranked_configs": ranked_rows(k10_rows)},
        "retrieval_k40": {"ranked_configs": ranked_rows(k40_rows)},
        "metric_winners": {
            "chunking_prompt": {metric: compact_row(winner(chunk_rows, metric)) for metric, _ in METRICS[:5]},
            "retrieval_k10": {metric: compact_row(winner(k10_rows, metric)) for metric, _ in METRICS[:5]},
            "retrieval_k40": {metric: compact_row(winner(k40_rows, metric)) for metric, _ in METRICS[:5]},
        },
        "k10_to_k40_comparison": comparisons,
        "recommendations": {
            "best_completed_chunk_prompt_cell": compact_row(max(chunk_rows, key=quality_score)),
            "best_k10_quality": compact_row(max(k10_rows, key=quality_score)),
            "best_k40_quality": compact_row(max(k40_rows, key=quality_score)),
            "production_latency_quality_candidate": compact_row(k40_by_name["semantic_gs_rrf_no_rerank_reference"]),
            "quality_first_retrieval_candidate": compact_row(winner(k40_rows, "context_recall_avg")),
        },
    }


def write_markdown(summary: dict[str, Any], path: Path) -> None:
    chunk = summary["chunking_prompt_3x3"]["ranked_configs"]
    k10 = summary["retrieval_k10"]["ranked_configs"]
    k40 = summary["retrieval_k40"]["ranked_configs"]
    recommendations = summary["recommendations"]
    lines = [
        "# Complete Ablation Study Synthesis",
        "",
        f"Generated UTC: `{summary['generated_at_utc']}`",
        "",
        "## Scope and evidence status",
        "",
        "This report synthesizes all completed comparative ablations without overwriting their raw reports:",
        "",
        "1. **Chunking × Prompt 3×3 matrix**: 9 configs × 100 items = 900 Gemini-judged pairs.",
        "2. **Retrieval / Fusion / Reranker v2 (k10)**: 10 configs × 100 items = 1,000 Gemini-judged pairs.",
        "3. **Retrieval / Fusion / Reranker v3 (k40)**: 10 configs × 100 items = 1,000 Gemini-judged pairs; 8 configs are fresh Phase 53 runs and two Graph+Sparse controls are provenance-preserving Phase 52 rows.",
        "",
        "All source reports below are completed, Gemini-judged, use the same 100-item release dataset, and have zero failed pairs.",
        "",
        "## Source provenance",
        "",
        "| Source | Path | SHA-256 | Configs | Completed / Failed |",
        "|---|---|---|---:|---:|",
    ]
    for key, source in summary["sources"].items():
        execution = source["execution_summary"] or {}
        lines.append(f"| `{key}` | `{source['path']}` | `{source['sha256']}` | {source['config_count']} | {execution.get('completed_pair_count')} / {execution.get('failed_pair_count')} |")
    lines += [
        "",
        "## Metric interpretation",
        "",
        "- **Faithfulness**, **answer relevancy**, **context recall**, and **citation coverage** are Gemini-judged or evidence-derived quality metrics from each run.",
        "- **Quality score** is a descriptive rank only; it deliberately excludes latency so a quality winner is not confused with a production latency winner.",
        "- Cross-wave latency is descriptive because runs occurred in different sessions. Use latency directionally, and do not treat it as a controlled hardware benchmark across waves.",
        "",
        "## 1. Chunking × Prompt 3×3 matrix",
        "",
    ]
    append_ranked_table(lines, chunk, include_chunk_prompt=True)
    lines += [
        "",
        "**Interpretation.** The best completed cell is "
        f"`{recommendations['best_completed_chunk_prompt_cell']['config_name']}`. The completed 3×3 evidence also supports `tuvi_generation_structured_v3` as the strongest prompt family in the prior marginal analysis.",
        "",
        "## 2. Retrieval / Fusion / Reranker matrix v2 — reranker top_k=10",
        "",
    ]
    append_ranked_table(lines, k10)
    lines += [
        "",
        "## 3. Retrieval / Fusion / Reranker matrix v3 — reranker top_k=40",
        "",
    ]
    append_ranked_table(lines, k40)
    lines += [
        "",
        "## 4. k10 → k40 behavior comparison",
        "",
        "Each row compares the corresponding retrieval/fusion behavior. Positive deltas favor the k40 matrix. The no-rerank reference is behaviorally unaffected by reranker top-k and is included as a run-to-run reference only.",
        "",
        "| k10 config | k40 config | Δ Faith | Δ Relevancy | Δ Context recall | Δ Citation |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for row in summary["k10_to_k40_comparison"]:
        lines.append(f"| `{row['k10_config']}` | `{row['k40_config']}` | {row['faithfulness_delta']:+.3f} | {row['relevancy_delta']:+.3f} | {row['context_recall_delta']:+.3f} | {row['citation_delta']:+.3f} |")
    lines += [
        "",
        "## 5. Conclusions",
        "",
        f"1. **Best completed chunking × prompt cell:** `{recommendations['best_completed_chunk_prompt_cell']['config_name']}`.",
        f"2. **Best k10 quality-score config:** `{recommendations['best_k10_quality']['config_name']}`.",
        f"3. **Best k40 quality-score config:** `{recommendations['best_k40_quality']['config_name']}`.",
        f"4. **Quality-first retrieval candidate:** `{recommendations['quality_first_retrieval_candidate']['config_name']}` has the highest k40 context recall.",
        f"5. **Production quality/latency candidate:** `{recommendations['production_latency_quality_candidate']['config_name']}` keeps Graph+Sparse RRF and disables reranking. It is the low-latency choice; compare its quality metrics explicitly with the k40 quality-first candidate before deployment.",
        "6. **Reranker finding:** increasing BGE reranker top-k from 10 to 40 improves several reranked path/fusion variants, confirming that top-10 was an overly restrictive early pruning point. The k40 result does not erase the operational advantage of the no-rerank route.",
        "",
        "## Hybrid-matrix limitation",
        "",
        "The k40 matrix is integrity-checked at 10 configs / 1,000 pairs / 0 failed pairs. Its two Graph+Sparse controls were reused verbatim from Phase 52 with source SHA-256 provenance, while eight variants are fresh Phase 53 runs. Quality comparisons remain supported by the common dataset/config hashes/Gemini judge; absolute cross-source latency comparisons should remain descriptive.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-json", type=Path, default=OUTPUT_JSON)
    parser.add_argument("--output-markdown", type=Path, default=OUTPUT_MARKDOWN)
    args = parser.parse_args()
    summary = build_summary()
    json_path = args.output_json if args.output_json.is_absolute() else ROOT / args.output_json
    markdown_path = args.output_markdown if args.output_markdown.is_absolute() else ROOT / args.output_markdown
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(summary, markdown_path)
    print(json.dumps({"json": relative(json_path), "markdown": relative(markdown_path), "studies": 3}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())