# P5 decision

- Recommended winner: `p5_prompt_1` (`tuvi_generation_v1`)
- Control: `p5_prompt_2`
- Primary metric: `faithfulness_avg`
- Report SHA-256: `0b96bf3b878e034a4bd56565cd75c6634aba44a95205a79c211b16c62aab42ec`
- Selection rule: highest Faithfulness among candidates that pass the Answer
  Relevancy/validity guardrail.

| Candidate | Faithfulness | Answer Relevancy | Latency p95 ms | Guardrail | Note |
|---|---:|---:|---:|---|---|
| p5_prompt_1 | 0.926000 | 0.858 | 4649.16 | PASS | invalid_markers=0; relevancy=0.858; relevancy_floor=0.815 |
| p5_prompt_2 | 0.913000 | 0.835 | 5410.09 | PASS | invalid_markers=0; relevancy=0.835; relevancy_floor=0.815 |
| p5_prompt_3 | 0.886000 | 0.894 | 6064.77 | PASS | invalid_markers=0; relevancy=0.894; relevancy_floor=0.815 |

## Paired bootstrap

- Not performed: Top-two primary gap 0.013000 is not below 0.01.

## P6 prompt-sensitivity matrix

P6 additionally runs `p5_prompt_3` (`tuvi_generation_answer_first_v4`) for
each generator because it has the highest Answer Relevancy (`0.894`). This is
a planned **model × shortlisted-prompt matrix**, not a replacement for the P5
winner: P5 remains locked to Prompt 1 by its pre-registered Faithfulness rule.
