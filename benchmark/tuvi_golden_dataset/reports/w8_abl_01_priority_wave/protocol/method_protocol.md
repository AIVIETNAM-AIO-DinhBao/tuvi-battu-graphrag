# W8-ABL-01 Priority Full-100 Wave Protocol

This protocol was frozen before launching the live wave.

## Candidates

1. `sparse_only_rrf`
2. `dense_sparse_rrf`
3. `baseline_no_reranker`
4. `baseline_weighted_sum`

The behavior-equivalent `default_production_v2` full-100 result is reused as the Graph+Sparse+RRF+lexical-reranker control. The control and matrix baseline differ only by `experiment_id` and display `name`.

All candidates hold semantic BGE-M3 chunking, prompt v1, Gemini Flash Lite, query rewrite off, document grading on, balanced context, and cache disabled constant.

## Execution gates

- Full live Neo4j + Gemini run over ordered `TVQA-001..TVQA-100`.
- Expected pairs: 400; failed pairs: 0.
- Generation/retrieval/judge backend fallback: 0.
- Resume verification: 0 executed, 400 resumed.
- No config changes or threshold changes after launch.

## Analysis policy

Compare each candidate with the frozen production control by item ID. Report overall and subgroup metric deltas, latency deltas, win/tie/loss counts, and fixed-seed paired bootstrap confidence intervals. Do not promote a candidate solely from the evaluator's preliminary weighted heuristic.

Any candidate selected for production requires a new experiment ID/config hash and an explicit acceptance decision. This wave does not silently overwrite `default_production_v2`.

## Runtime key-routing decision

The prelaunch exact-model probe found original `key_1` exhausted at the provider's 500 free-tier requests/day limit, while original keys 2-4 initially remained healthy. A rotated probe then confirmed original key 2 as the new primary and found two currently usable keys in total. For this wave only, the supervisor rotates the in-memory child-process order to keys 2, 3, 4, then 1. No secret value is persisted or changed in `.env`. This operational routing does not change the model, prompt, config, dataset, or evaluator identity. Two healthy free-tier keys provide at most about 1,000 daily requests against roughly 800 required successful calls, so checkpoint/resume after quota reset remains the required recovery path if reserve is exhausted.