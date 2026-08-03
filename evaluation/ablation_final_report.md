# Final Ablation Report

Status: **in_progress**
Generated UTC: `2026-08-03T06:33:17.485077+00:00`
Git SHA: `0173f4605ec6c96c87fda5e3f50e9bfeaf6d64f5`

Git status:

```text
M benchmark/tuvi_golden_dataset/reports_final/README.md
 M benchmark/tuvi_golden_dataset/reports_final/ablation_final_summary.json
 M benchmark/tuvi_golden_dataset/reports_final/protocol/commands.md
 M benchmark/tuvi_golden_dataset/reports_final/protocol/method_protocol.md
 M benchmark/tuvi_golden_dataset/reports_final/protocol/run_registry.md
 M evaluation/ablation_final_report.md
 M scripts/build_final_ablation_report.py
?? benchmark/tuvi_golden_dataset/reports_final/protocol/next_session_handoff.md
```

## Dataset / Identity

| Dataset | Items | SHA256 |
|---|---:|---|
| `benchmark/tuvi_golden_dataset/release/tuviqa_v1_release.jsonl` | 100 | `90376a87cec29cc22e93dc71b41e054ed2f0183bc515a52aa461fecd43cc008c` |

Notes:
- Official conclusion rows require `judge_backend=gemini`; offline smoke is not used as final evidence.
- Supabase persistence is intentionally non-blocking; local artifacts and checkpoints are the source of truth.
- `Score` is a transparent report heuristic for ranking only, not a replacement for individual metrics.
- Interaction phases vary more than one factor jointly; use them as supporting evidence, not as replacements for single-axis ablations.

## Run Status

| Phase | Status | Judge | Configs | Pairs processed/expected | Current | Output |
|---|---|---|---|---|---|---|
| Chunking Strategy Ablation | **completed** | `gemini` | 3/3 | 300/300 | semantic_bge_m3_graph_sparse_rrf / TVQA-100 | `benchmark/tuvi_golden_dataset/reports_final/10_chunking_strategy_ablation` |
| Chunking × Prompt Interaction (v1/v2) | **completed** | `gemini` | 6/6 | 600/600 | semantic_bge_m3_prompt_v2_graph_sparse_rrf / TVQA-100 | `benchmark/tuvi_golden_dataset/reports_final/11_chunking_prompt_interaction_v1_v2` |
| Retrieval / Fusion / Reranker Matrix v2 | **not_started** | `pending` | 0/10 | n/a/1000 | n/a | `benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix` |
| Prompt / Generation Ablation on Current Retrieval | **not_started** | `pending` | 0/3 | n/a/300 | n/a | `benchmark/tuvi_golden_dataset/reports_final/30_prompt_generation_current_retrieval` |
| Prompt / Generation Ablation on Best Retrieval | **conditional_or_missing** | `pending` | 0/0 | n/a/0 | n/a | `benchmark/tuvi_golden_dataset/reports_final/31_prompt_generation_best_retrieval` |
| Targeted Hard-case Wave | **not_started** | `pending` | 0/4 | n/a/400 | n/a | `benchmark/tuvi_golden_dataset/reports_final/40_targeted_hard_cases` |

## 1. Experiment Inventory

