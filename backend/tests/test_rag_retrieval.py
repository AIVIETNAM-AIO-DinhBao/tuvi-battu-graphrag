from __future__ import annotations

from typing import Any

import pytest

import app.rag.nodes as rag_nodes
from app.rag.config import ExperimentConfig, load_experiment_config
from app.rag.graph import run_rag_dry_run
from app.rag.generation import DeterministicGenerationClient
from app.rag.retrieval import (
    build_fulltext_query,
    normalize_candidate,
    retrieve_dense_candidates,
    retrieve_graph_candidates,
    retrieve_sparse_candidates,
)
from app.rag.rewrite import PassthroughQueryRewriter


def sample_node(**overrides: Any) -> dict[str, Any]:
    node = {
        "chunk_hash": "hash-1",
        "chunk_id": "chunk-1",
        "chunk_strategy_id": "chunk_fixed_512",
        "chunk_type": "leaf",
        "domain": "TUVI",
        "parent_id": None,
        "provenance_json": '{"source":"unit-test"}',
        "source_id": "TVKL",
        "source_name": "Tu Vi Khoa Luat",
        "source_page": 12,
        "text": "Alpha beta gamma",
        "title": "A test chunk",
    }
    node.update(overrides)
    return node


class RecordingTx:
    def __init__(self, responses: list[list[dict[str, Any]]]) -> None:
        self.responses = list(responses)
        self.runs: list[tuple[str, dict[str, Any]]] = []

    def run(self, query: str, **kwargs: Any) -> list[dict[str, Any]]:
        self.runs.append((query, kwargs))
        return self.responses.pop(0) if self.responses else []


class RecordingSession:
    def __init__(self, responses: list[list[dict[str, Any]]]) -> None:
        self.responses = responses
        self.runs: list[tuple[str, dict[str, Any]]] = []

    def __enter__(self) -> "RecordingSession":
        return self

    def __exit__(self, *args: Any) -> None:
        return None

    def execute_read(self, tx_func: Any, **kwargs: Any) -> list[Any]:
        tx = RecordingTx(self.responses)
        result = tx_func(tx, **kwargs)
        self.runs.extend(tx.runs)
        return result


class RecordingDriver:
    def __init__(self, session_responses: list[list[list[dict[str, Any]]]]) -> None:
        self.session_responses = list(session_responses)
        self.sessions: list[RecordingSession] = []

    def session(self, **kwargs: Any) -> RecordingSession:
        session = RecordingSession(self.session_responses.pop(0) if self.session_responses else [])
        self.sessions.append(session)
        return session


class FakeEmbeddingService:
    def __init__(self) -> None:
        self.queries: list[str] = []

    def embed_query(self, text: str) -> list[float]:
        self.queries.append(text)
        return [0.0] * 1024


class FailingDriver:
    def __init__(self) -> None:
        self.session_calls = 0

    def session(self, **kwargs: Any) -> Any:
        self.session_calls += 1
        raise OSError("synthetic DNS failure")


def config_with(**overrides: Any) -> ExperimentConfig:
    payload = load_experiment_config().model_dump(mode="json")
    payload.update(overrides)
    return ExperimentConfig.model_validate(payload)


def fake_chart_loader(chart_id: str, user_id: str | None = None) -> dict[str, Any]:
    return {
        "chart_system": "TUVI",
        "chart_data": {"chart_type": "TUVI", "id": chart_id, "user_id": user_id},
    }


def fake_query_entity_extractor(query: str, config: Any) -> list[dict[str, Any]]:
    return [
        {
            "canonical_name": "Thien Ma",
            "entity_type": "Sao",
            "surface_text": "Thien Ma",
            "char_start": 0,
            "char_end": 8,
        }
    ]


def trace_entry(state: dict[str, Any], node_name: str) -> dict[str, Any]:
    for entry in state["retrieval_trace"]["nodes"]:
        if entry["node"] == node_name:
            return entry
    raise AssertionError(f"Missing trace node {node_name}")


def test_build_fulltext_query_sanitizes_lucene_operators() -> None:
    assert build_fulltext_query("foo +bar && (baz:qux)") == "foo OR bar OR baz OR qux"


