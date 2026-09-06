from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from .common import (
    BUNDLE_SCHEMA_VERSION,
    assert_no_secret_keys,
    atomic_write_json,
    iter_json_records,
    sha256_file,
    sha256_text,
    stable_pair_id,
    write_jsonl_atomic,
)


SUITE_NAME = "model_only"
CONFIG_NAME = "question_chart_direct"
CONFIG_KEY = f"{SUITE_NAME}::{CONFIG_NAME}"
PROMPT_TEMPLATE_ID = "tuvi_model_only_direct_v0"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_model_only_prompt(item: dict[str, Any]) -> str:
    """Build the shared minimal prompt without retrieval or derived chart features."""
    query = str(item.get("query") or item.get("question") or "").strip()
    chart_data = item.get("chart_data") or item.get("chart_repr")
    birth_info = item.get("birth_info") or {}
    if not query:
        raise ValueError("Dataset item requires a non-empty query/question")
    if not isinstance(chart_data, dict) or not chart_data:
        raise ValueError(f"Dataset item {item.get('id')} requires chart_data/chart_repr")
    input_payload = {
        "birth_info": birth_info if isinstance(birth_info, dict) else {},
        "chart": chart_data,
    }
    chart_json = json.dumps(input_payload, ensure_ascii=False, sort_keys=True, indent=2)
    return (
        "Bạn là trợ lý trả lời câu hỏi về Tử Vi.\n"
        "Hãy trả lời trực tiếp bằng tiếng Việt dựa trên câu hỏi và dữ liệu lá số bên dưới. "
        "Không bịa thêm dữ kiện về lá số; nếu dữ liệu không đủ thì nói rõ giới hạn.\n\n"
        f"DỮ LIỆU LÁ SỐ:\n{chart_json}\n\n"
        f"CÂU HỎI:\n{query}\n\n"
        "TRẢ LỜI:"
    )


def item_payload(payload: dict[str, Any], *, line_number: int) -> dict[str, Any]:
    item_id = str(payload.get("id") or f"item-{line_number:04d}").strip()
    query = str(payload.get("query") or payload.get("question") or "").strip()
    chart_id = str(payload.get("chart_id") or "").strip()
    chart_data = payload.get("chart_data") or payload.get("chart_repr")
    if not query or not chart_id or not isinstance(chart_data, dict) or not chart_data:
        raise ValueError(f"Invalid model-only dataset item at record {line_number}: {item_id}")
    reserved = {
        "id",
        "query",
        "question",
        "chart_id",
        "user_id",
        "chart_data",
        "chart_repr",
        "gold_answer",
        "expected_answer_summary",
        "gold_context_spans",
        "gold_spans",
        "labels",
        "question_complexity",
        "birth_info",
        "metadata",
    }
    metadata = dict(payload.get("metadata") or {})
    metadata.update({key: value for key, value in payload.items() if key not in reserved})
    return {
        "id": item_id,
        "query": query,
        "chart_id": chart_id,
        "user_id": payload.get("user_id"),
        "chart_data": chart_data,
        "gold_answer": payload.get("gold_answer"),
        "expected_answer_summary": payload.get("expected_answer_summary"),
        "gold_context_spans": payload.get("gold_context_spans") or payload.get("gold_spans") or [],
        "labels": payload.get("labels") or {},
        "question_complexity": payload.get("question_complexity"),
        "birth_info": payload.get("birth_info") or {},
        "metadata": metadata,
    }


def model_only_config(repo_root: Path) -> dict[str, Any]:
    config_path = repo_root / "configs" / "default_production.yaml"
    payload = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    payload.update(
        {
            "experiment_id": "model_only_question_chart_direct",
            "name": "Model only - question and raw chart",
            "branch": "local-kaggle",
            "query_rewrite_enabled": False,
            "entity_extraction_enabled": False,
            "graph_retrieval_enabled": False,
            "dense_retrieval_enabled": False,
            "sparse_retrieval_enabled": False,
            "document_grading_enabled": False,
            "prompt_template_id": PROMPT_TEMPLATE_ID,
            "generation_model": "offline-local-llm",
            "cache_disabled": True,
        }
    )
    reranker = dict(payload.get("reranker_config") or {})
    reranker["enabled"] = False
    payload["reranker_config"] = reranker
    return payload


