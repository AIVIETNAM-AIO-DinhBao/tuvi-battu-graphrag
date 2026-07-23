# W6 Evaluation report: w8_abl_01_retrieval_fusion_reranker_v2

- Dataset: `D:\University\Năm 3 ĐH\Kì 3 (18th6)\Text Mining\tuvi-battu-graphrag\benchmark\tuvi_golden_dataset\release\tuviqa_v1_release.jsonl`
- Dataset items: 100
- Configs: 10
- Judge backend: `static-smoke`
- Started: 2026-07-23T10:18:13.915893Z
- Completed: 2026-07-23T10:19:29.314688Z
- Notes: W8 retrieval/fusion/reranker matrix v2. All variants hold semantic BGE-M3 chunking, prompt v1, Gemini Flash Lite, balanced context assembly, query rewrite off, document grading on, and cache disabled constant. Dense remains planner-gated at runtime. This matrix removes the duplicate graph+sparse cell and isolates graph_first to fusion_method only.
- Run status: `completed`

## Execution completeness

- Expected pairs: 1000
- Completed pairs: 1000
- Failed pairs: 0
- Executed pairs: 1000
- Resumed pairs: 0

> **Caveat:** This is not an official W6 metric run because RAGAS-like metrics were not judged by Gemini.

> **Metric policy:** W6-EVAL-02 runs the RAG pipeline directly with the selected `ExperimentConfig`. `Context recall` is the Gemini-judged corpus-grounding score for non-Direct items; Direct/chart-only items are excluded from corpus retrieval/citation metrics and reported through `chart_context_grounding`.

## Overall metrics

| Config | Status | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms | Retrieval p95 ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline_graph_sparse_rrf | completed | 100 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 117.79 | 1.01 |
| graph_only_rrf | completed | 100 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 79.6 | 0.42 |
| sparse_only_rrf | completed | 100 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 77.58 | 0.46 |
| dense_only_rrf | completed | 100 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 79.33 | 0.22 |
| dense_sparse_rrf | completed | 100 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 83.71 | 0.58 |
| graph_dense_rrf | completed | 100 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 80.47 | 0.49 |
| all_paths_planner_dense_rrf | completed | 100 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 77.26 | 0.69 |
| baseline_no_reranker | completed | 100 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 78.08 | 0.75 |
| baseline_weighted_sum | completed | 100 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 81.59 | 0.73 |
| baseline_graph_first | completed | 100 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 79.53 | 0.7 |

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
- Preliminary recommendation: `all_paths_planner_dense_rrf`
  - Preliminary heuristic ranks configs by context recall, citation coverage, faithfulness, answer relevancy, graph hit rate, and a small p95 latency penalty.
  - Selected `all_paths_planner_dense_rrf` with context_recall_avg=1.0, citation_coverage_rate=0.75, p95_latency_ms=77.26.
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
| 1 | all_paths_planner_dense_rrf | 77.26 |
| 2 | sparse_only_rrf | 77.58 |
| 3 | baseline_no_reranker | 78.08 |
| 4 | dense_only_rrf | 79.33 |
| 5 | baseline_graph_first | 79.53 |
| 6 | graph_only_rrf | 79.6 |
| 7 | graph_dense_rrf | 80.47 |
| 8 | baseline_weighted_sum | 81.59 |
| 9 | dense_sparse_rrf | 83.71 |
| 10 | baseline_graph_sparse_rrf | 117.79 |

### Retrieval miss summary

