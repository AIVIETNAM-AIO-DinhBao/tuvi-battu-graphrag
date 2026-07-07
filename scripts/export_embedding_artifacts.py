"""Export existing Neo4j chunk embeddings as portable JSONL artifacts."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

import embed_chunks


ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_SMOKE_QUERY = "Thiên Mã tại Quan Lộc"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def fetch_embedding_records(args: argparse.Namespace) -> list[dict[str, Any]]:
    required_env = {
        "NEO4J_URI": os.getenv("NEO4J_URI"),
        "NEO4J_USERNAME": os.getenv("NEO4J_USERNAME") or os.getenv("NEO4J_USER"),
        "NEO4J_PASSWORD": os.getenv("NEO4J_PASSWORD"),
    }
    missing = [key for key, value in required_env.items() if not value]
    if missing:
        raise ValueError(f"{', '.join(missing)} are required.")

    from neo4j import GraphDatabase

    slot = embed_chunks.get_embedding_slot_spec(args.embedding_slot)
    child_only = embed_chunks.should_use_child_only_policy(args.chunking_strategy, args.include_parent_chunks)
    cypher = f"""
        MATCH (c:Chunk)
        WHERE c.domain = $domain
          AND c.source_id = $source_id
          AND c.chunk_strategy_id = $chunk_strategy_id
          AND c.{slot.vector_property} IS NOT NULL
          AND ($child_only = false OR c.chunk_type = 'child' OR coalesce(c.retrieval_unit, false) = true)
        RETURN
          c.chunk_hash AS chunk_hash,
          c.chunk_id AS chunk_id,
          c.chunk_strategy_id AS chunk_strategy_id,
          c.chunk_type AS chunk_type,
          c.{slot.vector_property} AS embedding,
          c.{slot.dim_property} AS embedding_dim,
          c.{slot.model_property} AS embedding_model,
          c.{slot.text_hash_property} AS embedding_text_hash,
          c.{slot.embedded_at_property} AS embedded_at,
          c.keywords AS keywords,
          c.parent_id AS parent_id,
          coalesce(c.retrieval_unit, false) AS retrieval_unit,
          c.source_id AS source_id,
          c.title AS title,
          coalesce(c.text, c.chunk_text, '') AS embedding_text
        ORDER BY c.chunk_id
        SKIP $skip
        LIMIT $limit
    """
    driver = GraphDatabase.driver(
        required_env["NEO4J_URI"] or "",
        auth=(required_env["NEO4J_USERNAME"] or "", required_env["NEO4J_PASSWORD"] or ""),
    )
    try:
        with driver.session(database=os.getenv("NEO4J_DATABASE") or None) as session:
            records = []
            skip = 0
            while True:
                rows = list(
                    session.run(
                        cypher,
                        domain=args.domain,
                        source_id=args.source_id,
                        chunk_strategy_id=args.chunking_strategy,
                        child_only=child_only,
                        skip=skip,
                        limit=args.fetch_batch_size,
                    )
                )
                if not rows:
                    break
                records.extend(dict(row) for row in rows)
                if len(rows) < args.fetch_batch_size:
                    break
                skip += len(rows)
    finally:
        driver.close()

    updates: list[dict[str, Any]] = []
    for record in records:
        embedding = record.get("embedding")
        if not isinstance(embedding, list):
            continue
        embed_chunks.validate_embedding_dimension(embedding, args.expected_dim)
        updates.append(
            {
                "chunk_hash": record.get("chunk_hash"),
                "chunk_id": record.get("chunk_id"),
                "chunk_strategy_id": record.get("chunk_strategy_id"),
                "chunk_type": record.get("chunk_type"),
                "embedding": [float(value) for value in embedding],
                "embedding_backend": "exported_neo4j",
                "embedding_dim": args.expected_dim,
                "embedding_model": record.get("embedding_model") or args.model,
                "embedding_slot": slot.slot,
                "embedding_text": record.get("embedding_text") or "",
                "embedding_text_hash": record.get("embedding_text_hash"),
                "embedded_at": record.get("embedded_at"),
                "keywords": record.get("keywords") or "",
                "parent_id": record.get("parent_id"),
                "retrieval_unit": bool(record.get("retrieval_unit")),
                "source_id": record.get("source_id"),
                "title": record.get("title"),
                "vector_index_name": args.vector_index_name,
                "vector_property": slot.vector_property,
            }
        )
    return updates


def build_retrieval_smoke(updates: list[dict[str, Any]], args: argparse.Namespace) -> dict[str, Any]:
    slot = embed_chunks.get_embedding_slot_spec(args.embedding_slot)
    query_embedding = embed_chunks.l2_normalize(updates[0]["embedding"]) if updates else []
    dense_hits = sorted(
        (
            {
                "chunk_hash": update["chunk_hash"],
                "chunk_id": update["chunk_id"],
                "chunk_strategy_id": update["chunk_strategy_id"],
                "chunk_type": update.get("chunk_type"),
                "domain": args.domain,
                "parent_id": update.get("parent_id"),
                "score": round(embed_chunks.dot_product(embed_chunks.l2_normalize(update["embedding"]), query_embedding), 6),
                "source_id": update["source_id"],
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
                "chunk_strategy_id": update["chunk_strategy_id"],
                "chunk_type": update.get("chunk_type"),
                "domain": args.domain,
                "parent_id": update.get("parent_id"),
                "score": round(embed_chunks.lexical_sparse_score(args.smoke_query, str(update.get("embedding_text") or "")), 6),
                "source_id": update["source_id"],
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
            "embedding_property": slot.vector_property,
            "embedding_slot": slot.slot,
            "mode": "offline_artifact",
            "sparse_hit_count": len([hit for hit in sparse_hits if hit["score"] > 0]),
        },
        "domain": args.domain,
        "embedding_model": args.model,
        "embedding_slot": slot.slot,
        "generated_at": utc_now(),
        "query": args.smoke_query,
        "source_id": args.source_id,
        "sparse_hits": sparse_hits,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export Neo4j embeddings into portable artifacts.")
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--chunking-strategy", required=True)
    parser.add_argument("--domain", default=embed_chunks.DEFAULT_DOMAIN)
    parser.add_argument("--embedding-slot", choices=sorted(embed_chunks.EMBEDDING_SLOT_SPECS), default="bge_m3")
    parser.add_argument("--model", default=embed_chunks.DEFAULT_LOCAL_EMBEDDING_MODEL)
    parser.add_argument("--expected-dim", type=int, default=embed_chunks.DEFAULT_LOCAL_EMBEDDING_DIM)
    parser.add_argument("--vector-index-name", default=embed_chunks.DEFAULT_LOCAL_VECTOR_INDEX)
    parser.add_argument("--include-parent-chunks", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--summary-output", type=Path, default=None)
    parser.add_argument("--retrieval-smoke-output", type=Path, default=None)
    parser.add_argument("--smoke-query", default=DEFAULT_SMOKE_QUERY)
    parser.add_argument("--smoke-limit", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=500)
    parser.add_argument("--fetch-batch-size", type=int, default=200)
    args = parser.parse_args(argv)
    args.dry_run = False
    args.force = False
    args.limit = None
    args.mock_embedding = False
    args.requests_per_minute = 90.0
    args.smoke_candidate_k = 500
    args.embedding_backend = "exported_neo4j"
    return args


def run(argv: list[str] | None = None) -> dict[str, Any]:
    load_dotenv(ROOT_DIR / ".env")
    args = parse_args(argv)
    updates = fetch_embedding_records(args)
    if not updates:
        raise ValueError("No Neo4j embeddings matched the requested filters.")

    embed_chunks.write_jsonl(args.output, updates)
    smoke_payload = None
    if args.retrieval_smoke_output:
        smoke_payload = build_retrieval_smoke(updates, args)
        write_json(args.retrieval_smoke_output, smoke_payload)

    slot = embed_chunks.get_embedding_slot_spec(args.embedding_slot)
    summary = embed_chunks.build_run_summary(
        args=args,
        db_counts={"exported_neo4j_embeddings": len(updates)},
        embedding_model=args.model,
        selected_chunks=len(updates),
        update_count=len(updates),
        completed=True,
        selected_chunk_records=updates,
        updates=updates,
        parent_skipped_count=0,
        retrieval_smoke_output=str(args.retrieval_smoke_output) if args.retrieval_smoke_output else None,
    )
    summary.update(
        {
            "dry_run": False,
            "embedding_backend": "exported_neo4j",
            "embedding_property": slot.vector_property,
            "mode": "offline_artifact",
            "output": str(args.output),
            "retrieval_smoke": smoke_payload["diagnostics"] if smoke_payload else None,
        }
    )
    if args.summary_output:
        write_json(args.summary_output, summary)
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