def build_model_only_bundle(config: dict[str, Any]) -> dict[str, Any]:
    repo_root = Path(config["repo_root"]).expanduser().resolve()
    dataset_path = Path(
        config.get("dataset_path")
        or repo_root / "benchmark" / "tuvi_golden_dataset" / "release" / "tuviqa_v1_release.jsonl"
    ).expanduser().resolve()
    output_dir = Path(config["output_dir"]).expanduser().resolve()
    limit = config.get("item_limit")
    if not dataset_path.exists():
        raise FileNotFoundError(dataset_path)

    raw_items = list(iter_json_records(dataset_path))
    if limit is not None:
        raw_items = raw_items[: int(limit)]
    if not raw_items:
        raise RuntimeError("Model-only bundle has no dataset items")

    items: list[dict[str, Any]] = []
    cases: list[dict[str, Any]] = []
    for index, raw_item in enumerate(raw_items, start=1):
        item = item_payload(raw_item, line_number=index)
        prompt = build_model_only_prompt(item)
        pair_id = stable_pair_id(SUITE_NAME, CONFIG_NAME, item["id"], sha256_text(prompt))
        items.append(item)
        cases.append(
            {
                "schema_version": BUNDLE_SCHEMA_VERSION,
                "status": "completed",
                "pair_id": pair_id,
                "suite": SUITE_NAME,
                "config_key": CONFIG_KEY,
                "item_id": item["id"],
                "prompt": prompt,
                "prompt_sha256": sha256_text(prompt),
                "bundle_build_latency_ms": 0.0,
                "state": {
                    "query": item["query"],
                    "chart_id": item["chart_id"],
                    "chart_data": item["chart_data"],
                    "final_context": "",
                    "context_chunks": [],
                    "retrieval_trace": [],
                    "retrieval_diagnostics": {
                        "baseline_type": "model_only",
                        "retrieval_executed": False,
                    },
                },
            }
        )

    config_payload = model_only_config(repo_root)
    config_record = {
        "config_key": CONFIG_KEY,
        "suite": SUITE_NAME,
        "manifest_name": "model_only_v1",
        "manifest_path": None,
        "config_name": CONFIG_NAME,
        "source_config_hash": None,
        "bundle_config_hash": sha256_text(
            json.dumps(config_payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        ),
        "config": config_payload,
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl_atomic(output_dir / "items.jsonl", items)
    write_jsonl_atomic(output_dir / "configs.jsonl", [config_record])
    write_jsonl_atomic(output_dir / "cases.jsonl", cases)
    manifest = {
        "schema_version": BUNDLE_SCHEMA_VERSION,
        "bundle_type": "model_only_question_plus_raw_chart",
        "created_at": utc_now(),
        "repo_root_name": repo_root.name,
        "selected_suites": [SUITE_NAME],
        "item_limit": limit,
        "item_count": len(items),
        "config_count": 1,
        "planned_pair_count": len(cases),
        "completed_pair_count": len(cases),
        "failed_pair_count": 0,
        "is_complete": True,
        "retrieval_executed": False,
        "derived_chart_features_used": False,
        "corpus_context_used": False,
        "prompt_template_id": PROMPT_TEMPLATE_ID,
        "files": {
            "items": {"name": "items.jsonl", "sha256": sha256_file(output_dir / "items.jsonl")},
            "configs": {"name": "configs.jsonl", "sha256": sha256_file(output_dir / "configs.jsonl")},
            "cases": {"name": "cases.jsonl", "sha256": sha256_file(output_dir / "cases.jsonl")},
        },
        "metric_note": (
            "This baseline has no retrieval candidates or book citations. Retrieval and citation metrics are "
            "not applicable; compare generation-quality metrics only."
        ),
    }
    assert_no_secret_keys(manifest)
    atomic_write_json(output_dir / "bundle_manifest.json", manifest)
    return manifest

