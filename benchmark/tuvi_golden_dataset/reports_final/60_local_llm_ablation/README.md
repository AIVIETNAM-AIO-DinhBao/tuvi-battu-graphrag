# Local-LLM Ablation — Canonical Merged Results

This directory is the tracked, portable publication of the local-model generalization study:

- generation models: `Qwen/Qwen2.5-7B-Instruct` and `google/gemma-3-4b-it`;
- inference: deterministic 4-bit generation over one frozen retrieval bundle;
- retrieval configurations: `graph_dense_rrf`, `semantic_gs_rrf_rerank_k40`, and `semantic_gs_rrf_no_rerank_reference`;
- evaluation: `gemini-3.1-flash-lite-preview` using the repository's canonical evaluator.

## Completeness gate

- Source judge shards: 3 (B/C/D)
- Expected/completed pairs: 600/600
- Failed pairs: 0
- Model-config result rows: 6
- Merge status: complete

The merge validates every shard checksum, requires one identical judge model, rejects conflicting `model_id + pair_id` records, and does not call Gemini again.

## Files

- `evaluation_report.json`: canonical report with all six model-config entries and per-item results.
- `evaluation_report.md`: rendered human-readable report.
- `local_llm_metrics.csv`: compact six-row table for the written report and plots.
- `judged_items.jsonl`: 600 merged item-level judge records.
- `checkpoints/`: canonical audit/checkpoint representation.
- `merge_summary.json`: completion gate and SHA-256 checksums.

Prediction archives, model weights, API keys, intermediate extraction folders, and the three handoff ZIPs remain under the ignored `local_llm_ablation/artifacts/` tree and are intentionally not committed.
