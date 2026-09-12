# P2 decision draft

- Recommended winner: `p2_graph_dense_sparse`
- Control: `p2_dense_sparse`
- Primary metric: `recall_at_8`
- Report SHA-256: `1d5f5b4ba685d27c15fb9018900d47e1785a795dec43f8ccceac2357daec086c`

| Candidate | Primary | Precision@8 | F1@8 | Guardrail | Note |
|---|---:|---:|---:|---|---|
| p2_graph_sparse | 0.584488 | 0.803543 | 0.67673 | FAIL | precision=0.803543; floor=0.826626 |
| p2_graph_dense_sparse | 0.581717 | 0.8544 | 0.692171 | PASS | precision=0.8544; floor=0.826626 |
| p2_sparse | 0.569252 | 0.83033 | 0.67544 | PASS | precision=0.83033; floor=0.826626 |
| p2_dense_sparse | 0.558172 | 0.846626 | 0.672784 | PASS | precision=0.846626; floor=0.826626 |
| p2_graph_dense | 0.556787 | 0.832381 | 0.667247 | PASS | precision=0.832381; floor=0.826626 |
| p2_dense | 0.500000 | 0.91314 | 0.646178 | PASS | precision=0.91314; floor=0.826626 |
| p2_graph | 0.279778 | 0.773134 | 0.410872 | FAIL | precision=0.773134; floor=0.826626 |

## Paired bootstrap

- Not performed: Top-two primary gap 0.012465 is not below 0.01.

This file is a deterministic draft. A must review failures, hashes and factor isolation before locking the winner.
