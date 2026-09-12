# Retrieval-only report — sequential_p2_retrieval_shard_a

- Status: `completed`
- Dataset items: `100`
- Anchor mapping coverage: `0.860111`
- Backend: `rule-based-token-overlap-v2`

| Config | Status | Recall@8 | Precision@8 | F1@8 | Retrieval p95 ms | Failed |
|---|---|---:|---:|---:|---:|---:|
| p2_graph | completed | 0.279778 | 0.773134 | 0.410872 | 2722.85 | 0 |
| p2_dense | completed | 0.5 | 0.91314 | 0.646178 | 1268.7 | 0 |
| p2_graph_dense | completed | 0.556787 | 0.832381 | 0.667247 | 3226.49 | 0 |

Recall@8 and Precision@8 use source-aligned multiset token overlap at tau=0.25. All annotated gold spans enter the recall denominator.
Exact-coordinate gold metrics remain in JSON as provenance diagnostics only.
Generation and AI judging were not executed in this report.
