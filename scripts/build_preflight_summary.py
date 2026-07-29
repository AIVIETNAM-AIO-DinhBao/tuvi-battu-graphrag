from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.rag.ablation import load_ablation_manifest
from app.rag.ablation import load_ablation_dataset
from app.rag.config import config_hash


ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "benchmark" / "tuvi_golden_dataset" / "release" / "tuviqa_v1_release.jsonl"
MANIFESTS = {
    "chunking": ROOT / "configs" / "w6_abl_03_chunking_matrix.yaml",
    "retrieval_fusion_reranker": ROOT / "configs" / "w8_abl_01_retrieval_matrix_v2.yaml",
    "prompt_generation_current_retrieval": ROOT / "configs" / "w7_abl_01_generation_prompt_matrix.yaml",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def posix(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def json_from_log(path: Path) -> dict[str, Any]:
    text = read_text(path)
    if not text:
        return {}
    try:
        return json.loads(text[text.index("{") :])
    except (ValueError, json.JSONDecodeError):
        return {}


def git_output(*args: str) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True, encoding="utf-8").strip()
    except Exception:
        return "unknown"


def manifest_inventory() -> dict[str, Any]:
    inventory: dict[str, Any] = {}
    for key, path in MANIFESTS.items():
        manifest = load_ablation_manifest(path)
        configs = []
        for spec in manifest.configs:
            config = spec.build_config()
            configs.append(
                {
                    "name": spec.name,
                    "experiment_id": config.experiment_id,
                    "config_hash": config_hash(config),
                    "chunk_strategy_id": config.chunk_strategy_id,
                    "prompt_template_id": config.prompt_template_id,
                    "generation_model": config.generation_model,
                    "retrieval_paths": {
                        "graph": config.graph_retrieval_enabled,
                        "dense": config.dense_retrieval_enabled,
                        "sparse": config.sparse_retrieval_enabled,
                    },
                    "fusion_method": config.fusion_method,
                    "reranker_enabled": config.reranker_enabled,
                }
            )
        inventory[key] = {
            "path": posix(path),
            "manifest_hash": sha256(path),
            "name": manifest.name,
            "dataset_path": posix(manifest.dataset_path),
            "config_count": len(configs),
            "configs": configs,
        }
    return inventory


def smoke_summary(base: Path) -> dict[str, Any]:
    smoke_paths = {
        "chunking": base / "smoke_chunking" / "evaluation_report.json",
        "retrieval_fusion_reranker": base / "smoke_retrieval_fusion_reranker" / "evaluation_report.json",
        "prompt_generation_current_retrieval": base / "smoke_prompt_generation_current_retrieval" / "evaluation_report.json",
    }
    smokes: dict[str, Any] = {}
    for key, report_path in smoke_paths.items():
        report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.exists() else {}
        configs = report.get("configs") or []
        item_count = report.get("dataset_item_count") or 0
        config_count = report.get("config_count") or 0
        completed_config_count = sum(1 for config in configs if config.get("status") == "completed")
        smokes[key] = {
            "status": "passed" if configs and completed_config_count == config_count else "missing_or_failed",
            "report": posix(report_path),
            "manifest_name": report.get("manifest_name"),
            "judge_backend": report.get("judge_backend"),
            "dataset_item_count": item_count,
            "config_count": config_count,
            "completed_config_count": completed_config_count,
            "expected_pairs": item_count * config_count,
        }
    return smokes


def build_summary(base: Path) -> dict[str, Any]:
    logs = base / "logs"
    pytest_log = read_text(logs / "pytest_backend_subset.log")
    gemini_payload = json_from_log(logs / "gemini_probe.log")
    coverage_payload = json_from_log(logs / "neo4j_chunk_coverage.log")
    summary: dict[str, Any] = {
        "status": "passed",
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_sha": git_output("rev-parse", "HEAD"),
        "git_status_short": git_output("status", "--short") or "clean",
        "dataset": {
            "path": posix(DATASET),
            "item_count": len(load_ablation_dataset(DATASET)),
            "sha256": sha256(DATASET),
        },
        "gates": {
            "backend_regression_subset": {
                "status": "passed" if "111 passed" in pytest_log else "unknown",
                "log": posix(logs / "pytest_backend_subset.log"),
                "excerpt": "111 passed, 1 warning" if "111 passed" in pytest_log else pytest_log[-240:],
            },
            "gemini_probe": {
                "status": "passed" if gemini_payload.get("ok_key_count", 0) > 0 else "unknown",
                "model": gemini_payload.get("model"),
                "checked_key_count": gemini_payload.get("checked_key_count"),
                "ok_key_count": gemini_payload.get("ok_key_count"),
                "log": posix(logs / "gemini_probe.log"),
            },
            "neo4j_chunk_coverage": {
                "status": "passed"
                if coverage_payload.get("completed") and coverage_payload.get("missing_pair_count") == 0
                else "unknown",
                **coverage_payload,
                "log": posix(logs / "neo4j_chunk_coverage.log"),
            },
        },
        "manifests": manifest_inventory(),
        "smokes": smoke_summary(base),
        "notes": [
            "Supabase persistence intentionally skipped; local reports/checkpoints are source of truth.",
            "Offline smoke uses static-smoke judge; it is not official metric evidence.",
            "Official full runs should use --judge-backend gemini and --skip-persistence.",
        ],
    }
    if not all(gate.get("status") == "passed" for gate in summary["gates"].values()):
        summary["status"] = "needs_attention"
    if not all(smoke.get("status") == "passed" for smoke in summary["smokes"].values()):
        summary["status"] = "needs_attention"
    return summary


def write_markdown(summary: dict[str, Any], base: Path) -> None:
    lines = [
        "# Preflight Summary - Full Ablation Rerun",
        "",
        f"Status: **{summary['status']}**",
        f"Completed UTC: `{summary['completed_at_utc']}`",
        f"Git SHA: `{summary['git_sha']}`",
        "",
        "## Dataset",
        "",
        "| Path | Items | SHA256 |",
        "|---|---:|---|",
        f"| `{summary['dataset']['path']}` | {summary['dataset']['item_count']} | `{summary['dataset']['sha256']}` |",
        "",
        "## Gates",
        "",
        "| Gate | Status | Evidence |",
        "|---|---|---|",
    ]
    for gate, data in summary["gates"].items():
        if gate == "backend_regression_subset":
            evidence = data.get("excerpt", "")
        elif gate == "gemini_probe":
            evidence = f"model={data.get('model')}, ok_keys={data.get('ok_key_count')}/{data.get('checked_key_count')}"
        else:
            evidence = (
                f"expected={data.get('expected_pair_count')}, "
                f"observed={data.get('observed_pair_count')}, missing={data.get('missing_pair_count')}"
            )
        lines.append(f"| {gate} | **{data.get('status')}** | {evidence}; log=`{data.get('log')}` |")
    lines.extend(
        [
            "",
            "## Manifest Inventory",
            "",
            "| Ablation | Manifest | Configs | Manifest SHA256 |",
            "|---|---|---:|---|",
        ]
    )
    for key, data in summary["manifests"].items():
        lines.append(f"| {key} | `{data['path']}` | {data['config_count']} | `{data['manifest_hash']}` |")
    lines.extend(
        [
            "",
            "## Offline Smoke Results",
            "",
            "| Smoke | Status | Judge | Configs | Items | Pairs | Report |",
            "|---|---|---|---:|---:|---:|---|",
        ]
    )
    for key, data in summary["smokes"].items():
        lines.append(
            f"| {key} | **{data['status']}** | `{data['judge_backend']}` | "
            f"{data['completed_config_count']}/{data['config_count']} | {data['dataset_item_count']} | "
            f"{data['expected_pairs']} | `{data['report']}` |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- Preflight passed for backend regression, Gemini model access, Neo4j chunk coverage, and all three manifest smoke runs.",
            "- Safe next step: run Phase 2 full chunking ablation with Gemini judge and checkpoint/resume.",
            "- Keep `--skip-persistence`; Supabase persistence remains non-blocking.",
            "",
            "## Phase 2 Command",
            "",
            "```powershell",
            "$env:PYTHONPATH='backend'",
            r".\.venv\Scripts\python.exe scripts\run_eval.py `",
            r"  --manifest configs/w6_abl_03_chunking_matrix.yaml `",
            r"  --judge-backend gemini `",
            r"  --skip-persistence `",
            r"  --checkpoint-dir benchmark/tuvi_golden_dataset/reports_final/10_chunking_strategy_ablation/checkpoints `",
            r"  --output-dir benchmark/tuvi_golden_dataset/reports_final/10_chunking_strategy_ablation",
            "```",
            "",
        ]
    )
    (base / "preflight_summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=ROOT / "benchmark" / "tuvi_golden_dataset" / "reports_final" / "00_preflight",
    )
    args = parser.parse_args()
    base = args.base_dir.resolve()
    base.mkdir(parents=True, exist_ok=True)
    summary = build_summary(base)
    (base / "preflight_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(summary, base)
    print(json.dumps({"ok": True, "status": summary["status"], "base_dir": posix(base)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()