# W6 Evaluation report: sequential_p5_prompt_shard_b

- Dataset: `D:\UNI_STUDY\Year3\Semester3\TextMining\tuvi-battu-graphrag\benchmark\tuvi_golden_dataset\release\tuviqa_v1_release.jsonl`
- Dataset items: 100
- Configs: 1
- Judge backend: `gemini`
- Judge protocol: `blind-v2`
- Started: 2026-09-12T13:59:45.329669Z
- Completed: 2026-09-12T14:09:36.220272Z
- Notes: Only prompt_template_id changes on the P4-locked final context. Two-person official shard assigned to B.
- Run status: `completed`

## Run identity and provenance

- Identity SHA-256: `19f62f3121d8b395cc1f895bbf2da5f08155ec3075e41ea31c487aff8adbb4d1`
- Dataset SHA-256: `90376a87cec29cc22e93dc71b41e054ed2f0183bc515a52aa461fecd43cc008c`
- Manifest SHA-256: `e6e2dc6929cbb37b313405dcf906213e3d33613692cc647a301a46c01d72837f`
- Evaluator SHA-256: `a69fb4de27b0be1531f7972e8689f891cfac71a769934624e24d136420ef5f5f`
- Git SHA: `7d9f4b7294968540ce24d53f1cecccfd28d1c03b`
- Git dirty: `True`
- Judge model: `gemini-3.1-flash-lite-preview`
- Checkpoint: `benchmark\tuvi_golden_dataset\sequential_ablation\results\P5_prompt_final\shards\B\checkpoints\evaluation_checkpoint.json`

## Execution completeness

- Expected pairs: 100
- Completed pairs: 100
- Failed pairs: 0
- Executed pairs: 100
- Resumed pairs: 0

> **Metric policy:** Sequential blind Judge v2 scores Faithfulness and Answer Relevancy. AI-judged Context Recall is not a headline metric.

## Overall metrics

| Config | Status | Items | Faithfulness | Answer relevancy | Latency p95 ms | Invalid markers |
|---|---:|---:|---:|---:|---:|---:|
| p5_prompt_3 | completed | 100 | 0.886 | 0.894 | 6064.77 | 0 |

## Failure and fallback summary

| Config | Failed | Generation backend fallback | Judge failure | No context | Retrieval backend fallback | Citation fallback |
|---|---:|---:|---:|---:|---:|---:|
| p5_prompt_3 | 0 | 0 | 0 | 0 | 0 | 5 |

## Ablation analysis

- Baseline config: `baseline_graph_sparse_rrf`
- Preliminary recommendation: `p5_prompt_3`
  - Preliminary heuristic ranks configs by context recall, citation coverage, faithfulness, answer relevancy, graph hit rate, and a small p95 latency penalty.
  - Selected `p5_prompt_3` with context_recall_avg=None, citation_coverage_rate=0.989, p95_latency_ms=6064.77.
  - Treat this as a smoke/first-pass recommendation until official Gemini judge and full dataset runs are complete.

### Context recall ranking

| Rank | Config | Value |
|---:|---|---:|

### Citation coverage ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | p5_prompt_3 | 0.989 |

### Graph hit ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | p5_prompt_3 | 0.967 |

### p95 latency ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | p5_prompt_3 | 6064.77 |

### Retrieval miss summary

| Config | Miss count | Example item IDs |
|---|---:|---|
| p5_prompt_3 | 1 | TVQA-061 |

### Rerank miss summary

| Config | Miss count | Example item IDs |
|---|---:|---|
| p5_prompt_3 | 0 |  |

## Metrics by question complexity

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| p5_prompt_3 | Direct | 10 | 0.95 | 0.98 | None | 0.0 | 0.0 | 3843.52 |
| p5_prompt_3 | One-hop | 46 | 0.8793 | 0.8761 | None | 0.9783 | 1.0 | 5869.55 |
| p5_prompt_3 | Two-hop | 44 | 0.8784 | 0.8932 | None | 0.9773 | 1.0 | 7097.54 |

## Metrics by question family

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| p5_prompt_3 | core_identity | 10 | 0.95 | 0.98 | None | 0.0 | 0.0 | 3843.52 |
| p5_prompt_3 | dai_van_interpretation | 10 | 0.84 | 0.78 | None | 1.0 | 1.0 | 4765.56 |
| p5_prompt_3 | menh_cuc_relation | 10 | 0.81 | 0.83 | None | 1.0 | 1.0 | 5167.06 |
| p5_prompt_3 | menh_house_interpretation | 10 | 0.9 | 0.85 | None | 0.9 | 1.0 | 5328.43 |
| p5_prompt_3 | menh_tam_hop | 10 | 0.82 | 0.81 | None | 1.0 | 1.0 | 6709.95 |
| p5_prompt_3 | menh_xung_chieu | 10 | 0.94 | 0.98 | None | 1.0 | 1.0 | 8321.76 |
| p5_prompt_3 | special_state_interpretation | 10 | 1.0 | 0.98 | None | 1.0 | 1.0 | 5008.04 |
| p5_prompt_3 | synthesis_judgement | 10 | 0.905 | 0.92 | None | 0.9 | 1.0 | 6381.85 |
| p5_prompt_3 | than_cu_interpretation | 10 | 0.775 | 0.89 | None | 1.0 | 1.0 | 6006.02 |
| p5_prompt_3 | topic_house_plus_relations | 10 | 0.92 | 0.92 | None | 1.0 | 1.0 | 4377.62 |

