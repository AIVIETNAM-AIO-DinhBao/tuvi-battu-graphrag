from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .common import KIT_SCHEMA_VERSION, atomic_write_json, environment_summary, sha256_file


DEFAULT_MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"
DEFAULT_WHEEL_PACKAGES = [
    "transformers",
    "accelerate",
    "bitsandbytes",
    "safetensors",
    "huggingface-hub",
    "tokenizers",
    "sentencepiece",
]


def prepare_model_assets(config: dict[str, Any]) -> dict[str, Any]:
    """Download a pinned HF snapshot and optional wheels for an offline Kaggle run."""
    from huggingface_hub import HfApi, snapshot_download

    model_id = str(config.get("model_id") or DEFAULT_MODEL_ID)
    model_key = str(config.get("model_key") or model_id.rsplit("/", 1)[-1]).strip()
    loader = str(config.get("loader") or "causal_lm").strip()
    requested_revision = str(config.get("revision") or "main")
    output_root = Path(config.get("output_root") or f"/kaggle/working/{model_key}_offline_dataset").resolve()
    model_dir = output_root / "model"
    wheelhouse = output_root / "wheelhouse"
    output_root.mkdir(parents=True, exist_ok=True)

    hf_token = config.get("hf_token") or os.getenv("HF_TOKEN") or None
    info = HfApi(token=hf_token).model_info(model_id, revision=requested_revision)
    resolved_revision = str(info.sha)
    snapshot_path = snapshot_download(
        repo_id=model_id,
        revision=resolved_revision,
        local_dir=model_dir,
        token=hf_token,
        allow_patterns=[
            "*.json",
            "*.model",
            "*.py",
            "*.safetensors",
            "*.txt",
            "*.jinja",
            "tokenizer*",
            "vocab*",
            "merges*",
        ],
        ignore_patterns=["*.bin", "*.h5", "*.msgpack", "*.onnx"],
    )
    # snapshot_download may create local transfer metadata. It is unnecessary for
    # inference and should not be published with a gated model dataset.
    shutil.rmtree(model_dir / ".cache", ignore_errors=True)

    if bool(config.get("download_wheels", True)):
        wheelhouse.mkdir(parents=True, exist_ok=True)
        packages = list(config.get("wheel_packages") or DEFAULT_WHEEL_PACKAGES)
        for package in packages:
            module_name = package.replace("-", "_")
            try:
                module = __import__(module_name)
                version = str(getattr(module, "__version__"))
            except Exception:
                continue
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "download",
                    "--no-deps",
                    "--dest",
                    str(wheelhouse),
                    f"{package}=={version}",
                ],
                check=True,
            )

    files: list[dict[str, Any]] = []
    hash_large_files = bool(config.get("hash_large_files", True))
    for path in sorted(file for file in output_root.rglob("*") if file.is_file()):
        size = path.stat().st_size
        checksum = sha256_file(path) if hash_large_files or size < 256 * 1024 * 1024 else None
        files.append(
            {
                "path": path.relative_to(output_root).as_posix(),
                "size_bytes": size,
                "sha256": checksum,
            }
        )

    manifest = {
        "schema_version": KIT_SCHEMA_VERSION,
        "asset_type": "offline_huggingface_model",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "model_id": model_id,
        "model_key": model_key,
        "loader": loader,
        "requested_revision": requested_revision,
        "resolved_revision": resolved_revision,
        "snapshot_path": str(snapshot_path),
        "model_subdir": "model",
        "wheelhouse_subdir": "wheelhouse" if wheelhouse.exists() else None,
        "environment": environment_summary(),
        "file_count": len(files),
        "total_size_bytes": sum(int(item["size_bytes"]) for item in files),
        "files": files,
    }
    atomic_write_json(output_root / "asset_manifest.json", manifest)

    config_path = model_dir / "config.json"
    tokenizer_path = model_dir / "tokenizer_config.json"
    if not config_path.exists() or not tokenizer_path.exists():
        raise RuntimeError("Downloaded model is incomplete: config.json/tokenizer_config.json missing")
    if not list(model_dir.glob("*.safetensors")):
        raise RuntimeError("Downloaded model is incomplete: no safetensors weights found")
    return manifest


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python -m src.prepare_model CONFIG.json")
    config = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    print(json.dumps(prepare_model_assets(config), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
