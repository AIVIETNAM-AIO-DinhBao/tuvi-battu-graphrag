# Kế Hoạch Công Việc: Hệ Thống Hỏi Đáp Tử Vi / Bát Tự với Hybrid GraphRAG
**Dựa trên:** Specification v6.0  
**Phiên bản:** 3.0  
**Ngày:** 2026-06-22  
**Thời gian thực hiện:** 7–8 tuần  
**Định dạng:** Các task được chia theo tuần, rất cụ thể, và không gán theo thành viên. Team tự phân công nội bộ.

***

## Cách đọc tài liệu này

- Mỗi task có mã duy nhất theo dạng `W[tuần]-[nhóm]-[số]`, ví dụ `W1-INFRA-01`.
- **When:** tuần hoặc khoảng thời gian cần làm task.
- **What to do:** các việc cần thực hiện cụ thể.
- **Deliverable:** kết quả đầu ra có thể kiểm tra được.
- **Depends on:** các task phải hoàn thành trước.
- **Done when:** tiêu chí hoàn thành rõ ràng, có thể xác minh.

> **Môi trường thực hiện:**  
> - 💻 **Local** = chạy trên laptop, không cần GPU  
> - ☁️ **Kaggle** = nên chạy trên Kaggle Free Tier cho job nặng  
> - 🌐 **Cloud** = chạy trên Render / Vercel / Supabase / Neo4j AuraDB

***

## Tuần 1 — Nền tảng và hạ tầng

Mục tiêu: Tất cả dịch vụ hạ tầng được tạo, skeleton project chạy local, và schema database được áp dụng.

***

### W1-INFRA-01 — Tạo tất cả dịch vụ cloud

**When:** Ngày 1–2  
**Môi trường:** 🌐 **Cloud**  
**What to do:**
- Tạo Supabase project ở free tier. Ghi lại project URL, anon key, và service key.
- Tạo Neo4j AuraDB Free instance. Ghi lại connection URI, username, password.
- Tạo project Vercel và kết nối với repo frontend. Cấu hình cho Next.js.
- Tạo service Render cho backend repo. Cấu hình môi trường Python 3.11.
- Tạo project Langfuse (cloud hoặc self-hosted). Ghi lại public key và secret key.
- Tạo file `.env.example` dùng chung, ghi đầy đủ toàn bộ biến môi trường cần thiết.

**Deliverable:** Tất cả dịch vụ hoạt động. File `.env.example` được commit vào repo.  
**Depends on:** —  
**Done when:** Team có thể kết nối tới từng dịch vụ từ máy local bằng biến môi trường.

***

### W1-INFRA-02 — Thiết lập cấu trúc repo

**When:** Ngày 1–2  
**Môi trường:** 💻 **Local**  
**What to do:**
- Quyết định và ghi rõ cấu trúc repo: monorepo (frontend + backend trong một repo) hoặc hai repo riêng.
- Khởi tạo project frontend: `npx create-next-app@14 --typescript`.
- Khởi tạo project backend: FastAPI với Python 3.11, dùng `pyproject.toml` hoặc `requirements.txt`.
- Thiết lập `.gitignore`, `README.md`, và chiến lược branch (ví dụ: `main`, `dev`, feature branches).
- Cấu hình chiến lược quản lý secrets và env cho cả dự án.

**Deliverable:** Repo được khởi tạo, `README.md` mô tả cách chạy, cả hai app chạy local bằng `npm run dev` và `uvicorn`.  
**Depends on:** W1-INFRA-01  
**Done when:** Bất kỳ thành viên nào cũng có thể clone repo và chạy cả hai app local trong vòng 10 phút theo README.

***

### W1-DB-01 — Áp dụng schema Supabase và RLS

**When:** Ngày 2–4  
**Môi trường:** 🌐 **Cloud** (Supabase dashboard + local SQL client)  
**What to do:**
- Viết migration SQL cho đủ 4 bảng: `profiles`, `la_so`, `chat_sessions`, `source_chunks`.
- Thêm constraint `UNIQUE (la_so_id)` trên `chat_sessions` để đảm bảo mỗi chart chỉ có một chat session.
- Thêm `CHECK (chart_system IN ('TUVI', 'BATU', 'TUVI_BATU'))` trên `la_so`.
- Thêm toàn bộ index theo schema đã định.
- Viết và áp dụng toàn bộ policy RLS cho `profiles`, `la_so`, `chat_sessions`.
- Thêm extension `moddatetime` và trigger tự động cập nhật `updated_at` cho cả 3 bảng.
- Viết script seed SQL tạo một test user + một `la_so` test + một `chat_sessions` test để dùng trong local dev.

**Deliverable:** File migration Supabase được áp dụng và commit. Seed script được commit. RLS được test thủ công để xác nhận user không đọc được data của user khác.  
**Depends on:** W1-INFRA-01  
**Done when:** Các bảng xuất hiện đúng trong Supabase dashboard. RLS chặn được truy cập chéo giữa user.

***

### W1-DB-02 — Khởi tạo schema và index Neo4j

**When:** Ngày 3–5  
**Môi trường:** 🌐 **Cloud** (Neo4j AuraDB + local Cypher client)  
**What to do:**
- Kết nối tới Neo4j AuraDB và chạy script setup Cypher.
- Tạo uniqueness constraint cho các node canonical: `Sao`, `Cung`, `ThienCan`, `DiaChi`, `NguHanh`, `Chunk`.
- Tạo vector index cho embedding chunk:
  ```cypher
  CREATE VECTOR INDEX chunkVector IF NOT EXISTS
  FOR (c:Chunk) ON (c.embedding)
  OPTIONS {indexConfig: {`vector.dimensions`: 768, `vector.similarity_function`: 'cosine'}}
  ```
- Tạo fulltext index cho sparse/BM25 retrieval:
  ```cypher
  CREATE FULLTEXT INDEX chunkFulltext IF NOT EXISTS
  FOR (c:Chunk) ON EACH [c.text, c.title, c.keywords]
  ```
- Commit toàn bộ Cypher setup vào repo trong `/infra/neo4j/`.

**Deliverable:** Neo4j có đầy đủ constraint và index. Script setup được commit.  
**Depends on:** W1-INFRA-01  
**Done when:** Cypher chạy không lỗi. `SHOW INDEXES` xác nhận vector index và fulltext index đã online.

***

### W1-AUTH-01 — Tích hợp Supabase Auth trong Next.js

**When:** Ngày 3–5  
**Môi trường:** 💻 **Local**  
**What to do:**
- Cài `@supabase/supabase-js` và `@supabase/auth-helpers-nextjs`.
- Tạo `/app/(auth)/login/page.tsx` có form đăng nhập email/password.
- Tạo `/app/(auth)/register/page.tsx` có form đăng ký.
- Cài session handling ở server bằng `createServerComponentClient`.
- Tạo `lib/supabase.ts` cho client-side Supabase instance.
- Tạo middleware bảo vệ route: redirect user chưa đăng nhập về `/login`.
- Tạo chức năng logout.

**Deliverable:** Có trang login và register chạy được. Protected routes redirect đúng. Session tồn tại sau refresh trang.  
**Depends on:** W1-DB-01, W1-INFRA-02  
**Done when:** Thành viên có thể đăng ký, đăng nhập, vào trang protected, và đăng xuất. Truy cập dashboard khi chưa đăng nhập bị redirect về login.

***

### W1-API-01 — Tạo skeleton FastAPI và health endpoint

**When:** Ngày 3–5  
**Môi trường:** 💻 **Local**  
**What to do:**
- Thiết lập FastAPI app với cấu trúc router:
  - `/health` — GET, trả về `{status: "ok"}`
  - `/chart/tuvi` — POST placeholder (tạm thời trả 501)
  - `/chat` — POST placeholder (tạm thời trả 501)
- Cấu hình CORS cho Vercel frontend và `localhost:3000`.
- Thêm stub tích hợp Langfuse SDK (khởi tạo client, chưa trace).
- Cấu hình đọc biến môi trường bằng `pydantic-settings`.
- Viết `Dockerfile` hoặc `render.yaml` cho deploy Render.

**Deliverable:** FastAPI chạy local. `/health` trả 200. Config deploy Render được commit.  
**Depends on:** W1-INFRA-01, W1-INFRA-02  
**Done when:** `curl http://localhost:8000/health` trả về `{"status":"ok"}`.

***

### W1-FE-01 — Tạo app shell và routing cho Next.js

**When:** Ngày 3–5  
**Môi trường:** 💻 **Local**  
**What to do:**
- Tạo cấu trúc route:
  - `/` — landing hoặc redirect sang dashboard nếu đã đăng nhập.
  - `/dashboard` — protected, hiển thị danh sách chart.
  - `/chart/[id]` — protected, hiển thị chi tiết chart và chat.
- Cài và cấu hình Tailwind CSS và shadcn/ui.
- Cài và cấu hình Zustand cho global state.
- Tạo các component placeholder: `TuViBoard.tsx`, `BatuBoard.tsx`, `ChatInterface.tsx`, `ChartSummaryCard.tsx`.
- Tạo Next.js API route stub:
  - `/api/chat` — proxy tới FastAPI (tạm mock).
  - `/api/battu/calculate` — stub (tạm trả 501).

**Deliverable:** App shell có thể điều hướng. Route tồn tại và render placeholder content. Tailwind và shadcn/ui hoạt động.  
**Depends on:** W1-AUTH-01, W1-INFRA-02  
**Done when:** Vào `/dashboard` sau khi login thấy một trang hợp lệ. Không có route nào bị 404.

