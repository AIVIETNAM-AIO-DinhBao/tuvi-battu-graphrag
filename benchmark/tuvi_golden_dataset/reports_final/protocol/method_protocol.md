# Full Ablation Frozen Method Protocol

Frozen before launching live ablation waves on 2026-07-28. Deploy/production operations are out of scope.

## Scope

- Dataset: `benchmark/tuvi_golden_dataset/release/tuviqa_v1_release.jsonl` with 100 ordered items.
- Corpus runtime: Neo4j corpus should cover 4 sources `TVKL`, `TVNL`, `TVHS`, `TVGM` across 3 chunk strategies.
- Judge backend for official conclusions: `gemini`. `static`/`offline-smoke` is preflight only.
- Supabase `experiment_runs`: skipped by default with `--skip-persistence`; local report/checkpoint artifacts are source of truth.
- Checkpoint/resume is mandatory for full live waves.

## Ablation axes

1. Chunking strategy ablation: `configs/w6_abl_03_chunking_matrix.yaml`, 3 configs x 100 items = 300 pairs.
2. Retrieval / fusion / reranker matrix: `configs/w8_abl_01_retrieval_matrix_v2.yaml`, 10 configs x 100 items = 1000 pairs.
3. Prompt / generation ablation: `configs/w7_abl_01_generation_prompt_matrix.yaml` or a v2 prompt matrix built on the Phase 3 retrieval winner, 3 configs x 100 items = 300 pairs.

## Validity gates

A wave is valid for analysis only if:

- expected config-item pair count completed, or checkpoint shows the exact resumed/completed set;
- no identity mismatch across resume;
- no retrieval backend fallback, generation backend fallback, or judge backend systemic failure;
- dataset SHA/config hashes/manifest fingerprint are recorded.

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

- Phase 4 prompt ablation should be run after Phase 3. If the retrieval winner differs from the default retrieval control in `w7_abl_01_generation_prompt_matrix.yaml`, create a new prompt-v2 manifest instead of mutating old results.
- Targeted hard-case wave is optional and diagnostic; it must not be pooled into full-100 aggregate metrics.
