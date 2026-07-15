from __future__ import annotations

import re
import unicodedata
from typing import Any


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

HOUSE_ALIASES = {
    "menh": "Mệnh",
    "mệnh": "Mệnh",
    "phu mau": "Phụ Mẫu",
    "phụ mẫu": "Phụ Mẫu",
    "phu": "Phụ Mẫu",
    "phụ": "Phụ Mẫu",
    "mau": "Phụ Mẫu",
    "mẫu": "Phụ Mẫu",
    "phuc": "Phúc Đức",
    "phúc": "Phúc Đức",
    "phuc duc": "Phúc Đức",
    "phúc đức": "Phúc Đức",
    "dien": "Điền Trạch",
    "điền": "Điền Trạch",
    "dien trach": "Điền Trạch",
    "điền trạch": "Điền Trạch",
    "quan": "Quan Lộc",
    "quan loc": "Quan Lộc",
    "quan lộc": "Quan Lộc",
    "no": "Nô Bộc",
    "nô": "Nô Bộc",
    "no boc": "Nô Bộc",
    "nô bộc": "Nô Bộc",
    "di": "Thiên Di",
    "thien di": "Thiên Di",
    "thiên di": "Thiên Di",
    "tat": "Tật Ách",
    "tật": "Tật Ách",
    "tat ach": "Tật Ách",
    "tật ách": "Tật Ách",
    "tai": "Tài Bạch",
    "tài": "Tài Bạch",
    "tai bach": "Tài Bạch",
    "tài bạch": "Tài Bạch",
    "tu": "Tử Tức",
    "tử": "Tử Tức",
    "tu tuc": "Tử Tức",
    "tử tức": "Tử Tức",
    "phoi": "Phu Thê",
    "phối": "Phu Thê",
    "phu the": "Phu Thê",
    "phu thê": "Phu Thê",
    "huynh": "Huynh Đệ",
    "huynh de": "Huynh Đệ",
    "huynh đệ": "Huynh Đệ",
}

HOUSE_TRIADS = [
    {"name": "Mệnh-Tài-Quan", "houses": ["Mệnh", "Tài Bạch", "Quan Lộc"]},
    {"name": "Phúc-Phối-Di", "houses": ["Phúc Đức", "Phu Thê", "Thiên Di"]},
    {"name": "Điền-Tật-Huynh", "houses": ["Điền Trạch", "Tật Ách", "Huynh Đệ"]},
    {"name": "Phụ-Nô-Tử", "houses": ["Phụ Mẫu", "Nô Bộc", "Tử Tức"]},
]

TRIAD_SOURCE = "tuvi_house_ontology"


def normalize_text(value: Any) -> str:
    return " ".join(str(value or "").casefold().split())


def strip_accents(value: str) -> str:
    normalized = unicodedata.normalize("NFD", value)
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn").replace("đ", "d").replace("Đ", "D")


def normalize_key(value: Any) -> str:
    return normalize_text(strip_accents(str(value or "")))


def canonical_house_name(value: str) -> str | None:
    normalized = normalize_text(value)
    ascii_normalized = normalize_key(value)
    for house in HOUSE_NAMES:
        if normalize_text(house) == normalized or normalize_key(house) == ascii_normalized:
            return house
    return HOUSE_ALIASES.get(normalized) or HOUSE_ALIASES.get(ascii_normalized)


def explicit_house_triad(query: str) -> dict[str, Any] | None:
    """Parse explicit user triads such as `tam hợp Phúc-Phối-Di`.

    The parser is intentionally conservative: it only locks target houses when it
    sees a tam-hop phrase plus three recognizable house aliases. This prevents
    runtime entity extraction noise from adding unrelated houses such as Phụ Mẫu.
    """

    text = str(query or "")
    normalized = normalize_key(text)
    if "tam hop" not in normalized:
        return None
    tail_match = re.search(r"tam\s+h[oợơ]p\s+(.+)$", text, flags=re.IGNORECASE)
    tail = tail_match.group(1) if tail_match else text
    parts = [part.strip(" .,:;()[]{}\t\n\r") for part in re.split(r"\s*[-–—/,+]\s*|\s+va\s+|\s+và\s+", tail) if part.strip()]
    houses: list[str] = []
    for part in parts:
        canonical = canonical_house_name(part)
        if canonical and canonical not in houses:
            houses.append(canonical)
        if len(houses) >= 3:
            break
    if len(houses) != 3:
        return None
    known = find_house_triad(houses)
    return {
        "type": "house_triad",
        "name": known.get("name") if known else "-".join(houses),
        "houses": houses,
        "available": True,
        "source": TRIAD_SOURCE,
        "explicit": True,
        "recognized_standard_triad": bool(known),
    }


def find_house_triad(houses: list[str]) -> dict[str, Any] | None:
    wanted = {canonical_house_name(house) or house for house in houses}
    for triad in HOUSE_TRIADS:
        if set(triad["houses"]) == wanted:
            return {"type": "house_triad", "available": True, "source": TRIAD_SOURCE, **triad}
    return None


def triads_for_target_houses(target_houses: list[str]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    targets = {canonical_house_name(house) or house for house in target_houses}
    for triad in HOUSE_TRIADS:
        triad_set = set(triad["houses"])
        if targets and (targets == triad_set or len(targets & triad_set) >= 2):
            result.append({"type": "house_triad", "available": True, "source": TRIAD_SOURCE, **triad})
    return result