from __future__ import annotations

import json
import os
import re
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .common import (
    PREDICTION_SCHEMA_VERSION,
    append_jsonl,
    atomic_write_json,
    iter_json_records,
    resolve_directory,
    sha256_file,
    stable_pair_id,
    write_jsonl_atomic,
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "gemini"


def _load_latest_records(path: Path) -> dict[str, dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    if not path.exists():
        return latest
    for record in iter_json_records(path):
        pair_id = str(record.get("pair_id") or "")
        if pair_id:
            latest[pair_id] = record
    return latest


def run_gemini_model_only(config: dict[str, Any]) -> dict[str, Any]:
    """Generate model-only predictions through Gemini API with key rotation and resume."""
    repo_root = Path(config["repo_root"]).expanduser().resolve()
    bundle_dir = resolve_directory(config.get("bundle_dir"), marker="bundle_manifest.json")
    output_root = Path(config["output_root"]).expanduser().resolve()
    model_id = str(config.get("model_id") or "gemini-3.1-flash-lite-preview")
    model_key = str(config.get("model_key") or "gemini31_flash_lite")
    temperature = float(config.get("temperature", 0.0))
    max_output_tokens = int(config.get("max_output_tokens", 1024))
    request_timeout_seconds = int(config.get("request_timeout_seconds", 20))
    retry_attempts = int(config.get("retry_attempts", 3))
    retry_base_seconds = float(config.get("retry_base_seconds", 2.0))
    retry_errors = bool(config.get("retry_errors", True))
    initial_key_offset = int(config.get("initial_key_offset", 0))
    minimum_key_count = int(config.get("minimum_key_count", 1))
    limit = config.get("limit")

    manifest = json.loads((bundle_dir / "bundle_manifest.json").read_text(encoding="utf-8"))
    if manifest.get("bundle_type") != "model_only_question_plus_raw_chart":
        raise RuntimeError(f"Expected model-only bundle, found {manifest.get('bundle_type')!r}")
    if manifest["files"]["cases"]["sha256"] != sha256_file(bundle_dir / "cases.jsonl"):
        raise RuntimeError("cases.jsonl checksum does not match bundle_manifest.json")

    try:
        from dotenv import load_dotenv

        load_dotenv(repo_root / ".env", override=False)
    except Exception:
        pass
    backend_dir = repo_root / "backend"
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))

    try:
        import google.generativeai as genai
    except Exception as exc:
        raise RuntimeError(
            "Missing google-generativeai. Install requirements-online.txt in the active notebook kernel."
        ) from exc
    from app.rag.gemini_keys import load_runtime_gemini_api_keys

    api_keys = load_runtime_gemini_api_keys()
    if len(api_keys) < minimum_key_count:
        raise RuntimeError(
            f"Found {len(api_keys)} Gemini key(s), but minimum_key_count={minimum_key_count}. "
            "Set GEMINI_API_KEYS, GEMINI_API_KEY, or numbered GEMINI_API_KEY_N variables."
        )

    cases = [
        row
        for row in iter_json_records(bundle_dir / "cases.jsonl")
        if row.get("status") == "completed"
        and row.get("suite") == "model_only"
        and row.get("config_key") == "model_only::question_chart_direct"
    ]
    cases.sort(key=lambda row: str(row["pair_id"]))
    if limit is not None:
        cases = cases[: int(limit)]
    if not cases:
        raise RuntimeError("No model-only cases found")

    output_dir = output_root / model_key / "question-chart-direct" / "shard_00_of_01"
    output_dir.mkdir(parents=True, exist_ok=True)
    predictions_path = output_dir / "predictions_shard_00.jsonl"
    latest = _load_latest_records(predictions_path)
    pending = [
        row
        for row in cases
        if row["pair_id"] not in latest
        or (latest[row["pair_id"]].get("status") != "completed" and retry_errors)
    ]

    key_labels = [f"key_{index + 1}" for index in range(len(api_keys))]
    usage_counts = {label: 0 for label in key_labels}
    success_counts = {label: 0 for label in key_labels}
    failure_counts = {label: 0 for label in key_labels}
    request_counter = 0
    started_at = utc_now()

    for case_index, case in enumerate(pending, start=1):
        pair_id = str(case["pair_id"])
        pair_started = time.perf_counter()
        answer = ""
        used_label: str | None = None
        attempt_errors: list[str] = []
        try:
            for attempt in range(1, retry_attempts + 1):
                start = (initial_key_offset + request_counter) % len(api_keys)
                request_counter += 1
                for step in range(len(api_keys)):
                    key_index = (start + step) % len(api_keys)
                    label = key_labels[key_index]
                    usage_counts[label] += 1
                    request_started = time.perf_counter()
                    try:
                        genai.configure(api_key=api_keys[key_index])
                        model = genai.GenerativeModel(model_id)
                        response = model.generate_content(
                            str(case["prompt"]),
                            generation_config={
                                "temperature": temperature,
                                "max_output_tokens": max_output_tokens,
                            },
                            request_options={"timeout": request_timeout_seconds},
                        )
                        answer = str(getattr(response, "text", "") or "").strip()
                        if not answer:
                            raise RuntimeError("Gemini returned an empty answer")
                        generation_ms = round((time.perf_counter() - request_started) * 1000, 2)
                        success_counts[label] += 1
                        used_label = label
                        break
                    except Exception as exc:
                        failure_counts[label] += 1
                        attempt_errors.append(type(exc).__name__)
                if answer:
                    break
                if attempt < retry_attempts:
                    time.sleep(retry_base_seconds * (2 ** (attempt - 1)))
            if not answer:
                raise RuntimeError(
                    f"Gemini generation failed after {retry_attempts} attempt cycle(s); "
                    f"error_types={attempt_errors}"
                )
            prediction_id = stable_pair_id(pair_id, model_id, "provider-managed", "api", "temperature-0")
            record = {
                "schema_version": PREDICTION_SCHEMA_VERSION,
                "status": "completed",
                "prediction_id": prediction_id,
                "pair_id": pair_id,
                "suite": case["suite"],
                "config_key": case["config_key"],
                "item_id": case["item_id"],
                "prompt_sha256": case["prompt_sha256"],
                "model_key": model_key,
                "model_id": model_id,
                "model_revision": "provider-managed",
                "loader": "gemini_api",
                "quantization": "api",
                "compute_dtype": None,
                "seed": None,
                "do_sample": False,
                "temperature": temperature,
                "input_tokens": None,
                "output_tokens": None,
                "generation_latency_ms": generation_ms,
                "total_pair_latency_ms": round((time.perf_counter() - pair_started) * 1000, 2),
                "answer": answer,
                "key_label": used_label,
                "completed_at": utc_now(),
            }
        except Exception as exc:
            record = {
                "schema_version": PREDICTION_SCHEMA_VERSION,
                "status": "failed",
                "pair_id": pair_id,
                "suite": case["suite"],
                "config_key": case["config_key"],
                "item_id": case["item_id"],
                "prompt_sha256": case["prompt_sha256"],
                "model_key": model_key,
                "model_id": model_id,
                "model_revision": "provider-managed",
                "loader": "gemini_api",
                "quantization": "api",
                "error_type": type(exc).__name__,
                "error": str(exc)[:2000],
                "failed_at": utc_now(),
            }
        append_jsonl(predictions_path, record)
        latest[pair_id] = record
        if case_index % 10 == 0 or case_index == len(pending):
            print(
                f"model={model_key} processed={case_index}/{len(pending)} "
                f"pair_id={pair_id} status={record['status']}"
            )

    compacted = [latest[row["pair_id"]] for row in cases if row["pair_id"] in latest]
    write_jsonl_atomic(predictions_path, compacted)
    completed = sum(row.get("status") == "completed" for row in compacted)
    failed = sum(row.get("status") == "failed" for row in compacted)
    summary = {
        "schema_version": PREDICTION_SCHEMA_VERSION,
        "started_at": started_at,
        "completed_at": utc_now(),
        "shard_id": 0,
        "num_shards": 1,
        "selected_suites": ["model_only"],
        "selected_config_keys": ["model_only::question_chart_direct"],
        "assigned_pair_count": len(cases),
        "completed_pair_count": completed,
        "failed_pair_count": failed,
        "is_complete": completed == len(cases) and failed == 0,
        "model_key": model_key,
        "model_id": model_id,
        "model_revision": "provider-managed",
        "loader": "gemini_api",
        "quantization": "api",
        "temperature": temperature,
        "max_output_tokens": max_output_tokens,
        "bundle_cases_sha256": manifest["files"]["cases"]["sha256"],
        "key_rotation": {
            "key_count": len(api_keys),
            "initial_offset": initial_key_offset,
            "usage_counts": usage_counts,
            "success_counts": success_counts,
            "failure_counts": failure_counts,
        },
        "predictions_file": predictions_path.name,
        "predictions_sha256": sha256_file(predictions_path),
    }
    atomic_write_json(output_dir / "shard_summary.json", summary)
    archive_base = output_root / f"local_llm_predictions_{model_key}_question-chart-direct_00_of_01"
    archive_path = Path(shutil.make_archive(str(archive_base), "zip", root_dir=output_dir))
    summary["archive_path"] = str(archive_path)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary
