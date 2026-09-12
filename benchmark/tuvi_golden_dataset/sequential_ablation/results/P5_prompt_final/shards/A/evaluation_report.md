# W6 Evaluation report: sequential_p5_prompt_shard_a

- Dataset: `D:\UNI_STUDY\Year3\Semester3\TextMining\tuvi-battu-graphrag\benchmark\tuvi_golden_dataset\release\tuviqa_v1_release.jsonl`
- Dataset items: 100
- Configs: 2
- Judge backend: `gemini`
- Judge protocol: `blind-v2`
- Started: 2026-09-12T13:21:08.363447Z
- Completed: 2026-09-12T13:40:47.123805Z
- Notes: Only prompt_template_id changes on the P4-locked final context. Two-person official shard assigned to A.
- Run status: `completed`

## Run identity and provenance

- Identity SHA-256: `aee5cd4d00f8430c1c836ba1db83c9880dd4cab38194a2adfbd9f9caf21e3a1d`
- Dataset SHA-256: `90376a87cec29cc22e93dc71b41e054ed2f0183bc515a52aa461fecd43cc008c`
- Manifest SHA-256: `cbf847da975a2dbea631b02a326d0a36d7734ac3ef7b0b82ca437bd3d26536e1`
- Evaluator SHA-256: `a69fb4de27b0be1531f7972e8689f891cfac71a769934624e24d136420ef5f5f`
- Git SHA: `7d9f4b7294968540ce24d53f1cecccfd28d1c03b`
- Git dirty: `True`
- Judge model: `gemini-3.1-flash-lite-preview`
- Checkpoint: `benchmark\tuvi_golden_dataset\sequential_ablation\results\P5_prompt_final\shards\A\checkpoints\evaluation_checkpoint.json`

## Execution completeness

- Expected pairs: 200
- Completed pairs: 200
- Failed pairs: 0
- Executed pairs: 200
- Resumed pairs: 0

> **Metric policy:** Sequential blind Judge v2 scores Faithfulness and Answer Relevancy. AI-judged Context Recall is not a headline metric.

## Overall metrics

| Config | Status | Items | Faithfulness | Answer relevancy | Latency p95 ms | Invalid markers |
|---|---:|---:|---:|---:|---:|---:|
| p5_prompt_1 | completed | 100 | 0.926 | 0.858 | 4649.16 | 0 |
| p5_prompt_2 | completed | 100 | 0.913 | 0.835 | 5410.09 | 0 |

## Failure and fallback summary

| Config | Failed | Generation backend fallback | Judge failure | No context | Retrieval backend fallback | Citation fallback |
|---|---:|---:|---:|---:|---:|---:|
| p5_prompt_1 | 0 | 0 | 0 | 0 | 0 | 1 |
| p5_prompt_2 | 0 | 0 | 0 | 0 | 0 | 0 |

## Ablation analysis

- Baseline config: `baseline_graph_sparse_rrf`
- Preliminary recommendation: `p5_prompt_1`
  - Preliminary heuristic ranks configs by context recall, citation coverage, faithfulness, answer relevancy, graph hit rate, and a small p95 latency penalty.
  - Selected `p5_prompt_1` with context_recall_avg=None, citation_coverage_rate=0.9973, p95_latency_ms=4649.16.
  - Treat this as a smoke/first-pass recommendation until official Gemini judge and full dataset runs are complete.

### Context recall ranking

| Rank | Config | Value |
|---:|---|---:|

### Citation coverage ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | p5_prompt_1 | 0.9973 |
| 2 | p5_prompt_2 | 0.989 |

### Graph hit ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | p5_prompt_1 | 0.967 |
| 2 | p5_prompt_2 | 0.967 |

### p95 latency ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | p5_prompt_1 | 4649.16 |
| 2 | p5_prompt_2 | 5410.09 |

### Retrieval miss summary

| Config | Miss count | Example item IDs |
|---|---:|---|
| p5_prompt_1 | 1 | TVQA-061 |
| p5_prompt_2 | 1 | TVQA-061 |

### Rerank miss summary

