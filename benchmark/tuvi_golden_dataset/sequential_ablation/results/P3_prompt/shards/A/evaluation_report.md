# W6 Evaluation report: sequential_p3_prompt_shard_a

- Dataset: `D:\UNI_STUDY\Year3\Semester3\TextMining\tuvi-battu-graphrag\benchmark\tuvi_golden_dataset\release\tuviqa_v1_release.jsonl`
- Dataset items: 100
- Configs: 2
- Judge backend: `gemini`
- Judge protocol: `blind-v2`
- Started: 2026-09-12T03:13:35.089190Z
- Completed: 2026-09-12T03:28:17.359246Z
- Notes: Only prompt_template_id changes. Prompt 2 keeps grounded-v2; structured-v3 is excluded by the pre-registered three-prompt shortlist. Two-person official shard assigned to A.
- Run status: `completed`

## Run identity and provenance

- Identity SHA-256: `a1baa0859f49dc33bc98f72381211655cf25cf8dcd92c3263d0782ef3d72c782`
- Dataset SHA-256: `90376a87cec29cc22e93dc71b41e054ed2f0183bc515a52aa461fecd43cc008c`
- Manifest SHA-256: `69cdd67e5b2aab3d1aa36567da3c38585e7122b3978db618ba48cf23ecbc42b1`
- Evaluator SHA-256: `a69fb4de27b0be1531f7972e8689f891cfac71a769934624e24d136420ef5f5f`
- Git SHA: `a2a2bb7d5d1e67605b5740596eafa2ee16758551`
- Git dirty: `False`
- Judge model: `gemini-3.1-flash-lite-preview`
- Checkpoint: `benchmark\tuvi_golden_dataset\sequential_ablation\results\P3_prompt\shards\A\checkpoints\evaluation_checkpoint.json`

## Execution completeness

- Expected pairs: 200
- Completed pairs: 200
- Failed pairs: 0
- Executed pairs: 200
- Resumed pairs: 0

> **Metric policy:** Sequential blind Judge v2 scores only Faithfulness and Answer Relevancy. Citation Evidence F1 is rule-based from cited chunks and gold-span provenance; AI-judged Context Recall is not a headline metric.

## Overall metrics

| Config | Status | Items | Faithfulness | Answer relevancy | Citation Evidence F1 | Latency p95 ms | Invalid markers |
|---|---:|---:|---:|---:|---:|---:|---:|
| p3_prompt_1 | completed | 100 | 0.912 | 0.871 | 0.0296 | 3376.01 | 0 |
| p3_prompt_2 | completed | 100 | 0.9 | 0.826 | 0.0274 | 3934.55 | 0 |

## Failure and fallback summary

| Config | Failed | Generation backend fallback | Judge failure | No context | Retrieval backend fallback | Citation fallback |
|---|---:|---:|---:|---:|---:|---:|
| p3_prompt_1 | 0 | 0 | 0 | 0 | 0 | 4 |
| p3_prompt_2 | 0 | 0 | 0 | 0 | 0 | 0 |

## Ablation analysis

- Baseline config: `baseline_graph_sparse_rrf`
- Preliminary recommendation: `p3_prompt_1`
  - Preliminary heuristic ranks configs by context recall, citation coverage, faithfulness, answer relevancy, graph hit rate, and a small p95 latency penalty.
  - Selected `p3_prompt_1` with context_recall_avg=None, citation_coverage_rate=0.9973, p95_latency_ms=3376.01.
  - Treat this as a smoke/first-pass recommendation until official Gemini judge and full dataset runs are complete.

### Context recall ranking

| Rank | Config | Value |
|---:|---|---:|

### Citation coverage ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | p3_prompt_1 | 0.9973 |
| 2 | p3_prompt_2 | 0.989 |

### Graph hit ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | p3_prompt_1 | 0.9121 |
| 2 | p3_prompt_2 | 0.9121 |

### p95 latency ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | p3_prompt_1 | 3376.01 |
| 2 | p3_prompt_2 | 3934.55 |

### Retrieval miss summary

