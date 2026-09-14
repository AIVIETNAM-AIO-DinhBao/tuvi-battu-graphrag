# W6 Evaluation report: local_llm_gemini_judge_sequential-p6-final

- Dataset: `benchmark/tuvi_golden_dataset/release/tuviqa_v1_release.jsonl`
- Dataset items: 100
- Configs: 3
- Judge backend: `gemini`
- Judge protocol: `blind-v2`
- Started: 2026-09-13T04:30:06.741233+00:00
- Completed: 2026-09-13T04:38:52.976475+00:00
- Notes: Local-LLM generation answers judged with GeminiEvaluationJudge protocol=blind-v2, summarize_evaluation_item, provenance Citation Evidence F1, and aggregate metric functions.
- Run status: `completed`

## Run identity and provenance

- Identity SHA-256: `ef8794feecbb6622d824d7574309e9655e9f917d0cfa764f5783981128c00175`
- Dataset SHA-256: `90376a87cec29cc22e93dc71b41e054ed2f0183bc515a52aa461fecd43cc008c`
- Manifest SHA-256: `9f60052e643085ba36790cfcf13da3701ffa9d9441e76079b5108b1d81a3e331`
- Evaluator SHA-256: `78dce3092a4e28ee915bbfdad61341d6f0ad1761070d0c12240ab7b5b4202464`
- Git SHA: `15b87f74ec9e94bfa07a272301d931c846d5ec3c`
- Git dirty: `True`
- Judge model: `gemini-3.1-flash-lite-preview`
- Checkpoint: `D:\UNI_STUDY\Year3\Semester3\TextMining\tuvi-battu-graphrag\benchmark\tuvi_golden_dataset\sequential_ablation\p6_kaggle\judge_final\checkpoints\evaluation_checkpoint.json`

## Execution completeness

- Expected pairs: 300
- Completed pairs: 300
- Failed pairs: 0
- Executed pairs: 300
- Resumed pairs: 0

> **Metric policy:** Sequential blind Judge v2 scores Faithfulness and Answer Relevancy. AI-judged Context Recall is not a headline metric.

## Overall metrics

| Config | Status | Items | Faithfulness | Answer relevancy | Latency p95 ms | Invalid markers |
|---|---:|---:|---:|---:|---:|---:|
| qwen25_7b__p6_frozen_context | completed | 100 | 0.435 | 0.577 | 164319.99 | 0 |
| gemini31_flash_lite__p6_frozen_context | completed | 100 | 0.938 | 0.839 | 162862.24 | 0 |
| gemma3_4b__p6_frozen_context | completed | 100 | 0.346 | 0.444 | 164261.92 | 0 |

## Failure and fallback summary

| Config | Failed | Generation backend fallback | Judge failure | No context | Retrieval backend fallback | Citation fallback |
|---|---:|---:|---:|---:|---:|---:|
| qwen25_7b__p6_frozen_context | 0 | 0 | 0 | 0 | 0 | 18 |
| gemini31_flash_lite__p6_frozen_context | 0 | 0 | 0 | 0 | 0 | 3 |
| gemma3_4b__p6_frozen_context | 0 | 0 | 0 | 0 | 0 | 9 |

## Metrics by question complexity

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| qwen25_7b__p6_frozen_context | Direct | 10 | 0.73 | 0.7 | None | 0.0 | 0.75 | 1800.48 |
| qwen25_7b__p6_frozen_context | One-hop | 46 | 0.4217 | 0.5522 | None | 0.5 | 1.0 | 174962.2 |
| qwen25_7b__p6_frozen_context | Two-hop | 44 | 0.3818 | 0.575 | None | 0.5682 | 1.0 | 149326.94 |
| gemini31_flash_lite__p6_frozen_context | Direct | 10 | 1.0 | 0.96 | None | 0.0 | 0.75 | 1939.23 |
| gemini31_flash_lite__p6_frozen_context | One-hop | 46 | 0.9283 | 0.7935 | None | 0.5 | 1.0 | 174233.07 |
| gemini31_flash_lite__p6_frozen_context | Two-hop | 44 | 0.9341 | 0.8591 | None | 0.5682 | 1.0 | 147764.59 |
| gemma3_4b__p6_frozen_context | Direct | 10 | 0.72 | 0.63 | None | 0.0 | 0.0 | 2049.59 |
| gemma3_4b__p6_frozen_context | One-hop | 46 | 0.2935 | 0.3652 | None | 0.5 | 1.0 | 176530.12 |
| gemma3_4b__p6_frozen_context | Two-hop | 44 | 0.3159 | 0.4841 | None | 0.5682 | 1.0 | 149099.73 |

