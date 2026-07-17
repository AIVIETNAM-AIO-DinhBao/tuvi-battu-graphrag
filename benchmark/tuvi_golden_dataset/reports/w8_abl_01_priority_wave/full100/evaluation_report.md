# W6 Evaluation report: w8_abl_01_priority_wave_full100

- Dataset: `D:\University\Năm 3 ĐH\Kì 3 (18th6)\Text Mining\tuvi-battu-graphrag\benchmark\tuvi_golden_dataset\release\tuviqa_v1_release.jsonl`
- Dataset items: 100
- Configs: 4
- Judge backend: `gemini`
- Started: 2026-07-16T19:51:29.580689Z
- Completed: 2026-07-16T21:01:41.775132Z
- Notes: W8 priority full-100 retrieval/fusion/reranker wave. Reuse the behavior-equivalent default_production_v2 full-100 run as the Graph+Sparse+RRF+reranker control. This wave isolates sparse-only, planner-gated dense+sparse, reranker-off, and weighted-sum variants while holding semantic BGE-M3 chunking, prompt v1, Gemini Flash Lite, balanced context, query rewrite off, document grading on, and cache disabled constant.
- Run status: `partial`

## Run identity and provenance

- Identity SHA-256: `c7fb0b98c5f2d00f2e80b2d1cec27091808d71a157a9f77ba199fa3a0f199b08`
- Dataset SHA-256: `90376a87cec29cc22e93dc71b41e054ed2f0183bc515a52aa461fecd43cc008c`
- Manifest SHA-256: `c21034d0c96e3fd9aca60483bd1a73a95d85c7a780b638e02dcf40c9b67d7056`
- Evaluator SHA-256: `9ae528d893159c4092c3129523da8d69a7a79a6ab5c32a132791158287eda314`
- Git SHA: `132cb0948d4e221ccabec0d620f0a8acb3d880ca`
- Git dirty: `False`
- Judge model: `gemini-3.1-flash-lite-preview`
- Checkpoint: `benchmark\tuvi_golden_dataset\reports\w8_abl_01_priority_wave\full100\checkpoint\evaluation_checkpoint.json`

## Execution completeness

- Expected pairs: 400
- Completed pairs: 379
- Failed pairs: 21
- Executed pairs: 379
- Resumed pairs: 0

> **Metric policy:** W6-EVAL-02 runs the RAG pipeline directly with the selected `ExperimentConfig`. `Context recall` is the Gemini-judged corpus-grounding score for non-Direct items; Direct/chart-only items are excluded from corpus retrieval/citation metrics and reported through `chart_context_grounding`.

## Overall metrics

| Config | Status | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms | Retrieval p95 ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| sparse_only_rrf | completed | 100 | 0.872 | 0.736 | 0.6099 | 0.0 | 0.989 | 6245.82 | 3798.45 |
| dense_sparse_rrf | completed | 100 | 0.868 | 0.751 | 0.6088 | 0.0 | 0.9835 | 7619.89 | 5314.74 |
| baseline_no_reranker | failed | 100 | 0.8734 | 0.762 | 0.625 | 0.9861 | 0.9896 | 22749.23 | 19835.53 |
| baseline_weighted_sum | completed | 100 | 0.88 | 0.743 | 0.6088 | 0.967 | 0.9863 | 22436.26 | 19443.21 |

## Failure and fallback summary

| Config | Failed | Generation backend fallback | Judge failure | No context | Retrieval backend fallback | Citation fallback |
|---|---:|---:|---:|---:|---:|---:|
| sparse_only_rrf | 0 | 0 | 0 | 0 | 0 | 0 |
| dense_sparse_rrf | 0 | 0 | 0 | 0 | 0 | 0 |
| baseline_no_reranker | 21 | 0 | 0 | 0 | 0 | 0 |
| baseline_weighted_sum | 0 | 0 | 0 | 0 | 0 | 0 |

## Ablation analysis

