# Final Ablation Report

Status: **complete**
Generated UTC: `2026-08-10T15:29:48.933566+00:00`
Git SHA: `cc93bb66e8b8cbe2c9843916ffe6ae504bd86c9e`

Git status:

```text
dirty (6 changed paths)
```

## Dataset / Identity

| Dataset | Items | SHA256 |
|---|---:|---|
| `benchmark/tuvi_golden_dataset/release/tuviqa_v1_release.jsonl` | 100 | `90376a87cec29cc22e93dc71b41e054ed2f0183bc515a52aa461fecd43cc008c` |

Notes:
- Official conclusion rows require `judge_backend=gemini`; offline smoke is not used as final evidence.
- Supabase persistence is intentionally non-blocking; local artifacts and checkpoints are the source of truth.
- `Score` is a transparent report heuristic for ranking only, not a replacement for individual metrics.
- `reports_final/10_chunking_strategy_ablation` and `reports_final/11_chunking_prompt_interaction_v1_v2` are immutable source waves for one canonical completed 3×3 Chunking × Prompt factorial matrix.
- No separate prompt/generation phase is active for the current study; prompt evidence is contained in the completed 3×3 matrix.

## Run Status

| Phase | Status | Judge | Configs | Pairs processed/expected | Current | Output |
|---|---|---|---|---|---|---|
| Chunking × Prompt Matrix (3 × 3, v1/v2/v3) | **completed** | `gemini` | 9/9 | 900/900 | n/a | `benchmark/tuvi_golden_dataset/reports_final/10_chunking_strategy_ablation + benchmark/tuvi_golden_dataset/reports_final/11_chunking_prompt_interaction_v1_v2` |
| Retrieval / Fusion / Reranker Matrix v2 | **completed** | `gemini` | 10/10 | 1000/1000 | baseline_graph_first / TVQA-100 | `benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix` |
| Targeted Hard-case Wave | **not_started** | `pending` | 0/4 | n/a/400 | n/a | `benchmark/tuvi_golden_dataset/reports_final/40_targeted_hard_cases` |

## 1. Experiment Inventory

