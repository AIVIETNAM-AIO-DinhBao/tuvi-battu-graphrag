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

Kaggle notebooks nam o `notebooks/kaggle/`:

1. `00_setup_and_smoke.ipynb`
2. `01_chunk_bge_m3.ipynb`
3. `02_entity_qwen.ipynb`
4. `03_relation_qwen_hybrid.ipynb`
5. `04_embed_and_pack_artifacts.ipynb`

## Kaggle execution playbook

Phan nay la quy trinh thao tac chi tiet de chay W3-INGEST tren Kaggle, ke ca truong hop can chia lam 2 version song song va resume sau khi het session.

### 1. Tao va attach 2 Kaggle datasets

Can attach 2 datasets vao moi notebook:

1. Corpus dataset:
   - slug mac dinh: `tuvi-golden-corpus`
   - phai chua `benchmark/tuvi_golden_dataset/corpus/`
2. Scripts dataset:
   - slug mac dinh: `tuvi-battu-scripts`
   - phai chua `scripts/`, `configs/`, `backend/requirements-kaggle.txt`

Neu slug khac, sua `CORPUS_SLUG` va `SCRIPTS_SLUG` trong notebook.

### 2. Chia batch mac dinh theo strategy

Mac dinh duoc khuyen nghi la chia theo strategy, khong chia theo source cho entity/relation notebooks.

Version A:

- `RUN_TAG = 'part_a'`
- `PARTITION_MODE = 'strategy'`
- `SELECTED_STRATEGIES = ['chunk_fixed_512', 'chunk_structure_parent_child']`
- `SELECTED_SOURCES = ['TVKL', 'TVNL', 'TVHS', 'TVGM']`

Version B:

- `RUN_TAG = 'part_b'`
- `PARTITION_MODE = 'strategy'`
- `SELECTED_STRATEGIES = ['chunk_semantic_embedding_bge_m3']`
- `SELECTED_SOURCES = ['TVKL', 'TVNL', 'TVHS', 'TVGM']`

Khong de 2 version xu ly cung mot strategy trong cung mot dot chay. Dieu nay tranh dung do output, state va artifact bi trung lap.

### 3. Chay notebook 00 - Setup va smoke

Notebook: `00_setup_and_smoke.ipynb`

Muc tieu:

- install dependencies tu `requirements-kaggle.txt`
- xac nhan 2 scripts import moi ton tai:
  - `import_graph_payload.py`
  - `import_embedding_artifacts.py`
- sinh local-kaggle command manifest
- xac nhan layout output:
  - `chunks/`
  - `entities/`
  - `payloads/`
  - `embeddings/`
  - `reports/`
  - `state/`

Ban can:

1. Sua `RUN_TAG`, `PARTITION_MODE`, `SELECTED_STRATEGIES`, `SELECTED_SOURCES` theo version dang chay.
2. Chay toan bo notebook.
3. Kiem tra cell cuoi co manifest va thong bao output layout.

Neu notebook 00 khong pass, khong nen chay 01-04.

### 4. Chay notebook 01 - Chunking

Notebook: `01_chunk_bge_m3.ipynb`

Muc tieu:

- sinh `chunks/<strategy>/`
- sinh `reports/<strategy>_chunk_summary.json`
- neu strategy la `chunk_semantic_embedding_bge_m3`, sinh them `reports/<strategy>_semantic_similarity_report.json`

Ban can:

1. Giu cung partition contract nhu notebook 00.
2. Chay notebook.
3. Kiem tra cell summary cuoi:
   - strategy nao da chay
   - strategy nao bi skip
   - file summary nao da ton tai

Neu Version A:

- se chi sinh chunks cho `chunk_fixed_512` va `chunk_structure_parent_child`

Neu Version B:

- se chi sinh chunks cho `chunk_semantic_embedding_bge_m3`

### 5. Chay notebook 02 - Entity extraction

Notebook: `02_entity_qwen.ipynb`

Muc tieu:

- doc chunks da sinh
- ghi `entities/<strategy>/<strategy>_entities.jsonl`
- ghi:
  - `reports/<strategy>_entity_summary.json`
  - `reports/<strategy>_entity_review.json`
  - `state/<strategy>_entity_state.json`

Notebook nay da bat `--resume`.

Ban can:

1. Giu cung `SELECTED_STRATEGIES` cua notebook 01 cho cung version.
2. Chay notebook.
3. Kiem tra cell summary cuoi:
   - file entity summary
   - file entity review
   - file state

Khuyen nghi:

- khong chia notebook 02 theo source
- neu session co dau hieu sap het, dung o cuoi notebook, Save Version, va tai artifact ve

### 6. Chay notebook 03 - Relation/payload export

Notebook: `03_relation_qwen_hybrid.ipynb`

Muc tieu:

- chay `write_graph_provenance.py` o `--dry-run`
- sinh:
  - `reports/<strategy>_graph_write_summary.json`
  - `reports/<strategy>_relation_review.json`
  - `state/<strategy>_graph_relation_state.json`
  - `payloads/<strategy>/`

Quan trong:

- notebook nay da truyen `--payload-output-dir`
- payloads nay la artifact importable, dung cho local import ve sau ma khong can chay lai relation LLM

Ban can:

1. Giu cung partition strategy nhu 01 va 02.
2. Chay notebook.
3. Kiem tra cell summary cuoi:
   - `summary` ton tai
   - `review` ton tai
   - `payloads/<strategy>/` ton tai

Neu `payloads/<strategy>/` chua co, khong duoc coi la hoan tat graph step.

### 7. Chay notebook 04 - Embedding va dong goi artifact

Notebook: `04_embed_and_pack_artifacts.ipynb`

Muc tieu:

- sinh embeddings JSONL trong:
  - `embeddings/<strategy>/<source>_<strategy>_embeddings.jsonl`
- sinh:
  - `reports/embed_<source>_<strategy>.json`
  - `reports/retrieval_<source>_<strategy>.json`
  - `state/<source>_<strategy>_embedding_state.json`
- dong goi zip:
  - `w3_local_outputs_<run_tag>.zip`

Notebook nay da:

- bat `--resume`
- truyen explicit `--embedding-slot bge_m3`
- giu nguyen `state/`, `payloads/`, `embeddings/`, `reports/` trong zip

Ban co 2 cach chay:

1. Giu mac dinh chia theo strategy:
   - dung khi muon nhat quan voi 01-03
2. Neu can, doi sang chia theo source:
   - `PARTITION_MODE = 'source'`
   - `SELECTED_SOURCES = [...]`
   - chi nen dung cho notebook 04 neu embeddings la nut that

Khuyen nghi:

- van uu tien chia theo strategy cho ca dot chay
- chi dung source partition cho notebook 04 khi can toi uu thoi gian buoc embedding

### 8. Resume sau khi het 12h session

Co 2 muc resume:

1. Resume trong cung workspace/session:
   - supported boi `--resume`
2. Resume o session moi:
   - chi co tac dung neu ban giu duoc `w3_local_outputs/`
   - phai con:
     - `state/`
     - artifact da ghi trong `entities/`, `payloads/`, `embeddings/`, `reports/`

Quy trinh an toan:

1. Sau moi notebook quan trong, Save Version.
2. O cuoi notebook 04, tai `w3_local_outputs_<run_tag>.zip`.
3. Neu can session moi, giai nen artifact cu vao `/kaggle/working/w3_local_outputs/` truoc khi rerun.
4. Rerun cung notebook cung partition contract; `--resume` se skip phan da xong neu state va artifact con day du.

Khong co `state/` thi `--resume` khong giup duoc.

### 9. Merge artifact tu 2 Kaggle versions

Sau khi Version A va Version B chay xong:

1. Tai ca hai file zip:
   - `w3_local_outputs_part_a.zip`
   - `w3_local_outputs_part_b.zip`
2. Giai nen ra hai thu muc tam.
3. Merge theo strategy vao mot artifact root local duy nhat.

Can ket qua cuoi cung co:

- `chunks/chunk_fixed_512/`
- `chunks/chunk_structure_parent_child/`
- `chunks/chunk_semantic_embedding_bge_m3/`
- `entities/...`
- `payloads/...`
- `embeddings/...`
- `reports/...`
- `state/...`

Khong merge theo kieu de 2 version ghi de cung mot strategy.

## Official local-Kaggle import flow

Kaggle GPU batch is now treated as an artifact producer only. Local web/runtime on laptop does not rerun chunk/entity/relation LLM steps.

