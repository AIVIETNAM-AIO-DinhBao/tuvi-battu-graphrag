"""Add the official token-overlap Evidence Recall/Precision/F1 to a retrieval report."""

from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.rag.ablation import load_ablation_dataset  # noqa: E402
from app.rag.evaluation_checkpoint import atomic_write_json, sha256_file  # noqa: E402
from app.rag.token_overlap import (  # noqa: E402
    TOKEN_OVERLAP_THRESHOLD,
    aggregate_token_overlap,
    score_token_overlap,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--threshold", type=float, default=TOKEN_OVERLAP_THRESHOLD)
    parser.add_argument("--expected-span-count", type=int, default=722)
    return parser.parse_args()


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT_DIR / path


def render_markdown(report: dict[str, Any]) -> str:
    rescore = report["token_overlap_rescore"]
    lines = [
        f"# P1 token-overlap report — {report['manifest_name']}",
        "",
        f"- Status: `{report['status']}`",
        f"- Threshold: `{rescore['threshold']}`",
        f"- Gold spans: `{rescore['gold_span_count']}/{rescore['expected_gold_span_count']}`",
        "- Evidence Recall/Evidence Precision/Evidence F1 use source-aligned multiset token overlap over the final selected context.",
        "",
        "| Config | Evidence Recall | Evidence Precision | Evidence F1 | Hits | Relevant chunks | Retrieval p95 ms |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for config in report["configs"]:
        metrics = config["metrics"]
        lines.append(
            "| {name} | {recall:.4f} | {precision:.4f} | {f1:.4f} | {hits}/{spans} | "
            "{relevant}/{chunks} | {p95} |".format(
                name=config["config_name"],
                recall=float(metrics["recall_at_8"]),
                precision=float(metrics["precision_at_8"]),
                f1=float(metrics["f1_at_8"]),
                hits=metrics["token_overlap_hit_span_count"],
                spans=metrics["token_overlap_gold_span_count"],
                relevant=metrics["token_overlap_relevant_chunk_count"],
                chunks=metrics["token_overlap_context_chunk_count"],
                p95=metrics.get("retrieval_p95_ms"),
            )
        )
    lines.extend(
        [
            "",
            "## Definitions",
            "",
            "- `overlap(g,c) = Σ min(count_g(t), count_c(t)) / |tokens(g)|`.",
            "- A gold span is hit when a same-source chunk has overlap >= 0.25.",
            "- A corpus chunk is relevant when it satisfies that condition for at least one same-source gold span.",
            "- All annotated gold spans are included, regardless of coordinate mapping status; CHART chunks are excluded.",
            "- Evidence F1 is the harmonic mean of the two micro-aggregates.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    report_path = resolve(args.report).resolve()
    dataset_path = resolve(args.dataset).resolve()
    output_path = resolve(args.output).resolve()
    report = json.loads(report_path.read_text(encoding="utf-8"))
    dataset = {item.id: item for item in load_ablation_dataset(dataset_path)}

    rescored = deepcopy(report)
    for config in rescored.get("configs") or []:
        item_results = config.get("items") or []
        for item_result in item_results:
            if item_result.get("status") != "completed":
                continue
            item_id = str(item_result.get("item_id") or "")
            if item_id not in dataset:
                raise ValueError(f"Report item is absent from dataset: {item_id}")
            gold_spans = list(dataset[item_id].gold_context_spans)
            scores = score_token_overlap(
                list(item_result.get("context_chunks") or []),
                gold_spans,
                threshold=args.threshold,
            )
            item_result.update(
                {
                    "gold_annotation_span_count": len(gold_spans),
                    "token_overlap_threshold": scores["token_overlap_threshold"],
                    "recall_at_8": scores["recall_at_8"],
                    "precision_at_8": scores["precision_at_8"],
                    "f1_at_8": scores["f1_at_8"],
                    "token_overlap_span_details": scores["token_overlap_span_details"],
                    "token_overlap_chunk_details": scores["token_overlap_chunk_details"],
                }
            )
        config.setdefault("metrics", {}).update(aggregate_token_overlap(item_results))

    span_counts = {
        int(config["metrics"].get("token_overlap_gold_span_count") or 0)
        for config in rescored.get("configs") or []
    }
    if span_counts != {args.expected_span_count}:
        raise ValueError(
            f"Expected every config to score {args.expected_span_count} gold spans; found {sorted(span_counts)}"
        )
    rescored["metric_definitions"] = {
        **dict(rescored.get("metric_definitions") or {}),
        "recall_at_8": "Gold-span hit rate using same-source multiset token coverage >= 0.25; all spans included.",
        "precision_at_8": "Fraction of selected corpus chunks matching >= 0.25 of a same-source gold span's tokens.",
        "f1_at_8": "Harmonic mean of aggregate Evidence Recall and Evidence Precision over the final selected context.",
    }
    source_backend = report.get("judge_backend")
    rescored["judge_backend"] = "rule-based-token-overlap-v2"
    rescored["token_overlap_rescore"] = {
        "scorer": "source-aligned-multiset-token-overlap-v1",
        "threshold": args.threshold,
        "gold_span_count": next(iter(span_counts)),
        "expected_gold_span_count": args.expected_span_count,
        "source_report": str(report_path),
        "source_report_sha256": sha256_file(report_path),
        "source_report_backend": source_backend,
        "dataset_sha256": sha256_file(dataset_path),
        "created_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path = output_path.with_suffix(".md")
    atomic_write_json(output_path, rescored)
    markdown_path.write_text(render_markdown(rescored), encoding="utf-8", newline="\n")
    print(
        json.dumps(
            {
                "status": "completed",
                "output": str(output_path),
                "markdown": str(markdown_path),
                "gold_span_count": next(iter(span_counts)),
                "configs": {
                    config["config_name"]: {
                        key: config["metrics"][key] for key in ("recall_at_8", "precision_at_8", "f1_at_8")
                    }
                    for config in rescored["configs"]
                },
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
