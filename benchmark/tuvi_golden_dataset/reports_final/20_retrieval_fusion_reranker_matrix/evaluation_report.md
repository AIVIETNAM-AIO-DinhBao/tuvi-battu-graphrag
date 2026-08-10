# W6 Evaluation report: w8_abl_01_retrieval_fusion_reranker_v2

- Dataset: `benchmark/tuvi_golden_dataset/release/tuviqa_v1_release.jsonl`
- Dataset items: 100
- Configs: 10
- Judge backend: `gemini`
- Started: 2026-08-06T09:13:49.836708Z
- Completed: 2026-08-10T03:18:48.340961Z
- Notes: W8 retrieval/fusion/reranker matrix v2. All variants hold semantic BGE-M3 chunking, structured prompt v3, Gemini Flash Lite, balanced context assembly, query rewrite off, document grading on, and cache disabled constant. Dense remains planner-gated at runtime. This matrix removes the duplicate graph+sparse cell and isolates graph_first to fusion_method only.
- Run status: `completed`

## Run identity and provenance

- Identity SHA-256: `5b8e24f33f8384fe620df5829244a21ec228025df4a3256e9cea67bde7c99afc`
- Dataset SHA-256: `90376a87cec29cc22e93dc71b41e054ed2f0183bc515a52aa461fecd43cc008c`
- Manifest SHA-256: `b2e1412df515814ab0f31e4ceb378ad46b624ef2799850e061b9349cd1f28ea0`
- Evaluator SHA-256: `487e4762a669fec1d4c3059f75d3665b35ad1327ea05ae5de6421dc41487ff8f`
- Git SHA: `cc93bb66e8b8cbe2c9843916ffe6ae504bd86c9e`
- Git dirty: `True`
- Judge model: `gemini-3.1-flash-lite-preview`
- Checkpoint: `benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/checkpoints/checkpoint_summary.json`

## Execution completeness

- Expected pairs: 1000
- Completed pairs: 1000
- Failed pairs: 0
- Executed pairs: 249
- Resumed pairs: 751

> **Metric policy:** W6-EVAL-02 runs the RAG pipeline directly with the selected `ExperimentConfig`. `Context recall` is the Gemini-judged corpus-grounding score for non-Direct items; Direct/chart-only items are excluded from corpus retrieval/citation metrics and reported through `chart_context_grounding`.

## Overall metrics

| Config | Status | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms | Retrieval p95 ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline_graph_sparse_rrf | completed | 100 | 0.888 | 0.789 | 0.7044 | 0.967 | 0.9863 | 138041.28 | 133807.67 |
| graph_only_rrf | completed | 100 | 0.823 | 0.686 | 0.5297 | 0.967 | 0.978 | 50835.98 | 40969.78 |
| sparse_only_rrf | completed | 100 | 0.9 | 0.802 | 0.6956 | 0.0 | 0.9863 | 163360.43 | 155286.27 |
| dense_only_rrf | completed | 100 | 0.904 | 0.812 | 0.7363 | 0.0 | 0.989 | 28176.52 | 18159.75 |
| dense_sparse_rrf | completed | 100 | 0.902 | 0.818 | 0.7418 | 0.0 | 0.989 | 226613.43 | 221270.99 |
| graph_dense_rrf | completed | 100 | 0.912 | 0.837 | 0.7593 | 0.967 | 0.989 | 72032.09 | 67813.93 |
| all_paths_planner_dense_rrf | completed | 100 | 0.88 | 0.801 | 0.7253 | 0.967 | 0.989 | 254152.13 | 249658.28 |
| baseline_no_reranker | completed | 100 | 0.915 | 0.828 | 0.744 | 0.967 | 0.989 | 12819.41 | 6374.74 |
| baseline_weighted_sum | completed | 100 | 0.881 | 0.794 | 0.6945 | 0.967 | 0.989 | 181602.9 | 176712.84 |
| baseline_graph_first | completed | 100 | 0.876 | 0.798 | 0.7253 | 0.967 | 0.9863 | 272370.05 | 256114.68 |

## Failure and fallback summary

| Config | Failed | Generation backend fallback | Judge failure | No context | Retrieval backend fallback | Citation fallback |
|---|---:|---:|---:|---:|---:|---:|
| baseline_graph_sparse_rrf | 0 | 0 | 0 | 0 | 0 | 0 |
| graph_only_rrf | 0 | 0 | 0 | 0 | 0 | 2 |
| sparse_only_rrf | 0 | 0 | 0 | 0 | 0 | 0 |
| dense_only_rrf | 0 | 0 | 0 | 0 | 0 | 0 |
| dense_sparse_rrf | 0 | 0 | 0 | 0 | 0 | 0 |
| graph_dense_rrf | 0 | 0 | 0 | 0 | 0 | 0 |
| all_paths_planner_dense_rrf | 0 | 0 | 0 | 0 | 0 | 1 |
| baseline_no_reranker | 0 | 0 | 0 | 0 | 0 | 0 |
| baseline_weighted_sum | 0 | 0 | 0 | 0 | 0 | 0 |
| baseline_graph_first | 0 | 0 | 0 | 0 | 0 | 1 |

## Ablation analysis

- Baseline config: `baseline_graph_sparse_rrf`
- Preliminary recommendation: `graph_dense_rrf`
  - Preliminary heuristic ranks configs by context recall, citation coverage, faithfulness, answer relevancy, graph hit rate, and a small p95 latency penalty.
  - Selected `graph_dense_rrf` with context_recall_avg=0.7593, citation_coverage_rate=0.989, p95_latency_ms=72032.09.
  - Treat this as a smoke/first-pass recommendation until official Gemini judge and full dataset runs are complete.

### Context recall ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | graph_dense_rrf | 0.7593 |
| 2 | baseline_no_reranker | 0.744 |
| 3 | dense_sparse_rrf | 0.7418 |
| 4 | dense_only_rrf | 0.7363 |
| 5 | all_paths_planner_dense_rrf | 0.7253 |
| 6 | baseline_graph_first | 0.7253 |
| 7 | baseline_graph_sparse_rrf | 0.7044 |
| 8 | sparse_only_rrf | 0.6956 |
| 9 | baseline_weighted_sum | 0.6945 |
| 10 | graph_only_rrf | 0.5297 |

### Citation coverage ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | dense_only_rrf | 0.989 |
| 2 | dense_sparse_rrf | 0.989 |
| 3 | graph_dense_rrf | 0.989 |
| 4 | all_paths_planner_dense_rrf | 0.989 |
| 5 | baseline_no_reranker | 0.989 |
| 6 | baseline_weighted_sum | 0.989 |
| 7 | baseline_graph_sparse_rrf | 0.9863 |
| 8 | sparse_only_rrf | 0.9863 |
| 9 | baseline_graph_first | 0.9863 |
| 10 | graph_only_rrf | 0.978 |

### Graph hit ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | baseline_graph_sparse_rrf | 0.967 |
| 2 | graph_only_rrf | 0.967 |
| 3 | graph_dense_rrf | 0.967 |
| 4 | all_paths_planner_dense_rrf | 0.967 |
| 5 | baseline_no_reranker | 0.967 |
| 6 | baseline_weighted_sum | 0.967 |
| 7 | baseline_graph_first | 0.967 |
| 8 | sparse_only_rrf | 0.0 |
| 9 | dense_only_rrf | 0.0 |
| 10 | dense_sparse_rrf | 0.0 |

### p95 latency ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | baseline_no_reranker | 12819.41 |
| 2 | dense_only_rrf | 28176.52 |
| 3 | graph_only_rrf | 50835.98 |
| 4 | graph_dense_rrf | 72032.09 |
| 5 | baseline_graph_sparse_rrf | 138041.28 |
| 6 | sparse_only_rrf | 163360.43 |
| 7 | baseline_weighted_sum | 181602.9 |
| 8 | dense_sparse_rrf | 226613.43 |
| 9 | all_paths_planner_dense_rrf | 254152.13 |
| 10 | baseline_graph_first | 272370.05 |

### Retrieval miss summary

| Config | Miss count | Example item IDs |
|---|---:|---|
| baseline_graph_sparse_rrf | 19 | TVQA-010, TVQA-028, TVQA-032, TVQA-038, TVQA-039 |
| graph_only_rrf | 37 | TVQA-005, TVQA-008, TVQA-010, TVQA-017, TVQA-018 |
| sparse_only_rrf | 18 | TVQA-008, TVQA-027, TVQA-028, TVQA-032, TVQA-038 |
| dense_only_rrf | 17 | TVQA-008, TVQA-010, TVQA-025, TVQA-027, TVQA-028 |
| dense_sparse_rrf | 13 | TVQA-008, TVQA-010, TVQA-027, TVQA-028, TVQA-038 |
| graph_dense_rrf | 9 | TVQA-027, TVQA-032, TVQA-038, TVQA-045, TVQA-061 |
| all_paths_planner_dense_rrf | 18 | TVQA-010, TVQA-017, TVQA-025, TVQA-027, TVQA-028 |
| baseline_no_reranker | 15 | TVQA-008, TVQA-010, TVQA-015, TVQA-017, TVQA-028 |
| baseline_weighted_sum | 18 | TVQA-008, TVQA-027, TVQA-028, TVQA-032, TVQA-038 |
| baseline_graph_first | 17 | TVQA-008, TVQA-010, TVQA-027, TVQA-028, TVQA-032 |

