# Kaggle Notebooks for Tu Vi GraphRAG Ingestion

These notebooks are the `local-kaggle`/Qwen fallback, reproducibility, and comparison path for `W3-INGEST`. The accepted W3 full-corpus baseline as of 2026-07-07 is the `gemini_call` live DB branch; this notebook path remains useful when Gemini quota/runtime is not stable enough for a rerun.

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

Important: do not upload only `benchmark/tuvi_golden_dataset/corpus/`. Notebook 01 passes `--source-registry` to `chunk_text.py`, so the corpus dataset must also include `benchmark/tuvi_golden_dataset/guideline/source_registry.json`.

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

Run in this order, but treat every notebook as an isolated Kaggle Save Version run.
`/kaggle/working` is not shared between notebooks.

1. `00_setup_and_smoke.ipynb`
2. `01_chunk_bge_m3.ipynb`
3. `02_entity_qwen.ipynb`
4. `03_relation_qwen_hybrid.ipynb`
5. `04_embed_and_pack_artifacts.ipynb`

Artifact handoff between notebooks:

- Notebook 01 writes `w3_local_outputs_01_<run_tag>.zip`
- Notebook 02 restores the notebook 01 zip via `PREVIOUS_OUTPUT_SLUGS`, then writes `w3_local_outputs_02_<run_tag>.zip`
- Notebook 03 restores the notebook 02 zip via `PREVIOUS_OUTPUT_SLUGS`, then writes `w3_local_outputs_03_<run_tag>.zip`
- Notebook 04 restores the notebook 03 zip via `PREVIOUS_OUTPUT_SLUGS`, then writes final `w3_local_outputs_<run_tag>.zip`

Attach the previous notebook output as a Kaggle input dataset, or download/upload the zip as a dataset, before running the next notebook. The notebooks now support both a preserved `.zip` file and a folder that Kaggle has automatically unpacked from that zip.

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

Notebooks 02-04 also expose:

```python
PREVIOUS_OUTPUT_SLUGS
```

Set `PREVIOUS_OUTPUT_SLUGS` to the Kaggle input dataset path that contains the previous notebook artifact. If your Kaggle dataset auto-unpacks the zip, point to the unpacked folder, for example `w3-local-outputs/w3_local_outputs_01_part_a`.

If the input root contains only the artifact for the current `RUN_TAG`, you can leave `PREVIOUS_OUTPUT_SLUGS = []`; the notebook will look for `w3_local_outputs_<step>_<run_tag>` automatically.

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

Because notebooks 00-04 are independent Save Version runs, you must keep and restore the previous `w3_local_outputs/` bundle through the zip artifact. `--resume` cannot recover without those files.

Practical rule:

- save/download the zip after every notebook step
- attach/upload the previous step zip before running the next notebook
- set `PREVIOUS_OUTPUT_SLUGS` to the dataset path that contains that artifact, or leave it empty when the current `RUN_TAG` artifact is the only match

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
- Entity extraction: dictionary/rule + Qwen augmentation with `LLM_AUGMENTATION = 'on'`
- Entity local LLM quantization: `none`
- Entity local LLM device: `auto-cuda`
- Entity JSON retries: `2`
- Entity Qwen preflight: optional diagnostic only; default `LLM_PREFLIGHT_CHUNK_LIMIT = 0`
- Entity runtime budget: 36000 seconds soft stop, 39600 seconds hard timeout
- Relation augmentation: `Qwen/Qwen2.5-7B-Instruct`

Entity extraction uses the full non-quantized Qwen model. Notebook 02 supports a real one-chunk Qwen preflight, but this is disabled by default because it loads Qwen in a separate subprocess before the full batch. Set `LLM_PREFLIGHT_CHUNK_LIMIT = 1` only for a diagnostic run; after it passes, set it back to `0` so the full batch loads Qwen once. If Qwen fails to load, is too slow, or the command times out, the notebook kills the child process and fails instead of silently producing zero entities or burning the whole Kaggle session.

`auto-cuda` allows HuggingFace to shard the full model across multiple Kaggle GPUs when available, but rejects CPU/disk offload after load. This keeps the run on full-quality weights without falling into extremely slow CPU inference.

Notebook 02 does not execute scripts directly from the read-only Kaggle input dataset. Cell 1 copies `tuvi-battu-scripts` to `/kaggle/working/tuvi_battu_scripts_runtime`, applies notebook hotfixes there, and cell 2 runs `/kaggle/working/tuvi_battu_scripts_runtime/scripts/extract_entities.py`. If a traceback still points to `/kaggle/input/.../tuvi-battu-scripts/scripts/extract_entities.py`, rerun the updated notebook from cell 1.

Cell 2 shows progress from the entity `state` file while the subprocess runs. With `tqdm` installed this appears as a progress bar; otherwise the notebook prints periodic `completed/total` updates.

If a strategy reaches the soft runtime budget, `extract_entities.py` writes partial `entities/`, `state/`, and `reports/`, exits successfully, and notebook 02 still packs the zip. Re-upload that zip as the next notebook 02 input with the same `RUN_TAG` and `SELECTED_STRATEGIES`; notebook 02 restores notebook 01 chunks through `PREVIOUS_OUTPUT_SLUGS` and optional notebook 02 partial state through `PREVIOUS_ENTITY_OUTPUT_SLUGS`. `--resume` skips completed chunks. Move to notebook 03 only after summaries show `completed = true`.

The Transformers warning about invalid `temperature`, `top_p`, or `top_k` generation flags is not the failure condition by itself. Treat OOM, preflight timeout, non-zero command exit, or non-zero `error_count` as the actionable failures.

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
/kaggle/input/datasets/dinhbaobao/tuvi-golden-corpus/benchmark/tuvi_golden_dataset
/kaggle/input/datasets/dinhbaobao/tuvi-battu-scripts
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
