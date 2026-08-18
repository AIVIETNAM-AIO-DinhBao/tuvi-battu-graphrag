# W6 Evaluation report: w8_reranker_top_k_sweep

- Dataset: `D:\University\Năm 3 ĐH\Kì 3 (18th6)\Text Mining\tuvi-battu-graphrag\benchmark\tuvi_golden_dataset\release\tuviqa_v1_release.jsonl`
- Dataset items: 100
- Configs: 4
- Judge backend: `gemini`
- Started: 2026-08-15T01:33:56.123582Z
- Completed: 2026-08-15T01:33:56.290478Z
- Notes: Controlled Phase 52 top-k sweep for the model-backed reranker. Holds semantic BGE-M3 chunking, structured prompt v3, Gemini Flash Lite, Graph+Sparse retrieval, RRF fusion, query rewrite off, document grading on, balanced context assembly, cache disabled, release dataset, and Gemini judging constant. It tests whether the Phase 50 reranker regression is caused by pruning the fused candidate pool to top 10 before document grading/context assembly. Artifacts are separate from W8 and Phase 50.
- Run status: `completed`

## Run identity and provenance

- Identity SHA-256: `5790e4b71aef4d1a8b3dca56e2a36830b5304ff2651f48f4bfebf7cd66d03145`
- Dataset SHA-256: `90376a87cec29cc22e93dc71b41e054ed2f0183bc515a52aa461fecd43cc008c`
- Manifest SHA-256: `3ea782f6f1f5684db99162947b04e2f4f8d5e3ee0aef835be570115c30e94d53`
- Evaluator SHA-256: `487e4762a669fec1d4c3059f75d3665b35ad1327ea05ae5de6421dc41487ff8f`
- Git SHA: `3d3d4afc2939c2eb8438de2ce3c55c6d0e05a2f1`
- Git dirty: `False`
- Judge model: `gemini-3.1-flash-lite-preview`
- Checkpoint: `benchmark\tuvi_golden_dataset\reports_final\52_reranker_top_k_sweep\checkpoints\evaluation_checkpoint.json`

## Execution completeness

- Expected pairs: 400
- Completed pairs: 400
- Failed pairs: 0
- Executed pairs: 0
- Resumed pairs: 400

> **Metric policy:** W6-EVAL-02 runs the RAG pipeline directly with the selected `ExperimentConfig`. `Context recall` is the Gemini-judged corpus-grounding score for non-Direct items; Direct/chart-only items are excluded from corpus retrieval/citation metrics and reported through `chart_context_grounding`.

## Overall metrics

| Config | Status | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms | Retrieval p95 ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| semantic_gs_rrf_rerank_k10_control | completed | 100 | 0.888 | 0.795 | 0.7088 | 0.967 | 0.9863 | 175499.24 | 163993.71 |
| semantic_gs_rrf_rerank_k20 | completed | 100 | 0.914 | 0.808 | 0.7484 | 0.967 | 0.989 | 156730.69 | 143343.65 |
| semantic_gs_rrf_rerank_k40 | completed | 100 | 0.906 | 0.83 | 0.7571 | 0.967 | 0.989 | 168191.23 | 162516.16 |
| semantic_gs_rrf_no_rerank_reference | completed | 100 | 0.888 | 0.815 | 0.7407 | 0.967 | 0.989 | 21543.56 | 8321.1 |

## Failure and fallback summary

| Config | Failed | Generation backend fallback | Judge failure | No context | Retrieval backend fallback | Citation fallback |
|---|---:|---:|---:|---:|---:|---:|
| semantic_gs_rrf_rerank_k10_control | 0 | 0 | 0 | 0 | 0 | 0 |
| semantic_gs_rrf_rerank_k20 | 0 | 0 | 0 | 0 | 0 | 1 |
| semantic_gs_rrf_rerank_k40 | 0 | 0 | 0 | 0 | 0 | 0 |
| semantic_gs_rrf_no_rerank_reference | 0 | 0 | 0 | 0 | 0 | 0 |

## Ablation analysis

- Baseline config: `baseline_graph_sparse_rrf`
- Preliminary recommendation: `semantic_gs_rrf_rerank_k40`
  - Preliminary heuristic ranks configs by context recall, citation coverage, faithfulness, answer relevancy, graph hit rate, and a small p95 latency penalty.
  - Selected `semantic_gs_rrf_rerank_k40` with context_recall_avg=0.7571, citation_coverage_rate=0.989, p95_latency_ms=168191.23.
  - Treat this as a smoke/first-pass recommendation until official Gemini judge and full dataset runs are complete.

