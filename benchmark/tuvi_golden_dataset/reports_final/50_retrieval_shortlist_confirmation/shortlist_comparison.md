# W8 Retrieval Shortlist Confirmation

This is a Phase 50 isolated confirmation run. It is separate from the canonical W8 matrix and does not replace its artifacts.

- Generated UTC: `2026-08-14T02:01:56.038001Z`
- Dataset items: `100`
- Judge backend: `gemini`
- Pairwise deltas are `right - left`; positive values favor the right-hand configuration.
- Bootstrap CIs use 5,000 seeded resamples and are descriptive, not a replacement for a preregistered significance test.

## Aggregate metrics

| Config | Faith | Relevancy | Context recall | Citation | Graph hit | RAG p95 ms | Retrieval p95 ms |
|---|---:|---:|---:|---:|---:|---:|---:|
| semantic_gs_rrf_rerank_on_control | 0.890 | 0.790 | 0.700 | 0.978 | 0.967 | 190410.2 | 181112.5 |
| semantic_gs_rrf_rerank_off_candidate | 0.916 | 0.829 | 0.763 | 0.989 | 0.967 | 13283.5 | 7293.2 |
| semantic_gd_rrf_rerank_on_quality | 0.908 | 0.819 | 0.731 | 0.989 | 0.967 | 47950.2 | 41092.4 |

## Reranker on vs off: matched Graph + Sparse + RRF

`semantic_gs_rrf_rerank_off_candidate` minus `semantic_gs_rrf_rerank_on_control`; shared items: `100`.

| Metric | N | Mean delta | Bootstrap 95% CI | Right better / same / worse |
|---|---:|---:|---|---:|
| faithfulness | 100 | 0.026 | [-0.009, 0.066] | 21 / 63 / 16 |
| answer_relevancy | 100 | 0.039 | [0.007, 0.075] | 35 / 46 / 19 |
| context_recall | 91 | 0.063 | [0.018, 0.110] | 35 / 38 / 18 |
| citation_coverage | 91 | 0.011 | [0.000, 0.033] | 1 / 90 / 0 |

## Production candidate vs quality challenger: Graph + Sparse no-rerank vs Graph + Dense rerank

`semantic_gd_rrf_rerank_on_quality` minus `semantic_gs_rrf_rerank_off_candidate`; shared items: `100`.

| Metric | N | Mean delta | Bootstrap 95% CI | Right better / same / worse |
|---|---:|---:|---|---:|
| faithfulness | 100 | -0.008 | [-0.044, 0.027] | 18 / 60 / 22 |
| answer_relevancy | 100 | -0.010 | [-0.045, 0.024] | 26 / 41 / 33 |
| context_recall | 91 | -0.032 | [-0.081, 0.013] | 24 / 36 / 31 |
| citation_coverage | 91 | 0.000 | [0.000, 0.000] | 0 / 91 / 0 |

## Decision rule

Promote reranker-off only if it is non-inferior on the three quality metrics versus the matched Graph+Sparse control and its operational latency is acceptable. Promote Graph+Dense only if its quality gain over reranker-off justifies the measured latency/cost trade-off in this same-machine run.
