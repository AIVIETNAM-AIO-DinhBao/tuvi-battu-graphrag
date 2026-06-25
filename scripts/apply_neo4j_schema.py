"""
Apply Neo4j schema from Cypher file to AuraDB instance.
"""
import os
from pathlib import Path

from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError, ServiceUnavailable
from dotenv import load_dotenv


def apply_cypher(driver, cypher_file: Path, database: str | None = None) -> int:
    sql_content = cypher_file.read_text(encoding="utf-8")
    statements = [s.strip() for s in sql_content.split(";") if s.strip()]

    failures = 0
    with driver.session(database=database or None) as session:
        for statement in statements:
            try:
                session.run(statement)
                print(f"✓ Executed: {statement[:80]}...")
            except Exception as e:
                failures += 1
                print(f"✗ Failed: {statement[:80]}...")
                print(f"  Error: {e}")
    return failures


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    load_dotenv(root / ".env")
    
    neo4j_uri = os.getenv("NEO4J_URI")
    neo4j_user = os.getenv("NEO4J_USERNAME") or os.getenv("NEO4J_USER")
    neo4j_pass = os.getenv("NEO4J_PASSWORD")
    neo4j_database = os.getenv("NEO4J_DATABASE")
    
    if not all([neo4j_uri, neo4j_user, neo4j_pass]):
        raise SystemExit("Neo4j credentials missing in .env")
    
    driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_pass))
    try:
        print(f"Checking Neo4j connectivity: {neo4j_uri}")
        driver.verify_connectivity()

        cypher_file = root / "infra" / "neo4j" / "schema.cypher"
        print(f"Applying Neo4j schema from {cypher_file}")
        failures = apply_cypher(driver, cypher_file, database=neo4j_database)
    except (Neo4jError, ServiceUnavailable, OSError) as exc:
        raise SystemExit(f"Neo4j connectivity failed: {exc}") from exc
    finally:
        driver.close()

    if failures:
        raise SystemExit(f"Neo4j schema apply finished with {failures} failed statement(s).")
    print("Neo4j schema applied successfully.")


if __name__ == "__main__":
    main()