### Rerank miss summary

| Config | Miss count | Example item IDs |
|---|---:|---|
| baseline_graph_sparse_rrf | 2 | TVQA-068, TVQA-084 |
| graph_only_rrf | 2 | TVQA-017, TVQA-084 |
| sparse_only_rrf | 2 | TVQA-068, TVQA-084 |
| dense_only_rrf | 1 | TVQA-025 |
| dense_sparse_rrf | 1 | TVQA-068 |
| graph_dense_rrf | 1 | TVQA-084 |
| all_paths_planner_dense_rrf | 1 | TVQA-068 |
| baseline_no_reranker | 0 |  |
| baseline_weighted_sum | 1 | TVQA-068 |
| baseline_graph_first | 2 | TVQA-068, TVQA-097 |

## Metrics by question complexity

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| baseline_graph_sparse_rrf | Direct | 10 | 1.0 | 0.86 | 0.7 | 0.0 | 0.0 | 6939.14 |
| baseline_graph_sparse_rrf | One-hop | 46 | 0.8848 | 0.7826 | 0.7152 | 0.9783 | 0.9946 | 147025.88 |
| baseline_graph_sparse_rrf | Two-hop | 44 | 0.8659 | 0.7795 | 0.6932 | 0.9773 | 1.0 | 133255.05 |
| graph_only_rrf | Direct | 10 | 1.0 | 0.81 | 0.8 | 0.0 | 0.0 | 7220.57 |
| graph_only_rrf | One-hop | 46 | 0.8022 | 0.6826 | 0.55 | 0.9783 | 1.0 | 53674.25 |
| graph_only_rrf | Two-hop | 44 | 0.8045 | 0.6614 | 0.5023 | 0.9773 | 0.9773 | 45256.72 |
| sparse_only_rrf | Direct | 10 | 1.0 | 0.86 | 0.8 | 0.0 | 0.0 | 4355.89 |
| sparse_only_rrf | One-hop | 46 | 0.8891 | 0.7913 | 0.6783 | 0.0 | 0.9946 | 178302.3 |
| sparse_only_rrf | Two-hop | 44 | 0.8886 | 0.8 | 0.7114 | 0.0 | 1.0 | 155663.21 |
| dense_only_rrf | Direct | 10 | 1.0 | 0.84 | 0.8 | 0.0 | 0.0 | 4331.7 |
| dense_only_rrf | One-hop | 46 | 0.8957 | 0.8087 | 0.7478 | 0.0 | 1.0 | 27924.57 |
| dense_only_rrf | Two-hop | 44 | 0.8909 | 0.8091 | 0.7227 | 0.0 | 1.0 | 27972.11 |
| dense_sparse_rrf | Direct | 10 | 1.0 | 0.83 | 0.7 | 0.0 | 0.0 | 8984.52 |
| dense_sparse_rrf | One-hop | 46 | 0.9022 | 0.8326 | 0.7783 | 0.0 | 1.0 | 211654.26 |
| dense_sparse_rrf | Two-hop | 44 | 0.8795 | 0.8 | 0.7045 | 0.0 | 1.0 | 238530.38 |
| graph_dense_rrf | Direct | 10 | 1.0 | 0.84 | 0.7 | 0.0 | 0.0 | 3881.42 |
| graph_dense_rrf | One-hop | 46 | 0.9109 | 0.8696 | 0.7957 | 0.9783 | 1.0 | 72155.94 |
| graph_dense_rrf | Two-hop | 44 | 0.8932 | 0.8023 | 0.7227 | 0.9773 | 1.0 | 70058.17 |
| all_paths_planner_dense_rrf | Direct | 10 | 1.0 | 0.83 | 0.8 | 0.0 | 0.0 | 4318.84 |
| all_paths_planner_dense_rrf | One-hop | 46 | 0.887 | 0.8174 | 0.7717 | 0.9783 | 1.0 | 253331.75 |
| all_paths_planner_dense_rrf | Two-hop | 44 | 0.8455 | 0.7773 | 0.675 | 0.9773 | 1.0 | 254786.17 |
| baseline_no_reranker | Direct | 10 | 1.0 | 0.77 | 0.7 | 0.0 | 0.0 | 4189.75 |
| baseline_no_reranker | One-hop | 46 | 0.9239 | 0.8478 | 0.7565 | 0.9783 | 1.0 | 13026.38 |
| baseline_no_reranker | Two-hop | 44 | 0.8864 | 0.8205 | 0.7318 | 0.9773 | 1.0 | 11892.69 |
| baseline_weighted_sum | Direct | 10 | 1.0 | 0.84 | 0.7 | 0.0 | 0.0 | 7929.15 |
| baseline_weighted_sum | One-hop | 46 | 0.8652 | 0.7696 | 0.687 | 0.9783 | 1.0 | 179826.07 |
| baseline_weighted_sum | Two-hop | 44 | 0.8705 | 0.8091 | 0.7023 | 0.9773 | 1.0 | 196405.2 |
| baseline_graph_first | Direct | 10 | 1.0 | 0.84 | 0.7 | 0.0 | 0.0 | 7567.06 |
| baseline_graph_first | One-hop | 46 | 0.8674 | 0.8065 | 0.763 | 0.9783 | 1.0 | 298655.86 |
| baseline_graph_first | Two-hop | 44 | 0.8568 | 0.7795 | 0.6864 | 0.9773 | 0.9943 | 264742.89 |

