# Kế hoạch operational để chạy full ablation

## Phase 0 — Chuẩn hoá thư mục output và checkpoint

Tạo các thư mục output riêng, không ghi đè report cũ:

```text
benchmark/tuvi_golden_dataset/reports/full_ablation_chunking/
benchmark/tuvi_golden_dataset/reports/full_ablation_retrieval_matrix_v2/
benchmark/tuvi_golden_dataset/reports/full_ablation_prompt/
benchmark/tuvi_golden_dataset/reports/full_ablation_prompt_v2/        # nếu cần tạo prompt matrix mới
benchmark/tuvi_golden_dataset/reports/targeted_hard_cases/             # optional
evaluation/ablation_final_report.md
```

Nguyên tắc: mỗi full run có checkpoint riêng trong output folder, ví dụ:

```text
.../full_ablation_chunking/checkpoints/evaluation_checkpoint.json
.../full_ablation_chunking/checkpoints/checkpoint_summary.json
```

Không dùng chung checkpoint giữa các manifest vì run identity đã khóa theo manifest/config/dataset/judge.

---

## Phase 1 — Preflight gate

### 1.1 Backend regression test

Chạy subset liên quan evaluator/RAG/config trước:

```powershell
$env:PYTHONPATH='backend'
.\.venv\Scripts\python.exe -m pytest `
  backend/tests/test_experiment_config.py `
  backend/tests/test_rag_evaluation.py `
  backend/tests/test_evaluation_checkpoint.py `
  backend/tests/test_evaluation_runner_resilience.py `
  backend/tests/test_run_eval_cli.py `
  backend/tests/test_rag_retrieval.py `
  backend/tests/test_rag_context_generation_citations.py `
  backend/tests/test_rag_planner.py `
  backend/tests/test_rag_chart_facts.py `
  -q -p no:cacheprovider
```

Nếu fail: dừng và sửa test trước, không chạy full để tránh mất quota Gemini.

### 1.2 Gemini key/model probe

```powershell
.\.venv\Scripts\python.exe scripts/check_gemini_api.py
```

Gate: model generation/judge gọi được, không lộ secret trong log.

### 1.3 Neo4j coverage cho 12 source-strategy pairs

```powershell
.\.venv\Scripts\python.exe scripts/check_w6_abl_03_chunk_coverage.py --mode neo4j
```

Gate bắt buộc:

```text
completed=true
expected_pair_count=12
observed_pair_count=12
missing_pair_count=0
```

### 1.4 Offline smoke 3 manifest

Chạy cực nhỏ để confirm manifest load và report write:

```powershell
.\.venv\Scripts\python.exe scripts/run_eval.py --manifest configs/w6_abl_03_chunking_matrix.yaml --offline-smoke --limit 2 --skip-persistence --output-dir benchmark/tuvi_golden_dataset/reports/preflight_chunking_smoke

.\.venv\Scripts\python.exe scripts/run_eval.py --manifest configs/w8_abl_01_retrieval_matrix_v2.yaml --offline-smoke --limit 2 --skip-persistence --output-dir benchmark/tuvi_golden_dataset/reports/preflight_retrieval_smoke

.\.venv\Scripts\python.exe scripts/run_eval.py --manifest configs/w7_abl_01_generation_prompt_matrix.yaml --offline-smoke --limit 2 --skip-persistence --output-dir benchmark/tuvi_golden_dataset/reports/preflight_prompt_smoke
```

---

## Phase 2 — Full chunking strategy ablation

Manifest:

```text
configs/w6_abl_03_chunking_matrix.yaml
```

Expected workload:

```text
3 configs x 100 items = 300 pairs
```

Run chính thức:

```powershell
$env:PYTHONPATH='backend'
.\.venv\Scripts\python.exe scripts/run_eval.py `
  --manifest configs/w6_abl_03_chunking_matrix.yaml `
  --judge-backend gemini `
  --skip-persistence `
  --checkpoint-dir benchmark/tuvi_golden_dataset/reports/full_ablation_chunking/checkpoints `
  --output-dir benchmark/tuvi_golden_dataset/reports/full_ablation_chunking `
  --max-item-attempts 3 `
  --retry-base-seconds 2