| Config | Miss count | Example item IDs |
|---|---:|---|
| baseline_graph_sparse_rrf | 91 | TVQA-002, TVQA-003, TVQA-004, TVQA-005, TVQA-006 |
| graph_only_rrf | 91 | TVQA-002, TVQA-003, TVQA-004, TVQA-005, TVQA-006 |
| sparse_only_rrf | 91 | TVQA-002, TVQA-003, TVQA-004, TVQA-005, TVQA-006 |
| dense_only_rrf | 91 | TVQA-002, TVQA-003, TVQA-004, TVQA-005, TVQA-006 |
| dense_sparse_rrf | 91 | TVQA-002, TVQA-003, TVQA-004, TVQA-005, TVQA-006 |
| graph_dense_rrf | 91 | TVQA-002, TVQA-003, TVQA-004, TVQA-005, TVQA-006 |
| all_paths_planner_dense_rrf | 91 | TVQA-002, TVQA-003, TVQA-004, TVQA-005, TVQA-006 |
| baseline_no_reranker | 91 | TVQA-002, TVQA-003, TVQA-004, TVQA-005, TVQA-006 |
| baseline_weighted_sum | 91 | TVQA-002, TVQA-003, TVQA-004, TVQA-005, TVQA-006 |
| baseline_graph_first | 91 | TVQA-002, TVQA-003, TVQA-004, TVQA-005, TVQA-006 |

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
| baseline_graph_sparse_rrf | Direct | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 119.92 |
| baseline_graph_sparse_rrf | One-hop | 46 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 107.61 |
| baseline_graph_sparse_rrf | Two-hop | 44 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 115.9 |
| graph_only_rrf | Direct | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 76.08 |
| graph_only_rrf | One-hop | 46 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 76.83 |
| graph_only_rrf | Two-hop | 44 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 82.12 |
| sparse_only_rrf | Direct | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 72.75 |
| sparse_only_rrf | One-hop | 46 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 76.78 |
| sparse_only_rrf | Two-hop | 44 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 79.26 |
| dense_only_rrf | Direct | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 77.18 |
| dense_only_rrf | One-hop | 46 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 75.41 |
| dense_only_rrf | Two-hop | 44 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 78.74 |
| dense_sparse_rrf | Direct | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 82.88 |
| dense_sparse_rrf | One-hop | 46 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 85.69 |
| dense_sparse_rrf | Two-hop | 44 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 82.54 |
| graph_dense_rrf | Direct | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 71.96 |
| graph_dense_rrf | One-hop | 46 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 83.18 |
| graph_dense_rrf | Two-hop | 44 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 80.25 |
| all_paths_planner_dense_rrf | Direct | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 75.36 |
| all_paths_planner_dense_rrf | One-hop | 46 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 77.28 |
| all_paths_planner_dense_rrf | Two-hop | 44 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 77.23 |
| baseline_no_reranker | Direct | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 119.4 |
| baseline_no_reranker | One-hop | 46 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 76.73 |
| baseline_no_reranker | Two-hop | 44 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 77.87 |
| baseline_weighted_sum | Direct | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 81.66 |
| baseline_weighted_sum | One-hop | 46 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 79.92 |
| baseline_weighted_sum | Two-hop | 44 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 81.97 |
| baseline_graph_first | Direct | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 72.57 |
| baseline_graph_first | One-hop | 46 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 79.46 |
| baseline_graph_first | Two-hop | 44 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 79.41 |

