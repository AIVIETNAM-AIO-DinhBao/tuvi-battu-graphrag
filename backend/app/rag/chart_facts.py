from __future__ import annotations

from typing import Any

from app.rag.house_ontology import canonical_house_name, find_house_triad, triads_for_target_houses


EXTRACTOR_VERSION = "w6_rag_03_v1"
SPECIAL_STATE_TERMS = {"Tuần", "Triệt", "Tuần Không", "Triệt Không"}
MAJOR_STAR_NAMES = {
    "tử vi",
    "thiên cơ",
    "thái dương",
    "vũ khúc",
    "thiên đồng",
    "liêm trinh",
    "thiên phủ",
    "thái âm",
    "tham lang",
    "cự môn",
    "thiên tướng",
    "thiên lương",
    "thất sát",
    "phá quân",
}


def extract_chart_facts(
    chart_data: dict[str, Any],
    query_entities: list[dict[str, Any]] | None = None,
    retrieval_plan: dict[str, Any] | None = None,
) -> dict[str, Any]:
    normalized = normalize_chart_data(chart_data)
    houses = extract_houses(normalized)
    target_houses = find_target_houses(normalized, houses, query_entities or [], retrieval_plan or {})
    target_stars = find_target_stars(houses, query_entities or [], retrieval_plan or {})
    selected_houses = [build_house_fact(house, normalized) for house in houses if should_include_house(house, target_houses, target_stars)]
    relations = build_relation_placeholders(retrieval_plan or {}, target_houses)
    claims_verified, unverified_claims = verify_fact_claims(selected_houses, target_houses, target_stars)
    warnings: list[str] = list(normalized.get("warnings") or [])
    if normalized["chart_available"] and not houses:
        warnings.append("no_houses_detected")
    return {
        "extractor_version": EXTRACTOR_VERSION,
        "chart_available": normalized["chart_available"],
        "chart_schema_detected": normalized["chart_schema_detected"],
        "target_houses": target_houses,
        "target_stars": target_stars,
        "summary": normalized["summary"],
        "house_facts": selected_houses,
        "relations": relations,
        "claims_verified": claims_verified,
        "unverified_claims": unverified_claims,
        "warnings": warnings,
    }


def normalize_chart_data(chart_data: dict[str, Any]) -> dict[str, Any]:
    warnings: list[str] = []
    if not isinstance(chart_data, dict) or not chart_data:
        return {
            "raw": {},
            "chart_available": False,
            "chart_schema_detected": "unknown",
            "summary": {},
            "warnings": ["chart_data_missing_or_empty"],
        }

    schema = "unknown"
    if isinstance(chart_data.get("houses"), list) or chart_data.get("schema_role") == "chart_repr":
        schema = "chart_repr_v2"
    elif isinstance(chart_data.get("palaces"), dict):
        schema = "palaces_v1"
    elif any(key in chart_data for key in ("thap_nhi_cung", "cung", "dia_ban")):
        schema = "legacy"
    else:
        warnings.append("chart_schema_unknown")

    metadata = chart_data.get("metadata") if isinstance(chart_data.get("metadata"), dict) else {}
    summary = compact_dict(
        {
            "menh_position": chart_data.get("menh_position") or metadata.get("menh_position"),
            "than_position": chart_data.get("than_position") or metadata.get("than_position"),
            "ban_menh": chart_data.get("ban_menh") or chart_data.get("banMenh") or metadata.get("ban_menh"),
            "ngu_hanh_ban_menh": chart_data.get("ngu_hanh_ban_menh") or metadata.get("ngu_hanh_ban_menh"),
            "cuc": chart_data.get("cuc") or chart_data.get("cục") or metadata.get("cuc"),
        }
    )
    return {
        "raw": chart_data,
        "chart_available": True,
        "chart_schema_detected": schema,
        "summary": summary,
        "warnings": warnings,
    }


