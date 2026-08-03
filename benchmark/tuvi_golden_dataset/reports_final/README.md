# TuViQA Full Ablation Reports Final

This directory contains local reproducible artifacts for the full ablation rerun. Deploy/production operations are intentionally excluded.

## Directory map

- `protocol/`: frozen method, command log, run registry, identity hashes.
- `00_preflight/`: tests, Gemini probe, Neo4j coverage, offline smoke reports.
- `10_chunking_strategy_ablation/`: source wave A for the canonical Chunking × Prompt 3×3 matrix; contains the 3 prompt-v3 cells.
- `11_chunking_prompt_interaction_v1_v2/`: source wave B for the canonical Chunking × Prompt 3×3 matrix; contains the 6 prompt-v1/v2 cells.
- `20_retrieval_fusion_reranker_matrix/`: official 10-config retrieval/fusion/reranker matrix output and checkpoint. During multi-teammate execution, shard artifacts live under `20_retrieval_fusion_reranker_matrix/shards/` and are merged into the canonical root report with `scripts/merge_w8_retrieval_shards.py`.
- `40_targeted_hard_cases/`: optional diagnostic hard-case wave.
- `90_final_report/`: synthesized final ablation report.
- `protocol/next_session_handoff.md`: current progress, exact resume commands, and next-session decision gates.

## Source of truth

Local checkpoints and `evaluation_report.json/md` files are canonical. Supabase persistence is skipped unless explicitly unblocked.
