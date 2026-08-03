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