| Config | Miss count | Example item IDs |
|---|---:|---|
| p3_prompt_1 | 2 | TVQA-061, TVQA-074 |
| p3_prompt_2 | 2 | TVQA-061, TVQA-074 |

### Rerank miss summary

| Config | Miss count | Example item IDs |
|---|---:|---|
| p3_prompt_1 | 0 |  |
| p3_prompt_2 | 0 |  |

## Phân tích ablation generation prompt/model

- Phạm vi: So sánh prompt template và generation model, giữ retrieval config cố định để cô lập ảnh hưởng generation.
- Retrieval control: Retrieval stack cố định theo W6 integration candidate: chunk_semantic_embedding_bge_m3, Graph + Sparse + RRF + BGE cross-encoder reranker, dense off.
- Chính sách run: Run chính của task này là Gemini judge partial 10 câu balanced; full/expanded run sẽ để W7-CONFIG-01/W8 hoặc khi quota cho phép.
- Prompt templates: `tuvi_generation_grounded_v2, tuvi_generation_v1`
- Generation models: `gemini-3.1-flash-lite-preview`
- Ứng viên generation sơ bộ: prompt `tuvi_generation_v1` với model `gemini-3.1-flash-lite-preview` qua config `p3_prompt_1`
  - Đây là gợi ý sơ bộ cho W7-ABL-01 dựa trên partial run, không phải quyết định production cuối cùng.
  - Điểm ưu tiên Faithfulness, Answer Relevancy, Citation Evidence F1 và Chart Context Grounding; p95 latency bị phạt nhẹ.
  - Ứng viên hiện tại là prompt `tuvi_generation_v1` với model `gemini-3.1-flash-lite-preview` qua config `p3_prompt_1`: faithfulness_avg=0.912, answer_relevancy_avg=0.871, citation_evidence_f1_avg=0.0296, p95_latency_ms=3376.01.
  - W7-CONFIG-01 sẽ tổng hợp thêm evidence retrieval/chunking/latency trước khi lock default_production.yaml.

### Xếp hạng theo Faithfulness

| Hạng | Prompt template | Model | Config | Giá trị |
|---:|---|---|---|---:|
| 1 | tuvi_generation_v1 | gemini-3.1-flash-lite-preview | p3_prompt_1 | 0.912 |
| 2 | tuvi_generation_grounded_v2 | gemini-3.1-flash-lite-preview | p3_prompt_2 | 0.9 |

### Xếp hạng theo Answer Relevancy

| Hạng | Prompt template | Model | Config | Giá trị |
|---:|---|---|---|---:|
| 1 | tuvi_generation_v1 | gemini-3.1-flash-lite-preview | p3_prompt_1 | 0.871 |
| 2 | tuvi_generation_grounded_v2 | gemini-3.1-flash-lite-preview | p3_prompt_2 | 0.826 |

### Xếp hạng theo Citation Coverage

| Hạng | Prompt template | Model | Config | Giá trị |
|---:|---|---|---|---:|

### Xếp hạng theo p95 latency

| Hạng | Prompt template | Model | Config | Giá trị |
|---:|---|---|---|---:|
| 1 | tuvi_generation_v1 | gemini-3.1-flash-lite-preview | p3_prompt_1 | 3376.01 |
| 2 | tuvi_generation_grounded_v2 | gemini-3.1-flash-lite-preview | p3_prompt_2 | 3934.55 |

## Metrics by question complexity

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| p3_prompt_1 | Direct | 10 | 1.0 | 0.98 | None | 0.0 | 0.75 | 1771.45 |
| p3_prompt_1 | One-hop | 46 | 0.8848 | 0.8217 | None | 0.8696 | 1.0 | 2899.11 |
| p3_prompt_1 | Two-hop | 44 | 0.9205 | 0.8977 | None | 0.9773 | 1.0 | 3414.66 |
| p3_prompt_2 | Direct | 10 | 0.95 | 0.87 | None | 0.0 | 0.0 | 2835.07 |
| p3_prompt_2 | One-hop | 46 | 0.8565 | 0.787 | None | 0.8696 | 1.0 | 3575.97 |
| p3_prompt_2 | Two-hop | 44 | 0.9341 | 0.8568 | None | 0.9773 | 1.0 | 4034.25 |

