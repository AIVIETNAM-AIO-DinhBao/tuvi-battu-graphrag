# W6 Evaluation report: w8_abl_02_chunking_prompt_interaction_v1_v2

- Dataset: `D:\University\Năm 3 ĐH\Kì 3 (18th6)\Text Mining\tuvi-battu-graphrag\benchmark\tuvi_golden_dataset\release\tuviqa_v1_release.jsonl`
- Dataset items: 100
- Configs: 6
- Judge backend: `gemini`
- Started: 2026-07-30T02:54:17.358929Z
- Completed: 2026-07-30T03:01:26.950147Z
- Notes: W8-ABL-02 completes the chunking x prompt interaction study by running the two prompt templates not covered by the completed W6/W8 prompt-v3 chunking ablation. Holds retrieval fixed to Graph + Sparse + RRF + BGE reranker, dense off, balanced context assembly, document grading on, Gemini Flash Lite generation. Main variables: chunk_strategy_id in {chunk_fixed_512, chunk_structure_parent_child, chunk_semantic_embedding_bge_m3} and prompt_template_id in {tuvi_generation_v1, tuvi_generation_grounded_v2}. Combine with reports_final/10_chunking_strategy_ablation for the full 3 chunking x 3 prompt matrix.
- Run status: `completed`

## Run identity and provenance

- Identity SHA-256: `6705e1fb81820229f553cc561c37ea010398c01f11d15fa77529416742240270`
- Dataset SHA-256: `90376a87cec29cc22e93dc71b41e054ed2f0183bc515a52aa461fecd43cc008c`
- Manifest SHA-256: `e68fe9690b117153028a08c854ac58aaf8ae2467dbc0a9062473c81c83b3b8b3`
- Evaluator SHA-256: `487e4762a669fec1d4c3059f75d3665b35ad1327ea05ae5de6421dc41487ff8f`
- Git SHA: `94a8ee65b9fad04e1026f2f5f03fa8c771e2e957`
- Git dirty: `False`
- Judge model: `gemini-3.1-flash-lite-preview`
- Checkpoint: `benchmark\tuvi_golden_dataset\reports_final\11_chunking_prompt_interaction_v1_v2\checkpoints\evaluation_checkpoint.json`

## Execution completeness

- Expected pairs: 600
- Completed pairs: 600
- Failed pairs: 0
- Executed pairs: 3
- Resumed pairs: 597

> **Metric policy:** W6-EVAL-02 runs the RAG pipeline directly with the selected `ExperimentConfig`. `Context recall` is the Gemini-judged corpus-grounding score for non-Direct items; Direct/chart-only items are excluded from corpus retrieval/citation metrics and reported through `chart_context_grounding`.

## Overall metrics

| Config | Status | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms | Retrieval p95 ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| fixed_512_prompt_v1_graph_sparse_rrf | completed | 100 | 0.88 | 0.77 | 0.6674 | 0.967 | 0.9918 | 181525.32 | 178549.27 |
| parent_child_prompt_v1_graph_sparse_rrf | completed | 100 | 0.878 | 0.763 | 0.663 | 0.967 | 0.9945 | 119401.33 | 115384.22 |
| semantic_bge_m3_prompt_v1_graph_sparse_rrf | completed | 100 | 0.872 | 0.782 | 0.7055 | 0.967 | 0.9863 | 166491.79 | 163307.54 |
| fixed_512_prompt_v2_graph_sparse_rrf | completed | 100 | 0.813 | 0.683 | 0.5835 | 0.967 | 0.9973 | 147154.61 | 143860.35 |
| parent_child_prompt_v2_graph_sparse_rrf | completed | 100 | 0.859 | 0.715 | 0.6198 | 0.967 | 0.9973 | 100804.93 | 96942.64 |
| semantic_bge_m3_prompt_v2_graph_sparse_rrf | completed | 100 | 0.87 | 0.736 | 0.6385 | 0.967 | 0.9973 | 164979.46 | 161562.29 |

## Failure and fallback summary

| Config | Failed | Generation backend fallback | Judge failure | No context | Retrieval backend fallback | Citation fallback |
|---|---:|---:|---:|---:|---:|---:|
| fixed_512_prompt_v1_graph_sparse_rrf | 0 | 0 | 0 | 0 | 0 | 0 |
| parent_child_prompt_v1_graph_sparse_rrf | 0 | 0 | 0 | 0 | 0 | 0 |
| semantic_bge_m3_prompt_v1_graph_sparse_rrf | 0 | 0 | 0 | 0 | 0 | 0 |
| fixed_512_prompt_v2_graph_sparse_rrf | 0 | 0 | 0 | 0 | 0 | 0 |
| parent_child_prompt_v2_graph_sparse_rrf | 0 | 0 | 0 | 0 | 0 | 0 |
| semantic_bge_m3_prompt_v2_graph_sparse_rrf | 0 | 0 | 0 | 0 | 0 | 0 |

## Ablation analysis

- Baseline config: `baseline_graph_sparse_rrf`
- Preliminary recommendation: `semantic_bge_m3_prompt_v1_graph_sparse_rrf`
  - Preliminary heuristic ranks configs by context recall, citation coverage, faithfulness, answer relevancy, graph hit rate, and a small p95 latency penalty.
  - Selected `semantic_bge_m3_prompt_v1_graph_sparse_rrf` with context_recall_avg=0.7055, citation_coverage_rate=0.9863, p95_latency_ms=166491.79.
  - Treat this as a smoke/first-pass recommendation until official Gemini judge and full dataset runs are complete.

### Context recall ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | semantic_bge_m3_prompt_v1_graph_sparse_rrf | 0.7055 |
| 2 | fixed_512_prompt_v1_graph_sparse_rrf | 0.6674 |
| 3 | parent_child_prompt_v1_graph_sparse_rrf | 0.663 |
| 4 | semantic_bge_m3_prompt_v2_graph_sparse_rrf | 0.6385 |
| 5 | parent_child_prompt_v2_graph_sparse_rrf | 0.6198 |
| 6 | fixed_512_prompt_v2_graph_sparse_rrf | 0.5835 |

### Citation coverage ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | fixed_512_prompt_v2_graph_sparse_rrf | 0.9973 |
| 2 | parent_child_prompt_v2_graph_sparse_rrf | 0.9973 |
| 3 | semantic_bge_m3_prompt_v2_graph_sparse_rrf | 0.9973 |
| 4 | parent_child_prompt_v1_graph_sparse_rrf | 0.9945 |
| 5 | fixed_512_prompt_v1_graph_sparse_rrf | 0.9918 |
| 6 | semantic_bge_m3_prompt_v1_graph_sparse_rrf | 0.9863 |

### Graph hit ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | fixed_512_prompt_v1_graph_sparse_rrf | 0.967 |
| 2 | parent_child_prompt_v1_graph_sparse_rrf | 0.967 |
| 3 | semantic_bge_m3_prompt_v1_graph_sparse_rrf | 0.967 |
| 4 | fixed_512_prompt_v2_graph_sparse_rrf | 0.967 |
| 5 | parent_child_prompt_v2_graph_sparse_rrf | 0.967 |
| 6 | semantic_bge_m3_prompt_v2_graph_sparse_rrf | 0.967 |

### p95 latency ranking

| Rank | Config | Value |
|---:|---|---:|
| 1 | parent_child_prompt_v2_graph_sparse_rrf | 100804.93 |
| 2 | parent_child_prompt_v1_graph_sparse_rrf | 119401.33 |
| 3 | fixed_512_prompt_v2_graph_sparse_rrf | 147154.61 |
| 4 | semantic_bge_m3_prompt_v2_graph_sparse_rrf | 164979.46 |
| 5 | semantic_bge_m3_prompt_v1_graph_sparse_rrf | 166491.79 |
| 6 | fixed_512_prompt_v1_graph_sparse_rrf | 181525.32 |

### Retrieval miss summary

| Config | Miss count | Example item IDs |
|---|---:|---|
| fixed_512_prompt_v1_graph_sparse_rrf | 26 | TVQA-003, TVQA-010, TVQA-012, TVQA-025, TVQA-027 |
| parent_child_prompt_v1_graph_sparse_rrf | 20 | TVQA-003, TVQA-005, TVQA-010, TVQA-022, TVQA-025 |
| semantic_bge_m3_prompt_v1_graph_sparse_rrf | 18 | TVQA-008, TVQA-015, TVQA-022, TVQA-027, TVQA-028 |
| fixed_512_prompt_v2_graph_sparse_rrf | 31 | TVQA-003, TVQA-006, TVQA-010, TVQA-012, TVQA-015 |
| parent_child_prompt_v2_graph_sparse_rrf | 26 | TVQA-003, TVQA-005, TVQA-006, TVQA-008, TVQA-010 |
| semantic_bge_m3_prompt_v2_graph_sparse_rrf | 28 | TVQA-010, TVQA-012, TVQA-015, TVQA-016, TVQA-017 |

### Rerank miss summary

| Config | Miss count | Example item IDs |
|---|---:|---|
| fixed_512_prompt_v1_graph_sparse_rrf | 2 | TVQA-045, TVQA-074 |
| parent_child_prompt_v1_graph_sparse_rrf | 2 | TVQA-025, TVQA-045 |
| semantic_bge_m3_prompt_v1_graph_sparse_rrf | 5 | TVQA-038, TVQA-039, TVQA-045, TVQA-068, TVQA-076 |
| fixed_512_prompt_v2_graph_sparse_rrf | 0 |  |
| parent_child_prompt_v2_graph_sparse_rrf | 0 |  |
| semantic_bge_m3_prompt_v2_graph_sparse_rrf | 1 | TVQA-068 |

## Phân tích ablation chiến lược chunking

- Phạm vi: So sánh chiến lược chunking trên cùng corpus TVKL/TVNL/TVHS/TVGM; biến chính là chunk_strategy_id.
- Ghi chú tên strategy: PLAN.md gọi chiến lược semantic là chunk_semantic_embedding; runtime hiện dùng mã chunk_semantic_embedding_bge_m3.
- Chính sách dense: Matrix chính tắt dense retrieval để không trộn lẫn biến chunking với biến dense retrieval. Retrieval stack cố định là Graph + Sparse + RRF + reranker.
- Các chiến lược được so sánh: `chunk_fixed_512, chunk_semantic_embedding_bge_m3, chunk_structure_parent_child`
- Ứng viên chunking sơ bộ: `chunk_semantic_embedding_bge_m3` qua config `semantic_bge_m3_prompt_v1_graph_sparse_rrf`
  - Đây là gợi ý sơ bộ do máy tính tổng hợp, không phải quyết định production cuối cùng.
  - Điểm ưu tiên Context Recall, Citation Coverage, Graph Hit Rate, sau đó mới xét Faithfulness, Answer Relevancy và phạt nhẹ p95 latency.
  - Ứng viên hiện tại là `chunk_semantic_embedding_bge_m3` qua config `semantic_bge_m3_prompt_v1_graph_sparse_rrf` với context_recall_avg=0.7055, citation_coverage_rate=0.9863, graph_hit_rate=0.967, p95_latency_ms=166491.79.
  - Chỉ được dùng làm bằng chứng chính thức sau khi chạy Gemini judge/live database trên cùng golden dataset và đủ 12 cặp source-strategy.

### Xếp hạng theo Context Recall

| Hạng | Chunk strategy | Config | Giá trị |
|---:|---|---|---:|
| 1 | chunk_semantic_embedding_bge_m3 | semantic_bge_m3_prompt_v1_graph_sparse_rrf | 0.7055 |
| 2 | chunk_fixed_512 | fixed_512_prompt_v1_graph_sparse_rrf | 0.6674 |
| 3 | chunk_structure_parent_child | parent_child_prompt_v1_graph_sparse_rrf | 0.663 |
| 4 | chunk_semantic_embedding_bge_m3 | semantic_bge_m3_prompt_v2_graph_sparse_rrf | 0.6385 |
| 5 | chunk_structure_parent_child | parent_child_prompt_v2_graph_sparse_rrf | 0.6198 |
| 6 | chunk_fixed_512 | fixed_512_prompt_v2_graph_sparse_rrf | 0.5835 |

### Xếp hạng theo Citation Coverage

| Hạng | Chunk strategy | Config | Giá trị |
|---:|---|---|---:|
| 1 | chunk_fixed_512 | fixed_512_prompt_v2_graph_sparse_rrf | 0.9973 |
| 2 | chunk_structure_parent_child | parent_child_prompt_v2_graph_sparse_rrf | 0.9973 |
| 3 | chunk_semantic_embedding_bge_m3 | semantic_bge_m3_prompt_v2_graph_sparse_rrf | 0.9973 |
| 4 | chunk_structure_parent_child | parent_child_prompt_v1_graph_sparse_rrf | 0.9945 |
| 5 | chunk_fixed_512 | fixed_512_prompt_v1_graph_sparse_rrf | 0.9918 |
| 6 | chunk_semantic_embedding_bge_m3 | semantic_bge_m3_prompt_v1_graph_sparse_rrf | 0.9863 |

### Xếp hạng theo Graph Hit Rate

| Hạng | Chunk strategy | Config | Giá trị |
|---:|---|---|---:|
| 1 | chunk_fixed_512 | fixed_512_prompt_v1_graph_sparse_rrf | 0.967 |
| 2 | chunk_structure_parent_child | parent_child_prompt_v1_graph_sparse_rrf | 0.967 |
| 3 | chunk_semantic_embedding_bge_m3 | semantic_bge_m3_prompt_v1_graph_sparse_rrf | 0.967 |
| 4 | chunk_fixed_512 | fixed_512_prompt_v2_graph_sparse_rrf | 0.967 |
| 5 | chunk_structure_parent_child | parent_child_prompt_v2_graph_sparse_rrf | 0.967 |
| 6 | chunk_semantic_embedding_bge_m3 | semantic_bge_m3_prompt_v2_graph_sparse_rrf | 0.967 |

### Xếp hạng theo p95 latency

| Hạng | Chunk strategy | Config | Giá trị |
|---:|---|---|---:|
| 1 | chunk_structure_parent_child | parent_child_prompt_v2_graph_sparse_rrf | 100804.93 |
| 2 | chunk_structure_parent_child | parent_child_prompt_v1_graph_sparse_rrf | 119401.33 |
| 3 | chunk_fixed_512 | fixed_512_prompt_v2_graph_sparse_rrf | 147154.61 |
| 4 | chunk_semantic_embedding_bge_m3 | semantic_bge_m3_prompt_v2_graph_sparse_rrf | 164979.46 |
| 5 | chunk_semantic_embedding_bge_m3 | semantic_bge_m3_prompt_v1_graph_sparse_rrf | 166491.79 |
| 6 | chunk_fixed_512 | fixed_512_prompt_v1_graph_sparse_rrf | 181525.32 |

## Phân tích ablation generation prompt/model

- Phạm vi: So sánh prompt template và generation model, giữ retrieval config cố định để cô lập ảnh hưởng generation.
- Retrieval control: Retrieval stack cố định theo W6 integration candidate: chunk_semantic_embedding_bge_m3, Graph + Sparse + RRF + BGE cross-encoder reranker, dense off.
- Chính sách run: Run chính của task này là Gemini judge partial 10 câu balanced; full/expanded run sẽ để W7-CONFIG-01/W8 hoặc khi quota cho phép.
- Prompt templates: `tuvi_generation_grounded_v2, tuvi_generation_v1`
- Generation models: `gemini-3.1-flash-lite-preview`
- Ứng viên generation sơ bộ: prompt `tuvi_generation_v1` với model `gemini-3.1-flash-lite-preview` qua config `semantic_bge_m3_prompt_v1_graph_sparse_rrf`
  - Đây là gợi ý sơ bộ cho W7-ABL-01 dựa trên partial run, không phải quyết định production cuối cùng.
  - Điểm ưu tiên Faithfulness, Answer Relevancy, Citation Coverage và Chart Context Grounding; p95 latency bị phạt nhẹ.
  - Ứng viên hiện tại là prompt `tuvi_generation_v1` với model `gemini-3.1-flash-lite-preview` qua config `semantic_bge_m3_prompt_v1_graph_sparse_rrf`: faithfulness_avg=0.872, answer_relevancy_avg=0.782, citation_coverage_rate=0.9863, p95_latency_ms=166491.79.
  - W7-CONFIG-01 sẽ tổng hợp thêm evidence retrieval/chunking/latency trước khi lock default_production.yaml.

### Xếp hạng theo Faithfulness

