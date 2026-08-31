# W6 Evaluation report: local_llm_gemini_judge_final_2x3

- Dataset: `benchmark/tuvi_golden_dataset/release/tuviqa_v1_release.jsonl`
- Dataset items: 100
- Configs: 6
- Judge backend: `gemini`
- Started: 2026-08-31T04:07:39.879451+00:00
- Completed: 2026-08-31T07:58:58.993333+00:00
- Notes: Merged three complete B/C/D judge shards. No Gemini API calls occur during merge; all per-item records were produced by the canonical repository evaluator.
- Run status: `completed`

## Run identity and provenance

- Identity SHA-256: `ccb7abd3a29bb213b9a8196d157812afa1234933975fb2fa2f1a2cb0a4f2684c`
- Dataset SHA-256: `90376a87cec29cc22e93dc71b41e054ed2f0183bc515a52aa461fecd43cc008c`
- Manifest SHA-256: `e12eba5d7273514ec797bf4f509233a4069df0e4f43a0a63cb39b1a3a31f7a0a`
- Evaluator SHA-256: `856f6351c93f605ee37cd26af18d847dd040de8b93fae163398526a423939659`
- Git SHA: `81c1f950f071e3eb75fb2adb0623483158ab5833`
- Git dirty: `True`
- Judge model: `gemini-3.1-flash-lite-preview`
- Checkpoint: `benchmark/tuvi_golden_dataset/reports_final/60_local_llm_ablation/checkpoints/evaluation_checkpoint.json`

## Execution completeness

- Expected pairs: 600
- Completed pairs: 600
- Failed pairs: 0
- Executed pairs: 0
- Resumed pairs: 600

> **Metric policy:** W6-EVAL-02 runs the RAG pipeline directly with the selected `ExperimentConfig`. `Context recall` is the Gemini-judged corpus-grounding score for non-Direct items; Direct/chart-only items are excluded from corpus retrieval/citation metrics and reported through `chart_context_grounding`.

## Overall metrics

| Config | Status | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms | Retrieval p95 ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| qwen25_7b__graph_dense_rrf | completed | 100 | 0.574 | 0.63 | 0.5179 | 0.967 | 0.989 | 90062.85 | 84919.2 |
| qwen25_7b__semantic_gs_rrf_no_rerank_reference | completed | 100 | 0.597 | 0.645 | 0.5363 | 0.4286 | 0.989 | 16343.85 | 9353.66 |
| qwen25_7b__semantic_gs_rrf_rerank_k40 | completed | 100 | 0.607 | 0.642 | 0.5549 | 0.4286 | 0.989 | 192338.4 | 185842.75 |
| gemma3_4b__graph_dense_rrf | completed | 100 | 0.625 | 0.654 | 0.5538 | 0.967 | 0.9643 | 98554.09 | 84919.2 |
| gemma3_4b__semantic_gs_rrf_no_rerank_reference | completed | 100 | 0.626 | 0.633 | 0.544 | 0.4286 | 0.989 | 27546.26 | 9353.66 |
| gemma3_4b__semantic_gs_rrf_rerank_k40 | completed | 100 | 0.631 | 0.627 | 0.544 | 0.4286 | 0.9835 | 201114.43 | 185842.75 |

## Failure and fallback summary

| Config | Failed | Generation backend fallback | Judge failure | No context | Retrieval backend fallback | Citation fallback |
|---|---:|---:|---:|---:|---:|---:|
| qwen25_7b__graph_dense_rrf | 0 | 0 | 0 | 0 | 0 | 8 |
| qwen25_7b__semantic_gs_rrf_no_rerank_reference | 0 | 0 | 0 | 0 | 0 | 5 |
| qwen25_7b__semantic_gs_rrf_rerank_k40 | 0 | 0 | 0 | 0 | 0 | 7 |
| gemma3_4b__graph_dense_rrf | 0 | 0 | 0 | 0 | 0 | 0 |
| gemma3_4b__semantic_gs_rrf_no_rerank_reference | 0 | 0 | 0 | 0 | 0 | 2 |
| gemma3_4b__semantic_gs_rrf_rerank_k40 | 0 | 0 | 0 | 0 | 0 | 1 |

## Metrics by question complexity

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| qwen25_7b__graph_dense_rrf | Direct | 10 | 0.78 | 0.71 | 0.5 | 0.0 | 0.0 | 6346.01 |
| qwen25_7b__graph_dense_rrf | One-hop | 46 | 0.5435 | 0.5957 | 0.4963 | 0.9783 | 1.0 | 89772.03 |
| qwen25_7b__graph_dense_rrf | Two-hop | 44 | 0.5591 | 0.6477 | 0.5409 | 0.9773 | 1.0 | 95355.04 |
| qwen25_7b__semantic_gs_rrf_no_rerank_reference | Direct | 10 | 0.8 | 0.68 | 0.5 | 0.0 | 0.0 | 6566.78 |
| qwen25_7b__semantic_gs_rrf_no_rerank_reference | One-hop | 46 | 0.5717 | 0.6457 | 0.55 | 0.4348 | 1.0 | 14264.37 |
| qwen25_7b__semantic_gs_rrf_no_rerank_reference | Two-hop | 44 | 0.5773 | 0.6364 | 0.5227 | 0.4318 | 1.0 | 17692.22 |
| qwen25_7b__semantic_gs_rrf_rerank_k40 | Direct | 10 | 0.8 | 0.64 | 0.5 | 0.0 | 0.0 | 6308.51 |
| qwen25_7b__semantic_gs_rrf_rerank_k40 | One-hop | 46 | 0.6196 | 0.6717 | 0.5913 | 0.3478 | 1.0 | 189514.23 |
| qwen25_7b__semantic_gs_rrf_rerank_k40 | Two-hop | 44 | 0.55 | 0.6114 | 0.5182 | 0.5227 | 1.0 | 197061.73 |
| gemma3_4b__graph_dense_rrf | Direct | 10 | 0.81 | 0.69 | 0.5 | 0.0 | 0.0 | 15929.21 |
| gemma3_4b__graph_dense_rrf | One-hop | 46 | 0.5957 | 0.6283 | 0.5457 | 0.9783 | 0.9674 | 97639.96 |
| gemma3_4b__graph_dense_rrf | Two-hop | 44 | 0.6136 | 0.6727 | 0.5636 | 0.9773 | 0.983 | 102067.94 |
| gemma3_4b__semantic_gs_rrf_no_rerank_reference | Direct | 10 | 0.83 | 0.67 | 0.6 | 0.0 | 0.0 | 15887.0 |
| gemma3_4b__semantic_gs_rrf_no_rerank_reference | One-hop | 46 | 0.6957 | 0.6652 | 0.6174 | 0.4348 | 1.0 | 23824.77 |
| gemma3_4b__semantic_gs_rrf_no_rerank_reference | Two-hop | 44 | 0.5068 | 0.5909 | 0.4659 | 0.4318 | 1.0 | 29422.25 |
| gemma3_4b__semantic_gs_rrf_rerank_k40 | Direct | 10 | 0.85 | 0.66 | 0.5 | 0.0 | 0.0 | 15766.45 |
| gemma3_4b__semantic_gs_rrf_rerank_k40 | One-hop | 46 | 0.613 | 0.6261 | 0.5435 | 0.3478 | 0.9946 | 199320.57 |
| gemma3_4b__semantic_gs_rrf_rerank_k40 | Two-hop | 44 | 0.6 | 0.6205 | 0.5455 | 0.5227 | 0.9943 | 207232.3 |

## Metrics by question family

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| qwen25_7b__graph_dense_rrf | core_identity | 10 | 0.78 | 0.71 | 0.5 | 0.0 | 0.0 | 6346.01 |
| qwen25_7b__graph_dense_rrf | dai_van_interpretation | 10 | 0.32 | 0.42 | 0.31 | 1.0 | 1.0 | 77487.71 |
| qwen25_7b__graph_dense_rrf | menh_cuc_relation | 10 | 0.3 | 0.36 | 0.263 | 1.0 | 1.0 | 55136.06 |
| qwen25_7b__graph_dense_rrf | menh_house_interpretation | 10 | 0.62 | 0.62 | 0.53 | 0.9 | 1.0 | 107753.01 |
| qwen25_7b__graph_dense_rrf | menh_tam_hop | 10 | 0.56 | 0.65 | 0.5 | 1.0 | 1.0 | 2660754.79 |
| qwen25_7b__graph_dense_rrf | menh_xung_chieu | 10 | 0.52 | 0.54 | 0.45 | 1.0 | 1.0 | 79670.49 |
| qwen25_7b__graph_dense_rrf | special_state_interpretation | 10 | 0.64 | 0.72 | 0.57 | 1.0 | 1.0 | 78248.86 |
| qwen25_7b__graph_dense_rrf | synthesis_judgement | 10 | 0.64 | 0.73 | 0.61 | 0.9 | 1.0 | 71101.7 |
| qwen25_7b__graph_dense_rrf | than_cu_interpretation | 10 | 0.68 | 0.77 | 0.69 | 1.0 | 1.0 | 85521.32 |
| qwen25_7b__graph_dense_rrf | topic_house_plus_relations | 10 | 0.68 | 0.78 | 0.74 | 1.0 | 1.0 | 60739.21 |
| qwen25_7b__semantic_gs_rrf_no_rerank_reference | core_identity | 10 | 0.8 | 0.68 | 0.5 | 0.0 | 0.0 | 6566.78 |
| qwen25_7b__semantic_gs_rrf_no_rerank_reference | dai_van_interpretation | 10 | 0.42 | 0.5 | 0.42 | 0.9 | 1.0 | 14467.8 |
| qwen25_7b__semantic_gs_rrf_no_rerank_reference | menh_cuc_relation | 10 | 0.41 | 0.52 | 0.53 | 0.4 | 1.0 | 11976.26 |
| qwen25_7b__semantic_gs_rrf_no_rerank_reference | menh_house_interpretation | 10 | 0.62 | 0.64 | 0.53 | 0.6 | 1.0 | 15236.23 |
| qwen25_7b__semantic_gs_rrf_no_rerank_reference | menh_tam_hop | 10 | 0.56 | 0.6 | 0.48 | 0.3 | 1.0 | 16201.91 |
| qwen25_7b__semantic_gs_rrf_no_rerank_reference | menh_xung_chieu | 10 | 0.46 | 0.5 | 0.38 | 0.6 | 1.0 | 16807.19 |
| qwen25_7b__semantic_gs_rrf_no_rerank_reference | special_state_interpretation | 10 | 0.62 | 0.7 | 0.54 | 0.1 | 1.0 | 14331.18 |
| qwen25_7b__semantic_gs_rrf_no_rerank_reference | synthesis_judgement | 10 | 0.68 | 0.73 | 0.55 | 0.5 | 1.0 | 19153.8 |
| qwen25_7b__semantic_gs_rrf_no_rerank_reference | than_cu_interpretation | 10 | 0.7 | 0.77 | 0.65 | 0.4 | 1.0 | 13946.02 |
| qwen25_7b__semantic_gs_rrf_no_rerank_reference | topic_house_plus_relations | 10 | 0.7 | 0.81 | 0.75 | 0.1 | 1.0 | 15150.77 |
| qwen25_7b__semantic_gs_rrf_rerank_k40 | core_identity | 10 | 0.8 | 0.64 | 0.5 | 0.0 | 0.0 | 6308.51 |
| qwen25_7b__semantic_gs_rrf_rerank_k40 | dai_van_interpretation | 10 | 0.44 | 0.52 | 0.37 | 0.8 | 1.0 | 144731.6 |
| qwen25_7b__semantic_gs_rrf_rerank_k40 | menh_cuc_relation | 10 | 0.53 | 0.62 | 0.56 | 0.3 | 1.0 | 118956.35 |
| qwen25_7b__semantic_gs_rrf_rerank_k40 | menh_house_interpretation | 10 | 0.6 | 0.57 | 0.51 | 0.4 | 1.0 | 209895.89 |
| qwen25_7b__semantic_gs_rrf_rerank_k40 | menh_tam_hop | 10 | 0.58 | 0.62 | 0.53 | 0.6 | 1.0 | 192468.91 |
| qwen25_7b__semantic_gs_rrf_rerank_k40 | menh_xung_chieu | 10 | 0.44 | 0.48 | 0.41 | 0.4 | 1.0 | 170216.48 |
| qwen25_7b__semantic_gs_rrf_rerank_k40 | special_state_interpretation | 10 | 0.7 | 0.78 | 0.68 | 0.1 | 1.0 | 166887.38 |
| qwen25_7b__semantic_gs_rrf_rerank_k40 | synthesis_judgement | 10 | 0.6 | 0.66 | 0.51 | 0.6 | 1.0 | 241827.41 |
| qwen25_7b__semantic_gs_rrf_rerank_k40 | than_cu_interpretation | 10 | 0.68 | 0.73 | 0.69 | 0.4 | 1.0 | 189247.33 |
| qwen25_7b__semantic_gs_rrf_rerank_k40 | topic_house_plus_relations | 10 | 0.7 | 0.8 | 0.74 | 0.3 | 1.0 | 186742.41 |
| gemma3_4b__graph_dense_rrf | core_identity | 10 | 0.81 | 0.69 | 0.5 | 0.0 | 0.0 | 15929.21 |
| gemma3_4b__graph_dense_rrf | dai_van_interpretation | 10 | 0.42 | 0.43 | 0.36 | 1.0 | 0.975 | 84300.93 |
| gemma3_4b__graph_dense_rrf | menh_cuc_relation | 10 | 0.41 | 0.45 | 0.34 | 1.0 | 1.0 | 64163.2 |
| gemma3_4b__graph_dense_rrf | menh_house_interpretation | 10 | 0.58 | 0.58 | 0.51 | 0.9 | 0.9 | 116289.59 |
| gemma3_4b__graph_dense_rrf | menh_tam_hop | 10 | 0.46 | 0.54 | 0.44 | 1.0 | 0.975 | 2668670.52 |
| gemma3_4b__graph_dense_rrf | menh_xung_chieu | 10 | 0.58 | 0.59 | 0.47 | 1.0 | 0.975 | 85428.75 |
| gemma3_4b__graph_dense_rrf | special_state_interpretation | 10 | 0.68 | 0.8 | 0.67 | 1.0 | 0.975 | 85886.75 |
| gemma3_4b__graph_dense_rrf | synthesis_judgement | 10 | 0.76 | 0.85 | 0.68 | 0.9 | 1.0 | 81387.93 |
| gemma3_4b__graph_dense_rrf | than_cu_interpretation | 10 | 0.77 | 0.79 | 0.77 | 1.0 | 1.0 | 90224.93 |
| gemma3_4b__graph_dense_rrf | topic_house_plus_relations | 10 | 0.78 | 0.82 | 0.75 | 1.0 | 0.975 | 68178.87 |
| gemma3_4b__semantic_gs_rrf_no_rerank_reference | core_identity | 10 | 0.83 | 0.67 | 0.6 | 0.0 | 0.0 | 15887.0 |
| gemma3_4b__semantic_gs_rrf_no_rerank_reference | dai_van_interpretation | 10 | 0.52 | 0.49 | 0.41 | 0.9 | 1.0 | 23325.19 |
| gemma3_4b__semantic_gs_rrf_no_rerank_reference | menh_cuc_relation | 10 | 0.76 | 0.67 | 0.69 | 0.4 | 1.0 | 24247.82 |
| gemma3_4b__semantic_gs_rrf_no_rerank_reference | menh_house_interpretation | 10 | 0.7 | 0.62 | 0.57 | 0.6 | 1.0 | 27336.9 |
| gemma3_4b__semantic_gs_rrf_no_rerank_reference | menh_tam_hop | 10 | 0.36 | 0.42 | 0.29 | 0.3 | 1.0 | 27917.58 |
| gemma3_4b__semantic_gs_rrf_no_rerank_reference | menh_xung_chieu | 10 | 0.43 | 0.52 | 0.35 | 0.6 | 1.0 | 24579.42 |
| gemma3_4b__semantic_gs_rrf_no_rerank_reference | special_state_interpretation | 10 | 0.66 | 0.76 | 0.65 | 0.1 | 1.0 | 20911.1 |
| gemma3_4b__semantic_gs_rrf_no_rerank_reference | synthesis_judgement | 10 | 0.64 | 0.72 | 0.55 | 0.5 | 1.0 | 30431.71 |
| gemma3_4b__semantic_gs_rrf_no_rerank_reference | than_cu_interpretation | 10 | 0.72 | 0.76 | 0.72 | 0.4 | 1.0 | 23313.44 |
| gemma3_4b__semantic_gs_rrf_no_rerank_reference | topic_house_plus_relations | 10 | 0.64 | 0.7 | 0.66 | 0.1 | 1.0 | 27368.99 |
| gemma3_4b__semantic_gs_rrf_rerank_k40 | core_identity | 10 | 0.85 | 0.66 | 0.5 | 0.0 | 0.0 | 15766.45 |
| gemma3_4b__semantic_gs_rrf_rerank_k40 | dai_van_interpretation | 10 | 0.54 | 0.48 | 0.42 | 0.8 | 1.0 | 154914.92 |
| gemma3_4b__semantic_gs_rrf_rerank_k40 | menh_cuc_relation | 10 | 0.61 | 0.53 | 0.53 | 0.3 | 1.0 | 128570.3 |
| gemma3_4b__semantic_gs_rrf_rerank_k40 | menh_house_interpretation | 10 | 0.46 | 0.54 | 0.43 | 0.4 | 1.0 | 218658.76 |
| gemma3_4b__semantic_gs_rrf_rerank_k40 | menh_tam_hop | 10 | 0.48 | 0.46 | 0.35 | 0.6 | 1.0 | 202530.87 |
| gemma3_4b__semantic_gs_rrf_rerank_k40 | menh_xung_chieu | 10 | 0.48 | 0.52 | 0.42 | 0.4 | 1.0 | 178034.87 |
| gemma3_4b__semantic_gs_rrf_rerank_k40 | special_state_interpretation | 10 | 0.73 | 0.75 | 0.61 | 0.1 | 0.975 | 171689.08 |
| gemma3_4b__semantic_gs_rrf_rerank_k40 | synthesis_judgement | 10 | 0.66 | 0.75 | 0.62 | 0.6 | 0.975 | 249672.89 |
| gemma3_4b__semantic_gs_rrf_rerank_k40 | than_cu_interpretation | 10 | 0.74 | 0.82 | 0.73 | 0.4 | 1.0 | 198219.36 |
| gemma3_4b__semantic_gs_rrf_rerank_k40 | topic_house_plus_relations | 10 | 0.76 | 0.76 | 0.79 | 0.3 | 1.0 | 191351.07 |

