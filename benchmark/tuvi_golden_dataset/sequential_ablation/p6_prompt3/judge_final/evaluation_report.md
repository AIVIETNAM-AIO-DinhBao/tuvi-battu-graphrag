# W6 Evaluation report: local_llm_gemini_judge_sequential-p6-final

- Dataset: `benchmark/tuvi_golden_dataset/release/tuviqa_v1_release.jsonl`
- Dataset items: 100
- Configs: 3
- Judge backend: `gemini`
- Judge protocol: `blind-v2`
- Started: 2026-09-14T09:30:01.401343+00:00
- Completed: 2026-09-14T09:40:51.916000+00:00
- Notes: Local-LLM generation answers judged with GeminiEvaluationJudge protocol=blind-v2, summarize_evaluation_item, provenance Citation Evidence F1, and aggregate metric functions.
- Run status: `completed`

## Run identity and provenance

- Identity SHA-256: `64f4d970e894398091b95b130869a9fc51a6243a02709c1fa34e86ab6f510807`
- Dataset SHA-256: `90376a87cec29cc22e93dc71b41e054ed2f0183bc515a52aa461fecd43cc008c`
- Manifest SHA-256: `9f60052e643085ba36790cfcf13da3701ffa9d9441e76079b5108b1d81a3e331`
- Evaluator SHA-256: `78dce3092a4e28ee915bbfdad61341d6f0ad1761070d0c12240ab7b5b4202464`
- Git SHA: `15b87f74ec9e94bfa07a272301d931c846d5ec3c`
- Git dirty: `True`
- Judge model: `gemini-3.1-flash-lite-preview`
- Checkpoint: `D:\UNI_STUDY\Year3\Semester3\TextMining\tuvi-battu-graphrag\benchmark\tuvi_golden_dataset\sequential_ablation\p6_prompt3\judge_final\checkpoints\evaluation_checkpoint.json`

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
| qwen25_7b__p6_prompt3_frozen_context | completed | 100 | 0.303 | 0.519 | 163615.79 | 0 |
| gemini31_flash_lite__p6_prompt3_frozen_context | completed | 100 | 0.8755 | 0.898 | 163276.75 | 0 |
| gemma3_4b__p6_prompt3_frozen_context | completed | 100 | 0.298 | 0.503 | 167223.43 | 0 |

## Failure and fallback summary

| Config | Failed | Generation backend fallback | Judge failure | No context | Retrieval backend fallback | Citation fallback |
|---|---:|---:|---:|---:|---:|---:|
| qwen25_7b__p6_prompt3_frozen_context | 0 | 0 | 0 | 0 | 0 | 30 |
| gemini31_flash_lite__p6_prompt3_frozen_context | 0 | 0 | 0 | 0 | 0 | 6 |
| gemma3_4b__p6_prompt3_frozen_context | 0 | 0 | 0 | 0 | 0 | 51 |

## Metrics by question complexity

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| qwen25_7b__p6_prompt3_frozen_context | Direct | 10 | 0.57 | 0.55 | None | 0.0 | 1.0 | 2237.87 |
| qwen25_7b__p6_prompt3_frozen_context | One-hop | 46 | 0.2543 | 0.5217 | None | 0.5 | 1.0 | 174419.21 |
| qwen25_7b__p6_prompt3_frozen_context | Two-hop | 44 | 0.2932 | 0.5091 | None | 0.5682 | 1.0 | 148109.37 |
| gemini31_flash_lite__p6_prompt3_frozen_context | Direct | 10 | 0.95 | 0.88 | None | 0.0 | 0.0 | 2688.68 |
| gemini31_flash_lite__p6_prompt3_frozen_context | One-hop | 46 | 0.8478 | 0.8848 | None | 0.5 | 1.0 | 174688.93 |
| gemini31_flash_lite__p6_prompt3_frozen_context | Two-hop | 44 | 0.8875 | 0.9159 | None | 0.5682 | 1.0 | 147745.35 |
| gemma3_4b__p6_prompt3_frozen_context | Direct | 10 | 0.63 | 0.64 | None | 0.0 | 1.0 | 4264.27 |
| gemma3_4b__p6_prompt3_frozen_context | One-hop | 46 | 0.237 | 0.4304 | None | 0.5 | 1.0 | 178815.39 |
| gemma3_4b__p6_prompt3_frozen_context | Two-hop | 44 | 0.2864 | 0.5477 | None | 0.5682 | 1.0 | 151713.56 |