| Config | Miss count | Example item IDs |
|---|---:|---|
| p5_prompt_1 | 0 |  |
| p5_prompt_2 | 0 |  |

## Phân tích ablation generation prompt/model

- Phạm vi: So sánh prompt template và generation model, giữ retrieval config cố định để cô lập ảnh hưởng generation.
- Retrieval control: Retrieval stack cố định theo W6 integration candidate: chunk_semantic_embedding_bge_m3, Graph + Sparse + RRF + BGE cross-encoder reranker, dense off.
- Chính sách run: Run chính của task này là Gemini judge partial 10 câu balanced; full/expanded run sẽ để W7-CONFIG-01/W8 hoặc khi quota cho phép.
- Prompt templates: `tuvi_generation_grounded_v2, tuvi_generation_v1`
- Generation models: `gemini-3.1-flash-lite-preview`
- Ứng viên generation sơ bộ: prompt `tuvi_generation_v1` với model `gemini-3.1-flash-lite-preview` qua config `p5_prompt_1`
  - Đây là gợi ý sơ bộ cho W7-ABL-01 dựa trên partial run, không phải quyết định production cuối cùng.
  - Điểm ưu tiên Faithfulness và Answer Relevancy; p95 latency bị phạt nhẹ.
  - Ứng viên hiện tại là prompt `tuvi_generation_v1` với model `gemini-3.1-flash-lite-preview` qua config `p5_prompt_1`: faithfulness_avg=0.926, answer_relevancy_avg=0.858, citation_evidence_f1_avg=0.0313, p95_latency_ms=4649.16.
  - W7-CONFIG-01 sẽ tổng hợp thêm evidence retrieval/chunking/latency trước khi lock default_production.yaml.

### Xếp hạng theo Faithfulness

| Hạng | Prompt template | Model | Config | Giá trị |
|---:|---|---|---|---:|
| 1 | tuvi_generation_v1 | gemini-3.1-flash-lite-preview | p5_prompt_1 | 0.926 |
| 2 | tuvi_generation_grounded_v2 | gemini-3.1-flash-lite-preview | p5_prompt_2 | 0.913 |

### Xếp hạng theo Answer Relevancy

| Hạng | Prompt template | Model | Config | Giá trị |
|---:|---|---|---|---:|
| 1 | tuvi_generation_v1 | gemini-3.1-flash-lite-preview | p5_prompt_1 | 0.858 |
| 2 | tuvi_generation_grounded_v2 | gemini-3.1-flash-lite-preview | p5_prompt_2 | 0.835 |

### Xếp hạng theo Citation Coverage

| Hạng | Prompt template | Model | Config | Giá trị |
|---:|---|---|---|---:|

### Xếp hạng theo p95 latency

| Hạng | Prompt template | Model | Config | Giá trị |
|---:|---|---|---|---:|
| 1 | tuvi_generation_v1 | gemini-3.1-flash-lite-preview | p5_prompt_1 | 4649.16 |
| 2 | tuvi_generation_grounded_v2 | gemini-3.1-flash-lite-preview | p5_prompt_2 | 5410.09 |

## Metrics by question complexity

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| p5_prompt_1 | Direct | 10 | 1.0 | 0.91 | None | 0.0 | 0.75 | 3003.7 |
| p5_prompt_1 | One-hop | 46 | 0.9043 | 0.8 | None | 0.9783 | 1.0 | 4467.32 |
| p5_prompt_1 | Two-hop | 44 | 0.9318 | 0.9068 | None | 0.9773 | 1.0 | 5411.63 |
| p5_prompt_2 | Direct | 10 | 0.95 | 0.74 | None | 0.0 | 0.0 | 3715.41 |
| p5_prompt_2 | One-hop | 46 | 0.8978 | 0.8087 | None | 0.9783 | 1.0 | 5152.83 |
| p5_prompt_2 | Two-hop | 44 | 0.9205 | 0.8841 | None | 0.9773 | 1.0 | 5836.91 |

