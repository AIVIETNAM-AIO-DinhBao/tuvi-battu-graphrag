from __future__ import annotations

from typing import Any

from app.rag.config import ExperimentConfig
from app.rag.graph import build_rag_graph, run_rag_dry_run
from app.rag.nodes import DRY_RUN_NODE_ORDER
from app.rag.rewrite import PassthroughQueryRewriter


def fake_chart_loader(chart_id: str, user_id: str | None = None) -> dict[str, Any]:
    assert chart_id == "chart-1"
    assert user_id == "user-1"
    return {
        "id": chart_id,
        "user_id": user_id,
        "chart_system": "TUVI",
        "chart_data": {
            "chart_type": "legacy-value-that-should-not-win",
            "metadata": {"label": "Dry run chart"},
        },
    }


class EmptyNeo4jSession:
    def __enter__(self) -> "EmptyNeo4jSession":
        return self

    def __exit__(self, *args: Any) -> None:
        return None

    def execute_read(self, tx_func: Any, **kwargs: Any) -> list[Any]:
        return tx_func(self, **kwargs)

    def run(self, query: str, **kwargs: Any) -> list[Any]:
        return []


class EmptyNeo4jDriver:
    def session(self, **kwargs: Any) -> EmptyNeo4jSession:
        return EmptyNeo4jSession()


class FakeEmbeddingService:
    def embed_query(self, text: str) -> list[float]:
        return [0.0] * 1024


def fake_retrieval_dependencies() -> dict[str, Any]:
    return {
        "neo4j_driver": EmptyNeo4jDriver(),
        "dense_embedding_service": FakeEmbeddingService(),
    }


def test_build_rag_graph_returns_invokable_graph() -> None:
    graph = build_rag_graph(
        chart_loader=fake_chart_loader,
        query_rewriter=PassthroughQueryRewriter(),
        **fake_retrieval_dependencies(),
    )

    assert hasattr(graph, "invoke")


def test_rag_dry_run_traverses_expected_nodes_and_preserves_query() -> None:
    state = run_rag_dry_run(
        {
            "query": "  Cung Mệnh có ý nghĩa gì?  ",
            "chart_id": "chart-1",
            "user_id": "user-1",
        },
        chart_loader=fake_chart_loader,
        query_rewriter=PassthroughQueryRewriter(),
        **fake_retrieval_dependencies(),
    )

    assert state["query"] == "  Cung Mệnh có ý nghĩa gì?  "
    assert state["normalized_query"] == "Cung Mệnh có ý nghĩa gì?"
    assert state["chart_id"] == "chart-1"
    assert state["chart_type"] == "TUVI"
    assert state["domain_filter"] == "TUVI"
    assert state["experiment_id"] == "default_production_v1"
    assert isinstance(state["experiment_config"], ExperimentConfig)
    assert state["experiment_config"].branch == "gemini-call"
    assert state["experiment_config"].embedding.slot == "bge_m3"
    assert state["rewritten_query"] == "Cung Mệnh có ý nghĩa gì?"
    assert "Mệnh" in state["entities"]
    assert state["query_entities"]
    assert state["graph_candidates"] == []
    assert state["dense_candidates"] == []
    assert state["sparse_candidates"] == []
    assert state["fused_candidates"] == []
    assert state["reranked_candidates"] == []
    assert state["final_context"] == ""
    assert state["answer"] == ""
    assert state["sources"] == []

    trace_nodes = [entry["node"] for entry in state["retrieval_trace"]["nodes"]]
    assert trace_nodes == DRY_RUN_NODE_ORDER


def test_rag_dry_run_forces_tuvi_chart_and_domain() -> None:
    state = run_rag_dry_run(
        {
            "query": "Thiên Mã tại Quan Lộc",
            "chart_id": "chart-1",
            "chart_type": "BATU",
            "domain_filter": "BATU",
            "user_id": "user-1",
        },
        chart_loader=fake_chart_loader,
        query_rewriter=PassthroughQueryRewriter(),
        **fake_retrieval_dependencies(),
    )

    assert state["chart_type"] == "TUVI"
    assert state["domain_filter"] == "TUVI"
