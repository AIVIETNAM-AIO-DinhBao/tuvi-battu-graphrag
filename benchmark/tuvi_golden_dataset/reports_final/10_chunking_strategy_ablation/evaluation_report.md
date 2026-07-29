# W6 Evaluation report: w6_abl_03_chunking_strategy_v1

- Dataset: `D:\University\Năm 3 ĐH\Kì 3 (18th6)\Text Mining\tuvi-battu-graphrag\benchmark\tuvi_golden_dataset\release\tuviqa_v1_release.jsonl`
- Dataset items: 100
- Configs: 3
- Judge backend: `gemini`
- Started: 2026-07-28T14:57:08.241546Z
- Completed: 2026-07-28T23:15:56.686302Z
- Notes: W6-ABL-03 so sánh 3 chiến lược chunking trên cùng bộ corpus TVKL/TVNL/TVHS/TVGM. Biến chính của ablation là chunk_strategy_id. PLAN.md gọi chiến lược semantic là chunk_semantic_embedding; runtime hiện dùng mã chính thức chunk_semantic_embedding_bge_m3, nên manifest này dùng chunk_semantic_embedding_bge_m3 và ghi rõ như alias vận hành. Matrix chính giữ Graph+Sparse+RRF+reranker, tắt dense để không trộn lẫn biến chunking với biến dense retrieval.
- Run status: `completed`

## Run identity and provenance

- Identity SHA-256: `fe12c1a671646f74a9df2e085260441d5364eb86656e2f76f538a8d28aa4eb7c`
- Dataset SHA-256: `90376a87cec29cc22e93dc71b41e054ed2f0183bc515a52aa461fecd43cc008c`
- Manifest SHA-256: `e6c131fa25707566175f6db369ac80d9c71eef4044e8cabbf9d76f025d9a5b77`
- Evaluator SHA-256: `487e4762a669fec1d4c3059f75d3665b35ad1327ea05ae5de6421dc41487ff8f`
- Git SHA: `22ca387b11fec3b96a488fb42ed49a7cfc3b4d5e`
- Git dirty: `True`
- Judge model: `gemini-3.1-flash-lite-preview`
- Checkpoint: `benchmark\tuvi_golden_dataset\reports_final\10_chunking_strategy_ablation\checkpoints\evaluation_checkpoint.json`

## Execution completeness

- Expected pairs: 300
- Completed pairs: 300
- Failed pairs: 0
- Executed pairs: 275
- Resumed pairs: 25

> **Metric policy:** W6-EVAL-02 runs the RAG pipeline directly with the selected `ExperimentConfig`. `Context recall` is the Gemini-judged corpus-grounding score for non-Direct items; Direct/chart-only items are excluded from corpus retrieval/citation metrics and reported through `chart_context_grounding`.

## Overall metrics

| Config | Status | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms | Retrieval p95 ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| fixed_512_graph_sparse_rrf | completed | 100 | 0.894 | 0.794 | 0.7176 | 0.967 | 0.989 | 207600.52 | 199379.74 |
| parent_child_graph_sparse_rrf | completed | 100 | 0.9 | 0.799 | 0.7143 | 0.967 | 0.989 | 123459.13 | 118592.79 |
| semantic_bge_m3_graph_sparse_rrf | completed | 100 | 0.889 | 0.779 | 0.6989 | 0.967 | 0.989 | 168386.94 | 163092.55 |

## Failure and fallback summary

| Config | Failed | Generation backend fallback | Judge failure | No context | Retrieval backend fallback | Citation fallback |
|---|---:|---:|---:|---:|---:|---:|
| fixed_512_graph_sparse_rrf | 0 | 0 | 0 | 0 | 0 | 0 |
| parent_child_graph_sparse_rrf | 0 | 0 | 0 | 0 | 0 | 0 |
| semantic_bge_m3_graph_sparse_rrf | 0 | 0 | 0 | 0 | 0 | 0 |

## Ablation analysis