## Per-question results

### qwen25_7b__graph_dense_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 6602.51 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.9 | 1.0 | True | 1.0 | 3 | 130507.99 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 0.8 | 1.0 | 1.0 | True | 1.0 | 3 | 89939.4 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 0.2 | 0.4 | 0.6 | True | 1.0 | 2 | 59317.06 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 3 | 89269.92 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 2 | 114413.98 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.9 | True | 1.0 | 4 | 98752.91 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 0.2 | 0.2 | 0.2 | True | 1.0 | 1 | 92408.42 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.9 | 0.8 | True | 1.0 | 4 | 66325.16 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.2 | 0.5 | 0.2 | True | 1.0 | 2 | 64992.14 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4622.15 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.6 | 0.5 | True | 1.0 | 2 | 79941.37 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 2 | 80121.44 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 0.6 | 0.5 | 0.0 | True | 1.0 | 1 | 49288.19 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.2 | 0.4 | 0.2 | True | 1.0 | 3 | 64778.68 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 4 | 4744124.54 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 1 | 26291.25 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 0.2 | 0.4 | 0.2 | True | 1.0 | 8 | 35115.01 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 0.2 | 0.5 | 0.2 | True | 1.0 | 2 | 44148.31 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 0.8 | 1.0 | 1.0 | True | 1.0 | 4 | 59724.62 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 2416.72 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 0.6 | 0.8 | 0.5 | True | 1.0 | 2 | 60545.27 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 0.6 | 0.7 | 0.5 | True | 1.0 | 4 | 56061.24 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 0.0 | 0.2 | 0.0 | True | 1.0 | 3 | 44096.55 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 0.2 | 0.4 | 0.2 | True | 1.0 | 4 | 55230.06 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 0.4 | 0.6 | 0.5 | True | 1.0 | 3 | 66280.64 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.2 | 0.4 | 0.2 | True | 1.0 | 3 | 44506.39 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.2 | 0.4 | 0.3 | True | 1.0 | 2 | 48561.66 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.9 | 0.9 | True | 1.0 | 2 | 53397.41 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 0.6 | 0.8 | 0.7 | True | 1.0 | 1 | 76100.44 |  |
| TVQA-031 | completed | Direct | core_identity | True | 0.0 | 0.0 | None | None | None | 1 | 2737.11 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.3 | 0.2 | True | 1.0 | 6 | 60946.5 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 0.8 | 1.0 | 1.0 | True | 1.0 | 2 | 41646.66 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 0.4 | 0.6 | 0.8 | True | 1.0 | 4 | 44884.74 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 3 | 56517.02 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 0.6 | 0.8 | 0.5 | True | 1.0 | 6 | 69156.43 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.8 | True | 1.0 | 2 | 56347.53 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 0.0 | 0.5 | 0.0 | True | 1.0 | 1 | 51500.61 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.2 | 0.3 | 0.2 | True | 1.0 | 9 | 49184.32 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 9 | 45715.48 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 2821.04 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 0.4 | 0.6 | 0.2 | True | 1.0 | 2 | 42976.08 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 0.8 | 1.0 | 1.0 | True | 1.0 | 4 | 45379.19 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 2 | 38007.34 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 0.2 | 0.6 | 0.0 | True | 1.0 | 3 | 48766.69 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 0.6 | 0.8 | 0.7 | True | 1.0 | 1 | 42833.77 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.4 | 0.3 | 0.2 | True | 1.0 | 2 | 51846.06 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 0.2 | 0.4 | 0.3 | True | 1.0 | 2 | 51826.61 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 1.0 | 1.0 | True | 1.0 | 2 | 34843.63 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 61473.12 |  |
| TVQA-051 | completed | Direct | core_identity | True | 0.0 | 0.0 | None | None | None | 1 | 4229.85 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.1 | 0.2 | True | 1.0 | 2 | 56888.63 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 0.2 | 0.5 | 0.3 | True | 1.0 | 3 | 49228.73 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 1 | 41971.38 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 58567.95 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 0.4 | 0.8 | 0.5 | True | 1.0 | 3 | 43859.73 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 1.0 | True | 1.0 | 3 | 45517.99 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 0.2 | 0.2 | 0.2 | True | 1.0 | 1 | 59251.28 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 0.6 | 0.4 | 0.3 | True | 1.0 | 4 | 53911.93 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 0.2 | 0.2 | 0.2 | True | 1.0 | 2 | 58190.79 |  |
| TVQA-061 | completed | Direct | core_identity | False | 0.8 | 0.6 | 0.5 | False | 0.0 | 1 | 3822.79 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 0.6 | 0.8 | 0.7 | True | 1.0 | 2 | 38880.18 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 2 | 61067.94 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 0.2 | 0.5 | 0.33 | True | 1.0 | 2 | 46835.94 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 40556.32 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 1 | 43824.41 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 0.2 | 0.2 | 0.2 | True | 1.0 | 3 | 39032.57 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.8 | 1.0 | True | 1.0 | 2 | 39212.56 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.9 | 1.0 | True | 1.0 | 5 | 40411.11 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 0.8 | 1.0 | 1.0 | True | 1.0 | 2 | 34096.31 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 6032.5 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.6 | 0.7 | True | 1.0 | 3 | 47852.9 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 0.8 | 1.0 | 1.0 | True | 1.0 | 4 | 59631.87 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 0.2 | 0.2 | 0.3 | True | 1.0 | 1 | 35301.97 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 0.6 | 0.8 | 0.7 | True | 1.0 | 2 | 43874.94 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 0.2 | 0.3 | 0.2 | True | 1.0 | 1 | 51889.67 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 0.2 | 0.3 | 0.2 | True | 1.0 | 2 | 43204.92 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 0.2 | 0.4 | 0.2 | True | 1.0 | 9 | 50355.14 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 1.0 | 1.0 | True | 1.0 | 3 | 41130.49 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 0.6 | 0.4 | 0.2 | True | 1.0 | 2 | 45524.72 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4393.55 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 0.4 | 0.5 | 0.3 | False | 1.0 | 1 | 21835.37 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 3 | 60852.89 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 0.2 | 0.2 | 0.0 | True | 1.0 | 1 | 33140.01 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 53272.1 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 1.0 | True | 1.0 | 1 | 55660.88 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 9 | 42758.69 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 1 | 47911.96 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 47527.21 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 0.6 | 0.8 | 0.5 | False | 1.0 | 2 | 24672.49 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.5 | None | None | None | 1 | 4768.87 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 44409.37 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 0.4 | 0.6 | 0.5 | True | 1.0 | 1 | 57052.85 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 0.2 | 0.2 | 0.0 | True | 1.0 | 2 | 50025.94 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 0.8 | True | 1.0 | 4 | 51683.19 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 0.2 | 0.2 | 0.0 | True | 1.0 | 2 | 43093.12 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.2 | 0.3 | 0.2 | True | 1.0 | 1 | 44770.72 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 0.2 | 0.3 | 0.2 | True | 1.0 | 1 | 44207.87 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.9 | 1.0 | True | 1.0 | 2 | 45663.86 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 52069.67 |  |

