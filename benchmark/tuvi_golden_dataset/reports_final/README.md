# TuViQA Full Ablation Reports Final

This directory contains local reproducible artifacts for the full ablation rerun. Deploy/production operations are intentionally excluded.

## Directory map

- `protocol/`: frozen method, command log, run registry, identity hashes.
- `00_preflight/`: tests, Gemini probe, Neo4j coverage, offline smoke reports.
- `10_chunking_strategy_ablation/`: official chunking ablation output and checkpoint.
- `11_chunking_prompt_interaction_v1_v2/`: completed supporting chunking x prompt interaction wave.
- `20_retrieval_fusion_reranker_matrix/`: official 10-config retrieval/fusion/reranker matrix output and checkpoint.
- `30_prompt_generation_current_retrieval/`: prompt ablation on current retrieval control.
- `31_prompt_generation_best_retrieval/`: prompt ablation on Phase 3 retrieval winner if a v2 manifest is created.
- `40_targeted_hard_cases/`: optional diagnostic hard-case wave.
- `90_final_report/`: synthesized final ablation report.
- `protocol/next_session_handoff.md`: current progress, exact resume commands, and next-session decision gates.

## Source of truth

Local checkpoints and `evaluation_report.json/md` files are canonical. Supabase persistence is skipped unless explicitly unblocked.
