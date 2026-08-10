# W6 Evaluation report: w8_abl_01_retrieval_fusion_reranker_v2_shard_a_controls

- Dataset: `D:\UNI_STUDY\Year3\Semester3\TextMining\tuvi-battu-graphrag\benchmark\tuvi_golden_dataset\release\tuviqa_v1_release.jsonl`
- Dataset items: 100
- Configs: 4
- Judge backend: `gemini`
- Started: 2026-08-06T09:13:49.830069Z
- Completed: 2026-08-06T09:13:51.159337Z
- Notes: Shard A of W8 retrieval/fusion/reranker matrix v2. Contains baseline, reranker, and fusion control variants. Merge into the canonical 10-config report after all shards complete.
- Run status: `completed`

## Run identity and provenance

- Identity SHA-256: `2e8630cae82be6df533d0a30ae6ba03555b7407e1e2fde2ff0ae2103a823b6a3`
- Dataset SHA-256: `90376a87cec29cc22e93dc71b41e054ed2f0183bc515a52aa461fecd43cc008c`
- Manifest SHA-256: `33db402bea5a948d359b4d2ffe8a0cb6ff28b8ca8095c7da8eafb332528394b5`
- Evaluator SHA-256: `47e83febfb2247a151d91605f72ead40dc0ec7f9044194eabd5038d75d74c435`
- Git SHA: `957d35f124e51916215c6b4a64fd5d35d7e66ec7`
- Git dirty: `False`
- Judge model: `gemini-3.1-flash-lite-preview`
- Checkpoint: `benchmark\tuvi_golden_dataset\reports_final\20_retrieval_fusion_reranker_matrix\shards\shard_a_controls\checkpoints\evaluation_checkpoint.json`

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
| baseline_graph_sparse_rrf | completed | 100 | 0.888 | 0.789 | 0.7044 | 0.967 | 0.9863 | 138041.28 | 133807.67 |
| baseline_no_reranker | completed | 100 | 0.915 | 0.828 | 0.744 | 0.967 | 0.989 | 12819.41 | 6374.74 |
| baseline_weighted_sum | completed | 100 | 0.881 | 0.794 | 0.6945 | 0.967 | 0.989 | 181602.9 | 176712.84 |
| baseline_graph_first | completed | 100 | 0.876 | 0.798 | 0.7253 | 0.967 | 0.9863 | 272370.05 | 256114.68 |

## Failure and fallback summary

| Config | Failed | Generation backend fallback | Judge failure | No context | Retrieval backend fallback | Citation fallback |
|---|---:|---:|---:|---:|---:|---:|
| baseline_graph_sparse_rrf | 0 | 0 | 0 | 0 | 0 | 0 |
| baseline_no_reranker | 0 | 0 | 0 | 0 | 0 | 0 |
| baseline_weighted_sum | 0 | 0 | 0 | 0 | 0 | 0 |
| baseline_graph_first | 0 | 0 | 0 | 0 | 0 | 1 |

## Ablation analysis

- Baseline config: `baseline_graph_sparse_rrf`
- Preliminary recommendation: `baseline_no_reranker`
  - Preliminary heuristic ranks configs by context recall, citation coverage, faithfulness, answer relevancy, graph hit rate, and a small p95 latency penalty.
  - Selected `baseline_no_reranker` with context_recall_avg=0.744, citation_coverage_rate=0.989, p95_latency_ms=12819.41.
  - Treat this as a smoke/first-pass recommendation until official Gemini judge and full dataset runs are complete.

### Context recall ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | baseline_no_reranker | 0.744 |
| 2 | baseline_graph_first | 0.7253 |
| 3 | baseline_graph_sparse_rrf | 0.7044 |
| 4 | baseline_weighted_sum | 0.6945 |

### Citation coverage ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | baseline_no_reranker | 0.989 |
| 2 | baseline_weighted_sum | 0.989 |
| 3 | baseline_graph_sparse_rrf | 0.9863 |
| 4 | baseline_graph_first | 0.9863 |

