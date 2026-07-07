"""Create Neo4j Chunk embeddings and fulltext metadata for W3-INGEST-06."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable, Mapping

from dotenv import load_dotenv

from gemini_keys import load_gemini_api_keys as discover_gemini_api_keys
from local_embeddings import (
    DEFAULT_LOCAL_EMBEDDING_BATCH_SIZE,
    DEFAULT_LOCAL_EMBEDDING_DIM,
    DEFAULT_LOCAL_EMBEDDING_MODEL,
    LocalBgeM3EmbeddingClient,
    l2_normalize,
)


ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DOMAIN = "TUVI"
DEFAULT_SOURCE_ID = "TVGM"
DEFAULT_STRATEGY = "chunk_structure_parent_child"
STRATEGY_PARENT_CHILD = "chunk_structure_parent_child"
DEFAULT_EMBEDDING_MODEL = "gemini-embedding-2"
DEFAULT_EXPECTED_DIM = 768
DEFAULT_EMBEDDING_SLOT = "gemini"
DEFAULT_LOCAL_VECTOR_INDEX = "chunkVectorBgeM3"
DEFAULT_REQUESTS_PER_MINUTE = 90.0
DEFAULT_MAX_RETRY_SLEEP_SECONDS = 300.0
DEFAULT_VECTOR_INDEX_NAME = "chunkVector"
REQUIRED_INDEXES = {"chunkFulltext"}

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


@dataclass(frozen=True)
class EmbeddingSlotSpec:
    slot: str
    vector_property: str
    vector_index_name: str
    expected_dim: int
    default_model: str
    default_backend: str
    model_property: str
    dim_property: str
    text_hash_property: str
    embedded_at_property: str

    @property
    def metadata_fields(self) -> dict[str, str]:
        return {
            "embedded_at": self.embedded_at_property,
            "embedding_dim": self.dim_property,
            "embedding_model": self.model_property,
            "embedding_text_hash": self.text_hash_property,
        }


EMBEDDING_SLOT_SPECS: dict[str, EmbeddingSlotSpec] = {
    "gemini": EmbeddingSlotSpec(
        slot="gemini",
        vector_property="embedding",
        vector_index_name=DEFAULT_VECTOR_INDEX_NAME,
        expected_dim=DEFAULT_EXPECTED_DIM,
        default_model=DEFAULT_EMBEDDING_MODEL,
        default_backend="gemini",
        model_property="embedding_model",
        dim_property="embedding_dim",
        text_hash_property="embedding_text_hash",
        embedded_at_property="embedded_at",
    ),
    "bge_m3": EmbeddingSlotSpec(
        slot="bge_m3",
        vector_property="embedding_bge_m3",
        vector_index_name=DEFAULT_LOCAL_VECTOR_INDEX,
        expected_dim=DEFAULT_LOCAL_EMBEDDING_DIM,
        default_model=DEFAULT_LOCAL_EMBEDDING_MODEL,
        default_backend="local",
        model_property="embedding_bge_m3_model",
        dim_property="embedding_bge_m3_dim",
        text_hash_property="embedding_bge_m3_text_hash",
        embedded_at_property="embedding_bge_m3_embedded_at",
    ),
}


def utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def embedding_text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalize_keyword(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def normalize_keywords(values: Iterable[Any], limit: int = 40) -> str:
    seen: dict[str, str] = {}
    for value in values:
        keyword = normalize_keyword(value)
        if not keyword:
            continue
        seen.setdefault(keyword.casefold(), keyword)
    return " ".join(sorted(seen.values(), key=lambda item: item.casefold())[:limit])


def make_title(chunk: dict[str, Any]) -> str:
    return normalize_keyword(chunk.get("section_id") or chunk.get("source_name") or chunk.get("source_id") or "")


def make_embedding_text(chunk: dict[str, Any]) -> str:
    return str(chunk.get("text") or chunk.get("chunk_text") or "").strip()


def should_use_child_only_policy(chunk_strategy_id: str, include_parent_chunks: bool) -> bool:
    return chunk_strategy_id == STRATEGY_PARENT_CHILD and not include_parent_chunks


def chunk_retrieval_unit(chunk: dict[str, Any]) -> bool:
    if "retrieval_unit" in chunk:
        return bool(chunk.get("retrieval_unit"))
    return str(chunk.get("chunk_type") or "").casefold() != "parent"


def validate_embedding_dimension(vector: list[float], expected_dim: int) -> None:
    if len(vector) != expected_dim:
        raise ValueError(f"Embedding dimension mismatch: expected {expected_dim}, got {len(vector)}.")


def safe_index_name(value: str) -> str:
    if not value or not re.match(r"^[A-Za-z][A-Za-z0-9_]*$", value):
        raise ValueError(f"Unsafe Neo4j index name: {value!r}")
    return value


def safe_property_name(value: str) -> str:
    if not value or not re.match(r"^[A-Za-z][A-Za-z0-9_]*$", value):
        raise ValueError(f"Unsafe Neo4j property name: {value!r}")
    return value


def get_embedding_slot_spec(slot: str | None) -> EmbeddingSlotSpec:
    key = str(slot or DEFAULT_EMBEDDING_SLOT).strip()
    try:
        return EMBEDDING_SLOT_SPECS[key]
    except KeyError as exc:
        supported = ", ".join(sorted(EMBEDDING_SLOT_SPECS))
        raise ValueError(f"Unsupported embedding slot {key!r}. Expected one of: {supported}.") from exc


def embedding_slot_config(slot: str | None) -> dict[str, Any]:
    spec = get_embedding_slot_spec(slot)
    return {
        "default_backend": spec.default_backend,
        "default_model": spec.default_model,
        "expected_dim": spec.expected_dim,
        "metadata_fields": spec.metadata_fields,
        "slot": spec.slot,
        "vector_index_name": spec.vector_index_name,
        "vector_property": spec.vector_property,
    }


def infer_embedding_slot(args: argparse.Namespace) -> str:
    if getattr(args, "embedding_slot", None):
        return str(args.embedding_slot)
    if (
        getattr(args, "embedding_backend", None) == "local"
        or getattr(args, "model", None) == DEFAULT_LOCAL_EMBEDDING_MODEL
        or getattr(args, "expected_dim", None) == DEFAULT_LOCAL_EMBEDDING_DIM
        or getattr(args, "vector_index_name", None) == DEFAULT_LOCAL_VECTOR_INDEX
    ):
        return "bge_m3"
    return DEFAULT_EMBEDDING_SLOT


def resolve_embedding_slot_args(args: argparse.Namespace) -> argparse.Namespace:
    spec = get_embedding_slot_spec(infer_embedding_slot(args))
    args.embedding_slot = spec.slot

    vector_index_name = getattr(args, "vector_index_name", None)
    if vector_index_name is None:
        args.vector_index_name = spec.vector_index_name
    elif vector_index_name != spec.vector_index_name:
        raise ValueError(
            f"--vector-index-name {vector_index_name!r} conflicts with --embedding-slot {spec.slot!r}; "
            f"expected {spec.vector_index_name!r}."
        )

    expected_dim = getattr(args, "expected_dim", None)
    if expected_dim is None:
        args.expected_dim = spec.expected_dim
    elif int(expected_dim) != spec.expected_dim:
        raise ValueError(
            f"--expected-dim {expected_dim!r} conflicts with --embedding-slot {spec.slot!r}; "
            f"expected {spec.expected_dim}."
        )

    if getattr(args, "mock_embedding", False):
        if getattr(args, "model", None) is None:
            args.model = spec.default_model
        return args

    embedding_backend = getattr(args, "embedding_backend", None)
    if embedding_backend is not None and embedding_backend != spec.default_backend:
        raise ValueError(
            f"--embedding-backend {embedding_backend!r} conflicts with --embedding-slot {spec.slot!r}; "
            f"expected {spec.default_backend!r}."
        )

    if getattr(args, "model", None) is None:
        args.model = spec.default_model
    elif args.model != spec.default_model:
        raise ValueError(
            f"--model {args.model!r} conflicts with --embedding-slot {spec.slot!r}; "
            f"expected {spec.default_model!r}."
        )

    if spec.slot == "bge_m3":
        local_model = getattr(args, "local_embedding_model", None)
        if local_model is None:
            args.local_embedding_model = spec.default_model
        elif local_model != spec.default_model:
            raise ValueError(
                f"--local-embedding-model {local_model!r} conflicts with --embedding-slot {spec.slot!r}; "
                f"expected {spec.default_model!r}."
            )

    return args


def required_indexes(vector_index_name: str) -> set[str]:
    return REQUIRED_INDEXES | {safe_index_name(vector_index_name)}


def load_gemini_api_keys(env: Mapping[str, str | None] | None = None) -> list[str]:
    return discover_gemini_api_keys(env)


def mock_embedding(text: str, expected_dim: int = DEFAULT_EXPECTED_DIM) -> list[float]:
    """Deterministic 768-dim vector for tests and dry-runs."""
    values: list[float] = []
    seed = text.encode("utf-8")
    counter = 0
    while len(values) < expected_dim:
        digest = hashlib.sha256(seed + str(counter).encode("ascii")).digest()
        for byte in digest:
            values.append(round((byte / 255.0) * 2.0 - 1.0, 6))
            if len(values) == expected_dim:
                break
        counter += 1
    return values


class MockEmbeddingClient:
    def __init__(self, expected_dim: int = DEFAULT_EXPECTED_DIM) -> None:
        self.model_name = f"mock-embedding-{expected_dim}"
        self.embedding_backend = "mock"
        self.expected_dim = expected_dim

    def embed_document(self, text: str, title: str | None = None) -> list[float]:
        return mock_embedding(f"title:{title or 'none'}|text:{text}", self.expected_dim)

    def embed_query(self, text: str) -> list[float]:
        return mock_embedding(f"query:{text}", self.expected_dim)


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
        )
    )


class GeminiEmbeddingClient:
    def __init__(
        self,
        api_key: str | None,
        model_name: str,
        output_dimensionality: int,
        *,
        requests_per_minute: float | None = DEFAULT_REQUESTS_PER_MINUTE,
        max_retries: int = 6,
        retry_base_seconds: float = 10.0,
        max_retry_sleep_seconds: float = DEFAULT_MAX_RETRY_SLEEP_SECONDS,
        stop_on_daily_quota: bool = True,
    ) -> None:
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required unless --mock-embedding is used.")
        try:
            from google import genai  # type: ignore[import-not-found]
            from google.genai import types  # type: ignore[import-not-found]
        except ImportError as exc:
            raise RuntimeError("google-genai is not installed. Install it with: pip install google-genai") from exc
        self._client = genai.Client(api_key=api_key)
        self._types = types
        self.model_name = model_name
        self.embedding_backend = "gemini"
        self.output_dimensionality = output_dimensionality
        self.requests_per_minute = requests_per_minute
        self.max_retries = max(0, max_retries)
        self.retry_base_seconds = max(0.0, retry_base_seconds)
        self.max_retry_sleep_seconds = max(0.0, max_retry_sleep_seconds)
        self.stop_on_daily_quota = stop_on_daily_quota
        self._rate_limiter = RequestRateLimiter(requests_per_minute)

    def _embed(self, text: str) -> list[float]:
        for attempt in range(self.max_retries + 1):
            self._rate_limiter.wait()
            try:
                response = self._client.models.embed_content(
                    model=self.model_name,
                    contents=text,
                    config=self._types.EmbedContentConfig(output_dimensionality=self.output_dimensionality),
                )
                embeddings = getattr(response, "embeddings", None)
                if not embeddings:
                    raise ValueError("Embedding response does not contain embeddings.")
                values = getattr(embeddings[0], "values", None)
                if not isinstance(values, list):
                    raise ValueError("Embedding response does not contain embedding values.")
                return [float(value) for value in values]
            except Exception as exc:
                if self.stop_on_daily_quota and is_daily_quota_error(exc):
                    raise RuntimeError(
                        "Gemini embedding daily quota appears exhausted. "
                        "Re-run this script after the quota resets; already-written chunks will be skipped."
                    ) from exc
                if not is_rate_limit_error(exc) or attempt >= self.max_retries:
                    raise
                sleep_for = min(
                    self.max_retry_sleep_seconds,
                    max(
                        self._rate_limiter.min_interval_seconds,
                        self.retry_base_seconds * (2**attempt),
                    ),
                )
                quota_kind = "daily quota" if is_daily_quota_error(exc) else "rate limit"
                print(
                    f"{quota_kind.capitalize()} from Gemini embedding API; sleeping {sleep_for:.1f}s "
                    f"before retry {attempt + 1}/{self.max_retries}.",
                    file=sys.stderr,
                    flush=True,
                )
                if sleep_for <= 0:
                    continue
                time.sleep(sleep_for)
        raise RuntimeError("Embedding retry loop exited unexpectedly.")

    def embed_document(self, text: str, title: str | None = None) -> list[float]:
        document = f"title: {title or 'none'} | text: {text}"
        return self._embed(document)

    def embed_query(self, text: str) -> list[float]:
        return self._embed(f"task: search result | query: {text}")


class MultiKeyGeminiEmbeddingClient:
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
            raise ValueError("GEMINI_API_KEYS or GEMINI_API_KEY is required unless --mock-embedding is used.")
        self.clients = clients
        self.model_name = str(getattr(clients[0], "model_name", DEFAULT_EMBEDDING_MODEL))
        self.embedding_backend = "gemini"
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
            raise RuntimeError("All Gemini API keys are unavailable for this run.")

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
                raise RuntimeError("All Gemini API keys are unavailable for this run.")
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

    def _embed(self, method_name: str, *args: Any, **kwargs: Any) -> list[float]:
        while True:
            index = self._next_available_index()
            client = self.clients[index]
            label = self._key_label(index)
            try:
                vector = getattr(client, method_name)(*args, **kwargs)
                self._rate_limit_attempts[index] = 0
                self.api_key_usage_counts[label] += 1
                return vector
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

    def embed_document(self, text: str, title: str | None = None) -> list[float]:
        return self._embed("embed_document", text, title=title)

    def embed_query(self, text: str) -> list[float]:
        return self._embed("embed_query", text)


def build_select_chunks_cypher(
    *,
    force: bool,
    limit: int | None,
    child_only: bool = False,
    embedding_slot: str = DEFAULT_EMBEDDING_SLOT,
) -> str:
    spec = get_embedding_slot_spec(embedding_slot)
    embedding_property = safe_property_name(spec.vector_property)
    embedding_filter = "" if force else f"AND c.{embedding_property} IS NULL"
    child_filter = "AND (c.chunk_type = 'child' OR c.retrieval_unit = true)" if child_only else ""
    limit_clause = "\nLIMIT $limit" if limit is not None else ""
    return f"""
        MATCH (c:Chunk)
        WHERE c.domain = $domain
          AND c.source_id = $source_id
          AND c.chunk_strategy_id = $chunk_strategy_id
          {embedding_filter}
          {child_filter}
        OPTIONAL MATCH (c)-[:MENTIONS]->(e:Entity)
        WITH c, collect(DISTINCT e.canonical_name) AS keywords
        ORDER BY c.chunk_id
        RETURN
          c.chunk_hash AS chunk_hash,
          c.chunk_id AS chunk_id,
          c.chunk_strategy_id AS chunk_strategy_id,
          c.chunk_type AS chunk_type,
          c.domain AS domain,
          c.parent_id AS parent_id,
          c.retrieval_unit AS retrieval_unit,
          c.source_id AS source_id,
          c.source_name AS source_name,
          c.source_page AS source_page,
          c.section_id AS section_id,
          c.text AS text,
          c.chunk_text AS chunk_text,
          keywords AS mention_keywords
        {limit_clause}
    """


def normalize_chunk_record(record: Any) -> dict[str, Any]:
    data = dict(record)
    data["mention_keywords"] = list(data.get("mention_keywords") or [])
    return data


def select_chunks_tx(
    tx: Any,
    *,
    domain: str,
    source_id: str,
    chunk_strategy_id: str,
    force: bool,
    limit: int | None,
    include_parent_chunks: bool = False,
    embedding_slot: str = DEFAULT_EMBEDDING_SLOT,
) -> list[dict[str, Any]]:
    child_only = should_use_child_only_policy(chunk_strategy_id, include_parent_chunks)
    result = tx.run(
        build_select_chunks_cypher(
            force=force,
            limit=limit,
            child_only=child_only,
            embedding_slot=embedding_slot,
        ),
        domain=domain,
        source_id=source_id,
        chunk_strategy_id=chunk_strategy_id,
        limit=limit,
    )
    return [normalize_chunk_record(record) for record in result]


def build_parent_skipped_count_cypher(
    *,
    force: bool,
    embedding_slot: str = DEFAULT_EMBEDDING_SLOT,
) -> str:
    spec = get_embedding_slot_spec(embedding_slot)
    embedding_property = safe_property_name(spec.vector_property)
    embedding_filter = "" if force else f"AND c.{embedding_property} IS NULL"
    return f"""
        MATCH (c:Chunk)
        WHERE c.domain = $domain
          AND c.source_id = $source_id
          AND c.chunk_strategy_id = $chunk_strategy_id
          AND c.chunk_type = 'parent'
          {embedding_filter}
        RETURN count(c) AS parent_skipped_count
    """


def count_parent_skipped_tx(
    tx: Any,
    *,
    domain: str,
    source_id: str,
    chunk_strategy_id: str,
    force: bool,
    embedding_slot: str = DEFAULT_EMBEDDING_SLOT,
) -> int:
    result = tx.run(
        build_parent_skipped_count_cypher(force=force, embedding_slot=embedding_slot),
        domain=domain,
        source_id=source_id,
        chunk_strategy_id=chunk_strategy_id,
    )
    record = result.single() if hasattr(result, "single") else None
    if record is None:
        return 0
    return int(record["parent_skipped_count"])


def verify_indexes_tx(tx: Any, index_names: Iterable[str] | None = None) -> list[dict[str, Any]]:
    names = sorted(index_names or REQUIRED_INDEXES)
    result = tx.run(
        """
        SHOW INDEXES
        YIELD name, state, type, entityType, labelsOrTypes, properties, options
        WHERE name IN $index_names
        RETURN name, state, type, entityType, labelsOrTypes, properties, options
        ORDER BY name
        """,
        index_names=names,
    )
    return [dict(record) for record in result]


def vector_index_dimensions(record: Mapping[str, Any]) -> int | None:
    options = record.get("options")
    if not isinstance(options, Mapping):
        return None
    index_config = options.get("indexConfig")
    if not isinstance(index_config, Mapping):
        index_config = options
    for key in ("vector.dimensions", "`vector.dimensions`"):
        value = index_config.get(key)
        if value is not None:
            return int(value)
    return None


def assert_slot_vector_index_compatible(
    indexes: list[dict[str, Any]],
    slot: str | EmbeddingSlotSpec,
    vector_index_name: str | None = None,
) -> None:
    spec = slot if isinstance(slot, EmbeddingSlotSpec) else get_embedding_slot_spec(slot)
    index_name = vector_index_name or spec.vector_index_name
    by_name = {str(record.get("name")): record for record in indexes}
    record = by_name.get(index_name)
    if record is None:
        raise ValueError(f"Missing Neo4j vector index: {index_name}")

    properties = [str(value) for value in (record.get("properties") or [])]
    if properties != [spec.vector_property]:
        raise ValueError(
            f"Neo4j vector index {index_name} targets {properties!r}, expected [{spec.vector_property!r}]."
        )

    dimensions = vector_index_dimensions(record)
    if dimensions != spec.expected_dim:
        raise ValueError(
            f"Neo4j vector index {index_name} has dimension {dimensions!r}, expected {spec.expected_dim}."
        )


def assert_required_indexes_online(
    indexes: list[dict[str, Any]],
    index_names: Iterable[str] | None = None,
    *,
    embedding_slot: str | EmbeddingSlotSpec | None = None,
    vector_index_name: str | None = None,
) -> None:
    expected = set(index_names or REQUIRED_INDEXES)
    by_name = {record.get("name"): record for record in indexes}
    missing = sorted(expected - set(by_name))
    if missing:
        raise ValueError(f"Missing Neo4j index(es): {', '.join(missing)}")
    offline = sorted(name for name, record in by_name.items() if record.get("state") != "ONLINE")
    if offline:
        raise ValueError(f"Neo4j index(es) not ONLINE: {', '.join(offline)}")
    if embedding_slot is not None:
        assert_slot_vector_index_compatible(indexes, embedding_slot, vector_index_name)


def prepare_embedding_updates(
    chunks: list[dict[str, Any]],
    client: Any,
    *,
    expected_dim: int,
    embedding_slot: str = DEFAULT_EMBEDDING_SLOT,
) -> list[dict[str, Any]]:
    updates: list[dict[str, Any]] = []
    embedded_at = utc_now()
    for chunk in chunks:
        update = prepare_embedding_update(
            chunk,
            client,
            expected_dim=expected_dim,
            embedded_at=embedded_at,
            embedding_slot=embedding_slot,
        )
        if update:
            updates.append(update)
    return updates


def prepare_embedding_update(
    chunk: dict[str, Any],
    client: Any,
    *,
    expected_dim: int,
    embedded_at: str | None = None,
    embedding_slot: str = DEFAULT_EMBEDDING_SLOT,
) -> dict[str, Any] | None:
    text = make_embedding_text(chunk)
    if not text:
        return None
    title = make_title(chunk)
    embedding = client.embed_document(text, title=title)
    return build_embedding_update(
        chunk,
        embedding,
        client,
        expected_dim=expected_dim,
        embedded_at=embedded_at,
        embedding_slot=embedding_slot,
        text=text,
        title=title,
    )


def build_embedding_update(
    chunk: dict[str, Any],
    embedding: list[float],
    client: Any,
    *,
    expected_dim: int,
    embedded_at: str | None = None,
    embedding_slot: str = DEFAULT_EMBEDDING_SLOT,
    text: str | None = None,
    title: str | None = None,
) -> dict[str, Any]:
    text = make_embedding_text(chunk) if text is None else text
    title = make_title(chunk) if title is None else title
    spec = get_embedding_slot_spec(embedding_slot)
    validate_embedding_dimension(embedding, expected_dim)
    return {
        "chunk_hash": chunk["chunk_hash"],
        "chunk_id": chunk["chunk_id"],
        "chunk_type": chunk.get("chunk_type"),
        "embedding": embedding,
        "embedding_dim": expected_dim,
        "embedding_model": client.model_name,
        "embedding_slot": spec.slot,
        "embedding_text_hash": embedding_text_hash(text),
        "embedded_at": embedded_at or utc_now(),
        "keywords": normalize_keywords(chunk.get("mention_keywords") or []),
        "parent_id": chunk.get("parent_id"),
        "retrieval_unit": chunk_retrieval_unit(chunk),
        "title": title,
        "vector_index_name": spec.vector_index_name,
        "vector_property": spec.vector_property,
    }


def make_local_embedding_document(text: str, title: str | None = None) -> str:
    return f"title: {title} | text: {text}" if title else text


def supports_local_document_batch(client: Any) -> bool:
    return getattr(client, "embedding_backend", None) == "local" and callable(
        getattr(client, "embed_documents", None)
    )


def prepare_embedding_update_batch(
    chunks: list[dict[str, Any]],
    client: Any,
    *,
    expected_dim: int,
    embedded_at: str | None = None,
    embedding_slot: str = DEFAULT_EMBEDDING_SLOT,
) -> list[dict[str, Any]]:
    candidates = [
        (chunk, text, make_title(chunk))
        for chunk in chunks
        if (text := make_embedding_text(chunk))
    ]
    if not candidates:
        return []
    if not supports_local_document_batch(client):
        return [
            update
            for chunk, _, _ in candidates
            if (
                update := prepare_embedding_update(
                    chunk,
                    client,
                    expected_dim=expected_dim,
                    embedded_at=embedded_at,
                    embedding_slot=embedding_slot,
                )
            )
        ]

    documents = [make_local_embedding_document(text, title) for _, text, title in candidates]
    embeddings = client.embed_documents(documents)
    if len(embeddings) != len(candidates):
        raise ValueError(f"Embedding batch returned {len(embeddings)} vectors for {len(candidates)} documents.")
    return [
        build_embedding_update(
            chunk,
            embedding,
            client,
            expected_dim=expected_dim,
            embedded_at=embedded_at,
            embedding_slot=embedding_slot,
            text=text,
            title=title,
        )
        for (chunk, text, title), embedding in zip(candidates, embeddings, strict=True)
    ]


def build_write_embedding_updates_cypher(embedding_slot: str = DEFAULT_EMBEDDING_SLOT) -> str:
    spec = get_embedding_slot_spec(embedding_slot)
    vector_property = safe_property_name(spec.vector_property)
    model_property = safe_property_name(spec.model_property)
    dim_property = safe_property_name(spec.dim_property)
    text_hash_property = safe_property_name(spec.text_hash_property)
    embedded_at_property = safe_property_name(spec.embedded_at_property)
    return f"""
        UNWIND $updates AS row
        MATCH (c:Chunk {{chunk_hash: row.chunk_hash}})
        SET c.{vector_property} = row.embedding,
            c.{model_property} = row.embedding_model,
            c.{dim_property} = row.embedding_dim,
            c.{embedded_at_property} = row.embedded_at,
            c.{text_hash_property} = row.embedding_text_hash,
            c.chunk_type = row.chunk_type,
            c.parent_id = row.parent_id,
            c.retrieval_unit = row.retrieval_unit,
            c.title = row.title,
            c.keywords = row.keywords
    """


def write_embedding_updates_tx(
    tx: Any,
    updates: list[dict[str, Any]],
    batch_size: int,
    embedding_slot: str = DEFAULT_EMBEDDING_SLOT,
) -> int:
    cypher = build_write_embedding_updates_cypher(embedding_slot)
    for batch in batched(updates, batch_size):
        tx.run(cypher, updates=batch)
    return len(updates)


def batched(records: list[dict[str, Any]], batch_size: int) -> Iterable[list[dict[str, Any]]]:
    size = max(1, batch_size)
    for index in range(0, len(records), size):
        yield records[index : index + size]


def write_summary(path: Path, summary: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def chunk_type_counts(records: Iterable[dict[str, Any]]) -> dict[str, int]:
    counts = Counter(str(record.get("chunk_type") or "unknown") for record in records)
    return dict(sorted(counts.items()))


def keyword_coverage(updates: list[dict[str, Any]]) -> dict[str, Any]:
    if not updates:
        return {"chunk_count": 0, "with_keywords": 0, "coverage": 0.0}
    with_keywords = sum(1 for update in updates if str(update.get("keywords") or "").strip())
    return {
        "chunk_count": len(updates),
        "coverage": round(with_keywords / len(updates), 6),
        "with_keywords": with_keywords,
    }


def build_run_summary(
    *,
    args: argparse.Namespace,
    db_counts: dict[str, Any],
    embedding_model: str,
    selected_chunks: int,
    update_count: int,
    completed: bool,
    selected_chunk_records: list[dict[str, Any]] | None = None,
    updates: list[dict[str, Any]] | None = None,
    parent_skipped_count: int = 0,
    retrieval_smoke_output: str | None = None,
    embedding_client: Any | None = None,
    error: BaseException | None = None,
) -> dict[str, Any]:
    selected_chunk_records = selected_chunk_records or []
    updates = updates or []
    slot_spec = get_embedding_slot_spec(getattr(args, "embedding_slot", DEFAULT_EMBEDDING_SLOT))
    summary = {
        "batch_size": args.batch_size,
        "chunk_strategy_id": args.chunking_strategy,
        "completed": completed,
        "db_write_counts": db_counts,
        "domain": args.domain,
        "dry_run": args.dry_run,
        "embedding_metadata_fields": slot_spec.metadata_fields,
        "embedding_model": embedding_model,
        "embedding_backend": getattr(args, "embedding_backend", None)
        or ("mock" if args.mock_embedding else slot_spec.default_backend),
        "embedding_property": slot_spec.vector_property,
        "embedding_slot": slot_spec.slot,
        "expected_dim": args.expected_dim,
        "force": args.force,
        "generated_at": utc_now(),
        "include_parent_chunks": args.include_parent_chunks,
        "keyword_coverage": keyword_coverage(updates),
        "limit": args.limit,
        "parent_skipped_count": parent_skipped_count,
        "requests_per_minute": None if args.mock_embedding else args.requests_per_minute,
        "retrieval_smoke_output": retrieval_smoke_output,
        "selected_chunk_type_counts": chunk_type_counts(selected_chunk_records),
        "embedded_chunk_type_counts": chunk_type_counts(updates),
        "selected_chunks": selected_chunks,
        "smoke_candidate_k": args.smoke_candidate_k,
        "source_id": args.source_id,
        "update_count": update_count,
        "vector_index_name": getattr(args, "vector_index_name", slot_spec.vector_index_name),
    }
    if error is not None:
        summary["error"] = f"{type(error).__name__}: {error}"
    if embedding_client is not None and hasattr(embedding_client, "get_usage_summary"):
        summary.update(embedding_client.get_usage_summary())
    return summary


def build_dense_retrieval_smoke_cypher(
    *,
    child_only: bool,
    limit: int,
    candidate_k: int | None = None,
    vector_index_name: str = "chunkVector",
) -> str:
    child_filter = "AND (node.chunk_type = 'child' OR node.retrieval_unit = true)" if child_only else ""
    index_name = safe_index_name(vector_index_name)
    candidate_k = max(candidate_k or limit, limit)
    return f"""
        CALL db.index.vector.queryNodes('{index_name}', $candidate_k, $query_embedding)
        YIELD node, score
        WHERE node.domain = $domain
          AND node.source_id = $source_id
          AND node.chunk_strategy_id = $chunk_strategy_id
          {child_filter}
        RETURN
          node.chunk_hash AS chunk_hash,
          node.chunk_id AS chunk_id,
          node.chunk_strategy_id AS chunk_strategy_id,
          node.chunk_type AS chunk_type,
          node.domain AS domain,
          node.parent_id AS parent_id,
          node.source_id AS source_id,
          node.source_page AS source_page,
          score AS score
        ORDER BY score DESC
        LIMIT {max(1, limit)}
    """


def build_sparse_retrieval_smoke_cypher(*, child_only: bool, limit: int) -> str:
    child_filter = "AND (node.chunk_type = 'child' OR node.retrieval_unit = true)" if child_only else ""
    return f"""
        CALL db.index.fulltext.queryNodes('chunkFulltext', $query_text)
        YIELD node, score
        WHERE node.domain = $domain
          AND node.source_id = $source_id
          AND node.chunk_strategy_id = $chunk_strategy_id
          {child_filter}
        RETURN
          node.chunk_hash AS chunk_hash,
          node.chunk_id AS chunk_id,
          node.chunk_strategy_id AS chunk_strategy_id,
          node.chunk_type AS chunk_type,
          node.domain AS domain,
          node.parent_id AS parent_id,
          node.source_id AS source_id,
          node.source_page AS source_page,
          score AS score
        ORDER BY score DESC
        LIMIT {max(1, limit)}
    """


def normalize_hit_record(record: Any) -> dict[str, Any]:
    data = dict(record)
    if data.get("score") is not None:
        data["score"] = float(data["score"])
    return data


def dense_retrieval_smoke_tx(
    tx: Any,
    *,
    args: argparse.Namespace,
    query_embedding: list[float],
    child_only: bool,
) -> list[dict[str, Any]]:
    candidate_k = max(args.smoke_candidate_k, args.smoke_limit)
    result = tx.run(
        build_dense_retrieval_smoke_cypher(
            child_only=child_only,
            limit=args.smoke_limit,
            candidate_k=candidate_k,
            vector_index_name=args.vector_index_name,
        ),
        domain=args.domain,
        source_id=args.source_id,
        chunk_strategy_id=args.chunking_strategy,
        query_embedding=query_embedding,
        candidate_k=candidate_k,
        limit=args.smoke_limit,
    )
    return [normalize_hit_record(record) for record in result]


def sparse_retrieval_smoke_tx(
    tx: Any,
    *,
    args: argparse.Namespace,
    child_only: bool,
) -> list[dict[str, Any]]:
    result = tx.run(
        build_sparse_retrieval_smoke_cypher(child_only=child_only, limit=args.smoke_limit),
        domain=args.domain,
        source_id=args.source_id,
        chunk_strategy_id=args.chunking_strategy,
        query_text=args.smoke_query,
    )
    return [normalize_hit_record(record) for record in result]


def fetch_parent_chunks_tx(tx: Any, parent_ids: list[str]) -> list[dict[str, Any]]:
    if not parent_ids:
        return []
    result = tx.run(
        """
        MATCH (p:Chunk)
        WHERE p.chunk_id IN $parent_ids
        RETURN
          p.chunk_hash AS chunk_hash,
          p.chunk_id AS chunk_id,
          p.chunk_strategy_id AS chunk_strategy_id,
          p.chunk_type AS chunk_type,
          p.source_id AS source_id,
          p.source_page AS source_page
        ORDER BY p.chunk_id
        """,
        parent_ids=parent_ids,
    )
    return [normalize_hit_record(record) for record in result]


def build_parent_expansion_diagnostics(
    dense_hits: list[dict[str, Any]],
    sparse_hits: list[dict[str, Any]],
    parent_records: list[dict[str, Any]],
) -> dict[str, Any]:
    hits = [*dense_hits, *sparse_hits]
    parent_ids = sorted({str(hit.get("parent_id")) for hit in hits if hit.get("parent_id")})
    fetched_ids = {str(parent.get("chunk_id")) for parent in parent_records}
    with_parent = len(parent_ids)
    fetched = sum(1 for parent_id in parent_ids if parent_id in fetched_ids)
    return {
        "child_hits_with_parent": with_parent,
        "parent_expansion_hit_rate": round(fetched / with_parent, 6) if with_parent else 0.0,
        "parent_fetch_count": fetched,
        "parent_ids": parent_ids,
    }


def write_retrieval_smoke(
    path: Path,
    *,
    args: argparse.Namespace,
    dense_hits: list[dict[str, Any]],
    sparse_hits: list[dict[str, Any]],
    parent_records: list[dict[str, Any]],
) -> dict[str, Any]:
    slot_spec = get_embedding_slot_spec(getattr(args, "embedding_slot", DEFAULT_EMBEDDING_SLOT))
    diagnostics = {
        "dense_hit_count": len(dense_hits),
        "embedding_property": slot_spec.vector_property,
        "embedding_slot": slot_spec.slot,
        "sparse_hit_count": len(sparse_hits),
        "parent_expansion": build_parent_expansion_diagnostics(dense_hits, sparse_hits, parent_records),
    }
    payload = {
        "chunk_strategy_id": args.chunking_strategy,
        "dense_hits": dense_hits,
        "diagnostics": diagnostics,
        "domain": args.domain,
        "embedding_slot": slot_spec.slot,
        "generated_at": utc_now(),
        "parent_expansion_records": parent_records,
        "query": args.smoke_query,
        "source_id": args.source_id,
        "sparse_hits": sparse_hits,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def discover_chunk_files(inputs: Iterable[Path]) -> list[Path]:
    discovered: list[Path] = []
    for path in inputs:
        if not path.exists():
            raise FileNotFoundError(f"Chunks input does not exist: {path}")
        if path.is_dir():
            discovered.extend(sorted(path.rglob("*_chunks.jsonl")) or sorted(path.rglob("*.jsonl")))
            continue
        if path.suffix.lower() != ".jsonl":
            raise ValueError(f"Chunks input must be JSONL or a directory: {path}")
        discovered.append(path)
    return sorted({path.resolve(): None for path in discovered})


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                records.append(json.loads(line))
    return records


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
            handle.write("\n")


def load_offline_embedding_state(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {"completed_chunks": {}}
    state = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(state.get("completed_chunks"), dict):
        state["completed_chunks"] = {}
    return state


def write_offline_embedding_state(path: Path | None, state: dict[str, Any]) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def offline_state_key(chunk: dict[str, Any]) -> str:
    return str(chunk.get("chunk_hash") or chunk.get("chunk_id"))


def filter_offline_chunks(chunks: list[dict[str, Any]], args: argparse.Namespace) -> list[dict[str, Any]]:
    selected = [
        chunk
        for chunk in chunks
        if str(chunk.get("source_id")) == args.source_id
        and str(chunk.get("domain") or DEFAULT_DOMAIN) == args.domain
        and str(chunk.get("chunk_strategy_id")) == args.chunking_strategy
    ]
    if should_use_child_only_policy(args.chunking_strategy, args.include_parent_chunks):
        selected = [
            chunk
            for chunk in selected
            if str(chunk.get("chunk_type") or "").casefold() == "child" or chunk_retrieval_unit(chunk)
        ]
    if args.limit is not None:
        selected = selected[: args.limit]
    return selected


def dot_product(left: list[float], right: list[float]) -> float:
    if len(left) != len(right):
        return 0.0
    return sum(a * b for a, b in zip(left, right, strict=True))


def lexical_sparse_score(query: str, text: str) -> float:
    query_terms = {term.casefold() for term in re.findall(r"\w+", query, flags=re.UNICODE)}
    text_terms = {term.casefold() for term in re.findall(r"\w+", text, flags=re.UNICODE)}
    if not query_terms or not text_terms:
        return 0.0
    return len(query_terms & text_terms) / len(query_terms)


def build_offline_retrieval_smoke(
    updates: list[dict[str, Any]],
    *,
    args: argparse.Namespace,
    client: Any,
) -> dict[str, Any]:
    query_embedding = l2_normalize(client.embed_query(args.smoke_query))
    slot_spec = get_embedding_slot_spec(getattr(args, "embedding_slot", DEFAULT_EMBEDDING_SLOT))
    dense_hits = sorted(
        (
            {
                "chunk_hash": update["chunk_hash"],
                "chunk_id": update["chunk_id"],
                "chunk_type": update.get("chunk_type"),
                "parent_id": update.get("parent_id"),
                "score": round(dot_product(l2_normalize(update["embedding"]), query_embedding), 6),
            }
            for update in updates
        ),
        key=lambda item: item["score"],
        reverse=True,
    )[: args.smoke_limit]
    sparse_hits = sorted(
        (
            {
                "chunk_hash": update["chunk_hash"],
                "chunk_id": update["chunk_id"],
                "chunk_type": update.get("chunk_type"),
                "parent_id": update.get("parent_id"),
                "score": round(lexical_sparse_score(args.smoke_query, str(update.get("embedding_text") or "")), 6),
            }
            for update in updates
        ),
        key=lambda item: item["score"],
        reverse=True,
    )[: args.smoke_limit]
    return {
        "chunk_strategy_id": args.chunking_strategy,
        "dense_hits": dense_hits,
        "diagnostics": {
            "dense_hit_count": len([hit for hit in dense_hits if hit["score"] > 0]),
            "embedding_property": slot_spec.vector_property,
            "embedding_slot": slot_spec.slot,
            "mode": "offline_artifact",
            "sparse_hit_count": len([hit for hit in sparse_hits if hit["score"] > 0]),
        },
        "domain": args.domain,
        "embedding_model": client.model_name,
        "embedding_slot": slot_spec.slot,
        "generated_at": utc_now(),
        "query": args.smoke_query,
        "source_id": args.source_id,
        "sparse_hits": sparse_hits,
    }


def run_offline_embedding(args: argparse.Namespace) -> dict[str, Any]:
    if not args.output:
        raise ValueError("--output is required when --chunks-input is used.")
    chunk_files = discover_chunk_files(args.chunks_input or [])
    chunks = []
    for path in chunk_files:
        chunks.extend(read_jsonl(path))
    selected_chunks = filter_offline_chunks(chunks, args)
    state = load_offline_embedding_state(args.state_output)
    completed_chunks = state.setdefault("completed_chunks", {})
    existing_updates = (
        [
            update
            for update in read_jsonl(args.output)
            if offline_state_key(update) in completed_chunks
        ]
        if args.resume and args.output.exists()
        else []
    )
    updates = list(existing_updates)
    client = make_embedding_client(args)
    completed = True
    error: Exception | None = None
    processed = 0
    pending_chunks = [
        chunk
        for chunk in selected_chunks
        if not (args.resume and offline_state_key(chunk) in completed_chunks)
    ]
    try:
        slot_spec = get_embedding_slot_spec(args.embedding_slot)
        for chunk_batch in batched(pending_chunks, args.batch_size):
            batch_updates = prepare_embedding_update_batch(
                chunk_batch,
                client,
                expected_dim=args.expected_dim,
                embedding_slot=args.embedding_slot,
            )
            chunks_by_id = {str(chunk.get("chunk_id")): chunk for chunk in chunk_batch}
            for update in batch_updates:
                chunk = chunks_by_id.get(str(update.get("chunk_id")))
                update["embedding_backend"] = getattr(
                    client,
                    "embedding_backend",
                    args.embedding_backend or slot_spec.default_backend,
                )
                if chunk is not None:
                    update["embedding_text"] = make_embedding_text(chunk)
                updates.append(update)
                completed_chunks[offline_state_key(update)] = {
                    "chunk_hash": update.get("chunk_hash"),
                    "chunk_id": update.get("chunk_id"),
                    "completed_at": utc_now(),
                    "embedding_model": client.model_name,
                }
                processed += 1
            write_offline_embedding_state(args.state_output, state)
    except Exception as exc:  # noqa: BLE001 - persist partial artifact before returning.
        completed = False
        error = exc

    write_jsonl(args.output, updates)
    write_offline_embedding_state(args.state_output, state)
    smoke_payload = None
    if args.retrieval_smoke_output:
        smoke_payload = build_offline_retrieval_smoke(updates, args=args, client=client)
        write_summary(args.retrieval_smoke_output, smoke_payload)
    summary = build_run_summary(
        args=args,
        db_counts={"offline_artifact_embeddings": len(updates)},
        embedding_model=client.model_name,
        selected_chunks=len(selected_chunks),
        update_count=len(updates),
        completed=completed,
        selected_chunk_records=selected_chunks,
        updates=updates,
        parent_skipped_count=0,
        retrieval_smoke_output=str(args.retrieval_smoke_output) if args.retrieval_smoke_output else None,
        embedding_client=client,
        error=error,
    )
    summary.update(
        {
            "chunk_files": [str(path) for path in chunk_files],
            "mode": "offline_artifact",
            "output": str(args.output),
            "processed_chunk_count": processed,
            "resume": args.resume,
            "state_output": str(args.state_output) if args.state_output else None,
        }
    )
    if smoke_payload is not None:
        summary["retrieval_smoke"] = smoke_payload["diagnostics"]
    if args.summary_output:
        write_summary(args.summary_output, summary)
    if error is not None:
        raise error
    return summary


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Embed Neo4j Chunk nodes for Tử Vi retrieval.")
    parser.add_argument("--source-id", default=DEFAULT_SOURCE_ID)
    parser.add_argument("--chunking-strategy", default=DEFAULT_STRATEGY)
    parser.add_argument("--domain", default=DEFAULT_DOMAIN)
    parser.add_argument("--embedding-slot", choices=sorted(EMBEDDING_SLOT_SPECS), default=None)
    parser.add_argument("--model", default=None)
    parser.add_argument("--expected-dim", type=int, default=None)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--chunks-input", nargs="+", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--state-output", type=Path, default=None)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--include-parent-chunks", action="store_true")
    parser.add_argument("--mock-embedding", action="store_true")
    parser.add_argument("--embedding-backend", choices=["gemini", "local", "mock"], default=None)
    parser.add_argument("--local-embedding-model", default=DEFAULT_LOCAL_EMBEDDING_MODEL)
    parser.add_argument("--local-embedding-device", default=None)
    parser.add_argument("--local-embedding-batch-size", type=int, default=DEFAULT_LOCAL_EMBEDDING_BATCH_SIZE)
    parser.add_argument(
        "--local-embedding-implementation",
        choices=["auto", "flagembedding", "sentence-transformers"],
        default="auto",
    )
    parser.add_argument("--local-embedding-normalize", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--vector-index-name", default=None)
    parser.add_argument("--requests-per-minute", type=float, default=DEFAULT_REQUESTS_PER_MINUTE)
    parser.add_argument("--max-retries", type=int, default=6)
    parser.add_argument("--retry-base-seconds", type=float, default=10.0)
    parser.add_argument("--max-retry-sleep-seconds", type=float, default=DEFAULT_MAX_RETRY_SLEEP_SECONDS)
    parser.add_argument("--stop-on-daily-quota", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--progress-every", type=int, default=25)
    parser.add_argument("--skip-index-check", action="store_true")
    parser.add_argument("--summary-output", type=Path, default=None)
    parser.add_argument("--retrieval-smoke-output", type=Path, default=None)
    parser.add_argument("--smoke-query", default="Tu Vi")
    parser.add_argument("--smoke-candidate-k", type=int, default=500)
    parser.add_argument("--smoke-limit", type=int, default=5)
    return resolve_embedding_slot_args(parser.parse_args(argv))


def make_embedding_client(args: argparse.Namespace) -> Any:
    slot_spec = get_embedding_slot_spec(getattr(args, "embedding_slot", DEFAULT_EMBEDDING_SLOT))
    backend = "mock" if args.mock_embedding else (args.embedding_backend or slot_spec.default_backend)
    if backend == "mock":
        return MockEmbeddingClient(args.expected_dim)
    if backend == "local":
        return LocalBgeM3EmbeddingClient(
            model_name=args.local_embedding_model or args.model,
            expected_dim=args.expected_dim,
            batch_size=args.local_embedding_batch_size,
            device=args.local_embedding_device,
            implementation=args.local_embedding_implementation,
            normalize=args.local_embedding_normalize,
        )
    if backend != "gemini":
        raise ValueError("--embedding-backend must be gemini, local, or mock.")
    clients = [
        GeminiEmbeddingClient(
            api_key,
            args.model,
            args.expected_dim,
            requests_per_minute=args.requests_per_minute,
            max_retries=0,
            retry_base_seconds=args.retry_base_seconds,
            max_retry_sleep_seconds=args.max_retry_sleep_seconds,
            stop_on_daily_quota=False,
        )
        for api_key in load_gemini_api_keys()
    ]
    return MultiKeyGeminiEmbeddingClient(
        clients,
        max_retries=args.max_retries,
        retry_base_seconds=args.retry_base_seconds,
        max_retry_sleep_seconds=args.max_retry_sleep_seconds,
        stop_on_daily_quota=args.stop_on_daily_quota,
    )


def run(argv: list[str] | None = None) -> dict[str, Any]:
    load_dotenv(ROOT_DIR / ".env")
    args = parse_args(argv)
    if args.chunks_input:
        return run_offline_embedding(args)

    required_env = {
        "NEO4J_URI": os.getenv("NEO4J_URI"),
        "NEO4J_USERNAME": os.getenv("NEO4J_USERNAME") or os.getenv("NEO4J_USER"),
        "NEO4J_PASSWORD": os.getenv("NEO4J_PASSWORD"),
    }
    missing = [key for key, value in required_env.items() if not value]
    if missing:
        raise ValueError(f"{', '.join(missing)} are required.")

    from neo4j import GraphDatabase

    driver = GraphDatabase.driver(
        required_env["NEO4J_URI"] or "",
        auth=(required_env["NEO4J_USERNAME"] or "", required_env["NEO4J_PASSWORD"] or ""),
    )
    db_counts: dict[str, Any] = {}
    try:
        with driver.session(database=os.getenv("NEO4J_DATABASE") or None) as session:
            if not args.skip_index_check:
                expected_indexes = required_indexes(args.vector_index_name)
                indexes = session.execute_read(verify_indexes_tx, expected_indexes)
                assert_required_indexes_online(
                    indexes,
                    expected_indexes,
                    embedding_slot=args.embedding_slot,
                    vector_index_name=args.vector_index_name,
                )
                db_counts["verified_indexes"] = sorted(expected_indexes)

            chunks = session.execute_read(
                select_chunks_tx,
                domain=args.domain,
                source_id=args.source_id,
                chunk_strategy_id=args.chunking_strategy,
                force=args.force,
                limit=args.limit,
                include_parent_chunks=args.include_parent_chunks,
                embedding_slot=args.embedding_slot,
            )
            child_only = should_use_child_only_policy(args.chunking_strategy, args.include_parent_chunks)
            parent_skipped_count = (
                session.execute_read(
                    count_parent_skipped_tx,
                    domain=args.domain,
                    source_id=args.source_id,
                    chunk_strategy_id=args.chunking_strategy,
                    force=args.force,
                    embedding_slot=args.embedding_slot,
                )
                if child_only
                else 0
            )
            client = make_embedding_client(args)
            embedding_model = client.model_name
            updates: list[dict[str, Any]] = []
            pending_updates: list[dict[str, Any]] = []
            written_count = 0
            embedded_at = utc_now()
            embedding_batch_size = args.local_embedding_batch_size if supports_local_document_batch(client) else 1
            processed_count = 0
            next_progress_at = args.progress_every if args.progress_every else None
            try:
                for chunk_batch in batched(chunks, embedding_batch_size):
                    batch_updates = prepare_embedding_update_batch(
                        chunk_batch,
                        client,
                        expected_dim=args.expected_dim,
                        embedded_at=embedded_at,
                        embedding_slot=args.embedding_slot,
                    )
                    updates.extend(batch_updates)
                    pending_updates.extend(batch_updates)
                    processed_count += len(chunk_batch)

                    if pending_updates and not args.dry_run and len(pending_updates) >= args.batch_size:
                        written_count += session.execute_write(
                            write_embedding_updates_tx,
                            pending_updates,
                            args.batch_size,
                            args.embedding_slot,
                        )
                        pending_updates = []

                    if next_progress_at is not None and processed_count >= next_progress_at:
                        print(
                            f"Embedded {len(updates)}/{len(chunks)} selected chunks "
                            f"for {args.source_id}/{args.chunking_strategy}.",
                            file=sys.stderr,
                            flush=True,
                        )
                        while next_progress_at <= processed_count:
                            next_progress_at += args.progress_every

                if pending_updates and not args.dry_run:
                    written_count += session.execute_write(
                        write_embedding_updates_tx,
                        pending_updates,
                        args.batch_size,
                        args.embedding_slot,
                    )
                    pending_updates = []
            except (Exception, KeyboardInterrupt) as exc:
                if pending_updates and not args.dry_run:
                    written_count += session.execute_write(
                        write_embedding_updates_tx,
                        pending_updates,
                        args.batch_size,
                        args.embedding_slot,
                    )
                    db_counts["embedded_chunks"] = written_count
                    print(
                        f"Flushed {written_count} embedded chunks before stopping.",
                        file=sys.stderr,
                        flush=True,
                    )
                db_counts["embedded_chunks"] = written_count if not args.dry_run else 0
                if args.summary_output:
                    write_summary(
                        args.summary_output,
                        build_run_summary(
                            args=args,
                            db_counts=db_counts,
                            embedding_model=embedding_model,
                            selected_chunks=len(chunks),
                            update_count=len(updates),
                            completed=False,
                            selected_chunk_records=chunks,
                            updates=updates,
                            parent_skipped_count=parent_skipped_count,
                            retrieval_smoke_output=str(args.retrieval_smoke_output)
                            if args.retrieval_smoke_output
                            else None,
                            embedding_client=client,
                            error=exc,
                        ),
                    )
                raise

            db_counts["embedded_chunks"] = written_count if not args.dry_run else 0
            if args.retrieval_smoke_output:
                query_embedding = client.embed_query(args.smoke_query)
                dense_hits = session.execute_read(
                    dense_retrieval_smoke_tx,
                    args=args,
                    query_embedding=query_embedding,
                    child_only=child_only,
                )
                sparse_hits = session.execute_read(sparse_retrieval_smoke_tx, args=args, child_only=child_only)
                parent_ids = sorted(
                    {
                        str(hit.get("parent_id"))
                        for hit in [*dense_hits, *sparse_hits]
                        if hit.get("parent_id")
                    }
                )
                parent_records = session.execute_read(fetch_parent_chunks_tx, parent_ids)
                smoke_payload = write_retrieval_smoke(
                    args.retrieval_smoke_output,
                    args=args,
                    dense_hits=dense_hits,
                    sparse_hits=sparse_hits,
                    parent_records=parent_records,
                )
                db_counts["retrieval_smoke"] = smoke_payload["diagnostics"]
    finally:
        driver.close()

    summary = build_run_summary(
        args=args,
        db_counts=db_counts,
        embedding_model=embedding_model,
        selected_chunks=len(chunks),
        update_count=len(updates),
        completed=True,
        selected_chunk_records=chunks,
        updates=updates,
        parent_skipped_count=parent_skipped_count,
        retrieval_smoke_output=str(args.retrieval_smoke_output) if args.retrieval_smoke_output else None,
        embedding_client=client,
    )
    if args.summary_output:
        write_summary(args.summary_output, summary)
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
