# Re-index phase migration

The preliminary prompt experiment formerly called P3 was discarded because it
used pre-reranker context. Its `results/P3_prompt` directory and manifests were
removed and must not be cited as an ablation result.

The executed retrieval-only artifacts were re-indexed without changing any raw
scores:

| Previous label | Current label | Canonical directory |
|---|---|---|
| P4 reranker on/off | P3 reranker on/off | `results/P3_reranker` |
| P5 retention 10/20/40 | P4 reranked retention depth | `results/P4_reranker_depth` |

Some immutable item JSON records retain their former experiment IDs and report
hashes. They are legacy provenance only; all current plans, manifests, tickets,
and report prose use the current phase labels.

P5 is now the final prompt comparison: three prompts share the frozen context
reassembled from the completed P4 max-rerank bundle at the locked retention
depth `k=20`. This reuses existing reranker output and does not invoke Neo4j or
the cross-encoder again.