### Context recall ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | semantic_gs_rrf_rerank_k40 | 0.7571 |
| 2 | semantic_gs_rrf_rerank_k20 | 0.7484 |
| 3 | semantic_gs_rrf_no_rerank_reference | 0.7407 |
| 4 | semantic_gs_rrf_rerank_k10_control | 0.7088 |

### Citation coverage ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | semantic_gs_rrf_rerank_k20 | 0.989 |
| 2 | semantic_gs_rrf_rerank_k40 | 0.989 |
| 3 | semantic_gs_rrf_no_rerank_reference | 0.989 |
| 4 | semantic_gs_rrf_rerank_k10_control | 0.9863 |

### Graph hit ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | semantic_gs_rrf_rerank_k10_control | 0.967 |
| 2 | semantic_gs_rrf_rerank_k20 | 0.967 |
| 3 | semantic_gs_rrf_rerank_k40 | 0.967 |
| 4 | semantic_gs_rrf_no_rerank_reference | 0.967 |

### p95 latency ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | semantic_gs_rrf_no_rerank_reference | 21543.56 |
| 2 | semantic_gs_rrf_rerank_k20 | 156730.69 |
| 3 | semantic_gs_rrf_rerank_k40 | 168191.23 |
| 4 | semantic_gs_rrf_rerank_k10_control | 175499.24 |

### Retrieval miss summary

| Config | Miss count | Example item IDs |
|---|---:|---|
| semantic_gs_rrf_rerank_k10_control | 19 | TVQA-008, TVQA-010, TVQA-025, TVQA-027, TVQA-028 |
| semantic_gs_rrf_rerank_k20 | 14 | TVQA-010, TVQA-012, TVQA-027, TVQA-028, TVQA-032 |
| semantic_gs_rrf_rerank_k40 | 11 | TVQA-008, TVQA-010, TVQA-027, TVQA-039, TVQA-045 |
| semantic_gs_rrf_no_rerank_reference | 13 | TVQA-008, TVQA-010, TVQA-028, TVQA-032, TVQA-038 |

### Rerank miss summary

| Config | Miss count | Example item IDs |
|---|---:|---|
| semantic_gs_rrf_rerank_k10_control | 2 | TVQA-068, TVQA-084 |
| semantic_gs_rrf_rerank_k20 | 0 |  |
| semantic_gs_rrf_rerank_k40 | 0 |  |
| semantic_gs_rrf_no_rerank_reference | 0 |  |

## Metrics by question complexity

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| semantic_gs_rrf_rerank_k10_control | Direct | 10 | 1.0 | 0.86 | 0.7 | 0.0 | 0.0 | 10337.39 |
| semantic_gs_rrf_rerank_k10_control | One-hop | 46 | 0.8826 | 0.8087 | 0.7326 | 0.9783 | 0.9946 | 182758.69 |
| semantic_gs_rrf_rerank_k10_control | Two-hop | 44 | 0.8682 | 0.7659 | 0.6841 | 0.9773 | 1.0 | 168113.29 |
| semantic_gs_rrf_rerank_k20 | Direct | 10 | 0.98 | 0.83 | 0.7 | 0.0 | 0.0 | 20942.06 |
| semantic_gs_rrf_rerank_k20 | One-hop | 46 | 0.9152 | 0.8239 | 0.7739 | 0.9783 | 1.0 | 158275.85 |
| semantic_gs_rrf_rerank_k20 | Two-hop | 44 | 0.8977 | 0.7864 | 0.7227 | 0.9773 | 1.0 | 155377.38 |
| semantic_gs_rrf_rerank_k40 | Direct | 10 | 1.0 | 0.81 | 0.6 | 0.0 | 0.0 | 18605.05 |
| semantic_gs_rrf_rerank_k40 | One-hop | 46 | 0.8957 | 0.8326 | 0.7793 | 0.9783 | 1.0 | 162084.43 |
| semantic_gs_rrf_rerank_k40 | Two-hop | 44 | 0.8955 | 0.8318 | 0.7375 | 0.9773 | 1.0 | 172411.33 |
| semantic_gs_rrf_no_rerank_reference | Direct | 10 | 1.0 | 0.81 | 0.8 | 0.0 | 0.0 | 27542.93 |
| semantic_gs_rrf_no_rerank_reference | One-hop | 46 | 0.8826 | 0.8174 | 0.75 | 0.9783 | 1.0 | 23486.2 |
| semantic_gs_rrf_no_rerank_reference | Two-hop | 44 | 0.8682 | 0.8136 | 0.7295 | 0.9773 | 1.0 | 20075.08 |

