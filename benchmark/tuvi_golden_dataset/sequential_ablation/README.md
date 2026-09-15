# Sequential ablation — runbook A/B

> **Current sequence (authoritative):** P1 chunking → P2 retrieval → P3 reranker
> on/off → P4 reranked candidate-retention depth → P5 final prompt → P6 generator
> → P7 confirmation. The old pre-reranker P3 prompt run was discarded; see
> [`REPHASE_MIGRATION.md`](REPHASE_MIGRATION.md).

Đây là entrypoint vận hành cho chuỗi ablation tuần tự mới. Mỗi phase chỉ thay một factor, khóa winner rồi mới sinh manifest phase sau. Không dùng lại bảng factorial cũ để khóa winner.

## Trạng thái setup hiện tại

- P0 mapper chạy trên release 100 câu và clean corpus runtime.
- Có 722 gold spans: 621 exact anchors, 101 annotation không map được; mapping coverage `0.860111`.
- 90/91 câu có gold corpus span còn ít nhất một exact anchor. Exact anchors chỉ
  dùng audit provenance; metric token-overlap vẫn chấm `TVQA-061`.
- Evidence Recall dùng đủ 722/722 span, kể cả 101 span `unmapped`, bằng cách so trực tiếp
  gold quote với final selected context cùng source family.
- P1 đã hoàn tất 300/300 pairs, zero failure và khóa `p1_fixed_512`.
- P2 đã hoàn tất 700/700 pairs, zero failure và khóa `p2_graph_dense_sparse`
  (Graph+Dense+Sparse).
- Prompt pre-reranker cũ đã bị loại bỏ; P5 là prompt comparison chính thức sau P4 k20.
- Không có phase smoke. Official command luôn chạy full-100; unit test và kiểm tra hash tĩnh vẫn được giữ.

## Sáu metric headline

| Metric | Dùng ở đâu |
|---|---|
| Evidence Recall | Primary của P1/P2/P3/P4; source-aligned token overlap trên final selected context, `τ=0.25`. |
| Evidence Precision | Guardrail của P1/P2/P3/P4; cùng relevance rule với Evidence Recall. |
| Evidence F1 | Cân bằng aggregate Evidence Recall và Evidence Precision. |
| Faithfulness | Primary của P5/P6. |
| Answer Relevancy | Guardrail/secondary của P5/P6. |
| Latency p95 | Secondary/tie-break; chỉ so trực tiếp khi chạy cùng máy. |

Context Recall của AI judge không thuộc Judge v2 và không vào bảng chính. Metric kỹ thuật khác vẫn được lưu trong JSON để truy lỗi nhưng không xuất hiện trong bảng quyết định. Completeness, zero fallback và zero invalid citation marker là gate hợp lệ, không phải metric.

Định nghĩa retrieval: casefold, bỏ dấu Unicode/dấu câu, tách `\w+`, giữ tần
suất token và chỉ so cùng source family. Với span `g`, chunk `c`:

```text
overlap(g,c) = Σ_t min(count_g(t), count_c(t)) / |tokens(g)|
Evidence Recall     = số span có max overlap >= 0.25 / tổng 722 span
Evidence Precision  = số final-context chunk relevant / tổng corpus context chunk
Evidence F1         = 2 × Evidence Recall × Evidence Precision / (Evidence Recall + Evidence Precision)
```

CHART bị loại khỏi mẫu số Precision; item không có gold span bị loại khỏi ba
metric retrieval. Aggregate là micro-average. Không loại span theo
`mapping_status`.

## Chạy ở đâu?