## Metrics by question family

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| qwen25_7b__p6_prompt3_frozen_context | core_identity | 10 | 0.57 | 0.55 | None | 0.0 | 1.0 | 2237.87 |
| qwen25_7b__p6_prompt3_frozen_context | dai_van_interpretation | 10 | 0.16 | 0.33 | None | 0.6 | 1.0 | 150353.92 |
| qwen25_7b__p6_prompt3_frozen_context | menh_cuc_relation | 10 | 0.09 | 0.43 | None | 0.3 | 1.0 | 112996.52 |
| qwen25_7b__p6_prompt3_frozen_context | menh_house_interpretation | 10 | 0.22 | 0.47 | None | 0.5 | 1.0 | 182002.79 |
| qwen25_7b__p6_prompt3_frozen_context | menh_tam_hop | 10 | 0.22 | 0.47 | None | 0.6 | 1.0 | 168542.02 |
| qwen25_7b__p6_prompt3_frozen_context | menh_xung_chieu | 10 | 0.2 | 0.42 | None | 0.9 | 1.0 | 137547.14 |
| qwen25_7b__p6_prompt3_frozen_context | special_state_interpretation | 10 | 0.34 | 0.66 | None | 0.5 | 1.0 | 144197.79 |
| qwen25_7b__p6_prompt3_frozen_context | synthesis_judgement | 10 | 0.42 | 0.52 | None | 0.5 | 1.0 | 156442.89 |
| qwen25_7b__p6_prompt3_frozen_context | than_cu_interpretation | 10 | 0.48 | 0.73 | None | 0.6 | 1.0 | 186337.47 |
| qwen25_7b__p6_prompt3_frozen_context | topic_house_plus_relations | 10 | 0.33 | 0.61 | None | 0.3 | 1.0 | 136067.76 |
| gemini31_flash_lite__p6_prompt3_frozen_context | core_identity | 10 | 0.95 | 0.88 | None | 0.0 | 0.0 | 2688.68 |
| gemini31_flash_lite__p6_prompt3_frozen_context | dai_van_interpretation | 10 | 0.855 | 0.88 | None | 0.6 | 1.0 | 150285.68 |
| gemini31_flash_lite__p6_prompt3_frozen_context | menh_cuc_relation | 10 | 0.76 | 0.8 | None | 0.3 | 1.0 | 112448.96 |
| gemini31_flash_lite__p6_prompt3_frozen_context | menh_house_interpretation | 10 | 0.88 | 0.85 | None | 0.5 | 1.0 | 181465.65 |
| gemini31_flash_lite__p6_prompt3_frozen_context | menh_tam_hop | 10 | 0.92 | 0.87 | None | 0.6 | 1.0 | 168443.74 |
| gemini31_flash_lite__p6_prompt3_frozen_context | menh_xung_chieu | 10 | 0.775 | 0.89 | None | 0.9 | 1.0 | 136191.61 |
| gemini31_flash_lite__p6_prompt3_frozen_context | special_state_interpretation | 10 | 0.925 | 0.98 | None | 0.5 | 1.0 | 144080.66 |
| gemini31_flash_lite__p6_prompt3_frozen_context | synthesis_judgement | 10 | 0.955 | 0.94 | None | 0.5 | 1.0 | 156333.77 |
| gemini31_flash_lite__p6_prompt3_frozen_context | than_cu_interpretation | 10 | 0.755 | 0.89 | None | 0.6 | 1.0 | 186554.42 |
| gemini31_flash_lite__p6_prompt3_frozen_context | topic_house_plus_relations | 10 | 0.98 | 1.0 | None | 0.3 | 1.0 | 136174.76 |
| gemma3_4b__p6_prompt3_frozen_context | core_identity | 10 | 0.63 | 0.64 | None | 0.0 | 1.0 | 4264.27 |
| gemma3_4b__p6_prompt3_frozen_context | dai_van_interpretation | 10 | 0.2 | 0.42 | None | 0.6 | 1.0 | 154755.2 |
| gemma3_4b__p6_prompt3_frozen_context | menh_cuc_relation | 10 | 0.14 | 0.24 | None | 0.3 | 1.0 | 116613.65 |
| gemma3_4b__p6_prompt3_frozen_context | menh_house_interpretation | 10 | 0.16 | 0.36 | None | 0.5 | 1.0 | 185631.42 |
| gemma3_4b__p6_prompt3_frozen_context | menh_tam_hop | 10 | 0.24 | 0.46 | None | 0.6 | 1.0 | 172932.37 |
| gemma3_4b__p6_prompt3_frozen_context | menh_xung_chieu | 10 | 0.28 | 0.41 | None | 0.9 | 1.0 | 140335.18 |
| gemma3_4b__p6_prompt3_frozen_context | special_state_interpretation | 10 | 0.4 | 0.61 | None | 0.5 | 1.0 | 145517.33 |
| gemma3_4b__p6_prompt3_frozen_context | synthesis_judgement | 10 | 0.38 | 0.75 | None | 0.5 | 1.0 | 160596.41 |
| gemma3_4b__p6_prompt3_frozen_context | than_cu_interpretation | 10 | 0.25 | 0.53 | None | 0.6 | 1.0 | 193573.94 |
| gemma3_4b__p6_prompt3_frozen_context | topic_house_plus_relations | 10 | 0.3 | 0.61 | None | 0.3 | 1.0 | 139616.93 |

