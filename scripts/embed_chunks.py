"""Create Neo4j Chunk embeddings and fulltext metadata for W3-INGEST-06."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable, Mapping

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DOMAIN = "TUVI"
DEFAULT_SOURCE_ID = "TVGM"
DEFAULT_STRATEGY = "chunk_structure_parent_child"
DEFAULT_EMBEDDING_MODEL = "gemini-embedding-2"
DEFAULT_EXPECTED_DIM = 768
DEFAULT_REQUESTS_PER_MINUTE = 90.0
DEFAULT_MAX_RETRY_SLEEP_SECONDS = 300.0
REQUIRED_INDEXES = {"chunkVector", "chunkFulltext"}

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


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


def validate_embedding_dimension(vector: list[float], expected_dim: int) -> None:
    if len(vector) != expected_dim:
        raise ValueError(f"Embedding dimension mismatch: expected {expected_dim}, got {len(vector)}.")


def load_gemini_api_keys(env: Mapping[str, str | None] | None = None) -> list[str]:
    source = env if env is not None else os.environ
    raw_keys = str(source.get("GEMINI_API_KEYS") or "").split(",")
    if not any(key.strip() for key in raw_keys):
        raw_keys = [
            str(source.get("GEMINI_API_KEY") or ""),
            str(source.get("GEMINI_API_KEY_2") or ""),
        ]

    keys: list[str] = []
    seen: set[str] = set()
    for raw_key in raw_keys:
        key = raw_key.strip()
        if not key or key in seen:
            continue
        keys.append(key)
        seen.add(key)
    return keys


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
        self.model_name = "mock-embedding-768"
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


def build_select_chunks_cypher(*, force: bool, limit: int | None) -> str:
    embedding_filter = "" if force else "AND c.embedding IS NULL"
    limit_clause = "\nLIMIT $limit" if limit is not None else ""
    return f"""
        MATCH (c:Chunk)
        WHERE c.domain = $domain
          AND c.source_id = $source_id
          AND c.chunk_strategy_id = $chunk_strategy_id
          {embedding_filter}
        OPTIONAL MATCH (c)-[:MENTIONS]->(e:Entity)
        WITH c, collect(DISTINCT e.canonical_name) AS keywords
        ORDER BY c.chunk_id
        RETURN
          c.chunk_hash AS chunk_hash,
          c.chunk_id AS chunk_id,
          c.chunk_strategy_id AS chunk_strategy_id,
          c.domain AS domain,
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
) -> list[dict[str, Any]]:
    result = tx.run(
        build_select_chunks_cypher(force=force, limit=limit),
        domain=domain,
        source_id=source_id,
        chunk_strategy_id=chunk_strategy_id,
        limit=limit,
    )
    return [normalize_chunk_record(record) for record in result]


def verify_indexes_tx(tx: Any) -> list[dict[str, Any]]:
    result = tx.run(
        """
        SHOW INDEXES
        YIELD name, state, type, entityType, labelsOrTypes, properties
        WHERE name IN $index_names
        RETURN name, state, type, entityType, labelsOrTypes, properties
        ORDER BY name
        """,
        index_names=sorted(REQUIRED_INDEXES),
    )
    return [dict(record) for record in result]


def assert_required_indexes_online(indexes: list[dict[str, Any]]) -> None:
    by_name = {record.get("name"): record for record in indexes}
    missing = sorted(REQUIRED_INDEXES - set(by_name))
    if missing:
        raise ValueError(f"Missing Neo4j index(es): {', '.join(missing)}")
    offline = sorted(name for name, record in by_name.items() if record.get("state") != "ONLINE")
    if offline:
        raise ValueError(f"Neo4j index(es) not ONLINE: {', '.join(offline)}")


def prepare_embedding_updates(
    chunks: list[dict[str, Any]],
    client: Any,
    *,
    expected_dim: int,
) -> list[dict[str, Any]]:
    updates: list[dict[str, Any]] = []
    embedded_at = utc_now()
    for chunk in chunks:
        update = prepare_embedding_update(chunk, client, expected_dim=expected_dim, embedded_at=embedded_at)
        if update:
            updates.append(update)
    return updates


def prepare_embedding_update(
    chunk: dict[str, Any],
    client: Any,
    *,
    expected_dim: int,
    embedded_at: str | None = None,
) -> dict[str, Any] | None:
    text = make_embedding_text(chunk)
    if not text:
        return None
    embedding = client.embed_document(text, title=make_title(chunk))
    validate_embedding_dimension(embedding, expected_dim)
    return {
        "chunk_hash": chunk["chunk_hash"],
        "chunk_id": chunk["chunk_id"],
        "embedding": embedding,
        "embedding_dim": expected_dim,
        "embedding_model": client.model_name,
        "embedding_text_hash": embedding_text_hash(text),
        "embedded_at": embedded_at or utc_now(),
        "keywords": normalize_keywords(chunk.get("mention_keywords") or []),
        "title": make_title(chunk),
    }


def write_embedding_updates_tx(tx: Any, updates: list[dict[str, Any]], batch_size: int) -> int:
    for batch in batched(updates, batch_size):
        tx.run(
            """
            UNWIND $updates AS row
            MATCH (c:Chunk {chunk_hash: row.chunk_hash})
            SET c.embedding = row.embedding,
                c.embedding_model = row.embedding_model,
                c.embedding_dim = row.embedding_dim,
                c.embedded_at = row.embedded_at,
                c.embedding_text_hash = row.embedding_text_hash,
                c.title = row.title,
                c.keywords = row.keywords
            """,
            updates=batch,
        )
    return len(updates)