***

## Tuần 2 — Engine và visualizer

Mục tiêu: Tử Vi và Bát Tự engine được tích hợp và kiểm chứng. Visualizer hiển thị dữ liệu thật.

***

### W2-ENGINE-01 — Tích hợp engine Tử Vi (`lasotuvi`)

**When:** Tuần 2, ngày 1–3  
**Môi trường:** 💻 **Local**  
**What to do:**
- Thêm `doanguyen/lasotuvi` và `pyvnlunar` vào backend dependencies.
- Implement endpoint `POST /chart/tuvi` trong FastAPI:
  - Nhận `{birth_date, birth_time, gender, label}`
  - Trả về full Tử Vi chart JSON.
- Chuẩn hóa output của engine thành internal schema ổn định.
- Xử lý các case lỗi: ngày không hợp lệ, giờ không hỗ trợ, thiếu field.

**Deliverable:** `POST /chart/tuvi` trả về chart JSON hợp lệ cho test birth date.  
**Depends on:** W1-API-01  
**Done when:** Endpoint được test với ít nhất 3 input khác nhau. Schema response được ghi trong `/docs/chart-schema.md`.

***

### W2-ENGINE-02 — Unit test độ chính xác engine Tử Vi

**When:** Tuần 2, ngày 2–4  
**Môi trường:** 💻 **Local**  
**What to do:**
- Chọn ít nhất 5 ngày sinh thật có chart Tử Vi đã được xác minh bằng tay từ yeutuvi.com và tuvilyso.net.
- Viết unit test so sánh output của engine với reference đã kiểm chứng, cả theo sao và cung.
- Ghi lại mọi sai lệch nếu có, đánh dấu là chấp nhận được hoặc cần sửa.

**Deliverable:** File test `tests/test_tuvi_engine.py` có ít nhất 5 case. Có test report ghi rõ pass/fail và deviation nếu có.  
**Depends on:** W2-ENGINE-01  
**Done when:** Cả 5 test case đều pass phần star placement (Chính Tinh). Nếu fail case nào thì phải có giải thích.

***

### W2-ENGINE-03 — Tích hợp engine Bát Tự (`alvamind`)

**When:** Tuần 2, ngày 1–3  
**Môi trường:** 💻 **Local**  
**What to do:**
- Thêm package `bazi-calculator-by-alvamind` vào project Next.js.
- Implement Next.js API Route `POST /api/battu/calculate`:
  - Nhận `{year, month, day, hour, gender}`
  - Trả về Bát Tự JSON từ `calc.getCompleteAnalysis()`
- Chuẩn hóa output thành internal schema ổn định.
- Xử lý input lỗi: ngày/giờ không hợp lệ, tham số thiếu.

**Deliverable:** `POST /api/battu/calculate` trả về Bát Tự JSON hợp lệ.  
**Depends on:** W1-FE-01  
**Done when:** API route được test với ít nhất 3 bộ input. Schema response được ghi lại.

***

### W2-ENGINE-04 — Luồng tạo và lưu chart end-to-end

**When:** Tuần 2, ngày 3–5  
**Môi trường:** 💻 **Local**  
**What to do:**
- Xây dựng form “Create new chart” trong Next.js:
  - Fields: label, birth date, birth time, gender, chart type (Tử Vi / Bát Tự / Both).
- Khi submit:
  - Gọi engine tương ứng.
  - Lưu chart JSON và metadata vào bảng `la_so` qua Supabase.
  - Redirect sang `/chart/[new_id]`.
- Xử lý loading state và error state.

**Deliverable:** Người dùng tạo chart được từ form và chart được lưu vào Supabase. Redirect sang chart page hoạt động.  
**Depends on:** W2-ENGINE-01, W2-ENGINE-03, W1-DB-01  
**Done when:** Tạo chart từ form sinh ra đúng một row trong `la_so` và redirect đúng.

***

### W2-VIZ-01 — Bảng Tử Vi 12 cung (SVG/D3 skeleton)

**When:** Tuần 2, ngày 3–5  
**Môi trường:** 💻 **Local**  
**What to do:**
- Implement component `TuViBoard.tsx`:
  - Render layout 12 cung dạng SVG.
  - Mỗi ô cung hiển thị tên cung và danh sách sao.
  - Nhận chart JSON qua props.
- Ưu tiên plain SVG trước, D3 transitions chỉ thêm nếu còn thời gian.
- Style bằng Tailwind khi phù hợp.

**Deliverable:** `TuViBoard.tsx` render đúng 12 cung từ chart data thật trên `/chart/[id]`.  
**Depends on:** W2-ENGINE-04  
**Done when:** Lưới hiển thị sao đúng ở đúng cung cho một chart test đã kiểm chứng.

***

### W2-VIZ-02 — Bảng Bát Tự cơ bản

**When:** Tuần 2, ngày 4–5  
**Môi trường:** 💻 **Local**  
**What to do:**
- Implement component `BatuBoard.tsx`:
  - Hiển thị bốn trụ (Năm, Tháng, Ngày, Giờ) theo layout 4 cột.
  - Hiển thị Thiên Can, Địa Chi, và Nạp Âm của từng trụ.
  - Nhận Bát Tự JSON qua props.

**Deliverable:** `BatuBoard.tsx` render đúng từ dữ liệu Bát Tự thật.  
**Depends on:** W2-ENGINE-04  
**Done when:** Bốn trụ hiển thị đúng cho một test birth date. Đã kiểm chứng với reference.

***

### W2-DASH-01 — Dashboard: danh sách chart

**When:** Tuần 2, ngày 4–5  
**Môi trường:** 💻 **Local**  
**What to do:**
- Implement trang `/dashboard`:
  - Lấy toàn bộ row `la_so` của user hiện tại.
  - Hiển thị mỗi chart bằng `ChartSummaryCard`: label, birth date, chart type, ngày tạo.
  - Bấm vào card thì đi tới `/chart/[id]`.
  - Có nút “Create new chart”.

**Deliverable:** Dashboard hiển thị danh sách chart đã lưu. Điều hướng tới chart detail và trang tạo mới hoạt động.  
**Depends on:** W2-ENGINE-04, W1-AUTH-01  
**Done when:** Sau khi đăng nhập, user thấy chart của mình. Empty state được xử lý tử tế.

***

## Tuần 3 — Ingestion pipeline

Mục tiêu: Sau khi đã có script extract/normalize PDF, phần còn lại của tuần 3 xây ingestion pipeline theo hướng strategy-aware để phục vụ ablation chunking trong SPEC v6.

***

### W3-INGEST-01 — Script extract và normalize PDF

**When:** Tuần 3, ngày 1–2  
**Môi trường:** 💻 **Local**  
**What to do:**
- Viết Python script `scripts/extract_pdf.py`:
  - Nhận đường dẫn PDF qua argument.
  - Detect text-based hay scanned bằng `pdfplumber`.
  - Extract text từ PDF text-based bằng `pdfplumber` hoặc `pymupdf`.
  - Normalize output: Unicode NFC, bỏ header/footer/page number, xóa khoảng trắng thừa.
  - Output ra danh sách `{page, text}` cho từng trang.
- Xử lý trường hợp text extraction ra dưới 50 ký tự mỗi trang thì đánh dấu “needs OCR”.

**Deliverable:** `scripts/extract_pdf.py` chạy được với PDF test và tạo ra text theo từng trang đã làm sạch. Output lưu dưới JSON.  
**Depends on:** —  
**Done when:** Script được test trên ít nhất 2 file PDF, một text-based và một borderline. Output sạch và chuẩn Unicode.

***

### W3-INGEST-02 — Chunking framework cho ablation

**When:** Tuần 3, ngày 1–3  
**Môi trường:** 💻 **Local**  
**What to do:**
- Viết `scripts/chunk_text.py` theo dạng strategy-aware:
  - Nhận text đã normalize theo trang từ W3-INGEST-01.
  - Nhận tham số `--chunking-strategy` hoặc đọc từ config.
  - Tạo output thống nhất cho mọi strategy: `{chunk_id, parent_id, chunk_type, chunk_text, source_name, source_page, domain, chunk_strategy_id, chunk_hash, metadata}`.
  - Bắt buộc `chunk_hash` bao gồm `chunk_strategy_id` để các strategy khác nhau không bị dedup lẫn nhau.
  - Ghi `chunk_strategy_id` vào metadata để downstream có thể trace lại.
- Tạo `configs/chunking_strategies.yaml` với các tag v6:
  - `chunk_structure_parent_child`
  - `chunk_fixed_256`
  - `chunk_fixed_512`
  - `chunk_fixed_1024`
  - `chunk_sentence_merge`
  - `chunk_semantic`
- Implement đầy đủ Strategy A mặc định:
  - Tách theo heading → section → paragraph → sentence.
  - Parent chunk 400–512 tokens, overlap 60–100 tokens.
  - Child chunk 120–180 tokens, overlap nhỏ.
  - Retrieve bằng child, trả context bằng parent.
- Danh sách tên sao, cung, thiên can, địa chi cần load từ config để tránh cắt ngang đơn vị khái niệm.

**Deliverable:** `scripts/chunk_text.py` chạy được với `chunk_structure_parent_child`, output có `chunk_strategy_id`, và `chunk_hash` khác nhau khi đổi strategy.  
**Depends on:** W3-INGEST-01  
**Done when:** Review thủ công 50+ chunk Strategy A. Không có tên sao/cung bị cắt ngang, và mỗi chunk có đủ metadata phục vụ ablation.

***