### qwen25_7b__semantic_gs_rrf_no_rerank_reference

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 6552.32 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.9 | 1.0 | False | 1.0 | 2 | 11120.15 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 0.8 | 1.0 | 1.0 | True | 1.0 | 2 | 11637.24 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 0.6 | 0.8 | 1.0 | False | 1.0 | 2 | 10234.93 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 0.6 | 0.8 | 0.5 | False | 1.0 | 4 | 11726.44 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 3 | 13788.82 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.8 | True | 1.0 | 3 | 12706.64 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 0.2 | 0.2 | 0.2 | True | 1.0 | 3 | 14369.04 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.9 | 1.0 | True | 1.0 | 3 | 12263.45 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.8 | 0.5 | True | 1.0 | 2 | 12417.37 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4585.8 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 0.4 | 0.6 | 0.5 | True | 1.0 | 7 | 13896.11 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.6 | 0.5 | False | 1.0 | 2 | 12097.27 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 0.5 | 0.8 | 0.5 | False | 1.0 | 2 | 9237.03 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 4 | 10572.21 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 0.6 | 0.4 | 0.3 | False | 1.0 | 3 | 14465.31 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.2 | 0.2 | 0.0 | False | 1.0 | 4 | 10030.04 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 0.4 | 0.5 | 0.2 | True | 1.0 | 2 | 13017.22 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 1.0 | 1.0 | False | 1.0 | 2 | 14343.45 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 0.8 | 1.0 | 1.0 | True | 1.0 | 3 | 13020.82 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 2398.16 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 0.6 | 0.8 | 0.7 | True | 1.0 | 3 | 12952.29 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 3 | 13090.83 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 0.2 | 0.4 | 0.6 | False | 1.0 | 2 | 11232.63 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 0.2 | 0.2 | 0.2 | False | 1.0 | 3 | 11013.29 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 0.6 | 0.7 | 0.5 | False | 1.0 | 3 | 14758.58 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.2 | 0.4 | 0.2 | True | 1.0 | 9 | 15120.56 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.2 | 0.3 | 0.2 | True | 1.0 | 1 | 14345.64 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 2 | 15811.3 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 3 | 20186.25 |  |
| TVQA-031 | completed | Direct | core_identity | True | 0.0 | 0.0 | None | None | None | 1 | 2713.65 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.4 | 0.3 | 0.2 | True | 1.0 | 4 | 16332.7 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 3 | 10465.28 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 0.2 | 0.3 | 0.2 | False | 1.0 | 4 | 12482.28 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 1.0 | False | 1.0 | 6 | 12836.87 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 0.2 | 0.4 | 0.3 | False | 1.0 | 3 | 15763.53 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 1 | 14517.26 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 0.2 | 0.2 | 0.0 | True | 1.0 | 1 | 14548.61 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.2 | 0.4 | 0.2 | False | 1.0 | 1 | 13218.79 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 0.6 | 0.8 | 0.5 | False | 1.0 | 2 | 12446.89 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 2795.2 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 0.6 | 0.8 | 0.5 | False | 1.0 | 1 | 11914.89 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 0.8 | 1.0 | 1.0 | False | 1.0 | 3 | 12847.32 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 0.0 | 0.2 | 0.0 | False | 1.0 | 2 | 10379.29 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 0.2 | 0.2 | 0.0 | True | 1.0 | 2 | 12876.11 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 1.0 | False | 1.0 | 3 | 16560.58 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.6 | 0.7 | True | 1.0 | 2 | 18187.16 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.9 | 1.0 | True | 1.0 | 9 | 12315.91 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 1.0 | 1.0 | False | 1.0 | 3 | 14136.87 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 0.8 | 1.0 | 0.8 | True | 1.0 | 2 | 17891.92 |  |
| TVQA-051 | completed | Direct | core_identity | True | 0.0 | 0.0 | None | None | None | 1 | 4185.68 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.2 | 0.2 | True | 1.0 | 5 | 13391.54 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 0.0 | 0.5 | 0.0 | False | 1.0 | 2 | 11049.68 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.9 | 1.0 | True | 1.0 | 3 | 10819.22 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 0.8 | 1.0 | 0.6 | False | 1.0 | 3 | 15182.99 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 0.8 | 1.0 | 0.7 | True | 1.0 | 2 | 12204.98 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 0.2 | 0.4 | 0.2 | False | 1.0 | 3 | 12366.38 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 0.2 | 0.2 | 0.2 | True | 1.0 | 1 | 13524.93 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 0.2 | 0.4 | 0.2 | False | 1.0 | 3 | 13296.93 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 0.2 | 0.2 | 0.2 | True | 1.0 | 1 | 16555.67 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 0.6 | 0.5 | False | 0.0 | 1 | 3765.16 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 0.6 | 0.5 | 0.4 | True | 1.0 | 2 | 9398.43 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 0.6 | 0.8 | 0.5 | True | 1.0 | 4 | 11045.38 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 1 | 10338.04 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 4 | 11945.66 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 0.2 | 0.4 | 0.3 | False | 1.0 | 2 | 12010.94 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 0.2 | 0.3 | 0.2 | True | 1.0 | 2 | 12563.63 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 3 | 11298.75 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.9 | 0.8 | False | 1.0 | 1 | 13968.07 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 1 | 12156.28 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 6578.61 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 3 | 11358.29 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 3 | 13950.36 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 0.0 | 0.0 | 0.0 | False | 1.0 | 1 | 9896.81 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 0.4 | 0.6 | 0.2 | False | 1.0 | 3 | 11261.0 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 1 | 13252.59 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 0.4 | 0.3 | 0.2 | True | 1.0 | 2 | 13849.31 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.9 | 0.9 | True | 1.0 | 2 | 13517.2 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 1.0 | False | 1.0 | 2 | 12388.3 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 0.4 | 0.5 | 0.2 | False | 1.0 | 2 | 11641.46 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4371.12 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.6 | 0.4 | False | 1.0 | 1 | 11355.06 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 4 | 12788.56 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 0.6 | 0.5 | 0.4 | True | 1.0 | 2 | 10627.72 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 0.8 | 1.0 | 1.0 | False | 1.0 | 3 | 13290.08 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 0.4 | 0.5 | 0.3 | False | 1.0 | 3 | 15535.45 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 3 | 12924.72 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 0.2 | 0.4 | 0.3 | True | 1.0 | 1 | 12899.55 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 1.0 | 1.0 | False | 1.0 | 3 | 13382.54 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.7 | 0.4 | False | 1.0 | 3 | 12817.22 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.2 | None | None | None | 1 | 4765.41 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.7 | False | 1.0 | 1 | 10396.19 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 0.4 | 0.6 | 0.5 | False | 1.0 | 2 | 13940.71 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 0.2 | 0.4 | 0.6 | True | 1.0 | 2 | 11357.8 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 2 | 12159.69 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 0.4 | 0.3 | 0.2 | True | 1.0 | 9 | 12378.1 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.2 | 0.3 | 0.2 | True | 1.0 | 2 | 13071.95 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 0.2 | 0.4 | 0.2 | True | 1.0 | 3 | 13682.79 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 2 | 13461.18 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 4 | 15113.31 |  |

