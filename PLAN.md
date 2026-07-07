# Kế Hoạch Công Việc: Hệ Thống Hỏi Đáp Tử Vi với Hybrid GraphRAG

**Dựa trên:** Specification v7.1
**Phiên bản:** 4.1
**Ngày:** 2026-06-29
**Thời gian thực hiện:** 7-8 tuần
**Định dạng:** Task chia theo tuần, không gán theo thành viên. Team tự phân công nội bộ.

***

## Cách đọc tài liệu này

- Mỗi task có mã duy nhất dạng `W[tuần]-[nhóm]-[số]`, ví dụ `W1-INFRA-01`.
- **When:** thời điểm cần làm task.
- **Môi trường:** Local, Kaggle hoặc Cloud.
- **What to do:** việc cần thực hiện cụ thể.
- **Deliverable:** đầu ra có thể kiểm tra.
- **Depends on:** task phải hoàn thành trước.
- **Done when:** tiêu chí hoàn thành rõ ràng.

***

## Tuần 1 - Nền tảng và hạ tầng

Mục tiêu: cloud services được tạo, repo skeleton chạy local, schema Tử Vi-only được áp dụng.

### W1-INFRA-01 - Tạo tất cả dịch vụ cloud

**When:** Ngày 1-2
**Môi trường:** Cloud

**What to do:**
- Tạo Supabase project free tier và lưu URL, anon key, service key.
- Tạo Neo4j AuraDB Free instance.
- Tạo project Vercel cho frontend.
- Tạo service Render cho FastAPI backend Python 3.11.
- Tạo project Langfuse.
- Tạo `.env.example` chung cho toàn bộ biến môi trường.

**Deliverable:** Cloud services hoạt động và `.env.example` được commit.
**Depends on:** -
**Done when:** Team kết nối được tới từng service từ local bằng env vars.

### W1-INFRA-02 - Thiết lập cấu trúc repo

**When:** Ngày 1-2
**Môi trường:** Local

**What to do:**
- Chuẩn hóa cấu trúc frontend/backend trong repo.
- Chuẩn hóa Next.js 14 + TypeScript frontend.
- Chuẩn hóa FastAPI backend Python 3.11.
- Thiết lập `.gitignore`, README chạy local, branch strategy và secrets policy.
- Bảo đảm frontend chạy bằng `npm run dev`, backend chạy bằng `uvicorn`.

**Deliverable:** Repo chạy local theo README.
**Depends on:** W1-INFRA-01
**Done when:** Thành viên mới clone repo và chạy cả hai app local trong vòng 10 phút.

### W1-DB-01 - Áp dụng schema Supabase và RLS

**When:** Ngày 2-4
**Môi trường:** Cloud

**What to do:**
- Viết migration cho `profiles`, `la_so`, `chat_sessions`, `source_chunks`.
- Thêm `UNIQUE (la_so_id)` trên `chat_sessions`.
- Giữ cột `chart_system` nhưng đặt `DEFAULT 'TUVI' CHECK (chart_system = 'TUVI')`.
- Đặt `domain TEXT DEFAULT 'TUVI' CHECK (domain = 'TUVI')` cho `source_chunks`.
- Thêm index cho `user_id`, `la_so_id`, `chunk_id`, `chunk_hash`, `chunk_strategy_id`.
- Viết RLS cho `profiles`, `la_so`, `chat_sessions`.
- Thêm trigger `updated_at`.
- Viết seed SQL tạo test user, một lá số Tử Vi test và một chat session test.

**Deliverable:** Migration và seed script được commit, RLS được test thủ công.
**Depends on:** W1-INFRA-01
**Done when:** User không đọc được dữ liệu của user khác và schema chỉ cho phép `TUVI`.

### W1-DB-02 - Khởi tạo schema và index Neo4j

**When:** Ngày 3-5
**Môi trường:** Cloud

**What to do:**
- Tạo uniqueness constraint cho `Sao`, `Cung`, `ThienCan`, `DiaChi`, `NguHanh`, `Chunk`.
- Tạo vector index cho `Chunk.embedding`.
- Tạo fulltext index cho `Chunk.text`, `Chunk.title`, `Chunk.keywords`.
- Bảo đảm mọi node/chunk runtime có `domain = 'TUVI'`.
- Commit Cypher setup vào `/infra/neo4j/`.

**Deliverable:** Neo4j có constraint, vector index và fulltext index.
**Depends on:** W1-INFRA-01
**Done when:** `SHOW INDEXES` xác nhận vector/fulltext index online.

### W1-AUTH-01 - Tích hợp Supabase Auth trong Next.js

**When:** Ngày 3-5
**Môi trường:** Local

**What to do:**
- Cài Supabase client libraries.
- Tạo login/register pages.
- Tạo server/client Supabase helpers.
- Tạo middleware bảo vệ route.
- Tạo logout flow.

**Deliverable:** Auth hoạt động ở local.
**Depends on:** W1-DB-01, W1-INFRA-02
**Done when:** User đăng ký, đăng nhập, truy cập dashboard protected và đăng xuất được.

### W1-API-01 - Tạo skeleton FastAPI và health endpoint

**When:** Ngày 3-5
**Môi trường:** Local

**What to do:**
- Tạo router `GET /health`, `POST /chart/tuvi`, `POST /chat`.
- Cấu hình CORS cho Vercel frontend và `localhost:3000`.
- Thêm config bằng `pydantic-settings`.
- Thêm Langfuse client stub.
- Thêm `Dockerfile` hoặc `render.yaml`.

**Deliverable:** FastAPI chạy local và có deploy config.
**Depends on:** W1-INFRA-01, W1-INFRA-02
**Done when:** `GET /health` trả 200.

### W1-FE-01 - Tạo app shell và routing Next.js

**When:** Ngày 3-5
**Môi trường:** Local

**What to do:**
- Tạo routes `/`, `/dashboard`, `/chart/[id]`.
- Cài Tailwind CSS, shadcn/ui và Zustand.
- Tạo placeholder `TuViBoard.tsx`, `ChatInterface.tsx`, `ChartSummaryCard.tsx`, `SourceCitationPanel.tsx`.
- Tạo `POST /api/chat` proxy stub tới FastAPI.