### W3-INGEST-03 — Implement các chunking strategy còn lại

**When:** Tuần 3, ngày 2–4  
**Môi trường:** 💻 **Local** + ☁️ **Kaggle** cho semantic chunking  
**What to do:**
- Mở rộng `scripts/chunk_text.py` để hỗ trợ:
  - Fixed-size sliding window 256 tokens, overlap 10–15%.
  - Fixed-size sliding window 512 tokens, overlap 10–15%.
  - Fixed-size sliding window 1024 tokens, overlap 10–15%.
  - Sentence-based dynamic merge, target 200–400 tokens, không merge qua heading/section.
  - Semantic chunking: tách câu trước, dùng embedding similarity để phát hiện điểm ngắt, target 300–500 tokens.
- Với semantic chunking, batch embedding và rate limit để không vượt quota.
- Ghi summary thống kê cho từng strategy: số chunk, token trung bình, số chunk quá ngắn/quá dài, số lỗi split.

**Deliverable:** Cùng một file text đầu vào tạo được 6 bộ chunk tương ứng với 6 `chunk_strategy_id`.  
**Depends on:** W3-INGEST-02  
**Done when:** Chạy thử trên 1 chương/sách mẫu, output của mỗi strategy khác nhau hợp lý và không crash.

***

### W3-INGEST-04 — Trích xuất entity theo chunk strategy

**When:** Tuần 3, ngày 3–5  
**Môi trường:** ☁️ **Kaggle**  
**What to do:**
- Viết `scripts/extract_entities.py`:
  - Nhận danh sách chunk đã có `chunk_strategy_id`.
  - Với mỗi chunk, gọi Gemini Flash-Lite bằng prompt có cấu trúc để trích:
    - Entity types: `Sao`, `Cung`, `ToHop`, `KhaiNiem`, `LuanGiai`, `ThienCan`, `DiaChi`, `NguHanh`
    - Relation giữa các entity trong chunk
    - Phân loại `domain`: `TUVI`, `BATU`, hoặc `SHARED`
  - Chuẩn hóa tên entity theo lookup table.
  - Ghi `chunk_strategy_id`, `entity_extraction_model`, prompt version, và extraction timestamp vào output.
- Viết prompt template cho entity extraction và commit vào `/prompts/entity_extraction.txt`.
- Thêm cache theo `chunk_hash + prompt_version + entity_extraction_model` để chạy lại không tốn quota.

**Deliverable:** Entity/relation output có cấu trúc, giữ nguyên liên kết với `chunk_strategy_id`.  
**Depends on:** W3-INGEST-02  
**Done when:** Review 30+ chunk từ ít nhất 2 strategy. Entity được type đúng, canonical name nhất quán, và output không mất provenance.

***

### W3-INGEST-05 — Ghi graph và provenance strategy-aware

**When:** Tuần 3, ngày 4–5  
**Môi trường:** ☁️ **Kaggle**  
**What to do:**
- Viết `scripts/write_graph.py`:
  - `MERGE` knowledge node theo `canonical_name + domain + entity_type`.
  - `MERGE` node `Chunk` theo `chunk_hash`, trong đó hash đã bao gồm `chunk_strategy_id`.
  - Gán property `chunk_strategy_id`, `chunk_type`, `parent_id`, `domain`, `source_name`, `source_page`.
  - Link chunk tới `Source` bằng `HAS_CHUNK`, tới entity bằng `MENTIONS`.
  - Không merge lẫn `Chunk` giữa các strategy khác nhau.
- Mở rộng ghi provenance vào Supabase `source_chunks`:
  - Metadata phải có `chunk_strategy_id`, `parent_id`, `chunk_type`, `source_page`, token count, strategy config snapshot.
  - Cross-reference: mỗi node `Chunk` trong Neo4j lưu `chunk_id` khớp UUID trong `source_chunks`.

**Deliverable:** Neo4j và Supabase đều lưu được chunk theo strategy, không mất provenance.  
**Depends on:** W3-INGEST-04, W1-DB-02  
**Done when:** Ingest cùng một đoạn với 2 strategy tạo 2 `Chunk` khác nhau nhưng cùng knowledge node canonical; kiểm tra ngẫu nhiên 5 chunk map đúng sang `source_chunks`.

***

### W3-INGEST-06 — Embedding và fulltext index theo strategy

**When:** Tuần 3, ngày 4–5  
**Môi trường:** ☁️ **Kaggle**  
**What to do:**
- Viết `scripts/embed_chunks.py`:
  - Nhận danh sách chunk theo `chunk_strategy_id`.
  - Gọi `gemini-embedding-001` để tạo embedding.
  - Ghi vector embedding vào node `Chunk`.
  - Lưu `embedding_model`, embedding timestamp, và embedding dimension.
- Bảo đảm dense retrieval và fulltext retrieval có thể filter theo:
  - `domain`
  - `chunk_strategy_id`
  - `source_name`
- Thêm batch processing, retry nhẹ, và rate limiting.

**Deliverable:** Chunk của strategy mặc định có embedding và fulltext-search được.  
**Depends on:** W3-INGEST-05  
**Done when:** `SHOW INDEXES` cho thấy vector/fulltext index online, và query similarity thử trả kết quả có đúng `chunk_strategy_id`.

***

### W3-INGEST-07 — Baseline ingest bằng Strategy A

**When:** Tuần 3, ngày 5  
**Môi trường:** ☁️ **Kaggle**  
**What to do:**
- Chọn 1–2 sách đại diện nhất cho MVP early corpus, ưu tiên có cả Tử Vi và Bát Tự nếu dữ liệu sẵn.
- Chạy pipeline baseline: extract → chunk Strategy A → entity extract → graph write → embed → provenance.
- Với mỗi sách, ghi lại:
  - Tổng số trang extract được.
  - Tổng số parent/child chunk.
  - Tổng số entity/node/relation tạo mới.
  - Tổng số node/relation được merge.
  - Các vấn đề extraction hoặc trang bị bỏ qua.

**Deliverable:** 1–2 sách đại diện được ingest đầy đủ bằng `chunk_structure_parent_child`. Báo cáo nằm trong `/docs/ingestion-reports/`.  
**Depends on:** W3-INGEST-01 đến W3-INGEST-06  
**Done when:** Neo4j/Supabase có dữ liệu baseline truy vấn được, số node/relation nằm trong phạm vi kiểm soát của SPEC Section 16.

***

### W3-INGEST-08 — Incremental ingestion và capacity guard

**When:** Tuần 3, ngày 5  
**Môi trường:** 💻 **Local** + ☁️ **Kaggle**  
**What to do:**
- Mở rộng pipeline để hỗ trợ chạy lại incremental:
  - Trước khi insert chunk, kiểm tra `chunk_hash` trong `source_chunks`.
  - Trước khi tạo node trong Neo4j, dùng `MERGE` như W3-INGEST-05.
  - Ghi log số chunk skip, chunk mới, node mới, relation mới.
- Thêm script/report đếm capacity:
  - Tổng node/relation hiện tại.
  - Tổng chunk theo từng `chunk_strategy_id`.
  - Cảnh báo nếu ablation chunking có nguy cơ vượt free-tier.

**Deliverable:** Chạy pipeline lặp lại không tạo duplicate, và có báo cáo capacity theo strategy.  
**Depends on:** W3-INGEST-05, W3-INGEST-06  
**Done when:** Chạy lại pipeline cùng sách + cùng strategy cho ra 0 duplicate; chạy cùng sách + strategy khác tạo chunk riêng đúng kỳ vọng.

***

## Tuần 4 — Core RAG pipeline + ExperimentConfig

Mục tiêu: Toàn bộ LangGraph Hybrid GraphRAG chạy end-to-end và mọi module thay thế được đều có toggle/config để phục vụ ablation.

***

### W4-EXP-01 — Bổ sung schema `experiment_runs` và `ExperimentConfig`

**When:** Tuần 4, ngày 1  
**Môi trường:** 💻 **Local** + 🌐 **Cloud**  
**What to do:**
- Vì W1 đã hoàn tất, tạo migration bổ sung thay vì sửa task W1:
  - Tạo bảng `experiment_runs` theo SPEC v6.
  - Thêm index `idx_experiment_runs_id`.
  - Thêm policy/RLS phù hợp hoặc giới hạn bảng này cho service role trong MVP.
- Định nghĩa `ExperimentConfig` trong backend:
  - Retrieval toggles: `graph_retrieval_enabled`, `dense_retrieval_enabled`, `sparse_retrieval_enabled`.
  - Chunking: `chunk_strategy_id`.
  - Fusion: `fusion_method`.
  - Reranking/grading: `reranker_enabled`, `reranker_model`, `reranker_threshold`, `document_grading_enabled`.
  - Query/model/prompt: `query_rewrite_enabled`, `query_rewrite_model`, `embedding_model`, `generation_model`, `prompt_template`.
  - Context: `context_assembly_strategy`, top-k/token budget.
- Tạo `configs/experiments/default_production.yaml`.

**Deliverable:** Migration `experiment_runs` và schema `ExperimentConfig` được commit.  
**Depends on:** W1-DB-01, W1-API-01  
**Done when:** Backend load được default config, serialize/deserialize config ổn định, và ghi thử một row `experiment_runs` thành công.

***

### W4-RAG-01 — RAGState và LangGraph config-aware

**When:** Tuần 4, ngày 1–2  
**Môi trường:** 💻 **Local**  
**What to do:**
- Định nghĩa `RAGState` TypedDict như SPEC Section 7.2, bao gồm:
  - `experiment_config`
  - `experiment_id`
  - `retrieval_trace`
  - `graded_candidates`
