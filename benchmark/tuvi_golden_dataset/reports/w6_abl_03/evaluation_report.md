# W6 Evaluation report: w6_abl_03_chunking_strategy_v1

- Dataset: `D:\University\Năm 3 ĐH\Kì 3 (18th6)\Text Mining\tuvi-battu-graphrag\benchmark\tuvi_golden_dataset\release\tuviqa_v1_release.jsonl`
- Dataset items: 10
- Configs: 3
- Judge backend: `gemini`
- Started: 2026-07-14T17:33:59.828418Z
- Completed: 2026-07-14T17:40:00.690794Z
- Notes: W6-ABL-03 so sánh 3 chiến lược chunking trên cùng bộ corpus TVKL/TVNL/TVHS/TVGM. Biến chính của ablation là chunk_strategy_id. PLAN.md gọi chiến lược semantic là chunk_semantic_embedding; runtime hiện dùng mã chính thức chunk_semantic_embedding_bge_m3, nên manifest này dùng chunk_semantic_embedding_bge_m3 và ghi rõ như alias vận hành. Matrix chính giữ Graph+Sparse+RRF+reranker, tắt dense để không trộn lẫn biến chunking với biến dense retrieval.

> **Metric policy:** W6-EVAL-02 runs the RAG pipeline directly with the selected `ExperimentConfig`. `Context recall` is the Gemini-judged corpus-grounding score for non-Direct items; Direct/chart-only items are excluded from corpus retrieval/citation metrics and reported through `chart_context_grounding`.

## Overall metrics

| Config | Status | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms | Retrieval p95 ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| fixed_512_graph_sparse_rrf | completed | 10 | 0.81 | 0.7 | 0.5556 | 1.0 | 1.0 | 14074.47 | None |
| parent_child_graph_sparse_rrf | completed | 10 | 0.74 | 0.67 | 0.5444 | 1.0 | 1.0 | 7431.16 | None |
| semantic_bge_m3_graph_sparse_rrf | completed | 10 | 0.85 | 0.74 | 0.5444 | 1.0 | 1.0 | 18042.16 | None |

## Ablation analysis

- Baseline config: `baseline_graph_sparse_rrf`
- Preliminary recommendation: `semantic_bge_m3_graph_sparse_rrf`
  - Preliminary heuristic ranks configs by context recall, citation coverage, faithfulness, answer relevancy, graph hit rate, and a small p95 latency penalty.
  - Selected `semantic_bge_m3_graph_sparse_rrf` with context_recall_avg=0.5444, citation_coverage_rate=1.0, p95_latency_ms=18042.16.
  - Treat this as a smoke/first-pass recommendation until official Gemini judge and full dataset runs are complete.

### Context recall ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | fixed_512_graph_sparse_rrf | 0.5556 |
| 2 | parent_child_graph_sparse_rrf | 0.5444 |
| 3 | semantic_bge_m3_graph_sparse_rrf | 0.5444 |

### Citation coverage ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | fixed_512_graph_sparse_rrf | 1.0 |
| 2 | parent_child_graph_sparse_rrf | 1.0 |
| 3 | semantic_bge_m3_graph_sparse_rrf | 1.0 |

### Graph hit ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | fixed_512_graph_sparse_rrf | 1.0 |
| 2 | parent_child_graph_sparse_rrf | 1.0 |
| 3 | semantic_bge_m3_graph_sparse_rrf | 1.0 |

### p95 latency ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | parent_child_graph_sparse_rrf | 7431.16 |
| 2 | fixed_512_graph_sparse_rrf | 14074.47 |
| 3 | semantic_bge_m3_graph_sparse_rrf | 18042.16 |

### Retrieval miss summary

| Config | Miss count | Example item IDs |
|---|---:|---|
| fixed_512_graph_sparse_rrf | 3 | TVQA-003, TVQA-008, TVQA-010 |
| parent_child_graph_sparse_rrf | 3 | TVQA-003, TVQA-008, TVQA-010 |
| semantic_bge_m3_graph_sparse_rrf | 2 | TVQA-003, TVQA-008 |