| Phase | Config | Manifest | Config hash | Main variable | Items | Status |
|---|---|---|---|---|---|---|
| Chunking × Prompt Matrix (3 × 3, v1/v2/v3) | `fixed_512_graph_sparse_rrf` | `configs/w6_abl_03_chunking_matrix.yaml` | `6b8250da09920192b47712fa7f04237d6cf4c7c1c37e85bd1e8d6dbaac9cdb8a` | chunk=chunk_fixed_512; prompt=tuvi_generation_structured_v3 | 100 | **completed** |
| Chunking × Prompt Matrix (3 × 3, v1/v2/v3) | `parent_child_graph_sparse_rrf` | `configs/w6_abl_03_chunking_matrix.yaml` | `39be6f7d0e9a354361665e8d79ef1db47cb7b73826414aef0e96726d75938dfa` | chunk=chunk_structure_parent_child; prompt=tuvi_generation_structured_v3 | 100 | **completed** |
| Chunking × Prompt Matrix (3 × 3, v1/v2/v3) | `semantic_bge_m3_graph_sparse_rrf` | `configs/w6_abl_03_chunking_matrix.yaml` | `c6e72838cb37a55ea68dcdf3a3016d1b3e2bb5a133800423196bacc0fda2c195` | chunk=chunk_semantic_embedding_bge_m3; prompt=tuvi_generation_structured_v3 | 100 | **completed** |
| Chunking × Prompt Matrix (3 × 3, v1/v2/v3) | `fixed_512_prompt_v1_graph_sparse_rrf` | `configs/w8_abl_02_chunking_prompt_interaction_v1_v2.yaml` | `cda88b946b27fe8d4b0a1947454e02621f376fbd6db7e2ea79bb9755f4ac7b09` | chunk=chunk_fixed_512; prompt=tuvi_generation_v1 | 100 | **completed** |
| Chunking × Prompt Matrix (3 × 3, v1/v2/v3) | `parent_child_prompt_v1_graph_sparse_rrf` | `configs/w8_abl_02_chunking_prompt_interaction_v1_v2.yaml` | `fc2cbcc5af8bc07634b52e6c36087a234dbfaeaad9ed955fe54c56852060ec9d` | chunk=chunk_structure_parent_child; prompt=tuvi_generation_v1 | 100 | **completed** |
| Chunking × Prompt Matrix (3 × 3, v1/v2/v3) | `semantic_bge_m3_prompt_v1_graph_sparse_rrf` | `configs/w8_abl_02_chunking_prompt_interaction_v1_v2.yaml` | `2f4353b8d817c3619a12f5a2fd209f281dcd075f55ada652d88c5c66b165bf79` | chunk=chunk_semantic_embedding_bge_m3; prompt=tuvi_generation_v1 | 100 | **completed** |
| Chunking × Prompt Matrix (3 × 3, v1/v2/v3) | `fixed_512_prompt_v2_graph_sparse_rrf` | `configs/w8_abl_02_chunking_prompt_interaction_v1_v2.yaml` | `b5a585b4555e727b4b2d1d49f4cfbd06a4f1af4aaa5f8db278682c2a4aaee943` | chunk=chunk_fixed_512; prompt=tuvi_generation_grounded_v2 | 100 | **completed** |
| Chunking × Prompt Matrix (3 × 3, v1/v2/v3) | `parent_child_prompt_v2_graph_sparse_rrf` | `configs/w8_abl_02_chunking_prompt_interaction_v1_v2.yaml` | `e161a00da5776cc7996e6b66ece820e1f4b10161e91dbaaba1013ab1b67794b3` | chunk=chunk_structure_parent_child; prompt=tuvi_generation_grounded_v2 | 100 | **completed** |
| Chunking × Prompt Matrix (3 × 3, v1/v2/v3) | `semantic_bge_m3_prompt_v2_graph_sparse_rrf` | `configs/w8_abl_02_chunking_prompt_interaction_v1_v2.yaml` | `11674749195729f664e1935e79a47f819cabf0d5aa18c59a5d13da7b03d3f0f6` | chunk=chunk_semantic_embedding_bge_m3; prompt=tuvi_generation_grounded_v2 | 100 | **completed** |
| Retrieval / Fusion / Reranker Matrix v2 | `baseline_graph_sparse_rrf` | `configs/w8_abl_01_retrieval_matrix_v2.yaml` | `627c79c1a041e10e04f29fdad8eebaa1073d7a819bb5d735b0a5258104423943` | paths=GS; fusion=rrf; rerank=yes | 100 | **completed** |
| Retrieval / Fusion / Reranker Matrix v2 | `graph_only_rrf` | `configs/w8_abl_01_retrieval_matrix_v2.yaml` | `2ba12da545db12a3e7195260afc9c171ccaa22cedf8e54ad213df64956e11743` | paths=G; fusion=rrf; rerank=yes | 100 | **completed** |
| Retrieval / Fusion / Reranker Matrix v2 | `sparse_only_rrf` | `configs/w8_abl_01_retrieval_matrix_v2.yaml` | `305287d273a12e8e7b38b7a54f307a76bb656645a8846c3b3da59060c0173683` | paths=S; fusion=rrf; rerank=yes | 100 | **completed** |
| Retrieval / Fusion / Reranker Matrix v2 | `dense_only_rrf` | `configs/w8_abl_01_retrieval_matrix_v2.yaml` | `bde1c6dca9b34383234564753adc6bb2394589530a4cae78045165a3d76ab3a2` | paths=D; fusion=rrf; rerank=yes | 100 | **completed** |
| Retrieval / Fusion / Reranker Matrix v2 | `dense_sparse_rrf` | `configs/w8_abl_01_retrieval_matrix_v2.yaml` | `c801bd9b3dcd211b5b580d1d1832bb122a1fce5daf4f8d2cad33dc9c759bc2d2` | paths=DS; fusion=rrf; rerank=yes | 100 | **completed** |
| Retrieval / Fusion / Reranker Matrix v2 | `graph_dense_rrf` | `configs/w8_abl_01_retrieval_matrix_v2.yaml` | `155aa01c9275b6fe8af34bd9f839052041811c145b00c24ade1e0d81305b7fc5` | paths=GD; fusion=rrf; rerank=yes | 100 | **completed** |
| Retrieval / Fusion / Reranker Matrix v2 | `all_paths_planner_dense_rrf` | `configs/w8_abl_01_retrieval_matrix_v2.yaml` | `826da9182fa625efeddcd0b98d06f2bfb1d49499d7c4a90cb5e32ce151efb6a5` | paths=GDS; fusion=rrf; rerank=yes | 100 | **completed** |
| Retrieval / Fusion / Reranker Matrix v2 | `baseline_no_reranker` | `configs/w8_abl_01_retrieval_matrix_v2.yaml` | `eb65d183e8a38286e52fd75ca9ac1b7117c70273554e94c125fd9de588251bf7` | paths=GS; fusion=rrf; rerank=no | 100 | **completed** |
| Retrieval / Fusion / Reranker Matrix v2 | `baseline_weighted_sum` | `configs/w8_abl_01_retrieval_matrix_v2.yaml` | `db9038d4fabf98a17a8db3259a94c811373a447c3d4db907efc8f8706a7f4d6d` | paths=GS; fusion=weighted_sum; rerank=yes | 100 | **completed** |
| Retrieval / Fusion / Reranker Matrix v2 | `baseline_graph_first` | `configs/w8_abl_01_retrieval_matrix_v2.yaml` | `0bb737b18f6627e617d80b2d65a28f589ced3725365e84e37825439fb7f3cb0b` | paths=GS; fusion=graph_first; rerank=yes | 100 | **completed** |
| Targeted Hard-case Wave | `sparse_only_rrf` | `configs/w8_abl_01_priority_wave.yaml` | `305287d273a12e8e7b38b7a54f307a76bb656645a8846c3b3da59060c0173683` | paths=S; fusion=rrf; rerank=yes | 100 | **not_started** |
| Targeted Hard-case Wave | `dense_sparse_rrf` | `configs/w8_abl_01_priority_wave.yaml` | `c801bd9b3dcd211b5b580d1d1832bb122a1fce5daf4f8d2cad33dc9c759bc2d2` | paths=DS; fusion=rrf; rerank=yes | 100 | **not_started** |
| Targeted Hard-case Wave | `baseline_no_reranker` | `configs/w8_abl_01_priority_wave.yaml` | `eb65d183e8a38286e52fd75ca9ac1b7117c70273554e94c125fd9de588251bf7` | paths=GS; fusion=rrf; rerank=no | 100 | **not_started** |
| Targeted Hard-case Wave | `baseline_weighted_sum` | `configs/w8_abl_01_priority_wave.yaml` | `db9038d4fabf98a17a8db3259a94c811373a447c3d4db907efc8f8706a7f4d6d` | paths=GS; fusion=weighted_sum; rerank=yes | 100 | **not_started** |

