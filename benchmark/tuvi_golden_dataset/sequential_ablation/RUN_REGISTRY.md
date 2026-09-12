# Sequential ablation run registry

Chỉ A cập nhật bảng này sau khi nhận và validate artifact. Một phase chưa có dòng `LOCKED` thì phase sau không được phát ticket.

| Phase | Ticket | Assignee | Manifest SHA | Code SHA | Data/anchor SHA | Snapshot | Expected | Completed | Failed | Artifact SHA | Status | Winner/lock |
|---|---|---|---|---|---|---|---:|---:|---:|---|---|---|
| P0 | P0-A | A | N/A | TBD | dataset `90376a...`; anchor `9db179...` | local corpus | 722 spans | 621 mapped | 101 excluded | TBD | READY | coverage 0.860111 |
| P1 | P1-A | A | TBD | TBD | frozen | TBD | 300 | 0 | 0 | TBD | PLANNED | TBD |
| P2 | P2-A | A | TBD | TBD | frozen | TBD | 300 | 0 | 0 | TBD | BLOCKED_BY_P1 | TBD |
| P2 | P2-B | B | TBD | TBD | frozen | TBD | 400 | 0 | 0 | TBD | BLOCKED_BY_P1 | TBD |
| P3 | P3-FREEZE | A | `697737...` | `a2a2bb7` | anchor + P2 lock | Neo4j | 100 retrieval states | 100 | 0 | `5c49eb...` | COMPLETE | shared bundle, hash `5c49eb...` |
| P3 | P3-A | A | `697737...` | `a2a2bb7` | frozen bundle | N/A | 200 | 200 | 0 | `a3b954...` | COMPLETE | Prompt 1 + Prompt 2 |
| P3 | P3-B | B | `697737...` | `a2a2bb7` | frozen bundle | N/A | 100 | 100 | 0 | `c899da...` | COMPLETE | Prompt 3 |
| P3 | P3-LOCK | A | `697737...` | `a2a2bb7` | frozen bundle | N/A | 300 | 300 | 0 | `6f70bf...` | LOCKED | `p3_prompt_1`; `locked_phase_3.yaml` |
| P4 | P4-A | A | TBD | TBD | P1--P3 locked | Neo4j | 100 | 0 | 0 | TBD | READY_TO_PREPARE | reranker off |
| P4 | P4-B | B | TBD | TBD | P1--P3 locked | Neo4j | 100 | 0 | 0 | TBD | READY_TO_PREPARE | reranker on, k20 |
| P5 | P5-MAX | B | TBD | TBD | P4 lock | local CPU | 100 reranker executions | 0 | 0 | TBD | CONDITIONAL | one shared bundle |
| P5 | P5-A | A | TBD | TBD | frozen | TBD | 100 | 0 | 0 | TBD | CONDITIONAL | TBD |
| P5 | P5-B | B | TBD | TBD | frozen | TBD | 200 | 0 | 0 | TBD | CONDITIONAL | TBD |
| P6 | P6-A | A | TBD | TBD | frozen context | N/A | Gemini 100 + Qwen 100 | 0 | 0 | TBD | BLOCKED | TBD |
| P6 | P6-B | B | TBD | TBD | frozen context | Kaggle GPU | Gemma 100 | 0 | 0 | TBD | BLOCKED | TBD |
| P7 | P7-A | A | TBD | TBD | frozen | TBD | 100 | 0 | 0 | TBD | BLOCKED | final |
