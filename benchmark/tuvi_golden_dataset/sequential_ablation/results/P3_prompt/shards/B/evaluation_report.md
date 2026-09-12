# W6 Evaluation report: sequential_p3_prompt_shard_b

- Dataset: `D:\UNI_STUDY\Year3\Semester3\TextMining\tuvi-battu-graphrag\benchmark\tuvi_golden_dataset\release\tuviqa_v1_release.jsonl`
- Dataset items: 100
- Configs: 1
- Judge backend: `gemini`
- Judge protocol: `blind-v2`
- Started: 2026-09-12T03:33:28.373740Z
- Completed: 2026-09-12T03:42:03.931561Z
- Notes: Only prompt_template_id changes. Prompt 2 keeps grounded-v2; structured-v3 is excluded by the pre-registered three-prompt shortlist. Two-person official shard assigned to B.
- Run status: `completed`

## Run identity and provenance

- Identity SHA-256: `3727d34d0a36cd20f54028362424892a1639e9c628df21a5a665dbc7f8e2372f`
- Dataset SHA-256: `90376a87cec29cc22e93dc71b41e054ed2f0183bc515a52aa461fecd43cc008c`
- Manifest SHA-256: `e2f3a565adf2b57ffdabb7bc4f97af471ef40c339762dfe827953c12d167ad39`
- Evaluator SHA-256: `a69fb4de27b0be1531f7972e8689f891cfac71a769934624e24d136420ef5f5f`
- Git SHA: `a2a2bb7d5d1e67605b5740596eafa2ee16758551`
- Git dirty: `False`
- Judge model: `gemini-3.1-flash-lite-preview`
- Checkpoint: `benchmark\tuvi_golden_dataset\sequential_ablation\results\P3_prompt\shards\B\checkpoints\evaluation_checkpoint.json`

## Execution completeness

- Expected pairs: 100
- Completed pairs: 100
- Failed pairs: 0
- Executed pairs: 100
- Resumed pairs: 0

> **Metric policy:** Sequential blind Judge v2 scores only Faithfulness and Answer Relevancy. Citation Evidence F1 is rule-based from cited chunks and gold-span provenance; AI-judged Context Recall is not a headline metric.

## Overall metrics

| Config | Status | Items | Faithfulness | Answer relevancy | Citation Evidence F1 | Latency p95 ms | Invalid markers |
|---|---:|---:|---:|---:|---:|---:|---:|
| p3_prompt_3 | completed | 100 | 0.8228 | 0.856 | 0.0264 | 4986.02 | 0 |

## Failure and fallback summary

| Config | Failed | Generation backend fallback | Judge failure | No context | Retrieval backend fallback | Citation fallback |
|---|---:|---:|---:|---:|---:|---:|
| p3_prompt_3 | 0 | 0 | 0 | 0 | 0 | 5 |

## Ablation analysis

- Baseline config: `baseline_graph_sparse_rrf`
- Preliminary recommendation: `p3_prompt_3`
  - Preliminary heuristic ranks configs by context recall, citation coverage, faithfulness, answer relevancy, graph hit rate, and a small p95 latency penalty.
  - Selected `p3_prompt_3` with context_recall_avg=None, citation_coverage_rate=0.989, p95_latency_ms=4986.02.
  - Treat this as a smoke/first-pass recommendation until official Gemini judge and full dataset runs are complete.

### Context recall ranking

| Rank | Config | Value |
|---:|---|---:|

### Citation coverage ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | p3_prompt_3 | 0.989 |

### Graph hit ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | p3_prompt_3 | 0.9121 |

### p95 latency ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | p3_prompt_3 | 4986.02 |

### Retrieval miss summary

| Config | Miss count | Example item IDs |
|---|---:|---|
| p3_prompt_3 | 2 | TVQA-061, TVQA-084 |

### Rerank miss summary

| Config | Miss count | Example item IDs |
|---|---:|---|
| p3_prompt_3 | 0 |  |

## Metrics by question complexity

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| p3_prompt_3 | Direct | 10 | 0.95 | 0.88 | None | 0.0 | 0.0 | 3447.64 |
| p3_prompt_3 | One-hop | 46 | 0.7583 | 0.8304 | None | 0.8696 | 1.0 | 5145.72 |
| p3_prompt_3 | Two-hop | 44 | 0.8614 | 0.8773 | None | 0.9773 | 1.0 | 4079.67 |

## Metrics by question family

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| p3_prompt_3 | core_identity | 10 | 0.95 | 0.88 | None | 0.0 | 0.0 | 3447.64 |
| p3_prompt_3 | dai_van_interpretation | 10 | 0.853 | 0.88 | None | 0.9 | 1.0 | 3268.98 |
| p3_prompt_3 | menh_cuc_relation | 10 | 0.53 | 0.76 | None | 0.8 | 1.0 | 4017.92 |
| p3_prompt_3 | menh_house_interpretation | 10 | 0.88 | 0.79 | None | 0.9 | 1.0 | 5384.78 |
| p3_prompt_3 | menh_tam_hop | 10 | 0.73 | 0.82 | None | 1.0 | 1.0 | 3800.82 |
| p3_prompt_3 | menh_xung_chieu | 10 | 0.76 | 0.81 | None | 1.0 | 1.0 | 4316.98 |
| p3_prompt_3 | special_state_interpretation | 10 | 0.935 | 0.88 | None | 0.9 | 1.0 | 4933.51 |
| p3_prompt_3 | synthesis_judgement | 10 | 0.92 | 0.9 | None | 0.9 | 1.0 | 4680.65 |
| p3_prompt_3 | than_cu_interpretation | 10 | 0.69 | 0.89 | None | 0.9 | 1.0 | 5216.07 |
| p3_prompt_3 | topic_house_plus_relations | 10 | 0.98 | 0.95 | None | 1.0 | 1.0 | 3970.84 |

