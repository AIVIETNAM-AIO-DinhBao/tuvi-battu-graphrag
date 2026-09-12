# P1 decision draft

- Recommended winner: `p1_fixed_512`
- Control: `p1_fixed_512`
- Primary metric: `recall_at_8`
- Report SHA-256: `f2d3747e3fadfa74582cacec687ed12d7f498e9ffb7fb7dda3c1492b94889970`

| Candidate | Primary | Precision@8 | F1@8 | Guardrail | Note |
|---|---:|---:|---:|---|---|
| p1_fixed_512 | 0.558172 | 0.846626 | 0.672784 | PASS | precision=0.846626; floor=0.826626 |
| p1_semantic_bge_m3 | 0.554017 | 0.822901 | 0.662205 | FAIL | precision=0.822901; floor=0.826626 |
| p1_parent_child | 0.538781 | 0.830455 | 0.653552 | PASS | precision=0.830455; floor=0.826626 |

## Paired bootstrap

- Not performed: Top-two primary gap 0.019391 is not below 0.01.

This file is a deterministic draft. A must review failures, hashes and factor isolation before locking the winner.