| Phase | Môi trường | GPU | Lý do |
|---|---|---:|---|
| P0 anchor/scorer | Local của A | Không | Đọc release và corpus trong repo. |
| P1 chunking | Local của A | Không bắt buộc | Cần Neo4j/fulltext/vector index; reranker off. |
| P2 retrieval | Local A và B | Không bắt buộc | Cần Neo4j và cùng snapshot; chia manifest thành hai shard. |
| P3 reranker on/off | Local A và B | Hiện tại CPU | Reranker implementation chưa chuyển Transformers model/tensor lên CUDA. Kaggle không có Neo4j local. |
| P4 reranked retention | Local A và B | Hiện tại CPU | B rerank max pool 100 lần; A/B replay k10/k20/k40. |
| P5 final prompt | Local A và B | Không | Cùng frozen k20 context; A/B chỉ generation + blind judge. |
| P6 Gemini | Local A | Không | Chạy API trên frozen prompt/context bundle. |
| P6 Qwen/Gemma | Kaggle A/B | Có | 4-bit inference; dùng notebook standalone và model dataset offline có sẵn quy trình. |
| P6 judge | Local A | Không | Gộp ba prediction set, một judge protocol Gemini. |
| P7 confirmation | Local A; Kaggle nếu local model thắng | Tùy winner | Xác nhận đúng final hash; không dùng để chọn lại. |

Không đưa P1–P5 nguyên pipeline lên Kaggle: các phase này phụ thuộc Neo4j và `.env` local. GPU Kaggle chỉ được dùng đúng chỗ mang lại lợi ích thật là Qwen/Gemma generation.

Runner offline đặt deadline reranker là 600 giây/item, tách biệt với timeout 8 giây của API tương tác. Vì vậy P4/P5 không được âm thầm rơi về thứ tự fusion trong lúc model CPU đang warm-up; nếu vượt deadline, pair bị đánh dấu failed và phải resume sau khi xử lý nguyên nhân.

Toàn chuỗi giữ candidate budget sau fusion ở mức 20. Cờ ablation `reranker_config.cap_fused_candidates_when_disabled=true` làm nhánh reranker-off cũng cắt fusion list ở 20; production mặc định vẫn là `false`. Control này ngăn P4 vô tình so sánh “off với tối đa 24 candidates” và “on với 20 candidates”.

## Vai trò

### A — owner

- Chạy P0 và toàn bộ P1 một mình.
- Đọc report, chọn winner theo metric đã đăng ký, khóa config.
- Sinh full manifest và hai shard A/B của phase tiếp theo.
- Từ P2 trở đi chạy shard A, merge shard A/B và phát ticket kế tiếp.
- Build frozen bundle, chạy Gemini + Qwen ở P6, judge tập trung và chạy P7.

### B — runner

- Bắt đầu tham gia từ P2.
- Pull đúng commit/tag hoặc nhận archive/ticket do A gửi.
- Chạy đúng một PowerShell command hoặc notebook đã preconfigure.
- Không sửa YAML/notebook, không đổi model/top-k/retry và không tự chọn winner.
- Gửi lại report/checkpoint/ZIP cùng log và SHA-256.

## 0. Điều kiện chung

Từ repo root, cả A và B cần:

```powershell
Test-Path .\.venv\Scripts\python.exe
Test-Path .\.env
$env:PYTHONPATH='backend'
```

Máy B mới clone thì cài một lần (Python ≥3.11):

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

A chuyển riêng các biến Neo4j/Gemini cần thiết cho B qua kênh bảo mật; không commit `.env` vào repo. P2 không cần model reranker. Trước P3-B/P4-B cần A chuyển hoặc chuẩn bị thư mục `models/bge-reranker-v2-m3`, rồi kiểm tra:

```powershell
Test-Path .\models\bge-reranker-v2-m3\model.safetensors
```

Nếu PowerShell báo `running scripts is disabled`, giữ nguyên tham số phía sau nhưng gọi wrapper theo mẫu `powershell -NoProfile -ExecutionPolicy Bypass -File <wrapper.ps1> ...`; không cần đổi execution policy toàn máy.

Neo4j của hai người phải có cùng bốn source và ba chunk strategies. A ghi snapshot counts/index state vào run ticket. Chất lượng rule-based có thể merge giữa hai máy; latency giữa hai máy không dùng để phá hòa.

## 1. P0 — A build anchors một lần

