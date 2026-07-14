# W6 Evaluation report: w6_abl_02_retrieval_fusion_reranker_v1

- Dataset: `D:\University\Năm 3 ĐH\Kì 3 (18th6)\Text Mining\tuvi-battu-graphrag\benchmark\tuvi_golden_dataset\release\tuviqa_v1_release.jsonl`
- Dataset items: 2
- Configs: 11
- Judge backend: `static-smoke`
- Started: 2026-07-14T16:47:35.504928Z
- Completed: 2026-07-14T16:47:36.115374Z
- Notes: W6-ABL-02 retrieval/fusion/reranker ablation v1. Official metrics require --judge-backend gemini; use --offline-smoke --limit 2 only for local plumbing checks. Dense variants use configs/w6_planner_gated_dense.yaml so Direct chart QA still skips dense by planner gate.

> **Caveat:** This is not an official W6 metric run because RAGAS-like metrics were not judged by Gemini.

> **Metric policy:** W6-EVAL-02 runs the RAG pipeline directly with the selected `ExperimentConfig`. `Context recall` is the Gemini-judged corpus-grounding score for non-Direct items; Direct/chart-only items are excluded from corpus retrieval/citation metrics and reported through `chart_context_grounding`.

## Overall metrics

| Config | Status | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms | Retrieval p95 ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline_graph_sparse_rrf | completed | 2 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 | 40.59 | None |
| graph_only_rrf | completed | 2 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 | 24.15 | None |
| sparse_only_rrf | completed | 2 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 | 32.2 | None |
| dense_only_rrf | completed | 2 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 | 26.62 | 0.04 |
| dense_sparse_rrf | completed | 2 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 | 23.47 | 0.03 |
| graph_dense_rrf | completed | 2 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 | 23.49 | 0.02 |
| graph_sparse_rrf | completed | 2 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 | 34.9 | None |
| all_paths_planner_dense_rrf | completed | 2 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 | 24.26 | 0.02 |
| baseline_no_reranker | completed | 2 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 | 21.53 | None |
| baseline_weighted_sum | completed | 2 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 | 21.74 | None |
| baseline_graph_first | completed | 2 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 | 21.1 | None |

## Ablation analysis

- Baseline config: `baseline_graph_sparse_rrf`
- Preliminary recommendation: `baseline_graph_first`
  - Preliminary heuristic ranks configs by context recall, citation coverage, faithfulness, answer relevancy, graph hit rate, and a small p95 latency penalty.
  - Selected `baseline_graph_first` with context_recall_avg=1.0, citation_coverage_rate=0.0, p95_latency_ms=21.1.
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
| 7 | graph_sparse_rrf | 1.0 |
| 8 | all_paths_planner_dense_rrf | 1.0 |
| 9 | baseline_no_reranker | 1.0 |
| 10 | baseline_weighted_sum | 1.0 |
| 11 | baseline_graph_first | 1.0 |

### Citation coverage ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | baseline_graph_sparse_rrf | 0.0 |
| 2 | graph_only_rrf | 0.0 |
| 3 | sparse_only_rrf | 0.0 |
| 4 | dense_only_rrf | 0.0 |
| 5 | dense_sparse_rrf | 0.0 |
| 6 | graph_dense_rrf | 0.0 |
| 7 | graph_sparse_rrf | 0.0 |
| 8 | all_paths_planner_dense_rrf | 0.0 |
| 9 | baseline_no_reranker | 0.0 |
| 10 | baseline_weighted_sum | 0.0 |
| 11 | baseline_graph_first | 0.0 |

### Graph hit ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | baseline_graph_sparse_rrf | 0.0 |
| 2 | graph_only_rrf | 0.0 |
| 3 | sparse_only_rrf | 0.0 |
| 4 | dense_only_rrf | 0.0 |
| 5 | dense_sparse_rrf | 0.0 |
| 6 | graph_dense_rrf | 0.0 |
| 7 | graph_sparse_rrf | 0.0 |
| 8 | all_paths_planner_dense_rrf | 0.0 |
| 9 | baseline_no_reranker | 0.0 |
| 10 | baseline_weighted_sum | 0.0 |
| 11 | baseline_graph_first | 0.0 |

### p95 latency ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | baseline_graph_first | 21.1 |
| 2 | baseline_no_reranker | 21.53 |
| 3 | baseline_weighted_sum | 21.74 |
| 4 | dense_sparse_rrf | 23.47 |
| 5 | graph_dense_rrf | 23.49 |
| 6 | graph_only_rrf | 24.15 |
| 7 | all_paths_planner_dense_rrf | 24.26 |
| 8 | dense_only_rrf | 26.62 |
| 9 | sparse_only_rrf | 32.2 |
| 10 | graph_sparse_rrf | 34.9 |
| 11 | baseline_graph_sparse_rrf | 40.59 |

### Retrieval miss summary

| Config | Miss count | Example item IDs |
|---|---:|---|
| baseline_graph_sparse_rrf | 1 | TVQA-002 |
| graph_only_rrf | 1 | TVQA-002 |
| sparse_only_rrf | 1 | TVQA-002 |
| dense_only_rrf | 1 | TVQA-002 |
| dense_sparse_rrf | 1 | TVQA-002 |
| graph_dense_rrf | 1 | TVQA-002 |
| graph_sparse_rrf | 1 | TVQA-002 |
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
| graph_sparse_rrf | 0 |  |
| all_paths_planner_dense_rrf | 0 |  |
| baseline_no_reranker | 0 |  |
| baseline_weighted_sum | 0 |  |
| baseline_graph_first | 0 |  |