| Hạng | Prompt template | Model | Config | Giá trị |
|---:|---|---|---|---:|
| 1 | tuvi_generation_v1 | gemini-3.1-flash-lite-preview | fixed_512_prompt_v1_graph_sparse_rrf | 0.88 |
| 2 | tuvi_generation_v1 | gemini-3.1-flash-lite-preview | parent_child_prompt_v1_graph_sparse_rrf | 0.878 |
| 3 | tuvi_generation_v1 | gemini-3.1-flash-lite-preview | semantic_bge_m3_prompt_v1_graph_sparse_rrf | 0.872 |
| 4 | tuvi_generation_grounded_v2 | gemini-3.1-flash-lite-preview | semantic_bge_m3_prompt_v2_graph_sparse_rrf | 0.87 |
| 5 | tuvi_generation_grounded_v2 | gemini-3.1-flash-lite-preview | parent_child_prompt_v2_graph_sparse_rrf | 0.859 |
| 6 | tuvi_generation_grounded_v2 | gemini-3.1-flash-lite-preview | fixed_512_prompt_v2_graph_sparse_rrf | 0.813 |

### Xếp hạng theo Answer Relevancy

| Hạng | Prompt template | Model | Config | Giá trị |
|---:|---|---|---|---:|
| 1 | tuvi_generation_v1 | gemini-3.1-flash-lite-preview | semantic_bge_m3_prompt_v1_graph_sparse_rrf | 0.782 |
| 2 | tuvi_generation_v1 | gemini-3.1-flash-lite-preview | fixed_512_prompt_v1_graph_sparse_rrf | 0.77 |
| 3 | tuvi_generation_v1 | gemini-3.1-flash-lite-preview | parent_child_prompt_v1_graph_sparse_rrf | 0.763 |
| 4 | tuvi_generation_grounded_v2 | gemini-3.1-flash-lite-preview | semantic_bge_m3_prompt_v2_graph_sparse_rrf | 0.736 |
| 5 | tuvi_generation_grounded_v2 | gemini-3.1-flash-lite-preview | parent_child_prompt_v2_graph_sparse_rrf | 0.715 |
| 6 | tuvi_generation_grounded_v2 | gemini-3.1-flash-lite-preview | fixed_512_prompt_v2_graph_sparse_rrf | 0.683 |

### Xếp hạng theo Citation Coverage

| Hạng | Prompt template | Model | Config | Giá trị |
|---:|---|---|---|---:|
| 1 | tuvi_generation_grounded_v2 | gemini-3.1-flash-lite-preview | fixed_512_prompt_v2_graph_sparse_rrf | 0.9973 |
| 2 | tuvi_generation_grounded_v2 | gemini-3.1-flash-lite-preview | parent_child_prompt_v2_graph_sparse_rrf | 0.9973 |
| 3 | tuvi_generation_grounded_v2 | gemini-3.1-flash-lite-preview | semantic_bge_m3_prompt_v2_graph_sparse_rrf | 0.9973 |
| 4 | tuvi_generation_v1 | gemini-3.1-flash-lite-preview | parent_child_prompt_v1_graph_sparse_rrf | 0.9945 |
| 5 | tuvi_generation_v1 | gemini-3.1-flash-lite-preview | fixed_512_prompt_v1_graph_sparse_rrf | 0.9918 |
| 6 | tuvi_generation_v1 | gemini-3.1-flash-lite-preview | semantic_bge_m3_prompt_v1_graph_sparse_rrf | 0.9863 |

### Xếp hạng theo p95 latency

| Hạng | Prompt template | Model | Config | Giá trị |
|---:|---|---|---|---:|
| 1 | tuvi_generation_grounded_v2 | gemini-3.1-flash-lite-preview | parent_child_prompt_v2_graph_sparse_rrf | 100804.93 |
| 2 | tuvi_generation_v1 | gemini-3.1-flash-lite-preview | parent_child_prompt_v1_graph_sparse_rrf | 119401.33 |
| 3 | tuvi_generation_grounded_v2 | gemini-3.1-flash-lite-preview | fixed_512_prompt_v2_graph_sparse_rrf | 147154.61 |
| 4 | tuvi_generation_grounded_v2 | gemini-3.1-flash-lite-preview | semantic_bge_m3_prompt_v2_graph_sparse_rrf | 164979.46 |
| 5 | tuvi_generation_v1 | gemini-3.1-flash-lite-preview | semantic_bge_m3_prompt_v1_graph_sparse_rrf | 166491.79 |
| 6 | tuvi_generation_v1 | gemini-3.1-flash-lite-preview | fixed_512_prompt_v1_graph_sparse_rrf | 181525.32 |

## Metrics by question complexity

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| fixed_512_prompt_v1_graph_sparse_rrf | Direct | 10 | 1.0 | 0.86 | 0.6 | 0.0 | 0.75 | 3381.74 |
| fixed_512_prompt_v1_graph_sparse_rrf | One-hop | 46 | 0.8652 | 0.7913 | 0.7087 | 0.9783 | 0.9891 | 182680.54 |
| fixed_512_prompt_v1_graph_sparse_rrf | Two-hop | 44 | 0.8682 | 0.7273 | 0.6257 | 0.9773 | 1.0 | 176929.71 |
| parent_child_prompt_v1_graph_sparse_rrf | Direct | 10 | 1.0 | 0.84 | 0.7 | 0.0 | 0.75 | 4470.31 |
| parent_child_prompt_v1_graph_sparse_rrf | One-hop | 46 | 0.8761 | 0.7609 | 0.6767 | 0.9783 | 0.9946 | 111545.65 |
| parent_child_prompt_v1_graph_sparse_rrf | Two-hop | 44 | 0.8523 | 0.7477 | 0.6477 | 0.9773 | 1.0 | 129335.27 |
| semantic_bge_m3_prompt_v1_graph_sparse_rrf | Direct | 10 | 0.98 | 0.89 | 0.6 | 0.0 | 0.75 | 2805.07 |
| semantic_bge_m3_prompt_v1_graph_sparse_rrf | One-hop | 46 | 0.8696 | 0.7804 | 0.7391 | 0.9783 | 0.9946 | 162416.9 |
| semantic_bge_m3_prompt_v1_graph_sparse_rrf | Two-hop | 44 | 0.85 | 0.7591 | 0.6727 | 0.9773 | 0.983 | 184233.72 |
| fixed_512_prompt_v2_graph_sparse_rrf | Direct | 10 | 1.0 | 0.83 | 0.6 | 0.0 | 0.75 | 2646.01 |
| fixed_512_prompt_v2_graph_sparse_rrf | One-hop | 46 | 0.7891 | 0.6457 | 0.5783 | 0.9783 | 1.0 | 147776.13 |
| fixed_512_prompt_v2_graph_sparse_rrf | Two-hop | 44 | 0.7955 | 0.6886 | 0.5886 | 0.9773 | 1.0 | 138517.4 |
| parent_child_prompt_v2_graph_sparse_rrf | Direct | 10 | 1.0 | 0.82 | 0.4 | 0.0 | 0.75 | 2865.18 |
| parent_child_prompt_v2_graph_sparse_rrf | One-hop | 46 | 0.8609 | 0.7152 | 0.6457 | 0.9783 | 1.0 | 98187.92 |
| parent_child_prompt_v2_graph_sparse_rrf | Two-hop | 44 | 0.825 | 0.6909 | 0.5977 | 0.9773 | 1.0 | 106451.82 |
| semantic_bge_m3_prompt_v2_graph_sparse_rrf | Direct | 10 | 1.0 | 0.83 | 0.6 | 0.0 | 0.75 | 3429.84 |
| semantic_bge_m3_prompt_v2_graph_sparse_rrf | One-hop | 46 | 0.913 | 0.7674 | 0.6913 | 0.9783 | 1.0 | 162429.64 |
| semantic_bge_m3_prompt_v2_graph_sparse_rrf | Two-hop | 44 | 0.7955 | 0.6818 | 0.5841 | 0.9773 | 1.0 | 177629.47 |

## Metrics by question family