**Deliverable:** App shell có routing và component placeholder.
**Depends on:** W1-AUTH-01, W1-INFRA-02
**Done when:** Login xong vào được dashboard và chart route không 404.

***

## Tuần 2 - Engine Tử Vi, chart schema và visualizer

Mục tiêu: engine Tử Vi được tích hợp, kiểm chứng sâu hơn, output chuẩn hóa và board 12 cung hiển thị dữ liệu thật.

### W2-ENGINE-01 - Tích hợp engine Tử Vi

**When:** Tuần 2, ngày 1-3
**Môi trường:** Local

**What to do:**
- Thêm `doanguyen/lasotuvi` và `pyvnlunar` vào backend dependencies.
- Implement `POST /chart/tuvi` nhận `{birth_date, birth_time, gender, label}`.
- Chuẩn hóa output thành internal schema ổn định.
- Xử lý lỗi ngày không hợp lệ, giờ không hợp lệ, thiếu field.

**Deliverable:** Endpoint trả chart JSON hợp lệ.
**Depends on:** W1-API-01
**Done when:** Endpoint được test với ít nhất 5 input khác nhau.

### W2-ENGINE-02 - Unit test độ chính xác engine Tử Vi

**When:** Tuần 2, ngày 2-4
**Môi trường:** Local

**What to do:**
- Chọn ít nhất 5 ngày giờ sinh có reference đã kiểm chứng.
- Viết test placement chính tinh theo cung.
- Viết test metadata quan trọng: âm/dương lịch, cục, mệnh, thân nếu engine cung cấp.
- Ghi report sai lệch và quyết định xử lý.

**Deliverable:** `tests/test_tuvi_engine.py` và test report.
**Depends on:** W2-ENGINE-01
**Done when:** Placement chính tinh pass hoặc sai lệch có giải thích được ghi lại.

### W2-SCHEMA-01 - Chuẩn hóa schema lá số Tử Vi

**When:** Tuần 2, ngày 2-4
**Môi trường:** Local

**What to do:**
- Viết `docs/chart-schema.md` cho Tử Vi-only.
- Định nghĩa shape cho metadata, 12 cung, sao, vận hạn và raw engine payload nếu cần.
- Đặt `chart_type = "TUVI"` và `chart_version = "tuvi-v1"`.
- Bảo đảm schema đủ ổn định để frontend render và RAG đọc chart context.

**Deliverable:** Chart schema Tử Vi được ghi thành docs.
**Depends on:** W2-ENGINE-01
**Done when:** Backend response và frontend type cùng bám schema này.

### W2-FLOW-01 - Luồng tạo và lưu lá số end-to-end

**When:** Tuần 2, ngày 3-5
**Môi trường:** Local

**What to do:**
- Xây form tạo lá số mới với fields: label, birth date, birth time, gender.
- Submit gọi `POST /chart/tuvi`.
- Lưu chart JSON và metadata vào `la_so` qua Supabase.
- Luôn ghi `chart_system = 'TUVI'`.
- Redirect sang `/chart/[new_id]`.
- Xử lý loading và error state.

**Deliverable:** User tạo và lưu được lá số Tử Vi từ UI.
**Depends on:** W2-ENGINE-01, W1-DB-01
**Done when:** Tạo lá số sinh đúng một row trong `la_so` và redirect đúng.

### W2-VIZ-01 - TuViBoard 12 cung

**When:** Tuần 2, ngày 3-5
**Môi trường:** Local

**What to do:**
- Implement `TuViBoard.tsx` bằng SVG/React.
- Render đúng 12 cung, tên cung, vị trí và danh sách sao.
- Bảo đảm layout responsive desktop/mobile.
- Tạo fallback state khi chart data thiếu phần cung.

**Deliverable:** `TuViBoard.tsx` render dữ liệu thật.
**Depends on:** W2-FLOW-01, W2-SCHEMA-01
**Done when:** Board hiển thị đúng 12 cung cho chart test đã kiểm chứng.

### W2-DASH-01 - Dashboard danh sách lá số

**When:** Tuần 2, ngày 4-5
**Môi trường:** Local

**What to do:**
- Implement `/dashboard`.
- Lấy toàn bộ `la_so` của user hiện tại.
- Hiển thị mỗi lá số bằng `ChartSummaryCard`.
- Có empty state và nút tạo lá số mới.
- Click card đi tới `/chart/[id]`.

**Deliverable:** Dashboard hiển thị lá số đã lưu.
**Depends on:** W2-FLOW-01, W1-AUTH-01
**Done when:** User thấy đúng dữ liệu của mình và empty state rõ ràng.

***

## Tuần 3 - Ingestion pipeline Tử Vi

Mục tiêu: có pipeline extract, normalize, chunk, annotate và index corpus Tử Vi theo hướng strategy-aware.

### W3-INGEST-01 - Script extract và normalize PDF

**When:** Tuần 3, ngày 1-2
**Môi trường:** Local

**What to do:**
- Viết `scripts/extract_pdf.py`.
- Detect text-based hay scanned.
- Extract text theo trang bằng `pdfplumber` hoặc `pymupdf`.
- Normalize Unicode NFC, bỏ header/footer/page number, xóa khoảng trắng thừa.
- Output `{page, text}` theo JSON.
- Đánh dấu `needs_ocr` nếu page có text quá ít.

**Deliverable:** Script extract PDF tạo text sạch theo trang.
**Depends on:** -
**Done when:** Test trên ít nhất 2 file trong `data/tuvi`.

### W3-INGEST-02 - Chunking framework và 3 strategy đại diện

**When:** Tuần 3, ngày 1-3
**Môi trường:** Local hoặc Kaggle

**What to do:**
- Rework `scripts/chunk_text.py` và `configs/chunking_strategies.yaml` để 3 strategy đại diện là nguồn chính thức cho baseline/ablation:
  - `chunk_fixed_512` làm fixed-size baseline.
  - `chunk_structure_parent_child` làm structure-aware parent-child.
  - `chunk_semantic_embedding` làm embedding-based semantic chunking chuẩn.
