from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from app.clients import get_dense_query_embedding_service, get_neo4j_driver, get_supabase_client
from app.config import settings
from app.rag.config import RuntimeEntityExtractionConfig, config_hash, load_experiment_config
from app.rag.citations import map_citations
from app.rag.context import assemble_context
from app.rag.generation import GenerationClient, generate_answer
from app.rag.query_entities import canonical_entity_names, extract_query_entities, surface_terms
from app.rag.retrieval import (
    retrieve_dense_candidates,
    retrieve_graph_candidates,
    retrieve_sparse_candidates,
)
from app.rag.ranking import (
    CandidateReranker,
    apply_document_grading,
    apply_reranking,
    count_candidates_by_path,
    fuse_retrieval_candidates,
    fusion_trace_summary,
    ranking_trace_summary,
)
from app.rag.rewrite import QueryRewriter, RewriteResult, guard_rewrite_result, make_default_query_rewriter
from app.rag.state import RAGState


ChartLoader = Callable[[str, str | None], dict[str, Any]]
QueryEntityExtractor = Callable[[str, RuntimeEntityExtractionConfig], list[dict[str, Any]]]

DRY_RUN_NODE_ORDER = [
    "load_chart_context",
    "load_config",
    "normalize_query",
    "classify_query_complexity",
    "query_rewrite",
    "entity_extraction",
    "graph_retrieval",
    "dense_retrieval",
    "sparse_retrieval",
    "fusion",
    "rerank",
    "document_grading",
    "context_assembly",
    "generation",
    "citation_map",
]


def append_trace_node(
    state: RAGState,
    node_name: str,
    *,
    status: str = "completed",
    detail: dict[str, Any] | None = None,
) -> RAGState:
    trace = dict(state.get("retrieval_trace") or {})
    nodes = list(trace.get("nodes") or [])
    entry: dict[str, Any] = {"node": node_name, "status": status}
    if detail:
        entry.update(detail)
    nodes.append(entry)
    trace["nodes"] = nodes
    state["retrieval_trace"] = trace
    return state


def default_chart_loader(chart_id: str, user_id: str | None = None) -> dict[str, Any]:
    client = get_supabase_client()
    query = (
        client.table("la_so")
        .select("id,user_id,chart_system,chart_data,chart_version")
        .eq("id", chart_id)
    )
    if user_id:
        query = query.eq("user_id", user_id)
    response = query.single().execute()
    data = getattr(response, "data", None)
    if not data:
        raise ValueError(f"Chart not found or not accessible: {chart_id}")
    return data


def with_neo4j_session(driver_or_session: Any | None, callback: Callable[[Any], Any]) -> Any:
    driver = driver_or_session or get_neo4j_driver()
    should_close_driver = driver_or_session is None

    if not hasattr(driver, "session"):
        return callback(driver)

    try:
        session_or_context = driver.session(database=settings.NEO4J_DATABASE or None)
    except TypeError:
        session_or_context = driver.session()

    try:
        if hasattr(session_or_context, "__enter__"):
            with session_or_context as session:
                return callback(session)
        try:
            return callback(session_or_context)
        finally:
            close_session = getattr(session_or_context, "close", None)
            if callable(close_session):
                close_session()
    finally:
        if should_close_driver:
            close_driver = getattr(driver, "close", None)
            if callable(close_driver):
                close_driver()


def make_load_chart_context_node(chart_loader: ChartLoader | None = None) -> Callable[[RAGState], RAGState]:
    loader = chart_loader or default_chart_loader

    def load_chart_context(state: RAGState) -> RAGState:
        chart_id = state.get("chart_id")
        if not chart_id:
            raise ValueError("RAGState requires chart_id before load_chart_context.")

        loaded = loader(chart_id, state.get("user_id"))
        if loaded.get("chart_system") and loaded.get("chart_system") != "TUVI":
            raise ValueError(f"Unsupported chart_system {loaded.get('chart_system')!r}; expected TUVI.")

        chart_data = loaded.get("chart_data") if "chart_data" in loaded else loaded
        if not isinstance(chart_data, dict):
            raise ValueError("Loaded chart_data must be an object.")

        state["chart_data"] = chart_data
        state["chart_type"] = "TUVI"
        state["domain_filter"] = "TUVI"
        return append_trace_node(
            state,
            "load_chart_context",
            detail={"chart_id": chart_id, "chart_type": "TUVI"},
        )

    return load_chart_context