## Metrics by question family

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| semantic_gs_rrf_rerank_k10_control | core_identity | 10 | 1.0 | 0.86 | 0.7 | 0.0 | 0.0 | 10337.39 |
| semantic_gs_rrf_rerank_k10_control | dai_van_interpretation | 10 | 0.84 | 0.63 | 0.49 | 1.0 | 1.0 | 130675.44 |
| semantic_gs_rrf_rerank_k10_control | menh_cuc_relation | 10 | 0.94 | 0.93 | 0.93 | 1.0 | 0.975 | 158617.67 |
| semantic_gs_rrf_rerank_k10_control | menh_house_interpretation | 10 | 0.9 | 0.71 | 0.62 | 0.9 | 1.0 | 184754.36 |
| semantic_gs_rrf_rerank_k10_control | menh_tam_hop | 10 | 0.94 | 0.82 | 0.7 | 1.0 | 1.0 | 169676.82 |
| semantic_gs_rrf_rerank_k10_control | menh_xung_chieu | 10 | 0.78 | 0.74 | 0.66 | 1.0 | 1.0 | 138722.93 |
| semantic_gs_rrf_rerank_k10_control | special_state_interpretation | 10 | 0.78 | 0.73 | 0.63 | 1.0 | 1.0 | 170537.18 |
| semantic_gs_rrf_rerank_k10_control | synthesis_judgement | 10 | 0.84 | 0.72 | 0.64 | 0.9 | 1.0 | 185522.25 |
| semantic_gs_rrf_rerank_k10_control | than_cu_interpretation | 10 | 0.94 | 0.95 | 0.89 | 1.0 | 1.0 | 173078.85 |
| semantic_gs_rrf_rerank_k10_control | topic_house_plus_relations | 10 | 0.92 | 0.86 | 0.82 | 1.0 | 1.0 | 142529.94 |
| semantic_gs_rrf_rerank_k20 | core_identity | 10 | 0.98 | 0.83 | 0.7 | 0.0 | 0.0 | 20942.06 |
| semantic_gs_rrf_rerank_k20 | dai_van_interpretation | 10 | 0.86 | 0.67 | 0.59 | 1.0 | 1.0 | 120501.75 |
| semantic_gs_rrf_rerank_k20 | menh_cuc_relation | 10 | 1.0 | 0.92 | 0.94 | 1.0 | 1.0 | 90713.4 |
| semantic_gs_rrf_rerank_k20 | menh_house_interpretation | 10 | 0.93 | 0.77 | 0.69 | 0.9 | 1.0 | 166260.4 |
| semantic_gs_rrf_rerank_k20 | menh_tam_hop | 10 | 0.95 | 0.83 | 0.78 | 1.0 | 1.0 | 145629.52 |
| semantic_gs_rrf_rerank_k20 | menh_xung_chieu | 10 | 0.87 | 0.67 | 0.62 | 1.0 | 1.0 | 128669.1 |
| semantic_gs_rrf_rerank_k20 | special_state_interpretation | 10 | 0.82 | 0.75 | 0.65 | 1.0 | 1.0 | 129680.47 |
| semantic_gs_rrf_rerank_k20 | synthesis_judgement | 10 | 0.91 | 0.86 | 0.77 | 0.9 | 1.0 | 180147.85 |
| semantic_gs_rrf_rerank_k20 | than_cu_interpretation | 10 | 0.88 | 0.87 | 0.85 | 1.0 | 1.0 | 161223.79 |
| semantic_gs_rrf_rerank_k20 | topic_house_plus_relations | 10 | 0.94 | 0.91 | 0.85 | 1.0 | 1.0 | 150462.21 |
| semantic_gs_rrf_rerank_k40 | core_identity | 10 | 1.0 | 0.81 | 0.6 | 0.0 | 0.0 | 18605.05 |
| semantic_gs_rrf_rerank_k40 | dai_van_interpretation | 10 | 0.83 | 0.67 | 0.59 | 1.0 | 1.0 | 123119.77 |
| semantic_gs_rrf_rerank_k40 | menh_cuc_relation | 10 | 0.97 | 0.94 | 0.925 | 1.0 | 1.0 | 141418.88 |
| semantic_gs_rrf_rerank_k40 | menh_house_interpretation | 10 | 0.89 | 0.83 | 0.77 | 0.9 | 1.0 | 160597.75 |
| semantic_gs_rrf_rerank_k40 | menh_tam_hop | 10 | 0.9 | 0.84 | 0.73 | 1.0 | 1.0 | 152479.18 |
| semantic_gs_rrf_rerank_k40 | menh_xung_chieu | 10 | 0.87 | 0.78 | 0.67 | 1.0 | 1.0 | 137222.48 |
| semantic_gs_rrf_rerank_k40 | special_state_interpretation | 10 | 0.82 | 0.75 | 0.66 | 1.0 | 1.0 | 143437.43 |
| semantic_gs_rrf_rerank_k40 | synthesis_judgement | 10 | 0.93 | 0.89 | 0.765 | 0.9 | 1.0 | 207908.29 |
| semantic_gs_rrf_rerank_k40 | than_cu_interpretation | 10 | 0.89 | 0.88 | 0.84 | 1.0 | 1.0 | 166124.0 |
| semantic_gs_rrf_rerank_k40 | topic_house_plus_relations | 10 | 0.96 | 0.91 | 0.88 | 1.0 | 1.0 | 163271.43 |
| semantic_gs_rrf_no_rerank_reference | core_identity | 10 | 1.0 | 0.81 | 0.8 | 0.0 | 0.0 | 27542.93 |
| semantic_gs_rrf_no_rerank_reference | dai_van_interpretation | 10 | 0.81 | 0.64 | 0.55 | 1.0 | 1.0 | 23857.41 |
| semantic_gs_rrf_no_rerank_reference | menh_cuc_relation | 10 | 1.0 | 0.92 | 0.88 | 1.0 | 1.0 | 23242.15 |
| semantic_gs_rrf_no_rerank_reference | menh_house_interpretation | 10 | 0.77 | 0.71 | 0.6 | 0.9 | 1.0 | 21903.1 |
| semantic_gs_rrf_no_rerank_reference | menh_tam_hop | 10 | 0.92 | 0.84 | 0.73 | 1.0 | 1.0 | 19184.5 |
| semantic_gs_rrf_no_rerank_reference | menh_xung_chieu | 10 | 0.82 | 0.79 | 0.71 | 1.0 | 1.0 | 19606.64 |
| semantic_gs_rrf_no_rerank_reference | special_state_interpretation | 10 | 0.78 | 0.77 | 0.68 | 1.0 | 1.0 | 19183.05 |
| semantic_gs_rrf_no_rerank_reference | synthesis_judgement | 10 | 0.92 | 0.86 | 0.77 | 0.9 | 1.0 | 17497.45 |
| semantic_gs_rrf_no_rerank_reference | than_cu_interpretation | 10 | 0.98 | 0.96 | 0.95 | 1.0 | 1.0 | 15431.81 |
| semantic_gs_rrf_no_rerank_reference | topic_house_plus_relations | 10 | 0.88 | 0.85 | 0.79 | 1.0 | 1.0 | 18816.15 |