- Giữ `chunk_semantic` cũ chỉ như lexical topic-shift legacy experiment nếu chưa dùng embedding similarity.
- Output contract bắt buộc: `chunk_id`, `parent_id`, `chunk_type`, `chunk_text`, `text`, `source_id`, `source_name`, `source_page`, `domain`, `chunk_strategy_id`, `chunk_hash`, `char_start`, `char_end`, `token_count`, `provenance`, `metadata.strategy_config_snapshot`.
- Bảo đảm `chunk_hash` stable và bao gồm `chunk_strategy_id`, chunking version, source provenance và text span.
- Parent-child policy: generate parent + child, giữ `parent_id`, chuẩn bị edge `HAS_PARENT`/`CONTAINS_CHILD`, và đánh dấu child là đơn vị retrieval mặc định.
- Semantic embedding policy: atomize sentence/paragraph, embed atoms, cắt theo cosine similarity/topic shift với min/target/max tokens, và ghi `embedding_model_for_chunking`, `semantic_similarity_threshold`, `semantic_break_score`.

**Deliverable:** Chunking framework chạy được 3 strategy đại diện và xuất evidence summary.
**Depends on:** W3-INGEST-01
**Done when:** `chunk_fixed_512` deterministic; parent-child map đúng; `chunk_semantic_embedding` có similarity report; mọi strategy giữ stable hash, provenance đầy đủ và `<strategy>_chunk_summary.json`.

### W3-INGEST-03 - Strategy mở rộng cho ablation phụ

**When:** Tuần 3, ngày 2-4
**Môi trường:** Local

**What to do:**
- Giữ hoặc bổ sung các strategy mở rộng: `chunk_fixed_256`, `chunk_fixed_1024`, `chunk_sentence_merge`, `chunk_semantic` legacy lexical.
- Không dùng các strategy này làm baseline chính nếu chưa có evidence tốt hơn bộ 3 đại diện.
- Viết smoke test để bảo đảm output contract/provenance giống W3-INGEST-02.

**Deliverable:** Strategy mở rộng chạy được khi cần ablation phụ.
**Depends on:** W3-INGEST-02
**Done when:** Cùng một input xuất được chunk JSON hợp lệ cho strategy mở rộng, không phá contract của 3 strategy đại diện.

### W3-INGEST-04 - Entity extraction hybrid evidence-first

**When:** Tuần 3, ngày 3-5
**Môi trường:** Local hoặc Kaggle

**What to do:**
- Rework entity extraction thành hybrid:
  - dictionary/rule-first cho thuật ngữ Tử Vi cố định;
  - LLM augmentation cho entity khó, ambiguous cases và `LuanGiai`;
  - merge/dedupe dictionary + LLM output theo `entity_type + canonical_name + span`.
- Extract taxonomy: `Sao`, `Cung`, `ThienCan`, `DiaChi`, `NguHanh`, `ToHop`, `QuanHeCung`, `TrangThaiSao`, `TuHoa`, `VanHan`, `DaiHan`, `CucBanMenh`, `KhaiNiem`, `LuanGiai`.
- `LuanGiai` chỉ là interpretive claim có evidence, ví dụ `X chủ về Y`, `X thì Y`, `gặp X thì Y`, `nên luận là Y`, `có nghĩa là Y`.
- Mỗi entity giữ `chunk_id`, `chunk_hash`, `chunk_strategy_id`, `source_id`, `source_page`, `section_id`, `char_start`, `char_end`, `evidence_text`, `entity_dict_version`, `prompt_version`, `extraction_model`, `extraction_run_id`.
- Với `chunk_structure_parent_child`, mặc định extract child only; parent chỉ dùng context expansion trừ khi config bật parent-level extraction.
- Thêm resume/skip processed chunks và partial summary khi quota/lỗi batch xảy ra.

**Deliverable:** Entity JSONL strategy-aware, evidence-only, canonicalized, resumable.
**Depends on:** W3-INGEST-02
**Done when:** `<strategy>_entity_review.json` và extraction summary pass; sample tối thiểu 20 chunks/strategy được review; mọi entity có provenance/span hợp lệ; không có entity hoặc `LuanGiai` suy diễn ngoài văn bản gốc.

### W3-INGEST-05 - Validated graph provenance và relation extraction

**When:** Tuần 3, ngày 4-5
**Môi trường:** Local hoặc Kaggle

**What to do:**
- Rework graph/provenance writer để ghi chunks, sources, canonical entities, mentions, evidence relations và canonical relation aggregation vào Neo4j + Supabase.
- Ghi source chunk provenance vào Supabase với đủ metadata citation.
- `MERGE` canonical entity theo `canonical_name + entity_type + domain`; `MERGE` chunk theo `chunk_hash`.
- Ghi relation MVP: `MENTIONS`, `THUOC_CUNG`, `DOI_CHIEU`, `LIEN_KE`, `GIAI_THICH`, `APPLIES_TO`, `RELATED_TO`, `LUU_Y`, `HAS_SOURCE`, `HAS_CHUNK`, `HAS_PARENT`, `CONTAINS_CHILD`.
- Mọi relation extracted phải giữ `chunk_id`, `chunk_hash`, `chunk_strategy_id`, `source_id`, `source_page`, `evidence_text`, `relation_source = rule|llm|ontology`, `relation_subtype`, `confidence`, `extraction_run_id`.
- Thêm relation type-pair schema validation, ví dụ `THUOC_CUNG` chỉ cho `Sao|ToHop|TuHoa|TrangThaiSao|CucBanMenh -> Cung`.
- Dùng hybrid relation extraction: rule trước, LLM chỉ bổ sung relation giữa entity có sẵn, ontology chỉ cho quan hệ nền ổn định.
- Tạo relation review report với evidence samples, invalid/drop counts và relation counts theo type/source/chunk_type.
- Với local-Kaggle path, `write_graph_provenance.py` phải export portable payload qua `--payload-output-dir` để local import lại mà không chạy lại relation LLM.

**Deliverable:** Graph, relation và provenance strategy-aware được ghi đúng, reviewable.
**Depends on:** W3-INGEST-04, W1-DB-02
**Done when:** Query Neo4j từ entity truy được chunk/source; parent-child edge expand được parent; relation type-pair validation pass; relation sample review không có relation suy diễn ngoài evidence; Supabase `source_chunks` có provenance đủ cho citation; local-Kaggle path có `payloads/<strategy>/` importable mà không cần chạy lại LLM.