## 2. Metric Tables

### Chunking × Prompt Matrix (3 × 3, v1/v2/v3)

| Rank | Config | Score | Main variable | Faith | Relev | CtxRecall | GraphHit | Citation | RAG p95 ms | Retr p95 ms | Gen p95 ms |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `parent_child_graph_sparse_rrf` | 0.749 | chunk=chunk_structure_parent_child; prompt=tuvi_generation_structured_v3 | 0.900 | 0.799 | 0.714 | 0.967 | 0.989 | 123459.1 | 118592.8 | 5595.9 |
| 2 | `fixed_512_graph_sparse_rrf` | 0.748 | chunk=chunk_fixed_512; prompt=tuvi_generation_structured_v3 | 0.894 | 0.794 | 0.718 | 0.967 | 0.989 | 207600.5 | 199379.7 | 8124.1 |
| 3 | `semantic_bge_m3_graph_sparse_rrf` | 0.738 | chunk=chunk_semantic_embedding_bge_m3; prompt=tuvi_generation_structured_v3 | 0.889 | 0.779 | 0.699 | 0.967 | 0.989 | 168386.9 | 163092.5 | 5686.5 |
| 4 | `semantic_bge_m3_prompt_v1_graph_sparse_rrf` | 0.737 | chunk=chunk_semantic_embedding_bge_m3; prompt=tuvi_generation_v1 | 0.872 | 0.782 | 0.706 | 0.967 | 0.986 | 166491.8 | 163307.5 | 6047.2 |
| 5 | `fixed_512_prompt_v1_graph_sparse_rrf` | 0.726 | chunk=chunk_fixed_512; prompt=tuvi_generation_v1 | 0.880 | 0.770 | 0.667 | 0.967 | 0.992 | 181525.3 | 178549.3 | 4799.7 |
| 6 | `parent_child_prompt_v1_graph_sparse_rrf` | 0.723 | chunk=chunk_structure_parent_child; prompt=tuvi_generation_v1 | 0.878 | 0.763 | 0.663 | 0.967 | 0.995 | 119401.3 | 115384.2 | 4461.3 |
| 7 | `semantic_bge_m3_prompt_v2_graph_sparse_rrf` | 0.709 | chunk=chunk_semantic_embedding_bge_m3; prompt=tuvi_generation_grounded_v2 | 0.870 | 0.736 | 0.638 | 0.967 | 0.997 | 164979.5 | 161562.3 | 4833.3 |
| 8 | `parent_child_prompt_v2_graph_sparse_rrf` | 0.697 | chunk=chunk_structure_parent_child; prompt=tuvi_generation_grounded_v2 | 0.859 | 0.715 | 0.620 | 0.967 | 0.997 | 100804.9 | 96942.6 | 4512.1 |
| 9 | `fixed_512_prompt_v2_graph_sparse_rrf` | 0.671 | chunk=chunk_fixed_512; prompt=tuvi_generation_grounded_v2 | 0.813 | 0.683 | 0.584 | 0.967 | 0.997 | 147154.6 | 143860.4 | 4427.7 |

