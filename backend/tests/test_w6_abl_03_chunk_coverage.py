from __future__ import annotations

import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = ROOT_DIR / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from check_w6_abl_03_chunk_coverage import (  # noqa: E402
    SOURCES,
    STRATEGIES,
    build_report,
    local_artifact_pairs,
    render_markdown,
)


def test_local_artifact_coverage_reports_all_12_pairs(tmp_path: Path) -> None:
    for strategy in STRATEGIES:
        strategy_dir = tmp_path / strategy
        strategy_dir.mkdir(parents=True)
        for source in SOURCES:
            (strategy_dir / f"{source}_chunks.jsonl").write_text('{"chunk_id":"x"}\n', encoding="utf-8")

    pairs = local_artifact_pairs(tmp_path)
    report = build_report(mode="local-artifacts", pairs=pairs, chunks_dir=tmp_path)
    markdown = render_markdown(report)

    assert report["expected_pair_count"] == 12
    assert report["observed_pair_count"] == 12
    assert report["missing_pair_count"] == 0
    assert report["completed"] is True
    assert "Báo cáo kiểm tra coverage W6-ABL-03" in markdown
    assert "chunk_semantic_embedding_bge_m3" in markdown


def test_local_artifact_coverage_records_missing_pairs(tmp_path: Path) -> None:
    strategy_dir = tmp_path / "chunk_fixed_512"
    strategy_dir.mkdir(parents=True)
    (strategy_dir / "TVKL_chunks.jsonl").write_text('{"chunk_id":"x"}\n', encoding="utf-8")

    pairs = local_artifact_pairs(tmp_path)
    report = build_report(mode="local-artifacts", pairs=pairs, chunks_dir=tmp_path)

    assert report["expected_pair_count"] == 12
    assert report["observed_pair_count"] == 1
    assert report["missing_pair_count"] == 11
    assert report["completed"] is False
    assert {pair["chunk_strategy_id"] for pair in report["missing_pairs"]} >= {
        "chunk_structure_parent_child",
        "chunk_semantic_embedding_bge_m3",
    }