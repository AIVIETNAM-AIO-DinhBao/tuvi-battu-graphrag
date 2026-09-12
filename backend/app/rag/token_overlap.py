"""Deterministic token-overlap metrics for retrieval ablations.

The metric deliberately consumes the original gold-span text rather than only
the subset that can be mapped to exact corpus character offsets.  This keeps
all annotated spans in the recall denominator while source alignment limits
obvious cross-document lexical matches.
"""

from __future__ import annotations

import re
import unicodedata
from collections import Counter
from typing import Any, Iterable


TOKEN_OVERLAP_THRESHOLD = 0.25
TOKEN_RE = re.compile(r"\w+", re.UNICODE)
SOURCE_FAMILY_PREFIXES = ("TVNL", "TVKL", "TVGM", "TVHS")


def source_family(value: Any) -> str:
    """Return the canonical source family used for gold/chunk alignment."""

    normalized = str(value or "").strip().upper()
    for prefix in SOURCE_FAMILY_PREFIXES:
        if normalized.startswith(prefix):
            return prefix
    return normalized


def normalized_tokens(text: Any) -> list[str]:
    """Case-fold, remove Vietnamese diacritics/punctuation, and tokenize."""

    decomposed = unicodedata.normalize("NFD", str(text or "")).casefold()
    accentless = "".join(character for character in decomposed if unicodedata.category(character) != "Mn")
    return TOKEN_RE.findall(accentless)


def token_coverage(gold_tokens: list[str], chunk_tokens: list[str]) -> float:
    """Return multiset token coverage of one gold span by one chunk."""

    if not gold_tokens:
        return 0.0
    gold_counts = Counter(gold_tokens)
    chunk_counts = Counter(chunk_tokens)
    matched = sum(min(count, chunk_counts[token]) for token, count in gold_counts.items())
    return matched / len(gold_tokens)


def _is_chart_chunk(chunk: dict[str, Any]) -> bool:
    return source_family(chunk.get("source_id")) == "CHART" or chunk.get("chunk_type") == "chart_facts"


def score_token_overlap(
    chunks: list[dict[str, Any]],
    gold_spans: list[dict[str, Any]],
    *,
    threshold: float = TOKEN_OVERLAP_THRESHOLD,
) -> dict[str, Any]:
    """Score final context chunks against every annotated gold span.

    A span is hit when at least one same-source corpus chunk covers ``threshold``
    of its normalized token multiset.  A chunk is relevant when it satisfies
    that same condition for at least one span.  Synthetic chart context is not
    part of the corpus retrieval denominator.
    """

    if not 0.0 <= threshold <= 1.0:
        raise ValueError("threshold must be in [0, 1].")

    corpus_chunks = [chunk for chunk in chunks if not _is_chart_chunk(chunk)]
    prepared_chunks = [
        (
            chunk,
            source_family(chunk.get("source_id") or (chunk.get("provenance") or {}).get("source_id")),
            normalized_tokens(chunk.get("excerpt") or chunk.get("text") or chunk.get("chunk_text")),
        )
        for chunk in corpus_chunks
    ]
    prepared_spans = [
        (span, source_family(span.get("doc_id") or span.get("source_id")), normalized_tokens(span.get("quote")))
        for span in gold_spans
    ]

    span_details: list[dict[str, Any]] = []
    for index, (span, span_source, gold_tokens) in enumerate(prepared_spans, start=1):
        candidates = [
            (token_coverage(gold_tokens, chunk_tokens), str(chunk.get("chunk_id") or ""))
            for chunk, chunk_source, chunk_tokens in prepared_chunks
            if span_source and chunk_source == span_source
        ]
        best_overlap, best_chunk_id = max(candidates, default=(0.0, ""), key=lambda pair: pair[0])
        span_details.append(
            {
                "span_id": str(span.get("span_id") or f"SPAN-{index:02d}"),
                "source_family": span_source,
                "best_chunk_id": best_chunk_id or None,
                "best_token_overlap": round(best_overlap, 6),
                "hit": best_overlap >= threshold,
            }
        )

    chunk_details: list[dict[str, Any]] = []
    for chunk, chunk_source, chunk_tokens in prepared_chunks:
        candidates = [
            (token_coverage(gold_tokens, chunk_tokens), str(span.get("span_id") or ""))
            for span, span_source, gold_tokens in prepared_spans
            if chunk_source and span_source == chunk_source
        ]
        best_overlap, best_span_id = max(candidates, default=(0.0, ""), key=lambda pair: pair[0])
        chunk_details.append(
            {
                "chunk_id": chunk.get("chunk_id"),
                "source_family": chunk_source,
                "best_span_id": best_span_id or None,
                "best_token_overlap": round(best_overlap, 6),
                "relevant": best_overlap >= threshold,
            }
        )

    recall = sum(bool(detail["hit"]) for detail in span_details) / len(span_details) if span_details else None
    precision = (
        sum(bool(detail["relevant"]) for detail in chunk_details) / len(chunk_details) if chunk_details else None
    )
    f1 = 0.0 if recall is not None and precision is not None and recall + precision == 0 else None
    if recall is not None and precision is not None and recall + precision > 0:
        f1 = 2 * recall * precision / (recall + precision)
    return {
        "token_overlap_threshold": threshold,
        "gold_span_count": len(span_details),
        "context_corpus_chunk_count": len(chunk_details),
        "recall_at_8": round(recall, 6) if recall is not None else None,
        "precision_at_8": round(precision, 6) if precision is not None else None,
        "f1_at_8": round(f1, 6) if f1 is not None else None,
        "token_overlap_span_details": span_details,
        "token_overlap_chunk_details": chunk_details,
    }


