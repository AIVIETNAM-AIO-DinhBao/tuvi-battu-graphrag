# P5 decision draft

- Recommended winner: `p5_top_k_20`
- Control: `p5_top_k_20`
- Primary metric: `recall_at_8`
- Report SHA-256: `9e176caffb8a90edcfad727e03203a9bf319217e921989fce4a9c0fb4b1c80e4`
- Selection rule: P5 pre-registered complexity tie-break: paired bootstrap was inconclusive, so select the smaller reranked candidate-retention depth.

| Candidate | Evidence Recall | Evidence Precision | Evidence F1 | Guardrail | Note |
|---|---:|---:|---:|---|---|
| p5_top_k_40 | 0.632964 | 0.878963 | 0.735951 | PASS | precision=0.878963; floor=0.867023 |
| p5_top_k_20 | 0.623269 | 0.887023 | 0.732115 | PASS | precision=0.887023; floor=0.867023 |
| p5_top_k_10 | 0.606648 | 0.900533 | 0.724938 | PASS | precision=0.900533; floor=0.867023 |

## Paired bootstrap

- Comparison: `p5_top_k_40` minus `p5_top_k_20`
- Mean delta: `0.009721`
- Observed paired delta: `0.009695`
- 95% CI: `[-0.006766, 0.026194]`
- P(delta > 0): `0.8645`
- Outcome: **inconclusive**

## Applied P5 tie-break

`p5_top_k_40` has the highest raw Evidence Recall, but its paired comparison with `p5_top_k_20` is inconclusive. The pre-registered lower-depth tie-break therefore selects `p5_top_k_20`; raw scores are retained unchanged.

This file is a deterministic draft. A must review failures, hashes and factor isolation before locking the winner.
