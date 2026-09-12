# P3 decision draft

- Recommended winner: `p3_prompt_1`
- Control: `p3_prompt_2`
- Primary metric: `faithfulness_avg`
- Report SHA-256: `6f70bf6aafd9824f4b47e6aaec557bb4203aed7f5323aac756534fc5a2b3d904`

| Candidate | Faithfulness | Citation Evidence F1 | Answer Relevancy | Latency p95 ms | Guardrail | Note |
|---|---:|---:|---:|---:|---|---|
| p3_prompt_1 | 0.912000 | 0.0296 | 0.871 | 3376.01 | PASS | citation_evidence_f1=0.0296; citation_f1_floor=0.0074; invalid_markers=0; relevancy=0.871; relevancy_floor=0.806 |
| p3_prompt_2 | 0.900000 | 0.0274 | 0.826 | 3934.55 | PASS | citation_evidence_f1=0.0274; citation_f1_floor=0.0074; invalid_markers=0; relevancy=0.826; relevancy_floor=0.806 |
| p3_prompt_3 | 0.822800 | 0.0264 | 0.856 | 4986.02 | PASS | citation_evidence_f1=0.0264; citation_f1_floor=0.0074; invalid_markers=0; relevancy=0.856; relevancy_floor=0.806 |

## Paired bootstrap

- Not performed: Top-two primary gap 0.012000 is not below 0.01.

This file is a deterministic draft. A must review failures, hashes and factor isolation before locking the winner.
