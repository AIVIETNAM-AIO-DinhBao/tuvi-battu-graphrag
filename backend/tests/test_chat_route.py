from __future__ import annotations

from typing import Any

from fastapi.testclient import TestClient

import app.main as main_module
from app.rag.config import load_experiment_config


client = TestClient(main_module.app)


def test_chat_route_returns_answer_sources_and_trace(monkeypatch) -> None:
    config = load_experiment_config()

    class FakeLangfuse:
        def log_event(self, event_name: str, payload: dict[str, Any]) -> None:
            return None

    def fake_run_rag_dry_run(initial_state: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        assert initial_state["chart_id"] == "chart-1"
        assert initial_state["query"] == "Thiên Mã tại Quan Lộc thế nào?"
        assert kwargs["neo4j_driver"] is main_module.neo4j_driver
        assert kwargs["retrieval_fallback_on_error"] is True
        return {
            "answer": "Thiên Mã tại Quan Lộc cần xét nguồn [S1].",
            "sources": [
                {
                    "citation_marker": "S1",
                    "chunk_id": "chunk-1",
                    "chunk_hash": "hash-1",
                    "chunk_strategy_id": config.chunk_strategy_id,
                    "excerpt": "Thiên Mã tại Quan Lộc...",
                    "source_id": "TVKL",
                    "source_name": "Tử Vi Khảo Luận",
                    "source_page": 12,
                }
            ],
            "retrieval_trace": {"nodes": [{"node": "generation", "status": "completed"}]},
            "retrieval_diagnostics": {
                "question_complexity": "One-hop",
                "question_family": "topic_house_plus_relations",
                "candidate_counts": {"graph": 1, "dense": 0, "sparse": 1, "fused": 1},
                "final_selected_retrieval_paths": ["graph"],
            },
            "experiment_id": config.experiment_id,
            "config_hash": "hash-test",
            "experiment_config": config,
            "generation_metadata": {"generation_model": "deterministic-test"},
            "citation_metadata": {"source_count": 1},
        }

    monkeypatch.setattr(main_module, "run_rag_dry_run", fake_run_rag_dry_run)
    monkeypatch.setattr(main_module, "langfuse", FakeLangfuse())

    response = client.post(
        "/chat",
        json={
            "chart_id": "chart-1",
            "query": "Thiên Mã tại Quan Lộc thế nào?",
            "user_id": "user-1",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["answer"]
    assert payload["sources"][0]["chunk_id"] == "chunk-1"
    assert payload["trace"]["nodes"][0]["node"] == "generation"
    assert payload["retrieval_diagnostics"]["question_family"] == "topic_house_plus_relations"
    assert payload["retrieval_diagnostics"]["candidate_counts"]["graph"] == 1
    assert payload["experiment_id"] == config.experiment_id
    assert payload["chunk_strategy_id"] == config.chunk_strategy_id


def test_chat_route_uses_supplied_chart_data_without_loading_supabase(monkeypatch) -> None:
    supplied_chart = {
        "chart_type": "TUVI",
        "palaces": {"MENH": {"name": "Mệnh", "stars": ["Tử Vi"]}},
    }

    def fail_remote_chart_load(chart_id: str, user_id: str | None = None) -> dict[str, Any]:
        raise AssertionError("Supabase chart loader must not run when chart_data is supplied")

    def fake_run_rag_dry_run(initial_state: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        loaded = kwargs["chart_loader"](initial_state["chart_id"], initial_state.get("user_id"))
        assert loaded == {"chart_system": "TUVI", "chart_data": supplied_chart}
        return {
            "answer": "Lá số đã được nhận trực tiếp.",
            "sources": [],
            "retrieval_trace": {},
            "retrieval_diagnostics": {},
            "experiment_id": "test",
            "config_hash": "hash-test",
            "experiment_config": load_experiment_config(),
            "generation_metadata": {},
            "citation_metadata": {},
        }

    monkeypatch.setattr(main_module, "resilient_chart_loader", fail_remote_chart_load)
    monkeypatch.setattr(main_module, "run_rag_dry_run", fake_run_rag_dry_run)

    response = client.post(
        "/chat",
        json={
            "chart_id": "chart-1",
            "query": "Luận giải cung Mệnh",
            "user_id": "user-1",
            "chart_data": supplied_chart,
        },
    )

    assert response.status_code == 200
    assert response.json()["answer"] == "Lá số đã được nhận trực tiếp."