### Graph hit ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | baseline_graph_sparse_rrf | 0.967 |
| 2 | baseline_no_reranker | 0.967 |
| 3 | baseline_weighted_sum | 0.967 |
| 4 | baseline_graph_first | 0.967 |

### p95 latency ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | baseline_no_reranker | 12819.41 |
| 2 | baseline_graph_sparse_rrf | 138041.28 |
| 3 | baseline_weighted_sum | 181602.9 |
| 4 | baseline_graph_first | 272370.05 |

### Retrieval miss summary

| Config | Miss count | Example item IDs |
|---|---:|---|
| baseline_graph_sparse_rrf | 19 | TVQA-010, TVQA-028, TVQA-032, TVQA-038, TVQA-039 |
| baseline_no_reranker | 15 | TVQA-008, TVQA-010, TVQA-015, TVQA-017, TVQA-028 |
| baseline_weighted_sum | 18 | TVQA-008, TVQA-027, TVQA-028, TVQA-032, TVQA-038 |
| baseline_graph_first | 17 | TVQA-008, TVQA-010, TVQA-027, TVQA-028, TVQA-032 |

### Rerank miss summary

| Config | Miss count | Example item IDs |
|---|---:|---|
| baseline_graph_sparse_rrf | 2 | TVQA-068, TVQA-084 |
| baseline_no_reranker | 0 |  |
| baseline_weighted_sum | 1 | TVQA-068 |
| baseline_graph_first | 2 | TVQA-068, TVQA-097 |

## Metrics by question complexity

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| baseline_graph_sparse_rrf | Direct | 10 | 1.0 | 0.86 | 0.7 | 0.0 | 0.0 | 6939.14 |
| baseline_graph_sparse_rrf | One-hop | 46 | 0.8848 | 0.7826 | 0.7152 | 0.9783 | 0.9946 | 147025.88 |
| baseline_graph_sparse_rrf | Two-hop | 44 | 0.8659 | 0.7795 | 0.6932 | 0.9773 | 1.0 | 133255.05 |
| baseline_no_reranker | Direct | 10 | 1.0 | 0.77 | 0.7 | 0.0 | 0.0 | 4189.75 |
| baseline_no_reranker | One-hop | 46 | 0.9239 | 0.8478 | 0.7565 | 0.9783 | 1.0 | 13026.38 |
| baseline_no_reranker | Two-hop | 44 | 0.8864 | 0.8205 | 0.7318 | 0.9773 | 1.0 | 11892.69 |
| baseline_weighted_sum | Direct | 10 | 1.0 | 0.84 | 0.7 | 0.0 | 0.0 | 7929.15 |
| baseline_weighted_sum | One-hop | 46 | 0.8652 | 0.7696 | 0.687 | 0.9783 | 1.0 | 179826.07 |
| baseline_weighted_sum | Two-hop | 44 | 0.8705 | 0.8091 | 0.7023 | 0.9773 | 1.0 | 196405.2 |
| baseline_graph_first | Direct | 10 | 1.0 | 0.84 | 0.7 | 0.0 | 0.0 | 7567.06 |
| baseline_graph_first | One-hop | 46 | 0.8674 | 0.8065 | 0.763 | 0.9783 | 1.0 | 298655.86 |
| baseline_graph_first | Two-hop | 44 | 0.8568 | 0.7795 | 0.6864 | 0.9773 | 0.9943 | 264742.89 |

