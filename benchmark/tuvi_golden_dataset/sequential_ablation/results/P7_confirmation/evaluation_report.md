# W6 Evaluation report: sequential_p7_confirmation

- Dataset: `D:\UNI_STUDY\Year3\Semester3\TextMining\tuvi-battu-graphrag\benchmark\tuvi_golden_dataset\release\tuviqa_v1_release.jsonl`
- Dataset items: 100
- Configs: 1
- Judge backend: `gemini`
- Judge protocol: `blind-v2`
- Started: 2026-09-15T02:09:32.060995Z
- Completed: 2026-09-15T02:30:04.630503Z
- Notes: Confirmation only: replay the locked P1--P6 winner live over all 100 TuViQA items. This is not a new selection phase and must not change any factor.
- Run status: `completed`

## Run identity and provenance

- Identity SHA-256: `26aafefaf4ac7af161eb23c485d4e46520da741d58452cd4223a6b02f173309b`
- Dataset SHA-256: `90376a87cec29cc22e93dc71b41e054ed2f0183bc515a52aa461fecd43cc008c`
- Manifest SHA-256: `19be7b6edeb03317ec7f0f5eb9143fc7987d571f9bfd2dbc42f332abe9c90361`
- Evaluator SHA-256: `c1b655e2a21c01e50e56de710f87c6a1b289ca5c44b9b5329de50070c96aea7e`
- Git SHA: `2c3f944c2c1a48f42aa62c31a1e4aaf571eaa764`
- Git dirty: `True`
- Judge model: `gemini-3.1-flash-lite-preview`
- Checkpoint: `benchmark\tuvi_golden_dataset\sequential_ablation\results\P7_confirmation\checkpoints\evaluation_checkpoint.json`

## Execution completeness

- Expected pairs: 100
- Completed pairs: 100
- Failed pairs: 0
- Executed pairs: 11
- Resumed pairs: 89

> **Metric policy:** Sequential blind Judge v2 scores Faithfulness and Answer Relevancy. AI-judged Context Recall is not a headline metric.

## Overall metrics

| Config | Status | Items | Faithfulness | Answer relevancy | Latency p95 ms | Invalid markers |
|---|---:|---:|---:|---:|---:|---:|
| p7_final_gemini_prompt1 | completed | 100 | 0.936 | 0.883 | 138990.49 | 0 |

## Failure and fallback summary

| Config | Failed | Generation backend fallback | Judge failure | No context | Retrieval backend fallback | Citation fallback |
|---|---:|---:|---:|---:|---:|---:|
| p7_final_gemini_prompt1 | 0 | 0 | 0 | 0 | 0 | 2 |

## Ablation analysis

- Baseline config: `baseline_graph_sparse_rrf`
- Preliminary recommendation: `p7_final_gemini_prompt1`
  - Preliminary heuristic ranks configs by context recall, citation coverage, faithfulness, answer relevancy, graph hit rate, and a small p95 latency penalty.
  - Selected `p7_final_gemini_prompt1` with context_recall_avg=None, citation_coverage_rate=0.9973, p95_latency_ms=138990.49.
  - Treat this as a smoke/first-pass recommendation until official Gemini judge and full dataset runs are complete.

### Context recall ranking

| Rank | Config | Value |
|---:|---|---:|

### Citation coverage ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | p7_final_gemini_prompt1 | 0.9973 |

### Graph hit ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | p7_final_gemini_prompt1 | 0.967 |

### p95 latency ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | p7_final_gemini_prompt1 | 138990.49 |

### Retrieval miss summary

| Config | Miss count | Example item IDs |
|---|---:|---|
| p7_final_gemini_prompt1 | 1 | TVQA-061 |

### Rerank miss summary

| Config | Miss count | Example item IDs |
|---|---:|---|
| p7_final_gemini_prompt1 | 0 |  |

## Metrics by question complexity

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| p7_final_gemini_prompt1 | Direct | 10 | 1.0 | 0.96 | None | 0.0 | 0.75 | 10696.94 |
| p7_final_gemini_prompt1 | One-hop | 46 | 0.9261 | 0.8478 | None | 0.9783 | 1.0 | 142763.12 |
| p7_final_gemini_prompt1 | Two-hop | 44 | 0.9318 | 0.9023 | None | 0.9773 | 1.0 | 127118.12 |

## Metrics by question family

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| p7_final_gemini_prompt1 | core_identity | 10 | 1.0 | 0.96 | None | 0.0 | 0.75 | 10696.94 |
| p7_final_gemini_prompt1 | dai_van_interpretation | 10 | 0.91 | 0.72 | None | 1.0 | 1.0 | 102902.96 |
| p7_final_gemini_prompt1 | menh_cuc_relation | 10 | 0.93 | 0.93 | None | 1.0 | 1.0 | 96682.54 |
| p7_final_gemini_prompt1 | menh_house_interpretation | 10 | 0.94 | 0.81 | None | 0.9 | 1.0 | 178530.74 |
| p7_final_gemini_prompt1 | menh_tam_hop | 10 | 0.87 | 0.9 | None | 1.0 | 1.0 | 127025.72 |
| p7_final_gemini_prompt1 | menh_xung_chieu | 10 | 0.92 | 0.94 | None | 1.0 | 1.0 | 116189.45 |
| p7_final_gemini_prompt1 | special_state_interpretation | 10 | 0.83 | 0.85 | None | 1.0 | 1.0 | 147844.85 |
| p7_final_gemini_prompt1 | synthesis_judgement | 10 | 0.98 | 0.83 | None | 0.9 | 1.0 | 156308.34 |
| p7_final_gemini_prompt1 | than_cu_interpretation | 10 | 0.98 | 0.92 | None | 1.0 | 1.0 | 137871.37 |
| p7_final_gemini_prompt1 | topic_house_plus_relations | 10 | 1.0 | 0.97 | None | 1.0 | 1.0 | 112921.24 |