### Rerank miss summary

| Config | Miss count | Example item IDs |
|---|---:|---|
| fixed_512_graph_sparse_rrf | 0 |  |
| parent_child_graph_sparse_rrf | 0 |  |
| semantic_bge_m3_graph_sparse_rrf | 0 |  |

## Phân tích ablation chiến lược chunking

- Phạm vi: So sánh chiến lược chunking trên cùng corpus TVKL/TVNL/TVHS/TVGM; biến chính là chunk_strategy_id.
- Ghi chú tên strategy: PLAN.md gọi chiến lược semantic là chunk_semantic_embedding; runtime hiện dùng mã chunk_semantic_embedding_bge_m3.
- Chính sách dense: Matrix chính tắt dense retrieval để không trộn lẫn biến chunking với biến dense retrieval. Retrieval stack cố định là Graph + Sparse + RRF + reranker.
- Các chiến lược được so sánh: `chunk_fixed_512, chunk_semantic_embedding_bge_m3, chunk_structure_parent_child`
- Ứng viên chunking sơ bộ: `chunk_semantic_embedding_bge_m3` qua config `semantic_bge_m3_graph_sparse_rrf`
  - Đây là gợi ý sơ bộ do máy tính tổng hợp, không phải quyết định production cuối cùng.
  - Điểm ưu tiên Context Recall, Citation Coverage, Graph Hit Rate, sau đó mới xét Faithfulness, Answer Relevancy và phạt nhẹ p95 latency.
  - Ứng viên hiện tại là `chunk_semantic_embedding_bge_m3` qua config `semantic_bge_m3_graph_sparse_rrf` với context_recall_avg=0.5444, citation_coverage_rate=1.0, graph_hit_rate=1.0, p95_latency_ms=18042.16.
  - Chỉ được dùng làm bằng chứng chính thức sau khi chạy Gemini judge/live database trên cùng golden dataset và đủ 12 cặp source-strategy.

### Xếp hạng theo Context Recall

| Hạng | Chunk strategy | Config | Giá trị |
|---:|---|---|---:|
| 1 | chunk_fixed_512 | fixed_512_graph_sparse_rrf | 0.5556 |
| 2 | chunk_structure_parent_child | parent_child_graph_sparse_rrf | 0.5444 |
| 3 | chunk_semantic_embedding_bge_m3 | semantic_bge_m3_graph_sparse_rrf | 0.5444 |

### Xếp hạng theo Citation Coverage

| Hạng | Chunk strategy | Config | Giá trị |
|---:|---|---|---:|
| 1 | chunk_fixed_512 | fixed_512_graph_sparse_rrf | 1.0 |
| 2 | chunk_structure_parent_child | parent_child_graph_sparse_rrf | 1.0 |
| 3 | chunk_semantic_embedding_bge_m3 | semantic_bge_m3_graph_sparse_rrf | 1.0 |

### Xếp hạng theo Graph Hit Rate

| Hạng | Chunk strategy | Config | Giá trị |
|---:|---|---|---:|
| 1 | chunk_fixed_512 | fixed_512_graph_sparse_rrf | 1.0 |
| 2 | chunk_structure_parent_child | parent_child_graph_sparse_rrf | 1.0 |
| 3 | chunk_semantic_embedding_bge_m3 | semantic_bge_m3_graph_sparse_rrf | 1.0 |

### Xếp hạng theo p95 latency

| Hạng | Chunk strategy | Config | Giá trị |
|---:|---|---|---:|
| 1 | chunk_structure_parent_child | parent_child_graph_sparse_rrf | 7431.16 |
| 2 | chunk_fixed_512 | fixed_512_graph_sparse_rrf | 14074.47 |
| 3 | chunk_semantic_embedding_bge_m3 | semantic_bge_m3_graph_sparse_rrf | 18042.16 |