## Metrics by question family

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| baseline_graph_sparse_rrf | core_identity | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 119.92 |
| baseline_graph_sparse_rrf | dai_van_interpretation | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 133.05 |
| baseline_graph_sparse_rrf | menh_cuc_relation | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 129.16 |
| baseline_graph_sparse_rrf | menh_house_interpretation | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 101.49 |
| baseline_graph_sparse_rrf | menh_tam_hop | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 130.25 |
| baseline_graph_sparse_rrf | menh_xung_chieu | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 137.74 |
| baseline_graph_sparse_rrf | special_state_interpretation | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 104.53 |
| baseline_graph_sparse_rrf | synthesis_judgement | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 105.72 |
| baseline_graph_sparse_rrf | than_cu_interpretation | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 104.25 |
| baseline_graph_sparse_rrf | topic_house_plus_relations | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 106.23 |
| graph_only_rrf | core_identity | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 76.08 |
| graph_only_rrf | dai_van_interpretation | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 83.15 |
| graph_only_rrf | menh_cuc_relation | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 77.04 |
| graph_only_rrf | menh_house_interpretation | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 74.53 |
| graph_only_rrf | menh_tam_hop | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 101.02 |
| graph_only_rrf | menh_xung_chieu | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 78.6 |
| graph_only_rrf | special_state_interpretation | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 74.28 |
| graph_only_rrf | synthesis_judgement | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 76.4 |
| graph_only_rrf | than_cu_interpretation | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 76.19 |
| graph_only_rrf | topic_house_plus_relations | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 77.46 |
| sparse_only_rrf | core_identity | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 72.75 |
| sparse_only_rrf | dai_van_interpretation | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 79.14 |
| sparse_only_rrf | menh_cuc_relation | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 74.63 |
| sparse_only_rrf | menh_house_interpretation | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 76.89 |
| sparse_only_rrf | menh_tam_hop | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 75.34 |
| sparse_only_rrf | menh_xung_chieu | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 74.31 |
| sparse_only_rrf | special_state_interpretation | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 73.99 |
| sparse_only_rrf | synthesis_judgement | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 78.62 |
| sparse_only_rrf | than_cu_interpretation | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 73.01 |
| sparse_only_rrf | topic_house_plus_relations | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 116.56 |
| dense_only_rrf | core_identity | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 77.18 |
| dense_only_rrf | dai_van_interpretation | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 77.09 |
| dense_only_rrf | menh_cuc_relation | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 77.93 |
| dense_only_rrf | menh_house_interpretation | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 71.03 |
| dense_only_rrf | menh_tam_hop | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 77.85 |
| dense_only_rrf | menh_xung_chieu | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 77.48 |
| dense_only_rrf | special_state_interpretation | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 78.04 |
| dense_only_rrf | synthesis_judgement | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 73.79 |
| dense_only_rrf | than_cu_interpretation | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 74.8 |
| dense_only_rrf | topic_house_plus_relations | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 75.26 |
| dense_sparse_rrf | core_identity | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 82.88 |
| dense_sparse_rrf | dai_van_interpretation | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 77.06 |
| dense_sparse_rrf | menh_cuc_relation | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 122.92 |
| dense_sparse_rrf | menh_house_interpretation | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 84.55 |
| dense_sparse_rrf | menh_tam_hop | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 79.13 |
| dense_sparse_rrf | menh_xung_chieu | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 78.87 |
| dense_sparse_rrf | special_state_interpretation | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 81.14 |
| dense_sparse_rrf | synthesis_judgement | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 82.53 |
| dense_sparse_rrf | than_cu_interpretation | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 79.43 |
| dense_sparse_rrf | topic_house_plus_relations | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 82.38 |
| graph_dense_rrf | core_identity | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 71.96 |
| graph_dense_rrf | dai_van_interpretation | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 79.28 |
| graph_dense_rrf | menh_cuc_relation | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 72.58 |
| graph_dense_rrf | menh_house_interpretation | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 81.22 |
| graph_dense_rrf | menh_tam_hop | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 91.36 |
| graph_dense_rrf | menh_xung_chieu | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 80.03 |
| graph_dense_rrf | special_state_interpretation | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 90.02 |
| graph_dense_rrf | synthesis_judgement | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 72.91 |
| graph_dense_rrf | than_cu_interpretation | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 77.61 |
| graph_dense_rrf | topic_house_plus_relations | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 77.32 |
| all_paths_planner_dense_rrf | core_identity | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 75.36 |
| all_paths_planner_dense_rrf | dai_van_interpretation | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 76.0 |
| all_paths_planner_dense_rrf | menh_cuc_relation | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 77.56 |
| all_paths_planner_dense_rrf | menh_house_interpretation | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 75.36 |
| all_paths_planner_dense_rrf | menh_tam_hop | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 75.89 |
| all_paths_planner_dense_rrf | menh_xung_chieu | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 77.6 |
| all_paths_planner_dense_rrf | special_state_interpretation | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 75.73 |
| all_paths_planner_dense_rrf | synthesis_judgement | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 75.83 |
| all_paths_planner_dense_rrf | than_cu_interpretation | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 76.33 |
| all_paths_planner_dense_rrf | topic_house_plus_relations | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 77.14 |
| baseline_no_reranker | core_identity | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 119.4 |
| baseline_no_reranker | dai_van_interpretation | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 73.01 |
| baseline_no_reranker | menh_cuc_relation | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 75.59 |
| baseline_no_reranker | menh_house_interpretation | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 75.9 |
| baseline_no_reranker | menh_tam_hop | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 78.38 |
| baseline_no_reranker | menh_xung_chieu | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 75.96 |
| baseline_no_reranker | special_state_interpretation | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 76.06 |
| baseline_no_reranker | synthesis_judgement | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 74.23 |
| baseline_no_reranker | than_cu_interpretation | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 77.62 |
| baseline_no_reranker | topic_house_plus_relations | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 81.17 |
| baseline_weighted_sum | core_identity | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 81.66 |
| baseline_weighted_sum | dai_van_interpretation | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 77.9 |
| baseline_weighted_sum | menh_cuc_relation | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 82.47 |
| baseline_weighted_sum | menh_house_interpretation | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 77.98 |
| baseline_weighted_sum | menh_tam_hop | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 84.4 |
| baseline_weighted_sum | menh_xung_chieu | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 78.67 |
| baseline_weighted_sum | special_state_interpretation | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 78.11 |
| baseline_weighted_sum | synthesis_judgement | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 83.57 |
| baseline_weighted_sum | than_cu_interpretation | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 78.83 |
| baseline_weighted_sum | topic_house_plus_relations | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 81.18 |
| baseline_graph_first | core_identity | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 72.57 |
| baseline_graph_first | dai_van_interpretation | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 120.43 |
| baseline_graph_first | menh_cuc_relation | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 86.22 |
| baseline_graph_first | menh_house_interpretation | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 76.6 |
| baseline_graph_first | menh_tam_hop | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 75.51 |
| baseline_graph_first | menh_xung_chieu | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 79.18 |
| baseline_graph_first | special_state_interpretation | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 76.28 |
| baseline_graph_first | synthesis_judgement | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 81.16 |
| baseline_graph_first | than_cu_interpretation | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 77.92 |
| baseline_graph_first | topic_house_plus_relations | 10 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 75.0 |

