from __future__ import annotations

from app.rag.config import load_experiment_config
from app.rag.diagnostics import build_retrieval_diagnostics, infer_question_complexity, infer_question_family


def test_build_retrieval_diagnostics_summarizes_counts_paths_and_entities() -> None:
    config = load_experiment_config()
    state = {
        "query": "Cung Mệnh của tôi nói lên gì?",
        "normalized_query": "Cung Mệnh của tôi nói lên gì?",
        "question_complexity": "One-hop",
        "question_family": "menh_house_interpretation",
        "experiment_config": config,
        "query_entities": [{"canonical_name": "Mệnh", "entity_type": "Cung", "surface": "Cung Mệnh"}],
        "graph_candidates": [{"chunk_id": "g1", "evidence_role": "star_definition", "evidence_roles": ["star_definition"]}],
        "dense_candidates": [],
        "sparse_candidates": [{"chunk_id": "s1"}, {"chunk_id": "s2"}],
        "fused_candidates": [{"chunk_id": "g1"}, {"chunk_id": "s1"}],
        "reranked_candidates": [{"chunk_id": "g1"}],
        "graded_candidates": [{"chunk_id": "g1"}],
        "ranked_candidates": [{"chunk_id": "g1"}],
        "context_chunks": [
            {
                "chunk_id": "g1",
                "evidence_role": "star_definition",
                "evidence_roles": ["star_definition", "generic"],
                "source_id": "TVGM",
                "retrieval_paths": ["graph", "sparse"],
            }
        ],
        "sources": [{"chunk_id": "g1", "source_id": "TVGM", "retrieval_paths": ["graph", "sparse"]}],
        "retrieval_trace": {"nodes": [{"node": "graph_retrieval", "status": "completed"}]},
        "retrieval_plan": {
            "planner_version": "w6_rag_02_v1",
            "question_family": "menh_house_interpretation",
            "required_evidence_roles": ["house_scope", "star_definition"],
        },
        "graph_retrieval_metadata": {
            "requested_mode": "entity_all",
            "effective_mode": "entity_any",
            "fallback_used": True,
            "fallback_reason": "strict_mode_returned_no_candidates",
            "role_query_count": 1,
        },
        "chart_facts": {
            "chart_available": True,
            "chart_schema_detected": "chart_repr_v2",
            "target_houses": ["Mệnh"],
            "target_stars": [],
            "house_facts": [{"house_name": "Mệnh"}],
            "relations": [],
            "claims_verified": [{"claim": "target_house_exists"}],
            "unverified_claims": [],
            "warnings": [],
        },
    }

    diagnostics = build_retrieval_diagnostics(state)

    assert diagnostics["question_complexity"] == "One-hop"
    assert diagnostics["question_complexity_source"] == "provided"
    assert diagnostics["question_family"] == "menh_house_interpretation"
    assert diagnostics["question_family_source"] == "provided"
    assert diagnostics["extracted_entities"][0]["canonical_name"] == "Mệnh"
    assert diagnostics["candidate_counts"]["graph"] == 1
    assert diagnostics["candidate_counts"]["sparse"] == 2
    assert diagnostics["candidate_counts"]["context_selected"] == 1
    assert diagnostics["final_selected_retrieval_paths"] == ["graph", "sparse"]
    assert diagnostics["selected_evidence_roles"] == ["star_definition", "generic"]
    assert diagnostics["candidate_counts_by_role"]["graph"] == {"star_definition": 1}
    assert diagnostics["required_evidence_roles"] == ["house_scope", "star_definition"]
    assert diagnostics["missing_evidence_roles"] == ["house_scope"]
    assert diagnostics["graph_retrieval"]["fallback_used"] is True
    assert diagnostics["graph_retrieval"]["effective_mode"] == "entity_any"
    assert diagnostics["selected_chunk_ids"] == ["g1"]
    assert diagnostics["selected_source_ids"] == ["TVGM"]
    assert diagnostics["retrieval_plan"]["planner_version"] == "w6_rag_02_v1"
    assert diagnostics["retrieval_plan_source"] == "generated_by_query_planner"
    assert diagnostics["chart_facts"]["house_fact_count"] == 1
    assert diagnostics["chart_facts"]["verified_claim_count"] == 1


def test_dense_retrieval_diagnostics_reports_gate_latency_and_selected_rate() -> None:
    config = load_experiment_config()
    state = {
        "experiment_config": config,
        "dense_candidates": [{"chunk_id": "d1"}, {"chunk_id": "d2"}],
        "context_chunks": [{"chunk_id": "d1", "retrieval_paths": ["dense", "sparse"]}],
        "retrieval_trace": {
            "nodes": [
                {
                    "node": "dense_retrieval",
                    "status": "completed",
                    "enabled": True,
                    "enabled_by_config": True,
                    "enabled_by_plan": True,
                    "enabled_by_dense_gate": True,
                    "duration_ms": 12.5,
                    "query_term_count": 3,
                    "min_query_terms": 2,
                    "embedding_cache_stats": {"query_cache_hits": 1, "query_cache_misses": 2},
                }
            ]
        },
    }

    diagnostics = build_retrieval_diagnostics(state)

    dense = diagnostics["dense_retrieval"]
    assert dense["enabled"] is True
    assert dense["enabled_by_config"] is True
    assert dense["enabled_by_plan"] is True
    assert dense["enabled_by_dense_gate"] is True
    assert dense["candidate_count"] == 2
    assert dense["selected_context_count"] == 1
    assert dense["selected_context_rate"] == 0.5
    assert dense["duration_ms"] == 12.5
    assert dense["embedding_cache_stats"]["query_cache_hits"] == 1


def test_heuristic_question_family_and_complexity_for_live_chat_queries() -> None:
    assert infer_question_family("Cung Mệnh của lá số này nằm ở đâu?", [], {}) == "core_identity"
    assert infer_question_family("Mệnh của tôi có những sao gì", [], {}) == "core_identity"
    assert infer_question_complexity("Mệnh của tôi có những sao gì") == "Direct"
    assert infer_question_family("Cung Mệnh của tôi nói lên gì về bản thân?", [], {}) == "menh_house_interpretation"
    assert infer_question_family("Luận giải về mệnh của tôi", [], {}) == "menh_house_interpretation"
    assert infer_question_family("Thân cư Thiên Di thì hậu vận thế nào?", [], {}) == "than_cu_interpretation"
    assert infer_question_family("Mệnh và Cục có hợp nhau không?", [], {}) == "menh_cuc_relation"
    assert infer_question_family("Cung Phu Thê có Triệt thì hôn nhân ra sao?", [], {}) == "special_state_interpretation"

    assert infer_question_complexity("Cung Mệnh nằm ở đâu?") == "Direct"
    assert infer_question_complexity("Cung Mệnh nói lên gì?") == "One-hop"
    assert infer_question_complexity("Đường công danh có thuận lợi không hay trắc trở?") == "Two-hop"