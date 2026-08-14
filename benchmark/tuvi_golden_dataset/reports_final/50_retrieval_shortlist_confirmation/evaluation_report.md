# W6 Evaluation report: w8_retrieval_shortlist_confirmation

- Dataset: `D:\University\Năm 3 ĐH\Kì 3 (18th6)\Text Mining\tuvi-battu-graphrag\benchmark\tuvi_golden_dataset\release\tuviqa_v1_release.jsonl`
- Dataset items: 100
- Configs: 3
- Judge backend: `gemini`
- Started: 2026-08-12T05:25:05.332646Z
- Completed: 2026-08-12T09:00:16.993217Z
- Notes: Controlled single-machine confirmation of the W8 retrieval shortlist. Holds semantic BGE-M3 chunking, structured prompt v3, Gemini Flash Lite, balanced context assembly, query rewrite off, document grading on, cache disabled, release dataset, and Gemini judging constant. It isolates Graph+Sparse RRF reranker on/off and Graph+Dense RRF reranker on. Artifacts are intentionally separate from the canonical W8 matrix.
- Run status: `completed`

## Run identity and provenance

- Identity SHA-256: `9dde3772e2f36e7051a7e530590f1499730ebf4f5f0b1471adbc26d19fb9ad52`
- Dataset SHA-256: `90376a87cec29cc22e93dc71b41e054ed2f0183bc515a52aa461fecd43cc008c`
- Manifest SHA-256: `b1771ac02f013f722da5a1ef40bc8ab4b0e7a08fee9bc194420977c8a6061ee9`
- Evaluator SHA-256: `487e4762a669fec1d4c3059f75d3665b35ad1327ea05ae5de6421dc41487ff8f`
- Git SHA: `8d642408ae16e22adce463882273dc74b3f17345`
- Git dirty: `False`
- Judge model: `gemini-3.1-flash-lite-preview`
- Checkpoint: `benchmark\tuvi_golden_dataset\reports_final\50_retrieval_shortlist_confirmation\checkpoints\evaluation_checkpoint.json`

## Execution completeness

- Expected pairs: 300
- Completed pairs: 300
- Failed pairs: 0
- Executed pairs: 276
- Resumed pairs: 24

> **Metric policy:** W6-EVAL-02 runs the RAG pipeline directly with the selected `ExperimentConfig`. `Context recall` is the Gemini-judged corpus-grounding score for non-Direct items; Direct/chart-only items are excluded from corpus retrieval/citation metrics and reported through `chart_context_grounding`.

## Overall metrics

| Config | Status | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms | Retrieval p95 ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| semantic_gs_rrf_rerank_on_control | completed | 100 | 0.89 | 0.79 | 0.7 | 0.967 | 0.978 | 190410.16 | 181112.51 |
| semantic_gs_rrf_rerank_off_candidate | completed | 100 | 0.916 | 0.829 | 0.7626 | 0.967 | 0.989 | 13283.52 | 7293.18 |
| semantic_gd_rrf_rerank_on_quality | completed | 100 | 0.908 | 0.819 | 0.7308 | 0.967 | 0.989 | 47950.25 | 41092.44 |

## Failure and fallback summary

| Config | Failed | Generation backend fallback | Judge failure | No context | Retrieval backend fallback | Citation fallback |
|---|---:|---:|---:|---:|---:|---:|
| semantic_gs_rrf_rerank_on_control | 0 | 0 | 0 | 0 | 0 | 1 |
| semantic_gs_rrf_rerank_off_candidate | 0 | 0 | 0 | 0 | 0 | 0 |
| semantic_gd_rrf_rerank_on_quality | 0 | 0 | 0 | 0 | 0 | 0 |

## Ablation analysis