| Config | Group | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| fixed_512_prompt_v1_graph_sparse_rrf | core_identity | 10 | 1.0 | 0.86 | 0.6 | 0.0 | 0.75 | 3381.74 |
| fixed_512_prompt_v1_graph_sparse_rrf | dai_van_interpretation | 10 | 0.87 | 0.69 | 0.64 | 1.0 | 1.0 | 151874.73 |
| fixed_512_prompt_v1_graph_sparse_rrf | menh_cuc_relation | 10 | 0.81 | 0.81 | 0.71 | 1.0 | 0.975 | 103520.3 |
| fixed_512_prompt_v1_graph_sparse_rrf | menh_house_interpretation | 10 | 0.92 | 0.72 | 0.62 | 0.9 | 1.0 | 188994.85 |
| fixed_512_prompt_v1_graph_sparse_rrf | menh_tam_hop | 10 | 0.77 | 0.69 | 0.56 | 1.0 | 1.0 | 175968.74 |
| fixed_512_prompt_v1_graph_sparse_rrf | menh_xung_chieu | 10 | 0.9 | 0.62 | 0.49 | 1.0 | 1.0 | 153543.3 |
| fixed_512_prompt_v1_graph_sparse_rrf | special_state_interpretation | 10 | 0.83 | 0.79 | 0.73 | 1.0 | 0.975 | 160677.29 |
| fixed_512_prompt_v1_graph_sparse_rrf | synthesis_judgement | 10 | 0.91 | 0.84 | 0.723 | 0.9 | 1.0 | 214395.63 |
| fixed_512_prompt_v1_graph_sparse_rrf | than_cu_interpretation | 10 | 0.89 | 0.86 | 0.77 | 1.0 | 1.0 | 174489.04 |
| fixed_512_prompt_v1_graph_sparse_rrf | topic_house_plus_relations | 10 | 0.9 | 0.82 | 0.77 | 1.0 | 1.0 | 163558.55 |
| parent_child_prompt_v1_graph_sparse_rrf | core_identity | 10 | 1.0 | 0.84 | 0.7 | 0.0 | 0.75 | 4470.31 |
| parent_child_prompt_v1_graph_sparse_rrf | dai_van_interpretation | 10 | 0.84 | 0.66 | 0.52 | 1.0 | 1.0 | 79103.6 |
| parent_child_prompt_v1_graph_sparse_rrf | menh_cuc_relation | 10 | 1.0 | 0.94 | 0.93 | 1.0 | 1.0 | 69211.8 |
| parent_child_prompt_v1_graph_sparse_rrf | menh_house_interpretation | 10 | 0.89 | 0.7 | 0.653 | 0.9 | 1.0 | 126829.5 |
| parent_child_prompt_v1_graph_sparse_rrf | menh_tam_hop | 10 | 0.74 | 0.64 | 0.54 | 1.0 | 1.0 | 113892.16 |
| parent_child_prompt_v1_graph_sparse_rrf | menh_xung_chieu | 10 | 0.81 | 0.68 | 0.6 | 1.0 | 1.0 | 87488.78 |
| parent_child_prompt_v1_graph_sparse_rrf | special_state_interpretation | 10 | 0.79 | 0.72 | 0.58 | 1.0 | 0.975 | 99922.38 |
| parent_child_prompt_v1_graph_sparse_rrf | synthesis_judgement | 10 | 0.9 | 0.81 | 0.67 | 0.9 | 1.0 | 161223.1 |
| parent_child_prompt_v1_graph_sparse_rrf | than_cu_interpretation | 10 | 0.85 | 0.77 | 0.65 | 1.0 | 1.0 | 109588.92 |
| parent_child_prompt_v1_graph_sparse_rrf | topic_house_plus_relations | 10 | 0.96 | 0.87 | 0.82 | 1.0 | 1.0 | 111118.19 |
| semantic_bge_m3_prompt_v1_graph_sparse_rrf | core_identity | 10 | 0.98 | 0.89 | 0.6 | 0.0 | 0.75 | 2805.07 |
| semantic_bge_m3_prompt_v1_graph_sparse_rrf | dai_van_interpretation | 10 | 0.82 | 0.6 | 0.55 | 1.0 | 0.975 | 128905.4 |
| semantic_bge_m3_prompt_v1_graph_sparse_rrf | menh_cuc_relation | 10 | 1.0 | 0.92 | 0.91 | 1.0 | 1.0 | 105218.16 |
| semantic_bge_m3_prompt_v1_graph_sparse_rrf | menh_house_interpretation | 10 | 0.8 | 0.71 | 0.67 | 0.9 | 1.0 | 167075.6 |
| semantic_bge_m3_prompt_v1_graph_sparse_rrf | menh_tam_hop | 10 | 0.92 | 0.77 | 0.61 | 1.0 | 0.975 | 182063.62 |
| semantic_bge_m3_prompt_v1_graph_sparse_rrf | menh_xung_chieu | 10 | 0.76 | 0.68 | 0.6 | 1.0 | 1.0 | 139989.36 |
| semantic_bge_m3_prompt_v1_graph_sparse_rrf | special_state_interpretation | 10 | 0.72 | 0.66 | 0.58 | 1.0 | 0.975 | 133730.38 |
| semantic_bge_m3_prompt_v1_graph_sparse_rrf | synthesis_judgement | 10 | 0.87 | 0.84 | 0.72 | 0.9 | 1.0 | 202356.25 |
| semantic_bge_m3_prompt_v1_graph_sparse_rrf | than_cu_interpretation | 10 | 0.94 | 0.92 | 0.93 | 1.0 | 1.0 | 162197.02 |
| semantic_bge_m3_prompt_v1_graph_sparse_rrf | topic_house_plus_relations | 10 | 0.91 | 0.83 | 0.79 | 1.0 | 0.975 | 160115.42 |
| fixed_512_prompt_v2_graph_sparse_rrf | core_identity | 10 | 1.0 | 0.83 | 0.6 | 0.0 | 0.75 | 2646.01 |
| fixed_512_prompt_v2_graph_sparse_rrf | dai_van_interpretation | 10 | 0.87 | 0.72 | 0.65 | 1.0 | 1.0 | 111854.31 |
| fixed_512_prompt_v2_graph_sparse_rrf | menh_cuc_relation | 10 | 0.8 | 0.77 | 0.71 | 1.0 | 1.0 | 82149.1 |
| fixed_512_prompt_v2_graph_sparse_rrf | menh_house_interpretation | 10 | 0.66 | 0.39 | 0.29 | 0.9 | 1.0 | 153264.32 |
| fixed_512_prompt_v2_graph_sparse_rrf | menh_tam_hop | 10 | 0.8 | 0.67 | 0.56 | 1.0 | 1.0 | 138067.34 |
| fixed_512_prompt_v2_graph_sparse_rrf | menh_xung_chieu | 10 | 0.51 | 0.41 | 0.33 | 1.0 | 1.0 | 120698.09 |
| fixed_512_prompt_v2_graph_sparse_rrf | special_state_interpretation | 10 | 0.9 | 0.7 | 0.62 | 1.0 | 1.0 | 128644.68 |
| fixed_512_prompt_v2_graph_sparse_rrf | synthesis_judgement | 10 | 0.88 | 0.76 | 0.66 | 0.9 | 1.0 | 172504.35 |
| fixed_512_prompt_v2_graph_sparse_rrf | than_cu_interpretation | 10 | 0.76 | 0.7 | 0.66 | 1.0 | 1.0 | 148835.89 |
| fixed_512_prompt_v2_graph_sparse_rrf | topic_house_plus_relations | 10 | 0.95 | 0.88 | 0.77 | 1.0 | 1.0 | 126954.24 |
| parent_child_prompt_v2_graph_sparse_rrf | core_identity | 10 | 1.0 | 0.82 | 0.4 | 0.0 | 0.75 | 2865.18 |
| parent_child_prompt_v2_graph_sparse_rrf | dai_van_interpretation | 10 | 0.83 | 0.6 | 0.51 | 1.0 | 1.0 | 75768.53 |
| parent_child_prompt_v2_graph_sparse_rrf | menh_cuc_relation | 10 | 0.98 | 0.9 | 0.88 | 1.0 | 1.0 | 55303.89 |
| parent_child_prompt_v2_graph_sparse_rrf | menh_house_interpretation | 10 | 0.89 | 0.63 | 0.51 | 0.9 | 1.0 | 100736.12 |
| parent_child_prompt_v2_graph_sparse_rrf | menh_tam_hop | 10 | 0.68 | 0.6 | 0.46 | 1.0 | 1.0 | 103017.68 |
| parent_child_prompt_v2_graph_sparse_rrf | menh_xung_chieu | 10 | 0.77 | 0.57 | 0.47 | 1.0 | 1.0 | 88828.44 |
| parent_child_prompt_v2_graph_sparse_rrf | special_state_interpretation | 10 | 0.78 | 0.67 | 0.57 | 1.0 | 1.0 | 80225.38 |
| parent_child_prompt_v2_graph_sparse_rrf | synthesis_judgement | 10 | 0.9 | 0.75 | 0.63 | 0.9 | 1.0 | 127480.7 |
| parent_child_prompt_v2_graph_sparse_rrf | than_cu_interpretation | 10 | 0.84 | 0.75 | 0.73 | 1.0 | 1.0 | 99383.71 |
| parent_child_prompt_v2_graph_sparse_rrf | topic_house_plus_relations | 10 | 0.92 | 0.86 | 0.84 | 1.0 | 1.0 | 93628.23 |
| semantic_bge_m3_prompt_v2_graph_sparse_rrf | core_identity | 10 | 1.0 | 0.83 | 0.6 | 0.0 | 0.75 | 3429.84 |
| semantic_bge_m3_prompt_v2_graph_sparse_rrf | dai_van_interpretation | 10 | 0.81 | 0.54 | 0.48 | 1.0 | 1.0 | 141969.39 |
| semantic_bge_m3_prompt_v2_graph_sparse_rrf | menh_cuc_relation | 10 | 0.98 | 0.92 | 0.88 | 1.0 | 1.0 | 109456.17 |
| semantic_bge_m3_prompt_v2_graph_sparse_rrf | menh_house_interpretation | 10 | 0.82 | 0.65 | 0.54 | 0.9 | 1.0 | 157175.9 |
| semantic_bge_m3_prompt_v2_graph_sparse_rrf | menh_tam_hop | 10 | 0.78 | 0.6 | 0.46 | 1.0 | 1.0 | 153929.81 |
| semantic_bge_m3_prompt_v2_graph_sparse_rrf | menh_xung_chieu | 10 | 0.72 | 0.62 | 0.51 | 1.0 | 1.0 | 123643.03 |
| semantic_bge_m3_prompt_v2_graph_sparse_rrf | special_state_interpretation | 10 | 0.84 | 0.74 | 0.59 | 1.0 | 1.0 | 137123.51 |
| semantic_bge_m3_prompt_v2_graph_sparse_rrf | synthesis_judgement | 10 | 0.88 | 0.8 | 0.67 | 0.9 | 1.0 | 185109.02 |
| semantic_bge_m3_prompt_v2_graph_sparse_rrf | than_cu_interpretation | 10 | 0.98 | 0.85 | 0.85 | 1.0 | 1.0 | 166842.86 |
| semantic_bge_m3_prompt_v2_graph_sparse_rrf | topic_house_plus_relations | 10 | 0.89 | 0.81 | 0.77 | 1.0 | 1.0 | 163171.76 |