## Metrics by question family

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| baseline_graph_sparse_rrf | core_identity | 10 | 1.0 | 0.86 | 0.7 | 0.0 | 0.0 | 6939.14 |
| baseline_graph_sparse_rrf | dai_van_interpretation | 10 | 0.86 | 0.5 | 0.39 | 1.0 | 1.0 | 113888.76 |
| baseline_graph_sparse_rrf | menh_cuc_relation | 10 | 0.94 | 0.96 | 0.89 | 1.0 | 0.975 | 84728.04 |
| baseline_graph_sparse_rrf | menh_house_interpretation | 10 | 0.89 | 0.71 | 0.65 | 0.9 | 1.0 | 160225.52 |
| baseline_graph_sparse_rrf | menh_tam_hop | 10 | 0.88 | 0.78 | 0.69 | 1.0 | 1.0 | 148841.25 |
| baseline_graph_sparse_rrf | menh_xung_chieu | 10 | 0.85 | 0.82 | 0.71 | 1.0 | 1.0 | 120080.1 |
| baseline_graph_sparse_rrf | special_state_interpretation | 10 | 0.74 | 0.68 | 0.6 | 1.0 | 1.0 | 109746.98 |
| baseline_graph_sparse_rrf | synthesis_judgement | 10 | 0.8 | 0.75 | 0.65 | 0.9 | 1.0 | 144369.32 |
| baseline_graph_sparse_rrf | than_cu_interpretation | 10 | 0.98 | 0.94 | 0.9 | 1.0 | 1.0 | 158349.66 |
| baseline_graph_sparse_rrf | topic_house_plus_relations | 10 | 0.94 | 0.89 | 0.86 | 1.0 | 1.0 | 123311.39 |
| graph_only_rrf | core_identity | 10 | 1.0 | 0.81 | 0.8 | 0.0 | 0.0 | 7220.57 |
| graph_only_rrf | dai_van_interpretation | 10 | 0.84 | 0.55 | 0.42 | 1.0 | 1.0 | 48566.0 |
| graph_only_rrf | menh_cuc_relation | 10 | 0.94 | 0.88 | 0.76 | 1.0 | 1.0 | 32217.18 |
| graph_only_rrf | menh_house_interpretation | 10 | 0.75 | 0.58 | 0.49 | 0.9 | 1.0 | 56851.43 |
| graph_only_rrf | menh_tam_hop | 10 | 0.85 | 0.78 | 0.6 | 1.0 | 1.0 | 43062.97 |
| graph_only_rrf | menh_xung_chieu | 10 | 0.59 | 0.6 | 0.39 | 1.0 | 1.0 | 35911.58 |
| graph_only_rrf | special_state_interpretation | 10 | 0.51 | 0.44 | 0.28 | 1.0 | 1.0 | 42675.55 |
| graph_only_rrf | synthesis_judgement | 10 | 0.93 | 0.67 | 0.51 | 0.9 | 0.9 | 55073.86 |
| graph_only_rrf | than_cu_interpretation | 10 | 0.93 | 0.88 | 0.74 | 1.0 | 1.0 | 116648.1 |
| graph_only_rrf | topic_house_plus_relations | 10 | 0.89 | 0.67 | 0.55 | 1.0 | 1.0 | 41675.13 |
| sparse_only_rrf | core_identity | 10 | 1.0 | 0.86 | 0.8 | 0.0 | 0.0 | 4355.89 |
| sparse_only_rrf | dai_van_interpretation | 10 | 0.77 | 0.57 | 0.44 | 0.0 | 1.0 | 146179.51 |
| sparse_only_rrf | menh_cuc_relation | 10 | 0.96 | 0.9 | 0.84 | 0.0 | 0.975 | 91623.77 |
| sparse_only_rrf | menh_house_interpretation | 10 | 0.92 | 0.7 | 0.57 | 0.0 | 1.0 | 174309.45 |
| sparse_only_rrf | menh_tam_hop | 10 | 0.89 | 0.81 | 0.7 | 0.0 | 1.0 | 148914.9 |
| sparse_only_rrf | menh_xung_chieu | 10 | 0.87 | 0.77 | 0.69 | 0.0 | 1.0 | 131818.59 |
| sparse_only_rrf | special_state_interpretation | 10 | 0.84 | 0.72 | 0.6 | 0.0 | 1.0 | 410361.96 |
| sparse_only_rrf | synthesis_judgement | 10 | 0.9 | 0.86 | 0.75 | 0.0 | 1.0 | 160186.43 |
| sparse_only_rrf | than_cu_interpretation | 10 | 0.88 | 0.92 | 0.79 | 0.0 | 1.0 | 858866.88 |
| sparse_only_rrf | topic_house_plus_relations | 10 | 0.97 | 0.91 | 0.87 | 0.0 | 1.0 | 2043126.37 |
| dense_only_rrf | core_identity | 10 | 1.0 | 0.84 | 0.8 | 0.0 | 0.0 | 4331.7 |
| dense_only_rrf | dai_van_interpretation | 10 | 0.77 | 0.66 | 0.57 | 0.0 | 1.0 | 23166.58 |
| dense_only_rrf | menh_cuc_relation | 10 | 0.96 | 0.92 | 0.89 | 0.0 | 1.0 | 24096.16 |
| dense_only_rrf | menh_house_interpretation | 10 | 0.85 | 0.74 | 0.65 | 0.0 | 1.0 | 32828.98 |
| dense_only_rrf | menh_tam_hop | 10 | 0.91 | 0.78 | 0.69 | 0.0 | 1.0 | 20779.99 |
| dense_only_rrf | menh_xung_chieu | 10 | 0.91 | 0.81 | 0.68 | 0.0 | 1.0 | 28571.39 |
| dense_only_rrf | special_state_interpretation | 10 | 0.87 | 0.77 | 0.69 | 0.0 | 1.0 | 24482.57 |
| dense_only_rrf | synthesis_judgement | 10 | 0.94 | 0.85 | 0.72 | 0.0 | 1.0 | 26188.89 |
| dense_only_rrf | than_cu_interpretation | 10 | 0.95 | 0.88 | 0.84 | 0.0 | 1.0 | 28377.06 |
| dense_only_rrf | topic_house_plus_relations | 10 | 0.88 | 0.87 | 0.89 | 0.0 | 1.0 | 28874.92 |
| dense_sparse_rrf | core_identity | 10 | 1.0 | 0.83 | 0.7 | 0.0 | 0.0 | 8984.52 |
| dense_sparse_rrf | dai_van_interpretation | 10 | 0.8 | 0.67 | 0.57 | 0.0 | 1.0 | 163872.48 |
| dense_sparse_rrf | menh_cuc_relation | 10 | 0.94 | 0.91 | 0.9 | 0.0 | 1.0 | 134894.06 |
| dense_sparse_rrf | menh_house_interpretation | 10 | 0.94 | 0.82 | 0.79 | 0.0 | 1.0 | 227806.35 |
| dense_sparse_rrf | menh_tam_hop | 10 | 0.91 | 0.75 | 0.64 | 0.0 | 1.0 | 218428.11 |
| dense_sparse_rrf | menh_xung_chieu | 10 | 0.85 | 0.74 | 0.68 | 0.0 | 1.0 | 197495.67 |
| dense_sparse_rrf | special_state_interpretation | 10 | 0.79 | 0.77 | 0.64 | 0.0 | 1.0 | 189953.75 |
| dense_sparse_rrf | synthesis_judgement | 10 | 0.88 | 0.84 | 0.72 | 0.0 | 1.0 | 259366.09 |
| dense_sparse_rrf | than_cu_interpretation | 10 | 0.99 | 0.93 | 0.91 | 0.0 | 1.0 | 210237.66 |
| dense_sparse_rrf | topic_house_plus_relations | 10 | 0.92 | 0.92 | 0.83 | 0.0 | 1.0 | 225074.05 |
| graph_dense_rrf | core_identity | 10 | 1.0 | 0.84 | 0.7 | 0.0 | 0.0 | 3881.42 |
| graph_dense_rrf | dai_van_interpretation | 10 | 0.91 | 0.75 | 0.68 | 1.0 | 1.0 | 59749.06 |
| graph_dense_rrf | menh_cuc_relation | 10 | 0.91 | 0.93 | 0.89 | 1.0 | 1.0 | 59450.82 |
| graph_dense_rrf | menh_house_interpretation | 10 | 0.92 | 0.82 | 0.74 | 0.9 | 1.0 | 81217.74 |
| graph_dense_rrf | menh_tam_hop | 10 | 0.9 | 0.75 | 0.66 | 1.0 | 1.0 | 72912.44 |
| graph_dense_rrf | menh_xung_chieu | 10 | 0.83 | 0.77 | 0.66 | 1.0 | 1.0 | 56816.83 |
| graph_dense_rrf | special_state_interpretation | 10 | 0.82 | 0.86 | 0.71 | 1.0 | 1.0 | 67841.75 |
| graph_dense_rrf | synthesis_judgement | 10 | 0.94 | 0.86 | 0.78 | 0.9 | 1.0 | 89095.87 |
| graph_dense_rrf | than_cu_interpretation | 10 | 0.96 | 0.92 | 0.88 | 1.0 | 1.0 | 75766.65 |
| graph_dense_rrf | topic_house_plus_relations | 10 | 0.93 | 0.87 | 0.84 | 1.0 | 1.0 | 58236.88 |
| all_paths_planner_dense_rrf | core_identity | 10 | 1.0 | 0.83 | 0.8 | 0.0 | 0.0 | 4318.84 |
| all_paths_planner_dense_rrf | dai_van_interpretation | 10 | 0.74 | 0.68 | 0.59 | 1.0 | 1.0 | 194823.74 |
| all_paths_planner_dense_rrf | menh_cuc_relation | 10 | 0.98 | 0.91 | 0.88 | 1.0 | 1.0 | 163528.53 |
| all_paths_planner_dense_rrf | menh_house_interpretation | 10 | 0.86 | 0.72 | 0.69 | 0.9 | 1.0 | 271129.66 |
| all_paths_planner_dense_rrf | menh_tam_hop | 10 | 0.91 | 0.79 | 0.67 | 1.0 | 1.0 | 251130.44 |
| all_paths_planner_dense_rrf | menh_xung_chieu | 10 | 0.77 | 0.74 | 0.61 | 1.0 | 1.0 | 224971.12 |
| all_paths_planner_dense_rrf | special_state_interpretation | 10 | 0.76 | 0.73 | 0.64 | 1.0 | 1.0 | 223181.02 |
| all_paths_planner_dense_rrf | synthesis_judgement | 10 | 0.91 | 0.8 | 0.69 | 0.9 | 1.0 | 316890.72 |
| all_paths_planner_dense_rrf | than_cu_interpretation | 10 | 0.95 | 0.93 | 0.93 | 1.0 | 1.0 | 252713.21 |
| all_paths_planner_dense_rrf | topic_house_plus_relations | 10 | 0.92 | 0.88 | 0.82 | 1.0 | 1.0 | 250466.12 |
| baseline_no_reranker | core_identity | 10 | 1.0 | 0.77 | 0.7 | 0.0 | 0.0 | 4189.75 |
| baseline_no_reranker | dai_van_interpretation | 10 | 0.82 | 0.68 | 0.58 | 1.0 | 1.0 | 10652.57 |
| baseline_no_reranker | menh_cuc_relation | 10 | 1.0 | 0.94 | 0.92 | 1.0 | 1.0 | 14863.71 |
| baseline_no_reranker | menh_house_interpretation | 10 | 0.84 | 0.73 | 0.63 | 0.9 | 1.0 | 13670.47 |
| baseline_no_reranker | menh_tam_hop | 10 | 0.89 | 0.79 | 0.67 | 1.0 | 1.0 | 10889.18 |
| baseline_no_reranker | menh_xung_chieu | 10 | 0.87 | 0.81 | 0.72 | 1.0 | 1.0 | 10565.21 |
| baseline_no_reranker | special_state_interpretation | 10 | 0.94 | 0.83 | 0.7 | 1.0 | 1.0 | 11861.08 |
| baseline_no_reranker | synthesis_judgement | 10 | 0.92 | 0.88 | 0.8 | 0.9 | 1.0 | 13621.12 |
| baseline_no_reranker | than_cu_interpretation | 10 | 0.93 | 0.97 | 0.87 | 1.0 | 1.0 | 11940.49 |
| baseline_no_reranker | topic_house_plus_relations | 10 | 0.94 | 0.88 | 0.81 | 1.0 | 1.0 | 11053.96 |
| baseline_weighted_sum | core_identity | 10 | 1.0 | 0.84 | 0.7 | 0.0 | 0.0 | 7929.15 |
| baseline_weighted_sum | dai_van_interpretation | 10 | 0.79 | 0.55 | 0.41 | 1.0 | 1.0 | 135952.63 |
| baseline_weighted_sum | menh_cuc_relation | 10 | 0.98 | 0.89 | 0.87 | 1.0 | 1.0 | 115661.71 |
| baseline_weighted_sum | menh_house_interpretation | 10 | 0.86 | 0.71 | 0.63 | 0.9 | 1.0 | 186369.8 |
| baseline_weighted_sum | menh_tam_hop | 10 | 0.88 | 0.82 | 0.7 | 1.0 | 1.0 | 189319.47 |
| baseline_weighted_sum | menh_xung_chieu | 10 | 0.86 | 0.79 | 0.69 | 1.0 | 1.0 | 153840.77 |
| baseline_weighted_sum | special_state_interpretation | 10 | 0.7 | 0.69 | 0.61 | 1.0 | 1.0 | 161273.81 |
| baseline_weighted_sum | synthesis_judgement | 10 | 0.9 | 0.85 | 0.7 | 0.9 | 1.0 | 229528.16 |
| baseline_weighted_sum | than_cu_interpretation | 10 | 0.92 | 0.93 | 0.82 | 1.0 | 1.0 | 179452.3 |
| baseline_weighted_sum | topic_house_plus_relations | 10 | 0.92 | 0.87 | 0.82 | 1.0 | 1.0 | 179481.35 |
| baseline_graph_first | core_identity | 10 | 1.0 | 0.84 | 0.7 | 0.0 | 0.0 | 7567.06 |
| baseline_graph_first | dai_van_interpretation | 10 | 0.76 | 0.6 | 0.49 | 1.0 | 1.0 | 350322.69 |
| baseline_graph_first | menh_cuc_relation | 10 | 0.98 | 0.95 | 0.91 | 1.0 | 1.0 | 144737.42 |
| baseline_graph_first | menh_house_interpretation | 10 | 0.84 | 0.73 | 0.71 | 0.9 | 1.0 | 280513.36 |
| baseline_graph_first | menh_tam_hop | 10 | 0.88 | 0.79 | 0.69 | 1.0 | 1.0 | 249989.17 |
| baseline_graph_first | menh_xung_chieu | 10 | 0.86 | 0.75 | 0.65 | 1.0 | 0.975 | 232925.12 |
| baseline_graph_first | special_state_interpretation | 10 | 0.74 | 0.69 | 0.63 | 1.0 | 1.0 | 298280.38 |
| baseline_graph_first | synthesis_judgement | 10 | 0.77 | 0.76 | 0.63 | 0.9 | 1.0 | 276988.36 |
| baseline_graph_first | than_cu_interpretation | 10 | 0.95 | 0.95 | 0.95 | 1.0 | 1.0 | 254716.91 |
| baseline_graph_first | topic_house_plus_relations | 10 | 0.98 | 0.92 | 0.87 | 1.0 | 1.0 | 210001.37 |

