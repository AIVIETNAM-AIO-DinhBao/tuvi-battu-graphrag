# Guideline Tạo Golden Dataset QA 100 Câu cho Benchmark RAG Tử Vi

## Mục lục

- [Mục tiêu của dataset](#mục-tiêu-của-dataset)
- [1. NGUỒN TRI THỨC: 4 SÁCH](#1-nguồn-tri-thức-4-sách)
- [2. HỆ THỐNG ID CHUẨN HOÁ](#2-hệ-thống-id-chuẩn-hoá)
- [3. RELEASE SCHEMA - Dataset Xuất Chính Thức](#3-release-schema---dataset-xuất-chính-thức)
- [4. OPS SCHEMA - Metadata Nội Bộ (Không Export)](#4-ops-schema---metadata-nội-bộ-không-export)
- [5. PHÂN TÍCH TUVI_ENGINE VÀ CHART CONTEXT](#5-phân-tích-tuvi_engine-và-chart-context)
- [6. QUY TRÌNH THỰC HIỆN: 3 PHASE](#6-quy-trình-thực-hiện-3-phase)
  - [PHASE 1 — SETUP 10 LÁ SỐ](#phase-1--setup-10-lá-số-chart-selection)
  - [PHASE 2 — SINH 100 CÂU HỎI](#phase-2--sinh-100-câu-hỏi-10-chart-x-10-câu)
  - [PHASE 3 — HUMAN-LLM COLLABORATION](#phase-3--human-llm-collaboration)
- [7. PROMPT TEMPLATES CHO LLM](#7-prompt-templates-cho-llm)
- [8. QUY ĐỊNH CHUẨN HÓA](#8-quy-định-chuẩn-hóa)
- [9. CẤU TRÚC THƯ MỤC KHUYẾN NGHỊ](#9-cấu-trúc-thư-mục-khuyến-nghị)
- [10. SAMPLE MINH HỌA HOÀN CHỈNH (5 mẫu)](#10-sample-minh-họa-hoàn-chỉnh-5-mẫu)
- [11. CHECKLIST CHẤT LƯỢNG TRƯỚC KHI KHÓA SAMPLE](#11-checklist-chất-lượng-trước-khi-khóa-sample)
- [12. KẾT LUẬN VÀ KHUYẾN NGHỊ THỰC THI](#12-kết-luận-và-khuyến-nghị-thực-thi)

---

## Mục tiêu của dataset
Tạo 100 sample QA để benchmark hệ thống RAG Tử Vi với 2 cụm đánh giá:

**Retrieval Evaluation:**
- Hit@1 / Hit@3 / Hit@5
- MRR@K (Mean Reciprocal Rank)
- Context Recall
- Graph Hit Rate (custom metric cho Knowledge Graph)
- Citation Coverage

**Generation Evaluation:**
- Faithfulness / Groundedness
- Answer Correctness
- Answer Relevancy
- Coverage
- Tone / Safety

---

## 1. NGUỒN TRI THỨC: 4 SÁCH 

Benchmark sử dụng đúng 4 sách PDF đính kèm làm nguồn pháp điển duy nhất:

| doc_id | Tên sách chuẩn | File gốc | Điểm mạnh |
|---|---|---|---|
| `TVKL` | Tử Vi Khảo Luận | Tử Vi Khảo Luận.pdf | Nền tảng, tinh đẩu, vận hạn, cách/phú |
| `TVNL` | Tử Vi Nghiệm Lý Toàn Thư | Tử Vi Nghiệm Lý, Lý Mệnh Học.pdf | Logic nghiệm lý, 3 vòng, Tứ Hóa |
| `TVHS` | Tử Vi Hàm Số | Tử Vi Hàm Số.pdf | Hệ thống 12 cung, cấu trúc |
| `TVGM` | Tử Vi Giảng Minh | Tử Vi Giảng Minh.pdf | Nguyên tắc đầu, an sao, giải đoán |

**Lưu ý**: Mọi `gold_context_spans` phải trích từ 4 sách này. Không được dùng nguồn ngoài.

---

## 2. HỆ THỐNG ID CHUẨN HOÁ

### 2.1. `doc_id` - Mã sách
Format: 4 ký tự viết hoa
- `TVKL`, `TVNL`, `TVHS`, `TVGM`

### 2.2. `section_id` - Mã phần/mục
**Format ưu tiên** (nếu sách có cấu trúc chương rõ):
```
{doc_id}_CH{chapter_no}_SEC{section_no}
```
Ví dụ: `TVGM_CH03_SEC04`, `TVHS_CH02_SEC11`

**Format fallback** (nếu không xác định được chương):
```
{doc_id}_P{start_page}_{end_page}_SEC{running_no}
```
Ví dụ: `TVKL_P074_076_SEC01`, `TVNL_P092_092_SEC03`

### 2.3. `span_id` - Mã đoạn trích cụ thể
Format:
```
{section_id}_SP{span_no}
```
Ví dụ: `TVGM_CH03_SEC04_SP01`, `TVNL_P092_092_SEC03_SP02`

### 2.4. `chunk_id` - Mã chunk của retrieval pipeline
Format:
```
{doc_id}_CK_{running_no}
```
Ví dụ: `TVGM_CK_001245`, `TVNL_CK_000918`

**Quy tắc quan trọng:**
- `section_id` / `span_id` = **ground truth pháp điển** (human chọn)
- `chunk_id` = **implementation detail** của retriever
- Benchmark retrieval phải chấm theo: `gold span → map sang chunk_id(s)` SAU, không được định nghĩa gold trực tiếp từ retriever

### 2.5. Số trang PDF vs số trang in sách
Lưu cả hai nếu có thể:
- `page_pdf`: số trang trong file PDF (dùng để verify)
- `page_book`: số trang in trong sách (dùng để đọc thuận tiện)

---

## 3. RELEASE SCHEMA - Dataset Xuất Chính Thức

### 3.1. Nguyên tắc thiết kế
Schema release phải:
- **Gọn**: chỉ chứa trường cần cho benchmark
- **Đủ**: đủ để đánh giá retrieval và generation
- **Ổn định**: không thay đổi giữa các lần chạy benchmark
- **Không chứa metadata nội bộ**: annotator, review status, v.v.

### 3.2. Schema JSON đầy đủ

```json
{
  "id": "TVQA-001",
  "chart_id": "CHART-001",
  "birth_info": {
    "date_solar": "1990-10-15",
    "time": "09:00",
    "timezone": "Asia/Ho_Chi_Minh",
    "gender": "Nam"
  },
  "chart_repr": {
    "menh_position": "Thìn",
    "than_position": "Dần",
    "ban_menh": "Lộ Bàng Thổ",
    "ngu_hanh_ban_menh": "Thổ",
    "cuc": "Thủy Nhị Cục",
    "am_duong_nam_nu": "Dương Nam",
    "houses": [
      {
        "house_index": 1,
        "earthly_branch": "Tý",
        "house_name": "Tài Bạch",
        "is_menh_resident": false,
        "is_than_resident": false,
        "house_element": "Thủy",
        "yin_yang": "Dương",
        "dai_han_age": 84,
        "tieu_han_branch": "Dần",
        "major_stars": [
          {"name": "Cú Môn", "status": "Vượng"}
        ],
        "aux_stars": [
          {"name": "Tướng Quân"},
          {"name": "Tuế Phá"}
        ]
      }
    ]
  },
  "question": "Câu hỏi từ người dùng",
  "question_complexity": "Direct",
  "gold_answer": "Câu trả lời chuẩn cuối cùng được human verify",
  "expected_answer_summary": "Tóm tắt ngắn các ý cốt lõi bắt buộc có",
  "gold_context_spans": [
    {
      "doc_id": "TVGM",
      "section_id": "TVGM_CH03_SEC04",
      "span_id": "TVGM_CH03_SEC04_SP01",
      "page_pdf": 195,
      "page_book": 195,
      "quote": "Trích đoạn nguyên văn CHÍNH XÁC từ sách",
      "char_start": null,
      "char_end": null
    }
  ],
  "gold_chunk_ids": [],
  "required_entities": ["Thái Dương", "Mệnh", "Ngọ"],
  "labels": {
    "topic": "career",
    "retrieval_eval_included": true,
    "generation_eval_included": true,
    "safety_flag": 0
  }
}
```

### 3.3. Định nghĩa chi tiết từng trường

| Field | Bắt buộc | Type | Mô tả |
|---|:---:|---|---|
| `id` | ✅ | string | Mã sample duy nhất, format: `TVQA-{001..100}` |
| `chart_id` | ✅ | string | ID lá số, format: `CHART-{001..010}` |
| `birth_info` | ✅ | object | Thông tin sinh đầu vào |
| `birth_info.date_solar` | ✅ | string | Ngày sinh dương lịch (YYYY-MM-DD) |
| `birth_info.time` | ✅ | string | Giờ sinh (HH:MM) |
| `birth_info.timezone` | ✅ | string | Múi giờ |
| `birth_info.gender` | ✅ | string | "Nam" hoặc "Nữ" |
| `chart_repr` | ✅ | object | Biểu diễn JSON rút gọn của lá số |
| `chart_repr.menh_position` | ✅ | string | Vị trí cung Mệnh (địa chi) |
| `chart_repr.than_position` | ✅ | string | Vị trí cung Thân (địa chi) |
| `chart_repr.ban_menh` | ✅ | string | Bản mệnh納音 |
| `chart_repr.ngu_hanh_ban_menh` | ✅ | string | Ngũ hành bản mệnh |
| `chart_repr.cuc` | ✅ | string | Cục (VD: "Thủy Nhị Cục") |
| `chart_repr.am_duong_nam_nu` | ✅ | string | "Dương Nam", "Dương Nữ", "Âm Nam", "Âm Nữ" |
| `chart_repr.houses` | ✅ | array | Danh sách 12 cung |
| `question` | ✅ | string | Câu hỏi benchmark |
| `question_complexity` | ✅ | enum | `"Direct"`, `"One-hop"`, hoặc `"Two-hop"` |
| `gold_answer` | ✅ | string | Câu trả lời chuẩn cuối cùng |
| `expected_answer_summary` | ✅ | string | Tóm tắt ngắn các ý bắt buộc |
| `gold_context_spans` | ✅ | array | Danh sách đoạn trích ground truth |
| `gold_chunk_ids` | ✅ | array | Chunk IDs tương ứng (post-processing) |
| `required_entities` | ✅ | array | Sao/cung/khái niệm bắt buộc nhận diện |
| `labels.topic` | ✅ | string | Chủ đề (career, wealth, personality, v.v.) |

---

## 4. OPS SCHEMA - Metadata Nội Bộ (Không Export)

### 4.1. Metadata chỉ dùng nội bộ

Các trường sau KHÔNG nằm trong release schema, chỉ dùng cho workflow:
- `expected_answer_points`: Checklist các ý bắt buộc phải có trong answer
- `negative_constraints`: Những điều không được nói sai hoặc không được bịa
- `answer_rubric`: Tiêu chí chấm correctness chi tiết
- `annotator`: `{author, created_at}`
- `verification`: `{reviewer, status, notes}`
- `status`: `draft` / `verified` / `adjudicated` / `locked`
- `difficulty`: `easy` / `medium` / `hard` (không bắt buộc)

**Lưu trong file riêng**: `golden_v1_ops.jsonl` hoặc `review_reports.csv`

### 4.2. Tại sao tách riêng?
- Dataset release phải gọn, ổn định, chỉ chứa ground truth
- Metadata ops giúp quản lý workflow nhưng không cần cho benchmark
- Tách rõ giúp maintain và version control dễ hơn

---

## 5. PHÂN TÍCH TUVI_ENGINE VÀ CHART CONTEXT

### 5.1. Output hiện tại của engine
Từ file Tuvi_Engine.pdf, engine trả ra:
- Input: ngày, tháng, năm, giờ sinh, giới tính, múi giờ
- Output: `cungMenh`, `cungThan`, `thapNhiCung`
- Mỗi cung: `cungSo`, `cungTen`, `cungChu`, `cungThan`, `hanhCung`, `cungAmDuong`, `cungDaiHan`, `cungTieuHan`, `cungSao`
- Mỗi sao: `saoTen`, `saoDacTinh`

### 5.2. Vấn đề cần chuẩn hóa
- Raw output chưa tách chính tinh/phụ tinh rõ ràng
- Chưa có `ban_menh` / `cuc` / `am_duong_nam_nu` trong snippet
- Tên sao có thể có OCR noise
- Cần normalize về format chuẩn cho benchmark

### 5.3. Chart schema đề xuất cho RAG context

**Các field bắt buộc:**

Top-level:
- `chart_id`
- `birth_info` (date_solar, time, timezone, gender)
- `menh_position`, `than_position`
- `ban_menh`, `ngu_hanh_ban_menh`
- `cuc`
- `am_duong_nam_nu`

Per house (đủ 12 cung):
- `house_index` (1-12)
- `earthly_branch` (Tý, Sửu, Dần...)
- `house_name` (Mệnh, Phụ Mẫu, Phúc Đức...)
- `is_menh_resident` (boolean)
- `is_than_resident` (boolean)
- `house_element` (Thủy, Hỏa, Mộc, Kim, Thổ)
- `yin_yang` (Âm/Dương)
- `dai_han_age`
- `tieu_han_branch`
- `major_stars` (array of {name, status})
- `aux_stars` (array of {name, status})

### 5.4. Taxonomy sao chính tinh / phụ tinh
Cần file taxonomy để phân loại:
```json
{
  "major_stars": [
    "Tử Vi", "Thiên Cơ", "Thái Dương", "Thái Âm",
    "Liêm Trinh", "Thiên Phủ", "Vũ Khúc", "Tham Lang",
    "Cự Môn", "Thiên Tướng", "Thiên Lương", "Thất Sát",
    "Phá Quân", "Thiên Đồng"
  ],
  "aux_stars": [
    "Hóa Lộc", "Hóa Quyền", "Hóa Khoa", "Hóa Kỵ",
    "Lộc Tồn", "Địa Kiếp", "Địa Không", "Kình Dương",
    "Đà La", "Thiên Khôi", "Thiên Việt", "Tả Phụ",
    "Hữu Bật", "Văn Xương", "Văn Khúc", "Linh Tinh",
    "Hỏa Tinh", "Thiên Khốc", "Thiên Hư", "Long Trì",
    "Phượng Các", "Thai Phù", "Phong Cáo", "Giải Thần",
    "Thiên Mã", "Tam Đài", "Bát Tọa"
  ]
}
```

---

## 6. QUY TRÌNH THỰC HIỆN: 3 PHASE

### PHASE 1 — SETUP 10 LÁ SỐ (Chart Selection)

#### 6.1.1. Mục tiêu
Chọn 10 chart đa dạng để sinh 100 câu benchmark cân bằng.

#### 6.1.2. Nguyên tắc đa dạng

| Trục | Yêu cầu |
|---|---|
| Giới tính | 5 Nam / 5 Nữ |
| Giờ sinh | Phủ nhiều địa chi giờ khác nhau |
| Mệnh/Cục | Phủ nhiều ngũ hành, nhiều loại cục |
| Vị trí Mệnh | Không dồn vào 1-2 cung |
| Vị trí Thân | Đa dạng |
| Chính tinh chủ đạo | Phủ các nhóm: Tử Phủ Vũ Tướng, Sát Phá Liêm Tham, Cơ Nguyệt Đồng Lương, Cự Nhật |
| Phụ tinh nổi bật | Có chart có Khoa/Quyền/Lộc, có chart có Không/Kiếp, Kình/Đà |
| Độ phức tạp | Cả chart dễ luận và chart khó luận |

#### 6.1.3. Deliverable Phase 1
- `charts/chart_registry.json`
- `charts/CHART-001.json` ... `charts/CHART-010.json`
- `coverage_matrix.xlsx` (optional, để tracking)

---

### PHASE 2 — SINH 100 CÂU HỎI (10 chart x 10 câu)

#### 6.2.1. Phân bổ cố định cho mỗi chart
```
Mỗi chart = 1 Direct + 4 One-hop + 5 Two-hop
Total = 10 Direct + 40 One-hop + 50 Two-hop = 100 samples
```

#### 6.2.2. Chủ đề cần phủ
- Overview / tổng quan
- Personality / tính cách
- Career / sự nghiệp
- Wealth / tài lộc
- Love/Marriage / tình cảm
- Health / sức khỏe
- Family/Parents / gia đạo
- Property / điền trạch
- Social relations / giao tế
- Major luck / đại hạn

#### 6.2.3. Định nghĩa DIRECT (10%)

**Tiêu chí:**
- Chỉ cần đọc `chart_repr`
- Không cần sách
- Không cần suy luận

**Ví dụ tốt:**
- "Cung Mệnh của lá số này nằm ở đâu?"
- "Cung Quan Lộc có những chính tinh nào?"
- "Đại hạn của cung Tài Bạch bắt đầu từ tuổi nào?"

**Ví dụ KHÔNG tốt:**
- "Cung Mệnh có tốt không?" → đã sang one-hop

**Rule chấm:**
- Đúng fact từ chart
- Đúng tên cung/sao
- Không bỏ sót fact chính nếu liệt kê

#### 6.2.4. Định nghĩa ONE-HOP (40%)

**Tiêu chí:**
```
1 fact từ chart + 1 rule từ sách → answer
```

**Ví dụ tốt:**
- "Thái Dương ở cung Mệnh tại Ngọ nên gọi theo cách nào?"
- "Mệnh nằm trong tam hợp Thái Tuế thì khí chất nên luận ra sao?"
- "Cung Điền Trạch có Tử Vi, Phá Quân thì ý nghĩa trọng tâm là gì?"

**Rule chấm:**
- Phải dùng đúng source quote
- Không suy diễn thêm ngoài 1 bước
- Nếu chỉ hỏi "ý nghĩa chính", không lan man sang nhiều cung khác

#### 6.2.5. Định nghĩa TWO-HOP (50%)

**Tiêu chí:**
```
chart fact A + chart fact B + rule(s) từ sách → answer
```
Cần ít nhất 2 bước reasoning, thường là đa cung, đa sao, hoặc đa nguồn.

**Ví dụ tốt:**
- "Mệnh có Không Kiếp, Tài Bạch có Hóa Lộc thì xu hướng kiếm tiền ra sao?"
- "Quan Lộc và Tài Bạch của lá số này hỗ trợ hay xung nhau?"
- "Mệnh trong tam hợp Thái Tuế, Quan Lộc có Lộc Tồn; khi luận công danh cần kết hợp hai lớp nghĩa nào?"

**Rule chấm:**
- Phải chứng minh được ít nhất 2 bước
- Phải có 1-3 gold spans
- Không được "nhảy cóc" sang kết luận không có evidence

#### 6.2.6. Ma trận 10 câu cho mỗi chart

| Slot | Loại | Gợi ý nội dung |
|---|---|---|
| Q1 | Direct | 1 fact thuần chart |
| Q2 | One-hop | 1 sao/cung nổi bật |
| Q3 | One-hop | 1 tổ hợp sao đơn giản |
| Q4 | One-hop | 1 rule mệnh/cục/tam hợp |
| Q5 | One-hop | Đại hạn hoặc orientation |
| Q6 | Two-hop | Mệnh + Tài Bạch |
| Q7 | Two-hop | Mệnh + Quan Lộc |
| Q8 | Two-hop | Mệnh + Thiên Di/Phu Thê |
| Q9 | Two-hop | Chính tinh + phụ tinh |
| Q10 | Two-hop | Tổng hợp 2+ source spans |

---

### PHASE 3 — HUMAN-LLM COLLABORATION

#### 6.3.1. Vai trò phân công
- **Project Lead**: chốt source, adjudicate conflicts, sign-off cuối
- **Infra/Dev**: script generate draft, map chunk_ids, validation
- **4 Annotators**: primary edit (25 samples/người) + cross review

#### 6.3.2. Quy trình chuẩn

**Bước 1 — Freeze chart**
- Export chart JSON chuẩn hóa
- Gắn `chart_id` ổn định
- Không đổi chart sau khi đã tạo câu hỏi

**Bước 2 — LLM sinh nháp câu hỏi**
Input: chart_repr + slot type + topic target
Output: 2-3 candidate questions/slot

**Bước 3 — Human chọn + sửa câu hỏi tốt nhất**
- Chọn 1 câu rõ ràng nhất
- Sửa wording cho tự nhiên
- Bỏ câu mơ hồ/quá rộng

**Bước 4 — LLM gợi ý nơi tìm evidence (KHÔNG BỊA QUOTE)**
LLM chỉ được:
- Gợi ý sách nào nên tra
- Section nào nên mở
- Entity nào phải xuất hiện

**Bước 5 — Human trích `gold_context_spans` thủ công**
Annotator phải:
- Mở đúng PDF/corpus cleaned
- Copy **nguyên văn chính xác**
- Điền `doc_id`, `section_id`, `span_id`, `page_pdf`, `quote`

**Bước 6 — LLM draft answer → Human verify thành `gold_answer`**
- LLM viết draft answer dựa trên chart + gold spans
- Human chỉnh sửa để đảm bảo grounded và đúng tone
- Điền `expected_answer_summary`

**Bước 7 — Cross review (20% samples)**
Reviewer khác kiểm tra:
- Fidelity: Answer có supported bởi gold spans không?
- Consistency: Không mâu thuẫn với nguồn?
- Tone: An toàn, không quyết định thay user?

**Bước 8 — Adjudication**
Lead xử lý các sample bị flag, chốt cuối.

#### 6.3.3. Luật chống bias
- Người tạo câu hỏi KHÔNG là người verify cuối cùng
- Ít nhất 2 người chạm vào mỗi sample
- Sample khó → Lead adjudicate

---

## 7. PROMPT TEMPLATES CHO LLM

### 7.1. Prompt A — Generate candidate questions

```
Bạn là trợ lý tạo benchmark QA cho hệ RAG Tử Vi.

Input:
- chart_repr JSON
- target complexity: {Direct|One-hop|Two-hop}
- target topic: {topic}

Nhiệm vụ:
- Sinh 3 câu hỏi candidate bằng tiếng Việt
- Câu hỏi rõ, tự nhiên, phù hợp người dùng phổ thông
- KHÔNG trả lời câu hỏi
- KHÔNG bịa thông tin ngoài chart
- Direct: chỉ hỏi fact có sẵn trong chart
- One-hop: cần chart + 1 tri thức từ sách
- Two-hop: cần ít nhất 2 bước suy luận

Output JSON:
[
  {
    "question": "...",
    "why_valid": "...",
    "required_entities": ["..."]
  }
]
```

### 7.2. Prompt B — Suggest source lookup (KHÔNG BỊA QUOTE)

```
Bạn KHÔNG được trích sách nếu chưa thấy văn bản nguồn.

Input:
- question
- chart_repr JSON
- danh sách 4 doc_id: TVKL, TVNL, TVHS, TVGM

Nhiệm vụ:
- Gợi ý sách nào nên tra
- Gợi ý loại section nên mở
- Liệt kê entity cần dò trong sách
- KHÔNG được tạo quote giả

Output JSON:
{
  "candidate_docs": ["TVGM", "TVNL"],
  "suggested_entities": ["Thái Dương", "tam hợp Thái Tuế"],
  "reason": "..."
}
```

### 7.3. Prompt C — Draft answer grounded

```
Bạn phải viết câu trả lời CHỈ dựa trên:
1) chart_repr JSON đã cho
2) gold_context_spans đã cung cấp

KHÔNG được dùng kiến thức ngoài input.
KHÔNG được thêm suy diễn vượt quá evidence.
Giọng văn: trung tính, giải thích rõ, không quyết định thay người dùng.
Độ dài: tối đa 250 từ.

Output JSON:
{
  "gold_answer_draft": "...",
  "expected_answer_summary": "..."
}
```

### 7.4. Prompt D — Judge answer quality

```
Bạn là reviewer benchmark.

Input:
- question
- chart_repr
- gold_context_spans
- gold_answer

Đánh giá:
- groundedness: 1-5 (answer có bám sát evidence không?)
- coverage: 1-5 (answer có đủ ý cần thiết không?)
- relevance: 1-5 (answer có đúng trọng tâm câu hỏi không?)
- tone_safety: 1-5 (tone có an toàn không?)
- issues: [danh sách vấn đề nếu có]

Chỉ chấm dựa trên evidence đã cho.
```

---

## 8. QUY ĐỊNH CHUẨN HÓA

### 8.1. Chuẩn hóa tên sao
**Phải dùng Title Case có dấu đầy đủ.**

✅ Đúng:
- `Tử Vi`, `Thiên Cơ`, `Thái Dương`, `Thái Âm`
- `Cự Môn`, `Liêm Trinh`, `Tham Lang`, `Phá Quân`
- `Hóa Lộc`, `Hóa Quyền`, `Hóa Khoa`, `Hóa Kỵ`

❌ Sai:
- `tử vi`, `Tu Vi`, `Thai Duong`, `hoa loc`

### 8.2. Chuẩn hóa 12 cung
Canonical list:
1. `Mệnh`
2. `Phụ Mẫu`
3. `Phúc Đức`
4. `Điền Trạch`
5. `Quan Lộc`
6. `Nô Bộc`
7. `Thiên Di`
8. `Tật Ách`
9. `Tài Bạch`
10. `Tử Tức`
11. `Phu Thê`
12. `Huynh Đệ`

### 8.3. Alias map (cho normalization)
```json
{
  "Phụ": "Phụ Mẫu",
  "Phúc": "Phúc Đức",
  "Điền": "Điền Trạch",
  "Quan": "Quan Lộc",
  "Nô": "Nô Bộc",
  "Di": "Thiên Di",
  "Ách": "Tật Ách",
  "Tài": "Tài Bạch",
  "Tử": "Tử Tức",
  "Phối": "Phu Thê",
  "Phu": "Phu Thê",
  "Bào": "Huynh Đệ"
}
```

### 8.4. Chuẩn hóa đắc tính sao
- `Miếu`, `Vượng`, `Đắc`, `Hãm`

Nếu engine cho ký hiệu: `M→Miếu`, `V→Vượng`, `Đ→Đắc`, `H→Hãm`

---

## 9. CẤU TRÚC THƯ MỤC KHUYẾN NGHỊ

```
benchmark_tuvi/
├── guideline.md (file này)
├── schema_release.json
├── schema_ops.json
├── corpus_cleaned/
│   ├── source_registry.json
│   ├── TVKL/
│   ├── TVNL/
│   ├── TVHS/
│   └── TVGM/
├── charts/
│   ├── chart_registry.json
│   ├── CHART-001.json
│   └── ...CHART-010.json
├── datasets/
│   ├── golden_v1_release.jsonl (100 samples chính thức)
│   ├── golden_v1_ops.jsonl (metadata nội bộ)
│   └── gold_with_chunk_map.jsonl (sau post-processing)
├── reviews/
│   └── review_reports.csv
└── tests/
    └── chart_validation.py
```

---

## 10. SAMPLE MINH HỌA HOÀN CHỈNH (5 mẫu)

### Sample 1 — Direct

```json
{
  "id": "TVQA-001",
  "chart_id": "CHART-001",
  "birth_info": {
    "date_solar": "1990-10-15",
    "time": "09:00",
    "timezone": "Asia/Ho_Chi_Minh",
    "gender": "Nam"
  },
  "chart_repr": {
    "menh_position": "Thìn",
    "than_position": "Dần",
    "ban_menh": "Lộ Bàng Thổ",
    "ngu_hanh_ban_menh": "Thổ",
    "cuc": "Thủy Nhị Cục",
    "am_duong_nam_nu": "Dương Nam",
    "houses": [
      {
        "house_index": 5,
        "earthly_branch": "Thìn",
        "house_name": "Mệnh",
        "is_menh_resident": true,
        "is_than_resident": false,
        "house_element": "Thổ",
        "yin_yang": "Dương",
        "dai_han_age": 54,
        "tieu_han_branch": "Mùi",
        "major_stars": [
          {"name": "Thái Dương", "status": "Vượng"}
        ],
        "aux_stars": [
          {"name": "Địa Kiếp", "status": "Hãm"},
          {"name": "Hóa Lộc"}
        ]
      }
    ]
  },
  "question": "Cung Mệnh của lá số này nằm ở đâu và có chính tinh nào?",
  "question_complexity": "Direct",
  "gold_answer": "Cung Mệnh nằm tại Thìn và chính tinh nổi bật trong cung Mệnh là Thái Dương ở trạng thái Vượng.",
  "expected_answer_summary": "Phải nêu đúng vị trí cung Mệnh là Thìn và nêu đúng chính tinh là Thái Dương (Vượng).",
  "gold_context_spans": [],
  "gold_chunk_ids": [],
  "required_entities": ["Mệnh", "Thìn", "Thái Dương"],
  "labels": {
    "topic": "overview",
    "retrieval_eval_included": false,
    "generation_eval_included": true,
    "safety_flag": 0
  }
}
```

### Sample 2 — One-hop

```json
{
  "id": "TVQA-015",
  "chart_id": "CHART-002",
  "birth_info": {
    "date_solar": "1992-06-21",
    "time": "11:30",
    "timezone": "Asia/Ho_Chi_Minh",
    "gender": "Nữ"
  },
  "chart_repr": {
    "menh_position": "Ngọ",
    "than_position": "Tuất",
    "ban_menh": "Dương Liễu Mộc",
    "ngu_hanh_ban_menh": "Mộc",
    "cuc": "Hỏa Lục Cục",
    "am_duong_nam_nu": "Dương Nữ",
    "houses": [
      {
        "house_index": 7,
        "earthly_branch": "Ngọ",
        "house_name": "Mệnh",
        "is_menh_resident": true,
        "is_than_resident": false,
        "house_element": "Hỏa",
        "yin_yang": "Dương",
        "dai_han_age": 36,
        "tieu_han_branch": "Mão",
        "major_stars": [
          {"name": "Thái Dương", "status": "Miếu"}
        ],
        "aux_stars": []
      }
    ]
  },
  "question": "Thái Dương ở cung Mệnh tại Ngọ của lá số này nên được gọi theo cách nào?",
  "question_complexity": "One-hop",
  "gold_answer": "Theo sách, Thái Dương ở Ngọ được gọi là 'Nhật lệ trung thiên'. Vì vậy trong lá số này, khi thấy Thái Dương đóng Mệnh tại Ngọ thì trước hết phải nhận diện đúng cách này.",
  "expected_answer_summary": "Phải xác định đúng tên cách là 'Nhật lệ trung thiên' dựa trên việc Thái Dương ở Ngọ.",
  "gold_context_spans": [
    {
      "doc_id": "TVGM",
      "section_id": "TVGM_P195_195_SEC01",
      "span_id": "TVGM_P195_195_SEC01_SP01",
      "page_pdf": 195,
      "page_book": 195,
      "quote": "Thái Dương ở Ngọ gọi là Nhật lệ trung thiên.",
      "char_start": null,
      "char_end": null
    }
  ],
  "gold_chunk_ids": [],
  "required_entities": ["Thái Dương", "Mệnh", "Ngọ", "Nhật lệ trung thiên"],
  "labels": {
    "topic": "personality",
    "retrieval_eval_included": true,
    "generation_eval_included": true,
    "safety_flag": 0
  }
}
```

### Sample 3 — One-hop (tam hợp)

```json
{
  "id": "TVQA-023",
  "chart_id": "CHART-003",
  "birth_info": {
    "date_solar": "1988-03-09",
    "time": "07:15",
    "timezone": "Asia/Ho_Chi_Minh",
    "gender": "Nam"
  },
  "chart_repr": {
    "menh_position": "Tý",
    "than_position": "Thìn",
    "ban_menh": "Bích Thượng Thổ",
    "ngu_hanh_ban_menh": "Thổ",
    "cuc": "Mộc Tam Cục",
    "am_duong_nam_nu": "Dương Nam",
    "houses": []
  },
  "question": "Nếu Mệnh của lá số này nằm trong tam hợp Thái Tuế thì khí chất cơ bản nên luận ra sao?",
  "question_complexity": "One-hop",
  "gold_answer": "Theo sách, người có Mệnh ở tam hợp Thái Tuế được luận là người có lý tưởng và có tính tình ngay thẳng. Vì vậy khi trả lời câu hỏi này, hệ thống phải ưu tiên nêu hai ý đó trước.",
  "expected_answer_summary": "Phải nêu được hai ý chính: có lý tưởng, tính tình ngay thẳng.",
  "gold_context_spans": [
    {
      "doc_id": "TVGM",
      "section_id": "TVGM_P044_044_SEC01",
      "span_id": "TVGM_P044_044_SEC01_SP01",
      "page_pdf": 44,
      "page_book": 44,
      "quote": "Mệnh ở tam hợp Thái Tuế... là người có lý tưởng, có tính tình ngay thẳng.",
      "char_start": null,
      "char_end": null
    }
  ],
  "gold_chunk_ids": [],
  "required_entities": ["Mệnh", "tam hợp Thái Tuế"],
  "labels": {
    "topic": "personality",
    "retrieval_eval_included": true,
    "generation_eval_included": true,
    "safety_flag": 0
  }
}
```

### Sample 4 — Two-hop (đa cung)

```json
{
  "id": "TVQA-046",
  "chart_id": "CHART-005",
  "birth_info": {
    "date_solar": "1994-12-02",
    "time": "13:20",
    "timezone": "Asia/Ho_Chi_Minh",
    "gender": "Nữ"
  },
  "chart_repr": {
    "menh_position": "Dần",
    "than_position": "Thân",
    "ban_menh": "Đại Lâm Mộc",
    "ngu_hanh_ban_menh": "Mộc",
    "cuc": "Thổ Ngũ Cục",
    "am_duong_nam_nu": "Âm Nữ",
    "houses": [
      {
        "house_index": 3,
        "earthly_branch": "Dần",
        "house_name": "Mệnh",
        "is_menh_resident": true,
        "is_than_resident": false,
        "house_element": "Mộc",
        "yin_yang": "Dương",
        "dai_han_age": 15,
        "tieu_han_branch": "Tuất",
        "major_stars": [],
        "aux_stars": [
          {"name": "Địa Kiếp"},
          {"name": "Địa Không"}
        ]
      },
      {
        "house_index": 9,
        "earthly_branch": "Thân",
        "house_name": "Tài Bạch",
        "is_menh_resident": false,
        "is_than_resident": true,
        "house_element": "Kim",
        "yin_yang": "Dương",
        "dai_han_age": 75,
        "tieu_han_branch": "Thân",
        "major_stars": [],
        "aux_stars": [
          {"name": "Hóa Lộc"}
        ]
      }
    ]
  },
  "question": "Mệnh có Không Kiếp, Tài Bạch có Hóa Lộc thì xu hướng kiếm tiền của lá số này nên luận ra sao?",
  "question_complexity": "Two-hop",
  "gold_answer": "Khi luận xu hướng kiếm tiền cho lá số này, cần kết hợp hai lớp: (1) Mệnh có Không Kiếp thể hiện khuynh hướng không quá trọng vật chất hoặc dễ thất tán; (2) Tài Bạch có Hóa Lộc cho thấy vẫn có cơ hội phát tài hoặc nguồn lộc. Hai lớp này không mâu thuẫn mà bổ sung: người có thể kiếm được nhưng không chắc giữ được lâu, hoặc dùng tiền vào mục đích tinh thần nhiều hơn hưởng thụ vật chất.",
  "expected_answer_summary": "Phải kết hợp đúng hai lớp nghĩa: Không Kiếp = thất tán/không quá trọng vật chất; Hóa Lộc = có nguồn phúc lộc. Không kết luận đơn giản là giàu hay nghèo.",
  "gold_context_spans": [
    {
      "doc_id": "TVGM",
      "section_id": "TVGM_P089_089_SEC02",
      "span_id": "TVGM_P089_089_SEC02_SP01",
      "page_pdf": 89,
      "page_book": 89,
      "quote": "Mệnh có Không Kiếp... thể hiện khuynh hướng không quá trọng vật chất, hay tiêu tán tài lộc.",
      "char_start": null,
      "char_end": null
    },
    {
      "doc_id": "TVNL",
      "section_id": "TVNL_P156_156_SEC03",
      "span_id": "TVNL_P156_156_SEC03_SP01",
      "page_pdf": 156,
      "page_book": 156,
      "quote": "Hóa Lộc tại Tài Bạch là dấu hiệu có nguồn phúc lộc, điều kiện vật chất ổn định.",
      "char_start": null,
      "char_end": null
    }
  ],
  "gold_chunk_ids": [],
  "required_entities": ["Mệnh", "Địa Kiếp", "Địa Không", "Tài Bạch", "Hóa Lộc"],
  "labels": {
    "topic": "wealth",
    "retrieval_eval_included": true,
    "generation_eval_included": true,
    "safety_flag": 0
  }
}
```

### Sample 5 — Two-hop (đa cung + đa nguồn)

```json
{
  "id": "TVQA-078",
  "chart_id": "CHART-008",
  "birth_info": {
    "date_solar": "1985-08-17",
    "time": "16:45",
    "timezone": "Asia/Ho_Chi_Minh",
    "gender": "Nam"
  },
  "chart_repr": {
    "menh_position": "Tỵ",
    "than_position": "Dậu",
    "ban_menh": "Phúc Đăng Hỏa",
    "ngu_hanh_ban_menh": "Hỏa",
    "cuc": "Kim Tứ Cục",
    "am_duong_nam_nu": "Âm Nam",
    "houses": [
      {
        "house_index": 6,
        "earthly_branch": "Tỵ",
        "house_name": "Mệnh",
        "is_menh_resident": true,
        "is_than_resident": false,
        "house_element": "Hỏa",
        "yin_yang": "Âm",
        "dai_han_age": 45,
        "tieu_han_branch": "Ngọ",
        "major_stars": [
          {"name": "Thiên Lương", "status": "Miếu"}
        ],
        "aux_stars": []
      },
      {
        "house_index": 5,
        "earthly_branch": "Thìn",
        "house_name": "Quan Lộc",
        "is_menh_resident": false,
        "is_than_resident": false,
        "house_element": "Thổ",
        "yin_yang": "Dương",
        "dai_han_age": 35,
        "tieu_han_branch": "Tỵ",
        "major_stars": [],
        "aux_stars": [
          {"name": "Lộc Tồn"},
          {"name": "Thiên Mã"}
        ]
      }
    ]
  },
  "question": "Mệnh có Thiên Lương Miếu, Quan Lộc có Lộc Tồn và Thiên Mã; khi luận công danh sự nghiệp nên ưu tiên kết hợp các lớp nghĩa nào?",
  "question_complexity": "Two-hop",
  "gold_answer": "Khi luận công danh sự nghiệp cho lá số này, cần kết hợp: (1) Thiên Lương Miếu tại Mệnh thể hiện tư chất thanh cao, có uy tín, thường làm công việc văn chức hoặc tư vấn; (2) Lộc Tồn tại Quan Lộc cho thấy phần hưởng và địa vị ổn định; (3) Thiên Mã tại Quan Lộc cho thấy vận động nhiều, có thể thay đổi môi trường làm việc hoặc di chuyển công tác. Tổng hợp: người này có uy tín và chuyên môn tốt, địa vị ổn định nhưng vẫn năng động trong công việc.",
  "expected_answer_summary": "Phải kết hợp đúng 3 lớp: Thiên Lương Miếu = tư chất thanh cao/uy tín; Lộc Tồn = phần hưởng/địa vị; Thiên Mã = vận động/di chuyển.",
  "gold_context_spans": [
    {
      "doc_id": "TVHS",
      "section_id": "TVHS_P127_127_SEC01",
      "span_id": "TVHS_P127_127_SEC01_SP01",
      "page_pdf": 127,
      "page_book": 127,
      "quote": "Thiên Lương Miếu thể hiện người có tư chất thanh cao, uy tín, thường làm công việc liên quan đến văn chức, tư vấn, giảng dạy.",
      "char_start": null,
      "char_end": null
    },
    {
      "doc_id": "TVNL",
      "section_id": "TVNL_P203_203_SEC02",
      "span_id": "TVNL_P203_203_SEC02_SP01",
      "page_pdf": 203,
      "page_book": 203,
      "quote": "Lộc Tồn tại Quan Lộc là dấu hiệu địa vị ổn định, có phần hưởng trong công danh.",
      "char_start": null,
      "char_end": null
    },
    {
      "doc_id": "TVKL",
      "section_id": "TVKL_P112_112_SEC01",
      "span_id": "TVKL_P112_112_SEC01_SP01",
      "page_pdf": 112,
      "page_book": 112,
      "quote": "Thiên Mã tại Quan Lộc cho thấy vận động nhiều trong công việc, có thể di chuyển công tác hoặc thay đổi môi trường.",
      "char_start": null,
      "char_end": null
    }
  ],
  "gold_chunk_ids": [],
  "required_entities": ["Mệnh", "Thiên Lương", "Quan Lộc", "Lộc Tồn", "Thiên Mã"],
  "labels": {
    "topic": "career",
    "retrieval_eval_included": true,
    "generation_eval_included": true,
    "safety_flag": 0
  }
}
```

---

## 11. CHECKLIST CHẤT LƯỢNG TRƯỚC KHI KHÓA SAMPLE

Mỗi sample chỉ được đánh dấu hoàn thành khi đạt đủ:

- [ ] Câu hỏi đúng loại (Direct / One-hop / Two-hop)
- [ ] Có `chart_id` hợp lệ
- [ ] Có `birth_info` đầy đủ
- [ ] Có `chart_repr` chuẩn hóa
- [ ] Có `required_entities` đầy đủ
- [ ] Có `expected_answer_summary` rõ ràng
- [ ] Với One-hop / Two-hop: có `gold_context_spans` với quote thật
- [ ] Quote là **nguyên văn chính xác** từ sách
- [ ] Có `doc_id`, `section_id`, `span_id`, `page_pdf` đầy đủ
- [ ] Không có phrase bịa ngoài evidence
- [ ] `gold_answer` bám sát chart + gold spans
- [ ] Reviewer khác author đã verify
- [ ] Với Direct: `gold_context_spans = []` và `retrieval_eval_included = false`

---

## 12. KẾT LUẬN VÀ KHUYẾN NGHỊ THỰC THI

### 12.1. Format tốt nhất
- **Canonical**: JSONL (1 line = 1 sample)
- **Evidence**: tách rõ chart facts và book quotes
- **Ground truth retrieval**: dùng `span_id` + `doc_id` + `page`

### 12.2. Quy trình tốt nhất
- 10 chart đa dạng
- Mỗi chart 10 câu: 1 Direct + 4 One-hop + 5 Two-hop
- LLM generate candidate → Human trích evidence thật → Human khác verify → Lead adjudicate

### 12.3. Điểm quan trọng nhất
**ĐỪNG ĐỂ LLM TỰ BỊA `gold_context_spans`**

Mọi `quote` phải do human copy từ nguồn thật. Đây là điểm then chốt để dataset có chất lượng.

### 12.4. Timeline thực thi đề xuất

| Phase | Thời gian | Deliverable |
|---|---|---|
| Phase 0 | 1 ngày | Chuẩn hóa 4 sách PDF → corpus cleaned |
| Phase 1 | 2 ngày | Chọn 10 chart + export JSON |
| Phase 2 | 5 ngày | LLM draft 100 questions + Human chọn/sửa |
| Phase 3 | 7 ngày | Human trích gold spans + verify |
| Phase 4 | 2 ngày | Cross review + adjudication |
| Phase 5 | 1 ngày | Post-processing: map chunk_ids |
| Phase 6 | 1 ngày | Validation run + export release |
| **Total** | **~19 ngày** | **golden_v1_release.jsonl** |

### 12.5. Checklist triển khai

- [ ] Chuẩn bị 4 sách PDF → corpus cleaned với doc_id chuẩn
- [ ] Tạo taxonomy sao chính tinh/phụ tinh
- [ ] Viết script chuẩn hóa chart từ engine output
- [ ] Chọn 10 chart đa dạng → freeze JSON
- [ ] Setup LLM prompts A, B, C, D
- [ ] Phân công 4 annotators (25 samples/người)
- [ ] Chạy Phase 2-3: sinh câu hỏi + trích evidence
- [ ] Cross review 20% samples
- [ ] Adjudication conflicts
- [ ] Map gold spans → chunk_ids
- [ ] Validation run với pipeline hiện tại
- [ ] Export `golden_v1_release.jsonl`
- [ ] Document release notes + known limitations

---

**Tài liệu này là phiên bản cuối cùng sau khi rà soát toàn bộ feedback. Mọi thành viên nhóm nên tuân thủ đúng schema và quy trình để đảm bảo chất lượng dataset benchmark.**
