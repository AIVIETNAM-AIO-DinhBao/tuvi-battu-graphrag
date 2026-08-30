from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

from .common import iter_json_records, shard_for_pair


def validate_kit(kit_root: Path, repo_root: Path | None = None, bundle_dir: Path | None = None) -> dict:
    errors: list[str] = []
    notebooks = sorted((kit_root / "notebooks").glob("*.ipynb"))
    expected_notebooks = {
        "00_prepare_model_dataset_kaggle.ipynb",
        "01_build_retrieval_bundle_local.ipynb",
        "02_generate_offline_kaggle.ipynb",
        "03_gemini_judge_local.ipynb",
    }
    observed_notebooks = {path.name for path in notebooks}
    if observed_notebooks != expected_notebooks:
        errors.append(
            f"notebook set mismatch: missing={sorted(expected_notebooks - observed_notebooks)}, "
            f"unexpected={sorted(observed_notebooks - expected_notebooks)}"
        )
    standalone_rows: list[dict] = []
    for notebook in notebooks:
        try:
            payload = json.loads(notebook.read_text(encoding="utf-8"))
            if payload.get("nbformat") != 4 or not payload.get("cells"):
                errors.append(f"invalid notebook structure: {notebook.name}")
                continue
            for index, cell in enumerate(payload["cells"]):
                if cell.get("cell_type") != "code":
                    continue
                source = "".join(cell.get("source") or [])
                if "%pip " in source:
                    continue
                try:
                    ast.parse(source)
                except SyntaxError as exc:
                    errors.append(f"invalid Python in {notebook.name} cell {index}: {exc}")
            if "_kaggle" in notebook.stem:
                raw = notebook.read_text(encoding="utf-8")
                runtime_cells = sum(
                    "standalone-runtime" in (cell.get("metadata", {}).get("tags") or [])
                    for cell in payload["cells"]
                )
                row = {
                    "notebook": notebook.name,
                    "runtime_cell_count": runtime_cells,
                    "imports_local_tools": "from local_tools" in raw or "import local_tools" in raw,
                    "imports_src": "from src" in raw or "import src" in raw,
                    "mentions_repo_root": "REPO_ROOT" in raw,
                }
                standalone_rows.append(row)
                if runtime_cells != 1 or row["imports_local_tools"] or row["imports_src"] or row["mentions_repo_root"]:
                    errors.append(f"Kaggle notebook is not standalone: {row}")
        except Exception as exc:
            errors.append(f"invalid notebook JSON {notebook.name}: {exc}")

    plan = json.loads((kit_root / "experiment_plan.json").read_text(encoding="utf-8"))
    suite_rows: list[dict] = []
    if repo_root is not None:
        try:
            import yaml
        except ImportError as exc:
            errors.append(f"PyYAML is required to validate manifests: {exc}")
            yaml = None

        for suite_name, suite in plan["suites"].items():
            config_count = 0
            item_counts: set[int] = set()
            selected_names: set[str] = set()
            for selection in suite["manifest_selections"]:
                relative = str(selection["path"])
                include_configs = {str(name) for name in selection.get("include_configs") or []}
                manifest_path = repo_root / relative
                if not manifest_path.exists():
                    errors.append(f"missing manifest: {relative}")
                    continue
                if yaml is None:
                    continue
                manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
                available = {str(spec["name"]) for spec in manifest.get("configs") or []}
                missing = sorted(include_configs - available)
                if missing:
                    errors.append(f"manifest {relative} missing selected configs {missing}")
                duplicates = selected_names & include_configs
                if duplicates:
                    errors.append(f"duplicate selected config names: {sorted(duplicates)}")
                selected_names.update(include_configs)
                config_count += len(include_configs)
                dataset_path = repo_root / str(manifest["dataset_path"])
                if not dataset_path.exists():
                    errors.append(f"missing dataset: {manifest['dataset_path']}")
                else:
                    item_counts.add(sum(1 for _ in iter_json_records(dataset_path)))
            expected = int(suite["expected_config_count"])
            if config_count != expected:
                errors.append(f"suite {suite_name}: expected {expected} configs, found {config_count}")
            if len(item_counts) > 1:
                errors.append(f"suite {suite_name}: manifests use inconsistent dataset sizes {item_counts}")
            item_count = next(iter(item_counts), 0)
            expected_items = int(suite.get("expected_item_count") or item_count)
            if item_count != expected_items:
                errors.append(f"suite {suite_name}: expected {expected_items} items, found {item_count}")
            expected_pairs = int(suite.get("expected_retrieval_pair_count") or expected * expected_items)
            if config_count * item_count != expected_pairs:
                errors.append(
                    f"suite {suite_name}: expected {expected_pairs} retrieval pairs, "
                    f"found {config_count * item_count}"
                )
            suite_rows.append(
                {
                    "suite": suite_name,
                    "config_count": config_count,
                    "item_count": item_count,
                    "pair_count": config_count * item_count,
                }
            )

    shard_counts: list[int] | None = None
    if bundle_dir is not None:
        cases = list(iter_json_records(bundle_dir / "cases.jsonl"))
        pair_ids = [str(record.get("pair_id") or "") for record in cases]
        if any(not pair_id for pair_id in pair_ids):
            errors.append("bundle contains case without pair_id")
        if len(pair_ids) != len(set(pair_ids)):
            errors.append("bundle contains duplicate pair_id")
        shard_counts = [sum(shard_for_pair(pair_id, 3) == shard for pair_id in pair_ids) for shard in range(3)]
        manifest = json.loads((bundle_dir / "bundle_manifest.json").read_text(encoding="utf-8"))
        if int(manifest["completed_pair_count"]) != len(cases):
            errors.append("bundle manifest completed_pair_count does not match cases.jsonl")
        if len(cases) != 300:
            errors.append(f"official bundle must contain 300 cases, found {len(cases)}")

    result = {
        "kit_root": str(kit_root),
        "notebook_count": len(notebooks),
        "standalone_notebooks": standalone_rows,
        "suite_rows": suite_rows,
        "bundle_shard_counts": shard_counts,
        "errors": errors,
        "ok": not errors,
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kit-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--repo-root", type=Path, default=None)
    parser.add_argument("--bundle-dir", type=Path, default=None)
    args = parser.parse_args()
    result = validate_kit(args.kit_root.resolve(), args.repo_root.resolve() if args.repo_root else None, args.bundle_dir.resolve() if args.bundle_dir else None)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