## Metrics by question family

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| baseline_graph_sparse_rrf | core_identity | 10 | 1.0 | 0.86 | 0.7 | 0.0 | 0.0 | 6939.14 |
| baseline_graph_sparse_rrf | dai_van_interpretation | 10 | 0.86 | 0.5 | 0.39 | 1.0 | 1.0 | 113888.76 |
| baseline_graph_sparse_rrf | menh_cuc_relation | 10 | 0.94 | 0.96 | 0.89 | 1.0 | 0.975 | 84728.04 |
| baseline_graph_sparse_rrf | menh_house_interpretation | 10 | 0.89 | 0.71 | 0.65 | 0.9 | 1.0 | 160225.52 |
| baseline_graph_sparse_rrf | menh_tam_hop | 10 | 0.88 | 0.78 | 0.69 | 1.0 | 1.0 | 148841.25 |
| baseline_graph_sparse_rrf | menh_xung_chieu | 10 | 0.85 | 0.82 | 0.71 | 1.0 | 1.0 | 120080.1 |
| baseline_graph_sparse_rrf | special_state_interpretation | 10 | 0.74 | 0.68 | 0.6 | 1.0 | 1.0 | 109746.98 |
| baseline_graph_sparse_rrf | synthesis_judgement | 10 | 0.8 | 0.75 | 0.65 | 0.9 | 1.0 | 144369.32 |
| baseline_graph_sparse_rrf | than_cu_interpretation | 10 | 0.98 | 0.94 | 0.9 | 1.0 | 1.0 | 158349.66 |
| baseline_graph_sparse_rrf | topic_house_plus_relations | 10 | 0.94 | 0.89 | 0.86 | 1.0 | 1.0 | 123311.39 |
| baseline_no_reranker | core_identity | 10 | 1.0 | 0.77 | 0.7 | 0.0 | 0.0 | 4189.75 |
| baseline_no_reranker | dai_van_interpretation | 10 | 0.82 | 0.68 | 0.58 | 1.0 | 1.0 | 10652.57 |
| baseline_no_reranker | menh_cuc_relation | 10 | 1.0 | 0.94 | 0.92 | 1.0 | 1.0 | 14863.71 |
| baseline_no_reranker | menh_house_interpretation | 10 | 0.84 | 0.73 | 0.63 | 0.9 | 1.0 | 13670.47 |
| baseline_no_reranker | menh_tam_hop | 10 | 0.89 | 0.79 | 0.67 | 1.0 | 1.0 | 10889.18 |
| baseline_no_reranker | menh_xung_chieu | 10 | 0.87 | 0.81 | 0.72 | 1.0 | 1.0 | 10565.21 |
| baseline_no_reranker | special_state_interpretation | 10 | 0.94 | 0.83 | 0.7 | 1.0 | 1.0 | 11861.08 |
| baseline_no_reranker | synthesis_judgement | 10 | 0.92 | 0.88 | 0.8 | 0.9 | 1.0 | 13621.12 |
| baseline_no_reranker | than_cu_interpretation | 10 | 0.93 | 0.97 | 0.87 | 1.0 | 1.0 | 11940.49 |
| baseline_no_reranker | topic_house_plus_relations | 10 | 0.94 | 0.88 | 0.81 | 1.0 | 1.0 | 11053.96 |
| baseline_weighted_sum | core_identity | 10 | 1.0 | 0.84 | 0.7 | 0.0 | 0.0 | 7929.15 |
| baseline_weighted_sum | dai_van_interpretation | 10 | 0.79 | 0.55 | 0.41 | 1.0 | 1.0 | 135952.63 |
| baseline_weighted_sum | menh_cuc_relation | 10 | 0.98 | 0.89 | 0.87 | 1.0 | 1.0 | 115661.71 |
| baseline_weighted_sum | menh_house_interpretation | 10 | 0.86 | 0.71 | 0.63 | 0.9 | 1.0 | 186369.8 |
| baseline_weighted_sum | menh_tam_hop | 10 | 0.88 | 0.82 | 0.7 | 1.0 | 1.0 | 189319.47 |
| baseline_weighted_sum | menh_xung_chieu | 10 | 0.86 | 0.79 | 0.69 | 1.0 | 1.0 | 153840.77 |
| baseline_weighted_sum | special_state_interpretation | 10 | 0.7 | 0.69 | 0.61 | 1.0 | 1.0 | 161273.81 |
| baseline_weighted_sum | synthesis_judgement | 10 | 0.9 | 0.85 | 0.7 | 0.9 | 1.0 | 229528.16 |
| baseline_weighted_sum | than_cu_interpretation | 10 | 0.92 | 0.93 | 0.82 | 1.0 | 1.0 | 179452.3 |
| baseline_weighted_sum | topic_house_plus_relations | 10 | 0.92 | 0.87 | 0.82 | 1.0 | 1.0 | 179481.35 |
| baseline_graph_first | core_identity | 10 | 1.0 | 0.84 | 0.7 | 0.0 | 0.0 | 7567.06 |
| baseline_graph_first | dai_van_interpretation | 10 | 0.76 | 0.6 | 0.49 | 1.0 | 1.0 | 350322.69 |
| baseline_graph_first | menh_cuc_relation | 10 | 0.98 | 0.95 | 0.91 | 1.0 | 1.0 | 144737.42 |
| baseline_graph_first | menh_house_interpretation | 10 | 0.84 | 0.73 | 0.71 | 0.9 | 1.0 | 280513.36 |
| baseline_graph_first | menh_tam_hop | 10 | 0.88 | 0.79 | 0.69 | 1.0 | 1.0 | 249989.17 |
| baseline_graph_first | menh_xung_chieu | 10 | 0.86 | 0.75 | 0.65 | 1.0 | 0.975 | 232925.12 |
| baseline_graph_first | special_state_interpretation | 10 | 0.74 | 0.69 | 0.63 | 1.0 | 1.0 | 298280.38 |
| baseline_graph_first | synthesis_judgement | 10 | 0.77 | 0.76 | 0.63 | 0.9 | 1.0 | 276988.36 |
| baseline_graph_first | than_cu_interpretation | 10 | 0.95 | 0.95 | 0.95 | 1.0 | 1.0 | 254716.91 |
| baseline_graph_first | topic_house_plus_relations | 10 | 0.98 | 0.92 | 0.87 | 1.0 | 1.0 | 210001.37 |