```powershell
.\scripts\sequential_ablation\build_gold_anchors.ps1
```

Kết quả bắt buộc:

```text
benchmark/tuvi_golden_dataset/sequential_ablation/gold_span_anchors.jsonl
benchmark/tuvi_golden_dataset/sequential_ablation/gold_span_anchor_summary.json
ready_for_official_run = true
mapping_coverage = 0.860111
```

Nếu dataset/corpus thay đổi byte thì chạy lại P0 và không resume checkpoint cũ.

## 2. P1 Chunking — A chạy một mình

Lệnh official đầu tiên:

```powershell
.\scripts\sequential_ablation\run_p1_chunking.ps1
```

Wrapper chạy read-only preflight trước khi bắt đầu 300 pairs: manifest chỉ đổi chunk strategy, anchors đúng dataset hash, đủ 12 cặp source × strategy có BGE-M3 embedding, và hai index `chunkFulltext`/`chunkVectorBgeM3` đều `ONLINE`. Kết quả lưu ở `sequential_ablation/preflight/P1_preflight.json`; preflight không phải smoke run.

Nếu máy/API/Neo4j bị ngắt:

```powershell
.\scripts\sequential_ablation\run_p1_chunking.ps1 -Resume
```

Không thêm `--limit`; không có smoke. Runner thực hiện ba candidate tuần tự, full-100 mỗi candidate:

1. `p1_fixed_512`
2. `p1_parent_child`
3. `p1_semantic_bge_m3`

Theo dõi:

```powershell
Get-Content .\benchmark\tuvi_golden_dataset\sequential_ablation\results\P1_chunking\checkpoints\checkpoint_summary.json -Raw | ConvertFrom-Json
```

Validate sau khi đủ 300 pairs:

```powershell
.\scripts\sequential_ablation\validate_phase_report.ps1 `
  -ReportPath .\benchmark\tuvi_golden_dataset\sequential_ablation\results\P1_chunking\evaluation_report.json `
  -ExpectedConfigs 3 -ExpectedPairs 300 -Backend rule-based-gold-evidence-v1
```

A chọn Evidence Recall cao nhất trong candidate qua Evidence Precision guardrail. Nếu hai candidate chênh dưới 0.01, chạy paired bootstrap; chỉ khi vẫn hòa mới replay hai candidate trên cùng máy để so latency.

Với P1 đã chạy bằng scorer provenance v1, chấm hậu xử lý context đã lưu mà không
chạy lại retrieval:

```powershell
.\.venv\Scripts\python.exe .\scripts\rescore_token_overlap_report.py `
  --report benchmark\tuvi_golden_dataset\sequential_ablation\results\P1_chunking\evaluation_report.json `
  --dataset benchmark\tuvi_golden_dataset\release\tuviqa_v1_release.jsonl `
  --output benchmark\tuvi_golden_dataset\sequential_ablation\results\P1_chunking\evaluation_report_token_overlap.json `
  --threshold 0.25 --expected-span-count 722
```

Tạo decision draft và paired bootstrap cố định seed trước khi khóa:

```powershell
.\.venv\Scripts\python.exe .\scripts\analyze_sequential_phase.py `
  --phase p1 `
  --report benchmark\tuvi_golden_dataset\sequential_ablation\results\P1_chunking\evaluation_report_token_overlap.json `
  --output benchmark\tuvi_golden_dataset\sequential_ablation\results\P1_chunking\P1_DECISION.json
```

Với P2–P5 dùng cùng lệnh và thay `--phase`, report, output tương ứng. Script chỉ đề xuất; A vẫn phải xem failure/hash/factor isolation rồi mới lock.

P1 đã khóa winner `p1_fixed_512`:

```powershell
.\.venv\Scripts\python.exe .\scripts\lock_sequential_phase.py `
  --manifest configs\ablation_sequential\p1_chunking.yaml `
  --report benchmark\tuvi_golden_dataset\sequential_ablation\results\P1_chunking\evaluation_report_token_overlap.json `
  --winner p1_fixed_512 `
  --output configs\ablation_sequential\locked_phase_1.yaml
