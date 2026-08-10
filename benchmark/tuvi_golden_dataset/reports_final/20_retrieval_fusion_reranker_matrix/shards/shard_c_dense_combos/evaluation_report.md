# W6 Evaluation report: w8_abl_01_retrieval_fusion_reranker_v2_shard_c_dense_combos

- Dataset: `D:\Study\text mining\main\tuvi-battu-graphrag\benchmark\tuvi_golden_dataset\release\tuviqa_v1_release.jsonl`
- Dataset items: 100
- Configs: 3
- Judge backend: `gemini`
- Started: 2026-08-10T03:14:42.401464Z
- Completed: 2026-08-10T03:18:48.340961Z
- Notes: Shard C of W8 retrieval/fusion/reranker matrix v2. Contains dense-combination variants. Merge into the canonical 10-config report after all shards complete.
- Run status: `completed`

## Run identity and provenance

- Identity SHA-256: `3084cf5441c697ce88e2200d9ba45889320d4c614728216082c0d8a63eb07ce2`
- Dataset SHA-256: `90376a87cec29cc22e93dc71b41e054ed2f0183bc515a52aa461fecd43cc008c`
- Manifest SHA-256: `3e51db65e88945b53a18851d493c1fa59e5b9e34a7f2e4b6d7723a746646f338`
- Evaluator SHA-256: `47e83febfb2247a151d91605f72ead40dc0ec7f9044194eabd5038d75d74c435`
- Git SHA: `957d35f124e51916215c6b4a64fd5d35d7e66ec7`
- Git dirty: `False`
- Judge model: `gemini-3.1-flash-lite-preview`
- Checkpoint: `benchmark\tuvi_golden_dataset\reports_final\20_retrieval_fusion_reranker_matrix\shards\shard_c_dense_combos\checkpoints\evaluation_checkpoint.json`

## Execution completeness

- Expected pairs: 300
- Completed pairs: 300
- Failed pairs: 0
- Executed pairs: 1
- Resumed pairs: 299

> **Metric policy:** W6-EVAL-02 runs the RAG pipeline directly with the selected `ExperimentConfig`. `Context recall` is the Gemini-judged corpus-grounding score for non-Direct items; Direct/chart-only items are excluded from corpus retrieval/citation metrics and reported through `chart_context_grounding`.

## Overall metrics

| Config | Status | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms | Retrieval p95 ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| dense_sparse_rrf | completed | 100 | 0.902 | 0.818 | 0.7418 | 0.0 | 0.989 | 226613.43 | 221270.99 |
| graph_dense_rrf | completed | 100 | 0.912 | 0.837 | 0.7593 | 0.967 | 0.989 | 72032.09 | 67813.93 |
| all_paths_planner_dense_rrf | completed | 100 | 0.88 | 0.801 | 0.7253 | 0.967 | 0.989 | 254152.13 | 249658.28 |

## Failure and fallback summary

| Config | Failed | Generation backend fallback | Judge failure | No context | Retrieval backend fallback | Citation fallback |
|---|---:|---:|---:|---:|---:|---:|
| dense_sparse_rrf | 0 | 0 | 0 | 0 | 0 | 0 |
| graph_dense_rrf | 0 | 0 | 0 | 0 | 0 | 0 |
| all_paths_planner_dense_rrf | 0 | 0 | 0 | 0 | 0 | 1 |

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
| 2 | dense_sparse_rrf | 0.7418 |
| 3 | all_paths_planner_dense_rrf | 0.7253 |

### Citation coverage ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | dense_sparse_rrf | 0.989 |
| 2 | graph_dense_rrf | 0.989 |
| 3 | all_paths_planner_dense_rrf | 0.989 |

### Graph hit ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | graph_dense_rrf | 0.967 |
| 2 | all_paths_planner_dense_rrf | 0.967 |
| 3 | dense_sparse_rrf | 0.0 |

### p95 latency ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | graph_dense_rrf | 72032.09 |
| 2 | dense_sparse_rrf | 226613.43 |
| 3 | all_paths_planner_dense_rrf | 254152.13 |

### Retrieval miss summary

| Config | Miss count | Example item IDs |
|---|---:|---|
| dense_sparse_rrf | 13 | TVQA-008, TVQA-010, TVQA-027, TVQA-028, TVQA-038 |
| graph_dense_rrf | 9 | TVQA-027, TVQA-032, TVQA-038, TVQA-045, TVQA-061 |
| all_paths_planner_dense_rrf | 18 | TVQA-010, TVQA-017, TVQA-025, TVQA-027, TVQA-028 |

### Rerank miss summary

| Config | Miss count | Example item IDs |
|---|---:|---|
| dense_sparse_rrf | 1 | TVQA-068 |
| graph_dense_rrf | 1 | TVQA-084 |
| all_paths_planner_dense_rrf | 1 | TVQA-068 |

## Metrics by question complexity

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dense_sparse_rrf | Direct | 10 | 1.0 | 0.83 | 0.7 | 0.0 | 0.0 | 8984.52 |
| dense_sparse_rrf | One-hop | 46 | 0.9022 | 0.8326 | 0.7783 | 0.0 | 1.0 | 211654.26 |
| dense_sparse_rrf | Two-hop | 44 | 0.8795 | 0.8 | 0.7045 | 0.0 | 1.0 | 238530.38 |
| graph_dense_rrf | Direct | 10 | 1.0 | 0.84 | 0.7 | 0.0 | 0.0 | 3881.42 |
| graph_dense_rrf | One-hop | 46 | 0.9109 | 0.8696 | 0.7957 | 0.9783 | 1.0 | 72155.94 |
| graph_dense_rrf | Two-hop | 44 | 0.8932 | 0.8023 | 0.7227 | 0.9773 | 1.0 | 70058.17 |
| all_paths_planner_dense_rrf | Direct | 10 | 1.0 | 0.83 | 0.8 | 0.0 | 0.0 | 4318.84 |
| all_paths_planner_dense_rrf | One-hop | 46 | 0.887 | 0.8174 | 0.7717 | 0.9783 | 1.0 | 253331.75 |
| all_paths_planner_dense_rrf | Two-hop | 44 | 0.8455 | 0.7773 | 0.675 | 0.9773 | 1.0 | 254786.17 |

## Metrics by question family

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
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

## Per-question results

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