## Metrics by question family

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| qwen25_7b__p6_frozen_context | core_identity | 10 | 0.73 | 0.7 | None | 0.0 | 0.75 | 1800.48 |
| qwen25_7b__p6_frozen_context | dai_van_interpretation | 10 | 0.14 | 0.25 | None | 0.6 | 1.0 | 150555.6 |
| qwen25_7b__p6_frozen_context | menh_cuc_relation | 10 | 0.27 | 0.39 | None | 0.3 | 1.0 | 112508.55 |
| qwen25_7b__p6_frozen_context | menh_house_interpretation | 10 | 0.62 | 0.64 | None | 0.5 | 1.0 | 181830.14 |
| qwen25_7b__p6_frozen_context | menh_tam_hop | 10 | 0.36 | 0.54 | None | 0.6 | 1.0 | 170062.01 |
| qwen25_7b__p6_frozen_context | menh_xung_chieu | 10 | 0.26 | 0.33 | None | 0.9 | 1.0 | 136428.97 |
| qwen25_7b__p6_frozen_context | special_state_interpretation | 10 | 0.36 | 0.69 | None | 0.5 | 1.0 | 143132.36 |
| qwen25_7b__p6_frozen_context | synthesis_judgement | 10 | 0.55 | 0.71 | None | 0.5 | 1.0 | 158033.9 |
| qwen25_7b__p6_frozen_context | than_cu_interpretation | 10 | 0.61 | 0.7 | None | 0.6 | 1.0 | 186273.79 |
| qwen25_7b__p6_frozen_context | topic_house_plus_relations | 10 | 0.45 | 0.82 | None | 0.3 | 1.0 | 136434.84 |
| gemini31_flash_lite__p6_frozen_context | core_identity | 10 | 1.0 | 0.96 | None | 0.0 | 0.75 | 1939.23 |
| gemini31_flash_lite__p6_frozen_context | dai_van_interpretation | 10 | 0.91 | 0.57 | None | 0.6 | 1.0 | 150005.92 |
| gemini31_flash_lite__p6_frozen_context | menh_cuc_relation | 10 | 0.93 | 0.87 | None | 0.3 | 1.0 | 111249.56 |
| gemini31_flash_lite__p6_frozen_context | menh_house_interpretation | 10 | 0.9 | 0.77 | None | 0.5 | 1.0 | 180991.17 |
| gemini31_flash_lite__p6_frozen_context | menh_tam_hop | 10 | 0.92 | 0.9 | None | 0.6 | 1.0 | 168362.42 |
| gemini31_flash_lite__p6_frozen_context | menh_xung_chieu | 10 | 0.94 | 0.82 | None | 0.9 | 1.0 | 136265.6 |
| gemini31_flash_lite__p6_frozen_context | special_state_interpretation | 10 | 0.88 | 0.82 | None | 0.5 | 1.0 | 143579.85 |
| gemini31_flash_lite__p6_frozen_context | synthesis_judgement | 10 | 1.0 | 0.88 | None | 0.5 | 1.0 | 156765.39 |
| gemini31_flash_lite__p6_frozen_context | than_cu_interpretation | 10 | 0.98 | 0.91 | None | 0.6 | 1.0 | 186044.24 |
| gemini31_flash_lite__p6_frozen_context | topic_house_plus_relations | 10 | 0.92 | 0.89 | None | 0.3 | 1.0 | 135681.62 |
| gemma3_4b__p6_frozen_context | core_identity | 10 | 0.72 | 0.63 | None | 0.0 | 0.0 | 2049.59 |
| gemma3_4b__p6_frozen_context | dai_van_interpretation | 10 | 0.3 | 0.34 | None | 0.6 | 1.0 | 150192.56 |
| gemma3_4b__p6_frozen_context | menh_cuc_relation | 10 | 0.11 | 0.21 | None | 0.3 | 1.0 | 112315.46 |
| gemma3_4b__p6_frozen_context | menh_house_interpretation | 10 | 0.19 | 0.26 | None | 0.5 | 1.0 | 182597.4 |
| gemma3_4b__p6_frozen_context | menh_tam_hop | 10 | 0.2 | 0.36 | None | 0.6 | 1.0 | 168953.54 |
| gemma3_4b__p6_frozen_context | menh_xung_chieu | 10 | 0.27 | 0.36 | None | 0.9 | 1.0 | 138030.33 |
| gemma3_4b__p6_frozen_context | special_state_interpretation | 10 | 0.42 | 0.46 | None | 0.5 | 1.0 | 145078.46 |
| gemma3_4b__p6_frozen_context | synthesis_judgement | 10 | 0.4 | 0.59 | None | 0.5 | 1.0 | 157132.62 |
| gemma3_4b__p6_frozen_context | than_cu_interpretation | 10 | 0.45 | 0.53 | None | 0.6 | 1.0 | 187463.7 |
| gemma3_4b__p6_frozen_context | topic_house_plus_relations | 10 | 0.4 | 0.7 | None | 0.3 | 1.0 | 136490.63 |