def test_normalize_candidate_uses_common_shape() -> None:
    candidate = normalize_candidate(
        {
            "node": sample_node(text="x" * 300),
            "score": 0.42,
            "matched_entities": ["Thien Ma"],
            "relation_types": ["MENTIONS"],
        },
        retrieval_path="graph",
        rank=2,
    )

    assert candidate["retrieval_path"] == "graph"
    assert candidate["rank"] == 2
    assert candidate["score"] == 0.42
    assert candidate["chunk_id"] == "chunk-1"
    assert candidate["chunk_hash"] == "hash-1"
    assert candidate["text"] == "x" * 300
    assert candidate["text_preview"] == "x" * 240
    assert candidate["matched_entities"] == ["Thien Ma"]
    assert candidate["relation_types"] == ["MENTIONS"]
    assert candidate["provenance"]["source"] == "unit-test"


def test_graph_retrieval_filters_by_domain_sources_strategy_and_entities() -> None:
    config = config_with()
    session = RecordingSession(
        [
            [
                {
                    "node": sample_node(chunk_hash="direct", chunk_id="direct"),
                    "score": 1.0,
                    "matched_entities": ["Thien Ma"],
                    "relation_types": ["MENTIONS"],
                }
            ],
            [
                {
                    "node": sample_node(chunk_hash="related", chunk_id="related"),
                    "score": 0.7,
                    "matched_entities": ["Thien Ma"],
                    "relation_types": ["GIAI_THICH"],
                }
            ],
        ]
    )

    candidates = retrieve_graph_candidates(
        {
            "query_entities": [
                {"canonical_name": "Thien Ma", "entity_type": "Sao"},
                {"canonical_name": "Thien Ma", "entity_type": "Sao"},
            ]
        },
        session=session,
        config=config,
    )

    assert [candidate["chunk_id"] for candidate in candidates] == ["direct", "related"]
    assert len(session.runs) == 2
    direct_query, direct_params = session.runs[0]
    related_query, related_params = session.runs[1]
    assert "source_id IN $source_ids" in direct_query
    assert "node.chunk_strategy_id = $chunk_strategy_id" in direct_query
    assert direct_params["domain"] == "TUVI"
    assert direct_params["source_ids"] == ["TVKL", "TVNL", "TVHS", "TVGM"]
    assert direct_params["chunk_strategy_id"] == "chunk_fixed_512"
    assert direct_params["entities"] == [{"canonical_name": "Thien Ma", "entity_type": "Sao"}]
    assert direct_params["per_entity_limit"] == config.graph_retrieval.per_entity_limit
    assert "type(rel) IN $relation_types" in related_query
    assert "MENTIONS" not in related_params["relation_types"]


def test_dense_retrieval_uses_bge_m3_vector_index_and_filters() -> None:
    config = config_with()
    session = RecordingSession(
        [[{"node": sample_node(), "score": 0.91, "matched_entities": [], "relation_types": []}]]
    )
    embedding_service = FakeEmbeddingService()

    candidates = retrieve_dense_candidates(
        {"rewritten_query": "rewritten query"},
        session=session,
        embedding_service=embedding_service,
        config=config,
    )

    query, params = session.runs[0]
    assert candidates[0]["retrieval_path"] == "dense"
    assert embedding_service.queries == ["rewritten query"]
    assert "chunkVectorBgeM3" in query
    assert "source_id IN $source_ids" in query
    assert params["candidate_k"] == config.dense_retrieval.candidate_k
    assert len(params["embedding"]) == 1024
    assert params["source_ids"] == config.source_ids
    assert params["chunk_strategy_id"] == config.chunk_strategy_id


def test_sparse_retrieval_uses_chunk_fulltext_and_sanitized_query() -> None:
    config = config_with()
    session = RecordingSession(
        [[{"node": sample_node(), "score": 0.51, "matched_entities": [], "relation_types": []}]]
    )

    candidates = retrieve_sparse_candidates(
        {"normalized_query": "foo +bar && (baz:qux)"},
        session=session,
        config=config,
    )

    query, params = session.runs[0]
    assert candidates[0]["retrieval_path"] == "sparse"
    assert "chunkFulltext" in query
    assert params["fulltext_query"] == "foo OR bar OR baz OR qux"
    assert params["source_ids"] == config.source_ids
    assert params["chunk_strategy_id"] == config.chunk_strategy_id