## Metrics by question complexity

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| fixed_512_graph_sparse_rrf | Direct | 1 | 1.0 | 1.0 | None | None | None | 6442.62 |
| fixed_512_graph_sparse_rrf | One-hop | 5 | 0.76 | 0.66 | 0.48 | 1.0 | 1.0 | 13923.91 |
| fixed_512_graph_sparse_rrf | Two-hop | 4 | 0.825 | 0.675 | 0.65 | 1.0 | 1.0 | 13882.21 |
| parent_child_graph_sparse_rrf | Direct | 1 | 0.0 | 1.0 | None | None | None | 4741.87 |
| parent_child_graph_sparse_rrf | One-hop | 5 | 0.88 | 0.62 | 0.58 | 1.0 | 1.0 | 6804.29 |
| parent_child_graph_sparse_rrf | Two-hop | 4 | 0.75 | 0.65 | 0.5 | 1.0 | 1.0 | 7459.21 |
| semantic_bge_m3_graph_sparse_rrf | Direct | 1 | 1.0 | 1.0 | None | None | None | 7079.43 |
| semantic_bge_m3_graph_sparse_rrf | One-hop | 5 | 0.86 | 0.66 | 0.46 | 1.0 | 1.0 | 16147.4 |
| semantic_bge_m3_graph_sparse_rrf | Two-hop | 4 | 0.8 | 0.775 | 0.65 | 1.0 | 1.0 | 18112.91 |

## Metrics by question family

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| fixed_512_graph_sparse_rrf | core_identity | 1 | 1.0 | 1.0 | None | None | None | 6442.62 |
| fixed_512_graph_sparse_rrf | dai_van_interpretation | 1 | 0.8 | 0.4 | 0.2 | 1.0 | 1.0 | 7095.52 |
| fixed_512_graph_sparse_rrf | menh_cuc_relation | 1 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 10993.32 |
| fixed_512_graph_sparse_rrf | menh_house_interpretation | 1 | 1.0 | 0.8 | 0.5 | 1.0 | 1.0 | 11642.8 |
| fixed_512_graph_sparse_rrf | menh_tam_hop | 1 | 0.8 | 0.4 | 0.5 | 1.0 | 1.0 | 13910.49 |
| fixed_512_graph_sparse_rrf | menh_xung_chieu | 1 | 0.9 | 0.8 | 0.7 | 1.0 | 1.0 | 13458.77 |
| fixed_512_graph_sparse_rrf | special_state_interpretation | 1 | 0.8 | 0.7 | 0.5 | 1.0 | 1.0 | 12785.02 |
| fixed_512_graph_sparse_rrf | synthesis_judgement | 1 | 0.8 | 0.6 | 0.4 | 1.0 | 1.0 | 10041.67 |
| fixed_512_graph_sparse_rrf | than_cu_interpretation | 1 | 0.2 | 0.4 | 0.2 | 1.0 | 1.0 | 14208.63 |
| fixed_512_graph_sparse_rrf | topic_house_plus_relations | 1 | 0.8 | 0.9 | 1.0 | 1.0 | 1.0 | 13721.93 |
| parent_child_graph_sparse_rrf | core_identity | 1 | 0.0 | 1.0 | None | None | None | 4741.87 |
| parent_child_graph_sparse_rrf | dai_van_interpretation | 1 | 0.8 | 0.5 | 0.4 | 1.0 | 1.0 | 6338.75 |
| parent_child_graph_sparse_rrf | menh_cuc_relation | 1 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 5390.97 |
| parent_child_graph_sparse_rrf | menh_house_interpretation | 1 | 0.8 | 0.9 | 1.0 | 1.0 | 1.0 | 6730.75 |
| parent_child_graph_sparse_rrf | menh_tam_hop | 1 | 0.8 | 0.9 | 0.7 | 1.0 | 1.0 | 7379.73 |
| parent_child_graph_sparse_rrf | menh_xung_chieu | 1 | 0.8 | 0.6 | 0.5 | 1.0 | 1.0 | 7008.97 |
| parent_child_graph_sparse_rrf | special_state_interpretation | 1 | 0.8 | 0.7 | 0.5 | 1.0 | 1.0 | 6822.67 |
| parent_child_graph_sparse_rrf | synthesis_judgement | 1 | 0.6 | 0.4 | 0.2 | 1.0 | 1.0 | 7293.23 |
| parent_child_graph_sparse_rrf | than_cu_interpretation | 1 | 1.0 | 0.0 | 0.0 | 1.0 | 1.0 | 6714.14 |
| parent_child_graph_sparse_rrf | topic_house_plus_relations | 1 | 0.8 | 0.7 | 0.6 | 1.0 | 1.0 | 7473.24 |
| semantic_bge_m3_graph_sparse_rrf | core_identity | 1 | 1.0 | 1.0 | None | None | None | 7079.43 |
| semantic_bge_m3_graph_sparse_rrf | dai_van_interpretation | 1 | 1.0 | 0.2 | 0.0 | 1.0 | 1.0 | 8142.41 |
| semantic_bge_m3_graph_sparse_rrf | menh_cuc_relation | 1 | 1.0 | 0.9 | 1.0 | 1.0 | 1.0 | 16542.7 |
| semantic_bge_m3_graph_sparse_rrf | menh_house_interpretation | 1 | 1.0 | 0.8 | 0.6 | 1.0 | 1.0 | 14566.21 |
| semantic_bge_m3_graph_sparse_rrf | menh_tam_hop | 1 | 0.6 | 0.7 | 0.5 | 1.0 | 1.0 | 18148.28 |
| semantic_bge_m3_graph_sparse_rrf | menh_xung_chieu | 1 | 0.8 | 0.7 | 0.6 | 1.0 | 1.0 | 17912.45 |
| semantic_bge_m3_graph_sparse_rrf | special_state_interpretation | 1 | 0.8 | 0.9 | 0.7 | 1.0 | 1.0 | 10562.8 |
| semantic_bge_m3_graph_sparse_rrf | synthesis_judgement | 1 | 0.8 | 0.9 | 0.7 | 1.0 | 1.0 | 14745.35 |
| semantic_bge_m3_graph_sparse_rrf | than_cu_interpretation | 1 | 0.5 | 0.5 | 0.0 | 1.0 | 1.0 | 12373.48 |
| semantic_bge_m3_graph_sparse_rrf | topic_house_plus_relations | 1 | 1.0 | 0.8 | 0.8 | 1.0 | 1.0 | 13731.17 |

