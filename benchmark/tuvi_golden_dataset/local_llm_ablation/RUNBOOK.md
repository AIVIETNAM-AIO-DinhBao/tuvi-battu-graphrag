# Runbook chính thức: Local-LLM ablation

Thí nghiệm dùng một retrieval bundle cố định cho 100 câu và 3 config, sau đó sinh câu trả lời bằng Qwen2.5-7B-Instruct và Gemma-3-4B-IT. B/C/D mỗi người chạy một config trên cả hai model và tự chấm 200 câu bằng Gemini. A chỉ gộp ba judge shard, không gọi Gemini lại.

## 0. Ma trận và phân công cố định

| Người | Config | Qwen | Gemma | Gemini judge |
|---|---|---:|---:|---:|
| A | Chuẩn bị + merge | - | - | 0 API calls khi merge |
| B | `graph_dense_rrf` | 100 | 100 | 200 answers |
| C | `semantic_gs_rrf_rerank_k40` | 100 | 100 | 200 answers |
| D | `semantic_gs_rrf_no_rerank_reference` | 100 | 100 | 200 answers |

Tổng cộng: 300 retrieval cases, 600 generated answers và 600 judged answers.

Từ repo root, cài dependency local:

```powershell
pip install -r backend\requirements.txt
pip install -r benchmark\tuvi_golden_dataset\local_llm_ablation\requirements-online.txt
```

Không commit `.env`, Hugging Face token, Kaggle credentials hoặc Gemini API key.

## 1. A — notebook 00: tạo hai model dataset trên Kaggle

Notebook: `notebooks/00_prepare_model_dataset_kaggle.ipynb`.

### Qwen

1. Upload notebook lên Kaggle, bật Internet.
2. Đặt `MODEL_KEY='qwen25_7b'` rồi Run All.
3. Cell cuối phải in `PASS=True`, model ID và pinned revision.
4. Save Version kèm output.
5. Tạo private Kaggle Dataset từ output, ví dụ `qwen25-7b-instruct-offline`.

### Gemma

1. Chấp nhận license của `google/gemma-3-4b-it` trên Hugging Face.
2. Tạo Hugging Face read token và thêm Kaggle Secret tên `HF_TOKEN`.
3. Đặt `MODEL_KEY='gemma3_4b'`, Run All và kiểm tra `PASS=True`.
4. Save Version rồi tạo private dataset, ví dụ `gemma3-4b-it-offline`.

Mỗi model dataset phải có trực tiếp:

```text
asset_manifest.json
model/config.json
model/tokenizer_config.json
model/*.safetensors
wheelhouse/*.whl
```

Không zip model weights trước khi Add Input.

## 2. A — notebook 01: build retrieval một lần trên local

Notebook: `notebooks/01_build_retrieval_bundle_local.ipynb`.

1. Mở notebook từ clone của repo; đặt `REPO_ROOT` thủ công nếu auto-detect thất bại.
2. Kiểm tra `.env`, Neo4j, embedding model và reranker giống các ablation cũ.
3. Đặt `RUN_MODE='smoke'`, Run All; phải đạt 6/6.
4. Đặt `RUN_MODE='official'`, Run All; phải đạt 300/300 và zero failed.

Output:

```text
benchmark/tuvi_golden_dataset/local_llm_ablation/artifacts/context_bundle_v1/
benchmark/tuvi_golden_dataset/local_llm_ablation/artifacts/context_bundle_v1.zip
```

Chỉ chia sẻ bundle khi manifest ghi:

```text
config_count = 3
item_count = 100
planned_pair_count = 300
completed_pair_count = 300
failed_pair_count = 0
```

Upload `context_bundle_v1.zip` thành private Kaggle Dataset và share cho B/C/D. Xem thêm `KAGGLE_DATASET_GUIDE.md`.

### Resume retrieval

Nếu retrieval lỗi, đọc `bundle_errors.jsonl`, sửa backend rồi chạy lại cùng output directory với `retry_failed=True`. Checkpoint dùng `pair_id`, không cần chạy lại các pair đã hoàn tất.

## 3. B/C/D — notebook 02: inference offline trên Kaggle

Notebook: `notebooks/02_generate_offline_kaggle.ipynb`. Notebook này standalone; không upload repo và không cần `local_tools`.

Mỗi run Add Input đúng hai dataset:

1. dataset chứa `context_bundle_v1.zip`;
2. một model dataset tương ứng.

Kaggle settings:

- Accelerator: GPU;
- Internet: OFF;
- mỗi session chỉ mount/chạy một model.

