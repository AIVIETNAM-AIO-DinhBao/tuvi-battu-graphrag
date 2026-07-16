from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from app.rag.evaluation_checkpoint import (
    CHECKPOINT_SCHEMA_VERSION,
    CheckpointError,
    CheckpointRunMismatchError,
    EvaluationCheckpointStore,
    artifact_provenance,
    atomic_write_json,
    build_evaluation_provenance,
    build_run_identity,
    sha256_file,
    sha256_json,
    validate_run_identity,
)


CONFIG_A_HASH = "a" * 64
CONFIG_B_HASH = "b" * 64


def make_dataset(tmp_path: Path, content: str = '{"id":"TVQA-001"}\n') -> Path:
    path = tmp_path / "dataset.jsonl"
    path.write_text(content, encoding="utf-8")
    return path


def make_identity(dataset_path: Path, **overrides: object) -> dict:
    kwargs = {
        "manifest_name": "w8-final",
        "dataset_path": dataset_path,
        "config_hashes": {"production": CONFIG_A_HASH},
        "judge_backend": "gemini",
        "judge_model": "gemini-3.1-flash-lite-preview",
        "generation_models": {"production": "gemini-3.1-flash-lite-preview"},
        "manifest_sha256": "c" * 64,
        "git_sha": "d5c4f734e5acb42679cb9e0755bbd935a4e9fa7f",
        "git_dirty": False,
        "evaluator_sha256": "d" * 64,
        "selected_item_ids": ["TVQA-001", "TVQA-002"],
    }
    kwargs.update(overrides)
    return build_run_identity(**kwargs)


def test_sha256_helpers_use_file_bytes_and_canonical_json(tmp_path: Path) -> None:
    dataset = tmp_path / "dataset.jsonl"
    raw_content = "Tử Vi\r\n".encode("utf-8")
    dataset.write_bytes(raw_content)

    assert sha256_file(dataset) == hashlib.sha256(raw_content).hexdigest()
    assert sha256_json({"b": 2, "a": "Tử Vi"}) == sha256_json({"a": "Tử Vi", "b": 2})


def test_build_run_identity_captures_reproducibility_inputs(tmp_path: Path) -> None:
    dataset = make_dataset(tmp_path)

    identity = make_identity(dataset)

    assert identity["schema_version"] == 1
    assert identity["manifest_name"] == "w8-final"
    assert identity["dataset_sha256"] == sha256_file(dataset)
    assert identity["config_hashes"] == {"production": CONFIG_A_HASH}
    assert identity["judge_backend"] == "gemini"
    assert identity["judge_model"] == "gemini-3.1-flash-lite-preview"
    assert identity["generation_models"] == {"production": "gemini-3.1-flash-lite-preview"}
    assert identity["manifest_sha256"] == "c" * 64
    assert identity["git_sha"] == "d5c4f734e5acb42679cb9e0755bbd935a4e9fa7f"
    assert identity["git_dirty"] is False
    assert identity["evaluator_sha256"] == "d" * 64
    assert identity["selected_item_ids"] == ["TVQA-001", "TVQA-002"]
    assert len(identity["identity_sha256"]) == 64
    validate_run_identity(identity, dict(identity))


@pytest.mark.parametrize(
    "overrides",
    [
        {"manifest_name": "another-manifest"},
        {"config_hashes": {"production": CONFIG_B_HASH}},
        {"judge_backend": "static"},
        {"judge_model": "another-judge-model"},
        {"manifest_sha256": "e" * 64},
        {"evaluator_sha256": "f" * 64},
        {"selected_item_ids": ["TVQA-001"]},
    ],
)
def test_validate_run_identity_rejects_changed_run_inputs(tmp_path: Path, overrides: dict) -> None:
    dataset = make_dataset(tmp_path)
    original = make_identity(dataset)
    changed = make_identity(dataset, **overrides)

    with pytest.raises(CheckpointRunMismatchError, match="does not match"):
        validate_run_identity(original, changed)


def test_validate_run_identity_rejects_tampered_identity_digest(tmp_path: Path) -> None:
    identity = make_identity(make_dataset(tmp_path))
    identity["manifest_name"] = "tampered-without-rehashing"

    with pytest.raises(CheckpointError, match="integrity"):
        validate_run_identity(identity, identity)