| Phase | Config | Manifest | Config hash | Main variable | Items | Status |
|---|---|---|---|---|---|---|
| Chunking Strategy Ablation | `fixed_512_graph_sparse_rrf` | `configs/w6_abl_03_chunking_matrix.yaml` | `6b8250da09920192b47712fa7f04237d6cf4c7c1c37e85bd1e8d6dbaac9cdb8a` | chunk=chunk_fixed_512 | 100 | **completed** |
| Chunking Strategy Ablation | `parent_child_graph_sparse_rrf` | `configs/w6_abl_03_chunking_matrix.yaml` | `39be6f7d0e9a354361665e8d79ef1db47cb7b73826414aef0e96726d75938dfa` | chunk=chunk_structure_parent_child | 100 | **completed** |
| Chunking Strategy Ablation | `semantic_bge_m3_graph_sparse_rrf` | `configs/w6_abl_03_chunking_matrix.yaml` | `c6e72838cb37a55ea68dcdf3a3016d1b3e2bb5a133800423196bacc0fda2c195` | chunk=chunk_semantic_embedding_bge_m3 | 100 | **completed** |
| Chunking × Prompt Interaction (v1/v2) | `fixed_512_prompt_v1_graph_sparse_rrf` | `configs/w8_abl_02_chunking_prompt_interaction_v1_v2.yaml` | `cda88b946b27fe8d4b0a1947454e02621f376fbd6db7e2ea79bb9755f4ac7b09` | chunk=chunk_fixed_512; prompt=tuvi_generation_v1 | 100 | **completed** |
| Chunking × Prompt Interaction (v1/v2) | `parent_child_prompt_v1_graph_sparse_rrf` | `configs/w8_abl_02_chunking_prompt_interaction_v1_v2.yaml` | `fc2cbcc5af8bc07634b52e6c36087a234dbfaeaad9ed955fe54c56852060ec9d` | chunk=chunk_structure_parent_child; prompt=tuvi_generation_v1 | 100 | **completed** |
| Chunking × Prompt Interaction (v1/v2) | `semantic_bge_m3_prompt_v1_graph_sparse_rrf` | `configs/w8_abl_02_chunking_prompt_interaction_v1_v2.yaml` | `2f4353b8d817c3619a12f5a2fd209f281dcd075f55ada652d88c5c66b165bf79` | chunk=chunk_semantic_embedding_bge_m3; prompt=tuvi_generation_v1 | 100 | **completed** |
| Chunking × Prompt Interaction (v1/v2) | `fixed_512_prompt_v2_graph_sparse_rrf` | `configs/w8_abl_02_chunking_prompt_interaction_v1_v2.yaml` | `b5a585b4555e727b4b2d1d49f4cfbd06a4f1af4aaa5f8db278682c2a4aaee943` | chunk=chunk_fixed_512; prompt=tuvi_generation_grounded_v2 | 100 | **completed** |
| Chunking × Prompt Interaction (v1/v2) | `parent_child_prompt_v2_graph_sparse_rrf` | `configs/w8_abl_02_chunking_prompt_interaction_v1_v2.yaml` | `e161a00da5776cc7996e6b66ece820e1f4b10161e91dbaaba1013ab1b67794b3` | chunk=chunk_structure_parent_child; prompt=tuvi_generation_grounded_v2 | 100 | **completed** |
| Chunking × Prompt Interaction (v1/v2) | `semantic_bge_m3_prompt_v2_graph_sparse_rrf` | `configs/w8_abl_02_chunking_prompt_interaction_v1_v2.yaml` | `11674749195729f664e1935e79a47f819cabf0d5aa18c59a5d13da7b03d3f0f6` | chunk=chunk_semantic_embedding_bge_m3; prompt=tuvi_generation_grounded_v2 | 100 | **completed** |
| Retrieval / Fusion / Reranker Matrix v2 | `baseline_graph_sparse_rrf` | `configs/w8_abl_01_retrieval_matrix_v2.yaml` | `627c79c1a041e10e04f29fdad8eebaa1073d7a819bb5d735b0a5258104423943` | paths=GS; fusion=rrf; rerank=yes | 100 | **not_started** |
| Retrieval / Fusion / Reranker Matrix v2 | `graph_only_rrf` | `configs/w8_abl_01_retrieval_matrix_v2.yaml` | `2ba12da545db12a3e7195260afc9c171ccaa22cedf8e54ad213df64956e11743` | paths=G; fusion=rrf; rerank=yes | 100 | **not_started** |
| Retrieval / Fusion / Reranker Matrix v2 | `sparse_only_rrf` | `configs/w8_abl_01_retrieval_matrix_v2.yaml` | `305287d273a12e8e7b38b7a54f307a76bb656645a8846c3b3da59060c0173683` | paths=S; fusion=rrf; rerank=yes | 100 | **not_started** |
| Retrieval / Fusion / Reranker Matrix v2 | `dense_only_rrf` | `configs/w8_abl_01_retrieval_matrix_v2.yaml` | `bde1c6dca9b34383234564753adc6bb2394589530a4cae78045165a3d76ab3a2` | paths=D; fusion=rrf; rerank=yes | 100 | **not_started** |
| Retrieval / Fusion / Reranker Matrix v2 | `dense_sparse_rrf` | `configs/w8_abl_01_retrieval_matrix_v2.yaml` | `c801bd9b3dcd211b5b580d1d1832bb122a1fce5daf4f8d2cad33dc9c759bc2d2` | paths=DS; fusion=rrf; rerank=yes | 100 | **not_started** |
| Retrieval / Fusion / Reranker Matrix v2 | `graph_dense_rrf` | `configs/w8_abl_01_retrieval_matrix_v2.yaml` | `155aa01c9275b6fe8af34bd9f839052041811c145b00c24ade1e0d81305b7fc5` | paths=GD; fusion=rrf; rerank=yes | 100 | **not_started** |
| Retrieval / Fusion / Reranker Matrix v2 | `all_paths_planner_dense_rrf` | `configs/w8_abl_01_retrieval_matrix_v2.yaml` | `826da9182fa625efeddcd0b98d06f2bfb1d49499d7c4a90cb5e32ce151efb6a5` | paths=GDS; fusion=rrf; rerank=yes | 100 | **not_started** |
| Retrieval / Fusion / Reranker Matrix v2 | `baseline_no_reranker` | `configs/w8_abl_01_retrieval_matrix_v2.yaml` | `eb65d183e8a38286e52fd75ca9ac1b7117c70273554e94c125fd9de588251bf7` | paths=GS; fusion=rrf; rerank=no | 100 | **not_started** |
| Retrieval / Fusion / Reranker Matrix v2 | `baseline_weighted_sum` | `configs/w8_abl_01_retrieval_matrix_v2.yaml` | `db9038d4fabf98a17a8db3259a94c811373a447c3d4db907efc8f8706a7f4d6d` | paths=GS; fusion=weighted_sum; rerank=yes | 100 | **not_started** |
| Retrieval / Fusion / Reranker Matrix v2 | `baseline_graph_first` | `configs/w8_abl_01_retrieval_matrix_v2.yaml` | `0bb737b18f6627e617d80b2d65a28f589ced3725365e84e37825439fb7f3cb0b` | paths=GS; fusion=graph_first; rerank=yes | 100 | **not_started** |
| Prompt / Generation Ablation on Current Retrieval | `baseline_v1_flash_lite` | `configs/w7_abl_01_generation_prompt_matrix.yaml` | `db5251237290acbf3567a6c1da1ad4979a2d703e2c0b24a7de2d2ad972e655c3` | prompt=tuvi_generation_v1; model=gemini-3.1-flash-lite-preview | 100 | **not_started** |
| Prompt / Generation Ablation on Current Retrieval | `grounded_v2_flash_lite` | `configs/w7_abl_01_generation_prompt_matrix.yaml` | `3974b524b0f763262121715fd61e0d0374fdd6e42c72003941f69418139434e4` | prompt=tuvi_generation_grounded_v2; model=gemini-3.1-flash-lite-preview | 100 | **not_started** |
| Prompt / Generation Ablation on Current Retrieval | `structured_v3_flash_lite` | `configs/w7_abl_01_generation_prompt_matrix.yaml` | `c099aacc105da68acba15b06bb08fd456f3320f5d222350cd50a71a67deca2fe` | prompt=tuvi_generation_structured_v3; model=gemini-3.1-flash-lite-preview | 100 | **not_started** |
| Prompt / Generation Ablation on Best Retrieval | n/a | `configs/w8_abl_02_prompt_matrix_on_best_retrieval.yaml` | n/a | manifest_missing | n/a | **conditional_or_missing** |
| Targeted Hard-case Wave | `sparse_only_rrf` | `configs/w8_abl_01_priority_wave.yaml` | `305287d273a12e8e7b38b7a54f307a76bb656645a8846c3b3da59060c0173683` | paths=S; fusion=rrf; rerank=yes | 100 | **not_started** |
| Targeted Hard-case Wave | `dense_sparse_rrf` | `configs/w8_abl_01_priority_wave.yaml` | `c801bd9b3dcd211b5b580d1d1832bb122a1fce5daf4f8d2cad33dc9c759bc2d2` | paths=DS; fusion=rrf; rerank=yes | 100 | **not_started** |
| Targeted Hard-case Wave | `baseline_no_reranker` | `configs/w8_abl_01_priority_wave.yaml` | `eb65d183e8a38286e52fd75ca9ac1b7117c70273554e94c125fd9de588251bf7` | paths=GS; fusion=rrf; rerank=no | 100 | **not_started** |
| Targeted Hard-case Wave | `baseline_weighted_sum` | `configs/w8_abl_01_priority_wave.yaml` | `db9038d4fabf98a17a8db3259a94c811373a447c3d4db907efc8f8706a7f4d6d` | paths=GS; fusion=weighted_sum; rerank=yes | 100 | **not_started** |

