from __future__ import annotations

from collections.abc import Iterable
from typing import Any, TypedDict

from app.rag.state import RAGState


GENERIC_EVIDENCE_ROLE = "generic"
EVIDENCE_ROLES = {
    GENERIC_EVIDENCE_ROLE,
    "house_scope",
    "star_definition",
    "modifier_effect",
    "relation_rule",
    "combination_pattern",
}
ROLE_ENTITY_ANY = {"house_scope", "star_definition"}
ROLE_PLANNER_GRAPH_MODE = {"generic", "relation_rule", "combination_pattern"}
STAR_ENTITY_TYPES = {"sao", "star", "chinh_tinh", "chính tinh", "phu_tinh", "phụ tinh"}
HOUSE_ENTITY_TYPES = {"cung", "house"}
MODIFIER_TERMS = ("tuần", "tuan", "triệt", "triet", "hãm", "ham", "miếu", "mieu", "đắc", "dac", "vượng", "vuong", "hóa", "hoa")
MODIFIER_STAR_NAMES = {
    "hóa lộc",
    "hóa quyền",
    "hóa khoa",
    "hóa kỵ",
    "hoa loc",
    "hoa quyen",
    "hoa khoa",
    "hoa ky",
    "tuần",
    "tuan",
    "triệt",
    "triet",
    "kình dương",
    "kinh duong",
    "đà la",
    "da la",
    "địa không",
    "dia khong",
    "địa kiếp",
    "dia kiep",
    "thiên không",
    "thien khong",
    "thiên la",
    "thien la",
    "địa võng",
    "dia vong",
    "thái tuế",
    "thai tue",
}
MAX_STAR_DEFINITION_QUERIES = 3
MAX_MODIFIER_QUERIES = 3


class RoleQuery(TypedDict, total=False):
    evidence_role: str
    retrieval_intent: str
    query: str
    entities: list[dict[str, str]]
    target_houses: list[str]
    target_stars: list[str]


def build_role_queries(state: RAGState) -> list[RoleQuery]:
    plan = state.get("retrieval_plan") or {}
    chart_facts = state.get("chart_facts") or {}
    query_entities = entity_rows(state.get("query_entities") or [])
    required_roles = [str(role) for role in plan.get("required_evidence_roles") or [] if str(role) in EVIDENCE_ROLES]
    query = str(state.get("rewritten_query") or state.get("normalized_query") or state.get("query") or "")
    target_houses = unique_strings([*(plan.get("target_houses") or []), *(chart_facts.get("target_houses") or [])])
    target_stars = unique_strings([*(plan.get("target_stars") or []), *(chart_facts.get("target_stars") or [])])
    entity_houses = [entity["canonical_name"] for entity in query_entities if entity_type(entity) in HOUSE_ENTITY_TYPES]
    entity_stars = [entity["canonical_name"] for entity in query_entities if entity_type(entity) in STAR_ENTITY_TYPES]
    target_houses = unique_strings([*target_houses, *entity_houses])
    target_stars = unique_strings([*target_stars, *entity_stars])

    roles = list(required_roles)
    text = normalize_text(query)
    if any(term in text for term in MODIFIER_TERMS):
        append_unique(roles, "modifier_effect")
    family = str(plan.get("question_family") or state.get("question_family") or "")
    if family in {
        "menh_cuc_relation",
        "than_cu_interpretation",
        "menh_tam_hop",
        "menh_xung_chieu",
        "dai_van_interpretation",
        "topic_house_plus_relations",
        "synthesis_judgement",
    }:
        append_unique(roles, "relation_rule")
    if target_houses and target_stars:
        append_unique(roles, "combination_pattern")

    queries: list[RoleQuery] = []
    for role in roles:
        if role == "generic":
            continue
        role_queries = make_role_queries(role, query, target_houses, target_stars, query_entities)
        queries.extend(role_query for role_query in role_queries if role_query.get("query"))
    return dedupe_role_queries(queries)