- Baseline config: `baseline_graph_sparse_rrf`
- Preliminary recommendation: `parent_child_graph_sparse_rrf`
  - Preliminary heuristic ranks configs by context recall, citation coverage, faithfulness, answer relevancy, graph hit rate, and a small p95 latency penalty.
  - Selected `parent_child_graph_sparse_rrf` with context_recall_avg=0.7143, citation_coverage_rate=0.989, p95_latency_ms=123459.13.
  - Treat this as a smoke/first-pass recommendation until official Gemini judge and full dataset runs are complete.

### Context recall ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | fixed_512_graph_sparse_rrf | 0.7176 |
| 2 | parent_child_graph_sparse_rrf | 0.7143 |
| 3 | semantic_bge_m3_graph_sparse_rrf | 0.6989 |

### Citation coverage ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | fixed_512_graph_sparse_rrf | 0.989 |
| 2 | parent_child_graph_sparse_rrf | 0.989 |
| 3 | semantic_bge_m3_graph_sparse_rrf | 0.989 |

### Graph hit ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | fixed_512_graph_sparse_rrf | 0.967 |
| 2 | parent_child_graph_sparse_rrf | 0.967 |
| 3 | semantic_bge_m3_graph_sparse_rrf | 0.967 |

### p95 latency ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | parent_child_graph_sparse_rrf | 123459.13 |
| 2 | semantic_bge_m3_graph_sparse_rrf | 168386.94 |
| 3 | fixed_512_graph_sparse_rrf | 207600.52 |

### Retrieval miss summary

| Config | Miss count | Example item IDs |
|---|---:|---|
| fixed_512_graph_sparse_rrf | 13 | TVQA-010, TVQA-027, TVQA-032, TVQA-038, TVQA-039 |
| parent_child_graph_sparse_rrf | 16 | TVQA-008, TVQA-010, TVQA-025, TVQA-027, TVQA-028 |
| semantic_bge_m3_graph_sparse_rrf | 19 | TVQA-010, TVQA-012, TVQA-015, TVQA-017, TVQA-028 |

### Rerank miss summary

| Config | Miss count | Example item IDs |
|---|---:|---|
| fixed_512_graph_sparse_rrf | 0 |  |
| parent_child_graph_sparse_rrf | 0 |  |
| semantic_bge_m3_graph_sparse_rrf | 1 | TVQA-068 |

## Phân tích ablation chiến lược chunking

- Phạm vi: So sánh chiến lược chunking trên cùng corpus TVKL/TVNL/TVHS/TVGM; biến chính là chunk_strategy_id.
- Ghi chú tên strategy: PLAN.md gọi chiến lược semantic là chunk_semantic_embedding; runtime hiện dùng mã chunk_semantic_embedding_bge_m3.
- Chính sách dense: Matrix chính tắt dense retrieval để không trộn lẫn biến chunking với biến dense retrieval. Retrieval stack cố định là Graph + Sparse + RRF + reranker.
- Các chiến lược được so sánh: `chunk_fixed_512, chunk_semantic_embedding_bge_m3, chunk_structure_parent_child`
- Ứng viên chunking sơ bộ: `chunk_fixed_512` qua config `fixed_512_graph_sparse_rrf`
  - Đây là gợi ý sơ bộ do máy tính tổng hợp, không phải quyết định production cuối cùng.
  - Điểm ưu tiên Context Recall, Citation Coverage, Graph Hit Rate, sau đó mới xét Faithfulness, Answer Relevancy và phạt nhẹ p95 latency.
  - Ứng viên hiện tại là `chunk_fixed_512` qua config `fixed_512_graph_sparse_rrf` với context_recall_avg=0.7176, citation_coverage_rate=0.989, graph_hit_rate=0.967, p95_latency_ms=207600.52.
  - Chỉ được dùng làm bằng chứng chính thức sau khi chạy Gemini judge/live database trên cùng golden dataset và đủ 12 cặp source-strategy.

### Xếp hạng theo Context Recall

