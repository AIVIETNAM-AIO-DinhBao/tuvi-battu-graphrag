# W6 Evaluation report: w8_abl_01_retrieval_fusion_reranker_v3_k40

- Dataset: `benchmark/tuvi_golden_dataset/release/tuviqa_v1_release.jsonl`
- Dataset items: 100
- Configs: 10
- Judge backend: `gemini`
- Started: 2026-08-15T01:33:56.212641Z
- Completed: 2026-08-16T19:02:15.653079Z
- Notes: Hybrid W8 retrieval/fusion/reranker matrix v3. Reranker-enabled variants use BGE reranker top_k=40; two completed Graph+Sparse controls are reused with provenance from Phase 52. Semantic BGE-M3 chunking, structured prompt v3, Gemini Flash Lite, balanced context assembly, query rewrite off, document grading on, and cache disabled are held constant.
- Run status: `completed`

## Run identity and provenance

- Identity SHA-256: `2b5a44703b1cc57650b39206ce287fd6dddd5d2d7f44fdbb2791b832ed4db520`
- Dataset SHA-256: `90376a87cec29cc22e93dc71b41e054ed2f0183bc515a52aa461fecd43cc008c`
- Manifest SHA-256: `b6810b2814e9280b68d5b24f6debd2a43039dceb46848ed351eeaabb9468b7b7`
- Evaluator SHA-256: `487e4762a669fec1d4c3059f75d3665b35ad1327ea05ae5de6421dc41487ff8f`
- Git SHA: `b8b514c5f7f4e1c87488c3a559c51085324515a4`
- Git dirty: `False`
- Judge model: `gemini-3.1-flash-lite-preview`
- Checkpoint: `benchmark/tuvi_golden_dataset/reports_final/53_retrieval_fusion_reranker_k40_matrix/checkpoints/checkpoint_summary.json`

## Execution completeness

- Expected pairs: 1000
- Completed pairs: 1000
- Failed pairs: 0
- Executed pairs: 69
- Resumed pairs: 931

> **Metric policy:** W6-EVAL-02 runs the RAG pipeline directly with the selected `ExperimentConfig`. `Context recall` is the Gemini-judged corpus-grounding score for non-Direct items; Direct/chart-only items are excluded from corpus retrieval/citation metrics and reported through `chart_context_grounding`.

## Overall metrics

| Config | Status | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms | Retrieval p95 ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| semantic_gs_rrf_rerank_k40 | completed | 100 | 0.906 | 0.83 | 0.7571 | 0.967 | 0.989 | 168191.23 | 162516.16 |
| graph_only_rrf_k40 | completed | 100 | 0.858 | 0.737 | 0.5885 | 0.967 | 0.9533 | 40724.49 | 34791.93 |
| sparse_only_rrf_k40 | completed | 100 | 0.909 | 0.8 | 0.7275 | 0.0 | 0.989 | 162410.7 | 157760.03 |
| dense_only_rrf_k40 | completed | 100 | 0.901 | 0.811 | 0.7302 | 0.0 | 0.978 | 25463.88 | 21173.1 |
| dense_sparse_rrf_k40 | completed | 100 | 0.911 | 0.833 | 0.7549 | 0.0 | 0.989 | 172348.24 | 167455.73 |
| graph_dense_rrf_k40 | completed | 100 | 0.907 | 0.809 | 0.7286 | 0.967 | 0.989 | 76817.94 | 72364.38 |
| all_paths_planner_dense_rrf_k40 | completed | 100 | 0.927 | 0.819 | 0.7396 | 0.967 | 0.989 | 198212.63 | 191696.37 |
| semantic_gs_rrf_no_rerank_reference | completed | 100 | 0.888 | 0.815 | 0.7407 | 0.967 | 0.989 | 21543.56 | 8321.1 |
| graph_sparse_weighted_sum_k40 | completed | 100 | 0.925 | 0.82 | 0.7297 | 0.967 | 0.989 | 170644.91 | 164716.39 |
| graph_sparse_graph_first_k40 | completed | 100 | 0.923 | 0.834 | 0.7516 | 0.967 | 0.978 | 215686.52 | 204464.14 |

## Failure and fallback summary

| Config | Failed | Generation backend fallback | Judge failure | No context | Retrieval backend fallback | Citation fallback |
|---|---:|---:|---:|---:|---:|---:|
| semantic_gs_rrf_rerank_k40 | 0 | 0 | 0 | 0 | 0 | 0 |
| graph_only_rrf_k40 | 0 | 0 | 0 | 0 | 0 | 0 |
| sparse_only_rrf_k40 | 0 | 0 | 0 | 0 | 0 | 0 |
| dense_only_rrf_k40 | 0 | 0 | 0 | 0 | 0 | 0 |
| dense_sparse_rrf_k40 | 0 | 0 | 0 | 0 | 0 | 0 |
| graph_dense_rrf_k40 | 0 | 0 | 0 | 0 | 0 | 0 |
| all_paths_planner_dense_rrf_k40 | 0 | 0 | 0 | 0 | 0 | 0 |
| semantic_gs_rrf_no_rerank_reference | 0 | 0 | 0 | 0 | 0 | 0 |
| graph_sparse_weighted_sum_k40 | 0 | 0 | 0 | 0 | 0 | 0 |
| graph_sparse_graph_first_k40 | 0 | 0 | 0 | 0 | 0 | 1 |

## Ablation analysis

- Baseline config: `baseline_graph_sparse_rrf`
- Preliminary recommendation: `semantic_gs_rrf_rerank_k40`
  - Preliminary heuristic ranks configs by context recall, citation coverage, faithfulness, answer relevancy, graph hit rate, and a small p95 latency penalty.
  - Selected `semantic_gs_rrf_rerank_k40` with context_recall_avg=0.7571, citation_coverage_rate=0.989, p95_latency_ms=168191.23.
  - Treat this as a smoke/first-pass recommendation until official Gemini judge and full dataset runs are complete.

### Context recall ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | semantic_gs_rrf_rerank_k40 | 0.7571 |
| 2 | dense_sparse_rrf_k40 | 0.7549 |
| 3 | graph_sparse_graph_first_k40 | 0.7516 |
| 4 | semantic_gs_rrf_no_rerank_reference | 0.7407 |
| 5 | all_paths_planner_dense_rrf_k40 | 0.7396 |
| 6 | dense_only_rrf_k40 | 0.7302 |
| 7 | graph_sparse_weighted_sum_k40 | 0.7297 |
| 8 | graph_dense_rrf_k40 | 0.7286 |
| 9 | sparse_only_rrf_k40 | 0.7275 |
| 10 | graph_only_rrf_k40 | 0.5885 |

### Citation coverage ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | semantic_gs_rrf_rerank_k40 | 0.989 |
| 2 | sparse_only_rrf_k40 | 0.989 |
| 3 | dense_sparse_rrf_k40 | 0.989 |
| 4 | graph_dense_rrf_k40 | 0.989 |
| 5 | all_paths_planner_dense_rrf_k40 | 0.989 |
| 6 | semantic_gs_rrf_no_rerank_reference | 0.989 |
| 7 | graph_sparse_weighted_sum_k40 | 0.989 |
| 8 | dense_only_rrf_k40 | 0.978 |
| 9 | graph_sparse_graph_first_k40 | 0.978 |
| 10 | graph_only_rrf_k40 | 0.9533 |

### Graph hit ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | semantic_gs_rrf_rerank_k40 | 0.967 |
| 2 | graph_only_rrf_k40 | 0.967 |
| 3 | graph_dense_rrf_k40 | 0.967 |
| 4 | all_paths_planner_dense_rrf_k40 | 0.967 |
| 5 | semantic_gs_rrf_no_rerank_reference | 0.967 |
| 6 | graph_sparse_weighted_sum_k40 | 0.967 |
| 7 | graph_sparse_graph_first_k40 | 0.967 |
| 8 | sparse_only_rrf_k40 | 0.0 |
| 9 | dense_only_rrf_k40 | 0.0 |
| 10 | dense_sparse_rrf_k40 | 0.0 |

### p95 latency ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | semantic_gs_rrf_no_rerank_reference | 21543.56 |
| 2 | dense_only_rrf_k40 | 25463.88 |
| 3 | graph_only_rrf_k40 | 40724.49 |
| 4 | graph_dense_rrf_k40 | 76817.94 |
| 5 | sparse_only_rrf_k40 | 162410.7 |
| 6 | semantic_gs_rrf_rerank_k40 | 168191.23 |
| 7 | graph_sparse_weighted_sum_k40 | 170644.91 |
| 8 | dense_sparse_rrf_k40 | 172348.24 |
| 9 | all_paths_planner_dense_rrf_k40 | 198212.63 |
| 10 | graph_sparse_graph_first_k40 | 215686.52 |

### Retrieval miss summary