- Thêm node/stub:
  - `load_experiment_config`
  - `load_chart_context`
  - `normalize_query`
  - `classify_query_complexity`
  - `rewrite_query`
  - `extract_entities`
  - `graph_retrieval`
  - `dense_retrieval`
  - `sparse_retrieval`
  - `fusion`
  - `rerank`
  - `document_grading`
  - `assemble_context`
  - `generate`
  - `map_citations`
  - `log_trace`
- Định nghĩa conditional routing dựa trên `ExperimentConfig`.

**Deliverable:** LangGraph compile được với config mặc định và chạy mock input không lỗi.  
**Depends on:** W4-EXP-01  
**Done when:** Mock config bật/tắt từng retrieval path làm graph bỏ qua hoặc chạy đúng node tương ứng.

***

### W4-RAG-02 — Query rewrite có toggle

**When:** Tuần 4, ngày 1–2  
**Môi trường:** 💻 **Local**  
**What to do:**
- Implement node `rewrite_query`:
  - Nếu `config.query_rewrite_enabled = false`, giữ nguyên query.
  - Nếu bật, dùng model từ `config.query_rewrite_model`.
  - Prompt `/prompts/query_rewrite.txt` phải chèn original query, chart type, key stars/houses, và guardrail không thêm claim mới.
  - Lưu output vào `state.rewritten_query` và `retrieval_trace.query_rewrite`.

**Deliverable:** Node query rewrite chạy được ở cả hai mode bật/tắt.  
**Depends on:** W4-RAG-01  
**Done when:** 5 query test cho thấy tắt rewrite giữ nguyên query, bật rewrite không thêm claim ngoài input.

***

### W4-RAG-03 — Entity extraction runtime có toggle/model override

**When:** Tuần 4, ngày 1–3  
**Môi trường:** 💻 **Local**  
**What to do:**
- Implement node `extract_entities`:
  - Chỉ chạy khi `config.graph_retrieval_enabled = true`.
  - Dùng model từ `config.entity_extraction_model` hoặc default Flash-Lite.
  - Tái sử dụng taxonomy và canonicalization từ ingestion.
  - Lưu entity, model, latency, và prompt version vào `retrieval_trace`.

**Deliverable:** Runtime entity extraction trả entity canonical và trace đầy đủ.  
**Depends on:** W4-RAG-01, W3-INGEST-04  
**Done when:** Tắt graph path thì node không gọi LLM; bật graph path thì 5 query mẫu extract đúng sao/cung.

***

### W4-RAG-04 — Graph retrieval config-aware

**When:** Tuần 4, ngày 2–3  
**Môi trường:** 💻 **Local**  
**What to do:**
- Implement node `graph_retrieval`:
  - Chỉ chạy khi `graph_retrieval_enabled = true`.
  - Dùng `graph_hop_depth` từ config, hỗ trợ 1 hoặc 2 hop.
  - Filter theo `domain`, `chunk_strategy_id`, và chart context khi phù hợp.
  - Trả về `state.graph_candidates`.
  - Ghi Cypher, số candidate, latency vào `retrieval_trace.graph`.

**Deliverable:** Graph retrieval trả ranked chunk candidate và filter đúng strategy.  
**Depends on:** W4-RAG-03, W3-INGEST-07  
**Done when:** Query liên quan sao/cung đã ingest trả kết quả không rỗng; đổi `chunk_strategy_id` không lẫn chunk strategy khác.

***

### W4-RAG-05 — Dense và sparse retrieval config-aware

**When:** Tuần 4, ngày 2–3  
**Môi trường:** 💻 **Local**  
**What to do:**
- Implement `dense_retrieval`:
  - Chỉ chạy khi `dense_retrieval_enabled = true`.
  - Dùng `embedding_model` từ config.
  - Filter theo `domain` và `chunk_strategy_id`.
- Implement `sparse_retrieval`:
  - Chỉ chạy khi `sparse_retrieval_enabled = true`.
  - Dùng Neo4j fulltext/BM25.
  - Filter theo `domain` và `chunk_strategy_id`.
- Ghi top-k, score, latency vào `retrieval_trace`.

**Deliverable:** Dense/sparse retrieval chạy độc lập được, có thể bật/tắt riêng.  
**Depends on:** W4-RAG-01, W3-INGEST-06  
**Done when:** 3 config `dense-only`, `sparse-only`, `dense+sparse` đều chạy end-to-end trên query mẫu.

***

### W4-RAG-06 — Fusion dispatcher

**When:** Tuần 4, ngày 3  
**Môi trường:** 💻 **Local**  
**What to do:**
- Implement node `fusion` đọc `config.fusion_method`:
  - `rrf`: Reciprocal Rank Fusion mặc định.
  - `weighted_sum`: normalize score rồi cộng trọng số.
  - `graph_first`: ưu tiên graph candidates, sau đó bổ sung dense/sparse.
- Dedup theo `chunk_id`, nhưng không làm mất `source_path` và score từng retrieval path.
- Lưu `state.fused_candidates` và trace cấu trúc điểm.

**Deliverable:** Fusion có thể đổi method bằng config, không cần sửa graph topology.  
**Depends on:** W4-RAG-04, W4-RAG-05  
**Done when:** Cùng input candidate, 3 fusion method tạo ranking khác nhau và được test snapshot.

***

### W4-RAG-07 — Rerank và document grading toggle

**When:** Tuần 4, ngày 3–4  
**Môi trường:** 💻 **Local**  
**What to do:**
- Implement `rerank`:
  - Chỉ chạy khi `reranker_enabled = true`.
  - Dùng `reranker_model` và `reranker_threshold` từ config.
  - Nếu tắt, chuyển `fused_candidates` sang bước context assembly.
- Implement stub/optional node `document_grading`:
  - Mặc định tắt trong production.
  - Khi bật trong ablation, dùng model từ `document_grading_model` để grade top candidates.
  - Lưu output vào `state.graded_candidates`.

**Deliverable:** Reranker production hoạt động, document grading có toggle để ablation.  
**Depends on:** W4-RAG-06  
**Done when:** Config tắt reranker không gọi model; config bật reranker thay đổi ranking ở một số query; document grading bật/tắt không phá pipeline.

***

### W4-RAG-08 — Context assembly strategies

**When:** Tuần 4, ngày 4  
**Môi trường:** 💻 **Local**  
**What to do:**
- Implement `assemble_context` theo `config.context_assembly_strategy`:
  - `parent_child`: retrieve child, fetch parent chunk.
  - `direct_chunk`: dùng chunk trực tiếp.
  - `balanced_sources`: giới hạn số chunk mỗi source để tránh một sách áp đảo.
- Đưa chart context summary lên đầu context.
- Cắt theo token budget từ config.
- Ghi context ids, token count, dropped chunks vào `retrieval_trace`.

**Deliverable:** Context assembly đổi được strategy và giữ citation map ổn định.  
**Depends on:** W4-RAG-07  
**Done when:** 3 strategy chạy được trên cùng query, output không vượt token budget và vẫn map citation đúng.

***

### W4-RAG-09 — Generation model và prompt template routing

**When:** Tuần 4, ngày 4–5  
**Môi trường:** 💻 **Local**  
**What to do:**
- Implement `generate`:
  - Chọn model theo `config.generation_model` hoặc routing policy.
  - Chọn prompt theo `config.prompt_template`.
  - Prompt phải yêu cầu trả lời tiếng Việt, bám context, cite chunk, và nói “không đủ dữ liệu” khi thiếu bằng chứng.
  - Log model, prompt template, latency, token usage vào Langfuse/retrieval trace.
- Tạo ít nhất 2 prompt template:
  - `grounded_default`
  - `strict_citation`

**Deliverable:** Generation node config-aware và có prompt templates để ablation.  
**Depends on:** W4-RAG-08  
**Done when:** Đổi `generation_model` hoặc `prompt_template` qua config làm request chạy đúng biến thể tương ứng.

***

### W4-RAG-10 — Citation mapping và trace theo experiment

**When:** Tuần 4, ngày 5  
**Môi trường:** 💻 **Local**  
**What to do:**
- Implement `map_citations`:
  - Map chunk ID sang `source_name`, `source_page`, `chunk_text_preview`, `chunk_strategy_id`.
  - Không trả citation nếu chunk không có provenance hợp lệ.
- Implement `log_trace`:
  - Ghi `experiment_id`, `ExperimentConfig`, `retrieval_trace`, sources, latency vào Langfuse.
  - Nếu request là ablation run, chuẩn bị payload để ghi vào `experiment_runs`.

**Deliverable:** Citation map đúng và mọi trace có experiment metadata.  
**Depends on:** W4-RAG-09, W3-INGEST-05  
**Done when:** Một answer test map đúng source chunk, và Langfuse trace hiển thị `experiment_id`/config.

***

### W4-RAG-11 — FastAPI `/chat` config-aware và cache policy

**When:** Tuần 4, ngày 5  
**Môi trường:** 💻 **Local**  
**What to do:**
- Implement `POST /chat`:
  - Nhận `{chart_id, user_id, query, messages, experiment_id?}`.
  - Load chart data từ Supabase.
  - Load `ExperimentConfig`: default production nếu không có `experiment_id`; config cụ thể nếu có.
  - Khởi tạo `RAGState` và invoke LangGraph.
  - Trả về `{answer, sources, rewritten_query, experiment_id, retrieval_trace?}`.