| Hạng | Chunk strategy | Config | Giá trị |
|---:|---|---|---:|
| 1 | chunk_fixed_512 | fixed_512_graph_sparse_rrf | 0.7176 |
| 2 | chunk_structure_parent_child | parent_child_graph_sparse_rrf | 0.7143 |
| 3 | chunk_semantic_embedding_bge_m3 | semantic_bge_m3_graph_sparse_rrf | 0.6989 |

### Xếp hạng theo Citation Coverage

| Hạng | Chunk strategy | Config | Giá trị |
|---:|---|---|---:|
| 1 | chunk_fixed_512 | fixed_512_graph_sparse_rrf | 0.989 |
| 2 | chunk_structure_parent_child | parent_child_graph_sparse_rrf | 0.989 |
| 3 | chunk_semantic_embedding_bge_m3 | semantic_bge_m3_graph_sparse_rrf | 0.989 |

### Xếp hạng theo Graph Hit Rate

| Hạng | Chunk strategy | Config | Giá trị |
|---:|---|---|---:|
| 1 | chunk_fixed_512 | fixed_512_graph_sparse_rrf | 0.967 |
| 2 | chunk_structure_parent_child | parent_child_graph_sparse_rrf | 0.967 |
| 3 | chunk_semantic_embedding_bge_m3 | semantic_bge_m3_graph_sparse_rrf | 0.967 |

### Xếp hạng theo p95 latency

| Hạng | Chunk strategy | Config | Giá trị |
|---:|---|---|---:|
| 1 | chunk_structure_parent_child | parent_child_graph_sparse_rrf | 123459.13 |
| 2 | chunk_semantic_embedding_bge_m3 | semantic_bge_m3_graph_sparse_rrf | 168386.94 |
| 3 | chunk_fixed_512 | fixed_512_graph_sparse_rrf | 207600.52 |

## Metrics by question complexity

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| fixed_512_graph_sparse_rrf | Direct | 10 | 1.0 | 0.82 | 0.6 | 0.0 | 0.0 | 6554.7 |
| fixed_512_graph_sparse_rrf | One-hop | 46 | 0.9109 | 0.8 | 0.75 | 0.9783 | 1.0 | 200753.81 |
| fixed_512_graph_sparse_rrf | Two-hop | 44 | 0.8523 | 0.7818 | 0.6864 | 0.9773 | 1.0 | 207658.02 |
| parent_child_graph_sparse_rrf | Direct | 10 | 1.0 | 0.85 | 0.7 | 0.0 | 0.0 | 4976.73 |
| parent_child_graph_sparse_rrf | One-hop | 46 | 0.8913 | 0.7978 | 0.7239 | 0.9783 | 1.0 | 119094.44 |
| parent_child_graph_sparse_rrf | Two-hop | 44 | 0.8864 | 0.7886 | 0.7045 | 0.9773 | 1.0 | 130965.45 |
| semantic_bge_m3_graph_sparse_rrf | Direct | 10 | 1.0 | 0.81 | 0.7 | 0.0 | 0.0 | 4848.15 |
| semantic_bge_m3_graph_sparse_rrf | One-hop | 46 | 0.9022 | 0.7978 | 0.7304 | 0.9783 | 1.0 | 166356.29 |
| semantic_bge_m3_graph_sparse_rrf | Two-hop | 44 | 0.85 | 0.7523 | 0.6659 | 0.9773 | 1.0 | 169559.66 |

