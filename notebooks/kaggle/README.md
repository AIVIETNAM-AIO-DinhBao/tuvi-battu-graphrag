# Kaggle Local W3 Ingestion

This folder contains Kaggle-oriented notebooks for running W3 ingestion without Gemini API calls.

## Model Choices

- Embeddings: `BAAI/bge-m3`, dense normalized vectors, `1024` dimensions.
- LLM augmentation: `Qwen/Qwen2.5-7B-Instruct`, 4-bit by default.
- Graph DB writes are disabled in Kaggle. Notebooks generate JSONL artifacts, state files, reports, and a zip bundle for local/cloud import.

## Kaggle Inputs

Attach one of these as a Kaggle Dataset:

- A repo snapshot containing `scripts/`, `configs/`, `benchmark/tuvi_golden_dataset/corpus/`, and `benchmark/tuvi_golden_dataset/guideline/`.
- Or upload the full project directory and set `PROJECT_DIR` to that path.

Optional:

- Attach Hugging Face token as Kaggle secret `HF_TOKEN` if the notebook needs to download gated/cached models.
- Attach BGE-M3/Qwen as Kaggle Models or Dataset cache if internet is unavailable.

## Run Order

1. `00_setup_and_smoke.ipynb`
2. `01_chunk_bge_m3.ipynb`
3. `02_entity_qwen.ipynb`
4. `03_relation_qwen_hybrid.ipynb`
5. `04_embed_and_pack_artifacts.ipynb`

All notebooks write to `/kaggle/working/w3_local_outputs` by default. Re-run cells with `--resume` after interruption.

## Local Import Notes

Download the zip from notebook `04`, inspect reports, then import graph/vector artifacts on a local/cloud environment with Neo4j/Supabase credentials. Use a separate BGE-M3 vector index such as `chunkVectorBgeM3`; do not mix these embeddings with Gemini `chunkVector`.