## Per-question results

### baseline_graph_sparse_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 5991.8 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 150234.67 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 137399.52 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 89846.57 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 105015.33 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 2 | 123806.77 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 97023.73 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 7 | 100814.38 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 98596.18 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 6 | 129399.52 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4007.28 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 7 | 168399.85 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 4 | 175490.69 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 72882.47 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 5 | 113618.33 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 5 | 169324.0 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 131256.45 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 6 | 124585.98 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 127015.62 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 7 | 130832.4 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4013.64 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 0.9 | 0.8 | 0.8 | True | 1.0 | 3 | 128914.87 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 3 | 103762.45 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 78472.06 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 5 | 91106.99 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 5 | 114281.68 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.6 | True | 1.0 | 7 | 84892.78 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.2 | 0.2 | True | 1.0 | 7 | 77166.76 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 118784.0 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 0.9 | 1.0 | 0.8 | True | 1.0 | 5 | 153174.24 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 1854.01 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.6 | 0.4 | 0.2 | True | 1.0 | 4 | 122410.01 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 82348.85 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 69837.03 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 8 | 99286.78 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 5 | 111902.08 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 106420.12 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.5 | 0.2 | True | 1.0 | 4 | 81367.8 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.6 | 0.5 | 0.4 | True | 1.0 | 4 | 95983.04 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 4 | 91271.97 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 7714.24 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 78765.46 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 6 | 86053.51 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.8 | 0.6 | True | 1.0 | 4 | 63757.23 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 4 | 101028.53 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 101601.89 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 5 | 100205.97 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 3 | 85160.88 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 81028.74 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 133607.75 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 2793.83 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.2 | 0.2 | True | 1.0 | 5 | 110073.99 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 0.8 | 1.0 | 0.6 | True | 1.0 | 3 | 94511.26 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.9 | 0.6 | True | 1.0 | 5 | 67182.78 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 4 | 96666.86 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 4 | 81174.6 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 81379.33 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.4 | 0.3 | True | 1.0 | 4 | 78288.91 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 7 | 81979.09 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 0.2 | 0.0 | 0.2 | True | 1.0 | 3 | 113364.88 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 0.8 | 0.7 | False | 0.0 | 1 | 3627.41 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 3 | 71409.25 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 117553.98 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 74571.91 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 6 | 60408.91 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 5 | 80784.29 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 7 | 76692.26 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 66868.39 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 4 | 86732.61 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 6 | 83719.31 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3837.14 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 100750.89 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 7 | 119190.06 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 57578.84 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 6 | 76195.78 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 4 | 110869.48 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 79574.95 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.0 | 0.0 | True | 1.0 | 6 | 84441.36 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 101333.39 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 0.6 | 0.4 | 0.2 | True | 1.0 | 5 | 86778.02 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4360.33 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.7 | 0.5 | False | 1.0 | 5 | 104435.23 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 6 | 107385.46 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.9 | 0.7 | True | 0.75 | 1 | 61253.95 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 93843.84 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 99845.56 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 79645.39 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.6 | 0.5 | True | 1.0 | 5 | 74171.27 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 110584.88 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 0.8 | 1.0 | 0.7 | False | 1.0 | 5 | 114131.56 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.2 | None | None | None | 1 | 4016.62 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 5 | 77361.22 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 114135.17 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 73200.14 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 6 | 85793.55 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 0.6 | 0.5 | 0.2 | True | 1.0 | 2 | 79162.54 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 5 | 77342.57 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 0.6 | 0.4 | 0.2 | True | 1.0 | 4 | 67373.47 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 6 | 85513.55 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 93229.04 |  |

