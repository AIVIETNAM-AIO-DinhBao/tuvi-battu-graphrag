from __future__ import annotations

from pathlib import Path
from typing import Any

from app.rag.ablation import AblationDatasetItem, InMemoryExperimentRunStore, load_ablation_manifest
from app.rag.config import ExperimentConfig
from app.rag.evaluation import (
    EvaluationJudgeResult,
    EvaluationRunner,
    StaticEvaluationJudge,
    aggregate_evaluation_metrics,
    aggregate_grouped_metrics,
    build_single_config_manifest,
    extract_json_object,
    render_markdown_report,
    summarize_evaluation_item,
)


ROOT_DIR = Path(__file__).resolve().parents[2]
RELEASE_DATASET_PATH = ROOT_DIR / "benchmark" / "tuvi_golden_dataset" / "release" / "tuviqa_v1_release.jsonl"
DEFAULT_CONFIG_PATH = ROOT_DIR / "configs" / "default_production.yaml"
W6_BASELINE_MANIFEST = ROOT_DIR / "configs" / "w6_eval_baseline.yaml"


def fake_state(item: AblationDatasetItem, config: ExperimentConfig) -> dict[str, Any]:
    context_chunks = [
        {
            "citation_marker": "S1",
            "chunk_id": f"chunk-{item.id}",
            "chunk_hash": f"hash-{item.id}",
            "chunk_strategy_id": config.chunk_strategy_id,
            "source_id": "TVKL",
            "source_name": "Tử Vi Khảo Luận",
            "source_page": 8,
            "excerpt": "Tương sinh thì hợp cách và tốt đẹp, tương khắc thì sái cách và tầm thường.",
            "retrieval_paths": ["graph", "sparse"],
        }
    ]
    return {
        "answer": f"Câu trả lời đánh giá cho {item.id} dựa trên nguồn [S1].",
        "sources": context_chunks,
        "context_chunks": context_chunks,
        "graph_candidates": [{"chunk_id": f"chunk-{item.id}"}],
        "citation_metadata": {"citation_fallback": False, "source_count": 1},
        "context_summary": {"selected_count": 1},
        "retrieval_trace": {
            "nodes": [
                {"node": "graph_retrieval", "status": "completed", "duration_ms": 100.0},
                {"node": "sparse_retrieval", "status": "completed", "duration_ms": 50.0},
                {"node": "generation", "status": "completed"},
            ]
        },
    }


class FixedJudge:
    backend = "gemini"

    def evaluate(
        self,
        *,
        item: AblationDatasetItem,
        state: dict[str, Any],
        config: ExperimentConfig,
    ) -> EvaluationJudgeResult:
        return EvaluationJudgeResult(
            faithfulness=0.8,
            answer_relevancy=0.7,
            context_recall=0.6,
            reasons={
                "faithfulness": "supported enough",
                "answer_relevancy": "answers the question",
                "context_recall": "some evidence present",
            },
            backend="gemini",
            model="fake-gemini",
            raw_response='{"faithfulness": 0.8}',
        )


def test_extract_json_object_accepts_plain_and_fenced_json() -> None:
    assert extract_json_object('{"faithfulness": 0.8}')["faithfulness"] == 0.8

    fenced = "```json\n{\"answer_relevancy\": 0.75, \"context_recall\": 1}\n```"
    payload = extract_json_object(fenced)

    assert payload["answer_relevancy"] == 0.75
    assert payload["context_recall"] == 1


def test_summarize_item_excludes_chart_only_from_corpus_metrics() -> None:
    manifest = load_ablation_manifest(ROOT_DIR / "configs" / "w4_ablation_smoke.yaml")
    config = manifest.configs[0].build_config()
    chart_only_item = AblationDatasetItem(
        id="direct",
        chart_id="chart-1",
        query="Cung Mệnh ở đâu?",
        chart_data={"chart_type": "TUVI"},
        expected_answer_summary="Cung Mệnh nằm tại Ngọ.",
        question_complexity="Direct",
        labels={"question_family": "core_identity"},
    )

    result = summarize_evaluation_item(
        chart_only_item,
        fake_state(chart_only_item, config),
        EvaluationJudgeResult(0.9, 0.8, 0.7, backend="gemini"),
        latency_ms=123.4,
    )

    assert result["chart_only"] is True
    assert result["context_recall"] is None
    assert result["chart_context_grounding"] == 0.7
    assert result["graph_hit"] is None
    assert result["citation_coverage"] is None