- Cache:
  - Production có thể cache theo `chart_id + normalized_query + top_context_ids`.
  - Request có `experiment_id` phải disable cache.

**Deliverable:** `/chat` chạy production config và experiment config.  
**Depends on:** W4-RAG-10  
**Done when:** `curl` không có `experiment_id` chạy default; `curl` có `experiment_id` chạy config riêng và không dùng cache.

***

### W4-ABL-01 — `AblationRunner` skeleton

**When:** Tuần 4, ngày 5  
**Môi trường:** 💻 **Local**  
**What to do:**
- Viết `evaluation/ablation_runner.py`:
  - Nhận dataset path, experiment config path/list, output directory.
  - Với mỗi experiment, gọi `/chat` hoặc invoke graph trực tiếp với cache disabled.
  - Lưu raw response, sources, retrieval trace, latency.
  - Ghi summary metric placeholder để W6 nối vào evaluator thật.
- Tạo thư mục `configs/experiments/`:
  - `default_production.yaml`
  - `retrieval_dense_only.yaml`
  - `retrieval_sparse_only.yaml`
  - `retrieval_graph_only.yaml`

**Deliverable:** `AblationRunner` chạy được smoke test trên 2 query mock và 2 config.  
**Depends on:** W4-RAG-11  
**Done when:** Runner tạo output JSONL theo experiment và không dùng cache.

***

## Tuần 5 — Tích hợp frontend và chat UI

Mục tiêu: Frontend kết nối đầy đủ với backend. Người dùng có thể chat với production config; luồng experiment chỉ dùng cho evaluation/dev, không phơi ra UI người dùng thường.

***

### W5-FE-01 — Kết nối proxy Next.js `/api/chat` tới FastAPI

**When:** Tuần 5, ngày 1–2  
**Môi trường:** 💻 **Local**  
**What to do:**
- Implement Next.js API route `/api/chat` như proxy đúng nghĩa tới FastAPI:
  - Đính kèm session token.
  - Forward `chart_id`, `query`, `messages`.
  - Không expose lựa chọn experiment trong UI người dùng thường.
  - Cho phép forward `experiment_id` chỉ khi request đến từ evaluation/dev mode có guard rõ ràng.
  - Handle lỗi từ FastAPI và trả structured error response cho frontend.
- Xử lý Render cold start: retry sau 3 giây nếu request đầu tiên timeout.
- Thêm loading state vào `ChatInterface.tsx`.

**Deliverable:** `/api/chat` của Next.js proxy được tới FastAPI và trả answer + sources.  
**Depends on:** W4-RAG-11, W1-FE-01  
**Done when:** Gõ message trong browser sẽ kích hoạt toàn bộ RAG pipeline và hiển thị phản hồi.

***

### W5-FE-02 — Chat UI đầy đủ

**When:** Tuần 5, ngày 1–3  
**Môi trường:** 💻 **Local**  
**What to do:**
- Implement `ChatInterface.tsx`:
  - Danh sách message cho user và assistant.
  - Input text + nút gửi.
  - Hiển thị full-response cho MVP hoặc streaming nếu kịp.
  - Loading indicator khi chờ phản hồi.
  - Hiển thị “System warming up…” và retry khi cold start timeout.
  - Lưu lịch sử chat vào `chat_sessions.messages` sau mỗi lần tương tác.
  - Load message cũ khi mở trang.

**Deliverable:** Chat UI hoàn chỉnh. Message được lưu và load lại từ Supabase.  
**Depends on:** W5-FE-01, W1-DB-01  
**Done when:** User gửi message, nhận phản hồi, refresh trang và vẫn thấy toàn bộ lịch sử chat.

***

### W5-FE-03 — Citation panel

**When:** Tuần 5, ngày 2–3  
**Môi trường:** 💻 **Local**  
**What to do:**
- Implement `SourceCitationPanel.tsx`:
  - Hiển thị danh sách citation cho assistant response gần nhất.
  - Mỗi citation hiển thị: tên sách nguồn, số trang, và đoạn preview ngắn.
  - Có thể collapse/expand.
  - Tự cập nhật khi có response mới.

**Deliverable:** Citation hiển thị trong UI sau mỗi câu trả lời. Citation khớp dữ liệu trong `source_chunks`.  
**Depends on:** W5-FE-02, W4-RAG-10  
**Done when:** Ít nhất một answer test hiển thị 2+ citation với đúng tên nguồn và page.

***

### W5-FE-04 — Ghép đầy đủ trang chi tiết chart

**When:** Tuần 5, ngày 3–4  
**Môi trường:** 💻 **Local**  
**What to do:**
- Ghép trang `/chart/[id]` với các component:
  - `ChartSummaryCard.tsx` ở đầu: hiển thị label, thông tin sinh, chart system.
  - `TuViBoard.tsx` hoặc `BatuBoard.tsx` theo `chart_system`.
  - `ChatInterface.tsx` đặt cạnh hoặc dưới board.
  - `SourceCitationPanel.tsx` gắn cùng chat hoặc bên cạnh.
- Bảo đảm render đúng theo `chart_system`.
- Xử lý data thiếu hoặc đang load.

**Deliverable:** Trang `/chart/[id]` hiển thị đầy đủ trải nghiệm: chart board + chat + citations.  
**Depends on:** W2-VIZ-01, W2-VIZ-02, W5-FE-02, W5-FE-03  
**Done when:** Trang full render được với data thật. Cả 3 vùng chính hiển thị đúng.

***

### W5-FE-05 — Tự tạo chat session khi mở chart lần đầu

**When:** Tuần 5, ngày 3–4  
**Môi trường:** 💻 **Local**  
**What to do:**
- Khi load `/chart/[id]`:
  - Query Supabase để xem có row `chat_sessions` nào với `la_so_id = chart_id` không.
  - Nếu chưa có, tự tạo mới (title = label chart, messages = []).
  - Load message hiện có vào `ChatInterface`.
- Bảo đảm một chart chỉ có một chat session: không bao giờ tạo session thứ hai cho cùng chart.

**Deliverable:** Chat session được tự tạo khi mở chart lần đầu. Lần sau load lại đúng session cũ.  
**Depends on:** W5-FE-02, W1-DB-01  
**Done when:** Lần đầu mở chart mới chỉ tạo đúng 1 row trong `chat_sessions`. Lần sau load đúng session đó. Constraint `UNIQUE (la_so_id)` không bao giờ bị vi phạm.

***

### W5-FE-06 — Context windowing: rolling history

**When:** Tuần 5, ngày 4–5  
**Môi trường:** 💻 **Local**  
**What to do:**
- Implement windowing ở frontend:
  - Chỉ gửi 20 message gần nhất trong payload tới `/api/chat`.
  - Nếu message > 20 thì trim phần cũ hơn khi gửi request, nhưng vẫn lưu đủ trong Supabase.
- Implement windowing ở backend:
  - FastAPI `/chat` chỉ dùng 20 message gần nhất từ payload.
- Khi `len(messages) > 30`, dùng Gemini Flash-Lite để tạo summary và lưu vào `chat_sessions.summary`.

**Deliverable:** Prompt history không vượt quá 20 message. Summary được tạo cho chat dài.  
**Depends on:** W5-FE-02, W4-RAG-11  
**Done when:** Test với 30+ message: prompt gửi lên Gemini chỉ có 20 message cuối. Cột summary được cập nhật trong Supabase sau khi vượt ngưỡng.

***

### W5-FE-07 — Error handling và fallback states

**When:** Tuần 5, ngày 5  
**Môi trường:** 💻 **Local**  
**What to do:**
- Định nghĩa và implement các error state:
  - Neo4j không truy cập được: trả message fallback chung, log lỗi vào Langfuse.
  - Gemini vượt quota: trả “Hệ thống đang bận, vui lòng thử lại sau”.
  - Supabase write fail khi lưu chat: retry một lần, sau đó log âm thầm (không chặn UI).
  - Retrieval rỗng: model vẫn phải trả “không đủ dữ liệu trong nguồn hiện tại”.
- Thêm rate limiting cho `/api/chat`: tối đa 10 request/phút cho mỗi `user_id`.

**Deliverable:** Tất cả error state được xử lý. Có rate limiter. Error message thân thiện bằng tiếng Việt.  
**Depends on:** W5-FE-01, W4-RAG-11  
**Done when:** Simulate Neo4j outage thì UI trả message graceful. Gửi 11 request trong 1 phút thì request thứ 11 nhận HTTP 429.

***

## Tuần 6 — Evaluation và ablation run v1

Mục tiêu: Chạy evaluation có hệ thống trên golden dataset, sweep các cấu hình retrieval/rerank/chunking, và dùng metric để quyết định hướng tuning.

***

### W6-EVAL-01 — Tạo golden dataset versioned

**When:** Tuần 6, ngày 1–2  
**Môi trường:** 💻 **Local**  
**What to do:**
- Tạo 50–100 cặp Q&A để đánh giá.
- Phân bổ: 40% factual, 40% interpretive, 20% multi-hop.
- Với mỗi Q&A:
  - `question`
  - `question_type`
  - `difficulty`
  - `chart_id` thật hoặc chart context test.
  - `expected_answer_summary`
  - `required_sources`
  - `gold_context`
- Thêm 5–10 câu adversarial ngoài corpus, yêu cầu hệ thống phải từ chối bằng “không đủ dữ liệu”.
- Lưu dataset thành `evaluation/golden_v1.jsonl`, không ghi đè tùy tiện.
- Ghi `dataset_version = golden_v1` để mọi experiment có thể so sánh lại.