### graph_only_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4614.55 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 5 | 50895.89 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 26706.89 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 15674.54 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.4 | True | 1.0 | 2 | 44502.34 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 45273.58 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 31431.22 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.2 | 0.3 | True | 1.0 | 3 | 33534.16 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 5 | 26628.26 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.5 | 0.2 | True | 1.0 | 6 | 25549.41 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 5745.1 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 4 | 36112.68 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 3 | 36651.38 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 16530.33 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 0.6 | True | 1.0 | 3 | 40442.81 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.5 | True | 1.0 | 2 | 27737.54 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.2 | 0.4 | 0.0 | True | 1.0 | 6 | 23828.68 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.6 | 0.2 | True | 1.0 | 7 | 26808.32 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 7 | 24647.51 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.6 | 0.5 | True | 1.0 | 5 | 37097.79 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3832.61 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 8 | 61724.15 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 7 | 41374.27 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 4 | 24528.17 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 0.5 | 0.6 | 0.0 | True | 1.0 | 4 | 30983.9 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 4 | 40361.11 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 6 | 26157.42 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.2 | 0.2 | 0.2 | True | 1.0 | 6 | 29564.17 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 6 | 30147.15 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 6 | 63184.24 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 0.7 | None | None | None | 1 | 2308.6 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.5 | 0.4 | 0.2 | True | 1.0 | 2 | 40322.09 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 29124.37 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 2 | 25265.05 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 5 | 36622.26 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 4 | 35882.58 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 0.5 | 0.8 | 0.2 | True | 1.0 | 5 | 31696.86 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 7 | 31745.06 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 5 | 31970.75 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 7 | 26475.64 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 2808.42 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 2 | 23008.95 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 5 | 28610.02 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.5 | True | 1.0 | 7 | 17754.86 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.0 | 0.0 | True | 1.0 | 3 | 32451.87 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 3 | 28092.26 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 2 | 39359.99 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 7 | 34510.6 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 7 | 27227.55 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 45161.17 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3169.93 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.5 | 0.2 | True | 1.0 | 5 | 39828.48 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 0.8 | 1.0 | 0.5 | True | 1.0 | 4 | 31259.85 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 5 | 24155.91 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 38775.46 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 7 | 25414.43 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.5 | True | 1.0 | 4 | 25340.19 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 0.5 | 0.5 | True | 1.0 | 3 | 30931.96 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 5 | 32209.48 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 0.9 | 1.0 | 0.8 | True | 1.0 | 5 | 43636.6 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 0.8 | 0.8 | False | 0.0 | 1 | 3863.1 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.6 | 0.2 | True | 1.0 | 3 | 21045.08 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.5 | True | 1.0 | 5 | 39724.04 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 28302.63 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 4 | 23088.9 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 6 | 22910.14 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 0.2 | 0.2 | 0.0 | True | 1.0 | 5 | 19016.43 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 18847.23 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.6 | 0.4 | True | 1.0 | 3 | 24794.83 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.7 | 0.4 | True | 1.0 | 3 | 26443.12 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3724.59 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 5 | 30730.67 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 0.9 | 1.0 | 1.0 | True | 1.0 | 4 | 170496.95 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 2 | 15401.45 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 3 | 22524.18 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 4 | 29877.12 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 6 | 27904.16 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.5 | True | 1.0 | 3 | 41190.67 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 0.2 | 0.2 | 0.0 | True | 1.0 | 4 | 27990.82 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.4 | 0.2 | True | 1.0 | 3 | 35622.05 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 8427.77 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 0.0 | 0.0 | 1.0 | False | 1.0 | 1 | 6180.47 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 50832.83 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 2 | 20601.45 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 0.8 | True | 1.0 | 3 | 40420.31 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 6 | 39357.59 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 3 | 29483.18 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.4 | 0.2 | True | 1.0 | 4 | 54600.37 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.2 | 0.0 | True | 1.0 | 6 | 49419.75 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.5 | 0.4 | False | 0.0 | 1 | 3847.02 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.0 | None | None | None | 1 | 4212.58 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.5 | 0.2 | True | 1.0 | 4 | 24436.48 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 7 | 43861.07 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 7 | 35419.99 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 0.0 | 0.2 | 0.0 | True | 1.0 | 3 | 35040.84 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 3 | 29645.19 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 9 | 30950.73 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 3 | 32403.65 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.5 | 0.4 | True | 1.0 | 5 | 28424.07 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.2 | 0.0 | True | 1.0 | 4 | 34786.77 |  |

### sparse_only_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3707.68 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.8 | False | 1.0 | 4 | 106015.3 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 4 | 116739.85 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 3 | 80983.64 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 6 | 128460.67 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 4 | 155677.95 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 8 | 136928.08 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.4 | 0.2 | False | 1.0 | 6 | 135408.85 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 3 | 117517.8 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.7 | 0.5 | False | 1.0 | 6 | 108034.84 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4433.54 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.7 | 0.5 | False | 1.0 | 8 | 136700.13 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.7 | False | 1.0 | 5 | 131127.98 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 5 | 73134.32 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.8 | 1.0 | 0.7 | False | 1.0 | 5 | 72108.57 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.7 | False | 1.0 | 7 | 109595.38 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.6 | 0.5 | False | 1.0 | 4 | 97188.99 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 0.9 | 0.8 | 0.7 | False | 1.0 | 5 | 154991.86 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 6 | 109150.44 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 5 | 133369.66 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3557.98 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.6 | False | 1.0 | 2 | 140069.54 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 1.0 | False | 1.0 | 5 | 125622.61 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 4 | 91723.12 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 5 | 640171.91 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.8 | False | 1.0 | 5 | 106522.59 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.5 | 0.2 | False | 1.0 | 4 | 81864.25 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.4 | 0.2 | False | 1.0 | 5 | 80712.27 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 1.0 | False | 1.0 | 6 | 3602752.48 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.9 | 0.8 | False | 1.0 | 7 | 150939.76 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 1670.5 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.4 | 0.2 | False | 1.0 | 6 | 138023.25 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 6 | 1442907.99 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.6 | False | 1.0 | 4 | 67383.07 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 8 | 107795.03 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 0.8 | False | 1.0 | 6 | 140648.95 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 5 | 125573.66 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.4 | 0.2 | False | 1.0 | 5 | 92141.76 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.7 | 0.4 | False | 1.0 | 3 | 102931.51 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 5 | 99685.17 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 2468.88 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 3 | 92584.28 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 7 | 104226.41 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.7 | 0.5 | False | 1.0 | 4 | 77170.48 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.0 | 0.0 | False | 1.0 | 5 | 129483.14 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 1.0 | False | 1.0 | 6 | 123867.02 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.9 | 0.8 | 0.7 | False | 1.0 | 5 | 117694.96 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 0.9 | 0.8 | False | 1.0 | 3 | 97774.14 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 4 | 88819.37 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 4 | 155579.7 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 2947.36 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.2 | 0.0 | False | 1.0 | 5 | 183293.36 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 0.0 | 1.0 | 0.0 | False | 1.0 | 5 | 127574.08 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.6 | False | 1.0 | 4 | 91502.34 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 4 | 117438.1 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 4 | 100506.55 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 8 | 91980.42 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 0.2 | 0.0 | 0.0 | False | 1.0 | 4 | 84477.51 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 0.8 | False | 1.0 | 4 | 93590.98 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 4 | 130728.51 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 0.8 | 0.8 | False | 0.0 | 1 | 3726.86 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.6 | False | 1.0 | 6 | 83770.44 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.7 | False | 1.0 | 3 | 132881.0 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 3 | 78339.51 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.6 | False | 1.0 | 6 | 71795.28 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.6 | 0.4 | False | 1.0 | 3 | 93734.49 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.8 | 1.0 | False | 1.0 | 7 | 92898.37 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 4 | 82319.73 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 0.9 | 0.8 | 0.7 | False | 1.0 | 3 | 104246.37 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.8 | 0.6 | False | 1.0 | 4 | 105022.71 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3464.86 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 1.0 | False | 1.0 | 5 | 110139.03 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.7 | False | 1.0 | 3 | 145038.85 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 1.0 | False | 1.0 | 2 | 73084.45 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 0.2 | 0.3 | 0.0 | False | 1.0 | 6 | 86900.55 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 5 | 134998.98 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 4 | 102816.0 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 5 | 99800.67 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 5 | 120456.99 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 3 | 110514.07 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4260.99 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.6 | 0.4 | False | 1.0 | 3 | 163329.11 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 5 | 124398.42 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.9 | 0.7 | False | 0.75 | 1 | 79499.14 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 5 | 105193.35 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.9 | 0.8 | False | 1.0 | 5 | 117578.99 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 5 | 91123.81 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.5 | 0.4 | False | 1.0 | 4 | 87588.82 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 6 | 136916.68 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 5 | 163955.58 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.2 | None | None | None | 1 | 3947.85 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.6 | False | 1.0 | 6 | 88372.62 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.9 | 0.8 | False | 1.0 | 2 | 135212.53 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 3 | 76736.21 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.8 | False | 1.0 | 5 | 97491.41 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.5 | 0.4 | False | 1.0 | 5 | 93510.1 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 3 | 89156.22 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 4 | 81766.27 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.8 | False | 1.0 | 7 | 93274.4 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 6 | 109943.41 |  |

