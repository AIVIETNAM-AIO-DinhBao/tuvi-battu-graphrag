# W6 Evaluation report: w8_abl_01_retrieval_fusion_reranker_v2

- Dataset: `D:\University\Năm 3 ĐH\Kì 3 (18th6)\Text Mining\tuvi-battu-graphrag\benchmark\tuvi_golden_dataset\release\tuviqa_v1_release.jsonl`
- Dataset items: 6
- Configs: 10
- Judge backend: `gemini`
- Started: 2026-07-16T17:33:52.418708Z
- Completed: 2026-07-16T17:46:23.146777Z
- Notes: W8 retrieval/fusion/reranker matrix v2. All variants hold semantic BGE-M3 chunking, prompt v1, Gemini Flash Lite, balanced context assembly, query rewrite off, document grading on, and cache disabled constant. Dense remains planner-gated at runtime. This matrix removes the duplicate graph+sparse cell and isolates graph_first to fusion_method only.
- Run status: `completed`

## Run identity and provenance

- Identity SHA-256: `46ea3d9211290cfd86f99e273c76bf5515ae026913e95111089463f4a038131c`
- Dataset SHA-256: `90376a87cec29cc22e93dc71b41e054ed2f0183bc515a52aa461fecd43cc008c`
- Manifest SHA-256: `5285d001b1ad92e80a98baf09d7f5f6c9997ec1d483e5c9b6c50139557591b14`
- Evaluator SHA-256: `9ae528d893159c4092c3129523da8d69a7a79a6ab5c32a132791158287eda314`
- Git SHA: `bd1305c1a97907cd1ee397790eb5bafa4f3a666f`
- Git dirty: `False`
- Judge model: `gemini-3.1-flash-lite-preview`
- Checkpoint: `benchmark\tuvi_golden_dataset\reports\w8_eval_preflight_01\retrieval_matrix_limit6\checkpoint\evaluation_checkpoint.json`

## Execution completeness

- Expected pairs: 60
- Completed pairs: 60
- Failed pairs: 0
- Executed pairs: 60
- Resumed pairs: 0

> **Metric policy:** W6-EVAL-02 runs the RAG pipeline directly with the selected `ExperimentConfig`. `Context recall` is the Gemini-judged corpus-grounding score for non-Direct items; Direct/chart-only items are excluded from corpus retrieval/citation metrics and reported through `chart_context_grounding`.

## Overall metrics

| Config | Status | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms | Retrieval p95 ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline_graph_sparse_rrf | completed | 6 | 0.95 | 0.8167 | 0.64 | 1.0 | 1.0 | 18355.95 | 15561.81 |
| graph_only_rrf | completed | 6 | 0.5833 | 0.5333 | 0.38 | 1.0 | 0.8 | 13784.43 | 11477.87 |
| sparse_only_rrf | completed | 6 | 0.9167 | 0.85 | 0.7 | 0.0 | 1.0 | 5325.9 | 3028.77 |
| dense_only_rrf | completed | 6 | 0.9667 | 0.8667 | 0.88 | 0.0 | 1.0 | 19639.46 | 17251.15 |
| dense_sparse_rrf | completed | 6 | 0.9667 | 0.9 | 0.78 | 0.0 | 1.0 | 7408.46 | 4783.67 |
| graph_dense_rrf | completed | 6 | 0.9333 | 0.8833 | 0.84 | 1.0 | 1.0 | 14766.62 | 12416.1 |
| all_paths_planner_dense_rrf | completed | 6 | 0.9333 | 0.7833 | 0.62 | 1.0 | 1.0 | 17414.4 | 15019.4 |
| baseline_no_reranker | completed | 6 | 0.9333 | 0.9 | 0.86 | 1.0 | 1.0 | 17360.68 | 15203.9 |
| baseline_weighted_sum | completed | 6 | 0.95 | 0.9167 | 0.94 | 1.0 | 1.0 | 17376.48 | 15119.33 |
| baseline_graph_first | completed | 6 | 0.85 | 0.7 | 0.6 | 1.0 | 1.0 | 17280.41 | 15052.0 |

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
  - Selected `baseline_weighted_sum` with context_recall_avg=0.94, citation_coverage_rate=1.0, p95_latency_ms=17376.48.
  - Treat this as a smoke/first-pass recommendation until official Gemini judge and full dataset runs are complete.