## 2. Metric Tables

### Chunking Strategy Ablation

| Rank | Config | Score | Main variable | Faith | Relev | CtxRecall | GraphHit | Citation | RAG p95 ms | Retr p95 ms | Gen p95 ms |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `parent_child_graph_sparse_rrf` | 0.749 | chunk=chunk_structure_parent_child | 0.900 | 0.799 | 0.714 | 0.967 | 0.989 | 123459.1 | 118592.8 | 5595.9 |
| 2 | `fixed_512_graph_sparse_rrf` | 0.748 | chunk=chunk_fixed_512 | 0.894 | 0.794 | 0.718 | 0.967 | 0.989 | 207600.5 | 199379.7 | 8124.1 |
| 3 | `semantic_bge_m3_graph_sparse_rrf` | 0.738 | chunk=chunk_semantic_embedding_bge_m3 | 0.889 | 0.779 | 0.699 | 0.967 | 0.989 | 168386.9 | 163092.5 | 5686.5 |

### Chunking × Prompt Interaction (v1/v2)

| Rank | Config | Score | Main variable | Faith | Relev | CtxRecall | GraphHit | Citation | RAG p95 ms | Retr p95 ms | Gen p95 ms |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `semantic_bge_m3_prompt_v1_graph_sparse_rrf` | 0.737 | chunk=chunk_semantic_embedding_bge_m3; prompt=tuvi_generation_v1 | 0.872 | 0.782 | 0.706 | 0.967 | 0.986 | 166491.8 | 163307.5 | 6047.2 |
| 2 | `fixed_512_prompt_v1_graph_sparse_rrf` | 0.726 | chunk=chunk_fixed_512; prompt=tuvi_generation_v1 | 0.880 | 0.770 | 0.667 | 0.967 | 0.992 | 181525.3 | 178549.3 | 4799.7 |
| 3 | `parent_child_prompt_v1_graph_sparse_rrf` | 0.723 | chunk=chunk_structure_parent_child; prompt=tuvi_generation_v1 | 0.878 | 0.763 | 0.663 | 0.967 | 0.995 | 119401.3 | 115384.2 | 4461.3 |
| 4 | `semantic_bge_m3_prompt_v2_graph_sparse_rrf` | 0.709 | chunk=chunk_semantic_embedding_bge_m3; prompt=tuvi_generation_grounded_v2 | 0.870 | 0.736 | 0.638 | 0.967 | 0.997 | 164979.5 | 161562.3 | 4833.3 |
| 5 | `parent_child_prompt_v2_graph_sparse_rrf` | 0.697 | chunk=chunk_structure_parent_child; prompt=tuvi_generation_grounded_v2 | 0.859 | 0.715 | 0.620 | 0.967 | 0.997 | 100804.9 | 96942.6 | 4512.1 |
| 6 | `fixed_512_prompt_v2_graph_sparse_rrf` | 0.671 | chunk=chunk_fixed_512; prompt=tuvi_generation_grounded_v2 | 0.813 | 0.683 | 0.584 | 0.967 | 0.997 | 147154.6 | 143860.4 | 4427.7 |