def make_role_queries(
    role: str,
    original_query: str,
    target_houses: list[str],
    target_stars: list[str],
    query_entities: list[dict[str, str]],
) -> list[RoleQuery]:
    if role == "star_definition" and target_stars:
        stars = prioritized_target_stars(target_stars, include_modifiers=False, max_count=MAX_STAR_DEFINITION_QUERIES)
        if not stars:
            stars = target_stars[:MAX_STAR_DEFINITION_QUERIES]
        return [
            {
                "evidence_role": role,
                "retrieval_intent": "define_star",
                "query": f"{star} tính chất ý nghĩa luận giải",
                "entities": select_entities(query_entities, entity_types=STAR_ENTITY_TYPES, names=[star]) or name_entities([star], "Sao"),
                "target_houses": target_houses,
                "target_stars": [star],
            }
            for star in stars
        ]
    if role == "modifier_effect":
        modifiers = modifier_target_stars(target_stars)
        query_modifiers = extract_modifier_terms(original_query)
        if not modifiers:
            modifiers = query_modifiers
        if modifiers:
            houses = target_houses[:1]
            return [
                {
                    "evidence_role": role,
                    "retrieval_intent": "modifier_effect",
                    "query": f"{modifier} {' '.join(houses)} ảnh hưởng ý nghĩa khi đóng cung".strip(),
                    "entities": unique_entity_rows(
                        [
                            *select_entities(query_entities, entity_types=STAR_ENTITY_TYPES, names=[modifier]),
                            *select_entities(query_entities, entity_types=HOUSE_ENTITY_TYPES, names=houses),
                            *name_entities([modifier], "Sao"),
                            *name_entities(houses, "Cung"),
                        ]
                    ),
                    "target_houses": target_houses,
                    "target_stars": [modifier],
                }
                for modifier in modifiers[:MAX_MODIFIER_QUERIES]
            ]
    if role == "combination_pattern" and (target_houses or target_stars):
        stars = prioritized_target_stars(target_stars, include_modifiers=False, max_count=2)
        modifiers = modifier_target_stars(target_stars)[:1]
        houses = target_houses[:1]
        focus_terms = unique_strings([*stars, *modifiers, *houses])
        focus = " ".join(focus_terms) or original_query
        return [
            {
                "evidence_role": role,
                "retrieval_intent": "combination_pattern",
                "query": f"{focus} phối hợp kết hợp đồng cung luận giải",
                "entities": unique_entity_rows(
                    [
                        *select_entities(query_entities, entity_types=STAR_ENTITY_TYPES, names=[*stars, *modifiers]),
                        *select_entities(query_entities, entity_types=HOUSE_ENTITY_TYPES, names=houses),
                        *name_entities([*stars, *modifiers], "Sao"),
                        *name_entities(houses, "Cung"),
                    ]
                )
                or query_entities,
                "target_houses": target_houses,
                "target_stars": unique_strings([*stars, *modifiers]),
            }
        ]
    role_query = make_role_query(role, original_query, target_houses, target_stars, query_entities)
    return [role_query] if role_query else []


def make_role_query(
    role: str,
    original_query: str,
    target_houses: list[str],
    target_stars: list[str],
    query_entities: list[dict[str, str]],
) -> RoleQuery | None:
    if role == "house_scope":
        house = target_houses[0] if target_houses else "cung"
        return {
            "evidence_role": role,
            "retrieval_intent": "house_scope",
            "query": f"Cung {house} ý nghĩa phạm vi luận giải",
            "entities": select_entities(query_entities, entity_types=HOUSE_ENTITY_TYPES) or name_entities(target_houses, "Cung"),
            "target_houses": target_houses,
            "target_stars": target_stars,
        }
    if role == "star_definition":
        star = target_stars[0] if target_stars else "sao"
        return {
            "evidence_role": role,
            "retrieval_intent": "define_star",
            "query": f"{star} tính chất ý nghĩa luận giải",
            "entities": select_entities(query_entities, entity_types=STAR_ENTITY_TYPES) or name_entities(target_stars, "Sao"),
            "target_houses": target_houses,
            "target_stars": target_stars,
        }
    if role == "modifier_effect":
        focus = " ".join([*modifier_target_stars(target_stars)[:1], *extract_modifier_terms(original_query)[:1]]).strip() or original_query
        return {
            "evidence_role": role,
            "retrieval_intent": "modifier_effect",
            "query": f"{focus} ảnh hưởng ý nghĩa khi đóng cung",
            "entities": query_entities,
            "target_houses": target_houses,
            "target_stars": target_stars,
        }
    if role == "relation_rule":
        focus = " ".join(unique_strings([*target_houses, *target_stars])) or original_query
        return {
            "evidence_role": role,
            "retrieval_intent": "relation_rule",
            "query": f"{focus} quan hệ tam hợp xung chiếu sinh khắc quy tắc luận giải",
            "entities": query_entities,
            "target_houses": target_houses,
            "target_stars": target_stars,
        }
    if role == "combination_pattern":
        focus = " ".join(unique_strings([*target_stars, *target_houses])) or original_query
        return {
            "evidence_role": role,
            "retrieval_intent": "combination_pattern",
            "query": f"{focus} phối hợp kết hợp đồng cung luận giải",
            "entities": query_entities,
            "target_houses": target_houses,
            "target_stars": target_stars,
        }
    return None


def annotate_candidate_role(candidate: dict[str, Any], role: str, intent: str, *, role_query: str | None = None) -> dict[str, Any]:
    item = dict(candidate)
    item["evidence_role"] = role
    roles = candidate_roles(item)
    append_unique(roles, role)
    item["evidence_roles"] = roles
    item["retrieval_intent"] = intent
    if role_query:
        item["role_query"] = role_query
    return item


def candidate_roles(candidate: dict[str, Any]) -> list[str]:
    roles: list[str] = []
    raw_roles = candidate.get("evidence_roles") or []
    if isinstance(raw_roles, str):
        raw_roles = [raw_roles]
    for role in raw_roles:
        append_unique(roles, str(role))
    raw_role = candidate.get("evidence_role") or candidate.get("retrieval_intent")
    if raw_role:
        append_unique(roles, str(raw_role))
    return roles or [GENERIC_EVIDENCE_ROLE]


