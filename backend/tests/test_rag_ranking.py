from __future__ import annotations

from typing import Any

import pytest

import app.rag.nodes as rag_nodes
from app.rag.config import ExperimentConfig, load_experiment_config
from app.rag.graph import run_rag_dry_run
from app.rag.ranking import (
    LexicalOverlapReranker,
    apply_document_grading,
    apply_reranking,
    fuse_graph_first,
    fuse_retrieval_candidates,
    fuse_rrf,
    fuse_weighted_sum,
)
from app.rag.rewrite import PassthroughQueryRewriter


def candidate(path: str, chunk_id: str, rank: int, score: float, text: str | None = None) -> dict[str, Any]:
    return {
        "retrieval_path": path,
        "rank": rank,
        "score": score,
        "chunk_id": chunk_id,
        "chunk_hash": f"hash-{chunk_id}",
        "chunk_type": "chunk",
        "parent_id": None,
        "chunk_strategy_id": "chunk_fixed_512",
        "domain": "TUVI",
        "source_id": "TVKL",
        "source_name": "Tu Vi Khoa Luat",
        "source_page": rank,
        "text": text or f"{chunk_id} Thiên Mã Quan Lộc",
        "text_preview": (text or f"{chunk_id} Thiên Mã Quan Lộc")[:240],
        "title": f"Title {chunk_id}",
        "matched_entities": ["Thiên Mã"] if path == "graph" else [],
        "relation_types": ["MENTIONS"] if path == "graph" else [],
        "provenance": {"source_id": "TVKL", "chunk_id": chunk_id},
    }


def config_with(**overrides: Any) -> ExperimentConfig:
    payload = load_experiment_config().model_dump(mode="json")
    payload.update(overrides)
    return ExperimentConfig.model_validate(payload)


def ranking_state(**overrides: Any) -> dict[str, Any]:
    state: dict[str, Any] = {
        "query": "Thiên Mã tại Quan Lộc",
        "normalized_query": "Thiên Mã tại Quan Lộc",
        "rewritten_query": "Thiên Mã tại Quan Lộc",
        "graph_candidates": [],
        "dense_candidates": [],
        "sparse_candidates": [],
    }
    state.update(overrides)
    return state


def trace_entry(state: dict[str, Any], node_name: str) -> dict[str, Any]:
    for entry in state["retrieval_trace"]["nodes"]:
        if entry["node"] == node_name:
            return entry
    raise AssertionError(f"Missing trace node {node_name}")


class ReversingReranker:
    def rerank(
        self,
        query: str,
        candidates: list[dict[str, Any]],
        *,
        config: ExperimentConfig,
        state: dict[str, Any],
    ) -> list[dict[str, Any]]:
        output = []
        for index, item in enumerate(reversed(candidates), start=1):
            updated = dict(item)
            updated["rerank_score"] = float(index)
            output.append(updated)
        return output


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


def fake_chart_loader(chart_id: str, user_id: str | None = None) -> dict[str, Any]:
    return {
        "id": chart_id,
        "user_id": user_id,
        "chart_system": "TUVI",
        "chart_data": {"chart_type": "TUVI", "metadata": {"label": "Ranking test"}},
    }


def test_rrf_fusion_dedupes_candidates_and_records_score_breakdown() -> None:
    fused = fuse_rrf(
        {
            "graph": [candidate("graph", "a", 1, 0.7)],
            "dense": [candidate("dense", "a", 1, 0.9), candidate("dense", "b", 2, 0.8)],
            "sparse": [candidate("sparse", "c", 1, 5.0)],
        }
    )

    by_id = {item["chunk_id"]: item for item in fused}
    assert set(by_id) == {"a", "b", "c"}
    assert by_id["a"]["retrieval_paths"] == ["graph", "dense"]
    assert set(by_id["a"]["score_breakdown"]) == {"graph", "dense"}
    assert by_id["a"]["fusion_method"] == "rrf"
    assert by_id["a"]["fusion_score"] > by_id["b"]["fusion_score"]


def test_fusion_preserves_multi_role_metadata_across_duplicate_candidates() -> None:
    graph_hit = {
        **candidate("graph", "shared", 1, 0.7),
        "evidence_role": "star_definition",
        "evidence_roles": ["star_definition"],
        "retrieval_intent": "define_star",
    }
    sparse_hit = {
        **candidate("sparse", "shared", 1, 5.0),
        "evidence_role": "combination_pattern",
        "evidence_roles": ["generic", "combination_pattern"],
        "retrieval_intent": "combination_pattern",
    }

    fused = fuse_rrf({"graph": [graph_hit], "dense": [], "sparse": [sparse_hit]})
    shared = next(item for item in fused if item["chunk_id"] == "shared")

    assert shared["retrieval_paths"] == ["graph", "sparse"]
    assert shared["evidence_roles"] == ["star_definition", "generic", "combination_pattern"]
    assert shared["evidence_role"] == "star_definition"
    assert shared["retrieval_intent"] == "define_star"


def test_weighted_sum_uses_normalized_scores_and_can_change_order() -> None:
    fused = fuse_weighted_sum(
        {
            "graph": [candidate("graph", "graph-hit", 1, 0.2)],
            "dense": [candidate("dense", "dense-hit", 1, 0.9), candidate("dense", "graph-hit", 2, 0.1)],
            "sparse": [],
        }
    )

    assert [item["chunk_id"] for item in fused][:2] == ["graph-hit", "dense-hit"]
    graph_hit = next(item for item in fused if item["chunk_id"] == "graph-hit")
    assert graph_hit["score_breakdown"]["graph"]["normalized_score"] == 1.0
    assert graph_hit["score_breakdown"]["dense"]["normalized_score"] < 1.0