```

Kết quả P1: Evidence Recall `0.558172`, Evidence Precision `0.846626`, Evidence F1 `0.672784`.

Kết quả P2: Graph+Dense+Sparse được khóa với Evidence Recall `0.581717`, Evidence Precision
`0.854400`, Evidence F1 `0.692171`. Graph+Sparse có Evidence Recall cao hơn (`0.584488`) nhưng
bị loại vì Evidence Precision `0.803543` thấp hơn guardrail `0.826626`.

Kết quả P3: reranker on được khóa. Kết quả P4: retention `k=20` được khóa theo
quy tắc tie-break đã đăng ký. P5 là so sánh prompt chính thức và đang dùng đúng
frozen context từ lock P4.

## 3. Sinh và chia phase P2–P5

A dùng cùng một pattern sau khi khóa phase trước. Ví dụ P2:

```powershell
.\.venv\Scripts\python.exe .\scripts\prepare_sequential_phase.py `
  --phase p2 `
  --base configs\ablation_sequential\locked_phase_1.yaml `
  --output configs\ablation_sequential\p2_retrieval.yaml `
  --output-dir benchmark/tuvi_golden_dataset/sequential_ablation/results/P2_retrieval `
  --two-person-shard-dir configs\ablation_sequential\shards
```

Script sinh full manifest canonical và hai shard. Phân công cố định:

| Phase | Shard A | Shard B |
|---|---|---|
| P2 | Graph, Dense, Graph+Dense | Sparse, Graph+Sparse, Dense+Sparse, GDS |
| P3 | reranker off | reranker on, top-k=20 |
| P4 | replay k10 | build max-rerank bundle, replay k20 và k40 |
| P5 | Prompt 1 (v1), Prompt 2 (grounded-v2) | Prompt 3 (answer-first-v4) |

B có nhiều candidate hơn vì A còn merge, phân tích và phát hành lock.

Lưu ý diễn giải P5: mỗi retrieval path hiện trả tối đa 8 candidates, nên `top_k=40` là điều kiện “không cắt thêm” chứ không bảo đảm context pool có đủ 40 phần tử (G+D+S có trần 24 trước dedup). Nếu P2 khóa strategy chỉ có một/hai path thì k20 và k40 có thể giống hệt theo cấu trúc; vẫn báo rõ saturation thay vì diễn giải “k40 không tốt hơn” như một kết luận tổng quát.

A tạo ticket copy/paste sau khi điền snapshot/deadline, ví dụ shard B của P2:

```powershell
.\.venv\Scripts\python.exe .\scripts\create_ablation_ticket.py `
  --phase p2 --member B `
  --manifest configs\ablation_sequential\shards\p2_shard_b.yaml `
  --output benchmark\tuvi_golden_dataset\sequential_ablation\tickets\P2_B.md `
  --neo4j-snapshot '<snapshot/counts>' `
  --deadline 'YYYY-MM-DD HH:mm Asia/Bangkok'
```

B chỉ cần pull đúng SHA trong ticket, kiểm tra snapshot rồi chạy nguyên lệnh. Tạo ticket A tương tự để registry của hai máy có cùng format.

Khi tạo ticket P4/P5, A bắt buộc thêm `--bundle <SHARED_BUNDLE_PATH>`; ticket generator
sẽ chọn đúng wrapper frozen/replay. Không phát ticket trước khi bundle hoàn tất và có checksum.

### Chạy shard retrieval: P2 và P3

A/B thay đúng đường dẫn ticket đã nhận:

```powershell
.\scripts\sequential_ablation\run_retrieval_phase.ps1 `
  -Manifest <SHARD_MANIFEST> `
  -OutputDir <SHARD_OUTPUT_DIR> `
  -CheckpointDir <SHARD_OUTPUT_DIR>\checkpoints
```