### W3-INGEST-06 - Strategy-aware embedding và retrieval indexing

**When:** Tuần 3, ngày 4-5
**Môi trường:** Local hoặc Kaggle

**What to do:**
- Tạo embedding cho chunk theo strategy-aware policy.
- Dùng cùng Neo4j DB nhưng tách embedding slot hoàn toàn:
  - Gemini baseline: `Chunk.embedding` + `chunkVector` + `768`
  - Local-Kaggle BGE-M3: `Chunk.embedding_bge_m3` + `chunkVectorBgeM3` + `1024`
- Flat strategies như `chunk_fixed_512` và `chunk_semantic_embedding`: embed toàn bộ chunks hợp lệ.
- Parent-child strategy: embed/retrieve `chunk_type = "child"` mặc định; parent được fetch bằng `parent_id` trong parent expansion.
- Ghi embedding vào Neo4j theo đúng slot, kèm metadata riêng cho slot đó: `embedding_model`, `embedding_dim`, `embedded_at`, `embedding_text_hash`, `title`, `keywords`.
- Fulltext metadata dùng source/section title và canonical entity names từ `MENTIONS` làm keywords.
- Retrieval smoke phải kiểm tra dense, sparse, filter theo `chunk_strategy_id`, filter theo `chunk_type`, và parent expansion diagnostics.
- Local-Kaggle path phải sinh embedding JSONL artifact, import lại bằng script riêng và smoke retrieval theo `--embedding-slot bge_m3`.

**Deliverable:** Dense và sparse index hoạt động theo strategy, child-only parent-child policy và parent expansion.
**Depends on:** W3-INGEST-05
**Done when:** `embed_<source>_<strategy>.json` có `completed=true`; `retrieval_<source>_<strategy>.json` có dense/sparse hits, source/strategy/chunk_type đúng và parent expansion diagnostics pass với parent-child strategy; slot `bge_m3` import/retrieval hoạt động mà không đụng baseline Gemini.

### W3-INGEST-07 - Full corpus baseline ingest với 3 strategy đại diện

**When:** Tuần 3, ngày 5
**Môi trường:** Local hoặc Kaggle

**What to do:**
- Dùng toàn bộ 4 sách Tử Vi nền đã chuẩn hóa trong `benchmark/tuvi_golden_dataset/corpus`: `TVKL`, `TVNL`, `TVHS`, `TVGM`.
- Không xóa hoặc rebuild corpus nền; chỉ tạo lại dữ liệu derived từ chunk/entity/relation/embedding/index.
- Branch policy for W3-INGEST-04..07:
  - `rule-only`: dictionary/rule entity extraction and rule relation extraction; no LLM calls for W3-INGEST-04/05.
  - `gemini-call`: official Gemini API branch for both entity extraction and relation extraction.
  - `local-kaggle`: keep Kaggle/Qwen notebook artifacts unchanged as a comparison branch.
- Gemini quota policy:
  - batch entity and relation calls with `--llm-batch-size 4`;
  - default per-key throttle is `--requests-per-minute 15`;
  - run W3-INGEST-04 Gemini entity first, wait for quota recovery, then run W3-INGEST-05 Gemini relation.
- Default branch artifacts:
  - `benchmark/tuvi_golden_dataset/rule_only/{entities,payloads,reports}/`;
  - `benchmark/tuvi_golden_dataset/gemini_call/{entities,payloads,reports,state}/`;
  - `notebooks/w3_local_outputs/` remains the local-Kaggle comparison output.
- Đường vận hành hiện tại để hoàn tất W3 là local-Kaggle artifact path:
  - chunking/entity/relation/embedding chạy trên Kaggle
  - graph payload và embedding artifacts được tải về local
  - local import vào Neo4j/Supabase và chạy retrieval smoke
- Chạy pipeline từ chunk đến index cho 3 strategy vận hành hiện tại:
  - `chunk_fixed_512`
  - `chunk_structure_parent_child`
  - `chunk_semantic_embedding_bge_m3`
- Với mỗi source-strategy pair, chạy chunking, entity extraction, graph/provenance writer, embedding và retrieval smoke theo artifact/import flow chính thức.
- Ghi số page, chunk, node, relation, Supabase `source_chunks`, embedding và retrieval smoke theo từng `source_id + chunk_strategy_id`.
- Review tối thiểu 20 chunk/entity/relation sample cho mỗi strategy.
- Evidence folder phải có `<strategy>_chunk_summary.json`, `<strategy>_semantic_similarity_report.json` khi áp dụng, `<strategy>_entity_review.json`, `<strategy>_relation_review.json`, `<strategy>_graph_write_summary.json`, `embed_<source>_<strategy>.json`, `retrieval_<source>_<strategy>.json`, và `payloads/<strategy>/`.

**Deliverable:** Full corpus Tử Vi đã ingest với 3 strategy đại diện.
**Depends on:** W3-INGEST-06
**Done when:** Có payload importable cho mọi strategy cần import; có embedding artifact theo slot `bge_m3`; local import graph payload và embeddings không gọi lại LLM; retrieval smoke pass với `--embedding-slot bge_m3`; local laptop không cần GPU để hoàn tất ingest/runtime query embedding.

***

## Tuần 4 - Core RAG pipeline và ExperimentConfig

Mục tiêu: LangGraph config-aware chạy được với retrieval paths, fusion, rerank, context assembly và generation.

### W4-EXP-01 - Schema `experiment_runs` và `ExperimentConfig`

**When:** Tuần 4, ngày 1
**Môi trường:** Local + Cloud

**What to do:**
- Tạo migration `experiment_runs`.
- Định nghĩa `ExperimentConfig` bằng Python model và YAML schema.
- Các field tối thiểu: retrieval toggles, chunking strategy, fusion method, reranker config, prompt template, generation model, context strategy, cache disabled flag.
- Tạo `default_production.yaml`.

**Deliverable:** Experiment config có schema và default.
**Depends on:** W1-DB-01
**Done when:** Config load được và validate fail rõ khi thiếu field bắt buộc.

