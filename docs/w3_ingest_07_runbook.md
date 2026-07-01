# W3-INGEST-07 Kaggle Runbook

Runbook nay chi mo ta cach chay W3-INGEST bang bo notebook Kaggle trong `notebooks/kaggle/`. Kaggle la noi sinh artifact offline; notebook khong ghi Neo4j hoac Supabase. Cac buoc local import sau Kaggle chi duoc giu ngan gon o cuoi tai lieu.

Notebook da duoc cap nhat de ho tro hai kieu mount input pho bien:

- `/kaggle/input/<dataset-slug>`
- `/kaggle/input/datasets/dinhbaobao/<dataset-slug>`

Artifact cua notebook truoc co the duoc doc duoi hai dang:

- file `.zip`
- folder da duoc Kaggle tu dong unzip

## Muc Tieu

Hoan tat W3-INGEST qua duong `local-kaggle`:

1. Chunk corpus theo strategy.
2. Extract entity bang Qwen/local LLM tren Kaggle.
3. Export relation/graph payload importable, khong ghi DB.
4. Sinh BGE-M3 embedding artifacts theo slot `bge_m3`.
5. Tai artifact ve local de import graph, import embedding va chay retrieval smoke.

Strategies hien dung:

- `chunk_fixed_512`
- `chunk_structure_parent_child`
- `chunk_semantic_embedding_bge_m3`

`chunk_semantic_embedding_bge_m3` la strategy rieng cho BGE-M3, khong ghi de baseline Gemini `chunk_semantic_embedding`.

## Source Of Truth

Trong mot notebook Kaggle dang chay, source of truth tam thoi la:

```text
/kaggle/working/w3_local_outputs/
```

Layout ky vong:

```text
w3_local_outputs/
|-- chunks/
|-- entities/
|-- payloads/
|-- embeddings/
|-- reports/
`-- state/
```

Cac notebook 00-04 la cac notebook doc lap. Save Version cua notebook sau khong nhin thay `/kaggle/working` cua notebook truoc. Vi vay source of truth giua cac notebook la zip artifact:

```text
w3_local_outputs_01_<RUN_TAG>.zip
w3_local_outputs_02_<RUN_TAG>.zip
w3_local_outputs_03_<RUN_TAG>.zip
w3_local_outputs_<RUN_TAG>.zip
```

De chay tiep notebook sau, ban phai attach/upload artifact cua notebook truoc lam Kaggle input dataset, roi set `PREVIOUS_OUTPUT_SLUGS` trong notebook sau. Artifact nay co the la file zip hoac folder da unzip.

Cac file duoi `benchmark/tuvi_golden_dataset/reports/w3_ingest_07/` thuoc local runner cu va khong dai dien cho trang thai notebook Kaggle hien tai.

## 1. Chuan Bi Kaggle Datasets

Attach 2 Kaggle datasets vao moi notebook.

### Corpus Dataset

Slug mac dinh trong notebook:

```python
CORPUS_SLUG = "tuvi-golden-corpus"
```

Dataset nay khong duoc chi chua `corpus/`. No phai chua toi thieu:

```text
benchmark/
`-- tuvi_golden_dataset/
    |-- corpus/
    |   |-- TVKL_clean.json
    |   |-- TVNL_clean.json
    |   |-- TVHS_clean.json
    |   `-- TVGM_clean.json
    `-- guideline/
        `-- source_registry.json
