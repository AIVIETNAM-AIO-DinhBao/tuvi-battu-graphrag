from __future__ import annotations

from typing import Any

from app.rag.citations import map_citations
from app.rag.config import ExperimentConfig, load_experiment_config
from app.rag.context import assemble_context, order_candidates
from app.rag.generation import (
    DeterministicGenerationClient,
    GENERATION_BACKEND_FALLBACK_PREFIX,
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


class FailingGenerationClient:
    def generate(self, prompt: str, *, config: ExperimentConfig, state: dict[str, Any]) -> Any:
        raise RuntimeError("test generation backend down")


def test_context_assembly_balanced_uses_relevance_before_multipath_and_preserves_provenance() -> None:
    config = config_with(context_assembly_strategy="balanced")
    state = {
        "chart_data": {"chart_type": "TUVI", "metadata": {"label": "Lá số test"}},
        "chart_facts": {
            "chart_available": True,
            "summary": {"menh_position": "Ngọ"},
            "house_facts": [{"house_name": "Mệnh", "earthly_branch": "Ngọ", "major_stars": [{"name": "Tử Vi"}], "aux_stars": []}],
            "target_houses": ["Mệnh"],
            "target_stars": [],
        },
        "ranked_candidates": [
            candidate("dense-only", paths=["dense"], score=0.9, rank=1),
            candidate("multi-path", paths=["graph", "dense"], score=0.8, rank=2),
        ],
    }

    final_context, chunks, summary = assemble_context(state, config)

    assert chunks[0]["citation_marker"] == "CHART"
    assert chunks[1]["chunk_id"] == "dense-only"
    assert chunks[1]["citation_marker"] == "S1"
    assert chunks[1]["provenance"]["source_id"] == "TVKL"
    assert "[CHART]" in final_context
    assert "[CHART]" in final_context
    assert "[S1]" in final_context
    assert summary["selected_count"] == 2
    assert summary["has_chart_facts"] is True
    assert summary["role_aware_enabled"] is False


def test_context_assembly_adds_chart_synthetic_source_before_corpus_sources() -> None:
    config = config_with(context_assembly_strategy="balanced")
    state = {
        "chart_data": {"chart_type": "TUVI"},
        "chart_facts": {
            "chart_available": True,
            "summary": {},
            "house_facts": [
                {
                    "house_name": "Mệnh",
                    "earthly_branch": "Ngọ",
                    "major_stars": [{"name": "Thiên Lương"}, {"name": "Thái Dương"}],
                    "aux_stars": [{"name": "Lộc Tồn"}],
                }
            ],
            "target_houses": ["Mệnh"],
            "target_stars": ["Thiên Lương", "Thái Dương", "Lộc Tồn"],
        },
        "ranked_candidates": [],
    }

    final_context, chunks, summary = assemble_context(state, config)

    assert "[CHART]" in final_context
    assert "[CHART_FACTS]" not in final_context
    assert chunks[0]["citation_marker"] == "CHART"
    assert chunks[0]["source_id"] == "CHART"
    assert summary["selected_count"] == 0


def test_role_aware_context_assembly_covers_required_roles_before_global_fill() -> None:
    config = config_with(context_assembly_strategy="balanced")
    star_hits = [
        {
            **candidate(f"star-{index}", score=1.0 - index * 0.01, rank=index),
            "evidence_role": "star_definition",
            "evidence_roles": ["star_definition"],
            "retrieval_intent": "define_star",
        }
        for index in range(1, 9)
    ]
    low_ranked_house_scope = {
        **candidate("house-scope", score=0.1, rank=9),
        "evidence_role": "house_scope",
        "evidence_roles": ["house_scope"],
        "retrieval_intent": "explain_house_scope",
    }
    state = {
        "retrieval_plan": {"required_evidence_roles": ["house_scope", "star_definition"]},
        "ranked_candidates": [*star_hits, low_ranked_house_scope],
    }

    final_context, chunks, summary = assemble_context(state, config)

    selected_ids = [chunk["chunk_id"] for chunk in chunks]
    assert len(chunks) == 8
    assert "house-scope" in selected_ids
    assert "star-8" not in selected_ids
    assert selected_ids[-1] == "house-scope"
    assert summary["role_aware_enabled"] is True
    assert summary["required_evidence_roles"] == ["house_scope", "star_definition"]
    assert summary["missing_evidence_roles"] == []
    assert summary["role_coverage_rate"] == 1.0
    assert summary["selected_chunks_by_role"]["house_scope"] == ["house-scope"]
    assert summary["selected_chunks_by_role"]["star_definition"][0] == "star-1"
    assert "evidence_roles: house_scope" in final_context


def test_role_aware_context_summary_reports_missing_roles() -> None:
    config = config_with(context_assembly_strategy="balanced")
    state = {
        "retrieval_plan": {"required_evidence_roles": ["relation_rule", "modifier_effect"]},
        "ranked_candidates": [
            {
                **candidate("modifier", score=0.8),
                "evidence_role": "modifier_effect",
                "evidence_roles": ["modifier_effect"],
            }
        ],
    }

    _final_context, chunks, summary = assemble_context(state, config)

    assert [chunk["chunk_id"] for chunk in chunks] == ["modifier"]
    assert summary["role_aware_enabled"] is True
    assert summary["selected_evidence_roles"] == ["modifier_effect"]
    assert summary["missing_evidence_roles"] == ["relation_rule"]
    assert summary["role_coverage_rate"] == 0.5


def test_context_block_renders_role_metadata_for_generation_prompt() -> None:
    config = config_with(context_assembly_strategy="balanced")
    state = {
        "ranked_candidates": [
            {
                **candidate("role-hit", paths=["graph", "sparse"], score=0.9),
                "evidence_role": "star_definition",
                "evidence_roles": ["generic", "star_definition"],
                "retrieval_intent": "define_star",
            }
        ]
    }

    final_context, chunks, _summary = assemble_context(state, config)

    assert chunks[0]["evidence_roles"] == ["generic", "star_definition"]
    assert "evidence_roles: generic, star_definition" in final_context
    assert "retrieval_intent: define_star" in final_context


def test_context_assembly_filters_low_signal_chunks_when_chart_relevance_is_available() -> None:
    config = config_with(context_assembly_strategy="balanced")
    state = {
        "chart_facts": {
            "chart_available": True,
            "summary": {},
            "house_facts": [
                {
                    "house_name": "Mệnh",
                    "major_stars": [{"name": "Thái Dương"}, {"name": "Thiên Lương"}],
                    "aux_stars": [{"name": "Lộc Tồn"}, {"name": "Tuế Phá"}],
                }
            ],
            "target_houses": ["Mệnh"],
            "target_stars": ["Thái Dương", "Thiên Lương", "Lộc Tồn", "Tuế Phá"],
        },
        "ranked_candidates": [
            candidate("unrelated-thatsat", score=0.99, text="Thất Sát ở Mệnh chủ uy quyền nhưng nóng nảy."),
            candidate("thai-duong", score=0.8, text="Thái Dương tại Mệnh chủ sáng sủa, quang minh."),
            candidate("thien-luong", score=0.7, text="Thiên Lương tại Mệnh chủ nhân hậu và phúc thiện."),
        ],
    }

    _final_context, chunks, summary = assemble_context(state, config)

    selected_ids = [chunk["chunk_id"] for chunk in chunks if chunk.get("source_id") != "CHART"]
    assert selected_ids == ["thai-duong", "thien-luong"]
    assert summary["chart_relevance_filter"]["mode"] == "filter"
    assert summary["chart_relevance_filter"]["input_count"] == 3
    assert summary["chart_relevance_filter"]["output_count"] == 2


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


def test_generation_allows_chart_only_context_without_corpus_sources() -> None:
    config = config_with()
    state = {
        "query": "Cung Mệnh của lá số này nằm ở đâu?",
        "final_context": "[CHART_FACTS]\n- Cung Mệnh: Ngọ, chính tinh: Tử Vi.",
        "context_chunks": [],
    }

    answer, metadata = generate_answer(state, config, generation_client=DeterministicGenerationClient())

    assert answer != NO_CONTEXT_ANSWER
    assert "Dưới đây là phần tóm tắt an toàn" in answer
    assert "khối dữ kiện lá số" in answer
    assert metadata["fallback_reason"] is None
    assert metadata["generation_model"] == "deterministic-test"


def test_generation_backend_error_returns_chart_aware_fallback_for_factual_chart_question() -> None:
    config = config_with()
    state = {
        "query": "Mệnh của lá số này nằm ở cung nào?",
        "final_context": "[CHART_FACTS]\n- Mệnh: Ngọ\n[CUNG Mệnh]\n- Chính tinh: Tử Vi",
        "context_chunks": [],
        "chart_facts": {
            "chart_available": True,
            "summary": {"menh_position": "Ngọ"},
            "house_facts": [
                {
                    "house_name": "Mệnh",
                    "earthly_branch": "Ngọ",
                    "major_stars": [{"name": "Tử Vi"}],
                    "aux_stars": [{"name": "Tả Phù"}],
                }
            ],
        },
    }

    answer, metadata = generate_answer(state, config, generation_client=FailingGenerationClient())

    assert answer.startswith(GENERATION_BACKEND_FALLBACK_PREFIX)
    assert "Dữ kiện lá số đã trích xuất" in answer
    assert "- Mệnh: Ngọ" in answer
    assert "Cung Mệnh tại Ngọ" in answer
    assert "chính tinh: Tử Vi" in answer
    assert "Dựa trên nguồn Tử Vi đã truy xuất" not in answer
    assert metadata["fallback_reason"] == "generation_backend_error"
    assert metadata["error_type"] == "RuntimeError"
    assert metadata["error_message"] == "test generation backend down"


def test_generation_backend_error_keeps_source_markers_for_interpretive_or_multihop_question() -> None:
    config = config_with()
    state = {
        "query": "Luận giải mệnh của lá số này",
        "final_context": "[CHART_FACTS]\n- Mệnh: Ngọ\n\n[S1] Nguồn\nTử Vi thủ Mệnh cần xét miếu hãm.",
        "context_chunks": [
            {**candidate("one"), "citation_marker": "S1"},
            {**candidate("two"), "citation_marker": "S2"},
        ],
        "chart_facts": {
            "chart_available": True,
            "summary": {"menh_position": "Ngọ", "cuc": "Hỏa lục cục"},
            "house_facts": [
                {
                    "house_name": "Mệnh",
                    "earthly_branch": "Ngọ",
                    "major_stars": [{"name": "Tử Vi"}],
                    "aux_stars": [{"name": "Thiên Phủ"}],
                    "triet_khong": True,
                }
            ],
        },
    }

    answer, metadata = generate_answer(state, config, generation_client=FailingGenerationClient())

    assert GENERATION_BACKEND_FALLBACK_PREFIX in answer
    assert "Cục: Hỏa lục cục" in answer
    assert "Cung Mệnh tại Ngọ" in answer
    assert "có Triệt" in answer
    assert "Nguồn Tử Vi liên quan đã truy xuất: [S1], [S2]." in answer
    assert "phần luận giải tổng hợp cần chạy lại" in answer
    assert metadata["fallback_reason"] == "generation_backend_error"


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


def test_citation_mapping_supports_chart_facts_marker_without_corpus_fallback() -> None:
    config = config_with()
    state = {
        "answer": "Cung Mệnh có Thiên Lương và Thái Dương [CHART_FACTS].",
        "context_chunks": [
            {
                "citation_marker": "CHART",
                "chunk_id": "chart_facts",
                "chunk_strategy_id": "chunk_fixed_512",
                "excerpt": "[CHART_FACTS] Dữ kiện lá số",
                "provenance": {"source_id": "CHART"},
                "retrieval_paths": ["chart"],
                "source_id": "CHART",
                "source_name": "Dữ kiện lá số",
            },
            {**candidate("one"), "citation_marker": "S1"},
        ],
    }

    sources, metadata = map_citations(state, config)

    assert [source["citation_marker"] for source in sources] == ["CHART"]
    assert sources[0]["source_name"] == "Dữ kiện lá số"
    assert metadata["citation_fallback"] is False
    assert metadata["markers"] == ["CHART"]


def test_citation_mapping_falls_back_when_model_hallucinates_unavailable_marker() -> None:
    config = config_with()
    state = {
        "answer": "Dựa trên lá số, cung Mệnh có Tử Vi [S1].",
        "context_chunks": [
            {
                "citation_marker": "CHART",
                "chunk_id": "chart_facts",
                "chunk_strategy_id": "chunk_fixed_512",
                "excerpt": "[CHART_FACTS] Dữ kiện lá số",
                "provenance": {"source_id": "CHART"},
                "retrieval_paths": ["chart"],
                "source_id": "CHART",
                "source_name": "Dữ kiện lá số",
            }
        ],
    }

    sources, metadata = map_citations(state, config)

    assert [source["citation_marker"] for source in sources] == ["CHART"]
    assert sources[0]["used_in_answer"] is False
    assert metadata["citation_fallback"] is True
    assert metadata["unmatched_markers"] == ["S1"]