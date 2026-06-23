#!/usr/bin/env python3
"""
Tu Vi data exporter for benchmark / RAG preparation.

Purpose
-------
Given birth date, birth time, gender, and optional name/label,
this script calls the existing TuViCalculator service in the repo,
then exports two data-oriented views:

1. chart_repr      : compact, deterministic, RAG-friendly chart view
2. chart_semantic  : semantic / retrieval-oriented chart view

Recommended usage
-----------------
Run this script from the repository root so it can import the existing
backend service layer.

Examples
--------
uu tien chay lenh nay nhe!
python tuvi_chart_exporter.py \
  --name "Nguyen Van A" \
  --birth-date 2005-03-09 \
  --birth-time 20:30 \
  --gender nam \
  --output-dir ./benchmark/tuvi_golden_dataset/charts/exports

cai nay de debug thoi
python tuvi_chart_exporter.py \
  --name "Nguyen Van A" \
  --birth-date 2005-03-09 \
  --birth-time 20:30 \
  --gender nam \
  --output-dir ./benchmark/tuvi_golden_dataset/charts/exports \
  --semantic-format both
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Import the existing calculator from the repo
# ---------------------------------------------------------------------------
try:
    from backend.app.services.tuvi_calculator import TuViCalculator  # repo-root execution
except Exception:
    try:
        from app.services.tuvi_calculator import TuViCalculator  # backend cwd execution
    except Exception as exc:  # pragma: no cover
        raise ImportError(
            "Cannot import TuViCalculator. Run this script from the repo root, "
            "or adjust the import path to your project structure."
        ) from exc


# ---------------------------------------------------------------------------
# Canonical vocabularies
# ---------------------------------------------------------------------------
BRANCH_ORDER = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]
ELEMENTS = {"Kim", "Mộc", "Thủy", "Hỏa", "Thổ"}

CANONICAL_HOUSE_NAMES = [
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

HOUSE_ALIAS_MAP = {
    "menh": "Mệnh",
    "phu mau": "Phụ Mẫu",
    "phuc duc": "Phúc Đức",
    "dien trach": "Điền Trạch",
    "quan loc": "Quan Lộc",
    "no boc": "Nô Bộc",
    "thien di": "Thiên Di",
    "tat ach": "Tật Ách",
    "tai bach": "Tài Bạch",
    "tu tuc": "Tử Tức",
    "tu nu": "Tử Tức",
    "phu the": "Phu Thê",
    "huynh de": "Huynh Đệ",
}

CANONICAL_MAJOR_STARS = {
    "tu vi": "Tử Vi",
    "thien co": "Thiên Cơ",
    "thai duong": "Thái Dương",
    "vu khuc": "Vũ Khúc",
    "thien dong": "Thiên Đồng",
    "liem trinh": "Liêm Trinh",
    "thien phu": "Thiên Phủ",
    "thai am": "Thái Âm",
    "tham lang": "Tham Lang",
    "cu mon": "Cự Môn",
    "thien tuong": "Thiên Tướng",
    "thien luong": "Thiên Lương",
    "that sat": "Thất Sát",
    "pha quan": "Phá Quân",
}

TU_HOA_STARS = {"Hóa Lộc", "Hóa Quyền", "Hóa Khoa", "Hóa Kỵ"}

STAR_ELEMENT_HINTS = {
    "Tử Vi": "Thổ",
    "Thiên Phủ": "Thổ",
    "Thái Dương": "Hỏa",
    "Thái Âm": "Thủy",
    "Thiên Đồng": "Thủy",
    "Thiên Cơ": "Mộc",
    "Vũ Khúc": "Kim",
    "Liêm Trinh": "Hỏa",
    "Tham Lang": "Mộc",
    "Cự Môn": "Thủy",
    "Thiên Tướng": "Thủy",
    "Thiên Lương": "Thổ",
    "Thất Sát": "Kim",
    "Phá Quân": "Thủy",
    "Hóa Lộc": "Mộc",
    "Hóa Quyền": "Hỏa",
    "Hóa Khoa": "Mộc",
    "Hóa Kỵ": "Thủy",
}

ELEMENT_REL = {
    ("Kim", "Thủy"): "sinh",
    ("Thủy", "Mộc"): "sinh",
    ("Mộc", "Hỏa"): "sinh",
    ("Hỏa", "Thổ"): "sinh",
    ("Thổ", "Kim"): "sinh",
    ("Kim", "Mộc"): "khắc",
    ("Mộc", "Thổ"): "khắc",
    ("Thổ", "Thủy"): "khắc",
    ("Thủy", "Hỏa"): "khắc",
    ("Hỏa", "Kim"): "khắc",
}

TAM_HOP_GROUPS = [
    ["Thân", "Tý", "Thìn"],
    ["Tỵ", "Dậu", "Sửu"],
    ["Dần", "Ngọ", "Tuất"],
    ["Hợi", "Mão", "Mùi"],
]

XUNG_CHIEU_MAP = {
    "Tý": "Ngọ",
    "Sửu": "Mùi",
    "Dần": "Thân",
    "Mão": "Dậu",
    "Thìn": "Tuất",
    "Tỵ": "Hợi",
    "Ngọ": "Tý",
    "Mùi": "Sửu",
    "Thân": "Dần",
    "Dậu": "Mão",
    "Tuất": "Thìn",
    "Hợi": "Tỵ",
}

NHI_HOP_MAP = {
    "Tý": "Sửu",
    "Sửu": "Tý",
    "Dần": "Hợi",
    "Hợi": "Dần",
    "Mão": "Tuất",
    "Tuất": "Mão",
    "Thìn": "Dậu",
    "Dậu": "Thìn",
    "Tỵ": "Thân",
    "Thân": "Tỵ",
    "Ngọ": "Mùi",
    "Mùi": "Ngọ",
}

LUC_HAI_MAP = {
    "Tý": "Mùi",
    "Mùi": "Tý",
    "Sửu": "Ngọ",
    "Ngọ": "Sửu",
    "Dần": "Tỵ",
    "Tỵ": "Dần",
    "Mão": "Thìn",
    "Thìn": "Mão",
    "Thân": "Hợi",
    "Hợi": "Thân",
    "Dậu": "Tuất",
    "Tuất": "Dậu",
}

TOPIC_HOUSES = {
    "career": ["Quan Lộc", "Mệnh", "Thiên Di"],
    "finance": ["Tài Bạch", "Mệnh", "Quan Lộc"],
    "marriage": ["Phu Thê", "Mệnh", "Thiên Di"],
    "health": ["Tật Ách", "Mệnh", "Phúc Đức"],
    "family": ["Phụ Mẫu", "Phúc Đức", "Huynh Đệ"],
}


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------
def strip_accents(text: str) -> str:
    if text is None:
        return ""
    text = unicodedata.normalize("NFD", str(text))
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return text.replace("đ", "d").replace("Đ", "D")


def normalize_key(text: str) -> str:
    text = strip_accents(text or "")
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def slugify(text: str) -> str:
    text = strip_accents(text or "")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text or "chart"


def title_case_vn(text: str) -> str:
    parts = re.split(r"(\s+)", (text or "").strip())
    return "".join(p[:1].upper() + p[1:].lower() if not p.isspace() else p for p in parts)


def canonical_house_name(name: str) -> str:
    key = normalize_key(name)
    return HOUSE_ALIAS_MAP.get(key, title_case_vn(name))


def canonical_branch(branch: Optional[str]) -> Optional[str]:
    if not branch:
        return None
    key = normalize_key(branch)
    for item in BRANCH_ORDER:
        if normalize_key(item) == key:
            return item
    return title_case_vn(branch)


def canonical_star_name(name: str) -> str:
    key = normalize_key(name)
    if key in CANONICAL_MAJOR_STARS:
        return CANONICAL_MAJOR_STARS[key]
    return title_case_vn(name)


def normalize_status(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    raw = normalize_key(value)
    mapping = {
        "m": "Miếu",
        "mieu": "Miếu",
        "vuong": "Vượng",
        "v": "Vượng",
        "dac": "Đắc",
        "d": "Đắc",
        "ham": "Hãm",
        "h": "Hãm",
        "binh": "Bình",
        "b": "Bình",
    }
    return mapping.get(raw, title_case_vn(value))


def safe_int(value: Any) -> Optional[int]:
    try:
        return int(value) if value is not None else None
    except Exception:
        return None


def extract_element_from_ban_menh(ban_menh: Optional[str]) -> Optional[str]:
    if not ban_menh:
        return None
    for e in ELEMENTS:
        if e in ban_menh:
            return e
    return None


def extract_element_from_cuc(cuc: Optional[str]) -> Optional[str]:
    if not cuc:
        return None
    for e in ELEMENTS:
        if e in cuc:
            return e
    return None


def relation_between_elements(source: Optional[str], target: Optional[str]) -> Optional[str]:
    if not source or not target:
        return None
    if source == target:
        return "đồng_hành"
    return ELEMENT_REL.get((source, target))


def find_tam_hop(branch: Optional[str]) -> List[str]:
    if not branch:
        return []
    for group in TAM_HOP_GROUPS:
        if branch in group:
            return list(group)
    return []


def find_giap(branch: Optional[str]) -> List[str]:
    if not branch or branch not in BRANCH_ORDER:
        return []
    idx = BRANCH_ORDER.index(branch)
    return [BRANCH_ORDER[(idx - 1) % 12], BRANCH_ORDER[(idx + 1) % 12]]


def compact_star(star: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "name": canonical_star_name(star.get("name") or star.get("saoTen") or ""),
        "status": normalize_status(star.get("brightness") or star.get("saoDacTinh") or star.get("status")),
    }


def compact_star_with_meta(star: Dict[str, Any], house_name: str, branch: Optional[str]) -> Dict[str, Any]:
    name = canonical_star_name(star.get("name") or star.get("saoTen") or "")
    return {
        "name": name,
        "status": normalize_status(star.get("brightness") or star.get("saoDacTinh") or star.get("status")),
        "house_name": house_name,
        "earthly_branch": branch,
        "star_element": STAR_ELEMENT_HINTS.get(name),
        "is_luu": bool(star.get("is_luu") or star.get("isLuu") or False),
    }


def is_major_star(star_name: str) -> bool:
    return normalize_key(star_name) in CANONICAL_MAJOR_STARS


def extract_birth_info(chart_full: Dict[str, Any]) -> Dict[str, Any]:
    md = chart_full.get("metadata", {})
    return {
        "name": md.get("label"),
        "birth_date": md.get("birth_date"),
        "birth_time": md.get("birth_time"),
        "gender": md.get("gender"),
        "timezone": "Asia/Ho_Chi_Minh",
        "calculated_at": md.get("calculated_at"),
    }


# ---------------------------------------------------------------------------
# Extraction helpers from chart_full
# ---------------------------------------------------------------------------
def get_destiny_info(chart_full: Dict[str, Any]) -> Dict[str, Any]:
    return chart_full.get("metadata", {}).get("destiny_info") or {}


def get_personal_info(chart_full: Dict[str, Any]) -> Dict[str, Any]:
    return chart_full.get("metadata", {}).get("personal_info") or {}


def find_menh_house(chart_full: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    palaces = chart_full.get("palaces", {}) or {}
    return palaces.get("Mệnh")


def infer_than_house_name(chart_full: Dict[str, Any]) -> Optional[str]:
    for house_name, house_data in (chart_full.get("palaces", {}) or {}).items():
        attrs = house_data.get("attributes", {}) or {}
        if attrs.get("has_than") is True:
            return house_name
    destiny = get_destiny_info(chart_full)
    than_cu = destiny.get("thanCu")
    if isinstance(than_cu, str):
        for house_name in chart_full.get("palaces", {}):
            if normalize_key(house_name) in normalize_key(than_cu):
                return house_name
            if normalize_key(than_cu).startswith(normalize_key(house_name)):
                return house_name
    return None


def infer_than_branch(chart_full: Dict[str, Any]) -> Optional[str]:
    than_house_name = infer_than_house_name(chart_full)
    if than_house_name and than_house_name in (chart_full.get("palaces", {}) or {}):
        attrs = chart_full["palaces"][than_house_name].get("attributes", {}) or {}
        return canonical_branch(attrs.get("dia_chi"))
    destiny = get_destiny_info(chart_full)
    val = destiny.get("cungThan") or destiny.get("thanPosition")
    if isinstance(val, str):
        return canonical_branch(val)
    return None


def infer_menh_branch(chart_full: Dict[str, Any]) -> Optional[str]:
    menh_house = find_menh_house(chart_full)
    if menh_house:
        attrs = menh_house.get("attributes", {}) or {}
        return canonical_branch(attrs.get("dia_chi"))
    destiny = get_destiny_info(chart_full)
    val = destiny.get("cungMenh") or destiny.get("menhPosition")
    if isinstance(val, str):
        return canonical_branch(val)
    return None


# ---------------------------------------------------------------------------
# Build chart_repr
# ---------------------------------------------------------------------------
def build_chart_repr(chart_full: Dict[str, Any]) -> Dict[str, Any]:
    destiny = get_destiny_info(chart_full)
    personal = get_personal_info(chart_full)
    palaces = chart_full.get("palaces", {}) or {}

    menh_position = infer_menh_branch(chart_full)
    than_position = infer_than_branch(chart_full)

    ban_menh = (
        destiny.get("banMenh")
        or destiny.get("ban_menh")
        or personal.get("banMenh")
        or chart_full.get("ban_menh")
    )
    cuc = destiny.get("cucMenh") or destiny.get("cuc") or chart_full.get("cuc")
    ngu_hanh_ban_menh = (
        destiny.get("menhNguHanh")
        or destiny.get("nguHanhBanMenh")
        or extract_element_from_ban_menh(ban_menh)
    )

    am_duong_nam_nu = destiny.get("amDuongLy")
    gender = str(chart_full.get("metadata", {}).get("gender", "")).strip()
    if not am_duong_nam_nu:
        am_duong_nam_nu = gender
    else:
        g = "Nam" if normalize_key(gender) in {"male", "nam", "0"} else "Nữ"
        if "nam" in normalize_key(am_duong_nam_nu) or "nu" in normalize_key(am_duong_nam_nu):
            pass
        else:
            am_duong_nam_nu = f"{title_case_vn(am_duong_nam_nu)} {g}"

    houses: List[Dict[str, Any]] = []
    derived_tags: List[str] = []

    for house_name_raw, house_data in palaces.items():
        house_name = canonical_house_name(house_name_raw)
        attrs = house_data.get("attributes", {}) or {}
        branch = canonical_branch(attrs.get("dia_chi"))
        star_details = house_data.get("star_details", []) or []

        major_stars = [compact_star(s) for s in star_details if is_major_star(s.get("name") or s.get("saoTen") or "")]
        aux_stars = [compact_star(s) for s in star_details if not is_major_star(s.get("name") or s.get("saoTen") or "")]

        if house_name == "Mệnh" and not major_stars:
            derived_tags.append("menh_vo_chinh_dieu")
        if attrs.get("has_than"):
            derived_tags.append(f"than_cu_{slugify(house_name)}")
        if any(st["name"] == "Hóa Lộc" for st in aux_stars + major_stars):
            derived_tags.append(f"{slugify(house_name)}_co_hoa_loc")

        houses.append(
            {
                "house_index": safe_int(house_data.get("position")),
                "house_name": house_name,
                "earthly_branch": branch,
                "is_than_resident": bool(attrs.get("has_than") is True),
                "house_element": attrs.get("element"),
                "yin_yang": attrs.get("yin_yang"),
                "dai_han_age": safe_int(attrs.get("dai_han_age") or attrs.get("dai_han")),
                "tieu_han_branch": canonical_branch(attrs.get("tieu_han")),
                "trang_sinh": attrs.get("trang_sinh"),
                "tuan_khong": bool(attrs.get("tuan_khong") is True),
                "triet_khong": bool(attrs.get("triet_khong") is True),
                "major_stars": major_stars,
                "aux_stars": aux_stars,
            }
        )

    houses.sort(key=lambda x: (x.get("house_index") is None, x.get("house_index") or 999))

    return {
        "chart_type": "TUVI",
        "schema_role": "chart_repr",
        "schema_version": "2.0",
        "menh_position": menh_position,
        "than_position": than_position,
        "ban_menh": ban_menh,
        "ngu_hanh_ban_menh": ngu_hanh_ban_menh,
        "cuc": cuc,
        "am_duong_nam_nu": am_duong_nam_nu,
        "houses": houses,
        "derived_tags": sorted(set(derived_tags)),
    }


# ---------------------------------------------------------------------------
# Build chart_semantic
# ---------------------------------------------------------------------------
@dataclass
class StarOccurrence:
    name: str
    status: Optional[str]
    house_name: str
    earthly_branch: Optional[str]
    star_element: Optional[str]
    is_luu: bool


def build_star_index(chart_repr: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    index: Dict[str, List[Dict[str, Any]]] = {}
    for house in chart_repr.get("houses", []):
        house_name = house.get("house_name")
        branch = house.get("earthly_branch")
        for group_name in ("major_stars", "aux_stars"):
            for star in house.get(group_name, []):
                name = star.get("name")
                if not name:
                    continue
                index.setdefault(name, []).append(
                    {
                        "house_name": house_name,
                        "earthly_branch": branch,
                        "status": star.get("status"),
                        "star_group": "major" if group_name == "major_stars" else "aux",
                        "star_element": STAR_ELEMENT_HINTS.get(name),
                    }
                )
    return dict(sorted(index.items(), key=lambda kv: kv[0]))


def compute_house_relations(branch: Optional[str]) -> Dict[str, Any]:
    return {
        "tam_hop_branches": find_tam_hop(branch),
        "xung_chieu_branch": XUNG_CHIEU_MAP.get(branch),
        "nhi_hop_branch": NHI_HOP_MAP.get(branch),
        "luc_hai_branch": LUC_HAI_MAP.get(branch),
        "giap_branches": find_giap(branch),
    }


def compute_elemental_flags(house_element: Optional[str], ban_menh_element: Optional[str], stars: List[Dict[str, Any]]) -> List[str]:
    flags: List[str] = []
    for st in stars:
        star_el = STAR_ELEMENT_HINTS.get(st.get("name"))
        if not star_el:
            continue
        rel_house_star = relation_between_elements(house_element, star_el)
        rel_star_menh = relation_between_elements(star_el, ban_menh_element)
        if rel_house_star == "sinh":
            flags.append("cung_sinh_sao")
        elif rel_house_star == "khắc":
            flags.append("cung_khac_sao")
        if rel_star_menh == "sinh":
            flags.append("sao_tuong_sinh_ban_menh")
        elif rel_star_menh == "khắc":
            flags.append("sao_khac_ban_menh")
    return sorted(set(flags))


def detect_tu_hoa_birth_year(chart_repr: Dict[str, Any]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for house in chart_repr.get("houses", []):
        house_name = house.get("house_name")
        for group in ("major_stars", "aux_stars"):
            for star in house.get(group, []):
                name = star.get("name")
                if name in TU_HOA_STARS:
                    result[name] = {
                        "house_name": house_name,
                        "earthly_branch": house.get("earthly_branch"),
                    }
    return result


def detect_notable_patterns(chart_repr: Dict[str, Any], chart_full: Dict[str, Any]) -> List[Dict[str, Any]]:
    patterns: List[Dict[str, Any]] = []
    all_star_names = set()
    for house in chart_repr.get("houses", []):
        for group in ("major_stars", "aux_stars"):
            for star in house.get(group, []):
                all_star_names.add(star.get("name"))

    if {"Tử Vi", "Thiên Phủ", "Vũ Khúc", "Thiên Tướng"}.issubset(all_star_names):
        patterns.append({"pattern_code": "tu_phu_vu_tuong_present", "evidence": ["Tử Vi", "Thiên Phủ", "Vũ Khúc", "Thiên Tướng"]})
    if {"Thất Sát", "Phá Quân", "Tham Lang"}.issubset(all_star_names):
        patterns.append({"pattern_code": "sat_pha_tham_present", "evidence": ["Thất Sát", "Phá Quân", "Tham Lang"]})
    if {"Thiên Cơ", "Thái Âm", "Thiên Đồng", "Thiên Lương"}.issubset(all_star_names):
        patterns.append({"pattern_code": "co_nguyet_dong_luong_present", "evidence": ["Thiên Cơ", "Thái Âm", "Thiên Đồng", "Thiên Lương"]})
    if {"Cự Môn", "Thái Dương"}.issubset(all_star_names):
        patterns.append({"pattern_code": "cu_nhat_present", "evidence": ["Cự Môn", "Thái Dương"]})

    than_house = infer_than_house_name(chart_full)
    if than_house:
        patterns.append({"pattern_code": f"than_cu_{slugify(than_house)}", "evidence": [than_house]})

    menh_house = next((h for h in chart_repr.get("houses", []) if h.get("house_name") == "Mệnh"), None)
    if menh_house and not menh_house.get("major_stars"):
        patterns.append({"pattern_code": "menh_vo_chinh_dieu", "evidence": ["Mệnh"]})

    return patterns


def build_palace_semantics(chart_full: Dict[str, Any], chart_repr: Dict[str, Any]) -> List[Dict[str, Any]]:
    destiny = get_destiny_info(chart_full)
    ban_menh_element = chart_repr.get("ngu_hanh_ban_menh")
    annual_year = chart_full.get("metadata", {}).get("nam_xem_han")
    results: List[Dict[str, Any]] = []
    palaces_full = chart_full.get("palaces", {}) or {}

    for house in chart_repr.get("houses", []):
        house_name = house.get("house_name")
        full_house = palaces_full.get(house_name, {})
        attrs = full_house.get("attributes", {}) or {}
        branch = house.get("earthly_branch")
        all_stars = (house.get("major_stars") or []) + (house.get("aux_stars") or [])

        yearly_transit_stars = []
        for st in full_house.get("star_details", []) or []:
            src = str(st.get("source") or "")
            if normalize_key(src) in {"annual_transit", "luu_nien"} or st.get("nam_xem_han"):
                yearly_transit_stars.append(canonical_star_name(st.get("name") or st.get("saoTen") or ""))

        semantic_item = {
            "house_name": house_name,
            "earthly_branch": branch,
            "heavenly_stem": attrs.get("heavenly_stem") or attrs.get("thien_can") or attrs.get("can_cung"),
            "house_element": house.get("house_element"),
            "yin_yang": house.get("yin_yang"),
            "is_menh": house_name == "Mệnh",
            "is_than_resident": bool(house.get("is_than_resident") is True),
            "dai_han_age": house.get("dai_han_age"),
            "tieu_han_branch": house.get("tieu_han_branch"),
            "trang_sinh": house.get("trang_sinh"),
            "tuan_khong": bool(house.get("tuan_khong") is True),
            "triet_khong": bool(house.get("triet_khong") is True),
            "major_stars": house.get("major_stars") or [],
            "aux_stars": house.get("aux_stars") or [],
            "house_relations": compute_house_relations(branch),
            "elemental_flags": compute_elemental_flags(house.get("house_element"), ban_menh_element, all_stars),
            "tu_hoa_birth_year": [s for s in all_stars if s.get("name") in TU_HOA_STARS],
            "phi_hoa": {
                "available": False,
                "note": "Requires can-cung + phi-hoa rule tables/helper. Left empty to avoid fabricated semantics.",
                "hoa_loc_to": None,
                "hoa_quyen_to": None,
                "hoa_khoa_to": None,
                "hoa_ky_to": None,
            },
            "tu_hoa_self": [],
            "yearly_transit": {
                "nam_xem_han": annual_year,
                "stars": sorted(set(yearly_transit_stars)),
            },
        }
        results.append(semantic_item)

    return results


def build_retrieval_hints(chart_repr: Dict[str, Any], chart_semantic_core: Dict[str, Any]) -> Dict[str, Any]:
    houses = {h["house_name"]: h for h in chart_repr.get("houses", [])}
    house_rel = {h["house_name"]: compute_house_relations(h.get("earthly_branch")) for h in chart_repr.get("houses", [])}

    def bundle(topic: str) -> Dict[str, Any]:
        house_names = [h for h in TOPIC_HOUSES[topic] if h in houses]
        relations = {h: house_rel.get(h) for h in house_names}
        key_stars: List[str] = []
        for h in house_names:
            for group in ("major_stars", "aux_stars"):
                key_stars.extend(st.get("name") for st in houses[h].get(group, []))
        return {
            "priority_houses": house_names,
            "priority_relations": relations,
            "key_stars": sorted(set(key_stars)),
        }

    return {
        "career": bundle("career"),
        "finance": bundle("finance"),
        "marriage": bundle("marriage"),
        "health": bundle("health"),
        "family": bundle("family"),
        "query_strategy": [
            "Ưu tiên lấy core_identity + cung đích + tam hợp/xung chiếu/nhị hợp/lục hại/giáp của cung đích.",
            "Nếu câu hỏi nhắc sao cụ thể, tra star_index trước rồi mới nạp palace_semantics liên quan.",
            "Chỉ nạp phi_hoa khi helper chuyên biệt đã được triển khai; không suy diễn bằng LLM nếu field còn rỗng.",
        ],
    }


def build_chart_semantic(chart_full: Dict[str, Any], chart_repr: Dict[str, Any]) -> Dict[str, Any]:
    destiny = get_destiny_info(chart_full)
    birth_info = extract_birth_info(chart_full)
    menh_branch = chart_repr.get("menh_position")
    than_branch = chart_repr.get("than_position")
    ngu_hanh_cuc = destiny.get("cucNguHanh") or extract_element_from_cuc(chart_repr.get("cuc"))

    semantic: Dict[str, Any] = {
        "chart_type": "TUVI",
        "schema_role": "chart_semantic",
        "schema_version": "2.0",
        "core_identity": {
            "name": birth_info.get("name"),
            "birth_date": birth_info.get("birth_date"),
            "birth_time": birth_info.get("birth_time"),
            "gender": birth_info.get("gender"),
            "timezone": birth_info.get("timezone"),
            "menh_branch": menh_branch,
            "than_branch": than_branch,
            "ban_menh": chart_repr.get("ban_menh"),
            "ngu_hanh_ban_menh": chart_repr.get("ngu_hanh_ban_menh"),
            "cuc": chart_repr.get("cuc"),
            "ngu_hanh_cuc": ngu_hanh_cuc,
            "am_duong_nam_nu": chart_repr.get("am_duong_nam_nu"),
            "menh_cuc_relation": destiny.get("menhCucTuongQuan") or relation_between_elements(ngu_hanh_cuc, chart_repr.get("ngu_hanh_ban_menh")),
            "chu_menh": destiny.get("chuMenh"),
            "chu_than": destiny.get("chuThan"),
            "lai_nhan_cung": destiny.get("laiNhanCung"),
            "than_cu": destiny.get("thanCu"),
            "can_chi_menh": destiny.get("canChiMenh"),
            "can_luong": destiny.get("canLuong"),
        },
        "birth_year_tu_hoa": detect_tu_hoa_birth_year(chart_repr),
        "focus_relations": {
            "menh": compute_house_relations(menh_branch),
            "than": compute_house_relations(than_branch),
        },
        "palace_semantics": build_palace_semantics(chart_full, chart_repr),
        "star_index": build_star_index(chart_repr),
        "notable_patterns": detect_notable_patterns(chart_repr, chart_full),
    }
    semantic["retrieval_hints"] = build_retrieval_hints(chart_repr, semantic)
    return semantic


# ---------------------------------------------------------------------------
# Optional projection: semantic markdown for prompt-time use
# ---------------------------------------------------------------------------
def render_semantic_markdown(chart_semantic: Dict[str, Any]) -> str:
    core = chart_semantic.get("core_identity", {})
    lines = []
    lines.append("# CHART_SEMANTIC")
    lines.append("")
    lines.append("## CORE_IDENTITY")
    for key in [
        "name",
        "birth_date",
        "birth_time",
        "gender",
        "timezone",
        "menh_branch",
        "than_branch",
        "ban_menh",
        "ngu_hanh_ban_menh",
        "cuc",
        "ngu_hanh_cuc",
        "am_duong_nam_nu",
        "menh_cuc_relation",
        "chu_menh",
        "chu_than",
        "lai_nhan_cung",
        "than_cu",
        "can_chi_menh",
        "can_luong",
    ]:
        lines.append(f"- {key}: {core.get(key)}")

    lines.append("")
    lines.append("## BIRTH_YEAR_TU_HOA")
    for k, v in (chart_semantic.get("birth_year_tu_hoa") or {}).items():
        lines.append(f"- {k}: house={v.get('house_name')}; branch={v.get('earthly_branch')}")
    if not chart_semantic.get("birth_year_tu_hoa"):
        lines.append("- none")

    lines.append("")
    lines.append("## FOCUS_RELATIONS")
    for scope in ["menh", "than"]:
        rel = (chart_semantic.get("focus_relations") or {}).get(scope, {})
        lines.append(f"### {scope.upper()}")
        lines.append(f"- tam_hop_branches: {', '.join(rel.get('tam_hop_branches') or [])}")
        lines.append(f"- xung_chieu_branch: {rel.get('xung_chieu_branch')}")
        lines.append(f"- nhi_hop_branch: {rel.get('nhi_hop_branch')}")
        lines.append(f"- luc_hai_branch: {rel.get('luc_hai_branch')}")
        lines.append(f"- giap_branches: {', '.join(rel.get('giap_branches') or [])}")

    lines.append("")
    lines.append("## PALACE_SEMANTICS")
    for palace in chart_semantic.get("palace_semantics", []):
        lines.append(f"### {palace.get('house_name')}")
        lines.append(f"- earthly_branch: {palace.get('earthly_branch')}")
        lines.append(f"- heavenly_stem: {palace.get('heavenly_stem')}")
        lines.append(f"- house_element: {palace.get('house_element')}")
        lines.append(f"- yin_yang: {palace.get('yin_yang')}")
        lines.append(f"- is_menh: {palace.get('is_menh')}")
        lines.append(f"- is_than_resident: {palace.get('is_than_resident')}")
        lines.append(f"- dai_han_age: {palace.get('dai_han_age')}")
        lines.append(f"- tieu_han_branch: {palace.get('tieu_han_branch')}")
        lines.append(f"- trang_sinh: {palace.get('trang_sinh')}")
        lines.append(f"- tuan_khong: {palace.get('tuan_khong')}")
        lines.append(f"- triet_khong: {palace.get('triet_khong')}")
        lines.append(
            "- major_stars: " + ", ".join(
                f"{s.get('name')}[{s.get('status')}]" if s.get('status') else s.get('name')
                for s in palace.get('major_stars', [])
            )
        )
        lines.append(
            "- aux_stars: " + ", ".join(
                f"{s.get('name')}[{s.get('status')}]" if s.get('status') else s.get('name')
                for s in palace.get('aux_stars', [])
            )
        )
        rel = palace.get("house_relations", {})
        lines.append(f"- tam_hop_branches: {', '.join(rel.get('tam_hop_branches') or [])}")
        lines.append(f"- xung_chieu_branch: {rel.get('xung_chieu_branch')}")
        lines.append(f"- nhi_hop_branch: {rel.get('nhi_hop_branch')}")
        lines.append(f"- luc_hai_branch: {rel.get('luc_hai_branch')}")
        lines.append(f"- giap_branches: {', '.join(rel.get('giap_branches') or [])}")
        lines.append(f"- elemental_flags: {', '.join(palace.get('elemental_flags') or [])}")
        birth_tu_hoa = palace.get("tu_hoa_birth_year") or []
        lines.append(
            "- tu_hoa_birth_year: " + ", ".join(s.get("name") for s in birth_tu_hoa) if birth_tu_hoa else "- tu_hoa_birth_year: none"
        )
        phi_hoa = palace.get("phi_hoa") or {}
        lines.append(
            f"- phi_hoa: available={phi_hoa.get('available')}; hoa_loc_to={phi_hoa.get('hoa_loc_to')}; hoa_quyen_to={phi_hoa.get('hoa_quyen_to')}; hoa_khoa_to={phi_hoa.get('hoa_khoa_to')}; hoa_ky_to={phi_hoa.get('hoa_ky_to')}"
        )
        year = (palace.get("yearly_transit") or {}).get("nam_xem_han")
        stars = ", ".join((palace.get("yearly_transit") or {}).get("stars") or [])
        lines.append(f"- yearly_transit: year={year}; stars={stars}")
        lines.append("")

    lines.append("## NOTABLE_PATTERNS")
    patterns = chart_semantic.get("notable_patterns") or []
    if patterns:
        for p in patterns:
            lines.append(f"- {p.get('pattern_code')}: {', '.join(p.get('evidence') or [])}")
    else:
        lines.append("- none")

    lines.append("")
    lines.append("## RETRIEVAL_HINTS")
    hints = chart_semantic.get("retrieval_hints") or {}
    for topic in ["career", "finance", "marriage", "health", "family"]:
        bundle = hints.get(topic, {})
        lines.append(f"### {topic.upper()}")
        lines.append(f"- priority_houses: {', '.join(bundle.get('priority_houses') or [])}")
        lines.append(f"- key_stars: {', '.join(bundle.get('key_stars') or [])}")
    lines.append("### QUERY_STRATEGY")
    for rule in hints.get("query_strategy", []):
        lines.append(f"- {rule}")

    return "\n".join(lines).strip() + "\n"


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------
def build_export_payload(
    name: str,
    birth_date: str,
    birth_time: str,
    gender: str,
    include_full: bool = False,
    nam_xem_han: Optional[int] = None,
) -> Dict[str, Any]:
    calculator = TuViCalculator()
    chart_full = calculator.calculate(
        birth_date=birth_date,
        birth_time=birth_time,
        gender=gender,
        label=name,
        nam_xem_han=nam_xem_han,
    )
    chart_repr = build_chart_repr(chart_full)
    chart_semantic = build_chart_semantic(chart_full, chart_repr)

    payload = {
        "exported_at": datetime.utcnow().isoformat() + "Z",
        "input": {
            "name": name,
            "birth_date": birth_date,
            "birth_time": birth_time,
            "gender": gender,
            "timezone": "Asia/Ho_Chi_Minh",
            "nam_xem_han": nam_xem_han,
        },
        "chart_repr": chart_repr,
        "chart_semantic": chart_semantic,
    }
    if include_full:
        payload["chart_full"] = chart_full
    return payload


def write_outputs(payload: Dict[str, Any], output_dir: Path, base_name: str, semantic_format: str) -> List[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    written: List[Path] = []

    chart_repr_path = output_dir / f"{base_name}__chart_repr.json"
    chart_repr_path.write_text(json.dumps(payload["chart_repr"], ensure_ascii=False, indent=2), encoding="utf-8")
    written.append(chart_repr_path)

    chart_semantic_path = output_dir / f"{base_name}__chart_semantic.json"
    chart_semantic_path.write_text(json.dumps(payload["chart_semantic"], ensure_ascii=False, indent=2), encoding="utf-8")
    written.append(chart_semantic_path)

    combined_path = output_dir / f"{base_name}__export_bundle.json"
    combined_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    written.append(combined_path)

    if semantic_format in {"md", "both"}:
        md_path = output_dir / f"{base_name}__chart_semantic.md"
        md_path.write_text(render_semantic_markdown(payload["chart_semantic"]), encoding="utf-8")
        written.append(md_path)

    return written


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export chart_repr and chart_semantic from TuViCalculator")
    parser.add_argument("--name", required=True, help="Person name / chart label")
    parser.add_argument("--birth-date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--birth-time", required=True, help="HH:MM or HH:MM:SS")
    parser.add_argument("--gender", required=True, help="nam/female/male/nữ/nu")
    parser.add_argument("--output-dir", required=True, help="Directory to write output files")
    parser.add_argument("--semantic-format", choices=["json", "md", "both"], default="both")
    parser.add_argument("--include-full", action="store_true", help="Also include chart_full in export_bundle.json")
    parser.add_argument("--nam-xem-han", type=int, default=None, help="Optional target year for transit data if supported")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_export_payload(
        name=args.name,
        birth_date=args.birth_date,
        birth_time=args.birth_time,
        gender=args.gender,
        include_full=args.include_full,
        nam_xem_han=args.nam_xem_han,
    )

    base_name = slugify(f"{args.name}_{args.birth_date}_{args.birth_time}")
    written = write_outputs(payload, Path(args.output_dir), base_name, args.semantic_format)

    print(json.dumps({
        "status": "ok",
        "written_files": [str(p) for p in written],
        "chart_repr_summary": {
            "menh_position": payload["chart_repr"].get("menh_position"),
            "than_position": payload["chart_repr"].get("than_position"),
            "ban_menh": payload["chart_repr"].get("ban_menh"),
            "cuc": payload["chart_repr"].get("cuc"),
        },
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
