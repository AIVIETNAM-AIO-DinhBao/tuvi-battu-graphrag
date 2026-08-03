# Bàn giao chạy shard W8 truy xuất / hợp nhất / xếp hạng lại

Cập nhật: `2026-08-03`

Mục tiêu: chia ma trận W8 truy xuất / hợp nhất / xếp hạng lại cho 3 người chạy song song, mỗi người chỉ ghi vào thư mục shard riêng để không đè checkpoint/report của nhau.

Tài liệu này viết theo kiểu “cầm tay chỉ việc”. Mỗi người chỉ cần đọc đúng phần của mình: **Người A**, **Người B**, hoặc **Người C**.

## 0. Bối cảnh cố định

- Thư mục gốc repo: chạy tất cả lệnh PowerShell từ thư mục gốc repo.
- Dataset chính thức: `benchmark/tuvi_golden_dataset/release/tuviqa_v1_release.jsonl`.
- Số item dataset: `100`.
- Bộ chấm chính thức: `gemini`.
- Ghi dữ liệu ngoài: dùng `--skip-persistence`; các tệp kết quả local là nguồn dữ liệu chính.
- Không chạy nhiều người vào thư mục output gốc `20_retrieval_fusion_reranker_matrix/`.
- Mỗi người chỉ chạy manifest shard được giao.

## 1. Vì sao shard này dùng `structured_v3`, không dùng prompt v1?

Không tự ý đổi prompt/chunking/generation model trong shard.

Kết quả Chunking × Prompt 3×3 đã hoàn tất chỉ ra:

- Ô cấu hình thắng chung cuộc: `parent_child_graph_sparse_rrf` = `chunk_structure_parent_child` + `tuvi_generation_structured_v3`, điểm `0.749`.
- Prompt thắng theo trung bình biên: `tuvi_generation_structured_v3`, điểm `0.745`.
- `tuvi_generation_v1` đứng sau, điểm `0.729`.

Ma trận W8 truy xuất / hợp nhất / xếp hạng lại đang cần cô lập các biến đường truy xuất, phương pháp hợp nhất, và bật/tắt bộ xếp hạng lại. Vì vậy prompt được giữ cố định theo `configs/default_production.yaml`:

```yaml
prompt_template_id: tuvi_generation_structured_v3
```

Nếu thấy tài liệu cũ ghi “prompt v1” thì coi đó là tài liệu lỗi thời, không được sửa shard về prompt v1.

## 2. Luật chung bắt buộc cho cả 3 người

1. Chỉ bắt đầu sau khi người phụ trách chính báo đã push commit setup/tag freeze.
2. Phải tạo branch riêng cho shard của mình trước khi chạy.
3. Không sửa:
   - `configs/default_production.yaml`
   - các manifest chuẩn/shard
   - dataset release
   - kết quả đã hoàn tất trong `10_chunking_strategy_ablation/` và `11_chunking_prompt_interaction_v1_v2/`
   - báo cáo cuối trong `evaluation/` hoặc `90_final_report/`
4. Không chạy manifest đầy đủ `configs/w8_abl_01_retrieval_matrix_v2.yaml` nếu đang làm shard được giao.
5. Luôn dùng đúng option:
   - `--judge-backend gemini`
   - `--skip-persistence`
   - `--max-item-attempts 2`
   - `--retry-base-seconds 2`
6. Nếu bị hết hạn mức Gemini / gián đoạn / crash, không xóa checkpoint. Chạy lại đúng lệnh của shard mình và thêm `--resume --retry-failed`.
7. Chỉ commit các tệp kết quả trong thư mục shard của mình.
8. Không commit `.env`, API key, `.venv/`, cache, notebook checkpoint.

## 3. Chuẩn bị máy local trước khi chạy shard

Cả Người A/B/C đều làm mục này một lần sau khi đã pull được code mới. Nếu máy đã có sẵn `.venv`, `.env`, model và đã chạy được evaluation trước đó thì vẫn phải chạy các lệnh kiểm tra ở cuối mục này.

### 3.1. Nhận và đặt file `.env`

Người phụ trách chính gửi riêng file `.env` qua kênh an toàn. Không commit file này.

Đặt `.env` ở thư mục gốc repo:

