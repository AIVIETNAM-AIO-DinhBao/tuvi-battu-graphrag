# W6 Evaluation report: w8_abl_02_chunking_prompt_interaction_v1_v2

- Dataset: `D:\University\Năm 3 ĐH\Kì 3 (18th6)\Text Mining\tuvi-battu-graphrag\benchmark\tuvi_golden_dataset\release\tuviqa_v1_release.jsonl`
- Dataset items: 2
- Configs: 6
- Judge backend: `static-smoke`
- Started: 2026-07-29T01:33:05.577009Z
- Completed: 2026-07-29T01:33:06.941345Z
- Notes: W8-ABL-02 completes the chunking x prompt interaction study by running the two prompt templates not covered by the completed W6/W8 prompt-v3 chunking ablation. Holds retrieval fixed to Graph + Sparse + RRF + BGE reranker, dense off, balanced context assembly, document grading on, Gemini Flash Lite generation. Main variables: chunk_strategy_id in {chunk_fixed_512, chunk_structure_parent_child, chunk_semantic_embedding_bge_m3} and prompt_template_id in {tuvi_generation_v1, tuvi_generation_grounded_v2}. Combine with reports_final/10_chunking_strategy_ablation for the full 3 chunking x 3 prompt matrix.
- Run status: `completed`

## Execution completeness

- Expected pairs: 12
- Completed pairs: 12
- Failed pairs: 0
- Executed pairs: 12
- Resumed pairs: 0

> **Caveat:** This is not an official W6 metric run because RAGAS-like metrics were not judged by Gemini.

> **Metric policy:** W6-EVAL-02 runs the RAG pipeline directly with the selected `ExperimentConfig`. `Context recall` is the Gemini-judged corpus-grounding score for non-Direct items; Direct/chart-only items are excluded from corpus retrieval/citation metrics and reported through `chart_context_grounding`.

## Overall metrics

| Config | Status | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms | Retrieval p95 ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| fixed_512_prompt_v1_graph_sparse_rrf | completed | 2 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 176.44 | 1.44 |
| parent_child_prompt_v1_graph_sparse_rrf | completed | 2 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 111.93 | 0.6 |
| semantic_bge_m3_prompt_v1_graph_sparse_rrf | completed | 2 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 127.14 | 0.59 |
| fixed_512_prompt_v2_graph_sparse_rrf | completed | 2 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 92.63 | 0.58 |
| parent_child_prompt_v2_graph_sparse_rrf | completed | 2 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 98.27 | 0.6 |
| semantic_bge_m3_prompt_v2_graph_sparse_rrf | completed | 2 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 98.75 | 0.61 |

## Failure and fallback summary

| Config | Failed | Generation backend fallback | Judge failure | No context | Retrieval backend fallback | Citation fallback |
|---|---:|---:|---:|---:|---:|---:|
| fixed_512_prompt_v1_graph_sparse_rrf | 0 | 0 | 0 | 0 | 0 | 0 |
| parent_child_prompt_v1_graph_sparse_rrf | 0 | 0 | 0 | 0 | 0 | 0 |
| semantic_bge_m3_prompt_v1_graph_sparse_rrf | 0 | 0 | 0 | 0 | 0 | 0 |
| fixed_512_prompt_v2_graph_sparse_rrf | 0 | 0 | 0 | 0 | 0 | 0 |
| parent_child_prompt_v2_graph_sparse_rrf | 0 | 0 | 0 | 0 | 0 | 0 |
| semantic_bge_m3_prompt_v2_graph_sparse_rrf | 0 | 0 | 0 | 0 | 0 | 0 |

## Ablation analysis

- Baseline config: `baseline_graph_sparse_rrf`
- Preliminary recommendation: `fixed_512_prompt_v2_graph_sparse_rrf`
  - Preliminary heuristic ranks configs by context recall, citation coverage, faithfulness, answer relevancy, graph hit rate, and a small p95 latency penalty.
  - Selected `fixed_512_prompt_v2_graph_sparse_rrf` with context_recall_avg=1.0, citation_coverage_rate=0.75, p95_latency_ms=92.63.
  - Treat this as a smoke/first-pass recommendation until official Gemini judge and full dataset runs are complete.

### Context recall ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | fixed_512_prompt_v1_graph_sparse_rrf | 1.0 |
| 2 | parent_child_prompt_v1_graph_sparse_rrf | 1.0 |
| 3 | semantic_bge_m3_prompt_v1_graph_sparse_rrf | 1.0 |
| 4 | fixed_512_prompt_v2_graph_sparse_rrf | 1.0 |
| 5 | parent_child_prompt_v2_graph_sparse_rrf | 1.0 |
| 6 | semantic_bge_m3_prompt_v2_graph_sparse_rrf | 1.0 |