def test_dry_run_populates_enabled_retrieval_paths_and_keeps_downstream_placeholders() -> None:
    driver = RecordingDriver(
        [
            [
                [
                    {
                        "node": sample_node(chunk_hash="graph", chunk_id="graph"),
                        "score": 1.0,
                        "matched_entities": ["Thien Ma"],
                        "relation_types": ["MENTIONS"],
                    }
                ],
                [],
            ],
            [[{"node": sample_node(chunk_hash="dense", chunk_id="dense"), "score": 0.9}]],
            [[{"node": sample_node(chunk_hash="sparse", chunk_id="sparse"), "score": 0.8}]],
        ]
    )

    state = run_rag_dry_run(
        {"query": "Thien Ma tai Quan Loc", "chart_id": "chart-1", "user_id": "user-1"},
        chart_loader=fake_chart_loader,
        query_rewriter=PassthroughQueryRewriter(),
        query_entity_extractor=fake_query_entity_extractor,
        neo4j_driver=driver,
        dense_embedding_service=FakeEmbeddingService(),
        generation_client=DeterministicGenerationClient(),
    )

    assert [candidate["chunk_id"] for candidate in state["graph_candidates"]] == ["graph"]
    assert [candidate["chunk_id"] for candidate in state["dense_candidates"]] == ["dense"]
    assert [candidate["chunk_id"] for candidate in state["sparse_candidates"]] == ["sparse"]
    assert trace_entry(state, "graph_retrieval")["candidate_count"] == 1
    assert trace_entry(state, "dense_retrieval")["candidate_count"] == 1
    assert trace_entry(state, "sparse_retrieval")["candidate_count"] == 1
    assert trace_entry(state, "context_assembly")["selected_count"] == 3
    assert trace_entry(state, "generation")["status"] == "completed"
    assert trace_entry(state, "citation_map")["source_count"] >= 1
    assert state["answer"]
    assert state["sources"]


def test_dry_run_retrieval_toggles_skip_independently(monkeypatch: pytest.MonkeyPatch) -> None:
    config = config_with(
        graph_retrieval_enabled=False,
        dense_retrieval_enabled=False,
        sparse_retrieval_enabled=False,
    )
    monkeypatch.setattr(rag_nodes, "load_experiment_config", lambda path=None: config)

    state = run_rag_dry_run(
        {"query": "Thien Ma tai Quan Loc", "chart_id": "chart-1", "user_id": "user-1"},
        chart_loader=fake_chart_loader,
        query_rewriter=PassthroughQueryRewriter(),
        query_entity_extractor=fake_query_entity_extractor,
        neo4j_driver=RecordingDriver([]),
        dense_embedding_service=FakeEmbeddingService(),
    )

    assert state["graph_candidates"] == []
    assert state["dense_candidates"] == []
    assert state["sparse_candidates"] == []
    assert trace_entry(state, "graph_retrieval")["status"] == "skipped"
    assert trace_entry(state, "dense_retrieval")["status"] == "skipped"
    assert trace_entry(state, "sparse_retrieval")["status"] == "skipped"


def test_dry_run_retrieval_backend_failure_can_fallback_to_no_context_answer() -> None:
    driver = FailingDriver()

    state = run_rag_dry_run(
        {"query": "Thien Ma tai Quan Loc", "chart_id": "chart-1", "user_id": "user-1"},
        chart_loader=fake_chart_loader,
        query_rewriter=PassthroughQueryRewriter(),
        query_entity_extractor=fake_query_entity_extractor,
        neo4j_driver=driver,
        dense_embedding_service=FakeEmbeddingService(),
        generation_client=DeterministicGenerationClient(),
        retrieval_fallback_on_error=True,
    )

    assert driver.session_calls == 1
    assert state["graph_candidates"] == []
    assert state["dense_candidates"] == []
    assert state["sparse_candidates"] == []
    assert state["answer"]
    assert state["generation_metadata"]["fallback_reason"] == "no_context"
    assert trace_entry(state, "graph_retrieval")["status"] == "fallback"
    assert trace_entry(state, "graph_retrieval")["fallback_reason"] == "retrieval_backend_unavailable"
    assert trace_entry(state, "dense_retrieval")["status"] == "fallback"
    assert trace_entry(state, "sparse_retrieval")["status"] == "fallback"