## Metrics by question family

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| p5_prompt_1 | core_identity | 10 | 1.0 | 0.91 | None | 0.0 | 0.75 | 3003.7 |
| p5_prompt_1 | dai_van_interpretation | 10 | 0.96 | 0.74 | None | 1.0 | 1.0 | 4837.37 |
| p5_prompt_1 | menh_cuc_relation | 10 | 0.8 | 0.81 | None | 1.0 | 1.0 | 3780.32 |
| p5_prompt_1 | menh_house_interpretation | 10 | 0.9 | 0.77 | None | 0.9 | 1.0 | 4081.77 |
| p5_prompt_1 | menh_tam_hop | 10 | 0.9 | 0.87 | None | 1.0 | 1.0 | 5953.89 |
| p5_prompt_1 | menh_xung_chieu | 10 | 0.92 | 0.95 | None | 1.0 | 1.0 | 4056.68 |
| p5_prompt_1 | special_state_interpretation | 10 | 0.88 | 0.78 | None | 1.0 | 1.0 | 3367.97 |
| p5_prompt_1 | synthesis_judgement | 10 | 0.98 | 0.91 | None | 0.9 | 1.0 | 5141.36 |
| p5_prompt_1 | than_cu_interpretation | 10 | 0.98 | 0.88 | None | 1.0 | 1.0 | 4267.56 |
| p5_prompt_1 | topic_house_plus_relations | 10 | 0.94 | 0.96 | None | 1.0 | 1.0 | 5336.8 |
| p5_prompt_2 | core_identity | 10 | 0.95 | 0.74 | None | 0.0 | 0.0 | 3715.41 |
| p5_prompt_2 | dai_van_interpretation | 10 | 0.94 | 0.8 | None | 1.0 | 1.0 | 5268.83 |
| p5_prompt_2 | menh_cuc_relation | 10 | 0.93 | 0.91 | None | 1.0 | 1.0 | 5108.06 |
| p5_prompt_2 | menh_house_interpretation | 10 | 0.88 | 0.73 | None | 0.9 | 1.0 | 5792.72 |
| p5_prompt_2 | menh_tam_hop | 10 | 0.91 | 0.86 | None | 1.0 | 1.0 | 5593.28 |
| p5_prompt_2 | menh_xung_chieu | 10 | 0.88 | 0.85 | None | 1.0 | 1.0 | 5040.88 |
| p5_prompt_2 | special_state_interpretation | 10 | 0.86 | 0.84 | None | 1.0 | 1.0 | 4548.16 |
| p5_prompt_2 | synthesis_judgement | 10 | 0.96 | 0.88 | None | 0.9 | 1.0 | 5673.7 |
| p5_prompt_2 | than_cu_interpretation | 10 | 0.9 | 0.8 | None | 1.0 | 1.0 | 4937.23 |
| p5_prompt_2 | topic_house_plus_relations | 10 | 0.92 | 0.94 | None | 1.0 | 1.0 | 6235.66 |

## Per-question results