## Per-question results

### baseline_graph_sparse_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 135.22 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 102.41 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 99.97 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 99.94 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 100.24 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 141.2 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 160.12 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 153.44 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 96.55 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 94.78 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 96.18 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 97.43 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 101.62 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 97.41 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 99.76 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 98.39 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 105.85 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 108.12 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 104.72 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 105.74 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 101.21 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 99.52 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 105.2 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 102.93 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 106.09 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 104.72 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 107.36 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 99.19 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 107.47 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 105.7 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 99.47 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 100.37 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 103.08 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 100.88 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 102.63 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 102.37 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 110.38 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 94.52 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 89.61 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 87.0 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 93.69 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 79.56 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 79.32 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 75.16 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 78.0 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.44 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 74.23 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 96.76 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 75.73 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 77.36 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 73.06 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 79.6 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 75.79 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 150.62 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.88 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.0 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.85 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 77.44 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.91 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 74.21 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.64 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.76 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 76.46 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 85.0 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 88.11 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 78.76 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.36 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 80.16 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 74.03 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.31 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 71.61 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 74.36 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 78.29 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.18 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.75 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.81 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.78 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.02 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.25 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.08 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 68.53 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.94 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.34 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 78.16 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 78.04 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 116.87 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.38 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.27 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 67.77 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 68.88 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 70.33 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.05 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.37 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.36 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.45 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 68.8 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.4 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 80.0 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.52 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 80.59 |  |

### graph_only_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 71.82 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.75 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 75.3 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.36 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.35 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.18 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.0 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 68.46 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.13 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 68.43 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 70.28 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.88 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 76.91 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 78.52 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 68.82 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.84 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.29 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.32 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 81.48 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.79 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 69.49 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.59 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.62 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.26 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.45 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 118.56 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 82.23 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.75 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.55 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 78.43 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 70.28 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 68.55 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.14 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 75.23 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.02 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.96 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 68.6 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.71 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.24 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.91 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 79.57 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.09 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.26 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.78 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.72 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.03 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.52 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 85.94 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.73 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.18 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 70.82 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.37 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.72 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.97 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 76.59 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.2 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 74.16 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.5 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.56 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.14 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 68.62 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 75.29 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.65 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.42 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.14 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.17 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.81 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 79.75 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.87 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.78 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 69.79 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.6 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.44 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 67.91 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.1 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.63 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.46 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 68.58 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.4 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.9 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 71.5 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.64 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 68.26 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.61 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.15 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.54 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.46 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.0 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 68.72 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 68.51 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 67.53 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.56 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.05 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.78 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 68.81 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 79.59 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.43 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.1 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.28 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 68.61 |  |

### sparse_only_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 70.24 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.68 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.65 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.12 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.6 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.76 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.27 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.25 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.34 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 83.17 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 69.16 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.5 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.42 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.01 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 68.55 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.33 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.92 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 68.49 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.39 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.05 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 71.75 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.59 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 74.32 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 76.78 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.09 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.61 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.79 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.95 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.11 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.11 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 69.85 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.86 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.21 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.74 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.63 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.01 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.61 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 79.56 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.41 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.57 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 69.6 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.33 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.72 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.44 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.61 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.17 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.15 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.35 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.81 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.7 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 69.77 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 75.86 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.12 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.05 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.48 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.4 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.62 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.08 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.52 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.03 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.32 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.71 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.88 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.44 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.86 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 77.57 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.63 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 76.78 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 152.68 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.28 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 68.64 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.88 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.05 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.49 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.38 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.78 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 75.7 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 78.63 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.59 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.77 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 73.27 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.41 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.25 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.47 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.2 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.41 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.48 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.87 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.4 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.97 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 72.11 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 77.73 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.48 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.09 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 74.1 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.43 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.78 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.22 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.6 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.8 |  |