| Config | Miss count | Example item IDs |
|---|---:|---|
| semantic_gs_rrf_rerank_k40 | 11 | TVQA-008, TVQA-010, TVQA-027, TVQA-039, TVQA-045 |
| graph_only_rrf_k40 | 30 | TVQA-008, TVQA-016, TVQA-017, TVQA-025, TVQA-027 |
| sparse_only_rrf_k40 | 16 | TVQA-008, TVQA-010, TVQA-012, TVQA-027, TVQA-028 |
| dense_only_rrf_k40 | 14 | TVQA-008, TVQA-010, TVQA-025, TVQA-027, TVQA-032 |
| dense_sparse_rrf_k40 | 12 | TVQA-008, TVQA-010, TVQA-027, TVQA-032, TVQA-038 |
| graph_dense_rrf_k40 | 18 | TVQA-008, TVQA-025, TVQA-027, TVQA-028, TVQA-032 |
| all_paths_planner_dense_rrf_k40 | 12 | TVQA-010, TVQA-012, TVQA-017, TVQA-027, TVQA-032 |
| semantic_gs_rrf_no_rerank_reference | 13 | TVQA-008, TVQA-010, TVQA-028, TVQA-032, TVQA-038 |
| graph_sparse_weighted_sum_k40 | 13 | TVQA-025, TVQA-027, TVQA-028, TVQA-032, TVQA-039 |
| graph_sparse_graph_first_k40 | 10 | TVQA-010, TVQA-012, TVQA-027, TVQA-030, TVQA-032 |

### Rerank miss summary

| Config | Miss count | Example item IDs |
|---|---:|---|
| semantic_gs_rrf_rerank_k40 | 0 |  |
| graph_only_rrf_k40 | 4 | TVQA-017, TVQA-039, TVQA-084, TVQA-096 |
| sparse_only_rrf_k40 | 0 |  |
| dense_only_rrf_k40 | 2 | TVQA-025, TVQA-047 |
| dense_sparse_rrf_k40 | 0 |  |
| graph_dense_rrf_k40 | 2 | TVQA-025, TVQA-084 |
| all_paths_planner_dense_rrf_k40 | 0 |  |
| semantic_gs_rrf_no_rerank_reference | 0 |  |
| graph_sparse_weighted_sum_k40 | 0 |  |
| graph_sparse_graph_first_k40 | 1 | TVQA-052 |

## Metrics by question complexity

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| semantic_gs_rrf_rerank_k40 | Direct | 10 | 1.0 | 0.81 | 0.6 | 0.0 | 0.0 | 18605.05 |
| semantic_gs_rrf_rerank_k40 | One-hop | 46 | 0.8957 | 0.8326 | 0.7793 | 0.9783 | 1.0 | 162084.43 |
| semantic_gs_rrf_rerank_k40 | Two-hop | 44 | 0.8955 | 0.8318 | 0.7375 | 0.9773 | 1.0 | 172411.33 |
| graph_only_rrf_k40 | Direct | 10 | 1.0 | 0.84 | 0.7 | 0.0 | 0.0 | 3836.92 |
| graph_only_rrf_k40 | One-hop | 46 | 0.8587 | 0.7413 | 0.6109 | 0.9783 | 0.9783 | 40372.46 |
| graph_only_rrf_k40 | Two-hop | 44 | 0.825 | 0.7091 | 0.5625 | 0.9773 | 0.9489 | 40444.01 |
| sparse_only_rrf_k40 | Direct | 10 | 1.0 | 0.8 | 0.5 | 0.0 | 0.0 | 3700.86 |
| sparse_only_rrf_k40 | One-hop | 46 | 0.9283 | 0.8 | 0.7435 | 0.0 | 1.0 | 160214.2 |
| sparse_only_rrf_k40 | Two-hop | 44 | 0.8682 | 0.8 | 0.7159 | 0.0 | 1.0 | 186707.03 |
| dense_only_rrf_k40 | Direct | 10 | 1.0 | 0.83 | 0.8 | 0.0 | 0.0 | 4038.62 |
| dense_only_rrf_k40 | One-hop | 46 | 0.8913 | 0.8065 | 0.738 | 0.0 | 1.0 | 26084.68 |
| dense_only_rrf_k40 | Two-hop | 44 | 0.8886 | 0.8114 | 0.7205 | 0.0 | 0.9773 | 25105.49 |
| dense_sparse_rrf_k40 | Direct | 10 | 1.0 | 0.81 | 0.7 | 0.0 | 0.0 | 4548.79 |
| dense_sparse_rrf_k40 | One-hop | 46 | 0.9174 | 0.8391 | 0.7674 | 0.0 | 1.0 | 168586.3 |
| dense_sparse_rrf_k40 | Two-hop | 44 | 0.8841 | 0.8318 | 0.7432 | 0.0 | 1.0 | 183169.72 |
| graph_dense_rrf_k40 | Direct | 10 | 1.0 | 0.87 | 0.7 | 0.0 | 0.0 | 6186.7 |
| graph_dense_rrf_k40 | One-hop | 46 | 0.9022 | 0.813 | 0.7522 | 0.9783 | 1.0 | 87690.46 |
| graph_dense_rrf_k40 | Two-hop | 44 | 0.8909 | 0.7909 | 0.7045 | 0.9773 | 1.0 | 58261.37 |
| all_paths_planner_dense_rrf_k40 | Direct | 10 | 1.0 | 0.85 | 0.8 | 0.0 | 0.0 | 8581.57 |
| all_paths_planner_dense_rrf_k40 | One-hop | 46 | 0.9391 | 0.8283 | 0.7739 | 0.9783 | 1.0 | 196423.01 |
| all_paths_planner_dense_rrf_k40 | Two-hop | 44 | 0.8977 | 0.8023 | 0.7023 | 0.9773 | 1.0 | 206383.49 |
| semantic_gs_rrf_no_rerank_reference | Direct | 10 | 1.0 | 0.81 | 0.8 | 0.0 | 0.0 | 27542.93 |
| semantic_gs_rrf_no_rerank_reference | One-hop | 46 | 0.8826 | 0.8174 | 0.75 | 0.9783 | 1.0 | 23486.2 |
| semantic_gs_rrf_no_rerank_reference | Two-hop | 44 | 0.8682 | 0.8136 | 0.7295 | 0.9773 | 1.0 | 20075.08 |
| graph_sparse_weighted_sum_k40 | Direct | 10 | 0.98 | 0.82 | 0.7 | 0.0 | 0.0 | 6002.8 |
| graph_sparse_weighted_sum_k40 | One-hop | 46 | 0.9304 | 0.8217 | 0.7435 | 0.9783 | 1.0 | 170083.35 |
| graph_sparse_weighted_sum_k40 | Two-hop | 44 | 0.9068 | 0.8182 | 0.7159 | 0.9773 | 1.0 | 170415.34 |
| graph_sparse_graph_first_k40 | Direct | 10 | 1.0 | 0.83 | 0.8 | 0.0 | 0.0 | 13888.31 |
| graph_sparse_graph_first_k40 | One-hop | 46 | 0.9435 | 0.8587 | 0.7891 | 0.9783 | 0.9783 | 248343.89 |
| graph_sparse_graph_first_k40 | Two-hop | 44 | 0.8841 | 0.8091 | 0.7114 | 0.9773 | 1.0 | 202501.16 |