### dense_only_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3903.14 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 1.0 | False | 1.0 | 6 | 37825.57 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 1.0 | False | 1.0 | 4 | 20107.95 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 7 | 19278.86 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 5 | 17905.61 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.8 | False | 1.0 | 7 | 18465.14 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 5 | 20581.96 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 0.6 | 0.4 | 0.3 | False | 1.0 | 4 | 16695.43 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 5 | 19166.17 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.7 | 0.4 | False | 1.0 | 5 | 26858.19 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3850.59 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 1.0 | False | 1.0 | 7 | 26722.04 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 0.9 | 0.8 | 0.7 | False | 1.0 | 4 | 28419.31 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 5 | 24832.68 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.8 | 1.0 | 0.6 | False | 1.0 | 5 | 26407.95 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.8 | False | 1.0 | 5 | 18062.54 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.9 | 0.8 | 0.8 | False | 1.0 | 4 | 28900.88 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 5 | 21849.32 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 4 | 24081.84 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 3 | 25370.85 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3422.33 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 5 | 21559.91 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 1.0 | False | 1.0 | 4 | 20145.51 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 1.0 | False | 1.0 | 4 | 23195.96 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.6 | 0.5 | False | 1.0 | 3 | 17310.03 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.8 | False | 1.0 | 4 | 19233.47 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.4 | False | 1.0 | 7 | 19886.4 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.2 | 0.3 | 0.2 | False | 1.0 | 5 | 20587.12 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 1.0 | False | 1.0 | 6 | 21685.84 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.9 | 0.8 | False | 1.0 | 6 | 21221.56 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 0.7 | None | None | None | 1 | 1852.94 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.4 | 0.3 | 0.2 | False | 1.0 | 4 | 18768.26 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 7 | 28325.42 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.7 | False | 1.0 | 5 | 20588.13 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.9 | 1.0 | False | 1.0 | 5 | 21356.72 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | False | 1.0 | 5 | 20086.07 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 6 | 18439.81 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.5 | 0.2 | False | 1.0 | 6 | 17797.04 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.2 | 0.3 | 0.2 | False | 1.0 | 3 | 31817.18 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 5 | 24705.32 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 2686.43 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 4 | 19765.4 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 4 | 19477.46 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.9 | 0.8 | False | 1.0 | 5 | 20143.94 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.0 | 0.0 | False | 1.0 | 6 | 21479.32 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | False | 1.0 | 4 | 19051.56 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.8 | 0.7 | False | 1.0 | 5 | 18820.07 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 6 | 20845.62 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 1.0 | False | 1.0 | 4 | 20044.71 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 6 | 18965.48 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3251.16 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.5 | 0.0 | False | 1.0 | 4 | 22339.8 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 0.8 | 1.0 | 0.8 | False | 1.0 | 4 | 17612.39 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 0.6 | 0.7 | 0.4 | False | 1.0 | 5 | 21664.24 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 7 | 19429.27 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 0.8 | False | 1.0 | 4 | 18374.16 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 4 | 20999.5 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 5 | 19291.05 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 0.9 | 0.8 | 0.7 | False | 1.0 | 4 | 25278.83 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 3 | 19632.48 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 0.9 | 0.8 | False | 0.0 | 1 | 4396.58 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.9 | False | 1.0 | 6 | 18026.6 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.7 | False | 1.0 | 3 | 19073.41 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 6 | 18656.15 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 0.9 | 1.0 | 0.8 | False | 1.0 | 5 | 19771.95 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 5 | 21347.74 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.5 | 0.2 | False | 1.0 | 5 | 19260.21 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.9 | 1.0 | False | 1.0 | 4 | 24244.33 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.9 | 1.0 | False | 1.0 | 3 | 19124.28 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 3 | 19717.6 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3727.3 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 0.9 | 0.8 | 0.7 | False | 1.0 | 5 | 18198.04 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.8 | False | 1.0 | 6 | 18304.94 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 4 | 19389.18 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 0.5 | 0.6 | 0.4 | False | 1.0 | 5 | 18392.74 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 2 | 17700.14 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.8 | 0.6 | False | 1.0 | 6 | 28168.68 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 4 | 18384.96 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 6 | 19193.26 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.5 | 0.0 | False | 1.0 | 3 | 21132.69 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4252.41 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 4 | 18139.28 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 0.8 | False | 1.0 | 4 | 18103.69 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 5 | 18816.57 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 0.9 | 1.0 | 1.0 | False | 1.0 | 4 | 22129.32 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.8 | False | 1.0 | 8 | 18541.25 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 3 | 17765.04 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 0.9 | 0.7 | 0.6 | False | 1.0 | 6 | 17140.72 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 6 | 18333.29 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 0.8 | False | 1.0 | 4 | 20414.07 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.0 | None | None | None | 1 | 4161.54 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.7 | False | 1.0 | 4 | 18233.06 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 4 | 18759.9 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 6 | 20124.02 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.9 | 1.0 | False | 1.0 | 6 | 16908.36 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.5 | 0.2 | False | 1.0 | 4 | 19197.01 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.6 | 0.4 | False | 1.0 | 3 | 19217.39 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 4 | 18066.88 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 0.9 | 0.9 | 1.0 | False | 1.0 | 4 | 17675.6 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 5 | 18808.52 |  |

### dense_sparse_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 10665.56 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 1.0 | False | 1.0 | 7 | 181422.09 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 4 | 158902.05 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 3 | 113590.14 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 6 | 170845.78 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.7 | False | 1.0 | 3 | 221194.35 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.9 | 1.0 | False | 1.0 | 7 | 173663.99 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.4 | 0.2 | False | 1.0 | 5 | 168456.53 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 0.8 | False | 1.0 | 7 | 170769.52 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.5 | 0.2 | False | 1.0 | 7 | 175017.4 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 2914.46 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.8 | False | 1.0 | 4 | 204588.39 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 0.8 | False | 1.0 | 4 | 201680.32 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 3 | 118918.05 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.8 | 1.0 | 0.8 | False | 1.0 | 5 | 123944.17 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.7 | False | 1.0 | 6 | 205230.38 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.6 | 0.5 | False | 1.0 | 7 | 156173.84 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 2 | 149831.71 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 6 | 140716.68 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 6 | 163947.31 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3406.46 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 4 | 211798.0 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.6 | False | 1.0 | 4 | 176611.78 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 1.0 | False | 1.0 | 5 | 124501.97 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.5 | False | 1.0 | 5 | 161399.68 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.7 | False | 1.0 | 5 | 206715.84 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.2 | 0.2 | False | 1.0 | 7 | 159272.53 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.6 | 0.4 | 0.3 | False | 1.0 | 6 | 149939.81 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 5 | 233748.29 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 5 | 268037.0 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 0.7 | None | None | None | 1 | 4608.18 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 4 | 226494.14 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 6 | 152729.85 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 1.0 | False | 1.0 | 6 | 137920.76 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 7 | 183514.01 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | False | 1.0 | 5 | 213452.92 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 0.9 | 1.0 | 0.8 | False | 1.0 | 4 | 202658.28 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.7 | 0.4 | False | 1.0 | 6 | 154600.07 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.6 | 0.7 | 0.4 | False | 1.0 | 4 | 180860.92 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 6 | 177422.31 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 2459.71 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 4 | 146983.29 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 8 | 148424.54 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 4 | 121659.87 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 0.0 | 0.0 | 0.0 | False | 1.0 | 6 | 195222.63 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | False | 1.0 | 6 | 188538.61 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 5 | 191185.82 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 0.9 | 0.9 | 1.0 | False | 1.0 | 6 | 158269.75 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 5 | 137782.09 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 5 | 239374.28 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 2650.01 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.4 | 0.2 | False | 1.0 | 5 | 203294.42 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 4 | 179670.76 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 5 | 131194.76 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 5 | 158480.31 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 5 | 150469.25 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.8 | False | 1.0 | 6 | 153958.73 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 5 | 149544.43 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 0.8 | False | 1.0 | 7 | 150448.69 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 3 | 202585.05 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 0.8 | 0.7 | False | 0.0 | 1 | 6929.91 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.8 | False | 1.0 | 7 | 131383.34 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 5 | 209033.31 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 2 | 126513.63 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.7 | False | 1.0 | 6 | 103203.63 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.4 | 0.3 | False | 1.0 | 6 | 153550.58 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.8 | 1.0 | False | 1.0 | 5 | 145627.71 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 0.9 | 1.0 | 1.0 | False | 1.0 | 5 | 129431.38 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 7 | 148421.2 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.9 | 0.8 | False | 1.0 | 5 | 156628.78 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3444.4 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 1.0 | False | 1.0 | 4 | 173122.75 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 1.0 | False | 1.0 | 3 | 211223.03 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 4 | 117494.02 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 0.5 | 0.5 | 0.0 | False | 1.0 | 6 | 137840.28 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | False | 1.0 | 4 | 215047.15 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 2 | 150631.73 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.5 | False | 1.0 | 5 | 150508.33 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 3 | 165691.31 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 3 | 156556.44 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4191.05 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.6 | 0.5 | False | 1.0 | 7 | 228879.97 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 1.0 | False | 1.0 | 4 | 179305.23 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 3 | 120741.71 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 5 | 166793.38 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 1.0 | False | 1.0 | 6 | 176262.49 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 5 | 150121.02 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.5 | False | 1.0 | 4 | 139317.92 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 5 | 214472.2 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 0.8 | 1.0 | 0.7 | False | 1.0 | 4 | 248768.31 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.0 | None | None | None | 1 | 4306.87 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 0.9 | False | 1.0 | 6 | 138167.83 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 0.9 | 0.8 | 0.7 | False | 1.0 | 5 | 204674.9 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 2 | 123341.32 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 0.8 | False | 1.0 | 6 | 145765.86 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.5 | 0.2 | False | 1.0 | 3 | 148276.14 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 4 | 140293.02 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 4 | 123374.5 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 5 | 147825.05 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 4 | 157955.31 |  |