### dense_only_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 69.27 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.99 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.45 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.83 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.2 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 81.0 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.51 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.13 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 75.46 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.5 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 68.19 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.3 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.28 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 68.62 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 68.95 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.72 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.79 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 68.39 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.66 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.82 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 71.04 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.56 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.26 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.02 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.73 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.17 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.06 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.43 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.94 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.94 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 68.55 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.0 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.48 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 81.95 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.91 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.0 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.33 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 79.48 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 74.92 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.34 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 70.86 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.05 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.32 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.48 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.88 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 74.01 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 79.32 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.39 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.93 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 75.41 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 70.53 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.66 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.03 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.07 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 74.58 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.5 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.96 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.37 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.02 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.86 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 81.78 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.56 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 75.68 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.34 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.36 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.0 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.34 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.58 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.38 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.58 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 68.94 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.11 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 68.86 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 68.29 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 80.87 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.47 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.04 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.9 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 75.02 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 68.87 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 68.33 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 68.89 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.72 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.11 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 68.65 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.07 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 75.23 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.45 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.79 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.0 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 71.55 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.46 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.48 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.79 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 68.78 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.18 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.55 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 74.18 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.13 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.27 |  |

### dense_sparse_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 75.74 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.3 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 78.52 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.0 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.79 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.92 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.52 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.47 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.7 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.49 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 70.35 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.32 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.72 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.35 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.85 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 77.66 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.07 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.18 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 81.02 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 76.43 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 71.3 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.22 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 76.12 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 76.92 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 77.76 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.12 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 74.08 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.21 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.1 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 80.39 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 71.7 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 76.6 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 74.15 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.66 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 74.15 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.59 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.63 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.73 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 78.18 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 83.68 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 88.28 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 87.43 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 76.03 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.06 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 75.38 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 80.34 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 82.79 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 77.86 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 83.5 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 81.13 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 76.27 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 81.04 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 80.17 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 86.19 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 83.5 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.25 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.02 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 74.64 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 75.49 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 79.3 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.79 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.87 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.45 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.78 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.05 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 76.67 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.24 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 76.08 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.07 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.91 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 76.13 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.92 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 74.63 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.34 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 74.67 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 74.8 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.13 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.59 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.09 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 75.09 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 71.07 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 79.95 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.98 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 152.98 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.76 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.88 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 68.66 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.15 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.69 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.31 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 68.61 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.04 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 76.4 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 84.19 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 78.26 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 77.58 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 68.52 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.03 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.53 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.28 |  |

### graph_dense_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 69.46 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.54 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.25 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 68.87 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.51 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.2 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 75.25 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 79.05 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.28 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.69 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 71.77 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.9 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.24 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.52 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.37 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.92 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.44 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.69 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.22 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.26 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 72.12 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.84 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.52 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.65 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.96 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.5 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.62 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.92 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.73 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.09 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 68.57 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.37 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 76.72 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.06 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 86.65 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 103.49 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.54 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.21 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.31 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.63 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 69.75 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 84.56 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 78.33 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.05 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.09 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.9 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 77.71 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 79.46 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.95 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.68 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 71.45 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.76 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.56 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.26 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.76 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.92 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 81.93 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.91 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.56 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.24 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.17 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 77.13 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.77 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.99 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.78 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.27 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.66 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.67 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.5 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.52 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 69.85 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.03 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.39 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.27 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 92.78 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 76.54 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.85 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.44 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.5 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.44 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 69.47 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.87 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.47 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 68.75 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.2 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.44 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.59 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.1 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 80.39 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.96 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 69.09 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.89 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.8 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.01 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.93 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.3 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.86 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 68.9 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 68.73 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.09 |  |