### Context recall ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | baseline_weighted_sum | 0.94 |
| 2 | dense_only_rrf | 0.88 |
| 3 | baseline_no_reranker | 0.86 |
| 4 | graph_dense_rrf | 0.84 |
| 5 | dense_sparse_rrf | 0.78 |
| 6 | sparse_only_rrf | 0.7 |
| 7 | baseline_graph_sparse_rrf | 0.64 |
| 8 | all_paths_planner_dense_rrf | 0.62 |
| 9 | baseline_graph_first | 0.6 |
| 10 | graph_only_rrf | 0.38 |

### Citation coverage ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | baseline_graph_sparse_rrf | 1.0 |
| 2 | sparse_only_rrf | 1.0 |
| 3 | dense_only_rrf | 1.0 |
| 4 | dense_sparse_rrf | 1.0 |
| 5 | graph_dense_rrf | 1.0 |
| 6 | all_paths_planner_dense_rrf | 1.0 |
| 7 | baseline_no_reranker | 1.0 |
| 8 | baseline_weighted_sum | 1.0 |
| 9 | baseline_graph_first | 1.0 |
| 10 | graph_only_rrf | 0.8 |

### Graph hit ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | baseline_graph_sparse_rrf | 1.0 |
| 2 | graph_only_rrf | 1.0 |
| 3 | graph_dense_rrf | 1.0 |
| 4 | all_paths_planner_dense_rrf | 1.0 |
| 5 | baseline_no_reranker | 1.0 |
| 6 | baseline_weighted_sum | 1.0 |
| 7 | baseline_graph_first | 1.0 |
| 8 | sparse_only_rrf | 0.0 |
| 9 | dense_only_rrf | 0.0 |
| 10 | dense_sparse_rrf | 0.0 |

### p95 latency ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | sparse_only_rrf | 5325.9 |
| 2 | dense_sparse_rrf | 7408.46 |
| 3 | graph_only_rrf | 13784.43 |
| 4 | graph_dense_rrf | 14766.62 |
| 5 | baseline_graph_first | 17280.41 |
| 6 | baseline_no_reranker | 17360.68 |
| 7 | baseline_weighted_sum | 17376.48 |
| 8 | all_paths_planner_dense_rrf | 17414.4 |
| 9 | baseline_graph_sparse_rrf | 18355.95 |
| 10 | dense_only_rrf | 19639.46 |

### Retrieval miss summary

| Config | Miss count | Example item IDs |
|---|---:|---|
| baseline_graph_sparse_rrf | 1 | TVQA-003 |
| graph_only_rrf | 5 | TVQA-002, TVQA-003, TVQA-004, TVQA-005, TVQA-006 |
| sparse_only_rrf | 1 | TVQA-003 |
| dense_only_rrf | 0 |  |
| dense_sparse_rrf | 0 |  |
| graph_dense_rrf | 0 |  |
| all_paths_planner_dense_rrf | 1 | TVQA-003 |
| baseline_no_reranker | 0 |  |
| baseline_weighted_sum | 0 |  |
| baseline_graph_first | 1 | TVQA-003 |

### Rerank miss summary

