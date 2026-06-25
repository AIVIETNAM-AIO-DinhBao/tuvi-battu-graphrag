"""Apply one or more Supabase/Postgres migration SQL files.

This is the psql-free path for Windows/dev machines where the PostgreSQL CLI is
not installed but backend dependencies already include psycopg.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parent.parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Apply Supabase migration SQL files.")
    parser.add_argument("migration", nargs="+", type=Path)
    return parser.parse_args()


def read_sql(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Migration file does not exist: {path}")
    return path.read_text(encoding="utf-8")


def apply_migration(database_url: str, path: Path) -> None:
    sql = read_sql(path)
    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()


def main() -> None:
    load_dotenv(ROOT_DIR / ".env")
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise SystemExit("DATABASE_URL is required in .env or the current shell environment.")

    args = parse_args()
    for path in args.migration:
        print(f"Applying migration: {path}")
        apply_migration(database_url, path)
        print(f"✓ Applied: {path}")


if __name__ == "__main__":
    main()