## Per-question results

### qwen25_7b__p6_frozen_context

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 470.27 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | None | False | 1.0 | 1 | 196237.04 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 0.5 | 1.0 | None | True | 1.0 | 1 | 119145.57 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 0.8 | 1.0 | None | False | 1.0 | 1 | 83285.12 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 1 | 132820.24 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | None | True | 1.0 | 9 | 186845.37 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | None | True | 1.0 | 1 | 145506.23 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 0.2 | 0.2 | None | True | 1.0 | 4 | 158504.87 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 0.5 | 1.0 | None | False | 1.0 | 1 | 108163.46 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.5 | 1.0 | None | True | 1.0 | 1 | 93339.79 |  |
| TVQA-011 | completed | Direct | core_identity | True | 0.5 | 0.8 | None | None | None | 1 | 427.32 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.6 | None | True | 1.0 | 1 | 125686.19 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.6 | None | False | 1.0 | 1 | 145792.45 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 0.0 | 0.5 | None | False | 1.0 | 1 | 69126.07 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.2 | 0.5 | None | False | 1.0 | 2 | 80427.92 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 0.2 | 0.2 | None | True | 1.0 | 9 | 104404.37 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.2 | 0.0 | None | True | 1.0 | 1 | 97865.64 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 0.0 | 0.0 | None | True | 1.0 | 1 | 89977.78 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 1.0 | None | False | 1.0 | 2 | 88162.06 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | None | False | 1.0 | 1 | 102899.53 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 407.89 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.5 | None | False | 1.0 | 2 | 143324.26 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.7 | None | True | 1.0 | 2 | 102989.94 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.5 | None | False | 1.0 | 1 | 76035.42 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 0.0 | 0.5 | None | True | 1.0 | 1 | 95329.6 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 0.2 | 0.4 | None | False | 1.0 | 9 | 122702.61 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.2 | 0.2 | None | True | 1.0 | 5 | 86390.27 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.2 | 0.2 | None | False | 1.0 | 1 | 83412.36 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 0.4 | 0.8 | None | True | 1.0 | 2 | 122837.65 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.9 | None | False | 1.0 | 9 | 166187.41 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 302.68 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.4 | None | True | 1.0 | 2 | 135879.24 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | None | False | 1.0 | 1 | 92186.68 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 0.5 | 0.8 | None | False | 1.0 | 1 | 72708.67 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 0.5 | 0.8 | None | False | 1.0 | 2 | 98536.33 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 0.2 | 0.4 | None | False | 1.0 | 1 | 119830.08 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 0.4 | 0.6 | None | True | 1.0 | 1 | 110011.1 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 0.0 | 0.5 | None | True | 1.0 | 1 | 97212.03 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.2 | 0.4 | None | True | 1.0 | 9 | 96965.47 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 0.6 | 0.8 | None | True | 1.0 | 1 | 100898.25 |  |
| TVQA-041 | completed | Direct | core_identity | True | 0.0 | 0.0 | None | None | None | 1 | 261.7 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 1 | 81629.24 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | None | False | 1.0 | 1 | 87007.8 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 0.0 | 0.0 | None | True | 1.0 | 1 | 71598.12 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 0.0 | 0.5 | None | True | 1.0 | 1 | 121217.42 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 0.2 | 0.4 | None | True | 1.0 | 1 | 104041.77 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.2 | 0.4 | None | True | 1.0 | 9 | 113390.3 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 0.2 | 0.4 | None | True | 1.0 | 2 | 96069.02 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 1.0 | None | False | 1.0 | 9 | 87761.53 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 0.4 | 1.0 | None | False | 1.0 | 1 | 148068.5 |  |
| TVQA-051 | completed | Direct | core_identity | True | 0.0 | 0.0 | None | None | None | 1 | 1013.85 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.0 | 0.2 | None | True | 1.0 | 5 | 125948.99 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 0.0 | 0.5 | None | True | 1.0 | 1 | 94385.97 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 0.2 | 0.4 | None | True | 1.0 | 2 | 77385.11 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 0.5 | 0.8 | None | False | 1.0 | 2 | 95937.32 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 0.2 | 0.8 | None | True | 1.0 | 2 | 83355.36 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 0.0 | 0.0 | None | True | 1.0 | 3 | 82191.9 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 0.2 | 0.2 | None | False | 1.0 | 1 | 84954.25 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 0.9 | 1.0 | None | False | 1.0 | 2 | 86249.22 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 0.2 | 0.6 | None | True | 1.0 | 1 | 124824.7 |  |
| TVQA-061 | completed | Direct | core_identity | False | 0.8 | 0.4 | None | False | 0.75 | 1 | 2444.08 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 0.8 | 1.0 | None | False | 1.0 | 1 | 80670.86 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 0.5 | 0.2 | None | True | 1.0 | 1 | 162275.69 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 0.2 | 0.2 | None | False | 1.0 | 1 | 112458.81 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 0.2 | 0.8 | None | True | 1.0 | 3 | 104802.15 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 0.2 | 0.4 | None | True | 1.0 | 3 | 128934.45 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 0.2 | 0.2 | None | True | 1.0 | 2 | 124415.58 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 0.4 | 0.2 | None | True | 1.0 | 1 | 116567.72 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 0.2 | 0.6 | None | True | 1.0 | 4 | 137437.57 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.8 | None | True | 1.0 | 2 | 141106.46 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 799.32 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.6 | None | False | 1.0 | 1 | 151873.02 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.8 | None | True | 1.0 | 1 | 192599.51 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 0.0 | 0.0 | None | False | 1.0 | 1 | 108809.58 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 0.2 | 0.4 | None | True | 1.0 | 1 | 109236.08 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 0.2 | 0.4 | None | True | 1.0 | 9 | 142748.73 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 0.0 | 0.2 | None | True | 1.0 | 7 | 125334.55 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 0.0 | 0.2 | None | True | 1.0 | 2 | 140839.83 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 0.5 | 1.0 | None | False | 1.0 | 2 | 135209.28 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 0.5 | 0.2 | None | True | 1.0 | 1 | 143580.68 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 715.58 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 0.4 | 0.6 | None | False | 1.0 | 7 | 164221.7 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 0.5 | 0.8 | None | False | 1.0 | 2 | 178542.36 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 0.0 | 0.0 | None | True | 1.0 | 2 | 112549.24 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 0.5 | 1.0 | None | False | 1.0 | 2 | 151569.55 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | None | False | 1.0 | 9 | 149549.02 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 0.6 | 0.8 | None | True | 1.0 | 7 | 115687.33 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 0.0 | 0.2 | None | False | 1.0 | 5 | 86625.6 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 0.0 | 0.8 | None | False | 1.0 | 2 | 115758.13 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 0.2 | 0.0 | None | False | 1.0 | 5 | 120110.04 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 934.26 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.7 | None | True | 1.0 | 1 | 82821.77 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 0.2 | 0.4 | None | True | 1.0 | 2 | 129117.37 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 0.0 | 0.5 | None | False | 1.0 | 1 | 71938.26 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 0.5 | 0.8 | None | False | 1.0 | 1 | 96073.88 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 0.6 | 0.8 | None | False | 1.0 | 8 | 84346.04 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.0 | 0.2 | None | False | 1.0 | 7 | 83964.8 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 0.2 | 0.4 | None | False | 1.0 | 1 | 83380.69 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 0.2 | 0.6 | None | False | 1.0 | 2 | 85740.41 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 0.5 | 0.8 | None | False | 1.0 | 1 | 96359.87 |  |

