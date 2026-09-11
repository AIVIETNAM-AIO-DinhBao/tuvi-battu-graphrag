"""Read-only data/config gate before the official sequential ablation starts."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.clients import get_neo4j_driver  # noqa: E402
from app.config import settings  # noqa: E402
from app.rag.ablation import load_ablation_dataset, load_ablation_manifest  # noqa: E402
from app.rag.evaluation_checkpoint import atomic_write_json, sha256_file  # noqa: E402


SOURCES = ["TVKL", "TVNL", "TVHS", "TVGM"]
STRATEGIES = ["chunk_fixed_512", "chunk_structure_parent_child", "chunk_semantic_embedding_bge_m3"]
REQUIRED_INDEXES = ["chunkFulltext", "chunkVectorBgeM3"]
DEFAULT_MANIFEST = ROOT_DIR / "configs" / "ablation_sequential" / "p1_chunking.yaml"
DEFAULT_ANCHOR_SUMMARY = (
    ROOT_DIR / "benchmark" / "tuvi_golden_dataset" / "sequential_ablation" / "gold_span_anchor_summary.json"
)
DEFAULT_OUTPUT = (
    ROOT_DIR / "benchmark" / "tuvi_golden_dataset" / "sequential_ablation" / "preflight" / "P1_preflight.json"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check P1 manifest, anchors, Neo4j chunks, embeddings and indexes.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--anchor-summary", type=Path, default=DEFAULT_ANCHOR_SUMMARY)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT_DIR / path


def config_isolation(manifest: Any) -> bool:
    controls: list[dict[str, Any]] = []
    for spec in manifest.configs:
        payload = spec.build_config().model_dump(mode="json")
        for key in ("experiment_id", "name", "chunk_strategy_id"):
            payload.pop(key)
        controls.append(payload)
    return bool(controls) and all(control == controls[0] for control in controls)


def neo4j_snapshot() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    driver = get_neo4j_driver()
    try:
        with driver.session(database=settings.NEO4J_DATABASE) as session:
            count_rows = [
                dict(record)
                for record in session.run(
                    """
                    MATCH (c:Chunk {domain: 'TUVI'})
                    WHERE c.source_id IN $sources
                      AND c.chunk_strategy_id IN $strategies
                      AND (c.chunk_strategy_id <> 'chunk_structure_parent_child' OR c.chunk_type = 'child')
                    RETURN c.source_id AS source_id,
                           c.chunk_strategy_id AS chunk_strategy_id,
                           count(c) AS retrieval_chunk_count,
                           count(c.embedding_bge_m3) AS embedded_chunk_count
                    ORDER BY chunk_strategy_id, source_id
                    """,
                    sources=SOURCES,
                    strategies=STRATEGIES,
                )
            ]
            index_rows = [
                dict(record)
                for record in session.run(
                    """
                    SHOW INDEXES YIELD name, state, type
                    WHERE name IN $names
                    RETURN name, state, type
                    ORDER BY name
                    """,
                    names=REQUIRED_INDEXES,
                )
            ]
    finally:
        driver.close()
    return count_rows, index_rows


def main() -> int:
    args = parse_args()
    manifest_path = resolve(args.manifest).resolve()
    summary_path = resolve(args.anchor_summary).resolve()
    output_path = resolve(args.output).resolve()
    manifest = load_ablation_manifest(manifest_path)
    anchors = json.loads(summary_path.read_text(encoding="utf-8"))
    items = load_ablation_dataset(manifest.dataset_path)
    counts, indexes = neo4j_snapshot()
    by_pair = {(str(row["source_id"]), str(row["chunk_strategy_id"])): row for row in counts}
    pair_checks: list[dict[str, Any]] = []
    for strategy in STRATEGIES:
        for source in SOURCES:
            row = by_pair.get((source, strategy), {})
            chunk_count = int(row.get("retrieval_chunk_count") or 0)
            embedded_count = int(row.get("embedded_chunk_count") or 0)
            pair_checks.append(
                {
                    "source_id": source,
                    "chunk_strategy_id": strategy,
                    "retrieval_chunk_count": chunk_count,
                    "embedded_chunk_count": embedded_count,
                    "passed": chunk_count > 0 and embedded_count == chunk_count,
                }
            )
    index_by_name = {str(row.get("name")): row for row in indexes}
    index_checks = [
        {
            "name": name,
            "state": index_by_name.get(name, {}).get("state"),
            "type": index_by_name.get(name, {}).get("type"),
            "passed": str(index_by_name.get(name, {}).get("state") or "").upper() == "ONLINE",
        }
        for name in REQUIRED_INDEXES
    ]
    gates = {
        "dataset_is_full_100": len(items) == 100,
        "manifest_has_three_configs": len(manifest.configs) == 3,
        "only_chunk_strategy_varies": config_isolation(manifest),
        "anchors_ready": bool(anchors.get("ready_for_official_run")),
        "anchor_dataset_hash_matches": anchors.get("dataset_sha256") == sha256_file(manifest.dataset_path),
        "all_12_source_strategy_pairs_embedded": all(row["passed"] for row in pair_checks),
        "required_indexes_online": all(row["passed"] for row in index_checks),
    }
    report = {
        "schema_version": "sequential-preflight-v1",
        "created_at": datetime.now(UTC).isoformat(),
        "manifest": manifest_path.as_posix(),
        "manifest_sha256": sha256_file(manifest_path),
        "dataset_sha256": sha256_file(manifest.dataset_path),
        "anchor_summary_sha256": sha256_file(summary_path),
        "gates": gates,
        "neo4j_pair_counts": pair_checks,
        "neo4j_indexes": index_checks,
        "ready": all(gates.values()),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_json(output_path, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