def merge_candidate_role_metadata(existing: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
    roles = unique_strings([*candidate_roles(existing), *candidate_roles(incoming)])
    existing["evidence_roles"] = roles
    primary = next((role for role in roles if role != GENERIC_EVIDENCE_ROLE), roles[0] if roles else GENERIC_EVIDENCE_ROLE)
    existing["evidence_role"] = primary
    if incoming.get("retrieval_intent") and (not existing.get("retrieval_intent") or existing.get("retrieval_intent") == "generic_query"):
        existing["retrieval_intent"] = incoming.get("retrieval_intent")
    if incoming.get("role_query") and not existing.get("role_query"):
        existing["role_query"] = incoming.get("role_query")
    return existing


def candidate_counts_by_role(candidates: Iterable[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for candidate in candidates:
        for role in candidate_roles(candidate):
            counts[role] = counts.get(role, 0) + 1
    return dict(sorted(counts.items()))


def role_query_summary(role_queries: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "evidence_role": query.get("evidence_role"),
            "retrieval_intent": query.get("retrieval_intent"),
            "entity_count": len(query.get("entities") or []),
        }
        for query in role_queries
    ]


def graph_mode_for_role(role: str, planner_mode: dict[str, Any]) -> dict[str, Any]:
    if role in ROLE_ENTITY_ANY:
        return {"mode": "entity_any", "min_hit_count": 1}
    if role == "modifier_effect":
        return dict(planner_mode) if str(planner_mode.get("mode") or "") == "min_hit_count" else {"mode": "entity_any", "min_hit_count": 1}
    if role in ROLE_PLANNER_GRAPH_MODE:
        return dict(planner_mode)
    return {"mode": "entity_any", "min_hit_count": 1}


def entity_rows(values: Iterable[dict[str, Any]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for entity in values:
        canonical_name = str(entity.get("canonical_name") or "").strip()
        etype = str(entity.get("entity_type") or "").strip()
        if not canonical_name or not etype:
            continue
        key = (canonical_name, etype)
        if key in seen:
            continue
        seen.add(key)
        rows.append({"canonical_name": canonical_name, "entity_type": etype})
    return rows


def select_entities(values: list[dict[str, str]], *, entity_types: set[str], names: list[str] | None = None) -> list[dict[str, str]]:
    normalized_names = {normalize_text(name) for name in names or [] if str(name).strip()}
    return [
        entity
        for entity in values
        if entity_type(entity) in entity_types
        and (not normalized_names or normalize_text(entity.get("canonical_name")) in normalized_names)
    ]


def name_entities(names: list[str], entity_type_value: str) -> list[dict[str, str]]:
    return [{"canonical_name": name, "entity_type": entity_type_value} for name in unique_strings(names)]


def entity_type(entity: dict[str, Any]) -> str:
    return str(entity.get("entity_type") or "").strip().casefold()


def dedupe_role_queries(queries: list[RoleQuery]) -> list[RoleQuery]:
    deduped: list[RoleQuery] = []
    seen: set[tuple[str, str]] = set()
    for query in queries:
        key = (str(query.get("evidence_role") or ""), normalize_text(query.get("query")))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(query)
    return deduped


def prioritized_target_stars(target_stars: list[str], *, include_modifiers: bool, max_count: int) -> list[str]:
    stars = [star for star in target_stars if include_modifiers or not is_modifier_like_star(star)]
    return unique_strings(stars)[:max_count]


def modifier_target_stars(target_stars: list[str]) -> list[str]:
    return unique_strings([star for star in target_stars if is_modifier_like_star(star)])


def is_modifier_like_star(value: Any) -> bool:
    text = normalize_text(value)
    if not text:
        return False
    return text in MODIFIER_STAR_NAMES or text.startswith("l.") or text.startswith("lưu ") or text.startswith("luu ")


def unique_entity_rows(values: Iterable[dict[str, Any]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for entity in values:
        canonical_name = str(entity.get("canonical_name") or "").strip()
        etype = str(entity.get("entity_type") or "").strip()
        if not canonical_name or not etype:
            continue
        key = (normalize_text(canonical_name), etype.casefold())
        if key in seen:
            continue
        seen.add(key)
        rows.append({"canonical_name": canonical_name, "entity_type": etype})
    return rows


def extract_modifier_terms(query: str) -> list[str]:
    text = normalize_text(query)
    return unique_strings([term for term in MODIFIER_TERMS if term in text])


def unique_strings(values: Iterable[Any]) -> list[str]:
    result: list[str] = []
    for value in values:
        append_unique(result, str(value).strip())
    return result


def append_unique(values: list[str], value: str) -> None:
    if value and value not in values:
        values.append(value)


def normalize_text(value: Any) -> str:
    return " ".join(str(value or "").casefold().split())