**Deliverable:** `evaluation/golden_v1.jsonl` có 50–100 entry theo schema SPEC v6.  
**Depends on:** W3-INGEST-07  
**Done when:** Dataset được ít nhất 2 thành viên review, có version rõ ràng, và không phụ thuộc vào một chunking strategy cụ thể.

***

### W6-EVAL-02 — Evaluation runner config-aware

**When:** Tuần 6, ngày 2–3  
**Môi trường:** 💻 **Local**  
**What to do:**
- Viết `evaluation/run_eval.py`:
  - Nhận `--dataset`, `--experiment-config`, `--output-dir`.
  - Gọi FastAPI `/chat` hoặc invoke graph trực tiếp với `experiment_id`.
  - Luôn disable cache khi có `experiment_id`.
  - Lưu answer, sources, rewritten query, retrieved context, retrieval trace, latency.
  - Tính RAGAS metrics: Faithfulness, Answer Relevancy, Context Recall.
  - Tính custom metrics: Graph Hit Rate, Citation Coverage.
  - Tính latency metrics: p95 end-to-end, retrieval p95.
  - Xuất results JSONL, summary CSV, và ghi summary vào `experiment_runs`.
- Bảo đảm output include `experiment_id`, `config_hash`, `dataset_version`.

**Deliverable:** Evaluation runner chạy được cho một config bất kỳ và xuất đủ 7 metrics.  
**Depends on:** W6-EVAL-01, W4-ABL-01  
**Done when:** Runner chạy hết 50+ entry không crash, output metric đọc được, và row `experiment_runs` được ghi.

***

### W6-ABL-01 — Định nghĩa experiment matrix v1

**When:** Tuần 6, ngày 2–3  
**Môi trường:** 💻 **Local**  
**What to do:**
- Tạo `configs/experiments/matrix_v1.yaml` với ít nhất 20 experiment được định nghĩa, trong đó tối thiểu 10 experiment runnable trong MVP.
- Matrix phải bao phủ:
  - Baseline production candidate.
  - Dense-only, sparse-only, graph-only.
  - Graph+dense, graph+sparse, dense+sparse, full hybrid.
  - Fusion method: `rrf`, `weighted_sum`, `graph_first`.
  - Reranker bật/tắt.
  - Document grading bật/tắt cho một subset nhỏ.
  - Chunking strategies: Strategy A, B1, B2, B3, C, D.
- Mỗi experiment config phải có tên ổn định, ví dụ `EXP-001_full_hybrid_rrf_rerank`.

**Deliverable:** Experiment matrix v1 và các config YAML tương ứng.  
**Depends on:** W4-EXP-01, W4-ABL-01  
**Done when:** `AblationRunner` đọc được matrix, validate được schema, và liệt kê đúng danh sách experiment.

***

### W6-ABL-02 — Ablation retrieval path, fusion, reranker

**When:** Tuần 6, ngày 3–4  
**Môi trường:** ☁️ **Kaggle**  
**What to do:**
- Chạy `AblationRunner` trên `golden_v1` cho nhóm experiment:
  - Baseline full hybrid.
  - Dense-only.
  - Sparse-only.
  - Graph-only.
  - Dense+sparse.
  - Full hybrid không reranker.
  - Full hybrid với `rrf`, `weighted_sum`, `graph_first`.
- Ghi raw traces và summary metrics.
- Phân loại lỗi:
  - retrieval miss
  - rerank miss
  - source mismatch
  - weak multi-hop
  - latency regression

**Deliverable:** `evaluation/reports/ablation_retrieval_v1.md` và raw results cho từng experiment.  
**Depends on:** W6-EVAL-02, W6-ABL-01  
**Done when:** Có ít nhất 7 experiment retrieval/fusion/reranker được chạy và ghi vào `experiment_runs`.

***

### W6-ABL-03 — Ablation chunking strategy

**When:** Tuần 6, ngày 3–5  
**Môi trường:** ☁️ **Kaggle**  
**What to do:**
- Chọn 1–2 sách đại diện để tránh vượt Neo4j free-tier.
- Với từng strategy:
  - `chunk_structure_parent_child`
  - `chunk_fixed_256`
  - `chunk_fixed_512`
  - `chunk_fixed_1024`
  - `chunk_sentence_merge`
  - `chunk_semantic`
- Chạy ingest subset hoặc dùng namespace/filter `chunk_strategy_id`.
- Chạy evaluation cùng retrieval config ổn định để cô lập ảnh hưởng của chunking.
- So sánh Context Recall, Citation Coverage, Retrieval p95, và lỗi source mismatch.

**Deliverable:** `evaluation/reports/ablation_chunking_v1.md` với bảng so sánh 6 strategy.  
**Depends on:** W3-INGEST-03, W6-EVAL-02  
**Done when:** Có kết quả metric cho đủ 6 chunking strategy hoặc ghi rõ strategy nào bị block vì quota/capacity.

***

### W6-EVAL-03 — Phân tích kết quả và tuning có bằng chứng

**When:** Tuần 6, ngày 4–5  
**Môi trường:** 💻 **Local** + ☁️ **Kaggle**  
**What to do:**
- Tổng hợp kết quả W6-ABL-02 và W6-ABL-03.
- Map metric sang quyết định kỹ thuật:
  - Context Recall thấp → đổi chunking hoặc retrieval mix.
  - Graph Hit Rate thấp → chỉnh entity extraction/canonicalization/hop depth.
  - Faithfulness thấp → siết prompt hoặc context assembly.
  - Citation Coverage thấp → sửa citation map/provenance.
  - Latency cao → giảm path, top-k, reranker threshold, hoặc document grading.
- Chỉ tuning các phần có bằng chứng từ ablation.
- Chạy lại subset experiment bị ảnh hưởng để đo delta.

**Deliverable:** `evaluation/reports/ablation_v1_summary.md` có quyết định tuning và delta metric.  
**Depends on:** W6-ABL-02, W6-ABL-03  
**Done when:** Có ít nhất một vòng tuning dựa trên metric, không chỉ dựa vào cảm tính.

***

### W6-INT-01 — Integration test với production candidate config

**When:** Tuần 6, ngày 5  
**Môi trường:** 💻 **Local**  
**What to do:**
- Chọn một production candidate config tạm thời từ kết quả W6.
- Chạy toàn bộ user journey:
  1. Đăng ký user mới.
  2. Tạo chart Tử Vi.
  3. Mở `/chart/[id]`.
  4. Hỏi 5 câu khác nhau.
  5. Kiểm tra câu trả lời có citation.
  6. Làm lại cho chart Bát Tự.
- Ghi lại bug hoặc luồng bị hỏng thành GitHub Issue.

**Deliverable:** Báo cáo integration test với config ID cụ thể.  
**Depends on:** Toàn bộ W4, W5, W6-EVAL-03  
**Done when:** Full journey pass không có P0/P1; báo cáo ghi rõ `experiment_id`/config được dùng.

***

## Tuần 7 — Ablation v2, chọn config production, deploy và QA

Mục tiêu: Hoàn tất ablation generation/prompt, chọn production config bằng bằng chứng, deploy hệ thống, và kiểm tra monitoring/latency/security.

***

### W7-ABL-01 — Ablation generation model và prompt template

**When:** Tuần 7, ngày 1  
**Môi trường:** ☁️ **Kaggle**  
**What to do:**
- Chạy subset ablation trên top 2–3 retrieval config từ W6.
- So sánh:
  - `generation_model`: Flash-Lite vs Flash nếu quota cho phép.
  - `prompt_template`: `grounded_default` vs `strict_citation`.
  - Context assembly: `parent_child` vs `balanced_sources` nếu W6 cho thấy source dominance.
- Đo Faithfulness, Answer Relevancy, Citation Coverage, p95 latency.

**Deliverable:** `evaluation/reports/ablation_generation_prompt_v1.md`.  
**Depends on:** W6-EVAL-03, W4-RAG-09  
**Done when:** Có kết quả cho ít nhất 4 biến thể generation/prompt và ghi vào `experiment_runs`.

***

### W7-CONFIG-01 — Chọn production config bằng evidence

**When:** Tuần 7, ngày 1–2  
**Môi trường:** 💻 **Local**  
**What to do:**
- Tổng hợp kết quả W6 và W7-ABL-01.
- Chọn `default_production.yaml` cuối cùng dựa trên:
  - Faithfulness >= 0.80 hoặc gần target nhất.
  - Answer Relevancy >= 0.75 hoặc gần target nhất.
  - Context Recall >= 0.70 hoặc gần target nhất.
  - Citation Coverage >= 0.90 hoặc có mitigation rõ.
  - p95 end-to-end <= 8s và retrieval p95 <= 3s, hoặc có trade-off được ghi rõ.
- Ghi rationale vào `evaluation/reports/production_config_decision.md`.
- Update `configs/experiments/default_production.yaml` với config được chọn.

**Deliverable:** Production config được chọn dựa trên metric, không phải giả định.  
**Depends on:** W7-ABL-01  
**Done when:** Report có bảng so sánh experiment, decision, trade-off, và config ID final.

***

### W7-DEPLOY-01 — Deploy backend FastAPI lên Render

**When:** Tuần 7, ngày 2  
**Môi trường:** 🌐 **Cloud**  
**What to do:**
- Cấu hình `render.yaml` hoặc Render dashboard:
  - Build command: `pip install -r requirements.txt`
  - Start command: `uvicorn main:app --host 0.0.0.0 --port 8000`
  - Set env vars: Neo4j URI, Gemini key, Supabase keys, Langfuse keys, `DEFAULT_EXPERIMENT_CONFIG`.