def extract_houses(normalized_chart: dict[str, Any]) -> list[dict[str, Any]]:
    raw = normalized_chart.get("raw") or {}
    schema = normalized_chart.get("chart_schema_detected")
    if schema == "chart_repr_v2":
        return extract_houses_from_chart_repr(raw, normalized_chart.get("summary") or {})
    if schema == "palaces_v1":
        return extract_houses_from_palaces(raw)
    if schema == "legacy":
        return extract_houses_from_legacy(raw)
    return []


def extract_houses_from_chart_repr(raw: dict[str, Any], summary: dict[str, Any]) -> list[dict[str, Any]]:
    houses: list[dict[str, Any]] = []
    for item in raw.get("houses") or []:
        if not isinstance(item, dict):
            continue
        house_name = item.get("house_name") or item.get("name") or item.get("cung")
        earthly_branch = item.get("earthly_branch") or item.get("branch") or item.get("dia_chi")
        houses.append(
            compact_dict(
                {
                    "house_name": house_name,
                    "earthly_branch": earthly_branch,
                    "is_menh": bool(house_name == "Mệnh" or earthly_branch == summary.get("menh_position")),
                    "is_than_resident": bool(item.get("is_than_resident") or item.get("cungThan") or earthly_branch == summary.get("than_position")),
                    "house_element": item.get("house_element") or item.get("element"),
                    "yin_yang": item.get("yin_yang") or item.get("am_duong"),
                    "dai_han_age": item.get("dai_han_age") or item.get("dai_han") or item.get("daiHan"),
                    "tuan_khong": bool(item.get("tuan_khong") or item.get("tuan") or item.get("tuần")),
                    "triet_khong": bool(item.get("triet_khong") or item.get("triet") or item.get("triệt")),
                    **split_star_groups(
                        normalize_star_list(item.get("major_stars") or item.get("chinh_tinh") or item.get("chinhTinh")),
                        normalize_star_list(item.get("aux_stars") or item.get("phu_tinh") or item.get("phuTinh") or item.get("stars")),
                    ),
                }
            )
        )
    return houses


def extract_houses_from_palaces(raw: dict[str, Any]) -> list[dict[str, Any]]:
    palaces = raw.get("palaces") or {}
    star_index = raw.get("stars") if isinstance(raw.get("stars"), dict) else {}
    houses: list[dict[str, Any]] = []
    for palace_name, palace in palaces.items():
        if not isinstance(palace, dict):
            continue
        star_names = palace.get("stars") or palace.get("danh_sach_sao") or []
        normalized_stars = []
        for star_name in star_names:
            star_detail = star_index.get(star_name) if isinstance(star_index, dict) else None
            payload = {"name": star_name}
            if isinstance(star_detail, dict):
                payload.update({"status": star_detail.get("brightness") or star_detail.get("status"), "category": star_detail.get("category")})
            normalized_stars.append(payload)
        houses.append(
            compact_dict(
                {
                    "house_name": palace.get("name") or palace_name,
                    "earthly_branch": palace.get("earthly_branch") or palace.get("branch") or palace.get("dia_chi"),
                    "is_menh": (palace.get("name") or palace_name) == "Mệnh",
                    "is_than_resident": bool(palace.get("is_than_resident") or palace.get("cungThan")),
                    **split_star_groups([], normalize_star_list(normalized_stars)),
                    "attributes": palace.get("attributes") if isinstance(palace.get("attributes"), dict) else None,
                }
            )
        )
    return houses


def extract_houses_from_legacy(raw: dict[str, Any]) -> list[dict[str, Any]]:
    container = raw.get("thap_nhi_cung") or raw.get("dia_ban") or raw.get("cung") or []
    if isinstance(container, dict):
        iterable = container.values()
    else:
        iterable = container if isinstance(container, list) else []
    houses: list[dict[str, Any]] = []
    for item in iterable:
        if not isinstance(item, dict):
            continue
        houses.append(
            compact_dict(
                {
                    "house_name": item.get("house_name") or item.get("cungTen") or item.get("ten") or item.get("name"),
                    "earthly_branch": item.get("earthly_branch") or item.get("diaChi") or item.get("chi"),
                    "is_menh": bool(item.get("is_menh") or item.get("cungMenh")),
                    "is_than_resident": bool(item.get("is_than_resident") or item.get("cungThan")),
                    **split_star_groups(
                        normalize_star_list(item.get("major_stars") or item.get("chinh_tinh") or item.get("chinhTinh")),
                        normalize_star_list(item.get("aux_stars") or item.get("phu_tinh") or item.get("danh_sach_sao") or item.get("sao") or item.get("stars")),
                    ),
                }
            )
        )
    return houses


