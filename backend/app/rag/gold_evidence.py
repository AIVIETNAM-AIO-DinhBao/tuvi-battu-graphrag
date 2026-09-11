"""Deterministic gold-evidence metrics for sequential retrieval ablations."""

from __future__ import annotations

import json
import math
import re
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable


TOKEN_RE = re.compile(r"\w+", re.UNICODE)
CITATION_RE = re.compile(r"\[(S\d+|CHART|CHART_FACTS)\]")


def load_gold_span_anchors(path: Path | str) -> dict[str, list[dict[str, Any]]]:
    """Load validated anchors grouped by TuViQA item ID."""

    source = Path(path)
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    with source.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            record = json.loads(line)
            if not isinstance(record, dict):
                raise ValueError(f"Anchor line {line_number} must be a JSON object.")
            status = str(record.get("mapping_status") or "")
            if status in {"ambiguous", "unmapped"}:
                continue
            if status not in {"exact", "manual-approved"}:
                raise ValueError(f"Anchor {record.get('span_id') or line_number} has invalid status: {status}")
            item_id = str(record.get("item_id") or "").strip()
            if not item_id:
                raise ValueError(f"Anchor line {line_number} is missing item_id.")
            _validated_interval(record, label=f"anchor line {line_number}")
            grouped[item_id].append(record)
    return dict(grouped)