```text
.env
```

Code cũng hỗ trợ `backend/.env`, nhưng để thống nhất thì dùng `.env` ở root repo.

Biến tối thiểu cần có:

```text
GEMINI_API_KEYS=...
NEO4J_URI=...
NEO4J_USERNAME=...
NEO4J_PASSWORD=...
NEO4J_DATABASE=...
```

Kiểm tra file `.env` đã có chưa:

```powershell
Test-Path .\.env
```

Kết quả phải là `True`.

### 3.2. Tạo `.venv` và cài dependency

Chạy từ thư mục gốc repo:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

Cài wrapper Tử Vi engine:

```powershell
cd backend
.\setup_lasotuvi.ps1
cd ..
```

Nếu PowerShell chặn chạy script, dùng:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
cd backend
.\setup_lasotuvi.ps1
cd ..
```

Kiểm tra Python trong `.venv`:

```powershell
Test-Path .\.venv\Scripts\python.exe
.\.venv\Scripts\python.exe --version
```

### 3.3. Tải model reranker local vào `models/`

Repo không commit thư mục `models/`, nên pull `main` sẽ **không** có model reranker. Shard A/B/C đều có config dùng reranker, vì vậy cả 3 người đều cần model này.

Đường dẫn bắt buộc:

```text
models/bge-reranker-v2-m3
```

Trong `configs/default_production.yaml` đang cố định:

```yaml
reranker_config:
  enabled: true
  local_files_only: true
  local_model_path: models/bge-reranker-v2-m3
