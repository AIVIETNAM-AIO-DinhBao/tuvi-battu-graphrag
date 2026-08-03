# Next-session Handoff — Canonical Full Ablation Track

Updated: `2026-08-03`  
Scope: comparative ablation evidence only. Deploy/production ops are out of scope.

## 1. Frozen identity

- Dataset: `benchmark/tuvi_golden_dataset/release/tuviqa_v1_release.jsonl`
- Dataset items: `100`
- Dataset SHA256: `90376a87cec29cc22e93dc71b41e054ed2f0183bc515a52aa461fecd43cc008c`
- Official judge: `gemini`
- Generation model in completed 3×3 cells: `gemini-3.1-flash-lite-preview`
- Persistence: `--skip-persistence`; local reports/checkpoints are source of truth
- Final comparative report: `evaluation/ablation_final_report.md`
- Machine-readable summary: `benchmark/tuvi_golden_dataset/reports_final/ablation_final_summary.json`

Do not mutate completed manifests/results. New controls require a new manifest and output directory.

## 2. Canonical completed evidence

### Chunking × Prompt factorial matrix — complete

The completed chunking/prompt evidence is **one canonical 3×3 factorial study**, not two separate ablation studies.

- Factors:
  - `chunk_strategy_id` in `{chunk_fixed_512, chunk_structure_parent_child, chunk_semantic_embedding_bge_m3}`
  - `prompt_template_id` in `{tuvi_generation_v1, tuvi_generation_grounded_v2, tuvi_generation_structured_v3}`
- Coverage: `9 configs x 100 = 900`; `900/900`; failed `0`
- Judge: `gemini`
- Retrieval control: Graph + Sparse + RRF + reranker; dense off; balanced context; document grading on

Source runs are preserved as immutable execution waves because they were run at different times:

| Source wave | Manifest | Output | Cells | Role |
|---|---|---|---:|---|
| Wave A | `configs/w6_abl_03_chunking_matrix.yaml` | `benchmark/tuvi_golden_dataset/reports_final/10_chunking_strategy_ablation` | 3 prompt-v3 cells | Source cells for the canonical 3×3 matrix |
| Wave B | `configs/w8_abl_02_chunking_prompt_interaction_v1_v2.yaml` | `benchmark/tuvi_golden_dataset/reports_final/11_chunking_prompt_interaction_v1_v2` | 6 prompt-v1/v2 cells | Source cells for the canonical 3×3 matrix |

Interpretation rule: **do not** describe Wave A as a final standalone chunking ablation and Wave B as a separate supporting prompt interaction. They are two execution waves that together form the completed Chunking × Prompt 3×3 study.

Current aggregate winner by report heuristic is `parent_child_graph_sparse_rrf` / `chunk_structure_parent_child` + `tuvi_generation_structured_v3`, but latency is very high and must be considered alongside quality.

## 3. Current state / remaining work

The comparative report remains **in_progress** only because retrieval/fusion/reranker has not been run. Prompt evidence for the current chunking/prompt study is already complete inside the 3×3 matrix.

| Work item | Status | Expected | Notes |
|---|---|---:|---|
| Preflight tests/probe/Neo4j/smoke | complete | n/a | `111 passed`; Gemini `4/4`; Neo4j `12/12`; smoke artifacts are static-smoke only |
| Chunking × Prompt 3×3 matrix | complete | 900 pairs | Canonical completed study, sourced from `10_...` + `11_...` |
| Retrieval/Fusion/Reranker v2 | not started | 1000 pairs | Active remaining comparative matrix |
| Targeted hard cases | optional; not started | diagnostic only | Run only after inspecting full matrix failures |

Primary remaining live work: `10 configs x 100 = 1000` pairs for retrieval/fusion/reranker. The preferred execution plan is split-by-config across three teammate shards, then merge into the canonical Phase 3 report on `main`.

## 4. Next session execution order

### Step 0 — Confirm frozen preflight, do not rerun completed waves blindly

Read `benchmark/tuvi_golden_dataset/reports_final/protocol/run_registry.md` and inspect `00_preflight/`.
Preflight completed on `2026-07-28`; rerun only after a material environment/configuration change.

### Step 1 — Run/resume retrieval/fusion/reranker matrix shards

Do not let multiple people write to the canonical root output/checkpoint directory concurrently. Each teammate writes only their assigned shard under `20_retrieval_fusion_reranker_matrix/shards/`.

| Shard | Manifest | Output dir | Configs | Expected |
|---|---|---|---|---:|
| A controls | `configs/w8_abl_01_retrieval_matrix_v2_shard_a_controls.yaml` | `.../shards/shard_a_controls` | baseline, no-reranker, weighted-sum, graph-first | 400 |
| B single paths | `configs/w8_abl_01_retrieval_matrix_v2_shard_b_single_paths.yaml` | `.../shards/shard_b_single_paths` | graph-only, sparse-only, dense-only | 300 |
| C dense combos | `configs/w8_abl_01_retrieval_matrix_v2_shard_c_dense_combos.yaml` | `.../shards/shard_c_dense_combos` | dense+sparse, graph+dense, all paths | 300 |

