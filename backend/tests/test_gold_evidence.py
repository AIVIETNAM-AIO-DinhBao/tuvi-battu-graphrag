from __future__ import annotations

from app.rag.gold_evidence import aggregate_gold_evidence, score_citation_evidence, score_gold_evidence


def anchor(*, span_id: str = "s1", doc: str = "TVKL", section: str = "SEC1", start: int = 10, end: int = 110):
    return {
        "span_id": span_id,
        "doc_id": doc,
        "corpus_section_id": section,
        "char_start": start,
        "char_end": end,
        "quote": "nội dung bằng chứng tử vi",
    }


def chunk(chunk_id: str, *, doc: str = "TVKL", section: str = "SEC1", start: int, end: int):
    return {
        "chunk_id": chunk_id,
        "source_id": doc,
        "excerpt": "nội dung bằng chứng và phần văn bản khác",
        "provenance": {"source_id": doc, "section_id": section, "char_start": start, "char_end": end},
    }


def test_union_of_chunks_can_cover_one_gold_span() -> None:
    result = score_gold_evidence(
        [chunk("c1", start=0, end=40), chunk("c2", start=40, end=70)],
        [anchor()],
    )

    assert result["gold_span_recall"] == 1.0
    assert result["character_recall"] == 0.6
    assert result["gold_chunk_precision"] == 1.0


def test_wrong_document_or_section_never_matches() -> None:
    result = score_gold_evidence(
        [
            chunk("wrong-doc", doc="TVGM", start=10, end=110),
            chunk("wrong-section", section="SEC2", start=10, end=110),
        ],
        [anchor()],
    )

    assert result["gold_span_recall"] == 0.0
    assert result["gold_chunk_precision"] == 0.0


def test_chart_chunk_is_excluded_from_precision_denominator() -> None:
    chart = {"chunk_id": "chart_facts", "source_id": "CHART", "chunk_type": "chart_facts", "excerpt": "chart"}
    result = score_gold_evidence([chart, chunk("c1", start=10, end=30)], [anchor()])

    assert result["corpus_chunk_count"] == 1
    assert result["gold_chunk_precision"] == 1.0


def test_no_approved_anchors_returns_not_applicable_metrics() -> None:
    result = score_gold_evidence([chunk("c1", start=10, end=30)], [])

    assert result["gold_span_recall"] is None
    assert result["gold_chunk_precision"] is None


def test_citation_evidence_f1_scores_only_explicitly_cited_chunks() -> None:
    first = chunk("c1", start=10, end=110)
    first["citation_marker"] = "S1"
    second = chunk("c2", start=200, end=260)
    second["citation_marker"] = "S2"

    result = score_citation_evidence("Luáº­n giáº£i [S1] vÃ  marker láº¡ [S9].", [first, second], [anchor()])

    assert result["citation_evidence_precision"] == 1.0
    assert result["citation_evidence_recall"] == 1.0
    assert result["citation_evidence_f1"] == 1.0
    assert result["invalid_citation_markers"] == ["S9"]


def test_citation_evidence_f1_is_zero_when_answer_has_no_citation() -> None:
    first = chunk("c1", start=10, end=110)
    first["citation_marker"] = "S1"

    result = score_citation_evidence("Luáº­n giáº£i khÃ´ng cÃ³ marker.", [first], [anchor()])

    assert result["citation_evidence_precision"] == 0.0
    assert result["citation_evidence_recall"] == 0.0
    assert result["citation_evidence_f1"] == 0.0


def test_missing_chunk_coordinates_still_count_in_precision_denominator() -> None:
    missing = {"chunk_id": "missing", "source_id": "TVKL", "excerpt": "không có provenance"}
    result = score_gold_evidence([chunk("mapped", start=10, end=30), missing], [anchor()])

    assert result["corpus_chunk_count"] == 2
    assert result["mapped_corpus_chunk_count"] == 1
    assert result["gold_chunk_precision"] == 0.5


def test_aggregate_uses_only_completed_corpus_items() -> None:
    metrics = aggregate_gold_evidence(
        [
            {
                "status": "completed",
                "chart_only": False,
                "rule_metric_eligible": True,
                "gold_span_recall": 0.5,
                "gold_chunk_precision": 0.25,
                "character_recall": 0.4,
                "character_precision": 0.2,
                "token_recall": 0.6,
                "token_precision": 0.3,
                "retrieval_latency_ms": 100,
                "gold_span_details": [
                    {"covered": True, "covered_chars": 40, "gold_chars": 100},
                    {"covered": False, "covered_chars": 0, "gold_chars": 100},
                ],
                "chunk_details": [
                    {"relevant": True, "coordinate_mapped": True, "overlap_chars": 20, "chunk_chars": 100},
                    {"relevant": False, "coordinate_mapped": True, "overlap_chars": 0, "chunk_chars": 100},
                    {"relevant": False, "coordinate_mapped": True, "overlap_chars": 0, "chunk_chars": 100},
                    {"relevant": False, "coordinate_mapped": True, "overlap_chars": 0, "chunk_chars": 100},
                ],
            },
            {"status": "completed", "chart_only": True, "retrieval_latency_ms": 0},
            {"status": "failed", "chart_only": False},
        ]
    )

    assert metrics["completed_count"] == 2
    assert metrics["failed_count"] == 1
    assert metrics["corpus_grounded_item_count"] == 1
    assert metrics["gold_span_recall_at_8"] == 0.5
    assert metrics["gold_chunk_precision_at_8"] == 0.25