### qwen25_7b__semantic_gs_rrf_rerank_k40

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 6556.29 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.9 | 1.0 | False | 1.0 | 2 | 124467.72 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 2 | 140433.31 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 1.0 | False | 1.0 | 2 | 97581.49 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 3 | 152320.42 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 1 | 197947.35 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.8 | True | 1.0 | 3 | 154201.58 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 0.4 | 0.3 | 0.2 | True | 1.0 | 3 | 150830.19 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.9 | 1.0 | False | 1.0 | 3 | 146618.27 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.2 | 0.4 | 0.2 | True | 1.0 | 1 | 144894.36 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 5216.42 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.4 | 0.5 | True | 1.0 | 2 | 185876.73 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 9 | 179777.26 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.6 | 0.5 | False | 1.0 | 3 | 96168.46 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.2 | 0.3 | 0.2 | False | 1.0 | 3 | 118844.47 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 2 | 172871.16 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.2 | 0.2 | 0.2 | False | 1.0 | 2 | 130890.31 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 0.6 | 0.8 | 0.4 | True | 1.0 | 2 | 136671.33 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 0.2 | 0.2 | 0.4 | False | 1.0 | 2 | 131805.79 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 0.8 | 1.0 | 1.0 | True | 1.0 | 3 | 158023.35 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 2403.66 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.3 | 0.0 | True | 1.0 | 1 | 217504.49 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 1.0 | False | 1.0 | 2 | 161170.81 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 0.5 | 0.5 | 0.5 | False | 1.0 | 1 | 114843.99 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 4 | 152425.72 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 0.2 | 0.3 | 0.4 | True | 1.0 | 2 | 185773.04 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.2 | 0.3 | 0.2 | True | 1.0 | 8 | 137521.39 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.2 | 0.3 | 0.2 | True | 1.0 | 1 | 127683.07 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.9 | 0.8 | False | 1.0 | 5 | 192043.19 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 1 | 261096.91 |  |
| TVQA-031 | completed | Direct | core_identity | True | 0.0 | 0.0 | None | None | None | 1 | 2716.28 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.2 | 0.0 | True | 1.0 | 5 | 200596.5 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 5 | 136529.34 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 0.2 | 0.4 | 0.2 | False | 1.0 | 2 | 113783.04 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 1.0 | False | 1.0 | 8 | 169012.88 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 2 | 183410.68 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 0.4 | 0.6 | 0.5 | False | 1.0 | 2 | 174498.03 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 0.2 | 0.2 | 0.2 | True | 1.0 | 2 | 135952.73 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.2 | 0.4 | 0.2 | True | 1.0 | 1 | 157455.1 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 9 | 146857.65 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 2793.51 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 0.6 | 0.8 | 0.7 | False | 1.0 | 4 | 128052.78 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 0.8 | 1.0 | 1.0 | True | 1.0 | 4 | 136436.34 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 0.6 | 0.8 | 0.5 | False | 1.0 | 2 | 103498.7 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 0.2 | 0.4 | 0.0 | True | 1.0 | 4 | 164289.55 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 2 | 168406.04 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 9 | 164983.48 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 0.4 | 0.6 | 0.3 | True | 1.0 | 2 | 137277.76 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.9 | 1.0 | False | 1.0 | 2 | 129965.06 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 0.2 | 0.6 | 0.4 | False | 1.0 | 2 | 218275.79 |  |
| TVQA-051 | completed | Direct | core_identity | True | 0.0 | 0.0 | None | None | None | 1 | 4189.8 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.1 | 0.0 | True | 1.0 | 2 | 178094.26 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 0.2 | 0.5 | 0.0 | False | 1.0 | 4 | 153205.64 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 110362.48 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 1.0 | False | 1.0 | 3 | 151895.67 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 0.8 | 1.0 | 1.0 | True | 1.0 | 3 | 131772.84 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 3 | 132146.17 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 0.2 | 0.2 | 0.2 | True | 1.0 | 1 | 126984.4 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 1.0 | 0.6 | False | 1.0 | 2 | 133131.8 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 0.2 | 0.4 | 0.2 | True | 1.0 | 2 | 185263.75 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 0.6 | 0.5 | False | 0.0 | 1 | 3794.41 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.7 | 1.0 | False | 1.0 | 1 | 118348.1 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 0.2 | 0.4 | 0.2 | True | 1.0 | 4 | 188513.34 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 0.8 | 1.0 | 1.0 | True | 1.0 | 2 | 119466.56 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 0.8 | 1.0 | 0.8 | False | 1.0 | 4 | 99598.49 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 0.4 | 0.3 | 0.2 | False | 1.0 | 2 | 131962.14 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 0.2 | 0.3 | 0.2 | False | 1.0 | 1 | 123696.91 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 0.8 | 1.0 | 1.0 | False | 1.0 | 2 | 110781.01 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 2 | 140455.93 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 3 | 137686.53 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 6005.67 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 3 | 156077.76 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 0.2 | 0.4 | 0.3 | False | 1.0 | 2 | 189847.86 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 0.2 | 0.4 | 0.8 | False | 1.0 | 5 | 95754.64 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 0.8 | False | 1.0 | 4 | 124615.22 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 0.2 | 0.4 | 0.3 | False | 1.0 | 3 | 184541.92 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 0.2 | 0.3 | 0.4 | True | 1.0 | 1 | 130058.85 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 0.2 | 0.3 | 0.2 | True | 1.0 | 2 | 137096.79 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 1.0 | 1.0 | False | 1.0 | 5 | 145488.53 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 0.6 | 0.5 | 0.4 | True | 1.0 | 3 | 141140.71 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4370.78 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.6 | 0.5 | False | 1.0 | 2 | 170581.71 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.7 | 0.8 | True | 1.0 | 3 | 172505.73 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 0.2 | 0.4 | 0.0 | False | 1.0 | 3 | 97004.61 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 4 | 152844.35 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.8 | False | 1.0 | 4 | 162367.65 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 0.6 | 0.5 | 0.4 | False | 1.0 | 3 | 128412.78 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 9 | 121249.55 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 1.0 | 1.0 | True | 1.0 | 3 | 180263.67 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 0.8 | 1.0 | 0.6 | False | 1.0 | 2 | 185966.02 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.2 | None | None | None | 1 | 4762.84 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 0.6 | 0.8 | 0.7 | False | 1.0 | 3 | 126169.73 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.9 | 1.0 | False | 1.0 | 2 | 185093.21 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 0.2 | 0.6 | 0.5 | True | 1.0 | 2 | 118332.77 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 0.8 | 1.0 | 0.8 | False | 1.0 | 6 | 137383.49 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 0.2 | 0.1 | 0.0 | True | 1.0 | 2 | 126402.12 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.2 | 0.3 | 0.2 | True | 1.0 | 2 | 124143.31 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 0.6 | 0.8 | 0.4 | False | 1.0 | 2 | 113507.82 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.7 | False | 1.0 | 2 | 133495.2 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 2 | 153030.57 |  |

