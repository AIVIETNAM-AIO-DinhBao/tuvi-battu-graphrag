# Golden Dataset QA 100 Câu cho Benchmark RAG Tử Vi

Đây là thư mục chứa bộ golden benchmark dataset cho hệ thống RAG Tử Vi, được xây dựng theo workplan và guideline chi tiết.

## Cấu trúc thư mục

```text
benchmark/
└── tuvi_golden_dataset/
    ├── workplan.md
    ├── README.md
    ├── guideline/
    │   ├── data-guideline.md
    │   ├── schema_release.json
    │   ├── schema_ops.json
    │   └── source_registry.json
    ├── charts/
    │   ├── chart_registry.json
    │   ├── CHART-001.json
    │   ├── CHART-002.json
    │   ├── CHART-003.json
    │   ├── CHART-004.json
    │   ├── CHART-005.json
    │   ├── CHART-006.json
    │   ├── CHART-007.json
    │   ├── CHART-008.json
    │   ├── CHART-009.json
    │   └── CHART-010.json
    ├── corpus/
    │   ├── TVKL/
    │   │   ├── TVKL_raw_pages.json
    │   │   ├── TVKL_clean_pages.json
    │   │   ├── TVKL_page_map.json
    │   │   ├── TVKL_sections.jsonl
    │   │   └── TVKL_clean.md
    │   ├── TVNL/
    │   │   ├── TVNL_raw_pages.json
    │   │   ├── TVNL_clean_pages.json
    │   │   ├── TVNL_page_map.json
    │   │   ├── TVNL_sections.jsonl
    │   │   └── TVNL_clean.md
    │   ├── TVHS/
    │   │   ├── TVHS_raw_pages.json
    │   │   ├── TVHS_clean_pages.json
    │   │   ├── TVHS_page_map.json
    │   │   ├── TVHS_sections.jsonl
    │   │   └── TVHS_clean.md
    │   └── TVGM/
    │       ├── TVGM_raw_pages.json
    │       ├── TVGM_clean_pages.json
    │       ├── TVGM_page_map.json
    │       ├── TVGM_sections.jsonl
    │       └── TVGM_clean.md
    ├── samples/
    │   ├── question_slots.csv
    │   ├── sample_plan.csv
    │   └── coverage_matrix.xlsx
    ├── drafts/
    │   ├── drafts_questions.jsonl
    │   └── drafts_answers.jsonl
    ├── annotations/
    │   ├── gold_sections_A.jsonl
    │   ├── gold_sections_B.jsonl
    │   ├── gold_sections_C.jsonl
    │   ├── gold_sections.jsonl
    │   ├── golden_candidates_A.jsonl
    │   ├── golden_candidates_B.jsonl
    │   ├── golden_candidates_C.jsonl
    │   ├── golden_candidates.jsonl
    │   └── sentence_span_map.jsonl
    ├── release/
    │   ├── golden_v1_release.jsonl
    │   └── gold_with_chunk_map.jsonl
    ├── reports/
    │   ├── daily_status.md
    │   ├── review_reports.csv
    │   ├── qa_audit.md
    │   └── final_summary.md
    └── scripts/
        ├── build_chart_registry.py
        ├── generate_llm_drafts.py
        ├── map_gold_spans_to_chunks.py
        └── validate_release_schema.py
```