### Retrieval / Fusion / Reranker Matrix v2

| Rank | Config | Score | Main variable | Faith | Relev | CtxRecall | GraphHit | Citation | RAG p95 ms | Retr p95 ms | Gen p95 ms |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `baseline_no_reranker` | 0.845 | paths=GS; fusion=rrf; rerank=no | 0.915 | 0.828 | 0.744 | 0.967 | 0.989 | 12819.4 | 6374.7 | 6150.7 |
| 2 | `graph_dense_rrf` | 0.773 | paths=GD; fusion=rrf; rerank=yes | 0.912 | 0.837 | 0.759 | 0.967 | 0.989 | 72032.1 | 67813.9 | 5713.8 |
| 3 | `all_paths_planner_dense_rrf` | 0.749 | paths=GDS; fusion=rrf; rerank=yes | 0.880 | 0.801 | 0.725 | 0.967 | 0.989 | 254152.1 | 249658.3 | 5650.3 |
| 4 | `baseline_graph_first` | 0.747 | paths=GS; fusion=graph_first; rerank=yes | 0.876 | 0.798 | 0.725 | 0.967 | 0.986 | 272370.0 | 256114.7 | 10911.4 |
| 5 | `baseline_graph_sparse_rrf` | 0.741 | paths=GS; fusion=rrf; rerank=yes | 0.888 | 0.789 | 0.704 | 0.967 | 0.986 | 138041.3 | 133807.7 | 8271.4 |
| 6 | `baseline_weighted_sum` | 0.738 | paths=GS; fusion=weighted_sum; rerank=yes | 0.881 | 0.794 | 0.695 | 0.967 | 0.989 | 181602.9 | 176712.8 | 8569.1 |
| 7 | `dense_only_rrf` | 0.715 | paths=D; fusion=rrf; rerank=yes | 0.904 | 0.812 | 0.736 | 0.000 | 0.989 | 28176.5 | 18159.8 | 10253.5 |
| 8 | `graph_only_rrf` | 0.669 | paths=G; fusion=rrf; rerank=yes | 0.823 | 0.686 | 0.530 | 0.967 | 0.978 | 50836.0 | 40969.8 | 7071.6 |
| 9 | `dense_sparse_rrf` | 0.665 | paths=DS; fusion=rrf; rerank=yes | 0.902 | 0.818 | 0.742 | 0.000 | 0.989 | 226613.4 | 221271.0 | 6168.4 |
| 10 | `sparse_only_rrf` | 0.647 | paths=S; fusion=rrf; rerank=yes | 0.900 | 0.802 | 0.696 | 0.000 | 0.986 | 163360.4 | 155286.3 | 12173.2 |

### Targeted Hard-case Wave

No completed `evaluation_report.json` yet. Current status: **not_started**; checkpoint processed n/a/400 pairs.

## 3. Marginal Summary within Completed Chunking × Prompt Matrix

These averages summarize the 9 completed factorial cells by one factor at a time. They are descriptive marginal summaries of the same 3×3 study, not additional runs.

### By chunking strategy

| Rank | Value | Cells | Score | Faith | Relev | CtxRecall | Citation | RAG p95 ms | Retr p95 ms |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `chunk_semantic_embedding_bge_m3` | 3 | 0.728 | 0.877 | 0.766 | 0.681 | 0.991 | 166619.4 | 162654.1 |
| 2 | `chunk_structure_parent_child` | 3 | 0.723 | 0.879 | 0.759 | 0.666 | 0.994 | 114555.1 | 110306.6 |
| 3 | `chunk_fixed_512` | 3 | 0.715 | 0.862 | 0.749 | 0.656 | 0.993 | 178760.1 | 173929.8 |