## Per-question results

### fixed_512_prompt_v1_graph_sparse_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 3225.64 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 2 | 183093.12 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 0.5 | 0.5 | 0.0 | True | 1.0 | 2 | 132697.55 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 85915.91 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 4 | 131191.82 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 177220.19 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 3 | 121252.08 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 5 | 136282.77 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 3 | 143243.93 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.5 | 0.2 | True | 1.0 | 2 | 126801.33 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 2354.81 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.5 | 0.2 | True | 1.0 | 6 | 171724.07 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 160122.82 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 0.8 | 1.0 | 1.0 | True | 1.0 | 3 | 87657.37 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.8 | 1.0 | 0.8 | True | 1.0 | 5 | 131607.39 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 5 | 148875.37 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 3 | 147539.03 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 3 | 164631.78 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 117787.61 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 136101.01 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1495.3 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 1.0 | True | 1.0 | 3 | 184943.93 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 5 | 129284.56 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 0.8 | 1.0 | 1.0 | True | 1.0 | 4 | 100784.79 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 4 | 127165.64 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 169008.3 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.0 | 0.0 | True | 1.0 | 4 | 106487.31 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.2 | 0.2 | True | 1.0 | 4 | 116748.95 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 6 | 175283.69 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 0.9 | 1.0 | 1.0 | True | 1.0 | 6 | 234068.13 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 2213.05 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 4 | 192309.23 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 123690.63 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.5 | True | 1.0 | 2 | 97821.6 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 5 | 135297.23 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 5 | 170144.29 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 3 | 150515.35 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 4 | 129483.08 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.2 | 0.2 | 0.0 | True | 1.0 | 2 | 128527.72 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 3 | 121820.09 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 2220.7 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 107485.13 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 6 | 128325.71 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 3 | 99137.62 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 0.75 | 1 | 181442.8 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 0.2 | 0.4 | 0.2 | True | 1.0 | 4 | 138701.44 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 6 | 156020.71 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 127829.87 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 109688.96 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 7 | 190351.47 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 2580.66 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.5 | 0.2 | True | 1.0 | 3 | 167758.11 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 125099.11 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 0.5 | 0.5 | 0.0 | True | 1.0 | 2 | 105758.45 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 0.9 | 1.0 | 1.0 | True | 1.0 | 4 | 133060.11 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 2 | 102041.55 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 102073.61 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 4 | 102367.33 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 3 | 110689.76 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 162166.16 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 0.7 | 0.6 | False | 0.75 | 1 | 3509.46 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 1.0 | True | 1.0 | 4 | 99644.96 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 178699.86 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 91699.08 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 3 | 89097.23 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 4 | 100761.87 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.5 | 0.3 | True | 1.0 | 3 | 96550.7 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 94068.57 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 4 | 120225.2 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 3 | 117449.16 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 2219.72 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.5 | 0.2 | True | 1.0 | 2 | 128318.91 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 9 | 169342.48 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 0.75 | 1 | 92801.33 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 3 | 115437.77 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.9 | 0.8 | True | 1.0 | 3 | 174439.2 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.8 | 0.5 | True | 1.0 | 3 | 110074.62 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 5 | 126361.37 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 133949.49 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.6 | 0.33 | True | 1.0 | 4 | 114435.16 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 2284.42 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.9 | 0.7 | False | 1.0 | 2 | 128332.84 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 6 | 140220.66 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 7 | 77630.62 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 109497.89 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 4 | 111411.37 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 6 | 120375.21 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 3 | 114954.43 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 149227.82 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.8 | 0.6 | False | 1.0 | 4 | 152902.6 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.5 | None | None | None | 1 | 1936.12 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 6 | 88282.74 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 3 | 146399.22 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 77515.22 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 109167.41 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 0.6 | 0.4 | 0.2 | True | 1.0 | 3 | 92781.0 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.4 | 0.2 | True | 1.0 | 2 | 97999.32 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 0.6 | 0.4 | 0.2 | True | 1.0 | 5 | 120802.89 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 4 | 120218.92 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 137876.48 |  |

