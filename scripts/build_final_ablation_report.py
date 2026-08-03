"""Build a local, reproducible full-ablation summary report.

The full ablation waves can take many hours and may be resumed from W8
checkpoints.  This script is deliberately read-only with respect to run
artifacts: it loads manifests, completed ``evaluation_report.json`` files, and
checkpoint summaries, then writes a Markdown/JSON summary.  It can be run while
an evaluation is still in progress; incomplete phases are marked as such.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.rag.ablation import load_ablation_dataset, load_ablation_manifest  # noqa: E402
from app.rag.config import config_hash  # noqa: E402


DATASET = ROOT / "benchmark" / "tuvi_golden_dataset" / "release" / "tuviqa_v1_release.jsonl"
DEFAULT_BASE = ROOT / "benchmark" / "tuvi_golden_dataset" / "reports_final"
DEFAULT_MARKDOWN = ROOT / "evaluation" / "ablation_final_report.md"

QUESTION_FAMILIES = [
    "core_identity",
    "menh_house_interpretation",
    "than_cu_interpretation",
    "menh_cuc_relation",
    "special_state_interpretation",
    "menh_tam_hop",
    "menh_xung_chieu",
    "dai_van_interpretation",
    "topic_house_plus_relations",
    "synthesis_judgement",
]

QUESTION_COMPLEXITIES = ["Direct", "One-hop", "Two-hop"]

METRIC_COLUMNS = [
    ("faithfulness_avg", "Faith"),
    ("answer_relevancy_avg", "Relev"),
    ("context_recall_avg", "CtxRecall"),
    ("graph_hit_rate", "GraphHit"),
    ("citation_coverage_rate", "Citation"),
    ("p95_latency_ms", "RAG p95 ms"),
    ("retrieval_p95_ms", "Retr p95 ms"),
    ("generation_p95_ms", "Gen p95 ms"),
]

# The completed 3 x 3 factorial matrix is materialized in two immutable source
# waves: reports_final/10 contains the three structured-v3 cells, while
# reports_final/11 contains the six v1/v2 cells.  They are one canonical
# analytical matrix in the synthesized report, not two separate studies.
CHUNKING_PROMPT_SOURCE_KEYS = (
    "chunking_strategy",
    "chunking_prompt_interaction_v1_v2",
)
CHUNKING_PROMPT_MATRIX_KEY = "chunking_prompt_matrix_v1_v2_v3"
CHUNKING_PROMPT_MATRIX_LABEL = "Chunking × Prompt Matrix (3 × 3, v1/v2/v3)"


@dataclass(frozen=True)
class PhaseSpec:
    key: str
    label: str
    axis: str
    manifest: Path
    output_dir: Path
    expected_note: str
    required_for_final: bool = True


PHASES = [
    PhaseSpec(
        key="chunking_strategy",
        label="Chunking × Prompt Source Wave A (prompt v3 cells)",
        axis="chunking_prompt_interaction",
        manifest=ROOT / "configs" / "w6_abl_03_chunking_matrix.yaml",
        output_dir=DEFAULT_BASE / "10_chunking_strategy_ablation",
        expected_note="3 prompt-v3 cells x 100 = 300",
    ),
    PhaseSpec(
        key="chunking_prompt_interaction_v1_v2",
        label="Chunking × Prompt Source Wave B (prompt v1/v2 cells)",
        axis="chunking_prompt_interaction",
        manifest=ROOT / "configs" / "w8_abl_02_chunking_prompt_interaction_v1_v2.yaml",
        output_dir=DEFAULT_BASE / "11_chunking_prompt_interaction_v1_v2",
        expected_note="6 prompt-v1/v2 cells x 100 = 600",
        required_for_final=False,
    ),
    PhaseSpec(
        key="retrieval_fusion_reranker",
        label="Retrieval / Fusion / Reranker Matrix v2",
        axis="retrieval",
        manifest=ROOT / "configs" / "w8_abl_01_retrieval_matrix_v2.yaml",
        output_dir=DEFAULT_BASE / "20_retrieval_fusion_reranker_matrix",
        expected_note="10 x 100 = 1000",
    ),
    PhaseSpec(
        key="targeted_hard_cases",
        label="Targeted Hard-case Wave",
        axis="targeted",
        manifest=ROOT / "configs" / "w8_abl_01_priority_wave.yaml",
        output_dir=DEFAULT_BASE / "40_targeted_hard_cases",
        expected_note="optional diagnostic wave",
        required_for_final=False,
    ),
]


def sha256(path: Path) -> str:
    if not path.exists():
        return "missing"
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


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"_json_error": f"Could not parse {posix(path)}"}


REPORT_TOP_LEVEL_KEYS = [
    "status",
    "manifest_name",
    "dataset_path",
    "dataset_item_count",
    "config_count",
    "judge_backend",
    "started_at",
    "completed_at",
    "output_dir",
    "command",
]

REPORT_CONFIG_KEYS = [
    "config_name",
    "experiment_id",
    "run_id",
    "config_hash",
    "status",
    "error",
    "started_at",
    "completed_at",
    "chunk_strategy_id",
    "context_assembly_strategy",
    "prompt_template_id",
    "generation_model",
    "graph_retrieval_enabled",
    "dense_retrieval_enabled",
    "sparse_retrieval_enabled",
    "fusion_method",
    "reranker_enabled",
    "document_grading_enabled",
    "metrics",
    "grouped_metrics",
]

CHECKPOINT_KEYS = [
    "status",
    "created_at",
    "updated_at",
    "manifest_name",
    "manifest_path",
    "dataset_path",
    "dataset_item_count",
    "config_count",
    "expected_pair_count",
    "processed_pair_count",
    "completed_pair_count",
    "failed_pair_count",
    "remaining_pair_count",
    "current_config",
    "current_item",
    "last_completed_config",
    "last_completed_item",
]


def compact_report_config(row: dict[str, Any]) -> dict[str, Any]:
    """Keep only fields needed by the final report tables.

    Raw ``evaluation_report.json`` files contain per-item answers, contexts and
    judge payloads.  A 1000-pair matrix can make the synthesized JSON summary
    very large if those item payloads are embedded again.  The raw artifacts
    remain in their phase directories; this compact view is enough for inventory,
    metric tables and winner analysis.
    """

    return {key: row[key] for key in REPORT_CONFIG_KEYS if key in row}


def compact_report(report: dict[str, Any]) -> dict[str, Any]:
    if not report or report.get("_json_error"):
        return report
    compact = {key: report[key] for key in REPORT_TOP_LEVEL_KEYS if key in report}
    compact["configs"] = [compact_report_config(row) for row in report.get("configs") or []]
    return compact


def compact_checkpoint(checkpoint: dict[str, Any]) -> dict[str, Any]:
    if not checkpoint or checkpoint.get("_json_error"):
        return checkpoint
    compact = {key: checkpoint[key] for key in CHECKPOINT_KEYS if key in checkpoint}
    # Preserve any unanticipated scalar counters without copying nested payloads.
    for key, value in checkpoint.items():
        if key in compact:
            continue
        if isinstance(value, (str, int, float, bool)) or value is None:
            compact[key] = value
    return compact


def git_output(*args: str) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True, encoding="utf-8").strip()
    except Exception:
        return "unknown"


def git_status_summary() -> str:
    status = git_output("status", "--short")
    if status in {"", "clean"}:
        return "clean"
    if status == "unknown":
        return "unknown"
    changed_path_count = len([line for line in status.splitlines() if line.strip()])
    return f"dirty ({changed_path_count} changed paths)"


def metric(metrics: dict[str, Any], key: str) -> float | None:
    value = metrics.get(key)
    if isinstance(value, (int, float)):
        return float(value)
    return None


def quality_latency_score(metrics: dict[str, Any]) -> float:
    """Heuristic score used only for report ranking, not as a judge metric."""

    def value(key: str) -> float:
        current = metric(metrics, key)
        return 0.0 if current is None else current

    quality = (
        0.30 * value("context_recall_avg")
        + 0.20 * value("faithfulness_avg")
        + 0.20 * value("answer_relevancy_avg")
        + 0.15 * value("citation_coverage_rate")
        + 0.10 * value("graph_hit_rate")
        + 0.05 * value("source_coverage_rate")
    )
    # Keep latency as a small tie-breaker. 60s p95 or worse subtracts 0.10.
    p95_ms = value("p95_latency_ms") or value("evaluation_total_p95_ms")
    latency_penalty = min(max(p95_ms, 0.0) / 60_000.0, 1.0) * 0.10
    return round(quality - latency_penalty, 6)


def average_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Average scalar metric keys across completed config rows.

    This is used only for transparent marginal summaries of the completed 3×3
    factorial matrix.  It does not change or rewrite any raw evaluation result.
    """

    metrics_rows = [row.get("metrics") or {} for row in rows]
    averaged: dict[str, Any] = {"cell_count": len(metrics_rows)}
    keys = sorted({key for metrics in metrics_rows for key in metrics})
    for key in keys:
        values = [metrics.get(key) for metrics in metrics_rows]
        numeric_values = [float(value) for value in values if isinstance(value, (int, float))]
        if len(numeric_values) == len(metrics_rows) and numeric_values:
            averaged[key] = sum(numeric_values) / len(numeric_values)
    return averaged