### W4-RAG-01 - RAGState và LangGraph config-aware

**When:** Tuần 4, ngày 1-2
**Môi trường:** Local

**What to do:**
- Implement `RAGState`.
- Thêm node load chart context.
- Thêm node load config.
- Compile graph với nodes placeholder đầy đủ.
- Bảo đảm `chart_type` và `domain_filter` luôn là `TUVI`.

**Deliverable:** LangGraph compile và chạy dry-run.
**Depends on:** W4-EXP-01
**Done when:** Dry-run trả trace state qua toàn pipeline.

### W4-RAG-02 - Query rewrite và entity extraction toggles

**When:** Tuần 4, ngày 2
**Môi trường:** Local

**What to do:**
- Implement query rewrite node.
- Implement entity extraction runtime node.
- Cả hai đọc toggle/model override từ config.
- Guardrail không mở rộng ngoài Tử Vi.

**Deliverable:** Rewrite/extraction bật tắt được.
**Depends on:** W4-RAG-01
**Done when:** Cùng query chạy được với toggle on/off và trace ghi rõ khác biệt.

### W4-RAG-03 - Retrieval paths config-aware

**When:** Tuần 4, ngày 2-3
**Môi trường:** Local

**What to do:**
- Implement graph retrieval.
- Implement dense retrieval.
- Implement sparse retrieval.
- Mỗi path có top-k, filters, chunk strategy và timeout config riêng.
- Trả candidate format thống nhất.

**Deliverable:** Ba retrieval path bật/tắt độc lập.
**Depends on:** W4-RAG-02, W3-INGEST-06
**Done when:** Path disabled không chạy, path enabled trả candidates có provenance.

### W4-RAG-04 - Fusion, rerank và document grading toggle

**When:** Tuần 4, ngày 3-4
**Môi trường:** Local

**What to do:**
- Implement fusion dispatcher cho `rrf`, `weighted_sum`, `graph_first`.
- Implement reranker wrapper.
- Implement document grading stub/toggle, mặc định off production.
- Log score breakdown vào trace.

**Deliverable:** Candidate ranking có thể đổi theo config.
**Depends on:** W4-RAG-03
**Done when:** Config đổi fusion/rerank tạo output khác và có trace.

### W4-RAG-05 - Context assembly, generation và citations

**When:** Tuần 4, ngày 4-5
**Môi trường:** Local

**What to do:**
- Implement context assembly strategies.
- Implement generation prompt Tử Vi.
- Map citations từ answer về chunk/source.
- Bảo đảm thiếu context thì model nói chưa đủ dữ liệu.
- Ghi trace Langfuse với `experiment_id`, `config_hash`, `chunk_strategy_id`.

**Deliverable:** `/chat` trả answer + sources + trace.
**Depends on:** W4-RAG-04
**Done when:** Một request test trả câu trả lời tiếng Việt có citations hợp lệ.

### W4-ABL-01 - `AblationRunner` skeleton

**When:** Tuần 4, ngày 5
**Môi trường:** Local

**What to do:**
- Implement runner đọc golden dataset và danh sách configs.
- Disable cache khi chạy.
- Ghi `experiment_runs`.
- Xuất report JSON/Markdown.

**Deliverable:** Runner chạy smoke test 2 câu x 2 config.
**Depends on:** W4-RAG-05
**Done when:** Có report và rows trong `experiment_runs`.

***

## Tuần 5 - Tích hợp frontend và chat UI

Mục tiêu: user có thể mở lá số, chat, xem nguồn trích dẫn và nhận feedback rõ khi lỗi/latency.

### W5-FE-01 - Kết nối proxy Next.js `/api/chat`

**When:** Tuần 5, ngày 1
**Môi trường:** Local

**What to do:**
- Implement proxy route gọi FastAPI `/chat`.
- Forward auth/session context cần thiết.
- Chuẩn hóa error response.
- Không lộ backend stack trace.

**Deliverable:** Frontend gọi được backend chat.
**Depends on:** W4-RAG-05
**Done when:** UI nhận answer + sources từ proxy.

### W5-FE-02 - Chat UI đầy đủ

**When:** Tuần 5, ngày 1-3
**Môi trường:** Local

**What to do:**
- Implement message list, input, submit, retry.
- Lưu lịch sử chat vào Supabase.
- Hiển thị trạng thái loading/cold start.
- Disable submit khi request đang chạy.

**Deliverable:** ChatInterface dùng được.
**Depends on:** W5-FE-01
**Done when:** User gửi nhiều câu liên tiếp và lịch sử vẫn đúng.

### W5-FE-03 - Citation panel

**When:** Tuần 5, ngày 2-3
**Môi trường:** Local

**What to do:**
- Implement `SourceCitationPanel`.
- Hiển thị source name, page, excerpt, confidence/score nếu có.
- Click source từ answer mở panel đúng item.
- Hiển thị fallback khi không có nguồn.

**Deliverable:** Người dùng kiểm tra được nguồn.
**Depends on:** W5-FE-02
**Done when:** Mỗi answer có sources hiển thị đúng provenance.

### W5-FE-04 - Ghép đầy đủ trang chi tiết lá số

**When:** Tuần 5, ngày 3-4
**Môi trường:** Local

**What to do:**
- `/chart/[id]` load lá số, render `TuViBoard`, chart summary và chat.
- Auto-create chat session nếu chưa có.
- Bảo vệ route bằng auth.
- Xử lý chart không tồn tại hoặc không thuộc user.

**Deliverable:** Chart detail hoàn chỉnh.
**Depends on:** W5-FE-03, W2-VIZ-01
**Done when:** End-to-end từ dashboard tới chart detail và chat chạy ổn.

### W5-FE-05 - Error handling và rate limiting

**When:** Tuần 5, ngày 4-5
**Môi trường:** Local

**What to do:**
- Thêm backend rate limiter hoặc proxy guard.
- Chuẩn hóa lỗi validation, timeout, quota, no-context.
- UI hiển thị message tiếng Việt dễ hiểu.
- Log lỗi quan trọng vào Langfuse hoặc server logs.

**Deliverable:** Error states không làm vỡ luồng chính.
**Depends on:** W5-FE-04
**Done when:** Test thủ công các lỗi phổ biến đều có feedback rõ.

