from __future__ import annotations

from app.rag.role_retrieval import build_role_queries


def test_role_queries_use_chart_fact_stars_when_query_has_no_explicit_star_entities() -> None:
    state = {
        "query": "Luận giải về mệnh của tôi",
        "retrieval_plan": {
            "question_family": "menh_house_interpretation",
            "required_evidence_roles": ["house_scope", "star_definition", "modifier_effect"],
            "target_houses": ["Mệnh"],
            "target_stars": [],
        },
        "query_entities": [{"canonical_name": "Mệnh", "entity_type": "Cung"}],
        "chart_facts": {
            "target_houses": ["Mệnh"],
            "target_stars": ["Thiên Lương", "Thái Dương", "Lộc Tồn", "Tuế Phá"],
        },
    }

    queries = build_role_queries(state)
    star_query = next(query for query in queries if query["evidence_role"] == "star_definition")

    assert star_query["target_stars"] == ["Thiên Lương", "Thái Dương", "Lộc Tồn", "Tuế Phá"]
    assert star_query["entities"] == [
        {"canonical_name": "Thiên Lương", "entity_type": "Sao"},
        {"canonical_name": "Thái Dương", "entity_type": "Sao"},
        {"canonical_name": "Lộc Tồn", "entity_type": "Sao"},
        {"canonical_name": "Tuế Phá", "entity_type": "Sao"},
    ]
