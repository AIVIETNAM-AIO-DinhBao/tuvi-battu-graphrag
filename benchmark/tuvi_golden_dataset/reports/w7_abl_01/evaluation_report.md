# W6 Evaluation report: w7_abl_01_generation_prompt_v1

- Dataset: `D:\University\Năm 3 ĐH\Kì 3 (18th6)\Text Mining\tuvi-battu-graphrag\benchmark\tuvi_golden_dataset\release\tuviqa_v1_release.jsonl`
- Dataset items: 10
- Configs: 3
- Judge backend: `gemini`
- Started: 2026-07-16T08:02:38.944780Z
- Completed: 2026-07-16T08:13:58.431780Z
- Notes: W7-ABL-01 compares generation prompt templates while holding retrieval fixed to the W6 integration candidate: semantic BGE-M3 chunking, Graph + Sparse + RRF + lexical reranker, dense off. Official partial run target is --judge-backend gemini --limit 10 --skip-persistence.

> **Metric policy:** W6-EVAL-02 runs the RAG pipeline directly with the selected `ExperimentConfig`. `Context recall` is the Gemini-judged corpus-grounding score for non-Direct items; Direct/chart-only items are excluded from corpus retrieval/citation metrics and reported through `chart_context_grounding`.

## Overall metrics

| Config | Status | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms | Retrieval p95 ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline_v1_flash_lite | completed | 10 | 0.92 | 0.79 | 0.7 | 1.0 | 1.0 | 25911.78 | None |
| grounded_v2_flash_lite | completed | 10 | 0.92 | 0.76 | 0.6444 | 1.0 | 1.0 | 30187.57 | None |
| structured_v3_flash_lite | completed | 10 | 0.67 | 0.52 | 0.3222 | 1.0 | 1.0 | 28321.4 | None |

## Ablation analysis

- Baseline config: `baseline_graph_sparse_rrf`
- Preliminary recommendation: `baseline_v1_flash_lite`
  - Preliminary heuristic ranks configs by context recall, citation coverage, faithfulness, answer relevancy, graph hit rate, and a small p95 latency penalty.
  - Selected `baseline_v1_flash_lite` with context_recall_avg=0.7, citation_coverage_rate=1.0, p95_latency_ms=25911.78.
  - Treat this as a smoke/first-pass recommendation until official Gemini judge and full dataset runs are complete.

### Context recall ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | baseline_v1_flash_lite | 0.7 |
| 2 | grounded_v2_flash_lite | 0.6444 |
| 3 | structured_v3_flash_lite | 0.3222 |

### Citation coverage ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | baseline_v1_flash_lite | 1.0 |
| 2 | grounded_v2_flash_lite | 1.0 |
| 3 | structured_v3_flash_lite | 1.0 |

### Graph hit ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | baseline_v1_flash_lite | 1.0 |
| 2 | grounded_v2_flash_lite | 1.0 |
| 3 | structured_v3_flash_lite | 1.0 |

### p95 latency ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | baseline_v1_flash_lite | 25911.78 |
| 2 | structured_v3_flash_lite | 28321.4 |
| 3 | grounded_v2_flash_lite | 30187.57 |

### Retrieval miss summary

| Config | Miss count | Example item IDs |
|---|---:|---|
| baseline_v1_flash_lite | 2 | TVQA-008, TVQA-010 |
| grounded_v2_flash_lite | 2 | TVQA-008, TVQA-010 |
| structured_v3_flash_lite | 5 | TVQA-003, TVQA-004, TVQA-005, TVQA-008, TVQA-010 |

### Rerank miss summary

| Config | Miss count | Example item IDs |
|---|---:|---|
| baseline_v1_flash_lite | 0 |  |
| grounded_v2_flash_lite | 0 |  |
| structured_v3_flash_lite | 0 |  |

## Phân tích ablation generation prompt/model

- Phạm vi: So sánh prompt template và generation model, giữ retrieval config cố định để cô lập ảnh hưởng generation.
- Retrieval control: Retrieval stack cố định theo W6 integration candidate: chunk_semantic_embedding_bge_m3, Graph + Sparse + RRF + lexical reranker, dense off.
- Chính sách run: Run chính của task này là Gemini judge partial 10 câu balanced; full/expanded run sẽ để W7-CONFIG-01/W8 hoặc khi quota cho phép.
- Prompt templates: `tuvi_generation_grounded_v2, tuvi_generation_structured_v3, tuvi_generation_v1`
- Generation models: `gemini-3.1-flash-lite-preview`
- Ứng viên generation sơ bộ: prompt `tuvi_generation_v1` với model `gemini-3.1-flash-lite-preview` qua config `baseline_v1_flash_lite`
  - Đây là gợi ý sơ bộ cho W7-ABL-01 dựa trên partial run, không phải quyết định production cuối cùng.
  - Điểm ưu tiên Faithfulness, Answer Relevancy, Citation Coverage và Chart Context Grounding; p95 latency bị phạt nhẹ.
  - Ứng viên hiện tại là prompt `tuvi_generation_v1` với model `gemini-3.1-flash-lite-preview` qua config `baseline_v1_flash_lite`: faithfulness_avg=0.92, answer_relevancy_avg=0.79, citation_coverage_rate=1.0, p95_latency_ms=25911.78.
  - W7-CONFIG-01 sẽ tổng hợp thêm evidence retrieval/chunking/latency trước khi lock default_production.yaml.