| Config | Miss count | Example item IDs |
|---|---:|---|
| baseline_graph_sparse_rrf | 0 |  |
| graph_only_rrf | 4 | TVQA-002, TVQA-003, TVQA-004, TVQA-006 |
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
| baseline_graph_sparse_rrf | Direct | 1 | 1.0 | 1.0 | None | None | None | 1444.03 |
| baseline_graph_sparse_rrf | One-hop | 4 | 0.95 | 0.75 | 0.6 | 1.0 | 1.0 | 15609.02 |
| baseline_graph_sparse_rrf | Two-hop | 1 | 0.9 | 0.9 | 0.8 | 1.0 | 1.0 | 19228.86 |
| graph_only_rrf | Direct | 1 | 1.0 | 1.0 | None | None | None | 966.52 |
| graph_only_rrf | One-hop | 4 | 0.375 | 0.35 | 0.3 | 1.0 | 0.8125 | 11903.27 |
| graph_only_rrf | Two-hop | 1 | 1.0 | 0.8 | 0.7 | 1.0 | 0.75 | 14386.3 |
| sparse_only_rrf | Direct | 1 | 1.0 | 1.0 | None | None | None | 884.82 |
| sparse_only_rrf | One-hop | 4 | 0.9 | 0.8 | 0.675 | 0.0 | 1.0 | 4547.38 |
| sparse_only_rrf | Two-hop | 1 | 0.9 | 0.9 | 0.8 | 0.0 | 1.0 | 5580.64 |
| dense_only_rrf | Direct | 1 | 1.0 | 1.0 | None | None | None | 878.74 |
| dense_only_rrf | One-hop | 4 | 0.95 | 0.85 | 0.9 | 0.0 | 1.0 | 21650.4 |
| dense_only_rrf | Two-hop | 1 | 1.0 | 0.8 | 0.8 | 0.0 | 1.0 | 3887.64 |
| dense_sparse_rrf | Direct | 1 | 1.0 | 1.0 | None | None | None | 880.04 |
| dense_sparse_rrf | One-hop | 4 | 0.95 | 0.875 | 0.775 | 0.0 | 1.0 | 5655.04 |
| dense_sparse_rrf | Two-hop | 1 | 1.0 | 0.9 | 0.8 | 0.0 | 1.0 | 7972.86 |
| graph_dense_rrf | Direct | 1 | 1.0 | 1.0 | None | None | None | 877.14 |
| graph_dense_rrf | One-hop | 4 | 0.95 | 0.9 | 0.9 | 1.0 | 1.0 | 13028.18 |
| graph_dense_rrf | Two-hop | 1 | 0.8 | 0.7 | 0.6 | 1.0 | 1.0 | 15333.34 |
| all_paths_planner_dense_rrf | Direct | 1 | 1.0 | 1.0 | None | None | None | 884.93 |
| all_paths_planner_dense_rrf | One-hop | 4 | 0.95 | 0.825 | 0.65 | 1.0 | 1.0 | 15054.42 |
| all_paths_planner_dense_rrf | Two-hop | 1 | 0.8 | 0.4 | 0.5 | 1.0 | 1.0 | 18200.58 |
| baseline_no_reranker | Direct | 1 | 1.0 | 1.0 | None | None | None | 820.42 |
| baseline_no_reranker | One-hop | 4 | 0.95 | 0.925 | 0.875 | 1.0 | 1.0 | 14861.7 |
| baseline_no_reranker | Two-hop | 1 | 0.8 | 0.7 | 0.8 | 1.0 | 1.0 | 18180.74 |
| baseline_weighted_sum | Direct | 1 | 1.0 | 1.0 | None | None | None | 944.7 |
| baseline_weighted_sum | One-hop | 4 | 0.95 | 0.9 | 0.925 | 1.0 | 1.0 | 15172.71 |
| baseline_weighted_sum | Two-hop | 1 | 0.9 | 0.9 | 1.0 | 1.0 | 1.0 | 18062.16 |
| baseline_graph_first | Direct | 1 | 1.0 | 1.0 | None | None | None | 848.07 |
| baseline_graph_first | One-hop | 4 | 0.825 | 0.625 | 0.6 | 1.0 | 1.0 | 15300.12 |
| baseline_graph_first | Two-hop | 1 | 0.8 | 0.7 | 0.6 | 1.0 | 1.0 | 17879.54 |

