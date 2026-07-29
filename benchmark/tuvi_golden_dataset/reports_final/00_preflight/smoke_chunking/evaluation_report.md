# W6 Evaluation report: w6_abl_03_chunking_strategy_v1

- Dataset: `D:\University\Năm 3 ĐH\Kì 3 (18th6)\Text Mining\tuvi-battu-graphrag\benchmark\tuvi_golden_dataset\release\tuviqa_v1_release.jsonl`
- Dataset items: 2
- Configs: 3
- Judge backend: `static-smoke`
- Started: 2026-07-28T12:26:54.012726Z
- Completed: 2026-07-28T12:26:54.721231Z
- Notes: W6-ABL-03 so sánh 3 chiến lược chunking trên cùng bộ corpus TVKL/TVNL/TVHS/TVGM. Biến chính của ablation là chunk_strategy_id. PLAN.md gọi chiến lược semantic là chunk_semantic_embedding; runtime hiện dùng mã chính thức chunk_semantic_embedding_bge_m3, nên manifest này dùng chunk_semantic_embedding_bge_m3 và ghi rõ như alias vận hành. Matrix chính giữ Graph+Sparse+RRF+reranker, tắt dense để không trộn lẫn biến chunking với biến dense retrieval.
- Run status: `completed`

## Execution completeness

- Expected pairs: 6
- Completed pairs: 6
- Failed pairs: 0
- Executed pairs: 6
- Resumed pairs: 0

> **Caveat:** This is not an official W6 metric run because RAGAS-like metrics were not judged by Gemini.

> **Metric policy:** W6-EVAL-02 runs the RAG pipeline directly with the selected `ExperimentConfig`. `Context recall` is the Gemini-judged corpus-grounding score for non-Direct items; Direct/chart-only items are excluded from corpus retrieval/citation metrics and reported through `chart_context_grounding`.

## Overall metrics

| Config | Status | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms | Retrieval p95 ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| fixed_512_graph_sparse_rrf | completed | 2 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 167.3 | 1.06 |
| parent_child_graph_sparse_rrf | completed | 2 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 102.79 | 0.64 |
| semantic_bge_m3_graph_sparse_rrf | completed | 2 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 99.65 | 0.7 |

## Failure and fallback summary

| Config | Failed | Generation backend fallback | Judge failure | No context | Retrieval backend fallback | Citation fallback |
|---|---:|---:|---:|---:|---:|---:|
| fixed_512_graph_sparse_rrf | 0 | 0 | 0 | 0 | 0 | 0 |
| parent_child_graph_sparse_rrf | 0 | 0 | 0 | 0 | 0 | 0 |
| semantic_bge_m3_graph_sparse_rrf | 0 | 0 | 0 | 0 | 0 | 0 |

## Ablation analysis

- Baseline config: `baseline_graph_sparse_rrf`
- Preliminary recommendation: `semantic_bge_m3_graph_sparse_rrf`
  - Preliminary heuristic ranks configs by context recall, citation coverage, faithfulness, answer relevancy, graph hit rate, and a small p95 latency penalty.
  - Selected `semantic_bge_m3_graph_sparse_rrf` with context_recall_avg=1.0, citation_coverage_rate=0.75, p95_latency_ms=99.65.
  - Treat this as a smoke/first-pass recommendation until official Gemini judge and full dataset runs are complete.

### Context recall ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | fixed_512_graph_sparse_rrf | 1.0 |
| 2 | parent_child_graph_sparse_rrf | 1.0 |
| 3 | semantic_bge_m3_graph_sparse_rrf | 1.0 |

### Citation coverage ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | fixed_512_graph_sparse_rrf | 0.75 |
| 2 | parent_child_graph_sparse_rrf | 0.75 |
| 3 | semantic_bge_m3_graph_sparse_rrf | 0.75 |

### Graph hit ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | fixed_512_graph_sparse_rrf | 0.0 |
| 2 | parent_child_graph_sparse_rrf | 0.0 |
| 3 | semantic_bge_m3_graph_sparse_rrf | 0.0 |

### p95 latency ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | semantic_bge_m3_graph_sparse_rrf | 99.65 |
| 2 | parent_child_graph_sparse_rrf | 102.79 |
| 3 | fixed_512_graph_sparse_rrf | 167.3 |

### Retrieval miss summary

| Config | Miss count | Example item IDs |
|---|---:|---|
| fixed_512_graph_sparse_rrf | 1 | TVQA-002 |
| parent_child_graph_sparse_rrf | 1 | TVQA-002 |
| semantic_bge_m3_graph_sparse_rrf | 1 | TVQA-002 |

### Rerank miss summary

| Config | Miss count | Example item IDs |
|---|---:|---|
| fixed_512_graph_sparse_rrf | 0 |  |
| parent_child_graph_sparse_rrf | 0 |  |
| semantic_bge_m3_graph_sparse_rrf | 0 |  |

## Phân tích ablation chiến lược chunking

