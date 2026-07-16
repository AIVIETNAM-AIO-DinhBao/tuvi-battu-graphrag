# W8-EVAL-01 Frozen Method Protocol

This protocol was frozen before launching the canonical full-100 evaluation.

## Scope

- One locked config: `configs/default_production.yaml` (`default_production_v2`).
- Ordered release dataset: `TVQA-001..TVQA-100`.
- Live Neo4j retrieval, live Gemini generation, and live Gemini judge.
- Generation and judge model: `gemini-3.1-flash-lite-preview`.
- No dataset limit, offline smoke, config mutation, dense promotion, query rewrite, or matrix variants.
- Supabase persistence is skipped because live `experiment_runs` remains blocked by `PGRST205`; checkpoint/report files are canonical.

## Predeclared gates

Execution validity requires 100/100 completed pairs and zero failed, generation fallback, retrieval fallback, or judge-failure pairs. Quality targets are Faithfulness >= 0.80, Answer Relevancy >= 0.75, Context Recall >= 0.70, Graph Hit Rate >= 0.65, and Citation Coverage >= 0.90. Performance targets are user-facing RAG p95 <= 8 seconds and retrieval p95 <= 3 seconds.

The runner exit code only establishes execution completeness. It does not by itself establish quality, performance, human, or production acceptance.

## Recovery policy

The run uses atomic per-pair checkpointing, at most two attempts per item, and a two-second exponential retry base. A recovery run must use the same identity and `--resume --retry-failed`. Repeated service failures are not retried indefinitely.

## Human review

All answers receive a lightweight review. All automatic threshold failures, retrieval/citation misses, retries, slowest-five-percent items, and suspected critical defects enter detailed double review and adjudication. Production human acceptance requires zero adjudicated critical defects.

## Boundary

This task evaluates the locked production config only. Comparative 10-config retrieval/fusion/reranker evaluation belongs to W8-ABL-01 and cannot be pooled into this result.