### parent_child_prompt_v1_graph_sparse_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 2094.75 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 57814.71 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 0.5 | 0.4 | 0.2 | True | 1.0 | 3 | 98653.91 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 59886.39 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 0.5 | 0.4 | 0.2 | True | 1.0 | 4 | 94052.17 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.8 | True | 1.0 | 4 | 98888.46 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.8 | 0.9 | True | 1.0 | 5 | 81490.38 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 5 | 84025.28 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 82787.44 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.5 | 0.5 | 0.0 | True | 1.0 | 5 | 79967.35 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 2266.52 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.6 | 0.5 | True | 1.0 | 3 | 99386.94 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 6 | 92534.28 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 54840.43 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 61721.24 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 6 | 87822.95 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.8 | True | 1.0 | 3 | 64310.09 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 2 | 63542.09 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 72363.81 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 90636.16 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 2197.11 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.5 | 0.33 | True | 1.0 | 4 | 128935.46 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 3 | 104418.68 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 69025.91 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 1 | 104725.27 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 5 | 119145.85 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 81142.86 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 4 | 73088.22 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 131133.4 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 0.9 | 1.0 | 1.0 | True | 1.0 | 5 | 171924.72 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1287.07 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.5 | 0.4 | True | 1.0 | 8 | 124255.54 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 0.8 | 1.0 | 1.0 | True | 1.0 | 4 | 88279.01 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 55966.64 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 0.2 | 0.2 | 0.2 | True | 1.0 | 6 | 81817.64 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 2 | 100549.42 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 4 | 85645.57 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 4 | 64248.79 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.6 | 0.5 | 0.2 | True | 1.0 | 3 | 74392.56 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 78234.69 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 6273.41 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 77820.59 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 79511.99 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 3 | 53088.12 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 0.0 | True | 0.75 | 1 | 85290.17 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 3 | 81715.42 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 5 | 88996.86 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 69563.81 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 4 | 77400.33 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 148143.35 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 1812.48 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.5 | 0.2 | 0.0 | True | 1.0 | 5 | 99647.68 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 0.8 | 1.0 | 0.6 | True | 1.0 | 3 | 76791.73 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 3 | 63031.41 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.8 | True | 1.0 | 3 | 74008.24 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 5 | 67428.88 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 66186.6 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 6 | 64094.85 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 5 | 69605.99 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 5 | 111338.98 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 0.8 | 0.7 | False | 0.75 | 1 | 2232.23 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 54552.14 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 5 | 103553.67 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 55271.46 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 5 | 51046.17 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 5 | 70595.89 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.4 | 0.5 | True | 1.0 | 4 | 60470.89 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 5 | 50704.99 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 3 | 66168.67 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 4 | 66870.47 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1553.57 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 6 | 83688.59 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 2 | 113819.11 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 69363.9 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 5 | 73155.63 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 3 | 107470.98 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 65300.01 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 5 | 65129.93 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 70148.69 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.6 | 0.5 | True | 1.0 | 5 | 63559.76 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1775.53 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.6 | 0.5 | False | 1.0 | 4 | 84791.48 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 5 | 92752.13 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 49509.05 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 78174.16 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 4 | 81663.88 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 0.9 | 0.8 | 0.8 | True | 1.0 | 4 | 64269.89 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.4 | 0.3 | True | 1.0 | 5 | 54252.87 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 86655.15 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.8 | 0.6 | False | 1.0 | 7 | 93031.57 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.2 | None | None | None | 1 | 2199.63 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 2 | 59377.52 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 2 | 102206.56 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 1.0 | True | 1.0 | 2 | 62644.59 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 6 | 76383.79 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 2 | 68154.76 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.6 | 0.4 | 0.3 | True | 1.0 | 4 | 60085.04 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 4 | 58341.49 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 3 | 68355.37 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 6 | 81410.85 |  |

### semantic_bge_m3_prompt_v1_graph_sparse_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1488.92 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 3 | 95338.32 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 109288.11 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 72076.99 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 3 | 117148.93 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 2 | 147486.6 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 4 | 115268.48 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.2 | 0.2 | True | 1.0 | 6 | 111245.76 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 2 | 110334.89 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 4 | 109397.37 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1745.58 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 4 | 139984.65 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 8 | 135384.74 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 70672.7 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.6 | 0.8 | 0.4 | True | 1.0 | 2 | 88540.0 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 3 | 130397.62 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 2 | 115817.94 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 102379.51 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 105811.23 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 127822.13 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 2982.69 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.2 | 0.0 | True | 1.0 | 3 | 167601.02 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 123209.22 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 91790.22 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 5 | 129901.82 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 5 | 141671.66 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 3 | 99515.31 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.5 | 0.4 | True | 1.0 | 5 | 92677.84 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 0.9 | 1.0 | 1.0 | True | 1.0 | 5 | 164312.42 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 0.9 | 0.9 | 0.8 | True | 1.0 | 5 | 215588.16 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 1654.84 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 3 | 153098.95 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 0.8 | 1.0 | 1.0 | True | 1.0 | 4 | 102687.42 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 85845.11 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 7 | 123808.29 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 3 | 139324.07 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 2 | 134146.59 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 0.0 | 0.0 | 0.0 | True | 0.75 | 1 | 102776.09 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.2 | 0.2 | 0.0 | True | 0.75 | 1 | 119962.59 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 2 | 111921.36 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 1390.26 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 94990.29 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 106501.24 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.6 | 0.5 | True | 1.0 | 2 | 75401.62 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 0.0 | 0.0 | 0.0 | True | 0.75 | 1 | 121286.41 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 2 | 123982.42 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 6 | 144769.81 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 2 | 123563.74 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 113212.61 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 186183.91 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 1971.32 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.2 | 0.0 | True | 1.0 | 4 | 166433.41 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 133185.48 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 3 | 98354.07 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 2 | 133463.84 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.6 | 0.4 | True | 1.0 | 2 | 108906.3 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 111664.63 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 0.8 | 1.0 | True | 1.0 | 4 | 107070.73 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 3 | 117100.22 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 154540.94 |  |
| TVQA-061 | completed | Direct | core_identity | False | 0.8 | 0.7 | 0.6 | False | 0.75 | 1 | 2587.99 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 1.0 | True | 1.0 | 4 | 99411.72 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.9 | 1.0 | True | 1.0 | 3 | 161592.34 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 110834.24 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 6 | 85823.89 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 2 | 185318.77 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.8 | True | 1.0 | 6 | 110408.16 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 2 | 99130.86 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 3 | 127895.99 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 0.8 | 1.0 | 0.8 | True | 1.0 | 3 | 122247.13 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1470.4 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 133437.54 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 2 | 162691.75 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 86027.47 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 0.2 | 0.2 | 0.2 | True | 1.0 | 5 | 108136.16 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | True | 0.75 | 1 | 178085.11 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 2 | 117505.7 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 6 | 133275.85 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 134347.71 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.6 | 0.5 | True | 1.0 | 2 | 125245.05 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1592.66 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | False | 1.0 | 3 | 148961.1 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 150924.13 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 1.0 | True | 1.0 | 4 | 83975.13 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 133948.46 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 5 | 146330.64 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.8 | True | 1.0 | 4 | 113284.19 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 4 | 102868.31 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 154985.75 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 0.8 | 1.0 | 0.8 | False | 1.0 | 3 | 159538.02 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 1967.47 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 5 | 101930.44 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 2 | 144339.27 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 91056.81 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 5 | 103104.54 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.4 | 0.2 | True | 1.0 | 2 | 96830.5 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 2 | 93309.49 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.4 | 0.2 | True | 1.0 | 3 | 84104.05 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.5 | 0.5 | True | 1.0 | 6 | 101561.02 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 5 | 114448.61 |  |

### fixed_512_prompt_v2_graph_sparse_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1505.89 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 3 | 91458.85 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 6 | 103460.94 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 74665.66 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 5 | 113973.36 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 9 | 137491.99 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 3 | 108501.12 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 118505.25 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 4 | 114350.09 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.6 | 0.4 | 0.2 | True | 1.0 | 3 | 96538.69 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1757.37 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.2 | 0.0 | True | 1.0 | 6 | 138097.64 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 4 | 129942.28 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 71534.25 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.6 | 0.5 | 0.2 | True | 1.0 | 5 | 86995.14 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 5 | 114751.3 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 6 | 88955.8 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 4 | 97823.78 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 96130.96 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 111629.43 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1446.94 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.2 | 0.2 | True | 1.0 | 6 | 157573.04 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 107505.4 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 0.5 | 0.5 | 0.0 | True | 1.0 | 7 | 82922.62 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 5 | 105662.99 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 6 | 135127.3 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 5 | 86753.69 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 5 | 88983.85 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 0.9 | 1.0 | 1.0 | True | 1.0 | 6 | 130014.46 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 181704.18 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 1474.15 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.6 | 0.4 | 0.2 | True | 1.0 | 5 | 147998.1 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 97715.8 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 1.0 | True | 1.0 | 3 | 78753.58 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 106824.29 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 3 | 130096.32 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 3 | 118541.87 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 4 | 103725.39 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.5 | 0.2 | True | 1.0 | 4 | 102801.51 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 5 | 97856.84 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 1433.06 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.0 | 0.0 | True | 1.0 | 5 | 85511.97 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 97277.69 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 3 | 73701.93 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.0 | 0.0 | True | 1.0 | 7 | 140648.49 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 4 | 110355.37 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.8 | True | 1.0 | 5 | 122462.27 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 3 | 102106.88 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 95980.3 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 161260.11 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 1923.23 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.2 | 0.0 | True | 1.0 | 3 | 143823.22 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 98556.09 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 0.5 | 0.6 | 0.5 | True | 1.0 | 3 | 81203.68 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 4 | 106129.65 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.5 | 0.4 | True | 1.0 | 2 | 86099.43 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 0.5 | 0.2 | 0.0 | True | 1.0 | 4 | 85539.38 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 85816.19 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.5 | True | 1.0 | 3 | 95071.65 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 138400.23 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 0.7 | 0.6 | False | 0.75 | 1 | 2821.67 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 4 | 84413.87 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.9 | 1.0 | True | 1.0 | 4 | 150247.81 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 77025.86 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 79512.11 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 3 | 86763.33 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 0.2 | 0.2 | 0.2 | True | 1.0 | 5 | 83680.2 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 83450.71 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 3 | 102567.2 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 3 | 98535.82 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1454.82 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.2 | 0.2 | True | 1.0 | 7 | 110148.99 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 0.2 | 0.2 | 0.0 | True | 1.0 | 3 | 147110.22 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 75400.92 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 3 | 89062.16 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 5 | 138538.08 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 4 | 86377.55 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.2 | 0.2 | True | 1.0 | 4 | 96842.93 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 99084.81 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 6 | 100731.13 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1613.45 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.4 | 0.2 | False | 1.0 | 6 | 116947.11 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 6 | 131936.68 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 7 | 72716.33 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 105609.19 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.9 | 0.8 | True | 1.0 | 6 | 107670.22 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.4 | 0.2 | True | 1.0 | 6 | 93474.53 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 0.6 | 0.4 | 0.3 | True | 1.0 | 5 | 92980.99 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 123213.98 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.5 | 0.2 | False | 1.0 | 4 | 131443.61 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.2 | None | None | None | 1 | 2431.32 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 4 | 86940.89 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 8 | 142598.63 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 75949.5 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 100874.47 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 4 | 86386.14 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.2 | 0.2 | 0.2 | True | 1.0 | 5 | 87864.48 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 88166.35 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 4 | 94225.2 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 5 | 109810.65 |  |