### gemini31_flash_lite__p6_frozen_context

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1089.79 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | None | False | 1.0 | 4 | 195916.73 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 2 | 118770.35 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | None | False | 1.0 | 2 | 80968.96 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 4 | 133630.11 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | None | True | 1.0 | 3 | 185058.62 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 145169.08 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.2 | None | True | 1.0 | 4 | 158410.71 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | False | 1.0 | 4 | 108571.88 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.8 | None | True | 1.0 | 3 | 92830.45 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1313.91 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 3 | 124163.49 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | None | False | 1.0 | 4 | 144729.33 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 0.5 | 0.8 | None | False | 1.0 | 2 | 67535.97 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.8 | None | False | 1.0 | 2 | 80999.04 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | None | True | 1.0 | 4 | 102983.8 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.6 | None | True | 1.0 | 4 | 99013.71 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 2 | 90469.77 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | False | 1.0 | 3 | 87310.26 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | None | False | 1.0 | 5 | 103409.29 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1033.65 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | None | False | 1.0 | 6 | 142911.81 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 103593.7 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | None | False | 1.0 | 2 | 74240.37 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 95204.48 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | None | False | 1.0 | 5 | 121557.08 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.5 | None | True | 1.0 | 3 | 84695.12 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.6 | None | False | 1.0 | 6 | 83077.51 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 6 | 122192.99 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | None | False | 1.0 | 7 | 165016.95 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1239.58 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.6 | None | True | 1.0 | 4 | 134319.99 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | None | False | 1.0 | 4 | 91872.62 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | None | False | 1.0 | 2 | 72012.54 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 0.8 | 1.0 | None | False | 1.0 | 6 | 97760.83 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | None | False | 1.0 | 6 | 118560.2 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.8 | None | True | 1.0 | 3 | 109869.42 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 5 | 96749.28 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.2 | 0.0 | None | True | 1.0 | 3 | 96102.67 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 101195.86 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1126.37 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | None | True | 1.0 | 4 | 81776.47 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | None | False | 1.0 | 5 | 87027.23 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | None | True | 1.0 | 4 | 70197.78 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.0 | None | True | 1.0 | 5 | 121389.63 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 0.8 | 1.0 | None | True | 1.0 | 3 | 102408.56 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 1.0 | None | True | 1.0 | 6 | 111960.21 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 94940.36 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | False | 1.0 | 5 | 86247.0 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | None | False | 1.0 | 3 | 146680.14 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1374.1 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.2 | None | True | 1.0 | 3 | 124166.89 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 9 | 92897.54 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.8 | None | True | 1.0 | 3 | 75982.89 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | None | False | 1.0 | 4 | 95808.88 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 82546.13 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 81486.5 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 0.5 | 0.5 | None | False | 1.0 | 4 | 82941.67 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | None | False | 1.0 | 3 | 86209.94 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.8 | None | True | 1.0 | 2 | 123441.35 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 0.6 | None | False | 0.75 | 1 | 1749.22 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 0.8 | 1.0 | None | False | 1.0 | 5 | 80885.52 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 5 | 161450.17 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | None | False | 1.0 | 3 | 110797.91 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | None | True | 1.0 | 3 | 103440.2 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 0.8 | 1.0 | None | True | 1.0 | 4 | 127109.87 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.5 | None | True | 1.0 | 4 | 123005.96 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 3 | 115827.22 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 136744.47 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | None | True | 1.0 | 5 | 140584.44 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 2094.7 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.9 | None | False | 1.0 | 3 | 151405.72 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 192575.86 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | None | False | 1.0 | 3 | 107654.41 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 5 | 109186.08 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | None | True | 1.0 | 2 | 140236.54 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 125383.56 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.2 | None | True | 1.0 | 4 | 139733.41 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | False | 1.0 | 3 | 134382.59 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.6 | None | True | 1.0 | 3 | 144139.32 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1298.26 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | None | False | 1.0 | 3 | 162748.83 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.8 | None | False | 1.0 | 6 | 178061.15 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.5 | None | True | 1.0 | 9 | 111619.09 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 0.6 | 1.0 | None | False | 1.0 | 5 | 151720.54 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | None | False | 1.0 | 7 | 147955.96 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 116161.46 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.0 | None | False | 1.0 | 2 | 85871.26 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | False | 1.0 | 5 | 114874.28 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.8 | None | False | 1.0 | 4 | 119222.99 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1379.06 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.9 | None | True | 1.0 | 2 | 82448.32 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.6 | None | True | 1.0 | 3 | 127985.47 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | None | False | 1.0 | 2 | 71557.41 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | None | False | 1.0 | 5 | 97545.29 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | None | False | 1.0 | 3 | 83864.77 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.8 | None | False | 1.0 | 2 | 83703.84 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.6 | None | False | 1.0 | 4 | 81062.21 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | False | 1.0 | 4 | 85189.21 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.8 | None | False | 1.0 | 3 | 96645.63 |  |

