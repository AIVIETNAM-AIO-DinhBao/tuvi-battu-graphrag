# Local LLM Ablation — Qwen2.5-7B và Gemma-3-4B

Đây là kit canonical nằm trực tiếp trong repo. Thí nghiệm cuối cùng gồm:

- 3 retrieval configs × 100 câu = **300 frozen retrieval cases**, build đúng một lần.
- 2 local generation models × 300 cases = **600 answers**.
- B/C/D mỗi người Gemini-judge 200 answers của config mình; A merge ba shard thành 600 results mà không gọi API lại.

## Notebook nào chạy ở đâu?

| Notebook | Môi trường | Internet | GPU | Có cần repo lúc chạy? |
|---|---|---:|---:|---:|
| `00_prepare_model_dataset_kaggle.ipynb` | Kaggle | ON | Không | **Không**, standalone |
| `01_build_retrieval_bundle_local.ipynb` | Máy local | Theo backend | Không bắt buộc | **Có** |
| `02_generate_offline_kaggle.ipynb` | Kaggle | **OFF** | **Có** | **Không**, standalone |
| `03_gemini_judge_local.ipynb` | Máy local của B/C/D, sau đó A merge | ON khi judge; merge không cần | Không | **Có** |

Hai notebook Kaggle đã nhúng toàn bộ runtime code vào cell có tag `standalone-runtime`. Thành viên chỉ cần nhận file `.ipynb`, Add Input datasets theo hướng dẫn và đổi biến config; không cần upload repo hoặc folder `local_tools`.

## Shortlist chính thức

| Config | Vai trò |
|---|---|
| `graph_dense_rrf` | Best-overall config trong kết quả Gemini hiện có |
| `semantic_gs_rrf_rerank_k40` | Quality-first; nhánh reranker on |
| `semantic_gs_rrf_no_rerank_reference` | Low-latency control; nhánh reranker off |

Hai config Semantic Graph+Sparse RRF tạo controlled comparison về tác động của reranker. `graph_dense_rrf` giữ vai trò ứng viên tốt nhất tổng thể.

## Hai model

| Key | Model ID | Access |
|---|---|---|
| `qwen25_7b` | `Qwen/Qwen2.5-7B-Instruct` | public |
| `gemma3_4b` | `google/gemma-3-4b-it` | gated; cần chấp nhận license và HF token |

Official inference giữ cố định: 4-bit NF4, seed 42, deterministic decoding, `max_input_tokens=24576`, `max_new_tokens=1024`, không truncate prompt.

## Cấu trúc

```text
local_llm_ablation/
├── experiment_plan.json
├── README.md
├── RUNBOOK.md
├── KAGGLE_DATASET_GUIDE.md
├── TEAM_PLAN.md
├── requirements-offline.txt
├── requirements-online.txt
├── notebooks/
│   ├── 00_prepare_model_dataset_kaggle.ipynb
│   ├── 01_build_retrieval_bundle_local.ipynb
│   ├── 02_generate_offline_kaggle.ipynb
│   └── 03_gemini_judge_local.ipynb
└── local_tools/
    ├── build_bundle.py
    ├── run_judge.py
    ├── prepare_model.py
    ├── run_inference.py
    ├── validate_kit.py
    └── generate_notebooks.py
```

`local_tools` là source canonical để maintain và chạy hai notebook local. Notebook Kaggle không import package này; script `generate_notebooks.py` đóng gói source cần thiết vào notebook trước khi phát hành.

## Bắt đầu nhanh

1. A đọc [RUNBOOK.md](RUNBOOK.md), chuẩn bị hai model datasets bằng notebook 00.
2. A chạy notebook 01 local: smoke 6 cases, sau đó official 300 cases.
3. A upload context bundle và chia sẻ hai model datasets theo [KAGGLE_DATASET_GUIDE.md](KAGGLE_DATASET_GUIDE.md).
4. B/C/D nhận notebook 02, mỗi người chạy config được giao trên cả hai model.
5. B/C/D tải hai prediction ZIP về máy mình, set `GEMINI_API_KEYS`, rồi chạy notebook 03 với `ACTION='judge'`.
6. A nhận ba `gemini_judge_shard_*.zip`, đặt `ACTION='merge'` và tạo report cuối.

## Output cuối

```text
artifacts/
├── context_bundle_v1/
│   ├── bundle_manifest.json
│   ├── cases.jsonl                 # 300
│   ├── configs.jsonl               # 3
│   └── items.jsonl                 # 100
├── judge_inputs/{B,C,D}/            # mỗi member có 2 prediction ZIP
├── downloaded_judge_shards/         # A nhận 3 judge ZIP
└── gemini_judge_final/
    ├── evaluation_report.json        # schema canonical như reports/reports_final
    ├── evaluation_report.md
    ├── checkpoints/
    │   ├── evaluation_checkpoint.json
    │   └── checkpoint_summary.json
    ├── judged_items.jsonl           # 600
    ├── local_llm_metrics.csv        # 6 model-config rows
    └── merge_summary.json
```

Một answer thành công chỉ dùng **một Gemini call**; cả ba score được trả trong cùng JSON. Ba retry chỉ chạy khi call lỗi. Key pool round-robin điểm bắt đầu và failover sang key kế tiếp; diagnostics chỉ ghi `key_1`, `key_2`, không ghi secret.

## Verification

Từ repo root:

```powershell
python -m benchmark.tuvi_golden_dataset.local_llm_ablation.local_tools.validate_kit `
  --kit-root benchmark\tuvi_golden_dataset\local_llm_ablation `
  --repo-root .
```

Kết quả hợp lệ phải có `"ok": true`, 4 notebooks, 3 configs, 100 items và 300 pairs.

## Metric caveat

Golden release không chứa `gold_chunk_ids`, nên chưa có exact-match retrieval candidate hit với gold chunk. Không diễn giải `graph_hit_rate` thành retrieval accuracy. Các metric evidence-based hiện có gồm gold document coverage, page hit ±1 và quote overlap.

Gemini-generation results cũ chỉ là historical cross-wave reference. Paired comparison chính thức của run mới là Qwen so với Gemma trên cùng frozen bundle.
