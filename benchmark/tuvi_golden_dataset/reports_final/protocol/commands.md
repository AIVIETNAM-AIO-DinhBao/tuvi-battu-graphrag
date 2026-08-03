# Full Ablation Execution Commands

All commands are Windows PowerShell commands from repository root. Production/deploy ops are intentionally excluded. Official runs use `--judge-backend gemini --skip-persistence` and local checkpoints.

## Interpretation rule

The completed Chunking × Prompt result is one canonical **3×3 factorial matrix**:

- Source wave A: `reports_final/10_chunking_strategy_ablation` contains the 3 prompt-v3 cells.
- Source wave B: `reports_final/11_chunking_prompt_interaction_v1_v2` contains the 6 prompt-v1/v2 cells.
- Together they equal `9 configs x 100 = 900/900` official Gemini pairs.

Do not treat source wave A as a separate final chunking study and source wave B as a separate supporting interaction study. Do not introduce a separate prompt/generation phase for the current completed 3×3 study.

## Phase 1 preflight, historical/completed

These commands are retained for reproducibility. Rerun only after material environment/configuration changes.

```powershell
$env:PYTHONPATH='backend'
.\.venv\Scripts\python.exe -m pytest `
  backend/tests/test_experiment_config.py `
  backend/tests/test_rag_evaluation.py `
  backend/tests/test_evaluation_checkpoint.py `
  backend/tests/test_evaluation_runner_resilience.py `
  backend/tests/test_run_eval_cli.py `
  backend/tests/test_rag_retrieval.py `
  backend/tests/test_rag_context_generation_citations.py `
  backend/tests/test_rag_planner.py `
  backend/tests/test_rag_chart_facts.py `
  -q -p no:cacheprovider
.\.venv\Scripts\python.exe scripts/check_gemini_api.py --model gemini-3.1-flash-lite-preview
.\.venv\Scripts\python.exe scripts/check_w6_abl_03_chunk_coverage.py --mode neo4j --output-dir benchmark/tuvi_golden_dataset/reports_final/00_preflight/neo4j_chunk_coverage
.\.venv\Scripts\python.exe scripts/run_eval.py --manifest configs/w6_abl_03_chunking_matrix.yaml --offline-smoke --limit 2 --skip-persistence --output-dir benchmark/tuvi_golden_dataset/reports_final/00_preflight/smoke_chunking
.\.venv\Scripts\python.exe scripts/run_eval.py --manifest configs/w8_abl_01_retrieval_matrix_v2.yaml --offline-smoke --limit 2 --skip-persistence --output-dir benchmark/tuvi_golden_dataset/reports_final/00_preflight/smoke_retrieval_fusion_reranker
```

## Phase 2A source wave, historical/completed: prompt-v3 cells

```powershell
$env:PYTHONPATH='backend'
.\.venv\Scripts\python.exe scripts/run_eval.py `
  --manifest configs/w6_abl_03_chunking_matrix.yaml `
  --judge-backend gemini `
  --skip-persistence `
  --checkpoint-dir benchmark/tuvi_golden_dataset/reports_final/10_chunking_strategy_ablation/checkpoints `
  --output-dir benchmark/tuvi_golden_dataset/reports_final/10_chunking_strategy_ablation `
  --max-item-attempts 2 `
  --retry-base-seconds 2
```

Resume historical source wave A only if its checkpoint/report is incomplete: append `--resume --retry-failed`.

## Phase 2B source wave, historical/completed: prompt-v1/v2 cells

```powershell
$env:PYTHONPATH='backend'
.\.venv\Scripts\python.exe scripts/run_eval.py `
  --manifest configs/w8_abl_02_chunking_prompt_interaction_v1_v2.yaml `
  --judge-backend gemini `
  --skip-persistence `
  --checkpoint-dir benchmark/tuvi_golden_dataset/reports_final/11_chunking_prompt_interaction_v1_v2/checkpoints `
  --output-dir benchmark/tuvi_golden_dataset/reports_final/11_chunking_prompt_interaction_v1_v2 `
  --max-item-attempts 2 `
  --retry-base-seconds 2
```