- Baseline config: `baseline_graph_sparse_rrf`
- Preliminary recommendation: `baseline_weighted_sum`
  - Preliminary heuristic ranks configs by context recall, citation coverage, faithfulness, answer relevancy, graph hit rate, and a small p95 latency penalty.
  - Selected `baseline_weighted_sum` with context_recall_avg=0.6088, citation_coverage_rate=0.9863, p95_latency_ms=22436.26.
  - Treat this as a smoke/first-pass recommendation until official Gemini judge and full dataset runs are complete.

### Context recall ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | baseline_no_reranker | 0.625 |
| 2 | sparse_only_rrf | 0.6099 |
| 3 | dense_sparse_rrf | 0.6088 |
| 4 | baseline_weighted_sum | 0.6088 |

### Citation coverage ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | baseline_no_reranker | 0.9896 |
| 2 | sparse_only_rrf | 0.989 |
| 3 | baseline_weighted_sum | 0.9863 |
| 4 | dense_sparse_rrf | 0.9835 |

### Graph hit ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | baseline_no_reranker | 0.9861 |
| 2 | baseline_weighted_sum | 0.967 |
| 3 | sparse_only_rrf | 0.0 |
| 4 | dense_sparse_rrf | 0.0 |

### p95 latency ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | sparse_only_rrf | 6245.82 |
| 2 | dense_sparse_rrf | 7619.89 |
| 3 | baseline_weighted_sum | 22436.26 |
| 4 | baseline_no_reranker | 22749.23 |

### Retrieval miss summary

| Config | Miss count | Example item IDs |
|---|---:|---|
| sparse_only_rrf | 26 | TVQA-008, TVQA-012, TVQA-015, TVQA-017, TVQA-018 |
| dense_sparse_rrf | 25 | TVQA-008, TVQA-010, TVQA-013, TVQA-015, TVQA-018 |
| baseline_no_reranker | 19 | TVQA-008, TVQA-010, TVQA-012, TVQA-015, TVQA-018 |
| baseline_weighted_sum | 30 | TVQA-008, TVQA-012, TVQA-017, TVQA-018, TVQA-023 |

### Rerank miss summary

| Config | Miss count | Example item IDs |
|---|---:|---|
| sparse_only_rrf | 3 | TVQA-063, TVQA-076, TVQA-093 |
| dense_sparse_rrf | 5 | TVQA-033, TVQA-045, TVQA-063, TVQA-083, TVQA-093 |
| baseline_no_reranker | 0 |  |
| baseline_weighted_sum | 4 | TVQA-033, TVQA-045, TVQA-063, TVQA-093 |

## Metrics by question complexity

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| sparse_only_rrf | Direct | 10 | 1.0 | 0.89 | 0.7 | 0.0 | 0.75 | 1838.6 |
| sparse_only_rrf | One-hop | 46 | 0.8565 | 0.6761 | 0.5804 | 0.0 | 0.9891 | 5525.35 |
| sparse_only_rrf | Two-hop | 44 | 0.8591 | 0.7636 | 0.6386 | 0.0 | 0.9943 | 6731.51 |
| dense_sparse_rrf | Direct | 10 | 1.0 | 0.88 | 0.8 | 0.0 | 0.75 | 1890.39 |
| dense_sparse_rrf | One-hop | 46 | 0.8435 | 0.7152 | 0.5739 | 0.0 | 0.9728 | 6758.7 |
| dense_sparse_rrf | Two-hop | 44 | 0.8636 | 0.7591 | 0.6409 | 0.0 | 1.0 | 8716.69 |
| baseline_no_reranker | Direct | 8 | 0.975 | 0.9125 | 0.6 | 0.0 | 0.75 | 1986.44 |
| baseline_no_reranker | One-hop | 36 | 0.8556 | 0.7111 | 0.5917 | 1.0 | 0.9931 | 17970.24 |
| baseline_no_reranker | Two-hop | 35 | 0.8686 | 0.78 | 0.66 | 1.0 | 0.9929 | 24190.85 |
| baseline_weighted_sum | Direct | 10 | 1.0 | 0.89 | 0.7 | 0.0 | 0.75 | 2285.74 |
| baseline_weighted_sum | One-hop | 46 | 0.8783 | 0.713 | 0.5826 | 0.9783 | 0.9783 | 17302.78 |
| baseline_weighted_sum | Two-hop | 44 | 0.8545 | 0.7409 | 0.6341 | 0.9773 | 1.0 | 24288.0 |