## Metrics by question family

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| fixed_512_graph_sparse_rrf | core_identity | 10 | 1.0 | 0.82 | 0.6 | 0.0 | 0.0 | 6554.7 |
| fixed_512_graph_sparse_rrf | dai_van_interpretation | 10 | 0.88 | 0.71 | 0.65 | 1.0 | 1.0 | 181800.14 |
| fixed_512_graph_sparse_rrf | menh_cuc_relation | 10 | 0.92 | 0.9 | 0.91 | 1.0 | 1.0 | 138337.97 |
| fixed_512_graph_sparse_rrf | menh_house_interpretation | 10 | 0.87 | 0.68 | 0.6 | 0.9 | 1.0 | 219136.33 |
| fixed_512_graph_sparse_rrf | menh_tam_hop | 10 | 0.85 | 0.77 | 0.63 | 1.0 | 1.0 | 211848.59 |
| fixed_512_graph_sparse_rrf | menh_xung_chieu | 10 | 0.8 | 0.72 | 0.63 | 1.0 | 1.0 | 187338.73 |
| fixed_512_graph_sparse_rrf | special_state_interpretation | 10 | 0.92 | 0.79 | 0.71 | 1.0 | 1.0 | 215286.42 |
| fixed_512_graph_sparse_rrf | synthesis_judgement | 10 | 0.79 | 0.74 | 0.62 | 0.9 | 1.0 | 233954.14 |
| fixed_512_graph_sparse_rrf | than_cu_interpretation | 10 | 0.95 | 0.91 | 0.87 | 1.0 | 1.0 | 184660.79 |
| fixed_512_graph_sparse_rrf | topic_house_plus_relations | 10 | 0.96 | 0.9 | 0.85 | 1.0 | 1.0 | 193870.16 |
| parent_child_graph_sparse_rrf | core_identity | 10 | 1.0 | 0.85 | 0.7 | 0.0 | 0.0 | 4976.73 |
| parent_child_graph_sparse_rrf | dai_van_interpretation | 10 | 0.73 | 0.62 | 0.53 | 1.0 | 1.0 | 90028.68 |
| parent_child_graph_sparse_rrf | menh_cuc_relation | 10 | 0.98 | 0.93 | 0.88 | 1.0 | 1.0 | 70179.6 |
| parent_child_graph_sparse_rrf | menh_house_interpretation | 10 | 0.88 | 0.72 | 0.68 | 0.9 | 1.0 | 131633.49 |
| parent_child_graph_sparse_rrf | menh_tam_hop | 10 | 0.9 | 0.76 | 0.66 | 1.0 | 1.0 | 121759.31 |
| parent_child_graph_sparse_rrf | menh_xung_chieu | 10 | 0.84 | 0.77 | 0.67 | 1.0 | 1.0 | 107936.52 |
| parent_child_graph_sparse_rrf | special_state_interpretation | 10 | 0.83 | 0.77 | 0.64 | 1.0 | 1.0 | 105364.54 |
| parent_child_graph_sparse_rrf | synthesis_judgement | 10 | 0.91 | 0.77 | 0.64 | 0.9 | 1.0 | 161545.2 |
| parent_child_graph_sparse_rrf | than_cu_interpretation | 10 | 0.95 | 0.88 | 0.84 | 1.0 | 1.0 | 118647.22 |
| parent_child_graph_sparse_rrf | topic_house_plus_relations | 10 | 0.98 | 0.92 | 0.89 | 1.0 | 1.0 | 118428.4 |
| semantic_bge_m3_graph_sparse_rrf | core_identity | 10 | 1.0 | 0.81 | 0.7 | 0.0 | 0.0 | 4848.15 |
| semantic_bge_m3_graph_sparse_rrf | dai_van_interpretation | 10 | 0.66 | 0.58 | 0.53 | 1.0 | 1.0 | 126145.27 |
| semantic_bge_m3_graph_sparse_rrf | menh_cuc_relation | 10 | 1.0 | 0.93 | 0.94 | 1.0 | 1.0 | 105368.37 |
| semantic_bge_m3_graph_sparse_rrf | menh_house_interpretation | 10 | 0.9 | 0.71 | 0.61 | 0.9 | 1.0 | 181483.13 |
| semantic_bge_m3_graph_sparse_rrf | menh_tam_hop | 10 | 0.9 | 0.79 | 0.67 | 1.0 | 1.0 | 166133.5 |
| semantic_bge_m3_graph_sparse_rrf | menh_xung_chieu | 10 | 0.84 | 0.74 | 0.63 | 1.0 | 1.0 | 147862.09 |
| semantic_bge_m3_graph_sparse_rrf | special_state_interpretation | 10 | 0.81 | 0.67 | 0.59 | 1.0 | 1.0 | 145565.8 |
| semantic_bge_m3_graph_sparse_rrf | synthesis_judgement | 10 | 0.89 | 0.77 | 0.69 | 0.9 | 1.0 | 210720.49 |
| semantic_bge_m3_graph_sparse_rrf | than_cu_interpretation | 10 | 0.93 | 0.93 | 0.84 | 1.0 | 1.0 | 166128.43 |
| semantic_bge_m3_graph_sparse_rrf | topic_house_plus_relations | 10 | 0.96 | 0.86 | 0.79 | 1.0 | 1.0 | 164506.0 |