Resume historical source wave B only if its checkpoint/report is incomplete: append `--resume --retry-failed`.

## Phase 3 active: full retrieval/fusion/reranker matrix

Preferred multi-teammate execution uses config shards. Do **not** run multiple people into the canonical root output/checkpoint directory concurrently. Each teammate writes only their assigned shard directory; the main owner merges shards after all are complete.

### Phase 3A shard A: controls, fusion, reranker

Configs: `baseline_graph_sparse_rrf`, `baseline_no_reranker`, `baseline_weighted_sum`, `baseline_graph_first` (`4 x 100 = 400`).

```powershell
$env:PYTHONPATH='backend'
.\.venv\Scripts\python.exe scripts\run_eval.py `
  --manifest configs/w8_abl_01_retrieval_matrix_v2_shard_a_controls.yaml `
  --judge-backend gemini `
  --skip-persistence `
  --checkpoint-dir benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/shards/shard_a_controls/checkpoints `
  --output-dir benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/shards/shard_a_controls `
  --max-item-attempts 2 `
  --retry-base-seconds 2
```

Resume shard A: same command plus `--resume --retry-failed`.

### Phase 3B shard B: single retrieval paths

Configs: `graph_only_rrf`, `sparse_only_rrf`, `dense_only_rrf` (`3 x 100 = 300`).

```powershell
$env:PYTHONPATH='backend'
.\.venv\Scripts\python.exe scripts\run_eval.py `
  --manifest configs/w8_abl_01_retrieval_matrix_v2_shard_b_single_paths.yaml `
  --judge-backend gemini `
  --skip-persistence `
  --checkpoint-dir benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/shards/shard_b_single_paths/checkpoints `
  --output-dir benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/shards/shard_b_single_paths `
  --max-item-attempts 2 `
  --retry-base-seconds 2
```

Resume shard B: same command plus `--resume --retry-failed`.

### Phase 3C shard C: dense combinations

Configs: `dense_sparse_rrf`, `graph_dense_rrf`, `all_paths_planner_dense_rrf` (`3 x 100 = 300`).

```powershell
$env:PYTHONPATH='backend'
.\.venv\Scripts\python.exe scripts\run_eval.py `
  --manifest configs/w8_abl_01_retrieval_matrix_v2_shard_c_dense_combos.yaml `
  --judge-backend gemini `
  --skip-persistence `
  --checkpoint-dir benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/shards/shard_c_dense_combos/checkpoints `
  --output-dir benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/shards/shard_c_dense_combos `
  --max-item-attempts 2 `
  --retry-base-seconds 2
```

Resume shard C: same command plus `--resume --retry-failed`.

### Phase 3 merge shards into canonical report

Run only on `main` after all three shards report `status=completed`, `judge_backend=gemini`, `failed_pair_count=0`.

```powershell
$env:PYTHONPATH='backend'
.\.venv\Scripts\python.exe scripts\merge_w8_retrieval_shards.py
.\.venv\Scripts\python.exe scripts\build_final_ablation_report.py
Copy-Item evaluation\ablation_final_report.md benchmark\tuvi_golden_dataset\reports_final\90_final_report\ablation_final_report.md -Force
Copy-Item benchmark\tuvi_golden_dataset\reports_final\ablation_final_summary.json benchmark\tuvi_golden_dataset\reports_final\90_final_report\ablation_final_summary.json -Force
```

### Phase 3 single-run fallback

Use this only if one operator runs the whole 10-config matrix alone. Do not run it concurrently with shard runs.

```powershell
$env:PYTHONPATH='backend'
.\.venv\Scripts\python.exe scripts/run_eval.py `
  --manifest configs/w8_abl_01_retrieval_matrix_v2.yaml `
  --judge-backend gemini `
  --skip-persistence `
  --checkpoint-dir benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/checkpoints `
  --output-dir benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix `
  --max-item-attempts 2 `
  --retry-base-seconds 2
```

Resume: same command plus `--resume --retry-failed`.

## Rebuild final comparative report

```powershell
$env:PYTHONPATH='backend'
.\.venv\Scripts\python.exe scripts/build_final_ablation_report.py
```