## Metrics by question complexity

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| baseline_graph_sparse_rrf | Direct | 1 | 1.0 | 1.0 | None | None | None | 41.42 |
| baseline_graph_sparse_rrf | One-hop | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 | 24.78 |
| graph_only_rrf | Direct | 1 | 1.0 | 1.0 | None | None | None | 22.2 |
| graph_only_rrf | One-hop | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 | 24.25 |
| sparse_only_rrf | Direct | 1 | 1.0 | 1.0 | None | None | None | 32.46 |
| sparse_only_rrf | One-hop | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 | 27.36 |
| dense_only_rrf | Direct | 1 | 1.0 | 1.0 | None | None | None | 25.34 |
| dense_only_rrf | One-hop | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 | 26.69 |
| dense_sparse_rrf | Direct | 1 | 1.0 | 1.0 | None | None | None | 23.53 |
| dense_sparse_rrf | One-hop | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 | 22.34 |
| graph_dense_rrf | Direct | 1 | 1.0 | 1.0 | None | None | None | 21.41 |
| graph_dense_rrf | One-hop | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 | 23.6 |
| graph_sparse_rrf | Direct | 1 | 1.0 | 1.0 | None | None | None | 35.33 |
| graph_sparse_rrf | One-hop | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 | 26.68 |
| all_paths_planner_dense_rrf | Direct | 1 | 1.0 | 1.0 | None | None | None | 24.35 |
| all_paths_planner_dense_rrf | One-hop | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 | 22.62 |
| baseline_no_reranker | Direct | 1 | 1.0 | 1.0 | None | None | None | 21.53 |
| baseline_no_reranker | One-hop | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 | 21.47 |
| baseline_weighted_sum | Direct | 1 | 1.0 | 1.0 | None | None | None | 21.77 |
| baseline_weighted_sum | One-hop | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 | 21.25 |
| baseline_graph_first | Direct | 1 | 1.0 | 1.0 | None | None | None | 21.11 |
| baseline_graph_first | One-hop | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 | 20.98 |

## Metrics by question family

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| baseline_graph_sparse_rrf | core_identity | 1 | 1.0 | 1.0 | None | None | None | 41.42 |
| baseline_graph_sparse_rrf | menh_house_interpretation | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 | 24.78 |
| graph_only_rrf | core_identity | 1 | 1.0 | 1.0 | None | None | None | 22.2 |
| graph_only_rrf | menh_house_interpretation | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 | 24.25 |
| sparse_only_rrf | core_identity | 1 | 1.0 | 1.0 | None | None | None | 32.46 |
| sparse_only_rrf | menh_house_interpretation | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 | 27.36 |
| dense_only_rrf | core_identity | 1 | 1.0 | 1.0 | None | None | None | 25.34 |
| dense_only_rrf | menh_house_interpretation | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 | 26.69 |
| dense_sparse_rrf | core_identity | 1 | 1.0 | 1.0 | None | None | None | 23.53 |
| dense_sparse_rrf | menh_house_interpretation | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 | 22.34 |
| graph_dense_rrf | core_identity | 1 | 1.0 | 1.0 | None | None | None | 21.41 |
| graph_dense_rrf | menh_house_interpretation | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 | 23.6 |
| graph_sparse_rrf | core_identity | 1 | 1.0 | 1.0 | None | None | None | 35.33 |
| graph_sparse_rrf | menh_house_interpretation | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 | 26.68 |
| all_paths_planner_dense_rrf | core_identity | 1 | 1.0 | 1.0 | None | None | None | 24.35 |
| all_paths_planner_dense_rrf | menh_house_interpretation | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 | 22.62 |
| baseline_no_reranker | core_identity | 1 | 1.0 | 1.0 | None | None | None | 21.53 |
| baseline_no_reranker | menh_house_interpretation | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 | 21.47 |
| baseline_weighted_sum | core_identity | 1 | 1.0 | 1.0 | None | None | None | 21.77 |
| baseline_weighted_sum | menh_house_interpretation | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 | 21.25 |
| baseline_graph_first | core_identity | 1 | 1.0 | 1.0 | None | None | None | 21.11 |
| baseline_graph_first | menh_house_interpretation | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 | 20.98 |

## Per-question results

### baseline_graph_sparse_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 0 | 41.42 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.0 | 0 | 24.78 |  |

### graph_only_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 0 | 22.2 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.0 | 0 | 24.25 |  |

### sparse_only_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 0 | 32.46 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.0 | 0 | 27.36 |  |

### dense_only_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 0 | 25.34 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.0 | 0 | 26.69 |  |

### dense_sparse_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 0 | 23.53 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.0 | 0 | 22.34 |  |

### graph_dense_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 0 | 21.41 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.0 | 0 | 23.6 |  |

### graph_sparse_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 0 | 35.33 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.0 | 0 | 26.68 |  |

### all_paths_planner_dense_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 0 | 24.35 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.0 | 0 | 22.62 |  |

### baseline_no_reranker

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 0 | 21.53 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.0 | 0 | 21.47 |  |

### baseline_weighted_sum

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 0 | 21.77 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.0 | 0 | 21.25 |  |

### baseline_graph_first

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 0 | 21.11 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.0 | 0 | 20.98 |  |