### gemma3_4b__graph_dense_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 14861.98 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.6 | 0.6 | True | 1.0 | 5 | 138965.05 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 0.8 | 1.0 | 1.0 | True | 1.0 | 4 | 95018.88 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.9 | 1.0 | True | 1.0 | 3 | 68559.38 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 1.0 | True | 1.0 | 5 | 98513.66 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 6 | 127512.04 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.9 | True | 1.0 | 6 | 105595.96 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 0.2 | 0.4 | 0.2 | True | 1.0 | 6 | 99322.17 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.9 | 0.8 | True | 1.0 | 5 | 74674.52 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.4 | 0.6 | 0.2 | True | 1.0 | 5 | 80547.13 |  |
| TVQA-011 | completed | Direct | core_identity | True | 0.8 | 1.0 | None | None | None | 1 | 9796.39 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.4 | 0.5 | True | 1.0 | 4 | 88575.15 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 2 | 84365.65 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 0.6 | 0.8 | 0.5 | True | 1.0 | 3 | 56270.15 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.6 | 0.8 | 0.5 | True | 1.0 | 5 | 70453.85 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 0.4 | 0.6 | 0.5 | True | 0.75 | 1 | 4747800.19 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.6 | 0.4 | True | 0.75 | 1 | 32253.46 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.7 | 0.6 | True | 0.75 | 1 | 39040.98 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 1.0 | 1.0 | True | 1.0 | 6 | 53196.42 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 0.8 | 1.0 | 0.9 | True | 1.0 | 6 | 65334.21 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 5491.5 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 0.4 | 0.6 | 0.5 | True | 0.0 | 5 | 70495.05 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.9 | 1.0 | True | 1.0 | 5 | 61356.48 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 0.2 | 0.3 | 0.5 | True | 1.0 | 5 | 52523.53 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 0.4 | 0.5 | 0.2 | True | 0.75 | 1 | 60476.49 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 0.6 | 0.8 | 0.7 | True | 1.0 | 5 | 70969.23 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.2 | 0.3 | 0.2 | True | 1.0 | 2 | 48635.88 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.2 | 0.4 | 0.3 | True | 1.0 | 6 | 60329.31 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.9 | 0.8 | True | 1.0 | 3 | 60239.74 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 3 | 82075.85 |  |
| TVQA-031 | completed | Direct | core_identity | True | 0.5 | 0.8 | None | None | None | 1 | 5106.94 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.2 | 0.0 | True | 1.0 | 5 | 68039.13 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 1.0 | True | 1.0 | 3 | 46776.18 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 0.6 | 0.5 | 0.4 | True | 1.0 | 5 | 52628.52 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 6 | 62118.13 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 0.2 | 0.3 | 0.2 | True | 1.0 | 6 | 80192.97 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 0.6 | 0.8 | 0.5 | True | 1.0 | 3 | 60779.94 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 0.2 | 0.4 | 0.2 | True | 1.0 | 7 | 58267.6 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.4 | 0.5 | 0.2 | True | 1.0 | 3 | 56870.96 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 3 | 52698.97 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 0.5 | None | None | None | 1 | 3797.8 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 0.8 | 1.0 | 0.8 | True | 1.0 | 4 | 50336.16 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 49287.98 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 0.2 | 0.4 | 0.2 | True | 1.0 | 3 | 42447.26 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 0.0 | 0.5 | 0.0 | True | 1.0 | 4 | 59276.85 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 0.2 | 0.4 | 0.3 | True | 1.0 | 4 | 46822.31 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.6 | 0.5 | 0.4 | True | 1.0 | 3 | 57550.59 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 0.6 | 0.4 | 0.3 | True | 1.0 | 5 | 59586.08 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 42909.2 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 0.8 | 1.0 | 1.0 | True | 1.0 | 3 | 67091.21 |  |
| TVQA-051 | completed | Direct | core_identity | True | 0.0 | 0.0 | None | None | None | 1 | 9583.83 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.2 | 0.2 | True | 1.0 | 9 | 63443.25 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 0.5 | 0.8 | 0.4 | True | 1.0 | 4 | 50762.05 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.7 | 0.8 | True | 1.0 | 6 | 48212.46 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 9 | 64305.32 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 48820.09 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 0.6 | 0.8 | 0.8 | True | 1.0 | 6 | 49386.23 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 0.2 | 0.4 | 0.6 | True | 1.0 | 8 | 65941.64 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 59618.02 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 7 | 69046.94 |  |
| TVQA-061 | completed | Direct | core_identity | False | 0.8 | 0.6 | 0.5 | False | 0.0 | 1 | 11893.01 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 7 | 47675.5 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 3 | 65288.67 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 0.5 | 0.4 | 0.0 | True | 1.0 | 4 | 54370.9 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 6 | 47579.85 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 0.2 | 0.3 | 0.2 | True | 1.0 | 7 | 53073.23 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 0.4 | 0.3 | 0.2 | True | 1.0 | 8 | 43739.36 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.6 | 0.5 | True | 1.0 | 4 | 47553.81 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 5 | 46914.94 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 43473.96 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 11853.13 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 6 | 54467.22 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.9 | 1.0 | True | 1.0 | 5 | 67564.1 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 0.0 | 0.2 | 0.0 | True | 1.0 | 3 | 42456.09 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 0.8 | True | 1.0 | 3 | 48973.45 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 0.2 | 0.4 | 0.3 | True | 1.0 | 5 | 60172.21 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 0.6 | 0.7 | 0.5 | True | 1.0 | 5 | 52452.74 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 0.2 | 0.2 | 0.2 | True | 1.0 | 6 | 58701.61 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 43589.4 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 5 | 52072.83 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 16802.4 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.3 | 0.2 | False | 1.0 | 6 | 28222.17 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.9 | 1.0 | True | 1.0 | 6 | 69656.23 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 0.2 | 0.3 | 0.0 | True | 1.0 | 3 | 42506.06 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 0.8 | 1.0 | 1.0 | True | 1.0 | 4 | 57807.6 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 3 | 58768.54 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 5 | 51572.76 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 0.6 | 0.4 | 0.5 | True | 1.0 | 5 | 53720.52 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.6 | 0.7 | True | 1.0 | 4 | 52247.06 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 0.6 | 0.8 | 0.5 | False | 1.0 | 5 | 28075.12 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.0 | None | None | None | 1 | 11603.48 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.9 | 1.0 | True | 1.0 | 5 | 53186.42 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 0.4 | 0.3 | 0.2 | True | 1.0 | 4 | 59812.08 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 0.2 | 0.0 | 0.0 | True | 1.0 | 4 | 58790.1 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 1.0 | True | 1.0 | 7 | 59356.0 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 0.2 | 0.2 | 0.1 | True | 1.0 | 4 | 54197.28 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.4 | 0.3 | 0.2 | True | 1.0 | 3 | 55751.36 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 0.2 | 0.4 | 0.2 | True | 1.0 | 7 | 51024.98 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 0.6 | 0.8 | 0.7 | True | 0.75 | 1 | 55037.15 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.8 | 0.7 | True | 1.0 | 5 | 59952.67 |  |

