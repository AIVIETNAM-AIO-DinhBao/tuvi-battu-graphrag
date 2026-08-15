"""Materialize the two completed Phase 52 controls for the hybrid Phase 53 matrix.

This creates a provenance-preserving two-config report rather than copying or
editing raw items manually.  Config rows, item results, and config hashes are
kept exactly as recorded in the completed Phase 52 report.
"""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
SOURCE_REPORT = ROOT / "benchmark" / "tuvi_golden_dataset" / "reports_final" / "52_reranker_top_k_sweep" / "evaluation_report.json"
OUTPUT_DIR = ROOT / "benchmark" / "tuvi_golden_dataset" / "reports_final" / "53_retrieval_fusion_reranker_k40_matrix" / "reused_phase52_controls"
CONTROL_NAMES = ("semantic_gs_rrf_rerank_k40", "semantic_gs_rrf_no_rerank_reference")


def sha256_file(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return payload


def validate_control(row: dict[str, Any]) -> None:
    metrics = row.get("metrics") or {}
    items = row.get("items") or []
    if row.get("status") != "completed":
        raise ValueError(f"Control {row.get('config_name')!r} is not completed")
    if metrics.get("item_count") != 100 or metrics.get("failed_count") != 0:
        raise ValueError(f"Control {row.get('config_name')!r} does not have 100 successful items")
    if len(items) != 100 or any(item.get("status") != "completed" for item in items if isinstance(item, dict)):
        raise ValueError(f"Control {row.get('config_name')!r} contains incomplete item results")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-report", type=Path, default=SOURCE_REPORT)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()
    source_path = args.source_report if args.source_report.is_absolute() else ROOT / args.source_report
    output_dir = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    source = load_json(source_path)
    source_execution = source.get("execution_summary") or {}
    if source.get("status") != "completed" or source.get("judge_backend") != "gemini":
        raise ValueError("Phase 52 source report must be completed and Gemini-judged")
    if source_execution.get("completed_pair_count") != 400 or source_execution.get("failed_pair_count") != 0:
        raise ValueError("Phase 52 source report must contain 400 successful pairs")
    by_name = {row.get("config_name"): row for row in source.get("configs") or [] if isinstance(row, dict)}
    missing = [name for name in CONTROL_NAMES if name not in by_name]
    if missing:
        raise ValueError(f"Missing Phase 52 controls: {missing}")
    controls = [by_name[name] for name in CONTROL_NAMES]
    for control in controls:
        validate_control(control)
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    source_relative = source_path.relative_to(ROOT).as_posix()
    report = {
        "manifest_name": "w8_abl_01_retrieval_fusion_reranker_v3_k40_reused_phase52_controls",
        "notes": "Derived Phase 53 control report. The two config rows and item results are reused verbatim from the completed Phase 52 top-k sweep; source SHA-256 is recorded below.",
        "dataset_path": source.get("dataset_path"),
        "output_dir": output_dir.relative_to(ROOT).as_posix(),
        "started_at": min(str(row.get("started_at")) for row in controls if row.get("started_at")),
        "completed_at": max(str(row.get("completed_at")) for row in controls if row.get("completed_at")),
        "dataset_item_count": 100,
        "config_count": len(controls),
        "judge_backend": "gemini",
        "metric_definitions": source.get("metric_definitions") or {},
        "configs": controls,
        "status": "completed",
        "execution_summary": {
            "expected_pair_count": 200,
            "completed_pair_count": 200,
            "failed_pair_count": 0,
            "executed_pair_count": 0,
            "resumed_pair_count": 200,
        },
        "source_phase52_provenance": {
            "source_report_path": source_relative,
            "source_report_sha256": sha256_file(source_path),
            "source_report_status": source.get("status"),
            "source_execution_summary": source_execution,
            "source_config_names": list(CONTROL_NAMES),
            "materialized_at": now,
            "policy": "Selected config rows and item results are retained verbatim; only enclosing report metadata is derived.",
        },
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "evaluation_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    markdown = "\n".join(
        [
            "# Phase 53 Reused Phase 52 Controls",
            "",
            "This report contains provenance-preserving selected rows from the completed Phase 52 top-k sweep.",
            "",
            f"- Source report: `{source_relative}`",
            f"- Source SHA-256: `{report['source_phase52_provenance']['source_report_sha256']}`",
            "- Judge backend: `gemini`",
            "- Controls: `semantic_gs_rrf_rerank_k40`, `semantic_gs_rrf_no_rerank_reference`",
            "- Completed pairs: `200/200`; failed pairs: `0`.",
            "",
        ]
    )
    (output_dir / "evaluation_report.md").write_text(markdown, encoding="utf-8")
    print(json.dumps({"output_dir": str(output_dir), "completed_pair_count": 200, "source_sha256": report["source_phase52_provenance"]["source_report_sha256"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())