### By prompt template

| Rank | Value | Cells | Score | Faith | Relev | CtxRecall | Citation | RAG p95 ms | Retr p95 ms |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `tuvi_generation_structured_v3` | 3 | 0.745 | 0.894 | 0.791 | 0.710 | 0.989 | 166482.2 | 160355.0 |
| 2 | `tuvi_generation_v1` | 3 | 0.729 | 0.877 | 0.772 | 0.679 | 0.991 | 155806.1 | 152413.7 |
| 3 | `tuvi_generation_grounded_v2` | 3 | 0.692 | 0.847 | 0.711 | 0.614 | 0.997 | 137646.3 | 134121.8 |

## 4. Winners by Axis

| Axis | Winner | Evidence / interpretation |
|---|---|---|
| Best chunking × prompt configuration | `parent_child_graph_sparse_rrf` (score=0.749) | Full 3 × 3 matrix: source wave A in `10_chunking_strategy_ablation` supplies the 3 prompt-v3 cells; source wave B in `11_chunking_prompt_interaction_v1_v2` supplies the 6 prompt-v1/v2 cells. Retrieval is held fixed. Score ranks Context Recall, Faithfulness, Relevancy, Citation Coverage, Graph Hit, and p95 latency. |
| Best chunking strategy within 3×3 matrix | `chunk_semantic_embedding_bge_m3` (marginal score=0.728, cells=3) | Marginal average across all 3 prompt templates in the completed matrix. |
| Best prompt template within 3×3 matrix | `tuvi_generation_structured_v3` (marginal score=0.745, cells=3) | Marginal average across all 3 chunking strategies in the completed matrix. This replaces the old separate prompt-ablation placeholder for the current study. |
| Best retrieval path combination | `baseline_no_reranker` (score=0.845) | paths=GS; fusion=rrf; rerank=no |
| Best fusion method | `baseline_no_reranker` (score=0.845) | Derived from the Phase 3 winning config; compare RRF vs weighted_sum vs graph_first in the Phase 3 table. |
| Reranker on/off | `baseline_no_reranker` (score=0.845) | Derived from baseline vs `baseline_no_reranker` once Phase 3 is complete. |

## 5. Winners by Question Family

### Chunking × Prompt Matrix (3 × 3, v1/v2/v3)

| Family | Winner | Score | Items | Faith | Relev | CtxRecall | GraphHit | Citation | Retr p95 ms |
|---|---|---|---|---|---|---|---|---|---|
| core_identity | `parent_child_prompt_v1_graph_sparse_rrf` | 0.733 | 10 | 1.000 | 0.840 | 0.700 | 0.000 | 0.750 | 0.2 |
| menh_house_interpretation | `parent_child_graph_sparse_rrf` | 0.714 | 10 | 0.880 | 0.720 | 0.680 | 0.900 | 1.000 | 126343.1 |
| than_cu_interpretation | `semantic_bge_m3_prompt_v1_graph_sparse_rrf` | 0.851 | 10 | 0.940 | 0.920 | 0.930 | 1.000 | 1.000 | 158771.9 |
| menh_cuc_relation | `semantic_bge_m3_graph_sparse_rrf` | 0.868 | 10 | 1.000 | 0.930 | 0.940 | 1.000 | 1.000 | 100384.5 |
| special_state_interpretation | `fixed_512_graph_sparse_rrf` | 0.755 | 10 | 0.920 | 0.790 | 0.710 | 1.000 | 1.000 | 208271.8 |
| menh_tam_hop | `semantic_bge_m3_graph_sparse_rrf` | 0.739 | 10 | 0.900 | 0.790 | 0.670 | 1.000 | 1.000 | 160919.1 |
| menh_xung_chieu | `parent_child_graph_sparse_rrf` | 0.723 | 10 | 0.840 | 0.770 | 0.670 | 1.000 | 1.000 | 102210.9 |
| dai_van_interpretation | `fixed_512_graph_sparse_rrf` | 0.713 | 10 | 0.880 | 0.710 | 0.650 | 1.000 | 1.000 | 176186.9 |
| topic_house_plus_relations | `parent_child_graph_sparse_rrf` | 0.847 | 10 | 0.980 | 0.920 | 0.890 | 1.000 | 1.000 | 112981.8 |
| synthesis_judgement | `fixed_512_prompt_v1_graph_sparse_rrf` | 0.757 | 10 | 0.910 | 0.840 | 0.723 | 0.900 | 1.000 | 209725.7 |