- Baseline config: `baseline_graph_sparse_rrf`
- Preliminary recommendation: `semantic_gs_rrf_rerank_off_candidate`
  - Preliminary heuristic ranks configs by context recall, citation coverage, faithfulness, answer relevancy, graph hit rate, and a small p95 latency penalty.
  - Selected `semantic_gs_rrf_rerank_off_candidate` with context_recall_avg=0.7626, citation_coverage_rate=0.989, p95_latency_ms=13283.52.
  - Treat this as a smoke/first-pass recommendation until official Gemini judge and full dataset runs are complete.

### Context recall ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | semantic_gs_rrf_rerank_off_candidate | 0.7626 |
| 2 | semantic_gd_rrf_rerank_on_quality | 0.7308 |
| 3 | semantic_gs_rrf_rerank_on_control | 0.7 |

### Citation coverage ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | semantic_gs_rrf_rerank_off_candidate | 0.989 |
| 2 | semantic_gd_rrf_rerank_on_quality | 0.989 |
| 3 | semantic_gs_rrf_rerank_on_control | 0.978 |

### Graph hit ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | semantic_gs_rrf_rerank_on_control | 0.967 |
| 2 | semantic_gs_rrf_rerank_off_candidate | 0.967 |
| 3 | semantic_gd_rrf_rerank_on_quality | 0.967 |

### p95 latency ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | semantic_gs_rrf_rerank_off_candidate | 13283.52 |
| 2 | semantic_gd_rrf_rerank_on_quality | 47950.25 |
| 3 | semantic_gs_rrf_rerank_on_control | 190410.16 |

### Retrieval miss summary

| Config | Miss count | Example item IDs |
|---|---:|---|
| semantic_gs_rrf_rerank_on_control | 19 | TVQA-008, TVQA-010, TVQA-013, TVQA-017, TVQA-027 |
| semantic_gs_rrf_rerank_off_candidate | 14 | TVQA-008, TVQA-010, TVQA-027, TVQA-028, TVQA-032 |
| semantic_gd_rrf_rerank_on_quality | 15 | TVQA-010, TVQA-025, TVQA-027, TVQA-028, TVQA-032 |

### Rerank miss summary

| Config | Miss count | Example item IDs |
|---|---:|---|
| semantic_gs_rrf_rerank_on_control | 2 | TVQA-068, TVQA-080 |
| semantic_gs_rrf_rerank_off_candidate | 0 |  |
| semantic_gd_rrf_rerank_on_quality | 2 | TVQA-025, TVQA-084 |

## Metrics by question complexity

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| semantic_gs_rrf_rerank_on_control | Direct | 10 | 1.0 | 0.84 | 0.7 | 0.0 | 0.0 | 11547.8 |
| semantic_gs_rrf_rerank_on_control | One-hop | 46 | 0.8565 | 0.7783 | 0.7087 | 0.9783 | 1.0 | 212025.44 |
| semantic_gs_rrf_rerank_on_control | Two-hop | 44 | 0.9 | 0.7909 | 0.6909 | 0.9773 | 0.9773 | 176065.83 |
| semantic_gs_rrf_rerank_off_candidate | Direct | 10 | 1.0 | 0.81 | 0.7 | 0.0 | 0.0 | 5644.13 |
| semantic_gs_rrf_rerank_off_candidate | One-hop | 46 | 0.9326 | 0.8391 | 0.7957 | 0.9783 | 1.0 | 13064.02 |
| semantic_gs_rrf_rerank_off_candidate | Two-hop | 44 | 0.8795 | 0.8227 | 0.7295 | 0.9773 | 1.0 | 14796.54 |
| semantic_gd_rrf_rerank_on_quality | Direct | 10 | 1.0 | 0.85 | 1.0 | 0.0 | 0.0 | 15368.7 |
| semantic_gd_rrf_rerank_on_quality | One-hop | 46 | 0.8935 | 0.8348 | 0.7609 | 0.9783 | 1.0 | 52915.85 |
| semantic_gd_rrf_rerank_on_quality | Two-hop | 44 | 0.9023 | 0.7955 | 0.6932 | 0.9773 | 1.0 | 47625.0 |

