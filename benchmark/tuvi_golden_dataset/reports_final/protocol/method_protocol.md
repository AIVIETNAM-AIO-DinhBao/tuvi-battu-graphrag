# Full Ablation Frozen Method Protocol

Frozen before launching live ablation waves on 2026-07-28. Updated on 2026-08-03 to reflect the completed Chunking × Prompt 3×3 factorial interpretation. Deploy/production operations are out of scope.

## Scope

- Dataset: `benchmark/tuvi_golden_dataset/release/tuviqa_v1_release.jsonl` with 100 ordered items.
- Corpus runtime: Neo4j corpus should cover 4 sources `TVKL`, `TVNL`, `TVHS`, `TVGM` across 3 chunk strategies.
- Judge backend for official conclusions: `gemini`. `static`/`offline-smoke` is preflight only.
- Supabase `experiment_runs`: skipped by default with `--skip-persistence`; local report/checkpoint artifacts are source of truth.
- Checkpoint/resume is mandatory for full live waves.

## Canonical ablation axes

1. **Chunking × Prompt factorial matrix**: completed canonical 3×3 study, `9 configs x 100 items = 900/900` official Gemini pairs.
   - Source wave A: `configs/w6_abl_03_chunking_matrix.yaml` → `reports_final/10_chunking_strategy_ablation`; 3 prompt-v3 cells.
   - Source wave B: `configs/w8_abl_02_chunking_prompt_interaction_v1_v2.yaml` → `reports_final/11_chunking_prompt_interaction_v1_v2`; 6 prompt-v1/v2 cells.
   - Interpretation rule: these are source waves of one study, not two separate final ablation studies.
2. **Retrieval / fusion / reranker matrix**: `configs/w8_abl_01_retrieval_matrix_v2.yaml`, `10 configs x 100 items = 1000 pairs`; active remaining matrix. It may be executed as three config shards under `20_retrieval_fusion_reranker_matrix/shards/`, then merged into the canonical root report with `scripts/merge_w8_retrieval_shards.py`.
3. **Targeted hard-case diagnostics**: optional, not pooled into full-100 aggregate metrics.

## Validity gates

A wave is valid for analysis only if:

- expected config-item pair count completed, or checkpoint shows the exact resumed/completed set;
- no identity mismatch across resume;
- no retrieval backend fallback, generation backend fallback, or judge backend systemic failure;
- dataset SHA/config hashes/manifest fingerprint are recorded.

For sharded retrieval execution, each shard must also satisfy `judge_backend=gemini`, full assigned pair count, and `failed_pair_count=0`; the merged canonical report must contain exactly the 10 configs from `configs/w8_abl_01_retrieval_matrix_v2.yaml` in canonical manifest order, with no duplicate or missing config.

## Main metrics

- Faithfulness
- Answer Relevancy
- Context Recall
- Graph Hit Rate
- Citation Coverage
- RAG p95
- Retrieval p95
- Generation p95

Break down by `question_complexity` and `question_family`.

## Analysis decisions

- Completed source waves `10_...` and `11_...` must be synthesized as the 3×3 Chunking × Prompt matrix.
- Retrieval/fusion/reranker conclusions require the active full matrix under `reports_final/20_retrieval_fusion_reranker_matrix`.
- Targeted hard-case wave is optional and diagnostic; it must not be pooled into full-100 aggregate metrics.