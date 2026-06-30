# W3-INGEST-07 Runbook

Tài liệu này ghi cách chạy full-corpus ingest, kiểm tra tiến trình, resume sau quota, và hướng thay thế Gemini bằng Kaggle/open-source models.

## Mục tiêu

`W3-INGEST-07` chạy 3 official chunking strategies trên 4 corpus `TVKL`, `TVNL`, `TVHS`, `TVGM`:

- `chunk_fixed_512`
- `chunk_structure_parent_child`
- `chunk_semantic_embedding`

Pipeline đầy đủ gồm:

1. Chunking
2. Entity extraction
3. Graph/relation extraction
4. Embedding + retrieval smoke

Task chỉ được claim completed khi production run xong, không tính dry-run/mock artifacts.

## Chuẩn bị

Kiểm tra `.env` có đủ Gemini keys và DB credentials:

- `GEMINI_API_KEYS` dạng comma-separated, hoặc
- `GEMINI_API_KEY`, `GEMINI_API_KEY_2`, `GEMINI_API_KEY_3`, ...
- Neo4j/Supabase env vars cho graph, embedding, retrieval.

Không commit `.env` hoặc raw API keys.

Chạy regression trước khi ingest:

```powershell
.\.venv\Scripts\python.exe -m pytest backend\tests\test_chunk_text.py backend\tests\test_extract_entities.py backend\tests\test_write_graph_provenance.py backend\tests\test_embed_chunks.py backend\tests\test_smoke_retrieval.py backend\tests\test_run_w3_ingest_07.py -q -p no:cacheprovider
```

## Cách chạy

Sinh manifest trước, không gọi Gemini/DB:

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts\run_w3_ingest_07.py --mode plan
```

Chạy production và lưu log live:

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts\run_w3_ingest_07.py --mode production --resume 2>&1 | Tee-Object -FilePath benchmark\tuvi_golden_dataset\reports\w3_ingest_07\production_run.log -Append
```

Nếu gặp RPM/TPM/RPD quota, chờ quota reset rồi chạy lại đúng command trên. Runner dùng state để resume.

Chỉ chạy dry-run khi cần kiểm orchestration offline:

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts\run_w3_ingest_07.py --mode dry-run --resume --mock-llm --mock-embedding
```

Dry-run sinh mock artifacts, không dùng để claim production. Nếu muốn tránh bẩn artifact chính, truyền `--reports-dir`, `--chunks-dir`, `--entities-dir` sang thư mục tạm.

## Kiểm tra tiến trình

File chính:

- `benchmark/tuvi_golden_dataset/reports/w3_ingest_07/w3_ingest_07_command_manifest.json`
- `benchmark/tuvi_golden_dataset/reports/w3_ingest_07/w3_ingest_07_state.json`
- `benchmark/tuvi_golden_dataset/reports/w3_ingest_07/w3_ingest_07_run_summary.json`

Xem summary:

```powershell
Get-Content benchmark\tuvi_golden_dataset\reports\w3_ingest_07\w3_ingest_07_run_summary.json -Raw
```

Xem command nào done/partial/skipped:

```powershell
$state = Get-Content benchmark\tuvi_golden_dataset\reports\w3_ingest_07\w3_ingest_07_state.json -Raw | ConvertFrom-Json
$state.commands.PSObject.Properties |
  ForEach-Object {
    $c = $_.Value
    [pscustomobject]@{
      command = $_.Name
      mode = $c.mode
      phase = $c.phase
      status = $c.status
      started = $c.started_at
      completed = $c.completed_at
      failed = $c.failed_at
    }
  } |
  Sort-Object mode, command |
  Format-Table -AutoSize
```

Đếm chunks theo strategy/corpus:

```powershell
Get-ChildItem benchmark\tuvi_golden_dataset\chunks -Directory |
  ForEach-Object {
    $strategy = $_.Name
    Get-ChildItem $_.FullName -Filter '*_chunks.jsonl' |
      ForEach-Object {
        [pscustomobject]@{
          strategy = $strategy
          corpus = $_.BaseName.Replace('_chunks', '')
          lines = (Get-Content $_.FullName | Measure-Object -Line).Lines
        }
      }
  } |
  Format-Table -AutoSize
```

Đếm entity files:

```powershell
Get-ChildItem benchmark\tuvi_golden_dataset\entities -Recurse -Filter '*.jsonl' |
  ForEach-Object {
    [pscustomobject]@{
      file = $_.FullName
      lines = (Get-Content $_.FullName | Measure-Object -Line).Lines
      bytes = $_.Length
    }
  } |
  Format-Table -AutoSize