Chỉ thay ba biến:

```python
RUNNER = 'B'               # B, C hoặc D
MODEL_KEY = 'qwen25_7b'    # hoặc gemma3_4b
RUN_MODE = 'smoke'         # sau đó official
```

Không đổi seed, quantization, token limits hoặc mapping config.

Quy trình của mỗi người:

1. Chạy Qwen smoke 2 cases.
2. Chạy Qwen official 100 cases, tải ZIP output về.
3. Restart Kaggle session.
4. Thay model input bằng Gemma dataset.
5. Chạy Gemma smoke 2 cases.
6. Chạy Gemma official 100 cases, tải ZIP output về.

Official gate cho mỗi model:

```text
assigned_pair_count = 100
completed_pair_count = 100
failed_pair_count = 0
is_complete = true
```

Nếu OOM, restart session và xác nhận đúng GPU/wheelhouse. Không tự giảm token limit, truncate prompt hoặc đổi quantization vì sẽ phá tính so sánh.

Nếu Gemma báo `Model returned an empty answer`, phải dùng notebook 02 từ commit có bản sửa BF16. Gemma 3 dùng BF16 cho phần tính toán 4-bit; Qwen vẫn dùng FP16. Xóa output smoke cũ hoặc mở session mới rồi chạy lại smoke. ZIP có `failed_pair_count > 0` chỉ là checkpoint chẩn đoán, không được đưa vào notebook 03.

## 4. B/C/D — chuẩn bị input judge trên local

Mỗi người giữ hai prediction ZIP của chính mình và chép nguyên file vào:

```text
benchmark/tuvi_golden_dataset/local_llm_ablation/artifacts/judge_inputs/B/
benchmark/tuvi_golden_dataset/local_llm_ablation/artifacts/judge_inputs/C/
benchmark/tuvi_golden_dataset/local_llm_ablation/artifacts/judge_inputs/D/
```

Không giải nén, đổi tên nội dung hoặc sửa JSONL. Notebook tự tìm `predictions_shard_*.jsonl`, đối chiếu model/config/checksum và từ chối judge nếu thiếu bất kỳ câu nào.

## 5. B/C/D — notebook 03: Gemini judge 200 answers/người

Notebook: `notebooks/03_gemini_judge_local.ipynb`.

Hạng mục cài môi trường, chọn kernel, xử lý lỗi và checklist bàn giao được ghi chi tiết trong `LOCAL_JUDGE_GUIDE.md`.

Trong PowerShell mở Jupyter, nạp tối thiểu hai key để có rotation/failover:

```powershell
$env:GEMINI_API_KEYS = 'KEY_1,KEY_2,KEY_3'
.\.venv\Scripts\python.exe -m jupyter lab
```

Cũng hỗ trợ `.env`, `GEMINI_API_KEY` và các biến `GEMINI_API_KEY_2`, `GEMINI_API_KEY_3`, ... thông qua đúng loader của backend. Không ghi key trực tiếp vào notebook.

Trong notebook đặt:

```python
ACTION = 'judge'
RUNNER = 'B'              # người C/D đổi tương ứng
MINIMUM_KEY_COUNT = 2
```

Sau đó Run All. Mapping config và offset điểm bắt đầu của key đã cố định:

| Runner | Key start offset | Số câu |
|---|---:|---:|
| B | 0 | 200 |
| C | 1 | 200 |
| D | 2 | 200 |

### Một câu gọi Gemini bao nhiêu lần?

Bình thường **một generated answer = một Gemini API request**. Request đó dùng đúng prompt cũ và trả cùng lúc một JSON gồm ba score:

- `faithfulness`;
- `answer_relevancy`;
- `context_recall`.

`retry_attempts=3` không có nghĩa là mỗi câu gọi ba lần. Nó chỉ là tối đa ba vòng thử khi request lỗi. Trong mỗi vòng, key pool bắt đầu round-robin rồi failover sang key kế tiếp nếu key hiện tại quota/network error. Vì vậy:

- đường chạy bình thường: 200 successful requests/người;
- khi có lỗi: có thể phát sinh thêm failed requests/retries;
- diagnostics chỉ ghi `key_1`, `key_2`, ... và số lần dùng/thành công/thất bại, không ghi secret.

Pipeline dùng trực tiếp code canonical trong `backend/app/rag/evaluation.py`:

