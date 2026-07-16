# W6 Evaluation report: w7_abl_01_generation_prompt_v1

- Dataset: `D:\University\Năm 3 ĐH\Kì 3 (18th6)\Text Mining\tuvi-battu-graphrag\benchmark\tuvi_golden_dataset\release\tuviqa_v1_release.jsonl`
- Dataset items: 1
- Configs: 3
- Judge backend: `gemini`
- Started: 2026-07-16T07:55:09.976127Z
- Completed: 2026-07-16T07:55:22.579772Z
- Notes: W7-ABL-01 compares generation prompt templates while holding retrieval fixed to the W6 integration candidate: semantic BGE-M3 chunking, Graph + Sparse + RRF + lexical reranker, dense off. Official partial run target is --judge-backend gemini --limit 10 --skip-persistence.

> **Metric policy:** W6-EVAL-02 runs the RAG pipeline directly with the selected `ExperimentConfig`. `Context recall` is the Gemini-judged corpus-grounding score for non-Direct items; Direct/chart-only items are excluded from corpus retrieval/citation metrics and reported through `chart_context_grounding`.

## Overall metrics

| Config | Status | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms | Retrieval p95 ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline_v1_flash_lite | completed | 1 | 1.0 | 1.0 | None | None | None | 2350.56 | None |
| grounded_v2_flash_lite | completed | 1 | 1.0 | 1.0 | None | None | None | 1631.24 | None |
| structured_v3_flash_lite | completed | 1 | 1.0 | 1.0 | None | None | None | 2040.87 | None |

## Ablation analysis

- Baseline config: `baseline_graph_sparse_rrf`
- Preliminary recommendation: `grounded_v2_flash_lite`
  - Preliminary heuristic ranks configs by context recall, citation coverage, faithfulness, answer relevancy, graph hit rate, and a small p95 latency penalty.
  - Selected `grounded_v2_flash_lite` with context_recall_avg=None, citation_coverage_rate=None, p95_latency_ms=1631.24.
  - Treat this as a smoke/first-pass recommendation until official Gemini judge and full dataset runs are complete.

### Context recall ranking

| Rank | Config | Value |
|---:|---|---:|

### Citation coverage ranking

| Rank | Config | Value |
|---:|---|---:|

### Graph hit ranking

| Rank | Config | Value |
|---:|---|---:|

### p95 latency ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | grounded_v2_flash_lite | 1631.24 |
| 2 | structured_v3_flash_lite | 2040.87 |
| 3 | baseline_v1_flash_lite | 2350.56 |

### Retrieval miss summary

| Config | Miss count | Example item IDs |
|---|---:|---|
| baseline_v1_flash_lite | 0 |  |
| grounded_v2_flash_lite | 0 |  |
| structured_v3_flash_lite | 0 |  |

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
- Ứng viên generation sơ bộ: prompt `tuvi_generation_grounded_v2` với model `gemini-3.1-flash-lite-preview` qua config `grounded_v2_flash_lite`
  - Đây là gợi ý sơ bộ cho W7-ABL-01 dựa trên partial run, không phải quyết định production cuối cùng.
  - Điểm ưu tiên Faithfulness, Answer Relevancy, Citation Coverage và Chart Context Grounding; p95 latency bị phạt nhẹ.
  - Ứng viên hiện tại là prompt `tuvi_generation_grounded_v2` với model `gemini-3.1-flash-lite-preview` qua config `grounded_v2_flash_lite`: faithfulness_avg=1.0, answer_relevancy_avg=1.0, citation_coverage_rate=None, p95_latency_ms=1631.24.
  - W7-CONFIG-01 sẽ tổng hợp thêm evidence retrieval/chunking/latency trước khi lock default_production.yaml.

### Xếp hạng theo Faithfulness

| Hạng | Prompt template | Model | Config | Giá trị |
|---:|---|---|---|---:|
| 1 | tuvi_generation_v1 | gemini-3.1-flash-lite-preview | baseline_v1_flash_lite | 1.0 |
| 2 | tuvi_generation_grounded_v2 | gemini-3.1-flash-lite-preview | grounded_v2_flash_lite | 1.0 |
| 3 | tuvi_generation_structured_v3 | gemini-3.1-flash-lite-preview | structured_v3_flash_lite | 1.0 |

### Xếp hạng theo Answer Relevancy

| Hạng | Prompt template | Model | Config | Giá trị |
|---:|---|---|---|---:|
| 1 | tuvi_generation_v1 | gemini-3.1-flash-lite-preview | baseline_v1_flash_lite | 1.0 |
| 2 | tuvi_generation_grounded_v2 | gemini-3.1-flash-lite-preview | grounded_v2_flash_lite | 1.0 |
| 3 | tuvi_generation_structured_v3 | gemini-3.1-flash-lite-preview | structured_v3_flash_lite | 1.0 |

### Xếp hạng theo Citation Coverage

| Hạng | Prompt template | Model | Config | Giá trị |
|---:|---|---|---|---:|

### Xếp hạng theo p95 latency

| Hạng | Prompt template | Model | Config | Giá trị |
|---:|---|---|---|---:|
| 1 | tuvi_generation_grounded_v2 | gemini-3.1-flash-lite-preview | grounded_v2_flash_lite | 1631.24 |
| 2 | tuvi_generation_structured_v3 | gemini-3.1-flash-lite-preview | structured_v3_flash_lite | 2040.87 |
| 3 | tuvi_generation_v1 | gemini-3.1-flash-lite-preview | baseline_v1_flash_lite | 2350.56 |

## Metrics by question complexity

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| baseline_v1_flash_lite | Direct | 1 | 1.0 | 1.0 | None | None | None | 2350.56 |
| grounded_v2_flash_lite | Direct | 1 | 1.0 | 1.0 | None | None | None | 1631.24 |
| structured_v3_flash_lite | Direct | 1 | 1.0 | 1.0 | None | None | None | 2040.87 |

## Metrics by question family

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| baseline_v1_flash_lite | core_identity | 1 | 1.0 | 1.0 | None | None | None | 2350.56 |
| grounded_v2_flash_lite | core_identity | 1 | 1.0 | 1.0 | None | None | None | 1631.24 |
| structured_v3_flash_lite | core_identity | 1 | 1.0 | 1.0 | None | None | None | 2040.87 |

## Per-question results

### baseline_v1_flash_lite

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 2350.56 |  |

### grounded_v2_flash_lite

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1631.24 |  |

### structured_v3_flash_lite

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 2040.87 |  |
