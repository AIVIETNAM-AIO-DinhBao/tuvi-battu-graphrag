# W6 Evaluation report: w8_abl_01_retrieval_fusion_reranker_v2

- Dataset: `D:\University\Năm 3 ĐH\Kì 3 (18th6)\Text Mining\tuvi-battu-graphrag\benchmark\tuvi_golden_dataset\release\tuviqa_v1_release.jsonl`
- Dataset items: 2
- Configs: 10
- Judge backend: `static-smoke`
- Started: 2026-07-28T12:26:59.525062Z
- Completed: 2026-07-28T12:27:01.798002Z
- Notes: W8 retrieval/fusion/reranker matrix v2. All variants hold semantic BGE-M3 chunking, prompt v1, Gemini Flash Lite, balanced context assembly, query rewrite off, document grading on, and cache disabled constant. Dense remains planner-gated at runtime. This matrix removes the duplicate graph+sparse cell and isolates graph_first to fusion_method only.
- Run status: `completed`

## Execution completeness

- Expected pairs: 20
- Completed pairs: 20
- Failed pairs: 0
- Executed pairs: 20
- Resumed pairs: 0

> **Caveat:** This is not an official W6 metric run because RAGAS-like metrics were not judged by Gemini.

> **Metric policy:** W6-EVAL-02 runs the RAG pipeline directly with the selected `ExperimentConfig`. `Context recall` is the Gemini-judged corpus-grounding score for non-Direct items; Direct/chart-only items are excluded from corpus retrieval/citation metrics and reported through `chart_context_grounding`.

## Overall metrics

| Config | Status | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms | Retrieval p95 ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline_graph_sparse_rrf | completed | 2 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 133.12 | 0.88 |
| graph_only_rrf | completed | 2 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 107.63 | 0.44 |
| sparse_only_rrf | completed | 2 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 112.0 | 0.49 |
| dense_only_rrf | completed | 2 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 113.14 | 0.2 |
| dense_sparse_rrf | completed | 2 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 106.0 | 0.48 |
| graph_dense_rrf | completed | 2 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 107.55 | 0.55 |
| all_paths_planner_dense_rrf | completed | 2 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 117.76 | 0.91 |
| baseline_no_reranker | completed | 2 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 106.29 | 0.74 |
| baseline_weighted_sum | completed | 2 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 100.13 | 0.65 |
| baseline_graph_first | completed | 2 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 124.46 | 0.64 |

## Failure and fallback summary

| Config | Failed | Generation backend fallback | Judge failure | No context | Retrieval backend fallback | Citation fallback |
|---|---:|---:|---:|---:|---:|---:|
| baseline_graph_sparse_rrf | 0 | 0 | 0 | 0 | 0 | 0 |
| graph_only_rrf | 0 | 0 | 0 | 0 | 0 | 0 |
| sparse_only_rrf | 0 | 0 | 0 | 0 | 0 | 0 |
| dense_only_rrf | 0 | 0 | 0 | 0 | 0 | 0 |
| dense_sparse_rrf | 0 | 0 | 0 | 0 | 0 | 0 |
| graph_dense_rrf | 0 | 0 | 0 | 0 | 0 | 0 |
| all_paths_planner_dense_rrf | 0 | 0 | 0 | 0 | 0 | 0 |
| baseline_no_reranker | 0 | 0 | 0 | 0 | 0 | 0 |
| baseline_weighted_sum | 0 | 0 | 0 | 0 | 0 | 0 |
| baseline_graph_first | 0 | 0 | 0 | 0 | 0 | 0 |

## Ablation analysis

- Baseline config: `baseline_graph_sparse_rrf`
- Preliminary recommendation: `baseline_weighted_sum`
  - Preliminary heuristic ranks configs by context recall, citation coverage, faithfulness, answer relevancy, graph hit rate, and a small p95 latency penalty.
  - Selected `baseline_weighted_sum` with context_recall_avg=1.0, citation_coverage_rate=0.75, p95_latency_ms=100.13.
  - Treat this as a smoke/first-pass recommendation until official Gemini judge and full dataset runs are complete.

