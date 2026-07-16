# W6 Evaluation report: w8_abl_01_retrieval_fusion_reranker_v2

- Dataset: `D:\University\Năm 3 ĐH\Kì 3 (18th6)\Text Mining\tuvi-battu-graphrag\benchmark\tuvi_golden_dataset\release\tuviqa_v1_release.jsonl`
- Dataset items: 2
- Configs: 10
- Judge backend: `static-smoke`
- Started: 2026-07-16T15:21:14.339684Z
- Completed: 2026-07-16T15:21:15.006298Z
- Notes: W8 retrieval/fusion/reranker matrix v2. All variants hold semantic BGE-M3 chunking, prompt v1, Gemini Flash Lite, balanced context assembly, query rewrite off, document grading on, and cache disabled constant. Dense remains planner-gated at runtime. This matrix removes the duplicate graph+sparse cell and isolates graph_first to fusion_method only.
- Run status: `completed`

## Run identity and provenance

- Identity SHA-256: `ad836be23f836d5e59cbbd03a91a71eebe9e5ea1bcc230976a127e9358806adb`
- Dataset SHA-256: `90376a87cec29cc22e93dc71b41e054ed2f0183bc515a52aa461fecd43cc008c`
- Manifest SHA-256: `5285d001b1ad92e80a98baf09d7f5f6c9997ec1d483e5c9b6c50139557591b14`
- Evaluator SHA-256: `9ae528d893159c4092c3129523da8d69a7a79a6ab5c32a132791158287eda314`
- Git SHA: `d5c4f734e5acb42679cb9e0755bbd935a4e9fa7f`
- Git dirty: `True`
- Judge model: `static-smoke`
- Checkpoint: `benchmark\tuvi_golden_dataset\reports\w8_eval_prep_02_smoke\checkpoint\evaluation_checkpoint.json`

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
| baseline_graph_sparse_rrf | completed | 2 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 40.81 | 0.58 |
| graph_only_rrf | completed | 2 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 24.44 | 0.23 |
| sparse_only_rrf | completed | 2 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 21.12 | 0.25 |
| dense_only_rrf | completed | 2 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 21.26 | 0.17 |
| dense_sparse_rrf | completed | 2 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 21.08 | 0.29 |
| graph_dense_rrf | completed | 2 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 20.91 | 0.24 |
| all_paths_planner_dense_rrf | completed | 2 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 21.72 | 0.35 |
| baseline_no_reranker | completed | 2 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 21.99 | 0.33 |
| baseline_weighted_sum | completed | 2 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 21.95 | 0.35 |
| baseline_graph_first | completed | 2 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 21.46 | 0.33 |

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
- Preliminary recommendation: `graph_dense_rrf`
  - Preliminary heuristic ranks configs by context recall, citation coverage, faithfulness, answer relevancy, graph hit rate, and a small p95 latency penalty.
  - Selected `graph_dense_rrf` with context_recall_avg=1.0, citation_coverage_rate=0.75, p95_latency_ms=20.91.
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
| 1 | graph_dense_rrf | 20.91 |
| 2 | dense_sparse_rrf | 21.08 |
| 3 | sparse_only_rrf | 21.12 |
| 4 | dense_only_rrf | 21.26 |
| 5 | baseline_graph_first | 21.46 |
| 6 | all_paths_planner_dense_rrf | 21.72 |
| 7 | baseline_weighted_sum | 21.95 |
| 8 | baseline_no_reranker | 21.99 |
| 9 | graph_only_rrf | 24.44 |
| 10 | baseline_graph_sparse_rrf | 40.81 |

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
| baseline_graph_sparse_rrf | Direct | 1 | 1.0 | 1.0 | None | None | None | 41.77 |
| baseline_graph_sparse_rrf | One-hop | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 22.54 |
| graph_only_rrf | Direct | 1 | 1.0 | 1.0 | None | None | None | 23.16 |
| graph_only_rrf | One-hop | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 24.51 |
| sparse_only_rrf | Direct | 1 | 1.0 | 1.0 | None | None | None | 20.58 |
| sparse_only_rrf | One-hop | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 21.15 |
| dense_only_rrf | Direct | 1 | 1.0 | 1.0 | None | None | None | 21.24 |
| dense_only_rrf | One-hop | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 21.26 |
| dense_sparse_rrf | Direct | 1 | 1.0 | 1.0 | None | None | None | 20.65 |
| dense_sparse_rrf | One-hop | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 21.1 |
| graph_dense_rrf | Direct | 1 | 1.0 | 1.0 | None | None | None | 20.93 |
| graph_dense_rrf | One-hop | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 20.45 |
| all_paths_planner_dense_rrf | Direct | 1 | 1.0 | 1.0 | None | None | None | 21.75 |
| all_paths_planner_dense_rrf | One-hop | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 21.06 |
| baseline_no_reranker | Direct | 1 | 1.0 | 1.0 | None | None | None | 21.12 |
| baseline_no_reranker | One-hop | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 22.04 |
| baseline_weighted_sum | Direct | 1 | 1.0 | 1.0 | None | None | None | 20.69 |
| baseline_weighted_sum | One-hop | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 22.02 |
| baseline_graph_first | Direct | 1 | 1.0 | 1.0 | None | None | None | 20.08 |
| baseline_graph_first | One-hop | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 21.53 |