## Per-question results

### qwen25_7b__p6_prompt3_frozen_context

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 0.5 | 0.5 | None | None | None | 1 | 1925.73 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.6 | None | False | 1.0 | 1 | 197092.48 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 0.5 | 1.0 | None | True | 1.0 | 2 | 119604.0 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 0.5 | 1.0 | None | False | 1.0 | 2 | 82420.37 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 0.5 | 0.8 | None | True | 1.0 | 3 | 133910.85 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 0.0 | 0.5 | None | True | 1.0 | 2 | 185009.46 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 0.5 | 0.8 | None | True | 1.0 | 9 | 144803.21 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 0.2 | 0.0 | None | True | 1.0 | 1 | 158233.72 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 1.0 | None | False | 1.0 | 3 | 108405.59 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.5 | 1.0 | None | True | 1.0 | 1 | 93962.07 |  |
| TVQA-011 | completed | Direct | core_identity | True | 0.5 | 0.5 | None | None | None | 1 | 1342.53 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.4 | None | True | 1.0 | 2 | 124867.34 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.7 | None | False | 1.0 | 9 | 145549.64 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 0.0 | 0.2 | None | False | 1.0 | 2 | 67508.6 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.2 | 0.8 | None | False | 1.0 | 2 | 80898.16 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.6 | None | True | 1.0 | 2 | 103869.35 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.5 | 0.2 | None | True | 1.0 | 2 | 98019.36 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 0.2 | 0.5 | None | True | 1.0 | 4 | 91460.26 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 0.5 | 1.0 | None | False | 1.0 | 1 | 87897.73 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 0.8 | 1.0 | None | False | 1.0 | 2 | 103990.12 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1419.92 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.6 | None | False | 1.0 | 2 | 142823.32 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 2 | 103333.31 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 0.0 | 0.5 | None | False | 1.0 | 2 | 74976.76 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 0.5 | 1.0 | None | True | 1.0 | 2 | 96066.5 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 0.2 | 0.8 | None | False | 1.0 | 9 | 121119.22 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.0 | 0.5 | None | True | 1.0 | 2 | 83327.32 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.6 | None | False | 1.0 | 2 | 84136.55 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 0.5 | 0.6 | None | True | 1.0 | 1 | 121088.49 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 0.2 | 0.6 | None | False | 1.0 | 9 | 164678.87 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1713.02 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.4 | None | True | 1.0 | 2 | 134403.79 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 0.5 | 1.0 | None | False | 1.0 | 9 | 91842.63 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 0.0 | 0.8 | None | False | 1.0 | 9 | 73004.93 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | None | False | 1.0 | 2 | 98319.64 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 0.2 | 0.4 | None | False | 1.0 | 9 | 118523.97 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 0.0 | 0.5 | None | True | 1.0 | 2 | 108832.66 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 0.2 | 0.8 | None | True | 1.0 | 6 | 97144.19 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.0 | 0.2 | None | True | 1.0 | 3 | 96789.42 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 0.6 | 1.0 | None | True | 1.0 | 9 | 101043.02 |  |
| TVQA-041 | completed | Direct | core_identity | True | 0.0 | 0.0 | None | None | None | 1 | 1048.09 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 0.0 | 1.0 | None | True | 1.0 | 9 | 81145.27 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | None | False | 1.0 | 2 | 87082.18 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 0.0 | 0.0 | None | True | 1.0 | 2 | 71477.66 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 0.0 | 0.0 | None | True | 1.0 | 2 | 123063.02 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 0.2 | 0.4 | None | True | 1.0 | 2 | 102665.81 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.6 | 0.8 | None | True | 1.0 | 1 | 112309.66 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 0.2 | 0.8 | None | True | 1.0 | 6 | 95827.74 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 0.0 | 0.2 | None | False | 1.0 | 2 | 86880.06 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 0.0 | 0.0 | None | False | 1.0 | 9 | 146098.6 |  |
| TVQA-051 | completed | Direct | core_identity | True | 0.0 | 0.0 | None | None | None | 1 | 2069.8 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.0 | 0.0 | None | True | 1.0 | 2 | 124178.91 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 0.0 | 1.0 | None | True | 1.0 | 2 | 93707.66 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 0.2 | 0.5 | None | True | 1.0 | 2 | 76124.26 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 0.5 | 0.8 | None | False | 1.0 | 2 | 96058.85 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 0.2 | 1.0 | None | True | 1.0 | 2 | 82492.69 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 0.0 | 0.2 | None | True | 1.0 | 2 | 82727.37 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 0.0 | 0.0 | None | False | 1.0 | 2 | 82965.92 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 0.0 | 0.5 | None | False | 1.0 | 9 | 86139.53 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 0.5 | 0.0 | None | True | 1.0 | 9 | 124306.17 |  |
| TVQA-061 | completed | Direct | core_identity | False | 0.2 | 0.0 | None | False | 1.0 | 1 | 2032.59 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 0.6 | 1.0 | None | False | 1.0 | 2 | 80865.29 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 0.0 | 0.2 | None | True | 1.0 | 9 | 161441.58 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 0.2 | 0.8 | None | False | 1.0 | 2 | 112461.33 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 0.2 | 0.8 | None | True | 1.0 | 2 | 104255.44 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 0.2 | 0.6 | None | True | 1.0 | 2 | 126869.32 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 0.2 | 0.4 | None | True | 1.0 | 2 | 123168.65 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 0.0 | 0.0 | None | True | 1.0 | 1 | 116538.96 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 0.0 | 0.0 | None | True | 1.0 | 9 | 137342.44 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.8 | None | True | 1.0 | 9 | 141408.71 |  |
| TVQA-071 | completed | Direct | core_identity | True | 0.5 | 0.5 | None | None | None | 1 | 1523.72 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 0.0 | 0.5 | None | False | 1.0 | 9 | 151457.36 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 0.5 | 0.8 | None | True | 1.0 | 9 | 193127.12 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 0.0 | 0.0 | None | False | 1.0 | 3 | 108345.53 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 0.0 | 0.5 | None | True | 1.0 | 9 | 108241.57 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 0.0 | 0.0 | None | True | 1.0 | 9 | 139754.74 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 0.2 | 0.4 | None | True | 1.0 | 4 | 128678.6 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 0.0 | 0.2 | None | True | 1.0 | 2 | 140723.06 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 0.5 | 0.8 | None | False | 1.0 | 9 | 134509.82 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 0.0 | 0.2 | None | True | 1.0 | 1 | 146376.7 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1901.23 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 0.0 | 0.2 | None | False | 1.0 | 2 | 163559.84 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 0.5 | 0.8 | None | False | 1.0 | 2 | 178039.0 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 0.0 | 0.0 | None | True | 1.0 | 3 | 113434.41 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 0.0 | 0.5 | None | False | 1.0 | 2 | 152614.37 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 0.2 | 0.4 | None | False | 1.0 | 2 | 148415.14 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 0.0 | 0.2 | None | True | 1.0 | 1 | 115412.11 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 0.0 | 0.2 | None | False | 1.0 | 5 | 88321.21 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 0.5 | 1.0 | None | False | 1.0 | 3 | 115296.25 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 0.0 | 0.0 | None | False | 1.0 | 1 | 119686.22 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 2375.39 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.0 | None | True | 1.0 | 2 | 82443.03 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 0.0 | 0.2 | None | True | 1.0 | 2 | 128691.54 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 0.0 | 0.5 | None | False | 1.0 | 1 | 73626.93 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 0.5 | 0.6 | None | False | 1.0 | 2 | 96994.71 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 0.0 | 0.0 | None | False | 1.0 | 1 | 83644.51 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.0 | 0.2 | None | False | 1.0 | 2 | 83864.78 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 0.0 | 0.2 | None | False | 1.0 | 8 | 81870.77 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 0.5 | 0.8 | None | False | 1.0 | 2 | 85117.67 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.6 | None | False | 1.0 | 2 | 96583.64 |  |

