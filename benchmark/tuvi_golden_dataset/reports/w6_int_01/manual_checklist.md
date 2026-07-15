# Checklist thủ công W6-INT-01

## Mục tiêu
Kiểm tra luồng người dùng thật trên browser: login, tạo lá số, xem board, chat và citation panel.

## Chuẩn bị

```powershell
cd backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

```powershell
cd frontend
npm run dev
```

Mở `http://localhost:3000` và dùng test account Supabase local/cloud hiện có.

## Config candidate

- Config smoke: `D:\University\Năm 3 ĐH\Kì 3 (18th6)\Text Mining\tuvi-battu-graphrag\configs\w6_integration_candidate.yaml`
- Chunk strategy: `chunk_semantic_embedding_bge_m3`
- Lưu ý: frontend chỉ gửi `experiment_config_path` nếu UI/dev payload có field này; nếu không, backend dùng `DEFAULT_EXPERIMENT_CONFIG`.
  Với manual UI test, cần xác nhận biến env hoặc payload đang trỏ đúng candidate nếu muốn test đúng config này.

## Các bước kiểm

| Bước | Kỳ vọng | Kết quả thực tế | Bug severity nếu fail |
|---|---|---|---|
| 1. Login | Đăng nhập thành công, vào dashboard protected |  | P0 nếu không login được |
| 2. Tạo lá số | Submit form label/ngày/giờ/giới tính thành công |  | P0 nếu không tạo được |
| 3. Redirect chart detail | Điều hướng sang `/chart/[id]` |  | P0/P1 |
| 4. TuViBoard | Hiển thị đủ 12 cung, không crash responsive desktop |  | P1 nếu sai dữ liệu, P2 nếu layout nhỏ |
| 5. Factual chat | Hỏi Mệnh ở cung nào, trả lời có grounding lá số |  | P1 nếu không trả lời |
| 6. Interpretive chat | Hỏi luận giải Mệnh, có answer tiếng Việt và nguồn nếu dùng corpus |  | P1 nếu không có source/citation |
| 7. Multi-hop chat | Hỏi tam hợp/xung chiếu, diagnostics/answer không no-context |  | P1 nếu retrieval/context miss |
| 8. Citation panel | Source name/page/excerpt hiển thị, click marker mở đúng item |  | P1 nếu không xem được nguồn |
| 9. Error/loading | Loading state rõ, không lộ raw stack trace |  | P1/P2 |

## Quy tắc severity

- P0: chặn luồng chính như không login, không tạo lá số, chart detail crash, chat 500 toàn bộ.
- P1: luồng chạy nhưng thiếu source/citation, board sai rõ, multi-hop luôn no-context, latency quá cao.
- P2: lỗi trình bày, wording, loading state chưa mượt nhưng không chặn demo.

