import json
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR / "scripts"))

import audit_w3_ingest_07 as audit  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records),
        encoding="utf-8",
    )


def test_w3_ingest_07_audit_accepts_complete_minimal_artifacts() -> None:
    work_dir = ROOT_DIR / "pytest-cache-files-w3-ingest-07-audit" / "complete"
    source = "TVGM"
    strategy = "chunk_fixed_512"
    reports = work_dir / "reports"
    chunks = work_dir / "chunks"
    regen = work_dir / "regen"
    entities = work_dir / "entities"
    payloads = work_dir / "payloads"
    embeddings = work_dir / "embeddings"
    imports = reports / "import_checks"
    vector = [0.0] * 1024

    chunk_record = {
        "chunk_hash": "hash-1",
        "chunk_id": "TVGM_chunk_fixed_512_chunk_000001",
        "chunk_strategy_id": strategy,
        "chunk_type": "chunk",
        "domain": "TUVI",
        "metadata": {"retrieval_unit": True},
        "parent_id": None,
        "source_id": source,
    }
    write_jsonl(chunks / strategy / f"{source}_chunks.jsonl", [chunk_record])
    write_jsonl(regen / strategy / f"{source}_chunks.jsonl", [chunk_record])
    write_json(
        reports / f"{strategy}_chunk_summary.json",
        {
            "chunk_strategy_id": strategy,
            "documents": {source: {"total_chunks": 1}},
            "total_chunks": 1,
        },
    )
    write_jsonl(entities / strategy / f"{strategy}_entities.jsonl", [{"chunk_id": chunk_record["chunk_id"]}])
    write_json(reports / f"{strategy}_entity_review.json", {"sample_size": 1})
    write_json(reports / f"{strategy}_relation_review.json", {"sample_size": 1})

    payload_summary = {
        "chunk_count": 1,
        "completed": True,
        "payload_record_counts": {
            "canonical_relation_records": 0,
            "chunk_records": 1,
            "entity_records": 0,
            "mention_records": 0,
            "relation_records": 0,
            "source_records": 1,
        },
    }
    payload_dir = payloads / strategy
    write_jsonl(payload_dir / "source_records.jsonl", [{"source_id": source}])
    write_jsonl(payload_dir / "chunk_records.jsonl", [chunk_record])
    write_jsonl(payload_dir / "entity_records.jsonl", [])
    write_jsonl(payload_dir / "mention_records.jsonl", [])
    write_jsonl(payload_dir / "relation_records.jsonl", [])
    write_jsonl(payload_dir / "canonical_relation_records.jsonl", [])
    write_json(payload_dir / "summary.json", payload_summary)
    write_json(
        reports / f"{strategy}_graph_write_summary.json",
        {
            "chunk_count": 1,
            "completed": True,
            "db_write_counts": {
                "neo4j": {"canonical_relations": 0, "chunks": 1, "relations": 0},
                "supabase_source_chunks": 1,
            },
            "dry_run": False,
            "relation_drop_counts": {},
        },
    )
    write_json(imports / f"import_graph_{strategy}.json", {"chunk_count": 1, "dry_run": True})

    write_json(
        reports / f"embed_{source}_{strategy}.json",
        {
            "chunk_strategy_id": strategy,
            "completed": True,
            "embedded_chunk_type_counts": {"chunk": 1},
            "embedding_backend": "local",
            "embedding_slot": "bge_m3",
            "expected_dim": 1024,
            "parent_skipped_count": 0,
            "selected_chunks": 1,
            "source_id": source,
            "vector_index_name": "chunkVectorBgeM3",
        },
    )
    retrieval_hit = {
        "chunk_hash": "hash-1",
        "chunk_id": chunk_record["chunk_id"],
        "chunk_strategy_id": strategy,
        "chunk_type": "chunk",
        "domain": "TUVI",
        "source_id": source,
    }
    write_json(
        reports / f"retrieval_{source}_{strategy}.json",
        {
            "chunk_strategy_id": strategy,
            "dense_hits": [retrieval_hit],
            "diagnostics": {
                "dense_hit_count": 1,
                "embedding_slot": "bge_m3",
                "parent_expansion": {},
                "sparse_hit_count": 1,
            },
            "embedding_slot": "bge_m3",
            "source_id": source,
            "sparse_hits": [retrieval_hit],
        },
    )
    embedding_record = {
        **chunk_record,
        "embedding": vector,
        "embedding_dim": 1024,
        "embedding_slot": "bge_m3",
    }
    write_jsonl(embeddings / strategy / f"{source}_{strategy}_embeddings.jsonl", [embedding_record])
    write_json(
        reports / "offline_embedding" / f"embed_{source}_{strategy}.json",
        {"completed": True, "embedding_slot": "bge_m3", "update_count": 1},
    )
    write_json(
        reports / "offline_embedding" / f"retrieval_{source}_{strategy}.json",
        {"diagnostics": {"dense_hit_count": 1, "mode": "offline_artifact"}},
    )
    write_json(
        imports / f"import_embedding_{source}_{strategy}.json",
        {"dry_run": True, "embedding_slot": "bge_m3", "update_count": 1},
    )

    result = audit.run(
        [
            "--sources",
            source,
            "--strategies",
            strategy,
            "--chunks-dir",
            str(chunks),
            "--regen-chunks-dir",
            str(regen),
            "--reports-dir",
            str(reports),
            "--entities-dir",
            str(entities),
            "--payloads-dir",
            str(payloads),
            "--embeddings-dir",
            str(embeddings),
            "--import-checks-dir",
            str(imports),
            "--skip-baseline-counts",
            "--output",
            str(reports / "audit.json"),
        ]
    )

    assert result["completed"] is True
    assert result["issues"] == []
    assert result["chunk_evidence"][strategy]["regeneration_comparison"]["completed"] is True


def test_w3_ingest_07_audit_reports_missing_embedding_artifact() -> None:
    work_dir = ROOT_DIR / "pytest-cache-files-w3-ingest-07-audit" / "missing-artifact"
    result = audit.run(
        [
            "--sources",
            "TVGM",
            "--strategies",
            "chunk_fixed_512",
            "--chunks-dir",
            str(work_dir / "chunks"),
            "--reports-dir",
            str(work_dir / "reports"),
            "--entities-dir",
            str(work_dir / "entities"),
            "--payloads-dir",
            str(work_dir / "payloads"),
            "--embeddings-dir",
            str(work_dir / "embeddings"),
            "--import-checks-dir",
            str(work_dir / "reports" / "import_checks"),
            "--skip-baseline-counts",
            "--output",
            str(work_dir / "reports" / "audit.json"),
        ]
    )

    assert result["completed"] is False
    assert any(issue["check"] == "offline_embedding" for issue in result["issues"])
