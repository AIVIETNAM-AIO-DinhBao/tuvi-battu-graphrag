# Complete Ablation Study Synthesis

Generated UTC: `2026-08-17T01:50:34.027639Z`

## Scope and evidence status

This report synthesizes all completed comparative ablations without overwriting their raw reports:

1. **Chunking × Prompt 3×3 matrix**: 9 configs × 100 items = 900 Gemini-judged pairs.
2. **Retrieval / Fusion / Reranker v2 (k10)**: 10 configs × 100 items = 1,000 Gemini-judged pairs.
3. **Retrieval / Fusion / Reranker v3 (k40)**: 10 configs × 100 items = 1,000 Gemini-judged pairs; 8 configs are fresh Phase 53 runs and two Graph+Sparse controls are provenance-preserving Phase 52 rows.

All source reports below are completed, Gemini-judged, use the same 100-item release dataset, and have zero failed pairs.

## Source provenance

| Source | Path | SHA-256 | Configs | Completed / Failed |
|---|---|---|---:|---:|
| `chunking_prompt_v3` | `benchmark/tuvi_golden_dataset/reports_final/10_chunking_strategy_ablation/evaluation_report.json` | `766ca8aeadd3a6503be91038c55b2a7f46bb45180b60701ed452b16352b52f1b` | 3 | 300 / 0 |
| `chunking_prompt_v1_v2` | `benchmark/tuvi_golden_dataset/reports_final/11_chunking_prompt_interaction_v1_v2/evaluation_report.json` | `78f308fca2e75b34dde1e7c3587f4f68701b7da2ef0acac6e28f2329b5b7b562` | 6 | 600 / 0 |
| `retrieval_k10` | `benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/evaluation_report.json` | `7b2e1160a0acfcdcb2d18152ae8aad0cc622a60e07817c1c851924b2d26550da` | 10 | 1000 / 0 |
| `retrieval_k40` | `benchmark/tuvi_golden_dataset/reports_final/53_retrieval_fusion_reranker_k40_matrix/evaluation_report.json` | `51d7d3f337aca953528edc0920591d874c4b7ccdefc72ff1d8d5b168068dc538` | 10 | 1000 / 0 |
| `k40_reused_phase52_controls` | `benchmark/tuvi_golden_dataset/reports_final/53_retrieval_fusion_reranker_k40_matrix/reused_phase52_controls/evaluation_report.json` | `9802feef71e8d4b9bc2bd09620e5b0c63b26fad57d8d36da695135b0cbccead2` | 2 | 200 / 0 |

## Metric interpretation

- **Faithfulness**, **answer relevancy**, **context recall**, and **citation coverage** are Gemini-judged or evidence-derived quality metrics from each run.
- **Quality score** is a descriptive rank only; it deliberately excludes latency so a quality winner is not confused with a production latency winner.
- Cross-wave latency is descriptive because runs occurred in different sessions. Use latency directionally, and do not treat it as a controlled hardware benchmark across waves.

## 1. Chunking × Prompt 3×3 matrix

| Rank | Config | Chunk | Prompt | Quality score | Faith | Relev | CtxRecall | Citation | GraphHit | Retr p95 ms | RAG p95 ms |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `parent_child_graph_sparse_rrf` | chunk_structure_parent_child; tuvi_generation_structured_v3 | 0.832 | 0.900 | 0.799 | 0.714 | 0.989 | 0.967 | 118592.8 | 123459.1 |
| 2 | `fixed_512_graph_sparse_rrf` | chunk_fixed_512; tuvi_generation_structured_v3 | 0.830 | 0.894 | 0.794 | 0.718 | 0.989 | 0.967 | 199379.7 | 207600.5 |
| 3 | `semantic_bge_m3_graph_sparse_rrf` | chunk_semantic_embedding_bge_m3; tuvi_generation_structured_v3 | 0.819 | 0.889 | 0.779 | 0.699 | 0.989 | 0.967 | 163092.5 | 168386.9 |
| 4 | `semantic_bge_m3_prompt_v1_graph_sparse_rrf` | chunk_semantic_embedding_bge_m3; tuvi_generation_v1 | 0.818 | 0.872 | 0.782 | 0.706 | 0.986 | 0.967 | 163307.5 | 166491.8 |
| 5 | `fixed_512_prompt_v1_graph_sparse_rrf` | chunk_fixed_512; tuvi_generation_v1 | 0.805 | 0.880 | 0.770 | 0.667 | 0.992 | 0.967 | 178549.3 | 181525.3 |
| 6 | `parent_child_prompt_v1_graph_sparse_rrf` | chunk_structure_parent_child; tuvi_generation_v1 | 0.802 | 0.878 | 0.763 | 0.663 | 0.995 | 0.967 | 115384.2 | 119401.3 |
| 7 | `semantic_bge_m3_prompt_v2_graph_sparse_rrf` | chunk_semantic_embedding_bge_m3; tuvi_generation_grounded_v2 | 0.786 | 0.870 | 0.736 | 0.638 | 0.997 | 0.967 | 161562.3 | 164979.5 |
| 8 | `parent_child_prompt_v2_graph_sparse_rrf` | chunk_structure_parent_child; tuvi_generation_grounded_v2 | 0.773 | 0.859 | 0.715 | 0.620 | 0.997 | 0.967 | 96942.6 | 100804.9 |
| 9 | `fixed_512_prompt_v2_graph_sparse_rrf` | chunk_fixed_512; tuvi_generation_grounded_v2 | 0.742 | 0.813 | 0.683 | 0.584 | 0.997 | 0.967 | 143860.4 | 147154.6 |