def test_aggregate_metrics_and_groups_use_w6_metric_names() -> None:
    items = [
        {
            "status": "completed",
            "chart_only": True,
            "answer_present": True,
            "faithfulness": 0.9,
            "answer_relevancy": 0.8,
            "context_recall": None,
            "chart_context_grounding": 0.7,
            "graph_hit": None,
            "citation_coverage": None,
            "source_count": 0,
            "latency_ms": 100.0,
            "retrieval_latency_ms": None,
            "context_selected_count": 0,
            "question_complexity": "Direct",
            "question_family": "core_identity",
        },
        {
            "status": "completed",
            "chart_only": False,
            "answer_present": True,
            "faithfulness": 0.7,
            "answer_relevancy": 0.6,
            "context_recall": 0.5,
            "chart_context_grounding": None,
            "graph_hit": True,
            "citation_coverage": 1.0,
            "source_count": 2,
            "latency_ms": 300.0,
            "retrieval_latency_ms": 120.0,
            "context_selected_count": 2,
            "question_complexity": "One-hop",
            "question_family": "menh_house_interpretation",
        },
    ]

    metrics = aggregate_evaluation_metrics(items, expected_item_count=2)
    groups = aggregate_grouped_metrics(items)

    assert metrics["faithfulness_avg"] == 0.8
    assert metrics["answer_relevancy_avg"] == 0.7
    assert metrics["context_recall_avg"] == 0.5
    assert metrics["chart_context_grounding_avg"] == 0.7
    assert metrics["graph_hit_rate"] == 1.0
    assert metrics["citation_coverage_rate"] == 1.0
    assert metrics["corpus_grounded_item_count"] == 1
    assert metrics["corpus_source_coverage_rate"] == 1.0
    assert metrics["citation_marker_presence_rate"] == 0.0
    assert metrics["citation_source_alignment_rate"] == 0.0
    assert metrics["p95_latency_ms"] == 290.0
    assert groups["by_question_complexity"]["Direct"]["chart_only_count"] == 1
    assert groups["by_question_family"]["menh_house_interpretation"]["context_recall_avg"] == 0.5


def test_w6_eval_baseline_manifest_loads_release_dataset_and_default_config() -> None:
    manifest = load_ablation_manifest(W6_BASELINE_MANIFEST)
    config = manifest.configs[0].build_config()

    assert manifest.name == "w6_eval_02_baseline"
    assert manifest.dataset_path == RELEASE_DATASET_PATH
    assert manifest.output_dir == ROOT_DIR / "benchmark" / "tuvi_golden_dataset" / "reports" / "w6_eval_02"
    assert manifest.configs[0].name == "default_production_baseline"
    assert config.experiment_id == "w6_eval_02_default_production_baseline"
    assert config.cache_disabled is True


def test_evaluation_runner_writes_reports_and_experiment_rows(tmp_path: Path) -> None:
    manifest = build_single_config_manifest(
        dataset_path=RELEASE_DATASET_PATH,
        config_path=DEFAULT_CONFIG_PATH,
        output_dir=tmp_path,
    )
    store = InMemoryExperimentRunStore()
    calls: list[str] = []

    def runner(item: AblationDatasetItem, config: ExperimentConfig) -> dict[str, Any]:
        calls.append(item.id)
        return fake_state(item, config)

    report = EvaluationRunner(run_store=store, rag_runner=runner, judge=FixedJudge()).run(
        manifest,
        limit=2,
        output_dir=tmp_path,
    )

    assert calls == ["TVQA-001", "TVQA-002"]
    assert report["judge_backend"] == "gemini"
    assert report["dataset_item_count"] == 2
    assert report["configs"][0]["metrics"]["faithfulness_avg"] == 0.8
    assert "by_question_complexity" in report["configs"][0]["grouped_metrics"]
    assert len(store.rows) == 1
    assert store.rows[0]["status"] == "completed"
    assert store.rows[0]["metrics"]["answer_relevancy_avg"] == 0.7
    assert (tmp_path / "evaluation_report.json").exists()
    assert (tmp_path / "evaluation_report.md").exists()


def test_static_judge_is_marked_as_non_official_in_markdown(tmp_path: Path) -> None:
    report = {
        "manifest_name": "static-smoke",
        "dataset_path": "dataset.jsonl",
        "dataset_item_count": 1,
        "config_count": 1,
        "judge_backend": StaticEvaluationJudge.backend,
        "started_at": "start",
        "completed_at": "done",
        "configs": [
            {
                "config_name": "config",
                "status": "completed",
                "metrics": aggregate_evaluation_metrics([], expected_item_count=0),
                "grouped_metrics": {"by_question_complexity": {}, "by_question_family": {}},
                "items": [],
            }
        ],
    }

    markdown = render_markdown_report(report)

    assert "not an official W6 metric run" in markdown
    assert "Overall metrics" in markdown