## Metrics by question family

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| semantic_gs_rrf_rerank_k40 | core_identity | 10 | 1.0 | 0.81 | 0.6 | 0.0 | 0.0 | 18605.05 |
| semantic_gs_rrf_rerank_k40 | dai_van_interpretation | 10 | 0.83 | 0.67 | 0.59 | 1.0 | 1.0 | 123119.77 |
| semantic_gs_rrf_rerank_k40 | menh_cuc_relation | 10 | 0.97 | 0.94 | 0.925 | 1.0 | 1.0 | 141418.88 |
| semantic_gs_rrf_rerank_k40 | menh_house_interpretation | 10 | 0.89 | 0.83 | 0.77 | 0.9 | 1.0 | 160597.75 |
| semantic_gs_rrf_rerank_k40 | menh_tam_hop | 10 | 0.9 | 0.84 | 0.73 | 1.0 | 1.0 | 152479.18 |
| semantic_gs_rrf_rerank_k40 | menh_xung_chieu | 10 | 0.87 | 0.78 | 0.67 | 1.0 | 1.0 | 137222.48 |
| semantic_gs_rrf_rerank_k40 | special_state_interpretation | 10 | 0.82 | 0.75 | 0.66 | 1.0 | 1.0 | 143437.43 |
| semantic_gs_rrf_rerank_k40 | synthesis_judgement | 10 | 0.93 | 0.89 | 0.765 | 0.9 | 1.0 | 207908.29 |
| semantic_gs_rrf_rerank_k40 | than_cu_interpretation | 10 | 0.89 | 0.88 | 0.84 | 1.0 | 1.0 | 166124.0 |
| semantic_gs_rrf_rerank_k40 | topic_house_plus_relations | 10 | 0.96 | 0.91 | 0.88 | 1.0 | 1.0 | 163271.43 |
| graph_only_rrf_k40 | core_identity | 10 | 1.0 | 0.84 | 0.7 | 0.0 | 0.0 | 3836.92 |
| graph_only_rrf_k40 | dai_van_interpretation | 10 | 0.9 | 0.73 | 0.57 | 1.0 | 1.0 | 30112.82 |
| graph_only_rrf_k40 | menh_cuc_relation | 10 | 0.95 | 0.92 | 0.84 | 1.0 | 1.0 | 29168.79 |
| graph_only_rrf_k40 | menh_house_interpretation | 10 | 0.91 | 0.66 | 0.54 | 0.9 | 0.9 | 65555.85 |
| graph_only_rrf_k40 | menh_tam_hop | 10 | 0.91 | 0.74 | 0.595 | 1.0 | 0.975 | 39893.71 |
| graph_only_rrf_k40 | menh_xung_chieu | 10 | 0.74 | 0.68 | 0.52 | 1.0 | 1.0 | 29753.64 |
| graph_only_rrf_k40 | special_state_interpretation | 10 | 0.58 | 0.53 | 0.28 | 1.0 | 1.0 | 34043.34 |
| graph_only_rrf_k40 | synthesis_judgement | 10 | 0.92 | 0.75 | 0.59 | 0.9 | 0.9 | 51708.4 |
| graph_only_rrf_k40 | than_cu_interpretation | 10 | 0.97 | 0.88 | 0.85 | 1.0 | 1.0 | 40009.82 |
| graph_only_rrf_k40 | topic_house_plus_relations | 10 | 0.7 | 0.64 | 0.5 | 1.0 | 0.9 | 29613.65 |
| sparse_only_rrf_k40 | core_identity | 10 | 1.0 | 0.8 | 0.5 | 0.0 | 0.0 | 3700.86 |
| sparse_only_rrf_k40 | dai_van_interpretation | 10 | 0.7 | 0.61 | 0.49 | 0.0 | 1.0 | 113381.86 |
| sparse_only_rrf_k40 | menh_cuc_relation | 10 | 0.99 | 0.96 | 0.95 | 0.0 | 1.0 | 113373.31 |
| sparse_only_rrf_k40 | menh_house_interpretation | 10 | 0.94 | 0.72 | 0.68 | 0.0 | 1.0 | 159265.24 |
| sparse_only_rrf_k40 | menh_tam_hop | 10 | 0.94 | 0.83 | 0.76 | 0.0 | 1.0 | 178573.02 |
| sparse_only_rrf_k40 | menh_xung_chieu | 10 | 0.88 | 0.79 | 0.69 | 0.0 | 1.0 | 159987.11 |
| sparse_only_rrf_k40 | special_state_interpretation | 10 | 0.96 | 0.79 | 0.68 | 0.0 | 1.0 | 155373.69 |
| sparse_only_rrf_k40 | synthesis_judgement | 10 | 0.88 | 0.83 | 0.72 | 0.0 | 1.0 | 174646.8 |
| sparse_only_rrf_k40 | than_cu_interpretation | 10 | 0.88 | 0.79 | 0.78 | 0.0 | 1.0 | 159721.84 |
| sparse_only_rrf_k40 | topic_house_plus_relations | 10 | 0.92 | 0.88 | 0.82 | 0.0 | 1.0 | 170659.02 |
| dense_only_rrf_k40 | core_identity | 10 | 1.0 | 0.83 | 0.8 | 0.0 | 0.0 | 4038.62 |
| dense_only_rrf_k40 | dai_van_interpretation | 10 | 0.81 | 0.64 | 0.54 | 0.0 | 1.0 | 24644.34 |
| dense_only_rrf_k40 | menh_cuc_relation | 10 | 0.95 | 0.92 | 0.875 | 0.0 | 1.0 | 23706.43 |
| dense_only_rrf_k40 | menh_house_interpretation | 10 | 0.87 | 0.71 | 0.63 | 0.0 | 1.0 | 44260.6 |
| dense_only_rrf_k40 | menh_tam_hop | 10 | 0.9 | 0.77 | 0.66 | 0.0 | 1.0 | 22911.13 |
| dense_only_rrf_k40 | menh_xung_chieu | 10 | 0.88 | 0.77 | 0.67 | 0.0 | 0.9 | 24173.93 |
| dense_only_rrf_k40 | special_state_interpretation | 10 | 0.8 | 0.76 | 0.68 | 0.0 | 1.0 | 24252.38 |
| dense_only_rrf_k40 | synthesis_judgement | 10 | 0.89 | 0.88 | 0.77 | 0.0 | 1.0 | 25061.67 |
| dense_only_rrf_k40 | than_cu_interpretation | 10 | 0.95 | 0.93 | 0.89 | 0.0 | 1.0 | 22709.53 |
| dense_only_rrf_k40 | topic_house_plus_relations | 10 | 0.96 | 0.9 | 0.85 | 0.0 | 1.0 | 29383.31 |
| dense_sparse_rrf_k40 | core_identity | 10 | 1.0 | 0.81 | 0.7 | 0.0 | 0.0 | 4548.79 |
| dense_sparse_rrf_k40 | dai_van_interpretation | 10 | 0.85 | 0.71 | 0.61 | 0.0 | 1.0 | 158412.77 |
| dense_sparse_rrf_k40 | menh_cuc_relation | 10 | 0.98 | 0.95 | 0.92 | 0.0 | 1.0 | 127805.92 |
| dense_sparse_rrf_k40 | menh_house_interpretation | 10 | 0.94 | 0.82 | 0.72 | 0.0 | 1.0 | 174748.03 |
| dense_sparse_rrf_k40 | menh_tam_hop | 10 | 0.87 | 0.82 | 0.72 | 0.0 | 1.0 | 164340.24 |
| dense_sparse_rrf_k40 | menh_xung_chieu | 10 | 0.84 | 0.8 | 0.7 | 0.0 | 1.0 | 151672.46 |
| dense_sparse_rrf_k40 | special_state_interpretation | 10 | 0.84 | 0.77 | 0.68 | 0.0 | 1.0 | 141537.08 |
| dense_sparse_rrf_k40 | synthesis_judgement | 10 | 0.9 | 0.84 | 0.73 | 0.0 | 1.0 | 197027.31 |
| dense_sparse_rrf_k40 | than_cu_interpretation | 10 | 0.95 | 0.93 | 0.88 | 0.0 | 1.0 | 195354.43 |
| dense_sparse_rrf_k40 | topic_house_plus_relations | 10 | 0.94 | 0.88 | 0.84 | 0.0 | 1.0 | 179190.82 |
| graph_dense_rrf_k40 | core_identity | 10 | 1.0 | 0.87 | 0.7 | 0.0 | 0.0 | 6186.7 |
| graph_dense_rrf_k40 | dai_van_interpretation | 10 | 0.82 | 0.54 | 0.38 | 1.0 | 1.0 | 53130.78 |
| graph_dense_rrf_k40 | menh_cuc_relation | 10 | 0.98 | 0.94 | 0.89 | 1.0 | 1.0 | 100212.24 |
| graph_dense_rrf_k40 | menh_house_interpretation | 10 | 0.91 | 0.71 | 0.72 | 0.9 | 1.0 | 66266.73 |
| graph_dense_rrf_k40 | menh_tam_hop | 10 | 0.88 | 0.77 | 0.65 | 1.0 | 1.0 | 58779.69 |
| graph_dense_rrf_k40 | menh_xung_chieu | 10 | 0.88 | 0.78 | 0.68 | 1.0 | 1.0 | 43640.25 |
| graph_dense_rrf_k40 | special_state_interpretation | 10 | 0.76 | 0.77 | 0.69 | 1.0 | 1.0 | 76278.21 |
| graph_dense_rrf_k40 | synthesis_judgement | 10 | 0.95 | 0.86 | 0.78 | 0.9 | 1.0 | 60291.41 |
| graph_dense_rrf_k40 | than_cu_interpretation | 10 | 0.96 | 0.96 | 0.92 | 1.0 | 1.0 | 83043.45 |
| graph_dense_rrf_k40 | topic_house_plus_relations | 10 | 0.93 | 0.89 | 0.85 | 1.0 | 1.0 | 48947.57 |
| all_paths_planner_dense_rrf_k40 | core_identity | 10 | 1.0 | 0.85 | 0.8 | 0.0 | 0.0 | 8581.57 |
| all_paths_planner_dense_rrf_k40 | dai_van_interpretation | 10 | 0.86 | 0.71 | 0.62 | 1.0 | 1.0 | 153652.34 |
| all_paths_planner_dense_rrf_k40 | menh_cuc_relation | 10 | 1.0 | 0.92 | 0.9 | 1.0 | 1.0 | 146437.34 |
| all_paths_planner_dense_rrf_k40 | menh_house_interpretation | 10 | 0.87 | 0.75 | 0.71 | 0.9 | 1.0 | 198366.58 |
| all_paths_planner_dense_rrf_k40 | menh_tam_hop | 10 | 0.89 | 0.82 | 0.7 | 1.0 | 1.0 | 201473.04 |
| all_paths_planner_dense_rrf_k40 | menh_xung_chieu | 10 | 0.85 | 0.74 | 0.61 | 1.0 | 1.0 | 172459.7 |
| all_paths_planner_dense_rrf_k40 | special_state_interpretation | 10 | 0.94 | 0.8 | 0.71 | 1.0 | 1.0 | 177719.44 |
| all_paths_planner_dense_rrf_k40 | synthesis_judgement | 10 | 0.94 | 0.83 | 0.72 | 0.9 | 1.0 | 238555.85 |
| all_paths_planner_dense_rrf_k40 | than_cu_interpretation | 10 | 0.97 | 0.9 | 0.86 | 1.0 | 1.0 | 201702.16 |
| all_paths_planner_dense_rrf_k40 | topic_house_plus_relations | 10 | 0.95 | 0.87 | 0.82 | 1.0 | 1.0 | 185855.11 |
| semantic_gs_rrf_no_rerank_reference | core_identity | 10 | 1.0 | 0.81 | 0.8 | 0.0 | 0.0 | 27542.93 |
| semantic_gs_rrf_no_rerank_reference | dai_van_interpretation | 10 | 0.81 | 0.64 | 0.55 | 1.0 | 1.0 | 23857.41 |
| semantic_gs_rrf_no_rerank_reference | menh_cuc_relation | 10 | 1.0 | 0.92 | 0.88 | 1.0 | 1.0 | 23242.15 |
| semantic_gs_rrf_no_rerank_reference | menh_house_interpretation | 10 | 0.77 | 0.71 | 0.6 | 0.9 | 1.0 | 21903.1 |
| semantic_gs_rrf_no_rerank_reference | menh_tam_hop | 10 | 0.92 | 0.84 | 0.73 | 1.0 | 1.0 | 19184.5 |
| semantic_gs_rrf_no_rerank_reference | menh_xung_chieu | 10 | 0.82 | 0.79 | 0.71 | 1.0 | 1.0 | 19606.64 |
| semantic_gs_rrf_no_rerank_reference | special_state_interpretation | 10 | 0.78 | 0.77 | 0.68 | 1.0 | 1.0 | 19183.05 |
| semantic_gs_rrf_no_rerank_reference | synthesis_judgement | 10 | 0.92 | 0.86 | 0.77 | 0.9 | 1.0 | 17497.45 |
| semantic_gs_rrf_no_rerank_reference | than_cu_interpretation | 10 | 0.98 | 0.96 | 0.95 | 1.0 | 1.0 | 15431.81 |
| semantic_gs_rrf_no_rerank_reference | topic_house_plus_relations | 10 | 0.88 | 0.85 | 0.79 | 1.0 | 1.0 | 18816.15 |
| graph_sparse_weighted_sum_k40 | core_identity | 10 | 0.98 | 0.82 | 0.7 | 0.0 | 0.0 | 6002.8 |
| graph_sparse_weighted_sum_k40 | dai_van_interpretation | 10 | 0.84 | 0.68 | 0.58 | 1.0 | 1.0 | 128541.45 |
| graph_sparse_weighted_sum_k40 | menh_cuc_relation | 10 | 1.0 | 0.92 | 0.88 | 1.0 | 1.0 | 107756.48 |
| graph_sparse_weighted_sum_k40 | menh_house_interpretation | 10 | 0.94 | 0.74 | 0.69 | 0.9 | 1.0 | 183802.41 |
| graph_sparse_weighted_sum_k40 | menh_tam_hop | 10 | 0.93 | 0.82 | 0.71 | 1.0 | 1.0 | 168171.98 |
| graph_sparse_weighted_sum_k40 | menh_xung_chieu | 10 | 0.89 | 0.79 | 0.67 | 1.0 | 1.0 | 147720.04 |
| graph_sparse_weighted_sum_k40 | special_state_interpretation | 10 | 0.92 | 0.77 | 0.68 | 1.0 | 1.0 | 150229.58 |
| graph_sparse_weighted_sum_k40 | synthesis_judgement | 10 | 0.91 | 0.84 | 0.75 | 0.9 | 1.0 | 212030.23 |
| graph_sparse_weighted_sum_k40 | than_cu_interpretation | 10 | 0.88 | 0.9 | 0.78 | 1.0 | 1.0 | 169407.51 |
| graph_sparse_weighted_sum_k40 | topic_house_plus_relations | 10 | 0.96 | 0.92 | 0.83 | 1.0 | 1.0 | 166183.59 |
| graph_sparse_graph_first_k40 | core_identity | 10 | 1.0 | 0.83 | 0.8 | 0.0 | 0.0 | 13888.31 |
| graph_sparse_graph_first_k40 | dai_van_interpretation | 10 | 0.9 | 0.73 | 0.61 | 1.0 | 1.0 | 239773.53 |
| graph_sparse_graph_first_k40 | menh_cuc_relation | 10 | 1.0 | 0.97 | 0.96 | 1.0 | 1.0 | 129282.28 |
| graph_sparse_graph_first_k40 | menh_house_interpretation | 10 | 0.88 | 0.76 | 0.7 | 0.9 | 0.9 | 290820.13 |
| graph_sparse_graph_first_k40 | menh_tam_hop | 10 | 0.89 | 0.85 | 0.72 | 1.0 | 1.0 | 209115.79 |
| graph_sparse_graph_first_k40 | menh_xung_chieu | 10 | 0.91 | 0.81 | 0.7 | 1.0 | 1.0 | 173280.69 |
| graph_sparse_graph_first_k40 | special_state_interpretation | 10 | 0.94 | 0.82 | 0.68 | 1.0 | 1.0 | 154127.83 |
| graph_sparse_graph_first_k40 | synthesis_judgement | 10 | 0.8 | 0.77 | 0.65 | 0.9 | 1.0 | 246221.62 |
| graph_sparse_graph_first_k40 | than_cu_interpretation | 10 | 0.96 | 0.93 | 0.89 | 1.0 | 1.0 | 217594.3 |
| graph_sparse_graph_first_k40 | topic_house_plus_relations | 10 | 0.95 | 0.87 | 0.85 | 1.0 | 1.0 | 184936.11 |

