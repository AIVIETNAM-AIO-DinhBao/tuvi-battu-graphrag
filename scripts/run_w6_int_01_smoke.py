"""Chạy smoke integration cho W6-INT-01.

Script này kiểm tra luồng chính ở mức local/backend runtime:

1. GET /health qua FastAPI TestClient.
2. POST /chart/tuvi để tạo lá số Tử Vi thật bằng engine hiện có.
3. Chạy RAG trực tiếp với lá số vừa tạo, Neo4j thật, config candidate và
   deterministic generation để không tiêu Gemini quota ở bước integration.
4. Sinh báo cáo JSON, Markdown và checklist thủ công cho browser flow.

Phần login/Supabase Auth/dashboard/chart detail UI vẫn cần kiểm tra thủ công vì
repo hiện chưa có Playwright/Cypress setup chính thức.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from fastapi.testclient import TestClient  # noqa: E402

from app.clients import get_neo4j_driver  # noqa: E402
from app.main import app  # noqa: E402
from app.rag.config import config_hash, load_experiment_config  # noqa: E402
from app.rag.generation import DeterministicGenerationClient  # noqa: E402
from app.rag.graph import run_rag_dry_run  # noqa: E402


DEFAULT_REPORT_DIR = ROOT_DIR / "benchmark" / "tuvi_golden_dataset" / "reports" / "w6_int_01"
DEFAULT_CONFIG = ROOT_DIR / "configs" / "w6_integration_candidate.yaml"


@dataclass(frozen=True)
class SmokeQuestion:
    id: str
    kind: str
    expected_complexity: str
    question: str
    require_source: bool
    require_citation: bool


QUESTIONS = [
    SmokeQuestion(
        id="factual_chart_fact",
        kind="factual",
        expected_complexity="Direct",
        question="Lá số này có Mệnh ở cung nào và có những sao chính nào?",
        require_source=False,
        require_citation=False,
    ),
    SmokeQuestion(
        id="interpretive_menh",
        kind="interpretive",
        expected_complexity="One-hop",
        question="Mệnh có các sao chính như vậy thì nên hiểu tính cách tổng quan thế nào?",
        require_source=True,
        require_citation=True,
    ),
    SmokeQuestion(
        id="multi_hop_tam_hop_xung_chieu",
        kind="multi-hop",
        expected_complexity="Two-hop",
        question="Hãy xét Mệnh, tam hợp và xung chiếu để nhận định điểm mạnh điểm yếu chính của lá số này.",
        require_source=True,
        require_citation=True,
    ),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Chạy smoke integration W6-INT-01.")
    parser.add_argument(
        "--config",
        default=str(DEFAULT_CONFIG),
        help="Đường dẫn ExperimentConfig candidate dùng cho integration test.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_REPORT_DIR),
        help="Thư mục ghi integration_report.json/md và manual_checklist.md.",
    )
    parser.add_argument(
        "--fail-on-p0",
        action="store_true",
        help="Exit code 1 nếu phát hiện bug P0. Mặc định chỉ ghi report để không che mất bằng chứng bug.",
    )
    return parser.parse_args()


def palace_count(chart_payload: dict[str, Any]) -> int:
    palaces = chart_payload.get("palaces")
    if isinstance(palaces, dict):
        return len(palaces)
    if isinstance(palaces, list):
        return len(palaces)
    chart_data = chart_payload.get("chart_data")
    if isinstance(chart_data, dict):
        nested = chart_data.get("palaces") or chart_data.get("houses") or chart_data.get("cung")
        if isinstance(nested, dict):
            return len(nested)
        if isinstance(nested, list):
            return len(nested)
    return 0


def answer_has_citation(answer: str, sources: list[dict[str, Any]]) -> bool:
    if not sources:
        return False
    markers = [str(source.get("citation_marker") or "").strip() for source in sources]
    markers = [marker for marker in markers if marker]
    return any(f"[{marker}]" in answer or marker in answer for marker in markers)


def severity_summary(bugs: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "P0": sum(1 for bug in bugs if bug.get("severity") == "P0"),
        "P1": sum(1 for bug in bugs if bug.get("severity") == "P1"),
        "P2": sum(1 for bug in bugs if bug.get("severity") == "P2"),
    }


def record_bug(
    bugs: list[dict[str, Any]],
    *,
    severity: str,
    step: str,
    title: str,
    detail: str,
) -> None:
    bugs.append(
        {
            "severity": severity,
            "step": step,
            "title": title,
            "detail": detail,
        }
    )


def run_smoke(config_path: Path, output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    started_at = utc_now()
    started_perf = time.perf_counter()
    config = load_experiment_config(config_path)
    client = TestClient(app)
    bugs: list[dict[str, Any]] = []

    report: dict[str, Any] = {
        "task_id": "W6-INT-01",
        "status": "running",
        "started_at": started_at,
        "config_path": str(config_path),
        "experiment_id": config.experiment_id,
        "config_hash": config_hash(config),
        "chunk_strategy_id": config.chunk_strategy_id,
        "dense_retrieval_enabled": config.dense_retrieval_enabled,
        "retrieval_stack": {
            "graph": config.graph_retrieval_enabled,
            "dense": config.dense_retrieval_enabled,
            "sparse": config.sparse_retrieval_enabled,
            "fusion_method": config.fusion_method,
            "reranker_enabled": config.reranker_enabled,
        },
        "chart_input": {
            "label": "W6 INT 01 Test Chart",
            "birth_date": "1998-03-18",
            "birth_time": "07:30",
            "gender": "male",
            "nam_xem_han": 2026,
        },
        "steps": {},
        "questions": [],
        "bugs": bugs,
    }

    health_started = time.perf_counter()
    try:
        health_resp = client.get("/health")
        health_payload = health_resp.json()
        health_passed = health_resp.status_code == 200 and health_payload.get("status") == "ok"
        report["steps"]["health"] = {
            "passed": health_passed,
            "status_code": health_resp.status_code,
            "latency_ms": round((time.perf_counter() - health_started) * 1000, 2),
            "payload": health_payload,
        }
        if not health_passed:
            record_bug(
                bugs,
                severity="P0",
                step="health",
                title="Backend health không pass",
                detail=f"GET /health trả status={health_resp.status_code}, payload={health_payload}",
            )
    except Exception as exc:  # pragma: no cover - report path for broken local env
        report["steps"]["health"] = {
            "passed": False,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "latency_ms": round((time.perf_counter() - health_started) * 1000, 2),
        }
        record_bug(
            bugs,
            severity="P0",
            step="health",
            title="Không gọi được backend health",
            detail=f"{type(exc).__name__}: {exc}",
        )

    chart_started = time.perf_counter()
    chart_payload: dict[str, Any] = {}
    try:
        chart_resp = client.post("/chart/tuvi", json=report["chart_input"])
        chart_payload = chart_resp.json()
        palaces = palace_count(chart_payload)
        chart_passed = chart_resp.status_code == 200 and chart_payload.get("chart_type") == "TUVI" and palaces >= 12
        report["steps"]["chart_creation"] = {
            "passed": chart_passed,
            "status_code": chart_resp.status_code,
            "latency_ms": round((time.perf_counter() - chart_started) * 1000, 2),
            "chart_type": chart_payload.get("chart_type"),
            "palace_count": palaces,
            "metadata": chart_payload.get("metadata") or {},
        }
        if not chart_passed:
            record_bug(
                bugs,
                severity="P0",
                step="chart_creation",
                title="Tạo lá số không đạt điều kiện integration",
                detail=f"status={chart_resp.status_code}, chart_type={chart_payload.get('chart_type')}, palace_count={palaces}",
            )
    except Exception as exc:  # pragma: no cover - report path for broken local env
        report["steps"]["chart_creation"] = {
            "passed": False,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "latency_ms": round((time.perf_counter() - chart_started) * 1000, 2),
        }
        record_bug(
            bugs,
            severity="P0",
            step="chart_creation",
            title="Không tạo được lá số",
            detail=f"{type(exc).__name__}: {exc}",
        )

    def chart_loader(chart_id: str, user_id: str | None = None) -> dict[str, Any]:
        return {
            "id": chart_id,
            "user_id": user_id,
            "label": report["chart_input"]["label"],
            "chart_system": "TUVI",
            "chart_version": "tuvi-v1",
            "chart_data": chart_payload,
        }

    driver = get_neo4j_driver()
    all_chat_failed = True
    for question in QUESTIONS:
        query_started = time.perf_counter()
        item: dict[str, Any] = {
            "id": question.id,
            "kind": question.kind,
            "expected_complexity": question.expected_complexity,
            "question": question.question,
            "require_source": question.require_source,
            "require_citation": question.require_citation,
        }
        try:
            state = run_rag_dry_run(
                {
                    "chart_id": "w6-int-01-local-chart",
                    "user_id": "w6-int-01-local-user",
                    "query": question.question,
                    "experiment_config_path": str(config_path),
                },
                chart_loader=chart_loader,
                neo4j_driver=driver,
                generation_client=DeterministicGenerationClient(),
                retrieval_fallback_on_error=True,
            )
            answer = str(state.get("answer") or "")
            sources = state.get("sources") or []
            diagnostics = state.get("retrieval_diagnostics") or {}
            generation_metadata = state.get("generation_metadata") or {}
            candidate_counts = {
                "graph": len(state.get("graph_candidates") or []),
                "dense": len(state.get("dense_candidates") or []),
                "sparse": len(state.get("sparse_candidates") or []),
                "fused": len(state.get("fused_candidates") or []),
                "context": len(state.get("context_chunks") or []),
            }
            has_citation = answer_has_citation(answer, sources)
            passed = bool(answer.strip()) and bool(diagnostics)
            if question.require_source:
                passed = passed and len(sources) > 0
            if question.require_citation:
                passed = passed and has_citation
            item.update(
                {
                    "passed": passed,
                    "latency_ms": round((time.perf_counter() - query_started) * 1000, 2),
                    "answer_chars": len(answer),
                    "source_count": len(sources),
                    "has_citation_marker_in_answer": has_citation,
                    "candidate_counts": candidate_counts,
                    "question_family": diagnostics.get("question_family"),
                    "question_complexity": diagnostics.get("question_complexity"),
                    "selected_evidence_roles": diagnostics.get("selected_evidence_roles") or [],
                    "missing_evidence_roles": diagnostics.get("missing_evidence_roles") or [],
                    "final_selected_retrieval_paths": diagnostics.get("final_selected_retrieval_paths") or [],
                    "generation_metadata": generation_metadata,
                    "sample_sources": sources[:3],
                }
            )
            if answer.strip():
                all_chat_failed = False
            if not diagnostics:
                record_bug(
                    bugs,
                    severity="P1",
                    step=question.id,
                    title="Thiếu retrieval diagnostics",
                    detail="RAG response không có retrieval_diagnostics; khó debug integration/evaluation.",
                )
            if question.require_source and len(sources) == 0:
                record_bug(
                    bugs,
                    severity="P1",
                    step=question.id,
                    title="Câu hỏi cần luận giải nhưng không có source",
                    detail="Interpretive/multi-hop query phải có ít nhất một citation source.",
                )
            if question.require_citation and not has_citation:
                record_bug(
                    bugs,
                    severity="P1",
                    step=question.id,
                    title="Answer không hiển thị citation marker",
                    detail="Có thể làm citation panel khó đối chiếu từ câu trả lời.",
                )
            if generation_metadata.get("fallback_reason") == "no_context":
                record_bug(
                    bugs,
                    severity="P1",
                    step=question.id,
                    title="Generation fallback no-context",
                    detail="Pipeline không assemble được context đủ cho câu hỏi integration.",
                )
        except Exception as exc:  # pragma: no cover - report path for live dependency failure
            item.update(
                {
                    "passed": False,
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                    "latency_ms": round((time.perf_counter() - query_started) * 1000, 2),
                }
            )
            record_bug(
                bugs,
                severity="P1",
                step=question.id,
                title="RAG smoke query bị lỗi",
                detail=f"{type(exc).__name__}: {exc}",
            )
        report["questions"].append(item)

    if all_chat_failed:
        record_bug(
            bugs,
            severity="P0",
            step="chat_flow",
            title="Toàn bộ chat integration không có answer",
            detail="Cả 3 câu factual/interpretive/multi-hop đều không trả được answer hợp lệ.",
        )

    report["manual_browser_checklist"] = {
        "status": "pending_manual_verification",
        "path": str(output_dir / "manual_checklist.md"),
        "reason": "Repo chưa có Playwright/Cypress; login Supabase Auth và UI dashboard/chart detail cần kiểm thủ công.",
    }
    report["bug_summary"] = severity_summary(bugs)
    report["completed_at"] = utc_now()
    report["duration_ms"] = round((time.perf_counter() - started_perf) * 1000, 2)
    report["status"] = "pass" if report["bug_summary"]["P0"] == 0 else "blocked"
    report["interpretation_vi"] = (
        "Luồng backend/chart/RAG smoke không có P0; tiếp tục kiểm checklist thủ công cho login/UI."
        if report["status"] == "pass"
        else "Có P0 trong integration smoke; cần xử lý hoặc ghi blocker trước khi qua task sau."
    )
    return report


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Báo cáo integration W6-INT-01",
        "",
        f"- Trạng thái: `{report['status']}`",
        f"- Diễn giải: {report['interpretation_vi']}",
        f"- Bắt đầu: {report['started_at']}",
        f"- Hoàn tất: {report['completed_at']}",
        f"- Thời gian chạy: {report['duration_ms']} ms",
        f"- Config: `{report['config_path']}`",
        f"- Experiment ID: `{report['experiment_id']}`",
        f"- Config hash: `{report['config_hash']}`",
        f"- Chunk strategy: `{report['chunk_strategy_id']}`",
        f"- Dense retrieval: `{report['dense_retrieval_enabled']}`",
        "",
        "## Tóm tắt lỗi",
        "",
        f"- P0: {report['bug_summary']['P0']}",
        f"- P1: {report['bug_summary']['P1']}",
        f"- P2: {report['bug_summary']['P2']}",
        "",
        "## Bước hệ thống",
        "",
        "| Bước | Kết quả | Latency ms | Ghi chú |",
        "|---|---:|---:|---|",
    ]
    for name, step in report.get("steps", {}).items():
        note = ""
        if name == "chart_creation":
            note = f"chart_type={step.get('chart_type')}, palace_count={step.get('palace_count')}"
        elif name == "health":
            note = f"status_code={step.get('status_code')}"
        if step.get("error"):
            note = f"{step.get('error_type')}: {step.get('error')}"
        lines.append(f"| `{name}` | {step.get('passed')} | {step.get('latency_ms')} | {note} |")

    lines.extend(
        [
            "",
            "## Câu hỏi chat/RAG",
            "",
            "| ID | Loại | Pass | Sources | Citation | Complexity | Roles selected | Missing roles | Latency ms |",
            "|---|---|---:|---:|---:|---|---|---|---:|",
        ]
    )
    for item in report.get("questions", []):
        lines.append(
            "| "
            f"`{item.get('id')}` | {item.get('kind')} | {item.get('passed')} | "
            f"{item.get('source_count', 0)} | {item.get('has_citation_marker_in_answer')} | "
            f"{item.get('question_complexity')} | "
            f"{', '.join(item.get('selected_evidence_roles') or [])} | "
            f"{', '.join(item.get('missing_evidence_roles') or [])} | "
            f"{item.get('latency_ms')} |"
        )

    lines.extend(["", "## Danh sách bug P0/P1/P2", ""])
    if report.get("bugs"):
        lines.append("| Severity | Step | Title | Detail |")
        lines.append("|---|---|---|---|")
        for bug in report["bugs"]:
            detail = str(bug.get("detail") or "").replace("|", "\\|")
            title = str(bug.get("title") or "").replace("|", "\\|")
            lines.append(f"| {bug.get('severity')} | `{bug.get('step')}` | {title} | {detail} |")
    else:
        lines.append("Không ghi nhận bug P0/P1/P2 trong automated smoke.")

    lines.extend(
        [
            "",
            "## Kết luận",
            "",
            "Automated smoke kiểm được backend health, chart engine và RAG retrieval/context/citation ở local runtime.",
            "Checklist login/dashboard/chart detail/citation panel cần kiểm thủ công vì dự án chưa có Playwright/Cypress chính thức.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_manual_checklist(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Checklist thủ công W6-INT-01",
            "",
            "## Mục tiêu",
            "Kiểm tra luồng người dùng thật trên browser: login, tạo lá số, xem board, chat và citation panel.",
            "",
            "## Chuẩn bị",
            "",
            "```powershell",
            "cd backend",
            "..\\.venv\\Scripts\\python.exe -m uvicorn app.main:app --reload",
            "```",
            "",
            "```powershell",
            "cd frontend",
            "npm run dev",
            "```",
            "",
            "Mở `http://localhost:3000` và dùng test account Supabase local/cloud hiện có.",
            "",
            "## Config candidate",
            "",
            f"- Config smoke: `{report['config_path']}`",
            f"- Chunk strategy: `{report['chunk_strategy_id']}`",
            "- Lưu ý: frontend chỉ gửi `experiment_config_path` nếu UI/dev payload có field này; nếu không, backend dùng `DEFAULT_EXPERIMENT_CONFIG`.",
            "  Với manual UI test, cần xác nhận biến env hoặc payload đang trỏ đúng candidate nếu muốn test đúng config này.",
            "",
            "## Các bước kiểm",
            "",
            "| Bước | Kỳ vọng | Kết quả thực tế | Bug severity nếu fail |",
            "|---|---|---|---|",
            "| 1. Login | Đăng nhập thành công, vào dashboard protected |  | P0 nếu không login được |",
            "| 2. Tạo lá số | Submit form label/ngày/giờ/giới tính thành công |  | P0 nếu không tạo được |",
            "| 3. Redirect chart detail | Điều hướng sang `/chart/[id]` |  | P0/P1 |",
            "| 4. TuViBoard | Hiển thị đủ 12 cung, không crash responsive desktop |  | P1 nếu sai dữ liệu, P2 nếu layout nhỏ |",
            "| 5. Factual chat | Hỏi Mệnh ở cung nào, trả lời có grounding lá số |  | P1 nếu không trả lời |",
            "| 6. Interpretive chat | Hỏi luận giải Mệnh, có answer tiếng Việt và nguồn nếu dùng corpus |  | P1 nếu không có source/citation |",
            "| 7. Multi-hop chat | Hỏi tam hợp/xung chiếu, diagnostics/answer không no-context |  | P1 nếu retrieval/context miss |",
            "| 8. Citation panel | Source name/page/excerpt hiển thị, click marker mở đúng item |  | P1 nếu không xem được nguồn |",
            "| 9. Error/loading | Loading state rõ, không lộ raw stack trace |  | P1/P2 |",
            "",
            "## Quy tắc severity",
            "",
            "- P0: chặn luồng chính như không login, không tạo lá số, chart detail crash, chat 500 toàn bộ.",
            "- P1: luồng chạy nhưng thiếu source/citation, board sai rõ, multi-hop luôn no-context, latency quá cao.",
            "- P2: lỗi trình bày, wording, loading state chưa mượt nhưng không chặn demo.",
            "",
        ]
    ) + "\n"


def main() -> int:
    args = parse_args()
    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = ROOT_DIR / config_path
    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = ROOT_DIR / output_dir

    report = run_smoke(config_path=config_path, output_dir=output_dir)
    report_path = output_dir / "integration_report.json"
    markdown_path = output_dir / "integration_report.md"
    checklist_path = output_dir / "manual_checklist.md"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    checklist_path.write_text(render_manual_checklist(report), encoding="utf-8")

    print(f"status={report['status']}")
    print(f"bug_summary={report['bug_summary']}")
    print(f"report_json={report_path}")
    print(f"report_md={markdown_path}")
    print(f"manual_checklist={checklist_path}")
    if args.fail_on_p0 and report["bug_summary"]["P0"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())