## Metrics by question family

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| semantic_gs_rrf_rerank_on_control | core_identity | 10 | 1.0 | 0.84 | 0.7 | 0.0 | 0.0 | 11547.8 |
| semantic_gs_rrf_rerank_on_control | dai_van_interpretation | 10 | 0.85 | 0.64 | 0.53 | 1.0 | 1.0 | 177825.02 |
| semantic_gs_rrf_rerank_on_control | menh_cuc_relation | 10 | 0.96 | 0.92 | 0.88 | 1.0 | 1.0 | 143843.67 |
| semantic_gs_rrf_rerank_on_control | menh_house_interpretation | 10 | 0.82 | 0.7 | 0.64 | 0.9 | 1.0 | 322980.83 |
| semantic_gs_rrf_rerank_on_control | menh_tam_hop | 10 | 0.95 | 0.8 | 0.68 | 1.0 | 1.0 | 172708.2 |
| semantic_gs_rrf_rerank_on_control | menh_xung_chieu | 10 | 0.86 | 0.72 | 0.59 | 1.0 | 1.0 | 138791.17 |
| semantic_gs_rrf_rerank_on_control | special_state_interpretation | 10 | 0.77 | 0.72 | 0.61 | 1.0 | 1.0 | 170375.35 |
| semantic_gs_rrf_rerank_on_control | synthesis_judgement | 10 | 0.84 | 0.77 | 0.66 | 0.9 | 0.9 | 189059.78 |
| semantic_gs_rrf_rerank_on_control | than_cu_interpretation | 10 | 0.88 | 0.87 | 0.84 | 1.0 | 1.0 | 204287.66 |
| semantic_gs_rrf_rerank_on_control | topic_house_plus_relations | 10 | 0.97 | 0.92 | 0.87 | 1.0 | 1.0 | 144273.56 |
| semantic_gs_rrf_rerank_off_candidate | core_identity | 10 | 1.0 | 0.81 | 0.7 | 0.0 | 0.0 | 5644.13 |
| semantic_gs_rrf_rerank_off_candidate | dai_van_interpretation | 10 | 0.82 | 0.67 | 0.59 | 1.0 | 1.0 | 12036.19 |
| semantic_gs_rrf_rerank_off_candidate | menh_cuc_relation | 10 | 0.98 | 0.97 | 0.97 | 1.0 | 1.0 | 10574.4 |
| semantic_gs_rrf_rerank_off_candidate | menh_house_interpretation | 10 | 0.86 | 0.71 | 0.63 | 0.9 | 1.0 | 13288.94 |
| semantic_gs_rrf_rerank_off_candidate | menh_tam_hop | 10 | 0.87 | 0.81 | 0.7 | 1.0 | 1.0 | 13245.55 |
| semantic_gs_rrf_rerank_off_candidate | menh_xung_chieu | 10 | 0.85 | 0.8 | 0.65 | 1.0 | 1.0 | 11871.2 |
| semantic_gs_rrf_rerank_off_candidate | special_state_interpretation | 10 | 0.93 | 0.81 | 0.76 | 1.0 | 1.0 | 11913.81 |
| semantic_gs_rrf_rerank_off_candidate | synthesis_judgement | 10 | 0.93 | 0.91 | 0.84 | 0.9 | 1.0 | 22938.77 |
| semantic_gs_rrf_rerank_off_candidate | than_cu_interpretation | 10 | 0.98 | 0.93 | 0.9 | 1.0 | 1.0 | 13001.26 |
| semantic_gs_rrf_rerank_off_candidate | topic_house_plus_relations | 10 | 0.94 | 0.87 | 0.83 | 1.0 | 1.0 | 12959.35 |
| semantic_gd_rrf_rerank_on_quality | core_identity | 10 | 1.0 | 0.85 | 1.0 | 0.0 | 0.0 | 15368.7 |
| semantic_gd_rrf_rerank_on_quality | dai_van_interpretation | 10 | 0.92 | 0.74 | 0.62 | 1.0 | 1.0 | 40873.68 |
| semantic_gd_rrf_rerank_on_quality | menh_cuc_relation | 10 | 0.86 | 0.85 | 0.74 | 1.0 | 1.0 | 38060.1 |
| semantic_gd_rrf_rerank_on_quality | menh_house_interpretation | 10 | 0.93 | 0.79 | 0.76 | 0.9 | 1.0 | 136915.96 |
| semantic_gd_rrf_rerank_on_quality | menh_tam_hop | 10 | 0.86 | 0.76 | 0.65 | 1.0 | 1.0 | 47933.9 |
| semantic_gd_rrf_rerank_on_quality | menh_xung_chieu | 10 | 0.92 | 0.77 | 0.63 | 1.0 | 1.0 | 38099.0 |
| semantic_gd_rrf_rerank_on_quality | special_state_interpretation | 10 | 0.79 | 0.79 | 0.69 | 1.0 | 1.0 | 48867.96 |
| semantic_gd_rrf_rerank_on_quality | synthesis_judgement | 10 | 0.93 | 0.84 | 0.74 | 0.9 | 1.0 | 55869.88 |
| semantic_gd_rrf_rerank_on_quality | than_cu_interpretation | 10 | 0.95 | 0.94 | 0.9 | 1.0 | 1.0 | 46972.29 |
| semantic_gd_rrf_rerank_on_quality | topic_house_plus_relations | 10 | 0.92 | 0.86 | 0.82 | 1.0 | 1.0 | 38819.14 |