## Per-question results

### baseline_graph_sparse_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 5991.8 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 150234.67 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 137399.52 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 89846.57 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 105015.33 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 2 | 123806.77 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 97023.73 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 7 | 100814.38 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 98596.18 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 6 | 129399.52 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4007.28 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 7 | 168399.85 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 4 | 175490.69 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 72882.47 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 5 | 113618.33 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 5 | 169324.0 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 131256.45 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 6 | 124585.98 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 127015.62 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 7 | 130832.4 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4013.64 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 0.9 | 0.8 | 0.8 | True | 1.0 | 3 | 128914.87 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 3 | 103762.45 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 78472.06 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 5 | 91106.99 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 5 | 114281.68 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.6 | True | 1.0 | 7 | 84892.78 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.2 | 0.2 | True | 1.0 | 7 | 77166.76 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 118784.0 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 0.9 | 1.0 | 0.8 | True | 1.0 | 5 | 153174.24 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 1854.01 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.6 | 0.4 | 0.2 | True | 1.0 | 4 | 122410.01 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 82348.85 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 69837.03 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 8 | 99286.78 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 5 | 111902.08 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 106420.12 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.5 | 0.2 | True | 1.0 | 4 | 81367.8 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.6 | 0.5 | 0.4 | True | 1.0 | 4 | 95983.04 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 4 | 91271.97 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 7714.24 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 78765.46 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 6 | 86053.51 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.8 | 0.6 | True | 1.0 | 4 | 63757.23 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 4 | 101028.53 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 101601.89 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 5 | 100205.97 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 3 | 85160.88 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 81028.74 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 133607.75 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 2793.83 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.2 | 0.2 | True | 1.0 | 5 | 110073.99 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 0.8 | 1.0 | 0.6 | True | 1.0 | 3 | 94511.26 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.9 | 0.6 | True | 1.0 | 5 | 67182.78 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 4 | 96666.86 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 4 | 81174.6 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 81379.33 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.4 | 0.3 | True | 1.0 | 4 | 78288.91 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 7 | 81979.09 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 0.2 | 0.0 | 0.2 | True | 1.0 | 3 | 113364.88 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 0.8 | 0.7 | False | 0.0 | 1 | 3627.41 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 3 | 71409.25 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 117553.98 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 74571.91 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 6 | 60408.91 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 5 | 80784.29 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 7 | 76692.26 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 66868.39 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 4 | 86732.61 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 6 | 83719.31 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3837.14 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 100750.89 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 7 | 119190.06 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 57578.84 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 6 | 76195.78 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 4 | 110869.48 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 79574.95 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.0 | 0.0 | True | 1.0 | 6 | 84441.36 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 101333.39 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 0.6 | 0.4 | 0.2 | True | 1.0 | 5 | 86778.02 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4360.33 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.7 | 0.5 | False | 1.0 | 5 | 104435.23 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 6 | 107385.46 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.9 | 0.7 | True | 0.75 | 1 | 61253.95 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 93843.84 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 99845.56 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 79645.39 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.6 | 0.5 | True | 1.0 | 5 | 74171.27 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 110584.88 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 0.8 | 1.0 | 0.7 | False | 1.0 | 5 | 114131.56 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.2 | None | None | None | 1 | 4016.62 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 5 | 77361.22 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 114135.17 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 73200.14 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 6 | 85793.55 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 0.6 | 0.5 | 0.2 | True | 1.0 | 2 | 79162.54 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 5 | 77342.57 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 0.6 | 0.4 | 0.2 | True | 1.0 | 4 | 67373.47 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 6 | 85513.55 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 93229.04 |  |