## Per-question results

### fixed_512_graph_sparse_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 8 | 6442.62 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.5 | True | 1.0 | 1 | 11642.8 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 0.2 | 0.4 | 0.2 | True | 1.0 | 1 | 14208.63 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 1 | 10993.32 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 4 | 12785.02 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.4 | 0.5 | True | 1.0 | 3 | 13910.49 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 3 | 13458.77 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.4 | 0.2 | True | 1.0 | 3 | 7095.52 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.9 | 1.0 | True | 1.0 | 2 | 13721.93 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 4 | 10041.67 |  |

### parent_child_graph_sparse_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 0.0 | 1.0 | None | None | None | 8 | 4741.87 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.9 | 1.0 | True | 1.0 | 5 | 6730.75 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.0 | 0.0 | True | 1.0 | 8 | 6714.14 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 1 | 5390.97 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 3 | 6822.67 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 1 | 7379.73 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 1 | 7008.97 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.5 | 0.4 | True | 1.0 | 3 | 6338.75 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 3 | 7473.24 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.6 | 0.4 | 0.2 | True | 1.0 | 4 | 7293.23 |  |

### semantic_bge_m3_graph_sparse_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 8 | 7079.43 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 1 | 14566.21 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 0.5 | 0.5 | 0.0 | True | 1.0 | 1 | 12373.48 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 2 | 16542.7 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 3 | 10562.8 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 0.6 | 0.7 | 0.5 | True | 1.0 | 3 | 18148.28 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 1 | 17912.45 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.2 | 0.0 | True | 1.0 | 4 | 8142.41 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 3 | 13731.17 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 14745.35 |  |