### Retrieval / Fusion / Reranker Matrix v2

| Family | Winner | Score | Items | Faith | Relev | CtxRecall | GraphHit | Citation | Retr p95 ms |
|---|---|---|---|---|---|---|---|---|---|
| core_identity | `sparse_only_rrf` | 0.655 | 10 | 1.000 | 0.860 | 0.800 | 0.000 | 0.000 | 0.7 |
| menh_house_interpretation | `baseline_no_reranker` | 0.770 | 10 | 0.840 | 0.730 | 0.630 | 0.900 | 1.000 | 5907.3 |
| than_cu_interpretation | `baseline_no_reranker` | 0.921 | 10 | 0.930 | 0.970 | 0.870 | 1.000 | 1.000 | 6048.4 |
| menh_cuc_relation | `baseline_no_reranker` | 0.939 | 10 | 1.000 | 0.940 | 0.920 | 1.000 | 1.000 | 4630.8 |
| special_state_interpretation | `baseline_no_reranker` | 0.844 | 10 | 0.940 | 0.830 | 0.700 | 1.000 | 1.000 | 5997.8 |
| menh_tam_hop | `baseline_no_reranker` | 0.819 | 10 | 0.890 | 0.790 | 0.670 | 1.000 | 1.000 | 6199.6 |
| menh_xung_chieu | `baseline_no_reranker` | 0.834 | 10 | 0.870 | 0.810 | 0.720 | 1.000 | 1.000 | 5742.5 |
| dai_van_interpretation | `baseline_no_reranker` | 0.756 | 10 | 0.820 | 0.680 | 0.580 | 1.000 | 1.000 | 5516.9 |
| topic_house_plus_relations | `baseline_no_reranker` | 0.889 | 10 | 0.940 | 0.880 | 0.810 | 1.000 | 1.000 | 6105.9 |
| synthesis_judgement | `baseline_no_reranker` | 0.867 | 10 | 0.920 | 0.880 | 0.800 | 0.900 | 1.000 | 7809.3 |

### Targeted Hard-case Wave

Pending: no completed report yet for this phase (`not_started`).

## 6. Winners by Question Complexity

### Chunking × Prompt Matrix (3 × 3, v1/v2/v3)

| Complexity | Winner | Score | Items | Faith | Relev | CtxRecall | Citation | Retr p95 ms |
|---|---|---|---|---|---|---|---|---|
| Direct | `parent_child_prompt_v1_graph_sparse_rrf` | 0.733 | 10 | 1.000 | 0.840 | 0.700 | 0.750 | 0.2 |
| One-hop | `fixed_512_graph_sparse_rrf` | 0.765 | 46 | 0.911 | 0.800 | 0.750 | 1.000 | 192412.7 |
| Two-hop | `parent_child_graph_sparse_rrf` | 0.744 | 44 | 0.886 | 0.789 | 0.705 | 1.000 | 125391.6 |

### Retrieval / Fusion / Reranker Matrix v2

| Complexity | Winner | Score | Items | Faith | Relev | CtxRecall | Citation | Retr p95 ms |
|---|---|---|---|---|---|---|---|---|
| Direct | `sparse_only_rrf` | 0.655 | 10 | 1.000 | 0.860 | 0.800 | 0.000 | 0.7 |
| One-hop | `baseline_no_reranker` | 0.857 | 46 | 0.924 | 0.848 | 0.756 | 1.000 | 6072.8 |
| Two-hop | `baseline_no_reranker` | 0.839 | 44 | 0.886 | 0.821 | 0.732 | 1.000 | 6926.9 |

## 7. Research/Eval Candidate

All required evidence is available. Create a new candidate config rather than overwriting `configs/default_production.yaml`.

Recommended candidate ingredients:
- chunk_strategy_id: `chunk_structure_parent_child`
- prompt_template_id: `tuvi_generation_structured_v3`
- generation_model: `gemini-3.1-flash-lite-preview`
- retrieval: `paths=GS; fusion=rrf; rerank=no`

Suggested file: `configs/eval_candidate_v3.yaml`, followed by a final full-100 or hard-case confirmation run.

## 8. Next Steps / Resume Commands

Re-run this report builder after each phase completes:

```powershell
$env:PYTHONPATH='backend'
.\.venv\Scripts\python.exe scripts\build_final_ablation_report.py
```