def make_load_config_node(
    config_path: Path | str | None = None,
    experiment_config: Any | None = None,
) -> Callable[[RAGState], RAGState]:
    def load_config(state: RAGState) -> RAGState:
        state_config_path = state.get("experiment_config_path")
        config = experiment_config or load_experiment_config(config_path or state_config_path)
        state["experiment_config"] = config
        state["experiment_id"] = config.experiment_id
        state["config_hash"] = config_hash(config)
        state["domain_filter"] = "TUVI"
        return append_trace_node(
            state,
            "load_config",
            detail={
                "branch": config.branch,
                "chunk_strategy_id": config.chunk_strategy_id,
                "embedding_slot": config.embedding.slot,
                "experiment_id": config.experiment_id,
            },
        )

    return load_config


def normalize_query(state: RAGState) -> RAGState:
    query = state.get("query")
    if not query or not query.strip():
        raise ValueError("RAGState requires a non-empty query.")
    state["normalized_query"] = " ".join(query.split())
    return append_trace_node(state, "normalize_query")


def classify_query_complexity(state: RAGState) -> RAGState:
    normalized = state.get("normalized_query") or state.get("query") or ""
    state["query_complexity"] = "complex" if len(normalized) > 120 else "simple"
    return append_trace_node(
        state,
        "classify_query_complexity",
        detail={"query_complexity": state["query_complexity"]},
    )


def make_query_rewrite_node(query_rewriter: QueryRewriter | None = None) -> Callable[[RAGState], RAGState]:
    def query_rewrite(state: RAGState) -> RAGState:
        config = state["experiment_config"]
        original_query = state.get("normalized_query") or state.get("query") or ""
        if not config.query_rewrite_enabled:
            state["rewritten_query"] = original_query
            return append_trace_node(
                state,
                "query_rewrite",
                status="skipped",
                detail={"enabled": False},
            )

        preserved_records = extract_query_entities(
            original_query,
            config=config.runtime_entity_extraction,
        )
        terms_to_preserve = surface_terms(preserved_records)
        rewriter = query_rewriter or make_default_query_rewriter(config)
        try:
            raw_result = rewriter.rewrite(
                original_query,
                chart_data=state.get("chart_data") or {},
                config=config,
            )
        except Exception as exc:
            if not config.query_rewrite.fallback_on_error:
                raise
            raw_result = RewriteResult(
                rewritten_query=original_query,
                changed=False,
                reason="fallback_after_rewrite_error",
                domain="TUVI",
                fallback_reason=f"{type(exc).__name__}: {exc}",
            )

        result = guard_rewrite_result(
            original_query,
            raw_result,
            terms_to_preserve=terms_to_preserve,
        )
        state["rewritten_query"] = result.rewritten_query
        status = "fallback" if result.fallback_reason else "completed"
        return append_trace_node(
            state,
            "query_rewrite",
            status=status,
            detail={
                "backend": config.query_rewrite.backend,
                "changed": result.changed,
                "enabled": True,
                "fallback_reason": result.fallback_reason,
                "model": config.query_rewrite.model,
                "preserved_term_count": len(terms_to_preserve),
            },
        )

    return query_rewrite


def default_query_entity_extractor(
    query: str,
    config: RuntimeEntityExtractionConfig,
) -> list[dict[str, Any]]:
    return extract_query_entities(query, config=config)


def make_entity_extraction_node(
    query_entity_extractor: QueryEntityExtractor | None = None,
) -> Callable[[RAGState], RAGState]:
    extractor = query_entity_extractor or default_query_entity_extractor

    def entity_extraction(state: RAGState) -> RAGState:
        config = state["experiment_config"]
        if not config.entity_extraction_enabled:
            state["entities"] = []
            state["query_entities"] = []
            return append_trace_node(
                state,
                "entity_extraction",
                status="skipped",
                detail={"enabled": False},
            )

        query_text = state.get("rewritten_query") or state.get("normalized_query") or state.get("query") or ""
        query_entities = extractor(query_text, config.runtime_entity_extraction)
        state["query_entities"] = query_entities
        state["entities"] = canonical_entity_names(query_entities)
        entity_types = sorted({str(entity.get("entity_type")) for entity in query_entities})
        return append_trace_node(
            state,
            "entity_extraction",
            status="completed",
            detail={
                "backend": config.runtime_entity_extraction.backend,
                "enabled": True,
                "entity_count": len(query_entities),
                "entity_types": entity_types,
                "model": config.runtime_entity_extraction.model,
            },
        )

    return entity_extraction


