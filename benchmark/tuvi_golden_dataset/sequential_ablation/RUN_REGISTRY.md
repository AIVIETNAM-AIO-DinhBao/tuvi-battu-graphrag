# Sequential ablation run registry

Chỉ A cập nhật bảng này sau khi nhận và validate artifact. Một phase chưa có dòng `LOCKED` thì phase sau không được phát ticket.

| Phase | Ticket | Assignee | Manifest SHA | Code SHA | Data/anchor SHA | Snapshot | Expected | Completed | Failed | Artifact SHA | Status | Winner/lock |
|---|---|---|---|---|---|---|---:|---:|---:|---|---|---|
| P0 | P0-A | A | N/A | TBD | dataset `90376a...`; anchor `9db179...` | local corpus | 722 spans | 621 mapped | 101 excluded | TBD | READY | coverage 0.860111 |
| P1 | P1-A | A | TBD | TBD | frozen | TBD | 300 | 0 | 0 | TBD | PLANNED | TBD |
| P2 | P2-A | A | TBD | TBD | frozen | TBD | 300 | 0 | 0 | TBD | BLOCKED_BY_P1 | TBD |
| P2 | P2-B | B | TBD | TBD | frozen | TBD | 400 | 0 | 0 | TBD | BLOCKED_BY_P1 | TBD |
| P3 | P3-FREEZE | A | TBD | TBD | anchor + P2 lock | Neo4j | 100 retrieval states | 0 | 0 | TBD | BLOCKED_BY_P2 | one shared bundle |
| P3 | P3-A | A | TBD | TBD | frozen | TBD | 200 | 0 | 0 | TBD | BLOCKED_BY_P2 | TBD |
| P3 | P3-B | B | TBD | TBD | frozen | TBD | 200 | 0 | 0 | TBD | BLOCKED_BY_P2 | TBD |
| P4 | P4-A | A | TBD | TBD | frozen | TBD | 100 | 0 | 0 | TBD | BLOCKED_BY_P3 | TBD |
| P4 | P4-B | B | TBD | TBD | frozen | TBD | 100 | 0 | 0 | TBD | BLOCKED_BY_P3 | TBD |
| P5 | P5-MAX | B | TBD | TBD | P4 lock | local CPU | 100 reranker executions | 0 | 0 | TBD | CONDITIONAL | one shared bundle |
| P5 | P5-A | A | TBD | TBD | frozen | TBD | 100 | 0 | 0 | TBD | CONDITIONAL | TBD |
| P5 | P5-B | B | TBD | TBD | frozen | TBD | 200 | 0 | 0 | TBD | CONDITIONAL | TBD |
| P6 | P6-A | A | TBD | TBD | frozen context | N/A | Gemini 100 + Qwen 100 | 0 | 0 | TBD | BLOCKED | TBD |
| P6 | P6-B | B | TBD | TBD | frozen context | Kaggle GPU | Gemma 100 | 0 | 0 | TBD | BLOCKED | TBD |
| P7 | P7-A | A | TBD | TBD | frozen | TBD | 100 | 0 | 0 | TBD | BLOCKED | final |
