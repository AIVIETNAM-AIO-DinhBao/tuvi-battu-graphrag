import json
import sys
from pathlib import Path

import pytest


ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR / "scripts"))

import embed_chunks  # noqa: E402
import import_embedding_artifacts as embedding_importer  # noqa: E402
import import_graph_payload as graph_importer  # noqa: E402
import write_graph_provenance as writer  # noqa: E402


def smoke_dir(name: str) -> Path:
    path = ROOT_DIR / "pytest-cache-files-import-artifacts" / name
    path.mkdir(parents=True, exist_ok=True)
    return path


def test_import_graph_payload_dry_run_reads_portable_payload_dir() -> None:
    work_dir = smoke_dir("graph-payload")
    payload_dir = work_dir / "payload"
    payload = {
        "source_records": [{"source_id": "TVGM", "source_name": "Tu Vi", "source_type": "book", "domain": "TUVI"}],
        "chunk_records": [
            {
                "chunk_hash": "hash-1",
                "chunk_id": "chunk-1",
                "chunk_strategy_id": "chunk_fixed_512",
                "chunk_type": "child",
                "parent_id": None,
                "section_id": "SEC01",
                "text": "Thiên Mã tại Quan Lộc.",
                "chunk_text": "Thiên Mã tại Quan Lộc.",
                "domain": "TUVI",
                "source_id": "TVGM",
                "source_name": "Tu Vi",
                "source_page": 7,
                "char_start": 0,
                "char_end": 22,
                "token_count": 5,
                "provenance_json": "{}",
                "metadata_json": "{}",
                "provenance": {},
                "metadata": {},
            }
        ],
        "entity_records": [],
        "mention_records": [],
        "relation_records": [],
        "canonical_relation_records": [],
        "summary": {"chunk_count": 1, "entity_count": 0, "total_relation_count": 0},
    }
    writer.write_payload_output_dir(payload_dir, payload)

    summary = graph_importer.run(["--payload-input-dir", str(payload_dir), "--dry-run"])

    assert summary["dry_run"] is True
    assert summary["payload_input_dir"] == str(payload_dir)
    assert summary["chunk_count"] == 1
    assert summary["db_write_counts"] == {}


def test_import_embedding_artifacts_dry_run_validates_bge_slot() -> None:
    work_dir = smoke_dir("embedding-artifacts")
    path = work_dir / "TVGM_chunk_fixed_512_embeddings.jsonl"
    record = {
        "chunk_hash": "hash-1",
        "chunk_id": "chunk-1",
        "chunk_strategy_id": "chunk_fixed_512",
        "chunk_type": "child",
        "embedding": embed_chunks.mock_embedding("chunk-1", expected_dim=1024),
        "embedding_dim": 1024,
        "embedding_model": "BAAI/bge-m3",
        "embedding_slot": "bge_m3",
        "embedding_text_hash": "hash",
        "embedded_at": "2026-01-01T00:00:00Z",
        "keywords": "Thiên Mã",
        "parent_id": None,
        "retrieval_unit": True,
        "source_id": "TVGM",
        "title": "SEC01",
    }
    path.write_text(json.dumps(record, ensure_ascii=False) + "\n", encoding="utf-8")

    summary = embedding_importer.run(["--input", str(path), "--dry-run", "--embedding-slot", "bge_m3"])

    assert summary["dry_run"] is True
    assert summary["embedding_slot"] == "bge_m3"
    assert summary["embedding_property"] == "embedding_bge_m3"
    assert summary["update_count"] == 1


def test_import_embedding_artifacts_rejects_slot_mismatch() -> None:
    work_dir = smoke_dir("embedding-slot-mismatch")
    path = work_dir / "embeddings.jsonl"
    record = {
        "chunk_hash": "hash-1",
        "chunk_id": "chunk-1",
        "chunk_strategy_id": "chunk_fixed_512",
        "embedding": embed_chunks.mock_embedding("chunk-1", expected_dim=768),
        "embedding_dim": 768,
        "embedding_model": "gemini-embedding-2",
        "embedding_slot": "gemini",
    }
    path.write_text(json.dumps(record, ensure_ascii=False) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="does not match requested slot"):
        embedding_importer.run(["--input", str(path), "--dry-run", "--embedding-slot", "bge_m3"])
