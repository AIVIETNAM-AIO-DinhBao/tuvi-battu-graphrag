# Hướng dẫn verify và chốt câu hỏi final

Tài liệu này dùng cho bước **verify generated LLM question candidates** sau khi đã có file `drafts_questions.jsonl`.

Mục tiêu của bước này:
- mỗi slot chỉ giữ lại **1 câu hỏi final**
- câu hỏi final phải đúng chart, đúng độ khó, đúng phạm vi benchmark
- sau khi xong, lead chỉ cần **copy 3 file batch** lại là merge được, **không cần code**

---

# 1. File làm việc của mỗi người

## 1.1. Chia thành 3 file riêng
Mỗi người làm **1 file riêng**, không cùng sửa một file chung.

Tên file thống nhất:
- `final_questions_A.jsonl`
- `final_questions_B.jsonl`
- `final_questions_C.jsonl`

## 1.2. Batch phân công hiện tại

Phân batch theo `sample_plan.csv` và `samples/slot_batch_summary.csv`, không tự ý đổi batch.

- **A / batch A**: `CHART-001`–`CHART-002`, `TVQA-001`–`TVQA-020`, 20 slot, reviewer B.
- **B / batch B**: `CHART-003`–`CHART-006`, `TVQA-021`–`TVQA-060`, 40 slot, reviewer C.
- **C / batch C**: `CHART-007`–`CHART-010`, `TVQA-061`–`TVQA-100`, 40 slot, reviewer A.

Lưu ý: `CHART-010` hiện thuộc batch C, không còn thuộc batch A.

## 1.3. Vì sao phải tách 3 file
- tránh conflict
- dễ review
- dễ merge thủ công
- lead chỉ cần copy nối 3 file là xong

---

# 2. Schema cuối cùng của file final question

Mỗi dòng trong `final_questions_*.jsonl` là **1 object JSON phẳng**, không còn mảng `candidates`.

Schema cuối cùng:

```json
{
  "slot_id": "TVQA-001",
  "chart_id": "CHART-001",
  "question_complexity": "Direct",
  "question_family": "core_identity",
  "topic": "identity",
  "owner": "A",
  "reviewer": "B",
  "question": "Bản mệnh của đương số trong lá số này là gì?"
}
```

## Chỉ giữ 8 field này
- `slot_id`
- `chart_id`
- `question_complexity`
- `question_family`
- `topic`
- `owner`
- `reviewer`
- `question`

---

# 3. Từ file draft sang file final: giữ gì, xóa gì

## 3.1. Field giữ lại từ draft record
Giữ lại:
- `slot_id`
- `chart_id`
- `question_complexity`
- `question_family`
- `topic`
- `owner`
- `reviewer`

Sau đó thêm field mới:
- `question` = câu được chọn/chỉnh cuối cùng

## 3.2. Field phải xóa khỏi record final
Xóa toàn bộ các field này:
- `llm_model`
- `prompt_version`
- `chart_inputs`
- `candidates`
- `status`

## 3.3. Field không đưa sang file final
Trong từng candidate, **không giữ** các field sau:
- `candidate_id`
- `rationale`
- `expected_chart_signals`
- `risk_notes`

Các field đó chỉ phục vụ bước draft, không dùng trong file final.

---

# 4. Cách làm đúng: copy theo batch, không copy từng row lẻ

## Quy tắc chung
**Không làm kiểu copy từng slot lẻ sang file khác nhau.**

Cách đúng là:
1. lead hoặc từng thành viên lấy **toàn bộ batch của mình**
2. tạo một file `final_questions_X.jsonl`
3. đi lần lượt từ trên xuống dưới theo đúng thứ tự slot trong batch
4. mỗi slot xuất đúng 1 dòng JSON final

## Vì sao không nên copy từng row lẻ
- dễ sót slot
- dễ nhảy số thứ tự
- dễ trộn nhầm chart
- lúc merge khó check đủ 100 câu

---

# 5. Quy trình thao tác step-by-step cho từng thành viên

## Bước 1 — mở 3 file tham chiếu
Mỗi người mở đồng thời:
1. `sample_plan.csv`
2. file draft question chung hoặc file batch draft của mình
3. chart tương ứng (`chart_repr`, và nếu cần `chart_semantic`)

## Bước 2 — chỉ lọc đúng batch của mình
Ví dụ:
- A chỉ làm batch A: `CHART-001`–`CHART-002`, `TVQA-001`–`TVQA-020`
- B chỉ làm batch B: `CHART-003`–`CHART-006`, `TVQA-021`–`TVQA-060`
- C chỉ làm batch C: `CHART-007`–`CHART-010`, `TVQA-061`–`TVQA-100`

Không đụng slot của batch khác.

## Bước 3 — tạo file output final riêng
Ví dụ người B tạo file:
- `final_questions_B.jsonl`

## Bước 4 — xử lý từng slot theo thứ tự slot_id tăng dần
Ví dụ batch B đi từ:
- `TVQA-021`
- `TVQA-022`
- `TVQA-023`
...

Không đổi thứ tự slot.

## Bước 5 — đọc tất cả candidate của 1 slot
Với mỗi slot:
- đọc toàn bộ 2–3 candidate
- đối chiếu với chart thật
- kiểm tra complexity/family/topic có đúng intent không

## Bước 6 — chọn 1 câu tốt nhất
Có 3 khả năng:
1. **Giữ nguyên** 1 candidate nếu đã tốt
2. **Sửa nhẹ** 1 candidate nếu lõi đúng nhưng wording chưa tốt
3. **Viết lại ngắn gọn** dựa trên 1 candidate nếu các candidate đều gần đúng nhưng chưa chuẩn

## Bước 7 — xuất 1 dòng JSON final
Ví dụ:

```json
{"slot_id":"TVQA-021","chart_id":"CHART-003","question_complexity":"Direct","question_family":"core_identity","topic":"identity","owner":"B","reviewer":"C","question":"Trong lá số này, cung Mệnh đóng tại địa chi nào?"}
```

## Bước 8 — lặp lại đến hết batch
Mỗi slot chỉ còn **1 dòng final**.

## Bước 9 — tự check cuối file
Trước khi gửi lead:
- đủ số slot trong batch
- không trùng `slot_id`
- không thiếu `question`
- không còn field thừa
- JSON mỗi dòng hợp lệ

## Bước 10 — báo lead A nếu có trường hợp bất thường
Không cần thêm bool flag vào file.
Nếu có vấn đề, báo riêng cho A qua chat hoặc note ngoài file.

---

# 6. Tiêu chí chung để chọn câu hỏi final

## 6.1. Đúng chart
Mọi thực thể trong câu hỏi phải có căn cứ từ chart đó:
- đúng cung
- đúng sao
- đúng trạng thái
- đúng Mệnh/Thân/Cục/Bản Mệnh

Không được giữ câu hỏi nếu nó gọi sai thực thể của chart.

## 6.2. Đúng complexity
### Direct
- trả lời được chỉ bằng chart
- không cần sách
- thường hỏi fact rõ ràng

### One-hop
- cần **1 fact từ chart + 1 rule từ sách**
- không được biến thành câu hỏi tổng hợp quá rộng

### Two-hop
- cần ít nhất **2 bước nối**
- ví dụ:
  - Mệnh + tam hợp
  - Mệnh + xung chiếu
  - cung chủ đề + Mệnh/Thân
  - sao + trạng thái + quan hệ cung

## 6.3. Không quá rộng
Loại bỏ hoặc sửa các câu kiểu:
- “luận giải toàn bộ cuộc đời”
- “người này có giàu không”
- “có thành công không” nếu không gắn phạm vi rõ
- “nên làm gì” nếu không có khung hỏi rõ

## 6.4. Hỏi 1 việc chính
Ưu tiên câu hỏi chỉ có **1 trọng tâm chính**.
Không nên giữ câu hỏi gộp 2–3 ý lớn trong cùng một câu.

## 6.5. Dễ tìm gold span sau này
Ưu tiên câu mà ngày mai team có thể tìm được đoạn sách support tương đối rõ.
Nếu câu quá bay, quá đời thường, quá tư vấn cá nhân thì sẽ rất khó tìm gold span.

## 6.6. Ngôn ngữ tự nhiên nhưng chuẩn benchmark
Câu hỏi nên:
- rõ nghĩa
- tự nhiên
- không lủng củng
- không quá văn vẻ
- không dùng nhiều mệnh đề thừa

## 6.7. Ưu tiên kiểu hỏi naive nhưng vẫn chấm được
- Hãy ưu tiên câu hỏi nghe giống người dùng thật hỏi khi nhờ AI xem lá số.
- Không nên để người hỏi tự nêu quá nhiều reasoning kỹ thuật như tam hợp, xung chiếu, đồng cung, hãm địa, tọa thủ trong cùng một câu.
- Có thể giữ một số thuật ngữ tương đối phổ biến như Mệnh, Thân, Tài Bạch, Phu Thê, Tuần, Triệt nếu chúng giúp câu hỏi rõ hơn.
- Với câu Two-hop, phần multi-hop nên nằm ở backend và gold span; bề mặt câu hỏi vẫn nên tự nhiên.
- Nếu phải chọn giữa một câu rất kỹ thuật và một câu tự nhiên hơn nhưng vẫn đủ cụ thể để benchmark chấm được, hãy chọn câu tự nhiên hơn.

### Ví dụ nên tránh
- “Khi cung Mệnh có Lộc Tồn và bộ sao Thiên Đồng, Thái Âm bị Triệt, việc cung xung chiếu Thiên Di không có chính tinh nhưng có Địa Không (hãm) và Đào Hoa sẽ ảnh hưởng thế nào đến cách cục của lá số?”