## Per-question results

### fixed_512_graph_sparse_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 6224.23 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 7 | 159194.99 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 160169.57 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 115085.3 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 5 | 242199.1 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 5 | 215268.42 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 4 | 142368.57 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.6 | 0.5 | True | 1.0 | 5 | 165781.96 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 8 | 171082.13 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.5 | 0.5 | 0.2 | True | 1.0 | 3 | 145548.71 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 6825.08 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.5 | 0.5 | True | 1.0 | 6 | 202703.11 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 181785.29 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 154091.32 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.8 | 0.6 | True | 1.0 | 5 | 176633.32 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 207596.93 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 1.0 | True | 1.0 | 5 | 201277.74 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 5 | 194905.92 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 8 | 202561.38 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 181764.4 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4837.37 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 232581.7 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 1.0 | True | 1.0 | 5 | 152900.62 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.9 | 1.0 | True | 1.0 | 6 | 119083.88 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 0.8 | 1.0 | 1.0 | True | 1.0 | 5 | 157520.55 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 5 | 207668.8 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.2 | 0.2 | 0.0 | True | 1.0 | 7 | 131111.27 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 4 | 134022.86 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 183247.56 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 257150.97 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 0.5 | None | None | None | 1 | 2262.6 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.6 | 0.4 | 0.2 | True | 1.0 | 6 | 188625.96 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 7 | 123665.8 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 1.0 | True | 1.0 | 6 | 100525.88 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 7 | 144312.98 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.8 | True | 1.0 | 4 | 178542.44 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 0.9 | 0.9 | 1.0 | True | 1.0 | 3 | 170302.17 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 6 | 141226.68 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.6 | 0.5 | 0.4 | True | 1.0 | 4 | 141847.4 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 3 | 146352.33 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 2090.81 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 0.9 | 0.9 | 0.8 | True | 1.0 | 4 | 117751.78 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 135132.74 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 3 | 100640.55 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.0 | 0.0 | True | 1.0 | 3 | 182393.15 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 7 | 144883.82 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 7 | 160494.21 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 0.9 | 0.9 | 1.0 | True | 1.0 | 4 | 136988.54 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 124133.61 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 205602.47 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3889.36 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.4 | 0.2 | True | 1.0 | 4 | 187789.03 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 0.8 | 1.0 | 0.5 | True | 1.0 | 6 | 134059.47 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.9 | 1.0 | True | 1.0 | 6 | 103882.4 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 133171.14 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 2 | 105944.97 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.8 | 0.5 | True | 1.0 | 3 | 104201.58 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 104985.81 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 5 | 116928.2 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 3 | 166702.95 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 0.7 | 0.6 | False | 0.0 | 1 | 4400.53 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 99095.89 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 176652.49 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 92977.49 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 0.8 | True | 1.0 | 4 | 92150.0 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 3 | 103541.37 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.8 | 0.7 | True | 1.0 | 4 | 100543.46 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 3 | 98418.76 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 4 | 119658.08 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 6 | 116708.32 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3703.2 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 3 | 132282.1 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 4 | 170506.33 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.9 | 0.6 | True | 1.0 | 5 | 89756.3 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 3 | 118932.07 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.9 | 0.8 | True | 1.0 | 4 | 186435.53 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 114989.56 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 7 | 129105.34 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 134792.78 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 0.2 | 0.3 | 0.2 | True | 1.0 | 6 | 136208.36 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4764.2 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.7 | False | 1.0 | 3 | 158806.35 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 177998.35 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 1.0 | True | 1.0 | 5 | 98417.02 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 141078.92 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 4 | 143271.61 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 2 | 116700.47 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 0.6 | 0.4 | 0.5 | True | 1.0 | 5 | 121973.18 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 165160.88 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.5 | 0.2 | False | 1.0 | 8 | 173993.76 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.2 | None | None | None | 1 | 4832.97 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 5 | 110854.26 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 0.9 | 0.9 | 1.0 | True | 1.0 | 4 | 187013.47 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 101783.07 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 5 | 129734.49 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 2 | 113351.89 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 3 | 114052.31 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 4 | 112971.43 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 4 | 124812.06 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 6 | 147193.04 |  |