## Per-question results

### semantic_gs_rrf_rerank_on_control

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 11192.02 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.8 | 0.7 | True | 1.0 | 3 | 168781.7 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 142080.59 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 85160.41 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 6 | 144883.24 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 3 | 177744.64 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 145796.91 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.4 | 0.2 | True | 1.0 | 7 | 213288.83 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 6 | 147674.82 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.5 | 0.2 | True | 1.0 | 5 | 143532.81 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 10468.7 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.6 | 0.5 | True | 1.0 | 6 | 222029.05 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 9 | 208235.26 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 138242.24 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 6 | 174621.11 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 5 | 166552.54 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 6 | 130228.61 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 4 | 134480.37 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 125619.72 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 187991.66 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 11838.89 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.9 | 0.8 | True | 1.0 | 3 | 405577.74 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 9 | 199462.82 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 148426.65 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 6 | 165186.08 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 6 | 134786.09 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.5 | 0.2 | True | 1.0 | 7 | 97761.74 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 7 | 98182.75 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 140116.47 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 7 | 189933.7 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 2781.29 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 5 | 145667.01 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 101435.9 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 82269.53 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 7 | 123303.52 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 6 | 133246.23 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 7 | 126420.62 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 5 | 97700.84 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.7 | 0.4 | True | 1.0 | 4 | 113269.55 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 3 | 108122.7 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 4067.54 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 95218.21 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 99971.97 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 5 | 74593.97 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 5 | 119405.61 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 6 | 119946.06 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 5 | 118196.09 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 3 | 100945.86 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 96707.32 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 156123.68 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3161.04 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.2 | 0.2 | True | 1.0 | 6 | 130598.99 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 0.8 | True | 1.0 | 4 | 110846.67 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 5 | 81252.47 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 109332.29 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.6 | 0.4 | True | 1.0 | 2 | 93410.92 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 8 | 99463.33 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 3 | 94426.66 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 7 | 97687.31 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 0.2 | 0.2 | 0.2 | True | 1.0 | 4 | 133252.88 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 0.8 | 0.7 | False | 0.0 | 1 | 4603.0 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 6 | 97458.84 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 5 | 135803.87 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 87790.63 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 6 | 73204.19 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 5 | 96495.12 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 7 | 91143.0 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 97025.23 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 3 | 102332.31 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 4 | 99771.97 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4147.69 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 112141.65 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 139916.2 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 68657.99 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 0.5 | 0.5 | 0.0 | True | 1.0 | 4 | 91359.98 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 4 | 142950.26 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 2 | 107689.64 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 7 | 97594.17 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 107097.9 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.6 | 0.5 | True | 0.0 | 6 | 102238.94 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4426.64 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.6 | 0.5 | False | 1.0 | 5 | 127117.15 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 126951.77 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 73217.63 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 116070.99 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 6 | 124831.83 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 5 | 98177.05 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.4 | 0.2 | True | 1.0 | 4 | 88635.2 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 134510.9 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 0.8 | 1.0 | 0.7 | False | 1.0 | 6 | 136235.62 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.0 | None | None | None | 1 | 4335.64 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 6 | 92262.82 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 136240.92 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 86726.9 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 6 | 98814.85 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 2 | 94752.4 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 2 | 93227.3 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 0.6 | 0.4 | 0.2 | True | 1.0 | 7 | 80873.92 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 94897.67 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.9 | 0.8 | True | 1.0 | 6 | 113948.89 |  |

