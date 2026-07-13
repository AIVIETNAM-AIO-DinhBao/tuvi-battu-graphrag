from __future__ import annotations

import pytest

from app.rag.planner import QUESTION_FAMILY_PLANS, build_retrieval_plan


@pytest.mark.parametrize("family", sorted(QUESTION_FAMILY_PLANS))
def test_planner_builds_plan_for_all_w6_families(family: str) -> None:
    state = {
        "query": "Câu hỏi kiểm thử",
        "question_family": family,
        "question_complexity": "One-hop",
        "query_entities": [],
        "chart_data": {},
    }

    plan = build_retrieval_plan(state)

    assert plan["planner_version"] == "w6_rag_02_v1"
    assert plan["question_family"] == family
    assert plan["question_family_source"] == "provided"
    assert plan["question_complexity"] == "One-hop"
    assert plan["required_evidence_roles"]
    assert plan["chart_fact_intents"]
    assert set(plan["enabled_retrieval_paths"]) == {"graph", "dense", "sparse"}
    assert "graph_mode" in plan
    assert "dense_gate" in plan


def test_planner_uses_heuristics_for_live_direct_identity_query() -> None:
    plan = build_retrieval_plan(
        {
            "query": "Cung Mệnh của lá số này nằm ở đâu và có sao nào?",
            "query_entities": [{"canonical_name": "Mệnh", "entity_type": "Cung"}],
            "chart_data": {},
        }
    )

    assert plan["question_family"] == "core_identity"
    assert plan["question_family_source"] == "heuristic"
    assert plan["question_complexity"] == "Direct"
    assert plan["retrieval_depth"] == "chart_only"
    assert plan["enabled_retrieval_paths"] == {"graph": False, "dense": False, "sparse": False}
    assert plan["target_houses"] == ["Mệnh"]


def test_planner_prefers_dataset_labels_over_heuristics() -> None:
    plan = build_retrieval_plan(
        {
            "query": "Cung Mệnh nằm ở đâu?",
            "question_family": "menh_cuc_relation",
            "question_complexity": "Two-hop",
            "query_entities": [],
            "chart_data": {},
        }
    )

    assert plan["question_family"] == "menh_cuc_relation"
    assert plan["question_family_source"] == "provided"
    assert plan["question_complexity"] == "Two-hop"
    assert plan["question_complexity_source"] == "provided"