```

Khuyen nghi dong goi nguyen subtree toi thieu:

```text
benchmark/tuvi_golden_dataset/corpus/
benchmark/tuvi_golden_dataset/guideline/
```

Ly do: `chunk_text.py` can `source_registry.json` de doc metadata nguon. Neu thieu file nay, notebook 01 co the fail truoc khi sinh chunks.

### Scripts Dataset

Slug mac dinh trong notebook:

```python
SCRIPTS_SLUG = "tuvi-battu-scripts"
```

Dataset nay phai chua:

```text
scripts/
configs/
backend/requirements-kaggle.txt
```

Cac script quan trong phai co:

- `scripts/chunk_text.py`
- `scripts/extract_entities.py`
- `scripts/write_graph_provenance.py`
- `scripts/embed_chunks.py`
- `scripts/run_w3_ingest_07.py`
- `scripts/import_graph_payload.py`
- `scripts/import_embedding_artifacts.py`
- `scripts/local_embeddings.py`
- `scripts/local_llm.py`

Notebook 01 va 03 nen truyen explicit:

```text
--source-registry CORPUS_DIR / "guideline" / "source_registry.json"
```

Cach nay tranh loi script mac dinh tim guideline theo `SCRIPTS_DIR`.

## 2. Chia Partition Tren Kaggle

Mac dinh chia theo strategy, khong chia theo source cho notebook 01-03.

Version A:

```python
RUN_TAG = "part_a"
PARTITION_MODE = "strategy"
SELECTED_STRATEGIES = ["chunk_fixed_512", "chunk_structure_parent_child"]
SELECTED_SOURCES = ["TVKL", "TVNL", "TVHS", "TVGM"]
```

Version B:

```python
RUN_TAG = "part_b"
PARTITION_MODE = "strategy"
SELECTED_STRATEGIES = ["chunk_semantic_embedding_bge_m3"]
SELECTED_SOURCES = ["TVKL", "TVNL", "TVHS", "TVGM"]
```

Khong de 2 Kaggle versions xu ly cung mot strategy vao cung mot artifact set. Neu chay trung strategy, state va artifact co the ghi de nhau khi merge.

## 3. Artifact Handoff Giua Cac Notebook Doc Lap

Moi notebook phai duoc coi la mot run moi, khong co working cache cua notebook truoc.

Quy uoc:

- Notebook 01 tao `w3_local_outputs_01_<RUN_TAG>.zip`.
- Notebook 02 restore zip tu notebook 01 va tao `w3_local_outputs_02_<RUN_TAG>.zip`.
- Notebook 03 restore zip tu notebook 02 va tao `w3_local_outputs_03_<RUN_TAG>.zip`.
- Notebook 04 restore zip tu notebook 03 va tao final `w3_local_outputs_<RUN_TAG>.zip`.

Co 2 cach dua zip sang notebook sau:

1. Save Version notebook truoc, roi add output cua version do lam input dataset cho notebook sau.
2. Tai zip ve may, tao/upload Kaggle dataset rieng, roi attach dataset do vao notebook sau.

Trong notebook sau, set:

```python
PREVIOUS_OUTPUT_SLUGS = ["<duong-dan-tuong-doi-duoi-input-root-chua-artifact-cua-notebook-truoc>"]
```

Neu input dataset chi chua dung mot artifact theo `RUN_TAG`, co the de:

```python
PREVIOUS_OUTPUT_SLUGS = []
```

Notebook se tu tim folder/file tuong ung, vi du `w3_local_outputs_01_part_a`, ben duoi `INPUT_ROOT`.

Vi du cho `part_a`:

```python
# Notebook 02, neu Kaggle dataset da tu unzip zip thanh folder
PREVIOUS_OUTPUT_SLUGS = ["w3-local-outputs/w3_local_outputs_01_part_a"]

# Notebook 03
PREVIOUS_OUTPUT_SLUGS = ["w3-local-outputs/w3_local_outputs_02_part_a"]