### gemini31_flash_lite__p6_prompt3_frozen_context

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1898.77 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | None | False | 1.0 | 2 | 196395.14 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 119174.49 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | None | False | 1.0 | 2 | 81811.69 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 4 | 134394.84 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.2 | None | True | 1.0 | 3 | 185198.29 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 1.0 | None | True | 1.0 | 4 | 145112.53 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.5 | None | True | 1.0 | 3 | 158715.29 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | False | 1.0 | 3 | 109095.43 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.8 | 1.0 | None | True | 1.0 | 4 | 93319.94 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1627.54 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 3 | 125126.28 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.9 | None | False | 1.0 | 2 | 144925.94 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | None | False | 1.0 | 3 | 67697.83 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | None | False | 1.0 | 4 | 81585.06 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 103330.62 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.2 | 0.5 | None | True | 1.0 | 3 | 97873.72 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 90106.77 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | False | 1.0 | 3 | 87278.2 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | None | False | 1.0 | 3 | 103707.46 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 2399.85 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | None | False | 1.0 | 4 | 143160.38 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 5 | 103220.36 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 0.0 | 0.5 | None | False | 1.0 | 6 | 74869.95 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 96218.9 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.8 | None | False | 1.0 | 5 | 120980.88 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.8 | None | True | 1.0 | 5 | 83884.94 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 0.8 | None | False | 1.0 | 3 | 82397.28 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 121923.33 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | None | False | 1.0 | 5 | 164383.46 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 2500.86 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.7 | None | True | 1.0 | 5 | 134386.02 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 0.75 | 1.0 | None | False | 1.0 | 4 | 91519.45 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 0.8 | 1.0 | None | False | 1.0 | 5 | 72979.27 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | None | False | 1.0 | 4 | 98152.37 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | None | False | 1.0 | 4 | 118217.68 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | None | True | 1.0 | 3 | 109338.27 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 0.75 | 1.0 | None | True | 1.0 | 3 | 96830.07 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 1.0 | None | True | 1.0 | 2 | 96089.63 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 0.75 | 1.0 | None | True | 1.0 | 3 | 100858.22 |  |
| TVQA-041 | completed | Direct | core_identity | True | 0.5 | 1.0 | None | None | None | 1 | 2222.44 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 81371.52 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | None | False | 1.0 | 6 | 86786.22 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 70397.01 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 122433.87 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 0.8 | 1.0 | None | True | 1.0 | 9 | 103631.6 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.6 | 0.8 | None | True | 1.0 | 9 | 110669.57 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 95053.27 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | False | 1.0 | 4 | 86000.86 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | None | False | 1.0 | 2 | 146495.25 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 2273.61 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.5 | None | True | 1.0 | 3 | 124586.88 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 0.0 | 0.0 | None | True | 1.0 | 3 | 94129.46 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 76469.28 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 0.75 | 1.0 | None | False | 1.0 | 2 | 95969.28 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 83066.16 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 1.0 | None | True | 1.0 | 4 | 82137.6 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 0.0 | 0.5 | None | False | 1.0 | 4 | 83019.65 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | False | 1.0 | 3 | 85832.81 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 123288.21 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 0.8 | None | False | 0.0 | 1 | 2360.72 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | None | False | 1.0 | 5 | 80969.67 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 0.8 | 1.0 | None | True | 1.0 | 6 | 161813.86 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | None | False | 1.0 | 3 | 112412.78 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 104144.45 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 126623.84 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | None | True | 1.0 | 5 | 124693.15 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 116463.58 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 137031.42 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 140659.91 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1756.72 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.9 | None | False | 1.0 | 3 | 151597.69 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 0.2 | 1.0 | None | True | 1.0 | 2 | 193134.25 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | None | False | 1.0 | 5 | 108419.05 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 108688.22 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 139992.48 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 125288.26 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 0.8 | 1.0 | None | True | 1.0 | 3 | 139982.82 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | False | 1.0 | 4 | 135127.72 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.8 | None | True | 1.0 | 3 | 144644.17 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 2284.26 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | None | False | 1.0 | 2 | 163218.5 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | None | False | 1.0 | 4 | 178512.41 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.7 | None | True | 1.0 | 3 | 112478.57 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 0.5 | 1.0 | None | False | 1.0 | 3 | 152005.42 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | None | False | 1.0 | 2 | 147965.96 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 0.75 | 1.0 | None | True | 1.0 | 3 | 115027.61 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | None | False | 1.0 | 3 | 87096.47 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | False | 1.0 | 3 | 116306.61 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.8 | None | False | 1.0 | 5 | 119585.75 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.0 | None | None | None | 1 | 2842.36 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 2 | 83242.55 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 128930.58 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 0.0 | 0.0 | None | False | 1.0 | 2 | 72542.58 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | None | False | 1.0 | 4 | 97846.11 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | None | False | 1.0 | 2 | 83306.07 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | None | False | 1.0 | 2 | 83334.55 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | None | False | 1.0 | 2 | 82140.26 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | False | 1.0 | 2 | 85108.81 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.8 | None | False | 1.0 | 3 | 96774.86 |  |

