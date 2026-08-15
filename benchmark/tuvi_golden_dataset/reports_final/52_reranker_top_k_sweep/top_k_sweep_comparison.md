# Phase 52 — Reranker Top-k Sweep

This analysis is separate from the canonical W8 matrix and Phase 50 shortlist confirmation.

- Generated UTC: `2026-08-15T01:35:28.786497Z`
- Pairwise deltas are `right - left`; positive values favor the right-hand configuration.
- Bootstrap CIs use 5,000 seeded resamples and are descriptive.

## Aggregate quality, latency, and candidate flow

| Role | Config | Faith | Relevancy | Context recall | Citation | Retr p95 ms | Fused | Reranked | Graded | Context selected |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| k10 | semantic_gs_rrf_rerank_k10_control | 0.888 | 0.795 | 0.709 | 0.986 | 163993.710 | 72.615 | 9.890 | 8.901 | 7.440 |
| k20 | semantic_gs_rrf_rerank_k20 | 0.914 | 0.808 | 0.748 | 0.989 | 143343.650 | 72.615 | 19.780 | 16.978 | 8.604 |
| k40 | semantic_gs_rrf_rerank_k40 | 0.906 | 0.830 | 0.757 | 0.989 | 162516.160 | 72.615 | 39.560 | 29.637 | 8.857 |
| no_rerank | semantic_gs_rrf_no_rerank_reference | 0.888 | 0.815 | 0.741 | 0.989 | 8321.100 | 72.615 | 72.615 | 40.681 | 8.868 |

## Top-k 20 vs top-k 10

`semantic_gs_rrf_rerank_k20` minus `semantic_gs_rrf_rerank_k10_control`; shared items: `100`.

| Metric | N | Mean delta | Bootstrap 95% CI | Right better / same / worse |
|---|---:|---:|---|---:|
| faithfulness | 100 | 0.026 | [-0.010, 0.062] | 22 / 67 / 11 |
| answer_relevancy | 100 | 0.013 | [-0.028, 0.052] | 34 / 44 / 22 |
| context_recall | 91 | 0.040 | [-0.007, 0.086] | 32 / 44 / 15 |
| citation_coverage | 91 | 0.003 | [0.000, 0.008] | 1 / 90 / 0 |

## Top-k 40 vs top-k 10

`semantic_gs_rrf_rerank_k40` minus `semantic_gs_rrf_rerank_k10_control`; shared items: `100`.

| Metric | N | Mean delta | Bootstrap 95% CI | Right better / same / worse |
|---|---:|---:|---|---:|
| faithfulness | 100 | 0.018 | [-0.017, 0.052] | 22 / 67 / 11 |
| answer_relevancy | 100 | 0.035 | [-0.000, 0.072] | 36 / 45 / 19 |
| context_recall | 91 | 0.048 | [0.004, 0.093] | 35 / 41 / 15 |
| citation_coverage | 91 | 0.003 | [0.000, 0.008] | 1 / 90 / 0 |

## Top-k 20 vs no-rerank reference

`semantic_gs_rrf_rerank_k20` minus `semantic_gs_rrf_no_rerank_reference`; shared items: `100`.

| Metric | N | Mean delta | Bootstrap 95% CI | Right better / same / worse |
|---|---:|---:|---|---:|
| faithfulness | 100 | 0.026 | [-0.014, 0.066] | 25 / 63 / 12 |
| answer_relevancy | 100 | -0.007 | [-0.050, 0.034] | 27 / 48 / 25 |
| context_recall | 91 | 0.008 | [-0.042, 0.056] | 24 / 47 / 20 |
| citation_coverage | 91 | 0.000 | [0.000, 0.000] | 0 / 91 / 0 |

## Top-k 40 vs no-rerank reference

`semantic_gs_rrf_rerank_k40` minus `semantic_gs_rrf_no_rerank_reference`; shared items: `100`.

| Metric | N | Mean delta | Bootstrap 95% CI | Right better / same / worse |
|---|---:|---:|---|---:|
| faithfulness | 100 | 0.018 | [-0.023, 0.057] | 23 / 64 / 13 |
| answer_relevancy | 100 | 0.015 | [-0.018, 0.047] | 30 / 46 / 24 |
| context_recall | 91 | 0.016 | [-0.028, 0.060] | 30 / 38 / 23 |
| citation_coverage | 91 | 0.000 | [0.000, 0.000] | 0 / 91 / 0 |
