"""Durable checkpoints and provenance helpers for evaluation runs.

This module deliberately has no dependency on the evaluation runner.  Keeping
the persistence boundary small makes it possible to test resume behaviour
without loading model clients or database adapters.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from collections.abc import Callable, Iterable, Mapping
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


CHECKPOINT_SCHEMA_VERSION = 1
RUN_IDENTITY_SCHEMA_VERSION = 1
_SHA256_HEX_LENGTH = 64


class CheckpointError(ValueError):
    """Base error for invalid or incompatible checkpoint data."""


class CheckpointRunMismatchError(CheckpointError):
    """Raised when a checkpoint belongs to a different evaluation run."""


# Shorter alias for callers which do not include the storage context in the
# exception name.
RunIdentityMismatchError = CheckpointRunMismatchError


def utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def sha256_bytes(content: bytes) -> str:
    """Return the lowercase SHA256 digest for *content*."""

    return hashlib.sha256(content).hexdigest()


def sha256_file(path: Path | str, *, chunk_size: int = 1024 * 1024) -> str:
    """Hash a file without loading it entirely into memory."""

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


# ``file_sha256`` reads naturally at call sites and is retained as an alias.
file_sha256 = sha256_file


def canonical_json_bytes(payload: Any) -> bytes:
    """Serialize JSON data deterministically for hashing."""

    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def sha256_json(payload: Any) -> str:
    """Return a stable SHA256 digest of a JSON-compatible value."""

    return sha256_bytes(canonical_json_bytes(payload))


canonical_json_sha256 = sha256_json


def atomic_write_json(path: Path | str, payload: Any) -> None:
    """Write JSON through a same-directory temporary file and ``os.replace``.

    The temporary file is flushed and synced before replacement, so readers
    see either the previous complete document or the new complete document.
    A failed serialization or replacement leaves no temporary file behind.
    """

    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        descriptor, raw_temporary_path = tempfile.mkstemp(
            dir=destination.parent,
            prefix=f".{destination.name}.",
            suffix=".tmp",
        )
        temporary_path = Path(raw_temporary_path)
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(
                payload,
                handle,
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
                allow_nan=False,
            )
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, destination)
        temporary_path = None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def load_json_object(path: Path | str) -> dict[str, Any]:
    """Load a JSON object, rejecting arrays and scalar roots."""

    source = Path(path)
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CheckpointError(f"Invalid JSON in checkpoint {source}: {exc}") from exc
    if not isinstance(payload, dict):
        raise CheckpointError(f"Checkpoint must contain a JSON object: {source}")
    return payload


def _require_non_empty_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string.")
    return value.strip()


def _validate_sha256(value: Any, field: str) -> str:
    digest = _require_non_empty_string(value, field).lower()
    if len(digest) != _SHA256_HEX_LENGTH or any(character not in "0123456789abcdef" for character in digest):
        raise ValueError(f"{field} must be a 64-character SHA256 hex digest.")
    return digest


def _identity_content(identity: Mapping[str, Any]) -> dict[str, Any]:
    return {key: deepcopy(value) for key, value in identity.items() if key != "identity_sha256"}


def build_run_identity(
    *,
    manifest_name: str,
    dataset_path: Path | str,
    config_hashes: Mapping[str, str],
    judge_backend: str,
    judge_model: str | None = None,
    generation_models: Mapping[str, str] | None = None,
    manifest_sha256: str | None = None,
    git_sha: str | None = None,
    git_dirty: bool | None = None,
    evaluator_sha256: str | None = None,
    selected_item_ids: Iterable[str] | None = None,
) -> dict[str, Any]:
    """Build a content-addressed identity for an evaluation run.

    Dataset identity is based on file bytes rather than timestamps.  Config
    names are part of the identity because they are also the checkpoint
    namespace, while each value must be the config's full SHA256 hash.
    ``selected_item_ids`` is optional, but when supplied its order is retained:
    changing the selected subset or its execution order starts a different run.
    """

    manifest = _require_non_empty_string(manifest_name, "manifest_name")
    judge = _require_non_empty_string(judge_backend, "judge_backend")
    dataset = Path(dataset_path)
    if not config_hashes:
        raise ValueError("config_hashes must contain at least one config.")

    normalized_hashes: dict[str, str] = {}
    for raw_name, raw_digest in config_hashes.items():
        name = _require_non_empty_string(raw_name, "config name")
        if name in normalized_hashes:
            raise ValueError(f"Duplicate config name after normalization: {name}")
        normalized_hashes[name] = _validate_sha256(raw_digest, f"config_hashes[{name!r}]")

    normalized_ids: list[str] | None = None
    if selected_item_ids is not None:
        normalized_ids = []
        seen: set[str] = set()
        for raw_item_id in selected_item_ids:
            item_id = _require_non_empty_string(raw_item_id, "selected item id")
            if item_id in seen:
                raise ValueError(f"selected_item_ids contains duplicate item id: {item_id}")
            seen.add(item_id)
            normalized_ids.append(item_id)

    content: dict[str, Any] = {
        "schema_version": RUN_IDENTITY_SCHEMA_VERSION,
        "manifest_name": manifest,
        "dataset_sha256": sha256_file(dataset),
        "config_hashes": dict(sorted(normalized_hashes.items())),
        "judge_backend": judge,
    }
    if judge_model is not None:
        content["judge_model"] = _require_non_empty_string(judge_model, "judge_model")
    if generation_models is not None:
        normalized_generation_models: dict[str, str] = {}
        for raw_name, raw_model in generation_models.items():
            name = _require_non_empty_string(raw_name, "generation model config name")
            if name not in normalized_hashes:
                raise ValueError(f"Generation model config {name!r} is not present in config_hashes.")
            normalized_generation_models[name] = _require_non_empty_string(
                raw_model, f"generation_models[{name!r}]"
            )
        content["generation_models"] = dict(sorted(normalized_generation_models.items()))
    if manifest_sha256 is not None:
        content["manifest_sha256"] = _validate_sha256(manifest_sha256, "manifest_sha256")
    if git_sha is not None:
        content["git_sha"] = _require_non_empty_string(git_sha, "git_sha")
    if git_dirty is not None:
        if not isinstance(git_dirty, bool):
            raise ValueError("git_dirty must be a boolean.")
        content["git_dirty"] = git_dirty
    if evaluator_sha256 is not None:
        content["evaluator_sha256"] = _validate_sha256(evaluator_sha256, "evaluator_sha256")
    if normalized_ids is not None:
        content["selected_item_ids"] = normalized_ids
    return {**content, "identity_sha256": sha256_json(content)}


build_evaluation_run_identity = build_run_identity


def _validated_identity(identity: Mapping[str, Any], *, label: str) -> dict[str, Any]:
    if not isinstance(identity, Mapping):
        raise CheckpointError(f"{label} run identity must be a JSON object.")
    content = _identity_content(identity)
    if content.get("schema_version") != RUN_IDENTITY_SCHEMA_VERSION:
        raise CheckpointError(
            f"{label} run identity has unsupported schema_version: {content.get('schema_version')!r}."
        )
    for field in ("manifest_name", "judge_backend"):
        try:
            _require_non_empty_string(content.get(field), field)
        except ValueError as exc:
            raise CheckpointError(f"Invalid {label} run identity: {exc}") from exc
    if "judge_model" in content:
        try:
            _require_non_empty_string(content.get("judge_model"), "judge_model")
        except ValueError as exc:
            raise CheckpointError(f"Invalid {label} run identity: {exc}") from exc
    for field in ("manifest_sha256", "evaluator_sha256"):
        if field in content:
            try:
                _validate_sha256(content.get(field), field)
            except ValueError as exc:
                raise CheckpointError(f"Invalid {label} run identity: {exc}") from exc
    if "git_sha" in content:
        try:
            _require_non_empty_string(content.get("git_sha"), "git_sha")
        except ValueError as exc:
            raise CheckpointError(f"Invalid {label} run identity: {exc}") from exc
    if "git_dirty" in content and not isinstance(content.get("git_dirty"), bool):
        raise CheckpointError(f"Invalid {label} run identity: git_dirty must be a boolean.")
    try:
        _validate_sha256(content.get("dataset_sha256"), "dataset_sha256")
    except ValueError as exc:
        raise CheckpointError(f"Invalid {label} run identity: {exc}") from exc

    config_hashes = content.get("config_hashes")
    if not isinstance(config_hashes, dict) or not config_hashes:
        raise CheckpointError(f"Invalid {label} run identity: config_hashes must be a non-empty object.")
    for name, digest in config_hashes.items():
        try:
            _require_non_empty_string(name, "config name")
            _validate_sha256(digest, f"config_hashes[{name!r}]")
        except ValueError as exc:
            raise CheckpointError(f"Invalid {label} run identity: {exc}") from exc

    generation_models = content.get("generation_models")
    if generation_models is not None:
        if not isinstance(generation_models, dict):
            raise CheckpointError(f"Invalid {label} run identity: generation_models must be an object.")
        for name, model in generation_models.items():
            try:
                normalized_name = _require_non_empty_string(name, "generation model config name")
                _require_non_empty_string(model, f"generation_models[{normalized_name!r}]")
            except ValueError as exc:
                raise CheckpointError(f"Invalid {label} run identity: {exc}") from exc
            if normalized_name not in config_hashes:
                raise CheckpointError(
                    f"Invalid {label} run identity: generation model config {normalized_name!r} "
                    "is not present in config_hashes."
                )

    item_ids = content.get("selected_item_ids")
    if item_ids is not None:
        if not isinstance(item_ids, list):
            raise CheckpointError(f"Invalid {label} run identity: selected_item_ids must be an array.")
        normalized_item_ids: list[str] = []
        for item_id in item_ids:
            try:
                normalized_item_ids.append(_require_non_empty_string(item_id, "selected item id"))
            except ValueError as exc:
                raise CheckpointError(f"Invalid {label} run identity: {exc}") from exc
        if len(normalized_item_ids) != len(set(normalized_item_ids)):
            raise CheckpointError(f"Invalid {label} run identity: selected_item_ids contains duplicates.")

    recorded_digest = identity.get("identity_sha256")
    try:
        normalized_digest = _validate_sha256(recorded_digest, "identity_sha256")
    except ValueError as exc:
        raise CheckpointError(f"Invalid {label} run identity: {exc}") from exc
    calculated_digest = sha256_json(content)
    if normalized_digest != calculated_digest:
        raise CheckpointError(f"{label} run identity failed SHA256 integrity validation.")
    return {**content, "identity_sha256": normalized_digest}


def validate_run_identity(actual: Mapping[str, Any], expected: Mapping[str, Any]) -> None:
    """Validate integrity and equality of stored and requested run identities."""

    stored = _validated_identity(actual, label="Stored")
    requested = _validated_identity(expected, label="Requested")
    if stored == requested:
        return

    differing_fields = sorted(
        key
        for key in set(stored) | set(requested)
        if stored.get(key) != requested.get(key)
    )
    fields = ", ".join(differing_fields)
    raise CheckpointRunMismatchError(
        f"Checkpoint run identity does not match the requested run (different fields: {fields})."
    )


validate_evaluation_run_identity = validate_run_identity


def artifact_provenance(path: Path | str) -> dict[str, Any]:
    """Return portable content provenance for one file."""

    source = Path(path)
    stat = source.stat()
    return {
        "path": source.as_posix(),
        "sha256": sha256_file(source),
        "size_bytes": stat.st_size,
    }


def build_evaluation_provenance(
    *,
    run_identity: Mapping[str, Any],
    artifacts: Mapping[str, Path | str] | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Build a report-friendly provenance block for a completed run."""

    validated_identity = _validated_identity(run_identity, label="Evaluation")
    artifact_records = {
        _require_non_empty_string(name, "artifact name"): artifact_provenance(path)
        for name, path in sorted((artifacts or {}).items())
    }
    return {
        "schema_version": CHECKPOINT_SCHEMA_VERSION,
        "generated_at": generated_at or utc_now(),
        "run_identity": validated_identity,
        "artifacts": artifact_records,
    }