### Citation coverage ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | fixed_512_prompt_v1_graph_sparse_rrf | 0.75 |
| 2 | parent_child_prompt_v1_graph_sparse_rrf | 0.75 |
| 3 | semantic_bge_m3_prompt_v1_graph_sparse_rrf | 0.75 |
| 4 | fixed_512_prompt_v2_graph_sparse_rrf | 0.75 |
| 5 | parent_child_prompt_v2_graph_sparse_rrf | 0.75 |
| 6 | semantic_bge_m3_prompt_v2_graph_sparse_rrf | 0.75 |

### Graph hit ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | fixed_512_prompt_v1_graph_sparse_rrf | 0.0 |
| 2 | parent_child_prompt_v1_graph_sparse_rrf | 0.0 |
| 3 | semantic_bge_m3_prompt_v1_graph_sparse_rrf | 0.0 |
| 4 | fixed_512_prompt_v2_graph_sparse_rrf | 0.0 |
| 5 | parent_child_prompt_v2_graph_sparse_rrf | 0.0 |
| 6 | semantic_bge_m3_prompt_v2_graph_sparse_rrf | 0.0 |

### p95 latency ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | fixed_512_prompt_v2_graph_sparse_rrf | 92.63 |
| 2 | parent_child_prompt_v2_graph_sparse_rrf | 98.27 |
| 3 | semantic_bge_m3_prompt_v2_graph_sparse_rrf | 98.75 |
| 4 | parent_child_prompt_v1_graph_sparse_rrf | 111.93 |
| 5 | semantic_bge_m3_prompt_v1_graph_sparse_rrf | 127.14 |
| 6 | fixed_512_prompt_v1_graph_sparse_rrf | 176.44 |

### Retrieval miss summary

| Config | Miss count | Example item IDs |
|---|---:|---|
| fixed_512_prompt_v1_graph_sparse_rrf | 1 | TVQA-002 |
| parent_child_prompt_v1_graph_sparse_rrf | 1 | TVQA-002 |
| semantic_bge_m3_prompt_v1_graph_sparse_rrf | 1 | TVQA-002 |
| fixed_512_prompt_v2_graph_sparse_rrf | 1 | TVQA-002 |
| parent_child_prompt_v2_graph_sparse_rrf | 1 | TVQA-002 |
| semantic_bge_m3_prompt_v2_graph_sparse_rrf | 1 | TVQA-002 |

### Rerank miss summary

| Config | Miss count | Example item IDs |
|---|---:|---|
| fixed_512_prompt_v1_graph_sparse_rrf | 0 |  |
| parent_child_prompt_v1_graph_sparse_rrf | 0 |  |
| semantic_bge_m3_prompt_v1_graph_sparse_rrf | 0 |  |
| fixed_512_prompt_v2_graph_sparse_rrf | 0 |  |
| parent_child_prompt_v2_graph_sparse_rrf | 0 |  |
| semantic_bge_m3_prompt_v2_graph_sparse_rrf | 0 |  |

## Phân tích ablation chiến lược chunking

- Phạm vi: So sánh chiến lược chunking trên cùng corpus TVKL/TVNL/TVHS/TVGM; biến chính là chunk_strategy_id.
- Ghi chú tên strategy: PLAN.md gọi chiến lược semantic là chunk_semantic_embedding; runtime hiện dùng mã chunk_semantic_embedding_bge_m3.
- Chính sách dense: Matrix chính tắt dense retrieval để không trộn lẫn biến chunking với biến dense retrieval. Retrieval stack cố định là Graph + Sparse + RRF + reranker.
- Các chiến lược được so sánh: `chunk_fixed_512, chunk_semantic_embedding_bge_m3, chunk_structure_parent_child`
- Ứng viên chunking sơ bộ: `chunk_fixed_512` qua config `fixed_512_prompt_v2_graph_sparse_rrf`
  - Đây là gợi ý sơ bộ do máy tính tổng hợp, không phải quyết định production cuối cùng.
  - Điểm ưu tiên Context Recall, Citation Coverage, Graph Hit Rate, sau đó mới xét Faithfulness, Answer Relevancy và phạt nhẹ p95 latency.
  - Ứng viên hiện tại là `chunk_fixed_512` qua config `fixed_512_prompt_v2_graph_sparse_rrf` với context_recall_avg=1.0, citation_coverage_rate=0.75, graph_hit_rate=0.0, p95_latency_ms=92.63.
  - Chỉ được dùng làm bằng chứng chính thức sau khi chạy Gemini judge/live database trên cùng golden dataset và đủ 12 cặp source-strategy.

