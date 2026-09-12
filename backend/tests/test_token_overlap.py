from __future__ import annotations

import pytest

from app.rag.token_overlap import aggregate_token_overlap, normalized_tokens, score_token_overlap


def test_normalized_tokens_remove_case_diacritics_and_punctuation() -> None:
    assert normalized_tokens("Cục SINH Mệnh: tốt!") == ["cuc", "sinh", "menh", "tot"]


def test_score_token_overlap_uses_all_spans_and_source_alignment() -> None:
    chunks = [
        {"chunk_id": "chart", "source_id": "CHART", "chunk_type": "chart_facts", "excerpt": "ignored"},
        {"chunk_id": "c1", "source_id": "TVNL", "excerpt": "Cục sinh Mệnh là một trường hợp tốt."},
        {"chunk_id": "c2", "source_id": "TVHS", "excerpt": "Cục sinh Mệnh nhưng thuộc tài liệu khác."},
    ]
    spans = [
        {
            "span_id": "s1",
            "doc_id": "TVNL_001",
            "quote": "Cục sinh Mệnh tạo ra một trường hợp thuận lợi và tốt đẹp.",
            "mapping_status": "unmapped",
        },
        {
            "span_id": "s2",
            "doc_id": "TVGM",
            "quote": "Không có chunk nào cùng nguồn với span này.",
            "mapping_status": "unmapped",
        },
    ]

    result = score_token_overlap(chunks, spans, threshold=0.25)

    assert result["gold_span_count"] == 2
    assert result["context_corpus_chunk_count"] == 2
    assert result["recall_at_8"] == 0.5
    assert result["precision_at_8"] == 0.5
    assert result["f1_at_8"] == 0.5
    assert result["token_overlap_span_details"][0]["hit"] is True
    assert result["token_overlap_span_details"][1]["hit"] is False
    assert result["token_overlap_chunk_details"][0]["relevant"] is True
    assert result["token_overlap_chunk_details"][1]["relevant"] is False


def test_aggregate_token_overlap_is_micro_averaged() -> None:
    rows = [
        {
            "status": "completed",
            "gold_annotation_span_count": 2,
            "token_overlap_threshold": 0.25,
            "token_overlap_span_details": [{"hit": True}, {"hit": False}],
            "token_overlap_chunk_details": [{"relevant": True}],
        },
        {
            "status": "completed",
            "gold_annotation_span_count": 1,
            "token_overlap_threshold": 0.25,
            "token_overlap_span_details": [{"hit": True}],
            "token_overlap_chunk_details": [{"relevant": False}, {"relevant": False}],
        },
        {
            "status": "completed",
            "gold_annotation_span_count": 0,
            "token_overlap_span_details": [],
            "token_overlap_chunk_details": [{"relevant": False}],
        },
    ]

    result = aggregate_token_overlap(rows)

    assert result["token_overlap_gold_span_count"] == 3
    assert result["token_overlap_context_chunk_count"] == 3
    assert result["recall_at_8"] == pytest.approx(2 / 3, abs=1e-6)
    assert result["precision_at_8"] == pytest.approx(1 / 3, abs=1e-6)
    assert result["f1_at_8"] == 0.444444