## Metrics by question family

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| sparse_only_rrf | core_identity | 10 | 1.0 | 0.89 | 0.7 | 0.0 | 0.75 | 1838.6 |
| sparse_only_rrf | dai_van_interpretation | 10 | 0.86 | 0.35 | 0.25 | 0.0 | 1.0 | 5464.82 |
| sparse_only_rrf | menh_cuc_relation | 10 | 0.96 | 0.94 | 0.87 | 0.0 | 1.0 | 4739.42 |
| sparse_only_rrf | menh_house_interpretation | 10 | 0.82 | 0.67 | 0.53 | 0.0 | 1.0 | 5934.26 |
| sparse_only_rrf | menh_tam_hop | 10 | 0.81 | 0.8 | 0.63 | 0.0 | 0.975 | 6909.51 |
| sparse_only_rrf | menh_xung_chieu | 10 | 0.81 | 0.71 | 0.57 | 0.0 | 1.0 | 6142.9 |
| sparse_only_rrf | special_state_interpretation | 10 | 0.83 | 0.59 | 0.49 | 0.0 | 1.0 | 4826.53 |
| sparse_only_rrf | synthesis_judgement | 10 | 0.91 | 0.81 | 0.68 | 0.0 | 1.0 | 6630.24 |
| sparse_only_rrf | than_cu_interpretation | 10 | 0.8 | 0.71 | 0.64 | 0.0 | 0.95 | 5356.35 |
| sparse_only_rrf | topic_house_plus_relations | 10 | 0.92 | 0.89 | 0.82 | 0.0 | 1.0 | 6219.65 |
| dense_sparse_rrf | core_identity | 10 | 1.0 | 0.88 | 0.8 | 0.0 | 0.75 | 1890.39 |
| dense_sparse_rrf | dai_van_interpretation | 10 | 0.87 | 0.51 | 0.26 | 0.0 | 1.0 | 6389.6 |
| dense_sparse_rrf | menh_cuc_relation | 10 | 1.0 | 0.88 | 0.8 | 0.0 | 1.0 | 6376.4 |
| dense_sparse_rrf | menh_house_interpretation | 10 | 0.86 | 0.72 | 0.61 | 0.0 | 1.0 | 19296.02 |
| dense_sparse_rrf | menh_tam_hop | 10 | 0.83 | 0.76 | 0.61 | 0.0 | 1.0 | 10325.31 |
| dense_sparse_rrf | menh_xung_chieu | 10 | 0.85 | 0.72 | 0.61 | 0.0 | 1.0 | 7217.59 |
| dense_sparse_rrf | special_state_interpretation | 10 | 0.8 | 0.74 | 0.59 | 0.0 | 0.975 | 6419.5 |
| dense_sparse_rrf | synthesis_judgement | 10 | 0.88 | 0.81 | 0.72 | 0.0 | 1.0 | 8103.58 |
| dense_sparse_rrf | than_cu_interpretation | 10 | 0.71 | 0.67 | 0.51 | 0.0 | 0.9 | 6459.26 |
| dense_sparse_rrf | topic_house_plus_relations | 10 | 0.88 | 0.82 | 0.75 | 0.0 | 1.0 | 7701.9 |
| baseline_no_reranker | core_identity | 8 | 0.975 | 0.9125 | 0.6 | 0.0 | 0.75 | 1986.44 |
| baseline_no_reranker | dai_van_interpretation | 8 | 0.825 | 0.4125 | 0.325 | 1.0 | 1.0 | 13716.62 |
| baseline_no_reranker | menh_cuc_relation | 8 | 0.95 | 0.8875 | 0.8375 | 1.0 | 1.0 | 16629.79 |
| baseline_no_reranker | menh_house_interpretation | 8 | 0.85 | 0.625 | 0.45 | 1.0 | 1.0 | 18914.47 |
| baseline_no_reranker | menh_tam_hop | 8 | 0.8875 | 0.825 | 0.6875 | 1.0 | 1.0 | 24249.05 |
| baseline_no_reranker | menh_xung_chieu | 8 | 0.7875 | 0.6875 | 0.55 | 1.0 | 1.0 | 19662.73 |
| baseline_no_reranker | special_state_interpretation | 8 | 0.7 | 0.65 | 0.45 | 1.0 | 0.9688 | 16522.04 |
| baseline_no_reranker | synthesis_judgement | 7 | 0.9429 | 0.8286 | 0.7143 | 1.0 | 1.0 | 25194.28 |
| baseline_no_reranker | than_cu_interpretation | 8 | 0.875 | 0.875 | 0.775 | 1.0 | 1.0 | 16431.13 |
| baseline_no_reranker | topic_house_plus_relations | 8 | 0.95 | 0.925 | 0.85 | 1.0 | 0.9688 | 22393.72 |
| baseline_weighted_sum | core_identity | 10 | 1.0 | 0.89 | 0.7 | 0.0 | 0.75 | 2285.74 |
| baseline_weighted_sum | dai_van_interpretation | 10 | 0.9 | 0.43 | 0.33 | 1.0 | 1.0 | 13790.63 |
| baseline_weighted_sum | menh_cuc_relation | 10 | 1.0 | 0.94 | 0.92 | 1.0 | 1.0 | 16504.78 |
| baseline_weighted_sum | menh_house_interpretation | 10 | 0.86 | 0.74 | 0.65 | 0.9 | 1.0 | 18004.43 |
| baseline_weighted_sum | menh_tam_hop | 10 | 0.84 | 0.77 | 0.62 | 1.0 | 1.0 | 24980.06 |
| baseline_weighted_sum | menh_xung_chieu | 10 | 0.74 | 0.63 | 0.51 | 1.0 | 1.0 | 19513.34 |
| baseline_weighted_sum | special_state_interpretation | 10 | 0.82 | 0.74 | 0.53 | 1.0 | 0.975 | 16012.99 |
| baseline_weighted_sum | synthesis_judgement | 10 | 0.92 | 0.84 | 0.76 | 0.9 | 1.0 | 23897.04 |
| baseline_weighted_sum | than_cu_interpretation | 10 | 0.82 | 0.65 | 0.42 | 1.0 | 0.925 | 16795.57 |
| baseline_weighted_sum | topic_house_plus_relations | 10 | 0.9 | 0.8 | 0.73 | 1.0 | 1.0 | 22946.41 |