def find_target_houses(
    normalized_chart: dict[str, Any],
    houses: list[dict[str, Any]],
    query_entities: list[dict[str, Any]],
    retrieval_plan: dict[str, Any],
) -> list[str]:
    targets: list[str] = []
    for value in retrieval_plan.get("target_houses") or []:
        canonical = canonical_house_name(str(value)) or str(value).strip()
        append_unique(targets, canonical)
    # Nếu planner đã khóa bộ cung từ câu hỏi tam hợp tường minh, không trộn thêm
    # entity nhiễu. Trường hợp người dùng hỏi "tam hợp Phúc-Phối-Di" từng bị
    # runtime entity extraction thêm nhầm Phụ Mẫu; khóa ở đây giúp chart facts và
    # context chỉ bám đúng ba cung người dùng nêu.
    if retrieval_plan.get("explicit_house_triad") or retrieval_plan.get("target_houses_source") == "query_alias_parser":
        return targets
    for entity in query_entities:
        if str(entity.get("entity_type") or "").casefold() == "cung":
            canonical = canonical_house_name(str(entity.get("canonical_name") or "")) or str(entity.get("canonical_name") or "")
            append_unique(targets, canonical)
    if "Mệnh" in targets:
        menh_house = next((house for house in houses if house.get("is_menh")), None)
        if menh_house and menh_house.get("house_name"):
            append_unique(targets, str(menh_house.get("house_name")))
    return targets


def find_target_stars(houses: list[dict[str, Any]], query_entities: list[dict[str, Any]], retrieval_plan: dict[str, Any]) -> list[str]:
    targets: list[str] = [str(value) for value in retrieval_plan.get("target_stars") or [] if str(value).strip()]
    for entity in query_entities:
        if str(entity.get("entity_type") or "").casefold() in {"sao", "chinh_tinh", "phu_tinh", "star", "chính tinh", "phụ tinh"}:
            append_unique(targets, str(entity.get("canonical_name") or ""))
    if retrieval_plan.get("chart_fact_intents") and not targets:
        for house in houses:
            if not should_include_house(house, list(retrieval_plan.get("target_houses") or []), []):
                continue
            for star in (house.get("major_stars") or []) + (house.get("aux_stars") or []):
                append_unique(targets, str(star.get("name") or ""))
    return targets


def build_house_fact(house: dict[str, Any], normalized_chart: dict[str, Any]) -> dict[str, Any]:
    return compact_dict(
        {
            "house_name": house.get("house_name"),
            "earthly_branch": house.get("earthly_branch"),
            "is_menh": bool(house.get("is_menh")),
            "is_than_resident": bool(house.get("is_than_resident")),
            "house_element": house.get("house_element"),
            "yin_yang": house.get("yin_yang"),
            "dai_han_age": house.get("dai_han_age"),
            "tuan_khong": bool(house.get("tuan_khong")),
            "triet_khong": bool(house.get("triet_khong")),
            "major_stars": house.get("major_stars") or [],
            "aux_stars": house.get("aux_stars") or [],
        }
    )


