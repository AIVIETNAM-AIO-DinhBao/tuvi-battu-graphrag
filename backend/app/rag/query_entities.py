from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Any

import yaml

from app.rag.config import ROOT_DIR, RuntimeEntityExtractionConfig


def normalize_text(value: Any) -> str:
    return unicodedata.normalize("NFC", str(value or ""))


def normalize_lookup(value: Any) -> str:
    normalized = normalize_text(value).strip().casefold()
    return re.sub(r"\s+", " ", normalized)


def resolve_entity_config_path(path: Path) -> Path:
    return path if path.is_absolute() else ROOT_DIR / path


def load_runtime_entity_dictionary(path: Path) -> dict[str, Any]:
    config_path = resolve_entity_config_path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Runtime entity config not found: {config_path}")
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle) or {}
    required = {"entities", "entity_types"}
    missing = sorted(required - set(config))
    if missing:
        raise ValueError(f"Runtime entity config is missing required keys: {', '.join(missing)}")
    return config


def iter_alias_entries(config: dict[str, Any]) -> list[dict[str, str]]:
    entries: dict[tuple[str, str, str], dict[str, str]] = {}
    entity_types = set(config["entity_types"])
    for entity_type, canonical_map in config.get("entities", {}).items():
        if entity_type not in entity_types or not isinstance(canonical_map, dict):
            continue
        for canonical_name, aliases in canonical_map.items():
            alias_values = [str(canonical_name)]
            if isinstance(aliases, list):
                alias_values.extend(str(alias) for alias in aliases)
            for alias in alias_values:
                normalized_alias = normalize_lookup(alias)
                if not normalized_alias:
                    continue
                entries[(entity_type, str(canonical_name), normalized_alias)] = {
                    "alias": alias,
                    "canonical_name": str(canonical_name),
                    "entity_type": entity_type,
                    "normalized_alias": normalized_alias,
                }
    return sorted(
        entries.values(),
        key=lambda item: (len(item["normalized_alias"]), len(item["alias"])),
        reverse=True,
    )


def compile_alias_pattern(alias: str) -> re.Pattern[str]:
    escaped_parts = [re.escape(part) for part in normalize_text(alias).split()]
    body = r"\s+".join(escaped_parts)
    return re.compile(rf"(?<!\w){body}(?!\w)", flags=re.IGNORECASE | re.UNICODE)


def should_scan_alias(alias: str) -> bool:
    compact = normalize_lookup(alias).replace(" ", "")
    return len(compact) > 1


def overlaps(left: tuple[int, int], right: tuple[int, int]) -> bool:
    return left[0] < right[1] and right[0] < left[1]


def extract_query_entities(
    query: str,
    *,
    config: RuntimeEntityExtractionConfig,
) -> list[dict[str, Any]]:
    entity_dictionary = load_runtime_entity_dictionary(config.entity_config_path)
    text = normalize_text(query)
    records: list[dict[str, Any]] = []
    occupied: list[tuple[str, str, tuple[int, int]]] = []
    excluded = set(config.exclude_entity_types)

    for entry in iter_alias_entries(entity_dictionary):
        alias = entry["alias"]
        if entry["entity_type"] in excluded or not should_scan_alias(alias):
            continue
        for match in compile_alias_pattern(alias).finditer(text):
            span = (match.start(), match.end())
            overlap_key = (entry["entity_type"], entry["canonical_name"])
            if any(
                entity_type == overlap_key[0]
                and canonical_name == overlap_key[1]
                and overlaps(span, existing_span)
                for entity_type, canonical_name, existing_span in occupied
            ):
                continue
            surface_text = text[span[0] : span[1]]
            records.append(
                {
                    "aliases_matched": [alias],
                    "canonical_name": entry["canonical_name"],
                    "char_end": span[1],
                    "char_start": span[0],
                    "confidence": 0.92,
                    "entity_type": entry["entity_type"],
                    "extraction_source": "dictionary",
                    "surface_text": surface_text,
                }
            )
            occupied.append((entry["entity_type"], entry["canonical_name"], span))
            if len(records) >= config.max_entities:
                return records
    return records


def canonical_entity_names(records: list[dict[str, Any]]) -> list[str]:
    names: list[str] = []
    seen: set[str] = set()
    for record in records:
        name = str(record.get("canonical_name") or "").strip()
        if name and name not in seen:
            seen.add(name)
            names.append(name)
    return names


def surface_terms(records: list[dict[str, Any]]) -> list[str]:
    terms: list[str] = []
    seen: set[str] = set()
    for record in records:
        term = str(record.get("surface_text") or "").strip()
        key = normalize_lookup(term)
        if term and key not in seen:
            seen.add(key)
            terms.append(term)
    return terms