### parent_child_graph_sparse_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3888.72 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 67915.62 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 90389.49 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 64997.53 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 95848.96 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 3 | 116166.39 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 6 | 98762.64 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.4 | 0.2 | True | 1.0 | 4 | 96756.24 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 97338.52 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.5 | 0.2 | True | 1.0 | 5 | 87677.84 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4594.59 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.5 | 0.5 | True | 1.0 | 4 | 113772.52 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 6 | 110503.57 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 66962.14 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 75213.07 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 6 | 108817.39 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 80865.7 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 6 | 79267.5 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 83133.87 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 7 | 110455.76 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4934.11 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 137436.36 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 104009.52 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 70150.98 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 0.2 | 0.2 | 0.0 | True | 1.0 | 5 | 104045.75 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 4 | 121606.99 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.5 | 0.2 | True | 1.0 | 5 | 80588.82 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.2 | 0.3 | 0.2 | True | 1.0 | 5 | 75481.17 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 132300.15 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 171804.44 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 2148.23 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 5 | 124541.09 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 89254.51 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 6 | 70203.01 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 7 | 99771.87 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 3 | 121883.94 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 107854.55 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 5 | 81806.1 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 5 | 92044.55 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 6 | 94369.27 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 0.7 | None | None | None | 1 | 2738.68 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 2 | 78846.58 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 96379.63 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 5 | 67110.3 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.5 | 0.0 | True | 1.0 | 6 | 106443.55 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 96131.09 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 6 | 108003.59 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 0.9 | 0.9 | 1.0 | True | 1.0 | 5 | 80372.01 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 83337.76 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 8 | 149006.12 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3194.89 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.2 | 0.0 | True | 1.0 | 5 | 112028.89 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 4 | 86689.98 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 4 | 64994.06 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 0.9 | 1.0 | 1.0 | True | 1.0 | 5 | 84964.73 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 3 | 77240.76 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 75450.93 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.7 | True | 1.0 | 6 | 72773.57 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 79400.41 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.5 | 0.2 | True | 1.0 | 5 | 123402.18 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 0.8 | 0.7 | False | 0.0 | 1 | 5011.61 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 6 | 63124.85 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.9 | 0.8 | True | 1.0 | 5 | 117417.36 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 65028.81 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 6 | 58311.74 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 6 | 74640.86 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.8 | True | 1.0 | 7 | 67413.16 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 0.2 | 0.4 | 0.2 | True | 1.0 | 5 | 58193.09 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 6 | 74405.35 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 7 | 75905.72 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3790.26 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 6 | 90280.39 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 5 | 114314.37 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 60798.71 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 7 | 69260.07 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 4 | 114414.18 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 3 | 70737.13 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 5 | 72597.05 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 82126.37 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 6 | 74196.88 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4546.96 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.6 | 0.5 | False | 1.0 | 5 | 96650.96 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 0.9 | 0.8 | 0.8 | True | 1.0 | 5 | 105890.3 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 58703.22 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 92286.17 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 4 | 94516.09 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 7 | 73844.88 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 0.9 | 0.6 | 0.5 | True | 1.0 | 7 | 63936.8 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 101474.04 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.5 | 0.2 | False | 1.0 | 6 | 105002.08 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.2 | None | None | None | 1 | 4566.32 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 4 | 67083.86 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 3 | 119653.47 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 67573.02 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 6 | 85567.12 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 0.6 | 0.4 | 0.2 | True | 1.0 | 2 | 70102.15 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.5 | 0.4 | 0.2 | True | 1.0 | 4 | 70527.21 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 5 | 68232.95 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 5 | 78062.44 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 7 | 93426.84 |  |