- Phạm vi: So sánh chiến lược chunking trên cùng corpus TVKL/TVNL/TVHS/TVGM; biến chính là chunk_strategy_id.
- Ghi chú tên strategy: PLAN.md gọi chiến lược semantic là chunk_semantic_embedding; runtime hiện dùng mã chunk_semantic_embedding_bge_m3.
- Chính sách dense: Matrix chính tắt dense retrieval để không trộn lẫn biến chunking với biến dense retrieval. Retrieval stack cố định là Graph + Sparse + RRF + reranker.
- Các chiến lược được so sánh: `chunk_fixed_512, chunk_semantic_embedding_bge_m3, chunk_structure_parent_child`
- Ứng viên chunking sơ bộ: `chunk_semantic_embedding_bge_m3` qua config `semantic_bge_m3_graph_sparse_rrf`
  - Đây là gợi ý sơ bộ do máy tính tổng hợp, không phải quyết định production cuối cùng.
  - Điểm ưu tiên Context Recall, Citation Coverage, Graph Hit Rate, sau đó mới xét Faithfulness, Answer Relevancy và phạt nhẹ p95 latency.
  - Ứng viên hiện tại là `chunk_semantic_embedding_bge_m3` qua config `semantic_bge_m3_graph_sparse_rrf` với context_recall_avg=1.0, citation_coverage_rate=0.75, graph_hit_rate=0.0, p95_latency_ms=99.65.
  - Chỉ được dùng làm bằng chứng chính thức sau khi chạy Gemini judge/live database trên cùng golden dataset và đủ 12 cặp source-strategy.

### Xếp hạng theo Context Recall

| Hạng | Chunk strategy | Config | Giá trị |
|---:|---|---|---:|
| 1 | chunk_fixed_512 | fixed_512_graph_sparse_rrf | 1.0 |
| 2 | chunk_structure_parent_child | parent_child_graph_sparse_rrf | 1.0 |
| 3 | chunk_semantic_embedding_bge_m3 | semantic_bge_m3_graph_sparse_rrf | 1.0 |

### Xếp hạng theo Citation Coverage

| Hạng | Chunk strategy | Config | Giá trị |
|---:|---|---|---:|
| 1 | chunk_fixed_512 | fixed_512_graph_sparse_rrf | 0.75 |
| 2 | chunk_structure_parent_child | parent_child_graph_sparse_rrf | 0.75 |
| 3 | chunk_semantic_embedding_bge_m3 | semantic_bge_m3_graph_sparse_rrf | 0.75 |

### Xếp hạng theo Graph Hit Rate

| Hạng | Chunk strategy | Config | Giá trị |
|---:|---|---|---:|
| 1 | chunk_fixed_512 | fixed_512_graph_sparse_rrf | 0.0 |
| 2 | chunk_structure_parent_child | parent_child_graph_sparse_rrf | 0.0 |
| 3 | chunk_semantic_embedding_bge_m3 | semantic_bge_m3_graph_sparse_rrf | 0.0 |

### Xếp hạng theo p95 latency

| Hạng | Chunk strategy | Config | Giá trị |
|---:|---|---|---:|
| 1 | chunk_semantic_embedding_bge_m3 | semantic_bge_m3_graph_sparse_rrf | 99.65 |
| 2 | chunk_structure_parent_child | parent_child_graph_sparse_rrf | 102.79 |
| 3 | chunk_fixed_512 | fixed_512_graph_sparse_rrf | 167.3 |

## Metrics by question complexity

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| fixed_512_graph_sparse_rrf | Direct | 1 | 1.0 | 1.0 | None | None | None | 170.44 |
| fixed_512_graph_sparse_rrf | One-hop | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 107.56 |
| parent_child_graph_sparse_rrf | Direct | 1 | 1.0 | 1.0 | None | None | None | 102.93 |
| parent_child_graph_sparse_rrf | One-hop | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 100.12 |
| semantic_bge_m3_graph_sparse_rrf | Direct | 1 | 1.0 | 1.0 | None | None | None | 99.67 |
| semantic_bge_m3_graph_sparse_rrf | One-hop | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 99.24 |

## Metrics by question family

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| fixed_512_graph_sparse_rrf | core_identity | 1 | 1.0 | 1.0 | None | None | None | 170.44 |
| fixed_512_graph_sparse_rrf | menh_house_interpretation | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 107.56 |
| parent_child_graph_sparse_rrf | core_identity | 1 | 1.0 | 1.0 | None | None | None | 102.93 |
| parent_child_graph_sparse_rrf | menh_house_interpretation | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 100.12 |
| semantic_bge_m3_graph_sparse_rrf | core_identity | 1 | 1.0 | 1.0 | None | None | None | 99.67 |
| semantic_bge_m3_graph_sparse_rrf | menh_house_interpretation | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 99.24 |

## Per-question results

### fixed_512_graph_sparse_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 170.44 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 107.56 |  |

### parent_child_graph_sparse_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 102.93 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 100.12 |  |

### semantic_bge_m3_graph_sparse_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 99.67 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 99.24 |  |