def build_chart_fact_context_block(chart_facts: dict[str, Any]) -> str:
    if not isinstance(chart_facts, dict) or not chart_facts.get("chart_available"):
        return ""
    lines = ["[CHART] Dữ kiện lá số đã trích xuất"]
    summary = chart_facts.get("summary") or {}
    labels = {
        "menh_position": "Mệnh",
        "than_position": "Thân",
        "ban_menh": "Bản Mệnh",
        "ngu_hanh_ban_menh": "Ngũ hành Bản Mệnh",
        "cuc": "Cục",
    }
    for key, label in labels.items():
        if summary.get(key) not in (None, "", []):
            lines.append(f"- {label}: {summary.get(key)}")
    for house in chart_facts.get("house_facts") or []:
        lines.append("")
        lines.append(f"[CUNG {house.get('house_name') or 'Không rõ'}]")
        if house.get("earthly_branch"):
            lines.append(f"- Địa chi: {house.get('earthly_branch')}")
        major = format_star_names(house.get("major_stars") or [])
        aux = format_star_names(house.get("aux_stars") or [])
        if major:
            lines.append(f"- Chính tinh: {major}")
        if aux:
            lines.append(f"- Phụ tinh: {aux}")
        lines.append(f"- Tuần/Triệt: {format_tuan_triet(house)}")
        lines.append(f"- Thân cư tại cung này: {'có' if house.get('is_than_resident') else 'không'}")
    relation_lines = format_relation_lines(chart_facts.get("relations") or [])
    if relation_lines:
        lines.append("")
        lines.append("[LIÊN HỆ CUNG]")
        lines.extend(relation_lines)
    return "\n".join(lines).strip()


def should_include_house(house: dict[str, Any], target_houses: list[str], target_stars: list[str]) -> bool:
    if not target_houses and not target_stars:
        return bool(house.get("is_menh"))
    names = {normalize_text(house.get("house_name")), normalize_text(house.get("earthly_branch"))}
    if any(normalize_text(target) == "mệnh" for target in target_houses) and house.get("is_menh"):
        return True
    if any(normalize_text(target) in names for target in target_houses):
        return True
    star_names = {normalize_text(star.get("name")) for star in (house.get("major_stars") or []) + (house.get("aux_stars") or [])}
    return any(normalize_text(target) in star_names for target in target_stars)


def build_relation_placeholders(retrieval_plan: dict[str, Any], target_houses: list[str]) -> list[dict[str, Any]]:
    intents = set(retrieval_plan.get("chart_fact_intents") or [])
    relations: list[dict[str, Any]] = []
    if "tam_hop" in intents:
        explicit = retrieval_plan.get("explicit_house_triad") if isinstance(retrieval_plan.get("explicit_house_triad"), dict) else None
        if explicit:
            relations.append({**explicit, "type": "tam_hop"})
        else:
            known = find_house_triad(target_houses)
            if known:
                relations.append({"type": "tam_hop", **known})
            else:
                relations.extend({"type": "tam_hop", **triad} for triad in triads_for_target_houses(target_houses))
        if not relations:
            relations.append(
                {
                    "type": "tam_hop",
                    "anchor_house": target_houses[0] if target_houses else None,
                    "houses": target_houses,
                    "available": False,
                    "reason": "tam_hop_not_identified_from_target_houses",
                }
            )
    if "xung_chieu" in intents:
        relations.append(
            {
                "type": "xung_chieu",
                "anchor_house": target_houses[0] if target_houses else None,
                "houses": target_houses,
                "available": False,
                "reason": "xung_chieu_algorithm_not_enabled",
            }
        )
    return relations


def format_relation_lines(relations: list[dict[str, Any]]) -> list[str]:
    lines: list[str] = []
    for relation in relations:
        if not isinstance(relation, dict):
            continue
        relation_type = str(relation.get("type") or "").strip()
        houses = [str(value) for value in relation.get("houses") or [] if str(value).strip()]
        if relation_type == "tam_hop" and houses:
            status = "đã nhận diện" if relation.get("available") else f"chưa đủ thuật toán ({relation.get('reason')})"
            name = relation.get("name") or "-".join(houses)
            lines.append(f"- Tam hợp {name}: {', '.join(houses)}; trạng thái: {status}")
        elif relation_type:
            lines.append(f"- {relation_type}: {', '.join(houses) if houses else 'chưa xác định'}")
    return lines