def test_graph_first_prioritizes_graph_candidates() -> None:
    fused = fuse_graph_first(
        {
            "graph": [candidate("graph", "graph-hit", 3, 0.1)],
            "dense": [candidate("dense", "dense-hit", 1, 0.99)],
            "sparse": [candidate("sparse", "sparse-hit", 1, 8.0)],
        }
    )

    assert [item["chunk_id"] for item in fused] == ["graph-hit", "dense-hit", "sparse-hit"]
    assert fused[0]["fusion_method"] == "graph_first"


@pytest.mark.parametrize("fusion_method", ["rrf", "weighted_sum", "graph_first"])
def test_fusion_dispatcher_uses_config_method(fusion_method: str) -> None:
    config = config_with(fusion_method=fusion_method)
    state = ranking_state(
        graph_candidates=[candidate("graph", "graph-hit", 1, 0.2)],
        dense_candidates=[candidate("dense", "dense-hit", 1, 0.9)],
    )

    fused = fuse_retrieval_candidates(state, config)

    assert fused
    assert all(item["fusion_method"] == fusion_method for item in fused)


def test_reranker_disabled_passes_through_fused_candidates() -> None:
    config = config_with(reranker_config={"enabled": False, "model": None, "top_k": 10})
    fused = [candidate("dense", "a", 1, 0.9)]
    state = ranking_state(fused_candidates=fused)

    assert apply_reranking(state, config) == fused


def test_reranker_enabled_can_change_order_and_apply_top_k() -> None:
    payload = load_experiment_config().model_dump(mode="json")
    payload["reranker_config"] = {"enabled": True, "model": "unit-test-reranker", "top_k": 2}
    config = ExperimentConfig.model_validate(payload)
    state = ranking_state(
        fused_candidates=[
            candidate("dense", "a", 1, 0.9, text="không liên quan"),
            candidate("dense", "b", 2, 0.8, text="Thiên Mã Quan Lộc rất rõ"),
            candidate("dense", "c", 3, 0.7, text="Mệnh Thân"),
        ]
    )

    reranked = apply_reranking(state, config, candidate_reranker=ReversingReranker())

    assert [item["chunk_id"] for item in reranked] == ["c", "b"]
    assert [item["rerank_rank"] for item in reranked] == [1, 2]
    assert all(item["reranked"] is True for item in reranked)


def test_lexical_overlap_reranker_prefers_query_overlap() -> None:
    config = config_with(reranker_config={"enabled": True, "model": "unit-test-reranker", "top_k": 3})
    reranker = LexicalOverlapReranker()
    reranked = reranker.rerank(
        "Thiên Mã Quan Lộc",
        [
            candidate("dense", "low-overlap", 1, 0.9, text="Phúc Đức Tài Bạch"),
            candidate("dense", "high-overlap", 2, 0.2, text="Thiên Mã tại Quan Lộc"),
        ],
        config=config,
        state=ranking_state(),
    )

    assert reranked[0]["chunk_id"] == "high-overlap"
    assert reranked[0]["rerank_features"]["query_overlap"] == 1.0


def test_document_grading_disabled_passes_through() -> None:
    config = config_with(document_grading_enabled=False)
    reranked = [candidate("dense", "a", 1, 0.9)]
    state = ranking_state(reranked_candidates=reranked)

    assert apply_document_grading(state, config) == reranked


def test_document_grading_enabled_adds_grade_and_drops_empty_text() -> None:
    config = config_with(document_grading_enabled=True)
    state = ranking_state(
        reranked_candidates=[
            candidate("dense", "a", 1, 0.9, text="Thiên Mã Quan Lộc"),
            candidate("dense", "empty", 2, 0.1, text=""),
        ]
    )
    state["reranked_candidates"][1]["text"] = ""
    state["reranked_candidates"][1]["text_preview"] = ""

    graded = apply_document_grading(state, config)

    assert [item["chunk_id"] for item in graded] == ["a"]
    assert graded[0]["document_grade"]["accepted"] is True
    assert graded[0]["grade_score"] > 0


def test_dry_run_ranking_nodes_emit_trace_and_ranked_candidates(monkeypatch: pytest.MonkeyPatch) -> None:
    config = config_with(
        graph_retrieval_enabled=False,
        dense_retrieval_enabled=False,
        sparse_retrieval_enabled=False,
        reranker_config={"enabled": False, "model": None, "top_k": 10},
        document_grading_enabled=False,
    )
    monkeypatch.setattr(rag_nodes, "load_experiment_config", lambda path=None: config)

    state = run_rag_dry_run(
        {"query": "Thiên Mã tại Quan Lộc", "chart_id": "chart-1", "user_id": "user-1"},
        chart_loader=fake_chart_loader,
        query_rewriter=PassthroughQueryRewriter(),
        neo4j_driver=EmptyNeo4jDriver(),
        dense_embedding_service=FakeEmbeddingService(),
    )

    assert trace_entry(state, "fusion")["fusion_method"] == "rrf"
    assert trace_entry(state, "rerank")["status"] == "skipped"
    assert trace_entry(state, "document_grading")["status"] == "skipped"
    assert state["fused_candidates"] == []
    assert state["reranked_candidates"] == []
    assert state["ranked_candidates"] == []