## Metrics by question family

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| p3_prompt_1 | core_identity | 10 | 1.0 | 0.98 | None | 0.0 | 0.75 | 1771.45 |
| p3_prompt_1 | dai_van_interpretation | 10 | 0.96 | 0.87 | None | 0.9 | 1.0 | 3284.7 |
| p3_prompt_1 | menh_cuc_relation | 10 | 0.9 | 0.86 | None | 0.8 | 1.0 | 2580.4 |
| p3_prompt_1 | menh_house_interpretation | 10 | 0.86 | 0.79 | None | 0.9 | 1.0 | 2865.07 |
| p3_prompt_1 | menh_tam_hop | 10 | 0.89 | 0.91 | None | 1.0 | 1.0 | 3656.2 |
| p3_prompt_1 | menh_xung_chieu | 10 | 0.9 | 0.92 | None | 1.0 | 1.0 | 3423.86 |
| p3_prompt_1 | special_state_interpretation | 10 | 0.85 | 0.68 | None | 0.9 | 1.0 | 3080.45 |
| p3_prompt_1 | synthesis_judgement | 10 | 0.96 | 0.86 | None | 0.9 | 1.0 | 3280.44 |
| p3_prompt_1 | than_cu_interpretation | 10 | 0.88 | 0.92 | None | 0.9 | 1.0 | 2919.49 |
| p3_prompt_1 | topic_house_plus_relations | 10 | 0.92 | 0.92 | None | 1.0 | 1.0 | 3297.15 |
| p3_prompt_2 | core_identity | 10 | 0.95 | 0.87 | None | 0.0 | 0.0 | 2835.07 |
| p3_prompt_2 | dai_van_interpretation | 10 | 0.9 | 0.72 | None | 0.9 | 1.0 | 3808.73 |
| p3_prompt_2 | menh_cuc_relation | 10 | 0.83 | 0.86 | None | 0.8 | 1.0 | 2952.39 |
| p3_prompt_2 | menh_house_interpretation | 10 | 0.94 | 0.76 | None | 0.9 | 1.0 | 3656.81 |
| p3_prompt_2 | menh_tam_hop | 10 | 0.9 | 0.82 | None | 1.0 | 1.0 | 3927.3 |
| p3_prompt_2 | menh_xung_chieu | 10 | 0.87 | 0.85 | None | 1.0 | 1.0 | 4125.34 |
| p3_prompt_2 | special_state_interpretation | 10 | 0.79 | 0.73 | None | 0.9 | 1.0 | 3283.47 |
| p3_prompt_2 | synthesis_judgement | 10 | 0.98 | 0.88 | None | 0.9 | 1.0 | 3938.84 |
| p3_prompt_2 | than_cu_interpretation | 10 | 0.88 | 0.83 | None | 0.9 | 1.0 | 3510.24 |
| p3_prompt_2 | topic_house_plus_relations | 10 | 0.96 | 0.94 | None | 1.0 | 1.0 | 4075.54 |

## Per-question results