def make_graph_retrieval_node(neo4j_driver: Any | None = None) -> Callable[[RAGState], RAGState]:
    def graph_retrieval(state: RAGState) -> RAGState:
        config = state["experiment_config"]
        graph_config = config.graph_retrieval
        if not config.graph_retrieval_enabled:
            state["graph_candidates"] = []
            return append_trace_node(
                state,
                "graph_retrieval",
                status="skipped",
                detail={"enabled": False, "top_k": graph_config.top_k},
            )

        candidates = with_neo4j_session(
            neo4j_driver,
            lambda session: retrieve_graph_candidates(state, session=session, config=config),
        )
        state["graph_candidates"] = candidates
        return append_trace_node(
            state,
            "graph_retrieval",
            detail={
                "candidate_count": len(candidates),
                "chunk_strategy_id": config.chunk_strategy_id,
                "enabled": True,
                "per_entity_limit": graph_config.per_entity_limit,
                "source_ids": config.source_ids,
                "timeout_seconds": graph_config.timeout_seconds,
                "top_k": graph_config.top_k,
            },
        )

    return graph_retrieval


def make_dense_retrieval_node(
    neo4j_driver: Any | None = None,
    dense_embedding_service: Any | None = None,
) -> Callable[[RAGState], RAGState]:
    def dense_retrieval(state: RAGState) -> RAGState:
        config = state["experiment_config"]
        dense_config = config.dense_retrieval
        if not config.dense_retrieval_enabled:
            state["dense_candidates"] = []
            return append_trace_node(
                state,
                "dense_retrieval",
                status="skipped",
                detail={
                    "enabled": False,
                    "embedding_slot": dense_config.embedding_slot,
                    "top_k": dense_config.top_k,
                },
            )

        embedding_service = dense_embedding_service or get_dense_query_embedding_service()
        candidates = with_neo4j_session(
            neo4j_driver,
            lambda session: retrieve_dense_candidates(
                state,
                session=session,
                embedding_service=embedding_service,
                config=config,
            ),
        )
        state["dense_candidates"] = candidates
        return append_trace_node(
            state,
            "dense_retrieval",
            detail={
                "candidate_count": len(candidates),
                "candidate_k": dense_config.candidate_k,
                "chunk_strategy_id": config.chunk_strategy_id,
                "embedding_slot": dense_config.embedding_slot,
                "enabled": True,
                "source_ids": config.source_ids,
                "timeout_seconds": dense_config.timeout_seconds,
                "top_k": dense_config.top_k,
                "vector_index": dense_config.vector_index,
            },
        )

    return dense_retrieval


def make_sparse_retrieval_node(neo4j_driver: Any | None = None) -> Callable[[RAGState], RAGState]:
    def sparse_retrieval(state: RAGState) -> RAGState:
        config = state["experiment_config"]
        sparse_config = config.sparse_retrieval
        if not config.sparse_retrieval_enabled:
            state["sparse_candidates"] = []
            return append_trace_node(
                state,
                "sparse_retrieval",
                status="skipped",
                detail={"enabled": False, "top_k": sparse_config.top_k},
            )

        candidates = with_neo4j_session(
            neo4j_driver,
            lambda session: retrieve_sparse_candidates(state, session=session, config=config),
        )
        state["sparse_candidates"] = candidates
        return append_trace_node(
            state,
            "sparse_retrieval",
            detail={
                "candidate_count": len(candidates),
                "chunk_strategy_id": config.chunk_strategy_id,
                "enabled": True,
                "fulltext_index": sparse_config.fulltext_index,
                "source_ids": config.source_ids,
                "timeout_seconds": sparse_config.timeout_seconds,
                "top_k": sparse_config.top_k,
            },
        )

    return sparse_retrieval


