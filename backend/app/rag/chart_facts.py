from __future__ import annotations

import re
from typing import Any

from app.rag.house_ontology import canonical_house_name, find_house_triad, triads_for_target_houses


EXTRACTOR_VERSION = "w6_rag_03_v2"
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
    normalized["summary"] = enrich_summary_with_derived_chart_values(normalized.get("summary") or {}, houses)
    target_houses = find_target_houses(normalized, houses, query_entities or [], retrieval_plan or {})
    target_stars = find_target_stars(houses, query_entities or [], retrieval_plan or {}, target_houses=target_houses)
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
    raw_data = chart_data.get("raw_data") if isinstance(chart_data.get("raw_data"), dict) else {}
    personal_info = first_dict(
        chart_data.get("personal_info"),
        chart_data.get("personalInfo"),
        metadata.get("personal_info"),
        metadata.get("personalInfo"),
        raw_data.get("personalInfo"),
        raw_data.get("personal_info"),
    )
    destiny_info = first_dict(
        chart_data.get("destiny_info"),
        chart_data.get("destinyInfo"),
        metadata.get("destiny_info"),
        metadata.get("destinyInfo"),
        raw_data.get("destinyInfo"),
        raw_data.get("destiny_info"),
    )
    can_chi_info = personal_info.get("canChi") if isinstance(personal_info.get("canChi"), dict) else {}
    birth_date = first_value(metadata.get("birth_date"), chart_data.get("birth_date"))
    birth_year = first_value(
        chart_data.get("birth_year"),
        metadata.get("birth_year"),
        nested_get(personal_info, "solarDate", "year"),
        raw_data.get("nam"),
        parse_year(birth_date),
    )
    nam_xem_han = first_value(
        metadata.get("nam_xem_han"),
        chart_data.get("nam_xem_han"),
        raw_data.get("namXemHan"),
        raw_data.get("nam_xem_han"),
    )
    am_duong = first_value(
        personal_info.get("amDuong"),
        personal_info.get("am_duong"),
        metadata.get("am_duong"),
        chart_data.get("am_duong"),
    )
    gender = first_value(
        personal_info.get("gender"),
        raw_data.get("gioiTinh"),
        metadata.get("gender"),
        chart_data.get("gender"),
    )
    summary = compact_dict(
        {
            "menh_position": first_value(
                chart_data.get("menh_position"),
                metadata.get("menh_position"),
                raw_data.get("tenCungMenh"),
                destiny_info.get("tenCungMenh"),
            ),
            "than_position": first_value(
                chart_data.get("than_position"),
                metadata.get("than_position"),
                raw_data.get("tenCungThan"),
                destiny_info.get("tenCungThan"),
            ),
            "ban_menh": first_value(
                chart_data.get("ban_menh"),
                chart_data.get("banMenh"),
                metadata.get("ban_menh"),
                destiny_info.get("banMenh"),
                destiny_info.get("ban_menh"),
            ),
            "ngu_hanh_ban_menh": first_value(
                chart_data.get("ngu_hanh_ban_menh"),
                metadata.get("ngu_hanh_ban_menh"),
                destiny_info.get("menhNguHanh"),
                destiny_info.get("menh_ngu_hanh"),
            ),
            "cuc": first_value(
                chart_data.get("cuc"),
                chart_data.get("cục"),
                metadata.get("cuc"),
                destiny_info.get("cucMenh"),
                destiny_info.get("cuc_menh"),
            ),
            "cuc_ngu_hanh": first_value(destiny_info.get("cucNguHanh"), destiny_info.get("cuc_ngu_hanh")),
            "menh_cuc_tuong_quan": first_value(destiny_info.get("menhCucTuongQuan"), destiny_info.get("menh_cuc_tuong_quan")),
            "gender": gender,
            "am_duong": am_duong,
            "dai_van_direction": infer_dai_van_direction(am_duong),
            "birth_year": parse_int(birth_year),
            "can_chi_nam": first_value(can_chi_info.get("year"), raw_data.get("canChiNam"), chart_data.get("can_chi_nam")),
            "nam_xem_han": parse_int(nam_xem_han),
            "can_chi_nam_xem": first_value(metadata.get("can_chi_nam_xem"), raw_data.get("canChiNamXem"), chart_data.get("can_chi_nam_xem")),
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
        attributes = palace.get("attributes") if isinstance(palace.get("attributes"), dict) else {}
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
                    "earthly_branch": palace.get("earthly_branch") or palace.get("branch") or palace.get("dia_chi") or attributes.get("dia_chi"),
                    "is_menh": (palace.get("name") or palace_name) == "Mệnh",
                    "is_than_resident": bool(palace.get("is_than_resident") or palace.get("cungThan") or attributes.get("has_than")),
                    "position": palace.get("position") or attributes.get("position"),
                    "house_element": palace.get("house_element") or palace.get("element") or attributes.get("element"),
                    "yin_yang": palace.get("yin_yang") or palace.get("am_duong") or attributes.get("yin_yang"),
                    "dai_han_age": palace.get("dai_han_age") or palace.get("dai_han") or attributes.get("dai_han_age") or attributes.get("dai_han"),
                    "tieu_han": attributes.get("tieu_han"),
                    "luu_nien_dai_van": attributes.get("luu_nien_dai_van"),
                    "trang_sinh": attributes.get("trang_sinh"),
                    "tuan_khong": bool(palace.get("tuan_khong") or attributes.get("tuan_khong")),
                    "triet_khong": bool(palace.get("triet_khong") or attributes.get("triet_khong")),
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
                    "is_menh": bool(item.get("is_menh") or item.get("cungMenh") or item.get("cungChu") == "Mệnh"),
                    "is_than_resident": bool(item.get("is_than_resident") or item.get("cungThan")),
                    "position": item.get("position") or item.get("cungSo"),
                    "house_element": item.get("house_element") or item.get("hanhCung"),
                    "yin_yang": item.get("yin_yang") or item.get("amDuong"),
                    "dai_han_age": item.get("dai_han_age") or item.get("daiHan") or item.get("tuoiDaiHan"),
                    "tieu_han": item.get("tieuHan"),
                    "luu_nien_dai_van": item.get("luuNienDaiVan"),
                    "trang_sinh": item.get("trangSinh"),
                    "tuan_khong": bool(item.get("tuan_khong") or item.get("tuanKhong")),
                    "triet_khong": bool(item.get("triet_khong") or item.get("trietKhong")),
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
    if "dai_van" in set(retrieval_plan.get("chart_fact_intents") or []):
        summary = normalized_chart.get("summary") if isinstance(normalized_chart.get("summary"), dict) else {}
        current_dai_van_house = str(summary.get("current_dai_van_house") or "").strip()
        if current_dai_van_house:
            append_unique(targets, current_dai_van_house)
        menh_house = next((house for house in houses if house.get("is_menh")), None)
        if menh_house and menh_house.get("house_name"):
            append_unique(targets, str(menh_house.get("house_name")))
        than_house = next((house for house in houses if house.get("is_than_resident")), None)
        if than_house and than_house.get("house_name"):
            append_unique(targets, str(than_house.get("house_name")))
    return targets


def find_target_stars(
    houses: list[dict[str, Any]],
    query_entities: list[dict[str, Any]],
    retrieval_plan: dict[str, Any],
    *,
    target_houses: list[str] | None = None,
) -> list[str]:
    targets: list[str] = [str(value) for value in retrieval_plan.get("target_stars") or [] if str(value).strip()]
    for entity in query_entities:
        if str(entity.get("entity_type") or "").casefold() in {"sao", "chinh_tinh", "phu_tinh", "star", "chính tinh", "phụ tinh"}:
            append_unique(targets, str(entity.get("canonical_name") or ""))
    if retrieval_plan.get("chart_fact_intents") and not targets:
        effective_target_houses = target_houses or list(retrieval_plan.get("target_houses") or [])
        for house in houses:
            if not should_include_house(house, effective_target_houses, []):
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
            "dai_han_age_range": format_dai_han_age_range(house.get("dai_han_age")),
            "is_current_dai_van": is_current_dai_van_house(house, normalized_chart.get("summary") or {}),
            "tieu_han": house.get("tieu_han"),
            "luu_nien_dai_van": house.get("luu_nien_dai_van"),
            "trang_sinh": house.get("trang_sinh"),
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
        "gender": "Giới tính",
        "am_duong": "Âm dương",
        "dai_van_direction": "Chiều đại vận",
        "birth_year": "Năm sinh",
        "can_chi_nam": "Can Chi năm sinh",
        "nam_xem_han": "Năm xem hạn",
        "can_chi_nam_xem": "Can Chi năm xem hạn",
        "tuoi_xem_han": "Tuổi xem hạn",
        "ban_menh": "Bản Mệnh",
        "ngu_hanh_ban_menh": "Ngũ hành Bản Mệnh",
        "cuc": "Cục",
        "cuc_ngu_hanh": "Ngũ hành Cục",
        "menh_cuc_tuong_quan": "Mệnh-Cục tương quan",
        "current_dai_van_house": "Cung đại vận hiện tại",
        "current_dai_van_age_range": "Khoảng tuổi đại vận hiện tại",
    }
    for key, label in labels.items():
        if summary.get(key) not in (None, "", []):
            lines.append(f"- {label}: {summary.get(key)}")
    for house in chart_facts.get("house_facts") or []:
        lines.append("")
        lines.append(f"[CUNG {house.get('house_name') or 'Không rõ'}]")
        if house.get("is_current_dai_van"):
            lines.append("- Vai trò: cung đại vận hiện tại")
        if house.get("earthly_branch"):
            lines.append(f"- Địa chi: {house.get('earthly_branch')}")
        if house.get("house_element"):
            lines.append(f"- Ngũ hành cung: {house.get('house_element')}")
        if house.get("yin_yang"):
            lines.append(f"- Âm dương cung: {house.get('yin_yang')}")
        if house.get("dai_han_age_range") or house.get("dai_han_age"):
            lines.append(f"- Đại hạn: {house.get('dai_han_age_range') or house.get('dai_han_age')}")
        if house.get("trang_sinh"):
            lines.append(f"- Vòng Tràng Sinh: {house.get('trang_sinh')}")
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
    if any(normalize_text(target) == "thân" for target in target_houses) and house.get("is_than_resident"):
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


def enrich_summary_with_derived_chart_values(summary: dict[str, Any], houses: list[dict[str, Any]]) -> dict[str, Any]:
    enriched = dict(summary or {})
    birth_year = parse_int(enriched.get("birth_year"))
    nam_xem_han = parse_int(enriched.get("nam_xem_han"))
    if birth_year is not None:
        enriched["birth_year"] = birth_year
    if nam_xem_han is not None:
        enriched["nam_xem_han"] = nam_xem_han
    if birth_year is not None and nam_xem_han is not None:
        enriched["tuoi_xem_han"] = max(1, nam_xem_han - birth_year + 1)

    current_house = current_dai_van_house(houses, enriched)
    if current_house:
        enriched["current_dai_van_house"] = current_house.get("house_name") or current_house.get("earthly_branch")
        range_label = format_dai_han_age_range(current_house.get("dai_han_age"))
        if range_label:
            enriched["current_dai_van_age_range"] = range_label
    return compact_dict(enriched)


def current_dai_van_house(houses: list[dict[str, Any]], summary: dict[str, Any]) -> dict[str, Any] | None:
    tuoi_xem_han = parse_int(summary.get("tuoi_xem_han"))
    if tuoi_xem_han is None:
        birth_year = parse_int(summary.get("birth_year"))
        nam_xem_han = parse_int(summary.get("nam_xem_han"))
        if birth_year is not None and nam_xem_han is not None:
            tuoi_xem_han = max(1, nam_xem_han - birth_year + 1)
    if tuoi_xem_han is None:
        return None

    best_house: dict[str, Any] | None = None
    best_start: int | None = None
    for house in houses:
        start_age = parse_int(house.get("dai_han_age"))
        if start_age is None:
            continue
        if start_age <= tuoi_xem_han <= start_age + 9:
            return house
        if start_age <= tuoi_xem_han and (best_start is None or start_age > best_start):
            best_start = start_age
            best_house = house
    return best_house


def is_current_dai_van_house(house: dict[str, Any], summary: dict[str, Any]) -> bool:
    current = normalize_text(summary.get("current_dai_van_house"))
    if current:
        return current in {normalize_text(house.get("house_name")), normalize_text(house.get("earthly_branch"))}

    tuoi_xem_han = parse_int(summary.get("tuoi_xem_han"))
    start_age = parse_int(house.get("dai_han_age"))
    return tuoi_xem_han is not None and start_age is not None and start_age <= tuoi_xem_han <= start_age + 9


def format_dai_han_age_range(value: Any) -> str | None:
    start_age = parse_int(value)
    if start_age is None:
        return str(value).strip() if value not in (None, "") else None
    return f"{start_age}-{start_age + 9} tuổi"


def infer_dai_van_direction(am_duong: Any) -> str | None:
    normalized = normalize_text(am_duong)
    if not normalized:
        return None
    if "dương nam" in normalized or "duong nam" in normalized or "âm nữ" in normalized or "am nữ" in normalized or "am nu" in normalized:
        return "thuận"
    if "âm nam" in normalized or "am nam" in normalized or "dương nữ" in normalized or "duong nữ" in normalized or "duong nu" in normalized:
        return "nghịch"
    return None


def first_dict(*values: Any) -> dict[str, Any]:
    for value in values:
        if isinstance(value, dict):
            return value
    return {}


def first_value(*values: Any) -> Any:
    for value in values:
        if value not in (None, "", []):
            return value
    return None


def nested_get(payload: Any, *keys: str) -> Any:
    current = payload
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def parse_year(value: Any) -> int | None:
    if isinstance(value, int):
        return value if 1 <= value <= 9999 else None
    if value in (None, ""):
        return None
    match = re.search(r"(?<!\d)(\d{4})(?!\d)", str(value))
    return parse_int(match.group(1)) if match else None


def parse_int(value: Any) -> int | None:
    if isinstance(value, bool) or value in (None, ""):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value) if value.is_integer() else None
    match = re.search(r"-?\d+", str(value))
    if not match:
        return None
    try:
        return int(match.group(0))
    except ValueError:
        return None


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