## Per-question results

### p3_prompt_3

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 2466.88 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 2 | 4104.18 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 5 | 5086.6 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 0.8 | 1.0 | None | True | 1.0 | 2 | 3095.54 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 4 | 3021.6 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 0.2 | 0.4 | None | True | 1.0 | 4 | 2876.05 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 2937.81 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 0.2 | 0.0 | None | True | 1.0 | 3 | 2428.61 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 2 | 2817.14 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.2 | 0.5 | None | True | 1.0 | 3 | 3021.0 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 2164.84 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.5 | None | True | 1.0 | 3 | 3369.12 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | None | False | 1.0 | 3 | 3387.14 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 2986.19 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.8 | 1.0 | None | True | 1.0 | 4 | 2681.73 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | None | True | 1.0 | 3 | 2795.28 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.2 | 0.0 | None | True | 1.0 | 2 | 2667.51 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 2636.36 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 2684.31 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 2559.57 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 2279.02 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 2 | 3167.76 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 3073.73 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 0.0 | 0.5 | None | True | 1.0 | 4 | 3083.34 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 0.8 | 1.0 | None | True | 1.0 | 9 | 5165.43 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 0.5 | 0.8 | None | True | 1.0 | 4 | 3288.45 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.5 | None | True | 1.0 | 4 | 3033.52 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 3 | 2687.5 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 2770.05 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 2872.67 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1959.66 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 2395.78 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 0.5 | 1.0 | None | True | 1.0 | 3 | 2650.35 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | None | False | 1.0 | 4 | 2708.34 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 0.75 | 1.0 | None | True | 1.0 | 3 | 3086.8 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 0.8 | 1.0 | None | True | 1.0 | 2 | 3080.48 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.8 | None | True | 1.0 | 3 | 2976.1 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 2 | 3127.71 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.5 | None | True | 1.0 | 2 | 2898.83 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 2810.9 |  |
| TVQA-041 | completed | Direct | core_identity | True | 0.5 | 1.0 | None | None | None | 1 | 1723.63 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 5715.36 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 0.8 | 1.0 | None | True | 1.0 | 5 | 3093.17 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 0.0 | 0.5 | None | True | 1.0 | 3 | 3020.67 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.0 | None | False | 1.0 | 4 | 3176.8 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 0.8 | 1.0 | None | True | 1.0 | 4 | 3546.82 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 1.0 | None | True | 1.0 | 2 | 3970.83 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 2 | 3384.57 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 3822.49 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 2908.19 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 2268.91 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.0 | 0.0 | None | True | 1.0 | 3 | 4980.73 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 0.0 | 1.0 | None | True | 1.0 | 4 | 2824.31 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | None | True | 1.0 | 6 | 2635.15 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 3116.47 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 0.2 | 1.0 | None | True | 1.0 | 4 | 2719.24 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 3142.88 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 2958.36 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 2871.17 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | None | True | 1.0 | 2 | 3278.36 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 0.8 | None | False | 0.0 | 1 | 2958.69 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 2982.21 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.5 | None | True | 1.0 | 5 | 4579.34 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 0.5 | 1.0 | None | True | 1.0 | 2 | 2642.69 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 2879.77 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 4008.63 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 3211.37 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 2578.6 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 3040.9 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 4003.85 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3772.36 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 3689.01 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 0.0 | 1.0 | None | True | 1.0 | 2 | 3869.84 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 0.0 | 0.5 | None | False | 1.0 | 4 | 4043.88 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 4356.05 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 0.8 | 1.0 | None | True | 1.0 | 3 | 2925.15 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 0.2 | 0.8 | None | True | 1.0 | 3 | 4600.19 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 0.33 | 1.0 | None | True | 1.0 | 2 | 2394.38 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 2728.76 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 2603.67 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 2274.48 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.6 | None | False | 1.0 | 2 | 2798.93 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 0.6 | 1.0 | None | True | 1.0 | 3 | 3312.28 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.5 | None | True | 1.0 | 2 | 2996.81 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 2 | 2793.32 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 2810.8 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 1.0 | None | True | 1.0 | 4 | 3247.35 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 2963.11 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 5 | 4092.21 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.5 | None | False | 1.0 | 4 | 5234.4 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.0 | None | None | None | 1 | 3050.77 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 3 | 2900.96 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 4 | 5322.0 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 0.2 | 0.8 | None | True | 1.0 | 4 | 3986.19 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 5 | 4650.05 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.2 | None | True | 1.0 | 4 | 3496.68 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 1.0 | None | True | 1.0 | 3 | 2962.75 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | None | False | 1.0 | 3 | 2491.29 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 2502.43 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 2622.58 |  |