def verify_fact_claims(house_facts: list[dict[str, Any]], target_houses: list[str], target_stars: list[str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    verified: list[dict[str, Any]] = []
    unverified: list[dict[str, Any]] = []
    house_names = {normalize_text(house.get("house_name")) for house in house_facts}
    has_menh_house = any(house.get("is_menh") for house in house_facts)
    for target in target_houses:
        record = {"claim": "target_house_exists", "value": target}
        if normalize_text(target) in house_names or (normalize_text(target) == "mệnh" and has_menh_house) or target == "Thân":
            verified.append({**record, "status": "verified"})
        else:
            unverified.append({**record, "status": "unverified"})
    star_names = {
        normalize_text(star.get("name"))
        for house in house_facts
        for star in (house.get("major_stars") or []) + (house.get("aux_stars") or [])
    }
    for target in target_stars:
        record = {"claim": "target_star_exists", "value": target}
        if normalize_text(target) in star_names:
            verified.append({**record, "status": "verified"})
        else:
            unverified.append({**record, "status": "unverified"})
    return verified, unverified


def normalize_star_list(value: Any) -> list[dict[str, Any]]:
    stars: list[dict[str, Any]] = []
    if not value:
        return stars
    iterable = value if isinstance(value, list) else [value]
    for item in iterable:
        if isinstance(item, str):
            stars.append({"name": item, "status": None})
        elif isinstance(item, dict):
            name = item.get("name") or item.get("ten") or item.get("star")
            if name:
                stars.append(compact_dict({"name": name, "status": item.get("status") or item.get("brightness"), "category": item.get("category")}))
    return stars


def split_star_groups(major_candidates: list[dict[str, Any]], aux_candidates: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Normalize major/auxiliary star groups using the canonical 14 major stars.

    Some upstream chart payloads provide a generic `stars` list or a wrong
    category. In particular `Thái Dương` may arrive as an auxiliary star. The RAG
    answer should never inherit that error, so this splitter promotes any of the
    14 chính tinh to `major_stars` and removes duplicates from `aux_stars`.
    """
    major: list[dict[str, Any]] = []
    aux: list[dict[str, Any]] = []
    for star in [*major_candidates, *aux_candidates]:
        name = str(star.get("name") or "").strip()
        if not name:
            continue
        target = major if is_major_star(star) else aux
        append_star_unique(target, star)
    major_names = {normalize_text(star.get("name")) for star in major}
    aux = [star for star in aux if normalize_text(star.get("name")) not in major_names]
    return {"major_stars": major, "aux_stars": aux}


def is_major_star(star: dict[str, Any]) -> bool:
    category = normalize_text(star.get("category"))
    name = normalize_text(star.get("name"))
    if category in {"chính tinh", "chinh tinh", "major", "major star"}:
        return True
    if category in {"phụ tinh", "phu tinh", "aux", "auxiliary", "minor"} and name not in MAJOR_STAR_NAMES:
        return False
    return name in MAJOR_STAR_NAMES


def append_star_unique(values: list[dict[str, Any]], star: dict[str, Any]) -> None:
    name = normalize_text(star.get("name"))
    if not name or any(normalize_text(existing.get("name")) == name for existing in values):
        return
    values.append(star)


def format_star_names(stars: list[dict[str, Any]]) -> str:
    labels = []
    for star in stars:
        name = star.get("name")
        if not name:
            continue
        status = star.get("status")
        labels.append(f"{name} ({status})" if status else str(name))
    return ", ".join(labels)


def format_tuan_triet(house: dict[str, Any]) -> str:
    values = []
    if house.get("tuan_khong"):
        values.append("Tuần")
    if house.get("triet_khong"):
        values.append("Triệt")
    return ", ".join(values) if values else "không"


def compact_dict(payload: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in payload.items() if value not in (None, "", [])}


def append_unique(values: list[str], value: str) -> None:
    if value and value not in values:
        values.append(value)


def normalize_text(value: Any) -> str:
    return " ".join(str(value or "").casefold().split())