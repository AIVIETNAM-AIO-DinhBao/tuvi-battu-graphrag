"""Import offline embedding JSONL artifacts into Neo4j for a chosen embedding slot."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable

from dotenv import load_dotenv

import embed_chunks


ROOT_DIR = Path(__file__).resolve().parent.parent

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def write_summary(path: Path, summary: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def discover_embedding_files(inputs: Iterable[Path]) -> list[Path]:
    discovered: list[Path] = []
    for path in inputs:
        if not path.exists():
            raise FileNotFoundError(f"Embedding input does not exist: {path}")
        if path.is_dir():
            discovered.extend(sorted(path.rglob("*_embeddings.jsonl")) or sorted(path.rglob("*.jsonl")))
            continue
        if path.suffix.lower() != ".jsonl":
            raise ValueError(f"Embedding input must be JSONL or directory: {path}")
        discovered.append(path)
    unique: dict[Path, None] = {}
    for path in discovered:
        unique[path.resolve()] = None
    return sorted(unique)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import offline embedding artifacts into Neo4j.")
    parser.add_argument("--input", nargs="+", type=Path, required=True)
    parser.add_argument("--source-id", default=None)
    parser.add_argument("--chunking-strategy", default=None)
    parser.add_argument("--embedding-slot", choices=sorted(embed_chunks.EMBEDDING_SLOT_SPECS), default="bge_m3")
    parser.add_argument("--model", default=None)
    parser.add_argument("--expected-dim", type=int, default=None)
    parser.add_argument("--embedding-backend", choices=["gemini", "local", "mock"], default=None)
    parser.add_argument("--local-embedding-model", default=embed_chunks.DEFAULT_LOCAL_EMBEDDING_MODEL)
    parser.add_argument("--vector-index-name", default=None)
    parser.add_argument("--batch-size", type=int, default=500)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-index-check", action="store_true")
    parser.add_argument("--summary-output", type=Path, default=None)
    return embed_chunks.resolve_embedding_slot_args(parser.parse_args(argv))


def filter_updates(records: list[dict[str, Any]], args: argparse.Namespace) -> list[dict[str, Any]]:
    selected = records
    if args.source_id:
        selected = [record for record in selected if str(record.get("source_id")) == args.source_id]
    if args.chunking_strategy:
        selected = [record for record in selected if str(record.get("chunk_strategy_id")) == args.chunking_strategy]
    return selected


def validate_updates(records: list[dict[str, Any]], args: argparse.Namespace) -> None:
    for record in records:
        artifact_slot = record.get("embedding_slot")
        if artifact_slot and artifact_slot != args.embedding_slot:
            raise ValueError(
                f"Embedding artifact slot {artifact_slot!r} does not match requested slot {args.embedding_slot!r}."
            )
        embedding = record.get("embedding")
        if not isinstance(embedding, list):
            raise ValueError(f"Embedding artifact is missing a vector list for chunk {record.get('chunk_id')}.")
        embed_chunks.validate_embedding_dimension(embedding, args.expected_dim)


def run(argv: list[str] | None = None) -> dict[str, Any]:
    load_dotenv(ROOT_DIR / ".env")
    args = parse_args(argv)
    files = discover_embedding_files(args.input)
    records: list[dict[str, Any]] = []
    for path in files:
        records.extend(embed_chunks.read_jsonl(path))
    selected = filter_updates(records, args)
    if not selected:
        raise ValueError("No embedding artifact records matched the requested filters.")
    validate_updates(selected, args)

    db_counts: dict[str, Any] = {}
    if not args.dry_run:
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
                    db_counts["verified_indexes"] = sorted(expected_indexes)
                db_counts["embedded_chunks"] = session.execute_write(
                    embed_chunks.write_embedding_updates_tx,
                    selected,
                    args.batch_size,
                    args.embedding_slot,
                )
        finally:
            driver.close()

    slot_spec = embed_chunks.get_embedding_slot_spec(args.embedding_slot)
    summary = {
        "completed": True,
        "db_write_counts": db_counts,
        "dry_run": args.dry_run,
        "embedding_property": slot_spec.vector_property,
        "embedding_slot": slot_spec.slot,
        "expected_dim": args.expected_dim,
        "files": [str(path) for path in files],
        "generated_at": utc_now(),
        "source_id": args.source_id,
        "chunk_strategy_id": args.chunking_strategy,
        "update_count": len(selected),
        "vector_index_name": args.vector_index_name,
    }
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
