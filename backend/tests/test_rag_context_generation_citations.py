from __future__ import annotations

from typing import Any

from app.rag.citations import map_citations
from app.rag.config import ExperimentConfig, load_experiment_config
from app.rag.context import assemble_context, order_candidates
from app.rag.generation import (
    DeterministicGenerationClient,
    NO_CONTEXT_ANSWER,
    build_generation_prompt,
    generate_answer,
)


def config_with(**overrides: Any) -> ExperimentConfig:
    payload = load_experiment_config().model_dump(mode="json")
    payload.update(overrides)
    return ExperimentConfig.model_validate(payload)


def candidate(
    chunk_id: str,
    *,
    paths: list[str] | None = None,
    score: float = 0.5,
    text: str | None = None,
    rank: int = 1,
) -> dict[str, Any]:
    return {
        "chunk_id": chunk_id,
        "chunk_hash": f"hash-{chunk_id}",
        "chunk_strategy_id": "chunk_fixed_512",
        "chunk_type": "chunk",
        "domain": "TUVI",
        "excerpt": text or f"{chunk_id} nói về Thiên Mã tại Quan Lộc.",
        "fusion_score": score,
        "matched_entities": ["Thiên Mã"],
        "parent_id": None,
        "provenance": {"source_id": "TVKL", "chunk_id": chunk_id},
        "rank": rank,
        "retrieval_paths": paths or ["dense"],
        "score": score,
        "source_id": "TVKL",
        "source_name": "Tử Vi Khảo Luận",
        "source_page": 10 + rank,
        "text": text or f"{chunk_id} nói về Thiên Mã tại Quan Lộc.",
        "title": f"Mục {chunk_id}",
    }


def test_context_assembly_balanced_uses_ranked_candidates_and_preserves_provenance() -> None:
    config = config_with(context_assembly_strategy="balanced")
    state = {
        "chart_data": {"chart_type": "TUVI", "metadata": {"label": "Lá số test"}},
        "ranked_candidates": [
            candidate("dense-only", paths=["dense"], score=0.9, rank=1),
            candidate("multi-path", paths=["graph", "dense"], score=0.8, rank=2),
        ],
    }

    final_context, chunks, summary = assemble_context(state, config)

    assert chunks[0]["chunk_id"] == "multi-path"
    assert chunks[0]["citation_marker"] == "S1"
    assert chunks[0]["provenance"]["source_id"] == "TVKL"
    assert "[CHART]" in final_context
    assert "[S1]" in final_context
    assert summary["selected_count"] == 2


def test_context_assembly_strategy_ordering_can_change_order() -> None:
    candidates = [
        candidate("graph-hit", paths=["graph"], score=0.2, rank=2),
        candidate("dense-hit", paths=["dense"], score=0.9, rank=1),
    ]

    graph_first = order_candidates(candidates, strategy="graph_first")
    dense_first = order_candidates(candidates, strategy="dense_first")

    assert graph_first[0]["chunk_id"] == "graph-hit"
    assert dense_first[0]["chunk_id"] == "dense-hit"


def test_generation_no_context_returns_safe_vietnamese_fallback() -> None:
    config = config_with()
    answer, metadata = generate_answer({"query": "Cung Mệnh là gì?", "context_chunks": []}, config)

    assert answer == NO_CONTEXT_ANSWER
    assert metadata["fallback_reason"] == "no_context"


def test_generation_prompt_and_deterministic_client_use_citations() -> None:
    config = config_with()
    state = {
        "query": "Thiên Mã tại Quan Lộc thế nào?",
        "final_context": "[S1] Nguồn\nThiên Mã tại Quan Lộc chủ về dịch chuyển.",
        "context_chunks": [{"citation_marker": "S1"}],
    }

    prompt = build_generation_prompt(state, config)
    answer, metadata = generate_answer(state, config, generation_client=DeterministicGenerationClient())

    assert "Chỉ trả lời trong domain TUVI" in prompt
    assert "[S1]" in answer
    assert metadata["generation_model"] == "deterministic-test"


def test_citation_mapping_filters_explicit_markers_and_preserves_source_fields() -> None:
    config = config_with()
    state = {
        "answer": "Luận điểm chính dựa trên [S2].",
        "context_chunks": [
            {**candidate("one"), "citation_marker": "S1"},
            {**candidate("two"), "citation_marker": "S2"},
        ],
    }

    sources, metadata = map_citations(state, config)

    assert [source["citation_marker"] for source in sources] == ["S2"]
    assert sources[0]["chunk_strategy_id"] == "chunk_fixed_512"
    assert sources[0]["source_page"] == 11
    assert metadata["markers"] == ["S2"]
    assert metadata["source_count"] == 1


def test_citation_mapping_without_markers_returns_context_sources_as_fallback() -> None:
    config = config_with()
    state = {
        "answer": "Không có marker citation rõ ràng.",
        "context_chunks": [{**candidate("one"), "citation_marker": "S1"}],
    }

    sources, metadata = map_citations(state, config)

    assert len(sources) == 1
    assert sources[0]["used_in_answer"] is False
    assert metadata["citation_fallback"] is True