from __future__ import annotations

from typing import Any

import pytest

import app.rag.nodes as rag_nodes
from app.rag.config import ExperimentConfig, load_experiment_config
from app.rag.graph import run_rag_dry_run
from app.rag.rewrite import RewriteResult


def fake_chart_loader(chart_id: str, user_id: str | None = None) -> dict[str, Any]:
    return {
        "id": chart_id,
        "user_id": user_id,
        "chart_system": "TUVI",
        "chart_data": {"chart_type": "TUVI", "metadata": {"label": "Query processing test"}},
    }


class StaticRewriter:
    def __init__(self, result: RewriteResult) -> None:
        self.result = result
        self.calls = 0

    def rewrite(self, query: str, *, chart_data: dict[str, Any], config: ExperimentConfig) -> RewriteResult:
        self.calls += 1
        return self.result


class RaisingRewriter:
    def __init__(self) -> None:
        self.calls = 0

    def rewrite(self, query: str, *, chart_data: dict[str, Any], config: ExperimentConfig) -> RewriteResult:
        self.calls += 1
        raise AssertionError("rewriter should not be called")


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


def default_config(**overrides: Any) -> ExperimentConfig:
    payload = load_experiment_config().model_dump(mode="json")
    for key, value in overrides.items():
        payload[key] = value
    return ExperimentConfig.model_validate(payload)


def patch_config(monkeypatch: pytest.MonkeyPatch, config: ExperimentConfig) -> None:
    monkeypatch.setattr(rag_nodes, "load_experiment_config", lambda path=None: config)


def run_query(query: str, *, rewriter: Any, monkeypatch: pytest.MonkeyPatch, config: ExperimentConfig) -> dict[str, Any]:
    patch_config(monkeypatch, config)
    return run_rag_dry_run(
        {"query": query, "chart_id": "chart-1", "user_id": "user-1"},
        chart_loader=fake_chart_loader,
        query_rewriter=rewriter,
        neo4j_driver=EmptyNeo4jDriver(),
        dense_embedding_service=FakeEmbeddingService(),
    )


def trace_entry(state: dict[str, Any], node_name: str) -> dict[str, Any]:
    for entry in state["retrieval_trace"]["nodes"]:
        if entry["node"] == node_name:
            return entry
    raise AssertionError(f"Missing trace node {node_name}")


def test_query_rewrite_disabled_preserves_normalized_query(monkeypatch: pytest.MonkeyPatch) -> None:
    config = default_config(query_rewrite_enabled=False)
    rewriter = RaisingRewriter()

    state = run_query("  Thiên Mã tại Quan Lộc  ", rewriter=rewriter, monkeypatch=monkeypatch, config=config)

    assert rewriter.calls == 0
    assert state["rewritten_query"] == "Thiên Mã tại Quan Lộc"
    assert trace_entry(state, "query_rewrite")["status"] == "skipped"


def test_query_rewrite_enabled_uses_injected_rewriter(monkeypatch: pytest.MonkeyPatch) -> None:
    config = default_config(query_rewrite_enabled=True)
    rewriter = StaticRewriter(
        RewriteResult(
            rewritten_query="Cung Mệnh có ý nghĩa như thế nào?",
            changed=True,
            reason="clarified wording",
            domain="TUVI",
        )
    )

    state = run_query("Cung Mệnh có ý nghĩa gì?", rewriter=rewriter, monkeypatch=monkeypatch, config=config)

    assert rewriter.calls == 1
    assert state["rewritten_query"] == "Cung Mệnh có ý nghĩa như thế nào?"
    rewrite_trace = trace_entry(state, "query_rewrite")
    assert rewrite_trace["status"] == "completed"
    assert rewrite_trace["changed"] is True


def test_query_rewrite_out_of_domain_falls_back(monkeypatch: pytest.MonkeyPatch) -> None:
    config = default_config(query_rewrite_enabled=True)
    rewriter = StaticRewriter(
        RewriteResult(
            rewritten_query="Bát Tự của người này ra sao?",
            changed=True,
            domain="BATU",
        )
    )

    state = run_query("Cung Mệnh có ý nghĩa gì?", rewriter=rewriter, monkeypatch=monkeypatch, config=config)

    assert state["rewritten_query"] == "Cung Mệnh có ý nghĩa gì?"
    rewrite_trace = trace_entry(state, "query_rewrite")
    assert rewrite_trace["status"] == "fallback"
    assert rewrite_trace["fallback_reason"] == "out_of_domain"


def test_query_rewrite_preserves_tuvi_terms(monkeypatch: pytest.MonkeyPatch) -> None:
    config = default_config(query_rewrite_enabled=True)
    rewriter = StaticRewriter(
        RewriteResult(
            rewritten_query="Sao này có ý nghĩa gì?",
            changed=True,
            domain="TUVI",
        )
    )

    state = run_query("Thiên Mã tại Quan Lộc", rewriter=rewriter, monkeypatch=monkeypatch, config=config)

    assert state["rewritten_query"] == "Thiên Mã tại Quan Lộc"
    rewrite_trace = trace_entry(state, "query_rewrite")
    assert rewrite_trace["status"] == "fallback"
    assert str(rewrite_trace["fallback_reason"]).startswith("missing_terms:")


def test_entity_extraction_disabled_returns_empty_entities(monkeypatch: pytest.MonkeyPatch) -> None:
    config = default_config(entity_extraction_enabled=False)
    rewriter = StaticRewriter(RewriteResult(rewritten_query="Thiên Mã tại Quan Lộc", changed=False))

    state = run_query("Thiên Mã tại Quan Lộc", rewriter=rewriter, monkeypatch=monkeypatch, config=config)

    assert state["entities"] == []
    assert state["query_entities"] == []
    assert trace_entry(state, "entity_extraction")["status"] == "skipped"


def test_dictionary_entity_extraction_finds_canonical_entities(monkeypatch: pytest.MonkeyPatch) -> None:
    config = default_config(entity_extraction_enabled=True)
    rewriter = StaticRewriter(
        RewriteResult(
            rewritten_query="Thiên Mã tại Quan Lộc gặp Hóa Kỵ",
            changed=False,
            domain="TUVI",
        )
    )

    state = run_query(
        "Thiên Mã tại Quan Lộc gặp Hóa Kỵ",
        rewriter=rewriter,
        monkeypatch=monkeypatch,
        config=config,
    )

    assert {"Thiên Mã", "Quan Lộc", "Hóa Kỵ"}.issubset(set(state["entities"]))
    assert all(entity["char_start"] < entity["char_end"] for entity in state["query_entities"])
    entity_trace = trace_entry(state, "entity_extraction")
    assert entity_trace["status"] == "completed"
    assert entity_trace["backend"] == "dictionary"
    assert entity_trace["entity_count"] >= 3