Shard A:

```powershell
$env:PYTHONPATH='backend'
.\.venv\Scripts\python.exe scripts/run_eval.py `
  --manifest configs/w8_abl_01_retrieval_matrix_v2_shard_a_controls.yaml `
  --judge-backend gemini `
  --skip-persistence `
  --checkpoint-dir benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/shards/shard_a_controls/checkpoints `
  --output-dir benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/shards/shard_a_controls `
  --max-item-attempts 2 `
  --retry-base-seconds 2
```

Shard B:

```powershell
$env:PYTHONPATH='backend'
.\.venv\Scripts\python.exe scripts/run_eval.py `
  --manifest configs/w8_abl_01_retrieval_matrix_v2_shard_b_single_paths.yaml `
  --judge-backend gemini `
  --skip-persistence `
  --checkpoint-dir benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/shards/shard_b_single_paths/checkpoints `
  --output-dir benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/shards/shard_b_single_paths `
  --max-item-attempts 2 `
  --retry-base-seconds 2
```

Shard C:

```powershell
$env:PYTHONPATH='backend'
.\.venv\Scripts\python.exe scripts/run_eval.py `
  --manifest configs/w8_abl_01_retrieval_matrix_v2_shard_c_dense_combos.yaml `
  --judge-backend gemini `
  --skip-persistence `
  --checkpoint-dir benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/shards/shard_c_dense_combos/checkpoints `
  --output-dir benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/shards/shard_c_dense_combos `
  --max-item-attempts 2 `
  --retry-base-seconds 2
```

Resume any shard after interruption/quota exhaustion: rerun its exact command and append `--resume --retry-failed`. Never delete shard checkpoints.

### Step 1b — Merge completed shards on `main`

Run only after all three shards have `status=completed`, `judge_backend=gemini`, `failed_pair_count=0`, and expected pair counts `400/300/300`.

```powershell
$env:PYTHONPATH='backend'
.\.venv\Scripts\python.exe scripts/merge_w8_retrieval_shards.py
```

The merge writes the canonical Phase 3 artifacts to:

- `benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/evaluation_report.json`
- `benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/evaluation_report.md`
- `benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/checkpoints/checkpoint_summary.json`

### Single-run fallback — only if one operator runs the full matrix

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

Resume after interruption/quota exhaustion: append `--resume --retry-failed`. Never delete checkpoints. Do not use the single-run fallback concurrently with shard runs.

Expected canonical total after merge: `10 configs x 100 = 1000` pairs. Before accepting results, check completion, failed count, backend fallback counts, dataset/config identity, and judge backend.

### Step 2 — Optional targeted hard-case wave

Run only after inspecting full retrieval failures. Keep it diagnostic and separate from full-100 aggregate conclusions. Candidate focus:

- `dai_van_interpretation`
- low Context Recall items
- high retrieval-latency items
- sparse/dense/reranker failure cases

Use `configs/w8_abl_01_priority_wave.yaml` only after confirming its dataset/subset semantics and expected pair count.

### Step 3 — Rebuild and review final report

```powershell
$env:PYTHONPATH='backend'
.\.venv\Scripts\python.exe scripts/build_final_ablation_report.py
```

Then inspect:

- `evaluation/ablation_final_report.md`
- `benchmark/tuvi_golden_dataset/reports_final/ablation_final_summary.json`
- `benchmark/tuvi_golden_dataset/reports_final/protocol/run_registry.md`

Final status is complete when the canonical 3×3 Chunking × Prompt matrix and required Retrieval/Fusion/Reranker matrix both have valid full coverage. Optional targeted waves and legacy prompt placeholders must not block final status.

## 5. Decision questions for the next session

1. Does any retrieval path/fusion/reranker variant improve Context Recall without unacceptable p95 regression?
2. Is dense retrieval worth its latency cost versus graph+sparse baseline?
3. Does reranking help, or does it remove evidence-role coverage?
4. Are the 3×3 chunking/prompt winners stable by `question_family` and `question_complexity`?
5. Is the current latency a real retrieval bottleneck or a backend/runtime condition requiring a separate diagnostic note?

## 6. Important interpretation constraints

- `Score` is a ranking heuristic, not a scientific replacement for individual metrics.
- Do not select a winner on aggregate Score alone; report quality and p95 together.
- `core_identity` chart-only rows can have zero graph/citation metrics by design; inspect them separately.
- Do not use offline smoke/static judge as final evidence.
- Supabase errors do not block the experiment unless local artifacts/checkpoints fail.
- `evaluation/report_final.md` is historical W8 production-config evaluation evidence, not the canonical comparative report for the completed 3×3 Chunking × Prompt study.

## 7. Session-start checklist

- [ ] Read this file and the latest final comparative report.
- [ ] Check git status and preserve completed artifacts.
- [ ] Confirm preflight artifacts remain valid for the current environment.
- [ ] Start/resume retrieval/fusion/reranker matrix.
- [ ] Analyze retrieval matrix against the completed 3×3 Chunking × Prompt evidence.
- [ ] Rebuild report and update registry if new runs complete.