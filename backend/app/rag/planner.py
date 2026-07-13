from __future__ import annotations

from typing import Any

from app.rag.state import RAGState


PLANNER_VERSION = "w6_rag_02_v1"

QUESTION_FAMILIES = {
    "core_identity",
    "menh_house_interpretation",
    "than_cu_interpretation",
    "menh_cuc_relation",
    "special_state_interpretation",
    "dai_van_interpretation",
    "menh_tam_hop",
    "menh_xung_chieu",
    "topic_house_plus_relations",
    "synthesis_judgement",
}
QUESTION_COMPLEXITIES = {"Direct", "One-hop", "Two-hop"}

HOUSE_NAMES = [
    "Mệnh",
    "Phụ Mẫu",
    "Phúc Đức",
    "Điền Trạch",
    "Quan Lộc",
    "Nô Bộc",
    "Thiên Di",
    "Tật Ách",
    "Tài Bạch",
    "Tử Tức",
    "Phu Thê",
    "Huynh Đệ",
]

QUESTION_FAMILY_PLANS: dict[str, dict[str, Any]] = {
    "core_identity": {
        "retrieval_depth": "chart_only",
        "required_evidence_roles": ["house_scope"],
        "chart_fact_intents": ["identity", "house_facts"],
        "enabled_retrieval_paths": {"graph": False, "dense": False, "sparse": False},
        "graph_mode": {"mode": "entity_any", "min_hit_count": 1},
        "dense_gate": {"enabled": False},
    },
    "menh_house_interpretation": {
        "retrieval_depth": "medium",
        "required_evidence_roles": ["house_scope", "star_definition", "modifier_effect"],
        "chart_fact_intents": ["house_facts", "star_facts", "special_states"],
        "enabled_retrieval_paths": {"graph": True, "dense": True, "sparse": True},
        "graph_mode": {"mode": "entity_any", "min_hit_count": 1},
        "dense_gate": {"enabled": True, "min_query_terms": 2},
    },
    "than_cu_interpretation": {
        "retrieval_depth": "medium",
        "required_evidence_roles": ["house_scope", "relation_rule", "star_definition"],
        "chart_fact_intents": ["than_position", "house_facts", "star_facts"],
        "enabled_retrieval_paths": {"graph": True, "dense": True, "sparse": True},
        "graph_mode": {"mode": "entity_any", "min_hit_count": 1},
        "dense_gate": {"enabled": True, "min_query_terms": 2},
    },
    "menh_cuc_relation": {
        "retrieval_depth": "medium",
        "required_evidence_roles": ["relation_rule", "house_scope"],
        "chart_fact_intents": ["menh_cuc", "identity"],
        "enabled_retrieval_paths": {"graph": True, "dense": True, "sparse": True},
        "graph_mode": {"mode": "entity_all", "min_hit_count": 2},
        "dense_gate": {"enabled": True, "min_query_terms": 2},
    },
    "special_state_interpretation": {
        "retrieval_depth": "medium",
        "required_evidence_roles": ["modifier_effect", "house_scope", "star_definition"],
        "chart_fact_intents": ["special_states", "house_facts", "star_facts"],
        "enabled_retrieval_paths": {"graph": True, "dense": True, "sparse": True},
        "graph_mode": {"mode": "entity_any", "min_hit_count": 1},
        "dense_gate": {"enabled": True, "min_query_terms": 2},
    },
    "dai_van_interpretation": {
        "retrieval_depth": "medium",
        "required_evidence_roles": ["house_scope", "relation_rule", "modifier_effect"],
        "chart_fact_intents": ["dai_van", "house_facts", "star_facts"],
        "enabled_retrieval_paths": {"graph": True, "dense": True, "sparse": True},
        "graph_mode": {"mode": "entity_any", "min_hit_count": 1},
        "dense_gate": {"enabled": True, "min_query_terms": 2},
    },
    "menh_tam_hop": {
        "retrieval_depth": "deep",
        "required_evidence_roles": ["relation_rule", "combination_pattern", "house_scope", "star_definition"],
        "chart_fact_intents": ["tam_hop", "house_facts", "star_facts"],
        "enabled_retrieval_paths": {"graph": True, "dense": True, "sparse": True},
        "graph_mode": {"mode": "min_hit_count", "min_hit_count": 2},
        "dense_gate": {"enabled": True, "min_query_terms": 2},
    },
    "menh_xung_chieu": {
        "retrieval_depth": "deep",
        "required_evidence_roles": ["relation_rule", "combination_pattern", "house_scope", "star_definition"],
        "chart_fact_intents": ["xung_chieu", "house_facts", "star_facts"],
        "enabled_retrieval_paths": {"graph": True, "dense": True, "sparse": True},
        "graph_mode": {"mode": "min_hit_count", "min_hit_count": 2},
        "dense_gate": {"enabled": True, "min_query_terms": 2},
    },
    "topic_house_plus_relations": {
        "retrieval_depth": "deep",
        "required_evidence_roles": ["house_scope", "star_definition", "modifier_effect", "relation_rule"],
        "chart_fact_intents": ["topic_house", "related_houses", "star_facts", "special_states"],
        "enabled_retrieval_paths": {"graph": True, "dense": True, "sparse": True},
        "graph_mode": {"mode": "min_hit_count", "min_hit_count": 2},
        "dense_gate": {"enabled": True, "min_query_terms": 2},
    },
    "synthesis_judgement": {
        "retrieval_depth": "deep",
        "required_evidence_roles": ["house_scope", "star_definition", "modifier_effect", "relation_rule", "combination_pattern"],
        "chart_fact_intents": ["synthesis_core", "related_houses", "star_facts", "special_states"],
        "enabled_retrieval_paths": {"graph": True, "dense": True, "sparse": True},
        "graph_mode": {"mode": "min_hit_count", "min_hit_count": 2},
        "dense_gate": {"enabled": True, "min_query_terms": 2},
    },
}


