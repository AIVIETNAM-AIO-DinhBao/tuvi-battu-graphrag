"""Strategy-aware Tá»­ Vi entity extraction for W3-INGEST-04.

The script reads chunk JSONL emitted by scripts/chunk_text.py and writes
entity JSONL with chunk strategy provenance. Production extraction uses Gemini
when available; tests and local smoke checks can use --mock-llm for a fully
deterministic offline path.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
import unicodedata
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable, Mapping

import yaml
from dotenv import load_dotenv

from gemini_keys import load_gemini_api_keys as discover_gemini_api_keys
from local_llm import DEFAULT_LOCAL_LLM_MAX_NEW_TOKENS, DEFAULT_LOCAL_LLM_MODEL, LocalQwenJsonClient


ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_PATH = ROOT_DIR / "configs" / "entity_extraction.yaml"
DEFAULT_REVIEW_SAMPLE_SIZE = 20
DEFAULT_REQUESTS_PER_MINUTE = 30.0
DEFAULT_LLM_BATCH_SIZE = 4
DEFAULT_MAX_RETRY_SLEEP_SECONDS = 300.0
STRATEGY_PARENT_CHILD = "chunk_structure_parent_child"
REQUIRED_CHUNK_KEYS = {
    "chunk_hash",
    "chunk_id",
    "chunk_strategy_id",
    "domain",
    "source_id",
    "source_page",
}
REVIEW_NOISE_TYPES = {"CucBanMenh", "KhaiNiem", "LuanGiai", "ToHop"}
VALID_EXTRACTION_SOURCES = {"dictionary", "rule", "llm"}

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


def format_seconds(seconds: float | None) -> str:
    if seconds is None:
        return "unknown"
    seconds = max(0.0, seconds)
    if seconds < 60:
        return f"{seconds:.0f}s"
    minutes, remaining_seconds = divmod(int(seconds), 60)
    if minutes < 60:
        return f"{minutes}m{remaining_seconds:02d}s"
    hours, remaining_minutes = divmod(minutes, 60)
    return f"{hours}h{remaining_minutes:02d}m"


def log_progress(prefix: str, message: str) -> None:
    print(f"[{prefix}] {utc_now()} {message}", file=sys.stderr, flush=True)


def summarize_exception(exc: Exception, *, max_length: int = 700) -> str:
    message = f"{type(exc).__name__}: {exc}".replace("\n", " ").strip()
    if len(message) > max_length:
        return message[: max_length - 3].rstrip() + "..."
    return message


def make_extraction_run_id() -> str:
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    digest = hashlib.sha256(f"{timestamp}:{time.time_ns()}".encode("ascii")).hexdigest()[:8]
    return f"entity_extract_{timestamp}_{digest}"


def load_gemini_api_keys(env: Mapping[str, str | None] | None = None) -> list[str]:
    return discover_gemini_api_keys(env)


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
                    "extraction_source": "dictionary",
                    "needs_review": False,
                    "surface_text": surface_text,
                }
            )
            occupied.append((entry["entity_type"], entry["canonical_name"], span))
    return candidates


def sentence_spans(text: str) -> list[tuple[int, int, str]]:
    spans: list[tuple[int, int, str]] = []
    start = 0
    for match in re.finditer(r"[.!?â€¦]\s+", text):
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
        if trigger and trigger != "thÃ¬" and trigger in lookup:
            return True
    return bool(re.search(r"\b(?:gáº·p|náº¿u|cÃ³)\b.{0,80}\bthÃ¬\b", lookup, flags=re.UNICODE))


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
                "extraction_source": "rule",
                "needs_review": True,
                "surface_text": surface_text,
            }
        )
    return candidates


class MockLLMAdapter:
    extraction_model = "mock-llm-augmentation"

    def extract(self, chunk: dict[str, Any], config: dict[str, Any]) -> list[dict[str, Any]]:
        text = chunk_text(chunk)
        candidates = dictionary_candidates(text, config) + luan_giai_candidates(text, config)
        return [{**candidate, "extraction_source": "llm"} for candidate in candidates]

    def extract_many(
        self,
        chunks: list[dict[str, Any]],
        config: dict[str, Any],
    ) -> dict[str, list[dict[str, Any]]]:
        return {str(chunk["chunk_id"]): self.extract(chunk, config) for chunk in chunks}


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
        return extract_entities_from_payload(payload, source="Gemini")

    def extract_many(
        self,
        chunks: list[dict[str, Any]],
        config: dict[str, Any],
    ) -> dict[str, list[dict[str, Any]]]:
        self._rate_limiter.wait()
        self._genai.configure(api_key=self._api_key)
        model = self._genai.GenerativeModel(self.model_name)
        response = model.generate_content(build_batch_extraction_prompt(chunks, config))
        payload = parse_json_payload(getattr(response, "text", ""))
        return extract_entities_by_chunk_from_payload(
            payload,
            expected_chunk_ids=[str(chunk["chunk_id"]) for chunk in chunks],
            source="Gemini",
        )


def extract_entities_from_payload(payload: Any, *, source: str) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        entities = payload
    elif isinstance(payload, dict):
        entities = payload.get("entities", [])
    else:
        raise ValueError(f"{source} response must be a JSON object or list.")
    if not isinstance(entities, list):
        raise ValueError(f"{source} response must contain an entities list.")
    return [entity for entity in entities if isinstance(entity, dict)]


def extract_entities_by_chunk_from_payload(
    payload: Any,
    *,
    expected_chunk_ids: list[str],
    source: str,
) -> dict[str, list[dict[str, Any]]]:
    if not isinstance(payload, dict):
        raise ValueError(f"{source} batch response must be a JSON object.")
    chunks = payload.get("chunks")
    if not isinstance(chunks, list):
        raise ValueError(f"{source} batch response must contain a chunks list.")

    expected = set(expected_chunk_ids)
    by_chunk: dict[str, list[dict[str, Any]]] = {}
    for item in chunks:
        if not isinstance(item, dict):
            continue
        chunk_id = str(item.get("chunk_id") or "").strip()
        if not chunk_id or chunk_id not in expected:
            continue
        by_chunk[chunk_id] = extract_entities_from_payload(item, source=source)
    return by_chunk


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
        self._last_errors: list[str | None] = [None for _ in clients]
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
            "api_key_last_errors": {
                self._key_label(index): error
                for index, error in enumerate(self._last_errors)
                if error
            },
            "api_key_usage_counts": dict(self.api_key_usage_counts),
            "disabled_key_count": self.disabled_key_count,
            "quota_failover_count": self.quota_failover_count,
        }

    def _key_label(self, index: int) -> str:
        return f"key_{index + 1}"

    def _last_error_summary(self) -> str:
        errors = [
            f"{self._key_label(index)}={error}"
            for index, error in enumerate(self._last_errors)
            if error
        ]
        return "; ".join(errors)

    def _next_available_index(self) -> int:
        if all(self._disabled):
            details = self._last_error_summary()
            suffix = f" Last errors: {details}" if details else ""
            raise GeminiKeysUnavailableError(f"All Gemini API keys are unavailable for this run.{suffix}")

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
                details = self._last_error_summary()
                suffix = f" Last errors: {details}" if details else ""
                raise GeminiKeysUnavailableError(f"All Gemini API keys are unavailable for this run.{suffix}")
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
                self._last_errors[index] = summarize_exception(exc)
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

    def extract_many(
        self,
        chunks: list[dict[str, Any]],
        config: dict[str, Any],
    ) -> dict[str, list[dict[str, Any]]]:
        while True:
            index = self._next_available_index()
            client = self.clients[index]
            label = self._key_label(index)
            try:
                if not hasattr(client, "extract_many"):
                    return {str(chunk["chunk_id"]): client.extract(chunk, config) for chunk in chunks}
                entities_by_chunk = client.extract_many(chunks, config)
                self._rate_limit_attempts[index] = 0
                self.api_key_usage_counts[label] += 1
                return entities_by_chunk
            except Exception as exc:
                self._last_errors[index] = summarize_exception(exc)
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


class LocalQwenEntityLLMAdapter:
    def __init__(self, client: LocalQwenJsonClient) -> None:
        self.client = client
        self.extraction_model = client.model_name
        self.llm_backend = "local"

    def warmup(self) -> None:
        self.client.warmup()

    def get_usage_summary(self) -> dict[str, Any]:
        return self.client.get_usage_summary()

    def extract(self, chunk: dict[str, Any], config: dict[str, Any]) -> list[dict[str, Any]]:
        payload = self.client.generate_json(build_extraction_prompt(chunk, config))
        return extract_entities_from_payload(payload, source="Local Qwen")


def build_extraction_prompt(chunk: dict[str, Any], config: dict[str, Any]) -> str:
    taxonomy = ", ".join(config["entity_types"])
    return (
        "You are the LLM augmentation step for a dictionary-first Tu Vi entity pipeline.\n"
        "Return compact minified JSON only. No markdown. No explanation.\n"
        "If there are no additional candidates, return {\"entities\":[]}.\n"
        "Return at most 20 additional entity candidates that appear verbatim in chunk_text; do not infer.\n"
        f"Taxonomy: {taxonomy}\n"
        "Dictionary and rule candidates have already been extracted before this prompt; "
        "do not use the model as a replacement for those deterministic sources.\n"
        "Create LuanGiai only when the chunk has an explicit interpretation claim with evidence, "
        "for example 'X chu ve Y', 'X thi Y', 'gap X thi Y', 'nen luan la Y', or 'co nghia la Y'.\n"
        "Use exactly this item schema: "
        "{\"entity_type\":\"...\",\"surface_text\":\"...\",\"evidence_text\":\"...\",\"confidence\":0.0}.\n"
        "Do not include char_start, char_end, canonical_name, aliases, or needs_review.\n"
        f"chunk_id: {chunk.get('chunk_id')}\n"
        f"chunk_strategy_id: {chunk.get('chunk_strategy_id')}\n"
        f"chunk_text:\n{chunk_text(chunk)}"
    )


def build_batch_extraction_prompt(chunks: list[dict[str, Any]], config: dict[str, Any]) -> str:
    taxonomy = ", ".join(config["entity_types"])
    chunk_payload = [
        {
            "chunk_id": chunk.get("chunk_id"),
            "chunk_strategy_id": chunk.get("chunk_strategy_id"),
            "chunk_text": chunk_text(chunk),
        }
        for chunk in chunks
    ]
    return (
        "You are the LLM augmentation step for a dictionary-first Tu Vi entity pipeline.\n"
        "Return compact minified JSON only. No markdown. No explanation.\n"
        "Return exactly one result object for every input chunk, preserving chunk_id.\n"
        "If a chunk has no additional candidates, return an empty entities list for that chunk.\n"
        "Return at most 20 additional entity candidates per chunk that appear verbatim in chunk_text; do not infer.\n"
        f"Taxonomy: {taxonomy}\n"
        "Dictionary and rule candidates have already been extracted before this prompt; "
        "do not use the model as a replacement for those deterministic sources.\n"
        "Create LuanGiai only when the chunk has an explicit interpretation claim with evidence, "
        "for example 'X chu ve Y', 'X thi Y', 'gap X thi Y', 'nen luan la Y', or 'co nghia la Y'.\n"
        "Use exactly this output schema: "
        "{\"chunks\":[{\"chunk_id\":\"...\",\"entities\":[{\"entity_type\":\"...\","
        "\"surface_text\":\"...\",\"evidence_text\":\"...\",\"confidence\":0.0}]}]}.\n"
        "Do not include char_start, char_end, canonical_name, aliases, or needs_review.\n"
        f"chunks:\n{json.dumps(chunk_payload, ensure_ascii=False, separators=(',', ':'))}"
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
    extraction_run_id: str = "manual",
    default_extraction_source: str = "llm",
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
        extraction_source = str(raw.get("extraction_source") or default_extraction_source)
        if extraction_source not in VALID_EXTRACTION_SOURCES:
            extraction_source = default_extraction_source

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
            "extraction_run_id": extraction_run_id,
            "extraction_source": extraction_source,
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


def deterministic_candidates(chunk: dict[str, Any], config: dict[str, Any]) -> list[dict[str, Any]]:
    text = chunk_text(chunk)
    return dictionary_candidates(text, config) + luan_giai_candidates(text, config)


def extract_chunk_entities(
    chunk: dict[str, Any],
    config: dict[str, Any],
    *,
    adapter: Any | None,
    llm_augmentation_enabled: bool,
    extraction_run_id: str,
) -> list[dict[str, Any]]:
    raw_entities = deterministic_candidates(chunk, config)
    extraction_model = "dictionary-rule"
    if llm_augmentation_enabled and adapter is not None:
        llm_entities = adapter.extract(chunk, config)
        raw_entities.extend(
            {
                **entity,
                "extraction_source": str(entity.get("extraction_source") or "llm"),
            }
            for entity in llm_entities
            if isinstance(entity, dict)
        )
        extraction_model = f"dictionary-rule+{adapter.extraction_model}"

    return postprocess_entities(
        raw_entities,
        chunk,
        config,
        extraction_model=extraction_model,
        extraction_run_id=extraction_run_id,
        default_extraction_source="dictionary",
    )


def extract_chunk_entities_batch(
    chunks: list[dict[str, Any]],
    config: dict[str, Any],
    *,
    adapter: Any,
    extraction_run_id: str,
) -> dict[str, list[dict[str, Any]]]:
    llm_entities_by_chunk = adapter.extract_many(chunks, config)
    extraction_model = f"dictionary-rule+{adapter.extraction_model}"
    records_by_chunk: dict[str, list[dict[str, Any]]] = {}
    for chunk in chunks:
        chunk_id = str(chunk["chunk_id"])
        if chunk_id not in llm_entities_by_chunk:
            continue
        raw_entities = deterministic_candidates(chunk, config)
        raw_entities.extend(
            {
                **entity,
                "extraction_source": str(entity.get("extraction_source") or "llm"),
            }
            for entity in llm_entities_by_chunk[chunk_id]
            if isinstance(entity, dict)
        )
        records_by_chunk[chunk_id] = postprocess_entities(
            raw_entities,
            chunk,
            config,
            extraction_model=extraction_model,
            extraction_run_id=extraction_run_id,
            default_extraction_source="dictionary",
        )
    return records_by_chunk


def infer_chunk_type(chunk: dict[str, Any]) -> str | None:
    chunk_type = chunk.get("chunk_type")
    if chunk_type:
        return str(chunk_type)
    chunk_id = str(chunk.get("chunk_id") or "")
    if "_child_" in chunk_id:
        return "child"
    if "_parent_" in chunk_id:
        return "parent"
    if "_chunk_" in chunk_id:
        return "chunk"
    return None


def split_processable_chunks(
    chunks: list[dict[str, Any]],
    *,
    include_parent_chunks: bool,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    processable: list[dict[str, Any]] = []
    skipped_parents: list[dict[str, Any]] = []
    for chunk in chunks:
        if (
            chunk.get("chunk_strategy_id") == STRATEGY_PARENT_CHILD
            and infer_chunk_type(chunk) == "parent"
            and not include_parent_chunks
        ):
            skipped_parents.append(chunk)
            continue
        processable.append(chunk)
    return processable, skipped_parents


def load_state(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {"completed_chunks": {}}
    with path.open("r", encoding="utf-8") as handle:
        state = json.load(handle)
    if not isinstance(state.get("completed_chunks"), dict):
        state["completed_chunks"] = {}
    return state


def write_state(path: Path | None, state: dict[str, Any]) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def state_key(chunk: dict[str, Any]) -> str:
    return str(chunk.get("chunk_hash") or chunk.get("chunk_id"))


def completed_state_entry(chunk: dict[str, Any], entity_count: int, extraction_run_id: str) -> dict[str, Any]:
    return {
        "chunk_hash": chunk.get("chunk_hash"),
        "chunk_id": chunk.get("chunk_id"),
        "chunk_strategy_id": chunk.get("chunk_strategy_id"),
        "completed_at": utc_now(),
        "entity_count": entity_count,
        "extraction_run_id": extraction_run_id,
    }


def batched(records: list[dict[str, Any]], batch_size: int) -> Iterable[list[dict[str, Any]]]:
    size = max(1, batch_size)
    for index in range(0, len(records), size):
        yield records[index : index + size]


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
            handle.write("\n")


def read_jsonl_records(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if not path.exists():
        return records
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                records.append(json.loads(line))
    return records


def filter_entities_for_completed_chunks(
    entities: list[dict[str, Any]],
    completed_chunks: dict[str, Any],
) -> list[dict[str, Any]]:
    if not completed_chunks:
        return []
    completed_keys = {str(key) for key in completed_chunks}
    completed_chunk_ids = {
        str(entry.get("chunk_id"))
        for entry in completed_chunks.values()
        if isinstance(entry, dict) and entry.get("chunk_id")
    }
    completed_chunk_hashes = {
        str(entry.get("chunk_hash"))
        for entry in completed_chunks.values()
        if isinstance(entry, dict) and entry.get("chunk_hash")
    }
    return [
        entity
        for entity in entities
        if str(entity.get("chunk_hash")) in completed_keys
        or str(entity.get("chunk_hash")) in completed_chunk_hashes
        or str(entity.get("chunk_id")) in completed_chunk_ids
    ]


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
        "chunk_type_counts": dict(sorted(Counter(infer_chunk_type(chunk) or "unknown" for chunk in chunks).items())),
        "entity_type_counts": dict(sorted(Counter(entity["entity_type"] for entity in entities).items())),
        "entity_count": len(entities),
        "error_count": len(errors),
        "extraction_source_counts": dict(
            sorted(Counter(entity.get("extraction_source", "unknown") for entity in entities).items())
        ),
        "generated_at": utc_now(),
        "reviewed_chunks": reviewed,
        "sample_size": len(reviewed),
        "source_counts": dict(sorted(Counter(chunk["source_id"] for chunk in chunks).items())),
        "strategy_counts": dict(sorted(Counter(chunk["chunk_strategy_id"] for chunk in chunks).items())),
    }


def write_review_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def write_summary_report(path: Path | None, summary: dict[str, Any]) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def resolve_llm_backend(args: argparse.Namespace) -> str:
    if args.mock_llm:
        return "mock"
    return str(args.llm_backend or "gemini")


def make_llm_adapter(args: argparse.Namespace, config: dict[str, Any]) -> Any:
    backend = resolve_llm_backend(args)
    if backend == "mock":
        return MockLLMAdapter()
    if backend == "local":
        return LocalQwenEntityLLMAdapter(
            LocalQwenJsonClient(
                model_name=args.model or args.local_llm_model,
                device=args.local_llm_device,
                quantization=args.local_llm_quantization,
                max_new_tokens=args.local_llm_max_new_tokens,
                temperature=args.local_llm_temperature,
                top_p=args.local_llm_top_p,
                max_json_retries=args.local_llm_max_json_retries,
            )
        )
    if backend != "gemini":
        raise ValueError("--llm-backend must be gemini, local, or mock.")

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
    parser = argparse.ArgumentParser(description="Extract Tá»­ Vi entities from strategy-aware chunks.")
    parser.add_argument("--input", nargs="+", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--chunking-strategy", default=None)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--review-output", type=Path, default=None)
    parser.add_argument("--partial-summary-output", type=Path, default=None)
    parser.add_argument("--state-output", type=Path, default=None)
    parser.add_argument("--extraction-run-id", default=None)
    parser.add_argument("--llm-augmentation", choices=["on", "off"], default=None)
    parser.add_argument("--limit-chunks", type=int, default=None)
    parser.add_argument("--max-runtime-seconds", type=float, default=None)
    parser.add_argument("--include-parent-chunks", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--mock-llm", action="store_true")
    parser.add_argument("--llm-backend", choices=["gemini", "local", "mock"], default=None)
    parser.add_argument("--model", default=None)
    parser.add_argument("--local-llm-model", default=DEFAULT_LOCAL_LLM_MODEL)
    parser.add_argument("--local-llm-device", default=None)
    parser.add_argument("--local-llm-quantization", choices=["4bit", "8bit", "none"], default="4bit")
    parser.add_argument("--local-llm-max-new-tokens", type=int, default=DEFAULT_LOCAL_LLM_MAX_NEW_TOKENS)
    parser.add_argument("--local-llm-temperature", type=float, default=0.0)
    parser.add_argument("--local-llm-top-p", type=float, default=0.9)
    parser.add_argument("--local-llm-max-json-retries", type=int, default=1)
    parser.add_argument("--requests-per-minute", type=float, default=DEFAULT_REQUESTS_PER_MINUTE)
    parser.add_argument("--llm-batch-size", type=int, default=DEFAULT_LLM_BATCH_SIZE)
    parser.add_argument("--max-llm-requests", type=int, default=None)
    parser.add_argument("--progress-interval", type=int, default=50)
    parser.add_argument("--max-retries", type=int, default=6)
    parser.add_argument("--retry-base-seconds", type=float, default=10.0)
    parser.add_argument("--max-retry-sleep-seconds", type=float, default=DEFAULT_MAX_RETRY_SLEEP_SECONDS)
    parser.add_argument("--stop-on-daily-quota", action=argparse.BooleanOptionalAction, default=True)
    return parser.parse_args(argv)


def run(argv: list[str] | None = None) -> dict[str, Any]:
    load_dotenv(ROOT_DIR / ".env")
    args = parse_args(argv)
    config = load_entity_config(args.config)
    extraction_policy = dict(config.get("extraction_policy") or {})
    extraction_run_id = args.extraction_run_id or make_extraction_run_id()
    state_output = args.state_output or Path(str(args.output) + ".state.json")
    run_started_monotonic = time.monotonic()
    llm_default = bool(extraction_policy.get("llm_augmentation_default", True))
    llm_augmentation_enabled = llm_default if args.llm_augmentation is None else args.llm_augmentation == "on"
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

    processable_chunks, parent_skipped_chunks = split_processable_chunks(
        chunks,
        include_parent_chunks=args.include_parent_chunks,
    )
    if args.limit_chunks is not None:
        if args.limit_chunks < 1:
            raise ValueError("--limit-chunks must be a positive integer.")
        processable_chunks = processable_chunks[: args.limit_chunks]
    if args.llm_batch_size < 1:
        raise ValueError("--llm-batch-size must be a positive integer.")
    if args.max_llm_requests is not None and args.max_llm_requests < 1:
        raise ValueError("--max-llm-requests must be a positive integer.")
    if args.progress_interval < 0:
        raise ValueError("--progress-interval must be zero or a positive integer.")
    state = load_state(state_output)
    completed_chunks = state.setdefault("completed_chunks", {})
    resume_skipped_chunks = [
        chunk for chunk in processable_chunks if args.resume and state_key(chunk) in completed_chunks
    ]
    chunks_to_process = [
        chunk for chunk in processable_chunks if not (args.resume and state_key(chunk) in completed_chunks)
    ]

    adapter = make_llm_adapter(args, config) if llm_augmentation_enabled else None
    if chunks_to_process and hasattr(adapter, "warmup"):
        adapter.warmup()

    entities: list[dict[str, Any]] = (
        filter_entities_for_completed_chunks(read_jsonl_records(args.output), completed_chunks)
        if args.resume
        else []
    )
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    completed = True
    stop_reason: str | None = None
    processed_chunk_count = 0
    llm_batch_size = max(1, int(args.llm_batch_size or 1))
    progress_interval = int(args.progress_interval or 0)
    llm_request_count = 0
    use_batch_llm = (
        llm_augmentation_enabled
        and adapter is not None
        and llm_batch_size > 1
        and hasattr(adapter, "extract_many")
    )
    processing_batch_size = llm_batch_size if use_batch_llm else 1

    def maybe_log_progress(*, force: bool = False, last_chunk_id: str | None = None) -> None:
        if progress_interval == 0 and not force:
            return
        if not force and processed_chunk_count % progress_interval != 0:
            return
        elapsed = time.monotonic() - run_started_monotonic
        rate = processed_chunk_count / elapsed if elapsed > 0 and processed_chunk_count > 0 else 0.0
        remaining = max(0, len(chunks_to_process) - processed_chunk_count)
        eta = remaining / rate if rate > 0 else None
        log_progress(
            "entity-progress",
            (
                f"processed={processed_chunk_count}/{len(chunks_to_process)} "
                f"overall={len(resume_skipped_chunks) + processed_chunk_count}/{len(processable_chunks)} "
                f"entities={len(entities)} llm_requests={llm_request_count} "
                f"errors={len(errors)} warnings={len(warnings)} "
                f"elapsed={format_seconds(elapsed)} eta={format_seconds(eta)} "
                f"last_chunk={last_chunk_id or '-'}"
            ),
        )

    maybe_log_progress(force=True)

    def runtime_budget_exhausted() -> bool:
        return (
            args.max_runtime_seconds is not None
            and processed_chunk_count > 0
            and time.monotonic() - run_started_monotonic >= args.max_runtime_seconds
        )

    def llm_request_budget_exhausted() -> bool:
        return (
            llm_augmentation_enabled
            and adapter is not None
            and args.max_llm_requests is not None
            and llm_request_count >= args.max_llm_requests
        )

    def store_chunk_entities(chunk: dict[str, Any], chunk_entities: list[dict[str, Any]]) -> None:
        nonlocal processed_chunk_count
        entities.extend(chunk_entities)
        processed_chunk_count += 1
        completed_chunks[state_key(chunk)] = completed_state_entry(
            chunk,
            len(chunk_entities),
            extraction_run_id,
        )
        write_state(state_output, state)
        maybe_log_progress(last_chunk_id=str(chunk.get("chunk_id") or "-"))

    for chunk_batch in batched(chunks_to_process, processing_batch_size):
        if (
            runtime_budget_exhausted()
        ):
            completed = False
            stop_reason = "max_runtime_seconds"
            break
        if llm_request_budget_exhausted():
            completed = False
            stop_reason = "max_llm_requests"
            break

        if use_batch_llm and len(chunk_batch) > 1:
            try:
                llm_request_count += 1
                batch_records = extract_chunk_entities_batch(
                    chunk_batch,
                    config,
                    adapter=adapter,
                    extraction_run_id=extraction_run_id,
                )
            except GeminiKeysUnavailableError as exc:
                completed = False
                errors.append(
                    {
                        "chunk_id": ",".join(str(chunk.get("chunk_id")) for chunk in chunk_batch),
                        "error": str(exc),
                    }
                )
                break
            except ValueError as exc:
                warnings.append(
                    {
                        "chunk_id": ",".join(str(chunk.get("chunk_id")) for chunk in chunk_batch),
                        "warning": f"batch_response_error: {exc}; fallback_to_single_chunk",
                    }
                )
                for chunk in chunk_batch:
                    if runtime_budget_exhausted():
                        completed = False
                        stop_reason = "max_runtime_seconds"
                        break
                    if llm_request_budget_exhausted():
                        completed = False
                        stop_reason = "max_llm_requests"
                        break
                    try:
                        if llm_augmentation_enabled and adapter is not None:
                            llm_request_count += 1
                        store_chunk_entities(
                            chunk,
                            extract_chunk_entities(
                                chunk,
                                config,
                                adapter=adapter,
                                llm_augmentation_enabled=llm_augmentation_enabled,
                                extraction_run_id=extraction_run_id,
                            ),
                        )
                    except GeminiKeysUnavailableError as fallback_exc:
                        completed = False
                        errors.append({"chunk_id": chunk.get("chunk_id"), "error": str(fallback_exc)})
                        break
                    except Exception as fallback_exc:  # noqa: BLE001 - continue per chunk.
                        errors.append({"chunk_id": chunk.get("chunk_id"), "error": str(fallback_exc)})
                if completed is False and stop_reason != "missing_batch_chunk_response":
                    break
                continue
            except Exception as exc:  # noqa: BLE001 - fall back only for parse/shape errors.
                errors.append(
                    {
                        "chunk_id": ",".join(str(chunk.get("chunk_id")) for chunk in chunk_batch),
                        "error": str(exc),
                    }
                )
                continue

            missing_chunk_ids: list[str] = []
            for chunk in chunk_batch:
                chunk_id = str(chunk["chunk_id"])
                if chunk_id not in batch_records:
                    missing_chunk_ids.append(chunk_id)
                    continue
                store_chunk_entities(chunk, batch_records[chunk_id])
            if missing_chunk_ids:
                completed = False
                stop_reason = "missing_batch_chunk_response"
                for chunk_id in missing_chunk_ids:
                    errors.append({"chunk_id": chunk_id, "error": "missing chunk_id in batch LLM response"})
            continue

        for chunk in chunk_batch:
            if runtime_budget_exhausted():
                completed = False
                stop_reason = "max_runtime_seconds"
                break
            if llm_request_budget_exhausted():
                completed = False
                stop_reason = "max_llm_requests"
                break
            try:
                if llm_augmentation_enabled and adapter is not None:
                    llm_request_count += 1
                store_chunk_entities(
                    chunk,
                    extract_chunk_entities(
                        chunk,
                        config,
                        adapter=adapter,
                        llm_augmentation_enabled=llm_augmentation_enabled,
                        extraction_run_id=extraction_run_id,
                    ),
                )
            except GeminiKeysUnavailableError as exc:
                completed = False
                errors.append({"chunk_id": chunk.get("chunk_id"), "error": str(exc)})
                break
            except Exception as exc:  # noqa: BLE001 - batch extraction must continue per chunk.
                errors.append({"chunk_id": chunk.get("chunk_id"), "error": str(exc)})
        if completed is False and stop_reason != "missing_batch_chunk_response":
            break

    write_jsonl(args.output, entities)
    write_state(state_output, state)
    maybe_log_progress(force=True)
    if args.review_output:
        write_review_report(args.review_output, build_review_report(processable_chunks, entities, errors))

    summary = {
        "chunk_count": len(processable_chunks),
        "completed": completed,
        "entity_count": len(entities),
        "error_count": len(errors),
        "error_samples": errors[:10],
        "extraction_model": (
            f"dictionary-rule+{adapter.extraction_model}" if adapter is not None else "dictionary-rule"
        ),
        "extraction_run_id": extraction_run_id,
        "input_files": [str(path) for path in input_files],
        "input_chunk_count": len(chunks),
        "llm_backend": resolve_llm_backend(args) if llm_augmentation_enabled else "off",
        "llm_augmentation_enabled": llm_augmentation_enabled,
        "llm_batch_size": llm_batch_size,
        "llm_request_count": llm_request_count,
        "limit_chunks": args.limit_chunks,
        "max_llm_requests": args.max_llm_requests,
        "max_runtime_seconds": args.max_runtime_seconds,
        "output": str(args.output),
        "parent_skipped_count": len(parent_skipped_chunks),
        "processed_chunk_count": processed_chunk_count,
        "review_output": str(args.review_output) if args.review_output else None,
        "resume": args.resume,
        "resume_skipped_count": len(resume_skipped_chunks),
        "skipped_chunk_count": len(parent_skipped_chunks) + len(resume_skipped_chunks),
        "state_output": str(state_output),
        "stop_reason": stop_reason,
        "elapsed_seconds": round(time.monotonic() - run_started_monotonic, 3),
        "warning_count": len(warnings),
        "warning_samples": warnings[:10],
    }
    if hasattr(adapter, "get_usage_summary"):
        summary.update(adapter.get_usage_summary())
    write_summary_report(args.partial_summary_output, summary)
    return summary


def cli(argv: list[str] | None = None) -> int:
    try:
        summary = run(argv)
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    if summary.get("completed") is False:
        if summary.get("stop_reason") in {"max_runtime_seconds", "max_llm_requests"}:
            print("Info: Entity extraction reached a configured budget; partial output/state were written for resume.", file=sys.stderr)
            return 0
        print("Error: Entity extraction stopped before completion; see partial summary/state for resume.", file=sys.stderr)
        return 2
    if int(summary.get("error_count") or 0) > 0:
        print("Error: Entity extraction completed with per-chunk errors; see error_samples/review/state.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(cli())
