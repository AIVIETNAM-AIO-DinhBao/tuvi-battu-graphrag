# Ablation report: w4_abl_01_smoke

- Dataset: `D:\University\Năm 3 ĐH\Kì 3 (18th6)\Text Mining\tuvi-battu-graphrag\benchmark\tuvi_golden_dataset\release\tuviqa_v1_release.jsonl`
- Dataset items: 2
- Configs: 2
- Started: 2026-07-11T01:13:14.633867Z
- Completed: 2026-07-11T01:13:14.991429Z
- Notes: W4-ABL-01 golden smoke run: release TuViQA dataset, use --limit 2 for local smoke checks

## Config summary

| Config | Status | Items | Answer rate | Source coverage | Avg sources | Avg latency ms |
|---|---:|---:|---:|---:|---:|---:|
| golden_smoke_rrf_balanced | completed | 2 | 1.0 | 0.0 | 0.0 | 101.37 |
| golden_smoke_graph_first | completed | 2 | 1.0 | 0.0 | 0.0 | 68.82 |

## Golden answer metrics

| Config | Avg recall vs gold | Avg recall vs summary | Summary coverage | Avg char ngram sim | Avg ROUGE-L-like |
|---|---:|---:|---:|---:|---:|
| golden_smoke_rrf_balanced | 0.075 | 0.1389 | 0.0 | 0.0766 | 0.1658 |
| golden_smoke_graph_first | 0.075 | 0.1389 | 0.0 | 0.0766 | 0.1658 |

## Gold context and citation metrics

| Config | Gold doc coverage | Gold page hit | Gold quote overlap | Citation marker presence | Citation source alignment |
|---|---:|---:|---:|---:|---:|
| golden_smoke_rrf_balanced | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| golden_smoke_graph_first | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |

## Per-question results

### golden_smoke_rrf_balanced

| Item | Status | Complexity | Gold spans | Sources | Summary recall | Doc coverage | Page hit | Citation markers | Context chunks | Latency ms | Error |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | 0 | 0 | 0.1667 | None | None | 0 | 0 | 98.95 |  |
| TVQA-002 | completed | One-hop | 6 | 0 | 0.1111 | 0.0 | 0.0 | 0 | 0 | 103.78 |  |

### golden_smoke_graph_first

| Item | Status | Complexity | Gold spans | Sources | Summary recall | Doc coverage | Page hit | Citation markers | Context chunks | Latency ms | Error |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | 0 | 0 | 0.1667 | None | None | 0 | 0 | 67.8 |  |
| TVQA-002 | completed | One-hop | 6 | 0 | 0.1111 | 0.0 | 0.0 | 0 | 0 | 69.85 |  |