def fusion_node(state: RAGState) -> RAGState:
    config = state["experiment_config"]
    fused_candidates = fuse_retrieval_candidates(state, config)
    state["fused_candidates"] = fused_candidates
    return append_trace_node(
        state,
        "fusion",
        detail={
            "fusion_method": config.fusion_method,
            "input_counts": count_candidates_by_path(state),
            "output_count": len(fused_candidates),
            "score_breakdown": fusion_trace_summary(fused_candidates),
        },
    )


def make_rerank_node(candidate_reranker: CandidateReranker | None = None) -> Callable[[RAGState], RAGState]:
    def rerank(state: RAGState) -> RAGState:
        config = state["experiment_config"]
        reranked_candidates = apply_reranking(state, config, candidate_reranker=candidate_reranker)
        state["reranked_candidates"] = reranked_candidates
        return append_trace_node(
            state,
            "rerank",
            status="completed" if config.reranker_enabled else "skipped",
            detail={
                "enabled": config.reranker_enabled,
                "input_count": len(state.get("fused_candidates") or []),
                "model": config.reranker_config.model,
                "output_count": len(reranked_candidates),
                "rankings": ranking_trace_summary(reranked_candidates),
                "top_k": config.reranker_config.top_k,
            },
        )

    return rerank


def document_grading_node(state: RAGState) -> RAGState:
    config = state["experiment_config"]
    graded_candidates = apply_document_grading(state, config)
    state["graded_candidates"] = graded_candidates
    state["ranked_candidates"] = graded_candidates
    return append_trace_node(
        state,
        "document_grading",
        status="completed" if config.document_grading_enabled else "skipped",
        detail={
            "dropped_count": len(state.get("reranked_candidates") or []) - len(graded_candidates),
            "enabled": config.document_grading_enabled,
            "input_count": len(state.get("reranked_candidates") or []),
            "output_count": len(graded_candidates),
            "rankings": ranking_trace_summary(graded_candidates),
        },
    )


def context_assembly_node(state: RAGState) -> RAGState:
    config = state["experiment_config"]
    final_context, context_chunks, context_summary = assemble_context(state, config)
    state["final_context"] = final_context
    state["context_chunks"] = context_chunks
    state["context_summary"] = context_summary
    return append_trace_node(
        state,
        "context_assembly",
        detail=context_summary,
    )


def make_generation_node(generation_client: GenerationClient | None = None) -> Callable[[RAGState], RAGState]:
    def generation(state: RAGState) -> RAGState:
        config = state["experiment_config"]
        answer, metadata = generate_answer(state, config, generation_client=generation_client)
        state["answer"] = answer
        state["generation_metadata"] = metadata
        status = "fallback" if metadata.get("fallback_reason") else "completed"
        return append_trace_node(
            state,
            "generation",
            status=status,
            detail=metadata,
        )

    return generation


def citation_map_node(state: RAGState) -> RAGState:
    config = state["experiment_config"]
    sources, metadata = map_citations(state, config)
    state["sources"] = sources
    state["citation_metadata"] = metadata
    return append_trace_node(state, "citation_map", detail=metadata)


def build_node_map(
    *,
    chart_loader: ChartLoader | None = None,
    config_path: Path | str | None = None,
    experiment_config: Any | None = None,
    query_rewriter: QueryRewriter | None = None,
    query_entity_extractor: QueryEntityExtractor | None = None,
    neo4j_driver: Any | None = None,
    dense_embedding_service: Any | None = None,
    candidate_reranker: CandidateReranker | None = None,
    generation_client: GenerationClient | None = None,
) -> dict[str, Callable[[RAGState], RAGState]]:
    return {
        "load_chart_context": make_load_chart_context_node(chart_loader),
        "load_config": make_load_config_node(config_path, experiment_config),
        "normalize_query": normalize_query,
        "classify_query_complexity": classify_query_complexity,
        "query_rewrite": make_query_rewrite_node(query_rewriter),
        "entity_extraction": make_entity_extraction_node(query_entity_extractor),
        "graph_retrieval": make_graph_retrieval_node(neo4j_driver),
        "dense_retrieval": make_dense_retrieval_node(neo4j_driver, dense_embedding_service),
        "sparse_retrieval": make_sparse_retrieval_node(neo4j_driver),
        "fusion": fusion_node,
        "rerank": make_rerank_node(candidate_reranker),
        "document_grading": document_grading_node,
        "context_assembly": context_assembly_node,
        "generation": make_generation_node(generation_client),
        "citation_map": citation_map_node,
    }
