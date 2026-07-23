from __future__ import annotations

from typing import Any, TypedDict

from app.rag.config import ExperimentConfig


class RAGState(TypedDict, total=False):
    query: str
    rewritten_query: str
    query_complexity: str
    question_complexity: str
    question_family: str
    chart_id: str
    chart_type: str
    chart_data: dict[str, Any]
    chart_facts: dict[str, Any]
    user_id: str
    domain_filter: str

    entities: list[str]
    query_entities: list[dict[str, Any]]
    graph_candidates: list[dict[str, Any]]
    dense_candidates: list[dict[str, Any]]
    sparse_candidates: list[dict[str, Any]]
    fused_candidates: list[dict[str, Any]]
    reranked_candidates: list[dict[str, Any]]
    graded_candidates: list[dict[str, Any]]
    ranked_candidates: list[dict[str, Any]]
    context_chunks: list[dict[str, Any]]
    context_summary: dict[str, Any]
    final_context: str

    answer: str
    sources: list[dict[str, Any]]
    generation_metadata: dict[str, Any]
    citation_metadata: dict[str, Any]
    cache_key: str

    experiment_config: "ExperimentConfig"
    experiment_id: str
    config_hash: str
    retrieval_trace: dict[str, Any]
    retrieval_plan: dict[str, Any]
    retrieval_diagnostics: dict[str, Any]
    retrieval_backend_unavailable: bool
    retrieval_backend_error_type: str

    normalized_query: str
    experiment_config_path: str