### p3_prompt_1

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1358.02 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.9 | None | True | 1.0 | 4 | 2356.02 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 2559.75 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | None | True | 1.0 | 2 | 1763.32 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 5 | 2287.32 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | None | True | 1.0 | 4 | 2802.07 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | None | True | 1.0 | 5 | 3009.69 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.7 | None | True | 1.0 | 4 | 2638.66 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 6 | 2679.08 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.8 | 1.0 | None | True | 1.0 | 5 | 3034.73 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1718.55 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.5 | None | True | 1.0 | 2 | 2230.72 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | None | False | 1.0 | 4 | 3043.02 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 2301.33 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.5 | 0.4 | None | True | 1.0 | 2 | 2181.09 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | None | True | 1.0 | 4 | 2236.69 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.8 | None | True | 1.0 | 5 | 2981.52 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 2330.05 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 2164.06 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | None | True | 1.0 | 5 | 2074.37 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1239.86 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 2404.97 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 5 | 2768.52 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | None | True | 1.0 | 2 | 2269.43 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 0.0 | 0.0 | None | True | 1.0 | 3 | 2339.17 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | None | True | 1.0 | 4 | 3253.62 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.6 | 0.4 | None | True | 1.0 | 4 | 3387.47 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.6 | None | True | 1.0 | 4 | 3375.41 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 3302.66 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 3177.41 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1170.27 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 2 | 2941.66 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 2093.2 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | None | False | 1.0 | 2 | 1805.24 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 3424.76 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 0.9 | 1.0 | None | True | 1.0 | 5 | 3419.46 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 2273.75 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 3052.63 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.2 | 0.2 | None | True | 1.0 | 4 | 3290.41 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.9 | None | True | 1.0 | 5 | 3364.73 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1473.92 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 2664.44 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | None | True | 1.0 | 2 | 2278.19 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | None | True | 1.0 | 3 | 1806.75 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.0 | None | False | 1.0 | 6 | 1290.06 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 0.8 | 1.0 | None | True | 1.0 | 4 | 2516.73 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 1.0 | None | True | 1.0 | 6 | 2803.79 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 3080.31 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 5 | 2620.48 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 2993.05 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1358.83 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.2 | None | True | 1.0 | 4 | 2708.98 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 2186.46 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 0.0 | 0.0 | None | True | 1.0 | 3 | 2433.49 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 2659.63 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 0.8 | 1.0 | None | True | 1.0 | 3 | 3127.42 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 2913.24 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 4 | 3173.83 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 5 | 2750.39 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.9 | None | True | 1.0 | 4 | 2331.38 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 0.8 | None | False | 0.75 | 1 | 1550.92 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 2139.64 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.8 | None | True | 1.0 | 2 | 2185.19 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | None | True | 1.0 | 2 | 1769.01 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 2 | 1898.65 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | None | True | 1.0 | 3 | 3071.11 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 2864.21 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 2522.17 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 2842.5 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | None | True | 1.0 | 5 | 3081.52 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1563.6 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.7 | None | True | 1.0 | 3 | 2423.22 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 0.0 | 1.0 | None | True | 1.0 | 5 | 2459.63 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | None | False | 1.0 | 2 | 1746.72 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 2098.89 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 2921.87 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 1.0 | None | True | 1.0 | 3 | 2766.82 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 2 | 1852.55 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 2122.17 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.5 | None | True | 1.0 | 2 | 1848.49 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1814.74 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | None | False | 1.0 | 2 | 2771.47 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 5 | 2677.4 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 2700.6 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 2293.93 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 0.8 | 1.0 | None | True | 1.0 | 5 | 2873.12 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 3137.96 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 3 | 2549.91 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 6 | 2820.1 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.5 | None | False | 1.0 | 4 | 2999.91 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1543.06 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 2486.95 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.7 | None | True | 1.0 | 7 | 2175.32 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | None | True | 1.0 | 2 | 1808.24 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 3 | 2089.87 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | None | True | 1.0 | 3 | 3849.89 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 1.0 | None | True | 1.0 | 3 | 3453.63 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.8 | None | False | 1.0 | 4 | 2234.84 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 2713.94 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.8 | None | True | 1.0 | 4 | 2585.6 |  |