### Ví dụ nên ưu tiên hơn
- “Công việc và việc đi xa của lá số này có gặp trở ngại gì đáng chú ý không?”
- “Mệnh và Thân của lá số này nói gì về tính cách và hướng phát triển của người này?”
- “Tuần hoặc Triệt trong lá số này ảnh hưởng gì đến công việc / tình duyên?”

---

# 7. Khi nào nên sửa candidate

## Sửa nhẹ khi:
- wording dài dòng
- có thể rút gọn mà không đổi ý
- cần thay từ cho chuẩn hơn
- cần làm rõ phạm vi hỏi
- cần chuyển từ câu hỏi quá kỹ thuật sang câu hỏi tự nhiên hơn mà vẫn giữ nguyên intent slot

## Sửa mạnh hơn khi:
- candidate đúng hướng nhưng đang hỏi quá rộng
- candidate có 2 ý chính, cần rút còn 1 ý
- candidate dùng từ quá đời thường hoặc mơ hồ

## Không nên tự sửa quá xa khi:
- đổi hẳn intent slot
- đổi complexity
- thêm thực thể mới không có trong chart
- biến một câu Direct thành One-hop hoặc ngược lại

Nếu buộc phải sửa rất mạnh, báo A riêng.

---

# 8. Khi nào phải báo lại cho lead A

Báo riêng cho A nếu gặp một trong các trường hợp sau:
1. cả 2–3 candidate đều không usable
2. question_family có vẻ không hợp với chart thật
3. complexity ở slot này có vẻ sai thiết kế
4. chart có dữ kiện mâu thuẫn hoặc thiếu
5. câu hỏi hợp lý duy nhất lại vượt ra ngoài phạm vi benchmark

Không cần nhét các ghi chú này vào JSONL final.
Chỉ cần báo riêng qua chat / note ngoài file.

---

# 9. Checklist tự kiểm trước khi nộp file

Trước khi gửi file final cho lead, mỗi người tự check:
- [ ] đúng batch của mình: A = 20 slot, B = 40 slot, C = 40 slot
- [ ] đủ số slot trong batch
- [ ] mỗi slot chỉ có 1 câu final
- [ ] không còn `candidates`
- [ ] không còn `llm_model`, `prompt_version`, `status`
- [ ] mỗi dòng là JSON hợp lệ
- [ ] thứ tự `slot_id` tăng dần
- [ ] không sửa `slot_id`, `chart_id`, `owner`, `reviewer`
- [ ] `question` là tiếng Việt tự nhiên, đúng complexity

---

# 10. Cách merge để lead không cần code

Sau khi A/B/C hoàn tất:
1. A nhận 3 file:
   - `final_questions_A.jsonl`
   - `final_questions_B.jsonl`
   - `final_questions_C.jsonl`
2. A mở file mới tên:
   - `final_questions.jsonl`
3. copy toàn bộ nội dung của file A
4. nối tiếp nội dung file B
5. nối tiếp nội dung file C
6. lưu lại

Vì cả nhóm đã thống nhất:
- schema giống nhau
- mỗi slot chỉ có 1 dòng
- không có field thừa

nên merge chỉ cần copy nối file là đủ.

---

# 11. Ví dụ một slot từ draft sang final

## Draft
```json
{
  "slot_id":"TVQA-001",
  "chart_id":"CHART-001",
  "question_complexity":"Direct",
  "question_family":"core_identity",
  "topic":"identity",
  "owner":"A",
  "reviewer":"B",
  "llm_model":"gemini-3.1-flash-lite",
  "prompt_version":"v1",
  "chart_inputs":{"used_chart_repr":true,"used_chart_semantic":true},
  "candidates":[
    {
      "candidate_id":"TVQA-001-C1",
      "question":"Bản mệnh của đương số trong lá số này là gì?",
      "rationale":"...",
      "expected_chart_signals":["Bản Mệnh","Thành Đầu Thổ"],
      "risk_notes":"Thấp"
    },
    {
      "candidate_id":"TVQA-001-C2",
      "question":"Cục của lá số này được xác định là gì?",
      "rationale":"...",
      "expected_chart_signals":["Cục","Hỏa lục cục"],
      "risk_notes":"Thấp"
    }
  ],
  "status":"draft_generated"
}
```

## Final
```json
{"slot_id":"TVQA-001","chart_id":"CHART-001","question_complexity":"Direct","question_family":"core_identity","topic":"identity","owner":"A","reviewer":"B","question":"Bản mệnh của đương số trong lá số này là gì?"}
```

---

# 12. Kết luận

Mục tiêu của bước này không phải giữ lại nhiều thông tin draft, mà là chốt ra **1 câu hỏi final sạch, thống nhất, dễ merge, dễ dùng cho bước gold span hôm sau**.
