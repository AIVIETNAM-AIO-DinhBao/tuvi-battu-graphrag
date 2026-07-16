# W6 Evaluation report: w6_eval_02_single_config

- Dataset: `D:\University\Năm 3 ĐH\Kì 3 (18th6)\Text Mining\tuvi-battu-graphrag\benchmark\tuvi_golden_dataset\release\tuviqa_v1_release.jsonl`
- Dataset items: 6
- Configs: 1
- Judge backend: `gemini`
- Started: 2026-07-16T17:31:49.284227Z
- Completed: 2026-07-16T17:33:13.899282Z
- Notes: W6-EVAL-02 single-config evaluation run.
- Run status: `completed`

## Run identity and provenance

- Identity SHA-256: `18a11a7a93ce2a6a82a70f4f8637d5643ca290adc3cdd09e42424fbeb299e577`
- Dataset SHA-256: `90376a87cec29cc22e93dc71b41e054ed2f0183bc515a52aa461fecd43cc008c`
- Manifest SHA-256: `b9cccbfb5cfe3a6cbc820bc80ce3befd2970a9fec0c33f073a0d9b7de2ee3b5a`
- Evaluator SHA-256: `9ae528d893159c4092c3129523da8d69a7a79a6ab5c32a132791158287eda314`
- Git SHA: `bd1305c1a97907cd1ee397790eb5bafa4f3a666f`
- Git dirty: `False`
- Judge model: `gemini-3.1-flash-lite-preview`
- Checkpoint: `benchmark\tuvi_golden_dataset\reports\w8_eval_preflight_01\production_limit6\checkpoint\evaluation_checkpoint.json`

## Execution completeness

- Expected pairs: 6
- Completed pairs: 6
- Failed pairs: 0
- Executed pairs: 6
- Resumed pairs: 0

> **Metric policy:** W6-EVAL-02 runs the RAG pipeline directly with the selected `ExperimentConfig`. `Context recall` is the Gemini-judged corpus-grounding score for non-Direct items; Direct/chart-only items are excluded from corpus retrieval/citation metrics and reported through `chart_context_grounding`.

## Overall metrics

| Config | Status | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms | Retrieval p95 ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| default_production | completed | 6 | 1.0 | 0.8833 | 0.8 | 1.0 | 1.0 | 18395.29 | 15946.62 |

## Failure and fallback summary

| Config | Failed | Generation backend fallback | Judge failure | No context | Retrieval backend fallback | Citation fallback |
|---|---:|---:|---:|---:|---:|---:|
| default_production | 0 | 0 | 0 | 0 | 0 | 0 |

## Ablation analysis

- Baseline config: `baseline_graph_sparse_rrf`
- Preliminary recommendation: `default_production`
  - Preliminary heuristic ranks configs by context recall, citation coverage, faithfulness, answer relevancy, graph hit rate, and a small p95 latency penalty.
  - Selected `default_production` with context_recall_avg=0.8, citation_coverage_rate=1.0, p95_latency_ms=18395.29.
  - Treat this as a smoke/first-pass recommendation until official Gemini judge and full dataset runs are complete.

### Context recall ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | default_production | 0.8 |

### Citation coverage ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | default_production | 1.0 |

### Graph hit ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | default_production | 1.0 |

### p95 latency ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | default_production | 18395.29 |

### Retrieval miss summary

| Config | Miss count | Example item IDs |
|---|---:|---|
| default_production | 0 |  |

### Rerank miss summary

| Config | Miss count | Example item IDs |
|---|---:|---|
| default_production | 0 |  |

## Metrics by question complexity

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| default_production | Direct | 1 | 1.0 | 1.0 | None | None | None | 1715.9 |
| default_production | One-hop | 4 | 1.0 | 0.85 | 0.75 | 1.0 | 1.0 | 15604.39 |
| default_production | Two-hop | 1 | 1.0 | 0.9 | 1.0 | 1.0 | 1.0 | 19291.13 |

## Metrics by question family

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| default_production | core_identity | 1 | 1.0 | 1.0 | None | None | None | 1715.9 |
| default_production | menh_cuc_relation | 1 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 15018.57 |
| default_production | menh_house_interpretation | 1 | 1.0 | 0.8 | 0.7 | 1.0 | 1.0 | 15707.77 |
| default_production | menh_tam_hop | 1 | 1.0 | 0.9 | 1.0 | 1.0 | 1.0 | 19291.13 |
| default_production | special_state_interpretation | 1 | 1.0 | 0.8 | 0.7 | 1.0 | 1.0 | 11481.46 |
| default_production | than_cu_interpretation | 1 | 1.0 | 0.8 | 0.6 | 1.0 | 1.0 | 12047.05 |

## Per-question results

### default_production

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1715.9 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 2 | 15707.77 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 2 | 12047.05 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 15018.57 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 3 | 11481.46 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 6 | 19291.13 |  |
