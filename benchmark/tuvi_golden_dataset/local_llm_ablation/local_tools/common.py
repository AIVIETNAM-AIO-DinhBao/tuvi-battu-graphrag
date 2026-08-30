from __future__ import annotations

import hashlib
import json
import os
import platform
import tempfile
from pathlib import Path
from typing import Any, Iterable, Iterator


KIT_SCHEMA_VERSION = "local-llm-ablation-kit-v2"
BUNDLE_SCHEMA_VERSION = "model-agnostic-context-bundle-v2"
PREDICTION_SCHEMA_VERSION = "local-llm-predictions-v2"
JUDGE_SCHEMA_VERSION = "local-llm-gemini-judge-v2"


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=json_default)


def json_default(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, set):
        return sorted(value)
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_file(path: Path, *, block_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(block_size):
            digest.update(block)
    return digest.hexdigest()


def stable_pair_id(*parts: str) -> str:
    raw = "::".join(str(part) for part in parts)
    return sha256_text(raw)[:24]


def shard_for_pair(pair_id: str, num_shards: int) -> int:
    if num_shards < 1:
        raise ValueError("num_shards must be positive")
    return int(sha256_text(pair_id)[:16], 16) % num_shards


def iter_json_records(path: Path) -> Iterator[dict[str, Any]]:
    """Read JSONL, pretty multi-line concatenated JSON, or a JSON array."""
    content = path.read_text(encoding="utf-8")
    decoder = json.JSONDecoder()
    offset = 0
    while offset < len(content):
        while offset < len(content) and (content[offset].isspace() or content[offset] == ","):
            offset += 1
        if offset >= len(content):
            break
        if content[offset] == "[":
            payload = json.loads(content)
            if not isinstance(payload, list):
                raise ValueError(f"Expected JSON array in {path}")
            for record in payload:
                if isinstance(record, dict):
                    yield record
            return
        payload, next_offset = decoder.raw_decode(content, offset)
        if not isinstance(payload, dict):
            raise ValueError(f"Expected JSON object at character {offset} in {path}")
        yield payload
        offset = next_offset


def load_jsonl_map(path: Path, key: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    if not path.exists():
        return result
    for record in iter_json_records(path):
        value = str(record.get(key) or "")
        if not value:
            raise ValueError(f"Record in {path} is missing key {key}")
        if value in result and canonical_json(result[value]) != canonical_json(record):
            raise ValueError(f"Conflicting duplicate {key}={value} in {path}")
        result[value] = record
    return result


def append_jsonl(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True, default=json_default))
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())


def atomic_write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True, default=json_default)
            handle.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def write_jsonl_atomic(path: Path, records: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            for record in records:
                handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True, default=json_default))
                handle.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def resolve_directory(
    explicit: str | Path | None,
    *,
    marker: str,
    search_roots: Iterable[str | Path] = ("/kaggle/input", "."),
) -> Path:
    if explicit:
        candidate = Path(explicit).expanduser().resolve()
        if not (candidate / marker).exists():
            raise FileNotFoundError(f"{candidate} does not contain {marker}")
        return candidate
    matches: list[Path] = []
    for root in search_roots:
        root_path = Path(root)
        if not root_path.exists():
            continue
        matches.extend(path.parent.resolve() for path in root_path.rglob(marker))
    unique = sorted(set(matches))
    if len(unique) != 1:
        raise FileNotFoundError(f"Expected exactly one directory containing {marker}; found {unique}")
    return unique[0]


def environment_summary() -> dict[str, Any]:
    summary: dict[str, Any] = {
        "python": platform.python_version(),
        "platform": platform.platform(),
    }
    for package in ("torch", "transformers", "accelerate", "bitsandbytes", "safetensors"):
        try:
            module = __import__(package)
            summary[package] = str(getattr(module, "__version__", "unknown"))
        except Exception:
            summary[package] = None
    try:
        import torch

        summary["cuda_available"] = torch.cuda.is_available()
        summary["cuda_device_count"] = torch.cuda.device_count()
        summary["cuda_devices"] = [torch.cuda.get_device_name(index) for index in range(torch.cuda.device_count())]
    except Exception:
        summary["cuda_available"] = False
        summary["cuda_device_count"] = 0
        summary["cuda_devices"] = []
    return summary


def assert_no_secret_keys(payload: Any) -> None:
    forbidden = {"api_key", "gemini_api_key", "hf_token", "token", "password", "neo4j_password"}

    def walk(value: Any, path: str) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                normalized = str(key).strip().lower()
                if normalized in forbidden and child not in (None, "", False):
                    raise ValueError(f"Secret-like value found at {path}.{key}; never persist secrets in artifacts")
                walk(child, f"{path}.{key}")
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, f"{path}[{index}]")

    walk(payload, "root")