### Xếp hạng theo Faithfulness

| Hạng | Prompt template | Model | Config | Giá trị |
|---:|---|---|---|---:|
| 1 | tuvi_generation_v1 | gemini-3.1-flash-lite-preview | baseline_v1_flash_lite | 0.92 |
| 2 | tuvi_generation_grounded_v2 | gemini-3.1-flash-lite-preview | grounded_v2_flash_lite | 0.92 |
| 3 | tuvi_generation_structured_v3 | gemini-3.1-flash-lite-preview | structured_v3_flash_lite | 0.67 |

### Xếp hạng theo Answer Relevancy

| Hạng | Prompt template | Model | Config | Giá trị |
|---:|---|---|---|---:|
| 1 | tuvi_generation_v1 | gemini-3.1-flash-lite-preview | baseline_v1_flash_lite | 0.79 |
| 2 | tuvi_generation_grounded_v2 | gemini-3.1-flash-lite-preview | grounded_v2_flash_lite | 0.76 |
| 3 | tuvi_generation_structured_v3 | gemini-3.1-flash-lite-preview | structured_v3_flash_lite | 0.52 |

### Xếp hạng theo Citation Coverage

| Hạng | Prompt template | Model | Config | Giá trị |
|---:|---|---|---|---:|
| 1 | tuvi_generation_v1 | gemini-3.1-flash-lite-preview | baseline_v1_flash_lite | 1.0 |
| 2 | tuvi_generation_grounded_v2 | gemini-3.1-flash-lite-preview | grounded_v2_flash_lite | 1.0 |
| 3 | tuvi_generation_structured_v3 | gemini-3.1-flash-lite-preview | structured_v3_flash_lite | 1.0 |

### Xếp hạng theo p95 latency

| Hạng | Prompt template | Model | Config | Giá trị |
|---:|---|---|---|---:|
| 1 | tuvi_generation_v1 | gemini-3.1-flash-lite-preview | baseline_v1_flash_lite | 25911.78 |
| 2 | tuvi_generation_structured_v3 | gemini-3.1-flash-lite-preview | structured_v3_flash_lite | 28321.4 |
| 3 | tuvi_generation_grounded_v2 | gemini-3.1-flash-lite-preview | grounded_v2_flash_lite | 30187.57 |

## Metrics by question complexity

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| baseline_v1_flash_lite | Direct | 1 | 1.0 | 1.0 | None | None | None | 2398.43 |
| baseline_v1_flash_lite | One-hop | 5 | 0.92 | 0.7 | 0.64 | 1.0 | 1.0 | 23101.93 |
| baseline_v1_flash_lite | Two-hop | 4 | 0.9 | 0.85 | 0.775 | 1.0 | 1.0 | 26590.73 |
| grounded_v2_flash_lite | Direct | 1 | 1.0 | 1.0 | None | None | None | 1504.81 |
| grounded_v2_flash_lite | One-hop | 5 | 0.96 | 0.74 | 0.68 | 1.0 | 1.0 | 24739.22 |
| grounded_v2_flash_lite | Two-hop | 4 | 0.85 | 0.725 | 0.6 | 1.0 | 1.0 | 31124.34 |
| structured_v3_flash_lite | Direct | 1 | 1.0 | 1.0 | None | None | None | 1509.68 |
| structured_v3_flash_lite | One-hop | 5 | 0.62 | 0.44 | 0.24 | 1.0 | 1.0 | 24038.26 |
| structured_v3_flash_lite | Two-hop | 4 | 0.65 | 0.5 | 0.425 | 1.0 | 1.0 | 28417.61 |