### p5_prompt_1

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 2704.61 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 4 | 2850.25 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 2 | 2743.39 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | None | True | 1.0 | 2 | 2094.69 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 4 | 2209.18 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | None | True | 1.0 | 2 | 2816.05 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | None | True | 1.0 | 5 | 3110.64 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.2 | None | True | 1.0 | 4 | 2655.64 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 2624.67 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | None | True | 1.0 | 5 | 3059.66 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 2127.98 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.6 | None | True | 1.0 | 2 | 4532.88 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 4 | 3586.45 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 0.5 | 0.8 | None | True | 1.0 | 2 | 2385.11 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.6 | None | True | 1.0 | 3 | 2543.51 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 0.8 | 1.0 | None | True | 1.0 | 4 | 2602.73 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 1.0 | None | True | 1.0 | 3 | 3054.55 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 3024.97 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 2316.33 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 2866.74 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1533.98 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 3421.78 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 0.8 | 1.0 | None | True | 1.0 | 4 | 3260.69 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 2601.69 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.6 | None | True | 1.0 | 5 | 3238.74 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.6 | None | True | 1.0 | 4 | 4042.9 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.8 | None | True | 1.0 | 5 | 2834.08 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.5 | None | True | 1.0 | 5 | 4620.47 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 6 | 4223.35 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | None | True | 1.0 | 7 | 3825.79 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1496.33 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.7 | None | True | 1.0 | 5 | 3267.75 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 5 | 2928.7 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | None | True | 1.0 | 2 | 2212.66 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 3455.31 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 7517.43 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 1.0 | None | True | 1.0 | 3 | 2891.24 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 1.0 | None | True | 1.0 | 4 | 4605.49 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.6 | 0.8 | None | True | 1.0 | 2 | 6185.03 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 4645.86 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 2207.98 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 0.8 | 1.0 | None | True | 1.0 | 2 | 3530.41 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 4 | 4711.84 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | None | True | 1.0 | 4 | 3181.04 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.0 | None | True | 1.0 | 5 | 2421.0 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | None | True | 1.0 | 4 | 3774.93 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 1.0 | None | True | 1.0 | 6 | 4572.46 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 4366.77 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 3025.68 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 3593.57 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 2181.64 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.6 | 0.2 | None | True | 1.0 | 3 | 2807.91 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 2 | 2576.47 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 0.5 | 0.5 | None | True | 1.0 | 3 | 2891.53 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 0.8 | 1.0 | None | True | 1.0 | 3 | 2976.5 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | None | True | 1.0 | 4 | 2835.74 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 3115.67 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 0.5 | None | True | 1.0 | 4 | 4059.59 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 3892.66 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | None | True | 1.0 | 2 | 3007.24 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 0.6 | None | False | 0.75 | 1 | 3100.77 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 0.8 | 1.0 | None | True | 1.0 | 6 | 3374.55 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 5 | 2591.91 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | None | True | 1.0 | 2 | 2432.17 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 4 | 3243.2 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 0.8 | 1.0 | None | True | 1.0 | 4 | 3963.34 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 3426.29 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 2224.79 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | None | True | 1.0 | 5 | 2857.5 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | None | True | 1.0 | 5 | 2752.58 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1654.04 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 2816.54 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 3696.99 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | None | True | 1.0 | 2 | 2066.48 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 3261.22 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 3845.32 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 1.0 | None | True | 1.0 | 4 | 3297.04 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 5 | 3635.13 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 1.0 | None | True | 1.0 | 3 | 3414.3 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.8 | None | True | 1.0 | 4 | 3055.03 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 2885.05 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | None | False | 1.0 | 3 | 3137.86 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 4 | 2664.25 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 0.0 | 0.0 | None | True | 1.0 | 4 | 2928.46 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 0.6 | 1.0 | None | True | 1.0 | 5 | 2225.43 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 0.8 | 1.0 | None | True | 1.0 | 7 | 3671.67 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.9 | None | True | 1.0 | 3 | 3192.23 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.6 | None | True | 1.0 | 4 | 5014.83 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 6 | 4300.07 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.5 | None | False | 1.0 | 4 | 5546.77 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.5 | None | None | None | 1 | 2637.28 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.6 | None | True | 1.0 | 2 | 2143.24 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.6 | None | True | 1.0 | 3 | 3724.55 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | None | True | 1.0 | 2 | 4270.64 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 0.8 | 1.0 | None | True | 1.0 | 5 | 2984.69 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.5 | None | True | 1.0 | 2 | 3246.74 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.8 | None | True | 1.0 | 2 | 3414.04 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 4 | 3484.81 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 3143.37 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.8 | None | True | 1.0 | 4 | 3206.6 |  |