## Per-question results

### sparse_only_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1804.6 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 1.0 | False | 1.0 | 2 | 4771.55 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.6 | False | 1.0 | 2 | 4760.31 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 3 | 3891.92 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.6 | False | 1.0 | 3 | 4747.88 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 6 | 6746.74 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.8 | 0.7 | False | 1.0 | 2 | 4561.17 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.4 | 0.2 | False | 1.0 | 4 | 5041.09 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 4 | 6143.78 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.7 | 0.5 | False | 1.0 | 5 | 6045.08 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1062.25 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.4 | 0.2 | False | 1.0 | 8 | 5510.76 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.6 | 0.5 | False | 1.0 | 5 | 4807.67 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 0.8 | 1.0 | 1.0 | False | 1.0 | 3 | 4849.92 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.5 | 0.2 | False | 1.0 | 2 | 4694.48 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.7 | False | 1.0 | 3 | 5580.47 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.5 | 0.4 | False | 1.0 | 4 | 4926.34 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 0.5 | 0.2 | 0.0 | False | 1.0 | 4 | 4150.06 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 3 | 5066.41 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 3 | 5703.57 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 828.83 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.7 | False | 1.0 | 3 | 5907.19 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 2 | 5121.76 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 2 | 4366.87 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 0.5 | 0.2 | 0.0 | False | 1.0 | 5 | 4718.09 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 5 | 7042.68 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.5 | 0.5 | 0.2 | False | 1.0 | 2 | 5076.62 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.5 | 0.2 | 0.2 | False | 1.0 | 3 | 5362.72 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 4 | 6281.72 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 0.9 | 1.0 | 1.0 | False | 1.0 | 5 | 7109.0 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 814.44 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.6 | 0.4 | 0.2 | False | 1.0 | 4 | 5956.4 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 2 | 5431.25 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 2 | 3976.27 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.6 | False | 1.0 | 3 | 4798.65 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | False | 1.0 | 4 | 6645.24 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.8 | 0.7 | False | 1.0 | 5 | 6019.41 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 0.0 | 0.0 | False | 1.0 | 2 | 3750.63 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.2 | 0.4 | 0.2 | False | 1.0 | 5 | 5965.86 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 3 | 5495.51 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 795.84 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.6 | False | 1.0 | 2 | 4831.9 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 2 | 5075.68 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.5 | False | 1.0 | 3 | 4478.51 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.0 | 0.0 | False | 1.0 | 4 | 4727.12 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 2 | 5615.84 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 6 | 6243.93 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.5 | 0.2 | False | 1.0 | 3 | 3798.05 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 3 | 5865.75 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 3 | 5855.67 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 993.92 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.2 | 0.0 | False | 1.0 | 6 | 5530.21 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 3 | 5264.81 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 0.8 | 1.0 | 0.5 | False | 1.0 | 3 | 3854.66 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 3 | 4674.0 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 3 | 5181.02 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.8 | False | 1.0 | 3 | 5178.92 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.7 | False | 1.0 | 2 | 5548.35 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 0.8 | False | 1.0 | 6 | 5498.77 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 3 | 5902.87 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 0.8 | 0.7 | False | 0.75 | 1 | 1866.42 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.6 | False | 1.0 | 3 | 5134.69 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.2 | 0.0 | False | 0.75 | 1 | 4417.13 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 2 | 4345.29 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.7 | False | 1.0 | 5 | 4849.35 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 2 | 5546.29 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 6 | 4877.21 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.8 | 1.0 | False | 1.0 | 3 | 4899.86 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.6 | False | 1.0 | 4 | 5895.23 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.8 | 0.8 | False | 1.0 | 3 | 5378.94 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1165.46 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 9 | 4953.71 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.9 | 1.0 | False | 1.0 | 2 | 4801.95 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 1.0 | False | 1.0 | 3 | 3663.84 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 0.0 | 0.0 | 0.0 | False | 1.0 | 2 | 4645.88 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | False | 0.75 | 1 | 5723.23 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 2 | 5284.59 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.0 | 0.0 | False | 1.0 | 4 | 3870.66 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 4 | 4981.07 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.5 | 0.0 | False | 1.0 | 2 | 5511.97 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 956.61 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.6 | 0.5 | False | 1.0 | 3 | 4315.78 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 2 | 4842.81 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.7 | False | 1.0 | 3 | 4604.36 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 2 | 4218.26 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 6 | 5570.45 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 2 | 5402.26 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.2 | 0.0 | False | 1.0 | 2 | 4833.8 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.6 | False | 1.0 | 3 | 4789.84 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.5 | 0.2 | False | 1.0 | 3 | 5310.33 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.5 | None | None | None | 1 | 1316.57 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 0.8 | False | 1.0 | 2 | 4840.18 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 0.0 | 0.0 | 0.0 | False | 0.75 | 1 | 4166.59 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 2 | 3656.01 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.8 | False | 1.0 | 4 | 4714.69 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 0.6 | 0.5 | 0.2 | False | 1.0 | 2 | 5673.77 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.6 | 0.4 | False | 1.0 | 2 | 5675.9 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.4 | 0.2 | False | 1.0 | 4 | 4852.91 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 2 | 5370.39 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 3 | 5133.28 |  |

