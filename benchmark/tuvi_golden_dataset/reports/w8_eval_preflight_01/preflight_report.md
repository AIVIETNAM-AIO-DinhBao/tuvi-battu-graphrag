# W8-EVAL-PREFLIGHT-01

- **Overall:** `PASS`
- **Go/no-go:** `GO`
- Git SHA: `bd1305c1a97907cd1ee397790eb5bafa4f3a666f`
- Production config hash: `c40227a029588b7793201702798e96e640d7a436131d6f5f0437f67151803d96`
- Evaluator fingerprint: `9ae528d893159c4092c3129523da8d69a7a79a6ab5c32a132791158287eda314`
- Scope: `TVQA-001..006` (Direct + One-hop + Two-hop), all from `CHART-001`.
- This is an operational preflight, not a balanced quality benchmark or final scientific evidence.

## Gate summary

| Gate | Status | Evidence |
|---|---|---|
| `identity` | **PASS** | `{"dataset_item_count": 100, "evaluator_sha256": "9ae528d893159c4092c3129523da8d69a7a79a6ab5c32a132791158287eda314", "git_sha": "bd1305c1a97907cd1ee397790eb5bafa4f3a666f", "matrix_config_count": 10, "production_config_hash": "c40227a029588b7793201702798e96e640d7a436131d6f5f0437f67151803d96", "tracked_git_dirty": false}` |
| `regression_compile` | **PASS** | `{"compile_exit_code": 0, "pytest": "387 passed, 11 warnings", "pytest_exit_code": 0}` |
| `gemini_exact_model` | **PASS** | `{"checked_key_count": 4, "model": "gemini-3.1-flash-lite-preview", "ok_key_count": 4, "primary_ok": true}` |
| `neo4j_coverage` | **PASS** | `{"expected_pair_count": 12, "missing_pair_count": 0, "observed_pair_count": 12}` |
| `semantic_retrieval` | **PASS** | `{"dense_hit_counts": [5, 5], "embedding_model": "BAAI/bge-m3", "query_count": 2, "sparse_hit_counts": [5, 5]}` |
| `production_limit6` | **PASS** | `{"completed_pair_count": 6, "executed_pair_count": 6, "expected_pair_count": 6, "failed_pair_count": 0, "resumed_pair_count": 0}` |
| `retrieval_matrix_limit6` | **PASS** | `{"completed_pair_count": 60, "executed_pair_count": 60, "expected_pair_count": 60, "failed_pair_count": 0, "resumed_pair_count": 0}` |
| `live_resume` | **PASS** | `{"completed_pair_count": 60, "executed_pair_count": 0, "expected_pair_count": 60, "failed_pair_count": 0, "resumed_pair_count": 60}` |
| `provenance_mismatch` | **PASS** | `{"different_fields": ["identity_sha256", "selected_item_ids"], "exit_code": 2}` |
| `secret_scan` | **PASS** | `{"finding_count": 0, "scanned_file_count": 40}` |

## Production limit-6

- Execution: `{"completed_pair_count": 6, "executed_pair_count": 6, "expected_pair_count": 6, "failed_pair_count": 0, "resumed_pair_count": 0}`
- Hard fallbacks: generation=`0`, retrieval=`0`, judge=`0`.
- Retrieval p95: `15946.62 ms`; generation p95: `2509.0 ms`; judge p95: `1597.56 ms`; RAG p95: `18395.29 ms`.

## Retrieval matrix limit-6

| Config | Dense/Graph/Sparse | Dense rate | Graph rate | Sparse rate | Failed | Retrieval p95 ms | RAG p95 ms |
|---|---|---:|---:|---:|---:|---:|---:|
| `baseline_graph_sparse_rrf` | 0/1/1 | 0.0 | 0.3333 | 0.8333 | 0 | 15561.81 | 18355.95 |
| `graph_only_rrf` | 0/1/0 | 0.0 | 0.8333 | 0.0 | 0 | 11477.87 | 13784.43 |
| `sparse_only_rrf` | 0/0/1 | 0.0 | 0.0 | 0.8333 | 0 | 3028.77 | 5325.9 |
| `dense_only_rrf` | 1/0/0 | 0.8333 | 0.0 | 0.0 | 0 | 17251.15 | 19639.46 |
| `dense_sparse_rrf` | 1/0/1 | 0.3333 | 0.0 | 0.8333 | 0 | 4783.67 | 7408.46 |
| `graph_dense_rrf` | 1/1/0 | 0.8333 | 0.8333 | 0.0 | 0 | 12416.1 | 14766.62 |
| `all_paths_planner_dense_rrf` | 1/1/1 | 0.3333 | 0.3333 | 0.8333 | 0 | 15019.4 | 17414.4 |
| `baseline_no_reranker` | 0/1/1 | 0.0 | 0.1667 | 0.8333 | 0 | 15203.9 | 17360.68 |
| `baseline_weighted_sum` | 0/1/1 | 0.0 | 0.5 | 0.8333 | 0 | 15119.33 | 17376.48 |
| `baseline_graph_first` | 0/1/1 | 0.0 | 0.6667 | 0.8333 | 0 | 15052.0 | 17280.41 |

## Resume and provenance

- Live resume: `executed=0`, `resumed=60`, all 60 results came from checkpoint.
- Deliberate `--limit 5` mismatch: exit code `2`; differing fields include `selected_item_ids`.

## Warnings

- `google.generativeai` is deprecated; migrate to `google.genai` in a separate task.
- Neo4j `db.index.vector.queryNodes` is deprecated in favor of `SEARCH`.
- One transient Neo4j read timeout was retried; final matrix remained 60/60 with zero retrieval fallback.
- BGE-M3 cold start can exceed a 30-second shell-wrapper timeout.

## Decision

**GO** for the subsequent full benchmark, subject to revalidating Git/config/model identity immediately before launch. Full-100 was not started by this task.

## Next commands (not executed)

```powershell
.venv/Scripts/python.exe scripts/run_eval.py --config configs/default_production.yaml --dataset benchmark/tuvi_golden_dataset/release/tuviqa_v1_release.jsonl --judge-backend gemini --judge-model gemini-3.1-flash-lite-preview --skip-persistence --checkpoint-dir benchmark/tuvi_golden_dataset/reports/w8_eval_01/production_full100/checkpoint --output-dir benchmark/tuvi_golden_dataset/reports/w8_eval_01/production_full100 --max-item-attempts 2 --retry-base-seconds 2

## After production full-100 passes
.venv/Scripts/python.exe scripts/run_eval.py --manifest configs/w8_abl_01_retrieval_matrix_v2.yaml --judge-backend gemini --judge-model gemini-3.1-flash-lite-preview --skip-persistence --checkpoint-dir benchmark/tuvi_golden_dataset/reports/w8_abl_01/retrieval_v2_full100/checkpoint --output-dir benchmark/tuvi_golden_dataset/reports/w8_abl_01/retrieval_v2_full100 --max-item-attempts 2 --retry-base-seconds 2
```