def _validated_interval(record: dict[str, Any], *, label: str) -> tuple[int, int]:
    try:
        start = int(record["char_start"])
        end = int(record["char_end"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"{label} requires integer char_start/char_end.") from exc
    if start < 0 or end <= start:
        raise ValueError(f"{label} has invalid interval [{start}, {end}).")
    return start, end


def _first_present(record: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = record.get(key)
        if value not in (None, ""):
            return value
    return None


def _chunk_coordinate(chunk: dict[str, Any]) -> dict[str, Any] | None:
    if str(chunk.get("source_id") or "").upper() == "CHART" or chunk.get("chunk_type") == "chart_facts":
        return None
    provenance = chunk.get("provenance") if isinstance(chunk.get("provenance"), dict) else {}
    metadata = chunk.get("metadata") if isinstance(chunk.get("metadata"), dict) else {}
    nested_provenance = metadata.get("provenance") if isinstance(metadata.get("provenance"), dict) else {}
    doc_id = _first_present(chunk, "doc_id", "source_id") or _first_present(provenance, "doc_id", "source_id")
    doc_id = doc_id or _first_present(nested_provenance, "doc_id", "source_id")
    section_id = _first_present(chunk, "section_id") or _first_present(provenance, "section_id")
    section_id = section_id or _first_present(nested_provenance, "section_id")
    start = _first_present(chunk, "char_start")
    end = _first_present(chunk, "char_end")
    if start is None:
        start = _first_present(provenance, "char_start")
    if end is None:
        end = _first_present(provenance, "char_end")
    if start is None:
        start = _first_present(metadata, "char_start") or _first_present(nested_provenance, "char_start")
    if end is None:
        end = _first_present(metadata, "char_end") or _first_present(nested_provenance, "char_end")
    if doc_id in (None, "") or start is None or end is None:
        return None
    try:
        start_int, end_int = int(start), int(end)
    except (TypeError, ValueError):
        return None
    if start_int < 0 or end_int <= start_int:
        return None
    return {
        "doc_id": str(doc_id),
        "section_id": str(section_id) if section_id not in (None, "") else None,
        "char_start": start_int,
        "char_end": end_int,
        "text": str(chunk.get("excerpt") or chunk.get("text") or chunk.get("chunk_text") or ""),
    }


def _same_coordinate_space(anchor: dict[str, Any], chunk: dict[str, Any]) -> bool:
    if str(anchor.get("doc_id")) != str(chunk.get("doc_id")):
        return False
    anchor_section = anchor.get("corpus_section_id") or anchor.get("section_id")
    chunk_section = chunk.get("section_id")
    return not anchor_section or not chunk_section or str(anchor_section) == str(chunk_section)


def _intersection(left: tuple[int, int], right: tuple[int, int]) -> int:
    return max(0, min(left[1], right[1]) - max(left[0], right[0]))


def _union_length(intervals: Iterable[tuple[int, int]]) -> int:
    ordered = sorted((start, end) for start, end in intervals if end > start)
    if not ordered:
        return 0
    total = 0
    current_start, current_end = ordered[0]
    for start, end in ordered[1:]:
        if start <= current_end:
            current_end = max(current_end, end)
        else:
            total += current_end - current_start
            current_start, current_end = start, end
    return total + current_end - current_start


def _tokens(text: str) -> set[str]:
    normalized = unicodedata.normalize("NFC", text).casefold()
    return set(TOKEN_RE.findall(normalized))


def score_gold_evidence(
    chunks: list[dict[str, Any]],
    anchors: list[dict[str, Any]],
    *,
    recall_coverage_threshold: float = 0.50,
    precision_min_chars: int = 20,
    precision_span_fraction: float = 0.10,
) -> dict[str, Any]:
    """Score selected chunks against gold intervals in the clean-corpus coordinate space."""

    non_chart_chunks = [
        chunk
        for chunk in chunks
        if str(chunk.get("source_id") or "").upper() != "CHART" and chunk.get("chunk_type") != "chart_facts"
    ]
    if not anchors:
        return {
            "gold_span_count": 0,
            "corpus_chunk_count": len(non_chart_chunks),
            "mapped_corpus_chunk_count": sum(_chunk_coordinate(chunk) is not None for chunk in non_chart_chunks),
            "gold_span_recall": None,
            "gold_chunk_precision": None,
            "character_recall": None,
            "character_precision": None,
            "token_recall": None,
            "token_precision": None,
            "gold_span_details": [],
            "chunk_details": [],
        }

    mapped_pairs = [
        (chunk, coordinate)
        for chunk in non_chart_chunks
        if (coordinate := _chunk_coordinate(chunk)) is not None
    ]

    covered_span_count = 0
    total_gold_chars = 0
    covered_gold_chars = 0
    span_details: list[dict[str, Any]] = []
    for anchor in anchors:
        gold_start, gold_end = _validated_interval(anchor, label=f"anchor {anchor.get('span_id')}")
        gold_length = gold_end - gold_start
        overlaps: list[tuple[int, int]] = []
        matching_chunk_ids: list[str] = []
        for raw_chunk, coordinate in mapped_pairs:
            if not _same_coordinate_space(anchor, coordinate):
                continue
            start = max(gold_start, coordinate["char_start"])
            end = min(gold_end, coordinate["char_end"])
            if end > start:
                overlaps.append((start, end))
                matching_chunk_ids.append(str(raw_chunk.get("chunk_id") or ""))
        covered_chars = _union_length(overlaps)
        coverage = covered_chars / gold_length
        covered = coverage >= recall_coverage_threshold
        covered_span_count += int(covered)
        total_gold_chars += gold_length
        covered_gold_chars += covered_chars
        span_details.append(
            {
                "span_id": anchor.get("span_id"),
                "coverage": round(coverage, 6),
                "covered": covered,
                "covered_chars": covered_chars,
                "gold_chars": gold_length,
                "matching_chunk_ids": matching_chunk_ids,
            }
        )

    relevant_chunk_count = 0
    total_chunk_chars = 0
    relevant_chunk_chars = 0
    chunk_details: list[dict[str, Any]] = []
    for raw_chunk, coordinate in mapped_pairs:
        chunk_start, chunk_end = coordinate["char_start"], coordinate["char_end"]
        chunk_length = chunk_end - chunk_start
        overlap_intervals: list[tuple[int, int]] = []
        matched_spans: list[str] = []
        for anchor in anchors:
            if not _same_coordinate_space(anchor, coordinate):
                continue
            gold_start, gold_end = _validated_interval(anchor, label=f"anchor {anchor.get('span_id')}")
            overlap = _intersection((chunk_start, chunk_end), (gold_start, gold_end))
            threshold = max(precision_min_chars, math.ceil((gold_end - gold_start) * precision_span_fraction))
            if overlap >= threshold:
                matched_spans.append(str(anchor.get("span_id") or ""))
            if overlap > 0:
                overlap_intervals.append((max(chunk_start, gold_start), min(chunk_end, gold_end)))
        relevant = bool(matched_spans)
        relevant_chunk_count += int(relevant)
        overlap_chars = _union_length(overlap_intervals)
        total_chunk_chars += chunk_length
        relevant_chunk_chars += overlap_chars
        chunk_details.append(
            {
                "chunk_id": raw_chunk.get("chunk_id"),
                "relevant": relevant,
                "matched_span_ids": matched_spans,
                "overlap_chars": overlap_chars,
                "chunk_chars": chunk_length,
                "coordinate_mapped": True,
            }
        )
    mapped_ids = {id(chunk) for chunk, _ in mapped_pairs}
    for raw_chunk in non_chart_chunks:
        if id(raw_chunk) in mapped_ids:
            continue
        chunk_details.append(
            {
                "chunk_id": raw_chunk.get("chunk_id"),
                "relevant": False,
                "matched_span_ids": [],
                "overlap_chars": 0,
                "chunk_chars": None,
                "coordinate_mapped": False,
            }
        )

    gold_token_union = set().union(*(_tokens(str(anchor.get("quote") or "")) for anchor in anchors))
    chunk_token_union = set().union(*(_tokens(str(chunk.get("excerpt") or chunk.get("text") or "")) for chunk in non_chart_chunks))
    common_tokens = gold_token_union & chunk_token_union

    return {
        "gold_span_count": len(anchors),
        "corpus_chunk_count": len(non_chart_chunks),
        "mapped_corpus_chunk_count": len(mapped_pairs),
        "gold_span_recall": round(covered_span_count / len(anchors), 6),
        "gold_chunk_precision": round(relevant_chunk_count / len(non_chart_chunks), 6) if non_chart_chunks else 0.0,
        "character_recall": round(covered_gold_chars / total_gold_chars, 6) if total_gold_chars else None,
        "character_precision": round(relevant_chunk_chars / total_chunk_chars, 6) if total_chunk_chars else 0.0,
        "token_recall": round(len(common_tokens) / len(gold_token_union), 6) if gold_token_union else None,
        "token_precision": round(len(common_tokens) / len(chunk_token_union), 6) if chunk_token_union else 0.0,
        "gold_span_details": span_details,
        "chunk_details": chunk_details,
    }


def score_citation_evidence(
    answer: str,
    context_chunks: list[dict[str, Any]],
    anchors: list[dict[str, Any]],
) -> dict[str, Any]:
    """Score only the evidence chunks explicitly cited by the generated answer.

    Precision is the fraction of cited corpus chunks that overlap a gold span.
    Recall is the fraction of gold spans covered by cited corpus chunks.  Both use
    the same provenance-coordinate rules as retrieval scoring, so fuzzy text
    matching is never used for the official number.
    """

    markers = list(
        dict.fromkeys("CHART" if marker == "CHART_FACTS" else marker for marker in CITATION_RE.findall(str(answer)))
    )
    chunks_by_marker = {
        str(chunk.get("citation_marker")): chunk
        for chunk in context_chunks
        if chunk.get("citation_marker")
    }
    invalid_markers = [marker for marker in markers if marker not in chunks_by_marker]
    cited_chunks = [chunks_by_marker[marker] for marker in markers if marker in chunks_by_marker]
    scores = score_gold_evidence(cited_chunks, anchors)
    precision = scores["gold_chunk_precision"]
    recall = scores["gold_span_recall"]
    if not anchors:
        f1 = None
    elif precision is None or recall is None or precision + recall == 0:
        f1 = 0.0
    else:
        f1 = round(2 * precision * recall / (precision + recall), 6)
    return {
        "citation_evidence_precision": precision,
        "citation_evidence_recall": recall,
        "citation_evidence_f1": f1,
        "valid_citation_marker_count": len(cited_chunks),
        "invalid_citation_markers": invalid_markers,
        "invalid_citation_marker_count": len(invalid_markers),
    }


def average_defined(values: Iterable[float | int | None]) -> float | None:
    defined = [float(value) for value in values if value is not None]
    return round(sum(defined) / len(defined), 6) if defined else None


def aggregate_gold_evidence(item_results: list[dict[str, Any]]) -> dict[str, Any]:
    completed = [item for item in item_results if item.get("status") == "completed"]
    corpus = [item for item in completed if not item.get("chart_only")]
    eligible = [item for item in corpus if item.get("rule_metric_eligible")]
    span_details = [detail for item in eligible for detail in item.get("gold_span_details") or []]
    chunk_details = [detail for item in eligible for detail in item.get("chunk_details") or []]
    total_gold_chars = sum(int(detail.get("gold_chars") or 0) for detail in span_details)
    covered_gold_chars = sum(int(detail.get("covered_chars") or 0) for detail in span_details)
    mapped_chunk_details = [detail for detail in chunk_details if detail.get("coordinate_mapped")]
    total_chunk_chars = sum(int(detail.get("chunk_chars") or 0) for detail in mapped_chunk_details)
    overlap_chunk_chars = sum(int(detail.get("overlap_chars") or 0) for detail in mapped_chunk_details)
    return {
        "item_count": len(item_results),
        "completed_count": len(completed),
        "failed_count": len(item_results) - len(completed),
        "corpus_grounded_item_count": len(corpus),
        "rule_metric_eligible_item_count": len(eligible),
        "gold_span_count": len(span_details),
        "context_corpus_chunk_count": len(chunk_details),
        "gold_span_recall_at_8": (
            round(sum(bool(detail.get("covered")) for detail in span_details) / len(span_details), 6)
            if span_details
            else None
        ),
        "gold_chunk_precision_at_8": (
            round(sum(bool(detail.get("relevant")) for detail in chunk_details) / len(chunk_details), 6)
            if chunk_details
            else None
        ),
        "character_recall": round(covered_gold_chars / total_gold_chars, 6) if total_gold_chars else None,
        "character_precision": round(overlap_chunk_chars / total_chunk_chars, 6) if total_chunk_chars else None,
        "token_recall": average_defined(item.get("token_recall") for item in eligible),
        "token_precision": average_defined(item.get("token_precision") for item in eligible),
        "retrieval_latency_ms_avg": average_defined(item.get("retrieval_latency_ms") for item in completed),
    }


__all__ = [
    "aggregate_gold_evidence",
    "average_defined",
    "load_gold_span_anchors",
    "score_citation_evidence",
    "score_gold_evidence",
]