***

## Tuần 6 - Evaluation và ablation run v1

Mục tiêu: có golden dataset Tử Vi, runner đo metric, experiment matrix v1 và báo cáo tuning có bằng chứng.

### W6-EVAL-01 - Tạo golden dataset versioned

**When:** Tuần 6, ngày 1-2
**Môi trường:** Local

**What to do:**
- Tạo `evaluation/golden_v1.jsonl`.
- Có 50-100 Q&A pairs Tử Vi.
- Mỗi item có question, type, chart context, expected summary, required sources, gold context, difficulty.
- Chia factual, interpretive, multi-hop.
- Validate schema dataset.

**Deliverable:** Golden dataset versioned.
**Depends on:** W3-INGEST-07
**Done when:** Dataset pass validator và có sample đại diện.

### W6-EVAL-02 - Evaluation runner config-aware

**When:** Tuần 6, ngày 2-3
**Môi trường:** Local hoặc Kaggle

**What to do:**
- Implement `run_eval.py`.
- Gọi `/chat` hoặc pipeline trực tiếp theo config.
- Tính Faithfulness, Answer Relevancy, Context Recall, Graph Hit Rate, Citation Coverage, latency.
- Ghi result vào `experiment_runs`.

**Deliverable:** Evaluation runner xuất report.
**Depends on:** W6-EVAL-01, W4-ABL-01
**Done when:** Baseline config chạy hết golden subset và có metric.

### W6-ABL-01 - Định nghĩa experiment matrix v1

**When:** Tuần 6, ngày 3
**Môi trường:** Local

**What to do:**
- Tạo ít nhất 20 config YAML.
- Nhóm theo retrieval path, fusion, reranker, chunking, prompt/model.
- Đặt naming convention ổn định.
- Ghi rationale ngắn cho mỗi config.

**Deliverable:** Experiment matrix v1.
**Depends on:** W4-EXP-01
**Done when:** Runner validate được toàn bộ configs.

### W6-ABL-02 - Ablation retrieval/fusion/reranker

**When:** Tuần 6, ngày 3-4
**Môi trường:** Kaggle hoặc Local

**What to do:**
- Chạy baseline, graph-only, dense-only, sparse-only, dense+sparse, graph+dense, graph+sparse.
- Chạy no-reranker và alternative fusion.
- Ghi metric và latency.
- Phân tích lỗi retrieval miss và rerank miss.

**Deliverable:** Report ablation retrieval v1.
**Depends on:** W6-EVAL-02, W6-ABL-01
**Done when:** Có bảng metric theo experiment và khuyến nghị sơ bộ.

### W6-ABL-03 - Ablation chunking strategy

**When:** Tuần 6, ngày 4-5
**Môi trường:** Kaggle hoặc Local

**What to do:**
- Giữ nguyên full corpus 4 sách đã dùng ở W3-INGEST-07: `TVKL`, `TVNL`, `TVHS`, `TVGM`.
- So sánh chính thức 3 strategy đại diện đã được ingest từ W3:
  - `chunk_fixed_512`
  - `chunk_structure_parent_child`
  - `chunk_semantic_embedding`
- Các strategy mở rộng như `chunk_fixed_256`, `chunk_fixed_1024`, `chunk_sentence_merge`, `chunk_semantic` legacy chỉ chạy thêm nếu còn quota/thời gian và phải báo cáo riêng như ablation phụ.
- Không thay đổi corpus khi so sánh strategy; biến chính của ablation phải là `chunk_strategy_id`.
- Chạy cùng golden subset trên toàn bộ 3 strategy đại diện.
- So sánh Context Recall, Citation Coverage, latency và graph hit.
- Chọn chunking candidate cho production.

**Deliverable:** Report chunking ablation trên cùng full corpus 4 sách.
**Depends on:** W3-INGEST-07, W6-EVAL-02
**Done when:** Có đủ dữ liệu cho 12 cặp source-strategy chính thức, cùng golden dataset/corpus/config được dùng để so sánh 3 strategy đại diện, và có ranking strategy kèm lý do chọn candidate.

### W6-INT-01 - Integration test với production candidate config

**When:** Tuần 6, ngày 5
**Môi trường:** Local

**What to do:**
- Chọn config candidate từ W6.
- Test flow: login, tạo lá số, xem board, hỏi factual, hỏi interpretive, hỏi multi-hop, xem citations.
- Ghi bug P0/P1/P2.

**Deliverable:** Integration test report.
**Depends on:** W6-ABL-02, W6-ABL-03, W5-FE-04
**Done when:** Luồng chính chạy được hoặc bug blocker đã được ghi rõ.

***

## Tuần 7 - Ablation v2, chọn config production, deploy và QA

Mục tiêu: chốt production config bằng evidence, deploy lên Render/Vercel, đo latency, QA và security review.

### W7-ABL-01 - Ablation generation model và prompt template

**When:** Tuần 7, ngày 1
**Môi trường:** Kaggle hoặc Local

**What to do:**
- So sánh model generation candidate.
- So sánh 2-3 prompt template.
- Giữ retrieval config ổn định để cô lập ảnh hưởng generation.
- Đánh giá Faithfulness, Answer Relevancy, Citation Coverage và cost/latency.

**Deliverable:** Report generation/prompt ablation.
**Depends on:** W6-ABL-02, W6-ABL-03
**Done when:** Có prompt/model candidate cuối.

### W7-CONFIG-01 - Chọn production config bằng evidence

**When:** Tuần 7, ngày 1-2
**Môi trường:** Local

**What to do:**
- Tổng hợp reports W6/W7.
- Chọn `default_production.yaml`.
- Ghi rationale theo metric.
- Ghi những experiment chưa chạy vì quota/capacity.
- Lock config hash.

**Deliverable:** Production config final.
**Depends on:** W7-ABL-01
**Done when:** Team đồng ý config final và có evidence đi kèm.

### W7-DEPLOY-01 - Deploy backend FastAPI lên Render

**When:** Tuần 7, ngày 2
**Môi trường:** Cloud