Resume bằng cách thêm `-Resume`.

### P4: rerank max pool một lần rồi replay

Chỉ làm vì P3 đã khóa `reranker.enabled=true`. B build bundle bằng full manifest:

```powershell
.\.venv\Scripts\python.exe .\scripts\build_p4_rerank_bundle.py `
  --manifest configs\ablation_sequential\p4_reranker_depth.yaml `
  --output-dir benchmark\tuvi_golden_dataset\sequential_ablation\results\P4_reranker_depth\max_rerank_bundle
```

Gate: `bundle_manifest.json` phải ghi `reranker_execution_count=100`, `max_k=40`,
`is_complete=true`. B gửi bundle/checksum cho A. A replay shard k10; B replay shard
k20+k40:

```powershell
.\scripts\sequential_ablation\run_p4_replay_phase.ps1 `
  -Manifest <SHARD_MANIFEST> `
  -Bundle benchmark\tuvi_golden_dataset\sequential_ablation\results\P4_reranker_depth\max_rerank_bundle `
  -OutputDir <SHARD_OUTPUT_DIR>
```

Replay chỉ truncate `reranked_candidates` rồi chạy grading/context/scorer; không gọi
Neo4j hay cross-encoder lần nữa. Hai report phải có cùng `bundle_manifest_sha256`.

### Merge hai shard

Sau khi A và B đều validate pass:

```powershell
.\.venv\Scripts\python.exe .\scripts\merge_sequential_shards.py `
  --manifest <FULL_MANIFEST> `
  --report-a <A_OUTPUT>\evaluation_report.json `
  --report-b <B_OUTPUT>\evaluation_report.json `
  --output-dir <CANONICAL_OUTPUT>
```

A validate canonical report rồi dùng `lock_sequential_phase.py`. Chỉ sau đó mới gọi `prepare_sequential_phase.py` cho phase kế.

Các lệnh prepare tiếp theo:

```powershell
# P3 sau locked_phase_2
.\.venv\Scripts\python.exe .\scripts\prepare_sequential_phase.py --phase p3 --base configs\ablation_sequential\locked_phase_2.yaml --output configs\ablation_sequential\p3_reranker.yaml --output-dir benchmark/tuvi_golden_dataset/sequential_ablation/results/P3_reranker --two-person-shard-dir configs\ablation_sequential\shards

# P4 sau locked_phase_3
.\.venv\Scripts\python.exe .\scripts\prepare_sequential_phase.py --phase p4 --base configs\ablation_sequential\locked_phase_3.yaml --output configs\ablation_sequential\p4_reranker_depth.yaml --output-dir benchmark/tuvi_golden_dataset/sequential_ablation/results/P4_reranker_depth --two-person-shard-dir configs\ablation_sequential\shards

# P5 sau locked_phase_4
.\.venv\Scripts\python.exe .\scripts\prepare_sequential_phase.py --phase p5 --base configs\ablation_sequential\locked_phase_4.yaml --output configs\ablation_sequential\p5_prompt.yaml --output-dir benchmark/tuvi_golden_dataset/sequential_ablation/results/P5_prompt_final --two-person-shard-dir configs\ablation_sequential\shards
```

P5 build frozen bundle từ lock P4, rồi chạy generation/judge trên hai shard:

```powershell
.\.venv\Scripts\python.exe .\scripts\build_p5_final_prompt_bundle.py `
  --manifest configs\ablation_sequential\p5_prompt.yaml `
  --output-dir benchmark\tuvi_golden_dataset\sequential_ablation\results\P5_prompt_final\frozen_context

.\scripts\sequential_ablation\run_p5_frozen_prompt_phase.ps1 `
  -Manifest <SHARD_MANIFEST> `
  -FrozenBundle benchmark\tuvi_golden_dataset\sequential_ablation\results\P5_prompt_final\frozen_context `
  -OutputDir <SHARD_OUTPUT_DIR> `
  -CheckpointDir <SHARD_OUTPUT_DIR>\checkpoints