## Metrics by question family

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| baseline_graph_sparse_rrf | core_identity | 1 | 1.0 | 1.0 | None | None | None | 1444.03 |
| baseline_graph_sparse_rrf | menh_cuc_relation | 1 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 14882.47 |
| baseline_graph_sparse_rrf | menh_house_interpretation | 1 | 1.0 | 0.8 | 0.8 | 1.0 | 1.0 | 15737.23 |
| baseline_graph_sparse_rrf | menh_tam_hop | 1 | 0.9 | 0.9 | 0.8 | 1.0 | 1.0 | 19228.86 |
| baseline_graph_sparse_rrf | special_state_interpretation | 1 | 0.8 | 0.7 | 0.6 | 1.0 | 1.0 | 11132.08 |
| baseline_graph_sparse_rrf | than_cu_interpretation | 1 | 1.0 | 0.5 | 0.0 | 1.0 | 1.0 | 11992.35 |
| graph_only_rrf | core_identity | 1 | 1.0 | 1.0 | None | None | None | 966.52 |
| graph_only_rrf | menh_cuc_relation | 1 | 1.0 | 0.8 | 1.0 | 1.0 | 0.75 | 11978.84 |
| graph_only_rrf | menh_house_interpretation | 1 | 0.0 | 0.0 | 0.0 | 1.0 | 0.75 | 11475.06 |
| graph_only_rrf | menh_tam_hop | 1 | 1.0 | 0.8 | 0.7 | 1.0 | 0.75 | 14386.3 |
| graph_only_rrf | special_state_interpretation | 1 | 0.5 | 0.6 | 0.2 | 1.0 | 1.0 | 8968.56 |
| graph_only_rrf | than_cu_interpretation | 1 | 0.0 | 0.0 | 0.0 | 1.0 | 0.75 | 9329.16 |
| sparse_only_rrf | core_identity | 1 | 1.0 | 1.0 | None | None | None | 884.82 |
| sparse_only_rrf | menh_cuc_relation | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 1.0 | 3806.53 |
| sparse_only_rrf | menh_house_interpretation | 1 | 1.0 | 0.8 | 0.8 | 0.0 | 1.0 | 4466.48 |
| sparse_only_rrf | menh_tam_hop | 1 | 0.9 | 0.9 | 0.8 | 0.0 | 1.0 | 5580.64 |
| sparse_only_rrf | special_state_interpretation | 1 | 0.8 | 0.9 | 0.7 | 0.0 | 1.0 | 4561.66 |
| sparse_only_rrf | than_cu_interpretation | 1 | 0.8 | 0.5 | 0.2 | 0.0 | 1.0 | 4241.94 |
| dense_only_rrf | core_identity | 1 | 1.0 | 1.0 | None | None | None | 878.74 |
| dense_only_rrf | menh_cuc_relation | 1 | 1.0 | 0.9 | 1.0 | 0.0 | 1.0 | 2570.98 |
| dense_only_rrf | menh_house_interpretation | 1 | 1.0 | 0.9 | 1.0 | 0.0 | 1.0 | 24890.06 |
| dense_only_rrf | menh_tam_hop | 1 | 1.0 | 0.8 | 0.8 | 0.0 | 1.0 | 3887.64 |
| dense_only_rrf | special_state_interpretation | 1 | 0.8 | 0.7 | 0.6 | 0.0 | 1.0 | 3058.17 |
| dense_only_rrf | than_cu_interpretation | 1 | 1.0 | 0.9 | 1.0 | 0.0 | 1.0 | 3292.32 |
| dense_sparse_rrf | core_identity | 1 | 1.0 | 1.0 | None | None | None | 880.04 |
| dense_sparse_rrf | menh_cuc_relation | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 1.0 | 4477.1 |
| dense_sparse_rrf | menh_house_interpretation | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 1.0 | 5040.46 |
| dense_sparse_rrf | menh_tam_hop | 1 | 1.0 | 0.9 | 0.8 | 0.0 | 1.0 | 7972.86 |
| dense_sparse_rrf | special_state_interpretation | 1 | 0.8 | 0.7 | 0.5 | 0.0 | 1.0 | 5715.26 |
| dense_sparse_rrf | than_cu_interpretation | 1 | 1.0 | 0.8 | 0.6 | 0.0 | 1.0 | 5313.77 |
| graph_dense_rrf | core_identity | 1 | 1.0 | 1.0 | None | None | None | 877.14 |
| graph_dense_rrf | menh_cuc_relation | 1 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 13066.48 |
| graph_dense_rrf | menh_house_interpretation | 1 | 1.0 | 0.9 | 1.0 | 1.0 | 1.0 | 12811.13 |
| graph_dense_rrf | menh_tam_hop | 1 | 0.8 | 0.7 | 0.6 | 1.0 | 1.0 | 15333.34 |
| graph_dense_rrf | special_state_interpretation | 1 | 0.8 | 0.7 | 0.6 | 1.0 | 1.0 | 9058.85 |
| graph_dense_rrf | than_cu_interpretation | 1 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 10215.78 |
| all_paths_planner_dense_rrf | core_identity | 1 | 1.0 | 1.0 | None | None | None | 884.93 |
| all_paths_planner_dense_rrf | menh_cuc_relation | 1 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 15046.26 |
| all_paths_planner_dense_rrf | menh_house_interpretation | 1 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 15055.86 |
| all_paths_planner_dense_rrf | menh_tam_hop | 1 | 0.8 | 0.4 | 0.5 | 1.0 | 1.0 | 18200.58 |
| all_paths_planner_dense_rrf | special_state_interpretation | 1 | 0.8 | 0.7 | 0.6 | 1.0 | 1.0 | 11405.95 |
| all_paths_planner_dense_rrf | than_cu_interpretation | 1 | 1.0 | 0.6 | 0.0 | 1.0 | 1.0 | 12221.56 |
| baseline_no_reranker | core_identity | 1 | 1.0 | 1.0 | None | None | None | 820.42 |
| baseline_no_reranker | menh_cuc_relation | 1 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 14900.51 |
| baseline_no_reranker | menh_house_interpretation | 1 | 1.0 | 0.8 | 0.8 | 1.0 | 1.0 | 14641.79 |
| baseline_no_reranker | menh_tam_hop | 1 | 0.8 | 0.7 | 0.8 | 1.0 | 1.0 | 18180.74 |
| baseline_no_reranker | special_state_interpretation | 1 | 0.8 | 0.9 | 0.7 | 1.0 | 1.0 | 10895.47 |
| baseline_no_reranker | than_cu_interpretation | 1 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 12128.99 |
| baseline_weighted_sum | core_identity | 1 | 1.0 | 1.0 | None | None | None | 944.7 |
| baseline_weighted_sum | menh_cuc_relation | 1 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 14341.27 |
| baseline_weighted_sum | menh_house_interpretation | 1 | 1.0 | 0.9 | 1.0 | 1.0 | 1.0 | 15319.43 |
| baseline_weighted_sum | menh_tam_hop | 1 | 0.9 | 0.9 | 1.0 | 1.0 | 1.0 | 18062.16 |
| baseline_weighted_sum | special_state_interpretation | 1 | 1.0 | 0.8 | 0.7 | 1.0 | 1.0 | 11091.75 |
| baseline_weighted_sum | than_cu_interpretation | 1 | 0.8 | 0.9 | 1.0 | 1.0 | 1.0 | 12264.62 |
| baseline_graph_first | core_identity | 1 | 1.0 | 1.0 | None | None | None | 848.07 |
| baseline_graph_first | menh_cuc_relation | 1 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 14263.71 |
| baseline_graph_first | menh_house_interpretation | 1 | 1.0 | 0.8 | 0.8 | 1.0 | 1.0 | 15483.02 |
| baseline_graph_first | menh_tam_hop | 1 | 0.8 | 0.7 | 0.6 | 1.0 | 1.0 | 17879.54 |
| baseline_graph_first | special_state_interpretation | 1 | 0.8 | 0.7 | 0.6 | 1.0 | 1.0 | 11135.59 |
| baseline_graph_first | than_cu_interpretation | 1 | 0.5 | 0.0 | 0.0 | 1.0 | 1.0 | 12164.33 |