### parent_child_prompt_v2_graph_sparse_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1807.32 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 0.9 | True | 1.0 | 4 | 51819.55 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 0.2 | 0.0 | 0.0 | True | 1.0 | 6 | 69771.72 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 2 | 48299.89 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 0.2 | 0.0 | 0.0 | True | 1.0 | 4 | 73983.21 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 0.2 | 0.2 | 0.2 | True | 1.0 | 5 | 87252.21 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 78728.07 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.4 | 0.2 | True | 1.0 | 5 | 84118.6 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 74985.16 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.5 | 0.5 | 0.0 | True | 1.0 | 4 | 67921.85 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1782.49 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.5 | 0.0 | True | 1.0 | 9 | 86814.6 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 7 | 86324.87 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 7 | 51703.96 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 3 | 59128.05 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 6 | 82989.0 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.8 | True | 1.0 | 4 | 61745.55 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 61126.23 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 65359.28 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 83859.04 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1574.38 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 3 | 103130.88 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 3 | 80581.72 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 52671.46 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 7 | 78999.9 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 6 | 92458.07 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.6 | 0.4 | 0.2 | True | 1.0 | 5 | 60680.59 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.4 | 0.3 | True | 1.0 | 5 | 57463.99 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 100744.05 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 132487.52 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 1543.16 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.6 | 0.4 | 0.2 | True | 1.0 | 5 | 97809.19 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 69418.56 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 5 | 52875.15 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 76802.3 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 3 | 107244.22 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 89115.11 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.5 | 0.2 | True | 1.0 | 9 | 61447.74 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.2 | 0.2 | 0.2 | True | 1.0 | 5 | 71585.1 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 3 | 78217.81 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 1707.42 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 60670.34 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 75008.45 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 4 | 51227.68 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.5 | 0.0 | True | 1.0 | 5 | 81228.04 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 3 | 77771.73 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 6 | 88478.07 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 5 | 65562.88 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 66276.26 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 4 | 121361.26 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 1619.0 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.2 | 0.2 | True | 1.0 | 7 | 94424.19 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 72893.14 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 4 | 54099.53 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 1.0 | True | 1.0 | 3 | 72616.76 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 0.0 | 0.2 | 0.0 | True | 1.0 | 5 | 64328.66 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 0.5 | 0.2 | 0.0 | True | 1.0 | 5 | 63104.86 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 1.0 | 0.8 | 1.0 | True | 1.0 | 6 | 59191.83 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 4 | 65666.15 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 4 | 101961.57 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 0.6 | 0.4 | False | 0.75 | 1 | 3241.83 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 6 | 51259.87 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.9 | 1.0 | True | 1.0 | 6 | 98197.13 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 53732.52 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.9 | 0.8 | True | 1.0 | 6 | 48508.49 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 8 | 62851.4 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.0 | 0.0 | True | 1.0 | 7 | 54819.37 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 0.5 | 0.5 | 0.5 | True | 1.0 | 5 | 48750.91 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 3 | 64000.2 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 64239.87 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1628.58 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 0.9 | 0.8 | 0.7 | True | 1.0 | 6 | 75413.54 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 3 | 98160.29 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 1.0 | True | 1.0 | 2 | 50379.87 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 0.2 | 0.3 | 0.0 | True | 1.0 | 7 | 59712.08 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 4 | 97851.9 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 59569.65 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.5 | 0.5 | True | 1.0 | 6 | 61390.76 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 69777.31 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.6 | 0.4 | True | 1.0 | 4 | 60959.04 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 2020.19 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.6 | 0.5 | False | 1.0 | 3 | 79360.53 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 5 | 87890.81 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 49612.09 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 75249.97 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 5 | 78251.2 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.5 | 0.4 | True | 1.0 | 8 | 62416.81 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.4 | 0.3 | True | 1.0 | 7 | 52714.42 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 7 | 84931.12 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.5 | 0.2 | False | 1.0 | 8 | 92373.51 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.2 | None | None | None | 1 | 2404.83 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.4 | 0.2 | True | 1.0 | 4 | 56026.96 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 3 | 100354.55 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 56289.28 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 6 | 69776.0 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.4 | 0.2 | True | 1.0 | 4 | 59504.79 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.6 | 0.5 | 0.4 | True | 1.0 | 4 | 58921.05 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 5 | 57131.73 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 3 | 65245.39 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.6 | 0.5 | True | 1.0 | 7 | 78936.48 |  |

### semantic_bge_m3_prompt_v2_graph_sparse_rrf