```

Tiếp theo, giải nén/copy nguyên thư mục model từ người phụ trách chính vào đúng đường dẫn:

```text
models/bge-reranker-v2-m3
```

Dung lượng model reranker khoảng vài GB. Không commit thư mục `models/`.

Kiểm tra model đã đủ file chính:

```powershell
Test-Path .\models\bge-reranker-v2-m3\config.json
Test-Path .\models\bge-reranker-v2-m3\model.safetensors
Test-Path .\models\bge-reranker-v2-m3\tokenizer.json
```

Cả 3 dòng phải trả về `True`.

### 3.4. Lưu ý riêng cho shard B/C có dense retrieval

Người B và Người C có config dùng dense retrieval, nên ngoài reranker còn cần:

- Neo4j phải có vector index `chunkVectorBgeM3`.
- Neo4j phải có dữ liệu/chunk embedding slot `bge_m3` đúng 1024 chiều.
- Máy có thể cần tải/cache model query embedding `BAAI/bge-m3` lần đầu.

Nếu muốn tải/cache `BAAI/bge-m3` trước khi chạy shard B/C, chạy:

```powershell
.\.venv\Scripts\python.exe -c "from FlagEmbedding import BGEM3FlagModel; BGEM3FlagModel('BAAI/bge-m3', use_fp16=True)"
```

Nếu lệnh trên fail do thiếu quyền mạng/Hugging Face hoặc thiếu RAM/disk, báo người phụ trách chính trước khi chạy shard B/C.

### 3.5. Kiểm tra nhanh trước khi chạy shard

```powershell
$env:PYTHONPATH='backend'
Test-Path .\.env
Test-Path .\.venv\Scripts\python.exe
Test-Path .\models\bge-reranker-v2-m3\model.safetensors
.\.venv\Scripts\python.exe -m pytest backend/tests/test_w8_retrieval_matrix.py backend/tests/test_run_eval_cli.py -q -p no:cacheprovider
.\.venv\Scripts\python.exe scripts\check_gemini_api.py --model gemini-3.1-flash-lite-preview
```

Nếu một dòng `Test-Path` trả về `False`, hoặc pytest/Gemini check fail, thì dừng và báo người phụ trách chính.

## 4. Bảng phân công nhanh

| Người | Shard | Branch | Manifest | Thư mục output | Config được chạy | Số cặp kỳ vọng |
|---|---|---|---|---|---|---:|
| A | controls | `run/w8-retrieval-shard-a-controls` | `configs/w8_abl_01_retrieval_matrix_v2_shard_a_controls.yaml` | `benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/shards/shard_a_controls` | `baseline_graph_sparse_rrf`, `baseline_no_reranker`, `baseline_weighted_sum`, `baseline_graph_first` | 400 |
| B | single paths | `run/w8-retrieval-shard-b-single-paths` | `configs/w8_abl_01_retrieval_matrix_v2_shard_b_single_paths.yaml` | `benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/shards/shard_b_single_paths` | `graph_only_rrf`, `sparse_only_rrf`, `dense_only_rrf` | 300 |
| C | dense combos | `run/w8-retrieval-shard-c-dense-combos` | `configs/w8_abl_01_retrieval_matrix_v2_shard_c_dense_combos.yaml` | `benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/shards/shard_c_dense_combos` | `dense_sparse_rrf`, `graph_dense_rrf`, `all_paths_planner_dense_rrf` | 300 |

## 5. Việc của Người A — shard controls

Người A chỉ làm shard A.

### A.1. Lấy `main` mới nhất và tạo branch A

```powershell
git fetch origin --tags
git switch main
git pull --ff-only origin main
git status --short
git --no-pager log -1 --oneline --decorate
git switch -c run/w8-retrieval-shard-a-controls
git branch --show-current
```

Kỳ vọng:

- `git status --short` không in gì trước khi tạo branch.
- `git branch --show-current` in ra `run/w8-retrieval-shard-a-controls`.

Nếu người phụ trách chính yêu cầu tạo branch từ tag freeze `w8-retrieval-v2-run-freeze`, dùng lệnh tạo branch này thay cho lệnh `git switch -c ...` ở trên:

```powershell
git switch -c run/w8-retrieval-shard-a-controls w8-retrieval-v2-run-freeze
```

### A.2. Kiểm tra môi trường trước khi chạy lâu

```powershell
$env:PYTHONPATH='backend'
Test-Path .\.env
Test-Path .\.venv\Scripts\python.exe
Test-Path .\models\bge-reranker-v2-m3\model.safetensors
.\.venv\Scripts\python.exe -m pytest backend/tests/test_w8_retrieval_matrix.py backend/tests/test_run_eval_cli.py -q -p no:cacheprovider
.\.venv\Scripts\python.exe scripts\check_gemini_api.py --model gemini-3.1-flash-lite-preview
```

Nếu một dòng `Test-Path` trả về `False`, hoặc pytest/Gemini check fail, thì dừng, báo người phụ trách chính, không chạy shard.

### A.3. Chạy shard A lần đầu

```powershell
$env:PYTHONPATH='backend'
.\.venv\Scripts\python.exe scripts\run_eval.py `
  --manifest configs/w8_abl_01_retrieval_matrix_v2_shard_a_controls.yaml `
  --judge-backend gemini `
  --skip-persistence `
  --checkpoint-dir benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/shards/shard_a_controls/checkpoints `
  --output-dir benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/shards/shard_a_controls `
  --max-item-attempts 2 `
  --retry-base-seconds 2
```

### A.4. Nếu bị ngắt/quota/crash thì resume shard A

```powershell
$env:PYTHONPATH='backend'
.\.venv\Scripts\python.exe scripts\run_eval.py `
  --manifest configs/w8_abl_01_retrieval_matrix_v2_shard_a_controls.yaml `
  --judge-backend gemini `
  --skip-persistence `
  --checkpoint-dir benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/shards/shard_a_controls/checkpoints `
  --output-dir benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/shards/shard_a_controls `
  --max-item-attempts 2 `
  --retry-base-seconds 2 `
  --resume `
  --retry-failed
