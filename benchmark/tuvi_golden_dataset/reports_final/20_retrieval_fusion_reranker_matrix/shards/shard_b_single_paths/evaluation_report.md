# W6 Evaluation report: w8_abl_01_retrieval_fusion_reranker_v2_shard_b_single_paths

- Dataset: `D:\TEXT_MINING\tuvi-battu-graphrag\benchmark\tuvi_golden_dataset\release\tuviqa_v1_release.jsonl`
- Dataset items: 100
- Configs: 3
- Judge backend: `gemini`
- Started: 2026-08-09T12:26:53.697215Z
- Completed: 2026-08-09T17:59:50.743302Z
- Notes: Shard B of W8 retrieval/fusion/reranker matrix v2. Contains single retrieval-path variants. Merge into the canonical 10-config report after all shards complete.
- Run status: `completed`

## Run identity and provenance

- Identity SHA-256: `fa392d4087a16b7158270b0678edf680f322c60ad55e9ac7b7c308cfa1d70a65`
- Dataset SHA-256: `90376a87cec29cc22e93dc71b41e054ed2f0183bc515a52aa461fecd43cc008c`
- Manifest SHA-256: `665c437a821583673c5afef08d6dfe2229ebc58c91867b85de7eb6618d88edba`
- Evaluator SHA-256: `47e83febfb2247a151d91605f72ead40dc0ec7f9044194eabd5038d75d74c435`
- Git SHA: `957d35f124e51916215c6b4a64fd5d35d7e66ec7`
- Git dirty: `False`
- Judge model: `gemini-3.1-flash-lite-preview`
- Checkpoint: `benchmark\tuvi_golden_dataset\reports_final\20_retrieval_fusion_reranker_matrix\shards\shard_b_single_paths\checkpoints\evaluation_checkpoint.json`

## Execution completeness

- Expected pairs: 300
- Completed pairs: 300
- Failed pairs: 0
- Executed pairs: 248
- Resumed pairs: 52

> **Metric policy:** W6-EVAL-02 runs the RAG pipeline directly with the selected `ExperimentConfig`. `Context recall` is the Gemini-judged corpus-grounding score for non-Direct items; Direct/chart-only items are excluded from corpus retrieval/citation metrics and reported through `chart_context_grounding`.

## Overall metrics

| Config | Status | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms | Retrieval p95 ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| graph_only_rrf | completed | 100 | 0.823 | 0.686 | 0.5297 | 0.967 | 0.978 | 50835.98 | 40969.78 |
| sparse_only_rrf | completed | 100 | 0.9 | 0.802 | 0.6956 | 0.0 | 0.9863 | 163360.43 | 155286.27 |
| dense_only_rrf | completed | 100 | 0.904 | 0.812 | 0.7363 | 0.0 | 0.989 | 28176.52 | 18159.75 |

## Failure and fallback summary

| Config | Failed | Generation backend fallback | Judge failure | No context | Retrieval backend fallback | Citation fallback |
|---|---:|---:|---:|---:|---:|---:|
| graph_only_rrf | 0 | 0 | 0 | 0 | 0 | 2 |
| sparse_only_rrf | 0 | 0 | 0 | 0 | 0 | 0 |
| dense_only_rrf | 0 | 0 | 0 | 0 | 0 | 0 |

## Ablation analysis

- Baseline config: `baseline_graph_sparse_rrf`
- Preliminary recommendation: `dense_only_rrf`
  - Preliminary heuristic ranks configs by context recall, citation coverage, faithfulness, answer relevancy, graph hit rate, and a small p95 latency penalty.
  - Selected `dense_only_rrf` with context_recall_avg=0.7363, citation_coverage_rate=0.989, p95_latency_ms=28176.52.
  - Treat this as a smoke/first-pass recommendation until official Gemini judge and full dataset runs are complete.

### Context recall ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | dense_only_rrf | 0.7363 |
| 2 | sparse_only_rrf | 0.6956 |
| 3 | graph_only_rrf | 0.5297 |

### Citation coverage ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | dense_only_rrf | 0.989 |
| 2 | sparse_only_rrf | 0.9863 |
| 3 | graph_only_rrf | 0.978 |

### Graph hit ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | graph_only_rrf | 0.967 |
| 2 | sparse_only_rrf | 0.0 |
| 3 | dense_only_rrf | 0.0 |

### p95 latency ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | dense_only_rrf | 28176.52 |
| 2 | graph_only_rrf | 50835.98 |
| 3 | sparse_only_rrf | 163360.43 |

### Retrieval miss summary

| Config | Miss count | Example item IDs |
|---|---:|---|
| graph_only_rrf | 37 | TVQA-005, TVQA-008, TVQA-010, TVQA-017, TVQA-018 |
| sparse_only_rrf | 18 | TVQA-008, TVQA-027, TVQA-028, TVQA-032, TVQA-038 |
| dense_only_rrf | 17 | TVQA-008, TVQA-010, TVQA-025, TVQA-027, TVQA-028 |

### Rerank miss summary

| Config | Miss count | Example item IDs |
|---|---:|---|
| graph_only_rrf | 2 | TVQA-017, TVQA-084 |
| sparse_only_rrf | 2 | TVQA-068, TVQA-084 |
| dense_only_rrf | 1 | TVQA-025 |

## Metrics by question complexity

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| graph_only_rrf | Direct | 10 | 1.0 | 0.81 | 0.8 | 0.0 | 0.0 | 7220.57 |
| graph_only_rrf | One-hop | 46 | 0.8022 | 0.6826 | 0.55 | 0.9783 | 1.0 | 53674.25 |
| graph_only_rrf | Two-hop | 44 | 0.8045 | 0.6614 | 0.5023 | 0.9773 | 0.9773 | 45256.72 |
| sparse_only_rrf | Direct | 10 | 1.0 | 0.86 | 0.8 | 0.0 | 0.0 | 4355.89 |
| sparse_only_rrf | One-hop | 46 | 0.8891 | 0.7913 | 0.6783 | 0.0 | 0.9946 | 178302.3 |
| sparse_only_rrf | Two-hop | 44 | 0.8886 | 0.8 | 0.7114 | 0.0 | 1.0 | 155663.21 |
| dense_only_rrf | Direct | 10 | 1.0 | 0.84 | 0.8 | 0.0 | 0.0 | 4331.7 |
| dense_only_rrf | One-hop | 46 | 0.8957 | 0.8087 | 0.7478 | 0.0 | 1.0 | 27924.57 |
| dense_only_rrf | Two-hop | 44 | 0.8909 | 0.8091 | 0.7227 | 0.0 | 1.0 | 27972.11 |

## Metrics by question family

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
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

## Per-question results

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
