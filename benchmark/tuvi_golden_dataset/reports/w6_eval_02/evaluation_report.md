# W6 Evaluation report: w6_eval_02_baseline

- Dataset: `D:\University\Năm 3 ĐH\Kì 3 (18th6)\Text Mining\tuvi-battu-graphrag\benchmark\tuvi_golden_dataset\release\tuviqa_v1_release.jsonl`
- Dataset items: 2
- Configs: 1
- Judge backend: `static-smoke`
- Started: 2026-07-13T13:48:30.258558Z
- Completed: 2026-07-13T13:48:30.337250Z
- Notes: W6-EVAL-02 baseline: pipeline-direct evaluation on TuViQA v1 release with default production config. Official metrics require --judge-backend gemini; use --offline-smoke only for plumbing checks.

> **Caveat:** This is not an official W6 metric run because RAGAS-like metrics were not judged by Gemini.

> **Metric policy:** W6-EVAL-02 runs the RAG pipeline directly with the selected `ExperimentConfig`. `Context recall` is the Gemini-judged corpus-grounding score for non-Direct items; Direct/chart-only items are excluded from corpus retrieval/citation metrics and reported through `chart_context_grounding`.

## Overall metrics

| Config | Status | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms | Retrieval p95 ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| default_production_baseline | completed | 2 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 | 43.34 | None |

## Metrics by question complexity

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| default_production_baseline | Direct | 1 | 1.0 | 1.0 | None | None | None | 44.22 |
| default_production_baseline | One-hop | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 | 26.65 |

## Metrics by question family

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| default_production_baseline | core_identity | 1 | 1.0 | 1.0 | None | None | None | 44.22 |
| default_production_baseline | menh_house_interpretation | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 | 26.65 |

## Per-question results

### default_production_baseline

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 0 | 44.22 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.0 | 0 | 26.65 |  |
