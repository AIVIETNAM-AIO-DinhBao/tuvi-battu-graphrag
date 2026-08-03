# Canonical Full Ablation Plan

This plan defines the active comparative ablation scope for `benchmark/tuvi_golden_dataset/reports_final/`.

## Active scope

- Preflight local gates: backend regression subset, Gemini probe, Neo4j source/strategy coverage, and static smoke for active manifests.
- Completed Chunking × Prompt factorial matrix on `benchmark/tuvi_golden_dataset/release/tuviqa_v1_release.jsonl`: `3 chunking strategies × 3 prompt templates × 100 QA = 900/900` official Gemini pairs.
- Active remaining retrieval/fusion/reranker matrix with checkpoint/resume: `configs/w8_abl_01_retrieval_matrix_v2.yaml`.
- Optional targeted hard-case diagnostics after full-matrix failure review; diagnostics are not pooled into the full-100 aggregate metrics.
- Final comparative report: `evaluation/ablation_final_report.md` and snapshot `benchmark/tuvi_golden_dataset/reports_final/90_final_report/`.

## Canonical interpretation

- `reports_final/10_chunking_strategy_ablation` is source wave A and contains the 3 prompt-v3 cells.
- `reports_final/11_chunking_prompt_interaction_v1_v2` is source wave B and contains the 6 prompt-v1/v2 cells.
- Together, source waves A+B are one completed **Chunking × Prompt 3×3 factorial matrix**, not two separate studies.
- No separate prompt/generation phase is active for the current study; prompt evidence is already represented inside the completed 3×3 matrix.

## Execution order

1. Keep the protocol files in `benchmark/tuvi_golden_dataset/reports_final/protocol/` as the source of truth.
2. Do not rerun completed source waves unless a material artifact/config/environment change invalidates them.
3. Run or resume the retrieval/fusion/reranker matrix:

   ```powershell
   $env:PYTHONPATH='backend'
   .\.venv\Scripts\python.exe scripts\run_eval.py `
     --manifest configs/w8_abl_01_retrieval_matrix_v2.yaml `
     --judge-backend gemini `
     --skip-persistence `
     --checkpoint-dir benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/checkpoints `
     --output-dir benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix `
     --max-item-attempts 2 `
     --retry-base-seconds 2
   ```

   If interrupted, append `--resume --retry-failed`.

4. Rebuild the final comparative report after each completed or resumed wave:

   ```powershell
   $env:PYTHONPATH='backend'
   .\.venv\Scripts\python.exe scripts\build_final_ablation_report.py
   ```

5. If a research/eval candidate is needed after evidence is complete, create a new candidate config such as `configs/eval_candidate_v3.yaml`; do not overwrite `configs/default_production.yaml`.