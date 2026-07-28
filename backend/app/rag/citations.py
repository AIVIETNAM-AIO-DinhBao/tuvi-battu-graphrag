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
        "evidence_warnings": build_evidence_warnings(state, sources, context_chunks),
        "marker_count": len(markers),
        "markers": markers,
        "unmatched_markers": unmatched_markers,
        "source_count": len(sources),
        "weak_source_count": sum(1 for source in sources if source.get("weak_evidence")),
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
        "evidence_role": chunk.get("evidence_role"),
        "evidence_roles": list(chunk.get("evidence_roles") or []),
        "provenance": dict(chunk.get("provenance") or {}),
        "retrieval_paths": list(chunk.get("retrieval_paths") or []),
        "retrieval_intent": chunk.get("retrieval_intent"),
        "chart_relevance_hits": list(chunk.get("chart_relevance_hits") or []),
        "chart_relevance_hit_count": chunk.get("chart_relevance_hit_count"),
        "score": chunk.get("score"),
        "source_id": chunk.get("source_id"),
        "source_name": chunk.get("source_name"),
        "source_page": chunk.get("source_page"),
        "title": chunk.get("title"),
        "used_in_answer": used_in_answer,
        "weak_evidence": bool(chunk.get("weak_evidence")),
        "weak_evidence_reasons": list(chunk.get("weak_evidence_reasons") or []),
    }


def build_evidence_warnings(
    state: RAGState,
    sources: list[dict[str, Any]],
    context_chunks: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    warnings: list[dict[str, Any]] = []
    answer_used_sources = [source for source in sources if source.get("used_in_answer")]
    weak_sources = [source for source in answer_used_sources if source.get("weak_evidence")]
    for source in weak_sources:
        warnings.append(
            {
                "type": "weak_evidence_cited",
                "citation_marker": source.get("citation_marker"),
                "chunk_id": source.get("chunk_id"),
                "reasons": list(source.get("weak_evidence_reasons") or []),
            }
        )

    required_roles = required_evidence_roles(state)
    if required_roles:
        source_roles = {role for source in sources for role in source_roles_list(source)}
        missing_roles = [role for role in required_roles if role not in source_roles and role != "chart_facts"]
        if missing_roles:
            warnings.append({"type": "missing_required_evidence_roles_in_sources", "roles": missing_roles})

    chart_source = next((source for source in sources if source.get("citation_marker") == "CHART"), None)
    if chart_source and any(role in source_roles_list(chart_source) for role in required_roles if role != "chart_facts"):
        warnings.append(
            {
                "type": "chart_source_should_not_satisfy_corpus_roles",
                "citation_marker": "CHART",
                "roles": source_roles_list(chart_source),
            }
        )

    selected_weak_chunks = [chunk for chunk in context_chunks if chunk.get("weak_evidence")]
    if selected_weak_chunks:
        warnings.append(
            {
                "type": "weak_evidence_selected_in_context",
                "chunk_ids": [chunk.get("chunk_id") for chunk in selected_weak_chunks],
                "count": len(selected_weak_chunks),
            }
        )
    return warnings


def required_evidence_roles(state: RAGState) -> list[str]:
    plan = state.get("retrieval_plan") or {}
    roles = plan.get("required_evidence_roles") if isinstance(plan, dict) else []
    result: list[str] = []
    for role in roles or []:
        text = str(role or "").strip()
        if text and text not in result:
            result.append(text)
    return result


def source_roles_list(source: dict[str, Any]) -> list[str]:
    roles: list[str] = []
    raw_roles = source.get("evidence_roles") or []
    if isinstance(raw_roles, str):
        raw_roles = [raw_roles]
    for role in raw_roles:
        text = str(role or "").strip()
        if text and text not in roles:
            roles.append(text)
    raw_role = str(source.get("evidence_role") or "").strip()
    if raw_role and raw_role not in roles:
        roles.append(raw_role)
    return roles


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