## Per-question results

### semantic_gs_rrf_rerank_k10_control

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 7033.44 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 4 | 183303.51 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 122966.93 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 84649.14 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 5 | 132286.04 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 2 | 175203.19 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 131156.38 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.4 | 0.3 | True | 1.0 | 7 | 142437.95 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 6 | 135885.27 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.6 | 0.2 | True | 1.0 | 7 | 141267.8 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 12557.56 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 8 | 164633.93 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 162579.4 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 88545.94 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 6 | 111081.71 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 5 | 154383.83 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 1.0 | True | 1.0 | 4 | 118372.93 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 116299.03 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 7 | 124175.04 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 7 | 138251.18 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 6854.85 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 3 | 185941.42 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 173859.12 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.9 | 1.0 | True | 1.0 | 4 | 209435.29 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 5 | 157597.46 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 5 | 150557.73 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.2 | 0.3 | 0.2 | True | 1.0 | 7 | 105093.08 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.2 | 0.2 | True | 1.0 | 7 | 96969.94 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 147966.49 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 4 | 199016.45 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 2663.86 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.6 | 0.4 | 0.2 | True | 1.0 | 9 | 158541.72 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 111721.8 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 96507.25 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 181124.23 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 5 | 149692.59 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 6 | 140399.92 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 5 | 107092.49 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.6 | 0.4 | 0.2 | True | 1.0 | 4 | 130319.05 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 3 | 120060.19 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 3099.65 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 104536.39 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 109607.57 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 86611.11 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 4 | 128328.56 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 6 | 136039.53 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 7 | 136673.27 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 6 | 108415.28 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 3 | 113450.06 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 169029.34 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 6689.08 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.2 | 0.2 | True | 1.0 | 5 | 135253.54 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 0.8 | 1.0 | 0.8 | True | 1.0 | 4 | 125094.21 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 5 | 88269.9 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 122339.34 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 3 | 102480.93 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 8 | 106977.27 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 5 | 100115.3 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 105027.62 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 0.2 | 0.0 | 0.2 | True | 1.0 | 3 | 146250.69 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 0.8 | 0.7 | False | 0.0 | 1 | 5878.55 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 3 | 88322.1 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 144769.31 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 93143.45 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 6 | 77877.11 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 5 | 119804.98 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 7 | 116269.07 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 100444.87 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 130748.75 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 3 | 121374.54 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4578.6 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 4 | 140555.11 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 2 | 172125.18 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 2 | 85321.02 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 0.2 | 0.4 | 0.0 | True | 1.0 | 6 | 112849.09 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.9 | 0.8 | True | 1.0 | 4 | 162922.37 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 2 | 103457.77 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 6 | 101699.24 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 7 | 107780.52 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.4 | 0.2 | True | 1.0 | 7 | 101551.33 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4399.05 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.6 | 0.5 | False | 1.0 | 3 | 124456.81 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 126011.97 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.9 | 1.0 | True | 0.75 | 1 | 74602.38 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 122931.67 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 5 | 132029.73 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 3 | 97628.61 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.4 | 0.2 | True | 1.0 | 5 | 86126.24 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 131848.39 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 6 | 134032.5 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.2 | None | None | None | 1 | 7623.85 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 6 | 91499.91 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 144490.03 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 3 | 86160.08 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 97788.24 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 2 | 96472.07 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 5 | 89501.95 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 4 | 82880.16 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 6 | 98460.73 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 6 | 116423.14 |  |

