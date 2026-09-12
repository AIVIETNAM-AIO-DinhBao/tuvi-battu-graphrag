# Sequential ablation run registry

Chỉ A cập nhật bảng này sau khi nhận và validate artifact. Một phase chưa có dòng `LOCKED` thì phase sau không được phát ticket.

| Phase | Ticket | Assignee | Manifest SHA | Code SHA | Data/anchor SHA | Snapshot | Expected | Completed | Failed | Artifact SHA | Status | Winner/lock |
|---|---|---|---|---|---|---|---:|---:|---:|---|---|---|
| P0 | P0-A | A | N/A | TBD | dataset `90376a...`; anchor `9db179...` | local corpus | 722 spans | 621 mapped | 101 excluded | TBD | READY | coverage 0.860111 |
| P1 | P1-A | A | TBD | TBD | frozen | TBD | 300 | 0 | 0 | TBD | PLANNED | TBD |
| P2 | P2-A | A | TBD | TBD | frozen | TBD | 300 | 0 | 0 | TBD | BLOCKED_BY_P1 | TBD |
| P2 | P2-B | B | TBD | TBD | frozen | TBD | 400 | 0 | 0 | TBD | BLOCKED_BY_P1 | TBD |
| P3 | P3-A | A | legacy re-index | legacy re-index | P1--P2 lock | Neo4j | 100 | 100 | 0 | see results | COMPLETE | reranker off |
| P3 | P3-B | B | legacy re-index | legacy re-index | P1--P2 lock | Neo4j | 100 | 100 | 0 | see results | LOCKED | reranker on, k20; `locked_phase_3.yaml` |
| P4 | P4-MAX | B | legacy re-index | legacy re-index | P3 lock | local CPU | 100 reranker executions | 100 | 0 | see results | COMPLETE | shared max-rerank bundle |
| P4 | P4-LOCK | A | legacy re-index | legacy re-index | frozen bundle | N/A | 300 | 300 | 0 | see results | LOCKED | retention k20; `locked_phase_4.yaml` |
| P5 | P5-A | A | `06de784...` | `7d9f4b7...` (dirty exception) | P4 k20 frozen context | N/A | 200 | 200 | 0 | shard A verified | COMPLETE | Prompt 1 + Prompt 2 |
| P5 | P5-B | B | `06de784...` | `7d9f4b7...` (dirty exception) | P4 k20 frozen context | N/A | 100 | 100 | 0 | shard B verified | COMPLETE | Prompt 3 |
| P5 | P5-LOCK | A | `06de784...` | current | P4 k20 frozen context | N/A | 300 | 300 | 0 | `0b96bf3...` | LOCKED | Prompt 1=v1; `locked_phase_5.yaml` |
| P6 | P6-A | A | TBD | TBD | frozen context | N/A | Gemini 100 + Qwen 100 | 0 | 0 | TBD | BLOCKED | TBD |
| P6 | P6-B | B | TBD | TBD | frozen context | Kaggle GPU | Gemma 100 | 0 | 0 | TBD | BLOCKED | TBD |
| P7 | P7-A | A | TBD | TBD | frozen | TBD | 100 | 0 | 0 | TBD | BLOCKED | final |