### p3_prompt_2

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1622.16 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 4 | 3036.37 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 3414.56 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | None | True | 1.0 | 2 | 2292.18 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.6 | None | True | 1.0 | 5 | 2863.27 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | None | True | 1.0 | 5 | 3707.23 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.9 | None | True | 1.0 | 4 | 3345.05 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 0.0 | 0.0 | None | True | 1.0 | 3 | 2669.9 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 5 | 2667.87 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.8 | None | True | 1.0 | 5 | 3450.28 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1866.53 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 7 | 2973.54 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | None | False | 1.0 | 4 | 3425.51 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 0.5 | 1.0 | None | True | 1.0 | 2 | 2182.66 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.8 | None | True | 1.0 | 4 | 2761.39 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.6 | None | True | 1.0 | 4 | 2503.87 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | None | True | 1.0 | 5 | 3275.12 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 3256.84 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 2690.55 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | None | True | 1.0 | 5 | 2521.67 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1234.21 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 6 | 3272.66 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 0.8 | 1.0 | None | True | 1.0 | 3 | 2660.5 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 2910.94 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 0.0 | 0.2 | None | True | 1.0 | 3 | 2911.62 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.6 | None | True | 1.0 | 4 | 3982.97 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 1.0 | None | True | 1.0 | 8 | 4216.33 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 4 | 3738.88 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | None | True | 1.0 | 5 | 3932.0 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | None | True | 1.0 | 6 | 3652.61 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1236.03 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.6 | None | True | 1.0 | 4 | 3050.69 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 2823.34 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | None | False | 1.0 | 3 | 2309.02 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 3 | 2214.03 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | None | True | 1.0 | 5 | 3859.27 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.8 | None | True | 1.0 | 4 | 3001.35 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 4 | 3129.13 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.6 | None | True | 1.0 | 5 | 4192.98 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.8 | None | True | 1.0 | 5 | 4037.8 |  |
| TVQA-041 | completed | Direct | core_identity | True | 0.5 | 0.5 | None | None | None | 1 | 1304.78 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 6 | 3565.15 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | None | True | 1.0 | 4 | 2698.01 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | None | True | 1.0 | 3 | 2057.53 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.5 | None | False | 1.0 | 6 | 2590.33 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 0.8 | 1.0 | None | True | 1.0 | 6 | 3199.23 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | None | True | 1.0 | 4 | 3092.5 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 3448.55 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 5 | 3906.56 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 3817.88 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1878.78 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.2 | None | True | 1.0 | 8 | 3731.8 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 3110.44 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 0.0 | 0.2 | None | True | 1.0 | 9 | 2098.64 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.6 | None | True | 1.0 | 9 | 2635.5 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | None | True | 1.0 | 6 | 2677.53 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | None | True | 1.0 | 2 | 2653.98 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 0.2 | None | True | 1.0 | 5 | 2975.44 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 1.0 | None | True | 1.0 | 6 | 2989.5 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | None | True | 1.0 | 2 | 3113.7 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 0.4 | None | False | 0.0 | 1 | 2531.84 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 3413.36 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 2 | 2831.38 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 2986.31 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 5 | 3463.77 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 0.8 | 1.0 | None | True | 1.0 | 3 | 3652.83 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 0.5 | 0.2 | None | True | 1.0 | 9 | 2360.37 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 2734.48 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 2845.3 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.8 | None | True | 1.0 | 4 | 3009.72 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1460.23 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | None | True | 1.0 | 6 | 3022.97 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 5 | 2611.7 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | None | False | 1.0 | 2 | 1938.71 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 0.8 | 1.0 | None | True | 1.0 | 4 | 3063.11 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 0.8 | 1.0 | None | True | 1.0 | 5 | 3467.26 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 1.0 | None | True | 1.0 | 5 | 3542.11 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 2 | 3010.85 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 2945.27 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.8 | None | True | 1.0 | 4 | 2675.71 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 1617.0 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.5 | None | False | 1.0 | 2 | 2399.78 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 7 | 3579.57 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.6 | None | True | 1.0 | 3 | 2529.13 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 0.5 | 1.0 | None | True | 1.0 | 2 | 2376.01 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | None | True | 1.0 | 5 | 3229.05 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | None | True | 1.0 | 5 | 3274.15 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 4 | 3865.88 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 7 | 3361.48 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.8 | None | False | 1.0 | 3 | 3738.35 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3083.17 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 3 | 3494.54 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 0.0 | 0.0 | None | True | 1.0 | 7 | 1941.28 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | None | True | 1.0 | 2 | 2227.43 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 5 | 2786.91 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.5 | None | True | 1.0 | 8 | 3451.71 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.8 | None | True | 1.0 | 6 | 4014.14 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.6 | None | False | 1.0 | 4 | 3060.09 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 2853.07 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.8 | None | True | 1.0 | 5 | 2936.08 |  |