- Deploy và verify `/health` trả 200 từ URL Render.
- Verify backend load đúng `default_production.yaml`.
- Verify CORS cho phép frontend Vercel.
- Test cold start.

**Deliverable:** FastAPI live trên Render với production config đã chọn.  
**Depends on:** W7-CONFIG-01, W4-RAG-11  
**Done when:** `/health` trả 200 và một `/chat` production request trả answer + sources + trace có config ID.

***

### W7-DEPLOY-02 — Deploy frontend Next.js lên Vercel

**When:** Tuần 7, ngày 2  
**Môi trường:** 🌐 **Cloud**  
**What to do:**
- Kết nối project Vercel với repo frontend.
- Set env vars: Supabase URL/keys, FastAPI URL, Langfuse public key nếu dùng phía client.
- Deploy và verify app load được ở URL Vercel.
- Cấu hình redirect URL Supabase Auth cho production domain.
- Test login, tạo chart, và chat từ URL live.

**Deliverable:** Next.js app live trên Vercel. Full user flow chạy từ production URL.  
**Depends on:** W7-DEPLOY-01, W5-FE-04  
**Done when:** User journey đăng ký → tạo chart → chat chạy được bằng production config.

***

### W7-OBS-01 — Theo dõi Langfuse cho pipeline và experiment

**When:** Tuần 7, ngày 2–3  
**Môi trường:** 🌐 **Cloud**  
**What to do:**
- Bảo đảm Langfuse trace được phát ra cho mọi request chat:
  - Root trace: toàn bộ `/chat`.
  - Spans: query_rewrite, entity_extraction, graph_retrieval, dense_retrieval, sparse_retrieval, fusion, rerank, document_grading nếu bật, context_assembly, generation.
  - Mỗi span log input/output summary, model, latency, token usage nếu có.
  - Trace có `experiment_id`, `config_hash`, `chunk_strategy_id`.
- Tạo dashboard cơ bản cho RPD usage, average latency, error rate, và experiment comparison.

**Deliverable:** Langfuse dashboard hiển thị trace production và experiment metadata.  
**Depends on:** W7-DEPLOY-01, W4-RAG-10  
**Done when:** Gửi 3 query test từ UI production tạo ra 3 trace đầy đủ, có config ID.

***

### W7-OBS-02 — Đo p95 latency cho production config

**When:** Tuần 7, ngày 3  
**Môi trường:** 🌐 **Cloud**  
**What to do:**
- Gửi 20 query test qua production system, mix simple và complex.
- Ghi end-to-end latency, retrieval latency, generation latency.
- Tính p95.
- So sánh target: p95 end-to-end <= 8s, p95 retrieval <= 3s.
- Nếu vượt target, dùng trace để tối ưu top-k, reranker threshold, context budget, hoặc tắt node có cost cao.

**Deliverable:** Báo cáo latency cho production config final.  
**Depends on:** W7-OBS-01  
**Done when:** p95 được đo và report ghi rõ pass/fail theo target.

***

### W7-QA-01 — Sprint fix bug

**When:** Tuần 7, ngày 3–5  
**Môi trường:** 💻 **Local** / 🌐 **Cloud**  
**What to do:**
- Review toàn bộ GitHub Issue mở từ W6-INT-01 và deploy.
- Ưu tiên: P0 (chặn core user journey), P1 (làm yếu feature chính), P2 (cosmetic/minor).
- Fix toàn bộ bug P0 và P1.
- Test lại production config sau khi fix.

**Deliverable:** Tất cả bug P0/P1 được fix và xác nhận.  
**Depends on:** W6-INT-01, W7-DEPLOY-01, W7-DEPLOY-02  
**Done when:** Không còn P0/P1 mở; P2 được ghi vào post-MVP backlog.

***

### W7-QA-02 — Kiểm tra cross-browser và mobile responsive

**When:** Tuần 7, ngày 4  
**Môi trường:** 🌐 **Cloud**  
**What to do:**
- Test app trên:
  - Chrome latest.
  - Safari latest.
  - Mobile browser iOS Safari hoặc Android Chrome.
- Kiểm tra layout, chart board, chat input, citation panel.
- Ghi lại mọi lỗi hiển thị.

**Deliverable:** Báo cáo test theo browser/device.  
**Depends on:** W7-DEPLOY-02  
**Done when:** App sử dụng được trên các browser đã test; lỗi layout nghiêm trọng được mở P1 issue.

***

### W7-SEC-01 — Checklist review bảo mật

**When:** Tuần 7, ngày 4–5  
**Môi trường:** 🌐 **Cloud**  
**What to do:**
- Xác nhận RLS Supabase chặn truy cập chéo user.
- Xác nhận `experiment_runs` không lộ dữ liệu user hoặc prompt nhạy cảm cho client.
- Xác nhận env vars nằm trong Vercel/Render secrets, không hardcode.
- Xác nhận rate limiter FastAPI hoặc proxy route hoạt động.
- Xác nhận frontend không nhận raw stack trace khi lỗi.
- Xác nhận Supabase anon key không bị dùng sai cho operation server-side.

**Deliverable:** Checklist bảo mật hoàn thành và sign off.  
**Depends on:** W7-DEPLOY-01, W7-DEPLOY-02  
**Done when:** Tất cả mục checklist pass hoặc có mitigation đã merge.

***

## Tuần 8 — Buffer, polish, final evaluation và demo

Mục tiêu: Hệ thống ổn định, có báo cáo ablation cuối cùng, production config được khóa, và demo thể hiện cả sản phẩm lẫn quyết định kỹ thuật dựa trên evidence.

***

### W8-POLISH-01 — Polish UX

**When:** Tuần 8, ngày 1–2  
**Môi trường:** 💻 **Local**  
**What to do:**
- Cải thiện empty state: dashboard không có chart, chart chưa có chat history.
- Cải thiện error message: tiếng Việt dễ hiểu, không lộ stack trace.
- Thêm feedback thành công khi tạo chart.
- Cải thiện loading state cho chat, citation panel, cold start, và retry.
- Sửa lỗi visual phát hiện ở W7-QA-02.

**Deliverable:** App đủ chỉn chu cho demo production flow.  
**Depends on:** W7-QA-01  
**Done when:** Team review xác nhận luồng chính dễ dùng, không còn lỗi UI nghiêm trọng.

***

### W8-DOCS-01 — Viết tài liệu developer và ablation

**When:** Tuần 8, ngày 1–3  
**Môi trường:** 💻 **Local**  
**What to do:**
- Viết hoặc hoàn thiện:
  - `README.md`: tổng quan dự án, cách chạy local, biến môi trường.
  - `docs/architecture.md`: kiến trúc hệ thống và LangGraph config-aware.
  - `docs/ingestion-guide.md`: cách ingest sách mới, cách chọn `chunk_strategy_id`.
  - `docs/ablation-guide.md`: `ExperimentConfig`, experiment matrix, cách chạy `AblationRunner`.
  - `docs/model-choices.md`: reranker, embedding, LLM, prompt templates.
  - `docs/evaluation-guide.md`: golden dataset, metrics, cách đọc report.
  - `docs/production-config.md`: config final và rationale.

**Deliverable:** Docs đủ để developer mới hiểu cả production pipeline lẫn ablation workflow.  
**Depends on:** W7-CONFIG-01  
**Done when:** Một thành viên không viết docs có thể chạy evaluation hoặc một experiment nhỏ theo hướng dẫn.

***

### W8-EVAL-01 — Chạy evaluation cuối cùng trên production config

**When:** Tuần 8, ngày 2–3  
**Môi trường:** ☁️ **Kaggle**  
**What to do:**
- Chạy `run_eval.py` trên production system với `default_production.yaml`.
- So sánh với target trong SPEC Section 19.3.
- Ghi final metrics:
  - Faithfulness
  - Answer Relevancy
  - Context Recall
  - Graph Hit Rate
  - Citation Coverage
  - p95 End-to-End Latency
  - Retrieval p95
- Tạo `evaluation/report_final.md`.

**Deliverable:** Báo cáo metric cuối cùng cho production config.  
**Depends on:** W6-EVAL-02, W7-DEPLOY-01  
**Done when:** Report có đủ 7 metric, pass/fail rõ ràng, và có link tới config final.

***

### W8-ABL-01 — Đóng gói báo cáo ablation cuối cùng

**When:** Tuần 8, ngày 2–4  
**Môi trường:** 💻 **Local**  
**What to do:**
- Tổng hợp W6 và W7 reports thành `evaluation/ablation_final_report.md`.
- Xác nhận tối thiểu 10 experiment đã chạy và có kết quả trong `experiment_runs`.
- Báo cáo phải có:
  - Experiment matrix.
  - Bảng metric theo experiment.
  - Kết luận về chunking strategy.
  - Kết luận về retrieval path/fusion/reranker.
  - Kết luận về generation model/prompt template.
  - Production config final và lý do chọn.
  - Các experiment bị hoãn vì quota/capacity.

**Deliverable:** `evaluation/ablation_final_report.md`.  
**Depends on:** W8-EVAL-01, W7-CONFIG-01  
**Done when:** Báo cáo chứng minh production config được chọn dựa trên evidence và có ít nhất 10 experiment đã chạy.

***

### W8-DEMO-01 — Chuẩn bị demo