### semantic_gs_rrf_rerank_k20

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 6736.7 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 95569.39 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 104157.46 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 69961.6 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 6 | 119205.11 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 148513.76 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 7 | 128697.49 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 8 | 129017.99 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 156588.61 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.5 | 0.2 | True | 1.0 | 4 | 135552.68 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 8021.12 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.4 | 0.2 | True | 1.0 | 4 | 171848.66 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 169672.14 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 91092.15 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 9 | 112946.79 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 126525.47 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 6 | 96969.48 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 5 | 96293.87 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 100290.05 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 113956.23 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 11573.58 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 154812.52 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 116673.73 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 1.0 | True | 1.0 | 4 | 86365.04 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 6 | 113372.9 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 5 | 129904.79 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.5 | 0.4 | True | 1.0 | 4 | 95739.64 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.2 | 0.2 | True | 1.0 | 5 | 92491.32 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 6 | 142974.39 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 193678.73 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 3462.96 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 8 | 152557.84 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 7 | 105124.61 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 81975.07 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 8 | 128859.89 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 136280.58 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 6 | 128634.41 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 4 | 100462.68 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.4 | 0.6 | 0.2 | True | 1.0 | 6 | 124255.32 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 5 | 111291.46 |  |
| TVQA-041 | completed | Direct | core_identity | True | 0.8 | 0.7 | None | None | None | 1 | 8082.89 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 113506.92 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 7 | 98915.11 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 5 | 75229.17 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 6 | 130351.85 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 4 | 131641.62 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 7 | 125298.72 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 3 | 102302.12 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 96590.96 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 163610.11 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 26507.27 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.2 | 0.0 | True | 1.0 | 6 | 134732.76 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 6 | 133538.53 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 5 | 80810.86 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 124193.54 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 112737.44 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 1.0 | True | 1.0 | 4 | 98887.49 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 0.2 | 0.2 | 0.2 | True | 1.0 | 6 | 94856.18 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 5 | 100781.98 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 0.8 | 1.0 | 0.8 | True | 1.0 | 4 | 133394.53 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 0.8 | 0.7 | False | 0.0 | 1 | 5055.17 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 85078.08 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 148067.04 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 90250.48 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 6 | 74581.83 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 5 | 103195.29 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 6 | 92673.25 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 7 | 84280.78 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 3 | 106826.67 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 0.9 | 0.9 | 0.8 | True | 1.0 | 4 | 107720.87 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 12062.9 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 0.9 | 1.0 | 0.8 | True | 1.0 | 4 | 120967.43 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 4 | 150898.02 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 1.0 | True | 1.0 | 2 | 77373.94 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 8 | 100552.74 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 4 | 142104.33 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.0 | 0.0 | True | 1.0 | 7 | 109636.47 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 3 | 110093.01 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 121571.47 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 5 | 101797.57 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4763.73 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.7 | False | 1.0 | 4 | 159430.3 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 149977.67 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 74498.4 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 115017.76 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 0.9 | True | 1.0 | 6 | 127132.53 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 3 | 96911.6 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 6 | 90416.67 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 134076.48 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 5 | 148359.47 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.0 | None | None | None | 1 | 14140.14 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 3 | 97066.49 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 143184.79 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 88615.44 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 100649.38 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.4 | 0.2 | True | 1.0 | 6 | 99170.94 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 3 | 103988.28 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 3 | 81981.51 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 4 | 99077.06 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 6 | 119290.65 |  |

