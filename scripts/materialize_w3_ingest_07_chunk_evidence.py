"""Materialize W3-INGEST-07 chunk summaries from existing chunk artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable

import chunk_text


ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_CHUNKS_DIR = ROOT_DIR / "notebooks" / "w3_local_outputs" / "chunks"
DEFAULT_REPORTS_DIR = ROOT_DIR / "benchmark" / "tuvi_golden_dataset" / "gemini_call" / "reports"
DEFAULT_CONFIG = ROOT_DIR / "configs" / "chunking_strategies.yaml"
DEFAULT_STRATEGIES = [
    "chunk_fixed_512",
    "chunk_structure_parent_child",
    "chunk_semantic_embedding_bge_m3",
]
SEMANTIC_STRATEGIES = {"chunk_semantic_embedding_bge_m3"}


def utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSONL record: {exc}") from exc
    return records


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def load_strategy_chunks(chunks_dir: Path, strategy: str) -> list[dict[str, Any]]:
    strategy_dir = chunks_dir / strategy
    if not strategy_dir.exists():
        raise FileNotFoundError(f"Missing chunk strategy directory: {strategy_dir}")
    records: list[dict[str, Any]] = []
    for path in sorted(strategy_dir.glob("*_chunks.jsonl")):
        records.extend(read_jsonl(path))
    if not records:
        raise ValueError(f"No chunks found for strategy: {strategy}")
    return records


def build_semantic_report_from_chunks(
    records: list[dict[str, Any]],
    *,
    strategy_id: str,
    strategy: dict[str, Any],
) -> dict[str, Any]:
    events: list[dict[str, Any]] = []
    break_reasons: Counter[str] = Counter()
    scores: list[float] = []
    for record in records:
        metadata = record.get("metadata") or {}
        reason = metadata.get("semantic_break_reason")
        score = metadata.get("semantic_break_score")
        if reason and reason != "document_start":
            break_reasons[str(reason)] += 1
        if isinstance(score, (float, int)):
            scores.append(float(score))
            events.append(
                {
                    "break_reason": reason,
                    "chunk_id": record.get("chunk_id"),
                    "current_tokens": record.get("token_count"),
                    "doc_id": record.get("doc_id") or record.get("source_id"),
                    "section_id": record.get("section_id"),
                    "similarity": round(float(score), 6),
                }
            )

    sorted_scores = sorted(scores)
    return {
        "avg_similarity": round(sum(scores) / len(scores), 6) if scores else None,
        "break_count": sum(break_reasons.values()),
        "break_reasons": dict(sorted(break_reasons.items())),
        "chunk_strategy_id": strategy_id,
        "derived_from_existing_chunk_metadata": True,
        "event_count": len(events),
        "generated_at": utc_now(),
        "max_similarity": sorted_scores[-1] if sorted_scores else None,
        "min_similarity": sorted_scores[0] if sorted_scores else None,
        "sample_events": events[:50],
        "semantic_method": strategy.get("semantic_method"),
        "semantic_similarity_threshold": float(strategy.get("similarity_threshold", 0.74)),
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Materialize W3-INGEST-07 chunk evidence.")
    parser.add_argument("--chunks-dir", type=Path, default=DEFAULT_CHUNKS_DIR)
    parser.add_argument("--reports-dir", type=Path, default=DEFAULT_REPORTS_DIR)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--strategies", nargs="+", default=DEFAULT_STRATEGIES)
    return parser.parse_args(argv)


def run(argv: list[str] | None = None) -> dict[str, Any]:
    args = parse_args(argv)
    config = chunk_text.load_chunking_config(args.config)
    outputs: dict[str, Any] = {}
    for strategy_id in args.strategies:
        strategy = chunk_text.get_strategy_config(config, strategy_id)
        records = load_strategy_chunks(args.chunks_dir, strategy_id)
        summary = chunk_text.build_summary(records, strategy_id, strategy)
        summary["outputs"] = {
            path.stem.replace("_chunks", ""): str(path)
            for path in sorted((args.chunks_dir / strategy_id).glob("*_chunks.jsonl"))
        }
        summary["derived_from_existing_chunks"] = True
        summary_path = args.reports_dir / f"{strategy_id}_chunk_summary.json"
        write_json(summary_path, summary)
        strategy_outputs = {"chunk_summary": str(summary_path), "total_chunks": len(records)}

        if strategy_id in SEMANTIC_STRATEGIES:
            report = build_semantic_report_from_chunks(records, strategy_id=strategy_id, strategy=strategy)
            report_path = args.reports_dir / f"{strategy_id}_semantic_similarity_report.json"
            write_json(report_path, report)
            strategy_outputs["semantic_similarity_report"] = str(report_path)
            strategy_outputs["semantic_event_count"] = report["event_count"]

        outputs[strategy_id] = strategy_outputs
    return {"completed": True, "generated_at": utc_now(), "outputs": outputs}


def cli(argv: list[str] | None = None) -> int:
    try:
        summary = run(argv)
    except (FileNotFoundError, NotImplementedError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(cli())
