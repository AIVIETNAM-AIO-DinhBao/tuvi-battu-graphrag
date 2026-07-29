# Final Ablation Report

Status: **in_progress**
Generated UTC: `2026-07-28T14:24:50.364082+00:00`
Git SHA: `22ca387b11fec3b96a488fb42ed49a7cfc3b4d5e`
Git status: `M  backend/tests/test_experiment_config.py
M  backend/tests/test_rag_evaluation.py
M  backend/tests/test_rag_retrieval.py
A  benchmark/tuvi_golden_dataset/reports_final/00_preflight/logs/gemini_probe.log
A  benchmark/tuvi_golden_dataset/reports_final/00_preflight/logs/neo4j_chunk_coverage.log
A  benchmark/tuvi_golden_dataset/reports_final/00_preflight/logs/pytest_backend_subset.log
A  benchmark/tuvi_golden_dataset/reports_final/00_preflight/logs/smoke_chunking.log
A  benchmark/tuvi_golden_dataset/reports_final/00_preflight/logs/smoke_prompt_generation_current_retrieval.log
A  benchmark/tuvi_golden_dataset/reports_final/00_preflight/logs/smoke_retrieval_fusion_reranker.log
A  benchmark/tuvi_golden_dataset/reports_final/00_preflight/neo4j_chunk_coverage/chunk_strategy_coverage.json
A  benchmark/tuvi_golden_dataset/reports_final/00_preflight/neo4j_chunk_coverage/chunk_strategy_coverage.md
A  benchmark/tuvi_golden_dataset/reports_final/00_preflight/preflight_summary.json
A  benchmark/tuvi_golden_dataset/reports_final/00_preflight/preflight_summary.md
A  benchmark/tuvi_golden_dataset/reports_final/00_preflight/smoke_chunking/evaluation_report.json
A  benchmark/tuvi_golden_dataset/reports_final/00_preflight/smoke_chunking/evaluation_report.md
A  benchmark/tuvi_golden_dataset/reports_final/00_preflight/smoke_prompt_generation_current_retrieval/evaluation_report.json
A  benchmark/tuvi_golden_dataset/reports_final/00_preflight/smoke_prompt_generation_current_retrieval/evaluation_report.md
A  benchmark/tuvi_golden_dataset/reports_final/00_preflight/smoke_retrieval_fusion_reranker/evaluation_report.json
A  benchmark/tuvi_golden_dataset/reports_final/00_preflight/smoke_retrieval_fusion_reranker/evaluation_report.md
A  benchmark/tuvi_golden_dataset/reports_final/PLAN.md
A  benchmark/tuvi_golden_dataset/reports_final/README.md
A  benchmark/tuvi_golden_dataset/reports_final/protocol/commands.md
A  benchmark/tuvi_golden_dataset/reports_final/protocol/identity.json
A  benchmark/tuvi_golden_dataset/reports_final/protocol/method_protocol.md
A  benchmark/tuvi_golden_dataset/reports_final/protocol/run_registry.md
A  scripts/build_preflight_summary.py
?? benchmark/tuvi_golden_dataset/reports_final/10_chunking_strategy_ablation/
?? scripts/build_final_ablation_report.py
?? scripts/watch_eval_run.py`

## Dataset / Identity

| Dataset | Items | SHA256 |
|---|---:|---|
| `benchmark/tuvi_golden_dataset/release/tuviqa_v1_release.jsonl` | 100 | `90376a87cec29cc22e93dc71b41e054ed2f0183bc515a52aa461fecd43cc008c` |

Notes:
- Official conclusion rows require `judge_backend=gemini`; offline smoke is not used as final evidence.
- Supabase persistence is intentionally non-blocking; local artifacts and checkpoints are the source of truth.
- `Score` is a transparent report heuristic for ranking only, not a replacement for individual metrics.

## Run Status