## Metrics by question family

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| baseline_graph_sparse_rrf | core_identity | 1 | 1.0 | 1.0 | None | None | None | 41.77 |
| baseline_graph_sparse_rrf | menh_house_interpretation | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 22.54 |
| graph_only_rrf | core_identity | 1 | 1.0 | 1.0 | None | None | None | 23.16 |
| graph_only_rrf | menh_house_interpretation | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 24.51 |
| sparse_only_rrf | core_identity | 1 | 1.0 | 1.0 | None | None | None | 20.58 |
| sparse_only_rrf | menh_house_interpretation | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 21.15 |
| dense_only_rrf | core_identity | 1 | 1.0 | 1.0 | None | None | None | 21.24 |
| dense_only_rrf | menh_house_interpretation | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 21.26 |
| dense_sparse_rrf | core_identity | 1 | 1.0 | 1.0 | None | None | None | 20.65 |
| dense_sparse_rrf | menh_house_interpretation | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 21.1 |
| graph_dense_rrf | core_identity | 1 | 1.0 | 1.0 | None | None | None | 20.93 |
| graph_dense_rrf | menh_house_interpretation | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 20.45 |
| all_paths_planner_dense_rrf | core_identity | 1 | 1.0 | 1.0 | None | None | None | 21.75 |
| all_paths_planner_dense_rrf | menh_house_interpretation | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 21.06 |
| baseline_no_reranker | core_identity | 1 | 1.0 | 1.0 | None | None | None | 21.12 |
| baseline_no_reranker | menh_house_interpretation | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 22.04 |
| baseline_weighted_sum | core_identity | 1 | 1.0 | 1.0 | None | None | None | 20.69 |
| baseline_weighted_sum | menh_house_interpretation | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 22.02 |
| baseline_graph_first | core_identity | 1 | 1.0 | 1.0 | None | None | None | 20.08 |
| baseline_graph_first | menh_house_interpretation | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 21.53 |

## Per-question results

### baseline_graph_sparse_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 41.77 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 22.54 |  |

### graph_only_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 23.16 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 24.51 |  |

### sparse_only_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 20.58 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 21.15 |  |

### dense_only_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 21.24 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 21.26 |  |

### dense_sparse_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 20.65 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 21.1 |  |

### graph_dense_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 20.93 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 20.45 |  |

### all_paths_planner_dense_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 21.75 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 21.06 |  |

### baseline_no_reranker

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 21.12 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 22.04 |  |

### baseline_weighted_sum

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 20.69 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 22.02 |  |

### baseline_graph_first

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 20.08 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 21.53 |  |