**Interpretation.** The best completed cell is `parent_child_graph_sparse_rrf`. The completed 3×3 evidence also supports `tuvi_generation_structured_v3` as the strongest prompt family in the prior marginal analysis.

## 2. Retrieval / Fusion / Reranker matrix v2 — reranker top_k=10

| Rank | Config | Retrieval / fusion / rerank | Quality score | Faith | Relev | CtxRecall | Citation | GraphHit | Retr p95 ms | RAG p95 ms |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `graph_dense_rrf` | paths=GD; fusion=rrf; rerank=on | 0.858 | 0.912 | 0.837 | 0.759 | 0.989 | 0.967 | 67813.9 | 72032.1 |
| 2 | `baseline_no_reranker` | paths=GS; fusion=rrf; rerank=off | 0.851 | 0.915 | 0.828 | 0.744 | 0.989 | 0.967 | 6374.7 | 12819.4 |
| 3 | `all_paths_planner_dense_rrf` | paths=GDS; fusion=rrf; rerank=on | 0.831 | 0.880 | 0.801 | 0.725 | 0.989 | 0.967 | 249658.3 | 254152.1 |
| 4 | `baseline_graph_first` | paths=GS; fusion=graph_first; rerank=on | 0.829 | 0.876 | 0.798 | 0.725 | 0.986 | 0.967 | 256114.7 | 272370.0 |
| 5 | `baseline_graph_sparse_rrf` | paths=GS; fusion=rrf; rerank=on | 0.823 | 0.888 | 0.789 | 0.704 | 0.986 | 0.967 | 133807.7 | 138041.3 |
| 6 | `baseline_weighted_sum` | paths=GS; fusion=weighted_sum; rerank=on | 0.819 | 0.881 | 0.794 | 0.695 | 0.989 | 0.967 | 176712.8 | 181602.9 |
| 7 | `dense_sparse_rrf` | paths=DS; fusion=rrf; rerank=on | 0.797 | 0.902 | 0.818 | 0.742 | 0.989 | 0.000 | 221271.0 | 226613.4 |
| 8 | `dense_only_rrf` | paths=D; fusion=rrf; rerank=on | 0.794 | 0.904 | 0.812 | 0.736 | 0.989 | 0.000 | 18159.8 | 28176.5 |
| 9 | `sparse_only_rrf` | paths=S; fusion=rrf; rerank=on | 0.777 | 0.900 | 0.802 | 0.696 | 0.986 | 0.000 | 155286.3 | 163360.4 |
| 10 | `graph_only_rrf` | paths=G; fusion=rrf; rerank=on | 0.723 | 0.823 | 0.686 | 0.530 | 0.978 | 0.967 | 40969.8 | 50836.0 |

## 3. Retrieval / Fusion / Reranker matrix v3 — reranker top_k=40