class EvaluationCheckpointStore:
    """Atomic item-level checkpoint storage for one evaluation run."""

    def __init__(
        self,
        path: Path | str,
        run_identity: Mapping[str, Any],
        *,
        clock: Callable[[], str] = utc_now,
    ) -> None:
        self.path = Path(path)
        self.run_identity = _validated_identity(run_identity, label="Requested")
        self._clock = clock
        self._payload: dict[str, Any] | None = None

    def load(self) -> dict[str, Any]:
        """Load an existing checkpoint, or create an empty in-memory one."""

        if self.path.exists():
            payload = load_json_object(self.path)
            self._validate_checkpoint(payload)
        else:
            now = self._clock()
            payload = {
                "schema_version": CHECKPOINT_SCHEMA_VERSION,
                "run_identity": deepcopy(self.run_identity),
                "created_at": now,
                "updated_at": now,
                "configs": {},
            }
        self._payload = payload
        return deepcopy(payload)

    @property
    def payload(self) -> dict[str, Any]:
        if self._payload is None:
            self.load()
        assert self._payload is not None
        return deepcopy(self._payload)

    def _mutable_payload(self) -> dict[str, Any]:
        if self._payload is None:
            self.load()
        assert self._payload is not None
        return self._payload

    def _validate_checkpoint(self, payload: Mapping[str, Any]) -> None:
        if payload.get("schema_version") != CHECKPOINT_SCHEMA_VERSION:
            raise CheckpointError(
                f"Unsupported checkpoint schema_version: {payload.get('schema_version')!r}."
            )
        stored_identity = payload.get("run_identity")
        if not isinstance(stored_identity, dict):
            raise CheckpointError("Checkpoint run_identity must be a JSON object.")
        validate_run_identity(stored_identity, self.run_identity)
        configs = payload.get("configs")
        if not isinstance(configs, dict):
            raise CheckpointError("Checkpoint configs must be a JSON object.")
        for config_name, config_state in configs.items():
            if not isinstance(config_name, str) or not config_name:
                raise CheckpointError("Checkpoint config names must be non-empty strings.")
            if not isinstance(config_state, dict) or not isinstance(config_state.get("items"), dict):
                raise CheckpointError(f"Checkpoint config {config_name!r} must contain an items object.")

    def save(self) -> None:
        payload = self._mutable_payload()
        payload["updated_at"] = self._clock()
        atomic_write_json(self.path, payload)

    def record_item(self, config_name: str, item_id: str, result: Mapping[str, Any]) -> None:
        """Upsert one completed item and immediately persist it atomically."""

        name = _require_non_empty_string(config_name, "config_name")
        identifier = _require_non_empty_string(item_id, "item_id")
        if name not in self.run_identity["config_hashes"]:
            raise CheckpointError(f"Config {name!r} is not present in the run identity.")
        if not isinstance(result, Mapping):
            raise TypeError("result must be a mapping.")
        payload = self._mutable_payload()
        config_state = payload["configs"].setdefault(name, {"items": {}})
        config_state["items"][identifier] = deepcopy(dict(result))
        self.save()

    def has_item(self, config_name: str, item_id: str) -> bool:
        payload = self._mutable_payload()
        return item_id in ((payload["configs"].get(config_name) or {}).get("items") or {})

    def completed_item_ids(self, config_name: str) -> set[str]:
        payload = self._mutable_payload()
        return set(((payload["configs"].get(config_name) or {}).get("items") or {}).keys())

    def item_results(
        self,
        config_name: str,
        *,
        item_ids: Iterable[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Return copied results, optionally in a caller-supplied item order."""

        payload = self._mutable_payload()
        items = ((payload["configs"].get(config_name) or {}).get("items") or {})
        order = list(item_ids) if item_ids is not None else list(items)
        return [deepcopy(items[item_id]) for item_id in order if item_id in items]

    def remove(self) -> None:
        """Delete the persisted checkpoint and reset the in-memory state."""

        self.path.unlink(missing_ok=True)
        self._payload = None


# Convenient shorter spelling for integration code.
CheckpointStore = EvaluationCheckpointStore


def load_evaluation_checkpoint(
    path: Path | str,
    run_identity: Mapping[str, Any],
) -> EvaluationCheckpointStore:
    """Construct and eagerly validate an evaluation checkpoint store."""

    store = EvaluationCheckpointStore(path, run_identity)
    store.load()
    return store