# P1 token-overlap report — sequential_p1_chunking

- Status: `completed`
- Threshold: `0.25`
- Gold spans: `722/722`
- Recall@8/Precision@8/F1@8 use source-aligned multiset token overlap.

| Config | Recall@8 | Precision@8 | F1@8 | Hits | Relevant chunks | Retrieval p95 ms |
|---|---:|---:|---:|---:|---:|---:|
| p1_fixed_512 | 0.5582 | 0.8466 | 0.6728 | 403/722 | 552/652 | 5654.32 |
| p1_parent_child | 0.5388 | 0.8305 | 0.6536 | 389/722 | 529/637 | 5056.67 |
| p1_semantic_bge_m3 | 0.5540 | 0.8229 | 0.6622 | 400/722 | 539/655 | 5158.39 |

## Definitions

- `overlap(g,c) = Σ min(count_g(t), count_c(t)) / |tokens(g)|`.
- A gold span is hit when a same-source chunk has overlap >= 0.25.
- A corpus chunk is relevant when it satisfies that condition for at least one same-source gold span.
- All annotated gold spans are included, regardless of coordinate mapping status; CHART chunks are excluded.
- F1@8 is the harmonic mean of the two micro-aggregates.
