# W6 Evaluation report: w6_eval_02_single_config

- Dataset: `D:\University\Năm 3 ĐH\Kì 3 (18th6)\Text Mining\tuvi-battu-graphrag\benchmark\tuvi_golden_dataset\release\tuviqa_v1_release.jsonl`
- Dataset items: 100
- Configs: 1
- Judge backend: `gemini`
- Started: 2026-07-16T19:16:10.463226Z
- Completed: 2026-07-16T19:16:10.645515Z
- Notes: W6-EVAL-02 single-config evaluation run.
- Run status: `completed`

## Run identity and provenance

- Identity SHA-256: `60c4ce22d8228f5cc826094d6bf68fd956b2a91e2d7a768d10cc51e0940aae8d`
- Dataset SHA-256: `90376a87cec29cc22e93dc71b41e054ed2f0183bc515a52aa461fecd43cc008c`
- Manifest SHA-256: `b9cccbfb5cfe3a6cbc820bc80ce3befd2970a9fec0c33f073a0d9b7de2ee3b5a`
- Evaluator SHA-256: `9ae528d893159c4092c3129523da8d69a7a79a6ab5c32a132791158287eda314`
- Git SHA: `c32771fefb5bc14686660a43ab0bd3ba4d79d4b7`
- Git dirty: `False`
- Judge model: `gemini-3.1-flash-lite-preview`
- Checkpoint: `benchmark\tuvi_golden_dataset\reports\w8_eval_01\production_full100\checkpoint\evaluation_checkpoint.json`

## Execution completeness

- Expected pairs: 100
- Completed pairs: 100
- Failed pairs: 0
- Executed pairs: 0
- Resumed pairs: 100

> **Metric policy:** W6-EVAL-02 runs the RAG pipeline directly with the selected `ExperimentConfig`. `Context recall` is the Gemini-judged corpus-grounding score for non-Direct items; Direct/chart-only items are excluded from corpus retrieval/citation metrics and reported through `chart_context_grounding`.

## Overall metrics

| Config | Status | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms | Retrieval p95 ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| default_production | completed | 100 | 0.853 | 0.719 | 0.6223 | 0.967 | 0.978 | 26530.42 | 24467.9 |

## Failure and fallback summary

| Config | Failed | Generation backend fallback | Judge failure | No context | Retrieval backend fallback | Citation fallback |
|---|---:|---:|---:|---:|---:|---:|
| default_production | 0 | 0 | 0 | 0 | 0 | 0 |

## Ablation analysis

- Baseline config: `baseline_graph_sparse_rrf`
- Preliminary recommendation: `default_production`
  - Preliminary heuristic ranks configs by context recall, citation coverage, faithfulness, answer relevancy, graph hit rate, and a small p95 latency penalty.
  - Selected `default_production` with context_recall_avg=0.6223, citation_coverage_rate=0.978, p95_latency_ms=26530.42.
  - Treat this as a smoke/first-pass recommendation until official Gemini judge and full dataset runs are complete.

### Context recall ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | default_production | 0.6223 |

### Citation coverage ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | default_production | 0.978 |

### Graph hit ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | default_production | 0.967 |

### p95 latency ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | default_production | 26530.42 |

### Retrieval miss summary

| Config | Miss count | Example item IDs |
|---|---:|---|
| default_production | 34 | TVQA-008, TVQA-010, TVQA-012, TVQA-013, TVQA-015 |

### Rerank miss summary

| Config | Miss count | Example item IDs |
|---|---:|---|
| default_production | 7 | TVQA-012, TVQA-042, TVQA-058, TVQA-063, TVQA-066 |

## Metrics by question complexity

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| default_production | Direct | 10 | 1.0 | 0.89 | 0.8 | 0.0 | 0.75 | 1794.08 |
| default_production | One-hop | 46 | 0.8239 | 0.6652 | 0.5978 | 0.9783 | 0.9783 | 25135.03 |
| default_production | Two-hop | 44 | 0.85 | 0.7364 | 0.6439 | 0.9773 | 0.983 | 29074.94 |

## Metrics by question family

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| default_production | core_identity | 10 | 1.0 | 0.89 | 0.8 | 0.0 | 0.75 | 1794.08 |
| default_production | dai_van_interpretation | 10 | 0.69 | 0.34 | 0.27 | 1.0 | 0.975 | 39779.29 |
| default_production | menh_cuc_relation | 10 | 1.0 | 0.88 | 0.84 | 1.0 | 1.0 | 24681.37 |
| default_production | menh_house_interpretation | 10 | 0.77 | 0.63 | 0.51 | 0.9 | 0.95 | 19920.87 |
| default_production | menh_tam_hop | 10 | 0.84 | 0.79 | 0.69 | 1.0 | 0.975 | 26240.76 |
| default_production | menh_xung_chieu | 10 | 0.86 | 0.66 | 0.563 | 1.0 | 1.0 | 20043.29 |
| default_production | special_state_interpretation | 10 | 0.85 | 0.7 | 0.61 | 1.0 | 1.0 | 22712.36 |
| default_production | synthesis_judgement | 10 | 0.97 | 0.82 | 0.74 | 0.9 | 1.0 | 55029.71 |
| default_production | than_cu_interpretation | 10 | 0.7 | 0.66 | 0.63 | 1.0 | 0.95 | 17303.8 |
| default_production | topic_house_plus_relations | 10 | 0.85 | 0.82 | 0.73 | 1.0 | 0.975 | 41385.19 |