## Per-question results

### semantic_gs_rrf_rerank_k40

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4183.44 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 98485.6 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 116142.19 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 72089.57 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 6 | 124382.33 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 142165.16 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 8 | 113674.15 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.2 | 0.3 | True | 1.0 | 8 | 114238.1 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 105244.97 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.5 | 0.0 | True | 1.0 | 5 | 105549.87 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 23721.51 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.5 | True | 1.0 | 3 | 147953.35 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 5 | 137552.32 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 0.9 | 1.0 | 1.0 | True | 1.0 | 4 | 71902.23 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 8 | 87752.63 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 129063.21 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 4 | 109344.23 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 4 | 103972.75 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 101201.34 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 121855.47 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 10473.42 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 0.9 | 1.0 | 1.0 | True | 1.0 | 6 | 160076.62 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 152921.04 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 108564.01 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 7 | 122486.47 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 4 | 138239.27 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.5 | 0.2 | True | 1.0 | 5 | 101835.57 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 5 | 117533.97 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 148973.57 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 5 | 186387.08 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 2890.5 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.9 | 0.8 | True | 1.0 | 6 | 149759.78 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 106399.54 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 104652.06 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 8 | 135997.81 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 3 | 137237.64 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 0.9 | 0.9 | 0.8 | True | 1.0 | 7 | 135991.27 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 5 | 117005.73 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.6 | 0.5 | 0.4 | True | 1.0 | 4 | 135805.26 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 148259.14 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 5273.3 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 104998.32 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 113160.9 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 4 | 83619.18 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 6 | 128921.68 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 127414.18 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 7 | 138229.83 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 6 | 103787.18 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 96929.09 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 170398.91 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 7884.47 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.1 | 0.0 | True | 1.0 | 7 | 148590.4 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 0.0 | 0.5 | 0.0 | True | 1.0 | 4 | 117588.38 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.75 | True | 1.0 | 6 | 162894.48 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 146904.36 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 129510.51 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 0.9 | 0.9 | 1.0 | True | 1.0 | 6 | 131484.46 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 0.2 | 0.2 | 0.2 | True | 1.0 | 7 | 127603.76 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 5 | 151666.39 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 0.8 | 1.0 | 0.7 | True | 1.0 | 4 | 225516.56 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 0.7 | 0.6 | False | 0.0 | 1 | 12351.59 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 5 | 112524.95 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 7 | 169190.16 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 115170.93 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 6 | 101144.18 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 136956.5 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 6 | 127723.91 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 7 | 105565.08 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 3 | 144489.9 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 132920.67 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 6890.37 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 155455.01 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 157938.63 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 73006.28 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 7 | 95181.23 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.9 | 0.8 | True | 1.0 | 3 | 140850.6 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 2 | 119877.53 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.9 | 0.8 | True | 1.0 | 6 | 99485.24 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 120811.72 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.8 | 0.75 | True | 1.0 | 4 | 128586.99 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 7479.62 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.7 | False | 1.0 | 4 | 161024.13 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 7 | 161208.31 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 89941.38 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 139200.08 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.9 | 0.8 | True | 1.0 | 6 | 160917.93 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 3 | 131818.43 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 0.9 | 0.7 | 0.6 | True | 1.0 | 6 | 117639.34 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 172766.46 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 5 | 168138.65 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.0 | None | None | None | 1 | 7687.05 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 0.9 | True | 1.0 | 2 | 105565.55 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 0.9 | 1.0 | 1.0 | True | 1.0 | 5 | 162376.47 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 99567.24 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 6 | 104298.17 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 5 | 107239.67 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 3 | 93011.87 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.6 | 0.4 | True | 1.0 | 4 | 88047.32 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 97205.09 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 6 | 111382.89 |  |

