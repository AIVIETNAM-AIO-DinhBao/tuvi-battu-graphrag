from __future__ import annotations

from typing import Any

from app.rag.planner import QUESTION_FAMILIES, infer_question_complexity, infer_question_family
from app.rag.role_retrieval import candidate_counts_by_role, candidate_roles
from app.rag.state import RAGState


def build_retrieval_diagnostics(state: RAGState) -> dict[str, Any]:
    config = state.get("experiment_config")
    question_family, family_source = resolve_question_family(state)
    question_complexity, complexity_source = resolve_question_complexity(state)
    candidate_counts = candidate_count_summary(state)
    selected_paths = selected_retrieval_paths(state)
    selected_roles = selected_evidence_roles(state)
    diagnostics = {
        "query": {
            "original": state.get("query"),
            "normalized": state.get("normalized_query"),
            "rewritten": state.get("rewritten_query"),
        },
        "question_complexity": question_complexity,
        "question_complexity_source": complexity_source,
        "question_family": question_family,
        "question_family_source": family_source,
        "extracted_entities": compact_entities(state.get("query_entities") or []),
        "entity_count": len(state.get("query_entities") or []),
        "retrieval_plan": state.get("retrieval_plan"),
        "retrieval_plan_source": retrieval_plan_source(state),
        "chart_facts": chart_facts_summary(state.get("chart_facts") or {}),
        "enabled_retrieval_paths": {
            "graph": bool(getattr(config, "graph_retrieval_enabled", False)),
            "dense": bool(getattr(config, "dense_retrieval_enabled", False)),
            "sparse": bool(getattr(config, "sparse_retrieval_enabled", False)),
        },
        "candidate_counts": candidate_counts,
        "candidate_counts_by_role": candidate_counts_by_path_and_role(state),
        "retrieval_node_statuses": retrieval_node_statuses(state),
        "final_selected_retrieval_paths": selected_paths,
        "selected_evidence_roles": selected_roles,
        "required_evidence_roles": required_evidence_roles(state),
        "missing_evidence_roles": missing_evidence_roles(state, selected_roles),
        "graph_retrieval": graph_retrieval_diagnostics(state),
        "dense_retrieval": dense_retrieval_diagnostics(state),
        "selected_chunk_ids": selected_chunk_ids(state),
        "selected_source_ids": selected_source_ids(state),
        "chunk_strategy_id": getattr(config, "chunk_strategy_id", None),
        "fallbacks": fallback_nodes(state),
        "warnings": diagnostics_warnings(state, candidate_counts),
    }
    return sanitize_diagnostics(diagnostics)


def candidate_count_summary(state: RAGState) -> dict[str, int]:
    return {
        "graph": len(state.get("graph_candidates") or []),
        "dense": len(state.get("dense_candidates") or []),
        "sparse": len(state.get("sparse_candidates") or []),
        "fused": len(state.get("fused_candidates") or []),
        "reranked": len(state.get("reranked_candidates") or []),
        "graded": len(state.get("graded_candidates") or []),
        "ranked": len(state.get("ranked_candidates") or []),
        "context_selected": len(state.get("context_chunks") or []),
        "sources": len(state.get("sources") or []),
    }


def resolve_question_family(state: RAGState) -> tuple[str, str]:
    provided = str(state.get("question_family") or "").strip()
    if provided in QUESTION_FAMILIES:
        return provided, "provided"
    inferred = infer_question_family(
        str(state.get("rewritten_query") or state.get("normalized_query") or state.get("query") or ""),
        state.get("query_entities") or [],
        state.get("chart_data") or {},
    )
    return inferred, "heuristic" if inferred != "unknown" else "unknown"


def resolve_question_complexity(state: RAGState) -> tuple[str, str]:
    provided = str(state.get("question_complexity") or "").strip()
    if provided in {"Direct", "One-hop", "Two-hop"}:
        return provided, "provided"
    inferred = infer_question_complexity(str(state.get("rewritten_query") or state.get("normalized_query") or state.get("query") or ""))
    return inferred, "heuristic"