**When:** Tuần 8, ngày 3–5  
**Môi trường:** 🌐 **Cloud**  
**What to do:**
- Chuẩn bị demo script cho user journey:
  1. Đăng ký và đăng nhập.
  2. Tạo chart Tử Vi.
  3. Xem bảng 12 cung.
  4. Hỏi 3 câu demo: factual, interpretive, multi-hop.
  5. Hiển thị citation panel.
  6. Tạo chart Bát Tự và hỏi lại một câu.
- Chuẩn bị slide hoặc phần nói ngắn về ablation:
  - Strategy chunking nào đang dùng.
  - Vì sao chọn production config.
  - Metric nào đạt/chưa đạt.
- Chạy thử demo script ít nhất 2 lần.
- Chuẩn bị 2–3 câu hỏi dự phòng nếu query live bị lỗi.
- Đảm bảo demo account có sẵn chart.

**Deliverable:** Demo script, demo account, và tóm tắt ablation decision.  
**Depends on:** W8-POLISH-01, W8-ABL-01  
**Done when:** Demo end-to-end chạy được trong một lần dry run và team giải thích được config final.

***

## Danh sách deliverables

| ID | Deliverable | Tuần |
|----|-------------|------|
| D-01 | Tất cả cloud services được provision, `.env.example` được commit | W1 |
| D-02 | Supabase schema, RLS, và seed script được áp dụng | W1 |
| D-03 | Neo4j constraint, vector index, fulltext index được tạo | W1 |
| D-04 | Supabase Auth hoạt động trong Next.js | W1 |
| D-05 | FastAPI skeleton chạy với cấu hình Render | W1 |
| D-06 | Next.js app shell với đầy đủ routes và placeholder components | W1 |
| D-07 | Tử Vi engine được tích hợp và test | W2 |
| D-08 | Bát Tự engine được tích hợp | W2 |
| D-09 | Luồng tạo và lưu chart end-to-end | W2 |
| D-10 | TuViBoard và BatuBoard hiển thị dữ liệu thật | W2 |
| D-11 | Dashboard hiển thị chart đã lưu | W2 |
| D-12 | PDF extraction và normalization script | W3 |
| D-13 | Chunking framework strategy-aware với `chunk_strategy_id` | W3 |
| D-14 | 6 chunking strategy v6 được implement | W3 |
| D-15 | Entity extraction giữ provenance theo chunk strategy | W3 |
| D-16 | Graph write và Supabase provenance strategy-aware | W3 |
| D-17 | Embedding/fulltext index filter được theo `chunk_strategy_id` | W3 |
| D-18 | Baseline ingest bằng Strategy A cho 1–2 sách đại diện | W3 |
| D-19 | Incremental ingestion và capacity guard theo strategy | W3 |
| D-20 | Migration `experiment_runs` và `ExperimentConfig` schema | W4 |
| D-21 | LangGraph/RAGState config-aware được compile | W4 |
| D-22 | Query rewrite toggle hoạt động | W4 |
| D-23 | Entity extraction runtime có toggle/model override | W4 |
| D-24 | Graph retrieval filter được theo config/hop depth/strategy | W4 |
| D-25 | Dense và sparse retrieval bật/tắt độc lập | W4 |
| D-26 | Fusion dispatcher hỗ trợ `rrf`, `weighted_sum`, `graph_first` | W4 |
| D-27 | Reranker và document grading có toggle | W4 |
| D-28 | Context assembly strategies hoạt động | W4 |
| D-29 | Generation model và prompt template routing | W4 |
| D-30 | Citation mapping và Langfuse trace có experiment metadata | W4 |
| D-31 | FastAPI `/chat` config-aware và cache disabled cho experiment | W4 |
| D-32 | `AblationRunner` skeleton chạy được | W4 |
| D-33 | Next.js chat proxy nối tới FastAPI production config | W5 |
| D-34 | Chat UI đầy đủ với lưu lịch sử | W5 |
| D-35 | Citation panel trong UI | W5 |
| D-36 | Trang chi tiết chart hoàn chỉnh | W5 |
| D-37 | Auto-create chat session khi mở chart lần đầu | W5 |
| D-38 | Context windowing + summary generation | W5 |
| D-39 | Error handling + rate limiting | W5 |
| D-40 | Golden dataset `golden_v1.jsonl` | W6 |
| D-41 | Evaluation runner config-aware ghi `experiment_runs` | W6 |
| D-42 | Experiment matrix v1 với tối thiểu 20 config định nghĩa | W6 |
| D-43 | Ablation retrieval/fusion/reranker v1 | W6 |
| D-44 | Ablation chunking strategy v1 | W6 |
| D-45 | Báo cáo tuning dựa trên ablation evidence | W6 |
| D-46 | Integration test với production candidate config | W6 |
| D-47 | Ablation generation model và prompt template | W7 |
| D-48 | Production config final được chọn bằng metric | W7 |
| D-49 | Backend FastAPI deploy lên Render với config final | W7 |
| D-50 | Frontend Next.js deploy lên Vercel | W7 |
| D-51 | Langfuse trace live có experiment/config metadata | W7 |
| D-52 | p95 latency production config được đo | W7 |
| D-53 | Tất cả bug P0/P1 được fix | W7 |
| D-54 | Cross-browser/mobile QA hoàn tất | W7 |
| D-55 | Checklist bảo mật hoàn tất | W7 |
| D-56 | UX polish hoàn tất | W8 |
| D-57 | Developer docs và ablation docs hoàn tất | W8 |
| D-58 | Báo cáo evaluation cuối cùng cho production config | W8 |
| D-59 | Báo cáo ablation cuối cùng với ít nhất 10 experiment đã chạy | W8 |
| D-60 | Demo script và rehearsal demo | W8 |

## Cách chạy hệ thống

### Chạy local trên laptop

Dùng cách này cho toàn bộ phần phát triển thường ngày: frontend, backend, auth, chart engine, RAG graph, và smoke test experiment nhỏ. Máy không cần GPU, vì các model lớn đều gọi qua API ngoài, còn cross-encoder reranker có thể chạy CPU trong quá trình dev. [sbert](https://sbert.net/docs/cross_encoder/usage/efficiency.html)

1. Khởi động các dịch vụ cloud trước: Supabase, Neo4j AuraDB, Langfuse, Render, và Vercel theo biến môi trường trong `.env.example`.
2. Chạy backend FastAPI local bằng `uvicorn`.
3. Chạy frontend Next.js local bằng `npm run dev`.
4. Kiểm tra `/health`, đăng nhập, tạo chart, rồi vào `/chart/[id]` để test chat bằng `default_production.yaml`.
5. Nếu cần test ingestion nhỏ, chạy từng script local trên một file PDF mẫu trước khi đưa lên Kaggle.
6. Nếu cần test ablation nhỏ, chạy `AblationRunner` trên 2–3 câu trong `golden_v1` với 1–2 config để kiểm tra schema và trace.

### Chạy trên Kaggle Free Tier

Dùng Kaggle cho các công việc nặng, đặc biệt là ingest hàng loạt và evaluation nhiều mẫu. Kaggle Free Tier hiện có T4 GPU, 29GB RAM và 4 CPU cores, phù hợp để tăng tốc embedding, rerank, và chạy batch pipeline. [lilys](https://lilys.ai/notes/en/google-tpu-20251128/free-kaggle-gpu-29gb-4-cpu-update)

1. Chỉ đẩy các task nặng lên Kaggle: `W3-INGEST-03` đến `W3-INGEST-07`, `W6-ABL-02`, `W6-ABL-03`, `W7-ABL-01`, `W8-EVAL-01`, và các batch evaluation lớn.
2. Chuẩn bị sẵn file input từ local: chunk JSON, entity JSON, experiment config YAML, hoặc `evaluation/golden_v1.jsonl`.
3. Chạy notebook Kaggle theo từng bước của pipeline, rồi ghi kết quả về Neo4j và Supabase qua secret keys.
4. Sau khi ingest hoặc ablation xong, quay lại local để chạy app và xác minh dữ liệu/metrics đã đồng bộ về Neo4j, Supabase, và `experiment_runs`.
5. Không dùng Kaggle để host app hay database; Kaggle chỉ nên là nơi xử lý batch, không phải nơi chạy hệ thống live. [reddit](https://www.reddit.com/r/LocalLLaMA/comments/17bhwtj/kaggle_upgraded_their_free_tier_to_t4_with_29gb/)

### Cách phối hợp giữa local và Kaggle

- Local là nơi viết code, test nhanh, và nối frontend-backend.
- Kaggle là nơi xử lý batch nặng, rồi đẩy kết quả về cloud DB.
- Supabase và Neo4j phải là nơi lưu trữ trung tâm để cả local lẫn Kaggle cùng đọc/ghi được.
- Sau mỗi lần chạy Kaggle, hãy sync lại state vào Neo4j/Supabase rồi kiểm tra lại bằng app local.
- Khi deploy xong, production vẫn chạy trên Render + Vercel; Kaggle chỉ còn dùng cho ingestion, ablation batch, hoặc evaluation lại khi cần. [lilys](https://lilys.ai/notes/en/google-tpu-20251128/free-kaggle-gpu-29gb-4-cpu-update)

### Quy trình khuyến nghị

1. Xây và test code local.
2. Chạy ingestion nhỏ local để kiểm tra logic.
3. Chạy smoke test `ExperimentConfig` và `AblationRunner` local.
4. Chuyển batch lớn sang Kaggle.
5. Đồng bộ kết quả vào Neo4j, Supabase, và `experiment_runs`.
6. Chọn `default_production.yaml` dựa trên report ablation.
7. Chạy lại app local để xác minh.
8. Deploy production lên Render và Vercel.
