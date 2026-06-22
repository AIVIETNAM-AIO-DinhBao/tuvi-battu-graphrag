# Giải thích chi tiết `schema_release.json` và `schema_ops.json`
**Phạm vi:** Golden Dataset QA 100 câu cho benchmark RAG Tử Vi  
**Mục đích file này:** Làm rõ thật kỹ ý nghĩa 2 schema, cách sinh từng field, ai là người điền field đó, field nào do script sinh, field nào do LLM gợi ý, field nào do human quyết định; đồng thời đưa ra ví dụ đầy đủ cho 3 loại sample: Direct / One-hop / Two-hop. File này là tài liệu “định hướng thao tác” để cả team làm đồng nhất, không hiểu sai giữa plan, guideline và dữ liệu thực tế. [schema_release.json](https://www.genspark.ai/api/files/s/seXZhhes) [schema_ops.json](https://www.genspark.ai/api/files/s/PwfQI55a) [Guideline benchmark](https://www.genspark.ai/api/files/s/fvJx9CFu)

---

# 1. Hai schema này dùng để làm gì?

## 1.1. `schema_release.json`
`schema_release.json` là **schema của bản dataset phát hành chính thức**. Đây là file mà về sau pipeline benchmark, evaluator, RAGAS script, retrieval evaluation script hoặc người review ngoài team sẽ dùng. Vì vậy schema này phải **gọn, ổn định, ít metadata nội bộ**, và chỉ giữ những trường thực sự cần để chấm retrieval + generation. [schema_release.json](https://www.genspark.ai/api/files/s/seXZhhes)

Nói ngắn gọn:  
- `schema_release.json` = **dữ liệu công bố / dữ liệu benchmark chính thức**  
- mục tiêu của nó là: **chấm được**, **dùng được**, **ít mơ hồ**, **không lẫn workflow nội bộ**. [schema_release.json](https://www.genspark.ai/api/files/s/seXZhhes)

---

## 1.2. `schema_ops.json`
`schema_ops.json` là **schema metadata nội bộ phục vụ workflow làm dataset**. Nó không phải trọng tâm của benchmark runner, mà là trọng tâm của **quy trình tạo dataset**: ai tạo sample, reviewer là ai, sample đang ở trạng thái nào, câu trả lời cần có những ý nào, không được bịa gì, mức độ khó ra sao. [schema_ops.json](https://www.genspark.ai/api/files/s/PwfQI55a)

Nói ngắn gọn:  
- `schema_ops.json` = **dữ liệu vận hành nội bộ**  
- mục tiêu của nó là: **quản lý chất lượng**, **review**, **adjudication**, **truy vết lý do vì sao sample được viết như vậy**. [schema_ops.json](https://www.genspark.ai/api/files/s/PwfQI55a)

---

## 1.3. Một sample hoàn chỉnh trên thực tế sẽ có 2 lớp dữ liệu
Trong quá trình làm việc, một sample tốt nhất nên tồn tại ở **2 lớp song song**:

1. **Release object**  
   Dùng cho benchmark thật.
2. **Ops object**  
   Dùng để cả team tạo, sửa, review, khóa sample.

Tức là cùng `id = TVQA-042`, các bạn có thể có:
- một record trong `golden_v1_release.jsonl`
- một record trong `golden_v1_ops.jsonl`

Hai record này phải liên kết bằng cùng `id`. [schema_release.json](https://www.genspark.ai/api/files/s/seXZhhes) [schema_ops.json](https://www.genspark.ai/api/files/s/PwfQI55a)

---

# 2. Vị trí của 2 schema trong toàn bộ pipeline làm dataset

## 2.1. Pipeline tổng quát
Quy trình thực tế nên hiểu như sau:

```text
PDF thô
→ extract text
→ clean / section hóa corpus
→ chọn 10 chart
→ thiết kế 100 slot câu hỏi
→ LLM gợi ý câu hỏi
→ Human chốt câu hỏi
→ Human chọn gold_context_spans từ corpus
→ LLM draft answer từ chart + spans
→ Human viết gold_answer cuối
→ Reviewer kiểm
→ map spans → chunk_ids
→ xuất release dataset
```

Trong pipeline này:
- `schema_release.json` được dùng mạnh nhất ở **2 bước cuối**: khi sample gần hoàn chỉnh và khi export release.
- `schema_ops.json` được dùng mạnh nhất ở **các bước giữa**: lúc con người đang tạo sample, chỉnh answer, review, adjudicate. [Guideline benchmark](https://www.genspark.ai/api/files/s/fvJx9CFu)

---

## 2.2. Ai chạm vào schema nào?
- **A (lead)**: chạm cả 2 schema, nhưng đặc biệt chịu trách nhiệm chốt `schema_release`.
- **B/C annotator**: dùng nhiều `schema_ops`, rồi sau đó xuất sang `schema_release`.
- **C/dev/tooling**: dùng `schema_release` để validate JSONL, dùng `schema_ops` để hỗ trợ workflow nếu cần. 

---

# 3. Giải thích chi tiết `schema_release.json`

## 3.1. Toàn văn tinh thần của schema release
Schema release hiện tại yêu cầu các trường bắt buộc:

- `id`
- `chart_id`
- `birth_info`
- `chart_repr`
- `question`
- `question_complexity`
- `gold_answer`
- `expected_answer_summary`
- `gold_context_spans`
- `gold_chunk_ids`
- `required_entities`
- `labels`

Đây là thiết kế hợp lý vì nó tách được:
- **input chart**
- **câu hỏi**
- **đáp án chuẩn**
- **ground truth retrieval**
- **thực thể bắt buộc**
- **nhãn phục vụ benchmark** [schema_release.json](https://www.genspark.ai/api/files/s/seXZhhes)

---

## 3.2. Giải thích từng field của release schema

## 3.2.1. `id`
### Ý nghĩa
Mã định danh duy nhất cho sample QA.

### Ví dụ
- `TVQA-001`
- `TVQA-057`
- `TVQA-100`

### Ai tạo?
- **Human / lead** quyết định convention
- thường được generate bán tự động từ slot matrix

### Lấy ở bước nào?
- tạo ngay sau khi freeze `question_slots.csv`

### Quy tắc nên dùng
```text
TVQA-001 ... TVQA-100
```

### Không nên
- `Q1`
- `sample_1`
- `chart1_question1`
vì khó quản lý khi merge/review.

---

## 3.2.2. `chart_id`
### Ý nghĩa
ID lá số mà câu hỏi này đang dựa vào.

### Ví dụ
- `CHART-001`
- `CHART-006`

### Ai tạo?
- **Human/dev phối hợp**
- chart registry được lead chốt trước

### Lấy ở bước nào?
- sau khi export và freeze 10 chart

### Nguồn của field này
- `chart_registry.json`

### Ghi chú
Một `chart_id` sẽ lặp lại ở 10 sample khác nhau, vì mỗi chart sinh 10 câu.

---

## 3.2.3. `birth_info`
### Ý nghĩa
Thông tin đầu vào sinh lá số.

### Cấu trúc hiện tại
- `date_solar`
- `time`
- `timezone`
- `gender` [schema_release.json](https://www.genspark.ai/api/files/s/seXZhhes)

### Ví dụ
```json
"birth_info": {
  "date_solar": "1990-10-15",
  "time": "09:00",
  "timezone": "Asia/Ho_Chi_Minh",
  "gender": "Nam"
}
```

### Ai tạo?
- **dev/script** lấy từ input chart
- **human** review lại

### Lấy ở bước nào?
- lúc export chart từ engine

### Nguồn của field này
- input thực tế đưa vào engine
- hoặc record chart đã lưu

### Lưu ý
Vì benchmark này là **Tử Vi**, `birth_info` giúp:
- trace lại chart
- tái tạo chart nếu cần
- audit khi nghi chart sai

---

## 3.2.4. `chart_repr`
### Ý nghĩa
Biểu diễn rút gọn của lá số để dùng cho benchmark và RAG.

### Vì sao cần?
Vì câu trả lời không chỉ dựa vào sách, mà còn dựa vào chính lá số. Do đó benchmark release phải mang theo **chart context tối thiểu cần thiết**. [Guideline benchmark](https://www.genspark.ai/api/files/s/fvJx9CFu)

### Hiện schema ghi gì?
Hiện tại chỉ ghi:
```json
"chart_repr": { "type": "object" }
```
Tức là schema chưa ép chi tiết bên trong. [schema_release.json](https://www.genspark.ai/api/files/s/seXZhhes)

### Điều này có nghĩa gì?
- Ưu: linh hoạt
- Nhược: nếu team không thống nhất nội bộ thì mỗi chart có thể ghi khác kiểu

### Khuyến nghị nội bộ bắt buộc
Ít nhất `chart_repr` phải có:
- `menh_position`
- `than_position`
- `ban_menh`
- `ngu_hanh_ban_menh`
- `cuc`
- `am_duong_nam_nu`
- `houses` (đủ 12 cung)
- mỗi cung có:
  - `house_name`
  - `earthly_branch`
  - `major_stars`
  - `aux_stars` [Guideline benchmark](https://www.genspark.ai/api/files/s/fvJx9CFu)

### Ai tạo?
- **C/dev** export từ engine
- **A** chuẩn hóa và freeze
- **B/C** không tự ý đổi format sau khi freeze

### Nguồn
- chart JSON sinh ra từ engine Tử Vi
- sau đó normalize

---

## 3.2.5. `question`
### Ý nghĩa
Câu hỏi benchmark cuối cùng mà hệ thống RAG phải trả lời.

### Ai tạo?
- **LLM** có thể gợi ý nháp
- **Human annotator** phải chọn/chỉnh/chốt câu cuối

### Không được làm gì?
- không copy nguyên xi câu mơ hồ của LLM nếu chưa review
- không hỏi quá rộng kiểu “luận cả cuộc đời”
- không hỏi sang Bát Tự

### Bước tạo
1. slot matrix xác định loại câu
2. LLM sinh 2–3 candidate
3. human chọn 1 câu tốt nhất
4. human rewrite nhẹ cho tự nhiên nếu cần

---

## 3.2.6. `question_complexity`
### Ý nghĩa
Nhãn loại câu hỏi:
- `Direct`
- `One-hop`
- `Two-hop` [schema_release.json](https://www.genspark.ai/api/files/s/seXZhhes)

### Ai gán?
- **Human**
- không để LLM tự quyết cuối cùng

### Gán ở bước nào?
- gán từ `question_slots.csv` trước cả khi viết question final

### Rule rất quan trọng
- `Direct`: trả lời từ chart, không cần sách
- `One-hop`: chart + 1 rule từ sách
- `Two-hop`: ít nhất 2 bước reasoning, thường đa cung / đa sao / đa span [Guideline benchmark](https://www.genspark.ai/api/files/s/fvJx9CFu)

---

## 3.2.7. `gold_answer`
### Ý nghĩa
Câu trả lời chuẩn cuối cùng.

### Ai tạo?
- **LLM có thể draft**
- **Human phải viết/chỉnh và chịu trách nhiệm cuối**

### Nguồn để viết
- `chart_repr`
- `gold_context_spans`
- không dùng trí nhớ ngoài của annotator
- không thêm kiến thức không có trong source

### Mục tiêu
- answer này sẽ là chuẩn để so sánh generation

### Lưu ý
Đây là field quan trọng nhất của generation benchmark.

---

## 3.2.8. `expected_answer_summary`
### Ý nghĩa
Bản tóm tắt ngắn các ý cốt lõi mà câu trả lời chuẩn phải có.

### Vai trò
- giúp chấm nhanh correctness
- giúp reviewer hiểu “ý chính bắt buộc”
- hỗ trợ LLM judge hoặc human judge

### Ví dụ tốt
```json
"expected_answer_summary": "Phải nêu đúng Mệnh ở Tuất, khi luận phải xét thêm hai cung Dần và Ngọ theo tam hợp."
```

### Không nên
- viết dài ngang `gold_answer`
- biến nó thành một answer thứ hai

### Ai tạo?
- Human viết
- LLM có thể draft

---

## 3.2.9. `gold_context_spans`
### Ý nghĩa
Ground truth retrieval ở cấp trích đoạn văn bản.

### Đây là field cốt lõi cho retrieval benchmark
Nó cho biết:
- lấy từ sách nào
- section nào
- span nào
- trang nào
- quote chính xác là gì [schema_release.json](https://www.genspark.ai/api/files/s/seXZhhes)

### Cấu trúc hiện tại trong schema
Mỗi item có:
- `doc_id`
- `section_id`
- `span_id`
- `page_pdf`
- `page_book`
- `quote` [schema_release.json](https://www.genspark.ai/api/files/s/seXZhhes)

### Ai tạo?
- **Human annotator** bắt buộc phải chọn
- LLM chỉ được gợi ý nơi cần tìm, không được bịa quote

### Lấy ở bước nào?
- sau khi đã có `question`
- sau khi đã có `corpus cleaned` / `sections.jsonl`

### Nguồn để điền
- từ `*_sections.jsonl`
- hoặc `*_clean.md` để đọc, rồi quay về `sections.jsonl` để cắt span chính xác

### Rule quan trọng
- One-hop / Two-hop: gần như luôn phải có 1–3 span
- Direct: có thể để `[]` nếu câu chỉ cần chart

### Lưu ý kỹ thuật quan trọng
Schema hiện tại ghi `page_book` là integer, nhưng trong file raw hiện tại `page_book` đang có `null`. Vì vậy lúc validate hoặc lúc hoàn thiện schema v1.1, team nên cân nhắc sửa:
```json
"page_book": { "type": ["integer", "null"] }
```
vì dữ liệu thực tế đang cho thấy `page_book` chưa phải lúc nào cũng có. [schema_release.json](https://www.genspark.ai/api/files/s/seXZhhes) [TVGM_raw_pages.json](https://www.genspark.ai/api/files/s/pZ31EmCY)

---

## 3.2.10. `gold_chunk_ids`
### Ý nghĩa
Danh sách chunk IDs tương ứng với các `gold_context_spans` sau khi đã chạy chunking.

### Rất quan trọng phải hiểu đúng
- `gold_context_spans` = ground truth gốc
- `gold_chunk_ids` = ground truth sau khi map qua chunking implementation

Tức là annotator **không điền tay field này từ đầu**. Field này thường do:
- script map span → chunk overlap
- hoặc dev tạo ở bước hậu xử lý

### Ai tạo?
- **C/dev/script**
- human chỉ review nếu có gì bất thường

### Direct sample thì sao?
Có thể:
```json
"gold_chunk_ids": []
```
nếu sample đó không dùng retrieval sách.

---

## 3.2.11. `required_entities`
### Ý nghĩa
Danh sách các thực thể bắt buộc hệ phải nhận diện hoặc không được bỏ sót.

### Ví dụ
- `["Mệnh", "Tuất", "Dần", "Ngọ", "tam hợp"]`
- `["Thái Dương", "Ngọ", "Nhật lệ trung thiên"]`

### Vai trò
- hỗ trợ Graph Hit Rate
- giúp kiểm tra retrieval có bắt đúng node/edge/sao/cung không
- giúp reviewer hiểu sample đang test cái gì

### Ai tạo?
- human quyết định
- LLM có thể gợi ý

### Rule
Field này phải **ngắn nhưng sắc**, không nhét tất cả từ khóa có thể nghĩ ra.

---

## 3.2.12. `labels`
### Ý nghĩa
Nhóm nhãn phụ phục vụ benchmark.

### Schema hiện tại
Hiện `labels` mới chỉ được khai báo là một object chung, chưa ép chi tiết bên trong. [schema_release.json](https://www.genspark.ai/api/files/s/seXZhhes)

### Khuyến nghị nội bộ tối thiểu
```json
"labels": {
  "topic": "career",
  "retrieval_eval_included": true,
  "generation_eval_included": true,
  "safety_flag": 0
}
```

### Ý nghĩa từng trường khuyến nghị
- `topic`: chủ đề chính
- `retrieval_eval_included`: có dùng sample này để chấm retrieval không
- `generation_eval_included`: có dùng sample này để chấm generation không
- `safety_flag`: câu có nhạy cảm không

### Ai tạo?
- topic: human
- retrieval/generation flags: lead hoặc annotator theo rule
- safety flag: human review

---

# 4. Giải thích chi tiết `schema_ops.json`

## 4.1. Tinh thần của ops schema
Schema này không phải để release, mà để **quản lý sample trong quá trình tạo**. Nếu release schema trả lời câu hỏi “benchmark cần gì để chạy?”, thì ops schema trả lời câu hỏi “team cần gì để làm đúng và review đúng?”. [schema_ops.json](https://www.genspark.ai/api/files/s/PwfQI55a)

---

## 4.2. Giải thích từng field của ops schema

## 4.2.1. `expected_answer_points`
### Ý nghĩa
Checklist các ý bắt buộc phải có trong `gold_answer`.

### Đây không phải answer
Nó là “khung chấm”.

### Ví dụ
```json
[
  "xác định đúng Mệnh ở Tuất",
  "nêu đúng hai cung tam hợp cần xét là Dần và Ngọ",
  "không mở rộng sang cung khác nếu câu hỏi chưa hỏi"
]
```

### Ai tạo?
- human annotator viết
- LLM có thể giúp draft

### Dùng khi nào?
- lúc primary edit
- lúc cross-review
- lúc adjudicate

### Có nên đưa vào release không?
Không bắt buộc. Đây là field workflow nội bộ.

---

## 4.2.2. `negative_constraints`
### Ý nghĩa
Danh sách những điều **không được nói**, **không được bịa**, **không được suy diễn**.

### Ví dụ
```json
[
  "không nhắc Bát Tự",
  "không dự đoán vận hạn nếu câu hỏi không hỏi",
  "không dùng kiến thức ngoài spans đã chọn"
]
```

### Ai tạo?
- human annotator
- lead có thể thêm rule chung

### Vì sao field này hữu ích?
Vì nhiều lỗi answer không nằm ở chỗ “thiếu ý”, mà nằm ở chỗ “thêm ý sai”.

---

## 4.2.3. `answer_rubric`
### Ý nghĩa
Mô tả ngắn cách chấm câu trả lời ở sample đó.

### Hiện schema đang để là string
```json
"answer_rubric": { "type": "string" }
```
tức là team có thể ghi một rubric ngắn dạng text. [schema_ops.json](https://www.genspark.ai/api/files/s/PwfQI55a)

### Ví dụ
```json
"answer_rubric": "Đạt nếu nêu đúng 2 cung tam hợp cần xét và giải thích được vì sao phải cộng 2 cung này khi luận cung Mệnh."
```

### Ai tạo?
- human annotator
- lead review

### Ghi chú
Nếu sau này muốn chấm máy nhiều hơn, field này có thể tách thành object. Nhưng v1 để string là chấp nhận được.

---

## 4.2.4. `annotator`
### Ý nghĩa
Thông tin ai tạo sample.

### Cấu trúc
- `author`
- `created_at` [schema_ops.json](https://www.genspark.ai/api/files/s/PwfQI55a)

### Ví dụ
```json
"annotator": {
  "author": "B",
  "created_at": "2026-06-22T14:30:00+07:00"
}
```

### Ai điền?
- có thể điền tay
- hoặc script append theo workflow

### Vai trò
- truy vết ownership
- xem sample này ai chịu trách nhiệm chính

---

## 4.2.5. `verification`
### Ý nghĩa
Thông tin review.

### Cấu trúc
- `reviewer`
- `status`
- `notes` [schema_ops.json](https://www.genspark.ai/api/files/s/PwfQI55a)

### Ví dụ
```json
"verification": {
  "reviewer": "A",
  "status": "needs_revision",
  "notes": "Span 2 chưa đủ support cho câu cuối của gold_answer."
}
```

### Ai điền?
- reviewer human

### Vai trò
- giúp adjudication dễ
- không cần mở chat/log cũ mới biết sample đang bị gì

---

## 4.2.6. `status`
### Ý nghĩa
Trạng thái lifecycle của sample.

### Enum hiện tại
- `draft`
- `verified`
- `adjudicated`
- `locked` [schema_ops.json](https://www.genspark.ai/api/files/s/PwfQI55a)

### Cách hiểu
- `draft`: sample đang làm
- `verified`: đã qua review đầu
- `adjudicated`: đã được lead xử lý tranh chấp
- `locked`: không sửa nữa, sẵn sàng export

### Ai cập nhật?
- author cập nhật từ `draft`
- reviewer / lead cập nhật các trạng thái sau

---

## 4.2.7. `difficulty`
### Ý nghĩa
Ước lượng độ khó nội bộ:
- `easy`
- `medium`
- `hard` [schema_ops.json](https://www.genspark.ai/api/files/s/PwfQI55a)

### Lưu ý
Đây không phải field bắt buộc cho benchmark release, nhưng hữu ích để:
- phân workload
- phân tích lỗi
- thống kê sau này

### Ai gán?
- author gán trước
- reviewer có thể sửa

---

# 5. Step-by-step: từng field được tạo ra như thế nào?

Đây là phần quan trọng nhất của tài liệu này.

---

## Bước 0 — Chuẩn bị corpus từ PDF thô
Hiện tại team mới có `raw_pages` và trong file `TVGM_raw_pages.json` đang thấy:
- đã có `doc_id`
- đã có `section_id`
- có `metadata.page_pdf`
- `page_book` đang là `null`
- `content` lại không đồng nhất: lúc là string, lúc là array, lúc là object [TVGM_raw_pages.json](https://www.genspark.ai/api/files/s/pZ31EmCY)

Điều này cho thấy file tên là `raw_pages`, nhưng về bản chất đã **nửa raw, nửa sectionized**. Nghĩa là team cần thêm một bước normalize nữa trước khi dùng ổn định:
- thống nhất `content` về text
- tách riêng metadata/title nếu cần
- đảm bảo mỗi section là một record logic
- chuẩn hóa page map [TVGM_raw_pages.json](https://www.genspark.ai/api/files/s/pZ31EmCY)

### Human hay LLM?
- **Human/dev** làm
- LLM không nên tham gia bước này trừ khi chỉ hỗ trợ phát hiện lỗi định dạng

### Output tốt nhất của bước này
- `*_clean_pages.json`
- `*_sections.jsonl`
- `*_clean.md`

---

## Bước 1 — Freeze chart pool
Từ engine Tử Vi, dev xuất 10 chart rồi normalize thành `chart_repr`.

### Human hay LLM?
- **C/dev** export
- **A** review và freeze
- LLM không tạo chart

### Field nào được sinh ở đây?
- `chart_id`
- `birth_info`
- `chart_repr`

---

## Bước 2 — Freeze question slots
Lead tạo `question_slots.csv`:
- chart nào
- câu số mấy
- Direct / One-hop / Two-hop
- topic gì

### Human hay LLM?
- **A** quyết định
- LLM không quyết định cuối

### Field nào được sinh ở đây?
- `id`
- `chart_id`
- `question_complexity`
- `labels.topic` (bản đầu)

---

## Bước 3 — LLM gợi ý câu hỏi
LLM nhận:
- chart_repr
- question_complexity
- topic

LLM sinh 2–3 candidate questions.

### Human hay LLM?
- **LLM draft**
- **Human chọn và sửa**

### Field nào được sinh ở đây?
- `question` (draft)
- `required_entities` (draft gợi ý)

### Human phải làm gì?
- chọn 1 câu tốt nhất
- bỏ câu quá rộng
- sửa câu cho tự nhiên
- chốt `required_entities`

---

## Bước 4 — Human chọn gold_context_spans
Annotator mở corpus cleaned/sections và chọn exact spans.

### Human hay LLM?
- **Human bắt buộc**
- LLM chỉ được gợi ý nên mở sách nào / section nào

### Field nào được sinh ở đây?
- `gold_context_spans`

### Đây là bước quan trọng nhất để chống bias
Vì nếu để LLM tự trích quote thì rất dễ:
- quote sai
- quote paraphrase
- quote ghép từ nhiều nơi mà không nói rõ

---

## Bước 5 — LLM draft answer từ chart + spans
Khi đã có:
- `chart_repr`
- `question`
- `gold_context_spans`

LLM mới được phép draft answer.

### Human hay LLM?
- **LLM draft**
- **Human chỉnh final**

### Field nào được sinh ở đây?
- `gold_answer` (draft)
- `expected_answer_summary` (draft)
- `expected_answer_points` (draft trong ops)
- `negative_constraints` (draft trong ops)
- `answer_rubric` (draft trong ops)

---

## Bước 6 — Human finalize answer
Annotator viết lại hoặc chỉnh answer để đảm bảo:
- grounded
- đúng trọng tâm
- không bịa
- tone an toàn

### Human hay LLM?
- **Human final**
- reviewer sẽ kiểm lần nữa

### Field nào chốt ở đây?
- `gold_answer`
- `expected_answer_summary`
- `expected_answer_points`
- `negative_constraints`
- `answer_rubric`

---

## Bước 7 — Review / verification
Reviewer đọc sample và quyết:
- hỗ trợ đủ chưa
- có câu nào vượt source không
- có thiếu entity quan trọng không

### Human hay LLM?
- **Human reviewer**

### Field nào được điền?
- `verification`
- `status`
- có thể chỉnh `difficulty`

---

## Bước 8 — Chunk mapping
Sau khi retrieval chunking được freeze, script map `gold_context_spans` sang `gold_chunk_ids`.

### Human hay LLM?
- **Dev/script**
- human chỉ audit khi cần

### Field nào được sinh?
- `gold_chunk_ids`

---

## Bước 9 — Export release
Khi sample `locked`, release exporter sẽ lấy các field từ bản ops + bản release draft và ghi ra `golden_v1_release.jsonl`.

### Human hay LLM?
- **A / script**

### Export những gì?
- chỉ field của release schema
- không export metadata nội bộ thừa

---

# 6. Lưu ý rất quan trọng về file `TVGM_raw_pages.json` hiện tại

File `TVGM_raw_pages.json` hiện bạn upload thực ra **không còn là “raw page” theo nghĩa thuần túy nữa**. Nó đã chứa:
- `section_id`
- metadata trang
- nội dung ở nhiều kiểu dữ liệu khác nhau (`string`, `array`, `object`) [TVGM_raw_pages.json](https://www.genspark.ai/api/files/s/pZ31EmCY)

Điều này dẫn đến 3 hệ quả:

## 6.1. Không nên dùng trực tiếp file này làm corpus annotation cuối
Vì `content` không đồng nhất nên:
- script tìm quote sẽ khó
- annotator mỗi người có thể copy khác kiểu
- parser downstream dễ lỗi [TVGM_raw_pages.json](https://www.genspark.ai/api/files/s/pZ31EmCY)

## 6.2. Nên chuẩn hóa thành một schema sections thống nhất
Khuyến nghị target schema trung gian:

```json
{
  "doc_id": "TVGM",
  "section_id": "TVGM_P7_7_SEC07",
  "metadata": {
    "page_pdf_start": 7,
    "page_pdf_end": 7,
    "page_book_start": null,
    "page_book_end": null,
    "title": "Các tam hợp"
  },
  "content_text": "Mỗi tam hợp có một hành ...",
  "content_raw_type": "string"
}
```

## 6.3. `page_book` hiện đang null nhiều chỗ
Do đó release schema nếu giữ `page_book` thì nên cho phép `null`, ít nhất trong giai đoạn đầu. [TVGM_raw_pages.json](https://www.genspark.ai/api/files/s/pZ31EmCY) [schema_release.json](https://www.genspark.ai/api/files/s/seXZhhes)

---

# 7. Ví dụ cực cụ thể cho 3 loại sample

> **Lưu ý quan trọng:**  
> Các ví dụ dưới đây được dùng để giải thích schema và workflow.  
> Vì hiện tại team mới có `raw_pages`/section thô, một số chỗ mình sẽ dùng nội dung từ `TVGM_raw_pages.json` làm evidence minh họa. Các `gold_chunk_ids` ở ví dụ dưới là **giả định minh họa** vì bước chunk mapping chưa chạy thật. [TVGM_raw_pages.json](https://www.genspark.ai/api/files/s/pZ31EmCY)

---

# 7.1. Ví dụ 1 — Direct

## 7.1.1. Ý nghĩa của Direct
Direct = câu trả lời lấy trực tiếp từ chart, **không cần** trích sách. Vì vậy:
- `gold_context_spans` có thể để `[]`
- `gold_chunk_ids` có thể để `[]`
- `retrieval_eval_included` thường là `false` [Guideline benchmark](https://www.genspark.ai/api/files/s/fvJx9CFu)

## 7.1.2. Release object mẫu
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
        "house_name": "Mệnh",
        "earthly_branch": "Thìn",
        "major_stars": [
          { "name": "Thái Dương", "status": "Vượng" }
        ],
        "aux_stars": [
          { "name": "Hóa Lộc" },
          { "name": "Địa Kiếp", "status": "Hãm" }
        ]
      }
    ]
  },
  "question": "Cung Mệnh của lá số này nằm ở đâu và có chính tinh nào?",
  "question_complexity": "Direct",
  "gold_answer": "Cung Mệnh của lá số này nằm tại Thìn và chính tinh nổi bật trong cung Mệnh là Thái Dương ở trạng thái Vượng.",
  "expected_answer_summary": "Phải nêu đúng Mệnh ở Thìn và chính tinh là Thái Dương (Vượng).",
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

## 7.1.3. Ops object mẫu
```json
{
  "expected_answer_points": [
    "xác định đúng vị trí cung Mệnh",
    "nêu đúng chính tinh trong cung Mệnh",
    "nếu có trạng thái sao thì nêu đúng"
  ],
  "negative_constraints": [
    "không thêm luận giải tính cách",
    "không mở rộng sang cung khác",
    "không viện dẫn sách khi câu hỏi chỉ hỏi fact chart"
  ],
  "answer_rubric": "Đạt nếu nêu đúng vị trí Mệnh và đúng chính tinh. Không cần thêm diễn giải sách.",
  "annotator": {
    "author": "A",
    "created_at": "2026-06-22T10:30:00+07:00"
  },
  "verification": {
    "reviewer": "B",
    "status": "verified",
    "notes": "Sample chart-only, không cần evidence từ sách."
  },
  "status": "locked",
  "difficulty": "easy"
}
```

## 7.1.4. Field nào do ai tạo?
- `question`: LLM gợi ý, human chốt
- `gold_answer`: human viết từ chart
- `gold_context_spans`: human để rỗng theo rule
- `required_entities`: human xác định
- `expected_answer_points`, `negative_constraints`: human viết
- `verification`: reviewer điền

---

# 7.2. Ví dụ 2 — One-hop

## 7.2.1. Ý nghĩa của One-hop
One-hop = phải kết hợp:
- 1 fact từ chart
- 1 rule từ sách

Ở đây mình dùng ví dụ từ `TVGM_raw_pages.json`, phần nói về tam hợp:  
“Nếu Mạng đóng ở Tuất, thì phải xét cả 2 cung Dần và Ngọ cũng quan trọng như Tuất.” Nội dung này đang xuất hiện trong section `TVGM_P7_7_SEC07` của file bạn upload. [TVGM_raw_pages.json](https://www.genspark.ai/api/files/s/pZ31EmCY)

## 7.2.2. Release object mẫu
```json
{
  "id": "TVQA-032",
  "chart_id": "CHART-004",
  "birth_info": {
    "date_solar": "1992-06-21",
    "time": "11:30",
    "timezone": "Asia/Ho_Chi_Minh",
    "gender": "Nữ"
  },
  "chart_repr": {
    "menh_position": "Tuất",
    "than_position": "Ngọ",
    "ban_menh": "TBD",
    "ngu_hanh_ban_menh": "TBD",
    "cuc": "TBD",
    "am_duong_nam_nu": "Âm Nữ",
    "houses": [
      {
        "house_name": "Mệnh",
        "earthly_branch": "Tuất",
        "major_stars": [],
        "aux_stars": []
      }
    ]
  },
  "question": "Nếu Mệnh đóng ở Tuất thì khi luận cần xét thêm hai cung nào trong tam hợp?",
  "question_complexity": "One-hop",
  "gold_answer": "Nếu Mệnh đóng ở Tuất thì khi luận phải xét thêm hai cung Dần và Ngọ, vì Tuất thuộc tam hợp Dần Ngọ Tuất và trong phép giải đoán phải xét cả ba cung trong tam hợp chiếu.",
  "expected_answer_summary": "Phải nêu đúng hai cung cần xét thêm là Dần và Ngọ, dựa trên quy tắc tam hợp Dần Ngọ Tuất.",
  "gold_context_spans": [
    {
      "doc_id": "TVGM",
      "section_id": "TVGM_P7_7_SEC07",
      "span_id": "TVGM_P7_7_SEC07_SP01",
      "page_pdf": 7,
      "page_book": null,
      "quote": "Trong phép giải đoán, khi xét một cung, phải xét cả 2 cung kia trong tam hợp (gọi là cung tam hợp chiếu) coi cả 3 cung như nhau. Như Mạng đóng ở Tuất, thì phải xét cả 2 Cung Dần và Ngọ cũng quan trọng như Tuất."
    }
  ],
  "gold_chunk_ids": ["TVGM_CK_000127"],
  "required_entities": ["Mệnh", "Tuất", "Dần", "Ngọ", "tam hợp"],
  "labels": {
    "topic": "personality",
    "retrieval_eval_included": true,
    "generation_eval_included": true,
    "safety_flag": 0
  }
}
```

## 7.2.3. Ops object mẫu
```json
{
  "expected_answer_points": [
    "xác định đúng Tuất thuộc tam hợp Dần Ngọ Tuất",
    "nêu đúng hai cung cần xét là Dần và Ngọ",
    "gắn câu trả lời với quy tắc giải đoán tam hợp"
  ],
  "negative_constraints": [
    "không suy diễn sang nhị hợp hay xung chiếu nếu câu hỏi chưa hỏi",
    "không thêm luận tốt/xấu của lá số",
    "không dùng nguồn ngoài quote đã chọn"
  ],
  "answer_rubric": "Đạt nếu trả lời đúng Dần và Ngọ, có nhắc logic tam hợp. Sai nếu trả lời thiếu một cung hoặc nói sang quan hệ khác.",
  "annotator": {
    "author": "B",
    "created_at": "2026-06-23T13:10:00+07:00"
  },
  "verification": {
    "reviewer": "A",
    "status": "verified",
    "notes": "Quote đủ support; answer chưa vượt source."
  },
  "status": "locked",
  "difficulty": "medium"
}
```

## 7.2.4. Field nào do ai tạo?
- `question`: LLM có thể gợi ý, human chốt
- `gold_context_spans`: human cắt từ `TVGM_P7_7_SEC07`
- `gold_answer`: LLM có thể draft, human chỉnh final
- `gold_chunk_ids`: script map sau

---

# 7.3. Ví dụ 3 — Two-hop

## 7.3.1. Ý nghĩa của Two-hop
Two-hop = cần ít nhất 2 bước reasoning hoặc 2 rule/source span trở lên.  
Ở đây mình dùng cùng chuỗi section đầu của `TVGM_raw_pages.json`:

- Page 7: quy tắc tam hợp, xét cả 2 cung trong tam hợp [TVGM_raw_pages.json](https://www.genspark.ai/api/files/s/pZ31EmCY)
- Page 9: nhị hợp có một chiều, cung được sinh nhập mới kể đến [TVGM_raw_pages.json](https://www.genspark.ai/api/files/s/pZ31EmCY)
- Page 11: xem một cung phải xem thêm cung chính chiếu [TVGM_raw_pages.json](https://www.genspark.ai/api/files/s/pZ31EmCY)

Từ đó có thể tạo câu hỏi cần kết hợp nhiều lớp quan hệ.

## 7.3.2. Release object mẫu
```json
{
  "id": "TVQA-078",
  "chart_id": "CHART-008",
  "birth_info": {
    "date_solar": "1988-03-09",
    "time": "07:15",
    "timezone": "Asia/Ho_Chi_Minh",
    "gender": "Nam"
  },
  "chart_repr": {
    "menh_position": "Tuất",
    "than_position": "Dần",
    "ban_menh": "TBD",
    "ngu_hanh_ban_menh": "TBD",
    "cuc": "TBD",
    "am_duong_nam_nu": "Dương Nam",
    "houses": [
      {
        "house_name": "Mệnh",
        "earthly_branch": "Tuất",
        "major_stars": [],
        "aux_stars": []
      }
    ]
  },
  "question": "Khi luận cung Mệnh đóng ở Tuất, ngoài hai cung tam hợp thì còn cần xét thêm những lớp quan hệ nào nữa để tránh bỏ sót thông tin?",
  "question_complexity": "Two-hop",
  "gold_answer": "Khi luận cung Mệnh ở Tuất, ngoài hai cung tam hợp là Dần và Ngọ, còn phải xét thêm quan hệ nhị hợp nếu cung đó được sinh nhập, và xét cả cung chính chiếu. Nghĩa là không chỉ dừng ở tam hợp mà phải cộng thêm các lớp quan hệ liên quan theo đúng quy tắc giải đoán của sách.",
  "expected_answer_summary": "Phải nêu ba lớp xét chính: tam hợp, nhị hợp (nếu được sinh nhập), và chính chiếu.",
  "gold_context_spans": [
    {
      "doc_id": "TVGM",
      "section_id": "TVGM_P7_7_SEC07",
      "span_id": "TVGM_P7_7_SEC07_SP01",
      "page_pdf": 7,
      "page_book": null,
      "quote": "Trong phép giải đoán, khi xét một cung, phải xét cả 2 cung kia trong tam hợp ... Như Mạng đóng ở Tuất, thì phải xét cả 2 Cung Dần và Ngọ cũng quan trọng như Tuất."
    },
    {
      "doc_id": "TVGM",
      "section_id": "TVGM_P9_9_SEC09",
      "span_id": "TVGM_P9_9_SEC09_SP01",
      "page_pdf": 9,
      "page_book": null,
      "quote": "Trong phép giải đoán, cung nào bị sinh xuất thì không kể đến nhị hợp. Cung nào được sinh nhập mới được kể đến nhị hợp. Thí dụ: Mạng Tuất, Tuất được Mão sinh nhập."
    },
    {
      "doc_id": "TVGM",
      "section_id": "TVGM_P11_11_SEC11",
      "span_id": "TVGM_P11_11_SEC11_SP01",
      "page_pdf": 11,
      "page_book": null,
      "quote": "Trong phép giải đoán, khi xem một cung, phải xem cả cung chính chiếu."
    }
  ],
  "gold_chunk_ids": ["TVGM_CK_000127", "TVGM_CK_000129", "TVGM_CK_000131"],
  "required_entities": ["Mệnh", "Tuất", "Dần", "Ngọ", "Mão", "tam hợp", "nhị hợp", "chính chiếu"],
  "labels": {
    "topic": "overview",
    "retrieval_eval_included": true,
    "generation_eval_included": true,
    "safety_flag": 0
  }
}
```

## 7.3.3. Ops object mẫu
```json
{
  "expected_answer_points": [
    "nêu được hai cung tam hợp Dần và Ngọ",
    "nêu được lớp nhị hợp chỉ tính khi sinh nhập",
    "nêu được phải xét thêm cung chính chiếu",
    "thể hiện được đây là câu hỏi đa lớp quan hệ, không phải fact đơn"
  ],
  "negative_constraints": [
    "không khẳng định một cung chính chiếu cụ thể nếu câu hỏi chưa yêu cầu nêu tên",
    "không mở rộng sang luận cát hung cụ thể khi chưa có sao/cung đầy đủ",
    "không trộn kiến thức ngoài ba span đã chọn"
  ],
  "answer_rubric": "Đạt nếu answer có đủ tam hợp + nhị hợp sinh nhập + chính chiếu. Thiếu 1 trong 3 lớp là chưa đạt.",
  "annotator": {
    "author": "C",
    "created_at": "2026-06-24T16:40:00+07:00"
  },
  "verification": {
    "reviewer": "A",
    "status": "adjudicated",
    "notes": "Giữ answer ở mức nguyên tắc, không bắt nêu đích danh cung chính chiếu để tránh overclaim."
  },
  "status": "locked",
  "difficulty": "hard"
}
```

## 7.3.4. Field nào do ai tạo?
- `question_complexity = Two-hop`: A chốt từ slot matrix
- `gold_context_spans`: human chọn 3 spans
- `gold_answer`: LLM draft từ chart + 3 spans, human rút gọn và sửa cho grounded
- `answer_rubric`: human/lead viết vì sample này dễ over-answer

---

# 8. Mapping nhanh: field nào do human, field nào do LLM, field nào do script?

| Field | Human | LLM | Script/dev | Ghi chú |
|---|---:|---:|---:|---|
| `id` | ✅ |  | ✅ | thường generate từ slot matrix |
| `chart_id` | ✅ |  | ✅ | lấy từ chart registry |
| `birth_info` | ✅ review |  | ✅ | xuất từ chart input |
| `chart_repr` | ✅ review |  | ✅ | normalize từ engine |
| `question` | ✅ final | ✅ draft |  | LLM chỉ gợi ý |
| `question_complexity` | ✅ |  |  | phải do human chốt |
| `gold_answer` | ✅ final | ✅ draft |  | field rất quan trọng |
| `expected_answer_summary` | ✅ final | ✅ draft |  | ngắn, chấm được |
| `gold_context_spans` | ✅ bắt buộc | gợi ý nơi tìm |  | không để LLM bịa quote |
| `gold_chunk_ids` | review |  | ✅ | map span → chunk |
| `required_entities` | ✅ final | ✅ gợi ý |  | phục vụ retrieval eval |
| `labels` | ✅ |  |  | topic / flags |
| `expected_answer_points` | ✅ | ✅ draft |  | ops only |
| `negative_constraints` | ✅ | ✅ draft |  | ops only |
| `answer_rubric` | ✅ | ✅ draft |  | ops only |
| `annotator` | ✅/auto |  | ✅ | ops only |
| `verification` | ✅ reviewer |  |  | ops only |
| `status` | ✅ |  |  | ops only |
| `difficulty` | ✅ |  |  | ops only |

---

# 9. Những lỗi team rất dễ gặp nếu không bám schema này

## 9.1. Lỗi 1 — Nhầm `gold_answer` với `expected_answer_summary`
- `gold_answer` = câu trả lời chuẩn đầy đủ
- `expected_answer_summary` = tóm tắt ý chính bắt buộc

Nếu viết 2 field này giống hệt nhau thì sample sẽ mất giá trị review. [schema_release.json](https://www.genspark.ai/api/files/s/seXZhhes)

## 9.2. Lỗi 2 — Để LLM tự bịa `gold_context_spans`
Đây là lỗi nguy hiểm nhất.  
LLM có thể “nói đúng ý” nhưng quote sai câu, hoặc quote ghép từ trí nhớ. Với benchmark retrieval, điều này làm hỏng ground truth. [Guideline benchmark](https://www.genspark.ai/api/files/s/fvJx9CFu)

## 9.3. Lỗi 3 — Direct sample vẫn cố gắng nhét quote sách
Điều này không sai hoàn toàn, nhưng thường làm sample bị méo. Nếu câu chỉ hỏi fact ở chart, cứ để `gold_context_spans = []` là rõ ràng hơn. [Guideline benchmark](https://www.genspark.ai/api/files/s/fvJx9CFu)

## 9.4. Lỗi 4 — `chart_repr` mỗi sample một kiểu
Vì `chart_repr` hiện schema còn mở, team bắt buộc phải có internal sub-schema thống nhất. Nếu không, model input sẽ rất không ổn định. [schema_release.json](https://www.genspark.ai/api/files/s/seXZhhes)

## 9.5. Lỗi 5 — File `raw_pages` hiện tại content không đồng nhất mà vẫn dùng thẳng
`TVGM_raw_pages.json` đang cho thấy `content` có lúc là string, lúc là array, lúc là object. Nếu không normalize lại trước khi annotate, script và con người đều sẽ làm lệch nhau. [TVGM_raw_pages.json](https://www.genspark.ai/api/files/s/pZ31EmCY)

---

# 10. Kết luận thao tác cho team

## 10.1. `schema_release.json` dùng khi nào?
Dùng khi sample gần hoàn chỉnh hoặc khi export release benchmark.

## 10.2. `schema_ops.json` dùng khi nào?
Dùng xuyên suốt lúc tạo sample, review, adjudication.

## 10.3. Nguyên tắc vàng
- **Release schema** = thứ pipeline benchmark cần
- **Ops schema** = thứ team cần để làm đúng
- `gold_context_spans` luôn do human chốt
- `gold_chunk_ids` luôn là hậu xử lý
- `chart_repr` phải có sub-schema thống nhất nội bộ
- file corpus hiện có phải normalize thêm trước khi annotate đại trà [schema_release.json](https://www.genspark.ai/api/files/s/seXZhhes) [schema_ops.json](https://www.genspark.ai/api/files/s/PwfQI55a) [TVGM_raw_pages.json](https://www.genspark.ai/api/files/s/pZ31EmCY)

---

# 11. Khuyến nghị cập nhật nhẹ sau khi team đọc xong file này

Nếu team muốn schema chặt hơn và đỡ mơ hồ hơn, nên cân nhắc:
1. cho `page_book` nhận `null`
2. define sub-schema rõ hơn cho `chart_repr`
3. define sub-schema tối thiểu cho `labels`
4. chuẩn hóa `sections.jsonl` để không còn `content` kiểu hỗn hợp [schema_release.json](https://www.genspark.ai/api/files/s/seXZhhes) [TVGM_raw_pages.json](https://www.genspark.ai/api/files/s/pZ31EmCY)
```

---

## Gợi ý tiếp theo rất nên làm
Nếu bạn muốn, ở tin nhắn tiếp theo mình có thể làm tiếp **3 thứ cực hữu ích** để khóa luôn phần schema/corpus:

1. `schema_raw_pages.json`  
2. `schema_sections.json`  
3. `schema_chart_repr.json`  

để C code theo đúng format, B annotate theo đúng format, còn bạn A review cũng dễ hơn rất nhiều.