### graph_only_rrf_k40

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3861.7 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 5 | 73068.86 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 27065.74 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 14588.72 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 0.7 | 0.8 | 0.5 | True | 1.0 | 2 | 32730.73 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 3 | 40719.16 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 6 | 29167.26 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 6 | 30748.49 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 2 | 24456.3 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 3 | 22663.21 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 3231.16 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 6 | 34574.66 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 3 | 33674.58 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 15203.57 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 0.6 | True | 1.0 | 3 | 25521.46 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.2 | 0.0 | True | 1.0 | 5 | 26617.54 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 6 | 23706.23 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 2 | 26010.98 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 7 | 23620.58 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 5 | 34348.5 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3261.1 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 56373.29 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 3 | 34367.78 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 23694.69 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 0.2 | 0.2 | 0.0 | True | 1.0 | 4 | 27124.46 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.75 | True | 1.0 | 4 | 38884.83 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.5 | 0.2 | True | 1.0 | 7 | 24380.03 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 4 | 26939.41 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.9 | 0.8 | True | 1.0 | 6 | 29044.97 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 60572.1 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 1703.65 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 7 | 35332.95 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 25843.23 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 0.9 | 1.0 | 0.8 | True | 1.0 | 4 | 21656.81 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 0.5 | 0.5 | 0.0 | True | 1.0 | 5 | 32846.84 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 4 | 29624.64 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 26687.7 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.5 | 0.2 | True | 1.0 | 7 | 27594.51 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.4 | 0.2 | True | 0.0 | 4 | 28921.25 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 7 | 23129.59 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 2343.19 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 20413.44 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 5 | 24951.46 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 7 | 14774.39 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.5 | 0.0 | True | 1.0 | 3 | 28063.71 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 25247.57 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 2 | 30233.4 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 7 | 29335.88 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 0.2 | 0.2 | 0.0 | True | 1.0 | 7 | 24484.86 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 40874.98 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3255.98 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.2 | 0.0 | True | 1.0 | 5 | 36769.56 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 27513.01 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 21553.2 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 4 | 35022.29 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.5 | True | 1.0 | 5 | 23427.84 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 3 | 22821.92 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 27426.45 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 30078.94 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 35235.78 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 0.8 | 0.7 | False | 0.0 | 1 | 3806.64 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.2 | 0.0 | True | 1.0 | 5 | 18197.01 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 6 | 39012.57 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 29408.53 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 4 | 21645.06 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 3 | 23229.13 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 0.2 | 0.2 | 0.2 | True | 1.0 | 5 | 18936.37 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 2 | 17596.64 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 3 | 24040.85 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.7 | 0.4 | True | 1.0 | 3 | 23835.98 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3416.44 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 0.9 | 0.9 | 0.8 | True | 1.0 | 6 | 28855.07 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 0.9 | 0.9 | 0.8 | True | 1.0 | 3 | 38794.95 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.7 | 0.0 | True | 1.0 | 2 | 14975.35 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 3 | 23441.88 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 3 | 30352.7 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 6 | 22675.99 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 3 | 27859.3 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 4 | 20270.95 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.4 | 0.2 | True | 1.0 | 3 | 24119.14 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3591.49 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.7 | False | 0.0 | 1 | 4009.5 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 5 | 40825.75 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.9 | 1.0 | True | 1.0 | 2 | 16248.54 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 0.8 | 1.0 | 0.7 | True | 1.0 | 3 | 30479.31 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.6 | True | 1.0 | 6 | 31164.31 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 2 | 22622.55 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 3 | 27280.37 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 6 | 27401.63 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.5 | 0.2 | False | 0.0 | 1 | 3718.85 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.2 | None | None | None | 1 | 3632.96 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.4 | 0.2 | True | 1.0 | 4 | 19839.31 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 36146.72 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 0.8 | 1.0 | 1.0 | True | 1.0 | 3 | 28875.78 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 3 | 28564.57 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.6 | 0.4 | True | 0.75 | 1 | 23787.95 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 5 | 23405.36 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.5 | 0.2 | True | 1.0 | 4 | 24822.48 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 7 | 23495.97 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 4 | 29498.4 |  |

### sparse_only_rrf_k40

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3769.95 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 1.0 | False | 1.0 | 5 | 85970.04 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 4 | 103425.28 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 4 | 70877.71 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 6 | 105450.05 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 0.8 | False | 1.0 | 6 | 133240.63 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 7 | 108073.63 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.4 | 0.2 | False | 1.0 | 6 | 107978.19 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 0.8 | False | 1.0 | 3 | 110804.28 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.5 | 0.5 | 0.2 | False | 1.0 | 5 | 107230.13 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3509.83 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.4 | 0.2 | False | 1.0 | 9 | 132369.09 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 0.8 | False | 1.0 | 4 | 130265.15 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 3 | 72331.87 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.8 | 1.0 | 0.6 | False | 1.0 | 5 | 81793.58 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.7 | False | 1.0 | 5 | 124315.14 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 1.0 | False | 1.0 | 6 | 94386.68 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 6 | 94272.98 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 2 | 90491.07 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 4 | 108637.63 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3484.56 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 1.0 | False | 1.0 | 5 | 136588.53 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 9 | 114739.56 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 3 | 81808.36 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 7 | 107933.3 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | False | 1.0 | 5 | 126972.97 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.6 | 0.2 | False | 1.0 | 9 | 94442.32 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.2 | 0.3 | 0.2 | False | 1.0 | 5 | 90321.59 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 1.0 | False | 1.0 | 6 | 192048.96 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 0.9 | 1.0 | 0.8 | False | 1.0 | 6 | 185227.09 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 0.6 | None | None | None | 1 | 1540.36 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.4 | 0.2 | False | 1.0 | 7 | 155866.99 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 7 | 127137.99 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.9 | 1.0 | False | 1.0 | 3 | 83778.0 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 8 | 169347.01 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.7 | False | 1.0 | 5 | 215663.15 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 5 | 186968.2 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 0.6 | 0.5 | 0.2 | False | 1.0 | 6 | 115692.3 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.2 | 0.4 | 0.2 | False | 1.0 | 4 | 144515.76 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.7 | 0.5 | False | 1.0 | 6 | 116472.99 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 2579.54 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 0.8 | False | 1.0 | 3 | 97734.33 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.8 | False | 1.0 | 6 | 98175.71 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 0.9 | 0.8 | 0.7 | False | 1.0 | 4 | 73979.23 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.0 | 0.0 | False | 1.0 | 5 | 124119.37 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 5 | 123411.2 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.8 | 0.7 | False | 1.0 | 7 | 127010.23 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 0.9 | 1.0 | False | 1.0 | 9 | 97045.57 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 4 | 76707.96 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 4 | 135699.28 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 2913.81 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.2 | 0.2 | False | 1.0 | 7 | 162045.63 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 0.0 | 0.0 | 0.0 | False | 1.0 | 9 | 158367.83 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 0.8 | False | 1.0 | 4 | 102186.4 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.8 | False | 1.0 | 4 | 138295.19 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 6 | 105630.56 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.9 | 1.0 | False | 1.0 | 4 | 118447.86 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 0.2 | 0.2 | 0.2 | False | 1.0 | 6 | 110557.98 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 0.8 | False | 1.0 | 5 | 132497.94 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 3 | 149450.93 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 0.6 | 0.5 | False | 0.0 | 1 | 3439.75 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.7 | False | 1.0 | 7 | 95201.15 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 1.0 | False | 1.0 | 5 | 123942.03 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 4 | 84793.23 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.6 | False | 1.0 | 6 | 81598.98 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 3 | 105831.93 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.8 | 0.7 | False | 1.0 | 7 | 102681.06 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 3 | 79165.72 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 0.8 | False | 1.0 | 5 | 88709.18 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 4 | 94019.84 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3206.32 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 1.0 | False | 1.0 | 4 | 132711.89 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.6 | False | 1.0 | 3 | 160829.66 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 3 | 122526.24 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.6 | False | 1.0 | 9 | 112920.91 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | False | 1.0 | 4 | 122833.84 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.6 | 0.5 | False | 1.0 | 2 | 79592.14 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 5 | 83716.08 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 5 | 114578.08 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.6 | 0.5 | False | 1.0 | 5 | 120593.06 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3616.41 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.7 | False | 1.0 | 4 | 151679.11 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 1.0 | False | 1.0 | 6 | 118403.98 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 4 | 81244.22 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 6 | 111031.19 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 6 | 121339.44 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 4 | 89065.99 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.4 | False | 1.0 | 5 | 83669.29 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 6 | 133858.36 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 5 | 161715.33 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.0 | None | None | None | 1 | 3539.31 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 3 | 89157.44 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 1.0 | False | 1.0 | 5 | 133867.6 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.9 | 1.0 | False | 1.0 | 3 | 75886.34 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.6 | False | 1.0 | 5 | 93029.29 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.5 | 0.4 | False | 1.0 | 5 | 90920.31 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.5 | False | 1.0 | 3 | 88875.28 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.4 | False | 1.0 | 3 | 79057.46 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.6 | False | 1.0 | 4 | 91944.26 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.6 | 0.5 | False | 1.0 | 4 | 105068.94 |  |