**What to do:**
- Cấu hình build/start command.
- Set env vars: Neo4j, Gemini, Supabase, Langfuse, `DEFAULT_EXPERIMENT_CONFIG`.
- Deploy và verify `/health`.
- Verify backend load đúng production config.
- Test `/chart/tuvi` và `/chat`.

**Deliverable:** Backend live trên Render.
**Depends on:** W7-CONFIG-01
**Done when:** Production `/chat` trả answer + sources + trace.

### W7-DEPLOY-02 - Deploy frontend Next.js lên Vercel

**When:** Tuần 7, ngày 2
**Môi trường:** Cloud

**What to do:**
- Kết nối Vercel với frontend.
- Set env vars Supabase và FastAPI URL.
- Cấu hình Supabase Auth redirect URL.
- Deploy và test production user flow.

**Deliverable:** Frontend live trên Vercel.
**Depends on:** W7-DEPLOY-01, W5-FE-04
**Done when:** User journey đăng ký, tạo lá số, xem chart, chat chạy được trên production URL.

### W7-OBS-01 - Theo dõi Langfuse cho pipeline và experiment

**When:** Tuần 7, ngày 2-3
**Môi trường:** Cloud

**What to do:**
- Trace root cho toàn bộ `/chat`.
- Span cho rewrite, extraction, retrieval paths, fusion, rerank, context assembly, generation.
- Log model, latency, token usage nếu có.
- Trace có `experiment_id`, `config_hash`, `chunk_strategy_id`.
- Tạo dashboard cơ bản cho RPD usage, latency, error rate, experiment comparison.

**Deliverable:** Langfuse dashboard có trace production.
**Depends on:** W7-DEPLOY-01
**Done when:** 3 query production tạo 3 trace đầy đủ.

### W7-OBS-02 - Đo p95 latency production config

**When:** Tuần 7, ngày 3
**Môi trường:** Cloud

**What to do:**
- Gửi 20 query test mix simple/complex.
- Ghi end-to-end latency, retrieval latency, generation latency.
- Tính p95.
- So sánh target end-to-end <= 8s, retrieval <= 3s.
- Tối ưu top-k, reranker threshold hoặc context budget nếu cần.

**Deliverable:** Latency report.
**Depends on:** W7-OBS-01
**Done when:** p95 được đo và pass/fail rõ.

### W7-QA-01 - Sprint fix bug

**When:** Tuần 7, ngày 3-5
**Môi trường:** Local + Cloud

**What to do:**
- Review toàn bộ P0/P1/P2 từ integration và deploy.
- Fix P0/P1.
- Test lại production config.

**Deliverable:** Bug P0/P1 được xử lý.
**Depends on:** W6-INT-01, W7-DEPLOY-01, W7-DEPLOY-02
**Done when:** Không còn P0/P1 mở.

### W7-QA-02 - Cross-browser và mobile responsive

**When:** Tuần 7, ngày 4
**Môi trường:** Cloud

**What to do:**
- Test Chrome, Safari, mobile browser.
- Kiểm tra dashboard, TuViBoard, chat input, citation panel.
- Ghi lỗi layout.

**Deliverable:** Browser/device QA report.
**Depends on:** W7-DEPLOY-02
**Done when:** App dùng được trên các browser đã test.

### W7-SEC-01 - Checklist review bảo mật

**When:** Tuần 7, ngày 4-5
**Môi trường:** Cloud

**What to do:**
- Xác nhận RLS chặn truy cập chéo user.
- Xác nhận `experiment_runs` không lộ dữ liệu nhạy cảm cho client.
- Xác nhận env vars không hardcode.
- Xác nhận rate limiter hoạt động.
- Xác nhận frontend không hiển thị raw stack trace.
- Xác nhận service role chỉ dùng server-side.

**Deliverable:** Security checklist hoàn thành.
**Depends on:** W7-DEPLOY-01, W7-DEPLOY-02
**Done when:** Checklist pass hoặc có mitigation đã merge.

***

## Tuần 8 - Buffer, polish, final evaluation và demo

Mục tiêu: hệ thống ổn định, docs đầy đủ, final evaluation và ablation report sẵn sàng cho demo.

### W8-POLISH-01 - Polish UX

**When:** Tuần 8, ngày 1-2
**Môi trường:** Local

**What to do:**
- Cải thiện empty state dashboard và chart chưa có chat history.
- Cải thiện error message tiếng Việt.
- Thêm success feedback khi tạo lá số.
- Cải thiện loading state cho chat, citation panel, cold start, retry.
- Sửa lỗi visual phát hiện ở QA.

**Deliverable:** UX đủ chỉn chu cho demo.
**Depends on:** W7-QA-01
**Done when:** Team review xác nhận luồng chính dễ dùng.

### W8-DOCS-01 - Viết tài liệu developer và ablation

**When:** Tuần 8, ngày 1-3
**Môi trường:** Local

**What to do:**
- Hoàn thiện README chạy local.
- Viết `docs/architecture.md`.
- Viết `docs/ingestion-guide.md`.
- Viết `docs/ablation-guide.md`.
- Viết `docs/model-choices.md`.
- Viết `docs/evaluation-guide.md`.
- Viết `docs/production-config.md`.

**Deliverable:** Docs đủ cho developer mới.
**Depends on:** W7-CONFIG-01
**Done when:** Một thành viên khác chạy được evaluation nhỏ theo docs.

### W8-EVAL-01 - Chạy evaluation cuối cùng

**When:** Tuần 8, ngày 2-3
**Môi trường:** Kaggle hoặc Local

**What to do:**
- Chạy `run_eval.py` với `default_production.yaml`.
- Ghi final metrics: Faithfulness, Answer Relevancy, Context Recall, Graph Hit Rate, Citation Coverage, p95 end-to-end, retrieval p95.
- Tạo `evaluation/report_final.md`.

**Deliverable:** Final evaluation report.
**Depends on:** W6-EVAL-02, W7-DEPLOY-01
**Done when:** Report có đủ metric và pass/fail rõ.

### W8-ABL-01 - Đóng gói báo cáo ablation cuối cùng

**When:** Tuần 8, ngày 2-4
**Môi trường:** Local

