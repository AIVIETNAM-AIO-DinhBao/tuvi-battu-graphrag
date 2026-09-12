# P5 decision draft

- Recommended winner: `p5_prompt_1`
- Control: `p5_prompt_2`
- Primary metric: `faithfulness_avg`
- Report SHA-256: `0b96bf3b878e034a4bd56565cd75c6634aba44a95205a79c211b16c62aab42ec`
- Selection rule: Highest primary metric among candidates that pass the pre-registered guardrail.

| Candidate | Faithfulness | Answer Relevancy | Latency p95 ms | Guardrail | Note |
|---|---:|---:|---:|---|---|
| p5_prompt_1 | 0.926000 | 0.858 | 4649.16 | PASS | invalid_markers=0; relevancy=0.858; relevancy_floor=0.815 |
| p5_prompt_2 | 0.913000 | 0.835 | 5410.09 | PASS | invalid_markers=0; relevancy=0.835; relevancy_floor=0.815 |
| p5_prompt_3 | 0.886000 | 0.894 | 6064.77 | PASS | invalid_markers=0; relevancy=0.894; relevancy_floor=0.815 |

## Paired bootstrap

- Not performed: Top-two primary gap 0.013000 is not below 0.01.

This file is a deterministic draft. A must review failures, hashes and factor isolation before locking the winner.