| Phase | Status | Judge | Configs | Pairs processed/expected | Current | Output |
|---|---|---|---|---|---|---|
| Chunking Strategy Ablation | **in_progress** | `pending` | 0/3 | 13/300 | fixed_512_graph_sparse_rrf / TVQA-013 | `benchmark/tuvi_golden_dataset/reports_final/10_chunking_strategy_ablation` |
| Retrieval / Fusion / Reranker Matrix v2 | **not_started** | `pending` | 0/10 | n/a/1000 | n/a | `benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix` |
| Prompt / Generation Ablation on Current Retrieval | **not_started** | `pending` | 0/3 | n/a/300 | n/a | `benchmark/tuvi_golden_dataset/reports_final/30_prompt_generation_current_retrieval` |
| Prompt / Generation Ablation on Best Retrieval | **conditional_or_missing** | `pending` | 0/0 | n/a/0 | n/a | `benchmark/tuvi_golden_dataset/reports_final/31_prompt_generation_best_retrieval` |
| Targeted Hard-case Wave | **not_started** | `pending` | 0/4 | n/a/400 | n/a | `benchmark/tuvi_golden_dataset/reports_final/40_targeted_hard_cases` |

## 1. Experiment Inventory

| Phase | Config | Manifest | Config hash | Main variable | Items | Status |
|---|---|---|---|---|---|---|
| Chunking Strategy Ablation | `fixed_512_graph_sparse_rrf` | `configs/w6_abl_03_chunking_matrix.yaml` | `6b8250da09920192b47712fa7f04237d6cf4c7c1c37e85bd1e8d6dbaac9cdb8a` | chunk=chunk_fixed_512 | 100 | **in_progress** |
| Chunking Strategy Ablation | `parent_child_graph_sparse_rrf` | `configs/w6_abl_03_chunking_matrix.yaml` | `39be6f7d0e9a354361665e8d79ef1db47cb7b73826414aef0e96726d75938dfa` | chunk=chunk_structure_parent_child | 100 | **in_progress** |
| Chunking Strategy Ablation | `semantic_bge_m3_graph_sparse_rrf` | `configs/w6_abl_03_chunking_matrix.yaml` | `c6e72838cb37a55ea68dcdf3a3016d1b3e2bb5a133800423196bacc0fda2c195` | chunk=chunk_semantic_embedding_bge_m3 | 100 | **in_progress** |
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

No completed `evaluation_report.json` yet. Current status: **in_progress**; checkpoint processed 13/300 pairs.

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
| Best chunking strategy | pending | Chosen by the report heuristic over Context Recall, Faithfulness, Relevancy, Citation Coverage, Graph Hit and p95 latency. |
| Best retrieval path combination | pending | pending |
| Best fusion method | pending | Derived from the Phase 3 winning config; compare RRF vs weighted_sum vs graph_first in the Phase 3 table. |
| Reranker on/off | pending | Derived from baseline vs `baseline_no_reranker` once Phase 3 is complete. |
| Best prompt template | pending | Prompt phase source: `prompt_generation_best_retrieval`. |

## 4. Winners by Question Family

### Chunking Strategy Ablation

Pending: no completed report yet for this phase (`in_progress`).

### Retrieval / Fusion / Reranker Matrix v2

Pending: no completed report yet for this phase (`not_started`).

### Prompt / Generation Ablation on Current Retrieval

Pending: no completed report yet for this phase (`not_started`).

### Prompt / Generation Ablation on Best Retrieval

Pending: no completed report yet for this phase (`conditional_or_missing`).

### Targeted Hard-case Wave

Pending: no completed report yet for this phase (`not_started`).

## 5. Winners by Question Complexity

## 6. Research/Eval Candidate

Candidate selection is **pending** until the core full runs finish.
- chunking phase: `in_progress`
- retrieval/fusion/reranker phase: `not_started`
- prompt phase: `conditional_or_missing`
- Do not overwrite `configs/default_production.yaml`; create `configs/eval_candidate_v3.yaml` once winners are known.

## 7. Next Steps / Resume Commands

Phase 2 is currently in progress. Monitor:

```powershell
Get-Content -LiteralPath benchmark\tuvi_golden_dataset\reports_final\10_chunking_strategy_ablation\phase2_full_status_latest.json -Raw
```

If interrupted, resume:

```powershell
$env:PYTHONPATH='backend'
.\.venv\Scripts\python.exe scripts\run_eval.py `
  --manifest configs/w6_abl_03_chunking_matrix.yaml `
  --judge-backend gemini `
  --skip-persistence `
  --checkpoint-dir benchmark/tuvi_golden_dataset/reports_final/10_chunking_strategy_ablation/checkpoints `
  --output-dir benchmark/tuvi_golden_dataset/reports_final/10_chunking_strategy_ablation `
  --resume --retry-failed
```

Re-run this report builder after each phase completes:

```powershell
$env:PYTHONPATH='backend'
.\.venv\Scripts\python.exe scripts\build_final_ablation_report.py
```