### Retrieval / Fusion / Reranker Matrix v2

No completed `evaluation_report.json` yet. Current status: **not_started**; checkpoint processed n/a/1000 pairs.

### Prompt / Generation Ablation on Current Retrieval

No completed `evaluation_report.json` yet. Current status: **not_started**; checkpoint processed n/a/300 pairs.

### Prompt / Generation Ablation on Best Retrieval

No completed `evaluation_report.json` yet. Current status: **conditional_or_missing**; checkpoint processed n/a/0 pairs.

### Targeted Hard-case Wave

No completed `evaluation_report.json` yet. Current status: **not_started**; checkpoint processed n/a/400 pairs.

## 3. Winners by Axis

| Axis | Winner | Evidence / interpretation |
|---|---|---|
| Best chunking strategy | `parent_child_graph_sparse_rrf` (score=0.749) | Chosen by the report heuristic over Context Recall, Faithfulness, Relevancy, Citation Coverage, Graph Hit and p95 latency. |
| Best chunking × prompt interaction | `semantic_bge_m3_prompt_v1_graph_sparse_rrf` (score=0.737) | chunk=chunk_semantic_embedding_bge_m3; prompt=tuvi_generation_v1; do not interpret as chunking-only or prompt-only evidence. |
| Best retrieval path combination | pending | pending |
| Best fusion method | pending | Derived from the Phase 3 winning config; compare RRF vs weighted_sum vs graph_first in the Phase 3 table. |
| Reranker on/off | pending | Derived from baseline vs `baseline_no_reranker` once Phase 3 is complete. |
| Best prompt template | pending | Prompt phase source: `prompt_generation_best_retrieval`. |