### semantic_bge_m3_graph_sparse_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3541.7 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 108492.29 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 124467.03 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 84067.54 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 131989.15 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 3 | 169779.55 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 133129.99 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 6 | 129904.87 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 6 | 127914.99 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.5 | 0.2 | True | 1.0 | 5 | 126560.27 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3885.0 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.5 | 0.0 | True | 1.0 | 6 | 161131.38 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 157103.84 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 84571.2 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.5 | 0.6 | 0.0 | True | 1.0 | 4 | 102602.44 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 6 | 152190.33 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.5 | 0.4 | True | 1.0 | 3 | 116191.88 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 0.9 | 0.9 | 0.8 | True | 1.0 | 5 | 116646.41 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 116339.81 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 136886.77 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4445.56 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 7 | 187919.11 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 3 | 140550.23 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 1.0 | True | 1.0 | 4 | 100375.97 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 5 | 130452.02 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 5 | 156647.91 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 7 | 118062.55 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.2 | 0.2 | 0.2 | True | 1.0 | 7 | 108272.13 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 168313.64 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 225208.34 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 0.5 | None | None | None | 1 | 2326.47 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 6 | 173616.93 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 119745.49 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 98900.48 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 8 | 147041.96 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 5 | 161677.22 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 7 | 152457.15 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 0.2 | 0.2 | 0.0 | True | 1.0 | 6 | 118686.7 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.6 | 0.4 | 0.2 | True | 1.0 | 5 | 137473.91 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 4 | 129273.43 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 2070.92 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 112129.03 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 120145.69 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 4 | 89563.76 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.0 | 0.0 | True | 1.0 | 4 | 143761.61 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 6 | 147174.84 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 5 | 142245.9 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 0.9 | 0.9 | 1.0 | True | 1.0 | 3 | 121550.21 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 117968.27 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 193013.12 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3849.59 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.2 | 0.2 | True | 1.0 | 4 | 157808.53 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 0.5 | 0.8 | 0.2 | True | 1.0 | 4 | 135901.94 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 4 | 96475.68 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 1.0 | True | 1.0 | 4 | 132485.87 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 4 | 113685.67 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 8 | 116152.52 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 0.2 | 0.2 | 0.3 | True | 1.0 | 5 | 111831.38 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 7 | 117760.22 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 0.2 | 0.0 | 0.0 | True | 1.0 | 3 | 161147.3 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 0.8 | 0.7 | False | 0.0 | 1 | 4738.11 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 7 | 104083.43 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 5 | 165501.84 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 107247.15 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 6 | 87661.1 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 6 | 114987.62 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 6 | 109255.93 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.9 | 1.0 | True | 1.0 | 4 | 96976.18 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 3 | 122958.24 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 3 | 120823.71 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4001.21 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 8 | 137432.15 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 166641.1 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 83992.28 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 6 | 108554.04 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 4 | 161176.15 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 3 | 114398.21 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 8 | 119877.9 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 129284.83 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.6 | 0.5 | True | 1.0 | 6 | 124361.18 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 4840.59 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 4 | 151705.84 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 0.9 | True | 1.0 | 6 | 151969.06 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 87656.56 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 136147.46 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.9 | 0.8 | True | 1.0 | 6 | 144757.54 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 3 | 114831.39 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 5 | 105429.61 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 159852.22 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 0.9 | 1.0 | 0.8 | False | 1.0 | 5 | 163065.35 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.0 | None | None | None | 1 | 4854.34 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 5 | 110245.78 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 2 | 164289.12 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 2 | 103072.09 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 7 | 119821.61 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 2 | 110881.36 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.6 | 0.4 | 0.3 | True | 1.0 | 5 | 108912.19 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.4 | 0.2 | True | 1.0 | 4 | 97928.4 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 7 | 117392.9 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 132300.03 |  |
