# WORKPLAN Tạo Golden Dataset QA 100 Câu cho Benchmark RAG Tử Vi

**Sprint:** 17/06/2026 – 27/06/2026  
**Phạm vi:** Chỉ Tử Vi, không bao gồm Bát Tự  
**Nhân sự chính:** A, B, C  
**Nhân sự hỗ trợ:** D (nếu rảnh, tối đa ~10%)  
**Owner tổng / final sign-off:** A

---

## Mục lục

- [WORKPLAN Tạo Golden Dataset QA 100 Câu cho Benchmark RAG Tử Vi](#workplan-tạo-golden-dataset-qa-100-câu-cho-benchmark-rag-tử-vi)
  - [Mục lục](#mục-lục)
  - [1. Mục tiêu sprint](#1-mục-tiêu-sprint)
  - [2. Quyết định quản lý quan trọng](#2-quyết-định-quản-lý-quan-trọng)
    - [2.1. Folder làm việc](#21-folder-làm-việc)
    - [2.2. Owner tổng](#22-owner-tổng)
    - [2.3. Nguyên tắc chống conflict](#23-nguyên-tắc-chống-conflict)
    - [2.4. 4 điểm bắt buộc phải khóa trước khi annotate hàng loạt](#24-4-điểm-bắt-buộc-phải-khóa-trước-khi-annotate-hàng-loạt)
  - [3. Phân vai tổng quát](#3-phân-vai-tổng-quát)
  - [4. Deliverables cuối sprint](#4-deliverables-cuối-sprint)
    - [4.1. Deliverables bắt buộc](#41-deliverables-bắt-buộc)
    - [4.2. Deliverables hỗ trợ](#42-deliverables-hỗ-trợ)
  - [5. Cấu trúc thư mục chuẩn](#5-cấu-trúc-thư-mục-chuẩn)
  - [6. Mã việc và breakdown công việc](#6-mã-việc-và-breakdown-công-việc)
    - [6.1. Nhóm SETUP / CONTROL](#61-nhóm-setup--control)
    - [6.2. Nhóm SOURCE / CORPUS](#62-nhóm-source--corpus)
    - [6.3. Nhóm CHART / ENGINE](#63-nhóm-chart--engine)
    - [6.4. Nhóm QUESTION DESIGN](#64-nhóm-question-design)
    - [6.5. Nhóm GOLD SECTION SELECTION](#65-nhóm-gold-section-selection)
    - [6.6. Nhóm GOLD ANSWER / ANNOTATION](#66-nhóm-gold-answer--annotation)
    - [6.7. Nhóm REVIEW / RELEASE](#67-nhóm-review--release)
  - [7. Dependency tổng quát](#7-dependency-tổng-quát)
  - [8. Timeline theo ngày](#8-timeline-theo-ngày)
    - [Day 1 — 17/06](#day-1--1706)
    - [Day 2 — 18/06](#day-2--1806)
    - [Day 3 — 19/06](#day-3--1906)
    - [Day 4 — 20/06](#day-4--2006)
    - [Day 5 — 21/06](#day-5--2106)
    - [Day 6 — 22/06](#day-6--2206)
    - [Day 7 — 23/06](#day-7--2306)
    - [Day 8 — 24/06](#day-8--2406)
    - [Day 9 — 25/06](#day-9--2506)
    - [Day 10 — 26/06](#day-10--2606)
    - [Day 11 — 27/06](#day-11--2706)
  - [9. Phân chia sample thực tế cho A/B/C](#9-phân-chia-sample-thực-tế-cho-abc)
  - [10. Chuẩn output của các file quan trọng](#10-chuẩn-output-của-các-file-quan-trọng)
    - [10.1. source\_registry.json](#101-source_registryjson)
    - [10.2. chart\_registry.json](#102-chart_registryjson)
    - [10.3. question\_slots.csv](#103-question_slotscsv)
    - [10.4. gold\_sections.jsonl](#104-gold_sectionsjsonl)
    - [10.5. golden\_v1\_release.jsonl](#105-golden_v1_releasejsonl)
  - [11. Checklist review của A theo từng nhóm việc](#11-checklist-review-của-a-theo-từng-nhóm-việc)
    - [11.1. Review source/corpus](#111-review-sourcecorpus)
    - [11.2. Review chart](#112-review-chart)
    - [11.3. Review question](#113-review-question)
    - [11.4. Review gold context](#114-review-gold-context)
    - [11.5. Review gold answer](#115-review-gold-answer)
    - [11.6. Review release](#116-review-release)
  - [12. Workflow quản lý công việc khuyến nghị cho A](#12-workflow-quản-lý-công-việc-khuyến-nghị-cho-a)
    - [12.1. Daily status bắt buộc](#121-daily-status-bắt-buộc)
    - [12.2. Nhịp họp ngắn](#122-nhịp-họp-ngắn)
    - [12.3. Git workflow khuyến nghị](#123-git-workflow-khuyến-nghị)
  - [13. Rủi ro chính và cách chặn](#13-rủi-ro-chính-và-cách-chặn)
  - [14. Định nghĩa Done của sprint](#14-định-nghĩa-done-của-sprint)
  - [15. Ghi chú cuối cho toàn team](#15-ghi-chú-cuối-cho-toàn-team)

---

## 1. Mục tiêu sprint

Trong 10 ngày, team phải hoàn thành bộ **golden benchmark dataset** cho hệ thống RAG Tử Vi với đầu ra tối thiểu gồm:

- 10 lá số Tử Vi đã được chuẩn hóa
- 100 sample QA hoàn chỉnh
- phân bổ đúng:
  - 10 Direct
  - 40 One-hop
  - 50 Two-hop
- release dataset ở dạng:
  - `golden_v1_release.jsonl`
  - `gold_with_chunk_map.jsonl`
- tài liệu/metadata hỗ trợ:
  - `source_registry.json`
  - `chart_registry.json`
  - `question_slots.csv`
  - `gold_sections.jsonl`
  - `review_reports.csv`
  - `final_summary.md`

Sprint này bám sát guideline benchmark cuối cùng của nhóm: dùng 4 sách nguồn pháp điển, schema release ổn định, chart context RAG-friendly, gold context được xác định từ section/span gốc rồi mới map sang chunk_id sau. Không dùng adversarial set.

---

## 2. Quyết định quản lý quan trọng

### 2.1. Folder làm việc

Toàn bộ công việc benchmark sẽ đặt trong:

```text
benchmark/tuvi_golden_dataset/
```

Lý do:
- không trộn với data/tuvi/ là nơi chứa dữ liệu thô
- không đụng trực tiếp frontend/, backend/, infra/
- rõ ownership cho benchmark
- dễ mở rộng về sau

### 2.2. Owner tổng

A là người duy nhất có quyền:
- chốt schema cuối
- freeze chart registry
- freeze slot matrix
- merge release dataset
- adjudicate xung đột
- sign-off bản final

### 2.3. Nguyên tắc chống conflict

Không ai sửa cùng lúc file release cuối. Mọi annotation ban đầu phải tách file theo người.

Ví dụ:
- `gold_sections_A.jsonl`
- `gold_sections_B.jsonl`
- `gold_sections_C.jsonl`

và:
- `golden_candidates_A.jsonl`
- `golden_candidates_B.jsonl`
- `golden_candidates_C.jsonl`

Sau đó A merge.

### 2.4. 4 điểm bắt buộc phải khóa trước khi annotate hàng loạt

Không được đẩy mạnh annotation nếu chưa khóa đủ 4 thứ sau:
1. `source_registry.json`
2. `schema_release.json`
3. `chart_registry.json`
4. `question_slots.csv`

Nếu thiếu 1 trong 4, mọi sample tạo ra rất dễ lệch format và phải sửa hàng loạt.

---

## 3. Phân vai tổng quát

| Thành viên | Vai trò chính | Tỷ trọng thực tế |
|------------|---------------|------------------|
| A | Lead benchmark, schema, chart selection, slot matrix, final review, release freeze | 45% |
| B | Corpus/source mapping, gold section selection, annotation chính | 30% |
| C | Tooling/script, chart cleanup/export, chunk mapping, annotation chính | 25% |
| D | Hỗ trợ low-conflict tasks nếu rảnh | 0–10% |

---

## 4. Deliverables cuối sprint

### 4.1. Deliverables bắt buộc

- `benchmark/tuvi_golden_dataset/guideline/data-guideline.md`
- `benchmark/tuvi_golden_dataset/guideline/source_registry.json`
- `benchmark/tuvi_golden_dataset/charts/chart_registry.json`
- `benchmark/tuvi_golden_dataset/samples/question_slots.csv`
- `benchmark/tuvi_golden_dataset/annotations/gold_sections.jsonl`
- `benchmark/tuvi_golden_dataset/annotations/golden_candidates.jsonl`
- `benchmark/tuvi_golden_dataset/annotations/sentence_span_map.jsonl`
- `benchmark/tuvi_golden_dataset/release/golden_v1_release.jsonl`
- `benchmark/tuvi_golden_dataset/release/gold_with_chunk_map.jsonl`
- `benchmark/tuvi_golden_dataset/reports/review_reports.csv`
- `benchmark/tuvi_golden_dataset/reports/final_summary.md`

### 4.2. Deliverables hỗ trợ

- `benchmark/tuvi_golden_dataset/guideline/schema_release.json`
- `benchmark/tuvi_golden_dataset/guideline/schema_ops.json`
- `benchmark/tuvi_golden_dataset/charts/CHART-001.json` ... `CHART-010.json`
- `benchmark/tuvi_golden_dataset/scripts/map_gold_spans_to_chunks.py`
- `benchmark/tuvi_golden_dataset/scripts/validate_release_schema.py`

---

## 5. Cấu trúc thư mục chuẩn

```text
benchmark/
└── tuvi_golden_dataset/
    ├── WORKPLAN_2026-06-17_2026-06-27.md
    ├── README.md
    ├── guideline/
    │   ├── data-guideline.md
    │   ├── schema_release.json
    │   ├── schema_ops.json
    │   └── source_registry.json
    ├── charts/
    │   ├── chart_registry.json
    │   ├── CHART-001.json
    │   ├── CHART-002.json
    │   ├── CHART-003.json
    │   ├── CHART-004.json
    │   ├── CHART-005.json
    │   ├── CHART-006.json
    │   ├── CHART-007.json
    │   ├── CHART-008.json
    │   ├── CHART-009.json
    │   └── CHART-010.json
    ├── corpus/
    │   ├── TVKL/
    │   ├── TVNL/
    │   ├── TVHS/
    │   └── TVGM/
    ├── samples/
    │   ├── question_slots.csv
    │   ├── sample_plan.csv
    │   └── coverage_matrix.xlsx
    ├── drafts/
    │   ├── drafts_questions.jsonl
    │   └── drafts_answers.jsonl
    ├── annotations/
    │   ├── gold_sections_A.jsonl
    │   ├── gold_sections_B.jsonl
    │   ├── gold_sections_C.jsonl
    │   ├── gold_sections.jsonl
    │   ├── golden_candidates_A.jsonl
    │   ├── golden_candidates_B.jsonl
    │   ├── golden_candidates_C.jsonl
    │   ├── golden_candidates.jsonl
    │   └── sentence_span_map.jsonl
    ├── release/
    │   ├── golden_v1_release.jsonl
    │   └── gold_with_chunk_map.jsonl
    ├── reports/
    │   ├── daily_status.md
    │   ├── review_reports.csv
    │   ├── qa_audit.md
    │   └── final_summary.md
    └── scripts/
        ├── build_chart_registry.py
        ├── generate_llm_drafts.py
        ├── map_gold_spans_to_chunks.py
        └── validate_release_schema.py
```

---

## 6. Mã việc và breakdown công việc

### 6.1. Nhóm SETUP / CONTROL

| Mã việc | Tên việc | Owner | Phụ | Depends on | Output |
|---------|----------|-------|-----|------------|--------|
| GD-SETUP-01 | Tạo folder benchmark + file khung | A | C | — | thư mục benchmark hoàn chỉnh |
| GD-SETUP-02 | Chốt cấu trúc file/folder, naming convention | A | B | GD-SETUP-01 | README + tree thư mục |
| GD-SETUP-03 | Copy guideline cuối + schema vào repo | A | — | GD-SETUP-01 | data-guideline.md, schema_release.json, schema_ops.json |
| GD-CTRL-01 | Tạo tracker tiến độ hằng ngày | A | — | GD-SETUP-01 | reports/daily_status.md |
| GD-CTRL-02 | Tạo bảng ownership file | A | B | GD-SETUP-02 | reports/file_ownership.md |

### 6.2. Nhóm SOURCE / CORPUS

| Mã việc | Tên việc | Owner | Phụ | Depends on | Output |
|---------|----------|-------|-----|------------|--------|
| GD-SRC-01 | Chốt 4 doc_id chuẩn | A | B | GD-SETUP-03 | source_registry.json |
| GD-SRC-02 | Chuẩn hóa metadata từng sách | B | A | GD-SRC-01 | title, filename, doc_id, note |
| GD-SRC-03 | Chốt format section_id, span_id, chunk_id | A | B | GD-SRC-01 | quy ước ID trong guideline |
| GD-SRC-04 | Tạo section index khung cho 4 sách | B | C | GD-SRC-02 | source_sections_index.json |
| GD-SRC-05 | Kiểm tra consistency page numbering | B | A | GD-SRC-04 | report |

### 6.3. Nhóm CHART / ENGINE

| Mã việc | Tên việc | Owner | Phụ | Depends on | Output |
|---------|----------|-------|-----|------------|--------|
| GD-CHART-01 | Chốt schema chart_repr | A | C | GD-SETUP-03 | chart_repr_schema.json |
| GD-CHART-02 | Export 10 chart từ engine | C | A | GD-CHART-01 | CHART-001.json ... CHART-010.json |
| GD-CHART-03 | Chuẩn hóa tên sao/cung/đắc tính | C | B | GD-CHART-02 | chart JSON sạch |
| GD-CHART-04 | Gán coverage tags cho 10 chart | A | B | GD-CHART-03 | chart_registry.json draft |
| GD-CHART-05 | Review chéo 10 chart | A | C | GD-CHART-04 | audit report |
| GD-CHART-06 | Freeze chart registry | A | — | GD-CHART-05 | chart_registry.json locked |

### 6.4. Nhóm QUESTION DESIGN

| Mã việc | Tên việc | Owner | Phụ | Depends on | Output |
|---------|----------|-------|-----|------------|--------|
| GD-QA-01 | Tạo question slot matrix 100 câu | A | B | GD-CHART-06 | question_slots.csv |
| GD-QA-02 | Phân bổ 10 chart x 10 câu | A | — | GD-QA-01 | slot theo chart |
| GD-QA-03 | Gắn topic + owner cho từng slot | A | B | GD-QA-02 | sample_plan.csv |
| GD-QA-04 | Generate candidate questions bằng LLM | C | A | GD-QA-03 | drafts_questions.jsonl |
| GD-QA-05 | Human chọn/sửa câu hỏi final | A/B/C | — | GD-QA-04 | 100 câu hỏi final |

### 6.5. Nhóm GOLD SECTION SELECTION

| Mã việc | Tên việc | Owner | Phụ | Depends on | Output |
|---------|----------|-------|-----|------------|--------|
| GD-EVD-01 | Chia 100 slot thành 3 batch | A | — | GD-QA-03 | bảng phân slot |
| GD-EVD-02 | Tìm gold_context_spans cho batch A | A | — | GD-EVD-01, GD-SRC-04 | gold_sections_A.jsonl |
| GD-EVD-03 | Tìm gold_context_spans cho batch B | B | — | GD-EVD-01, GD-SRC-04 | gold_sections_B.jsonl |
| GD-EVD-04 | Tìm gold_context_spans cho batch C | C | — | GD-EVD-01, GD-SRC-04 | gold_sections_C.jsonl |
| GD-EVD-05 | Merge gold sections | A | C | GD-EVD-02/03/04 | gold_sections.jsonl |
| GD-EVD-06 | Audit consistency spans | A | B | GD-EVD-05 | audit report |

### 6.6. Nhóm GOLD ANSWER / ANNOTATION

| Mã việc | Tên việc | Owner | Phụ | Depends on | Output |
|---------|----------|-------|-----|------------|--------|
| GD-ANS-01 | Generate draft answers | C | A | GD-EVD-05 | drafts_answers.jsonl |
| GD-ANS-02 | Primary edit batch A | A | — | GD-ANS-01 | golden_candidates_A.jsonl |
| GD-ANS-03 | Primary edit batch B | B | — | GD-ANS-01 | golden_candidates_B.jsonl |
| GD-ANS-04 | Primary edit batch C | C | — | GD-ANS-01 | golden_candidates_C.jsonl |
| GD-ANS-05 | Merge golden candidates | A | C | GD-ANS-02/03/04 | golden_candidates.jsonl |
| GD-ANS-06 | Tạo sentence-to-span map | A/B/C | — | GD-ANS-05 | sentence_span_map.jsonl |

### 6.7. Nhóm REVIEW / RELEASE

| Mã việc | Tên việc | Owner | Phụ | Depends on | Output |
|---------|----------|-------|-----|------------|--------|
| GD-RVW-01 | Cross-review batch A bởi B | B | — | GD-ANS-05 | review notes |
| GD-RVW-02 | Cross-review batch B bởi C | C | — | GD-ANS-05 | review notes |
| GD-RVW-03 | Cross-review batch C bởi A | A | — | GD-ANS-05 | review notes |
| GD-RVW-04 | Tổng hợp review reports | A | B | GD-RVW-01/02/03 | review_reports.csv |
| GD-RVW-05 | Sửa sample bị flag | owner batch | — | GD-RVW-04 | revised samples |
| GD-REL-01 | Map gold_context_spans → gold_chunk_ids | C | A | GD-RVW-05 | gold_with_chunk_map.jsonl |
| GD-REL-02 | Validate schema release | C | A | GD-REL-01 | validator report |
| GD-REL-03 | Freeze golden_v1_release.jsonl | A | — | GD-REL-02 | release v1 |
| GD-REL-04 | Viết final summary | A | B | GD-REL-03 | final_summary.md |

---

## 7. Dependency tổng quát

```text
SETUP
  -> SOURCE
  -> CHART
SOURCE + CHART
  -> QUESTION DESIGN
QUESTION DESIGN
  -> GOLD SECTION SELECTION
GOLD SECTION SELECTION
  -> GOLD ANSWER / ANNOTATION
ANNOTATION
  -> REVIEW
REVIEW
  -> CHUNK MAPPING
CHUNK MAPPING
  -> RELEASE FREEZE
```

---

## 8. Timeline theo ngày

### Day 1 — 17/06

**Mục tiêu:** Khóa workspace benchmark, file structure, ownership.

**A làm:**
- GD-SETUP-01
- GD-SETUP-02
- GD-SETUP-03
- GD-CTRL-01

**B làm:**
- rà lại tên file 4 sách, metadata gốc

**C làm:**
- tạo skeleton scripts folder
- chuẩn bị helper script nếu cần

**Output cuối ngày:**
- folder benchmark hoàn chỉnh
- guideline và schema đã đặt đúng chỗ
- daily tracker hoạt động

**A đánh giá:**
- tree thư mục có đúng không
- guideline có đúng file mới nhất không
- schema JSON có parse được không
- ai sở hữu file nào đã rõ chưa

### Day 2 — 18/06

**Mục tiêu:** Khóa source registry + chart schema.

**A làm:**
- GD-SRC-01
- GD-SRC-03
- GD-CHART-01

**B làm:**
- GD-SRC-02
- bắt đầu GD-SRC-04

**C làm:**
- chuẩn bị export chart từ engine

**Output cuối ngày:**
- source_registry.json
- format section_id, span_id, chunk_id
- chart_repr_schema.json

**A đánh giá:**
- 4 doc_id duy nhất
- schema chart có đủ field bắt buộc
- format ID không mơ hồ

### Day 3 — 19/06

**Mục tiêu:** Export 10 chart + source sections index draft.

**A làm:**
- hỗ trợ review chart
- bắt đầu gắn coverage logic

**B làm:**
- GD-SRC-04
- GD-SRC-05

**C làm:**
- GD-CHART-02
- GD-CHART-03

**Output cuối ngày:**
- 10 chart JSON
- source sections index bản đầu
- chart registry draft

**A đánh giá:**
- đủ 12 cung chưa
- tên cung chuẩn hóa chưa
- sao có dấu/Title Case chưa
- major/aux stars đã tách được chưa
- còn OCR noise hay raw dump không

### Day 4 — 20/06

**Mục tiêu:** Freeze chart registry + tạo question slot matrix.

**A làm:**
- GD-CHART-05
- GD-CHART-06
- GD-QA-01
- GD-QA-02

**B làm:**
- hỗ trợ topic coverage

**C làm:**
- chuẩn bị script generate question drafts

**Output cuối ngày:**
- chart_registry.json locked
- question_slots.csv phiên bản đầu

**A đánh giá:**
- 10 chart x 10 slot = 100 đúng tuyệt đối
- phân bổ 10/40/50 đúng tuyệt đối
- topic coverage không lệch quá mạnh

### Day 5 — 21/06

**Mục tiêu:** Generate candidate questions + chia batch annotation.

**A làm:**
- GD-QA-03
- GD-EVD-01

**B làm:**
- review candidate question sơ bộ

**C làm:**
- GD-QA-04

**Output cuối ngày:**
- drafts_questions.jsonl
- chia batch A/B/C rõ ràng

**A đánh giá:**
- question có đúng loại hop không
- có câu nào quá rộng không
- có trùng nghĩa không
- required_entities có rõ không

### Day 6 — 22/06

**Mục tiêu:** Chốt 100 câu hỏi final + bắt đầu gold section selection.

**A/B/C làm:**
- GD-QA-05
- bắt đầu GD-EVD-02/03/04

**Output cuối ngày:**
- 100 câu hỏi final
- khoảng 30–40 sample đã có gold spans

**A đánh giá:**
- câu hỏi có tự nhiên không
- span trích có thật không
- doc_id/page/section có điền đúng không

### Day 7 — 23/06

**Mục tiêu:** Hoàn thành gold sections cho 100 sample.

**A làm:**
- GD-EVD-05
- GD-EVD-06

**B/C làm:**
- hoàn tất batch gold sections còn lại

**Output cuối ngày:**
- gold_sections.jsonl

**A đánh giá:**
- 100/100 sample có evidence mode hợp lệ
- direct sample có spans rỗng đúng chủ đích
- one-hop/two-hop có 1–3 spans hợp lý
- format span IDs thống nhất

### Day 8 — 24/06

**Mục tiêu:** Generate draft answers + primary edit.

**A làm:**
- GD-ANS-02

**B làm:**
- GD-ANS-03

**C làm:**
- GD-ANS-01
- GD-ANS-04

**Output cuối ngày:**
- golden_candidates_A.jsonl
- golden_candidates_B.jsonl
- golden_candidates_C.jsonl

**A đánh giá:**
- answer grounded đúng theo spans chưa
- expected_answer_summary có ngắn gọn và chấm được không
- câu trả lời có tone an toàn không

### Day 9 — 25/06

**Mục tiêu:** Merge candidates + sentence-span map + cross-review.

**A làm:**
- GD-ANS-05
- GD-RVW-03

**B làm:**
- GD-RVW-01

**C làm:**
- GD-RVW-02

**A/B/C cùng làm:**
- GD-ANS-06

**Output cuối ngày:**
- golden_candidates.jsonl
- sentence_span_map.jsonl
- review notes

**A đánh giá:**
- sample nào fail phải có lý do rõ
- câu nào trong answer không map được về span phải bị flag
- không có answer vượt source

### Day 10 — 26/06

**Mục tiêu:** Fix flagged samples + chunk mapping + validate release.

**A/B/C làm:**
- GD-RVW-05

**C làm:**
- GD-REL-01
- GD-REL-02

**A làm:**
- review readiness để freeze

**Output cuối ngày:**
- gold_with_chunk_map.jsonl
- validator report

**A đánh giá:**
- sample count = 100
- schema pass
- no duplicate IDs
- direct sample có chunk_ids rỗng hợp lệ
- mapping chunk có dùng được cho retrieval eval

### Day 11 — 27/06

**Mục tiêu:** Freeze release + final summary.

**A làm:**
- GD-REL-03
- GD-REL-04

**B làm:**
- hỗ trợ thống kê

**C làm:**
- fix kỹ thuật nhỏ nếu còn

**Output cuối:**
- golden_v1_release.jsonl
- final_summary.md

**A đánh giá cuối:**
- có đúng 100 sample không
- có đúng 10 Direct / 40 One-hop / 50 Two-hop không
- 10 chart đều có 10 câu không
- release giao cho pipeline benchmark được ngay không

---

## 9. Phân chia sample thực tế cho A/B/C

Vì A giữ nhiều phần lõi và review cuối, A không nên annotate nhiều ngang B/C.

**Phân bổ primary annotation:**
- A: 28 sample
- B: 36 sample
- C: 36 sample

**Phân bổ cross-review:**
- B review 6 sample của A
- C review 7 sample của B
- A review 7 sample của C

Nếu tiến độ ổn và D rảnh, D có thể hỗ trợ các việc ít rủi ro:
- rename files
- fill metadata còn thiếu
- check duplicated IDs
- format CSV/JSONL

---

## 10. Chuẩn output của các file quan trọng

### 10.1. source_registry.json

Mỗi source phải có:
- doc_id
- title
- file_name
- domain
- citation_short
- id_convention
- notes

### 10.2. chart_registry.json

Mỗi chart phải có:
- chart_id
- birth_info
- chart_file
- status
- coverage_tags

### 10.3. question_slots.csv

Phải có tối thiểu các cột:
- slot_id
- sample_id
- chart_id
- question_no
- question_complexity
- topic
- owner_primary
- owner_review
- status
- notes

### 10.4. gold_sections.jsonl

Mỗi record phải có:
- id
- chart_id
- question
- gold_context_spans

### 10.5. golden_v1_release.jsonl

Mỗi sample phải có:
- id
- chart_id
- birth_info
- chart_repr
- question
- question_complexity
- gold_answer
- expected_answer_summary
- gold_context_spans
- gold_chunk_ids
- required_entities
- labels

---

## 11. Checklist review của A theo từng nhóm việc

### 11.1. Review source/corpus

- [ ] doc_id duy nhất
- [ ] format section/span/chunk chuẩn
- [ ] page numbering không lệch nghiêm trọng
- [ ] quote lấy đúng sách

### 11.2. Review chart

- [ ] đủ 12 cung
- [ ] tên sao chuẩn hóa
- [ ] major/aux stars đúng
- [ ] chart summary đủ field

### 11.3. Review question

- [ ] đúng loại hop
- [ ] không quá rộng
- [ ] không trùng ý
- [ ] benchmark được thật

### 11.4. Review gold context

- [ ] là quote thật
- [ ] có doc_id, section_id, span_id, page_pdf
- [ ] đủ support answer
- [ ] không quá ngắn vô nghĩa, không quá dài lan man

### 11.5. Review gold answer

- [ ] grounded
- [ ] đúng trọng tâm
- [ ] không bịa
- [ ] tone an toàn, không quá định mệnh

### 11.6. Review release

- [ ] 100 sample đủ
- [ ] schema pass
- [ ] không duplicate
- [ ] chunk mapping usable
- [ ] giao được cho pipeline benchmark

---

## 12. Workflow quản lý công việc khuyến nghị cho A

### 12.1. Daily status bắt buộc

A duy trì file:

```text
benchmark/tuvi_golden_dataset/reports/daily_status.md
```

Format:

```markdown
## 2026-06-17
### A
- done:
- blocked:
- next:

### B
- done:
- blocked:
- next:

### C
- done:
- blocked:
- next:
```

### 12.2. Nhịp họp ngắn

Mỗi ngày 2 lần là đủ:

**Buổi sáng, 15 phút:**
- ai đang block ai
- việc nào phụ thuộc việc nào
- output nào cần review sớm

**Cuối ngày, 15 phút:**
- file nào đã xong
- file nào A cần review
- việc ngày mai có bị nghẽn không

### 12.3. Git workflow khuyến nghị

Branches:
- `benchmark/a-work`
- `benchmark/b-annotation`
- `benchmark/c-tooling`

Rule:
- file chung phải rebase trước khi merge
- `golden_v1_release.jsonl` chỉ A commit/freeze cuối

---

## 13. Rủi ro chính và cách chặn

| Rủi ro | Dấu hiệu | Cách chặn |
|--------|----------|-----------|
| Conflict file | nhiều người sửa cùng 1 file | file ownership + tách file theo người |
| Trôi schema | mỗi người annotate 1 kiểu | khóa schema từ đầu |
| Quote sai nguồn | thiếu doc_id/page/section | bắt buộc metadata spans |
| Answer vượt source | answer "hay hơn" evidence | sentence-span mapping + cross-review |
| Chậm tiến độ | Day 7 chưa xong gold sections | ưu tiên spans trước, việc phụ làm sau |
| Chunk mapping lỗi | section chưa chuẩn | dry-run script trước Day 10 |

---

## 14. Định nghĩa Done của sprint

Sprint chỉ được coi là hoàn thành khi đạt đồng thời tất cả điều kiện sau:

- [ ] 10 chart đã freeze
- [ ] 100 sample đã freeze
- [ ] đúng 10 Direct / 40 One-hop / 50 Two-hop
- [ ] golden_v1_release.jsonl pass schema validation
- [ ] gold_with_chunk_map.jsonl dùng được cho retrieval eval
- [ ] review reports đầy đủ
- [ ] final summary đã commit

---

## 15. Ghi chú cuối cho toàn team

Trong sprint này, chất lượng benchmark quan trọng hơn số lượng draft.

**Quy tắc vàng:**
- Không được bịa quote sách.
- Không được sửa schema giữa chừng sau khi đã freeze.
- Nếu gặp case mơ hồ trong source hoặc chart, phải flag để A adjudicate, không tự quyết theo cảm tính.

**Ưu tiên cao nhất theo thứ tự:**
1. khóa schema
2. khóa chart pool
3. khóa question slots
4. lấy đúng gold spans
5. viết đúng gold answer
6. map chunk và freeze release