### p5_prompt_2

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1715.69 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 4604.36 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 2 | 4103.19 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 3228.34 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 4 | 4264.44 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 4292.78 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.9 | None | True | 1.0 | 3 | 5274.88 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.2 | None | True | 1.0 | 4 | 4899.39 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 5048.13 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.8 | 1.0 | None | True | 1.0 | 4 | 5156.33 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3199.44 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.6 | None | True | 1.0 | 3 | 4259.87 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 3 | 5167.59 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 0.5 | 1.0 | None | True | 1.0 | 2 | 3081.28 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.2 | 0.2 | None | True | 1.0 | 3 | 4116.51 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | None | True | 1.0 | 5 | 3103.31 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | None | True | 1.0 | 3 | 3820.47 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 4270.51 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 2934.36 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | None | True | 1.0 | 6 | 4241.75 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 2286.96 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 6 | 4218.58 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 5 | 4598.24 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 5108.56 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.6 | None | True | 1.0 | 6 | 4780.29 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | None | True | 1.0 | 5 | 5915.7 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.5 | None | True | 1.0 | 5 | 4743.39 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.8 | None | True | 1.0 | 6 | 5120.24 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 6 | 4931.36 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.9 | None | True | 1.0 | 7 | 6097.0 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3863.48 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 7 | 5799.83 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 4655.69 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 0.8 | 1.0 | None | True | 1.0 | 2 | 2597.35 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 6 | 3205.97 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | None | True | 1.0 | 4 | 5199.21 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | None | True | 1.0 | 3 | 4003.02 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 5 | 4358.34 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.2 | 0.4 | None | True | 1.0 | 6 | 7207.28 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.9 | None | True | 1.0 | 5 | 5128.63 |  |
| TVQA-041 | completed | Direct | core_identity | True | 0.5 | 0.5 | None | None | None | 1 | 3534.44 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | None | True | 1.0 | 5 | 5784.03 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 4 | 3802.06 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 5107.45 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 2 | 3135.8 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 0.8 | 1.0 | None | True | 1.0 | 5 | 4741.98 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 1.0 | None | True | 1.0 | 9 | 4392.96 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 5390.41 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 6 | 4065.77 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 4997.28 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3036.9 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.0 | None | True | 1.0 | 4 | 4665.76 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 2 | 3518.92 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.5 | None | True | 1.0 | 9 | 3750.66 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 0.8 | 1.0 | None | True | 1.0 | 4 | 3747.46 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.6 | None | True | 1.0 | 3 | 4964.43 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | None | True | 1.0 | 2 | 3699.52 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 4 | 4025.53 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 4512.43 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 4038.92 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 0.2 | None | False | 0.0 | 1 | 2453.53 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 6 | 3387.18 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 6 | 3414.78 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | None | True | 1.0 | 2 | 2141.91 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 4 | 3546.61 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | None | True | 1.0 | 5 | 3282.48 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 1.0 | None | True | 1.0 | 4 | 2993.46 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 3 | 3294.51 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 4717.46 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | None | True | 1.0 | 5 | 3737.61 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1563.22 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.8 | None | True | 1.0 | 5 | 2706.0 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 3 | 3215.39 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | None | True | 1.0 | 4 | 2683.3 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 2808.66 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | None | True | 1.0 | 5 | 3792.35 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 3485.63 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.6 | None | True | 1.0 | 4 | 3578.8 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 3 | 3301.97 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 2862.55 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 0.5 | None | None | None | 1 | 2284.04 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.6 | None | False | 1.0 | 3 | 3208.03 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 9 | 3413.52 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | None | True | 1.0 | 8 | 3547.23 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 0.8 | 1.0 | None | True | 1.0 | 5 | 2767.62 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | None | True | 1.0 | 6 | 3540.35 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.8 | None | True | 1.0 | 3 | 4754.89 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 3942.94 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 5 | 3417.6 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.2 | None | False | 1.0 | 5 | 3539.7 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.2 | None | None | None | 1 | 3358.96 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.6 | None | True | 1.0 | 4 | 3251.85 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 0.0 | 0.0 | None | True | 1.0 | 9 | 2711.72 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | None | True | 1.0 | 2 | 2531.03 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | None | True | 1.0 | 4 | 2644.8 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | None | True | 1.0 | 6 | 4131.5 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | None | True | 1.0 | 2 | 3417.45 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.8 | None | True | 1.0 | 5 | 2849.29 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | None | True | 1.0 | 6 | 3539.38 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.8 | None | True | 1.0 | 4 | 2666.7 |  |
