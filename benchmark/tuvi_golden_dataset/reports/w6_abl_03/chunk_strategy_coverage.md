# Báo cáo kiểm tra coverage W6-ABL-03

- Chế độ kiểm tra: `neo4j`
- Thời điểm tạo: 2026-07-14T17:32:51.778857Z
- Số cặp kỳ vọng: 12
- Số cặp có dữ liệu: 12
- Số cặp thiếu: 0
- Kết luận: Đủ 12 cặp source-strategy cho W6-ABL-03.
- Ghi chú strategy semantic: PLAN.md ghi chunk_semantic_embedding; runtime hiện dùng chunk_semantic_embedding_bge_m3.

## Bảng coverage

| Nguồn | Chunk strategy | Trạng thái | Số chunk | Artifact path |
|---|---|---:|---:|---|
| TVKL | chunk_fixed_512 | present | 347 |  |
| TVNL | chunk_fixed_512 | present | 266 |  |
| TVHS | chunk_fixed_512 | present | 287 |  |
| TVGM | chunk_fixed_512 | present | 258 |  |
| TVKL | chunk_structure_parent_child | present | 1330 |  |
| TVNL | chunk_structure_parent_child | present | 1110 |  |
| TVHS | chunk_structure_parent_child | present | 1138 |  |
| TVGM | chunk_structure_parent_child | present | 924 |  |
| TVKL | chunk_semantic_embedding_bge_m3 | present | 511 |  |
| TVNL | chunk_semantic_embedding_bge_m3 | present | 363 |  |
| TVHS | chunk_semantic_embedding_bge_m3 | present | 439 |  |
| TVGM | chunk_semantic_embedding_bge_m3 | present | 377 |  |

## Cách hiểu kết quả

- `local-artifacts` chỉ kiểm tra file có trong repo, phù hợp smoke cục bộ.
- `neo4j` kiểm tra dữ liệu runtime thật và nên chạy trước official Gemini evaluation.
- Nếu local-artifacts thiếu nhưng Neo4j đủ, W6-ABL-03 vẫn có thể chạy official vì retrieval đọc từ Neo4j.
