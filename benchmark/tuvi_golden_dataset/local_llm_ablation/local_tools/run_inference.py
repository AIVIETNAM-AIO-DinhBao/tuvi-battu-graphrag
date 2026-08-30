from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .common import (
    PREDICTION_SCHEMA_VERSION,
    append_jsonl,
    atomic_write_json,
    environment_summary,
    iter_json_records,
    resolve_directory,
    sha256_file,
    stable_pair_id,
    shard_for_pair,
    write_jsonl_atomic,
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "model"


def _install_wheelhouse(asset_root: Path) -> None:
    wheelhouse = asset_root / "wheelhouse"
    wheels = sorted(wheelhouse.glob("*.whl")) if wheelhouse.exists() else []
    if not wheels:
        return
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--no-index", "--no-deps", *map(str, wheels)],
        check=True,
    )


def _load_latest_records(path: Path) -> dict[str, dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    if not path.exists():
        return latest
    for record in iter_json_records(path):
        pair_id = str(record.get("pair_id") or "")
        if not pair_id:
            continue
        previous = latest.get(pair_id)
        if previous is None or previous.get("status") != "completed" or record.get("status") == "completed":
            latest[pair_id] = record
    return latest


def _quantization_kwargs(
    quantization: str,
    torch: Any,
    BitsAndBytesConfig: Any,
    *,
    compute_dtype: Any,
) -> dict[str, Any]:
    if quantization == "4bit":
        return {
            "quantization_config": BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
                bnb_4bit_compute_dtype=compute_dtype,
            )
        }
    if quantization in {"fp16", "float16"}:
        return {"torch_dtype": torch.float16}
    raise ValueError("quantization must be '4bit' or 'fp16'")


def _load_runtime(model_dir: Path, loader: str, model_kwargs: dict[str, Any]) -> tuple[Any, Any, Any]:
    import transformers

    if loader == "causal_lm":
        tokenizer = transformers.AutoTokenizer.from_pretrained(
            model_dir, local_files_only=True, trust_remote_code=False
        )
        if tokenizer.pad_token_id is None:
            tokenizer.pad_token_id = tokenizer.eos_token_id
        model = transformers.AutoModelForCausalLM.from_pretrained(model_dir, **model_kwargs)

        def encode(prompt: str) -> tuple[dict[str, Any], Any]:
            rendered = tokenizer.apply_chat_template(
                [{"role": "user", "content": prompt}],
                tokenize=False,
                add_generation_prompt=True,
            )
            return tokenizer(rendered, return_tensors="pt", add_special_tokens=False), tokenizer

        return model, tokenizer, encode

    if loader == "gemma3_conditional":
        processor = transformers.AutoProcessor.from_pretrained(
            model_dir, local_files_only=True, trust_remote_code=False
        )
        model_class = getattr(transformers, "Gemma3ForConditionalGeneration", None)
        if model_class is None:
            model_class = getattr(transformers, "AutoModelForImageTextToText", None)
        if model_class is None:
            raise RuntimeError("Gemma 3 requires transformers with Gemma3ForConditionalGeneration support")
        model = model_class.from_pretrained(model_dir, **model_kwargs)
        tokenizer = processor.tokenizer
        if tokenizer.pad_token_id is None:
            tokenizer.pad_token_id = tokenizer.eos_token_id

        def encode(prompt: str) -> tuple[dict[str, Any], Any]:
            messages = [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}],
                }
            ]
            inputs = processor.apply_chat_template(
                messages,
                add_generation_prompt=True,
                tokenize=True,
                return_dict=True,
                return_tensors="pt",
            )
            return dict(inputs), tokenizer

        return model, tokenizer, encode

    raise ValueError(f"Unsupported loader={loader!r}")