### semantic_gs_rrf_rerank_k40

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4183.44 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 98485.6 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 116142.19 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 72089.57 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 6 | 124382.33 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 142165.16 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 8 | 113674.15 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.2 | 0.3 | True | 1.0 | 8 | 114238.1 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 105244.97 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.5 | 0.0 | True | 1.0 | 5 | 105549.87 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 23721.51 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.5 | True | 1.0 | 3 | 147953.35 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 5 | 137552.32 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 0.9 | 1.0 | 1.0 | True | 1.0 | 4 | 71902.23 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 8 | 87752.63 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 129063.21 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 4 | 109344.23 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 4 | 103972.75 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 101201.34 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 121855.47 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 10473.42 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 0.9 | 1.0 | 1.0 | True | 1.0 | 6 | 160076.62 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 152921.04 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 108564.01 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 7 | 122486.47 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 4 | 138239.27 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.5 | 0.2 | True | 1.0 | 5 | 101835.57 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 5 | 117533.97 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 148973.57 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 5 | 186387.08 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 2890.5 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.9 | 0.8 | True | 1.0 | 6 | 149759.78 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 106399.54 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 104652.06 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 8 | 135997.81 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 3 | 137237.64 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 0.9 | 0.9 | 0.8 | True | 1.0 | 7 | 135991.27 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 5 | 117005.73 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.6 | 0.5 | 0.4 | True | 1.0 | 4 | 135805.26 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 148259.14 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 5273.3 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 104998.32 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 113160.9 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 4 | 83619.18 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 6 | 128921.68 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 127414.18 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 7 | 138229.83 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 6 | 103787.18 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 96929.09 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 170398.91 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 7884.47 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.1 | 0.0 | True | 1.0 | 7 | 148590.4 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 0.0 | 0.5 | 0.0 | True | 1.0 | 4 | 117588.38 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.75 | True | 1.0 | 6 | 162894.48 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 146904.36 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 129510.51 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 0.9 | 0.9 | 1.0 | True | 1.0 | 6 | 131484.46 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 0.2 | 0.2 | 0.2 | True | 1.0 | 7 | 127603.76 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 5 | 151666.39 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 0.8 | 1.0 | 0.7 | True | 1.0 | 4 | 225516.56 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 0.7 | 0.6 | False | 0.0 | 1 | 12351.59 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 5 | 112524.95 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 7 | 169190.16 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 115170.93 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 6 | 101144.18 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 136956.5 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 6 | 127723.91 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 7 | 105565.08 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 3 | 144489.9 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 132920.67 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 6890.37 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 155455.01 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 157938.63 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 73006.28 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 7 | 95181.23 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.9 | 0.8 | True | 1.0 | 3 | 140850.6 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 2 | 119877.53 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.9 | 0.8 | True | 1.0 | 6 | 99485.24 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 120811.72 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.8 | 0.75 | True | 1.0 | 4 | 128586.99 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 7479.62 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.7 | False | 1.0 | 4 | 161024.13 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 7 | 161208.31 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 89941.38 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 139200.08 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.9 | 0.8 | True | 1.0 | 6 | 160917.93 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 3 | 131818.43 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 0.9 | 0.7 | 0.6 | True | 1.0 | 6 | 117639.34 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 172766.46 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 5 | 168138.65 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.0 | None | None | None | 1 | 7687.05 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 0.9 | True | 1.0 | 2 | 105565.55 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 0.9 | 1.0 | 1.0 | True | 1.0 | 5 | 162376.47 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 99567.24 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 6 | 104298.17 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 5 | 107239.67 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 3 | 93011.87 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.6 | 0.4 | True | 1.0 | 4 | 88047.32 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 97205.09 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 6 | 111382.89 |  |