- `GeminiEvaluationJudge`;
- `build_gemini_judge_prompt`;
- `summarize_evaluation_item`;
- `aggregate_evaluation_metrics`;
- `aggregate_grouped_metrics`;
- `render_markdown_report`.

Judge model mặc định giữ giống run trước: `gemini-3.1-flash-lite-preview`, temperature `0.0`, `max_output_tokens=768`.

Nếu bị ngắt, Run All lại với cùng output directory. Completed `evaluation_id` được resume; chỉ failed/missing item bị gọi lại.

Gate của mỗi member:

```text
retrieval_pair_count = 100
expected_prediction_count = 200
judged_completed_count = 200
judged_failed_count = 0
is_complete = true
```

Mỗi người gửi A đúng một file:

```text
gemini_judge_shard_b.zip
gemini_judge_shard_c.zip
gemini_judge_shard_d.zip
```

Mỗi ZIP chứa:

```text
evaluation_report.json
evaluation_report.md
checkpoints/evaluation_checkpoint.json
checkpoints/checkpoint_summary.json
judged_items.jsonl
local_llm_metrics.csv
local_llm_evaluation_report.json
judge_shard_manifest.json
```

`judge_shard_manifest.json` có SHA-256 cho toàn bộ file chính; A merge sẽ kiểm tra checksum trước.

## 6. A — notebook 03: merge ba judge shard

A chép nguyên ba ZIP vào:

```text
benchmark/tuvi_golden_dataset/local_llm_ablation/artifacts/downloaded_judge_shards/
```

Trong notebook 03 đặt:

```python
ACTION = 'merge'
```

Run All. Merge không cần Gemini key, không gửi request ra Gemini và không chấm lại. Nó sẽ:

1. xác minh checksum và `is_complete` của từng shard;
2. buộc ba shard dùng cùng judge model;
3. chống duplicate/conflict theo `model_id + pair_id`;
4. yêu cầu đúng 600/600 completed records;
5. aggregate lại 6 model-config rows bằng đúng hàm evaluation cũ.

Final gate:

```text
source_shard_count = 3
expected_pair_count = 600
completed_pair_count = 600
failed_pair_count = 0
config_result_count = 6
is_complete = true
```

## 7. File kết quả dùng cho report

Output cuối nằm ở `artifacts/gemini_judge_final/`:

```text
evaluation_report.json
evaluation_report.md
checkpoints/evaluation_checkpoint.json
checkpoints/checkpoint_summary.json
judged_items.jsonl
local_llm_metrics.csv
merge_summary.json
```

Vai trò từng file:

- `evaluation_report.json`: artifact canonical, cùng top-level schema và per-item schema như `reports/` và `reports_final/`; có 6 config entries (2 models × 3 retrieval configs).
- `evaluation_report.md`: Markdown được tạo bởi chính `render_markdown_report` cũ.
- `checkpoints/evaluation_checkpoint.json`: toàn bộ item records theo config/model để audit/resume.
- `checkpoints/checkpoint_summary.json`: count và trạng thái hoàn thành.
- `judged_items.jsonl`: 600 per-item results đã compact, phù hợp để phân tích bổ sung.
- `local_llm_metrics.csv`: bảng gọn 6 rows để đưa vào report/plot.
- `merge_summary.json`: checksum, shard count và merge gate.

Không thể byte-identical với report Gemini-generation cũ vì generation model, config name và provenance khác. Tuy nhiên evaluator, prompt, metric computation, report renderer, field schema và checkpoint layout được tái sử dụng trực tiếp từ pipeline cũ.

## 8. Verification trước khi phát notebook

Từ repo root:

```powershell
python -m benchmark.tuvi_golden_dataset.local_llm_ablation.local_tools.validate_kit `
  --kit-root benchmark\tuvi_golden_dataset\local_llm_ablation `
  --repo-root .
```

Kết quả hợp lệ phải có `"ok": true`, 4 notebooks, 3 configs, 100 items và 300 retrieval pairs.

Trước official run, nên smoke judge 2 câu/người để xác nhận key, model access và JSON parsing. Không dùng smoke output thay cho official output.

## 9. Diễn giải metric

Golden release không chứa `gold_chunk_ids`, vì vậy không có exact-match retrieval candidate hit theo gold chunk. Không diễn giải `graph_hit_rate` thành retrieval accuracy. Các evidence-based retrieval metrics hiện có gồm gold document coverage, page hit ±1 và quote overlap.

Latency chỉ so sánh khi Kaggle GPU type và runtime settings giống nhau. Report phải ghi rõ 4-bit quantization và khả năng bias của Gemini judge.
