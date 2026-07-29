# Full Ablation Run Registry

| Phase | Run key | Manifest | Output dir | Checkpoint dir | Pair count | Status | Notes |
|---|---|---|---|---|---:|---|---|
| 1 | preflight_tests | n/a | `benchmark/tuvi_golden_dataset/reports_final/00_preflight/logs` | n/a | n/a | pending | Backend regression subset. |
| 1 | preflight_gemini_probe | n/a | `benchmark/tuvi_golden_dataset/reports_final/00_preflight/logs` | n/a | n/a | pending | Probe `gemini-3.1-flash-lite-preview`. |
| 1 | preflight_neo4j_chunk_coverage | n/a | `benchmark/tuvi_golden_dataset/reports_final/00_preflight/neo4j_chunk_coverage` | n/a | 12 source-strategy pairs | pending | Requires 12/12 coverage. |
| 1 | preflight_chunking_smoke | `configs/w6_abl_03_chunking_matrix.yaml` | `benchmark/tuvi_golden_dataset/reports_final/00_preflight/smoke_chunking` | n/a | 3 x 2 = 6 | pending | Offline smoke only. |
| 1 | preflight_retrieval_smoke | `configs/w8_abl_01_retrieval_matrix_v2.yaml` | `benchmark/tuvi_golden_dataset/reports_final/00_preflight/smoke_retrieval_fusion_reranker` | n/a | 10 x 2 = 20 | pending | Offline smoke only. |
| 1 | preflight_prompt_smoke | `configs/w7_abl_01_generation_prompt_matrix.yaml` | `benchmark/tuvi_golden_dataset/reports_final/00_preflight/smoke_prompt_generation_current_retrieval` | n/a | 3 x 2 = 6 | pending | Offline smoke only. |
| 2 | full_chunking_strategy | `configs/w6_abl_03_chunking_matrix.yaml` | `benchmark/tuvi_golden_dataset/reports_final/10_chunking_strategy_ablation` | `.../checkpoints` | 3 x 100 = 300 | pending | Official Gemini judge. |
| 3 | full_retrieval_fusion_reranker | `configs/w8_abl_01_retrieval_matrix_v2.yaml` | `benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix` | `.../checkpoints` | 10 x 100 = 1000 | pending | Official Gemini judge. |
| 4A | full_prompt_generation_current | `configs/w7_abl_01_generation_prompt_matrix.yaml` | `benchmark/tuvi_golden_dataset/reports_final/30_prompt_generation_current_retrieval` | `.../checkpoints` | 3 x 100 = 300 | pending | Use only if retrieval control remains acceptable. |
| 4B | full_prompt_generation_best_retrieval | `configs/w8_abl_02_prompt_matrix_on_best_retrieval.yaml` | `benchmark/tuvi_golden_dataset/reports_final/31_prompt_generation_best_retrieval` | `.../checkpoints` | 3 x 100 = 300 | conditional | Create after Phase 3 if needed. |
| 5 | targeted_hard_cases | TBD / `configs/w8_abl_01_priority_wave.yaml` | `benchmark/tuvi_golden_dataset/reports_final/40_targeted_hard_cases` | `.../checkpoints` | TBD | optional | Diagnostic only. |
