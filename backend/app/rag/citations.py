from __future__ import annotations

import re
from typing import Any

from app.rag.config import ExperimentConfig
from app.rag.state import RAGState


CITATION_MARKER_RE = re.compile(r"\[((?:S\d+)|CHART|CHART_FACTS)\]")


def map_citations(state: RAGState, config: ExperimentConfig) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    answer = state.get("answer") or ""
    context_chunks = [dict(chunk) for chunk in state.get("context_chunks") or []]
    markers = normalize_markers(CITATION_MARKER_RE.findall(answer))
    marker_set = set(markers)

    sources: list[dict[str, Any]] = []
    for chunk in context_chunks:
        marker = str(chunk.get("citation_marker") or "")
        used = marker in marker_set if marker_set else False
        sources.append(make_source(chunk, config=config, used_in_answer=used))

    unmatched_markers: list[str] = []
    if marker_set:
        matched_sources = [source for source in sources if source.get("used_in_answer")]
        matched_marker_set = {str(source.get("citation_marker") or "") for source in matched_sources}
        unmatched_markers = [marker for marker in markers if marker not in matched_marker_set]
        sources = matched_sources
        if not sources and context_chunks:
            sources = [make_source(chunk, config=config, used_in_answer=False) for chunk in context_chunks]

    metadata = {
        "citation_fallback": (not bool(marker_set) and bool(context_chunks)) or (bool(marker_set) and bool(unmatched_markers) and bool(sources) and not any(source.get("used_in_answer") for source in sources)),
        "context_chunk_count": len(context_chunks),
        "marker_count": len(markers),
        "markers": markers,
        "unmatched_markers": unmatched_markers,
        "source_count": len(sources),
    }
    return sources, metadata


def make_source(chunk: dict[str, Any], *, config: ExperimentConfig, used_in_answer: bool) -> dict[str, Any]:
    return {
        "citation_marker": chunk.get("citation_marker"),
        "chunk_id": chunk.get("chunk_id"),
        "chunk_hash": chunk.get("chunk_hash"),
        "chunk_strategy_id": chunk.get("chunk_strategy_id") or config.chunk_strategy_id,
        "confidence": first_present(chunk, "rerank_score", "grade_score", "fusion_score", "score"),
        "excerpt": chunk.get("excerpt") or "",
        "provenance": dict(chunk.get("provenance") or {}),
        "retrieval_paths": list(chunk.get("retrieval_paths") or []),
        "score": chunk.get("score"),
        "source_id": chunk.get("source_id"),
        "source_name": chunk.get("source_name"),
        "source_page": chunk.get("source_page"),
        "title": chunk.get("title"),
        "used_in_answer": used_in_answer,
    }


def normalize_markers(markers: list[str]) -> list[str]:
    result: list[str] = []
    for marker in markers:
        normalized = "CHART" if marker == "CHART_FACTS" else marker
        if normalized not in result:
            result.append(normalized)
    return result


def first_present(payload: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = payload.get(key)
        if value is not None:
            return value
    return None