```

Resume:

```powershell
$env:PYTHONPATH='backend'
.\.venv\Scripts\python.exe scripts/run_eval.py `
  --manifest configs/w6_abl_03_chunking_matrix.yaml `
  --judge-backend gemini `
  --skip-persistence `
  --checkpoint-dir benchmark/tuvi_golden_dataset/reports/full_ablation_chunking/checkpoints `
  --output-dir benchmark/tuvi_golden_dataset/reports/full_ablation_chunking `
  --resume `
  --retry-failed `
  --max-item-attempts 3 `
  --retry-base-seconds 2
```

Decision gate sau Phase 2:

- Nếu run `status != completed` hoặc `failed_pair_count > 0`: resume/retry trước khi phân tích.
- Chọn chunking winner theo score chính: `context_recall_avg`, `citation_coverage_rate`, `graph_hit_rate`, rồi xét `p95_latency_ms`.
- Nếu semantic thắng quality nhưng latency quá cao, ghi rõ trade-off, chưa vội đổi stack cho retrieval matrix vì retrieval matrix cần giữ chunking cố định theo baseline hiện tại trừ khi bạn muốn matrix v3.

---

## Phase 3 — Full retrieval / fusion / reranker matrix v2

Manifest:

```text
configs/w8_abl_01_retrieval_matrix_v2.yaml
```

Expected workload:

```text
10 configs x 100 items = 1000 pairs
```

Run chính thức:

```powershell
$env:PYTHONPATH='backend'
.\.venv\Scripts\python.exe scripts/run_eval.py `
  --manifest configs/w8_abl_01_retrieval_matrix_v2.yaml `
  --judge-backend gemini `
  --skip-persistence `
  --checkpoint-dir benchmark/tuvi_golden_dataset/reports/full_ablation_retrieval_matrix_v2/checkpoints `
  --output-dir benchmark/tuvi_golden_dataset/reports/full_ablation_retrieval_matrix_v2 `
  --max-item-attempts 3 `
  --retry-base-seconds 2
```

Resume:

```powershell
$env:PYTHONPATH='backend'
.\.venv\Scripts\python.exe scripts/run_eval.py `
  --manifest configs/w8_abl_01_retrieval_matrix_v2.yaml `
  --judge-backend gemini `
  --skip-persistence `
  --checkpoint-dir benchmark/tuvi_golden_dataset/reports/full_ablation_retrieval_matrix_v2/checkpoints `
  --output-dir benchmark/tuvi_golden_dataset/reports/full_ablation_retrieval_matrix_v2 `
  --resume `
  --retry-failed `
  --max-item-attempts 3 `
  --retry-base-seconds 2
```

Decision gates sau Phase 3:

1. **Retrieval path winner**
   - So sánh `graph_only_rrf`, `sparse_only_rrf`, `dense_only_rrf`, `dense_sparse_rrf`, `graph_dense_rrf`, baseline graph+sparse, all-paths planner dense.
   - Winner không chỉ là Context Recall cao nhất; phải xét thêm `retrieval_p95_ms`, `answer_relevancy_avg`, `citation_coverage_rate`.

2. **Fusion winner**
   - So sánh `baseline_graph_sparse_rrf`, `baseline_weighted_sum`, `baseline_graph_first`.
   - Nếu `graph_first` tăng graph hit nhưng giảm relevancy/citation, không chọn làm default candidate.

3. **Reranker impact**
   - So `baseline_graph_sparse_rrf` vs `baseline_no_reranker`.
   - Nếu reranker làm tăng latency nhiều nhưng không tăng recall/citation, đánh dấu cần bỏ hoặc thay reranker.

4. **Family yếu**
   - Đọc riêng các family: `dai_van_interpretation`, `menh_tam_hop`, `menh_xung_chieu`, `topic_house_plus_relations`, `synthesis_judgement`.

---

## Phase 4 — Prompt / generation ablation

Có 2 nhánh:

### Nhánh A — Nếu retrieval winner vẫn gần default hiện tại

Dùng manifest sẵn có:

```text
configs/w7_abl_01_generation_prompt_matrix.yaml
```

Run:

```powershell
$env:PYTHONPATH='backend'
.\.venv\Scripts\python.exe scripts/run_eval.py `
  --manifest configs/w7_abl_01_generation_prompt_matrix.yaml `
  --judge-backend gemini `
  --skip-persistence `
  --checkpoint-dir benchmark/tuvi_golden_dataset/reports/full_ablation_prompt/checkpoints `
  --output-dir benchmark/tuvi_golden_dataset/reports/full_ablation_prompt `
  --max-item-attempts 3 `
  --retry-base-seconds 2
```

### Nhánh B — Khuyến nghị nếu Phase 3 tìm được retrieval winner khác default

Tạo manifest mới:

```text
configs/w8_abl_02_prompt_matrix_on_best_retrieval.yaml
```

Trong đó giữ nguyên retrieval/chunking winner từ Phase 3, chỉ đổi:

```text
prompt_template_id
generation_model / generation config nếu có
```

Sau đó run:

```powershell
$env:PYTHONPATH='backend'
.\.venv\Scripts\python.exe scripts/run_eval.py `
  --manifest configs/w8_abl_02_prompt_matrix_on_best_retrieval.yaml `
  --judge-backend gemini `
  --skip-persistence `
  --checkpoint-dir benchmark/tuvi_golden_dataset/reports/full_ablation_prompt_v2/checkpoints `
  --output-dir benchmark/tuvi_golden_dataset/reports/full_ablation_prompt_v2 `
  --max-item-attempts 3 `
  --retry-base-seconds 2
```

Mình nghiêng về Nhánh B nếu retrieval matrix có winner rõ, vì prompt ablation mới sạch: prompt được đo trên retrieval stack tốt nhất chứ không bị baseline cũ kéo xuống.

---

## Phase 5 — Optional targeted hard-case wave

Chỉ chạy sau khi đã có full reports, để tiết kiệm quota và tập trung sửa lỗi.

Nguồn hard cases:

- `review_queue.jsonl` từ `w8_eval_01`
- `analysis/latency_outliers.csv`
- items có `context_recall < 0.5`
- family yếu, đặc biệt `dai_van_interpretation`

Nếu `configs/w8_abl_01_priority_wave.yaml` phù hợp sau inspect thì chạy:

```powershell
$env:PYTHONPATH='backend'
.\.venv\Scripts\python.exe scripts/run_eval.py `
  --manifest configs/w8_abl_01_priority_wave.yaml `
  --judge-backend gemini `
  --skip-persistence `
  --checkpoint-dir benchmark/tuvi_golden_dataset/reports/targeted_hard_cases/checkpoints `
  --output-dir benchmark/tuvi_golden_dataset/reports/targeted_hard_cases `
  --max-item-attempts 3 `
  --retry-base-seconds 2
```

Nếu priority manifest chưa đúng, tạo manifest targeted mới thay vì sửa bừa manifest cũ.

---

## Phase 6 — Tổng hợp final report

Sau khi đủ report JSON, tạo:

```text
evaluation/ablation_final_report.md
```

Nội dung report sẽ gồm:

1. **Experiment inventory**: manifest, config name, config hash, status, pair count, resume count, failed count.
2. **Metric tables** cho 3 trục:
   - `faithfulness_avg`
   - `answer_relevancy_avg`
   - `context_recall_avg`
   - `graph_hit_rate`
   - `citation_coverage_rate`
   - `p95_latency_ms`
   - `retrieval_p95_ms`
   - `generation_p95_ms`
3. **Winner theo trục**:
   - chunking
   - retrieval path
   - fusion
   - reranker on/off
   - prompt
4. **Winner theo question family** cho 10 family.
5. **Candidate config research/eval mới**:
   - nếu khác default hiện tại thì tạo `configs/eval_candidate_v3.yaml`, không ghi đè `default_production.yaml` ngay.
   - lock hash và chạy confirm nếu cần.

---

# Tổng workload dự kiến

```text
Chunking:   3 x 100  = 300 pairs
Retrieval: 10 x 100 = 1000 pairs
Prompt:    3 x 100  = 300 pairs
Total:               = 1600 pairs
```

Ước lượng Gemini calls:

```text
~3200 calls
```

Vì vậy thứ tự ưu tiên chạy là:

1. Preflight
2. Full chunking
3. Full retrieval matrix
4. Prompt ablation hoặc prompt v2 theo retrieval winner
5. Optional targeted hard cases
6. Final report