### gemma3_4b__p6_frozen_context

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 673.61 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 0.0 | 0.0 | None | False | 1.0 | 6 | 197605.77 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 0.5 | 0.6 | None | True | 1.0 | 1 | 119111.85 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 0.2 | 0.2 | None | False | 1.0 | 8 | 83026.66 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 0.5 | 0.5 | None | True | 1.0 | 2 | 133792.05 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 0.2 | 0.4 | None | True | 1.0 | 8 | 185072.19 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 0.2 | 0.4 | None | True | 1.0 | 7 | 147305.86 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 0.2 | 0.0 | None | True | 1.0 | 1 | 157456.4 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 0.0 | 0.5 | None | False | 1.0 | 9 | 108285.13 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.2 | 0.6 | None | True | 1.0 | 2 | 93070.61 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1564.47 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 0.0 | 0.2 | None | True | 1.0 | 6 | 125345.34 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 0.2 | 0.4 | None | False | 1.0 | 4 | 146445.68 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 0.0 | 0.2 | None | False | 1.0 | 5 | 69322.49 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.5 | 0.8 | None | False | 1.0 | 5 | 81027.32 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 0.0 | 0.0 | None | True | 1.0 | 7 | 107537.24 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.2 | 0.2 | None | True | 1.0 | 7 | 99004.69 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 0.2 | 0.6 | None | True | 1.0 | 4 | 90046.19 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 0.4 | 1.0 | None | False | 1.0 | 7 | 88625.76 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 0.8 | 1.0 | None | False | 1.0 | 8 | 104887.34 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 914.58 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 0.0 | 0.0 | None | False | 1.0 | 9 | 145248.95 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 8 | 103273.17 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 0.0 | 0.0 | None | False | 1.0 | 3 | 74810.21 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 0.2 | 0.0 | None | True | 1.0 | 3 | 96869.56 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 0.2 | 0.4 | None | False | 1.0 | 8 | 121374.46 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.5 | 0.6 | None | True | 1.0 | 5 | 88198.23 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.0 | 0.0 | None | False | 1.0 | 5 | 85225.87 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 0.4 | 0.6 | None | True | 1.0 | 2 | 124766.83 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 0.4 | 0.6 | None | False | 1.0 | 8 | 164415.41 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 331.62 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.0 | 0.2 | None | True | 1.0 | 7 | 139154.43 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.6 | None | False | 1.0 | 8 | 92033.57 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 0.5 | 0.8 | None | False | 1.0 | 5 | 72726.03 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 0.2 | 0.2 | None | False | 1.0 | 3 | 100507.36 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 0.2 | 0.4 | None | False | 1.0 | 6 | 122529.54 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 0.0 | 0.2 | None | True | 1.0 | 8 | 112024.06 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 0.0 | 0.2 | None | True | 1.0 | 4 | 99680.72 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.0 | 0.2 | None | True | 1.0 | 1 | 98341.0 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 0.4 | 0.6 | None | True | 1.0 | 8 | 103683.78 |  |
| TVQA-041 | completed | Direct | core_identity | True | 0.0 | 0.0 | None | None | None | 1 | 373.07 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 0.0 | 0.2 | None | True | 1.0 | 8 | 82120.93 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.7 | None | False | 1.0 | 2 | 88603.6 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 0.2 | 0.2 | None | True | 1.0 | 8 | 73294.9 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 0.0 | 0.0 | None | True | 1.0 | 4 | 123249.67 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 0.0 | 0.2 | None | True | 1.0 | 7 | 104218.18 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.5 | None | True | 1.0 | 8 | 114943.85 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 6 | 93513.59 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 1.0 | None | False | 1.0 | 8 | 87617.53 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.7 | None | False | 1.0 | 8 | 148231.44 |  |
| TVQA-051 | completed | Direct | core_identity | True | 0.0 | 0.0 | None | None | None | 1 | 1286.47 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.2 | None | True | 1.0 | 1 | 126694.85 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 0.0 | 0.5 | None | True | 1.0 | 1 | 93959.66 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 0.2 | 0.5 | None | True | 1.0 | 3 | 75405.79 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.6 | None | False | 1.0 | 2 | 96677.1 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 0.2 | 0.6 | None | True | 1.0 | 7 | 87785.43 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | None | True | 1.0 | 8 | 82851.26 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 0.2 | 0.2 | None | False | 1.0 | 5 | 83589.92 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 0.2 | 0.8 | None | False | 1.0 | 4 | 89364.36 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 0.2 | 0.4 | None | True | 1.0 | 9 | 124077.69 |  |
| TVQA-061 | completed | Direct | core_identity | False | 0.2 | 0.0 | None | False | 0.0 | 1 | 1904.85 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 0.5 | 0.8 | None | False | 1.0 | 3 | 80383.61 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 0.2 | 0.2 | None | True | 1.0 | 2 | 161344.48 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 0.0 | 0.0 | None | False | 1.0 | 1 | 111290.66 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 0.2 | 0.2 | None | True | 1.0 | 3 | 105593.29 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 0.2 | 0.4 | None | True | 1.0 | 3 | 127216.0 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 0.2 | 0.4 | None | True | 1.0 | 4 | 124353.63 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 0.2 | 0.4 | None | True | 1.0 | 4 | 116353.98 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.5 | None | True | 1.0 | 8 | 136739.86 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 0.4 | 0.6 | None | True | 1.0 | 9 | 142209.54 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1015.49 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 0.0 | 0.2 | None | False | 1.0 | 4 | 151933.0 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 0.2 | 0.5 | None | True | 1.0 | 2 | 193061.28 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 0.0 | 0.2 | None | False | 1.0 | 2 | 111042.99 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 0.2 | 0.6 | None | True | 1.0 | 7 | 109942.23 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 0.2 | 0.2 | None | True | 1.0 | 7 | 145140.7 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 0.0 | 0.2 | None | True | 1.0 | 6 | 126693.57 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 0.2 | 0.0 | None | True | 1.0 | 4 | 141314.53 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 0.5 | 1.0 | None | False | 1.0 | 9 | 136186.01 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 0.4 | 0.8 | None | True | 1.0 | 7 | 147623.52 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 784.5 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.2 | None | False | 1.0 | 6 | 164253.84 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 0.4 | 0.6 | None | False | 1.0 | 2 | 180622.22 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 0.0 | 0.0 | None | True | 1.0 | 1 | 113153.93 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 0.8 | 1.0 | None | False | 1.0 | 6 | 154312.79 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 0.6 | 0.5 | None | False | 1.0 | 3 | 149252.96 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 0.0 | 0.2 | None | True | 1.0 | 7 | 118535.65 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 0.2 | 0.2 | None | False | 1.0 | 4 | 88025.37 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 0.5 | 0.6 | None | False | 1.0 | 9 | 116392.63 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 0.2 | 0.2 | None | False | 1.0 | 6 | 121418.95 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.5 | None | None | None | 1 | 2168.02 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.6 | None | True | 1.0 | 2 | 81670.46 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 0.2 | 0.2 | None | True | 1.0 | 1 | 130235.66 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 0.0 | 0.0 | None | False | 1.0 | 8 | 72514.26 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | None | False | 1.0 | 3 | 97360.26 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 0.2 | 0.5 | None | False | 1.0 | 7 | 84122.44 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.0 | 0.2 | None | False | 1.0 | 6 | 85896.54 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 0.8 | 1.0 | None | False | 1.0 | 2 | 83584.48 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 0.4 | 0.8 | None | False | 1.0 | 8 | 87500.07 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 0.2 | 0.4 | None | False | 1.0 | 8 | 98729.44 |  |