### gemma3_4b__p6_prompt3_frozen_context

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 2678.72 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.5 | None | False | 1.0 | 9 | 201159.98 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 0.2 | 0.8 | None | True | 1.0 | 3 | 121634.74 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 0.2 | 0.2 | None | False | 1.0 | 5 | 88239.64 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 0.2 | 0.6 | None | True | 1.0 | 9 | 134889.01 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 0.2 | 0.4 | None | True | 1.0 | 7 | 190537.21 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 0.2 | 0.6 | None | True | 1.0 | 3 | 148090.64 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 0.2 | 0.0 | None | True | 1.0 | 2 | 162814.93 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 0.4 | 0.6 | None | False | 1.0 | 6 | 112533.77 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.2 | 0.4 | None | True | 1.0 | 5 | 96952.47 |  |
| TVQA-011 | completed | Direct | core_identity | True | 0.5 | 0.8 | None | None | None | 1 | 3297.6 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.4 | None | True | 1.0 | 7 | 129638.25 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 0.4 | 0.5 | None | False | 1.0 | 4 | 147743.79 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 0.2 | 0.2 | None | False | 1.0 | 9 | 70334.52 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.2 | 0.4 | None | False | 1.0 | 7 | 83388.61 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 0.5 | 0.4 | None | True | 1.0 | 9 | 105864.45 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.6 | 0.4 | None | True | 1.0 | 3 | 99491.01 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 0.2 | 0.8 | None | True | 1.0 | 4 | 90916.71 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 1.0 | None | False | 1.0 | 7 | 90548.8 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 0.8 | 1.0 | None | False | 1.0 | 9 | 105834.08 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1957.05 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 0.0 | 0.0 | None | False | 1.0 | 9 | 146425.32 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 0.5 | 0.8 | None | True | 1.0 | 9 | 105611.94 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 0.2 | 0.2 | None | False | 1.0 | 9 | 78346.89 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 0.5 | 1.0 | None | True | 1.0 | 3 | 103092.67 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 0.2 | 0.5 | None | False | 1.0 | 4 | 125266.67 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.2 | 0.4 | None | True | 1.0 | 5 | 87680.32 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.2 | 0.2 | None | False | 1.0 | 4 | 85889.45 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 0.2 | 0.8 | None | True | 1.0 | 9 | 123738.48 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 0.2 | 0.8 | None | False | 1.0 | 9 | 167821.14 |  |
| TVQA-031 | completed | Direct | core_identity | True | 0.0 | 0.0 | None | None | None | 1 | 746.18 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.0 | 0.0 | None | True | 1.0 | 9 | 142345.35 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 0.0 | 0.5 | None | False | 1.0 | 4 | 94178.27 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 0.0 | 0.2 | None | False | 1.0 | 3 | 76262.17 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 0.2 | 0.4 | None | False | 1.0 | 6 | 99548.05 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 0.2 | 0.4 | None | False | 1.0 | 9 | 128589.38 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 0.2 | 0.4 | None | True | 1.0 | 6 | 112824.37 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 0.2 | 0.8 | None | True | 1.0 | 4 | 97608.46 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.0 | 0.2 | None | True | 1.0 | 6 | 101022.84 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.8 | None | True | 1.0 | 9 | 105551.4 |  |
| TVQA-041 | completed | Direct | core_identity | True | 0.0 | 0.0 | None | None | None | 1 | 1667.32 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.4 | None | True | 1.0 | 9 | 87618.55 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.8 | None | False | 1.0 | 9 | 91240.43 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 0.0 | 0.2 | None | True | 1.0 | 9 | 72237.89 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 0.0 | 0.0 | None | True | 1.0 | 3 | 125856.51 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 0.2 | 0.4 | None | True | 1.0 | 9 | 107034.98 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.2 | 0.3 | None | True | 1.0 | 9 | 115189.28 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 0.2 | 0.6 | None | True | 1.0 | 4 | 96469.54 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 1.0 | None | False | 1.0 | 9 | 89523.49 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 0.4 | 1.0 | None | False | 1.0 | 9 | 151766.19 |  |
| TVQA-051 | completed | Direct | core_identity | True | 0.0 | 0.2 | None | None | None | 1 | 3310.31 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.4 | None | True | 1.0 | 8 | 127610.51 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 0.0 | 0.5 | None | True | 1.0 | 4 | 97516.12 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 0.4 | 0.6 | None | True | 1.0 | 9 | 79007.3 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 0.5 | 0.8 | None | False | 1.0 | 3 | 100457.93 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 0.5 | 1.0 | None | True | 1.0 | 5 | 85798.37 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.5 | None | True | 1.0 | 8 | 86158.69 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 0.0 | 0.2 | None | False | 1.0 | 4 | 84217.74 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 0.0 | 0.2 | None | False | 1.0 | 9 | 105459.89 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 0.6 | 1.0 | None | True | 1.0 | 9 | 125795.4 |  |
| TVQA-061 | completed | Direct | core_identity | False | 0.8 | 0.6 | None | False | 1.0 | 1 | 4497.13 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.6 | None | False | 1.0 | 4 | 81462.95 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 0.2 | 0.4 | None | True | 1.0 | 4 | 167191.97 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 0.2 | 0.2 | None | False | 1.0 | 9 | 117687.8 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 0.4 | 0.6 | None | True | 1.0 | 5 | 107042.88 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 0.0 | 0.5 | None | True | 1.0 | 5 | 130886.23 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 0.2 | 0.4 | None | True | 1.0 | 8 | 128707.89 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 0.2 | 0.4 | None | True | 1.0 | 7 | 119765.82 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 0.0 | 0.2 | None | True | 1.0 | 9 | 139384.49 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 0.2 | 0.5 | None | True | 1.0 | 9 | 143002.86 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1286.58 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.5 | None | False | 1.0 | 9 | 157568.58 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 0.2 | 0.4 | None | True | 1.0 | 6 | 202479.08 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 0.0 | 0.0 | None | False | 1.0 | 4 | 115300.8 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 0.2 | 0.5 | None | True | 1.0 | 9 | 113895.44 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 0.0 | 0.0 | None | True | 1.0 | 6 | 145585.27 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 0.2 | 0.4 | None | True | 1.0 | 3 | 130856.29 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 0.2 | 0.2 | None | True | 1.0 | 4 | 144904.43 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 0.2 | 1.0 | None | False | 1.0 | 5 | 139807.1 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 0.2 | 0.8 | None | True | 1.0 | 3 | 146929.81 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3227.22 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.4 | None | False | 1.0 | 3 | 166652.07 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 0.2 | 0.4 | None | False | 1.0 | 6 | 182689.87 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 0.2 | 0.4 | None | True | 1.0 | 9 | 114511.78 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | None | False | 1.0 | 4 | 154213.22 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 0.6 | 0.8 | None | False | 1.0 | 9 | 151415.34 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 0.0 | 0.2 | None | True | 1.0 | 4 | 127721.56 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 0.0 | 0.2 | None | False | 1.0 | 5 | 90479.83 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 0.4 | 0.6 | None | False | 1.0 | 9 | 120086.4 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 0.2 | 0.4 | None | False | 1.0 | 6 | 127293.31 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 3979.66 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.4 | None | True | 1.0 | 3 | 86779.49 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 0.0 | 0.2 | None | True | 1.0 | 9 | 130498.93 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 0.0 | 0.2 | None | False | 1.0 | 9 | 78022.85 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.8 | None | False | 1.0 | 9 | 99775.8 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 0.0 | 0.2 | None | False | 1.0 | 8 | 86607.86 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.2 | 0.5 | None | False | 1.0 | 7 | 85166.89 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 0.6 | 0.8 | None | False | 1.0 | 8 | 85332.42 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 0.2 | 0.5 | None | False | 1.0 | 4 | 87397.82 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 0.2 | 0.8 | None | False | 1.0 | 9 | 101655.13 |  |