### Xếp hạng theo Context Recall

| Hạng | Chunk strategy | Config | Giá trị |
|---:|---|---|---:|
| 1 | chunk_fixed_512 | fixed_512_prompt_v1_graph_sparse_rrf | 1.0 |
| 2 | chunk_structure_parent_child | parent_child_prompt_v1_graph_sparse_rrf | 1.0 |
| 3 | chunk_semantic_embedding_bge_m3 | semantic_bge_m3_prompt_v1_graph_sparse_rrf | 1.0 |
| 4 | chunk_fixed_512 | fixed_512_prompt_v2_graph_sparse_rrf | 1.0 |
| 5 | chunk_structure_parent_child | parent_child_prompt_v2_graph_sparse_rrf | 1.0 |
| 6 | chunk_semantic_embedding_bge_m3 | semantic_bge_m3_prompt_v2_graph_sparse_rrf | 1.0 |

### Xếp hạng theo Citation Coverage

| Hạng | Chunk strategy | Config | Giá trị |
|---:|---|---|---:|
| 1 | chunk_fixed_512 | fixed_512_prompt_v1_graph_sparse_rrf | 0.75 |
| 2 | chunk_structure_parent_child | parent_child_prompt_v1_graph_sparse_rrf | 0.75 |
| 3 | chunk_semantic_embedding_bge_m3 | semantic_bge_m3_prompt_v1_graph_sparse_rrf | 0.75 |
| 4 | chunk_fixed_512 | fixed_512_prompt_v2_graph_sparse_rrf | 0.75 |
| 5 | chunk_structure_parent_child | parent_child_prompt_v2_graph_sparse_rrf | 0.75 |
| 6 | chunk_semantic_embedding_bge_m3 | semantic_bge_m3_prompt_v2_graph_sparse_rrf | 0.75 |

### Xếp hạng theo Graph Hit Rate

| Hạng | Chunk strategy | Config | Giá trị |
|---:|---|---|---:|
| 1 | chunk_fixed_512 | fixed_512_prompt_v1_graph_sparse_rrf | 0.0 |
| 2 | chunk_structure_parent_child | parent_child_prompt_v1_graph_sparse_rrf | 0.0 |
| 3 | chunk_semantic_embedding_bge_m3 | semantic_bge_m3_prompt_v1_graph_sparse_rrf | 0.0 |
| 4 | chunk_fixed_512 | fixed_512_prompt_v2_graph_sparse_rrf | 0.0 |
| 5 | chunk_structure_parent_child | parent_child_prompt_v2_graph_sparse_rrf | 0.0 |
| 6 | chunk_semantic_embedding_bge_m3 | semantic_bge_m3_prompt_v2_graph_sparse_rrf | 0.0 |

### Xếp hạng theo p95 latency

| Hạng | Chunk strategy | Config | Giá trị |
|---:|---|---|---:|
| 1 | chunk_fixed_512 | fixed_512_prompt_v2_graph_sparse_rrf | 92.63 |
| 2 | chunk_structure_parent_child | parent_child_prompt_v2_graph_sparse_rrf | 98.27 |
| 3 | chunk_semantic_embedding_bge_m3 | semantic_bge_m3_prompt_v2_graph_sparse_rrf | 98.75 |
| 4 | chunk_structure_parent_child | parent_child_prompt_v1_graph_sparse_rrf | 111.93 |
| 5 | chunk_semantic_embedding_bge_m3 | semantic_bge_m3_prompt_v1_graph_sparse_rrf | 127.14 |
| 6 | chunk_fixed_512 | fixed_512_prompt_v1_graph_sparse_rrf | 176.44 |

## Phân tích ablation generation prompt/model

