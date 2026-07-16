from __future__ import annotations

from pathlib import Path
from typing import Any

from app.rag.ablation import AblationDatasetItem
from app.rag.config import ExperimentConfig
from app.rag.evaluation import EvaluationJudgeResult, EvaluationRunner, build_single_config_manifest
from app.rag.evaluation_checkpoint import EvaluationCheckpointStore, build_run_identity


ROOT_DIR = Path(__file__).resolve().parents[2]
DATASET_PATH = ROOT_DIR / "benchmark" / "tuvi_golden_dataset" / "release" / "tuviqa_v1_release.jsonl"
CONFIG_PATH = ROOT_DIR / "configs" / "default_production.yaml"


def valid_state() -> dict[str, Any]:
    source = {
        "citation_marker": "S1",
        "chunk_id": "chunk-1",
        "source_id": "TVKL",
        "retrieval_paths": ["graph", "sparse"],
    }
    return {
        "answer": "Câu trả lời có nguồn [S1].",
        "sources": [source],
        "context_chunks": [source],
        "graph_candidates": [source],
        "citation_metadata": {"citation_fallback": False},
        "context_summary": {"selected_count": 1},
        "generation_metadata": {"fallback_reason": None},
        "retrieval_trace": {
            "nodes": [
                {"node": "graph_retrieval", "status": "completed", "duration_ms": 4.0},
                {"node": "sparse_retrieval", "status": "completed", "duration_ms": 3.0},
                {"node": "context_assembly", "status": "completed", "duration_ms": 2.0},
                {"node": "generation", "status": "completed", "duration_ms": 5.0},
            ]
        },
        "retrieval_diagnostics": {
            "candidate_counts": {"graph": 1, "sparse": 1, "fused": 1, "ranked": 1},
            "final_selected_retrieval_paths": ["graph", "sparse"],
        },
    }


class CountingJudge:
    backend = "gemini"

    def __init__(self) -> None:
        self.calls = 0

    def evaluate(
        self,
        *,
        item: AblationDatasetItem,
        state: dict[str, Any],
        config: ExperimentConfig,
    ) -> EvaluationJudgeResult:
        self.calls += 1
        return EvaluationJudgeResult(
            faithfulness=0.9,
            answer_relevancy=0.8,
            context_recall=0.7,
            reasons={},
            backend=self.backend,
            model="test-judge",
        )


def manifest(output_dir: Path):
    return build_single_config_manifest(
        dataset_path=DATASET_PATH,
        config_path=CONFIG_PATH,
        output_dir=output_dir,
    )


def checkpoint_store(tmp_path: Path, *, selected_item_ids: list[str]) -> EvaluationCheckpointStore:
    identity = build_run_identity(
        manifest_name="w6_eval_02_single_config",
        dataset_path=DATASET_PATH,
        config_hashes={"default_production": "c40227a029588b7793201702798e96e640d7a436131d6f5f0437f67151803d96"},
        judge_backend="gemini",
        selected_item_ids=selected_item_ids,
    )
    store = EvaluationCheckpointStore(tmp_path / "checkpoint.json", identity)
    store.load()
    return store


def test_runner_retries_pair_and_records_attempt_metadata(tmp_path: Path) -> None:
    calls = 0

    def flaky_runner(item: AblationDatasetItem, config: ExperimentConfig) -> dict[str, Any]:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise TimeoutError("transient")
        return valid_state()

    report = EvaluationRunner(
        rag_runner=flaky_runner,
        judge=CountingJudge(),
        max_item_attempts=2,
        retry_base_seconds=0,
    ).run(manifest(tmp_path), limit=1, output_dir=tmp_path)

    item = report["configs"][0]["items"][0]
    assert calls == 2
    assert item["status"] == "completed"
    assert item["attempt_count"] == 2
    assert item["attempt_errors"] == ["TimeoutError: transient"]
    assert item["retrieval_latency_ms"] == 9.0
    assert report["status"] == "completed"