### dense_sparse_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 911.17 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 2 | 29053.93 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.5 | False | 1.0 | 2 | 6004.52 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 3 | 4834.23 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 4 | 6079.84 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 4 | 10841.44 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.8 | 0.7 | False | 1.0 | 5 | 6573.95 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.5 | 0.2 | False | 1.0 | 4 | 5789.12 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 1.0 | False | 1.0 | 4 | 6743.09 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.2 | 0.4 | 0.2 | False | 1.0 | 2 | 6780.27 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 1007.1 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.5 | 0.5 | False | 1.0 | 9 | 5926.09 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 0.6 | 0.8 | 0.4 | False | 1.0 | 5 | 6422.41 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 2 | 5540.03 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.2 | 0.3 | 0.2 | False | 1.0 | 4 | 5910.68 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 4 | 6214.18 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 3 | 6752.69 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 0.5 | 0.2 | 0.0 | False | 1.0 | 3 | 5384.76 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 2 | 6392.74 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 3 | 6322.36 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1170.59 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 3 | 6389.6 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 2 | 5972.63 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 3 | 5262.1 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.6 | False | 1.0 | 4 | 5977.65 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 5 | 7611.09 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.5 | 0.2 | 0.0 | False | 1.0 | 2 | 6071.38 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.4 | 0.2 | False | 1.0 | 4 | 6180.35 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 7 | 7787.0 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 5 | 8880.75 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 807.07 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.6 | 0.5 | False | 1.0 | 4 | 7369.68 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.0 | False | 0.75 | 1 | 5700.29 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.6 | False | 1.0 | 2 | 6821.89 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.7 | False | 1.0 | 3 | 6422.65 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | False | 1.0 | 6 | 9694.49 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.6 | 0.5 | False | 1.0 | 4 | 6415.82 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 0.5 | 0.0 | False | 1.0 | 4 | 5102.25 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.6 | 0.4 | False | 1.0 | 2 | 7597.88 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.9 | 0.8 | False | 1.0 | 2 | 6959.81 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 0.9 | None | None | None | 1 | 882.83 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.6 | False | 1.0 | 2 | 6414.91 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 1.0 | False | 1.0 | 3 | 6319.65 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.6 | False | 1.0 | 3 | 5780.13 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 0.0 | False | 0.75 | 1 | 5104.27 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 3 | 7580.14 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.6 | 0.4 | False | 1.0 | 5 | 7597.97 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.6 | False | 1.0 | 4 | 5643.2 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 2 | 6753.19 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 3 | 7153.71 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 926.71 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.2 | 0.0 | False | 1.0 | 2 | 6021.8 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 3 | 6209.18 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.6 | False | 1.0 | 2 | 5699.92 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 3 | 6338.62 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.6 | 0.4 | False | 1.0 | 3 | 5877.63 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 2 | 6503.77 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.5 | False | 1.0 | 3 | 6296.63 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.6 | False | 1.0 | 7 | 7033.29 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 4 | 6999.84 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 0.8 | 0.8 | False | 0.75 | 1 | 1581.86 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 3 | 6569.15 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 0.5 | 0.4 | 0.2 | False | 0.75 | 1 | 5763.23 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 2 | 5831.91 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.8 | False | 1.0 | 5 | 6108.94 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 2 | 6411.47 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.8 | 1.0 | False | 1.0 | 5 | 6548.89 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.6 | 0.5 | False | 1.0 | 4 | 6304.14 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 0.8 | False | 1.0 | 4 | 7140.76 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.8 | 0.7 | False | 1.0 | 3 | 6878.46 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 909.4 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.6 | 0.5 | False | 1.0 | 8 | 5875.6 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 2 | 6489.41 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.6 | 0.6 | False | 1.0 | 3 | 4754.02 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 0.0 | 0.0 | 0.0 | False | 1.0 | 9 | 6028.74 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 0.9 | 1.0 | 0.8 | False | 1.0 | 3 | 6908.16 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.8 | 0.5 | False | 1.0 | 2 | 6405.55 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.5 | 0.0 | False | 1.0 | 3 | 5124.3 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 4 | 6872.39 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.6 | 0.4 | False | 1.0 | 2 | 6150.4 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 975.37 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.7 | False | 1.0 | 3 | 5555.98 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 0.0 | 0.0 | 0.0 | False | 0.75 | 1 | 6033.75 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.6 | False | 1.0 | 3 | 5570.19 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 2 | 5099.42 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.9 | 0.8 | False | 1.0 | 6 | 6829.28 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.8 | False | 1.0 | 2 | 6390.37 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.5 | 0.2 | False | 1.0 | 2 | 5247.25 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 0.2 | 0.2 | 0.0 | False | 1.0 | 3 | 6422.3 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.7 | 0.5 | False | 1.0 | 4 | 6043.21 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.5 | None | None | None | 1 | 2142.83 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.6 | False | 1.0 | 2 | 6029.13 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 0.0 | 0.0 | 0.0 | False | 0.75 | 1 | 5740.65 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 2 | 5280.23 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 4 | 6415.65 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.4 | 0.2 | False | 1.0 | 4 | 6344.47 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.6 | 0.5 | False | 1.0 | 2 | 6692.84 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.5 | 0.4 | False | 1.0 | 5 | 6459.52 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 2 | 7542.07 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 4 | 6801.68 |  |