### all_paths_planner_dense_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 70.55 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 75.95 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 77.72 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.06 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.49 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 75.89 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.14 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.23 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.16 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.53 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 70.84 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.22 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.1 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.03 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.03 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 75.89 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.31 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.13 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.61 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 74.83 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 70.17 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.62 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.22 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.07 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.86 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 74.82 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.76 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 74.04 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.85 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 75.92 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 77.03 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.91 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.85 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.29 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.08 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.88 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.61 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.04 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 75.51 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 75.73 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 69.15 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.73 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.71 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 80.74 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.62 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.41 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 77.89 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 74.56 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.94 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.37 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 69.77 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 74.63 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.82 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.65 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.98 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.55 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 77.24 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 77.17 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.64 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.97 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.62 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.05 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.71 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.14 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.31 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.78 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.86 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.14 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.64 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.49 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 73.33 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.26 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.43 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.68 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.07 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 74.58 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.59 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.61 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.13 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.3 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 69.42 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.64 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 74.64 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.4 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 78.72 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 75.67 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.3 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.55 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 74.58 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.23 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 69.62 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.09 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.79 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.35 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.68 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.09 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.63 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.95 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 78.48 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 68.74 |  |

### baseline_no_reranker

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 69.7 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.24 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.25 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.3 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.03 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.31 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.82 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.11 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.72 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.95 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 157.77 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 78.08 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.65 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.99 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.14 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.54 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.18 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.83 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.44 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.77 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 71.87 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.93 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.16 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 76.59 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 76.78 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.27 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.12 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.15 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.31 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.77 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 69.31 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.58 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.06 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.28 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.87 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.18 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.81 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.4 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 83.65 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.83 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 70.24 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.28 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 74.2 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.43 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.74 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.38 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.51 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.8 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.44 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.82 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 70.91 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.27 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.75 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 68.52 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.88 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 76.31 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 76.23 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.46 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.4 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.74 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.74 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.21 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.58 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.64 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 75.17 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 80.08 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.67 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.0 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 74.19 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.35 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 72.51 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.67 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.16 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.67 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 74.26 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.21 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.94 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.83 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 78.14 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 75.37 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 72.43 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.86 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 80.41 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.37 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.2 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.0 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 75.63 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.92 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.41 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.32 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 71.94 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.62 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.03 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 74.36 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.88 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 75.58 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.39 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.7 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.6 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.24 |  |

### baseline_weighted_sum

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 73.27 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.06 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.34 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.55 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.58 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.08 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 77.89 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.37 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.81 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.43 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 71.51 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.37 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.46 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.83 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.86 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.24 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.14 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.48 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.01 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.99 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 81.12 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 74.09 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 74.82 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 76.88 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 76.1 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 75.72 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 77.2 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.71 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 75.41 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 74.64 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 75.28 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 74.81 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 75.35 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 80.87 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 74.92 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.19 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 76.73 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 80.65 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 79.52 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 84.83 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 82.11 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 79.97 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 79.73 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 83.77 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 75.09 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 75.54 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 76.74 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 74.54 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 80.77 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 74.55 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 73.74 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 75.34 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 77.73 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 75.42 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 75.54 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 81.57 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 79.31 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.05 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 78.74 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 82.04 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.01 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 74.7 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 75.36 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 74.97 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 74.63 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.87 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.58 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.69 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 81.51 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 74.37 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 75.98 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 75.55 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 76.72 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.25 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 79.76 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 86.71 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 74.02 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.91 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 76.52 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.74 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 74.79 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.6 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.3 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.42 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.93 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 76.72 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.88 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.02 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 77.2 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.74 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 69.53 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.33 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.53 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.72 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.7 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.83 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.22 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.51 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.22 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 77.96 |  |

### baseline_graph_first

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 71.55 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.53 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.34 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.88 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.68 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.09 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.56 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.55 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.33 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.3 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 70.03 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.83 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 75.75 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 80.58 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.05 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 75.34 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.48 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.86 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.77 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.49 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 70.02 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.75 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.15 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.01 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 74.45 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 75.65 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.97 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.12 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.99 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 75.73 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 69.81 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.88 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.56 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.64 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.57 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.92 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.43 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 159.13 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.31 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 84.01 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 70.75 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.89 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.55 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 74.25 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.02 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.54 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 78.76 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.94 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.66 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 75.88 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 68.67 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.11 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 79.7 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 90.84 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.49 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.81 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.12 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.65 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.5 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.75 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.64 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 78.74 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.8 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.58 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.46 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.75 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 79.52 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.33 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 72.61 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 74.14 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 72.2 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.47 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.25 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.0 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 75.09 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.65 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.44 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 69.69 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 76.13 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 77.68 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 72.88 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.98 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.38 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.33 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 77.25 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.91 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.75 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.28 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.61 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 75.24 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 70.13 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.99 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.9 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.54 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.9 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 75.26 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 71.47 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 73.13 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.63 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 70.11 |  |
