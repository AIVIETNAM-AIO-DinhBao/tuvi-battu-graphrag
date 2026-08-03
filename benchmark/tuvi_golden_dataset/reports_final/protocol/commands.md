# Full Ablation Execution Commands

All commands are Windows PowerShell commands from repository root. Production/deploy ops are intentionally excluded. Official runs use `--judge-backend gemini --skip-persistence` and local checkpoints.

## Phase 1 preflight

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
.\.venv\Scripts\python.exe scripts/run_eval.py --manifest configs/w7_abl_01_generation_prompt_matrix.yaml --offline-smoke --limit 2 --skip-persistence --output-dir benchmark/tuvi_golden_dataset/reports_final/00_preflight/smoke_prompt_generation_current_retrieval
```

## Phase 2 full chunking

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

Resume: same command plus `--resume --retry-failed`.

## Phase 2B chunking × prompt interaction v1/v2

This supporting wave varies `chunk_strategy_id` and `prompt_template_id` jointly. Treat it as interaction evidence, not as a replacement for the single-axis chunking or prompt ablations.

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

Resume: same command plus `--resume --retry-failed`.

## Phase 3 full retrieval/fusion/reranker matrix

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

## Phase 4 prompt/generation

```powershell
$env:PYTHONPATH='backend'
.\.venv\Scripts\python.exe scripts/run_eval.py `
  --manifest configs/w7_abl_01_generation_prompt_matrix.yaml `
  --judge-backend gemini `
  --skip-persistence `
  --checkpoint-dir benchmark/tuvi_golden_dataset/reports_final/30_prompt_generation_current_retrieval/checkpoints `
  --output-dir benchmark/tuvi_golden_dataset/reports_final/30_prompt_generation_current_retrieval `
  --max-item-attempts 2 `
  --retry-base-seconds 2
```

If Phase 3 winner changes retrieval stack, create `configs/w8_abl_02_prompt_matrix_on_best_retrieval.yaml` and use `31_prompt_generation_best_retrieval/`.