- Phạm vi: So sánh prompt template và generation model, giữ retrieval config cố định để cô lập ảnh hưởng generation.
- Retrieval control: Retrieval stack cố định theo W6 integration candidate: chunk_semantic_embedding_bge_m3, Graph + Sparse + RRF + BGE cross-encoder reranker, dense off.
- Chính sách run: Run chính của task này là Gemini judge partial 10 câu balanced; full/expanded run sẽ để W7-CONFIG-01/W8 hoặc khi quota cho phép.
- Prompt templates: `tuvi_generation_grounded_v2, tuvi_generation_v1`
- Generation models: `gemini-3.1-flash-lite-preview`
- Ứng viên generation sơ bộ: prompt `tuvi_generation_grounded_v2` với model `gemini-3.1-flash-lite-preview` qua config `fixed_512_prompt_v2_graph_sparse_rrf`
  - Đây là gợi ý sơ bộ cho W7-ABL-01 dựa trên partial run, không phải quyết định production cuối cùng.
  - Điểm ưu tiên Faithfulness, Answer Relevancy, Citation Coverage và Chart Context Grounding; p95 latency bị phạt nhẹ.
  - Ứng viên hiện tại là prompt `tuvi_generation_grounded_v2` với model `gemini-3.1-flash-lite-preview` qua config `fixed_512_prompt_v2_graph_sparse_rrf`: faithfulness_avg=1.0, answer_relevancy_avg=1.0, citation_coverage_rate=0.75, p95_latency_ms=92.63.
  - W7-CONFIG-01 sẽ tổng hợp thêm evidence retrieval/chunking/latency trước khi lock default_production.yaml.

### Xếp hạng theo Faithfulness

| Hạng | Prompt template | Model | Config | Giá trị |
|---:|---|---|---|---:|
| 1 | tuvi_generation_v1 | gemini-3.1-flash-lite-preview | fixed_512_prompt_v1_graph_sparse_rrf | 1.0 |
| 2 | tuvi_generation_v1 | gemini-3.1-flash-lite-preview | parent_child_prompt_v1_graph_sparse_rrf | 1.0 |
| 3 | tuvi_generation_v1 | gemini-3.1-flash-lite-preview | semantic_bge_m3_prompt_v1_graph_sparse_rrf | 1.0 |
| 4 | tuvi_generation_grounded_v2 | gemini-3.1-flash-lite-preview | fixed_512_prompt_v2_graph_sparse_rrf | 1.0 |
| 5 | tuvi_generation_grounded_v2 | gemini-3.1-flash-lite-preview | parent_child_prompt_v2_graph_sparse_rrf | 1.0 |
| 6 | tuvi_generation_grounded_v2 | gemini-3.1-flash-lite-preview | semantic_bge_m3_prompt_v2_graph_sparse_rrf | 1.0 |

### Xếp hạng theo Answer Relevancy

| Hạng | Prompt template | Model | Config | Giá trị |
|---:|---|---|---|---:|
| 1 | tuvi_generation_v1 | gemini-3.1-flash-lite-preview | fixed_512_prompt_v1_graph_sparse_rrf | 1.0 |
| 2 | tuvi_generation_v1 | gemini-3.1-flash-lite-preview | parent_child_prompt_v1_graph_sparse_rrf | 1.0 |
| 3 | tuvi_generation_v1 | gemini-3.1-flash-lite-preview | semantic_bge_m3_prompt_v1_graph_sparse_rrf | 1.0 |
| 4 | tuvi_generation_grounded_v2 | gemini-3.1-flash-lite-preview | fixed_512_prompt_v2_graph_sparse_rrf | 1.0 |
| 5 | tuvi_generation_grounded_v2 | gemini-3.1-flash-lite-preview | parent_child_prompt_v2_graph_sparse_rrf | 1.0 |
| 6 | tuvi_generation_grounded_v2 | gemini-3.1-flash-lite-preview | semantic_bge_m3_prompt_v2_graph_sparse_rrf | 1.0 |

### Xếp hạng theo Citation Coverage

| Hạng | Prompt template | Model | Config | Giá trị |
|---:|---|---|---|---:|
| 1 | tuvi_generation_v1 | gemini-3.1-flash-lite-preview | fixed_512_prompt_v1_graph_sparse_rrf | 0.75 |
| 2 | tuvi_generation_v1 | gemini-3.1-flash-lite-preview | parent_child_prompt_v1_graph_sparse_rrf | 0.75 |
| 3 | tuvi_generation_v1 | gemini-3.1-flash-lite-preview | semantic_bge_m3_prompt_v1_graph_sparse_rrf | 0.75 |
| 4 | tuvi_generation_grounded_v2 | gemini-3.1-flash-lite-preview | fixed_512_prompt_v2_graph_sparse_rrf | 0.75 |
| 5 | tuvi_generation_grounded_v2 | gemini-3.1-flash-lite-preview | parent_child_prompt_v2_graph_sparse_rrf | 0.75 |
| 6 | tuvi_generation_grounded_v2 | gemini-3.1-flash-lite-preview | semantic_bge_m3_prompt_v2_graph_sparse_rrf | 0.75 |

### Xếp hạng theo p95 latency