### baseline_no_reranker

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 931.43 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 2 | 15232.12 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 12132.5 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 14671.77 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 4 | 11141.56 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 1.0 | True | 1.0 | 5 | 17484.88 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 18162.82 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.2 | 0.2 | True | 1.0 | 4 | 8708.09 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 13985.67 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.5 | 0.2 | True | 1.0 | 3 | 12087.3 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1157.43 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.5 | 0.0 | True | 1.0 | 2 | 15461.49 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 0.6 | 0.8 | 0.5 | True | 1.0 | 5 | 9610.98 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 0.8 | 1.0 | 1.0 | True | 1.0 | 3 | 15017.64 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 3 | 10921.29 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 4 | 19343.01 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 3 | 16006.04 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.0 | 0.0 | True | 1.0 | 2 | 8244.23 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 10941.83 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 14024.84 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 886.34 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 6 | 16156.53 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 17233.04 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 16668.55 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.6 | 0.0 | True | 1.0 | 4 | 11651.28 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.5 | 0.3 | True | 1.0 | 6 | 24140.97 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.5 | 0.2 | 0.0 | True | 1.0 | 2 | 11426.44 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.4 | 0.2 | True | 1.0 | 4 | 11521.07 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 22595.9 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 4 | 26957.92 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 920.45 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.4 | 0.3 | 0.2 | True | 1.0 | 7 | 19247.34 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 0.8 | 1.0 | 1.0 | True | 1.0 | 5 | 12352.1 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 2 | 16023.44 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.5 | True | 1.0 | 3 | 17861.56 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 2 | 24307.24 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.8 | True | 1.0 | 3 | 19485.92 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 4 | 7432.97 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.6 | 0.2 | True | 0.75 | 1 | 22018.25 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 4 | 18974.36 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 773.83 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 18296.27 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 12436.46 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.5 | True | 1.0 | 5 | 16299.38 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 0.75 | 1 | 8808.53 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 24129.2 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 5 | 19757.93 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.5 | True | 1.0 | 5 | 8444.16 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 12017.78 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 21079.13 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 1437.18 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.2 | 0.0 | True | 1.0 | 4 | 14472.17 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 14941.86 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 14919.93 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 13392.5 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 0.8 | 1.0 | 0.6 | True | 1.0 | 3 | 16599.95 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 3 | 15872.9 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 3 | 12103.98 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 1.0 | 0.8 | True | 1.0 | 5 | 18472.98 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 0.8 | True | 1.0 | 3 | 13499.31 |  |
| TVQA-061 | completed | Direct | core_identity | False | 0.8 | 0.7 | 0.6 | False | 0.75 | 1 | 2282.19 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 15765.61 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.5 | 0.2 | True | 1.0 | 2 | 11630.64 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 16557.8 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 5 | 8079.15 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 2 | 16511.1 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.5 | 0.2 | True | 1.0 | 9 | 15565.46 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 3 | 14584.96 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 3 | 15680.93 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 4 | 16066.02 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1356.02 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 3 | 16720.99 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 3 | 12513.38 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 1.0 | True | 1.0 | 3 | 15970.13 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 0.2 | 0.4 | 0.0 | True | 1.0 | 3 | 14034.37 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 2 | 17755.09 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 2 | 11530.03 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.2 | 0.0 | True | 1.0 | 3 | 8371.93 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 19213.94 |  |

