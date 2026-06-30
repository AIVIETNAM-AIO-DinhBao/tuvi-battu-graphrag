"""Smoke-test dense and sparse Neo4j retrieval for W3-INGEST-06."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

import embed_chunks


ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_QUERIES = [
    "Thiên Mã tại Quan Lộc",
    "Mệnh xung chiếu Thiên Di",
    "Hóa Kỵ cần xét gì",
    "tam phương tứ chính",
    "Cung Phu Thê có ý nghĩa gì",
]
DEFAULT_CANDIDATE_K = 500
FULLTEXT_STOPWORDS = {"có", "của", "gì", "là", "tại", "thì", "trong", "và", "với"}

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def normalize_hit(record: Any) -> dict[str, Any]:
    node = record.get("node") if hasattr(record, "get") else record["node"]
    score = record.get("score") if hasattr(record, "get") else record["score"]
    return {
        "chunk_id": node.get("chunk_id") or node.get("id"),
        "chunk_hash": node.get("chunk_hash"),
        "chunk_strategy_id": node.get("chunk_strategy_id"),
        "domain": node.get("domain"),
        "score": float(score),
        "source_id": node.get("source_id"),
        "source_name": node.get("source_name"),
        "source_page": node.get("source_page"),
        "text_preview": str(node.get("text") or node.get("chunk_text") or "")[:240],
    }


def sanitize_fulltext_query(query: str) -> str:
    # Neo4j fulltext uses Lucene syntax; keep Vietnamese terms but neutralize operators.
    cleaned = re.sub(r'([+\-!(){}\[\]^"~*?:\\/]|&&|\|\|)', " ", query)
    return " ".join(cleaned.split())


def build_fulltext_query(query: str) -> str:
    terms = [
        term
        for term in sanitize_fulltext_query(query).split()
        if len(term) > 1 and term.casefold() not in FULLTEXT_STOPWORDS
    ]
    if not terms:
        return sanitize_fulltext_query(query)
    return " OR ".join(terms)


def dense_retrieval_tx(
    tx: Any,
    *,
    embedding: list[float],
    candidate_k: int,
    top_k: int,
    domain: str,
    source_id: str,
    chunk_strategy_id: str,
    vector_index_name: str = "chunkVector",
) -> list[dict[str, Any]]:
    index_name = embed_chunks.safe_index_name(vector_index_name)
    result = tx.run(
        f"""
        CALL db.index.vector.queryNodes('{index_name}', $candidate_k, $embedding)
        YIELD node, score
        WHERE node.domain = $domain
          AND node.source_id = $source_id
          AND node.chunk_strategy_id = $chunk_strategy_id
        RETURN node, score
        ORDER BY score DESC
        LIMIT $top_k
        """,
        candidate_k=max(candidate_k, top_k),
        embedding=embedding,
        top_k=top_k,
        domain=domain,
        source_id=source_id,
        chunk_strategy_id=chunk_strategy_id,
    )
    return [normalize_hit(record) for record in result]


def sparse_retrieval_tx(
    tx: Any,
    *,
    query: str,
    top_k: int,
    domain: str,
    source_id: str,
    chunk_strategy_id: str,
) -> list[dict[str, Any]]:
    result = tx.run(
        """
        CALL db.index.fulltext.queryNodes('chunkFulltext', $fulltext_query)
        YIELD node, score
        WHERE node.domain = $domain
          AND node.source_id = $source_id
          AND node.chunk_strategy_id = $chunk_strategy_id
        RETURN node, score
        ORDER BY score DESC
        LIMIT $top_k
        """,
        fulltext_query=build_fulltext_query(query),
        top_k=top_k,
        domain=domain,
        source_id=source_id,
        chunk_strategy_id=chunk_strategy_id,
    )
    return [normalize_hit(record) for record in result]


def build_query_result(query: str, dense_hits: list[dict[str, Any]], sparse_hits: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "dense_hits": dense_hits,
        "dense_hit_count": len(dense_hits),
        "passed": bool(dense_hits) and bool(sparse_hits),
        "query": query,
        "sparse_hits": sparse_hits,
        "sparse_hit_count": len(sparse_hits),
    }


def assert_smoke_passed(results: list[dict[str, Any]], diagnostics: dict[str, Any] | None = None) -> None:
    dense_failed = [result["query"] for result in results if result["dense_hit_count"] == 0]
    sparse_failed = [result["query"] for result in results if result["sparse_hit_count"] == 0]
    if not dense_failed and not sparse_failed:
        return

    details = []
    if dense_failed:
        details.append(f"dense_empty=[{'; '.join(dense_failed)}]")
    if sparse_failed:
        details.append(f"sparse_empty=[{'; '.join(sparse_failed)}]")
    if diagnostics:
        details.append(
            "diagnostics="
            + json.dumps(diagnostics, ensure_ascii=False, sort_keys=True)
        )
    raise ValueError("Dense/sparse smoke retrieval returned empty hits: " + " ".join(details))


def retrieval_diagnostics_tx(
    tx: Any,
    *,
    domain: str,
    source_id: str,
    chunk_strategy_id: str,
    embedding_slot: str = embed_chunks.DEFAULT_EMBEDDING_SLOT,
) -> dict[str, Any]:
    spec = embed_chunks.get_embedding_slot_spec(embedding_slot)
    vector_property = embed_chunks.safe_property_name(spec.vector_property)
    model_property = embed_chunks.safe_property_name(spec.model_property)
    result = tx.run(
        f"""
        MATCH (c:Chunk)
        WHERE c.domain = $domain
          AND c.source_id = $source_id
          AND c.chunk_strategy_id = $chunk_strategy_id
        RETURN
          count(c) AS total_chunks,
          sum(CASE WHEN c.{vector_property} IS NULL THEN 0 ELSE 1 END) AS embedded_chunks,
          sum(CASE WHEN coalesce(c.text, '') <> '' THEN 1 ELSE 0 END) AS text_chunks,
          sum(CASE WHEN coalesce(c.title, '') <> '' THEN 1 ELSE 0 END) AS title_chunks,
          sum(CASE WHEN coalesce(c.keywords, '') <> '' THEN 1 ELSE 0 END) AS keyword_chunks,
          collect(DISTINCT c.{model_property})[0..10] AS embedding_models
        """,
        domain=domain,
        source_id=source_id,
        chunk_strategy_id=chunk_strategy_id,
    )
    record = result.single() if hasattr(result, "single") else (result[0] if result else None)
    diagnostics = dict(record) if record else {}
    diagnostics["embedding_property"] = spec.vector_property
    diagnostics["embedding_slot"] = spec.slot
    return diagnostics


def write_summary(path: Path, summary: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Smoke-test Neo4j vector and fulltext retrieval.")
    parser.add_argument("--source-id", default=embed_chunks.DEFAULT_SOURCE_ID)
    parser.add_argument("--chunking-strategy", default=embed_chunks.DEFAULT_STRATEGY)
    parser.add_argument("--domain", default=embed_chunks.DEFAULT_DOMAIN)
    parser.add_argument(
        "--embedding-slot",
        choices=sorted(embed_chunks.EMBEDDING_SLOT_SPECS),
        default=None,
    )
    parser.add_argument("--model", default=None)
    parser.add_argument("--expected-dim", type=int, default=None)
    parser.add_argument("--candidate-k", type=int, default=DEFAULT_CANDIDATE_K)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--query", action="append", default=None)
    parser.add_argument("--mock-embedding", action="store_true")
    parser.add_argument("--embedding-backend", choices=["gemini", "local", "mock"], default=None)
    parser.add_argument("--local-embedding-model", default=embed_chunks.DEFAULT_LOCAL_EMBEDDING_MODEL)
    parser.add_argument("--local-embedding-device", default=None)
    parser.add_argument("--local-embedding-batch-size", type=int, default=embed_chunks.DEFAULT_LOCAL_EMBEDDING_BATCH_SIZE)
    parser.add_argument(
        "--local-embedding-implementation",
        choices=["auto", "flagembedding", "sentence-transformers"],
        default="auto",
    )
    parser.add_argument("--local-embedding-normalize", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--vector-index-name", default=None)
    parser.add_argument("--requests-per-minute", type=float, default=embed_chunks.DEFAULT_REQUESTS_PER_MINUTE)
    parser.add_argument("--max-retries", type=int, default=6)
    parser.add_argument("--retry-base-seconds", type=float, default=10.0)
    parser.add_argument("--max-retry-sleep-seconds", type=float, default=embed_chunks.DEFAULT_MAX_RETRY_SLEEP_SECONDS)
    parser.add_argument("--stop-on-daily-quota", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--skip-index-check", action="store_true")
    parser.add_argument("--allow-empty", action="store_true")
    parser.add_argument("--summary-output", type=Path, default=None)
    return embed_chunks.resolve_embedding_slot_args(parser.parse_args(argv))


def make_embedding_client(args: argparse.Namespace) -> Any:
    return embed_chunks.make_embedding_client(args)


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

    queries = args.query or DEFAULT_QUERIES
    client = make_embedding_client(args)
    results: list[dict[str, Any]] = []
    diagnostics: dict[str, Any] = {}
    driver = GraphDatabase.driver(
        required_env["NEO4J_URI"] or "",
        auth=(required_env["NEO4J_USERNAME"] or "", required_env["NEO4J_PASSWORD"] or ""),
    )
    try:
        with driver.session(database=os.getenv("NEO4J_DATABASE") or None) as session:
            if not args.skip_index_check:
                expected_indexes = embed_chunks.required_indexes(args.vector_index_name)
                indexes = session.execute_read(embed_chunks.verify_indexes_tx, expected_indexes)
                embed_chunks.assert_required_indexes_online(
                    indexes,
                    expected_indexes,
                    embedding_slot=args.embedding_slot,
                    vector_index_name=args.vector_index_name,
                )

            diagnostics = session.execute_read(
                retrieval_diagnostics_tx,
                domain=args.domain,
                source_id=args.source_id,
                chunk_strategy_id=args.chunking_strategy,
                embedding_slot=args.embedding_slot,
            )

            for query in queries:
                embedding = client.embed_query(query)
                embed_chunks.validate_embedding_dimension(embedding, args.expected_dim)
                dense_hits = session.execute_read(
                    dense_retrieval_tx,
                    embedding=embedding,
                    candidate_k=args.candidate_k,
                    top_k=args.top_k,
                    domain=args.domain,
                    source_id=args.source_id,
                    chunk_strategy_id=args.chunking_strategy,
                    vector_index_name=args.vector_index_name,
                )
                sparse_hits = session.execute_read(
                    sparse_retrieval_tx,
                    query=query,
                    top_k=args.top_k,
                    domain=args.domain,
                    source_id=args.source_id,
                    chunk_strategy_id=args.chunking_strategy,
                )
                results.append(build_query_result(query, dense_hits, sparse_hits))
    finally:
        driver.close()

    summary = {
        "candidate_k": args.candidate_k,
        "chunk_strategy_id": args.chunking_strategy,
        "diagnostics": diagnostics,
        "domain": args.domain,
        "embedding_slot": args.embedding_slot,
        "embedding_model": client.model_name,
        "embedding_backend": getattr(
            client,
            "embedding_backend",
            args.embedding_backend or embed_chunks.get_embedding_slot_spec(args.embedding_slot).default_backend,
        ),
        "generated_at": utc_now(),
        "passed": all(result["passed"] for result in results),
        "query_count": len(results),
        "results": results,
        "source_id": args.source_id,
        "top_k": args.top_k,
        "vector_index_name": args.vector_index_name,
    }
    if hasattr(client, "get_usage_summary"):
        summary.update(client.get_usage_summary())
    if args.summary_output:
        write_summary(args.summary_output, summary)

    if not args.allow_empty:
        assert_smoke_passed(results, diagnostics)
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