| Hạng | Prompt template | Model | Config | Giá trị |
|---:|---|---|---|---:|
| 1 | tuvi_generation_grounded_v2 | gemini-3.1-flash-lite-preview | fixed_512_prompt_v2_graph_sparse_rrf | 92.63 |
| 2 | tuvi_generation_grounded_v2 | gemini-3.1-flash-lite-preview | parent_child_prompt_v2_graph_sparse_rrf | 98.27 |
| 3 | tuvi_generation_grounded_v2 | gemini-3.1-flash-lite-preview | semantic_bge_m3_prompt_v2_graph_sparse_rrf | 98.75 |
| 4 | tuvi_generation_v1 | gemini-3.1-flash-lite-preview | parent_child_prompt_v1_graph_sparse_rrf | 111.93 |
| 5 | tuvi_generation_v1 | gemini-3.1-flash-lite-preview | semantic_bge_m3_prompt_v1_graph_sparse_rrf | 127.14 |
| 6 | tuvi_generation_v1 | gemini-3.1-flash-lite-preview | fixed_512_prompt_v1_graph_sparse_rrf | 176.44 |

## Metrics by question complexity

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| fixed_512_prompt_v1_graph_sparse_rrf | Direct | 1 | 1.0 | 1.0 | None | None | None | 180.35 |
| fixed_512_prompt_v1_graph_sparse_rrf | One-hop | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 102.09 |
| parent_child_prompt_v1_graph_sparse_rrf | Direct | 1 | 1.0 | 1.0 | None | None | None | 93.17 |
| parent_child_prompt_v1_graph_sparse_rrf | One-hop | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 112.92 |
| semantic_bge_m3_prompt_v1_graph_sparse_rrf | Direct | 1 | 1.0 | 1.0 | None | None | None | 128.05 |
| semantic_bge_m3_prompt_v1_graph_sparse_rrf | One-hop | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 109.94 |
| fixed_512_prompt_v2_graph_sparse_rrf | Direct | 1 | 1.0 | 1.0 | None | None | None | 90.59 |
| fixed_512_prompt_v2_graph_sparse_rrf | One-hop | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 92.74 |
| parent_child_prompt_v2_graph_sparse_rrf | Direct | 1 | 1.0 | 1.0 | None | None | None | 98.3 |
| parent_child_prompt_v2_graph_sparse_rrf | One-hop | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 97.75 |
| semantic_bge_m3_prompt_v2_graph_sparse_rrf | Direct | 1 | 1.0 | 1.0 | None | None | None | 98.92 |
| semantic_bge_m3_prompt_v2_graph_sparse_rrf | One-hop | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 95.57 |

## Metrics by question family

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| fixed_512_prompt_v1_graph_sparse_rrf | core_identity | 1 | 1.0 | 1.0 | None | None | None | 180.35 |
| fixed_512_prompt_v1_graph_sparse_rrf | menh_house_interpretation | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 102.09 |
| parent_child_prompt_v1_graph_sparse_rrf | core_identity | 1 | 1.0 | 1.0 | None | None | None | 93.17 |
| parent_child_prompt_v1_graph_sparse_rrf | menh_house_interpretation | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 112.92 |
| semantic_bge_m3_prompt_v1_graph_sparse_rrf | core_identity | 1 | 1.0 | 1.0 | None | None | None | 128.05 |
| semantic_bge_m3_prompt_v1_graph_sparse_rrf | menh_house_interpretation | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 109.94 |
| fixed_512_prompt_v2_graph_sparse_rrf | core_identity | 1 | 1.0 | 1.0 | None | None | None | 90.59 |
| fixed_512_prompt_v2_graph_sparse_rrf | menh_house_interpretation | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 92.74 |
| parent_child_prompt_v2_graph_sparse_rrf | core_identity | 1 | 1.0 | 1.0 | None | None | None | 98.3 |
| parent_child_prompt_v2_graph_sparse_rrf | menh_house_interpretation | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 97.75 |
| semantic_bge_m3_prompt_v2_graph_sparse_rrf | core_identity | 1 | 1.0 | 1.0 | None | None | None | 98.92 |
| semantic_bge_m3_prompt_v2_graph_sparse_rrf | menh_house_interpretation | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 95.57 |

## Per-question results

### fixed_512_prompt_v1_graph_sparse_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 180.35 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 102.09 |  |

### parent_child_prompt_v1_graph_sparse_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 93.17 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 112.92 |  |

### semantic_bge_m3_prompt_v1_graph_sparse_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 128.05 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 109.94 |  |

### fixed_512_prompt_v2_graph_sparse_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 90.59 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 92.74 |  |

### parent_child_prompt_v2_graph_sparse_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 98.3 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 97.75 |  |

### semantic_bge_m3_prompt_v2_graph_sparse_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 98.92 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 95.57 |  |