### baseline_weighted_sum

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 2406.64 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 15179.17 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.5 | True | 1.0 | 2 | 12371.08 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 14450.61 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 11952.33 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.9 | True | 1.0 | 3 | 17527.79 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 3 | 17955.1 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.5 | 0.4 | True | 1.0 | 3 | 10033.15 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 3 | 14182.44 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 6 | 12986.16 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1440.12 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.4 | 0.2 | True | 1.0 | 9 | 15849.14 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 10956.34 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 3 | 14971.04 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.8 | 1.0 | 0.6 | True | 1.0 | 3 | 11627.27 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 3 | 20053.88 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.2 | 0.2 | 0.2 | True | 1.0 | 5 | 16477.46 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.0 | 0.0 | True | 1.0 | 2 | 7342.4 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 9 | 12097.3 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 14503.1 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1492.34 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 1.0 | True | 1.0 | 4 | 17120.24 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.2 | 0.0 | True | 1.0 | 2 | 17363.62 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 16625.93 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.5 | 0.2 | True | 1.0 | 4 | 12077.99 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 6 | 23518.43 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.5 | 0.2 | 0.2 | True | 1.0 | 2 | 10200.18 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.5 | 0.2 | True | 1.0 | 3 | 12608.6 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 23405.54 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 26690.12 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1103.18 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.6 | 0.4 | 0.2 | True | 1.0 | 2 | 18727.85 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 0.75 | 1 | 12679.25 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 16139.81 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 3 | 18566.44 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 3 | 25435.17 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 4 | 19384.86 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 0.0 | 0.0 | True | 1.0 | 2 | 7595.89 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.5 | 0.2 | True | 1.0 | 3 | 22385.25 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 3 | 20483.28 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 1166.29 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 9 | 15998.22 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 2 | 12416.08 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 3 | 16071.62 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 0.0 | True | 0.75 | 1 | 9529.76 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 3 | 24423.81 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 5 | 19618.46 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.5 | True | 1.0 | 4 | 8395.31 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 12662.24 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 19969.59 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 1274.15 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.3 | 0.0 | True | 1.0 | 2 | 14291.89 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 0.8 | 1.0 | 0.5 | True | 1.0 | 3 | 16101.28 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 4 | 15694.36 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 1.0 | True | 1.0 | 2 | 12892.1 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.4 | True | 1.0 | 2 | 16100.72 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 3 | 16172.58 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.9 | 1.0 | True | 1.0 | 2 | 12151.35 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 5 | 13849.79 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 13670.94 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 0.8 | 0.7 | False | 0.75 | 1 | 2137.97 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 3 | 15773.1 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.5 | True | 0.75 | 1 | 11689.08 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 15862.94 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 5 | 8881.69 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 3 | 16902.34 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.5 | 0.2 | True | 1.0 | 3 | 15535.57 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 14757.74 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 4 | 15357.08 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 15868.26 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1153.25 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 3 | 16839.43 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 2 | 11339.66 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 14555.4 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 3 | 12745.59 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 2 | 16250.61 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 2 | 12051.25 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.2 | 0.0 | True | 1.0 | 4 | 7743.44 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 16918.24 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.4 | 0.2 | True | 1.0 | 2 | 15412.91 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1452.43 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 1.0 | False | 1.0 | 5 | 5390.33 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 6 | 11668.29 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 14500.6 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 11963.5 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 7 | 16026.93 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 2 | 16432.5 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.0 | 0.0 | True | 1.0 | 3 | 11985.71 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 0.2 | 0.2 | 0.0 | True | 1.0 | 4 | 18434.96 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.8 | 0.7 | False | 1.0 | 7 | 5611.21 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.5 | None | None | None | 1 | 2018.73 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 15922.74 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.5 | 0.0 | True | 0.75 | 1 | 15714.01 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 2 | 16356.7 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 3 | 11489.95 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 2 | 11376.94 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.6 | 0.5 | 0.3 | True | 1.0 | 2 | 12095.25 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 0.6 | 0.4 | 0.2 | True | 1.0 | 6 | 10811.45 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 9 | 12316.33 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 2 | 13076.52 |  |
