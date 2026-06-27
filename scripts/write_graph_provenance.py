"""Write strategy-aware Tử Vi graph and chunk provenance for W3-INGEST-05.

The script consumes chunk JSONL from scripts/chunk_text.py and entity JSONL
from scripts/extract_entities.py, derives evidence-backed relations, and writes
Neo4j graph data plus Supabase source_chunks provenance. The core relation
derivation is deterministic and testable without any database connection.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable, Mapping

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE_REGISTRY = (
    ROOT_DIR / "benchmark" / "tuvi_golden_dataset" / "guideline" / "source_registry.json"
)
DEFAULT_RELATION_MODEL = "gemini-2.0-flash-lite"
DEFAULT_REQUESTS_PER_MINUTE = 30.0
DEFAULT_MAX_RETRY_SLEEP_SECONDS = 300.0
ONTOLOGY_SOURCE_ID = "tuvi_ontology_v1"

ENTITY_TYPES = {
    "Sao",
    "Cung",
    "ThienCan",
    "DiaChi",
    "NguHanh",
    "ToHop",
    "QuanHeCung",
    "TrangThaiSao",
    "TuHoa",
    "VanHan",
    "DaiHan",
    "CucBanMenh",
    "KhaiNiem",
    "LuanGiai",
}
RELATION_TYPES = {
    "MENTIONS",
    "THUOC_CUNG",
    "DOI_CHIEU",
    "LIEN_KE",
    "GIAI_THICH",
    "APPLIES_TO",
    "RELATED_TO",
    "LUU_Y",
    "HAS_SOURCE",
    "HAS_CHUNK",
}
EXTRACTABLE_RELATION_TYPES = RELATION_TYPES - {"MENTIONS", "HAS_SOURCE", "HAS_CHUNK"}
REQUIRED_CHUNK_KEYS = {
    "chunk_hash",
    "chunk_id",
    "chunk_strategy_id",
    "domain",
    "source_id",
    "source_page",
}
REQUIRED_ENTITY_KEYS = {
    "canonical_name",
    "char_end",
    "char_start",
    "chunk_hash",
    "chunk_id",
    "chunk_strategy_id",
    "domain",
    "entity_id",
    "entity_type",
    "evidence_text",
    "source_id",
    "source_page",
}

CUNG_CYCLE = [
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
THUOC_CUNG_TRIGGERS = [
    "ở",
    "tại",
    "an tại",
    "thủ",
    "cư",
    "tọa",
    "toạ",
    "đóng",
    "thuộc",
    "nằm",
    "có",
    "gặp",
]
DOI_CHIEU_TRIGGERS = ["chính chiếu", "xung chiếu", "đối cung", "đối chiếu"]
LIEN_KE_TRIGGERS = ["giáp", "giáp cung", "liền kề", "kề", "cận"]
RELATED_TRIGGERS = ["gặp", "hội", "đồng cung", "đi cùng", "phối hợp", "kết hợp"]
LUU_Y_TRIGGERS = ["cần xét", "lưu ý", "không nên", "kỵ", "kiêng", "nên xét"]

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


@dataclass(frozen=True)
class SentenceSpan:
    start: int
    end: int
    text: str


def utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def load_gemini_api_keys(env: Mapping[str, str | None] | None = None) -> list[str]:
    source = env if env is not None else os.environ
    raw_keys: list[str] = []
    raw_keys.extend(str(source.get("GEMINI_API_KEYS") or "").split(","))
    raw_keys.append(str(source.get("GEMINI_API_KEY") or ""))

    numbered: list[tuple[int, str]] = []
    for key, value in source.items():
        match = re.fullmatch(r"GEMINI_API_KEY_(\d+)", str(key))
        if not match:
            continue
        numbered.append((int(match.group(1)), str(value or "")))
    raw_keys.extend(value for _, value in sorted(numbered))

    keys: list[str] = []
    seen: set[str] = set()
    for raw_key in raw_keys:
        key = raw_key.strip()
        if not key or key in seen:
            continue
        keys.append(key)
        seen.add(key)
    return keys


def is_rate_limit_error(exc: Exception) -> bool:
    message = f"{type(exc).__name__}: {exc}".casefold()
    return any(
        token in message
        for token in (
            "429",
            "quota",
            "rate limit",
            "rate_limit",
            "resourceexhausted",
            "resource exhausted",
            "requests per minute",
            "rpm",
        )
    )


def is_daily_quota_error(exc: Exception) -> bool:
    message = f"{type(exc).__name__}: {exc}".casefold()
    return any(
        token in message
        for token in (
            "daily",
            "per day",
            "perday",
            "requests per day",
            "requests_per_day",
            "generatedrequestsperday",
            "generaterequestsperday",
            "free_tier_requests",
            "rpd",
        )
    )


def normalize_text(value: Any) -> str:
    return unicodedata.normalize("NFC", str(value or ""))


def normalize_lookup(value: Any) -> str:
    normalized = normalize_text(value).casefold().strip()
    return re.sub(r"\s+", " ", normalized)


def chunk_text(chunk: dict[str, Any]) -> str:
    return normalize_text(chunk.get("chunk_text") if chunk.get("chunk_text") is not None else chunk.get("text"))


def short_hash(payload: dict[str, Any], width: int = 16) -> str:
    serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:width]


def stable_relation_id(relation: dict[str, Any]) -> str:
    payload = {
        "chunk_hash": relation.get("chunk_hash"),
        "chunk_strategy_id": relation.get("chunk_strategy_id"),
        "evidence_text": relation.get("evidence_text"),
        "head_key": relation.get("head_key"),
        "head_kind": relation.get("head_kind"),
        "relation_source": relation.get("relation_source"),
        "relation_subtype": relation.get("relation_subtype"),
        "relation_type": relation.get("relation_type"),
        "tail_key": relation.get("tail_key"),
        "tail_kind": relation.get("tail_kind"),
    }
    return f"REL_{short_hash(payload)}"


def discover_jsonl_files(inputs: Iterable[Path], preferred_suffix: str) -> list[Path]:
    discovered: list[Path] = []
    for path in inputs:
        if not path.exists():
            raise FileNotFoundError(f"Input path does not exist: {path}")
        if path.is_dir():
            preferred = sorted(path.rglob(preferred_suffix))
            discovered.extend(preferred or sorted(path.rglob("*.jsonl")))
            continue
        if path.suffix.lower() != ".jsonl":
            raise ValueError(f"Input must be JSONL: {path}")
        discovered.append(path)

    unique: dict[Path, None] = {}
    for path in discovered:
        unique[path.resolve()] = None
    return sorted(unique)


def read_jsonl(paths: list[Path]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in paths:
        with path.open("r", encoding="utf-8") as handle:
            for line_no, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"Invalid JSON in {path}:{line_no}: {exc}") from exc
                record["_input_path"] = str(path)
                record["_input_line"] = line_no
                records.append(record)
    return records


def load_source_registry(path: Path | None = DEFAULT_SOURCE_REGISTRY) -> dict[str, dict[str, Any]]:
    if path is None or not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        records = json.load(handle)
    return {str(record["doc_id"]): record for record in records}


def filter_by_strategy(
    chunks: list[dict[str, Any]],
    entities: list[dict[str, Any]],
    strategy_id: str | None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not strategy_id:
        return chunks, entities
    return (
        [chunk for chunk in chunks if chunk.get("chunk_strategy_id") == strategy_id],
        [entity for entity in entities if entity.get("chunk_strategy_id") == strategy_id],
    )


def validate_chunk(chunk: dict[str, Any]) -> None:
    missing = sorted(key for key in REQUIRED_CHUNK_KEYS if key not in chunk)
    if missing:
        raise ValueError(
            f"Chunk {chunk.get('chunk_id') or '<unknown>'} is missing required keys: {', '.join(missing)}"
        )
    if chunk.get("domain") != "TUVI":
        raise ValueError(
            f"Chunk {chunk.get('chunk_id')} has unsupported domain {chunk.get('domain')!r}; expected TUVI."
        )
    if not chunk_text(chunk).strip():
        raise ValueError(f"Chunk {chunk.get('chunk_id')} does not contain text/chunk_text.")


def validate_entity(entity: dict[str, Any], chunks_by_id: dict[str, dict[str, Any]]) -> None:
    missing = sorted(key for key in REQUIRED_ENTITY_KEYS if key not in entity)
    if missing:
        raise ValueError(
            f"Entity {entity.get('entity_id') or '<unknown>'} is missing required keys: {', '.join(missing)}"
        )
    if entity.get("domain") != "TUVI":
        raise ValueError(
            f"Entity {entity.get('entity_id')} has unsupported domain {entity.get('domain')!r}; expected TUVI."
        )
    if entity.get("entity_type") not in ENTITY_TYPES:
        raise ValueError(f"Unsupported entity_type for {entity.get('entity_id')}: {entity.get('entity_type')}")

    chunk = chunks_by_id.get(str(entity["chunk_id"]))
    if chunk is None:
        raise ValueError(f"Entity {entity['entity_id']} references unknown chunk_id {entity['chunk_id']}.")
    for key in ("chunk_hash", "chunk_strategy_id", "source_id", "source_page"):
        if entity.get(key) != chunk.get(key):
            raise ValueError(
                f"Entity {entity['entity_id']} {key}={entity.get(key)!r} does not match chunk {chunk['chunk_id']}."
            )

    start = entity.get("char_start")
    end = entity.get("char_end")
    if not isinstance(start, int) or not isinstance(end, int) or start < 0 or end <= start:
        raise ValueError(f"Entity {entity['entity_id']} has invalid char span.")
    if end > len(chunk_text(chunk)):
        raise ValueError(f"Entity {entity['entity_id']} char span exceeds chunk text length.")


def validate_inputs(chunks: list[dict[str, Any]], entities: list[dict[str, Any]]) -> None:
    if not chunks:
        raise ValueError("No chunks were loaded.")
    if not entities:
        raise ValueError("No entities were loaded.")
    for chunk in chunks:
        validate_chunk(chunk)
    chunks_by_id = {str(chunk["chunk_id"]): chunk for chunk in chunks}
    if len(chunks_by_id) != len(chunks):
        raise ValueError("Duplicate chunk_id values are not allowed in one writer run.")
    for entity in entities:
        validate_entity(entity, chunks_by_id)


def sentence_spans(text: str) -> list[SentenceSpan]:
    spans: list[SentenceSpan] = []
    start = 0
    for match in re.finditer(r"[.!?…]\s+", text):
        raw_end = match.end()
        segment = text[start:raw_end]
        stripped = segment.strip()
        if stripped:
            left = len(segment) - len(segment.lstrip())
            right = len(segment.rstrip())
            spans.append(SentenceSpan(start + left, start + right, stripped))
        start = raw_end
    if start < len(text):
        segment = text[start:]
        stripped = segment.strip()
        if stripped:
            left = len(segment) - len(segment.lstrip())
            right = len(segment.rstrip())
            spans.append(SentenceSpan(start + left, start + right, stripped))
    return spans


def entity_overlaps_sentence(entity: dict[str, Any], sentence: SentenceSpan) -> bool:
    return int(entity["char_start"]) < sentence.end and sentence.start < int(entity["char_end"])


def entities_in_sentence(entities: list[dict[str, Any]], sentence: SentenceSpan) -> list[dict[str, Any]]:
    return sorted(
        [entity for entity in entities if entity_overlaps_sentence(entity, sentence)],
        key=lambda item: (int(item["char_start"]), int(item["char_end"]), str(item["entity_id"])),
    )


def relation_endpoint(entity: dict[str, Any]) -> dict[str, Any]:
    return {
        "key": entity["entity_id"],
        "kind": "entity",
        "canonical_name": entity["canonical_name"],
        "entity_type": entity["entity_type"],
        "domain": entity["domain"],
    }


def chunk_endpoint(chunk: dict[str, Any]) -> dict[str, Any]:
    return {
        "key": chunk["chunk_hash"],
        "kind": "chunk",
        "canonical_name": chunk["chunk_id"],
        "entity_type": "Chunk",
        "domain": chunk["domain"],
    }


def make_relation(
    relation_type: str,
    head: dict[str, Any],
    tail: dict[str, Any],
    *,
    chunk: dict[str, Any] | None,
    evidence_text: str,
    relation_source: str,
    relation_subtype: str | None = None,
    confidence: float = 1.0,
) -> dict[str, Any]:
    if relation_type not in RELATION_TYPES:
        raise ValueError(f"Unsupported relation_type: {relation_type}")
    relation = {
        "chunk_hash": chunk.get("chunk_hash") if chunk else None,
        "chunk_id": chunk.get("chunk_id") if chunk else None,
        "chunk_strategy_id": chunk.get("chunk_strategy_id") if chunk else None,
        "confidence": max(0.0, min(1.0, float(confidence))),
        "domain": chunk.get("domain") if chunk else "TUVI",
        "evidence_text": evidence_text,
        "head_canonical_name": head["canonical_name"],
        "head_entity_type": head["entity_type"],
        "head_key": head["key"],
        "head_kind": head["kind"],
        "relation_id": "",
        "relation_source": relation_source,
        "relation_subtype": relation_subtype,
        "relation_type": relation_type,
        "source_id": chunk.get("source_id") if chunk else ONTOLOGY_SOURCE_ID,
        "source_page": chunk.get("source_page") if chunk else None,
        "tail_canonical_name": tail["canonical_name"],
        "tail_entity_type": tail["entity_type"],
        "tail_key": tail["key"],
        "tail_kind": tail["kind"],
    }
    relation["relation_id"] = stable_relation_id(relation)
    return relation


def text_between(sentence_text: str, sentence_start: int, left: dict[str, Any], right: dict[str, Any]) -> str:
    left_end = int(left["char_end"]) - sentence_start
    right_start = int(right["char_start"]) - sentence_start
    if left_end <= right_start:
        return sentence_text[left_end:right_start]
    right_end = int(right["char_end"]) - sentence_start
    left_start = int(left["char_start"]) - sentence_start
    return sentence_text[right_end:left_start]


def contains_any_trigger(text: str, triggers: list[str]) -> str | None:
    lookup = normalize_lookup(text)
    for trigger in triggers:
        if normalize_lookup(trigger) in lookup:
            return trigger
    return None


def relation_already_exists(
    relations: list[dict[str, Any]],
    relation_type: str,
    head_key: str,
    tail_key: str,
) -> bool:
    return any(
        relation["relation_type"] == relation_type
        and relation["head_key"] == head_key
        and relation["tail_key"] == tail_key
        for relation in relations
    )


def derive_thuoc_cung_relations(
    sentence: SentenceSpan,
    chunk: dict[str, Any],
    sent_entities: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    relations: list[dict[str, Any]] = []
    cungs = [entity for entity in sent_entities if entity["entity_type"] == "Cung"]
    subjects = [
        entity
        for entity in sent_entities
        if entity["entity_type"] in {"Sao", "ToHop", "TuHoa", "TrangThaiSao", "CucBanMenh"}
    ]
    for subject in subjects:
        for cung in cungs:
            if subject["entity_id"] == cung["entity_id"]:
                continue
            between = text_between(sentence.text, sentence.start, subject, cung)
            trigger = contains_any_trigger(between, THUOC_CUNG_TRIGGERS)
            if not trigger:
                continue
            relations.append(
                make_relation(
                    "THUOC_CUNG",
                    relation_endpoint(subject),
                    relation_endpoint(cung),
                    chunk=chunk,
                    evidence_text=sentence.text,
                    relation_source="rule",
                    relation_subtype=normalize_lookup(trigger).replace(" ", "_"),
                    confidence=0.95,
                )
            )
    return relations


def derive_doi_chieu_relations(
    sentence: SentenceSpan,
    chunk: dict[str, Any],
    sent_entities: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    cungs = [entity for entity in sent_entities if entity["entity_type"] == "Cung"]
    relations: list[dict[str, Any]] = []
    for index, left in enumerate(cungs):
        for right in cungs[index + 1 :]:
            between = text_between(sentence.text, sentence.start, left, right)
            trigger = contains_any_trigger(between, DOI_CHIEU_TRIGGERS)
            if not trigger:
                continue
            relations.append(
                make_relation(
                    "DOI_CHIEU",
                    relation_endpoint(left),
                    relation_endpoint(right),
                    chunk=chunk,
                    evidence_text=sentence.text,
                    relation_source="rule",
                    relation_subtype=normalize_lookup(trigger).replace(" ", "_"),
                    confidence=0.96,
                )
            )
    return relations


def derive_lien_ke_relations(
    sentence: SentenceSpan,
    chunk: dict[str, Any],
    sent_entities: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    relations: list[dict[str, Any]] = []
    if not contains_any_trigger(sentence.text, LIEN_KE_TRIGGERS):
        return relations

    candidates = [entity for entity in sent_entities if entity["entity_type"] != "LuanGiai"]
    for index, left in enumerate(candidates):
        for right in candidates[index + 1 :]:
            between = text_between(sentence.text, sentence.start, left, right)
            trigger = contains_any_trigger(between, LIEN_KE_TRIGGERS)
            if not trigger:
                continue
            relations.append(
                make_relation(
                    "LIEN_KE",
                    relation_endpoint(left),
                    relation_endpoint(right),
                    chunk=chunk,
                    evidence_text=sentence.text,
                    relation_source="rule",
                    relation_subtype=normalize_lookup(trigger).replace(" ", "_"),
                    confidence=0.9,
                )
            )
    return relations


def derive_luan_giai_relations(
    sentence: SentenceSpan,
    chunk: dict[str, Any],
    sent_entities: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    luan_giai_entities = [entity for entity in sent_entities if entity["entity_type"] == "LuanGiai"]
    targets = [entity for entity in sent_entities if entity["entity_type"] != "LuanGiai"]
    relations: list[dict[str, Any]] = []
    for luan_giai in luan_giai_entities:
        for target in targets:
            relations.append(
                make_relation(
                    "APPLIES_TO",
                    relation_endpoint(luan_giai),
                    relation_endpoint(target),
                    chunk=chunk,
                    evidence_text=sentence.text,
                    relation_source="rule",
                    relation_subtype="luan_giai_sentence",
                    confidence=0.86,
                )
            )
            relations.append(
                make_relation(
                    "GIAI_THICH",
                    relation_endpoint(target),
                    relation_endpoint(luan_giai),
                    chunk=chunk,
                    evidence_text=sentence.text,
                    relation_source="rule",
                    relation_subtype="luan_giai_sentence",
                    confidence=0.86,
                )
            )
    return relations


def derive_luu_y_relations(
    sentence: SentenceSpan,
    chunk: dict[str, Any],
    sent_entities: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    trigger = contains_any_trigger(sentence.text, LUU_Y_TRIGGERS)
    if not trigger:
        return []
    return [
        make_relation(
            "LUU_Y",
            chunk_endpoint(chunk),
            relation_endpoint(entity),
            chunk=chunk,
            evidence_text=sentence.text,
            relation_source="rule",
            relation_subtype=normalize_lookup(trigger).replace(" ", "_"),
            confidence=0.82,
        )
        for entity in sent_entities
        if entity["entity_type"] != "LuanGiai"
    ]


def derive_related_relations(
    sentence: SentenceSpan,
    chunk: dict[str, Any],
    sent_entities: list[dict[str, Any]],
    existing_relations: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    relations: list[dict[str, Any]] = []
    candidates = [entity for entity in sent_entities if entity["entity_type"] != "LuanGiai"]
    for index, left in enumerate(candidates):
        for right in candidates[index + 1 :]:
            between = text_between(sentence.text, sentence.start, left, right)
            trigger = contains_any_trigger(between, RELATED_TRIGGERS)
            if not trigger:
                continue
            if relation_already_exists(existing_relations, "THUOC_CUNG", left["entity_id"], right["entity_id"]):
                continue
            if relation_already_exists(existing_relations, "THUOC_CUNG", right["entity_id"], left["entity_id"]):
                continue
            if relation_already_exists(existing_relations, "DOI_CHIEU", left["entity_id"], right["entity_id"]):
                continue
            if relation_already_exists(existing_relations, "LIEN_KE", left["entity_id"], right["entity_id"]):
                continue
            relations.append(
                make_relation(
                    "RELATED_TO",
                    relation_endpoint(left),
                    relation_endpoint(right),
                    chunk=chunk,
                    evidence_text=sentence.text,
                    relation_source="rule",
                    relation_subtype=normalize_lookup(trigger).replace(" ", "_"),
                    confidence=0.74,
                )
            )
    return relations


def derive_rule_relations(
    chunks: list[dict[str, Any]],
    entities: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    by_chunk: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for entity in entities:
        by_chunk[str(entity["chunk_id"])].append(entity)

    chunks_by_id = {str(chunk["chunk_id"]): chunk for chunk in chunks}
    relations: list[dict[str, Any]] = []
    for chunk_id, chunk_entities in by_chunk.items():
        chunk = chunks_by_id[chunk_id]
        text = chunk_text(chunk)
        for sentence in sentence_spans(text):
            sent_entities = entities_in_sentence(chunk_entities, sentence)
            if len(sent_entities) < 1:
                continue
            current: list[dict[str, Any]] = []
            current.extend(derive_thuoc_cung_relations(sentence, chunk, sent_entities))
            current.extend(derive_doi_chieu_relations(sentence, chunk, sent_entities))
            current.extend(derive_lien_ke_relations(sentence, chunk, sent_entities))
            current.extend(derive_luan_giai_relations(sentence, chunk, sent_entities))
            current.extend(derive_luu_y_relations(sentence, chunk, sent_entities))
            current.extend(derive_related_relations(sentence, chunk, sent_entities, current))
            relations.extend(current)
    return deduplicate_relations(relations)


class MockRelationLLMAdapter:
    model_name = "mock-relation-llm"

    def extract(self, chunk: dict[str, Any], entities: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return []


class GeminiKeysUnavailableError(RuntimeError):
    """Raised when every configured Gemini API key is unavailable for this run."""


class RequestRateLimiter:
    def __init__(self, requests_per_minute: float | None) -> None:
        self.min_interval_seconds = 0.0
        if requests_per_minute and requests_per_minute > 0:
            self.min_interval_seconds = 60.0 / requests_per_minute
        self._last_request_at = 0.0

    def wait(self) -> None:
        if self.min_interval_seconds <= 0:
            return
        now = time.monotonic()
        sleep_for = self.min_interval_seconds - (now - self._last_request_at)
        if sleep_for > 0:
            time.sleep(sleep_for)
        self._last_request_at = time.monotonic()


class GeminiRelationLLMAdapter:
    def __init__(
        self,
        api_key: str | None,
        model_name: str,
        *,
        requests_per_minute: float | None = DEFAULT_REQUESTS_PER_MINUTE,
    ) -> None:
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required unless --mock-llm or --relation-mode rule is used.")
        try:
            import google.generativeai as genai  # type: ignore[import-not-found]
        except ImportError as exc:
            raise RuntimeError("google-generativeai is not installed.") from exc
        self._api_key = api_key
        self._genai = genai
        self._rate_limiter = RequestRateLimiter(requests_per_minute)
        self.model_name = model_name

    def extract(self, chunk: dict[str, Any], entities: list[dict[str, Any]]) -> list[dict[str, Any]]:
        self._rate_limiter.wait()
        self._genai.configure(api_key=self._api_key)
        model = self._genai.GenerativeModel(self.model_name)
        response = model.generate_content(build_relation_prompt(chunk, entities))
        payload = parse_json_payload(getattr(response, "text", ""))
        relations = payload.get("relations", payload if isinstance(payload, list) else [])
        if not isinstance(relations, list):
            raise ValueError("Gemini relation response must contain a relations list.")
        return [relation for relation in relations if isinstance(relation, dict)]


class MultiKeyGeminiRelationLLMAdapter:
    def __init__(
        self,
        clients: list[Any],
        *,
        max_retries: int = 6,
        retry_base_seconds: float = 10.0,
        max_retry_sleep_seconds: float = DEFAULT_MAX_RETRY_SLEEP_SECONDS,
        stop_on_daily_quota: bool = True,
        sleep_fn: Any = time.sleep,
        time_fn: Any = time.monotonic,
    ) -> None:
        if not clients:
            raise ValueError("GEMINI_API_KEYS or GEMINI_API_KEY is required unless --mock-llm or --relation-mode rule is used.")
        self.clients = clients
        self.model_name = str(getattr(clients[0], "model_name", DEFAULT_RELATION_MODEL))
        self.max_retries = max(0, max_retries)
        self.retry_base_seconds = max(0.0, retry_base_seconds)
        self.max_retry_sleep_seconds = max(0.0, max_retry_sleep_seconds)
        self.stop_on_daily_quota = stop_on_daily_quota
        self._sleep = sleep_fn
        self._time = time_fn
        self._cursor = 0
        self._disabled = [False for _ in clients]
        self._available_after = [0.0 for _ in clients]
        self._rate_limit_attempts = [0 for _ in clients]
        self.api_key_usage_counts = {self._key_label(index): 0 for index in range(len(clients))}
        self.quota_failover_count = 0

    @property
    def api_key_count(self) -> int:
        return len(self.clients)

    @property
    def disabled_key_count(self) -> int:
        return sum(1 for disabled in self._disabled if disabled)

    def get_usage_summary(self) -> dict[str, Any]:
        return {
            "api_key_count": self.api_key_count,
            "api_key_usage_counts": dict(self.api_key_usage_counts),
            "disabled_key_count": self.disabled_key_count,
            "quota_failover_count": self.quota_failover_count,
        }

    def _key_label(self, index: int) -> str:
        return f"key_{index + 1}"

    def _next_available_index(self) -> int:
        if all(self._disabled):
            raise GeminiKeysUnavailableError("All Gemini API keys are unavailable for this run.")

        while True:
            now = self._time()
            next_available_time: float | None = None
            for offset in range(len(self.clients)):
                index = (self._cursor + offset) % len(self.clients)
                if self._disabled[index]:
                    continue
                available_at = self._available_after[index]
                if available_at <= now:
                    self._cursor = (index + 1) % len(self.clients)
                    return index
                if next_available_time is None or available_at < next_available_time:
                    next_available_time = available_at

            if next_available_time is None:
                raise GeminiKeysUnavailableError("All Gemini API keys are unavailable for this run.")
            self._sleep(max(0.0, next_available_time - now))

    def _sleep_for_rate_limit(self, index: int) -> None:
        attempt = self._rate_limit_attempts[index]
        if attempt >= self.max_retries:
            self._disabled[index] = True
            return

        client = self.clients[index]
        rate_limiter = getattr(client, "_rate_limiter", None)
        min_interval = float(getattr(rate_limiter, "min_interval_seconds", 0.0) or 0.0)
        sleep_for = min(
            self.max_retry_sleep_seconds,
            max(min_interval, self.retry_base_seconds * (2**attempt)),
        )
        self._rate_limit_attempts[index] += 1
        self._available_after[index] = self._time() + sleep_for

    def extract(self, chunk: dict[str, Any], entities: list[dict[str, Any]]) -> list[dict[str, Any]]:
        while True:
            index = self._next_available_index()
            client = self.clients[index]
            label = self._key_label(index)
            try:
                relations = client.extract(chunk, entities)
                self._rate_limit_attempts[index] = 0
                self.api_key_usage_counts[label] += 1
                return relations
            except Exception as exc:
                if self.stop_on_daily_quota and is_daily_quota_error(exc):
                    self._disabled[index] = True
                    self.quota_failover_count += 1
                    print(
                        f"Daily quota exhausted for Gemini API {label}; trying another key.",
                        file=sys.stderr,
                        flush=True,
                    )
                    continue
                if is_rate_limit_error(exc):
                    self.quota_failover_count += 1
                    self._sleep_for_rate_limit(index)
                    print(
                        f"Rate limit for Gemini API {label}; trying another key.",
                        file=sys.stderr,
                        flush=True,
                    )
                    continue
                raise


def build_relation_prompt(chunk: dict[str, Any], entities: list[dict[str, Any]]) -> str:
    entity_payload = [
        {
            "entity_id": entity["entity_id"],
            "entity_type": entity["entity_type"],
            "canonical_name": entity["canonical_name"],
            "surface_text": entity.get("surface_text"),
            "char_start": entity["char_start"],
            "char_end": entity["char_end"],
        }
        for entity in entities
    ]
    relation_types = ", ".join(sorted(EXTRACTABLE_RELATION_TYPES))
    return (
        "Bạn là relation extractor cho corpus Tử Vi. "
        "Chỉ tạo relation giữa các entity_id đã được cung cấp; không tạo entity mới. "
        "Relation phải có evidence_text xuất hiện nguyên văn trong chunk_text. "
        f"Whitelist relation_type: {relation_types}.\n"
        "Output JSON strict dạng {\"relations\": [{\"relation_type\": \"...\", "
        "\"head_entity_id\": \"...\", \"tail_entity_id\": \"...\", "
        "\"evidence_text\": \"...\", \"relation_subtype\": \"...\", "
        "\"confidence\": 0.0}]}.\n"
        f"chunk_id: {chunk.get('chunk_id')}\n"
        f"chunk_strategy_id: {chunk.get('chunk_strategy_id')}\n"
        f"entities:\n{json.dumps(entity_payload, ensure_ascii=False)}\n"
        f"chunk_text:\n{chunk_text(chunk)}"
    )


def parse_json_payload(text: str) -> Any:
    stripped = text.strip()
    fenced = re.match(r"^```(?:json)?\s*(.*?)\s*```$", stripped, flags=re.S | re.I)
    if fenced:
        stripped = fenced.group(1).strip()
    return json.loads(stripped)


def validate_relation_evidence(relation: dict[str, Any], chunk: dict[str, Any] | None) -> None:
    if relation["relation_source"] == "ontology":
        return
    evidence = normalize_text(relation.get("evidence_text"))
    if not evidence.strip():
        raise ValueError(f"Relation {relation.get('relation_id')} is missing evidence_text.")
    if chunk is None:
        raise ValueError(f"Relation {relation.get('relation_id')} is missing chunk provenance.")
    if evidence not in chunk_text(chunk):
        raise ValueError(
            f"Relation {relation.get('relation_id')} evidence_text is not present in chunk {chunk['chunk_id']}."
        )


def postprocess_llm_relations(
    raw_relations: list[dict[str, Any]],
    chunk: dict[str, Any],
    entities: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    entities_by_id = {str(entity["entity_id"]): entity for entity in entities}
    records: list[dict[str, Any]] = []
    for raw in raw_relations:
        relation_type = str(raw.get("relation_type") or "").strip()
        if relation_type not in EXTRACTABLE_RELATION_TYPES:
            continue
        head = entities_by_id.get(str(raw.get("head_entity_id") or raw.get("head_id") or ""))
        tail = entities_by_id.get(str(raw.get("tail_entity_id") or raw.get("tail_id") or ""))
        if head is None or tail is None or head["entity_id"] == tail["entity_id"]:
            continue

        evidence_text = normalize_text(raw.get("evidence_text") or "")
        if evidence_text not in chunk_text(chunk):
            continue
        confidence = raw.get("confidence", 0.0)
        try:
            confidence = float(confidence)
        except (TypeError, ValueError):
            confidence = 0.0

        relation = make_relation(
            relation_type,
            relation_endpoint(head),
            relation_endpoint(tail),
            chunk=chunk,
            evidence_text=evidence_text,
            relation_source="llm",
            relation_subtype=normalize_text(raw.get("relation_subtype") or "llm_extracted").strip(),
            confidence=confidence,
        )
        records.append(relation)
    return deduplicate_relations(records)


def extract_llm_relations(
    chunks: list[dict[str, Any]],
    entities: list[dict[str, Any]],
    *,
    mock_llm: bool,
    model_name: str,
    requests_per_minute: float | None = DEFAULT_REQUESTS_PER_MINUTE,
    max_retries: int = 6,
    retry_base_seconds: float = 10.0,
    max_retry_sleep_seconds: float = DEFAULT_MAX_RETRY_SLEEP_SECONDS,
    stop_on_daily_quota: bool = True,
) -> list[dict[str, Any]]:
    by_chunk: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for entity in entities:
        by_chunk[str(entity["chunk_id"])].append(entity)

    adapter: Any
    if mock_llm:
        adapter = MockRelationLLMAdapter()
    else:
        clients = [
            GeminiRelationLLMAdapter(
                api_key,
                model_name,
                requests_per_minute=requests_per_minute,
            )
            for api_key in load_gemini_api_keys()
        ]
        adapter = MultiKeyGeminiRelationLLMAdapter(
            clients,
            max_retries=max_retries,
            retry_base_seconds=retry_base_seconds,
            max_retry_sleep_seconds=max_retry_sleep_seconds,
            stop_on_daily_quota=stop_on_daily_quota,
        )

    relations: list[dict[str, Any]] = []
    for chunk in chunks:
        chunk_entities = by_chunk.get(str(chunk["chunk_id"]), [])
        if len(chunk_entities) < 2:
            continue
        raw_relations = adapter.extract(chunk, chunk_entities)
        relations.extend(postprocess_llm_relations(raw_relations, chunk, chunk_entities))
    return deduplicate_relations(relations)


def make_ontology_entity(canonical_name: str) -> dict[str, Any]:
    entity_id = f"ONTOLOGY_CUNG_{short_hash({'canonical_name': canonical_name}, 10)}"
    return {
        "aliases_matched": [],
        "canonical_name": canonical_name,
        "char_end": 0,
        "char_start": 0,
        "chunk_hash": None,
        "chunk_id": None,
        "chunk_strategy_id": None,
        "confidence": 1.0,
        "created_at": utc_now(),
        "domain": "TUVI",
        "entity_dict_version": "tuvi_ontology_v1",
        "entity_id": entity_id,
        "entity_type": "Cung",
        "evidence_text": ONTOLOGY_SOURCE_ID,
        "extraction_model": "ontology",
        "needs_review": False,
        "prompt_version": "ontology_v1",
        "section_id": None,
        "source_id": ONTOLOGY_SOURCE_ID,
        "source_name": "Tử Vi ontology v1",
        "source_page": None,
        "surface_text": canonical_name,
    }


def build_ontology_entities_and_relations() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    entities = [make_ontology_entity(name) for name in CUNG_CYCLE]
    by_name = {entity["canonical_name"]: entity for entity in entities}
    relations: list[dict[str, Any]] = []

    for index, name in enumerate(CUNG_CYCLE):
        left = by_name[name]
        right = by_name[CUNG_CYCLE[(index + 1) % len(CUNG_CYCLE)]]
        for head, tail in ((left, right), (right, left)):
            relations.append(
                make_relation(
                    "LIEN_KE",
                    relation_endpoint(head),
                    relation_endpoint(tail),
                    chunk=None,
                    evidence_text=ONTOLOGY_SOURCE_ID,
                    relation_source="ontology",
                    relation_subtype="functional_cung_cycle",
                    confidence=1.0,
                )
            )

    for index, name in enumerate(CUNG_CYCLE[:6]):
        left = by_name[name]
        right = by_name[CUNG_CYCLE[index + 6]]
        for head, tail in ((left, right), (right, left)):
            relations.append(
                make_relation(
                    "DOI_CHIEU",
                    relation_endpoint(head),
                    relation_endpoint(tail),
                    chunk=None,
                    evidence_text=ONTOLOGY_SOURCE_ID,
                    relation_source="ontology",
                    relation_subtype="functional_cung_opposite",
                    confidence=1.0,
                )
            )

    return entities, deduplicate_relations(relations)


def deduplicate_relations(relations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    unique: dict[str, dict[str, Any]] = {}
    for relation in relations:
        unique[relation["relation_id"]] = relation
    return list(unique.values())


def validate_relations(
    relations: list[dict[str, Any]],
    chunks_by_hash: dict[str, dict[str, Any]],
    entity_keys: set[str],
) -> None:
    for relation in relations:
        if relation["relation_type"] not in RELATION_TYPES:
            raise ValueError(f"Unsupported relation_type: {relation['relation_type']}")
        if relation["relation_source"] not in {"rule", "llm", "ontology"}:
            raise ValueError(f"Unsupported relation_source: {relation['relation_source']}")
        for side in ("head", "tail"):
            kind = relation[f"{side}_kind"]
            key = relation[f"{side}_key"]
            if kind == "entity" and key not in entity_keys:
                raise ValueError(f"Relation {relation['relation_id']} references unknown {side} entity {key}.")
            if kind == "chunk" and key not in chunks_by_hash:
                raise ValueError(f"Relation {relation['relation_id']} references unknown {side} chunk {key}.")

        chunk = chunks_by_hash.get(relation.get("chunk_hash"))
        validate_relation_evidence(relation, chunk)


def build_source_records(
    chunks: list[dict[str, Any]],
    registry: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    records: dict[tuple[str, str], dict[str, Any]] = {}
    for chunk in chunks:
        source_id = str(chunk["source_id"])
        source_info = registry.get(source_id, {})
        key = (source_id, "TUVI")
        records[key] = {
            "citation_short": source_info.get("citation_short") or source_id,
            "domain": "TUVI",
            "file_name": source_info.get("file_name"),
            "source_id": source_id,
            "source_name": chunk.get("source_name") or source_info.get("title") or source_id,
            "source_type": "book",
        }
    return list(records.values())


def build_chunk_records(chunks: list[dict[str, Any]], entities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    entity_counts: dict[str, Counter[str]] = defaultdict(Counter)
    for entity in entities:
        entity_counts[str(entity["chunk_id"])][str(entity["entity_type"])] += 1

    records: list[dict[str, Any]] = []
    for chunk in chunks:
        text = chunk_text(chunk)
        provenance = dict(chunk.get("provenance") or {})
        metadata = dict(chunk.get("metadata") or {})
        metadata.update(
            {
                "chunk_id": chunk["chunk_id"],
                "chunk_strategy_id": chunk["chunk_strategy_id"],
                "entity_counts": dict(entity_counts.get(str(chunk["chunk_id"]), Counter())),
                "ingested_at": utc_now(),
                "provenance": provenance,
                "source_id": chunk["source_id"],
            }
        )
        metadata_json = json.dumps(metadata, ensure_ascii=False, sort_keys=True)
        provenance_json = json.dumps(provenance, ensure_ascii=False, sort_keys=True)
        records.append(
            {
                "char_end": chunk.get("char_end"),
                "char_start": chunk.get("char_start"),
                "chunk_hash": chunk["chunk_hash"],
                "chunk_id": chunk["chunk_id"],
                "chunk_strategy_id": chunk["chunk_strategy_id"],
                "chunk_text": text,
                "chunk_type": chunk.get("chunk_type"),
                "domain": chunk["domain"],
                "metadata": metadata,
                "metadata_json": metadata_json,
                "parent_id": chunk.get("parent_id"),
                "provenance": provenance,
                "provenance_json": provenance_json,
                "section_id": chunk.get("section_id"),
                "source_id": chunk["source_id"],
                "source_name": chunk.get("source_name") or chunk["source_id"],
                "source_page": chunk.get("source_page"),
                "source_type": "book",
                "text": text,
                "token_count": chunk.get("token_count"),
            }
        )
    return records


def build_entity_records(entities: list[dict[str, Any]], ontology_entities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_identity: dict[tuple[str, str, str], dict[str, Any]] = {}
    for entity in [*entities, *ontology_entities]:
        key = (str(entity["canonical_name"]), str(entity["entity_type"]), str(entity["domain"]))
        aliases = entity.get("aliases_matched") if isinstance(entity.get("aliases_matched"), list) else []
        record = by_identity.setdefault(
            key,
            {
                "aliases": sorted({str(alias) for alias in aliases}),
                "canonical_name": entity["canonical_name"],
                "domain": entity["domain"],
                "entity_type": entity["entity_type"],
                "first_entity_id": entity["entity_id"],
                "source_ids": set(),
            },
        )
        record["aliases"] = sorted(set(record["aliases"]) | {str(alias) for alias in aliases})
        if entity.get("source_id"):
            record["source_ids"].add(str(entity["source_id"]))

    records: list[dict[str, Any]] = []
    for record in by_identity.values():
        copied = dict(record)
        copied["source_ids"] = sorted(copied["source_ids"])
        records.append(copied)
    return records


def build_mention_records(entities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for entity in entities:
        records.append(
            {
                "aliases_matched": entity.get("aliases_matched") or [],
                "canonical_name": entity["canonical_name"],
                "char_end": entity["char_end"],
                "char_start": entity["char_start"],
                "chunk_hash": entity["chunk_hash"],
                "chunk_id": entity["chunk_id"],
                "chunk_strategy_id": entity["chunk_strategy_id"],
                "confidence": entity.get("confidence", 0.0),
                "domain": entity["domain"],
                "entity_id": entity["entity_id"],
                "entity_type": entity["entity_type"],
                "evidence_text": entity["evidence_text"],
                "source_id": entity["source_id"],
                "source_page": entity["source_page"],
                "surface_text": entity.get("surface_text") or entity["evidence_text"],
            }
        )
    return records


def build_ingest_payload(
    chunks: list[dict[str, Any]],
    entities: list[dict[str, Any]],
    *,
    relation_mode: str = "hybrid",
    mock_llm: bool = False,
    model_name: str = DEFAULT_RELATION_MODEL,
    requests_per_minute: float | None = DEFAULT_REQUESTS_PER_MINUTE,
    max_retries: int = 6,
    retry_base_seconds: float = 10.0,
    max_retry_sleep_seconds: float = DEFAULT_MAX_RETRY_SLEEP_SECONDS,
    stop_on_daily_quota: bool = True,
    include_ontology: bool = True,
    registry: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    validate_inputs(chunks, entities)
    registry = registry or {}
    chunks_by_hash = {str(chunk["chunk_hash"]): chunk for chunk in chunks}

    rule_relations = derive_rule_relations(chunks, entities) if relation_mode in {"rule", "hybrid"} else []
    llm_relations = (
        extract_llm_relations(
            chunks,
            entities,
            mock_llm=mock_llm,
            model_name=model_name,
            requests_per_minute=requests_per_minute,
            max_retries=max_retries,
            retry_base_seconds=retry_base_seconds,
            max_retry_sleep_seconds=max_retry_sleep_seconds,
            stop_on_daily_quota=stop_on_daily_quota,
        )
        if relation_mode in {"llm", "hybrid"}
        else []
    )
    ontology_entities: list[dict[str, Any]] = []
    ontology_relations: list[dict[str, Any]] = []
    if include_ontology:
        ontology_entities, ontology_relations = build_ontology_entities_and_relations()

    relations = deduplicate_relations([*rule_relations, *llm_relations, *ontology_relations])
    entity_keys = {str(entity["entity_id"]) for entity in entities} | {
        str(entity["entity_id"]) for entity in ontology_entities
    }
    validate_relations(relations, chunks_by_hash, entity_keys)

    return {
        "chunk_records": build_chunk_records(chunks, entities),
        "entity_records": build_entity_records(entities, ontology_entities),
        "mention_records": build_mention_records(entities),
        "relation_records": relations,
        "source_records": build_source_records(chunks, registry),
        "summary": build_summary(chunks, entities, rule_relations, llm_relations, ontology_relations, relations),
    }


def build_summary(
    chunks: list[dict[str, Any]],
    entities: list[dict[str, Any]],
    rule_relations: list[dict[str, Any]],
    llm_relations: list[dict[str, Any]],
    ontology_relations: list[dict[str, Any]],
    all_relations: list[dict[str, Any]],
) -> dict[str, Any]:
    relation_counts = Counter(relation["relation_type"] for relation in all_relations)
    source_counts = Counter(relation["relation_source"] for relation in all_relations)
    return {
        "chunk_count": len(chunks),
        "entity_count": len(entities),
        "generated_at": utc_now(),
        "llm_relation_count": len(llm_relations),
        "mention_relation_count": len(entities),
        "ontology_relation_count": len(ontology_relations),
        "relation_counts": dict(sorted(relation_counts.items())),
        "relation_source_counts": dict(sorted(source_counts.items())),
        "rule_relation_count": len(rule_relations),
        "total_relation_count": len(all_relations) + len(entities),
    }


def write_supabase_source_chunks(database_url: str, chunk_records: list[dict[str, Any]], batch_size: int) -> int:
    import psycopg
    from psycopg.types.json import Jsonb

    sql = """
        INSERT INTO source_chunks (
            source_id, source_name, source_type, domain, source_page, title,
            chunk_id, chunk_strategy_id, chunk_type, parent_id, section_id,
            text, chunk_text, chunk_hash, provenance, metadata
        )
        VALUES (
            %(source_id)s, %(source_name)s, %(source_type)s, %(domain)s, %(source_page)s, %(title)s,
            %(chunk_id)s, %(chunk_strategy_id)s, %(chunk_type)s, %(parent_id)s, %(section_id)s,
            %(text)s, %(chunk_text)s, %(chunk_hash)s, %(provenance)s, %(metadata)s
        )
        ON CONFLICT (chunk_hash) DO UPDATE SET
            source_id = EXCLUDED.source_id,
            source_name = EXCLUDED.source_name,
            source_type = EXCLUDED.source_type,
            domain = EXCLUDED.domain,
            source_page = EXCLUDED.source_page,
            title = EXCLUDED.title,
            chunk_id = EXCLUDED.chunk_id,
            chunk_strategy_id = EXCLUDED.chunk_strategy_id,
            chunk_type = EXCLUDED.chunk_type,
            parent_id = EXCLUDED.parent_id,
            section_id = EXCLUDED.section_id,
            text = EXCLUDED.text,
            chunk_text = EXCLUDED.chunk_text,
            provenance = EXCLUDED.provenance,
            metadata = EXCLUDED.metadata
    """
    count = 0
    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            for index in range(0, len(chunk_records), batch_size):
                batch = []
                for record in chunk_records[index : index + batch_size]:
                    row = dict(record)
                    row["title"] = record.get("section_id")
                    row["metadata"] = Jsonb(record["metadata"])
                    row["provenance"] = Jsonb(record["provenance"])
                    batch.append(row)
                cur.executemany(sql, batch)
                count += len(batch)
        conn.commit()
    return count


def safe_label(entity_type: str) -> str:
    if entity_type not in ENTITY_TYPES:
        raise ValueError(f"Unsafe or unsupported entity label: {entity_type}")
    return entity_type


def safe_relation_type(relation_type: str) -> str:
    if relation_type not in RELATION_TYPES:
        raise ValueError(f"Unsafe or unsupported relation type: {relation_type}")
    return relation_type


def write_neo4j_graph(
    uri: str,
    username: str,
    password: str,
    database: str | None,
    payload: dict[str, Any],
    batch_size: int,
) -> dict[str, int]:
    from neo4j import GraphDatabase

    counts: Counter[str] = Counter()
    driver = GraphDatabase.driver(uri, auth=(username, password))
    try:
        with driver.session(database=database or None) as session:
            counts["sources"] += session.execute_write(write_sources_tx, payload["source_records"])
            counts["chunks"] += session.execute_write(write_chunks_tx, payload["chunk_records"], batch_size)
            counts["source_chunk_edges"] += session.execute_write(
                write_source_chunk_edges_tx, payload["chunk_records"], batch_size
            )
            counts["entities"] += session.execute_write(write_entities_tx, payload["entity_records"])
            counts["mentions"] += session.execute_write(write_mentions_tx, payload["mention_records"], batch_size)
            counts["relations"] += session.execute_write(write_relations_tx, payload["relation_records"], batch_size)
    finally:
        driver.close()
    return dict(counts)


def write_sources_tx(tx: Any, records: list[dict[str, Any]]) -> int:
    tx.run(
        """
        UNWIND $records AS row
        MERGE (s:Source {source_id: row.source_id, domain: row.domain})
        SET s.source_name = row.source_name,
            s.source_type = row.source_type,
            s.citation_short = row.citation_short,
            s.file_name = row.file_name
        """,
        records=records,
    )
    return len(records)


def write_chunks_tx(tx: Any, records: list[dict[str, Any]], batch_size: int) -> int:
    for batch in batched(records, batch_size):
        tx.run(
            """
            UNWIND $records AS row
            MERGE (c:Chunk {chunk_hash: row.chunk_hash})
            SET c.id = row.chunk_id,
                c.chunk_id = row.chunk_id,
                c.chunk_strategy_id = row.chunk_strategy_id,
                c.chunk_type = row.chunk_type,
                c.parent_id = row.parent_id,
                c.section_id = row.section_id,
                c.text = row.text,
                c.chunk_text = row.chunk_text,
                c.domain = row.domain,
                c.source_id = row.source_id,
                c.source_name = row.source_name,
                c.source_page = row.source_page,
                c.char_start = row.char_start,
                c.char_end = row.char_end,
                c.token_count = row.token_count,
                c.provenance_json = row.provenance_json,
                c.metadata_json = row.metadata_json
            """,
            records=batch,
        )
    return len(records)


def write_source_chunk_edges_tx(tx: Any, records: list[dict[str, Any]], batch_size: int) -> int:
    for batch in batched(records, batch_size):
        tx.run(
            """
            UNWIND $records AS row
            MATCH (s:Source {source_id: row.source_id, domain: row.domain})
            MATCH (c:Chunk {chunk_hash: row.chunk_hash})
            MERGE (s)-[has_chunk:HAS_CHUNK]->(c)
            SET has_chunk.chunk_hash = row.chunk_hash,
                has_chunk.chunk_strategy_id = row.chunk_strategy_id
            MERGE (c)-[has_source:HAS_SOURCE]->(s)
            SET has_source.chunk_hash = row.chunk_hash,
                has_source.chunk_strategy_id = row.chunk_strategy_id
            """,
            records=batch,
        )
    return len(records) * 2


def write_entities_tx(tx: Any, records: list[dict[str, Any]]) -> int:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[str(record["entity_type"])].append(record)
    for entity_type, rows in grouped.items():
        label = safe_label(entity_type)
        tx.run(
            f"""
            UNWIND $records AS row
            MERGE (e:Entity:{label} {{
                canonical_name: row.canonical_name,
                entity_type: row.entity_type,
                domain: row.domain
            }})
            SET e.aliases = row.aliases,
                e.first_entity_id = row.first_entity_id,
                e.source_ids = row.source_ids
            """,
            records=rows,
        )
    return len(records)


def write_mentions_tx(tx: Any, records: list[dict[str, Any]], batch_size: int) -> int:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[str(record["entity_type"])].append(record)
    for entity_type, rows in grouped.items():
        label = safe_label(entity_type)
        for batch in batched(rows, batch_size):
            tx.run(
                f"""
                UNWIND $records AS row
                MATCH (c:Chunk {{chunk_hash: row.chunk_hash}})
                MATCH (e:Entity:{label} {{
                    canonical_name: row.canonical_name,
                    entity_type: row.entity_type,
                    domain: row.domain
                }})
                MERGE (c)-[r:MENTIONS {{entity_id: row.entity_id, chunk_hash: row.chunk_hash}}]->(e)
                SET r.chunk_id = row.chunk_id,
                    r.chunk_strategy_id = row.chunk_strategy_id,
                    r.source_id = row.source_id,
                    r.source_page = row.source_page,
                    r.evidence_text = row.evidence_text,
                    r.surface_text = row.surface_text,
                    r.char_start = row.char_start,
                    r.char_end = row.char_end,
                    r.confidence = row.confidence
                """,
                records=batch,
            )
    return len(records)


def write_relations_tx(tx: Any, records: list[dict[str, Any]], batch_size: int) -> int:
    count = 0
    for relation_type in sorted({record["relation_type"] for record in records}):
        rel_type = safe_relation_type(relation_type)
        rows = [record for record in records if record["relation_type"] == relation_type]
        for head_kind in sorted({record["head_kind"] for record in rows}):
            for tail_kind in sorted({record["tail_kind"] for record in rows if record["head_kind"] == head_kind}):
                batch_rows = [
                    record
                    for record in rows
                    if record["head_kind"] == head_kind and record["tail_kind"] == tail_kind
                ]
                for batch in batched(batch_rows, batch_size):
                    tx.run(build_relation_cypher(rel_type, head_kind, tail_kind), records=batch)
                    count += len(batch)
    return count


def build_relation_cypher(relation_type: str, head_kind: str, tail_kind: str) -> str:
    head_match = "MATCH (h:Chunk {chunk_hash: row.head_key})" if head_kind == "chunk" else (
        "MATCH (h:Entity {canonical_name: row.head_canonical_name, "
        "entity_type: row.head_entity_type, domain: row.domain})"
    )
    tail_match = "MATCH (t:Chunk {chunk_hash: row.tail_key})" if tail_kind == "chunk" else (
        "MATCH (t:Entity {canonical_name: row.tail_canonical_name, "
        "entity_type: row.tail_entity_type, domain: row.domain})"
    )
    return f"""
        UNWIND $records AS row
        {head_match}
        {tail_match}
        MERGE (h)-[r:{relation_type} {{relation_id: row.relation_id}}]->(t)
        SET r.chunk_id = row.chunk_id,
            r.chunk_hash = row.chunk_hash,
            r.chunk_strategy_id = row.chunk_strategy_id,
            r.source_id = row.source_id,
            r.source_page = row.source_page,
            r.evidence_text = row.evidence_text,
            r.relation_source = row.relation_source,
            r.relation_subtype = row.relation_subtype,
            r.confidence = row.confidence
    """


def batched(records: list[dict[str, Any]], batch_size: int) -> Iterable[list[dict[str, Any]]]:
    size = max(1, batch_size)
    for index in range(0, len(records), size):
        yield records[index : index + size]


def write_summary(path: Path, payload: dict[str, Any], dry_run: bool, db_counts: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    summary = dict(payload["summary"])
    summary["dry_run"] = dry_run
    summary["db_write_counts"] = db_counts
    path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write Tử Vi graph and source chunk provenance.")
    parser.add_argument("--chunks-input", nargs="+", type=Path, required=True)
    parser.add_argument("--entities-input", nargs="+", type=Path, required=True)
    parser.add_argument("--chunking-strategy", default=None)
    parser.add_argument("--source-registry", type=Path, default=DEFAULT_SOURCE_REGISTRY)
    parser.add_argument("--relation-mode", choices=["rule", "llm", "hybrid"], default="hybrid")
    parser.add_argument("--model", default=DEFAULT_RELATION_MODEL)
    parser.add_argument("--mock-llm", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-neo4j", action="store_true")
    parser.add_argument("--skip-supabase", action="store_true")
    parser.add_argument("--skip-ontology", action="store_true")
    parser.add_argument("--batch-size", type=int, default=500)
    parser.add_argument("--requests-per-minute", type=float, default=DEFAULT_REQUESTS_PER_MINUTE)
    parser.add_argument("--max-retries", type=int, default=6)
    parser.add_argument("--retry-base-seconds", type=float, default=10.0)
    parser.add_argument("--max-retry-sleep-seconds", type=float, default=DEFAULT_MAX_RETRY_SLEEP_SECONDS)
    parser.add_argument("--stop-on-daily-quota", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--summary-output", type=Path, default=None)
    return parser.parse_args(argv)


def run(argv: list[str] | None = None) -> dict[str, Any]:
    load_dotenv(ROOT_DIR / ".env")
    args = parse_args(argv)
    chunk_files = discover_jsonl_files(args.chunks_input, "*_chunks.jsonl")
    entity_files = discover_jsonl_files(args.entities_input, "*_entities.jsonl")
    chunks = read_jsonl(chunk_files)
    entities = read_jsonl(entity_files)
    chunks, entities = filter_by_strategy(chunks, entities, args.chunking_strategy)
    if not chunks:
        raise ValueError("No chunks matched the requested input/strategy.")
    if not entities:
        raise ValueError("No entities matched the requested input/strategy.")

    payload = build_ingest_payload(
        chunks,
        entities,
        relation_mode=args.relation_mode,
        mock_llm=args.mock_llm,
        model_name=args.model,
        requests_per_minute=args.requests_per_minute,
        max_retries=args.max_retries,
        retry_base_seconds=args.retry_base_seconds,
        max_retry_sleep_seconds=args.max_retry_sleep_seconds,
        stop_on_daily_quota=args.stop_on_daily_quota,
        include_ontology=not args.skip_ontology,
        registry=load_source_registry(args.source_registry),
    )

    db_counts: dict[str, Any] = {}
    if not args.dry_run:
        if not args.skip_supabase:
            database_url = os.getenv("DATABASE_URL")
            if not database_url:
                raise ValueError("DATABASE_URL is required unless --dry-run or --skip-supabase is used.")
            db_counts["supabase_source_chunks"] = write_supabase_source_chunks(
                database_url,
                payload["chunk_records"],
                args.batch_size,
            )
        if not args.skip_neo4j:
            required_env = {
                "NEO4J_URI": os.getenv("NEO4J_URI"),
                "NEO4J_USERNAME": os.getenv("NEO4J_USERNAME"),
                "NEO4J_PASSWORD": os.getenv("NEO4J_PASSWORD"),
            }
            missing = [key for key, value in required_env.items() if not value]
            if missing:
                raise ValueError(
                    f"{', '.join(missing)} are required unless --dry-run or --skip-neo4j is used."
                )
            db_counts["neo4j"] = write_neo4j_graph(
                required_env["NEO4J_URI"] or "",
                required_env["NEO4J_USERNAME"] or "",
                required_env["NEO4J_PASSWORD"] or "",
                os.getenv("NEO4J_DATABASE"),
                payload,
                args.batch_size,
            )

    if args.summary_output:
        write_summary(args.summary_output, payload, args.dry_run, db_counts)

    summary = dict(payload["summary"])
    summary.update(
        {
            "chunk_files": [str(path) for path in chunk_files],
            "db_write_counts": db_counts,
            "dry_run": args.dry_run,
            "entity_files": [str(path) for path in entity_files],
            "summary_output": str(args.summary_output) if args.summary_output else None,
        }
    )
    return summary


def cli(argv: list[str] | None = None) -> int:
    try:
        summary = run(argv)
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(cli())