| Item | Status | Complexity | Family | Chart-only | Faithfulness | Relevancy | Context recall | Graph hit | Citation coverage | Sources | Latency ms | Error |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| TVQA-001 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1884.45 |  |
| TVQA-002 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 4 | 91021.11 |  |
| TVQA-003 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 102705.39 |  |
| TVQA-004 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 69679.85 |  |
| TVQA-005 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 6 | 108189.61 |  |
| TVQA-006 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 3 | 141339.11 |  |
| TVQA-007 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.8 | 0.8 | True | 1.0 | 4 | 111855.93 |  |
| TVQA-008 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.8 | 1.0 | True | 1.0 | 6 | 107477.14 |  |
| TVQA-009 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 6 | 107098.07 |  |
| TVQA-010 | completed | Two-hop | synthesis_judgement | False | 0.5 | 0.4 | 0.2 | True | 1.0 | 4 | 104610.13 |  |
| TVQA-011 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1771.5 |  |
| TVQA-012 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.4 | 0.2 | True | 1.0 | 6 | 134154.7 |  |
| TVQA-013 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 7 | 132319.26 |  |
| TVQA-014 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 70635.41 |  |
| TVQA-015 | completed | One-hop | special_state_interpretation | False | 0.6 | 0.5 | 0.2 | True | 1.0 | 4 | 87059.2 |  |
| TVQA-016 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 5 | 129648.04 |  |
| TVQA-017 | completed | Two-hop | menh_xung_chieu | False | 0.5 | 0.4 | 0.2 | True | 1.0 | 3 | 95723.3 |  |
| TVQA-018 | completed | One-hop | dai_van_interpretation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 98551.54 |  |
| TVQA-019 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 97935.34 |  |
| TVQA-020 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 114134.03 |  |
| TVQA-021 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1563.63 |  |
| TVQA-022 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 4 | 155443.13 |  |
| TVQA-023 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 118799.46 |  |
| TVQA-024 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 3 | 83133.44 |  |
| TVQA-025 | completed | One-hop | special_state_interpretation | False | 0.8 | 0.8 | 0.7 | True | 1.0 | 5 | 112360.19 |  |
| TVQA-026 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 5 | 133022.18 |  |
| TVQA-027 | completed | Two-hop | menh_xung_chieu | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 5 | 95762.03 |  |
| TVQA-028 | completed | Two-hop | dai_van_interpretation | False | 0.6 | 0.4 | 0.3 | True | 1.0 | 6 | 91995.44 |  |
| TVQA-029 | completed | Two-hop | topic_house_plus_relations | False | 0.9 | 0.9 | 1.0 | True | 1.0 | 6 | 140308.18 |  |
| TVQA-030 | completed | Two-hop | synthesis_judgement | False | 0.9 | 1.0 | 0.8 | True | 1.0 | 5 | 190710.15 |  |
| TVQA-031 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 1526.52 |  |
| TVQA-032 | completed | One-hop | menh_house_interpretation | False | 0.6 | 0.4 | 0.2 | True | 1.0 | 3 | 144168.31 |  |
| TVQA-033 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 97838.11 |  |
| TVQA-034 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 3 | 81314.28 |  |
| TVQA-035 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 7 | 123253.71 |  |
| TVQA-036 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 135730.82 |  |
| TVQA-037 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 124793.85 |  |
| TVQA-038 | completed | Two-hop | dai_van_interpretation | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 7 | 100445.08 |  |
| TVQA-039 | completed | Two-hop | topic_house_plus_relations | False | 0.2 | 0.2 | 0.0 | True | 1.0 | 8 | 115977.95 |  |
| TVQA-040 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 4 | 109360.93 |  |
| TVQA-041 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 1575.1 |  |
| TVQA-042 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 2 | 94146.0 |  |
| TVQA-043 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 99405.39 |  |
| TVQA-044 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.5 | True | 1.0 | 3 | 77155.06 |  |
| TVQA-045 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 0.0 | True | 1.0 | 6 | 120109.89 |  |
| TVQA-046 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.7 | 0.5 | True | 1.0 | 6 | 123818.28 |  |
| TVQA-047 | completed | Two-hop | menh_xung_chieu | False | 0.9 | 0.9 | 0.8 | True | 1.0 | 5 | 122236.47 |  |
| TVQA-048 | completed | Two-hop | dai_van_interpretation | False | 0.9 | 0.9 | 1.0 | True | 1.0 | 4 | 102644.75 |  |
| TVQA-049 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 97936.71 |  |
| TVQA-050 | completed | Two-hop | synthesis_judgement | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 4 | 163202.08 |  |
| TVQA-051 | completed | Direct | core_identity | True | 1.0 | 0.8 | None | None | None | 1 | 1857.47 |  |
| TVQA-052 | completed | One-hop | menh_house_interpretation | False | 0.2 | 0.0 | 0.0 | True | 1.0 | 4 | 129177.79 |  |
| TVQA-053 | completed | One-hop | than_cu_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 114322.31 |  |
| TVQA-054 | completed | One-hop | menh_cuc_relation | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 4 | 80240.56 |  |
| TVQA-055 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.6 | 0.5 | True | 1.0 | 3 | 109876.83 |  |
| TVQA-056 | completed | Two-hop | menh_tam_hop | False | 0.2 | 0.2 | 0.0 | True | 1.0 | 2 | 130759.98 |  |
| TVQA-057 | completed | Two-hop | menh_xung_chieu | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 4 | 115041.11 |  |
| TVQA-058 | completed | Two-hop | dai_van_interpretation | False | 0.8 | 0.4 | 0.3 | True | 1.0 | 5 | 113199.71 |  |
| TVQA-059 | completed | Two-hop | topic_house_plus_relations | False | 0.8 | 0.6 | 0.4 | True | 1.0 | 5 | 125295.15 |  |
| TVQA-060 | completed | Two-hop | synthesis_judgement | False | 0.8 | 1.0 | 0.9 | True | 1.0 | 3 | 174038.4 |  |
| TVQA-061 | completed | Direct | core_identity | False | 1.0 | 0.7 | 0.6 | False | 0.75 | 1 | 3896.12 |  |
| TVQA-062 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 3 | 116461.03 |  |
| TVQA-063 | completed | One-hop | than_cu_interpretation | False | 0.8 | 0.9 | 1.0 | True | 1.0 | 4 | 168519.92 |  |
| TVQA-064 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 103365.7 |  |
| TVQA-065 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 6 | 88683.3 |  |
| TVQA-066 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.0 | 0.0 | True | 1.0 | 7 | 112856.76 |  |
| TVQA-067 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.5 | 0.4 | True | 1.0 | 6 | 105227.93 |  |
| TVQA-068 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.7 | 0.6 | True | 1.0 | 4 | 94307.53 |  |
| TVQA-069 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.7 | True | 1.0 | 4 | 119224.74 |  |
| TVQA-070 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 3 | 117530.16 |  |
| TVQA-071 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 1734.88 |  |
| TVQA-072 | completed | One-hop | menh_house_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 4 | 134597.91 |  |
| TVQA-073 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 2 | 164793.12 |  |
| TVQA-074 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 1.0 | True | 1.0 | 2 | 82211.76 |  |
| TVQA-075 | completed | One-hop | special_state_interpretation | False | 0.0 | 0.0 | 0.0 | True | 1.0 | 6 | 105512.83 |  |
| TVQA-076 | completed | Two-hop | menh_tam_hop | False | 1.0 | 0.9 | 0.8 | True | 1.0 | 3 | 158804.24 |  |
| TVQA-077 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.5 | 0.4 | True | 1.0 | 4 | 120191.38 |  |
| TVQA-078 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.5 | 0.5 | True | 1.0 | 6 | 117756.71 |  |
| TVQA-079 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 7 | 125706.85 |  |
| TVQA-080 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.6 | 0.4 | True | 1.0 | 7 | 117344.13 |  |
| TVQA-081 | completed | Direct | core_identity | True | 1.0 | 1.0 | None | None | None | 1 | 2056.65 |  |
| TVQA-082 | completed | One-hop | menh_house_interpretation | False | 0.8 | 0.7 | 0.6 | False | 1.0 | 3 | 158593.63 |  |
| TVQA-083 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.9 | 0.9 | True | 1.0 | 4 | 162646.26 |  |
| TVQA-084 | completed | One-hop | menh_cuc_relation | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 5 | 89730.94 |  |
| TVQA-085 | completed | One-hop | special_state_interpretation | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 5 | 140824.03 |  |
| TVQA-086 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.9 | 0.8 | True | 1.0 | 6 | 147972.17 |  |
| TVQA-087 | completed | Two-hop | menh_xung_chieu | False | 0.8 | 0.9 | 0.7 | True | 1.0 | 5 | 114072.92 |  |
| TVQA-088 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.4 | 0.2 | True | 1.0 | 7 | 109098.45 |  |
| TVQA-089 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.9 | 1.0 | True | 1.0 | 3 | 181878.33 |  |
| TVQA-090 | completed | Two-hop | synthesis_judgement | False | 1.0 | 0.8 | 0.6 | False | 1.0 | 3 | 178263.19 |  |
| TVQA-091 | completed | Direct | core_identity | True | 1.0 | 0.2 | None | None | None | 1 | 2859.94 |  |
| TVQA-092 | completed | One-hop | menh_house_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 6 | 110366.78 |  |
| TVQA-093 | completed | One-hop | than_cu_interpretation | False | 1.0 | 0.0 | 0.0 | True | 1.0 | 8 | 159682.03 |  |
| TVQA-094 | completed | One-hop | menh_cuc_relation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 2 | 114439.29 |  |
| TVQA-095 | completed | One-hop | special_state_interpretation | False | 1.0 | 1.0 | 1.0 | True | 1.0 | 5 | 132600.65 |  |
| TVQA-096 | completed | Two-hop | menh_tam_hop | False | 0.8 | 0.4 | 0.2 | True | 1.0 | 5 | 115795.0 |  |
| TVQA-097 | completed | Two-hop | menh_xung_chieu | False | 0.6 | 0.5 | 0.4 | True | 1.0 | 5 | 117837.04 |  |
| TVQA-098 | completed | One-hop | dai_van_interpretation | False | 1.0 | 0.4 | 0.2 | True | 1.0 | 3 | 161779.77 |  |
| TVQA-099 | completed | Two-hop | topic_house_plus_relations | False | 1.0 | 0.8 | 0.6 | True | 1.0 | 7 | 120929.88 |  |
| TVQA-100 | completed | Two-hop | synthesis_judgement | False | 0.8 | 0.7 | 0.6 | True | 1.0 | 5 | 133538.5 |  |