# Notebook 04
PREVIOUS_OUTPUT_SLUGS = ["w3-local-outputs/w3_local_outputs_03_part_a"]
```

Neu dataset cua ban van giu file zip, van co the dung kieu:

```python
PREVIOUS_OUTPUT_SLUGS = ["w3-01-part-a-output"]
```

Voi `part_b`, dung path rieng cho part_b. Khong attach chung part_a va part_b vao cung mot notebook run neu `RUN_TAG`/`SELECTED_STRATEGIES` dang chi xu ly mot partition.

## 4. Chay Notebook 00 - Setup And Smoke

Notebook:

```text
notebooks/kaggle/00_setup_and_smoke.ipynb
```

Muc tieu:

- Install dependencies tu `backend/requirements-kaggle.txt`.
- Kiem tra `CORPUS_DIR`.
- Kiem tra `CORPUS_DIR / "guideline" / "source_registry.json"`.
- Kiem tra cac scripts import moi.
- Sinh manifest local-kaggle o `reports/`.
- Tao layout `w3_local_outputs/`.

Thao tac:

1. Attach dung 2 datasets.
2. Sua `RUN_TAG`, `PARTITION_MODE`, `SELECTED_STRATEGIES`, `SELECTED_SOURCES`.
3. Run all cells.
4. Chi chuyen sang notebook 01 neu cell smoke pass va khong bao thieu `source_registry.json`.

Neu notebook fallback sang path local, kiem tra lai slug va cau truc dataset.

## 5. Chay Notebook 01 - Chunk BGE-M3

Notebook:

```text
notebooks/kaggle/01_chunk_bge_m3.ipynb
```

Muc tieu:

- Sinh chunks duoi `w3_local_outputs/chunks/<strategy>/`.
- Sinh summary duoi `w3_local_outputs/reports/<strategy>_chunk_summary.json`.
- Voi `chunk_semantic_embedding_bge_m3`, sinh them semantic similarity report.
- Dong goi zip `w3_local_outputs_01_<RUN_TAG>.zip`.

Dieu kien dau vao:

- `benchmark/tuvi_golden_dataset/corpus/` ton tai trong corpus dataset.
- `benchmark/tuvi_golden_dataset/guideline/source_registry.json` ton tai.
- Notebook truyen `--source-registry` tro ve guideline trong `CORPUS_DIR`.

Thao tac:

1. Giu cung partition contract nhu notebook 00.
2. Run all cells.
3. Kiem tra summary cuoi notebook:
   - strategy nao da chay
   - strategy nao skip
   - file summary nao ton tai
4. Kiem tra cell pack artifact da ghi zip:
   - `w3_local_outputs_01_part_a.zip`
   - hoac `w3_local_outputs_01_part_b.zip`
5. Save Version notebook 01.
6. Tai zip ve hoac attach output version 01 lam input dataset cho notebook 02.

Ky vong:

- Version A chi sinh chunks cho `chunk_fixed_512` va `chunk_structure_parent_child`.
- Version B chi sinh chunks cho `chunk_semantic_embedding_bge_m3`.

## 6. Chay Notebook 02 - Entity Qwen

Notebook:

```text
notebooks/kaggle/02_entity_qwen.ipynb
```

Muc tieu:

- Doc chunks da sinh o notebook 01.
- Ghi entities duoi `w3_local_outputs/entities/<strategy>/`.
- Ghi entity reports va state duoi `reports/` va `state/`.
- Dong goi zip `w3_local_outputs_02_<RUN_TAG>.zip`.

Notebook nay dung `--resume`.

Thao tac:

1. Attach corpus dataset, scripts dataset, va zip output tu notebook 01.
2. Giu cung `RUN_TAG` va `SELECTED_STRATEGIES` voi notebook 01 cho version dang chay.
3. Set `PREVIOUS_OUTPUT_SLUGS` den path chua artifact cua notebook 01, hoac de `[]` neu input root chi co artifact dung `RUN_TAG`.
4. Run all cells.
5. Kiem tra dau notebook co in `RESTORED_OUTPUTS` va zip notebook 01 da duoc restore.
6. Kiem tra summary cuoi:
   - `<strategy>_entities.jsonl`
   - `<strategy>_entity_summary.json`
   - `<strategy>_entity_review.json`
   - `<strategy>_entity_state.json`
7. Kiem tra cell pack artifact da ghi `w3_local_outputs_02_<RUN_TAG>.zip`.
8. Save Version notebook 02.
9. Tai zip ve hoac attach output version 02 lam input dataset cho notebook 03.

Khuyen nghi khong chia notebook 02 theo source, vi entity output hien duoc to chuc theo strategy.

## 7. Chay Notebook 03 - Relation Va Payload Export

Notebook:

```text
notebooks/kaggle/03_relation_qwen_hybrid.ipynb
```

Muc tieu:

- Chay `write_graph_provenance.py` o `--dry-run`.
- Khong ghi Neo4j/Supabase.
- Export graph payload importable vao `w3_local_outputs/payloads/<strategy>/`.
- Dong goi zip `w3_local_outputs_03_<RUN_TAG>.zip`.

Notebook phai truyen:

```text
--payload-output-dir /kaggle/working/w3_local_outputs/payloads/<strategy>
--source-registry /kaggle/input/<CORPUS_SLUG>/benchmark/tuvi_golden_dataset/guideline/source_registry.json
```

Thao tac:

1. Attach corpus dataset, scripts dataset, va zip output tu notebook 02.
2. Giu cung `RUN_TAG` va strategy partition voi notebook 01 va 02.
3. Set `PREVIOUS_OUTPUT_SLUGS` den path chua artifact cua notebook 02, hoac de `[]` neu input root chi co artifact dung `RUN_TAG`.
4. Run all cells.
5. Kiem tra dau notebook co in `RESTORED_OUTPUTS` va zip notebook 02 da duoc restore.
6. Kiem tra summary cuoi:
   - graph summary ton tai
   - relation review ton tai
   - `payloads/<strategy>/` ton tai
7. Kiem tra cell pack artifact da ghi `w3_local_outputs_03_<RUN_TAG>.zip`.
8. Save Version notebook 03.
9. Tai zip ve hoac attach output version 03 lam input dataset cho notebook 04.

Neu `payloads/<strategy>/` chua co, graph step chua du de import local.

## 8. Chay Notebook 04 - Embed Va Pack Artifacts

Notebook:

```text
notebooks/kaggle/04_embed_and_pack_artifacts.ipynb
```

Muc tieu:

- Sinh BGE-M3 embedding JSONL vao `w3_local_outputs/embeddings/<strategy>/`.
- Ghi reports retrieval smoke offline.
- Dong goi zip `w3_local_outputs_<RUN_TAG>.zip`.

Notebook nay phai dung:

```text
--embedding-slot bge_m3
```

Thao tac:

1. Attach corpus dataset, scripts dataset, va zip output tu notebook 03.
2. Giu strategy partition mac dinh va cung `RUN_TAG`.
3. Set `PREVIOUS_OUTPUT_SLUGS` den path chua artifact cua notebook 03, hoac de `[]` neu input root chi co artifact dung `RUN_TAG`.
4. Run all cells.
5. Kiem tra dau notebook co in `RESTORED_OUTPUTS` va zip notebook 03 da duoc restore.
6. Tai final zip `w3_local_outputs_<RUN_TAG>.zip` ve may local.

Chi dung source partition cho notebook 04 neu embedding la nut that thoi gian:

```python
PARTITION_MODE = "source"
SELECTED_SOURCES = ["TVKL", "TVNL"]
```

Khong doi source partition cho notebook 01-03 neu chua chu dong thiet ke lai flow merge entity/relation.

## 9. Resume Sau Khi Het Session

Vi moi notebook la doc lap, resume luon phu thuoc vao viec restore artifact truoc do.

Trong cung mot notebook run:

- `--resume` dung state da nam trong `/kaggle/working/w3_local_outputs/state/`.

Sang notebook run moi hoac Save Version moi:

- Phai attach/upload artifact gan nhat.
- Set `PREVIOUS_OUTPUT_SLUGS`.
- Notebook se unzip ve:

```text
/kaggle/working/w3_local_outputs/
```

`--resume` khong the tu phuc hoi neu ban khong restore zip co `state/` va artifact da ghi.

Quy trinh an toan:

1. Moi notebook sau khi chay xong phai co zip output.
2. Save Version notebook do.
3. Notebook tiep theo phai attach/upload artifact cua step truoc.
4. Chi rerun cung `RUN_TAG` va cung strategy partition.

## 10. Chay Song Song 2 Kaggle Versions

Kaggle co the chay nhieu saved versions. Cach an toan la chia theo strategy.

Version A:

- `RUN_TAG = "part_a"`
- `SELECTED_STRATEGIES = ["chunk_fixed_512", "chunk_structure_parent_child"]`

Version B:

- `RUN_TAG = "part_b"`
- `SELECTED_STRATEGIES = ["chunk_semantic_embedding_bge_m3"]`

Sau moi notebook step, ca hai part deu phai co zip rieng.

Sau notebook 01:

```text
w3_local_outputs_01_part_a.zip
w3_local_outputs_01_part_b.zip
```

Sau notebook 02:

```text
w3_local_outputs_02_part_a.zip
w3_local_outputs_02_part_b.zip
```

Sau notebook 03:

```text
w3_local_outputs_03_part_a.zip
w3_local_outputs_03_part_b.zip
```

Sau notebook 04, tai 2 final zip ve local:

```text
w3_local_outputs_part_a.zip
w3_local_outputs_part_b.zip
```

Merge theo strategy de co artifact root cuoi cung:

```text
local_kaggle/
|-- chunks/
|-- entities/
|-- payloads/
|-- embeddings/
|-- reports/
`-- state/
```