def batched(records: list[dict[str, Any]], batch_size: int) -> Iterable[list[dict[str, Any]]]:
    size = max(1, batch_size)
    for index in range(0, len(records), size):
        yield records[index : index + size]


def write_summary(path: Path, summary: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def build_run_summary(
    *,
    args: argparse.Namespace,
    db_counts: dict[str, Any],
    embedding_model: str,
    selected_chunks: int,
    update_count: int,
    completed: bool,
    embedding_client: Any | None = None,
    error: BaseException | None = None,
) -> dict[str, Any]:
    summary = {
        "batch_size": args.batch_size,
        "chunk_strategy_id": args.chunking_strategy,
        "completed": completed,
        "db_write_counts": db_counts,
        "domain": args.domain,
        "dry_run": args.dry_run,
        "embedding_model": embedding_model,
        "expected_dim": args.expected_dim,
        "force": args.force,
        "generated_at": utc_now(),
        "limit": args.limit,
        "requests_per_minute": None if args.mock_embedding else args.requests_per_minute,
        "selected_chunks": selected_chunks,
        "source_id": args.source_id,
        "update_count": update_count,
    }
    if error is not None:
        summary["error"] = f"{type(error).__name__}: {error}"
    if embedding_client is not None and hasattr(embedding_client, "get_usage_summary"):
        summary.update(embedding_client.get_usage_summary())
    return summary


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Embed Neo4j Chunk nodes for Tử Vi retrieval.")
    parser.add_argument("--source-id", default=DEFAULT_SOURCE_ID)
    parser.add_argument("--chunking-strategy", default=DEFAULT_STRATEGY)
    parser.add_argument("--domain", default=DEFAULT_DOMAIN)
    parser.add_argument("--model", default=DEFAULT_EMBEDDING_MODEL)
    parser.add_argument("--expected-dim", type=int, default=DEFAULT_EXPECTED_DIM)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--mock-embedding", action="store_true")
    parser.add_argument("--requests-per-minute", type=float, default=DEFAULT_REQUESTS_PER_MINUTE)
    parser.add_argument("--max-retries", type=int, default=6)
    parser.add_argument("--retry-base-seconds", type=float, default=10.0)
    parser.add_argument("--max-retry-sleep-seconds", type=float, default=DEFAULT_MAX_RETRY_SLEEP_SECONDS)
    parser.add_argument("--stop-on-daily-quota", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--progress-every", type=int, default=25)
    parser.add_argument("--skip-index-check", action="store_true")
    parser.add_argument("--summary-output", type=Path, default=None)
    return parser.parse_args(argv)


def make_embedding_client(args: argparse.Namespace) -> Any:
    if args.mock_embedding:
        return MockEmbeddingClient(args.expected_dim)
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
                indexes = session.execute_read(verify_indexes_tx)
                assert_required_indexes_online(indexes)
                db_counts["verified_indexes"] = sorted(REQUIRED_INDEXES)

            chunks = session.execute_read(
                select_chunks_tx,
                domain=args.domain,
                source_id=args.source_id,
                chunk_strategy_id=args.chunking_strategy,
                force=args.force,
                limit=args.limit,
            )
            client = make_embedding_client(args)
            embedding_model = client.model_name
            updates: list[dict[str, Any]] = []
            pending_updates: list[dict[str, Any]] = []
            written_count = 0
            embedded_at = utc_now()
            try:
                for index, chunk in enumerate(chunks, start=1):
                    update = prepare_embedding_update(
                        chunk,
                        client,
                        expected_dim=args.expected_dim,
                        embedded_at=embedded_at,
                    )
                    if update:
                        updates.append(update)
                        pending_updates.append(update)

                    if pending_updates and not args.dry_run and len(pending_updates) >= args.batch_size:
                        written_count += session.execute_write(
                            write_embedding_updates_tx,
                            pending_updates,
                            args.batch_size,
                        )
                        pending_updates = []

                    if args.progress_every and index % args.progress_every == 0:
                        print(
                            f"Embedded {len(updates)}/{len(chunks)} selected chunks "
                            f"for {args.source_id}/{args.chunking_strategy}.",
                            file=sys.stderr,
                            flush=True,
                        )

                if pending_updates and not args.dry_run:
                    written_count += session.execute_write(
                        write_embedding_updates_tx,
                        pending_updates,
                        args.batch_size,
                    )
                    pending_updates = []
            except (Exception, KeyboardInterrupt) as exc:
                if pending_updates and not args.dry_run:
                    written_count += session.execute_write(
                        write_embedding_updates_tx,
                        pending_updates,
                        args.batch_size,
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
                            embedding_client=client,
                            error=exc,
                        ),
                    )
                raise

            db_counts["embedded_chunks"] = written_count if not args.dry_run else 0
    finally:
        driver.close()

    summary = build_run_summary(
        args=args,
        db_counts=db_counts,
        embedding_model=embedding_model,
        selected_chunks=len(chunks),
        update_count=len(updates),
        completed=True,
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