```

### A.5. Theo dõi tiến độ shard A

```powershell
$ShardDir='benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/shards/shard_a_controls'
Get-Content "$ShardDir/checkpoints/checkpoint_summary.json" -Raw | ConvertFrom-Json
```

### A.6. Kiểm tra kết quả shard A

Shard A phải có `400` cặp hoàn tất và `0` cặp lỗi.

```powershell
$ShardDir='benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/shards/shard_a_controls'
$ExpectedPairs=400
$Report = Get-Content "$ShardDir/evaluation_report.json" -Raw | ConvertFrom-Json
if ($Report.status -ne 'completed') { throw "Shard A status is not completed: $($Report.status)" }
if ($Report.judge_backend -ne 'gemini') { throw "Shard A wrong judge backend: $($Report.judge_backend)" }
if ($Report.dataset_item_count -ne 100) { throw "Shard A wrong dataset_item_count: $($Report.dataset_item_count)" }
if ($Report.execution_summary.completed_pair_count -ne $ExpectedPairs) { throw "Shard A wrong completed pair count: $($Report.execution_summary.completed_pair_count)" }
if ($Report.execution_summary.failed_pair_count -ne 0) { throw "Shard A has failed pairs: $($Report.execution_summary.failed_pair_count)" }
```

Kiểm tra file bắt buộc:

```powershell
Test-Path "$ShardDir/evaluation_report.json"
Test-Path "$ShardDir/evaluation_report.md"
Test-Path "$ShardDir/checkpoints/evaluation_checkpoint.json"
Test-Path "$ShardDir/checkpoints/checkpoint_summary.json"
```

Tất cả phải trả về `True`.

### A.7. Commit và đẩy shard A lên remote

```powershell
git status --short
git add benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/shards/shard_a_controls
git commit -m "Add W8 retrieval shard A controls results"
git push -u origin run/w8-retrieval-shard-a-controls
```

Trước khi commit, `git status --short` chỉ được có file trong:

```text
benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/shards/shard_a_controls/...
```

### A.8. Tạo PR/MR shard A vào `main`

Nội dung PR/MR:

```text
Shard: A controls
Branch: run/w8-retrieval-shard-a-controls
Manifest: configs/w8_abl_01_retrieval_matrix_v2_shard_a_controls.yaml
Thư mục output: benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/shards/shard_a_controls
Trạng thái: completed
Bộ chấm: gemini
Số cặp hoàn tất: 400
Số cặp lỗi: 0
Ghi chú: ghi rõ nếu có gián đoạn/hết hạn mức Gemini và đã resume mấy lần
```

## 6. Việc của Người B — shard single paths

Người B chỉ làm shard B.

### B.1. Lấy `main` mới nhất và tạo branch B

```powershell
git fetch origin --tags
git switch main
git pull --ff-only origin main
git status --short
git --no-pager log -1 --oneline --decorate
git switch -c run/w8-retrieval-shard-b-single-paths
git branch --show-current
```

Kỳ vọng:

- `git status --short` không in gì trước khi tạo branch.
- `git branch --show-current` in ra `run/w8-retrieval-shard-b-single-paths`.

Nếu người phụ trách chính yêu cầu tạo branch từ tag freeze `w8-retrieval-v2-run-freeze`, dùng lệnh tạo branch này thay cho lệnh `git switch -c ...` ở trên:

```powershell
git switch -c run/w8-retrieval-shard-b-single-paths w8-retrieval-v2-run-freeze
```

### B.2. Kiểm tra môi trường trước khi chạy lâu

```powershell
$env:PYTHONPATH='backend'
Test-Path .\.env
Test-Path .\.venv\Scripts\python.exe
Test-Path .\models\bge-reranker-v2-m3\model.safetensors
.\.venv\Scripts\python.exe -m pytest backend/tests/test_w8_retrieval_matrix.py backend/tests/test_run_eval_cli.py -q -p no:cacheprovider
.\.venv\Scripts\python.exe scripts\check_gemini_api.py --model gemini-3.1-flash-lite-preview
```

Nếu một dòng `Test-Path` trả về `False`, hoặc pytest/Gemini check fail, thì dừng, báo người phụ trách chính, không chạy shard.

### B.3. Chạy shard B lần đầu

```powershell
$env:PYTHONPATH='backend'
.\.venv\Scripts\python.exe scripts\run_eval.py `
  --manifest configs/w8_abl_01_retrieval_matrix_v2_shard_b_single_paths.yaml `
  --judge-backend gemini `
  --skip-persistence `
  --checkpoint-dir benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/shards/shard_b_single_paths/checkpoints `
  --output-dir benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/shards/shard_b_single_paths `
  --max-item-attempts 2 `
  --retry-base-seconds 2
```

### B.4. Nếu bị ngắt/quota/crash thì resume shard B