## Per-question results

### baseline_graph_sparse_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1444.03 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 2 | 15737.23 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.5 | 0.0 | True | 1.0 | 2 | 11992.35 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 14882.47 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 11132.08 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.9 | 0.8 | True | 1.0 | 4 | 19228.86 |  |

### graph_only_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 966.52 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 0.0 | 0.0 | 0.0 | True | 0.75 | 1 | 11475.06 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 0.0 | 0.0 | 0.0 | True | 0.75 | 1 | 9329.16 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 1.0 | True | 0.75 | 1 | 11978.84 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 0.5 | 0.6 | 0.2 | True | 1.0 | 2 | 8968.56 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.7 | True | 0.75 | 1 | 14386.3 |  |

### sparse_only_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 884.82 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.8 | False | 1.0 | 2 | 4466.48 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.5 | 0.2 | False | 1.0 | 2 | 4241.94 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 4 | 3806.53 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 3 | 4561.66 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.9 | 0.8 | False | 1.0 | 5 | 5580.64 |  |

### dense_only_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 878.74 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 1.0 | False | 1.0 | 4 | 24890.06 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 1.0 | False | 1.0 | 3 | 3292.32 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.9 | 1.0 | False | 1.0 | 5 | 2570.98 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 3 | 3058.17 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.8 | False | 1.0 | 2 | 3887.64 |  |

### dense_sparse_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 880.04 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 2 | 5040.46 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.6 | False | 1.0 | 2 | 5313.77 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 3 | 4477.1 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.5 | False | 1.0 | 4 | 5715.26 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 0.8 | False | 1.0 | 4 | 7972.86 |  |

### graph_dense_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 877.14 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 12811.13 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 10215.78 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 13066.48 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 5 | 9058.85 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 2 | 15333.34 |  |

### all_paths_planner_dense_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 884.93 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 15055.86 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.6 | 0.0 | True | 1.0 | 2 | 12221.56 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 15046.26 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 3 | 11405.95 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.4 | 0.5 | True | 1.0 | 5 | 18200.58 |  |

### baseline_no_reranker

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 820.42 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 2 | 14641.79 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 12128.99 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 14900.51 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 10895.47 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.8 | True | 1.0 | 6 | 18180.74 |  |

### baseline_weighted_sum

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 944.7 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 2 | 15319.43 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.9 | 1.0 | True | 1.0 | 2 | 12264.62 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 14341.27 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 4 | 11091.75 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.9 | 1.0 | True | 1.0 | 4 | 18062.16 |  |

### baseline_graph_first

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 848.07 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 2 | 15483.02 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 0.5 | 0.0 | 0.0 | True | 1.0 | 2 | 12164.33 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 14263.71 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 3 | 11135.59 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 17879.54 |  |