```

P5 chỉ gọi Gemini generation và blind Judge v2. Chọn theo Faithfulness; Answer
Relevancy không được giảm quá `0.02` so với Prompt 2 và invalid marker phải bằng 0.

## 4. P6 Generator — local + Kaggle GPU

> **Current execution design.** P5 is locked to its Faithfulness winner,
> Prompt 1 (`v1`). P6 reports a 3-model × 2-shortlisted-prompt matrix: existing
> `p6_kaggle/` is Prompt 1 and `p6_prompt3/` adds Prompt 3
> (`tuvi_generation_answer_first_v4`), the highest-Relevancy P5 candidate.
> Do not overwrite the original directory. Prompt 3 re-renders over the same
> already frozen retrieval states, so it does not call Neo4j or rerank again; see
> `report/ablation/P6_PROMPT3_ALL_MODEL_RERUN.md`.

### 4.1 A tạo manifest một-config và asset P6

Giả sử config retrieval cuối là `locked_phase_5.yaml`:

```powershell
.\.venv\Scripts\python.exe .\scripts\prepare_sequential_phase.py `
  --phase p6-context `
  --base configs\ablation_sequential\locked_phase_5.yaml `
  --output configs\ablation_sequential\p6_frozen_context.yaml `
  --output-dir benchmark/tuvi_golden_dataset/sequential_ablation/results/P6_context

.\.venv\Scripts\python.exe .\scripts\prepare_p6_kaggle.py `
  --manifest configs\ablation_sequential\p6_frozen_context.yaml

.\.venv\Scripts\python.exe .\scripts\build_p6_context_bundle.py
```

Nếu P5 là N/A, thay base bằng `locked_phase_4.yaml` khi sinh manifest P6.

Bundle phải đúng một config × 100 item. Upload file này thành Kaggle Private Dataset:

```text
benchmark/tuvi_golden_dataset/sequential_ablation/p6_kaggle/p6_frozen_context_bundle.zip
```

### 4.2 Chia người

- A chạy `P6_qwen25_7b_official_kaggle.ipynb` trên Kaggle GPU, Internet OFF.
- B chạy `P6_gemma3_4b_official_kaggle.ipynb` trên Kaggle GPU, Internet OFF.
- A đồng thời chạy Gemini local:

```powershell
.\.venv\Scripts\python.exe .\scripts\run_p6_gemini.py
```

Hai notebook đã là `RUN_MODE='official'`; B không sửa cell config. Cả hai phải mount frozen context dataset và đúng model dataset. Gemma yêu cầu tài khoản đã accept license.

Quy trình đóng gói model thành Kaggle Dataset và quy tắc Internet OFF dùng lại từ `benchmark/tuvi_golden_dataset/local_llm_ablation/KAGGLE_DATASET_GUIDE.md`; P6 chỉ thay notebook và frozen context ZIP được generator tạo ra.

B gửi prediction ZIP cho A. A đặt ZIP Qwen và Gemma vào:

```text
benchmark/tuvi_golden_dataset/sequential_ablation/p6_kaggle/predictions_inbox/
```

Sau đó A judge tập trung 300 answers:

```powershell
.\.venv\Scripts\python.exe .\scripts\run_p6_judge.py
```

Không để A/B tự judge bằng model/rubric khác nhau. `run_p6_judge.py` dùng blind Judge
v2: request gửi judge không chứa tên model/config/prompt/retrieval/reranker và thứ tự
300 prediction được trộn deterministic với seed 42. Mù tuyệt đối theo văn phong là
không thể bảo đảm, nên vẫn audit thủ công 20 item đã ẩn nhãn để kiểm tra self-preference.

## 5. P7 confirmation

- Nếu Gemini thắng: tạo manifest một config từ retrieval lock + Gemini generation model và chạy full `run_generation_phase.ps1` trên local A.
- Nếu Qwen/Gemma thắng: backend hiện chưa tích hợp local generator vào live RAG. P7 phải lặp lại frozen-context generation bằng notebook official của model thắng, sau đó judge local; báo rõ đây là confirmation trên frozen context, không phải live serving integration.
- P7 chỉ xác nhận completeness/reproducibility trên cùng 100 câu, không phải held-out generalization.