```powershell
$env:PYTHONPATH='backend'
.\.venv\Scripts\python.exe scripts\run_eval.py `
  --manifest configs/w8_abl_01_retrieval_matrix_v2_shard_b_single_paths.yaml `
  --judge-backend gemini `
  --skip-persistence `
  --checkpoint-dir benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/shards/shard_b_single_paths/checkpoints `
  --output-dir benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/shards/shard_b_single_paths `
  --max-item-attempts 2 `
  --retry-base-seconds 2 `
  --resume `
  --retry-failed
```

### B.5. Theo dõi tiến độ shard B

```powershell
$ShardDir='benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/shards/shard_b_single_paths'
Get-Content "$ShardDir/checkpoints/checkpoint_summary.json" -Raw | ConvertFrom-Json
```

### B.6. Kiểm tra kết quả shard B

Shard B phải có `300` cặp hoàn tất và `0` cặp lỗi.

```powershell
$ShardDir='benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/shards/shard_b_single_paths'
$ExpectedPairs=300
$Report = Get-Content "$ShardDir/evaluation_report.json" -Raw | ConvertFrom-Json
if ($Report.status -ne 'completed') { throw "Shard B status is not completed: $($Report.status)" }
if ($Report.judge_backend -ne 'gemini') { throw "Shard B wrong judge backend: $($Report.judge_backend)" }
if ($Report.dataset_item_count -ne 100) { throw "Shard B wrong dataset_item_count: $($Report.dataset_item_count)" }
if ($Report.execution_summary.completed_pair_count -ne $ExpectedPairs) { throw "Shard B wrong completed pair count: $($Report.execution_summary.completed_pair_count)" }
if ($Report.execution_summary.failed_pair_count -ne 0) { throw "Shard B has failed pairs: $($Report.execution_summary.failed_pair_count)" }
```

Kiểm tra file bắt buộc:

```powershell
Test-Path "$ShardDir/evaluation_report.json"
Test-Path "$ShardDir/evaluation_report.md"
Test-Path "$ShardDir/checkpoints/evaluation_checkpoint.json"
Test-Path "$ShardDir/checkpoints/checkpoint_summary.json"
```

Tất cả phải trả về `True`.

### B.7. Commit và đẩy shard B lên remote

```powershell
git status --short
git add benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/shards/shard_b_single_paths
git commit -m "Add W8 retrieval shard B single-path results"
git push -u origin run/w8-retrieval-shard-b-single-paths
```

Trước khi commit, `git status --short` chỉ được có file trong:

```text
benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/shards/shard_b_single_paths/...
```

### B.8. Tạo PR/MR shard B vào `main`

Nội dung PR/MR:

```text
Shard: B single paths
Branch: run/w8-retrieval-shard-b-single-paths
Manifest: configs/w8_abl_01_retrieval_matrix_v2_shard_b_single_paths.yaml
Thư mục output: benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/shards/shard_b_single_paths
Trạng thái: completed
Bộ chấm: gemini
Số cặp hoàn tất: 300
Số cặp lỗi: 0
Ghi chú: ghi rõ nếu có gián đoạn/hết hạn mức Gemini và đã resume mấy lần
```

## 7. Việc của Người C — shard dense combos

Người C chỉ làm shard C.

### C.1. Lấy `main` mới nhất và tạo branch C

```powershell
git fetch origin --tags
git switch main
git pull --ff-only origin main
git status --short
git --no-pager log -1 --oneline --decorate
git switch -c run/w8-retrieval-shard-c-dense-combos
git branch --show-current
```

Kỳ vọng:

- `git status --short` không in gì trước khi tạo branch.
- `git branch --show-current` in ra `run/w8-retrieval-shard-c-dense-combos`.

Nếu người phụ trách chính yêu cầu tạo branch từ tag freeze `w8-retrieval-v2-run-freeze`, dùng lệnh tạo branch này thay cho lệnh `git switch -c ...` ở trên:

```powershell
git switch -c run/w8-retrieval-shard-c-dense-combos w8-retrieval-v2-run-freeze
```

### C.2. Kiểm tra môi trường trước khi chạy lâu

```powershell
$env:PYTHONPATH='backend'
Test-Path .\.env
Test-Path .\.venv\Scripts\python.exe
Test-Path .\models\bge-reranker-v2-m3\model.safetensors
.\.venv\Scripts\python.exe -m pytest backend/tests/test_w8_retrieval_matrix.py backend/tests/test_run_eval_cli.py -q -p no:cacheprovider
.\.venv\Scripts\python.exe scripts\check_gemini_api.py --model gemini-3.1-flash-lite-preview
```

Nếu một dòng `Test-Path` trả về `False`, hoặc pytest/Gemini check fail, thì dừng, báo người phụ trách chính, không chạy shard.

### C.3. Chạy shard C lần đầu

```powershell
$env:PYTHONPATH='backend'
.\.venv\Scripts\python.exe scripts\run_eval.py `
  --manifest configs/w8_abl_01_retrieval_matrix_v2_shard_c_dense_combos.yaml `
  --judge-backend gemini `
  --skip-persistence `
  --checkpoint-dir benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/shards/shard_c_dense_combos/checkpoints `
  --output-dir benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/shards/shard_c_dense_combos `
  --max-item-attempts 2 `
  --retry-base-seconds 2
```

