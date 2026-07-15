"""Kiểm tra độ phủ dữ liệu cho W6-ABL-03 chunking ablation.

Script này kiểm tra đủ 12 cặp nguồn-strategy chính thức:
4 nguồn TVKL/TVNL/TVHS/TVGM x 3 strategy chunking.

Hai chế độ:
- local-artifacts: kiểm tra file JSONL trong benchmark/tuvi_golden_dataset/chunks.
- neo4j: kiểm tra node Chunk trong Neo4j live DB.

Chế độ local-artifacts dùng cho smoke trên laptop. Chế độ neo4j mới là bằng
chứng runtime nên chạy trước official Gemini evaluation khi có env live DB.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


SOURCES = ["TVKL", "TVNL", "TVHS", "TVGM"]
STRATEGIES = [
    "chunk_fixed_512",
    "chunk_structure_parent_child",
    "chunk_semantic_embedding_bge_m3",
]
DEFAULT_CHUNKS_DIR = ROOT_DIR / "benchmark" / "tuvi_golden_dataset" / "chunks"
DEFAULT_OUTPUT_DIR = ROOT_DIR / "benchmark" / "tuvi_golden_dataset" / "reports" / "w6_abl_03"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Kiểm tra coverage 12 cặp source-strategy cho W6-ABL-03.")
    parser.add_argument(
        "--mode",
        choices=["local-artifacts", "neo4j"],
        default="local-artifacts",
        help="local-artifacts dùng cho smoke; neo4j dùng cho bằng chứng runtime chính thức.",
    )
    parser.add_argument("--chunks-dir", type=Path, default=DEFAULT_CHUNKS_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--allow-missing",
        action="store_true",
        help="Vẫn trả exit code 0 nếu thiếu cặp. Dùng cho smoke local khi artifact chưa commit đủ.",
    )
    return parser.parse_args()


def count_jsonl_records(path: Path) -> int:
    if not path.exists():
        return 0
    count = 0
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                count += 1
    return count


def local_artifact_pairs(chunks_dir: Path) -> list[dict[str, Any]]:
    pairs: list[dict[str, Any]] = []
    for strategy in STRATEGIES:
        for source in SOURCES:
            path = chunks_dir / strategy / f"{source}_chunks.jsonl"
            chunk_count = count_jsonl_records(path)
            pairs.append(
                {
                    "source_id": source,
                    "chunk_strategy_id": strategy,
                    "status": "present" if chunk_count > 0 else "missing",
                    "chunk_count": chunk_count,
                    "artifact_path": str(path),
                }
            )
    return pairs


def neo4j_pairs() -> list[dict[str, Any]]:
    from app.clients import get_neo4j_driver  # noqa: WPS433 - imported lazily for local smoke
    from app.config import settings  # noqa: WPS433 - imported lazily for local smoke

    pairs: list[dict[str, Any]] = []
    driver = get_neo4j_driver()
    try:
        with driver.session(database=settings.NEO4J_DATABASE) as session:
            for strategy in STRATEGIES:
                for source in SOURCES:
                    record = session.run(
                        """
                        MATCH (c:Chunk {domain: 'TUVI'})
                        WHERE c.source_id = $source_id
                          AND c.chunk_strategy_id = $chunk_strategy_id
                        RETURN count(c) AS chunk_count
                        """,
                        source_id=source,
                        chunk_strategy_id=strategy,
                    ).single()
                    chunk_count = int(record["chunk_count"] if record else 0)
                    pairs.append(
                        {
                            "source_id": source,
                            "chunk_strategy_id": strategy,
                            "status": "present" if chunk_count > 0 else "missing",
                            "chunk_count": chunk_count,
                        }
                    )
    finally:
        driver.close()
    return pairs


def build_report(*, mode: str, pairs: list[dict[str, Any]], chunks_dir: Path) -> dict[str, Any]:
    missing = [pair for pair in pairs if pair["status"] != "present"]
    return {
        "task_id": "W6-ABL-03",
        "mode": mode,
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "sources": SOURCES,
        "strategies": STRATEGIES,
        "strategy_note_vi": "PLAN.md ghi chunk_semantic_embedding; runtime hiện dùng chunk_semantic_embedding_bge_m3.",
        "chunks_dir": str(chunks_dir),
        "expected_pair_count": len(SOURCES) * len(STRATEGIES),
        "observed_pair_count": len(pairs) - len(missing),
        "missing_pair_count": len(missing),
        "completed": len(missing) == 0,
        "pairs": pairs,
        "missing_pairs": missing,
        "interpretation_vi": (
            "Đủ 12 cặp source-strategy cho W6-ABL-03."
            if not missing
            else "Chưa đủ 12 cặp source-strategy. Nếu đang chạy local-artifacts, đây có thể chỉ là thiếu artifact trong repo; cần chạy lại mode neo4j để xác nhận dữ liệu runtime."
        ),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Báo cáo kiểm tra coverage W6-ABL-03",
        "",
        f"- Chế độ kiểm tra: `{report['mode']}`",
        f"- Thời điểm tạo: {report['created_at']}",
        f"- Số cặp kỳ vọng: {report['expected_pair_count']}",
        f"- Số cặp có dữ liệu: {report['observed_pair_count']}",
        f"- Số cặp thiếu: {report['missing_pair_count']}",
        f"- Kết luận: {report['interpretation_vi']}",
        f"- Ghi chú strategy semantic: {report['strategy_note_vi']}",
        "",
        "## Bảng coverage",
        "",
        "| Nguồn | Chunk strategy | Trạng thái | Số chunk | Artifact path |",
        "|---|---|---:|---:|---|",
    ]
    for pair in report["pairs"]:
        lines.append(
            "| {source} | {strategy} | {status} | {count} | {path} |".format(
                source=pair["source_id"],
                strategy=pair["chunk_strategy_id"],
                status=pair["status"],
                count=pair["chunk_count"],
                path=pair.get("artifact_path", ""),
            )
        )
    if report["missing_pairs"]:
        lines.extend(
            [
                "",
                "## Các cặp còn thiếu",
                "",
                "| Nguồn | Chunk strategy |",
                "|---|---|",
            ]
        )
        for pair in report["missing_pairs"]:
            lines.append(f"| {pair['source_id']} | {pair['chunk_strategy_id']} |")
    lines.extend(
        [
            "",
            "## Cách hiểu kết quả",
            "",
            "- `local-artifacts` chỉ kiểm tra file có trong repo, phù hợp smoke cục bộ.",
            "- `neo4j` kiểm tra dữ liệu runtime thật và nên chạy trước official Gemini evaluation.",
            "- Nếu local-artifacts thiếu nhưng Neo4j đủ, W6-ABL-03 vẫn có thể chạy official vì retrieval đọc từ Neo4j.",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def write_reports(report: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "chunk_strategy_coverage.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (output_dir / "chunk_strategy_coverage.md").write_text(render_markdown(report), encoding="utf-8")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = parse_args()
    pairs = local_artifact_pairs(args.chunks_dir) if args.mode == "local-artifacts" else neo4j_pairs()
    report = build_report(mode=args.mode, pairs=pairs, chunks_dir=args.chunks_dir)
    write_reports(report, args.output_dir)
    print(json.dumps({
        "mode": report["mode"],
        "completed": report["completed"],
        "expected_pair_count": report["expected_pair_count"],
        "observed_pair_count": report["observed_pair_count"],
        "missing_pair_count": report["missing_pair_count"],
        "output_dir": str(args.output_dir),
    }, ensure_ascii=False, indent=2, sort_keys=True))
    if report["completed"] or args.allow_missing:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())