Gemini Prompt 1 là winner hiện tại. Manifest đã được chuẩn bị tại
`configs/ablation_sequential/p7_confirmation.yaml`; chạy live confirmation:

```powershell
.\scripts\sequential_ablation\run_generation_phase.ps1 `
  -Manifest configs\ablation_sequential\p7_confirmation.yaml `
  -OutputDir benchmark\tuvi_golden_dataset\sequential_ablation\results\P7_confirmation `
  -CheckpointDir benchmark\tuvi_golden_dataset\sequential_ablation\results\P7_confirmation\checkpoints
```

Nếu terminal bị ngắt, chạy lại đúng lệnh trên với thêm `-Resume`. Gate là 100/100
completed, zero failed/fallback, blind Judge v2, và config hash khớp
`locked_phase_5.yaml` ngoài `experiment_id`/`name` provenance của P7.

## 6. Khi nào một phase được khóa?

- Đủ 100 item cho mỗi candidate, không duplicate/missing ID.
- `failed_pair_count=0`, không retrieval/reranker fallback.
- Config/dataset/anchor/code hashes đúng ticket.
- Retrieval phase: chọn Evidence Recall token-overlap theo Evidence Precision guardrail đã đăng ký và báo Evidence F1.
- P5/P6: chọn Faithfulness; Answer Relevancy không được giảm quá 0.02 so với
  control; invalid citation marker phải bằng 0.
- Decision draft luôn báo paired delta, bootstrap CI95 (10.000 mẫu, seed 42) và nhãn
  `better`, `worse` hoặc `inconclusive`.
- A tạo `locked_phase_N.yaml`, `.lock.json`, `P{N}_DECISION.md` và artifact SHA manifest.

## 7. Thời gian thực tế tham khảo

Artifact cũ cho thấy full RAG chạy local từng mất:

| Run cũ | Quy mô | Wall time quan sát |
|---|---:|---:|
| Chunking | 300 pairs | khoảng 9,4 giờ |
| Retrieval single paths | 300 pairs | khoảng 9,6 giờ |
| Retrieval dense combos | 300 pairs | khoảng 11,1 giờ |
| Retrieval shortlist | 300 pairs | khoảng 7,6 giờ |
| Local-LLM Gemini judge | 600 pairs | khoảng 3,9 giờ |

P1–P4 chạy retrieval-only nên nhanh hơn full RAG, nhưng reranker CPU vẫn là rủi ro lớn. Với hai người, để hoàn tất ba ngày cần hai máy local chạy đồng thời từ P2, Kaggle GPU sẵn cho ngày 3 và dùng checkpoint qua đêm. P4 chỉ chạy cross-encoder 100 lần ở max pool rồi replay ba top-k; P5 reuse đúng k20 context nên không rerank lại.

## 8. File vận hành

```text
configs/ablation_sequential/p1_chunking.yaml
scripts/run_retrieval_eval.py
scripts/prepare_sequential_phase.py
scripts/merge_sequential_shards.py
scripts/analyze_sequential_phase.py
scripts/create_ablation_ticket.py
scripts/check_sequential_preflight.py
scripts/lock_sequential_phase.py
scripts/prepare_p6_kaggle.py
scripts/build_p6_context_bundle.py
scripts/run_p6_gemini.py
scripts/run_p6_judge.py
scripts/build_p4_rerank_bundle.py
scripts/build_p5_final_prompt_bundle.py
scripts/run_p4_replay_eval.py
scripts/sequential_ablation/*.ps1
benchmark/tuvi_golden_dataset/sequential_ablation/RUN_TICKET_TEMPLATE.md
benchmark/tuvi_golden_dataset/sequential_ablation/RUN_REGISTRY.md
```
