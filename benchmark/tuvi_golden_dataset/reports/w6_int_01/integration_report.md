# Báo cáo integration W6-INT-01

- Trạng thái: `pass`
- Diễn giải: Luồng backend/chart/RAG smoke không có P0; tiếp tục kiểm checklist thủ công cho login/UI.
- Bắt đầu: 2026-07-15T13:04:20.224435Z
- Hoàn tất: 2026-07-15T13:05:03.228709Z
- Thời gian chạy: 43004.27 ms
- Config: `D:\University\Năm 3 ĐH\Kì 3 (18th6)\Text Mining\tuvi-battu-graphrag\configs\w6_integration_candidate.yaml`
- Experiment ID: `w6_int_01_candidate_semantic_bge_m3`
- Config hash: `7f3d735a1468fe3edb17c300aff5bfa56ab6993035a83f39e30d2a04e94fa6e6`
- Chunk strategy: `chunk_semantic_embedding_bge_m3`
- Dense retrieval: `False`

## Tóm tắt lỗi

- P0: 0
- P1: 0
- P2: 0

## Bước hệ thống

| Bước | Kết quả | Latency ms | Ghi chú |
|---|---:|---:|---|
| `health` | True | 13.29 | status_code=200 |
| `chart_creation` | True | 34.55 | chart_type=TUVI, palace_count=12 |

## Câu hỏi chat/RAG

| ID | Loại | Pass | Sources | Citation | Complexity | Roles selected | Missing roles | Latency ms |
|---|---|---:|---:|---:|---|---|---|---:|
| `factual_chart_fact` | factual | True | 2 | True | One-hop | generic, house_scope, modifier_effect | star_definition | 10652.81 |
| `interpretive_menh` | interpretive | True | 2 | True | Two-hop | generic, house_scope, modifier_effect, relation_rule, combination_pattern, star_definition |  | 18553.89 |
| `multi_hop_tam_hop_xung_chieu` | multi-hop | True | 2 | True | Two-hop | generic, relation_rule, combination_pattern, house_scope | star_definition | 13741.21 |

## Danh sách bug P0/P1/P2

Không ghi nhận bug P0/P1/P2 trong automated smoke.

## Kết luận

Automated smoke kiểm được backend health, chart engine và RAG retrieval/context/citation ở local runtime.
Checklist login/dashboard/chart detail/citation panel cần kiểm thủ công vì dự án chưa có Playwright/Cypress chính thức.