## Per-question results

### default_production

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1800.79 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 2 | 15191.31 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 1.0 | True | 1.0 | 2 | 12267.37 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 14213.19 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 4 | 11455.69 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 3 | 18192.58 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 2 | 17058.28 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.4 | 0.2 | True | 1.0 | 4 | 9118.52 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 13853.46 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 4 | 11717.36 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 908.47 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.5 | 0.2 | True | 0.75 | 1 | 14780.97 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 0.6 | 0.5 | 0.4 | True | 1.0 | 4 | 9078.5 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 1.0 | True | 1.0 | 3 | 14593.81 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.5 | 0.4 | 0.2 | True | 1.0 | 3 | 10375.87 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 19849.22 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.6 | 0.5 | 0.4 | True | 1.0 | 5 | 15808.89 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 0.5 | 0.2 | 0.0 | True | 1.0 | 3 | 7365.92 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 11269.12 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 13671.59 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 862.68 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 3 | 20339.49 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 18059.68 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 25702.11 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 11666.44 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 5 | 23534.3 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.2 | 0.2 | True | 1.0 | 2 | 10164.48 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.2 | 0.2 | 0.2 | True | 1.0 | 3 | 18362.93 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 7 | 22983.93 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 29366.03 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 810.69 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 5 | 19409.22 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 11690.1 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 2 | 23433.79 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 3 | 18103.41 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.9 | 1.0 | True | 1.0 | 5 | 24451.73 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 4 | 20665.42 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 0.2 | 0.2 | 0.0 | True | 1.0 | 4 | 7522.54 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.2 | 0.2 | 0.0 | True | 1.0 | 3 | 22005.5 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 0.9 | 0.9 | 0.8 | True | 1.0 | 3 | 20564.71 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 1020.01 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.6 | True | 0.75 | 1 | 15736.79 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 0.2 | 0.2 | 0.0 | True | 1.0 | 1 | 12877.91 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 3 | 15738.5 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.5 | 0.0 | True | 1.0 | 3 | 11561.24 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 3 | 24792.86 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 4 | 19282.91 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 0.6 | 0.5 | True | 1.0 | 4 | 7940.31 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 11836.06 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 20175.82 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 978.99 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.3 | 0.0 | True | 1.0 | 2 | 14840.23 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 15608.77 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 4 | 16074.22 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 3 | 26483.32 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 0.5 | 0.4 | 0.2 | True | 1.0 | 2 | 15362.46 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 15260.97 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.5 | 0.4 | True | 0.75 | 1 | 17521.86 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 13957.23 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 76027.26 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 0.8 | 0.8 | False | 0.75 | 1 | 1785.87 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 9 | 17349.16 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 0.5 | 0.5 | 0.2 | True | 0.75 | 1 | 10651.31 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 16077.83 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 4 | 7841.73 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | True | 0.75 | 1 | 27425.41 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.5 | 0.33 | True | 1.0 | 3 | 15856.91 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 3 | 14332.04 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 4 | 14939.67 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 16354.12 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 844.45 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 2 | 15786.36 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 0.9 | 1.0 | 1.0 | True | 1.0 | 2 | 11273.72 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 1.0 | True | 1.0 | 3 | 14260.92 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 9 | 13355.16 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 3 | 17135.51 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 2 | 10006.29 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.2 | 0.2 | True | 1.0 | 4 | 7733.86 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 56440.77 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.4 | 0.2 | True | 1.0 | 3 | 14652.74 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1023.53 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 0.9 | 0.8 | 0.7 | False | 1.0 | 3 | 4953.97 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.6 | 0.7 | True | 1.0 | 2 | 12108.95 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 3 | 14434.79 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 10764.18 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 6 | 15684.4 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.8 | True | 1.0 | 3 | 16149.43 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.0 | 0.0 | True | 1.0 | 1 | 57301.76 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 0.5 | 0.5 | 0.0 | True | 1.0 | 2 | 22535.4 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.5 | 0.2 | False | 1.0 | 3 | 5329.59 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.5 | None | None | None | 1 | 1423.66 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 2 | 15554.68 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 0.0 | 0.0 | 0.0 | True | 0.75 | 1 | 16379.94 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 16880.36 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 4 | 10430.32 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 2 | 10944.06 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.6 | 0.4 | 0.2 | True | 1.0 | 3 | 11500.09 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 0.6 | 0.2 | 0.2 | True | 1.0 | 6 | 11375.81 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 1.0 | True | 0.75 | 1 | 11865.14 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 4 | 12491.58 |  |