def test_generation_backend_fallback_is_failed_without_judging(tmp_path: Path) -> None:
    judge = CountingJudge()

    def fallback_runner(item: AblationDatasetItem, config: ExperimentConfig) -> dict[str, Any]:
        state = valid_state()
        state["generation_metadata"] = {
            "fallback_reason": "generation_backend_error",
            "error_type": "TimeoutError",
            "error_message": "provider timeout",
        }
        return state

    report = EvaluationRunner(rag_runner=fallback_runner, judge=judge).run(
        manifest(tmp_path), limit=1, output_dir=tmp_path
    )

    config = report["configs"][0]
    item = config["items"][0]
    assert judge.calls == 0
    assert item["status"] == "failed"
    assert item["generation_fallback_reason"] == "generation_backend_error"
    assert config["status"] == "failed"
    assert report["status"] == "failed"
    assert report["execution_summary"]["failed_pair_count"] == 1


def test_no_context_result_remains_judgeable(tmp_path: Path) -> None:
    judge = CountingJudge()

    def no_context_runner(item: AblationDatasetItem, config: ExperimentConfig) -> dict[str, Any]:
        state = valid_state()
        state["generation_metadata"] = {"fallback_reason": "no_context"}
        return state

    report = EvaluationRunner(rag_runner=no_context_runner, judge=judge).run(
        manifest(tmp_path), limit=1, output_dir=tmp_path
    )

    metrics = report["configs"][0]["metrics"]
    assert judge.calls == 1
    assert metrics["no_context_count"] == 1
    assert metrics["failed_count"] == 0


def test_runner_resumes_completed_pair_without_rag_or_judge_call(tmp_path: Path) -> None:
    store = checkpoint_store(tmp_path, selected_item_ids=["TVQA-001"])
    first_judge = CountingJudge()
    first = EvaluationRunner(
        rag_runner=lambda item, config: valid_state(),
        judge=first_judge,
        checkpoint_store=store,
    ).run(manifest(tmp_path), limit=1, output_dir=tmp_path / "first")

    def must_not_run(item: AblationDatasetItem, config: ExperimentConfig) -> dict[str, Any]:
        raise AssertionError("completed checkpoint pair was executed again")

    second_judge = CountingJudge()
    resumed_store = EvaluationCheckpointStore(store.path, store.run_identity)
    resumed_store.load()
    second = EvaluationRunner(
        rag_runner=must_not_run,
        judge=second_judge,
        checkpoint_store=resumed_store,
    ).run(manifest(tmp_path), limit=1, output_dir=tmp_path / "second")

    assert first["execution_summary"]["executed_pair_count"] == 1
    assert second_judge.calls == 0
    assert second["execution_summary"]["executed_pair_count"] == 0
    assert second["execution_summary"]["resumed_pair_count"] == 1
    assert second["configs"][0]["items"][0]["result_source"] == "checkpoint"


def test_retry_failed_reexecutes_failed_checkpoint_pair(tmp_path: Path) -> None:
    store = checkpoint_store(tmp_path, selected_item_ids=["TVQA-001"])
    store.record_item(
        "default_production",
        "TVQA-001",
        {
            "item_id": "TVQA-001",
            "status": "failed",
            "error": "TimeoutError: old failure",
            "chart_only": True,
        },
    )
    judge = CountingJudge()
    report = EvaluationRunner(
        rag_runner=lambda item, config: valid_state(),
        judge=judge,
        checkpoint_store=store,
        retry_failed=True,
    ).run(manifest(tmp_path), limit=1, output_dir=tmp_path / "retry")

    item = report["configs"][0]["items"][0]
    assert judge.calls == 1
    assert item["status"] == "completed"
    assert item["result_source"] == "executed"
    assert report["execution_summary"]["executed_pair_count"] == 1
    assert report["execution_summary"]["resumed_pair_count"] == 0
    persisted = store.item_results("default_production", item_ids=["TVQA-001"])[0]
    assert persisted["status"] == "completed"
