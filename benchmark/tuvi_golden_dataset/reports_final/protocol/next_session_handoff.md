# Next-session Handoff — Full Ablation

Updated: `2026-08-03`  
Scope: full ablation evidence only. Deploy/production ops are out of scope.

## 1. Frozen identity

- Git SHA at last report build: `0173f4605ec6c96c87fda5e3f50e9bfeaf6d64f5`
- Dataset: `benchmark/tuvi_golden_dataset/release/tuviqa_v1_release.jsonl`
- Dataset items: `100`
- Dataset SHA256: `90376a87cec29cc22e93dc71b41e054ed2f0183bc515a52aa461fecd43cc008c`
- Official judge: `gemini`
- Generation model in completed waves: `gemini-3.1-flash-lite-preview`
- Persistence: `--skip-persistence`; local reports/checkpoints are source of truth
- Final report: `evaluation/ablation_final_report.md`
- Machine-readable summary: `benchmark/tuvi_golden_dataset/reports_final/ablation_final_summary.json`

Do not mutate completed manifests/results. New controls require a new manifest and output directory.

## 2. Completed evidence

### 2.1 Single-axis chunking — complete

- Manifest: `configs/w6_abl_03_chunking_matrix.yaml`
- Output: `benchmark/tuvi_golden_dataset/reports_final/10_chunking_strategy_ablation`
- Coverage: `3 configs x 100 = 300`; `300/300`; failed `0`
- Judge: `gemini`
- Current heuristic winner: `parent_child_graph_sparse_rrf`
- Winner metrics: Score `0.749`; Faithfulness `0.900`; Answer Relevancy `0.799`; Context Recall `0.714`; Graph Hit `0.967`; Citation Coverage `0.989`
- Winner p95: RAG `123459.1 ms`; Retrieval `118592.8 ms`; Generation `5595.9 ms`

Interpretation: parent-child currently ranks first by the report heuristic. Latency is very high and must not be ignored.

### 2.2 Chunking x Prompt interaction — complete supporting wave

- Manifest: `configs/w8_abl_02_chunking_prompt_interaction_v1_v2.yaml`
- Output: `benchmark/tuvi_golden_dataset/reports_final/11_chunking_prompt_interaction_v1_v2`
- Coverage: `6 configs x 100 = 600`; `600/600`; failed `0`
- Current winner: `semantic_bge_m3_prompt_v1_graph_sparse_rrf`
- Winner metrics: Score `0.737`; Faithfulness `0.872`; Answer Relevancy `0.782`; Context Recall `0.706`; Graph Hit `0.967`; Citation Coverage `0.986`

Interpretation: this wave varies chunking and prompt jointly. Use it only as interaction evidence; it does not replace single-axis prompt or retrieval conclusions.

## 3. Current state / remaining work

The report is correctly **in_progress**. Registry/report currently show:

| Wave | Status | Expected |
|---|---|---:|
| Preflight tests/probe/Neo4j/smoke | complete | `111 passed`; Gemini `4/4`; Neo4j `12/12`; smoke `6/6`, `20/20`, `6/6` |
| Chunking single-axis | complete | 300 pairs |
| Chunking x Prompt interaction | complete | 600 pairs |
| Retrieval/Fusion/Reranker v2 | not started | 1000 pairs |
| Prompt on current retrieval | not started | 300 pairs |
| Prompt on best retrieval | conditional; manifest missing | 300 pairs if Phase 3 winner changes |
| Targeted hard cases | optional; not started | diagnostic only |

Primary remaining live work: `1000 + 300 = 1300` pairs, plus conditional prompt-v2 and optional diagnostics.

## 4. Next session execution order

### Step 0 — Confirm frozen preflight, do not rerun completed waves blindly

Read `benchmark/tuvi_golden_dataset/reports_final/protocol/run_registry.md` and inspect `00_preflight/`.
Preflight completed on `2026-07-28`; read its summary/logs and ensure environment identity has not changed. Rerun Phase 1 in `protocol/commands.md` only after a material environment/configuration change. Recorded gates:

- backend regression subset passes;
- Gemini probe works without leaking keys;
- Neo4j chunk coverage is `12/12`;
- three offline smoke manifests complete.

Preflight is a gate for new live waves, not final evidence.

### Step 1 — Run retrieval/fusion/reranker full matrix

Official command from repo root (PowerShell):

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

Resume after interruption/quota exhaustion: append `--resume --retry-failed`. Never delete checkpoints.

Expected: `10 configs x 100 = 1000` pairs. Before accepting results, check completion, failed count, backend fallback counts, dataset/config identity, and judge backend.

### Step 2 — Decide prompt control using Phase 3 winner

Compare Phase 3 winner against the retrieval control used by `configs/w7_abl_01_generation_prompt_matrix.yaml`.

- If current retrieval remains the valid control: run Phase 4A into `30_prompt_generation_current_retrieval/`.
- If retrieval winner changes: create immutable `configs/w8_abl_02_prompt_matrix_on_best_retrieval.yaml`; run it into `31_prompt_generation_best_retrieval/`.
- Do not overwrite the old prompt manifest or pool current-control and best-retrieval results together.

Phase 4A command is in `protocol/commands.md`. Use the same `gemini`, `--skip-persistence`, checkpoint, retry, and resume policy.

### Step 3 — Optional targeted hard-case wave

Run only after inspecting full retrieval/prompt failures. Keep it diagnostic and separate from full-100 aggregates. Candidate focus:

- `dai_van_interpretation`
- low Context Recall items
- high retrieval-latency items
- sparse/dense/reranker failure cases

Use `configs/w8_abl_01_priority_wave.yaml` only after confirming its dataset/subset semantics and expected pair count.

### Step 4 — Rebuild and review final report

```powershell
$env:PYTHONPATH='backend'
.\.venv\Scripts\python.exe scripts/build_final_ablation_report.py
```

Then inspect:

- `evaluation/ablation_final_report.md`
- `benchmark/tuvi_golden_dataset/reports_final/ablation_final_summary.json`
- `benchmark/tuvi_golden_dataset/reports_final/protocol/run_registry.md`

Final status is complete only when all required single-axis waves have valid full coverage. The optional targeted wave must not block final status.

## 5. Decision questions for the next session

1. Does any retrieval path/fusion/reranker variant improve Context Recall without unacceptable p95 regression?
2. Is dense retrieval worth its latency cost versus graph+sparse baseline?
3. Does reranking help, or does it remove evidence-role coverage?
4. Which prompt wins after retrieval control is frozen?
5. Do the winners remain stable by `question_family` and `question_complexity`?
6. Is the current latency a real retrieval bottleneck or a backend/runtime condition requiring a separate diagnostic note?

## 6. Important interpretation constraints

- `Score` is a ranking heuristic, not a scientific replacement for individual metrics.
- Do not select a winner on aggregate Score alone; report quality and p95 together.
- `core_identity` chart-only rows can have zero graph/citation metrics by design; inspect them separately.
- Do not use offline smoke/static judge as final evidence.
- Supabase errors do not block the experiment unless local artifacts/checkpoints fail.

## 7. Session-start checklist

- [ ] Read this file and the latest final report.
- [ ] Check git status and preserve completed artifacts.
- [ ] Confirm preflight artifacts remain valid for the current environment.
- [ ] Start/resume Phase 3 retrieval matrix.
- [ ] Analyze Phase 3 winner and choose Phase 4A vs prompt-v2.
- [ ] Run prompt ablation, optional hard-case wave.
- [ ] Rebuild report and update registry.