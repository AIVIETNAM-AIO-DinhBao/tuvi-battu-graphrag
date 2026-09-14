"""Render a new generator prompt over an already frozen P6 retrieval bundle.

This intentionally never contacts Neo4j, the retriever, or the reranker.  It
copies each completed state from the source bundle and changes only `prompt`
and its provenance metadata, making prompt isolation auditable.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import shutil
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.rag.ablation import load_ablation_manifest  # noqa: E402
from app.rag.config import config_hash  # noqa: E402
from app.rag.evaluation_checkpoint import atomic_write_json, sha256_file  # noqa: E402
from app.rag.prompt_templates import build_prompt_from_template  # noqa: E402


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT_DIR / path


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, records: list[dict]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        "".join(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n" for record in records),
        encoding="utf-8",
        newline="\n",
    )
    temporary.replace(path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True, help="One-config P6 prompt manifest.")
    parser.add_argument("--source-bundle", type=Path, required=True, help="Completed P6 v1 context_bundle directory.")
    parser.add_argument("--output-dir", type=Path, required=True, help="Empty destination context_bundle directory.")
    parser.add_argument("--archive", type=Path, default=None, help="Optional output ZIP path without extension.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest_path = resolve(args.manifest).resolve()
    source_bundle = resolve(args.source_bundle).resolve()
    output_dir = resolve(args.output_dir).resolve()
    manifest = load_ablation_manifest(manifest_path)
    if len(manifest.configs) != 1:
        raise SystemExit("Prompt-rerender manifest must contain exactly one config.")
    if output_dir.exists() and any(output_dir.iterdir()):
        raise SystemExit(f"Destination must be empty: {output_dir}")
    source_meta = json.loads((source_bundle / "bundle_manifest.json").read_text(encoding="utf-8"))
    if not source_meta.get("is_complete") or int(source_meta.get("completed_pair_count") or 0) != 100:
        raise SystemExit("Source bundle is not a complete 100-item frozen bundle.")

    spec = manifest.configs[0]
    config = spec.build_config()
    config_key = f"sequential_final_1::{spec.name}"
    source_cases = read_jsonl(source_bundle / "cases.jsonl")
    if len(source_cases) != 100 or len({case.get("item_id") for case in source_cases}) != 100:
        raise SystemExit("Source bundle must contain exactly 100 unique cases.")

    output_dir.mkdir(parents=True, exist_ok=False)
    cases: list[dict] = []
    for source_case in source_cases:
        case = copy.deepcopy(source_case)
        state = case.get("state")
        if not isinstance(state, dict) or not state.get("final_context"):
            raise SystemExit(f"Missing final_context for {case.get('item_id')}")
        prompt = build_prompt_from_template(state, config)
        item_id = str(case["item_id"])
        case.update(
            {
                "pair_id": f"p6-prompt-rerender::{spec.name}::{item_id}",
                "config_key": config_key,
                "suite": "sequential_final_1",
                "prompt": prompt,
                "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
                "prompt_template_id": config.prompt_template_id,
            }
        )
        cases.append(case)

    config_record = {
        "bundle_config_hash": config_hash(config),
        "config": config.model_dump(mode="json"),
        "config_key": config_key,
        "config_name": spec.name,
        "manifest_name": manifest.name,
        "manifest_path": manifest_path.relative_to(ROOT_DIR).as_posix(),
        "source_config_hash": config_hash(config),
        "suite": "sequential_final_1",
    }
    write_jsonl(output_dir / "cases.jsonl", cases)
    write_jsonl(output_dir / "configs.jsonl", [config_record])
    shutil.copy2(source_bundle / "items.jsonl", output_dir / "items.jsonl")
    meta = {
        "schema_version": "model-agnostic-context-bundle-v2-prompt-rerender",
        "is_complete": True,
        "planned_pair_count": 100,
        "completed_pair_count": 100,
        "failed_pair_count": 0,
        "selected_suites": ["sequential_final_1"],
        "factor_isolation": "Only prompt_template_id changes; copied retrieval states and final_context verbatim.",
        "source_bundle": source_bundle.relative_to(ROOT_DIR).as_posix(),
        "source_bundle_manifest_sha256": sha256_file(source_bundle / "bundle_manifest.json"),
        "source_cases_sha256": sha256_file(source_bundle / "cases.jsonl"),
        "source_manifest": manifest_path.relative_to(ROOT_DIR).as_posix(),
        "prompt_template_id": config.prompt_template_id,
        "files": {
            name: {"name": f"{name}.jsonl", "sha256": sha256_file(output_dir / f"{name}.jsonl")}
            for name in ("cases", "configs", "items")
        },
    }
    atomic_write_json(output_dir / "bundle_manifest.json", meta)
    if args.archive:
        archive_base = resolve(args.archive)
        archive_base.parent.mkdir(parents=True, exist_ok=True)
        archive = Path(shutil.make_archive(str(archive_base), "zip", root_dir=output_dir))
        meta["archive"] = archive.relative_to(ROOT_DIR).as_posix()
        atomic_write_json(output_dir / "bundle_manifest.json", meta)
    print(json.dumps(meta, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
