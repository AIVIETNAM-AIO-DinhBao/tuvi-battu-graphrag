# W8-EVAL-01 Final Evaluation Report

- **Run verdict:** `RUN_VALID`
- **Quality verdict:** `QUALITY_FAIL`
- **Performance verdict:** `PERFORMANCE_FAIL`
- **Human verdict:** `HUMAN_PENDING`
- **Overall:** `PRODUCTION_HOLD`

> The full-100 run is operationally valid. Overall production acceptance is on hold because automatic quality/performance gates failed and human review is pending.

## Scope and identity

- Git SHA: `c32771fefb5bc14686660a43ab0bd3ba4d79d4b7`
- Run identity: `60c4ce22d8228f5cc826094d6bf68fd956b2a91e2d7a768d10cc51e0940aae8d`
- Dataset SHA-256: `90376a87cec29cc22e93dc71b41e054ed2f0183bc515a52aa461fecd43cc008c`
- Evaluator SHA-256: `9ae528d893159c4092c3129523da8d69a7a79a6ab5c32a132791158287eda314`
- Config hash: `c40227a029588b7793201702798e96e640d7a436131d6f5f0437f67151803d96`
- Generation model: `gemini-3.1-flash-lite-preview`
- Judge model: `gemini-3.1-flash-lite-preview`
- Dataset: 100 items, 10 charts, 10 families; Direct=10, One-hop=46, Two-hop=44; chart-only=9, corpus-grounded=91.

## Execution completeness

- Full run: `{"completed_pair_count": 100, "executed_pair_count": 100, "expected_pair_count": 100, "failed_pair_count": 0, "resumed_pair_count": 0}`
- Resume verification: `{"completed_pair_count": 100, "executed_pair_count": 0, "expected_pair_count": 100, "failed_pair_count": 0, "resumed_pair_count": 100}`
- Failed pairs: `0`; generation fallback: `0`; retrieval fallback: `0`; judge failure: `0`; no-context: `0`; citation fallback: `0`.

## Official target comparison

| Metric | Result | Target | Verdict |
|---|---:|---:|---|
| Faithfulness | 0.853 | >= 0.80 | PASS |
| Answer Relevancy | 0.719 | >= 0.75 | FAIL |
| Context Recall | 0.6223 | >= 0.70 | FAIL |
| Graph Hit Rate | 0.967 | >= 0.65 | PASS |
| Citation Coverage | 0.978 | >= 0.90 | PASS |
| RAG p95 | 26530.42 ms | <= 8000 ms | FAIL |
| Retrieval p95 | 24467.9 ms | <= 3000 ms | FAIL |

## Additional metrics

- Chart Context Grounding: `0.8889`.
- Corpus Source Coverage: `1.0`.
- Generation p95: `2835.35 ms`; judge p95: `2023.82 ms`; evaluation-total p95: `27926.93 ms`.
- Retried items (`attempt_count>1`): `0`.

## Subgroup and item analysis

- See `analysis/subgroup_complexity.csv`, `subgroup_family.csv`, `subgroup_chart.csv`, and `subgroup_topic.csv`.
- See `analysis/per_item_results.csv` and `analysis/latency_outliers.csv`.
- Group results are descriptive alerts; complexity, family, and chart dimensions may be confounded.
- One-hop: Answer Relevancy `0.6652`, Context Recall `0.5978`, RAG p95 `25135.03 ms`.
- Two-hop: Answer Relevancy `0.7364`, Context Recall `0.6439`, RAG p95 `29074.94 ms`.
- Direct: Answer Relevancy `0.89`; its chart-only-heavy retrieval latency is not comparable to corpus-grounded groups.
- Weakest family was `dai_van_interpretation`: Answer Relevancy `0.34`, Context Recall `0.27`, RAG p95 `39779.29 ms`.
- Lowest chart groups by Answer Relevancy were `CHART-010` (`0.60`), `CHART-008` (`0.61`), and `CHART-002` (`0.68`). These are diagnostic findings, not causal chart effects.

## Human review

- Status: `HUMAN_PENDING`.
- Detailed automatic review queue: `49` items.
- Non-triggered control sample: `20` items.
- Trigger counts include 41 Context Recall, 35 Answer Relevancy, 17 Faithfulness, 8 Citation Coverage, 8 zero gold-document coverage, and 3 graph-miss triggers; items may have multiple triggers.
- Production human acceptance requires zero adjudicated critical defects.

## Decision

Automatic quality failures: `answer_relevancy_avg, context_recall_avg`.
Performance failures: `rag_p95, retrieval_p95`.
The current locked config remains evaluable and operationally complete, but it must not be claimed as production-passing. Remediation should focus on answer relevancy, context recall, and retrieval latency before a new identified config is considered. Any changed config requires a new full-100 evaluation.

## Limitations

- Gemini is both generation provider and judge model family; judge bias and stochasticity remain limitations.
- The committed dataset release has a stable hash, but no committed reviewer sign-off report was found; project-lead dataset sign-off remains required.
- Supabase experiment persistence was skipped because live `experiment_runs` remains blocked by PGRST205.
- One detached-worker telemetry field recorded a null exit code; canonical report, checkpoint, and direct resume evidence establish run validity.
- This task evaluates one production config; full comparative retrieval/fusion/reranker analysis belongs to W8-ABL-01.