## 4. Winners by Question Family

### Chunking Strategy Ablation

| Family | Winner | Score | Items | Faith | Relev | CtxRecall | GraphHit | Citation | Retr p95 ms |
|---|---|---|---|---|---|---|---|---|---|
| core_identity | `parent_child_graph_sparse_rrf` | 0.622 | 10 | 1.000 | 0.850 | 0.700 | 0.000 | 0.000 | 0.2 |
| menh_house_interpretation | `parent_child_graph_sparse_rrf` | 0.714 | 10 | 0.880 | 0.720 | 0.680 | 0.900 | 1.000 | 126343.1 |
| than_cu_interpretation | `fixed_512_graph_sparse_rrf` | 0.833 | 10 | 0.950 | 0.910 | 0.870 | 1.000 | 1.000 | 179023.0 |
| menh_cuc_relation | `semantic_bge_m3_graph_sparse_rrf` | 0.868 | 10 | 1.000 | 0.930 | 0.940 | 1.000 | 1.000 | 100384.5 |
| special_state_interpretation | `fixed_512_graph_sparse_rrf` | 0.755 | 10 | 0.920 | 0.790 | 0.710 | 1.000 | 1.000 | 208271.8 |
| menh_tam_hop | `semantic_bge_m3_graph_sparse_rrf` | 0.739 | 10 | 0.900 | 0.790 | 0.670 | 1.000 | 1.000 | 160919.1 |
| menh_xung_chieu | `parent_child_graph_sparse_rrf` | 0.723 | 10 | 0.840 | 0.770 | 0.670 | 1.000 | 1.000 | 102210.9 |
| dai_van_interpretation | `fixed_512_graph_sparse_rrf` | 0.713 | 10 | 0.880 | 0.710 | 0.650 | 1.000 | 1.000 | 176186.9 |
| topic_house_plus_relations | `parent_child_graph_sparse_rrf` | 0.847 | 10 | 0.980 | 0.920 | 0.890 | 1.000 | 1.000 | 112981.8 |
| synthesis_judgement | `semantic_bge_m3_graph_sparse_rrf` | 0.729 | 10 | 0.890 | 0.770 | 0.690 | 0.900 | 1.000 | 204929.6 |

### Chunking × Prompt Interaction (v1/v2)

