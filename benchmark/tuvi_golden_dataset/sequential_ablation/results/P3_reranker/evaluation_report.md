# Retrieval-only report — sequential_p4_reranker

- Status: `completed`
- Dataset items: `100`
- Anchor mapping coverage: `0.860111`
- Backend: `rule-based-token-overlap-v2`

| Config | Status | Recall@8 | Precision@8 | F1@8 | Retrieval p95 ms | Failed |
|---|---|---:|---:|---:|---:|---:|
| p4_rerank_off | completed | 0.581717 | 0.8544 | 0.692171 | 10771.51 | 0 |
| p4_rerank_on | completed | 0.623269 | 0.887023 | 0.732115 | 144483.4 | 0 |

Recall@8 and Precision@8 use source-aligned multiset token overlap at tau=0.25. All annotated gold spans enter the recall denominator.
Exact-coordinate gold metrics remain in JSON as provenance diagnostics only.
Generation and AI judging were not executed in this report.