### graph_dense_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3011.8 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 51845.83 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 53075.11 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 38164.63 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 56951.46 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 3 | 74966.02 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 57477.91 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 6 | 59809.9 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 8 | 52633.44 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.9 | 0.5 | True | 1.0 | 5 | 47792.63 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 3604.79 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 5 | 61024.95 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 5 | 61048.54 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 37128.3 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 51013.55 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 51146.45 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.8 | 1.0 | True | 1.0 | 5 | 45654.71 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 3 | 52843.57 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 0.9 | 1.0 | 1.0 | True | 1.0 | 8 | 46197.93 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 65630.24 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3290.83 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 95943.57 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 65179.73 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 3 | 47181.18 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 0.8 | 1.0 | 0.7 | True | 1.0 | 4 | 58046.54 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 4 | 70402.51 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 4 | 45907.53 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 6 | 50497.18 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 55147.64 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 106268.66 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 1395.82 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.4 | 0.2 | True | 1.0 | 4 | 61694.54 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 48839.25 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 2 | 48572.13 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 62611.66 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 5 | 56132.09 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 56008.84 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.5 | 0.2 | True | 1.0 | 5 | 59674.69 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 6 | 52886.29 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 3 | 55099.2 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 2279.75 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 3 | 43666.08 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 47150.77 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 4 | 37860.05 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 0.0 | 0.5 | 0.0 | True | 1.0 | 4 | 54167.07 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 4 | 52431.39 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 55973.83 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 2 | 57613.13 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 43879.83 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 68106.91 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 2780.7 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 3 | 63219.5 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 53227.28 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 6 | 44006.8 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 65511.91 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 7 | 47659.93 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 47560.44 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.9 | 1.0 | True | 1.0 | 3 | 51015.4 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 4 | 56790.77 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 62770.87 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 0.8 | 0.7 | False | 0.0 | 1 | 3774.37 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 38994.66 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 5 | 72023.24 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 55632.03 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 0.8 | True | 1.0 | 5 | 43378.85 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 3 | 47956.84 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 0.5 | 0.5 | 0.0 | True | 1.0 | 4 | 40932.94 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 43810.36 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 3 | 48107.35 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 3 | 51474.28 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3167.45 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 51596.62 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 7 | 68107.79 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 0.8 | 1.0 | 1.0 | True | 1.0 | 3 | 37316.89 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.7 | 0.5 | True | 1.0 | 4 | 50208.89 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.9 | 0.8 | True | 1.0 | 3 | 56688.26 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.8 | True | 1.0 | 5 | 45781.59 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 3 | 56080.45 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 42612.05 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.4 | 0.2 | True | 1.0 | 5 | 57262.9 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3275.58 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 3 | 20554.97 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 5 | 78684.68 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 2 | 41244.34 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 69747.98 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 6 | 67309.12 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 5 | 52107.01 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.6 | 0.5 | True | 1.0 | 5 | 58245.31 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 59420.07 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 3 | 25119.82 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.2 | None | None | None | 1 | 3969.0 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 53075.42 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 72200.17 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 0.8 | 1.0 | 1.0 | True | 1.0 | 3 | 62575.29 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 6 | 58219.06 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.4 | 0.2 | True | 1.0 | 3 | 44576.37 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 4 | 48379.96 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 4 | 45398.38 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 3 | 46480.28 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 4 | 55974.13 |  |

### all_paths_planner_dense_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 2877.24 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 167689.05 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 188200.7 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 129578.32 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 6 | 199772.93 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 3 | 255048.95 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 207273.39 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 5 | 197209.86 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 8 | 189684.49 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.7 | 0.4 | True | 1.0 | 6 | 198301.68 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3371.59 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 6 | 240259.78 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 231433.71 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 130365.57 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.8 | 1.0 | 0.7 | True | 1.0 | 5 | 158190.64 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 4 | 231992.5 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.2 | 0.4 | 0.2 | True | 1.0 | 5 | 178442.8 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 4 | 176914.01 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 169674.85 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 207994.03 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3012.54 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 3 | 281231.28 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 3 | 217308.77 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 6 | 147334.62 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 0.2 | 0.2 | 0.0 | True | 1.0 | 4 | 197869.66 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 5 | 246341.15 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.5 | 0.2 | True | 1.0 | 7 | 179565.61 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.2 | 0.2 | 0.2 | True | 1.0 | 6 | 174381.54 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 253297.09 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 4 | 339253.47 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 0.5 | None | None | None | 1 | 1818.71 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.6 | 0.4 | 0.2 | True | 1.0 | 5 | 258783.24 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 180028.69 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 158516.94 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 221501.92 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 4 | 246133.87 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 3 | 232015.34 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.7 | 0.4 | True | 1.0 | 6 | 179949.84 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.6 | 0.5 | 0.2 | True | 1.0 | 5 | 215993.57 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 5 | 203752.04 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 0.5 | None | None | None | 1 | 2426.11 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 172004.51 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 175923.27 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 3 | 132398.63 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 6 | 224554.83 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 6 | 221810.84 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 5 | 216361.52 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 0.9 | 0.9 | 1.0 | True | 1.0 | 4 | 191907.38 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 168242.97 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 289558.48 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3621.11 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.1 | 0.0 | True | 1.0 | 4 | 240648.66 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 0.8 | 1.0 | 1.0 | True | 1.0 | 2 | 209684.13 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 5 | 151714.14 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 200963.85 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.4 | True | 1.0 | 5 | 180597.84 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 183961.2 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 0.2 | 0.3 | 0.2 | True | 1.0 | 6 | 175952.26 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 5 | 181376.32 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 0.6 | 0.5 | 0.4 | True | 1.0 | 3 | 240164.13 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 0.8 | 0.8 | False | 0.0 | 1 | 4531.21 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 6 | 155739.29 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 254104.93 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 163877.2 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 6 | 128704.33 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 176525.81 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 6 | 163938.15 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 151145.4 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 5 | 176358.21 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 184789.85 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3460.65 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 4 | 206449.8 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 251012.22 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 1.0 | True | 1.0 | 4 | 133558.88 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 4 | 171873.68 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 0.9 | 1.0 | 0.8 | True | 1.0 | 5 | 244457.76 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 2 | 176104.91 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.9 | 0.8 | True | 1.0 | 6 | 185487.53 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 192227.55 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.4 | 0.2 | True | 1.0 | 7 | 187638.43 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4059.27 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.7 | False | 1.0 | 4 | 233257.25 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 3 | 224114.68 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 136283.28 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 202671.23 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 215624.88 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.8 | True | 1.0 | 5 | 178861.53 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 7 | 163867.79 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 247006.04 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 0.9 | 1.0 | 0.8 | False | 1.0 | 6 | 249142.78 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.5 | None | None | None | 1 | 4028.82 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 169444.15 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 3 | 246581.9 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 163102.37 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 184204.56 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 4 | 174013.42 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 172887.72 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 4 | 147430.51 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 3 | 177257.44 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 4 | 242002.41 |  |