def run_offline_inference(config: dict[str, Any]) -> dict[str, Any]:
    """Generate deterministic answers for a frozen, model-agnostic retrieval bundle."""
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["TOKENIZERS_PARALLELISM"] = "false"

    bundle_dir = resolve_directory(config.get("bundle_dir"), marker="bundle_manifest.json")
    asset_root = resolve_directory(config.get("model_asset_dir"), marker="asset_manifest.json")
    bundle_manifest = json.loads((bundle_dir / "bundle_manifest.json").read_text(encoding="utf-8"))
    asset_manifest = json.loads((asset_root / "asset_manifest.json").read_text(encoding="utf-8"))
    if bundle_manifest["files"]["cases"]["sha256"] != sha256_file(bundle_dir / "cases.jsonl"):
        raise RuntimeError("cases.jsonl checksum does not match bundle_manifest.json")
    expected_model_id = str(config.get("expected_model_id") or "").strip()
    if expected_model_id and asset_manifest.get("model_id") != expected_model_id:
        raise RuntimeError(
            f"Mounted model is {asset_manifest.get('model_id')!r}, expected {expected_model_id!r}"
        )
    model_dir = asset_root / str(asset_manifest.get("model_subdir") or "model")
    if bool(config.get("install_wheelhouse", False)):
        _install_wheelhouse(asset_root)

    import torch
    from transformers import BitsAndBytesConfig, set_seed

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA GPU is required for the official inference run")

    shard_id = int(config.get("shard_id", 0))
    num_shards = int(config.get("num_shards", 1))
    if shard_id < 0 or shard_id >= num_shards:
        raise ValueError(f"shard_id must be in [0, {num_shards - 1}]")
    selected_suites = {str(value) for value in config.get("suites") or []}
    selected_config_keys = {str(value) for value in config.get("selected_config_keys") or []}
    limit = config.get("limit")
    seed = int(config.get("seed", 42))
    max_new_tokens = int(config.get("max_new_tokens", 1024))
    max_input_tokens = int(config.get("max_input_tokens", 24576))
    quantization = str(config.get("quantization") or "4bit").lower()
    retry_errors = bool(config.get("retry_errors", True))
    model_id = str(asset_manifest["model_id"])
    model_key = str(asset_manifest.get("model_key") or safe_slug(model_id))
    loader = str(asset_manifest.get("loader") or "causal_lm")
    # Gemma 3 is released in BF16 and can overflow/produce NaNs with FP16.
    # Qwen keeps the FP16 path used by the already validated run.
    compute_dtype = torch.bfloat16 if loader == "gemma3_conditional" else torch.float16
    compute_dtype_name = "bfloat16" if compute_dtype == torch.bfloat16 else "float16"
    selection_slug = (
        safe_slug(next(iter(selected_config_keys)).split("::")[-1])
        if len(selected_config_keys) == 1
        else "all-configs"
    )
    output_root = Path(config.get("output_root") or "/kaggle/working/local_llm_ablation").resolve()
    output_dir = output_root / model_key / selection_slug / f"shard_{shard_id:02d}_of_{num_shards:02d}"
    output_dir.mkdir(parents=True, exist_ok=True)
    predictions_path = output_dir / f"predictions_shard_{shard_id:02d}.jsonl"

    cases = [record for record in iter_json_records(bundle_dir / "cases.jsonl") if record.get("status") == "completed"]
    if selected_suites:
        cases = [record for record in cases if str(record.get("suite")) in selected_suites]
    if selected_config_keys:
        cases = [record for record in cases if str(record.get("config_key")) in selected_config_keys]
    assigned = [record for record in cases if shard_for_pair(str(record["pair_id"]), num_shards) == shard_id]
    assigned.sort(key=lambda record: str(record["pair_id"]))
    if limit is not None:
        assigned = assigned[: int(limit)]
    if not assigned:
        raise RuntimeError("No cases assigned; check selected_config_keys, shard_id and num_shards")

    latest = _load_latest_records(predictions_path)
    pending = [
        record
        for record in assigned
        if record["pair_id"] not in latest
        or (latest[record["pair_id"]].get("status") != "completed" and retry_errors)
    ]

    set_seed(seed)
    model_kwargs: dict[str, Any] = {
        "device_map": "auto",
        "local_files_only": True,
        "trust_remote_code": False,
        "low_cpu_mem_usage": True,
        **_quantization_kwargs(
            quantization,
            torch,
            BitsAndBytesConfig,
            compute_dtype=compute_dtype,
        ),
    }
    if loader == "gemma3_conditional":
        # Keep Gemma's non-quantized vision/projector modules in BF16 too.
        model_kwargs["torch_dtype"] = compute_dtype
    model, tokenizer, encode = _load_runtime(model_dir, loader, model_kwargs)
    model.eval()

    started_at = utc_now()
    for index, case in enumerate(pending, start=1):
        pair_id = str(case["pair_id"])
        pair_started = time.perf_counter()
        try:
            inputs, decode_tokenizer = encode(str(case["prompt"]))
            input_tokens = int(inputs["input_ids"].shape[-1])
            if input_tokens > max_input_tokens:
                raise ValueError(
                    f"Input has {input_tokens} tokens, exceeding max_input_tokens={max_input_tokens}; "
                    "evaluation prompts are never silently truncated"
                )
            model_device = next(model.parameters()).device
            inputs = {key: value.to(model_device) if hasattr(value, "to") else value for key, value in inputs.items()}
            torch.cuda.synchronize()
            generation_started = time.perf_counter()
            with torch.inference_mode():
                generated = model.generate(
                    **inputs,
                    do_sample=False,
                    max_new_tokens=max_new_tokens,
                    pad_token_id=decode_tokenizer.pad_token_id,
                    use_cache=True,
                )
            torch.cuda.synchronize()
            generation_ms = round((time.perf_counter() - generation_started) * 1000, 2)
            continuation = generated[0, input_tokens:]
            answer = decode_tokenizer.decode(continuation, skip_special_tokens=True).strip()
            if not answer:
                token_ids = continuation.detach().cpu().tolist()
                raw_decode = decode_tokenizer.decode(continuation, skip_special_tokens=False)
                raise RuntimeError(
                    "Model returned an empty answer; "
                    f"compute_dtype={compute_dtype_name}; input_tokens={input_tokens}; "
                    f"generated_shape={list(generated.shape)}; "
                    f"continuation_token_ids={token_ids[:32]!r}; raw_decode={raw_decode[:200]!r}"
                )
            prediction_id = stable_pair_id(
                pair_id,
                model_id,
                str(asset_manifest["resolved_revision"]),
                quantization,
                str(seed),
            )
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
                "model_revision": asset_manifest["resolved_revision"],
                "loader": loader,
                "quantization": quantization,
                "compute_dtype": compute_dtype_name,
                "seed": seed,
                "do_sample": False,
                "input_tokens": input_tokens,
                "output_tokens": int(continuation.shape[-1]),
                "generation_latency_ms": generation_ms,
                "total_pair_latency_ms": round((time.perf_counter() - pair_started) * 1000, 2),
                "answer": answer,
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
                "model_revision": asset_manifest["resolved_revision"],
                "loader": loader,
                "quantization": quantization,
                "compute_dtype": compute_dtype_name,
                "error_type": type(exc).__name__,
                "error": str(exc)[:2000],
                "failed_at": utc_now(),
            }
        append_jsonl(predictions_path, record)
        latest[pair_id] = record
        if index % 10 == 0 or index == len(pending):
            print(f"model={model_key} processed={index}/{len(pending)} pair_id={pair_id} status={record['status']}")

    compacted = [latest[record["pair_id"]] for record in assigned if record["pair_id"] in latest]
    write_jsonl_atomic(predictions_path, compacted)
    completed = sum(record.get("status") == "completed" for record in compacted)
    failed = sum(record.get("status") == "failed" for record in compacted)
    summary = {
        "schema_version": PREDICTION_SCHEMA_VERSION,
        "started_at": started_at,
        "completed_at": utc_now(),
        "shard_id": shard_id,
        "num_shards": num_shards,
        "selected_suites": sorted(selected_suites),
        "selected_config_keys": sorted(selected_config_keys),
        "assigned_pair_count": len(assigned),
        "completed_pair_count": completed,
        "failed_pair_count": failed,
        "is_complete": completed == len(assigned) and failed == 0,
        "model_key": model_key,
        "model_id": model_id,
        "model_revision": asset_manifest["resolved_revision"],
        "loader": loader,
        "quantization": quantization,
        "compute_dtype": compute_dtype_name,
        "seed": seed,
        "max_input_tokens": max_input_tokens,
        "max_new_tokens": max_new_tokens,
        "bundle_cases_sha256": bundle_manifest["files"]["cases"]["sha256"],
        "environment": environment_summary(),
        "predictions_file": predictions_path.name,
        "predictions_sha256": sha256_file(predictions_path),
    }
    atomic_write_json(output_dir / "shard_summary.json", summary)
    archive_base = output_root / (
        f"local_llm_predictions_{model_key}_{selection_slug}_{shard_id:02d}_of_{num_shards:02d}"
    )
    archive_path = Path(shutil.make_archive(str(archive_base), "zip", root_dir=output_dir))
    summary["archive_path"] = str(archive_path)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python -m src.run_inference CONFIG.json")
    config = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    run_offline_inference(config)


if __name__ == "__main__":
    main()