| Family | Winner | Score | Items | Faith | Relev | CtxRecall | GraphHit | Citation | Retr p95 ms |
|---|---|---|---|---|---|---|---|---|---|
| core_identity | `parent_child_prompt_v1_graph_sparse_rrf` | 0.733 | 10 | 1.000 | 0.840 | 0.700 | 0.000 | 0.750 | 0.2 |
| menh_house_interpretation | `fixed_512_prompt_v1_graph_sparse_rrf` | 0.704 | 10 | 0.920 | 0.720 | 0.620 | 0.900 | 1.000 | 184683.4 |
| than_cu_interpretation | `semantic_bge_m3_prompt_v1_graph_sparse_rrf` | 0.851 | 10 | 0.940 | 0.920 | 0.930 | 1.000 | 1.000 | 158771.9 |
| menh_cuc_relation | `parent_child_prompt_v1_graph_sparse_rrf` | 0.867 | 10 | 1.000 | 0.940 | 0.930 | 1.000 | 1.000 | 66262.5 |
| special_state_interpretation | `fixed_512_prompt_v1_graph_sparse_rrf` | 0.739 | 10 | 0.830 | 0.790 | 0.730 | 1.000 | 0.975 | 157319.3 |
| menh_tam_hop | `semantic_bge_m3_prompt_v1_graph_sparse_rrf` | 0.717 | 10 | 0.920 | 0.770 | 0.610 | 1.000 | 0.975 | 175353.5 |
| menh_xung_chieu | `parent_child_prompt_v1_graph_sparse_rrf` | 0.678 | 10 | 0.810 | 0.680 | 0.600 | 1.000 | 1.000 | 83868.5 |
| dai_van_interpretation | `fixed_512_prompt_v2_graph_sparse_rrf` | 0.713 | 10 | 0.870 | 0.720 | 0.650 | 1.000 | 1.000 | 107958.8 |
| topic_house_plus_relations | `parent_child_prompt_v1_graph_sparse_rrf` | 0.812 | 10 | 0.960 | 0.870 | 0.820 | 1.000 | 1.000 | 107460.2 |
| synthesis_judgement | `fixed_512_prompt_v1_graph_sparse_rrf` | 0.757 | 10 | 0.910 | 0.840 | 0.723 | 0.900 | 1.000 | 209725.7 |

### Retrieval / Fusion / Reranker Matrix v2

Pending: no completed report yet for this phase (`not_started`).

### Prompt / Generation Ablation on Current Retrieval

Pending: no completed report yet for this phase (`not_started`).

### Prompt / Generation Ablation on Best Retrieval

Pending: no completed report yet for this phase (`conditional_or_missing`).

### Targeted Hard-case Wave

Pending: no completed report yet for this phase (`not_started`).

## 5. Winners by Question Complexity

### Chunking Strategy Ablation

| Complexity | Winner | Score | Items | Faith | Relev | CtxRecall | Citation | Retr p95 ms |
|---|---|---|---|---|---|---|---|---|
| Direct | `parent_child_graph_sparse_rrf` | 0.622 | 10 | 1.000 | 0.850 | 0.700 | 0.000 | 0.2 |
| One-hop | `fixed_512_graph_sparse_rrf` | 0.765 | 46 | 0.911 | 0.800 | 0.750 | 1.000 | 192412.7 |
| Two-hop | `parent_child_graph_sparse_rrf` | 0.744 | 44 | 0.886 | 0.789 | 0.705 | 1.000 | 125391.6 |

### Chunking × Prompt Interaction (v1/v2)

| Complexity | Winner | Score | Items | Faith | Relev | CtxRecall | Citation | Retr p95 ms |
|---|---|---|---|---|---|---|---|---|
| Direct | `parent_child_prompt_v1_graph_sparse_rrf` | 0.733 | 10 | 1.000 | 0.840 | 0.700 | 0.750 | 0.2 |
| One-hop | `semantic_bge_m3_prompt_v1_graph_sparse_rrf` | 0.749 | 46 | 0.870 | 0.780 | 0.739 | 0.995 | 159023.4 |
| Two-hop | `semantic_bge_m3_prompt_v1_graph_sparse_rrf` | 0.719 | 44 | 0.850 | 0.759 | 0.673 | 0.983 | 176387.6 |

## 6. Research/Eval Candidate

Candidate selection is **pending** until the core full runs finish.
- chunking phase: `completed`
- retrieval/fusion/reranker phase: `not_started`
- prompt phase: `conditional_or_missing`
- Do not overwrite `configs/default_production.yaml`; create `configs/eval_candidate_v3.yaml` once winners are known.

## 7. Next Steps / Resume Commands

Launch Phase 3 after reviewing Phase 2 winner:

```powershell
$env:PYTHONPATH='backend'
.\.venv\Scripts\python.exe scripts\run_eval.py `
  --manifest configs/w8_abl_01_retrieval_matrix_v2.yaml `
  --judge-backend gemini `
  --skip-persistence `
  --checkpoint-dir benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/checkpoints `
  --output-dir benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix
```

Re-run this report builder after each phase completes:

```powershell
$env:PYTHONPATH='backend'
.\.venv\Scripts\python.exe scripts\build_final_ablation_report.py
```