def test_atomic_write_json_replaces_document_and_leaves_no_temp_files(tmp_path: Path) -> None:
    destination = tmp_path / "nested" / "checkpoint.json"
    atomic_write_json(destination, {"old": True})
    atomic_write_json(destination, {"answer": "Tử Vi", "items": [1, 2]})

    assert json.loads(destination.read_text(encoding="utf-8")) == {
        "answer": "Tử Vi",
        "items": [1, 2],
    }
    assert list(destination.parent.glob(f".{destination.name}.*.tmp")) == []


def test_atomic_write_json_preserves_previous_file_when_serialization_fails(tmp_path: Path) -> None:
    destination = tmp_path / "checkpoint.json"
    atomic_write_json(destination, {"complete": True})

    with pytest.raises(TypeError):
        atomic_write_json(destination, {"not_json": object()})

    assert json.loads(destination.read_text(encoding="utf-8")) == {"complete": True}
    assert list(tmp_path.glob(f".{destination.name}.*.tmp")) == []


def test_checkpoint_store_persists_and_resumes_item_results(tmp_path: Path) -> None:
    dataset = make_dataset(tmp_path)
    identity = make_identity(dataset)
    checkpoint_path = tmp_path / "checkpoint.json"
    timestamps = iter(["created", "initial", "first-save", "second-save"])
    store = EvaluationCheckpointStore(checkpoint_path, identity, clock=lambda: next(timestamps))

    empty = store.load()
    assert empty["schema_version"] == CHECKPOINT_SCHEMA_VERSION
    assert empty["configs"] == {}

    store.record_item("production", "TVQA-002", {"item_id": "TVQA-002", "score": 0.8})
    store.record_item("production", "TVQA-001", {"item_id": "TVQA-001", "score": 0.9})

    resumed = EvaluationCheckpointStore(checkpoint_path, identity)
    resumed.load()
    assert resumed.completed_item_ids("production") == {"TVQA-001", "TVQA-002"}
    assert resumed.has_item("production", "TVQA-001") is True
    assert resumed.item_results(
        "production", item_ids=["TVQA-001", "TVQA-002"]
    ) == [
        {"item_id": "TVQA-001", "score": 0.9},
        {"item_id": "TVQA-002", "score": 0.8},
    ]


def test_checkpoint_store_rejects_resume_for_different_identity(tmp_path: Path) -> None:
    dataset = make_dataset(tmp_path)
    identity = make_identity(dataset)
    checkpoint_path = tmp_path / "checkpoint.json"
    store = EvaluationCheckpointStore(checkpoint_path, identity)
    store.record_item("production", "TVQA-001", {"item_id": "TVQA-001"})

    incompatible = make_identity(dataset, judge_backend="static")
    with pytest.raises(CheckpointRunMismatchError, match="judge_backend"):
        EvaluationCheckpointStore(checkpoint_path, incompatible).load()


def test_checkpoint_store_rejects_corrupt_schema_and_unknown_config(tmp_path: Path) -> None:
    dataset = make_dataset(tmp_path)
    identity = make_identity(dataset)
    checkpoint_path = tmp_path / "checkpoint.json"
    atomic_write_json(
        checkpoint_path,
        {
            "schema_version": 999,
            "run_identity": identity,
            "configs": {},
        },
    )

    with pytest.raises(CheckpointError, match="schema_version"):
        EvaluationCheckpointStore(checkpoint_path, identity).load()

    checkpoint_path.unlink()
    store = EvaluationCheckpointStore(checkpoint_path, identity)
    with pytest.raises(CheckpointError, match="not present"):
        store.record_item("unknown", "TVQA-001", {})


def test_artifact_and_evaluation_provenance_include_sha256(tmp_path: Path) -> None:
    dataset = make_dataset(tmp_path)
    identity = make_identity(dataset)

    artifact = artifact_provenance(dataset)
    provenance = build_evaluation_provenance(
        run_identity=identity,
        artifacts={"dataset": dataset},
        generated_at="2026-07-17T00:00:00Z",
    )

    assert artifact == {
        "path": dataset.as_posix(),
        "sha256": sha256_file(dataset),
        "size_bytes": dataset.stat().st_size,
    }
    assert provenance["generated_at"] == "2026-07-17T00:00:00Z"
    assert provenance["run_identity"] == identity
    assert provenance["artifacts"]["dataset"] == artifact