### 1. Dat artifact vao repo local

Khuyen nghi giai nen artifact da merge vao:

```text
benchmark/tuvi_golden_dataset/local_kaggle/
```

Trong do:

- `benchmark/tuvi_golden_dataset/local_kaggle/chunks`
- `benchmark/tuvi_golden_dataset/local_kaggle/entities`
- `benchmark/tuvi_golden_dataset/local_kaggle/payloads`
- `benchmark/tuvi_golden_dataset/local_kaggle/embeddings`
- `benchmark/tuvi_golden_dataset/reports/w3_ingest_07_local_kaggle`

### 2. Import graph payload khong goi lai LLM

Chay theo tung strategy:

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts\import_graph_payload.py `
  --payload-input-dir benchmark\tuvi_golden_dataset\local_kaggle\payloads\chunk_fixed_512
```

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts\import_graph_payload.py `
  --payload-input-dir benchmark\tuvi_golden_dataset\local_kaggle\payloads\chunk_structure_parent_child
```

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts\import_graph_payload.py `
  --payload-input-dir benchmark\tuvi_golden_dataset\local_kaggle\payloads\chunk_semantic_embedding_bge_m3
```

### 3. Import BGE-M3 embeddings vao slot rieng

Chay theo tung strategy:

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts\import_embedding_artifacts.py `
  --input benchmark\tuvi_golden_dataset\local_kaggle\embeddings\chunk_fixed_512 `
  --embedding-slot bge_m3
```

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts\import_embedding_artifacts.py `
  --input benchmark\tuvi_golden_dataset\local_kaggle\embeddings\chunk_structure_parent_child `
  --embedding-slot bge_m3
```

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts\import_embedding_artifacts.py `
  --input benchmark\tuvi_golden_dataset\local_kaggle\embeddings\chunk_semantic_embedding_bge_m3 `
  --embedding-slot bge_m3
```

### 4. Chay retrieval smoke local

Chay toi thieu 1 source dai dien cho moi strategy. Neu muon kiem tra day du, chay cho ca 4 source.

Vi du:

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts\smoke_retrieval.py `
  --source-id TVGM `
  --chunking-strategy chunk_fixed_512 `
  --embedding-slot bge_m3
```

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts\smoke_retrieval.py `
  --source-id TVGM `
  --chunking-strategy chunk_structure_parent_child `
  --embedding-slot bge_m3
```

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts\smoke_retrieval.py `
  --source-id TVGM `
  --chunking-strategy chunk_semantic_embedding_bge_m3 `
  --embedding-slot bge_m3
```

### 5. Runtime local dung CPU embedding

Local web/runtime query embedding dung:

- `DENSE_QUERY_EMBEDDING_BACKEND=local`
- `DENSE_QUERY_EMBEDDING_MODEL=BAAI/bge-m3`
- `DENSE_QUERY_EMBEDDING_DEVICE=cpu`
- `DENSE_QUERY_EMBEDDING_SLOT=bge_m3`

Laptop local khong can GPU de phuc vu query embedding runtime.

## Acceptance checklist for W3 local-Kaggle path

W3 local-Kaggle path duoc coi la hoan tat khi:

1. Ca 3 strategy da co:
   - chunk artifacts
   - entity artifacts
   - graph payloads
   - embedding artifacts
2. `payloads/<strategy>/` ton tai cho moi strategy can import.
3. `embeddings/<strategy>/` ton tai cho moi source-strategy can import.
4. Import local khong goi lai LLM.
5. Retrieval smoke pass voi `--embedding-slot bge_m3`.
6. Runtime query embedding local tra vector `1024` dimensions tren CPU.

Notes:

- `chunk_semantic_embedding_bge_m3` remains a separate auxiliary strategy. Do not rename it to `chunk_semantic_embedding`, and do not overwrite Gemini baseline embeddings.
- Same Neo4j database is used for both backends, but vectors are isolated by slot:
  - Gemini: `Chunk.embedding` + `chunkVector` + `768`
  - BGE-M3: `Chunk.embedding_bge_m3` + `chunkVectorBgeM3` + `1024`
- `write_graph_provenance.py --payload-output-dir ...` exports importable JSONL payloads in both `dry-run` and production mode.
