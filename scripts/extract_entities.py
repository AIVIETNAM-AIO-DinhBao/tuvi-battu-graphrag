"""Strategy-aware Tử Vi entity extraction for W3-INGEST-04.

The script reads chunk JSONL emitted by scripts/chunk_text.py and writes
entity JSONL with chunk strategy provenance. Production extraction uses Gemini
when available; tests and local smoke checks can use --mock-llm for a fully
deterministic offline path.
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
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable, Mapping

import yaml
from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_PATH = ROOT_DIR / "configs" / "entity_extraction.yaml"
DEFAULT_REVIEW_SAMPLE_SIZE = 20
DEFAULT_REQUESTS_PER_MINUTE = 30.0
DEFAULT_MAX_RETRY_SLEEP_SECONDS = 300.0
REQUIRED_CHUNK_KEYS = {
    "chunk_hash",
    "chunk_id",
    "chunk_strategy_id",
    "domain",
    "source_id",
    "source_page",
}
REVIEW_NOISE_TYPES = {"CucBanMenh", "KhaiNiem", "LuanGiai", "ToHop"}

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def normalize_text(value: Any) -> str:
    return unicodedata.normalize("NFC", str(value or ""))


def normalize_lookup(value: Any) -> str:
    normalized = normalize_text(value).strip().casefold()
    return re.sub(r"\s+", " ", normalized)


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


def load_entity_config(path: Path = DEFAULT_CONFIG_PATH) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Entity extraction config does not exist: {path}")
    with path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle) or {}

    required = {"default_model", "entities", "entity_dict_version", "entity_types", "prompt_version"}
    missing = sorted(required - set(config))
    if missing:
        raise ValueError(f"Entity extraction config is missing required keys: {', '.join(missing)}")
    if not isinstance(config["entity_types"], list) or not config["entity_types"]:
        raise ValueError("Entity extraction config must define a non-empty entity_types list.")
    if not isinstance(config["entities"], dict):
        raise ValueError("Entity extraction config must define an entities mapping.")
    return config


def iter_alias_entries(config: dict[str, Any]) -> list[dict[str, str]]:
    entries: dict[tuple[str, str, str], dict[str, str]] = {}
    entity_types = set(config["entity_types"])

    for entity_type, canonical_map in config.get("entities", {}).items():
        if entity_type not in entity_types:
            raise ValueError(f"Config declares aliases for unknown entity type: {entity_type}")
        if not isinstance(canonical_map, dict):
            raise ValueError(f"Alias mapping for {entity_type} must be an object.")

        for canonical_name, aliases in canonical_map.items():
            alias_values = [canonical_name]
            if isinstance(aliases, list):
                alias_values.extend(str(alias) for alias in aliases)
            elif aliases is not None:
                raise ValueError(f"Aliases for {entity_type}/{canonical_name} must be a list.")

            for alias in alias_values:
                normalized_alias = normalize_lookup(alias)
                if not normalized_alias:
                    continue
                key = (entity_type, str(canonical_name), normalized_alias)
                entries[key] = {
                    "alias": str(alias),
                    "canonical_name": str(canonical_name),
                    "entity_type": entity_type,
                    "normalized_alias": normalized_alias,
                }

    return sorted(
        entries.values(),
        key=lambda item: (len(item["normalized_alias"]), len(item["alias"])),
        reverse=True,
    )


def build_alias_lookup(config: dict[str, Any]) -> dict[tuple[str, str], tuple[str, str]]:
    lookup: dict[tuple[str, str], tuple[str, str]] = {}
    for entry in iter_alias_entries(config):
        lookup[(entry["entity_type"], entry["normalized_alias"])] = (
            entry["canonical_name"],
            entry["alias"],
        )
    return lookup


def canonicalize_entity(
    entity_type: str,
    surface_text: str,
    config: dict[str, Any],
) -> tuple[str, list[str]]:
    lookup = build_alias_lookup(config)
    matched = lookup.get((entity_type, normalize_lookup(surface_text)))
    if matched:
        canonical_name, alias = matched
        return canonical_name, [alias]
    return normalize_text(surface_text).strip(), []


def discover_input_files(inputs: Iterable[Path]) -> list[Path]:
    discovered: list[Path] = []
    for path in inputs:
        if not path.exists():
            raise FileNotFoundError(f"Input path does not exist: {path}")
        if path.is_dir():
            chunk_files = sorted(path.rglob("*_chunks.jsonl"))
            discovered.extend(chunk_files or sorted(path.rglob("*.jsonl")))
            continue
        if path.suffix.lower() != ".jsonl":
            raise ValueError(f"Entity extraction input must be JSONL: {path}")
        discovered.append(path)

    unique: dict[Path, None] = {}
    for path in discovered:
        unique[path.resolve()] = None
    return sorted(unique)


def load_chunks(paths: list[Path]) -> list[dict[str, Any]]:
    chunks: list[dict[str, Any]] = []
    for path in paths:
        with path.open("r", encoding="utf-8") as handle:
            for line_no, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    chunk = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"Invalid JSON in {path}:{line_no}: {exc}") from exc
                chunk["_input_path"] = str(path)
                chunk["_input_line"] = line_no
                chunks.append(chunk)
    return chunks


def chunk_text(chunk: dict[str, Any]) -> str:
    text = chunk.get("chunk_text")
    if text is None:
        text = chunk.get("text")
    return normalize_text(text)


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
        raise ValueError(f"Chunk {chunk.get('chunk_id')} does not contain chunk_text/text.")


def compile_alias_pattern(alias: str) -> re.Pattern[str]:
    escaped_parts = [re.escape(part) for part in normalize_text(alias).split()]
    body = r"\s+".join(escaped_parts)
    return re.compile(rf"(?<!\w){body}(?!\w)", flags=re.IGNORECASE | re.UNICODE)


def should_scan_alias(alias: str) -> bool:
    compact = normalize_lookup(alias).replace(" ", "")
    return len(compact) > 1


def overlaps(left: tuple[int, int], right: tuple[int, int]) -> bool:
    return left[0] < right[1] and right[0] < left[1]


def dictionary_candidates(text: str, config: dict[str, Any]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    occupied: list[tuple[str, str, tuple[int, int]]] = []

    for entry in iter_alias_entries(config):
        alias = entry["alias"]
        if not should_scan_alias(alias):
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
            candidates.append(
                {
                    "aliases_matched": [alias],
                    "canonical_name": entry["canonical_name"],
                    "char_end": span[1],
                    "char_start": span[0],
                    "confidence": 0.92,
                    "entity_type": entry["entity_type"],
                    "evidence_text": surface_text,
                    "needs_review": False,
                    "surface_text": surface_text,
                }
            )
            occupied.append((entry["entity_type"], entry["canonical_name"], span))
    return candidates


def sentence_spans(text: str) -> list[tuple[int, int, str]]:
    spans: list[tuple[int, int, str]] = []
    start = 0
    for match in re.finditer(r"[.!?…]\s+", text):
        end = match.end()
        segment = text[start:end].strip()
        if segment:
            leading = len(text[start:end]) - len(text[start:end].lstrip())
            trailing = len(text[start:end].rstrip())
            spans.append((start + leading, start + trailing, segment))
        start = end

    if start < len(text):
        segment = text[start:].strip()
        if segment:
            leading = len(text[start:]) - len(text[start:].lstrip())
            trailing = len(text[start:].rstrip())
            spans.append((start + leading, start + trailing, segment))
    return spans


def has_luan_giai_trigger(sentence: str, config: dict[str, Any]) -> bool:
    lookup = normalize_lookup(sentence)
    triggers = [normalize_lookup(trigger) for trigger in config.get("luan_giai_triggers", [])]
    for trigger in triggers:
        if trigger and trigger != "thì" and trigger in lookup:
            return True
    return bool(re.search(r"\b(?:gặp|nếu|có)\b.{0,80}\bthì\b", lookup, flags=re.UNICODE))


def luan_giai_candidates(text: str, config: dict[str, Any]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for start, end, sentence in sentence_spans(text):
        if not has_luan_giai_trigger(sentence, config):
            continue
        surface_text = sentence if len(sentence) <= 360 else sentence[:357].rstrip() + "..."
        canonical_name = surface_text if len(surface_text) <= 120 else surface_text[:117].rstrip() + "..."
        candidates.append(
            {
                "aliases_matched": [],
                "canonical_name": canonical_name,
                "char_end": start + len(surface_text),
                "char_start": start,
                "confidence": 0.74,
                "entity_type": "LuanGiai",
                "evidence_text": surface_text,
                "needs_review": True,
                "surface_text": surface_text,
            }
        )
    return candidates


class MockLLMAdapter:
    extraction_model = "mock-dictionary"

    def extract(self, chunk: dict[str, Any], config: dict[str, Any]) -> list[dict[str, Any]]:
        text = chunk_text(chunk)
        return dictionary_candidates(text, config) + luan_giai_candidates(text, config)


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


class GeminiLLMAdapter:
    def __init__(
        self,
        api_key: str | None,
        model_name: str,
        *,
        requests_per_minute: float | None = DEFAULT_REQUESTS_PER_MINUTE,
    ) -> None:
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required unless --mock-llm is used.")
        try:
            import google.generativeai as genai  # type: ignore[import-not-found]
        except ImportError as exc:
            raise RuntimeError(
                "google-generativeai is not installed. Install backend dependencies or use --mock-llm."
            ) from exc

        self._api_key = api_key
        self._genai = genai
        self._rate_limiter = RequestRateLimiter(requests_per_minute)
        self.model_name = model_name
        self.extraction_model = model_name

    def extract(self, chunk: dict[str, Any], config: dict[str, Any]) -> list[dict[str, Any]]:
        self._rate_limiter.wait()
        self._genai.configure(api_key=self._api_key)
        model = self._genai.GenerativeModel(self.model_name)
        response = model.generate_content(build_extraction_prompt(chunk, config))
        payload = parse_json_payload(getattr(response, "text", ""))
        entities = payload.get("entities", payload if isinstance(payload, list) else [])
        if not isinstance(entities, list):
            raise ValueError("Gemini response must contain an entities list.")
        return [entity for entity in entities if isinstance(entity, dict)]


class MultiKeyGeminiLLMAdapter:
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
            raise ValueError("GEMINI_API_KEYS or GEMINI_API_KEY is required unless --mock-llm is used.")
        self.clients = clients
        self.extraction_model = str(getattr(clients[0], "extraction_model", "gemini"))
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

    def extract(self, chunk: dict[str, Any], config: dict[str, Any]) -> list[dict[str, Any]]:
        while True:
            index = self._next_available_index()
            client = self.clients[index]
            label = self._key_label(index)
            try:
                entities = client.extract(chunk, config)
                self._rate_limit_attempts[index] = 0
                self.api_key_usage_counts[label] += 1
                return entities
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


def build_extraction_prompt(chunk: dict[str, Any], config: dict[str, Any]) -> str:
    taxonomy = ", ".join(config["entity_types"])
    return (
        "Bạn là extractor entity cho corpus Tử Vi. "
        "Chỉ trích entity xuất hiện nguyên văn trong chunk_text, không suy diễn.\n"
        f"Taxonomy: {taxonomy}\n"
        "LuanGiai chỉ được tạo khi có claim diễn giải có evidence như 'X chủ về Y', "
        "'X thì Y', 'gặp X thì Y', 'nên luận là Y', 'có nghĩa là Y'.\n"
        "Output JSON strict dạng {\"entities\": [{\"entity_type\": \"...\", "
        "\"surface_text\": \"...\", \"canonical_name\": \"...\", "
        "\"char_start\": 0, \"char_end\": 10, \"evidence_text\": \"...\", "
        "\"confidence\": 0.0, \"needs_review\": false}]}.\n"
        f"chunk_id: {chunk.get('chunk_id')}\n"
        f"chunk_strategy_id: {chunk.get('chunk_strategy_id')}\n"
        f"chunk_text:\n{chunk_text(chunk)}"
    )


def parse_json_payload(text: str) -> Any:
    stripped = text.strip()
    fenced = re.match(r"^```(?:json)?\s*(.*?)\s*```$", stripped, flags=re.S | re.I)
    if fenced:
        stripped = fenced.group(1).strip()
    return json.loads(stripped)


def find_text_span(text: str, needle: str) -> tuple[int, int] | None:
    if not needle:
        return None
    pattern = compile_alias_pattern(needle)
    match = pattern.search(text)
    if match:
        return match.start(), match.end()
    index = normalize_text(text).casefold().find(normalize_text(needle).casefold())
    if index >= 0:
        return index, index + len(needle)
    return None


def resolve_span(candidate: dict[str, Any], text: str) -> tuple[int, int, str] | None:
    surface_text = normalize_text(candidate.get("surface_text") or "")
    evidence_text = normalize_text(candidate.get("evidence_text") or surface_text)
    start = candidate.get("char_start")
    end = candidate.get("char_end")

    if isinstance(start, int) and isinstance(end, int) and 0 <= start < end <= len(text):
        span_text = text[start:end]
        if normalize_lookup(span_text) == normalize_lookup(surface_text) or normalize_lookup(
            span_text
        ) == normalize_lookup(evidence_text):
            return start, end, span_text

    for value in (evidence_text, surface_text):
        span = find_text_span(text, value)
        if span:
            return span[0], span[1], text[span[0] : span[1]]
    return None


def make_entity_id(chunk: dict[str, Any], entity: dict[str, Any]) -> str:
    payload = {
        "canonical_name": entity["canonical_name"],
        "char_end": entity["char_end"],
        "char_start": entity["char_start"],
        "chunk_hash": chunk["chunk_hash"],
        "chunk_strategy_id": chunk["chunk_strategy_id"],
        "entity_type": entity["entity_type"],
    }
    digest = hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()[:12]
    return f"{chunk['chunk_id']}_ENT_{digest}"


def postprocess_entities(
    raw_entities: list[dict[str, Any]],
    chunk: dict[str, Any],
    config: dict[str, Any],
    extraction_model: str,
) -> list[dict[str, Any]]:
    text = chunk_text(chunk)
    entity_types = set(config["entity_types"])
    created_at = utc_now()
    records: list[dict[str, Any]] = []
    seen: set[tuple[str, str, int, int]] = set()

    for raw in raw_entities:
        entity_type = str(raw.get("entity_type") or "").strip()
        if entity_type not in entity_types:
            continue

        span = resolve_span(raw, text)
        if not span:
            continue
        char_start, char_end, evidence_text = span
        surface_text = normalize_text(raw.get("surface_text") or evidence_text).strip()
        canonical_name, aliases_matched = canonicalize_entity(entity_type, surface_text, config)
        if raw.get("canonical_name") and not aliases_matched:
            canonical_name = normalize_text(raw["canonical_name"]).strip()

        if raw.get("aliases_matched") and isinstance(raw["aliases_matched"], list):
            aliases_matched = sorted(
                {normalize_text(alias).strip() for alias in raw["aliases_matched"] if str(alias).strip()}
            )

        dedup_key = (entity_type, canonical_name, char_start, char_end)
        if dedup_key in seen:
            continue
        seen.add(dedup_key)

        needs_review = bool(raw.get("needs_review", False))
        if entity_type == "LuanGiai" or (not aliases_matched and entity_type in REVIEW_NOISE_TYPES):
            needs_review = True

        confidence = raw.get("confidence", 0.0)
        try:
            confidence = float(confidence)
        except (TypeError, ValueError):
            confidence = 0.0

        record = {
            "aliases_matched": aliases_matched,
            "canonical_name": canonical_name,
            "char_end": char_end,
            "char_start": char_start,
            "chunk_hash": chunk["chunk_hash"],
            "chunk_id": chunk["chunk_id"],
            "chunk_strategy_id": chunk["chunk_strategy_id"],
            "confidence": max(0.0, min(1.0, confidence)),
            "created_at": created_at,
            "domain": "TUVI",
            "entity_dict_version": config["entity_dict_version"],
            "entity_id": "",
            "entity_type": entity_type,
            "evidence_text": evidence_text,
            "extraction_model": extraction_model,
            "needs_review": needs_review,
            "prompt_version": config["prompt_version"],
            "section_id": chunk.get("section_id"),
            "source_id": chunk["source_id"],
            "source_name": chunk.get("source_name") or chunk["source_id"],
            "source_page": chunk["source_page"],
            "surface_text": surface_text,
        }
        record["entity_id"] = make_entity_id(chunk, record)
        records.append(record)

    return records


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
            handle.write("\n")


def build_review_report(
    chunks: list[dict[str, Any]],
    entities: list[dict[str, Any]],
    errors: list[dict[str, Any]],
    sample_size: int = DEFAULT_REVIEW_SAMPLE_SIZE,
) -> dict[str, Any]:
    by_chunk: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for entity in entities:
        by_chunk[entity["chunk_id"]].append(entity)

    errors_by_chunk: dict[str, list[str]] = defaultdict(list)
    for error in errors:
        errors_by_chunk[str(error.get("chunk_id") or "<unknown>")].append(str(error.get("error")))

    reviewed = []
    for chunk in chunks[:sample_size]:
        text = chunk_text(chunk)
        chunk_entities = by_chunk.get(chunk["chunk_id"], [])
        warnings: list[str] = []
        if not chunk_entities:
            warnings.append("no_entities_extracted")
        if any(entity["needs_review"] for entity in chunk_entities):
            warnings.append("needs_review_entities")
        if errors_by_chunk.get(chunk["chunk_id"]):
            warnings.append("chunk_errors")

        reviewed.append(
            {
                "chunk_id": chunk["chunk_id"],
                "chunk_strategy_id": chunk["chunk_strategy_id"],
                "entities": [
                    {
                        "canonical_name": entity["canonical_name"],
                        "entity_type": entity["entity_type"],
                        "evidence_text": entity["evidence_text"],
                        "needs_review": entity["needs_review"],
                    }
                    for entity in chunk_entities
                ],
                "excerpt": text[:700],
                "parse_errors": errors_by_chunk.get(chunk["chunk_id"], []),
                "source_id": chunk["source_id"],
                "source_page": chunk["source_page"],
                "warnings": warnings,
            }
        )

    return {
        "entity_count": len(entities),
        "error_count": len(errors),
        "generated_at": utc_now(),
        "reviewed_chunks": reviewed,
        "sample_size": len(reviewed),
    }


def write_review_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def make_llm_adapter(args: argparse.Namespace, config: dict[str, Any]) -> Any:
    if args.mock_llm:
        return MockLLMAdapter()

    model_name = args.model or str(config["default_model"])
    clients = [
        GeminiLLMAdapter(
            api_key,
            model_name,
            requests_per_minute=args.requests_per_minute,
        )
        for api_key in load_gemini_api_keys()
    ]
    return MultiKeyGeminiLLMAdapter(
        clients,
        max_retries=args.max_retries,
        retry_base_seconds=args.retry_base_seconds,
        max_retry_sleep_seconds=args.max_retry_sleep_seconds,
        stop_on_daily_quota=args.stop_on_daily_quota,
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract Tử Vi entities from strategy-aware chunks.")
    parser.add_argument("--input", nargs="+", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--chunking-strategy", default=None)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--review-output", type=Path, default=None)
    parser.add_argument("--mock-llm", action="store_true")
    parser.add_argument("--model", default=None)
    parser.add_argument("--requests-per-minute", type=float, default=DEFAULT_REQUESTS_PER_MINUTE)
    parser.add_argument("--max-retries", type=int, default=6)
    parser.add_argument("--retry-base-seconds", type=float, default=10.0)
    parser.add_argument("--max-retry-sleep-seconds", type=float, default=DEFAULT_MAX_RETRY_SLEEP_SECONDS)
    parser.add_argument("--stop-on-daily-quota", action=argparse.BooleanOptionalAction, default=True)
    return parser.parse_args(argv)


def run(argv: list[str] | None = None) -> dict[str, Any]:
    load_dotenv(ROOT_DIR / ".env")
    args = parse_args(argv)
    config = load_entity_config(args.config)
    input_files = discover_input_files(args.input)
    chunks = load_chunks(input_files)
    if not chunks:
        raise ValueError("No chunks were loaded from the requested input.")

    for chunk in chunks:
        validate_chunk(chunk)

    if args.chunking_strategy:
        chunks = [chunk for chunk in chunks if chunk["chunk_strategy_id"] == args.chunking_strategy]
    if not chunks:
        raise ValueError("No chunks matched the requested chunking strategy.")

    adapter = make_llm_adapter(args, config)

    entities: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    completed = True
    for chunk in chunks:
        try:
            raw_entities = adapter.extract(chunk, config)
            entities.extend(
                postprocess_entities(
                    raw_entities,
                    chunk,
                    config,
                    extraction_model=adapter.extraction_model,
                )
            )
        except GeminiKeysUnavailableError as exc:
            completed = False
            errors.append({"chunk_id": chunk.get("chunk_id"), "error": str(exc)})
            break
        except Exception as exc:  # noqa: BLE001 - batch extraction must continue per chunk.
            errors.append({"chunk_id": chunk.get("chunk_id"), "error": str(exc)})

    write_jsonl(args.output, entities)
    if args.review_output:
        write_review_report(args.review_output, build_review_report(chunks, entities, errors))

    summary = {
        "chunk_count": len(chunks),
        "completed": completed,
        "entity_count": len(entities),
        "error_count": len(errors),
        "extraction_model": adapter.extraction_model,
        "input_files": [str(path) for path in input_files],
        "output": str(args.output),
        "review_output": str(args.review_output) if args.review_output else None,
    }
    if hasattr(adapter, "get_usage_summary"):
        summary.update(adapter.get_usage_summary())
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
