"""Import portable graph payload artifacts into Neo4j/Supabase without rerunning LLMs."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

import write_graph_provenance as writer


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


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import graph payload artifacts into Neo4j/Supabase.")
    parser.add_argument("--payload-input-dir", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-neo4j", action="store_true")
    parser.add_argument("--skip-supabase", action="store_true")
    parser.add_argument("--batch-size", type=int, default=500)
    parser.add_argument("--summary-output", type=Path, default=None)
    return parser.parse_args(argv)


def run(argv: list[str] | None = None) -> dict[str, Any]:
    load_dotenv(ROOT_DIR / ".env")
    args = parse_args(argv)
    payload = writer.load_payload_output_dir(args.payload_input_dir)

    db_counts: dict[str, Any] = {}
    if not args.dry_run:
        if not args.skip_supabase:
            database_url = os.getenv("DATABASE_URL")
            if not database_url:
                raise ValueError("DATABASE_URL is required unless --dry-run or --skip-supabase is used.")
            db_counts["supabase_source_chunks"] = writer.write_supabase_source_chunks(
                database_url,
                payload["chunk_records"],
                args.batch_size,
            )
        if not args.skip_neo4j:
            required_env = {
                "NEO4J_URI": os.getenv("NEO4J_URI"),
                "NEO4J_USERNAME": os.getenv("NEO4J_USERNAME") or os.getenv("NEO4J_USER"),
                "NEO4J_PASSWORD": os.getenv("NEO4J_PASSWORD"),
            }
            missing = [key for key, value in required_env.items() if not value]
            if missing:
                raise ValueError(
                    f"{', '.join(missing)} are required unless --dry-run or --skip-neo4j is used."
                )
            db_counts["neo4j"] = writer.write_neo4j_graph(
                required_env["NEO4J_URI"] or "",
                required_env["NEO4J_USERNAME"] or "",
                required_env["NEO4J_PASSWORD"] or "",
                os.getenv("NEO4J_DATABASE"),
                payload,
                args.batch_size,
            )

    summary = {
        **payload["summary"],
        "db_write_counts": db_counts,
        "dry_run": args.dry_run,
        "generated_at": utc_now(),
        "payload_input_dir": str(args.payload_input_dir),
        "summary_output": str(args.summary_output) if args.summary_output else None,
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
