# Kaggle Notebooks for Tu Vi GraphRAG Ingestion

These notebooks are the current operational path for completing `W3-INGEST` when Gemini quota is not stable enough for full-corpus batch runs.

Kaggle is an **artifact producer only**:
- chunk/entity/relation/embedding generation happens on Kaggle
- Neo4j and Supabase imports happen later on local/cloud
- no database writes occur from the notebooks

## Required Kaggle datasets

Attach two Kaggle datasets to each notebook.

### 1. Corpus dataset

Default slug: `tuvi-golden-corpus`

Expected contents:

```text
benchmark/
└── tuvi_golden_dataset/
    └── corpus/
        ├── TVKL_clean.json
        ├── TVNL_clean.json
        ├── TVHS_clean.json
        └── TVGM_clean.json
```

### 2. Scripts dataset

Default slug: `tuvi-battu-scripts`

Expected contents:

```text
scripts/
├── chunk_text.py
├── extract_entities.py
├── write_graph_provenance.py
├── embed_chunks.py
├── run_w3_ingest_07.py
├── import_graph_payload.py
├── import_embedding_artifacts.py
├── local_embeddings.py
├── local_llm.py
└── gemini_keys.py
configs/
├── chunking_strategies.yaml
└── entity_extraction.yaml
backend/
└── requirements-kaggle.txt
```

## Notebook order

Run in this order:

1. `00_setup_and_smoke.ipynb`
2. `01_chunk_bge_m3.ipynb`
3. `02_entity_qwen.ipynb`
4. `03_relation_qwen_hybrid.ipynb`
5. `04_embed_and_pack_artifacts.ipynb`

## Shared partition contract

All notebooks now expose the same config variables:

```python
ALL_STRATEGIES
SOURCE_IDS
RUN_TAG
PARTITION_MODE = 'strategy'
SELECTED_STRATEGIES
SELECTED_SOURCES
```

Recommended default:

- `PARTITION_MODE = 'strategy'`
- Version A:
  - `SELECTED_STRATEGIES = ['chunk_fixed_512', 'chunk_structure_parent_child']`
- Version B:
  - `SELECTED_STRATEGIES = ['chunk_semantic_embedding_bge_m3']`

Do **not** let two Kaggle versions process the same strategy into the same logical artifact set. Merge results later on local after downloading the zips.

`SELECTED_SOURCES` is recorded in every notebook for consistency, but strategy split is the default and safest partition for entity/relation steps.

## Output structure

All notebooks write under `/kaggle/working/w3_local_outputs/`:

```text
w3_local_outputs/
├── chunks/
├── entities/
├── payloads/
│   ├── chunk_fixed_512/
│   ├── chunk_structure_parent_child/
│   └── chunk_semantic_embedding_bge_m3/
├── embeddings/
├── reports/
├── state/
└── w3_local_outputs_<run_tag>.zip
```

Important directories:

- `payloads/` contains portable graph payloads exported by `write_graph_provenance.py --payload-output-dir ...`
- `state/` contains resume state used by notebooks 02-04
- `embeddings/` contains BGE-M3 JSONL artifacts for later import

## Resume behavior

Resume is supported by notebooks 02-04 via `--resume`, but it depends on:

- `state/`
- already-written artifact files in `entities/`, `payloads/`, `embeddings/`, `reports/`

If a Kaggle session ends and you want to continue in a new session, you must keep and restore the previous `w3_local_outputs/` bundle. `--resume` cannot recover without those files.

Practical rule:

- save/download the zip after each major step
- reattach or rehydrate prior artifacts before expecting resume in a new session

## Parallel execution guidance

Kaggle can run multiple saved versions, but the recommended split is by strategy.

Recommended:

- Version A:
  - `chunk_fixed_512`
  - `chunk_structure_parent_child`
- Version B:
  - `chunk_semantic_embedding_bge_m3`

Avoid:

- two versions processing the same strategy
- source-based split for entity/relation notebooks unless you first redesign the chunk inputs

## Models and slots

- Chunk semantic embedding: `BAAI/bge-m3`
- Dense embedding artifact slot: `bge_m3`
- Dense vector dim: `1024`
- Relation/entity augmentation: `Qwen/Qwen2.5-7B-Instruct`

This does **not** overwrite Gemini baseline vectors in Neo4j. BGE-M3 imports go to:

- property: `Chunk.embedding_bge_m3`
- index: `chunkVectorBgeM3`
- dim: `1024`

## After Kaggle: local import flow

1. Download the artifact zip from Kaggle.
2. Extract it locally.
3. Import graph payload:

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts\import_graph_payload.py `
  --payload-input-dir benchmark\tuvi_golden_dataset\local_kaggle\payloads\chunk_structure_parent_child
```

4. Import embedding artifacts:

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts\import_embedding_artifacts.py `
  --input benchmark\tuvi_golden_dataset\local_kaggle\embeddings\chunk_structure_parent_child `
  --embedding-slot bge_m3
```

5. Run local retrieval smoke:

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts\smoke_retrieval.py `
  --source-id TVGM `
  --chunking-strategy chunk_structure_parent_child `
  --embedding-slot bge_m3
```

## Acceptance checklist

W3 local-Kaggle path is ready when:

- assigned strategies finished chunk/entity/relation/embed on Kaggle
- `payloads/<strategy>/` exists for every strategy you plan to import
- `embeddings/<strategy>/` exists for every source-strategy you plan to import
- local import does not call LLM again
- local retrieval smoke passes with `--embedding-slot bge_m3`
- runtime query embedding on local CPU returns `1024`-dim vectors

## Troubleshooting

### Dataset fallback triggered

Expected Kaggle paths:

```text
/kaggle/input/tuvi-golden-corpus/benchmark/tuvi_golden_dataset
/kaggle/input/tuvi-battu-scripts
```

If the notebook falls back to local paths, verify:

1. the datasets are attached
2. the slugs match the variables in the notebook
3. the folder structure matches this README

### GPU memory pressure

If memory is tight:

1. process one strategy partition at a time
2. reduce `--local-embedding-batch-size`
3. keep relation/entity on a smaller partition first, save version, then continue