### semantic_gs_rrf_rerank_off_candidate

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4143.73 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 10250.71 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 9678.19 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 9333.95 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 5 | 11402.53 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 6 | 10388.1 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 6 | 10445.36 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.4 | 0.2 | True | 1.0 | 7 | 12725.59 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 10115.56 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.7 | 0.4 | True | 1.0 | 4 | 11908.26 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 6337.72 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.5 | True | 1.0 | 3 | 12216.15 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 5 | 11037.78 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 9003.95 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 6 | 9029.95 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.8 | True | 1.0 | 5 | 12037.37 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 3 | 9535.48 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 11193.6 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 12084.18 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 11286.82 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3453.02 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 13145.43 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 10003.64 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 1.0 | True | 1.0 | 4 | 11226.13 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 1.0 | True | 1.0 | 5 | 10591.85 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 6 | 13277.06 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.6 | 0.2 | True | 1.0 | 5 | 11409.16 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.2 | 0.3 | 0.2 | True | 1.0 | 7 | 10045.05 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 13675.4 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 7 | 26937.02 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 0.5 | None | None | None | 1 | 2097.34 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.4 | 0.2 | True | 1.0 | 5 | 12032.46 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 10334.81 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 9432.33 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 12209.06 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 6 | 13207.04 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 0.9 | 0.9 | 0.8 | True | 1.0 | 6 | 12249.23 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 7 | 10891.64 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.6 | 0.7 | 0.4 | True | 1.0 | 3 | 10195.42 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 0.9 | 0.9 | 0.8 | True | 1.0 | 5 | 11392.89 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 2979.98 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 9730.24 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 10750.01 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 8611.54 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.0 | 0.0 | True | 1.0 | 4 | 11055.51 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 12580.06 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 7 | 10990.39 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 4 | 10575.63 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 11113.51 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 14994.39 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3114.46 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.1 | 0.2 | True | 1.0 | 5 | 10913.66 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 9993.84 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 8998.09 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 5 | 10779.97 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.6 | True | 1.0 | 4 | 11776.3 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 0.9 | 1.0 | 1.0 | True | 1.0 | 3 | 9620.88 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 5 | 9693.84 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 9695.07 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 0.8 | 1.0 | 0.7 | True | 1.0 | 6 | 18052.02 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 0.8 | 0.7 | False | 0.0 | 1 | 3917.74 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 3 | 13406.36 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 5 | 11873.3 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 8484.85 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 6 | 9682.67 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 6 | 10103.3 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 0.6 | 0.5 | 0.2 | True | 1.0 | 4 | 9679.47 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 7 | 9788.71 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 4 | 9177.2 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 9289.14 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3814.04 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 5 | 9699.36 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 0.9 | 0.9 | 1.0 | True | 1.0 | 4 | 10779.28 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 7421.67 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 9991.67 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 4 | 10769.52 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 2 | 9702.42 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 7 | 10371.47 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 10107.96 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 5 | 9447.27 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4113.34 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.6 | 0.4 | False | 1.0 | 5 | 10080.05 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 13142.47 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 9777.85 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 9 | 10960.22 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 5 | 10028.07 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 0.9 | 0.9 | 0.8 | True | 1.0 | 3 | 9570.88 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 7 | 10629.78 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.5 | 0.6 | True | 1.0 | 9 | 9969.9 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 5 | 10269.13 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.0 | None | None | None | 1 | 4796.4 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 2 | 9486.63 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 5 | 12828.68 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 9190.16 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 11552.94 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 3 | 10487.21 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 2 | 10634.48 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 4 | 10071.31 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 6 | 11446.7 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 11890.4 |  |

