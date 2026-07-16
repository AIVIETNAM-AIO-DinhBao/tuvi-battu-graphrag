# W6 Evaluation report: w6_eval_02_single_config

- Dataset: `D:\University\Năm 3 ĐH\Kì 3 (18th6)\Text Mining\tuvi-battu-graphrag\benchmark\tuvi_golden_dataset\release\tuviqa_v1_release.jsonl`
- Dataset items: 3
- Configs: 1
- Judge backend: `static-smoke`
- Started: 2026-07-16T15:21:18.275974Z
- Completed: 2026-07-16T15:21:18.381403Z
- Notes: W6-EVAL-02 single-config evaluation run.
- Run status: `completed`

## Run identity and provenance

- Identity SHA-256: `e3c5a5a7e4d2efdf8112ddb9c69f15c9998bae04b17502c9ce457885474027fb`
- Dataset SHA-256: `90376a87cec29cc22e93dc71b41e054ed2f0183bc515a52aa461fecd43cc008c`
- Manifest SHA-256: `b9cccbfb5cfe3a6cbc820bc80ce3befd2970a9fec0c33f073a0d9b7de2ee3b5a`
- Evaluator SHA-256: `9ae528d893159c4092c3129523da8d69a7a79a6ab5c32a132791158287eda314`
- Git SHA: `d5c4f734e5acb42679cb9e0755bbd935a4e9fa7f`
- Git dirty: `True`
- Judge model: `static-smoke`
- Checkpoint: `benchmark\tuvi_golden_dataset\reports\w8_eval_prep_01_smoke\checkpoint\evaluation_checkpoint.json`

## Execution completeness

- Expected pairs: 3
- Completed pairs: 3
- Failed pairs: 0
- Executed pairs: 3
- Resumed pairs: 0

> **Caveat:** This is not an official W6 metric run because RAGAS-like metrics were not judged by Gemini.

> **Metric policy:** W6-EVAL-02 runs the RAG pipeline directly with the selected `ExperimentConfig`. `Context recall` is the Gemini-judged corpus-grounding score for non-Direct items; Direct/chart-only items are excluded from corpus retrieval/citation metrics and reported through `chart_context_grounding`.

## Overall metrics

| Config | Status | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms | Retrieval p95 ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| default_production | completed | 3 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 36.7 | 0.54 |

## Failure and fallback summary

| Config | Failed | Generation backend fallback | Judge failure | No context | Retrieval backend fallback | Citation fallback |
|---|---:|---:|---:|---:|---:|---:|
| default_production | 0 | 0 | 0 | 0 | 0 | 0 |

## Ablation analysis

- Baseline config: `baseline_graph_sparse_rrf`
- Preliminary recommendation: `default_production`
  - Preliminary heuristic ranks configs by context recall, citation coverage, faithfulness, answer relevancy, graph hit rate, and a small p95 latency penalty.
  - Selected `default_production` with context_recall_avg=1.0, citation_coverage_rate=0.75, p95_latency_ms=36.7.
  - Treat this as a smoke/first-pass recommendation until official Gemini judge and full dataset runs are complete.

### Context recall ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | default_production | 1.0 |

### Citation coverage ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | default_production | 0.75 |

### Graph hit ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | default_production | 0.0 |

### p95 latency ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | default_production | 36.7 |

### Retrieval miss summary

| Config | Miss count | Example item IDs |
|---|---:|---|
| default_production | 2 | TVQA-002, TVQA-003 |

### Rerank miss summary

| Config | Miss count | Example item IDs |
|---|---:|---|
| default_production | 0 |  |

## Metrics by question complexity

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| default_production | Direct | 1 | 1.0 | 1.0 | None | None | None | 38.19 |
| default_production | One-hop | 2 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 23.23 |

## Metrics by question family

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| default_production | core_identity | 1 | 1.0 | 1.0 | None | None | None | 38.19 |
| default_production | menh_house_interpretation | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 22.27 |
| default_production | than_cu_interpretation | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.75 | 23.28 |

## Per-question results

### default_production

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 38.19 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 22.27 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.75 | 1 | 23.28 |  |