### C.4. Nếu bị ngắt/quota/crash thì resume shard C

```powershell
$env:PYTHONPATH='backend'
.\.venv\Scripts\python.exe scripts\run_eval.py `
  --manifest configs/w8_abl_01_retrieval_matrix_v2_shard_c_dense_combos.yaml `
  --judge-backend gemini `
  --skip-persistence `
  --checkpoint-dir benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/shards/shard_c_dense_combos/checkpoints `
  --output-dir benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/shards/shard_c_dense_combos `
  --max-item-attempts 2 `
  --retry-base-seconds 2 `
  --resume `
  --retry-failed
```

### C.5. Theo dõi tiến độ shard C

```powershell
$ShardDir='benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/shards/shard_c_dense_combos'
Get-Content "$ShardDir/checkpoints/checkpoint_summary.json" -Raw | ConvertFrom-Json
```

### C.6. Kiểm tra kết quả shard C

Shard C phải có `300` cặp hoàn tất và `0` cặp lỗi.

```powershell
$ShardDir='benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/shards/shard_c_dense_combos'
$ExpectedPairs=300
$Report = Get-Content "$ShardDir/evaluation_report.json" -Raw | ConvertFrom-Json
if ($Report.status -ne 'completed') { throw "Shard C status is not completed: $($Report.status)" }
if ($Report.judge_backend -ne 'gemini') { throw "Shard C wrong judge backend: $($Report.judge_backend)" }
if ($Report.dataset_item_count -ne 100) { throw "Shard C wrong dataset_item_count: $($Report.dataset_item_count)" }
if ($Report.execution_summary.completed_pair_count -ne $ExpectedPairs) { throw "Shard C wrong completed pair count: $($Report.execution_summary.completed_pair_count)" }
if ($Report.execution_summary.failed_pair_count -ne 0) { throw "Shard C has failed pairs: $($Report.execution_summary.failed_pair_count)" }
```

Kiểm tra file bắt buộc:

```powershell
Test-Path "$ShardDir/evaluation_report.json"
Test-Path "$ShardDir/evaluation_report.md"
Test-Path "$ShardDir/checkpoints/evaluation_checkpoint.json"
Test-Path "$ShardDir/checkpoints/checkpoint_summary.json"
```

Tất cả phải trả về `True`.

### C.7. Commit và đẩy shard C lên remote

```powershell
git status --short
git add benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/shards/shard_c_dense_combos
git commit -m "Add W8 retrieval shard C dense-combo results"
git push -u origin run/w8-retrieval-shard-c-dense-combos
```

Trước khi commit, `git status --short` chỉ được có file trong:

```text
benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/shards/shard_c_dense_combos/...
```

### C.8. Tạo PR/MR shard C vào `main`

Nội dung PR/MR:

```text
Shard: C dense combos
Branch: run/w8-retrieval-shard-c-dense-combos
Manifest: configs/w8_abl_01_retrieval_matrix_v2_shard_c_dense_combos.yaml
Thư mục output: benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/shards/shard_c_dense_combos
Trạng thái: completed
Bộ chấm: gemini
Số cặp hoàn tất: 300
Số cặp lỗi: 0
Ghi chú: ghi rõ nếu có gián đoạn/hết hạn mức Gemini và đã resume mấy lần
```

## 8. Checklist cuối cùng cho từng người trước khi báo xong

Trước khi báo người phụ trách chính, mỗi người tự tick đủ:

- Đang ở branch đúng của mình.
- Chỉ chạy đúng manifest của mình.
- `evaluation_report.json` tồn tại.
- `evaluation_report.md` tồn tại.
- `checkpoints/evaluation_checkpoint.json` tồn tại.
- `checkpoints/checkpoint_summary.json` tồn tại.
- `status = completed`.
- `judge_backend = gemini`.
- `dataset_item_count = 100`.
- `execution_summary.failed_pair_count = 0`.
- Số cặp đúng:
  - A: `400`
  - B: `300`
  - C: `300`
- `git status --short` trước commit chỉ có file trong thư mục shard của mình.
- Đã push branch shard lên origin.
- Đã mở PR/MR vào `main`.

## 9. Những lỗi hay gặp và cách xử lý

### Lỡ chạy sai output vào thư mục gốc chuẩn

Dừng ngay và báo người phụ trách chính. Không tự merge, không tự copy thủ công sang shard.

Thư mục gốc chuẩn không được người chạy shard ghi trực tiếp:

```text
benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/
```

Người chạy shard chỉ được ghi vào một trong ba thư mục:

```text
benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/shards/shard_a_controls/
benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/shards/shard_b_single_paths/
benchmark/tuvi_golden_dataset/reports_final/20_retrieval_fusion_reranker_matrix/shards/shard_c_dense_combos/
```

### Bị quota Gemini hoặc máy bị tắt giữa chừng

Không xóa checkpoint. Chạy lại lệnh resume của đúng shard mình.

### Thiếu model reranker local

Nếu lỗi liên quan `models/bge-reranker-v2-m3`, `model.safetensors`, `local_files_only`, hoặc `from_pretrained`, quay lại mục 3.3 để tải/copy model. Không sửa config để tắt reranker.

### Người B/C lỗi dense embedding hoặc vector index

Nếu shard B/C lỗi liên quan `BAAI/bge-m3`, `chunkVectorBgeM3`, `bge_m3`, hoặc vector dimension, kiểm tra lại mục 3.4 và báo người phụ trách chính. Không tự đổi dense config.

### Kiểm tra thấy số cặp lỗi > 0

Chạy lại lệnh resume với `--resume --retry-failed`. Nếu vẫn còn cặp lỗi sau retry, báo người phụ trách chính kèm log lỗi.

### Có file ngoài shard trong `git status --short`

Không commit. Kiểm tra kỹ file đó là gì. Chỉ add thư mục shard của mình theo đúng lệnh ở trên.

## 10. Phần của người phụ trách chính sau khi cả 3 PR/MR đã merge vào `main`

Người A/B/C không chạy phần này.

Người phụ trách chính chạy sau khi cả ba shard A/B/C đã được merge vào `main` và đều có:

- `status = completed`
- `judge_backend = gemini`
- số cặp lỗi `0`
- số cặp A/B/C = `400/300/300`

```powershell
git switch main
git pull --ff-only origin main
$env:PYTHONPATH='backend'
.\.venv\Scripts\python.exe scripts\merge_w8_retrieval_shards.py
.\.venv\Scripts\python.exe scripts\build_final_ablation_report.py
Copy-Item evaluation\ablation_final_report.md benchmark\tuvi_golden_dataset\reports_final\90_final_report\ablation_final_report.md -Force
Copy-Item benchmark\tuvi_golden_dataset\reports_final\ablation_final_summary.json benchmark\tuvi_golden_dataset\reports_final\90_final_report\ablation_final_summary.json -Force
```

Script gộp shard sẽ kiểm tra:

- đủ 10 cấu hình chuẩn, mỗi cấu hình xuất hiện đúng 1 lần
- mỗi cấu hình có 100 item
- tổng cộng 1000 cặp
- `judge_backend = gemini`
- `failed_pair_count = 0`
- config hash khớp manifest chuẩn
