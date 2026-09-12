# P4 decision draft

- Recommended winner: `p4_rerank_on`
- Control: `p4_rerank_off`
- Primary metric: `recall_at_8`
- Report SHA-256: `8e2d928b519ebe2d7c3dd63dc2a1f1f89a408185b346139ef589a1f8c283ad1d`

| Candidate | Recall@8 | Precision@8 | F1@8 | Guardrail | Note |
|---|---:|---:|---:|---|---|
| p4_rerank_on | 0.623269 | 0.887023 | 0.732115 | PASS | precision=0.887023; floor=0.8344 |
| p4_rerank_off | 0.581717 | 0.8544 | 0.692171 | PASS | precision=0.8544; floor=0.8344 |

## Paired bootstrap

- Not performed: Top-two primary gap 0.041552 is not below 0.01.

This file is a deterministic draft. A must review failures, hashes and factor isolation before locking the winner.