### semantic_gd_rrf_rerank_on_quality

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3955.99 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 198628.33 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 40745.52 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 26327.97 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 40306.88 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 2 | 47943.31 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 5 | 38236.12 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 5 | 40830.16 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 33650.05 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 4 | 34499.92 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 4080.83 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.6 | 0.5 | True | 1.0 | 5 | 39805.01 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 2 | 40091.24 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 0.9 | 1.0 | 1.0 | True | 1.0 | 4 | 26335.77 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 5 | 35227.95 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 35501.56 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 6 | 32479.37 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 3 | 36383.73 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 1.0 | 1.0 | True | 1.0 | 8 | 33684.86 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 42776.39 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 24387.92 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 0.9 | 0.8 | 1.0 | True | 1.0 | 5 | 61489.74 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 41754.36 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.9 | 1.0 | True | 1.0 | 4 | 32776.98 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 3 | 39496.98 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 4 | 47922.41 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 4 | 32881.59 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.5 | 0.4 | True | 1.0 | 4 | 38295.93 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 4 | 39574.71 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 6 | 65411.41 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 2108.42 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 3 | 40498.57 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 33423.78 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 3 | 32661.89 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 41951.2 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 6 | 37542.03 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 37931.41 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.7 | 0.4 | True | 1.0 | 4 | 36888.97 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.6 | 0.5 | 0.2 | True | 1.0 | 4 | 36795.09 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 0.9 | 0.9 | 0.8 | True | 1.0 | 6 | 34302.04 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 3059.55 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 3 | 33224.28 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 36771.97 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 28672.13 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 4 | 36944.69 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 4 | 35646.28 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 4 | 37901.72 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 7 | 40909.28 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 32314.26 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 44208.01 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3371.14 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 3 | 42719.8 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 36664.16 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 5 | 31207.91 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 54527.12 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 31519.22 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 32898.14 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 5 | 34568.78 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 4 | 37895.66 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 41064.25 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 0.9 | 1.0 | False | 0.0 | 1 | 4070.08 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 6 | 28395.79 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 4 | 48082.05 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 38947.63 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 5 | 30999.24 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 3 | 32578.33 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.5 | 0.0 | True | 1.0 | 5 | 28832.89 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 30333.5 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 3 | 33626.14 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 3 | 34598.91 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3991.37 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 36923.37 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 45613.69 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 0.5 | 0.2 | 0.0 | True | 1.0 | 4 | 26197.88 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 0.5 | 0.6 | 0.3 | True | 1.0 | 4 | 33016.52 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 4 | 38794.06 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 4 | 34224.88 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 4 | 38686.97 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 30199.28 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.2 | 0.0 | True | 1.0 | 5 | 34005.09 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4345.21 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 5 | 14759.34 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 0.9 | 0.9 | 1.0 | True | 1.0 | 5 | 45615.91 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 2 | 24897.21 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 39791.19 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 6 | 45939.66 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 6 | 31096.85 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.6 | 0.5 | True | 1.0 | 4 | 35109.38 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 35922.32 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 3 | 16217.57 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.2 | None | None | None | 1 | 4224.34 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 32768.27 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 42797.1 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 0.8 | 1.0 | 0.6 | True | 1.0 | 3 | 36975.34 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 4 | 38691.02 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.4 | 0.2 | True | 1.0 | 4 | 31754.65 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 3 | 32731.42 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 4 | 33625.16 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 3 | 34061.37 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 43679.38 |  |