```

Kiểm embed/retrieval reports:

```powershell
Get-ChildItem benchmark\tuvi_golden_dataset\reports\w3_ingest_07 -Filter 'embed_*.json' | Measure-Object
Get-ChildItem benchmark\tuvi_golden_dataset\reports\w3_ingest_07 -Filter 'retrieval_*.json' | Measure-Object
```

Expected completed state:

- `w3_ingest_07_run_summary.json`: `completed=true`
- 21 commands trong manifest.
- 3 chunk summaries.
- 3 entity summaries/reviews.
- 3 graph write summaries + relation reviews.
- 12 `embed_*.json`.
- 12 `retrieval_*.json`.

## Dọn artifacts an toàn

Có thể xóa dry-run/mock artifacts nếu không cần audit:

- `benchmark/tuvi_golden_dataset/reports/w3_ingest_07/dry-run/`
- mock entity outputs trong `benchmark/tuvi_golden_dataset/entities/`
- mock `chunk_semantic_embedding` chunks nếu metadata ghi `mock-semantic-hash-*`
- dry-run graph/relation summaries có `dry_run=true`

Không xóa các file này trừ khi muốn restart production từ đầu:

- `w3_ingest_07_state.json`
- `w3_ingest_07_command_manifest.json`
- `w3_ingest_07_run_summary.json`
- `reports/w3_ingest_07/production/`

Không xóa config:

- `configs/chunking_strategies.yaml`
- `configs/entity_extraction.yaml`

## Kaggle và open-source models thay Gemini

Có thể dùng Kaggle/open-source models, nhưng nên coi là một backend ingest khác, không lẫn với Gemini baseline.

Các phần phù hợp để chạy trên Kaggle:

- Fixed/structure chunking: chạy CPU được, không cần Gemini.
- Semantic chunking: có thể thay Gemini embedding bằng open-source embeddings như E5/BGE/multilingual sentence embeddings.
- Entity/relation extraction: có thể thử LLM open-source dạng instruction model.
- Offline artifact generation: sinh chunks/entities/relations thành JSONL rồi tải về chạy graph/embed/retrieval ở môi trường có DB.

Các điểm cần sửa nếu dùng open-source:

- Thêm adapter embedding/LLM mới, ví dụ `--embedding-backend local` hoặc `--llm-backend local`.
- Ghi rõ `embedding_model_for_chunking`, `extraction_model`, `relation_model`.
- Đổi `chunking_version` hoặc strategy id nếu chunk boundary thay đổi, để không trộn benchmark với Gemini baseline.
- Giữ schema validation, JSON repair, dedupe, provenance, resume state như hiện tại.
- Với model local, vẫn cần deterministic mock/offline tests.

Ưu điểm:

- Không bị Gemini RPM/TPM/RPD.
- Có thể chạy batch dài trên GPU notebook.
- Tái lập tốt nếu pin model checkpoint, prompt, quantization, seed.

Rủi ro:

- Kaggle quota/GPU availability thay đổi theo tài khoản và thời điểm.
- Notebook có thể không phù hợp để ghi trực tiếp Neo4j/Supabase production; tốt hơn là sinh artifacts offline rồi import ở local/cloud.
- LLM open-source nhỏ có thể kém ổn định về JSON và entity normalization hơn Gemini.
- Embedding model đổi sẽ làm semantic chunking/retrieval benchmark không so sánh trực tiếp được với Gemini baseline.

Khuyến nghị:

1. Giữ Gemini path làm official baseline theo spec.
2. Thêm Kaggle/open-source như auxiliary experiment, ví dụ `chunk_semantic_embedding_local`.
3. Sinh artifact offline trên Kaggle, tải về repo, rồi chạy graph write/embed/retrieval smoke ở local/cloud.
4. Chỉ promote thành baseline mới khi metrics retrieval và review report tốt hơn hoặc tương đương Gemini.
## Local-Kaggle profile

Repo co profile local/Kaggle rieng de chay khong can Gemini API:

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts\run_w3_ingest_07.py --mode plan --profile local-kaggle
```

Profile nay dung:

- `BAAI/bge-m3` cho semantic chunking va embeddings, `1024` dimensions.
- `Qwen/Qwen2.5-7B-Instruct` cho entity/relation LLM augmentation.
- `chunk_semantic_embedding_bge_m3` la auxiliary strategy rieng, khong doi official `chunk_semantic_embedding`.
- Graph/relation trong local-Kaggle chay dry-run artifact, khong ghi Neo4j/Supabase.
- Embedding trong local-Kaggle ghi JSONL artifact va offline retrieval smoke, khong can DB.

Default artifact dirs:

- `benchmark/tuvi_golden_dataset/local_kaggle/chunks`
- `benchmark/tuvi_golden_dataset/local_kaggle/entities`
- `benchmark/tuvi_golden_dataset/local_kaggle/embeddings`
- `benchmark/tuvi_golden_dataset/reports/w3_ingest_07_local_kaggle`

Kaggle notebooks nam o `notebooks/kaggle/`:

1. `00_setup_and_smoke.ipynb`
2. `01_chunk_bge_m3.ipynb`
3. `02_entity_qwen.ipynb`
4. `03_relation_qwen_hybrid.ipynb`
5. `04_embed_and_pack_artifacts.ipynb`