### baseline_no_reranker

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3437.66 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 3 | 9086.19 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 9 | 8670.86 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 7583.15 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 5 | 10194.33 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 6 | 9301.34 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 0.9 | 0.9 | 1.0 | True | 1.0 | 6 | 8590.01 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.4 | 0.2 | True | 1.0 | 7 | 11204.65 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 9341.22 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.7 | 0.4 | True | 1.0 | 5 | 10009.41 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 3979.01 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 4 | 10765.88 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 0.9 | 0.9 | 0.8 | True | 1.0 | 6 | 9467.26 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 7990.86 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.4 | True | 1.0 | 4 | 8280.73 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 5 | 10616.99 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.6 | 0.5 | 0.4 | True | 1.0 | 4 | 8860.31 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 6 | 8680.64 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 10038.79 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 10288.6 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3938.58 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 7 | 11296.32 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 9051.42 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 8674.25 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 5 | 10348.22 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 6 | 10873.16 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 3 | 9384.06 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.2 | 0.3 | 0.2 | True | 1.0 | 7 | 9109.87 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 0.9 | 1.0 | 0.8 | True | 1.0 | 4 | 11522.05 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 13019.69 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 0.5 | None | None | None | 1 | 2227.68 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.6 | 0.4 | 0.2 | True | 1.0 | 6 | 10518.84 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 8399.85 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 8199.95 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 6 | 9706.74 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 6 | 10902.28 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 10709.34 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 0.6 | 0.5 | 0.2 | True | 1.0 | 8 | 9977.8 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 4 | 9164.49 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 5 | 8855.3 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 3342.82 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 8943.96 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 9352.3 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 4 | 7995.86 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.5 | 0.0 | True | 1.0 | 4 | 9442.68 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.9 | 0.8 | True | 1.0 | 5 | 9585.1 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 8 | 10389.05 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 8812.17 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 7 | 10481.84 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 14113.2 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3977.32 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.2 | 0.0 | True | 1.0 | 4 | 15612.96 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 0.8 | 1.0 | 0.5 | True | 1.0 | 4 | 12808.87 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 5 | 19927.82 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 9 | 13098.88 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.4 | True | 1.0 | 4 | 8914.19 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 9626.23 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 6 | 9554.79 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 4 | 8629.84 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 0.9 | 1.0 | 1.0 | True | 1.0 | 6 | 11958.1 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 0.6 | 0.7 | False | 0.0 | 1 | 3967.93 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.6 | 0.5 | True | 1.0 | 3 | 10301.89 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 10879.14 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 7163.11 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 9256.37 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 9011.09 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 4 | 8572.62 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 8141.11 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 4 | 9477.77 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 3 | 9239.45 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3791.03 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 9384.84 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 10462.98 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 7061.66 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 3 | 8173.48 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 4 | 10308.64 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 4 | 8927.74 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 5 | 9235.01 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 8542.37 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 6 | 9106.0 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4283.97 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.6 | False | 1.0 | 7 | 8122.54 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 9751.04 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 7882.2 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 9168.65 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 5 | 8952.89 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 4 | 8908.24 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 7 | 8945.24 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 10251.12 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 6 | 8269.6 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.0 | None | None | None | 1 | 4074.59 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 8610.28 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 9007.71 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 5 | 7955.94 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 4 | 10056.07 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 3 | 8634.62 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 2 | 9781.76 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 4 | 8596.75 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 4 | 9291.12 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 10915.34 |  |

### baseline_weighted_sum

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3465.35 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 0.9 | 0.8 | 0.8 | True | 1.0 | 4 | 118319.32 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 138442.76 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 90847.62 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 6 | 139964.71 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 177778.24 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 144440.37 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.4 | 0.2 | True | 1.0 | 6 | 140126.88 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 147271.05 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.8 | 1.0 | 0.5 | True | 1.0 | 6 | 138899.54 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3982.95 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 7 | 121897.45 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 129349.99 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 60124.07 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.8 | 1.0 | 0.7 | True | 1.0 | 6 | 115827.38 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 7 | 176217.87 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 132244.55 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 5 | 126914.05 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 124711.88 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 154743.22 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3824.09 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 7 | 154530.36 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 105921.39 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 1.0 | True | 1.0 | 3 | 111568.04 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 0.6 | 0.5 | 0.5 | True | 1.0 | 5 | 142179.78 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 5 | 173535.72 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.5 | 0.2 | True | 1.0 | 7 | 124321.52 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.4 | 0.2 | True | 1.0 | 7 | 115383.09 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 6 | 181526.82 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 0.9 | 0.9 | 0.8 | True | 1.0 | 6 | 253225.13 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 2558.22 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.6 | 0.5 | 0.4 | True | 1.0 | 6 | 191246.54 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 135642.51 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 119011.07 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 8 | 160229.89 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 4 | 174236.5 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 0.9 | 1.0 | 1.0 | True | 1.0 | 7 | 136703.03 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 4 | 120094.49 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.4 | 0.5 | 0.2 | True | 1.0 | 2 | 132983.18 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 3 | 143658.89 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 2615.68 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 123019.28 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 136435.37 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 4 | 104027.84 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 4 | 162127.93 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 6 | 198762.29 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 7 | 161532.01 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 0.9 | 1.0 | 1.0 | True | 1.0 | 3 | 130850.76 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 7 | 124134.72 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 200565.2 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3108.99 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.2 | 0.0 | True | 1.0 | 6 | 180409.35 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 0.5 | 0.8 | 0.0 | True | 1.0 | 4 | 143539.78 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 5 | 104401.17 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 156635.22 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.8 | True | 1.0 | 3 | 117836.21 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 8 | 128512.42 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 0.2 | 0.3 | 0.2 | True | 1.0 | 5 | 117986.85 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.9 | 0.8 | True | 1.0 | 4 | 127426.3 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 4 | 174857.53 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 0.8 | 0.7 | False | 0.0 | 1 | 3993.4 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 94921.8 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 116181.62 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 90388.87 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 6 | 90873.1 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 5 | 122981.78 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 7 | 115650.73 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 105269.64 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 3 | 134042.92 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 6 | 103565.44 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3638.6 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 4 | 135040.56 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 3 | 180578.2 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 1.0 | True | 1.0 | 3 | 89315.28 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 6 | 119860.31 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 5 | 175151.39 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 4 | 126359.02 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.2 | 0.0 | True | 1.0 | 4 | 130053.39 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 139750.42 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 7 | 133692.77 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4373.15 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.6 | 0.5 | False | 1.0 | 3 | 166540.67 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 6 | 178076.21 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 4 | 86239.24 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 149929.39 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 159822.16 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 122515.3 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.4 | 0.3 | True | 1.0 | 4 | 116150.07 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 176981.34 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 0.8 | 1.0 | 0.8 | False | 1.0 | 6 | 183048.35 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.0 | None | None | None | 1 | 10838.6 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 6 | 107061.57 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 3 | 134114.41 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 91879.7 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 5 | 131425.99 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.4 | 0.2 | True | 1.0 | 4 | 119170.51 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 5 | 115279.61 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.5 | 0.2 | True | 1.0 | 7 | 109822.01 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 8 | 115745.04 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 5 | 147522.07 |  |

### baseline_graph_first

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3942.98 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 118893.2 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 140119.74 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 95582.44 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 6 | 247719.04 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 2 | 189695.21 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 176648.78 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.4 | 0.3 | True | 1.0 | 7 | 472940.69 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 214022.01 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.5 | 0.2 | True | 1.0 | 6 | 203917.11 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 5994.55 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.6 | 0.5 | True | 1.0 | 8 | 259752.15 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 299041.22 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 93205.49 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 114877.68 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 7 | 154172.09 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 138400.14 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 133313.48 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 154985.65 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 252557.15 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3819.21 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 3 | 203664.56 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 1.0 | True | 1.0 | 3 | 165097.26 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 113159.75 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 164244.0 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 4 | 224261.84 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.4 | 0.2 | True | 1.0 | 6 | 127964.6 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.2 | 0.1 | 0.2 | True | 1.0 | 7 | 127832.93 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 205087.25 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 0.9 | 0.9 | 0.8 | True | 1.0 | 7 | 271908.22 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 7398.35 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.4 | 0.3 | 0.2 | True | 1.0 | 5 | 183359.84 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 146283.12 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 121650.11 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 8 | 191919.97 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 5 | 200293.28 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 234888.98 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 4 | 200456.24 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 5 | 203205.87 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 4 | 215493.9 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 7705.09 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 0.8 | True | 1.0 | 2 | 178145.06 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 193741.63 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 4 | 148593.04 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 5 | 238854.13 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.9 | 1.0 | True | 1.0 | 6 | 229328.54 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 5 | 230524.84 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 3 | 176465.55 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 164559.07 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 205044.07 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4996.47 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.2 | 0.2 | True | 1.0 | 6 | 174708.77 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 0.8 | 1.0 | 1.0 | True | 1.0 | 5 | 147941.46 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 5 | 105368.83 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 4 | 152043.05 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.8 | 0.7 | True | 1.0 | 4 | 122854.06 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 8 | 122621.13 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 4 | 117051.9 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 7 | 124612.12 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 175903.32 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 0.8 | 0.7 | False | 0.0 | 1 | 3844.31 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 3 | 113143.21 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 186262.63 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 116077.95 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 6 | 94942.14 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 5 | 123580.79 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 7 | 114764.63 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 102360.51 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 3 | 136355.09 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 3 | 153648.25 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3422.78 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 148693.88 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 180867.28 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 91547.95 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 6 | 118044.16 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 177719.02 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 121870.01 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 4 | 127921.62 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 137966.79 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 6 | 281144.84 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4211.54 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.6 | 0.4 | False | 1.0 | 5 | 297499.8 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 200542.76 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 140024.99 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 339648.75 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 6 | 266893.32 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 5 | 179974.74 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 5 | 118179.23 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 179016.28 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 6 | 183153.67 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.0 | None | None | None | 1 | 4835.64 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 6 | 118902.22 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 0.9 | 0.9 | 0.8 | True | 1.0 | 3 | 190470.18 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 114179.97 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 6 | 136577.0 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 5 | 124147.38 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.6 | 0.4 | True | 0.75 | 1 | 120810.89 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 0.6 | 0.4 | 0.2 | True | 1.0 | 7 | 114558.29 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 3 | 133435.98 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 150212.31 |  |