### gemma3_4b__semantic_gs_rrf_no_rerank_reference

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 14639.61 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.9 | 1.0 | False | 1.0 | 3 | 21826.82 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 20155.62 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 1.0 | False | 1.0 | 3 | 16623.66 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 5 | 16309.06 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.6 | 0.7 | False | 1.0 | 6 | 23126.15 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 1.0 | True | 1.0 | 6 | 18027.87 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 0.4 | 0.3 | 0.2 | True | 1.0 | 7 | 20816.04 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 1.0 | 1.0 | True | 1.0 | 4 | 17216.23 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.2 | 0.4 | 0.2 | True | 1.0 | 5 | 16830.46 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 9919.7 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 0.6 | 0.4 | 0.2 | True | 1.0 | 5 | 19546.5 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.6 | 0.7 | False | 1.0 | 3 | 20525.14 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.9 | 1.0 | False | 1.0 | 4 | 17053.05 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 8 | 19648.3 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 0.2 | 0.6 | 0.4 | False | 1.0 | 6 | 22758.46 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.2 | 0.3 | 0.2 | False | 1.0 | 4 | 20557.01 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 0.6 | 0.4 | 0.2 | True | 1.0 | 4 | 20541.76 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 1.0 | 1.0 | False | 1.0 | 4 | 29817.97 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 0.8 | 1.0 | 1.0 | True | 1.0 | 6 | 22904.08 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 5496.7 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 8 | 23711.39 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 0.8 | 1.0 | 1.0 | False | 1.0 | 6 | 18826.52 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 0.6 | 0.5 | 0.5 | False | 1.0 | 8 | 22323.97 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 0.2 | 0.0 | 0.0 | False | 1.0 | 7 | 18935.73 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 0.6 | 0.4 | 0.2 | False | 1.0 | 9 | 27509.13 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.2 | 0.4 | 0.2 | True | 1.0 | 3 | 21423.96 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.4 | 0.3 | 0.2 | True | 1.0 | 3 | 23540.49 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 0.2 | 0.4 | 0.3 | False | 1.0 | 5 | 23379.94 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 3 | 31088.63 |  |
| TVQA-031 | completed | Direct | core_identity | True | 0.5 | 0.2 | None | None | None | 1 | 5166.53 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.2 | 0.0 | True | 1.0 | 9 | 30303.22 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 3 | 17153.21 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 0.6 | 0.4 | 0.3 | False | 1.0 | 6 | 18528.83 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 1.0 | False | 1.0 | 6 | 19799.63 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 0.2 | 0.4 | 0.3 | False | 1.0 | 6 | 28251.77 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 0.6 | 0.8 | 0.7 | False | 1.0 | 4 | 20906.37 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 0.2 | 0.8 | 0.2 | True | 1.0 | 5 | 21386.67 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.2 | 0.2 | 0.1 | False | 1.0 | 3 | 22713.42 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 0.6 | 0.5 | 0.4 | False | 1.0 | 3 | 18565.67 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 3823.64 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.9 | 1.0 | False | 1.0 | 3 | 20478.08 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 4 | 19987.24 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.6 | 0.4 | False | 1.0 | 5 | 18013.7 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 0.0 | 0.2 | 0.0 | True | 1.0 | 4 | 18209.29 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 0.2 | 0.3 | 0.2 | False | 1.0 | 5 | 23325.49 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.6 | 0.4 | 0.3 | True | 1.0 | 6 | 26395.23 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.9 | 1.0 | True | 1.0 | 6 | 18703.98 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 1.0 | False | 1.0 | 5 | 24375.8 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 0.6 | 1.0 | 0.8 | True | 1.0 | 7 | 29628.81 |  |
| TVQA-051 | completed | Direct | core_identity | True | 0.0 | 0.0 | None | None | None | 1 | 9608.17 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.1 | 0.2 | True | 1.0 | 6 | 21476.61 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 0.0 | 0.2 | 0.0 | False | 1.0 | 7 | 20013.09 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 8 | 19588.82 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 0.8 | 1.0 | 1.0 | False | 1.0 | 5 | 20822.48 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 0.4 | 0.6 | 0.2 | True | 1.0 | 5 | 19253.51 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 0.2 | 0.4 | 0.0 | False | 1.0 | 4 | 19542.18 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 0.2 | 0.4 | 0.6 | True | 1.0 | 7 | 19428.27 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 5 | 22183.91 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 0.2 | 0.4 | 0.2 | True | 1.0 | 2 | 25160.05 |  |
| TVQA-061 | completed | Direct | core_identity | False | 0.8 | 0.7 | 0.6 | False | 0.0 | 1 | 12408.05 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 16201.78 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 0.2 | 0.3 | 0.2 | True | 1.0 | 5 | 19538.39 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 25323.69 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 5 | 18264.92 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 0.2 | 0.3 | 0.2 | False | 1.0 | 4 | 23728.12 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 0.5 | 0.4 | 0.2 | True | 1.0 | 7 | 16141.34 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.9 | 1.0 | False | 1.0 | 6 | 23062.04 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.6 | 0.7 | False | 1.0 | 4 | 23353.35 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 4 | 19765.56 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 12228.37 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 4 | 16588.03 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 18234.52 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 0.2 | 0.4 | 0.6 | False | 1.0 | 3 | 15422.17 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 4 | 17500.75 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 0.6 | 0.4 | 0.3 | True | 1.0 | 6 | 22827.28 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 0.4 | 0.6 | 0.3 | True | 1.0 | 3 | 19066.71 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.0 | 0.0 | True | 1.0 | 6 | 18946.84 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 1.0 | 1.0 | False | 1.0 | 7 | 20182.21 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.6 | 0.4 | False | 1.0 | 9 | 19370.53 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 16907.6 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.4 | 0.3 | False | 1.0 | 5 | 20044.42 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.9 | 1.0 | True | 1.0 | 5 | 23862.56 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 7 | 17373.55 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 0.8 | 1.0 | 1.0 | False | 1.0 | 4 | 19341.95 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 0.2 | 0.3 | 0.2 | False | 1.0 | 5 | 25100.06 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 0.6 | 0.7 | 0.4 | False | 1.0 | 5 | 22095.72 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 0.6 | 0.7 | 0.5 | True | 1.0 | 7 | 18855.87 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 0.2 | 0.3 | 0.2 | False | 1.0 | 7 | 22804.51 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 0.8 | 1.0 | 0.6 | False | 1.0 | 4 | 19102.37 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.0 | None | None | None | 1 | 11857.49 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 4 | 22234.42 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 6 | 22642.29 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.5 | 0.5 | True | 1.0 | 7 | 22932.86 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 4 | 20983.6 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 0.2 | 0.3 | 0.2 | True | 1.0 | 4 | 20224.6 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.2 | 0.3 | 0.2 | True | 1.0 | 4 | 22360.1 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 0.2 | 0.2 | 0.2 | True | 1.0 | 5 | 18468.52 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 5 | 20580.97 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 5 | 18846.97 |  |