## Per-question results

### p5_prompt_3

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 2298.94 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 2819.69 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 2869.46 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | None | True | 1.0 | 3 | 2868.17 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 3 | 3034.87 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 0.2 | 0.0 | None | True | 1.0 | 9 | 7188.84 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 3069.02 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.5 | None | True | 1.0 | 2 | 2762.82 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 1 | 3506.17 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.5 | 0.8 | None | True | 1.0 | 5 | 3510.43 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 2275.27 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 3 | 5968.56 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | None | True | 1.0 | 3 | 2844.64 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 2614.83 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 2 | 2971.17 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 3087.42 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.8 | None | True | 1.0 | 4 | 3693.44 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 2 | 3887.19 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 4005.83 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 4498.09 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3862.29 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 3 | 3556.25 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 4502.67 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 0.5 | 0.5 | None | True | 1.0 | 6 | 2724.4 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 2731.49 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | None | True | 1.0 | 5 | 2761.33 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 1.0 | None | True | 1.0 | 5 | 6580.17 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 2718.33 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 3405.67 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.9 | None | True | 1.0 | 4 | 3965.44 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 2593.5 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 5 | 2744.93 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 0.5 | 1.0 | None | True | 1.0 | 4 | 3870.43 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | None | True | 1.0 | 2 | 3034.88 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 3467.87 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | None | True | 1.0 | 4 | 2952.77 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | None | True | 1.0 | 2 | 4296.22 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 2 | 5340.66 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.2 | 0.2 | None | True | 1.0 | 2 | 2848.02 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 4174.19 |  |
| TVQA-041 | completed | Direct | core_identity | True | 0.5 | 1.0 | None | None | None | 1 | 2966.41 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 2 | 3706.32 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 2 | 4206.67 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 0.8 | 1.0 | None | True | 1.0 | 5 | 5439.44 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 2662.03 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 0.8 | 1.0 | None | True | 1.0 | 3 | 2818.83 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.6 | 1.0 | None | True | 1.0 | 9 | 9746.7 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 1.0 | None | True | 1.0 | 3 | 2645.82 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 5 | 2469.82 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 3331.12 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 2471.19 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.2 | None | True | 1.0 | 3 | 3030.34 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 0.0 | 0.0 | None | True | 1.0 | 3 | 2723.34 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 0.8 | 1.0 | None | True | 1.0 | 4 | 2706.95 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 2684.57 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 0.6 | 1.0 | None | True | 1.0 | 2 | 3035.28 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 2802.4 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 0.0 | 0.0 | None | True | 1.0 | 3 | 3875.6 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 4681.81 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 0.75 | 1.0 | None | True | 1.0 | 3 | 3739.24 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 0.8 | None | False | 0.0 | 1 | 3121.71 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 3994.53 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 5938.07 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | None | True | 1.0 | 2 | 4031.77 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 2 | 4206.34 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 3712.11 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 3818.04 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 4062.65 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 2667.34 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.9 | None | True | 1.0 | 4 | 7923.1 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 2988.96 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | None | True | 1.0 | 2 | 2741.31 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 0.25 | 1.0 | None | True | 1.0 | 2 | 3681.46 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 4834.16 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 2943.08 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 6124.65 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 3032.68 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.5 | None | True | 1.0 | 2 | 2988.51 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 2941.95 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.8 | None | True | 1.0 | 3 | 3119.77 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 2873.57 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | None | False | 1.0 | 4 | 2970.27 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 2818.64 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 2934.68 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 3575.71 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 2778.44 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 3018.65 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 3 | 3036.22 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 2 | 2738.29 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.8 | None | False | 1.0 | 4 | 2794.57 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3820.58 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 0.8 | 1.0 | None | True | 1.0 | 2 | 4546.04 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 2 | 6061.62 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 0.0 | 0.0 | None | True | 1.0 | 3 | 3660.29 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 2 | 5663.98 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.5 | None | True | 1.0 | 3 | 4179.0 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | None | True | 1.0 | 2 | 3492.38 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 2 | 3588.14 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 3220.14 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 3989.22 |  |