**What to do:**
- Tổng hợp W6/W7 reports thành `evaluation/ablation_final_report.md`.
- Xác nhận tối thiểu 10 experiment đã chạy.
- Báo cáo gồm experiment matrix, metric table, kết luận chunking, retrieval, fusion, reranker, generation, prompt và production config final.

**Deliverable:** Final ablation report.
**Depends on:** W8-EVAL-01, W7-CONFIG-01
**Done when:** Production config được chứng minh bằng evidence.

### W8-DEMO-01 - Chuẩn bị demo

**When:** Tuần 8, ngày 3-5
**Môi trường:** Cloud

**What to do:**
- Chuẩn bị demo script:
  1. Đăng ký và đăng nhập.
  2. Tạo lá số Tử Vi.
  3. Xem bảng 12 cung.
  4. Hỏi 3 câu demo: factual, interpretive, multi-hop.
  5. Hiển thị citation panel.
  6. Mở Langfuse trace hoặc report ablation để giải thích config final.
- Chuẩn bị demo account có sẵn lá số.
- Chạy dry run ít nhất 2 lần.
- Chuẩn bị câu hỏi dự phòng nếu query live lỗi.

**Deliverable:** Demo script, demo account và tóm tắt ablation decision.
**Depends on:** W8-POLISH-01, W8-ABL-01
**Done when:** Demo end-to-end chạy được trong dry run.

***

## Danh sách deliverables

| ID | Deliverable | Tuần |
|----|-------------|------|
| D-01 | Cloud services và `.env.example` hoàn thành | W1 |
| D-02 | Supabase schema Tử Vi-only, RLS và seed script | W1 |
| D-03 | Neo4j constraint, vector index, fulltext index | W1 |
| D-04 | Supabase Auth hoạt động trong Next.js | W1 |
| D-05 | FastAPI skeleton với `/health`, `/chart/tuvi`, `/chat` | W1 |
| D-06 | Next.js app shell với routing và placeholder components | W1 |
| D-07 | Tử Vi engine tích hợp và test | W2 |
| D-08 | Chart schema Tử Vi `tuvi-v1` | W2 |
| D-09 | Luồng tạo/lưu lá số end-to-end | W2 |
| D-10 | TuViBoard 12 cung hiển thị dữ liệu thật | W2 |
| D-11 | Dashboard hiển thị lá số đã lưu | W2 |
| D-12 | PDF extraction và normalization script | W3 |
| D-13 | Chunking framework strategy-aware | W3 |
| D-14 | 3 chunking strategy đại diện được implement và có evidence | W3 |
| D-15 | Entity extraction Tử Vi có provenance | W3 |
| D-16 | Graph write và Supabase provenance strategy-aware | W3 |
| D-17 | Embedding/fulltext index filter theo `chunk_strategy_id` | W3 |
| D-18 | Full corpus baseline ingest với 3 strategy đại diện | W3 |
| D-19 | Migration `experiment_runs` và `ExperimentConfig` schema | W4 |
| D-20 | LangGraph/RAGState config-aware | W4 |
| D-21 | Query rewrite và entity extraction toggles | W4 |
| D-22 | Graph, dense và sparse retrieval toggles | W4 |
| D-23 | Fusion dispatcher, reranker và document grading toggle | W4 |
| D-24 | Context assembly, generation và citation mapping | W4 |
| D-25 | `AblationRunner` skeleton | W4 |
| D-26 | Next.js chat proxy | W5 |
| D-27 | Chat UI đầy đủ với lịch sử | W5 |
| D-28 | Citation panel | W5 |
| D-29 | Chart detail page hoàn chỉnh | W5 |
| D-30 | Error handling và rate limiting | W5 |
| D-31 | Golden dataset `golden_v1.jsonl` | W6 |
| D-32 | Evaluation runner config-aware | W6 |
| D-33 | Experiment matrix v1 | W6 |
| D-34 | Ablation retrieval/fusion/reranker v1 | W6 |
| D-35 | Full-corpus chunking ablation trên 3 strategy đại diện | W6 |
| D-36 | Integration test với production candidate | W6 |
| D-37 | Ablation generation model và prompt template | W7 |
| D-38 | Production config final | W7 |
| D-39 | Backend deploy lên Render | W7 |
| D-40 | Frontend deploy lên Vercel | W7 |
| D-41 | Langfuse traces và dashboard | W7 |
| D-42 | p95 latency report | W7 |
| D-43 | Bug P0/P1 được fix | W7 |
| D-44 | Cross-browser/mobile QA | W7 |
| D-45 | Security checklist | W7 |
| D-46 | UX polish | W8 |
| D-47 | Developer docs và ablation docs | W8 |
| D-48 | Final evaluation report | W8 |
| D-49 | Final ablation report | W8 |
| D-50 | Demo script và dry run | W8 |

***

## Cách chạy hệ thống

### Chạy local trên laptop

1. Chuẩn bị env vars theo `.env.example`.
2. Chạy backend FastAPI bằng `uvicorn`.
3. Chạy frontend Next.js bằng `npm run dev`.
4. Kiểm tra `/health`.
5. Đăng nhập, tạo lá số Tử Vi, mở `/chart/[id]`.
6. Gửi câu hỏi chat bằng `default_production.yaml`.
7. Nếu test ingestion nhỏ, chạy extract/chunk/index trên một file trong `data/tuvi`.
8. Nếu test ablation nhỏ, chạy `AblationRunner` trên 2-3 câu và 1-2 config.

### Chạy trên Kaggle Free Tier

Kaggle chỉ dùng cho batch job nặng:

- ingestion nhiều file,
- embedding batch,
- rerank/evaluation batch,
- ablation nhiều config.

Không dùng Kaggle để host app hoặc database. Sau mỗi batch, kết quả cần ghi về Neo4j, Supabase và `experiment_runs`.

### Quy trình khuyến nghị

1. Xây và test code local.
2. Chạy ingestion nhỏ local để kiểm tra logic.
3. Chạy smoke test `ExperimentConfig` và `AblationRunner`.
4. Chuyển batch lớn sang Kaggle nếu cần.
5. Đồng bộ kết quả về Neo4j, Supabase và `experiment_runs`.
6. Chọn `default_production.yaml` dựa trên report ablation.
7. Chạy lại app local để xác minh.
8. Deploy production lên Render và Vercel.
