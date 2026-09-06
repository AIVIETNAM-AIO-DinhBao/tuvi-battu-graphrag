# Hướng dẫn tạo và chia sẻ Kaggle Dataset

Tất cả dataset trong study này nên để **Private**. Chỉ cấp quyền cho bốn thành viên nhóm.

## 0. Upload notebook `.ipynb` lên Kaggle

Với notebook 00 hoặc 02:

1. Vào Kaggle → Code → New Notebook.
2. Dùng chức năng Import/Upload Notebook và chọn file `.ipynb` từ thư mục `notebooks/`.
3. Mở Settings và đặt Internet/GPU đúng bảng trong `README.md`.
4. Dùng Add Input để gắn private datasets cần thiết.
5. Không upload repo hoặc `local_tools`; notebook Kaggle đã standalone.

B/C/D chỉ cần upload notebook 02. A chịu trách nhiệm notebook 00 và hai bước local.

## A. Model dataset từ notebook 00

Đây là cách khuyến nghị vì không phải tải model lớn về máy rồi upload lại.

1. Chạy notebook 00 với Internet ON đến khi cell cuối báo PASS.
2. Chọn **Save Version** và bảo đảm lưu output files.
3. Mở trang version vừa hoàn tất và kiểm tra tab Output có folder `{MODEL_KEY}_offline_dataset`.
4. Dùng chức năng tạo Dataset từ notebook output, đặt dataset ở chế độ Private.
5. Đặt tên dễ nhận biết:
   - `qwen25-7b-instruct-offline`
   - `gemma3-4b-it-offline`
6. Mở trang Dataset, kiểm tra `asset_manifest.json`, `model/` và `wheelhouse/` xuất hiện.
7. Share private dataset với B/C/D.

Nếu giao diện Kaggle chỉ cho Add Input từ Notebook Output, có thể chia sẻ notebook/version đó và dùng trực tiếp làm data source; notebook 02 chỉ cần thấy `asset_manifest.json` dưới `/kaggle/input`.

### Gemma

- Dataset phải private.
- Các thành viên nên tự chấp nhận Gemma license trước khi truy cập/chạy.
- Không đưa `HF_TOKEN` vào output, metadata, notebook cell hoặc tên file.
- Notebook 00 xóa local Hugging Face transfer cache trước khi tạo manifest.

## B. Model-only bundle từ notebook 01

Để chạy baseline chỉ dùng mô hình, notebook 01 không gọi Neo4j hay retrieval. File cần upload là:

```text
artifacts/model_only_bundle_v1.zip
```

1. Vào Kaggle → Datasets → New Dataset.
2. Upload `model_only_bundle_v1.zip`.
3. Title gợi ý: `tuviqa-model-only-bundle-v1`.
4. Visibility: Private.
5. Tạo dataset và share với B/C/D.
6. Không upload `.env`, Neo4j credentials hoặc toàn bộ repo.

Notebook 02 tự phát hiện ZIP có `bundle_manifest.json` và giải nén an toàn vào `/kaggle/working`.

Manifest hợp lệ phải ghi:

```text
bundle_type = model_only_question_plus_raw_chart
selected_suites = ["model_only"]
item_count = 100
completed_pair_count = 100
retrieval_executed = false
derived_chart_features_used = false
corpus_context_used = false
```

Bundle chỉ chứa câu hỏi, dữ liệu lá số, nhãn vàng phục vụ đánh giá và prompt tối thiểu. Nó không chứa context sách hoặc kết quả retrieval.

## C. Context bundle bằng Kaggle CLI

Cài và đăng nhập Kaggle CLI theo hướng dẫn tài khoản Kaggle, sau đó tạo staging folder chỉ chứa ZIP:

```powershell
New-Item -ItemType Directory -Force .\kaggle_context_dataset
Copy-Item .\artifacts\model_only_bundle_v1.zip .\kaggle_context_dataset\
kaggle datasets init -p .\kaggle_context_dataset
```

Mở `dataset-metadata.json`, điền ID/title của tài khoản và đặt private nếu phiên bản CLI hỗ trợ trường đó. Sau đó:

```powershell
kaggle datasets create -p .\kaggle_context_dataset
```

Nếu CLI yêu cầu thiết lập visibility trên website, tạo xong rồi chuyển dataset sang Private trước khi share.

## D. Add Input cho notebook 02

Mỗi lần chạy baseline model-only chỉ nên mount:

1. `tuviqa-model-only-bundle-v1`;
2. một trong hai model datasets.

Không mount cả Qwen và Gemma nếu không cần; việc này làm tăng disk usage và dễ chọn nhầm asset.

Sau khi Add Input, chạy cell resolver. Output mong đợi:

```python
{
  'bundle': '/kaggle/input/...',
  'model_assets': '/kaggle/input/...'
}
```

Nếu resolver tìm thấy nhiều input, điền thủ công `BUNDLE_INPUT` hoặc `MODEL_ASSET_DIR` ở cell config.

Đặt `RUNNER='M'`. Cell resolver sẽ kiểm tra bundle thật sự chứa suite `model_only`; nếu gắn nhầm bundle RAG 300 cặp, notebook dừng trước khi tải model.

## E. Kiểm tra trước khi chia sẻ

Model dataset:

- [ ] `asset_manifest.json` có đúng model ID và pinned revision.
- [ ] Có `.safetensors`.
- [ ] Có tokenizer/config/processor files.
- [ ] Có wheelhouse Transformers >=4.51.
- [ ] Không có token hoặc `.cache` transfer metadata.

Model-only dataset:

- [ ] ZIP chứa đúng một `bundle_manifest.json`.
- [ ] Manifest báo 1 config, 100 items, 100 completed pairs.
- [ ] Ba cờ `retrieval_executed`, `derived_chart_features_used`, `corpus_context_used` đều là `false`.
- [ ] Không có `.env` hoặc credentials.

## F. Tải prediction ZIP sau official run

1. Cell cuối notebook 02 in đường dẫn `archive_path`.
2. Save Version để giữ output nếu session sắp hết thời gian.
3. Trong phần Output, tải đúng file `local_llm_predictions_*.zip`.
4. Không dùng ZIP smoke cho judging.
5. Mỗi member giữ hai ZIP official trên máy local để chạy notebook 03 cho config mình.
6. Sau Gemini judge, member gửi A `gemini_judge_shard_{B|C|D}.zip`; prediction ZIP vẫn nên lưu để audit.
