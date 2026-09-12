# Retrieval-only report — sequential_p1_chunking

- Status: `completed`
- Dataset items: `100`
- Anchor mapping coverage: `0.860111`
- Backend: `rule-based-gold-evidence-v1`

| Config | Status | Gold-span Recall@8 | Gold-chunk Precision@8 | Retrieval p95 ms | Failed |
|---|---|---:|---:|---:|---:|
| p1_fixed_512 | completed | 0.032206 | 0.029141 | 5654.32 | 0 |
| p1_parent_child | completed | 0.033816 | 0.029827 | 5056.67 | 0 |
| p1_semantic_bge_m3 | completed | 0.027375 | 0.021374 | 5158.39 | 0 |

Only exact/manual-approved anchors enter retrieval metric denominators. Unmapped annotations are reported separately.
Generation and AI judging were not executed in this report.