### baseline_no_reranker

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3437.66 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 3 | 9086.19 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 9 | 8670.86 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 7583.15 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 5 | 10194.33 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 6 | 9301.34 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 0.9 | 0.9 | 1.0 | True | 1.0 | 6 | 8590.01 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.4 | 0.2 | True | 1.0 | 7 | 11204.65 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 9341.22 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.7 | 0.4 | True | 1.0 | 5 | 10009.41 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 3979.01 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 4 | 10765.88 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 0.9 | 0.9 | 0.8 | True | 1.0 | 6 | 9467.26 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 7990.86 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.4 | True | 1.0 | 4 | 8280.73 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 5 | 10616.99 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.6 | 0.5 | 0.4 | True | 1.0 | 4 | 8860.31 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 6 | 8680.64 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 10038.79 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 10288.6 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3938.58 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 7 | 11296.32 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 9051.42 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 8674.25 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 5 | 10348.22 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 6 | 10873.16 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 3 | 9384.06 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.2 | 0.3 | 0.2 | True | 1.0 | 7 | 9109.87 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 0.9 | 1.0 | 0.8 | True | 1.0 | 4 | 11522.05 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 13019.69 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 0.5 | None | None | None | 1 | 2227.68 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.6 | 0.4 | 0.2 | True | 1.0 | 6 | 10518.84 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 8399.85 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 8199.95 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 6 | 9706.74 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 6 | 10902.28 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 10709.34 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 0.6 | 0.5 | 0.2 | True | 1.0 | 8 | 9977.8 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 4 | 9164.49 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 5 | 8855.3 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 3342.82 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 8943.96 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 9352.3 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 4 | 7995.86 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.5 | 0.0 | True | 1.0 | 4 | 9442.68 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.9 | 0.8 | True | 1.0 | 5 | 9585.1 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 8 | 10389.05 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 8812.17 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 7 | 10481.84 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 14113.2 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3977.32 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.2 | 0.0 | True | 1.0 | 4 | 15612.96 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 0.8 | 1.0 | 0.5 | True | 1.0 | 4 | 12808.87 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 5 | 19927.82 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 9 | 13098.88 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.4 | True | 1.0 | 4 | 8914.19 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 9626.23 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 6 | 9554.79 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 4 | 8629.84 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 0.9 | 1.0 | 1.0 | True | 1.0 | 6 | 11958.1 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 0.6 | 0.7 | False | 0.0 | 1 | 3967.93 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.6 | 0.5 | True | 1.0 | 3 | 10301.89 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 10879.14 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 7163.11 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 9256.37 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 9011.09 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 4 | 8572.62 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 8141.11 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 4 | 9477.77 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 3 | 9239.45 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3791.03 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 9384.84 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 10462.98 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 7061.66 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 3 | 8173.48 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 4 | 10308.64 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 4 | 8927.74 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 5 | 9235.01 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 8542.37 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 6 | 9106.0 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4283.97 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.6 | False | 1.0 | 7 | 8122.54 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 9751.04 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 7882.2 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 9168.65 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 5 | 8952.89 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 4 | 8908.24 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 7 | 8945.24 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 10251.12 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 6 | 8269.6 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.0 | None | None | None | 1 | 4074.59 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 8610.28 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 9007.71 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 5 | 7955.94 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 4 | 10056.07 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 3 | 8634.62 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 2 | 9781.76 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 4 | 8596.75 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 4 | 9291.12 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 10915.34 |  |