### dense_only_rrf_k40

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3541.14 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.8 | False | 1.0 | 6 | 60485.13 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 4 | 20532.35 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 6 | 20361.58 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 4 | 21000.97 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.7 | False | 1.0 | 4 | 23366.68 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.9 | 1.0 | False | 1.0 | 4 | 25412.34 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.2 | 0.2 | False | 1.0 | 4 | 24198.25 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 1.0 | False | 1.0 | 7 | 35873.61 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.2 | 0.5 | 0.0 | False | 1.0 | 4 | 28610.96 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 3655.87 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 0.8 | False | 1.0 | 8 | 24430.62 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 4 | 24490.86 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 6 | 26443.13 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 7 | 26912.63 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | False | 1.0 | 5 | 22354.34 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.9 | 0.8 | False | 1.0 | 5 | 22660.32 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.9 | 0.8 | False | 1.0 | 5 | 25009.33 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 4 | 21450.72 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 3 | 20723.66 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3630.23 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.9 | 1.0 | False | 1.0 | 5 | 21190.46 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 4 | 19399.76 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 3 | 18171.9 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 0.6 | 0.4 | 0.2 | False | 1.0 | 3 | 14413.88 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 4 | 15698.98 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.6 | 0.4 | False | 1.0 | 8 | 14663.8 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.5 | False | 1.0 | 6 | 18667.47 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 5 | 17520.23 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 8 | 17606.63 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 1543.52 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.4 | 0.2 | False | 1.0 | 4 | 15956.05 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 7 | 16438.2 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.9 | 1.0 | False | 1.0 | 3 | 17219.34 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.8 | False | 1.0 | 6 | 14573.96 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | False | 1.0 | 5 | 15188.85 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 6 | 15483.7 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 0.2 | 0.4 | 0.2 | False | 1.0 | 7 | 14931.34 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.7 | 0.5 | False | 1.0 | 2 | 16258.72 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 4 | 15179.88 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 2200.69 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 0.9 | 0.8 | 0.7 | False | 1.0 | 4 | 16765.93 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 4 | 15425.47 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.75 | False | 1.0 | 5 | 16985.63 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 0.0 | 0.0 | 0.0 | False | 1.0 | 6 | 15010.17 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 4 | 16809.13 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.8 | 0.8 | False | 0.0 | 6 | 16636.78 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 0.9 | 1.0 | False | 1.0 | 4 | 15853.01 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 1.0 | False | 1.0 | 4 | 19027.72 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 6 | 16511.61 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 2916.46 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.2 | 0.0 | False | 1.0 | 5 | 15695.22 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 3 | 15551.62 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 0.5 | 0.5 | 0.0 | False | 1.0 | 5 | 16917.28 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 7 | 17019.6 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.6 | False | 1.0 | 3 | 15722.44 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 4 | 16837.55 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.5 | False | 1.0 | 3 | 15649.42 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.6 | False | 1.0 | 4 | 15962.23 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 3 | 14987.46 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 0.9 | 0.8 | False | 0.0 | 1 | 3714.81 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 7 | 15654.45 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 0.9 | 1.0 | 1.0 | False | 1.0 | 4 | 16420.88 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 6 | 16333.63 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 0.8 | False | 1.0 | 7 | 16028.49 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.6 | 0.5 | False | 1.0 | 3 | 16160.38 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.5 | 0.2 | False | 1.0 | 4 | 16977.07 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.6 | False | 1.0 | 4 | 18607.23 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 3 | 15701.46 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 3 | 16758.05 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3725.37 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 0.8 | False | 1.0 | 6 | 16067.42 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 1.0 | False | 1.0 | 4 | 16525.53 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 6 | 17939.85 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.6 | False | 1.0 | 5 | 16400.44 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 5 | 15912.56 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 6 | 16765.58 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 3 | 16518.74 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 3 | 15476.66 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.6 | 0.5 | False | 1.0 | 3 | 18099.63 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3856.92 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 4 | 16660.49 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.8 | False | 1.0 | 3 | 16836.32 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 6 | 16822.42 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 4 | 16932.89 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 0.8 | False | 1.0 | 6 | 18325.66 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 5 | 17788.67 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 0.9 | 0.7 | 0.6 | False | 1.0 | 6 | 16557.81 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 5 | 16877.85 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 0.9 | 1.0 | 0.8 | False | 1.0 | 3 | 18103.27 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.0 | None | None | None | 1 | 4187.28 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 0.6 | 0.5 | 0.4 | False | 1.0 | 4 | 14762.93 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.7 | False | 1.0 | 8 | 16934.69 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 5 | 17644.75 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.9 | 1.0 | False | 1.0 | 6 | 16743.16 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.6 | 0.4 | False | 1.0 | 2 | 16740.58 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 3 | 17708.09 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.4 | False | 1.0 | 4 | 15144.11 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.7 | False | 1.0 | 3 | 15043.9 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.8 | 0.7 | False | 1.0 | 8 | 16965.82 |  |

### dense_sparse_rrf_k40

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3836.35 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 6 | 89221.59 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 4 | 101544.17 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 3 | 71692.32 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 7 | 104333.88 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 4 | 127955.22 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.9 | 1.0 | False | 1.0 | 9 | 102680.09 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.4 | 0.2 | False | 1.0 | 6 | 121695.61 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 1.0 | False | 1.0 | 4 | 112433.0 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.6 | 0.4 | False | 1.0 | 5 | 109452.74 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3988.91 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.5 | False | 1.0 | 4 | 139961.08 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 5 | 130420.61 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 4 | 122118.96 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 5 | 115824.6 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 3 | 170589.26 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.9 | 0.8 | False | 1.0 | 4 | 155202.71 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 0.9 | 0.9 | 0.8 | False | 1.0 | 6 | 169053.96 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 2 | 136110.44 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 5 | 137961.66 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4145.07 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.7 | False | 1.0 | 4 | 180937.33 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 1.0 | False | 1.0 | 4 | 224497.06 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.9 | 1.0 | False | 1.0 | 7 | 116918.35 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 5 | 127869.97 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 5 | 156702.55 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.2 | 0.2 | 0.1 | False | 1.0 | 8 | 109891.94 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 5 | 110358.49 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 4 | 185159.17 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 6 | 195460.7 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 0.5 | None | None | None | 1 | 1949.41 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.6 | 0.4 | False | 1.0 | 4 | 167183.32 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 6 | 117940.81 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.6 | False | 1.0 | 6 | 83311.96 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 5 | 108479.67 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.8 | False | 1.0 | 9 | 127138.34 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 0.9 | 0.9 | 0.8 | False | 1.0 | 4 | 147357.7 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.4 | False | 1.0 | 6 | 118301.88 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.7 | 0.4 | False | 1.0 | 4 | 142151.01 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 0.9 | 0.9 | 0.8 | False | 1.0 | 4 | 145525.65 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 3048.28 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 3 | 108182.78 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 6 | 111268.72 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.6 | False | 1.0 | 5 | 132458.89 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 0.0 | 0.0 | 0.0 | False | 1.0 | 6 | 152719.27 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 1.0 | False | 1.0 | 4 | 122435.35 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 6 | 135046.21 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 4 | 113985.52 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 5 | 104718.78 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 4 | 148065.56 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3089.83 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.6 | 0.5 | False | 1.0 | 7 | 142753.25 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 0.8 | 1.0 | 0.6 | False | 1.0 | 2 | 129240.84 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 7 | 94348.94 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 4 | 115302.54 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 6 | 106651.06 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 6 | 110593.12 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.9 | 0.8 | False | 1.0 | 9 | 107529.39 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 7 | 109206.27 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 0.8 | 1.0 | 0.7 | False | 1.0 | 2 | 148414.93 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 0.8 | 0.7 | False | 0.0 | 1 | 4405.82 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 5 | 96037.06 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 0.8 | False | 1.0 | 5 | 149034.95 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 2 | 90497.16 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.7 | False | 1.0 | 6 | 75444.56 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | False | 1.0 | 5 | 108671.88 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.8 | 0.6 | False | 1.0 | 8 | 104260.6 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 3 | 86595.24 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.8 | False | 1.0 | 5 | 101515.28 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 5 | 118425.32 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3837.08 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 0.8 | False | 1.0 | 4 | 105929.66 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 0.8 | False | 1.0 | 4 | 126683.83 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 3 | 73164.81 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.6 | False | 1.0 | 4 | 83550.16 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.7 | False | 1.0 | 5 | 128176.55 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 3 | 92187.48 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.5 | 0.4 | False | 1.0 | 6 | 91422.33 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 3 | 100056.31 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.6 | 0.5 | False | 1.0 | 5 | 97717.35 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4566.37 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.7 | False | 1.0 | 6 | 136136.51 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 1.0 | False | 1.0 | 5 | 107251.16 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 4 | 72992.09 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 5 | 99535.96 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 6 | 117402.16 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 0.9 | 0.8 | 0.7 | False | 1.0 | 6 | 106760.39 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.4 | 0.3 | False | 1.0 | 5 | 145406.87 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 5 | 171896.18 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.5 | 0.2 | False | 1.0 | 5 | 198309.09 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.0 | None | None | None | 1 | 4527.3 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 9 | 117026.62 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 0.9 | 1.0 | 1.0 | False | 1.0 | 5 | 159735.66 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 3 | 97502.32 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.6 | False | 1.0 | 5 | 109807.93 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.6 | 0.4 | False | 1.0 | 4 | 116481.98 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 3 | 105631.94 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 5 | 92114.92 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 4 | 101673.17 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 0.9 | 0.8 | 0.7 | False | 1.0 | 3 | 95520.74 |  |

