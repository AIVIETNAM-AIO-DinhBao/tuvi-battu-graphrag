# Sequential generation report — sequential_p5_prompt

- Status: `completed`
- Dataset items: `100`
- Judge backend/protocol: `gemini` / `blind-v2`
- Expected/completed/failed pairs: `300` / `300` / `0`

| Config | Faithfulness | Answer Relevancy | Latency p95 ms | Invalid markers |
|---|---:|---:|---:|---:|
| p5_prompt_1 | 0.926 | 0.858 | 4649.16 | 0 |
| p5_prompt_2 | 0.913 | 0.835 | 5410.09 | 0 |
| p5_prompt_3 | 0.886 | 0.894 | 6064.77 | 0 |

> Reproducibility exception: `dirty-worktree` for shard(s) `A, B`. Shared run hashes were verified; see JSON for the audit record.

Faithfulness and Answer Relevancy are scored by the registered blind judge. Invalid citation markers are reported as an execution-validity gate, not a quality metric.