def marginal_rows(report_configs: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in report_configs:
        value = row.get(key)
        if not value:
            continue
        grouped.setdefault(str(value), []).append(row)

    rows = []
    for value, configs in grouped.items():
        metrics = average_metrics(configs)
        rows.append(
            {
                "value": value,
                "cell_count": len(configs),
                "score": quality_latency_score(metrics),
                "metrics": metrics,
            }
        )
    return sorted(rows, key=lambda row: row["score"], reverse=True)


def fmt(value: Any, metric_key: str | None = None) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if metric_key and metric_key.endswith("_ms"):
            return f"{value:.1f}"
        return f"{value:.3f}"
    return str(value)


def table(lines: list[str], headers: Iterable[str]) -> None:
    header_list = list(headers)
    lines.append("| " + " | ".join(header_list) + " |")
    lines.append("|" + "|".join("---" for _ in header_list) + "|")


def manifest_config_rows(manifest_path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if not manifest_path.exists():
        return {"status": "manifest_missing", "path": posix(manifest_path), "manifest_hash": "missing"}, []
    try:
        manifest = load_ablation_manifest(manifest_path)
    except Exception as exc:
        return {
            "status": "manifest_load_failed",
            "path": posix(manifest_path),
            "manifest_hash": sha256(manifest_path),
            "error": str(exc),
        }, []

    rows: list[dict[str, Any]] = []
    for spec in manifest.configs:
        config = spec.build_config()
        rows.append(
            {
                "config_name": spec.name,
                "experiment_id": config.experiment_id,
                "config_hash": config_hash(config),
                "chunk_strategy_id": config.chunk_strategy_id,
                "prompt_template_id": config.prompt_template_id,
                "generation_model": config.generation_model,
                "graph_retrieval_enabled": config.graph_retrieval_enabled,
                "dense_retrieval_enabled": config.dense_retrieval_enabled,
                "sparse_retrieval_enabled": config.sparse_retrieval_enabled,
                "fusion_method": config.fusion_method,
                "reranker_enabled": config.reranker_enabled,
                "document_grading_enabled": config.document_grading_enabled,
            }
        )
    return (
        {
            "status": "loaded",
            "path": posix(manifest_path),
            "manifest_hash": sha256(manifest_path),
            "name": manifest.name,
            "dataset_path": posix(manifest.dataset_path),
            "dataset_item_count": len(load_ablation_dataset(manifest.dataset_path)),
            "config_count": len(rows),
        },
        rows,
    )


def variable_summary(axis: str, config: dict[str, Any]) -> str:
    if axis == "chunking":
        return f"chunk={config.get('chunk_strategy_id', 'n/a')}"
    if axis == "chunking_prompt_interaction":
        return (
            f"chunk={config.get('chunk_strategy_id', 'n/a')}; "
            f"prompt={config.get('prompt_template_id', 'n/a')}"
        )
    if axis == "prompt":
        return (
            f"prompt={config.get('prompt_template_id', 'n/a')}; "
            f"model={config.get('generation_model', 'n/a')}"
        )
    if axis in {"retrieval", "targeted"}:
        paths = "".join(
            label
            for flag, label in [
                (config.get("graph_retrieval_enabled"), "G"),
                (config.get("dense_retrieval_enabled"), "D"),
                (config.get("sparse_retrieval_enabled"), "S"),
            ]
            if flag
        ) or "none"
        return (
            f"paths={paths}; fusion={config.get('fusion_method', 'n/a')}; "
            f"rerank={fmt(config.get('reranker_enabled'))}"
        )
    return "n/a"


def phase_output_dir(spec: PhaseSpec, base_dir: Path) -> Path:
    return base_dir / spec.output_dir.relative_to(DEFAULT_BASE)


def summarize_phase(spec: PhaseSpec, base_dir: Path) -> dict[str, Any]:
    output_dir = phase_output_dir(spec, base_dir)
    report_path = output_dir / "evaluation_report.json"
    checkpoint_path = output_dir / "checkpoints" / "checkpoint_summary.json"
    report = compact_report(read_json(report_path))
    checkpoint = compact_checkpoint(read_json(checkpoint_path))
    manifest_meta, manifest_rows = manifest_config_rows(spec.manifest)

    report_configs = report.get("configs") or []
    report_by_name = {row.get("config_name"): row for row in report_configs if row.get("config_name")}
    completed_config_count = sum(1 for row in report_configs if row.get("status") == "completed")
    report_config_count = report.get("config_count") or len(report_configs) or manifest_meta.get("config_count", 0)

    if report:
        status = "completed" if completed_config_count == report_config_count else "partial_or_failed"
    elif checkpoint:
        remaining = checkpoint.get("remaining_pair_count")
        status = "completed_pending_report" if remaining == 0 else "in_progress"
    elif spec.manifest.exists() or spec.required_for_final:
        status = "not_started"
    else:
        status = "conditional_or_missing"

    expected_pair_count = (
        checkpoint.get("expected_pair_count")
        or (report.get("dataset_item_count") or manifest_meta.get("dataset_item_count") or 0)
        * (report_config_count or manifest_meta.get("config_count", 0) or 0)
    )
    processed_pair_count = checkpoint.get("processed_pair_count")
    if processed_pair_count is None and report_configs:
        processed_pair_count = sum((row.get("metrics") or {}).get("completed_count", 0) for row in report_configs)

    inventory_rows: list[dict[str, Any]] = []
    source_rows = manifest_rows or report_configs
    for row in source_rows:
        report_row = report_by_name.get(row.get("config_name"), {})
        merged = {**row, **{k: v for k, v in report_row.items() if k != "items"}}
        metrics = report_row.get("metrics") or {}
        inventory_rows.append(
            {
                **merged,
                "phase": spec.key,
                "phase_label": spec.label,
                "axis": spec.axis,
                "manifest": manifest_meta.get("path", posix(spec.manifest)),
                "main_variable": variable_summary(spec.axis, merged),
                "item_count": metrics.get("item_count") or report.get("dataset_item_count") or manifest_meta.get("dataset_item_count"),
                "run_status": report_row.get("status") or status,
            }
        )

    ranked_configs = []
    for row in report_configs:
        metrics = row.get("metrics") or {}
        ranked_configs.append(
            {
                "config_name": row.get("config_name"),
                "score": quality_latency_score(metrics),
                "metrics": metrics,
                "row": row,
            }
        )
    ranked_configs.sort(key=lambda item: item["score"], reverse=True)

    return {
        "key": spec.key,
        "label": spec.label,
        "axis": spec.axis,
        "required_for_final": spec.required_for_final,
        "expected_note": spec.expected_note,
        "manifest": manifest_meta,
        "output_dir": posix(output_dir),
        "report_path": posix(report_path),
        "checkpoint_path": posix(checkpoint_path),
        "report": report,
        "checkpoint": checkpoint,
        "status": status,
        "judge_backend": report.get("judge_backend") or "pending",
        "dataset_item_count": report.get("dataset_item_count") or manifest_meta.get("dataset_item_count"),
        "config_count": report_config_count or manifest_meta.get("config_count"),
        "completed_config_count": completed_config_count,
        "expected_pair_count": expected_pair_count,
        "processed_pair_count": processed_pair_count,
        "failed_pair_count": checkpoint.get("failed_pair_count"),
        "remaining_pair_count": checkpoint.get("remaining_pair_count"),
        "current_config": checkpoint.get("current_config"),
        "current_item": checkpoint.get("current_item"),
        "inventory_rows": inventory_rows,
        "ranked_configs": ranked_configs,
    }


def completed_count(phase: dict[str, Any]) -> int:
    """Return a phase counter as zero when a source artifact omits it."""

    value = phase.get("completed_config_count")
    return value if isinstance(value, int) else 0


def numeric_sum(*values: Any) -> int | float | None:
    numbers = [value for value in values if isinstance(value, (int, float))]
    return sum(numbers) if numbers else None


def combine_chunking_prompt_matrix(phases: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Merge W6 + W8 source waves into the completed 3 x 3 matrix view."""

    source = [phases[key] for key in CHUNKING_PROMPT_SOURCE_KEYS]
    source_reports = [phase.get("report") or {} for phase in source]
    report_configs = [row for report in source_reports for row in report.get("configs") or []]
    inventory_rows = [row for phase in source for row in phase.get("inventory_rows") or []]
    for row in inventory_rows:
        row["phase"] = CHUNKING_PROMPT_MATRIX_KEY
        row["phase_label"] = CHUNKING_PROMPT_MATRIX_LABEL
        row["axis"] = "chunking_prompt_interaction"
        row["main_variable"] = variable_summary("chunking_prompt_interaction", row)

    ranked_configs = []
    for phase in source:
        ranked_configs.extend(phase.get("ranked_configs") or [])
    ranked_configs.sort(key=lambda item: item["score"], reverse=True)

    source_statuses = [phase.get("status") for phase in source]
    if all(status == "completed" for status in source_statuses):
        status = "completed"
    elif any(status in {"in_progress", "partial_or_failed", "completed_pending_report"} for status in source_statuses):
        status = "in_progress"
    else:
        status = "not_started"

    source_output_dirs = [phase["output_dir"] for phase in source]
    return {
        "key": CHUNKING_PROMPT_MATRIX_KEY,
        "label": CHUNKING_PROMPT_MATRIX_LABEL,
        "axis": "chunking_prompt_interaction",
        "required_for_final": True,
        "expected_note": "3 chunking strategies x 3 prompt templates = 900",
        "manifest": {
            "status": "combined",
            "path": " + ".join(phase["manifest"].get("path", "n/a") for phase in source),
        },
        "output_dir": " + ".join(source_output_dirs),
        "report_path": " + ".join(phase["report_path"] for phase in source),
        "checkpoint_path": " + ".join(phase["checkpoint_path"] for phase in source),
        "report": {"configs": report_configs},
        "status": status,
        "judge_backend": "gemini" if all(phase.get("judge_backend") == "gemini" for phase in source) else "mixed_or_pending",
        "dataset_item_count": max((phase.get("dataset_item_count") or 0 for phase in source), default=0) or None,
        "config_count": numeric_sum(*(phase.get("config_count") for phase in source)),
        "completed_config_count": numeric_sum(*(completed_count(phase) for phase in source)) or 0,
        "expected_pair_count": numeric_sum(*(phase.get("expected_pair_count") for phase in source)),
        "processed_pair_count": numeric_sum(*(phase.get("processed_pair_count") for phase in source)),
        "failed_pair_count": numeric_sum(*(phase.get("failed_pair_count") for phase in source)),
        "remaining_pair_count": numeric_sum(*(phase.get("remaining_pair_count") for phase in source)),
        "current_config": None,
        "current_item": None,
        "inventory_rows": inventory_rows,
        "ranked_configs": ranked_configs,
        "marginal_winners": {
            "by_chunk_strategy_id": marginal_rows(report_configs, "chunk_strategy_id"),
            "by_prompt_template_id": marginal_rows(report_configs, "prompt_template_id"),
        },
        "source_phase_keys": list(CHUNKING_PROMPT_SOURCE_KEYS),
        "source_output_dirs": source_output_dirs,
    }


def display_phases(summary: dict[str, Any]) -> list[dict[str, Any]]:
    """Return report phases, replacing W6/W8 source rows with their 3 x 3 view."""

    phases = summary["phases"]
    return [
        summary["chunking_prompt_matrix"],
        *[
            phase
            for key, phase in phases.items()
            if key not in CHUNKING_PROMPT_SOURCE_KEYS
        ],
    ]


def winner_text(phase: dict[str, Any] | None, fallback: str = "pending") -> str:
    if not phase:
        return fallback
    ranked = phase.get("ranked_configs") or []
    if not ranked:
        return fallback
    top = ranked[0]
    return f"`{top['config_name']}` (score={top['score']:.3f})"


def build_summary(base_dir: Path) -> dict[str, Any]:
    phases = {spec.key: summarize_phase(spec, base_dir) for spec in PHASES}
    dataset_count = len(load_ablation_dataset(DATASET)) if DATASET.exists() else None
    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_sha": git_output("rev-parse", "HEAD"),
        "git_status_short": git_status_summary(),
        "dataset": {
            "path": posix(DATASET),
            "item_count": dataset_count,
            "sha256": sha256(DATASET),
        },
        "base_dir": posix(base_dir),
        "phases": phases,
    }
    summary["chunking_prompt_matrix"] = combine_chunking_prompt_matrix(phases)
    required = [
        summary["chunking_prompt_matrix"],
        phases["retrieval_fusion_reranker"],
    ]
    summary["status"] = "complete" if all(phase["status"] == "completed" for phase in required) else "in_progress"
    return summary


def append_phase_status(lines: list[str], summary: dict[str, Any]) -> None:
    lines.extend(["## Run Status", ""])
    table(
        lines,
        [
            "Phase",
            "Status",
            "Judge",
            "Configs",
            "Pairs processed/expected",
            "Current",
            "Output",
        ],
    )
    for phase in display_phases(summary):
        processed = phase.get("processed_pair_count")
        expected = phase.get("expected_pair_count")
        current = ""
        if phase.get("current_config") or phase.get("current_item"):
            current = f"{phase.get('current_config') or ''} / {phase.get('current_item') or ''}"
        lines.append(
            f"| {phase['label']} | **{phase['status']}** | `{phase['judge_backend']}` | "
            f"{phase.get('completed_config_count', 0)}/{phase.get('config_count') or 0} | "
            f"{fmt(processed)}/{fmt(expected)} | {current or 'n/a'} | `{phase['output_dir']}` |"
        )
    lines.append("")


def append_inventory(lines: list[str], summary: dict[str, Any]) -> None:
    lines.extend(["## 1. Experiment Inventory", ""])
    table(lines, ["Phase", "Config", "Manifest", "Config hash", "Main variable", "Items", "Status"])
    for phase in display_phases(summary):
        rows = phase.get("inventory_rows") or []
        if not rows:
            lines.append(
                f"| {phase['label']} | n/a | `{phase['manifest'].get('path')}` | n/a | "
                f"{phase['manifest'].get('status')} | n/a | **{phase['status']}** |"
            )
            continue
        for row in rows:
            lines.append(
                f"| {phase['label']} | `{row.get('config_name')}` | `{row.get('manifest')}` | "
                f"`{row.get('config_hash', 'n/a')}` | {row.get('main_variable')} | "
                f"{fmt(row.get('item_count'))} | **{row.get('run_status')}** |"
            )
    lines.append("")


def append_metric_tables(lines: list[str], summary: dict[str, Any]) -> None:
    lines.extend(["## 2. Metric Tables", ""])
    for phase in display_phases(summary):
        report_configs = phase.get("report", {}).get("configs") or []
        lines.extend([f"### {phase['label']}", ""])
        if not report_configs:
            lines.append(
                f"No completed `evaluation_report.json` yet. Current status: **{phase['status']}**; "
                f"checkpoint processed {fmt(phase.get('processed_pair_count'))}/{fmt(phase.get('expected_pair_count'))} pairs."
            )
            lines.append("")
            continue
        table(
            lines,
            ["Rank", "Config", "Score", "Main variable"] + [header for _, header in METRIC_COLUMNS],
        )
        ranked = phase.get("ranked_configs") or []
        for idx, entry in enumerate(ranked, start=1):
            row = entry["row"]
            metrics = entry["metrics"]
            values = [fmt(metrics.get(key), key) for key, _ in METRIC_COLUMNS]
            lines.append(
                f"| {idx} | `{entry['config_name']}` | {entry['score']:.3f} | "
                f"{variable_summary(phase['axis'], row)} | " + " | ".join(values) + " |"
            )
        lines.append("")


def marginal_winner_text(matrix: dict[str, Any], group_key: str) -> str:
    rows = (matrix.get("marginal_winners") or {}).get(group_key) or []
    if not rows:
        return "pending"
    top = rows[0]
    return f"`{top['value']}` (marginal score={top['score']:.3f}, cells={top['cell_count']})"


def append_marginal_tables(lines: list[str], summary: dict[str, Any]) -> None:
    matrix = summary["chunking_prompt_matrix"]
    marginal = matrix.get("marginal_winners") or {}
    if not marginal:
        return

    lines.extend(["## 3. Marginal Summary within Completed Chunking × Prompt Matrix", ""])
    lines.append(
        "These averages summarize the 9 completed factorial cells by one factor at a time. "
        "They are descriptive marginal summaries of the same 3×3 study, not additional runs."
    )
    lines.append("")
    for group_key, label in [
        ("by_chunk_strategy_id", "By chunking strategy"),
        ("by_prompt_template_id", "By prompt template"),
    ]:
        rows = marginal.get(group_key) or []
        lines.extend([f"### {label}", ""])
        table(lines, ["Rank", "Value", "Cells", "Score", "Faith", "Relev", "CtxRecall", "Citation", "RAG p95 ms", "Retr p95 ms"])
        for idx, row in enumerate(rows, start=1):
            metrics = row.get("metrics") or {}
            lines.append(
                f"| {idx} | `{row['value']}` | {row['cell_count']} | {row['score']:.3f} | "
                f"{fmt(metrics.get('faithfulness_avg'))} | {fmt(metrics.get('answer_relevancy_avg'))} | "
                f"{fmt(metrics.get('context_recall_avg'))} | {fmt(metrics.get('citation_coverage_rate'))} | "
                f"{fmt(metrics.get('p95_latency_ms'), 'p95_latency_ms')} | "
                f"{fmt(metrics.get('retrieval_p95_ms'), 'retrieval_p95_ms')} |"
            )
        lines.append("")


def append_axis_winners(lines: list[str], summary: dict[str, Any]) -> None:
    phases = summary["phases"]
    chunking_prompt_matrix = summary["chunking_prompt_matrix"]
    lines.extend(["## 4. Winners by Axis", ""])
    table(lines, ["Axis", "Winner", "Evidence / interpretation"])
    lines.append(
        f"| Best chunking × prompt configuration | {winner_text(chunking_prompt_matrix)} | "
        "Full 3 × 3 matrix: source wave A in `10_chunking_strategy_ablation` supplies the 3 prompt-v3 cells; "
        "source wave B in `11_chunking_prompt_interaction_v1_v2` supplies the 6 prompt-v1/v2 cells. Retrieval is held fixed. "
        "Score ranks Context Recall, Faithfulness, Relevancy, Citation Coverage, Graph Hit, and p95 latency. |"
    )
    lines.append(
        f"| Best chunking strategy within 3×3 matrix | {marginal_winner_text(chunking_prompt_matrix, 'by_chunk_strategy_id')} | "
        "Marginal average across all 3 prompt templates in the completed matrix. |"
    )
    lines.append(
        f"| Best prompt template within 3×3 matrix | {marginal_winner_text(chunking_prompt_matrix, 'by_prompt_template_id')} | "
        "Marginal average across all 3 chunking strategies in the completed matrix. This replaces the old separate prompt-ablation placeholder for the current study. |"
    )
    retrieval = phases.get("retrieval_fusion_reranker")
    retrieval_winner = winner_text(retrieval)
    retrieval_detail = "pending"
    if retrieval and retrieval.get("ranked_configs"):
        row = retrieval["ranked_configs"][0]["row"]
        retrieval_detail = variable_summary("retrieval", row)
    lines.append(f"| Best retrieval path combination | {retrieval_winner} | {retrieval_detail} |")
    lines.append(f"| Best fusion method | {retrieval_winner} | Derived from the Phase 3 winning config; compare RRF vs weighted_sum vs graph_first in the Phase 3 table. |")
    lines.append(f"| Reranker on/off | {retrieval_winner} | Derived from baseline vs `baseline_no_reranker` once Phase 3 is complete. |")
    lines.append("")


def family_winner_rows(phase: dict[str, Any], family: str) -> list[dict[str, Any]]:
    rows = []
    for config in phase.get("report", {}).get("configs") or []:
        grouped = config.get("grouped_metrics") or {}
        family_metrics = (grouped.get("by_question_family") or {}).get(family)
        if not isinstance(family_metrics, dict):
            continue
        rows.append(
            {
                "config_name": config.get("config_name"),
                "score": quality_latency_score(family_metrics),
                "metrics": family_metrics,
            }
        )
    return sorted(rows, key=lambda row: row["score"], reverse=True)


def complexity_winner_rows(phase: dict[str, Any], complexity: str) -> list[dict[str, Any]]:
    rows = []
    for config in phase.get("report", {}).get("configs") or []:
        grouped = config.get("grouped_metrics") or {}
        metrics = (grouped.get("by_question_complexity") or {}).get(complexity)
        if not isinstance(metrics, dict):
            continue
        rows.append({"config_name": config.get("config_name"), "score": quality_latency_score(metrics), "metrics": metrics})
    return sorted(rows, key=lambda row: row["score"], reverse=True)


def append_family_winners(lines: list[str], summary: dict[str, Any]) -> None:
    lines.extend(["## 5. Winners by Question Family", ""])
    for phase in display_phases(summary):
        lines.extend([f"### {phase['label']}", ""])
        if not phase.get("report"):
            lines.append(f"Pending: no completed report yet for this phase (`{phase['status']}`).")
            lines.append("")
            continue
        table(lines, ["Family", "Winner", "Score", "Items", "Faith", "Relev", "CtxRecall", "GraphHit", "Citation", "Retr p95 ms"])
        for family in QUESTION_FAMILIES:
            ranked = family_winner_rows(phase, family)
            if not ranked:
                lines.append(f"| {family} | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |")
                continue
            top = ranked[0]
            metrics = top["metrics"]
            lines.append(
                f"| {family} | `{top['config_name']}` | {top['score']:.3f} | {fmt(metrics.get('item_count'))} | "
                f"{fmt(metrics.get('faithfulness_avg'))} | {fmt(metrics.get('answer_relevancy_avg'))} | "
                f"{fmt(metrics.get('context_recall_avg'))} | {fmt(metrics.get('graph_hit_rate'))} | "
                f"{fmt(metrics.get('citation_coverage_rate'))} | {fmt(metrics.get('retrieval_p95_ms'), 'retrieval_p95_ms')} |"
            )
        lines.append("")


def append_complexity_winners(lines: list[str], summary: dict[str, Any]) -> None:
    lines.extend(["## 6. Winners by Question Complexity", ""])
    for phase in display_phases(summary):
        if not phase.get("report"):
            continue
        lines.extend([f"### {phase['label']}", ""])
        table(lines, ["Complexity", "Winner", "Score", "Items", "Faith", "Relev", "CtxRecall", "Citation", "Retr p95 ms"])
        for complexity in QUESTION_COMPLEXITIES:
            ranked = complexity_winner_rows(phase, complexity)
            if not ranked:
                lines.append(f"| {complexity} | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |")
                continue
            top = ranked[0]
            metrics = top["metrics"]
            lines.append(
                f"| {complexity} | `{top['config_name']}` | {top['score']:.3f} | {fmt(metrics.get('item_count'))} | "
                f"{fmt(metrics.get('faithfulness_avg'))} | {fmt(metrics.get('answer_relevancy_avg'))} | "
                f"{fmt(metrics.get('context_recall_avg'))} | {fmt(metrics.get('citation_coverage_rate'))} | "
                f"{fmt(metrics.get('retrieval_p95_ms'), 'retrieval_p95_ms')} |"
            )
        lines.append("")


def append_candidate_section(lines: list[str], summary: dict[str, Any]) -> None:
    phases = summary["phases"]
    chunking_prompt_matrix = summary["chunking_prompt_matrix"]
    complete_core = chunking_prompt_matrix["status"] == "completed" and phases["retrieval_fusion_reranker"]["status"] == "completed"
    lines.extend(["## 7. Research/Eval Candidate", ""])
    if complete_core:
        best_cell = chunking_prompt_matrix["ranked_configs"][0]["row"]
        retrieval = phases["retrieval_fusion_reranker"]["ranked_configs"][0]["row"]
        lines.extend(
            [
                "All required evidence is available. Create a new candidate config rather than overwriting `configs/default_production.yaml`.",
                "",
                "Recommended candidate ingredients:",
                f"- chunk_strategy_id: `{best_cell.get('chunk_strategy_id')}`",
                f"- prompt_template_id: `{best_cell.get('prompt_template_id')}`",
                f"- generation_model: `{best_cell.get('generation_model')}`",
                f"- retrieval: `{variable_summary('retrieval', retrieval)}`",
                "",
                "Suggested file: `configs/eval_candidate_v3.yaml`, followed by a final full-100 or hard-case confirmation run.",
            ]
        )
    else:
        lines.extend(
            [
                "Candidate selection is **pending** until the core full runs finish.",
                f"- chunking × prompt matrix: `{chunking_prompt_matrix['status']}`",
                f"- retrieval/fusion/reranker phase: `{phases['retrieval_fusion_reranker']['status']}`",
                "- prompt evidence: `completed inside the 3×3 chunking × prompt matrix`; no separate current-retrieval prompt phase is active.",
                "- Do not overwrite `configs/default_production.yaml`; create `configs/eval_candidate_v3.yaml` once winners are known.",
            ]
        )
    lines.append("")


def append_next_steps(lines: list[str], summary: dict[str, Any]) -> None:
    lines.extend(["## 8. Next Steps / Resume Commands", ""])
    phases = summary["phases"]
    chunking = summary["chunking_prompt_matrix"]
    if chunking["status"] == "in_progress":
        lines.extend(
            [
                "Phase 2 is currently in progress. Monitor:",
                "",
                "```powershell",
                r"Get-Content -LiteralPath benchmark\tuvi_golden_dataset\reports_final\10_chunking_strategy_ablation\phase2_full_status_latest.json -Raw",
                "```",
                "",
                "If interrupted, resume:",
                "",
                "```powershell",
                "$env:PYTHONPATH='backend'",
                r".\.venv\Scripts\python.exe scripts\run_eval.py `",
                r"  --manifest configs/w6_abl_03_chunking_matrix.yaml `",
                r"  --judge-backend gemini `",
                r"  --skip-persistence `",
                r"  --checkpoint-dir benchmark/tuvi_golden_dataset/reports_final/10_chunking_strategy_ablation/checkpoints `",
                r"  --output-dir benchmark/tuvi_golden_dataset/reports_final/10_chunking_strategy_ablation `",
                r"  --resume --retry-failed",
                "```",
                "",
            ]
        )
    if chunking["status"] == "completed" and phases["retrieval_fusion_reranker"]["status"] == "not_started":
        lines.extend(
            [
                "Launch Phase 3 using config shards for multi-teammate execution. Each teammate writes only their assigned shard directory; merge on `main` after all three shards complete.",
                "",
                "Shard manifests:",
                "",
                "- `configs/w8_abl_01_retrieval_matrix_v2_shard_a_controls.yaml` -> `20_retrieval_fusion_reranker_matrix/shards/shard_a_controls` (`4 x 100 = 400`)",
                "- `configs/w8_abl_01_retrieval_matrix_v2_shard_b_single_paths.yaml` -> `20_retrieval_fusion_reranker_matrix/shards/shard_b_single_paths` (`3 x 100 = 300`)",
                "- `configs/w8_abl_01_retrieval_matrix_v2_shard_c_dense_combos.yaml` -> `20_retrieval_fusion_reranker_matrix/shards/shard_c_dense_combos` (`3 x 100 = 300`)",
                "",
                "Merge completed shards:",
                "",
                "```powershell",
                "$env:PYTHONPATH='backend'",
                r".\.venv\Scripts\python.exe scripts\merge_w8_retrieval_shards.py",
                "```",
                "",
                "Single-run fallback, only if one operator runs all 10 configs alone:",
                "",
                "```powershell",
                "$env:PYTHONPATH='backend'",
                r".\.venv\Scripts\python.exe scripts\run_eval.py `",
                r"  --manifest configs/w8_abl_01_retrieval_matrix_v2.yaml `",
                r"  --judge-backend gemini `",
                r"  --skip-persistence `",
                r"  --checkpoint-dir benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/checkpoints `",
                r"  --output-dir benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix",
                "```",
                "",
            ]
        )
    lines.append("Re-run this report builder after each phase completes:")
    lines.extend(
        [
            "",
            "```powershell",
            "$env:PYTHONPATH='backend'",
            r".\.venv\Scripts\python.exe scripts\build_final_ablation_report.py",
            "```",
            "",
        ]
    )


def write_markdown(summary: dict[str, Any], output_path: Path) -> None:
    lines: list[str] = [
        "# Final Ablation Report",
        "",
        f"Status: **{summary['status']}**",
        f"Generated UTC: `{summary['generated_at_utc']}`",
        f"Git SHA: `{summary['git_sha']}`",
        "",
        "Git status:",
        "",
        "```text",
        str(summary["git_status_short"]),
        "```",
        "",
        "## Dataset / Identity",
        "",
        "| Dataset | Items | SHA256 |",
        "|---|---:|---|",
        f"| `{summary['dataset']['path']}` | {summary['dataset']['item_count']} | `{summary['dataset']['sha256']}` |",
        "",
        "Notes:",
        "- Official conclusion rows require `judge_backend=gemini`; offline smoke is not used as final evidence.",
        "- Supabase persistence is intentionally non-blocking; local artifacts and checkpoints are the source of truth.",
        "- `Score` is a transparent report heuristic for ranking only, not a replacement for individual metrics.",
        "- `reports_final/10_chunking_strategy_ablation` and `reports_final/11_chunking_prompt_interaction_v1_v2` are immutable source waves for one canonical completed 3×3 Chunking × Prompt factorial matrix.",
        "- No separate prompt/generation phase is active for the current study; prompt evidence is contained in the completed 3×3 matrix.",
        "",
    ]
    append_phase_status(lines, summary)
    append_inventory(lines, summary)
    append_metric_tables(lines, summary)
    append_marginal_tables(lines, summary)
    append_axis_winners(lines, summary)
    append_family_winners(lines, summary)
    append_complexity_winners(lines, summary)
    append_candidate_section(lines, summary)
    append_next_steps(lines, summary)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-dir", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--output", type=Path, default=DEFAULT_MARKDOWN)
    parser.add_argument(
        "--json-output",
        type=Path,
        default=DEFAULT_BASE / "ablation_final_summary.json",
        help="Machine-readable summary path.",
    )
    args = parser.parse_args()

    base_dir = args.base_dir if args.base_dir.is_absolute() else ROOT / args.base_dir
    output = args.output if args.output.is_absolute() else ROOT / args.output
    json_output = args.json_output if args.json_output.is_absolute() else ROOT / args.json_output

    summary = build_summary(base_dir)
    json_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(summary, output)
    print(json.dumps({"status": summary["status"], "markdown": posix(output), "json": posix(json_output)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":  # pragma: no cover - operational script
    raise SystemExit(main())