### semantic_gs_rrf_no_rerank_reference

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 5348.07 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 4 | 15691.15 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 14771.79 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 10172.8 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 7 | 22518.86 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 7 | 16945.57 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 0.9 | 0.9 | 1.0 | True | 1.0 | 6 | 12890.12 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.2 | 0.2 | True | 1.0 | 7 | 13790.95 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 10347.98 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.7 | 0.4 | True | 1.0 | 5 | 11167.16 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 4061.04 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 5 | 23808.65 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 5 | 11303.3 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 13584.37 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 11030.16 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 11543.69 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 11400.98 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 7 | 15161.54 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 10558.36 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 16847.97 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4314.24 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 0.9 | 1.0 | 1.0 | True | 1.0 | 6 | 18822.63 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 13796.93 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 13562.83 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 5 | 11739.07 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 6 | 12223.58 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 4 | 12466.61 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.2 | 0.3 | 0.2 | True | 1.0 | 7 | 11041.64 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 0.9 | 1.0 | 1.0 | True | 1.0 | 4 | 14065.86 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 7 | 17376.33 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 0.5 | None | None | None | 1 | 2135.28 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.3 | 0.2 | True | 1.0 | 6 | 19393.62 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 9118.06 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 9765.42 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 15105.96 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.9 | 0.8 | True | 1.0 | 5 | 17561.42 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 16606.04 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 6 | 11500.2 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.2 | 0.4 | 0.2 | True | 1.0 | 4 | 21492.23 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 5 | 11060.41 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 5087.29 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 15505.24 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 12224.11 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 3 | 14329.09 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 4 | 14143.81 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 15717.72 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.9 | 0.9 | 0.8 | True | 1.0 | 5 | 16250.27 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 12901.15 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 12991.95 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 14156.16 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4204.08 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.2 | 0.0 | True | 1.0 | 6 | 19574.09 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 11913.73 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 5 | 14792.7 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 6 | 13258.0 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 4 | 8949.49 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 9862.85 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.9 | True | 1.0 | 6 | 9394.68 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 6 | 15545.38 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 3 | 17596.54 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 0.8 | 0.8 | False | 0.0 | 1 | 3854.08 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 3 | 11365.49 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 15971.83 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 10735.31 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 9245.73 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 3 | 9706.57 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 0.2 | 0.2 | 0.2 | True | 1.0 | 9 | 21402.54 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 30972.22 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 4 | 12948.35 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 3 | 10668.49 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 5965.78 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 5 | 18193.89 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 14530.71 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 1.0 | True | 1.0 | 2 | 30155.33 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 5 | 10510.62 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 6 | 14084.26 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 4 | 17411.66 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 6 | 12723.53 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 13522.28 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 5 | 14494.57 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 19474.35 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 6 | 10708.41 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 11222.13 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 10009.52 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 14512.39 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 5 | 11369.37 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 3 | 11278.42 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 7 | 9466.51 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 14518.13 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 7 | 9528.71 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.2 | None | None | None | 1 | 34144.49 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 3 | 10490.2 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 0.9 | 0.9 | 0.8 | True | 1.0 | 4 | 11799.49 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 3 | 11437.61 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 10185.25 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.5 | True | 1.0 | 4 | 20512.47 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 2 | 15070.51 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 3 | 9773.47 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 4 | 10996.86 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 13914.12 |  |