### baseline_weighted_sum

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3465.35 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 0.9 | 0.8 | 0.8 | True | 1.0 | 4 | 118319.32 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 138442.76 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 90847.62 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 6 | 139964.71 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 177778.24 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 144440.37 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.4 | 0.2 | True | 1.0 | 6 | 140126.88 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 147271.05 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.8 | 1.0 | 0.5 | True | 1.0 | 6 | 138899.54 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3982.95 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 7 | 121897.45 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 129349.99 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 60124.07 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.8 | 1.0 | 0.7 | True | 1.0 | 6 | 115827.38 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 7 | 176217.87 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 132244.55 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 5 | 126914.05 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 124711.88 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 154743.22 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3824.09 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 7 | 154530.36 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 105921.39 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 1.0 | True | 1.0 | 3 | 111568.04 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 0.6 | 0.5 | 0.5 | True | 1.0 | 5 | 142179.78 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 5 | 173535.72 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.5 | 0.2 | True | 1.0 | 7 | 124321.52 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.4 | 0.2 | True | 1.0 | 7 | 115383.09 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 6 | 181526.82 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 0.9 | 0.9 | 0.8 | True | 1.0 | 6 | 253225.13 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 2558.22 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.6 | 0.5 | 0.4 | True | 1.0 | 6 | 191246.54 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 135642.51 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 119011.07 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 8 | 160229.89 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 4 | 174236.5 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 0.9 | 1.0 | 1.0 | True | 1.0 | 7 | 136703.03 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 4 | 120094.49 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.4 | 0.5 | 0.2 | True | 1.0 | 2 | 132983.18 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 3 | 143658.89 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 2615.68 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 123019.28 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 136435.37 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 4 | 104027.84 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 4 | 162127.93 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 6 | 198762.29 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 7 | 161532.01 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 0.9 | 1.0 | 1.0 | True | 1.0 | 3 | 130850.76 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 7 | 124134.72 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 200565.2 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3108.99 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.2 | 0.0 | True | 1.0 | 6 | 180409.35 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 0.5 | 0.8 | 0.0 | True | 1.0 | 4 | 143539.78 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 5 | 104401.17 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 156635.22 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.8 | True | 1.0 | 3 | 117836.21 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 8 | 128512.42 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 0.2 | 0.3 | 0.2 | True | 1.0 | 5 | 117986.85 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.9 | 0.8 | True | 1.0 | 4 | 127426.3 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 4 | 174857.53 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 0.8 | 0.7 | False | 0.0 | 1 | 3993.4 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 94921.8 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 116181.62 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 90388.87 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 6 | 90873.1 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 5 | 122981.78 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 7 | 115650.73 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 105269.64 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 3 | 134042.92 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 6 | 103565.44 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3638.6 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 4 | 135040.56 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 3 | 180578.2 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 1.0 | True | 1.0 | 3 | 89315.28 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 6 | 119860.31 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 5 | 175151.39 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 4 | 126359.02 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.2 | 0.0 | True | 1.0 | 4 | 130053.39 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 139750.42 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 7 | 133692.77 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4373.15 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.6 | 0.5 | False | 1.0 | 3 | 166540.67 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 6 | 178076.21 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 4 | 86239.24 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 149929.39 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 159822.16 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 122515.3 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.4 | 0.3 | True | 1.0 | 4 | 116150.07 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 176981.34 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 0.8 | 1.0 | 0.8 | False | 1.0 | 6 | 183048.35 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.0 | None | None | None | 1 | 10838.6 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 6 | 107061.57 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 3 | 134114.41 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 91879.7 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 5 | 131425.99 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.4 | 0.2 | True | 1.0 | 4 | 119170.51 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 5 | 115279.61 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.5 | 0.2 | True | 1.0 | 7 | 109822.01 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 8 | 115745.04 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 5 | 147522.07 |  |

