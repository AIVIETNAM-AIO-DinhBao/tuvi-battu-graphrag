from __future__ import annotations

from app.rag.chart_facts import build_chart_fact_context_block, extract_chart_facts


def test_extract_chart_facts_from_chart_repr_v2() -> None:
    chart_data = {
        "chart_type": "TUVI",
        "schema_role": "chart_repr",
        "schema_version": "2.0",
        "menh_position": "Ngọ",
        "than_position": "Tý",
        "ban_menh": "Thành Đầu Thổ",
        "ngu_hanh_ban_menh": "Thổ",
        "cuc": "Hỏa lục cục",
        "houses": [
            {
                "house_name": "Mệnh",
                "earthly_branch": "Ngọ",
                "major_stars": [{"name": "Thái Dương", "status": "Miếu"}],
                "aux_stars": [{"name": "Hóa Lộc"}],
            }
        ],
    }

    facts = extract_chart_facts(chart_data, [], {"target_houses": ["Mệnh"], "target_stars": ["Thái Dương"]})

    assert facts["chart_schema_detected"] == "chart_repr_v2"
    assert facts["summary"]["menh_position"] == "Ngọ"
    assert facts["house_facts"][0]["house_name"] == "Mệnh"
    assert facts["house_facts"][0]["major_stars"][0]["name"] == "Thái Dương"
    assert facts["claims_verified"]


def test_extract_chart_facts_from_palaces_v1_and_formats_context() -> None:
    chart_data = {
        "chart_type": "TUVI",
        "palaces": {"Mệnh": {"name": "Mệnh", "stars": ["Tử Vi", "Văn Xương"]}},
        "stars": {
            "Tử Vi": {"name": "Tử Vi", "palace": "Mệnh", "brightness": "Miếu", "category": "Chính Tinh"},
            "Văn Xương": {"name": "Văn Xương", "palace": "Mệnh", "category": "Phụ Tinh"},
        },
    }

    facts = extract_chart_facts(chart_data, [], {"target_houses": ["Mệnh"]})
    block = build_chart_fact_context_block(facts)

    assert facts["chart_schema_detected"] == "palaces_v1"
    assert facts["house_facts"][0]["major_stars"][0]["name"] == "Tử Vi"
    assert "[CHART]" in block
    assert "[CUNG Mệnh]" in block
    assert "Tử Vi (Miếu)" in block


def test_extract_chart_facts_promotes_thai_duong_to_major_star_even_if_payload_marks_aux() -> None:
    chart_data = {
        "chart_type": "TUVI",
        "houses": [
            {
                "house_name": "Mệnh",
                "earthly_branch": "Ngọ",
                "major_stars": [{"name": "Thiên Lương", "status": "Vượng"}],
                "aux_stars": [
                    {"name": "Thái Dương", "status": "Vượng", "category": "Phụ Tinh"},
                    {"name": "Lộc Tồn", "status": "Miếu"},
                ],
            }
        ],
    }

    facts = extract_chart_facts(chart_data, [], {"target_houses": ["Mệnh"], "chart_fact_intents": ["house_facts", "star_facts"]})
    block = build_chart_fact_context_block(facts)

    major_names = [star["name"] for star in facts["house_facts"][0]["major_stars"]]
    aux_names = [star["name"] for star in facts["house_facts"][0]["aux_stars"]]
    assert "Thái Dương" in major_names
    assert "Thiên Lương" in major_names
    assert "Thái Dương" not in aux_names
    assert "Chính tinh: Thiên Lương (Vượng), Thái Dương (Vượng)" in block
    assert "Lộc Tồn (Miếu)" in block


def test_extract_chart_facts_unknown_shape_is_defensive() -> None:
    facts = extract_chart_facts({"foo": "bar"}, [], {"target_houses": ["Mệnh"]})

    assert facts["chart_available"] is True
    assert facts["chart_schema_detected"] == "unknown"
    assert facts["house_facts"] == []
    assert "chart_schema_unknown" in facts["warnings"]


def test_extract_chart_facts_locks_explicit_house_triad_and_formats_relation() -> None:
    chart_data = {
        "chart_type": "TUVI",
        "houses": [
            {"house_name": "Phúc Đức", "major_stars": [{"name": "Thiên Cơ"}]},
            {"house_name": "Phu Thê", "major_stars": [{"name": "Thiên Đồng"}, {"name": "Cự Môn"}]},
            {"house_name": "Thiên Di", "aux_stars": [{"name": "Thái Tuế"}]},
            {"house_name": "Phụ Mẫu", "major_stars": [{"name": "Thất Sát"}]},
        ],
    }
    retrieval_plan = {
        "target_houses": ["Phúc Đức", "Phu Thê", "Thiên Di"],
        "target_houses_source": "query_alias_parser",
        "chart_fact_intents": ["tam_hop", "house_facts", "star_facts"],
        "explicit_house_triad": {
            "type": "house_triad",
            "name": "Phúc-Phối-Di",
            "houses": ["Phúc Đức", "Phu Thê", "Thiên Di"],
            "available": True,
            "source": "tuvi_house_ontology",
            "explicit": True,
            "recognized_standard_triad": True,
        },
    }
    noisy_entities = [{"canonical_name": "Phụ Mẫu", "entity_type": "Cung"}]

    facts = extract_chart_facts(chart_data, noisy_entities, retrieval_plan)
    block = build_chart_fact_context_block(facts)

    assert facts["target_houses"] == ["Phúc Đức", "Phu Thê", "Thiên Di"]
    assert [house["house_name"] for house in facts["house_facts"]] == ["Phúc Đức", "Phu Thê", "Thiên Di"]
    assert facts["relations"][0]["name"] == "Phúc-Phối-Di"
    assert "Tam hợp Phúc-Phối-Di" in block
    assert "[CUNG Phụ Mẫu]" not in block