| Rank | Config | Retrieval / fusion / rerank | Quality score | Faith | Relev | CtxRecall | Citation | GraphHit | Retr p95 ms | RAG p95 ms |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `graph_sparse_graph_first_k40` | paths=GS; fusion=graph_first; rerank=on | 0.856 | 0.923 | 0.834 | 0.752 | 0.978 | 0.967 | 204464.1 | 215686.5 |
| 2 | `semantic_gs_rrf_rerank_k40` | paths=GS; fusion=rrf; rerank=on | 0.854 | 0.906 | 0.830 | 0.757 | 0.989 | 0.967 | 162516.2 | 168191.2 |
| 3 | `all_paths_planner_dense_rrf_k40` | paths=GDS; fusion=rrf; rerank=on | 0.851 | 0.927 | 0.819 | 0.740 | 0.989 | 0.967 | 191696.4 | 198212.6 |
| 4 | `graph_sparse_weighted_sum_k40` | paths=GS; fusion=weighted_sum; rerank=on | 0.847 | 0.925 | 0.820 | 0.730 | 0.989 | 0.967 | 164716.4 | 170644.9 |
| 5 | `semantic_gs_rrf_no_rerank_reference` | paths=GS; fusion=rrf; rerank=off | 0.841 | 0.888 | 0.815 | 0.741 | 0.989 | 0.967 | 8321.1 | 21543.6 |
| 6 | `graph_dense_rrf_k40` | paths=GD; fusion=rrf; rerank=on | 0.840 | 0.907 | 0.809 | 0.729 | 0.989 | 0.967 | 72364.4 | 76817.9 |
| 7 | `dense_sparse_rrf_k40` | paths=DS; fusion=rrf; rerank=on | 0.807 | 0.911 | 0.833 | 0.755 | 0.989 | 0.000 | 167455.7 | 172348.2 |
| 8 | `sparse_only_rrf_k40` | paths=S; fusion=rrf; rerank=on | 0.790 | 0.909 | 0.800 | 0.728 | 0.989 | 0.000 | 157760.0 | 162410.7 |
| 9 | `dense_only_rrf_k40` | paths=D; fusion=rrf; rerank=on | 0.790 | 0.901 | 0.811 | 0.730 | 0.978 | 0.000 | 21173.1 | 25463.9 |
| 10 | `graph_only_rrf_k40` | paths=G; fusion=rrf; rerank=on | 0.759 | 0.858 | 0.737 | 0.589 | 0.953 | 0.967 | 34791.9 | 40724.5 |

## 4. k10 → k40 behavior comparison

Each row compares the corresponding retrieval/fusion behavior. Positive deltas favor the k40 matrix. The no-rerank reference is behaviorally unaffected by reranker top-k and is included as a run-to-run reference only.

| k10 config | k40 config | Δ Faith | Δ Relevancy | Δ Context recall | Δ Citation |
|---|---|---:|---:|---:|---:|
| `baseline_graph_sparse_rrf` | `semantic_gs_rrf_rerank_k40` | +0.018 | +0.041 | +0.053 | +0.003 |
| `graph_only_rrf` | `graph_only_rrf_k40` | +0.035 | +0.051 | +0.059 | -0.025 |
| `sparse_only_rrf` | `sparse_only_rrf_k40` | +0.009 | -0.002 | +0.032 | +0.003 |
| `dense_only_rrf` | `dense_only_rrf_k40` | -0.003 | -0.001 | -0.006 | -0.011 |
| `dense_sparse_rrf` | `dense_sparse_rrf_k40` | +0.009 | +0.015 | +0.013 | +0.000 |
| `graph_dense_rrf` | `graph_dense_rrf_k40` | -0.005 | -0.028 | -0.031 | +0.000 |
| `all_paths_planner_dense_rrf` | `all_paths_planner_dense_rrf_k40` | +0.047 | +0.018 | +0.014 | +0.000 |
| `baseline_no_reranker` | `semantic_gs_rrf_no_rerank_reference` | -0.027 | -0.013 | -0.003 | +0.000 |
| `baseline_weighted_sum` | `graph_sparse_weighted_sum_k40` | +0.044 | +0.026 | +0.035 | +0.000 |
| `baseline_graph_first` | `graph_sparse_graph_first_k40` | +0.047 | +0.036 | +0.026 | -0.008 |

## 5. Conclusions

1. **Best completed chunking × prompt cell:** `parent_child_graph_sparse_rrf`.
2. **Best k10 quality-score config:** `graph_dense_rrf`.
3. **Best k40 quality-score config:** `graph_sparse_graph_first_k40`.
4. **Quality-first retrieval candidate:** `semantic_gs_rrf_rerank_k40` has the highest k40 context recall.
5. **Production quality/latency candidate:** `semantic_gs_rrf_no_rerank_reference` keeps Graph+Sparse RRF and disables reranking. It is the low-latency choice; compare its quality metrics explicitly with the k40 quality-first candidate before deployment.
6. **Reranker finding:** increasing BGE reranker top-k from 10 to 40 improves several reranked path/fusion variants, confirming that top-10 was an overly restrictive early pruning point. The k40 result does not erase the operational advantage of the no-rerank route.

## Hybrid-matrix limitation

The k40 matrix is integrity-checked at 10 configs / 1,000 pairs / 0 failed pairs. Its two Graph+Sparse controls were reused verbatim from Phase 52 with source SHA-256 provenance, while eight variants are fresh Phase 53 runs. Quality comparisons remain supported by the common dataset/config hashes/Gemini judge; absolute cross-source latency comparisons should remain descriptive.
