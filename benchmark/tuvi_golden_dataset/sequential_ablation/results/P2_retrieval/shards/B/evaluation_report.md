# Retrieval-only report — sequential_p2_retrieval_shard_b

- Status: `completed`
- Dataset items: `100`
- Anchor mapping coverage: `0.860111`
- Backend: `rule-based-token-overlap-v2`

| Config | Status | Recall@8 | Precision@8 | F1@8 | Retrieval p95 ms | Failed |
|---|---|---:|---:|---:|---:|---:|
| p2_sparse | completed | 0.569252 | 0.83033 | 0.67544 | 4494.02 | 0 |
| p2_graph_sparse | completed | 0.584488 | 0.803543 | 0.67673 | 6848.74 | 0 |
| p2_dense_sparse | completed | 0.558172 | 0.846626 | 0.672784 | 6458.02 | 0 |
| p2_graph_dense_sparse | completed | 0.581717 | 0.8544 | 0.692171 | 7294.01 | 0 |

Recall@8 and Precision@8 use source-aligned multiset token overlap at tau=0.25. All annotated gold spans enter the recall denominator.
Exact-coordinate gold metrics remain in JSON as provenance diagnostics only.
Generation and AI judging were not executed in this report.