### graph_dense_rrf_k40

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3985.79 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 32672.6 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 35826.99 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 26545.92 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 4 | 37996.88 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.5 | 0.5 | True | 1.0 | 4 | 46451.05 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 9 | 38887.56 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.4 | 0.2 | True | 1.0 | 6 | 39029.87 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 33974.18 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.9 | 0.6 | True | 1.0 | 5 | 32651.28 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 4089.7 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.6 | 0.5 | True | 1.0 | 4 | 39940.44 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 39403.19 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 25273.29 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.8 | 1.0 | 0.8 | True | 1.0 | 6 | 34127.2 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 33597.39 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 5 | 31292.26 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 4 | 35136.8 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 31496.46 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 48261.45 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4240.32 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 0.9 | 0.8 | 1.0 | True | 1.0 | 5 | 79992.86 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 46604.16 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 34715.81 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 0.5 | 0.4 | 0.2 | True | 1.0 | 3 | 61051.25 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 4 | 64800.53 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 5 | 38815.16 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.2 | 0.4 | 0.3 | True | 1.0 | 4 | 59265.22 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 51951.76 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 7 | 66606.55 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 1905.91 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.6 | 0.4 | 0.2 | True | 1.0 | 3 | 42098.13 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 32781.96 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 34215.84 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 6 | 41514.9 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 5 | 36610.2 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 37737.63 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.2 | 0.2 | True | 1.0 | 4 | 37394.65 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 3 | 37158.67 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 3 | 39691.66 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 3183.9 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 40387.26 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 37809.26 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 4 | 65539.39 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 6 | 88736.63 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 6 | 43757.01 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 44791.14 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 3 | 45633.13 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 38329.84 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 52572.9 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4034.09 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.2 | 0.2 | True | 1.0 | 4 | 49490.34 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 0.8 | 1.0 | 1.0 | True | 1.0 | 3 | 44975.87 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 7 | 36106.58 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 49095.42 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 36818.69 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 35833.88 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.4 | 0.2 | True | 1.0 | 5 | 39467.88 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 45275.79 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 50244.54 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 0.8 | 0.7 | False | 0.0 | 1 | 4199.95 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 1.0 | True | 1.0 | 7 | 49475.83 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 76650.84 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 85940.54 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 39117.27 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 4 | 48293.11 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.5 | 0.2 | True | 1.0 | 5 | 33152.41 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.5 | 0.2 | True | 1.0 | 5 | 35931.23 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 3 | 32688.92 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 3 | 33021.41 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3689.12 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 34081.54 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 4 | 45762.87 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 28050.11 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 0.6 | 0.7 | 0.4 | True | 1.0 | 4 | 32431.49 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 8 | 37767.59 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 9 | 30495.18 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 3 | 36365.02 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 28623.3 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.4 | 0.2 | True | 1.0 | 5 | 34991.43 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4912.99 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.9 | 0.8 | False | 1.0 | 5 | 17929.67 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 88273.77 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 2 | 111889.09 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 0.8 | 1.0 | 1.0 | True | 1.0 | 3 | 52041.18 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 51420.88 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.8 | True | 1.0 | 5 | 37784.91 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.2 | 0.0 | True | 1.0 | 8 | 44882.36 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 41791.51 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 3 | 20378.05 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.5 | None | None | None | 1 | 7228.82 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.6 | 0.5 | True | 1.0 | 5 | 38036.99 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 5 | 51589.46 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 46406.95 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 5 | 47559.02 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.4 | 0.2 | True | 1.0 | 5 | 39559.45 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 3 | 42233.61 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 5 | 40463.49 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 3 | 39355.07 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 6 | 47785.93 |  |

### all_paths_planner_dense_rrf_k40

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 6503.83 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 6 | 125926.04 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 149508.06 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 122419.64 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 6 | 151957.99 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 184299.11 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 7 | 162643.39 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 7 | 160724.86 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 6 | 145950.25 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.5 | 0.2 | True | 1.0 | 6 | 149075.69 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 9218.34 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 0.5 | 0.5 | 0.0 | True | 1.0 | 4 | 174118.6 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 5 | 169906.59 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 96410.92 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.8 | 1.0 | 0.5 | True | 1.0 | 6 | 117241.12 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 3 | 171271.2 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.5 | 0.3 | True | 1.0 | 7 | 136316.92 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 4 | 135936.42 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 127858.53 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 152958.81 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4777.42 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 0.9 | 0.8 | 1.0 | True | 1.0 | 4 | 198197.24 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 5 | 161868.07 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 1.0 | True | 1.0 | 5 | 113801.92 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 6 | 155521.24 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 6 | 208838.72 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.4 | True | 1.0 | 5 | 143800.95 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 7 | 131747.41 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 191582.19 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 5 | 259877.15 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 2789.63 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.4 | 0.3 | 0.2 | True | 1.0 | 5 | 191100.34 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 129563.9 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 6 | 110298.13 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 176296.67 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 5 | 192470.54 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 173795.0 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 6 | 137257.36 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.7 | 0.4 | True | 1.0 | 4 | 154438.73 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 5 | 146141.99 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 3853.68 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 128889.21 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 136771.55 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 5 | 111397.24 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.0 | 0.0 | True | 1.0 | 5 | 178883.53 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.9 | 0.8 | True | 1.0 | 9 | 180043.75 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 6 | 170827.66 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.9 | 1.0 | True | 1.0 | 4 | 145008.14 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 132243.25 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 212496.49 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 7803.3 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 9 | 198505.13 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 179083.43 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 6 | 140659.58 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 159995.22 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 0.9 | 1.0 | 0.8 | True | 1.0 | 7 | 143509.77 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 140758.69 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 7 | 134448.06 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 5 | 144511.15 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 0.8 | 1.0 | 0.8 | True | 1.0 | 4 | 187888.49 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 0.9 | 0.8 | False | 0.0 | 1 | 6121.52 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 1.0 | True | 1.0 | 7 | 126978.85 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 6 | 211490.25 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 151164.59 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 6 | 116845.73 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 6 | 139650.72 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 5 | 131409.13 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 130544.69 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 0.9 | 0.8 | 0.8 | True | 1.0 | 3 | 159411.02 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 5 | 148844.5 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4598.79 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 160566.39 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 189738.95 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 97414.51 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 123637.89 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.9 | 0.8 | True | 1.0 | 5 | 174669.41 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 124798.07 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 5 | 131837.07 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 141171.36 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.6 | 0.5 | True | 1.0 | 6 | 137662.56 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4820.12 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 0.9 | 0.7 | 0.6 | False | 1.0 | 5 | 179806.1 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 7 | 161343.96 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 99967.56 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 155083.67 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 0.9 | True | 1.0 | 6 | 157133.27 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 6 | 128492.47 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 5 | 124583.12 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 7 | 178855.35 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 5 | 179610.8 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.2 | None | None | None | 1 | 5654.55 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 3 | 121725.8 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 5 | 178360.62 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 117670.0 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 131666.64 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.6 | 0.4 | True | 1.0 | 9 | 124027.22 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 5 | 122953.98 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 8 | 114302.7 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.4 | 0.2 | True | 1.0 | 6 | 135872.42 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 4 | 143843.72 |  |