### Context recall ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | baseline_graph_sparse_rrf | 1.0 |
| 2 | graph_only_rrf | 1.0 |
| 3 | sparse_only_rrf | 1.0 |
| 4 | dense_only_rrf | 1.0 |
| 5 | dense_sparse_rrf | 1.0 |
| 6 | graph_dense_rrf | 1.0 |
| 7 | all_paths_planner_dense_rrf | 1.0 |
| 8 | baseline_no_reranker | 1.0 |
| 9 | baseline_weighted_sum | 1.0 |
| 10 | baseline_graph_first | 1.0 |

### Citation coverage ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | baseline_graph_sparse_rrf | 0.75 |
| 2 | graph_only_rrf | 0.75 |
| 3 | sparse_only_rrf | 0.75 |
| 4 | dense_only_rrf | 0.75 |
| 5 | dense_sparse_rrf | 0.75 |
| 6 | graph_dense_rrf | 0.75 |
| 7 | all_paths_planner_dense_rrf | 0.75 |
| 8 | baseline_no_reranker | 0.75 |
| 9 | baseline_weighted_sum | 0.75 |
| 10 | baseline_graph_first | 0.75 |

### Graph hit ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | baseline_graph_sparse_rrf | 0.0 |
| 2 | graph_only_rrf | 0.0 |
| 3 | sparse_only_rrf | 0.0 |
| 4 | dense_only_rrf | 0.0 |
| 5 | dense_sparse_rrf | 0.0 |
| 6 | graph_dense_rrf | 0.0 |
| 7 | all_paths_planner_dense_rrf | 0.0 |
| 8 | baseline_no_reranker | 0.0 |
| 9 | baseline_weighted_sum | 0.0 |
| 10 | baseline_graph_first | 0.0 |

### p95 latency ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | baseline_weighted_sum | 100.13 |
| 2 | dense_sparse_rrf | 106.0 |
| 3 | baseline_no_reranker | 106.29 |
| 4 | graph_dense_rrf | 107.55 |
| 5 | graph_only_rrf | 107.63 |
| 6 | sparse_only_rrf | 112.0 |
| 7 | dense_only_rrf | 113.14 |
| 8 | all_paths_planner_dense_rrf | 117.76 |
| 9 | baseline_graph_first | 124.46 |
| 10 | baseline_graph_sparse_rrf | 133.12 |

### Retrieval miss summary

| Config | Miss count | Example item IDs |
|---|---:|---|
| baseline_graph_sparse_rrf | 1 | TVQA-002 |
| graph_only_rrf | 1 | TVQA-002 |
| sparse_only_rrf | 1 | TVQA-002 |
| dense_only_rrf | 1 | TVQA-002 |
| dense_sparse_rrf | 1 | TVQA-002 |
| graph_dense_rrf | 1 | TVQA-002 |
| all_paths_planner_dense_rrf | 1 | TVQA-002 |
| baseline_no_reranker | 1 | TVQA-002 |
| baseline_weighted_sum | 1 | TVQA-002 |
| baseline_graph_first | 1 | TVQA-002 |

### Rerank miss summary

| Config | Miss count | Example item IDs |
|---|---:|---|
| baseline_graph_sparse_rrf | 0 |  |
| graph_only_rrf | 0 |  |
| sparse_only_rrf | 0 |  |
| dense_only_rrf | 0 |  |
| dense_sparse_rrf | 0 |  |
| graph_dense_rrf | 0 |  |
| all_paths_planner_dense_rrf | 0 |  |
| baseline_no_reranker | 0 |  |
| baseline_weighted_sum | 0 |  |
| baseline_graph_first | 0 |  |