def compact_entities(query_entities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    compact: list[dict[str, Any]] = []
    for entity in query_entities:
        compact.append(
            {
                "canonical_name": entity.get("canonical_name"),
                "entity_type": entity.get("entity_type"),
                "surface": entity.get("surface") or entity.get("matched_text") or entity.get("text"),
            }
        )
    return compact


def selected_retrieval_paths(state: RAGState) -> list[str]:
    paths: list[str] = []
    for collection_name in ("context_chunks", "sources"):
        for item in state.get(collection_name) or []:
            raw_paths = item.get("retrieval_paths") or []
            if isinstance(raw_paths, str):
                raw_paths = [raw_paths]
            for path in raw_paths:
                value = str(path).strip()
                if value and value not in paths:
                    paths.append(value)
            raw_path = item.get("retrieval_path")
            if raw_path and str(raw_path) not in paths:
                paths.append(str(raw_path))
    return paths


def selected_evidence_roles(state: RAGState) -> list[str]:
    roles: list[str] = []
    for collection_name in ("context_chunks", "sources"):
        for item in state.get(collection_name) or []:
            for role in candidate_roles(item):
                if role and role not in roles:
                    roles.append(role)
    return roles or ["generic"]


def candidate_counts_by_path_and_role(state: RAGState) -> dict[str, dict[str, int]]:
    return {
        "graph": candidate_counts_by_role(state.get("graph_candidates") or []),
        "dense": candidate_counts_by_role(state.get("dense_candidates") or []),
        "sparse": candidate_counts_by_role(state.get("sparse_candidates") or []),
        "fused": candidate_counts_by_role(state.get("fused_candidates") or []),
        "context_selected": candidate_counts_by_role(state.get("context_chunks") or []),
    }


def required_evidence_roles(state: RAGState) -> list[str]:
    plan = state.get("retrieval_plan") or {}
    roles = plan.get("required_evidence_roles") if isinstance(plan, dict) else []
    result: list[str] = []
    for role in roles or []:
        value = str(role).strip()
        if value and value not in result:
            result.append(value)
    return result


def missing_evidence_roles(state: RAGState, selected_roles: list[str]) -> list[str]:
    selected = set(selected_roles or [])
    return [role for role in required_evidence_roles(state) if role not in selected]


def graph_retrieval_diagnostics(state: RAGState) -> dict[str, Any]:
    metadata = state.get("graph_retrieval_metadata") or {}
    return {
        "requested_mode": metadata.get("requested_mode"),
        "effective_mode": metadata.get("effective_mode"),
        "required_entity_hits": metadata.get("required_entity_hits"),
        "effective_required_entity_hits": metadata.get("effective_required_entity_hits"),
        "fallback_used": bool(metadata.get("fallback_used")),
        "fallback_reason": metadata.get("fallback_reason"),
        "role_query_count": metadata.get("role_query_count", len(state.get("graph_role_queries") or [])),
        "role_metadata": metadata.get("role_metadata") or [],
    }


def dense_retrieval_diagnostics(state: RAGState) -> dict[str, Any]:
    trace = trace_node(state, "dense_retrieval")
    candidate_count = len(state.get("dense_candidates") or [])
    selected_context_count = sum(
        1
        for chunk in state.get("context_chunks") or []
        if "dense" in [str(path) for path in chunk.get("retrieval_paths") or []]
    )
    selected_context_rate = round(selected_context_count / candidate_count, 4) if candidate_count else 0.0
    return {
        "candidate_count": candidate_count,
        "duration_ms": trace.get("duration_ms"),
        "embedding_cache_stats": trace.get("embedding_cache_stats") or {},
        "enabled": bool(trace.get("enabled")),
        "enabled_by_config": bool(trace.get("enabled_by_config")),
        "enabled_by_dense_gate": bool(trace.get("enabled_by_dense_gate")),
        "enabled_by_plan": bool(trace.get("enabled_by_plan")),
        "min_query_terms": trace.get("min_query_terms"),
        "query_term_count": trace.get("query_term_count"),
        "selected_context_count": selected_context_count,
        "selected_context_rate": selected_context_rate,
        "skipped_reason": trace.get("skipped_reason"),
        "status": trace.get("status"),
    }


def selected_chunk_ids(state: RAGState) -> list[str]:
    values: list[str] = []
    for item in state.get("context_chunks") or []:
        value = item.get("chunk_id")
        if value and str(value) not in values:
            values.append(str(value))
    return values


def selected_source_ids(state: RAGState) -> list[str]:
    values: list[str] = []
    for collection_name in ("context_chunks", "sources"):
        for item in state.get(collection_name) or []:
            value = item.get("source_id") or (item.get("provenance") or {}).get("source_id")
            if value and str(value) not in values:
                values.append(str(value))
    return values


def retrieval_node_statuses(state: RAGState) -> dict[str, str]:
    result: dict[str, str] = {}
    for node in (state.get("retrieval_trace") or {}).get("nodes") or []:
        name = str(node.get("node") or "")
        if name in {"graph_retrieval", "dense_retrieval", "sparse_retrieval", "fusion", "rerank", "document_grading", "context_assembly"}:
            result[name] = str(node.get("status") or "completed")
    return result


def trace_node(state: RAGState, node_name: str) -> dict[str, Any]:
    for node in (state.get("retrieval_trace") or {}).get("nodes") or []:
        if node.get("node") == node_name:
            return dict(node)
    return {}


def fallback_nodes(state: RAGState) -> list[dict[str, Any]]:
    fallbacks: list[dict[str, Any]] = []
    for node in (state.get("retrieval_trace") or {}).get("nodes") or []:
        if node.get("status") != "fallback":
            continue
        fallbacks.append(
            {
                "node": node.get("node"),
                "error_type": node.get("error_type"),
                "reason": node.get("reason") or node.get("error"),
            }
        )
    return fallbacks


def retrieval_plan_source(state: RAGState) -> str:
    plan = state.get("retrieval_plan") or {}
    if not plan:
        return "missing"
    if plan.get("planner_version"):
        return "generated_by_query_planner"
    return "provided"


def chart_facts_summary(chart_facts: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(chart_facts, dict) or not chart_facts:
        return {
            "chart_available": False,
            "chart_schema_detected": "unknown",
            "target_houses": [],
            "target_stars": [],
            "house_fact_count": 0,
            "relation_count": 0,
            "verified_claim_count": 0,
            "unverified_claim_count": 0,
            "warnings": ["chart_facts_missing"],
        }
    return {
        "chart_available": bool(chart_facts.get("chart_available")),
        "chart_schema_detected": chart_facts.get("chart_schema_detected") or "unknown",
        "target_houses": chart_facts.get("target_houses") or [],
        "target_stars": chart_facts.get("target_stars") or [],
        "house_fact_count": len(chart_facts.get("house_facts") or []),
        "relation_count": len(chart_facts.get("relations") or []),
        "verified_claim_count": len(chart_facts.get("claims_verified") or []),
        "unverified_claim_count": len(chart_facts.get("unverified_claims") or []),
        "warnings": chart_facts.get("warnings") or [],
    }


def diagnostics_warnings(state: RAGState, candidate_counts: dict[str, int]) -> list[str]:
    warnings: list[str] = []
    if candidate_counts["graph"] + candidate_counts["dense"] + candidate_counts["sparse"] == 0:
        warnings.append("no_retrieval_candidates")
    if candidate_counts["context_selected"] == 0:
        warnings.append("no_context_chunks_selected")
    if fallback_nodes(state):
        warnings.append("retrieval_fallback_used")
    return warnings


def sanitize_diagnostics(payload: dict[str, Any]) -> dict[str, Any]:
    """Keep diagnostics API-safe: no raw context, stack trace, vectors, or secrets."""
    return payload


def normalize_text(value: Any) -> str:
    return " ".join(str(value or "").casefold().split())