def aggregate_token_overlap(item_results: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Micro-average token-overlap metrics from completed gold-bearing items."""

    completed = [item for item in item_results if item.get("status") == "completed"]
    eligible = [item for item in completed if int(item.get("gold_annotation_span_count") or 0) > 0]
    spans = [detail for item in eligible for detail in item.get("token_overlap_span_details") or []]
    chunks = [detail for item in eligible for detail in item.get("token_overlap_chunk_details") or []]
    recall = sum(bool(detail.get("hit")) for detail in spans) / len(spans) if spans else None
    precision = sum(bool(detail.get("relevant")) for detail in chunks) / len(chunks) if chunks else None
    f1 = 0.0 if recall is not None and precision is not None and recall + precision == 0 else None
    if recall is not None and precision is not None and recall + precision > 0:
        f1 = 2 * recall * precision / (recall + precision)
    thresholds = {
        float(item.get("token_overlap_threshold"))
        for item in eligible
        if item.get("token_overlap_threshold") is not None
    }
    if len(thresholds) > 1:
        raise ValueError(f"Mixed token-overlap thresholds: {sorted(thresholds)}")
    return {
        "token_overlap_threshold": next(iter(thresholds), TOKEN_OVERLAP_THRESHOLD),
        "token_overlap_item_count": len(eligible),
        "token_overlap_gold_span_count": len(spans),
        "token_overlap_hit_span_count": sum(bool(detail.get("hit")) for detail in spans),
        "token_overlap_context_chunk_count": len(chunks),
        "token_overlap_relevant_chunk_count": sum(bool(detail.get("relevant")) for detail in chunks),
        "recall_at_8": round(recall, 6) if recall is not None else None,
        "precision_at_8": round(precision, 6) if precision is not None else None,
        "f1_at_8": round(f1, 6) if f1 is not None else None,
    }


__all__ = [
    "TOKEN_OVERLAP_THRESHOLD",
    "aggregate_token_overlap",
    "normalized_tokens",
    "score_token_overlap",
    "source_family",
    "token_coverage",
]