## Metrics by question complexity

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| baseline_graph_sparse_rrf | Direct | 1 | 1.0 | 1.0 | None | None | None | 134.35 |
| baseline_graph_sparse_rrf | One-hop | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 109.77 |
| graph_only_rrf | Direct | 1 | 1.0 | 1.0 | None | None | None | 107.88 |
| graph_only_rrf | One-hop | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 102.93 |
| sparse_only_rrf | Direct | 1 | 1.0 | 1.0 | None | None | None | 110.87 |
| sparse_only_rrf | One-hop | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 112.06 |
| dense_only_rrf | Direct | 1 | 1.0 | 1.0 | None | None | None | 103.05 |
| dense_only_rrf | One-hop | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 113.67 |
| dense_sparse_rrf | Direct | 1 | 1.0 | 1.0 | None | None | None | 105.28 |
| dense_sparse_rrf | One-hop | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 106.04 |
| graph_dense_rrf | Direct | 1 | 1.0 | 1.0 | None | None | None | 107.63 |
| graph_dense_rrf | One-hop | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 106.06 |
| all_paths_planner_dense_rrf | Direct | 1 | 1.0 | 1.0 | None | None | None | 103.1 |
| all_paths_planner_dense_rrf | One-hop | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 118.53 |
| baseline_no_reranker | Direct | 1 | 1.0 | 1.0 | None | None | None | 106.62 |
| baseline_no_reranker | One-hop | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 99.96 |
| baseline_weighted_sum | Direct | 1 | 1.0 | 1.0 | None | None | None | 99.71 |
| baseline_weighted_sum | One-hop | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 100.15 |
| baseline_graph_first | Direct | 1 | 1.0 | 1.0 | None | None | None | 99.16 |
| baseline_graph_first | One-hop | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 125.79 |

## Metrics by question family

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| baseline_graph_sparse_rrf | core_identity | 1 | 1.0 | 1.0 | None | None | None | 134.35 |
| baseline_graph_sparse_rrf | menh_house_interpretation | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 109.77 |
| graph_only_rrf | core_identity | 1 | 1.0 | 1.0 | None | None | None | 107.88 |
| graph_only_rrf | menh_house_interpretation | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 102.93 |
| sparse_only_rrf | core_identity | 1 | 1.0 | 1.0 | None | None | None | 110.87 |
| sparse_only_rrf | menh_house_interpretation | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 112.06 |
| dense_only_rrf | core_identity | 1 | 1.0 | 1.0 | None | None | None | 103.05 |
| dense_only_rrf | menh_house_interpretation | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 113.67 |
| dense_sparse_rrf | core_identity | 1 | 1.0 | 1.0 | None | None | None | 105.28 |
| dense_sparse_rrf | menh_house_interpretation | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 106.04 |
| graph_dense_rrf | core_identity | 1 | 1.0 | 1.0 | None | None | None | 107.63 |
| graph_dense_rrf | menh_house_interpretation | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 106.06 |
| all_paths_planner_dense_rrf | core_identity | 1 | 1.0 | 1.0 | None | None | None | 103.1 |
| all_paths_planner_dense_rrf | menh_house_interpretation | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 118.53 |
| baseline_no_reranker | core_identity | 1 | 1.0 | 1.0 | None | None | None | 106.62 |
| baseline_no_reranker | menh_house_interpretation | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 99.96 |
| baseline_weighted_sum | core_identity | 1 | 1.0 | 1.0 | None | None | None | 99.71 |
| baseline_weighted_sum | menh_house_interpretation | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 100.15 |
| baseline_graph_first | core_identity | 1 | 1.0 | 1.0 | None | None | None | 99.16 |
| baseline_graph_first | menh_house_interpretation | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 125.79 |

## Per-question results

### baseline_graph_sparse_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 134.35 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 109.77 |  |

### graph_only_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 107.88 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 102.93 |  |

### sparse_only_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 110.87 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 112.06 |  |

### dense_only_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 103.05 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 113.67 |  |

### dense_sparse_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 105.28 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 106.04 |  |

### graph_dense_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 107.63 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 106.06 |  |

### all_paths_planner_dense_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 103.1 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 118.53 |  |

### baseline_no_reranker

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 106.62 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 99.96 |  |

### baseline_weighted_sum

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 99.71 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 100.15 |  |

### baseline_graph_first

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 99.16 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 125.79 |  |