Khong merge bang cach ghi de mot strategy da co tu version khac.

## 11. Local Import Sau Kaggle

Dat artifact da merge vao:

```text
benchmark/tuvi_golden_dataset/local_kaggle/
```

Import graph payload theo tung strategy:

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts\import_graph_payload.py `
  --payload-input-dir benchmark\tuvi_golden_dataset\local_kaggle\payloads\chunk_fixed_512
```

Import BGE-M3 embeddings theo slot rieng:

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts\import_embedding_artifacts.py `
  --input benchmark\tuvi_golden_dataset\local_kaggle\embeddings\chunk_fixed_512 `
  --embedding-slot bge_m3
```

Chay retrieval smoke local:

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts\smoke_retrieval.py `
  --source-id TVGM `
  --chunking-strategy chunk_fixed_512 `
  --embedding-slot bge_m3
```

Lap lai cho cac strategy con lai neu muon acceptance day du.

## Acceptance Checklist

W3 local-Kaggle path duoc coi la san sang khi:

- Notebook 00 pass dataset/script smoke.
- Notebook 01 sinh chunks cho moi strategy duoc phan cong.
- Notebook 02 sinh entities va state cho moi strategy duoc phan cong.
- Notebook 03 sinh `payloads/<strategy>/` cho moi strategy can import.
- Notebook 04 sinh `embeddings/<strategy>/` va zip artifact.
- Local import graph payload khong goi lai LLM.
- Local import embeddings ghi vao slot `bge_m3`.
- Retrieval smoke local pass voi `--embedding-slot bge_m3`.

## Troubleshooting

### Notebook 01 bao thieu guideline/source registry

Kiem tra corpus dataset co file:

```text
benchmark/tuvi_golden_dataset/guideline/source_registry.json
```

Neu file co nhung van fail, kiem tra notebook 01 co truyen:

```text
--source-registry CORPUS_DIR / "guideline" / "source_registry.json"
```

### Notebook fallback sang path local

Kiem tra:

- Dataset da attach vao notebook chua.
- `CORPUS_SLUG`, `SCRIPTS_SLUG`, va `PREVIOUS_OUTPUT_SLUGS` dung chua.
- Cau truc dataset co dung root path khong.

Kaggle path ky vong:

```text
/kaggle/input/tuvi-golden-corpus/benchmark/tuvi_golden_dataset
/kaggle/input/tuvi-battu-scripts
/kaggle/input/datasets/dinhbaobao/tuvi-golden-corpus/benchmark/tuvi_golden_dataset
/kaggle/input/datasets/dinhbaobao/tuvi-battu-scripts
```

### Het GPU memory hoac session gan 12h

Uu tien:

1. Chia theo strategy nhu Version A/B.
2. Giam batch size embedding neu can.
3. Save Version sau tung notebook nang.
4. Tai zip artifact de co the restore `w3_local_outputs/` o session moi.