### semantic_gs_rrf_no_rerank_reference

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 5348.07 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 4 | 15691.15 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 14771.79 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 10172.8 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 7 | 22518.86 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 7 | 16945.57 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 0.9 | 0.9 | 1.0 | True | 1.0 | 6 | 12890.12 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.2 | 0.2 | True | 1.0 | 7 | 13790.95 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 10347.98 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.7 | 0.4 | True | 1.0 | 5 | 11167.16 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 4061.04 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 5 | 23808.65 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 5 | 11303.3 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 13584.37 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 11030.16 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 11543.69 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 11400.98 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 7 | 15161.54 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 10558.36 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 16847.97 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4314.24 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 0.9 | 1.0 | 1.0 | True | 1.0 | 6 | 18822.63 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 13796.93 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 13562.83 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 5 | 11739.07 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 6 | 12223.58 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 4 | 12466.61 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.2 | 0.3 | 0.2 | True | 1.0 | 7 | 11041.64 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 0.9 | 1.0 | 1.0 | True | 1.0 | 4 | 14065.86 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 7 | 17376.33 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 0.5 | None | None | None | 1 | 2135.28 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.3 | 0.2 | True | 1.0 | 6 | 19393.62 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 9118.06 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 9765.42 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 15105.96 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.9 | 0.8 | True | 1.0 | 5 | 17561.42 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 16606.04 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 6 | 11500.2 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.2 | 0.4 | 0.2 | True | 1.0 | 4 | 21492.23 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 5 | 11060.41 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 5087.29 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 15505.24 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 12224.11 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 3 | 14329.09 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 4 | 14143.81 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 15717.72 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.9 | 0.9 | 0.8 | True | 1.0 | 5 | 16250.27 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 12901.15 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 12991.95 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 14156.16 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4204.08 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.2 | 0.0 | True | 1.0 | 6 | 19574.09 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 11913.73 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 5 | 14792.7 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 6 | 13258.0 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 4 | 8949.49 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 9862.85 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.9 | True | 1.0 | 6 | 9394.68 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 6 | 15545.38 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 3 | 17596.54 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 0.8 | 0.8 | False | 0.0 | 1 | 3854.08 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 3 | 11365.49 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 15971.83 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 10735.31 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 9245.73 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 3 | 9706.57 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 0.2 | 0.2 | 0.2 | True | 1.0 | 9 | 21402.54 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 30972.22 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 4 | 12948.35 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 3 | 10668.49 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 5965.78 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 5 | 18193.89 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 14530.71 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 1.0 | True | 1.0 | 2 | 30155.33 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 5 | 10510.62 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 6 | 14084.26 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 4 | 17411.66 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 6 | 12723.53 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 13522.28 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 5 | 14494.57 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 19474.35 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 6 | 10708.41 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 11222.13 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 10009.52 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 14512.39 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 5 | 11369.37 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 3 | 11278.42 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 7 | 9466.51 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 14518.13 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 7 | 9528.71 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.2 | None | None | None | 1 | 34144.49 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 3 | 10490.2 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 0.9 | 0.9 | 0.8 | True | 1.0 | 4 | 11799.49 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 3 | 11437.61 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 10185.25 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.5 | True | 1.0 | 4 | 20512.47 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 2 | 15070.51 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 3 | 9773.47 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 4 | 10996.86 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 13914.12 |  |

### graph_sparse_weighted_sum_k40

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 6290.58 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 111621.32 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 133556.72 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 87636.61 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 136610.65 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 3 | 169198.94 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 6 | 137796.97 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 7 | 131708.51 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 129232.27 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 7 | 126986.3 |  |
| TVQA-011 | completed | Direct | core_identity | True | 0.8 | 0.8 | None | None | None | 1 | 4234.35 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.6 | 0.5 | True | 1.0 | 3 | 162330.36 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 158895.96 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 86607.7 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 6 | 107369.83 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 5 | 149707.68 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 4 | 116653.46 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 4 | 117876.48 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 117406.91 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 139113.23 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4440.23 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.9 | 1.0 | True | 1.0 | 6 | 193832.06 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 146239.93 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 102853.83 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.6 | 0.2 | True | 1.0 | 6 | 131416.34 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 5 | 159234.04 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 5 | 124054.42 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 0.2 | 0.2 | True | 1.0 | 6 | 109886.64 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 170630.0 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 229011.68 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 2452.36 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.4 | 0.2 | True | 1.0 | 5 | 171543.94 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 120971.04 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 101872.37 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 8 | 146900.5 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 6 | 161877.65 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.8 | True | 1.0 | 7 | 150620.47 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 1.0 | 0.5 | True | 1.0 | 4 | 118673.15 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.6 | 0.7 | 0.2 | True | 1.0 | 5 | 139102.27 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 4 | 132894.93 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 5045.3 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 3 | 110692.19 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 7 | 131834.65 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 4 | 91855.86 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.0 | 0.0 | True | 1.0 | 4 | 152953.38 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.8 | True | 1.0 | 5 | 155817.85 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 7 | 144175.06 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 124670.59 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 120043.87 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 191275.12 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3731.16 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.2 | 0.0 | True | 1.0 | 7 | 158461.77 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 0.2 | 0.5 | 0.0 | True | 1.0 | 6 | 136354.8 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 5 | 100675.96 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 5 | 134319.19 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 115435.98 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 117905.45 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 0.2 | 0.2 | 0.2 | True | 1.0 | 6 | 111125.32 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 5 | 123918.69 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 166449.89 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 0.8 | 0.7 | False | 0.0 | 1 | 5651.07 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 7 | 108957.23 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 6 | 167548.94 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 110560.03 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 6 | 91454.2 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 5 | 116949.62 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 6 | 110244.83 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 99246.15 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 3 | 124643.88 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 0.9 | 1.0 | 1.0 | True | 1.0 | 4 | 123953.64 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4606.52 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 7 | 140572.75 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 4 | 170928.16 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 87796.09 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 1.0 | True | 1.0 | 9 | 112852.8 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.9 | 0.8 | True | 1.0 | 6 | 166916.8 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 4 | 115997.32 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 5 | 118995.81 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 130782.48 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 6 | 126711.82 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4221.99 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.8 | False | 1.0 | 4 | 156175.68 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 7 | 154574.95 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 4 | 90720.1 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 135423.82 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 6 | 155971.96 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 5 | 113743.28 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 6 | 105076.72 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 160749.09 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.5 | 0.2 | False | 1.0 | 6 | 164959.43 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.0 | None | None | None | 1 | 4413.52 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 2 | 105769.21 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 166069.0 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 104329.91 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 125069.68 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 5 | 110384.56 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 6 | 109314.39 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 4 | 102630.38 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 9 | 117440.08 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 6 | 138040.06 |  |

### graph_sparse_graph_first_k40

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3902.64 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 110017.77 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 129924.13 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 86416.96 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 7 | 140461.83 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 3 | 169310.32 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 6 | 135960.76 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 6 | 325766.76 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 134055.17 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.6 | 0.2 | True | 1.0 | 4 | 175276.51 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4401.52 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.5 | 0.2 | True | 1.0 | 5 | 197616.59 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 250671.37 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 120473.72 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.8 | 1.0 | 0.6 | True | 1.0 | 5 | 141056.26 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 6 | 202736.5 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 3 | 162370.1 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 4 | 127155.46 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 9 | 131707.55 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 151166.03 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4709.94 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 7 | 241361.47 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 177166.76 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 136489.29 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 6 | 153296.31 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.8 | True | 1.0 | 5 | 179485.01 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.4 | True | 1.0 | 5 | 165510.38 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 6 | 121533.15 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 201167.54 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 9 | 286374.15 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 0.5 | None | None | None | 1 | 3215.9 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.4 | 0.3 | 0.2 | True | 1.0 | 7 | 331286.3 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 121158.1 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 104903.0 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 7 | 154808.17 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 6 | 214335.21 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 6 | 176822.11 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 3 | 122709.78 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.6 | 0.5 | 0.4 | True | 1.0 | 6 | 165097.7 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 132857.83 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 6920.71 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 113648.68 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 6 | 126861.39 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 5 | 94179.57 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.5 | 0.0 | True | 1.0 | 4 | 123584.46 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.9 | 0.8 | True | 1.0 | 5 | 124623.93 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.9 | 0.9 | 0.8 | True | 1.0 | 6 | 168952.28 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 4 | 134670.7 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 104050.84 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 197146.3 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4705.16 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.5 | 0.5 | True | 0.0 | 6 | 169279.18 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 139063.71 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 105206.15 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 4 | 130053.2 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 106838.3 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 91160.03 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 6 | 96797.95 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 5 | 93568.52 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 0.9 | 1.0 | 0.8 | True | 1.0 | 3 | 145822.72 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 0.8 | 0.8 | False | 0.0 | 1 | 4298.65 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 99698.81 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 7 | 133119.1 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 86803.38 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 6 | 70686.2 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 91200.31 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 6 | 84570.42 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 79756.08 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 4 | 97110.57 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 0.9 | 1.0 | 0.8 | True | 1.0 | 4 | 98940.28 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 12968.23 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 5 | 108356.82 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 159606.11 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 68288.35 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 94783.17 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 3 | 127650.99 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 4 | 90197.61 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 7 | 121237.23 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 147614.49 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.6 | 0.5 | True | 1.0 | 5 | 145306.93 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 14641.11 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.6 | 0.5 | False | 1.0 | 9 | 151700.89 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 6 | 129404.4 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 79512.13 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 116795.63 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 0.9 | 1.0 | 0.8 | True | 1.0 | 7 | 119428.79 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 126763.61 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 5 | 85999.18 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 138806.21 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.7 | 0.5 | False | 1.0 | 5 | 133398.55 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.2 | None | None | None | 1 | 11552.23 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 3 | 90538.6 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.9 | 0.8 | True | 1.0 | 5 | 134464.37 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 82574.78 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 106873.31 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.4 | 0.2 | True | 1.0 | 4 | 87495.99 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 3 | 84810.07 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 7 | 79915.01 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 5 | 93581.74 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.9 | 1.0 | True | 1.0 | 7 | 110840.55 |  |