def build_retrieval_plan(state: RAGState) -> dict[str, Any]:
    family, family_source = resolve_question_family_for_planner(state)
    complexity, complexity_source = resolve_question_complexity_for_planner(state, family)
    base = dict(QUESTION_FAMILY_PLANS.get(family) or QUESTION_FAMILY_PLANS["synthesis_judgement"])
    plan = {
        "planner_version": PLANNER_VERSION,
        "question_family": family,
        "question_family_source": family_source,
        "question_complexity": complexity,
        "question_complexity_source": complexity_source,
        **base,
        "target_houses": infer_target_houses(
            str(state.get("rewritten_query") or state.get("normalized_query") or state.get("query") or ""),
            state.get("query_entities") or [],
            state.get("chart_data") or {},
            family,
        ),
        "target_stars": infer_target_stars(
            str(state.get("rewritten_query") or state.get("normalized_query") or state.get("query") or ""),
            state.get("query_entities") or [],
            state.get("chart_data") or {},
        ),
        "notes": [],
    }
    if family == "unknown":
        plan["notes"].append("question_family_unknown_fallback_to_synthesis_shape")
    return plan


def resolve_question_family_for_planner(state: RAGState) -> tuple[str, str]:
    provided = str(state.get("question_family") or "").strip()
    if provided in QUESTION_FAMILIES:
        return provided, "provided"
    inferred = infer_question_family(
        str(state.get("rewritten_query") or state.get("normalized_query") or state.get("query") or ""),
        state.get("query_entities") or [],
        state.get("chart_data") or {},
    )
    return inferred, "heuristic" if inferred != "unknown" else "unknown"


def resolve_question_complexity_for_planner(state: RAGState, family: str | None = None) -> tuple[str, str]:
    provided = str(state.get("question_complexity") or "").strip()
    if provided in QUESTION_COMPLEXITIES:
        return provided, "provided"
    inferred = infer_question_complexity(str(state.get("rewritten_query") or state.get("normalized_query") or state.get("query") or ""))
    if inferred:
        return inferred, "heuristic"
    if family == "core_identity":
        return "Direct", "family_default"
    if family in {"menh_tam_hop", "menh_xung_chieu", "topic_house_plus_relations", "synthesis_judgement"}:
        return "Two-hop", "family_default"
    return "One-hop", "family_default"