### gemma3_4b__semantic_gs_rrf_rerank_k40

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 14429.16 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.9 | 1.0 | False | 1.0 | 4 | 133017.65 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 145903.25 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.6 | 0.5 | False | 1.0 | 6 | 104843.14 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 8 | 156699.01 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 0.2 | 0.4 | 0.3 | True | 1.0 | 9 | 209044.06 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 5 | 157813.12 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.2 | 0.2 | True | 1.0 | 6 | 159604.64 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.9 | 1.0 | False | 1.0 | 3 | 155533.33 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.2 | 0.4 | 0.2 | True | 1.0 | 7 | 153396.73 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 10273.39 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.3 | 0.2 | True | 1.0 | 5 | 192711.31 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.6 | 0.5 | False | 1.0 | 4 | 185492.45 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.9 | 1.0 | False | 1.0 | 6 | 105073.17 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.6 | 0.8 | 0.5 | False | 1.0 | 6 | 126400.55 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 0.4 | 0.3 | 0.2 | False | 1.0 | 5 | 178903.68 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.4 | 0.6 | 0.5 | False | 1.0 | 7 | 139321.65 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 0.2 | 0.3 | 0.2 | True | 1.0 | 9 | 143652.88 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 1.0 | 1.0 | False | 1.0 | 6 | 145343.19 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 168458.11 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 5374.98 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.3 | 0.2 | True | 1.0 | 8 | 225831.62 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 0.8 | 1.0 | 1.0 | False | 1.0 | 5 | 169668.28 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 0.5 | 0.4 | 0.5 | False | 1.0 | 8 | 121982.47 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 0.5 | 0.5 | 0.0 | False | 1.0 | 6 | 159569.43 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 4 | 192117.9 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.2 | 0.2 | 0.0 | True | 1.0 | 3 | 142910.22 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.6 | 0.4 | 0.3 | True | 1.0 | 3 | 133389.11 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.9 | 1.0 | False | 1.0 | 4 | 196965.65 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.9 | 0.8 | True | 1.0 | 5 | 267331.75 |  |
| TVQA-031 | completed | Direct | core_identity | True | 0.5 | 0.5 | None | None | None | 1 | 5100.3 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.4 | 0.3 | 0.2 | True | 1.0 | 5 | 209891.94 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 5 | 144498.81 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.6 | 0.5 | False | 1.0 | 4 | 120500.23 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.8 | False | 0.75 | 1 | 172149.92 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 0.2 | 0.3 | 0.4 | True | 1.0 | 6 | 193187.74 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 0.4 | 0.6 | 0.5 | False | 1.0 | 5 | 181193.68 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 0.2 | 0.4 | 0.2 | True | 1.0 | 7 | 144784.04 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 7 | 162628.21 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 0.2 | 0.4 | 0.3 | False | 1.0 | 8 | 153647.12 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 0.5 | None | None | None | 1 | 3770.94 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 0.4 | 0.8 | 0.6 | False | 1.0 | 5 | 136848.79 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 142001.71 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 0.2 | 0.2 | 0.0 | False | 1.0 | 6 | 112316.09 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 3 | 171125.83 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 0.6 | 0.8 | 0.5 | True | 1.0 | 5 | 179625.42 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.6 | 0.4 | 0.3 | False | 1.0 | 4 | 174174.1 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 149183.03 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 4 | 138414.43 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 0.8 | 1.0 | 1.0 | False | 1.0 | 6 | 228089.85 |  |
| TVQA-051 | completed | Direct | core_identity | True | 0.0 | 0.0 | None | None | None | 1 | 9540.46 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.1 | 0.0 | True | 1.0 | 7 | 184746.11 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 0.2 | 0.8 | 0.2 | False | 1.0 | 4 | 158609.65 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 8 | 114483.43 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 8 | 163448.64 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 136267.3 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 7 | 142723.52 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.7 | True | 1.0 | 6 | 134504.9 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.6 | 0.4 | False | 1.0 | 4 | 142917.18 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 0.6 | 0.8 | 0.5 | True | 1.0 | 6 | 194033.04 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 0.6 | 0.5 | False | 0.0 | 1 | 11782.09 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.4 | 0.3 | False | 1.0 | 7 | 125364.07 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 6 | 191366.49 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 1.0 | True | 1.0 | 3 | 129823.79 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 5 | 103730.08 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 0.6 | 0.4 | 0.3 | False | 1.0 | 5 | 143987.63 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 1.0 | False | 1.0 | 5 | 130886.97 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 0.6 | 0.8 | 0.7 | False | 1.0 | 5 | 123913.56 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 7 | 152485.06 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 5 | 146958.01 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 11437.73 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.9 | 1.0 | False | 1.0 | 7 | 164773.09 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.9 | 1.0 | False | 1.0 | 5 | 200697.08 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.6 | 1.0 | False | 1.0 | 4 | 105998.42 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 0.6 | 1.0 | 0.8 | False | 1.0 | 5 | 130102.67 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 0.4 | 0.3 | 0.2 | False | 1.0 | 6 | 194570.3 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 0.2 | 0.3 | 0.2 | True | 1.0 | 5 | 140900.94 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 0.2 | 0.1 | 0.2 | True | 1.0 | 8 | 142200.16 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.9 | 1.0 | False | 1.0 | 5 | 151995.56 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 0.6 | 0.4 | 0.2 | True | 0.75 | 1 | 150820.03 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 16860.6 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 0.6 | 0.4 | 0.2 | False | 1.0 | 6 | 177359.53 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.9 | 0.9 | True | 1.0 | 6 | 181452.71 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 0.2 | 0.2 | 0.2 | False | 1.0 | 4 | 107001.2 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 5 | 156572.74 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 0.6 | 0.4 | 0.3 | False | 1.0 | 4 | 168102.19 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 0.2 | 0.3 | 0.2 | False | 1.0 | 5 | 136704.17 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 3 | 131741.3 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.7 | 1.0 | True | 1.0 | 5 | 184488.81 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 0.8 | 1.0 | 0.8 | False | 1.0 | 5 | 195168.96 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.0 | None | None | None | 1 | 12090.09 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 0.8 | 1.0 | 0.6 | False | 1.0 | 5 | 137229.13 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 0.2 | 0.4 | 0.2 | False | 1.0 | 5 | 195191.04 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 0.0 | 0.2 | 0.0 | True | 1.0 | 5 | 127038.25 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.7 | False | 1.0 | 9 | 142878.15 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 0.2 | 0.2 | 0.1 | True | 1.0 | 6 | 138799.19 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.4 | 0.3 | 0.2 | True | 1.0 | 6 | 135985.36 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 0.2 | 0.4 | 0.2 | False | 1.0 | 5 | 117501.25 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.6 | 0.5 | False | 1.0 | 7 | 144606.57 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.9 | 0.8 | False | 1.0 | 8 | 160743.92 |  |
