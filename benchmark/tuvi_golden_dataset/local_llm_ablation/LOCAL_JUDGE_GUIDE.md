# Hướng dẫn chạy notebook 03 trên local

Tài liệu này dành cho B/C/D sau khi mỗi người đã hoàn tất notebook 02 trên Kaggle và tải về hai prediction ZIP: một ZIP của Qwen2.5-7B-Instruct và một ZIP của Gemma-3-4B-IT.

Notebook 03 cần Internet để gọi Gemini, không cần GPU và phải chạy từ clone của repo.

## 1. Pull đúng code và chuẩn bị môi trường

Mở PowerShell tại repo root:

```powershell
git checkout main
git pull origin main

.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
.\.venv\Scripts\python.exe -m pip install -r benchmark\tuvi_golden_dataset\local_llm_ablation\requirements-online.txt
```

Nếu clone chưa có `.venv`:

```powershell
py -3.12 -m venv .venv
```

Luôn mở Jupyter bằng Python trong `.venv`; không dùng lệnh `jupyter lab` của Python hệ thống:

```powershell
.\.venv\Scripts\python.exe -m jupyter lab
```

## 2. Chép hai prediction ZIP vào đúng folder

Không giải nén và không sửa JSONL bên trong ZIP.

| Thành viên | Folder local |
|---|---|
| B | `benchmark/tuvi_golden_dataset/local_llm_ablation/artifacts/judge_inputs/B/` |
| C | `benchmark/tuvi_golden_dataset/local_llm_ablation/artifacts/judge_inputs/C/` |
| D | `benchmark/tuvi_golden_dataset/local_llm_ablation/artifacts/judge_inputs/D/` |

Mỗi folder phải có đúng hai official prediction ZIP của người đó:

- một ZIP Qwen đủ 100/100;
- một ZIP Gemma đủ 100/100.

Smoke ZIP không được dùng làm official judge input. Notebook sẽ tự giải nén vào vùng tạm, kiểm tra model/config và từ chối gọi Gemini nếu thiếu bất kỳ prediction nào.

## 3. Nạp Gemini keys

Trong cùng PowerShell session dùng để mở Jupyter, nạp ít nhất hai key:

```powershell
$env:GEMINI_API_KEYS = 'KEY_1,KEY_2,KEY_3'
.\.venv\Scripts\python.exe -m jupyter lab
```

Không ghi key vào notebook, source code, screenshot hoặc Git. Code cũng hỗ trợ keys trong `.env` qua `GEMINI_API_KEYS`, `GEMINI_API_KEY` và `GEMINI_API_KEY_2`, `GEMINI_API_KEY_3`, ...

Notebook yêu cầu mặc định tối thiểu hai key để có round-robin và failover. Bình thường một answer dùng một Gemini request và request đó trả cả ba score. `retry_attempts=3` chỉ dùng khi request lỗi.

## 4. Cấu hình và chạy notebook 03

Mở:

```text
benchmark/tuvi_golden_dataset/local_llm_ablation/notebooks/03_gemini_judge_local.ipynb
```

Ở cell config đầu tiên chỉ đổi `RUNNER` theo người chạy:

```python
REPO_ROOT = None
ACTION = 'judge'
RUNNER = 'B'              # B, C hoặc D
MINIMUM_KEY_COUNT = 2
```

Giữ nguyên judge model, temperature, retry settings, mapping runner/config và expected model IDs. Chọn kernel của `.venv`, sau đó **Run All**.

Trước API call, notebook phải tìm đủ 200 predictions của đúng runner. Trong quá trình chạy, kết quả được checkpoint theo `evaluation_id`; nếu mất mạng hoặc hết quota, mở lại đúng notebook và Run All để resume. Completed items không bị gọi lại.

## 5. Điều kiện PASS

Cell cuối phải đạt:

```text
retrieval_pair_count = 100
expected_prediction_count = 200
judged_completed_count = 200
judged_failed_count = 0
is_complete = true
```

Output của từng người nằm tại:

```text
benchmark/tuvi_golden_dataset/local_llm_ablation/artifacts/gemini_judge_shards/B/
benchmark/tuvi_golden_dataset/local_llm_ablation/artifacts/gemini_judge_shards/C/
benchmark/tuvi_golden_dataset/local_llm_ablation/artifacts/gemini_judge_shards/D/
```

File gửi cho A nằm ngay trong folder cha:

```text
artifacts/gemini_judge_shards/gemini_judge_shard_b.zip
artifacts/gemini_judge_shards/gemini_judge_shard_c.zip
artifacts/gemini_judge_shards/gemini_judge_shard_d.zip
```

## 6. Bàn giao cho A

Mỗi người gửi:

1. một `gemini_judge_shard_b/c/d.zip`;
2. link lưu hai official prediction ZIP;
3. loại GPU Kaggle;
4. completed/failed count;
5. lỗi quota/network và số lần retry nếu có.

Không push folder `artifacts/` hoặc các ZIP lên Git. Nếu chỉ chạy thí nghiệm thì không cần tạo branch. Chỉ tạo branch riêng và PR khi thực sự sửa code/notebook.

## 7. Lỗi thường gặp

### `ModuleNotFoundError`

Jupyter đang dùng Python hệ thống. Đóng Jupyter và mở lại bằng:

```powershell
.\.venv\Scripts\python.exe -m jupyter lab
```

### Không tìm thấy prediction

Kiểm tra hai ZIP nằm trực tiếp trong `artifacts/judge_inputs/<RUNNER>/`, đúng runner và đều là official 100/100.

### Báo thiếu Gemini key

Đặt `$env:GEMINI_API_KEYS` trước khi mở Jupyter. Nếu Jupyter đã mở trước đó, đóng server rồi mở lại từ đúng PowerShell session.

### HTTP 429, quota hoặc network error

Không xóa output/checkpoint. Bổ sung key hợp lệ hoặc đợi quota hồi phục, sau đó Run All lại. Key pool sẽ round-robin/failover và chỉ retry failed/missing item.

### Judge xong nhưng không có ZIP

Kiểm tra cell cuối có thật sự đạt 200/200 và `is_complete=true`. ZIP chỉ được tạo sau khi report/checkpoint/checksum đã ghi thành công.

## 8. Sau khi A nhận đủ ba shard

A chép ba ZIP vào:

```text
benchmark/tuvi_golden_dataset/local_llm_ablation/artifacts/downloaded_judge_shards/
```

Sau đó mở chính notebook 03 và đặt:

```python
ACTION = 'merge'
```

Merge không cần Gemini key và không gọi API lại. Final gate là 3 shards, 600/600 completed và 6 model-config result rows.