## Metrics by question family

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| baseline_v1_flash_lite | core_identity | 1 | 1.0 | 1.0 | None | None | None | 2398.43 |
| baseline_v1_flash_lite | dai_van_interpretation | 1 | 0.8 | 0.2 | 0.2 | 1.0 | 1.0 | 16997.25 |
| baseline_v1_flash_lite | menh_cuc_relation | 1 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 20309.32 |
| baseline_v1_flash_lite | menh_house_interpretation | 1 | 1.0 | 0.8 | 0.8 | 1.0 | 1.0 | 23640.9 |
| baseline_v1_flash_lite | menh_tam_hop | 1 | 1.0 | 0.9 | 0.9 | 1.0 | 1.0 | 26930.2 |
| baseline_v1_flash_lite | menh_xung_chieu | 1 | 1.0 | 0.9 | 0.8 | 1.0 | 1.0 | 24667.05 |
| baseline_v1_flash_lite | special_state_interpretation | 1 | 0.8 | 0.7 | 0.6 | 1.0 | 1.0 | 18433.53 |
| baseline_v1_flash_lite | synthesis_judgement | 1 | 0.6 | 0.7 | 0.4 | 1.0 | 1.0 | 19639.49 |
| baseline_v1_flash_lite | than_cu_interpretation | 1 | 1.0 | 0.8 | 0.6 | 1.0 | 1.0 | 20946.07 |
| baseline_v1_flash_lite | topic_house_plus_relations | 1 | 1.0 | 0.9 | 1.0 | 1.0 | 1.0 | 21511.29 |
| grounded_v2_flash_lite | core_identity | 1 | 1.0 | 1.0 | None | None | None | 1504.81 |
| grounded_v2_flash_lite | dai_van_interpretation | 1 | 0.8 | 0.2 | 0.2 | 1.0 | 1.0 | 16261.04 |
| grounded_v2_flash_lite | menh_cuc_relation | 1 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 21327.2 |
| grounded_v2_flash_lite | menh_house_interpretation | 1 | 1.0 | 0.9 | 1.0 | 1.0 | 1.0 | 25592.23 |
| grounded_v2_flash_lite | menh_tam_hop | 1 | 0.8 | 0.7 | 0.6 | 1.0 | 1.0 | 28470.16 |
| grounded_v2_flash_lite | menh_xung_chieu | 1 | 0.8 | 0.7 | 0.6 | 1.0 | 1.0 | 31592.72 |
| grounded_v2_flash_lite | special_state_interpretation | 1 | 1.0 | 0.8 | 0.6 | 1.0 | 1.0 | 20278.58 |
| grounded_v2_flash_lite | synthesis_judgement | 1 | 0.8 | 0.5 | 0.2 | 1.0 | 1.0 | 18740.67 |
| grounded_v2_flash_lite | than_cu_interpretation | 1 | 1.0 | 0.8 | 0.6 | 1.0 | 1.0 | 19331.99 |
| grounded_v2_flash_lite | topic_house_plus_relations | 1 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 24776.27 |
| structured_v3_flash_lite | core_identity | 1 | 1.0 | 1.0 | None | None | None | 1509.68 |
| structured_v3_flash_lite | dai_van_interpretation | 1 | 0.8 | 0.2 | 0.2 | 1.0 | 1.0 | 14985.27 |
| structured_v3_flash_lite | menh_cuc_relation | 1 | 0.5 | 0.5 | 0.0 | 1.0 | 1.0 | 22731.03 |
| structured_v3_flash_lite | menh_house_interpretation | 1 | 0.8 | 0.7 | 0.6 | 1.0 | 1.0 | 24258.92 |
| structured_v3_flash_lite | menh_tam_hop | 1 | 0.8 | 0.6 | 0.5 | 1.0 | 1.0 | 28465.71 |
| structured_v3_flash_lite | menh_xung_chieu | 1 | 0.8 | 0.6 | 0.5 | 1.0 | 1.0 | 28145.02 |
| structured_v3_flash_lite | special_state_interpretation | 1 | 0.8 | 0.6 | 0.4 | 1.0 | 1.0 | 23155.6 |
| structured_v3_flash_lite | synthesis_judgement | 1 | 0.0 | 0.0 | 0.0 | 1.0 | 1.0 | 19964.96 |
| structured_v3_flash_lite | than_cu_interpretation | 1 | 0.2 | 0.2 | 0.0 | 1.0 | 1.0 | 20272.77 |
| structured_v3_flash_lite | topic_house_plus_relations | 1 | 1.0 | 0.8 | 0.7 | 1.0 | 1.0 | 24604.58 |

## Per-question results

### baseline_v1_flash_lite

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 2398.43 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 3 | 23640.9 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 2 | 20946.07 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 20309.32 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 3 | 18433.53 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 0.9 | True | 1.0 | 4 | 26930.2 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 2 | 24667.05 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.2 | 0.2 | True | 1.0 | 3 | 16997.25 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 21511.29 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.6 | 0.7 | 0.4 | True | 1.0 | 3 | 19639.49 |  |

### grounded_v2_flash_lite

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1504.81 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 2 | 25592.23 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 2 | 19331.99 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 21327.2 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 4 | 20278.58 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 5 | 28470.16 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 3 | 31592.72 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.2 | 0.2 | True | 1.0 | 3 | 16261.04 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 9 | 24776.27 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.5 | 0.2 | True | 1.0 | 6 | 18740.67 |  |

### structured_v3_flash_lite

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1509.68 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 2 | 24258.92 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 0.2 | 0.2 | 0.0 | True | 1.0 | 2 | 20272.77 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 0.5 | 0.5 | 0.0 | True | 1.0 | 3 | 22731.03 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 4 | 23155.6 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 5 | 28465.71 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 6 | 28145.02 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.2 | 0.2 | True | 1.0 | 2 | 14985.27 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 3 | 24604.58 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 5 | 19964.96 |  |
