# Preflight Summary - Full Ablation Rerun

Status: **passed**
Completed UTC: `2026-08-03T08:56:09.703027+00:00`
Git SHA: `668b9f6691d505594b859629cd4249b2dbce75ac`

## Dataset

| Path | Items | SHA256 |
|---|---:|---|
| `benchmark/tuvi_golden_dataset/release/tuviqa_v1_release.jsonl` | 100 | `90376a87cec29cc22e93dc71b41e054ed2f0183bc515a52aa461fecd43cc008c` |

## Gates

| Gate | Status | Evidence |
|---|---|---|
| backend_regression_subset | **passed** | 111 passed, 1 warning; log=`benchmark/tuvi_golden_dataset/reports_final/00_preflight/logs/pytest_backend_subset.log` |
| gemini_probe | **passed** | model=gemini-3.1-flash-lite-preview, ok_keys=4/4; log=`benchmark/tuvi_golden_dataset/reports_final/00_preflight/logs/gemini_probe.log` |
| neo4j_chunk_coverage | **passed** | expected=12, observed=12, missing=0; log=`benchmark/tuvi_golden_dataset/reports_final/00_preflight/logs/neo4j_chunk_coverage.log` |

## Manifest Inventory

| Ablation | Manifest | Configs | Manifest SHA256 |
|---|---|---:|---|
| chunking_prompt_source_v3 | `configs/w6_abl_03_chunking_matrix.yaml` | 3 | `3f04bac9e8e825dc6c9e4d743fca4331b49a9970de8d27f7a7e5f43651698b6b` |
| retrieval_fusion_reranker | `configs/w8_abl_01_retrieval_matrix_v2.yaml` | 10 | `a1f299ebd93f16b7ac6e7f205da00e9147ba91e8f41cd92f0dc66efa1e179b37` |

## Offline Smoke Results

| Smoke | Status | Judge | Configs | Items | Pairs | Report |
|---|---|---|---:|---:|---:|---|
| chunking_prompt_source_v3 | **passed** | `static-smoke` | 3/3 | 2 | 6 | `benchmark/tuvi_golden_dataset/reports_final/00_preflight/smoke_chunking/evaluation_report.json` |
| retrieval_fusion_reranker | **passed** | `static-smoke` | 10/10 | 2 | 20 | `benchmark/tuvi_golden_dataset/reports_final/00_preflight/smoke_retrieval_fusion_reranker/evaluation_report.json` |

## Decision

- Preflight passed for backend regression, Gemini model access, Neo4j chunk coverage, retrieval smoke, and source-wave smoke.
- Completed source waves `10_...` and `11_...` must be interpreted as one Chunking × Prompt 3×3 matrix.
- Current active next step after the completed 3×3 matrix: run/resume the retrieval/fusion/reranker matrix with Gemini judge and checkpoint/resume.
- Keep `--skip-persistence`; Supabase persistence remains non-blocking.

## Active Retrieval Matrix Command

```powershell
$env:PYTHONPATH='backend'
.\.venv\Scripts\python.exe scripts\run_eval.py `
  --manifest configs/w8_abl_01_retrieval_matrix_v2.yaml `
  --judge-backend gemini `
  --skip-persistence `
  --checkpoint-dir benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/checkpoints `
  --output-dir benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix
```