### baseline_graph_first

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3942.98 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 118893.2 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 140119.74 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 95582.44 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 6 | 247719.04 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 2 | 189695.21 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 176648.78 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.4 | 0.3 | True | 1.0 | 7 | 472940.69 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 214022.01 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.5 | 0.2 | True | 1.0 | 6 | 203917.11 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 5994.55 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.6 | 0.5 | True | 1.0 | 8 | 259752.15 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 299041.22 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 93205.49 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 114877.68 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 7 | 154172.09 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 138400.14 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 133313.48 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 154985.65 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 252557.15 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3819.21 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 3 | 203664.56 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 1.0 | True | 1.0 | 3 | 165097.26 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 113159.75 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 164244.0 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 4 | 224261.84 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.4 | 0.2 | True | 1.0 | 6 | 127964.6 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.2 | 0.1 | 0.2 | True | 1.0 | 7 | 127832.93 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 205087.25 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 0.9 | 0.9 | 0.8 | True | 1.0 | 7 | 271908.22 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 7398.35 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.4 | 0.3 | 0.2 | True | 1.0 | 5 | 183359.84 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 146283.12 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 121650.11 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 8 | 191919.97 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 5 | 200293.28 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 234888.98 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 4 | 200456.24 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 5 | 203205.87 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 4 | 215493.9 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 7705.09 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 0.8 | True | 1.0 | 2 | 178145.06 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 193741.63 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 4 | 148593.04 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 5 | 238854.13 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.9 | 1.0 | True | 1.0 | 6 | 229328.54 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 5 | 230524.84 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 3 | 176465.55 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 164559.07 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 205044.07 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4996.47 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.2 | 0.2 | True | 1.0 | 6 | 174708.77 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 0.8 | 1.0 | 1.0 | True | 1.0 | 5 | 147941.46 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 5 | 105368.83 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 4 | 152043.05 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.8 | 0.7 | True | 1.0 | 4 | 122854.06 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 8 | 122621.13 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 4 | 117051.9 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 7 | 124612.12 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 175903.32 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 0.8 | 0.7 | False | 0.0 | 1 | 3844.31 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 3 | 113143.21 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 186262.63 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 116077.95 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 6 | 94942.14 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 5 | 123580.79 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 7 | 114764.63 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 102360.51 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 3 | 136355.09 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 3 | 153648.25 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3422.78 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 148693.88 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 180867.28 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 91547.95 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 6 | 118044.16 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 177719.02 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 121870.01 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 4 | 127921.62 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 137966.79 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 6 | 281144.84 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4211.54 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.6 | 0.4 | False | 1.0 | 5 | 297499.8 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 200542.76 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 140024.99 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 339648.75 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 6 | 266893.32 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 5 | 179974.74 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 5 | 118179.23 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 179016.28 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 6 | 183153.67 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.0 | None | None | None | 1 | 4835.64 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 6 | 118902.22 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 0.9 | 0.9 | 0.8 | True | 1.0 | 3 | 190470.18 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 114179.97 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 6 | 136577.0 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 5 | 124147.38 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.6 | 0.4 | True | 0.75 | 1 | 120810.89 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 0.6 | 0.4 | 0.2 | True | 1.0 | 7 | 114558.29 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 3 | 133435.98 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 150212.31 |  |
