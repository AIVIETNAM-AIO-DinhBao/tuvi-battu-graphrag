# Canonical Full Ablation Run Registry

Interpretation rule: `10_chunking_strategy_ablation` and `11_chunking_prompt_interaction_v1_v2` are immutable source waves for one completed **Chunking × Prompt 3×3 factorial matrix**. They must not be interpreted as two separate final ablation studies.

| Phase | Run key | Manifest | Output dir | Checkpoint dir | Pair count | Status | Notes |
|---|---|---|---|---|---:|---|---|
| 1 | preflight_tests | n/a | `benchmark/tuvi_golden_dataset/reports_final/00_preflight/logs` | n/a | n/a | completed | `111 passed, 1 warning`; 2026-07-28. |
| 1 | preflight_gemini_probe | n/a | `benchmark/tuvi_golden_dataset/reports_final/00_preflight/logs` | n/a | n/a | completed | `gemini-3.1-flash-lite-preview`; keys `4/4` OK; 2026-07-28. |
| 1 | preflight_neo4j_chunk_coverage | n/a | `benchmark/tuvi_golden_dataset/reports_final/00_preflight/neo4j_chunk_coverage` | n/a | 12 source-strategy pairs | completed | Neo4j coverage `12/12`, missing `0`; 2026-07-28. |
| 1 | preflight_chunking_smoke | `configs/w6_abl_03_chunking_matrix.yaml` | `benchmark/tuvi_golden_dataset/reports_final/00_preflight/smoke_chunking` | n/a | 3 x 2 = 6 | completed | Static-smoke preflight only; `6/6`; 2026-07-28. |
| 1 | preflight_retrieval_smoke | `configs/w8_abl_01_retrieval_matrix_v2.yaml` | `benchmark/tuvi_golden_dataset/reports_final/00_preflight/smoke_retrieval_fusion_reranker` | n/a | 10 x 2 = 20 | completed | Static-smoke preflight only; `20/20`; 2026-07-28. |
| 2A | chunking_prompt_matrix_source_v3 | `configs/w6_abl_03_chunking_matrix.yaml` | `benchmark/tuvi_golden_dataset/reports_final/10_chunking_strategy_ablation` | `.../checkpoints` | 3 x 100 = 300 | completed | Official Gemini judge; `300/300`, failed `0`; 2026-07-28. Contains the 3 prompt-v3 cells of the canonical 3×3 matrix. |
| 2B | chunking_prompt_matrix_source_v1_v2 | `configs/w8_abl_02_chunking_prompt_interaction_v1_v2.yaml` | `benchmark/tuvi_golden_dataset/reports_final/11_chunking_prompt_interaction_v1_v2` | `.../checkpoints` | 6 x 100 = 600 | completed | Official Gemini judge; `600/600`, failed `0`. Contains the 6 prompt-v1/v2 cells of the canonical 3×3 matrix. |
| 2 | canonical_chunking_prompt_factorial_matrix | source waves `2A + 2B` | `10_... + 11_...` | source checkpoints | 9 x 100 = 900 | completed | Canonical completed Chunking × Prompt 3×3 factorial study. |
| 3 | full_retrieval_fusion_reranker | `configs/w8_abl_01_retrieval_matrix_v2.yaml` | `benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix` | `.../checkpoints` | 10 x 100 = 1000 | pending | Active remaining official Gemini comparative matrix. |
| optional | targeted_hard_cases | TBD / `configs/w8_abl_01_priority_wave.yaml` | `benchmark/tuvi_golden_dataset/reports_final/40_targeted_hard_cases` | `.../checkpoints` | TBD | optional | Diagnostic only; does not block final comparative status. |