def infer_question_family(query: str, query_entities: list[dict[str, Any]], chart_data: dict[str, Any]) -> str:
    text = normalize_text(query)
    entity_names = {normalize_text(entity.get("canonical_name")) for entity in query_entities}
    if any(term in text for term in ("tam hop", "tam hợp")):
        return "menh_tam_hop"
    if any(term in text for term in ("xung chieu", "xung chiếu", "doi cung", "đối cung")):
        return "menh_xung_chieu"
    if any(term in text for term in ("than cu", "thân cư", "cung than", "cung thân")):
        return "than_cu_interpretation"
    if any(term in text for term in ("dai van", "đại vận", "van han", "vận hạn", "giai doan", "giai đoạn")):
        return "dai_van_interpretation"
    if any(term in text for term in ("menh", "mệnh")) and any(term in text for term in ("cuc", "cục", "ngu hanh", "ngũ hành", "hop", "hợp", "khac", "khắc")):
        return "menh_cuc_relation"
    if any(term in text for term in ("tuan", "tuần", "triet", "triệt", "ham", "hãm", "mieu", "miếu", "dac", "đắc", "vuong", "vượng")):
        return "special_state_interpretation"
    if any(term in text for term in ("tong quan", "tổng quan", "ket luan", "kết luận", "tot khong", "tốt không", "thuan loi", "thuận lợi", "trac tro", "trắc trở")):
        return "synthesis_judgement"
    topic_houses = ("phu the", "phu thê", "quan loc", "quan lộc", "tai bach", "tài bạch", "thien di", "thiên di", "dien trach", "điền trạch")
    if any(term in text for term in topic_houses):
        return "topic_house_plus_relations"
    if any(term in text for term in ("cung menh", "cung mệnh", "menh", "mệnh")):
        if any(term in text for term in ("o dau", "ở đâu", "nam o", "nằm ở", "sao nao", "sao nào", "chinh tinh", "chính tinh")):
            return "core_identity"
        if any(term in text for term in ("noi len gi", "nói lên gì", "y nghia", "ý nghĩa", "ban than", "bản thân")):
            return "menh_house_interpretation"
    if "mệnh" in entity_names or "menh" in entity_names:
        return "menh_house_interpretation"
    return "unknown"


def infer_question_complexity(query: str) -> str:
    text = normalize_text(query)
    if any(term in text for term in ("o dau", "ở đâu", "nam o", "nằm ở", "sao nao", "sao nào", "chinh tinh", "chính tinh")):
        return "Direct"
    if any(term in text for term in ("tong quan", "tổng quan", "ket luan", "kết luận", "tot khong", "tốt không", "thuan loi", "thuận lợi", "trac tro", "trắc trở", "hon nhan", "hôn nhân", "cong danh", "công danh")):
        return "Two-hop"
    if any(term in text for term in ("tam hop", "tam hợp", "xung chieu", "xung chiếu", "phoi hop", "phối hợp", "ket hop", "kết hợp")):
        return "Two-hop"
    return "One-hop"


def infer_target_houses(query: str, entities: list[dict[str, Any]], chart_data: dict[str, Any], family: str) -> list[str]:
    targets: list[str] = []
    text = normalize_text(query)
    for house in HOUSE_NAMES:
        if normalize_text(house) in text:
            append_unique(targets, house)
    for entity in entities:
        if str(entity.get("entity_type") or "").casefold() != "cung":
            continue
        name = str(entity.get("canonical_name") or "").strip()
        canonical = canonical_house_name(name)
        if canonical:
            append_unique(targets, canonical)
    if not targets and family in {"core_identity", "menh_house_interpretation", "menh_cuc_relation", "menh_tam_hop", "menh_xung_chieu", "synthesis_judgement"}:
        targets.append("Mệnh")
    if not targets and family == "than_cu_interpretation":
        targets.append("Thân")
    return targets


def infer_target_stars(query: str, entities: list[dict[str, Any]], chart_data: dict[str, Any]) -> list[str]:
    stars: list[str] = []
    for entity in entities:
        entity_type = str(entity.get("entity_type") or "").casefold()
        if entity_type in {"sao", "chinh_tinh", "phu_tinh", "star", "chính tinh", "phụ tinh"}:
            name = str(entity.get("canonical_name") or "").strip()
            if name:
                append_unique(stars, name)
    return stars


def canonical_house_name(value: str) -> str | None:
    normalized = normalize_text(value)
    for house in HOUSE_NAMES:
        if normalize_text(house) == normalized:
            return house
    return None


def append_unique(values: list[str], value: str) -> None:
    if value and value not in values:
        values.append(value)


def normalize_text(value: Any) -> str:
    return " ".join(str(value or "").casefold().split())