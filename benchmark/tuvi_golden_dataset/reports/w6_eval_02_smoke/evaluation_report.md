# W6 Evaluation report: w6_eval_02_single_config

- Dataset: `D:\University\Năm 3 ĐH\Kì 3 (18th6)\Text Mining\tuvi-battu-graphrag\benchmark\tuvi_golden_dataset\release\tuviqa_v1_release.jsonl`
- Dataset items: 2
- Configs: 1
- Judge backend: `static-smoke`
- Started: 2026-07-13T12:08:39.562121Z
- Completed: 2026-07-13T12:08:39.623403Z
- Notes: W6-EVAL-02 single-config evaluation run.

> **Caveat:** This is not an official W6 metric run because RAGAS-like metrics were not judged by Gemini.

## Overall metrics

| Config | Status | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms | Retrieval p95 ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| default_production | completed | 2 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 | 35.6 | None |

## Metrics by question complexity

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| default_production | Direct | 1 | 1.0 | 1.0 | None | None | None | 36.41 |
| default_production | One-hop | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 | 20.25 |

## Metrics by question family

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| default_production | core_identity | 1 | 1.0 | 1.0 | None | None | None | 36.41 |
| default_production | menh_house_interpretation | 1 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 | 20.25 |

## Per-question results

### default_production

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 0 | 36.41 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 0.0 | 0 | 20.25 |  |