## Per-question results

### p7_final_gemini_prompt1

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4278.17 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 4 | 206692.77 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 136832.9 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | None | True | 1.0 | 2 | 111042.48 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 4 | 166671.4 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 126856.32 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 97734.93 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.2 | None | True | 1.0 | 3 | 108143.36 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 105424.49 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 98102.82 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4152.97 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.5 | None | True | 1.0 | 2 | 125057.76 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 4 | 119449.29 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | None | True | 1.0 | 2 | 79131.51 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.5 | 0.2 | None | True | 1.0 | 2 | 83349.59 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | None | True | 1.0 | 4 | 105993.06 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 1.0 | None | True | 1.0 | 4 | 87680.29 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 2 | 93270.59 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 85433.23 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | None | True | 1.0 | 7 | 106661.35 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4268.75 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | None | True | 1.0 | 5 | 144110.48 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 0.8 | 1.0 | None | True | 1.0 | 5 | 96846.08 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 65982.71 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.8 | None | True | 1.0 | 5 | 87397.38 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | None | True | 1.0 | 6 | 126453.71 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.8 | None | True | 1.0 | 5 | 86883.06 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.5 | None | True | 1.0 | 4 | 89730.51 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 7 | 109941.82 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | None | True | 1.0 | 7 | 165353.8 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 2195.05 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 5 | 138489.12 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 5 | 94271.66 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 0.8 | 1.0 | None | True | 1.0 | 2 | 73030.08 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 0.8 | 1.0 | None | True | 1.0 | 6 | 102158.64 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 0.9 | 1.0 | None | True | 1.0 | 5 | 123387.85 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | None | True | 1.0 | 2 | 117926.52 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 0.5 | 1.0 | None | True | 1.0 | 3 | 96498.03 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | None | True | 1.0 | 3 | 100747.11 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 94670.8 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 15071.35 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 9 | 83983.63 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 4 | 88541.19 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | None | True | 1.0 | 5 | 71515.71 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 5 | 124834.63 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 0.2 | 0.8 | None | True | 1.0 | 4 | 104253.64 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | None | True | 1.0 | 6 | 114066.37 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 5 | 95787.13 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 7 | 78809.15 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 145252.77 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 2370.57 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.5 | None | True | 1.0 | 3 | 129876.14 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 2 | 92835.83 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | None | True | 1.0 | 2 | 76878.5 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 0.8 | 1.0 | None | True | 1.0 | 4 | 97604.71 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 83089.52 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 83056.78 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 4 | 83605.08 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 85266.05 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.8 | None | True | 1.0 | 2 | 125271.13 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 0.6 | None | False | 0.75 | 1 | 5350.43 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 6 | 80108.78 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 5 | 138721.02 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 74906.84 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 5 | 71107.21 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.8 | None | True | 1.0 | 4 | 86798.23 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 87021.55 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 3 | 78569.15 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | None | True | 1.0 | 5 | 90612.92 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.9 | None | True | 1.0 | 4 | 95944.3 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 2910.82 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.9 | None | True | 1.0 | 4 | 101327.3 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 2 | 129580.08 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | None | True | 1.0 | 2 | 73374.56 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 0.8 | 1.0 | None | True | 1.0 | 4 | 85555.12 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 127164.32 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 1.0 | None | True | 1.0 | 4 | 82940.89 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 4 | 92269.57 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 90694.78 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.8 | None | True | 1.0 | 2 | 95785.56 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3686.99 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | None | False | 1.0 | 2 | 113258.62 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 5 | 119585.21 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 0.5 | 0.5 | None | True | 1.0 | 4 | 70489.73 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 0.8 | 1.0 | None | True | 1.0 | 5 | 97608.85 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 0.8 | 1.0 | None | True | 1.0 | 6 | 99186.98 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 84080.94 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.5 | None | True | 1.0 | 3 | 88355.57 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 5 | 115358.94 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.0 | None | False | 1.0 | 3 | 120976.23 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 2761.5 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.9 | None | True | 1.0 | 2 | 83649.22 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 4 | 124998.73 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | None | True | 1.0 | 2 | 73065.88 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | None | True | 1.0 | 5 | 88167.52 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | None | True | 1.0 | 2 | 85993.51 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | None | True | 1.0 | 2 | 85272.91 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.6 | None | True | 1.0 | 5 | 87005.58 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 89210.02 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.8 | None | True | 1.0 | 4 | 95976.83 |  |
