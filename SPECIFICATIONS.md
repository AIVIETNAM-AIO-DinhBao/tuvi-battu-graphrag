# System Specification: Hệ Thống Hỏi Đáp Tử Vi với Hybrid GraphRAG

**Version:** 7.2
**Date:** 2026-06-30
**Team size:** 4 người
**Budget:** $0 (MVP / free-tier first)

***

## Changelog

### v7.2

- Chốt đường vận hành hiện tại của `W3-INGEST` là local-Kaggle artifact path để hoàn tất ingest khi Gemini quota không đủ ổn định cho full corpus.
- Tách hoàn toàn Gemini và `BAAI/bge-m3` theo embedding slot trong cùng Neo4j:
  - Gemini dùng `Chunk.embedding` + `chunkVector` + `768`.
  - BGE-M3 dùng `Chunk.embedding_bge_m3` + `chunkVectorBgeM3` + `1024`.
- Chuẩn hóa graph payload export/import để Kaggle chỉ sinh artifact, còn local/cloud mới import vào Neo4j/Supabase mà không chạy lại LLM.
- Chốt query embedding runtime local dùng `BAAI/bge-m3` trên CPU qua `DENSE_QUERY_EMBEDDING_BACKEND`, `DENSE_QUERY_EMBEDDING_MODEL`, `DENSE_QUERY_EMBEDDING_DEVICE`, `DENSE_QUERY_EMBEDDING_SLOT`.
- Giữ `chunk_semantic_embedding_bge_m3` là strategy phụ riêng cho local-Kaggle, không đổi tên hay ghi đè baseline `chunk_semantic_embedding`.

### v7.1

- Rework phương pháp ingestion cho `W3-INGEST-02`, `W3-INGEST-04`, `W3-INGEST-05` và `W3-INGEST-06` theo hướng evidence-first, strategy-aware và reviewable.
- Chốt 3 chunking strategy đại diện cho baseline/ablation: `chunk_fixed_512`, `chunk_structure_parent_child`, `chunk_semantic_embedding`.
- Chuẩn hóa parent-child retrieval policy: embed/retrieve child mặc định, expand parent theo `parent_id`, cite child và dùng parent làm context bổ sung.
- Định nghĩa `chunk_semantic_embedding` là semantic chunking chuẩn dựa trên embedding similarity; `chunk_semantic` cũ chỉ là lexical topic-shift experiment nếu chưa được nâng cấp.
- Nâng entity extraction thành hybrid dictionary/rule-first + LLM augmentation, mọi entity/claim phải có evidence span trong `chunk_text`.
- Nâng graph provenance/relation extraction với relation type-pair validation, evidence relation + canonical relation aggregation, parent-child graph edges và relation review artifact.

### v7.0

- Thu hẹp phạm vi chính thức của MVP xuống **Tử Vi-only**.
- Loại bỏ khỏi tài liệu các engine, API route, visualizer, schema option, demo flow, corpus và runtime domain không phục vụ trực tiếp Tử Vi.
- Giữ **Hybrid GraphRAG** và **ablation study framework**, nhưng mọi experiment, dataset, metric, prompt, retrieval filter và production config chỉ áp dụng cho Tử Vi.
- Interface tạo chart chính thức chỉ dùng `POST /chart/tuvi`.
- Cột `chart_system` được giữ để tương thích triển khai, nhưng giá trị hợp lệ duy nhất trong MVP là `TUVI`.

***

## 1. Mục tiêu hệ thống

Xây dựng hệ thống hỏi đáp theo ngữ cảnh lá số dành riêng cho **Tử Vi**. Người dùng có thể tạo lá số, xem lá số 12 cung và trò chuyện với hệ thống để nhận giải thích có trích dẫn nguồn.

MVP tập trung vào:

1. Sinh lá số Tử Vi từ ngày sinh, giờ sinh, giới tính và tên gọi.
2. Hiển thị lá số 12 cung trên web.
3. Hỏi đáp theo lá số hiện tại bằng **Hybrid GraphRAG**, có citations và kiểm soát hallucination.
4. Chạy ablation study để chọn cấu hình retrieval/generation tốt nhất cho domain Tử Vi.

***

## 2. Phạm vi MVP

### 2.1 In-scope

- Đăng ký / đăng nhập bằng Supabase Auth.
- Tạo, lưu và xem lá số Tử Vi.
- Mỗi lá số có đúng một chat session.
- Chat trả lời trong ngữ cảnh lá số hiện tại.
- Retrieval dựa trên chart context + knowledge graph + dense vector + sparse/fulltext.
- Trích dẫn nguồn theo chunk provenance.
- Observability bằng Langfuse.
- Ablation study cho pipeline Tử Vi.

### 2.2 Out-of-scope

- Bất kỳ hệ thống lá số nào ngoài Tử Vi trong MVP.
- Mobile app native.
- Hỗ trợ ngôn ngữ ngoài tiếng Việt.
- Enterprise scale / HA / multi-region.
- Luận đoán vượt phạm vi nguồn Tử Vi đã ingest.
- LLM-based document grading mặc định trong mọi request production.

***

## 3. Engine Tử Vi

### 3.1 Engine chính thức

```text
github.com/doanguyen/lasotuvi | MIT License | Python
```

Engine được tích hợp trong FastAPI backend qua endpoint:

```text
POST /chart/tuvi
```

Request shape:

```json
{
  "birth_date": "1998-05-20",
  "birth_time": "14:30",
  "gender": "male",
  "label": "Lá số mẫu"
}
```

Response được chuẩn hóa thành schema nội bộ ổn định: metadata sinh, 12 cung, danh sách sao, thông tin vận hạn nếu engine cung cấp, `chart_type = "TUVI"` và `chart_version = "tuvi-v1"`.

Yêu cầu kiểm chứng trước go-live:

- Unit test tối thiểu 5 bộ ngày giờ sinh.
- So sánh placement chính tinh và cung với ít nhất 2 nguồn tham chiếu đáng tin cậy.
- Ghi rõ mọi sai lệch trong test report.

***

## 4. Technical stack

### 4.1 Frontend

```text
Framework: Next.js 14 + TypeScript
Styling: Tailwind CSS + shadcn/ui
Visualizer: Plain SVG/React trước, D3.js nếu cần tương tác cao hơn
State: Zustand
Auth: Supabase Auth
Deploy: Vercel Hobby
```

### 4.2 Backend

```text
Framework: FastAPI (Python 3.11)
RAG orchestration: LangGraph
LLM SDK: google-generativeai
Graph driver: neo4j Python driver
Observability: Langfuse
Deploy: Render Free
```

### 4.3 Databases / storage

```text
Graph + Vector + Fulltext: Neo4j AuraDB Free
Relational app data: Supabase PostgreSQL
Trace / auth / sessions: Supabase + Langfuse
```

***

## 5. Kiến trúc hệ thống

```text
┌──────────────────────────────────────────────────────┐
│                 Vercel - Next.js 14                  │
│                                                      │
│  /dashboard                                          │
│  /chart/[id]                                         │
│     ├── TuViBoard                                    │
│     ├── ChartSummaryCard                             │
│     └── ChatInterface                                │
│                                                      │
│  /api/chat              ──► FastAPI proxy            │
└───────────────────────┬──────────────────────────────┘
                        │ REST
┌───────────────────────▼──────────────────────────────┐
│                    Render - FastAPI                  │
│                                                      │
│  /health                                             │
│  /chart/tuvi      ←── doanguyen/lasotuvi             │
│  /chat            ←── LangGraph Hybrid GraphRAG      │
│     ├── Query rewrite                                │
│     ├── Entity extraction                            │
│     ├── Graph retrieval                              │
│     ├── Dense vector retrieval                       │
│     ├── Sparse fulltext retrieval                    │
│     ├── Fusion + rerank                              │
│     ├── Context assembly                             │
│     └── Generation + citations                       │
└───────────────┬────────────────────────┬─────────────┘
                │                        │
        ┌───────▼────────┐       ┌───────▼────────┐
        │ Neo4j AuraDB   │       │ Supabase Free  │
        │ - Knowledge KG │       │ - profiles     │
        │ - Vector index │       │ - la_so        │
        │ - Fulltext idx │       │ - chat_sessions│
        │ - Source graph │       │ - source_chunks│
        └────────────────┘       └────────────────┘
```

Architectural principles:

- Lá số là trung tâm của trải nghiệm.
- Chat luôn gắn với `chart_id` hiện tại.
- Retrieval phải hiểu quan hệ khái niệm trong graph, bắt đúng thuật ngữ chuyên ngành bằng sparse retrieval và giữ semantic recall bằng dense retrieval.
- MVP ưu tiên độ đúng, citations và khả năng đo lường hơn latency tối thiểu.
- Thành phần có thể thay thế trong pipeline phải có toggle để phục vụ ablation.

***

## 6. Luồng dữ liệu chính

```text
User nhập ngày/giờ sinh
    │
    ▼
FastAPI /chart/tuvi → lasotuvi → Tử Vi JSON chuẩn hóa
    │
    ▼
Lưu Supabase (la_so, chart_system = 'TUVI')
    │
    ▼
User mở /chart/[id]
    │
    ▼
TuViBoard hiển thị 12 cung + ChatInterface
    │
    ▼
Next.js /api/chat → FastAPI /chat
    │
    ▼
LangGraph Hybrid GraphRAG
    ├── Load chart context
    ├── Load ExperimentConfig
    ├── Query rewrite nếu bật
    ├── Entity extraction nếu bật
    ├── Graph retrieval nếu bật
    ├── Dense retrieval nếu bật
    ├── Sparse retrieval nếu bật
    ├── Fusion + rerank
    ├── Context assembly
    └── Generation + citations + Langfuse trace
```

***

## 7. RAG orchestration

### 7.1 RAGState

```python
from typing import TypedDict, Dict, Any, List

class RAGState(TypedDict, total=False):
    query: str
    rewritten_query: str
    query_complexity: str
    chart_id: str
    chart_type: str        # valid value in MVP: "TUVI"
    chart_data: Dict[str, Any]
    user_id: str
    domain_filter: str     # valid value in MVP: "TUVI"

    entities: List[str]
    graph_candidates: List[Dict[str, Any]]
    dense_candidates: List[Dict[str, Any]]
    sparse_candidates: List[Dict[str, Any]]
    fused_candidates: List[Dict[str, Any]]
    reranked_candidates: List[Dict[str, Any]]
    final_context: str

    answer: str
    sources: List[Dict[str, Any]]
    cache_key: str

    experiment_config: "ExperimentConfig"
    experiment_id: str
    retrieval_trace: Dict[str, Any]
```

### 7.2 Node graph

1. Load chart context.
2. Load `ExperimentConfig`.
3. Normalize query.
4. Classify query complexity.
5. Query rewrite nếu `config.query_rewrite_enabled`.
6. Extract entities nếu `config.entity_extraction_enabled`.
7. Chạy song song graph retrieval, dense retrieval và sparse retrieval theo config.
8. Fusion theo `config.fusion_method`.
9. Rerank nếu `config.reranker_enabled`.
10. Document grading nếu `config.document_grading_enabled`.
11. Context assembly theo `config.context_assembly_strategy`.
12. Final generation bằng `config.generation_model`.
13. Citation map + Langfuse trace + ghi `experiment_id`.

Không bắt buộc trong MVP production: document grading mặc định, query decomposition phức tạp và agentic planner nhiều bước.

***

## 8. Retrieval design

Retrieval gồm 2 nhánh lớn chạy song song:

1. **Graph retrieval path:** dùng entity extraction và Cypher để đi theo quan hệ trong knowledge graph Tử Vi.
2. **Hybrid retrieval path:** gồm dense retrieval và sparse/fulltext retrieval, sau đó fuse lại.

Mỗi candidate phải giữ `chunk_id`, `source_id`, `source_page`, `chunk_strategy_id`, score và provenance.

Production default:

- Graph + dense + sparse đều bật.
- Fusion bằng Reciprocal Rank Fusion.
- Reranker bật nếu latency vẫn đạt target.
- Document grading tắt trong production, chỉ bật cho ablation hoặc debug.

***

## 9. Query rewriting policy

Query rewrite chỉ dùng để làm rõ câu hỏi, không mở rộng ngoài domain `TUVI`.

Guardrails:

- Giữ nguyên tên sao, tên cung và thuật ngữ chuyên ngành.
- Không tự thêm luận đoán không có trong câu hỏi.
- Nếu query đã rõ thì giữ nguyên.
- Output rewrite phải trace được trong Langfuse.

***

## 10. Domain và corpus modeling

MVP chỉ có một domain runtime: `TUVI`.

Corpus chính thức:

```text
data/tuvi
benchmark/tuvi_golden_dataset
```

Metadata bắt buộc cho chunk:

- `source_id`
- `source_name`
- `source_page`
- `chunk_id`
- `chunk_hash`
- `chunk_strategy_id`
- `domain = "TUVI"`
- `provenance`

Các khái niệm Thiên Can, Địa Chi, Ngũ Hành vẫn được giữ nếu xuất hiện trong nguồn Tử Vi và có giá trị retrieval, nhưng không tạo domain runtime riêng.

***

## 11. Data model and auth

Business rules:

- Một user có nhiều lá số.
- Một lá số thuộc đúng một user.
- Một lá số có đúng một chat session.
- `chart_system` chỉ nhận `TUVI` trong MVP.

Schema lõi:

```sql
CREATE TABLE la_so (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  label TEXT NOT NULL,
  birth_date DATE NOT NULL,
  birth_time TIME NOT NULL,
  gender TEXT NOT NULL CHECK (gender IN ('male', 'female', 'other')),
  chart_system TEXT NOT NULL DEFAULT 'TUVI' CHECK (chart_system = 'TUVI'),
  chart_data JSONB NOT NULL,
  chart_version TEXT NOT NULL DEFAULT 'tuvi-v1',
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE chat_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  la_so_id UUID NOT NULL UNIQUE REFERENCES la_so(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  summary TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE source_chunks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source_id TEXT NOT NULL,
  source_name TEXT NOT NULL,
  source_page INT,
  chunk_id TEXT NOT NULL,
  chunk_hash TEXT NOT NULL,
  chunk_strategy_id TEXT NOT NULL,
  domain TEXT NOT NULL DEFAULT 'TUVI' CHECK (domain = 'TUVI'),
  text TEXT NOT NULL,
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ DEFAULT now()
);
```

RLS: user chỉ đọc/ghi `profiles`, `la_so`, `chat_sessions` của chính mình. `source_chunks` được ghi bằng service role, client chỉ truy cập qua backend.

***

## 12. Ingestion pipeline

Workflow:

1. Khai báo danh sách nguồn trong corpus Tử Vi.
2. Kiểm tra PDF text-based hay cần OCR.
3. Extract text bằng `pdfplumber` hoặc `pymupdf`.
4. Normalize Unicode tiếng Việt và clean artifacts.
5. Parse cấu trúc sách, chương, mục, trang.
6. Tạo chunks theo strategy đại diện, luôn gắn `domain = "TUVI"`, `chunk_strategy_id`, stable `chunk_hash` và provenance.
7. Extract entity theo cơ chế hybrid dictionary/rule-first + LLM augmentation, evidence-only.
8. Build graph provenance và relation theo schema validated, có evidence relation, canonical relation aggregation và review report.
9. Ghi node/edge/chunk vào Neo4j và source chunk provenance vào Supabase.
10. Tạo embeddings/fulltext metadata theo strategy-aware retrieval policy.
11. Chạy retrieval smoke, sample QA review và ghi evidence artifacts cho từng `source_id + chunk_strategy_id`.

Đường vận hành hiện tại để hoàn tất W3:

- Kaggle chạy batch cho chunk/entity/relation/embedding và chỉ sinh artifact.
- `write_graph_provenance.py --payload-output-dir ...` xuất payload importable trong cả `dry-run` lẫn production artifact mode.
- Local/cloud import graph payload bằng `import_graph_payload.py` và import embeddings bằng `import_embedding_artifacts.py`.
- Local runtime query embedding dùng `BAAI/bge-m3` trên CPU; laptop không cần GPU để phục vụ retrieval/chat runtime.

### 12.1 Chunking strategy policy

Ba strategy đại diện chính thức cho baseline/ablation:

| ID | Strategy | Tag | Purpose |
|----|----------|-----|---------|
| B2 | Fixed-size baseline | `chunk_fixed_512` | Đối chứng token-based đơn giản, deterministic, dễ debug. |
| A | Structure-aware parent-child | `chunk_structure_parent_child` | Retrieve bằng child nhỏ, expand parent để giữ ngữ cảnh dài. |
| D2 | Embedding-based semantic | `chunk_semantic_embedding` | Cắt theo topic shift bằng cosine similarity giữa embedding của sentence/paragraph atoms. |

Các strategy `chunk_fixed_256`, `chunk_fixed_1024`, `chunk_sentence_merge` và `chunk_semantic` có thể giữ làm experiment mở rộng. `chunk_semantic` cũ chỉ được xem là lexical topic-shift vì dùng token overlap/Jaccard; không được gọi là semantic chunking chuẩn nếu chưa dùng embedding similarity.

Output contract bắt buộc cho mọi chunk:

- `chunk_id`
- `parent_id`
- `chunk_type`
- `chunk_text` / `text`
- `source_id`
- `source_name`
- `source_page`
- `domain = "TUVI"`
- `chunk_strategy_id`
- `chunk_hash`
- `char_start`
- `char_end`
- `token_count`
- `provenance`
- `metadata.strategy_config_snapshot`

Parent-child best-practice policy:

- Generate cả parent và child chunks.
- Embed và retrieve `chunk_type = "child"` mặc định.
- Expand parent bằng `parent_id` trong retrieval/context assembly.
- Citation mặc định trỏ về child evidence; parent chỉ dùng làm context bổ sung.
- Graph phải có parent-child edge rõ ràng, ví dụ `HAS_PARENT` hoặc `CONTAINS_CHILD`, thay vì chỉ giữ `parent_id` property.

Embedding-based semantic chunking policy:

- Atomize text thành sentence/paragraph atoms và giữ protected terms không bị cắt vỡ.
- Embed từng atom bằng model embedding cấu hình được.
- Cắt chunk khi cosine similarity/running centroid similarity xuống dưới threshold sau khi đã đạt `min_tokens`, hoặc khi vượt `max_tokens`.
- Lưu metadata tối thiểu: `embedding_model_for_chunking`, `semantic_similarity_threshold`, `semantic_break_score`, `min_tokens`, `target_tokens`, `max_tokens`.
- Ghi `<strategy>_semantic_similarity_report.json` để review phân phối similarity và ngưỡng cắt.

### 12.2 Entity extraction policy

Entity extraction phải giữ provenance theo chunk strategy và chỉ trích các entity có bằng chứng trong `chunk_text`. Taxonomy ingestion gồm:

- `Sao`: chính tinh, phụ tinh và sao lưu niên khi xuất hiện trong nguồn.
- `Cung`: 12 cung chức năng và alias phổ biến như Phối, Bào, Tài, Quan.
- `ThienCan`, `DiaChi`, `NguHanh`: nền tảng can chi, ngũ hành và âm dương.
- `ToHop`: bộ sao/cung có tên như Sát Phá Tham, Cơ Nguyệt Đồng Lương, Không Kiếp, tam hợp Thái Tuế.
- `QuanHeCung`: tam hợp, nhị hợp, chính chiếu, xung chiếu, đồng cung, giáp và tam phương.
- `TrangThaiSao`: Miếu, Vượng, Đắc, Hãm và alias/ký hiệu tương ứng.
- `TuHoa`: Hóa Lộc, Hóa Quyền, Hóa Khoa, Hóa Kỵ.
- `VanHan`, `DaiHan`: vận hạn, đại hạn, tiểu hạn, lưu niên khi có evidence.
- `CucBanMenh`: Cục, bản mệnh, ngũ hành bản mệnh, Âm Dương Nam Nữ.
- `KhaiNiem`: fallback có kiểm soát cho thuật ngữ canonical như vô chính diệu, sinh nhập, sinh xuất, tứ sinh, tứ chính, tứ mộ.
- `LuanGiai`: interpretive claim có evidence, ví dụ cấu trúc `X chủ về Y`, `X thì Y`, `gặp X thì Y`, `nên luận là Y`, `có nghĩa là Y`; không biến mọi đoạn văn dài thành node và không tạo claim do model tự suy ra.

Best-practice extraction policy:

- Chạy deterministic dictionary/rule extractor trước cho thuật ngữ Tử Vi cố định như sao, cung, can/chi, ngũ hành, Tứ Hóa, trạng thái sao và quan hệ cung.
- Dùng LLM augmentation để bổ sung entity khó, ambiguous cases và `LuanGiai`; LLM không được tạo entity không có span/evidence trong text.
- Merge/dedupe dictionary output và LLM output theo `entity_type + canonical_name + char_start + char_end`.
- Mỗi entity giữ `chunk_id`, `chunk_hash`, `chunk_strategy_id`, `source_id`, `source_page`, `section_id`, `char_start`, `char_end`, `evidence_text`, `entity_dict_version`, `prompt_version`, `extraction_model`, `extraction_run_id`.
- Với `chunk_structure_parent_child`, mặc định extract trên child chunks; parent chỉ dùng context expansion, trừ khi config bật parent-level extraction để phục vụ relation analysis.
- Extraction phải resumable: skip chunk đã có complete entity output hợp lệ, ghi partial summary khi quota hoặc lỗi batch xảy ra.

Canonicalization: dùng tên canonical cho sao, cung, thiên can, địa chi, ngũ hành, quan hệ cung, trạng thái sao, Tứ Hóa, Cục/Bản Mệnh và vận hạn; `MERGE` entity theo `canonical_name + entity_type + domain`; `Chunk` dùng `chunk_hash` có bao gồm `chunk_strategy_id`.

### 12.3 Graph provenance and relation extraction policy

Graph writer phải ghi đồng thời:

- Source/chunk provenance phục vụ citation trong Supabase `source_chunks`.
- Evidence-level graph trong Neo4j, gồm `Chunk`, canonical `Entity`, `MENTIONS` và relation có `evidence_text`.
- Canonical relation aggregation cho retrieval, gom các relation cùng `head + relation_type + tail + domain` và giữ evidence count/source coverage.

Relation extraction dùng hybrid policy:

- `rule`: pattern deterministic cho quan hệ cấu trúc rõ.
- `llm`: chỉ bổ sung relation giữa các `entity_id` đã có, không tạo entity mới, phải có evidence text nguyên văn.
- `ontology`: chỉ dùng cho quan hệ nền Tử Vi ổn định như chu kỳ 12 cung và đối cung.
- Mọi relation phải pass whitelist, relation type-pair schema, evidence validation và review sampling.

Required relation artifacts:

- `<strategy>_relation_review.json`
- `<strategy>_graph_write_summary.json`
- relation counts theo `relation_type`, `relation_source`, `chunk_type`, `source_id`

### 12.4 Embedding and retrieval indexing policy

Embedding/indexing phải strategy-aware:

- Flat strategies như `chunk_fixed_512` và `chunk_semantic_embedding`: embed toàn bộ chunks hợp lệ.
- Parent-child strategy: embed/retrieve child chunks mặc định, không embed parent mặc định để tránh vector bị loãng và duplicate retrieval.
- Fulltext metadata phải gồm `title`, source/section hints và canonical entity names từ `MENTIONS` làm `keywords`.
- Dense và sparse retrieval đều phải filter được theo `domain`, `source_id`, `chunk_strategy_id` và `chunk_type` khi cần.
- Smoke retrieval phải ghi diagnostics về total chunks, embedded chunks, text chunks, keyword coverage, parent expansion hit rate.

Embedding slot policy:

- Gemini baseline slot:
  - property: `Chunk.embedding`
  - vector index: `chunkVector`
  - dimension: `768`
- Local-Kaggle BGE-M3 slot:
  - property: `Chunk.embedding_bge_m3`
  - vector index: `chunkVectorBgeM3`
  - dimension: `1024`
- Không trộn metadata, vector property hoặc index giữa hai slot.
- `chunk_semantic_embedding_bge_m3` tiếp tục là strategy phụ riêng cho local-Kaggle path; không ghi đè `chunk_semantic_embedding`.

Official import/retrieval flow sau Kaggle:

1. Chạy notebook Kaggle để sinh `chunks`, `entities`, `payloads`, `embeddings`, `reports`, `state`.
2. Tải artifact về local.
3. Import graph payload mà không gọi lại LLM.
4. Import embedding artifacts vào slot `bge_m3`.
5. Chạy retrieval smoke local với `--embedding-slot bge_m3`.

Runtime query embedding policy:

- Backend runtime local mặc định dùng:
  - `DENSE_QUERY_EMBEDDING_BACKEND=local`
  - `DENSE_QUERY_EMBEDDING_MODEL=BAAI/bge-m3`
  - `DENSE_QUERY_EMBEDDING_DEVICE=cpu`
  - `DENSE_QUERY_EMBEDDING_SLOT=bge_m3`
- CPU local runtime chỉ dùng cho query embedding; không dùng để chạy lại full ingest pipeline nặng.

Expected evidence artifacts:

- `<strategy>_chunk_summary.json`
- `<strategy>_semantic_similarity_report.json` cho `chunk_semantic_embedding`
- `<strategy>_entity_review.json`
- `<strategy>_relation_review.json`
- `<strategy>_graph_write_summary.json`
- `embed_<source>_<strategy>.json`
- `retrieval_<source>_<strategy>.json`

***

## 13. Knowledge graph schema

Node types MVP:

- `Chart`
- `Chunk`
- `Source`
- `Sao`
- `Cung`
- `ToHop`
- `KhaiNiem`
- `LuanGiai`
- `ThienCan`
- `DiaChi`
- `NguHanh`
- `VanHan`
- `DaiHan`
- `QuanHeCung`
- `TrangThaiSao`
- `TuHoa`
- `CucBanMenh`

`LuanGiai` là node claim diễn giải có evidence và phải liên kết về các entity nền như `Sao`, `Cung`, `ToHop` hoặc `QuanHeCung`. `KhaiNiem` chỉ dùng cho thuật ngữ canonical có giá trị retrieval rõ ràng, không dùng như nơi chứa mọi cụm danh từ khó phân loại.

Relation types MVP:

- `THUOC_CUNG`
- `LIEN_KE`
- `GIAI_THICH`
- `DOI_CHIEU`
- `LUU_Y`
- `HAS_SOURCE`
- `HAS_CHUNK`
- `HAS_PARENT`
- `CONTAINS_CHILD`
- `MENTIONS`
- `APPLIES_TO`
- `RELATED_TO`

Graph chỉ giữ relation có giá trị retrieval rõ ràng, tránh quan hệ suy diễn khó debug.

Relation validation policy:

- `THUOC_CUNG`: head thuộc `Sao`, `ToHop`, `TuHoa`, `TrangThaiSao` hoặc `CucBanMenh`; tail phải là `Cung`.
- `DOI_CHIEU`: hai đầu ưu tiên `Cung`; ontology chỉ tạo từ chu kỳ cung đã định nghĩa.
- `LIEN_KE`: dùng cho quan hệ giáp/liền kề giữa cung hoặc entity có evidence rõ.
- `GIAI_THICH`: head là entity nền, tail là `LuanGiai`.
- `APPLIES_TO`: head là `LuanGiai`, tail là entity nền.
- `LUU_Y`: head có thể là `Chunk` hoặc entity cảnh báo, tail là entity được cảnh báo.
- `RELATED_TO`: chỉ dùng khi có pattern/LLM evidence hợp lệ, không dùng co-occurrence rộng.
- `HAS_PARENT` / `CONTAINS_CHILD`: chỉ nối `Chunk` parent-child cùng `source_id`, `chunk_strategy_id` và provenance hợp lệ.

Graph provenance lưu hai lớp quan hệ:

- Evidence relation: từng relation xuất hiện trong một chunk cụ thể, có `chunk_hash`, `source_id`, `source_page`, `evidence_text`, `relation_source`, `relation_subtype`, `confidence`.
- Canonical relation: aggregation theo `head + relation_type + tail + domain`, giữ `evidence_count`, `source_ids`, `chunk_strategy_ids` và confidence tổng hợp để phục vụ graph retrieval.

***

## 14. Capacity và performance

Neo4j working assumptions cho MVP:

- 3-4 sách Tử Vi trọng tâm trong corpus đầu.
- 3,000-4,000 chunks với strategy mặc định.
- 15,000-20,000 graph nodes sau entity extraction mức vừa phải.
- 45,000-60,000 relationships.

Khi chạy ablation chunking, chỉ so sánh 1-2 sách đại diện trước khi mở rộng để giữ an toàn free-tier.

Latency target:

- p95 end-to-end <= 8s.
- p95 retrieval + rerank <= 3s.
- Cache tự tắt khi request thuộc ablation run.

***

## 15. Model routing và prompting

Model routing default:

- Query rewrite, LLM augmentation cho entity/relation extraction và ingestion annotation: Gemini Flash-Lite.
- Simple factual generation: Gemini Flash-Lite nếu query complexity thấp.
- Interpretive và multi-hop generation: Gemini Flash.
- Experiment có thể override model qua `ExperimentConfig`.

Current W3 operational routing:

- Full-corpus W3 ingest hiện hoàn tất theo local-Kaggle path:
  - semantic chunking và dense embeddings: `BAAI/bge-m3`
  - entity/relation augmentation: `Qwen/Qwen2.5-7B-Instruct`
- Gemini được giữ làm baseline/spec reference và production comparison path, không bị xóa khỏi kiến trúc.

Prompt generation phải:

- Bám lá số hiện tại.
- Ưu tiên retrieved context.
- Không suy diễn khi context không đủ.
- Trả lời bằng tiếng Việt.
- Gắn citations theo chunk/source map.
- Nói rõ khi thiếu bằng chứng.

Entity extraction prompt chỉ là lớp augmentation sau dictionary/rule extractor; prompt phải dùng taxonomy Tử Vi, `domain = "TUVI"`, alias phổ biến, rule canonicalization, structured JSON output, evidence span bắt buộc và guardrail không suy diễn entity/claim ngoài văn bản gốc.

***

## 16. Evaluation và ablation

Golden dataset MVP có 50-100 Q&A pairs:

- 40% factual.
- 40% interpretive.
- 20% multi-hop.

Metrics:

| Metric | Target MVP |
|--------|------------|
| Faithfulness | >= 0.80 |
| Answer Relevancy | >= 0.75 |
| Context Recall | >= 0.70 |
| Graph Hit Rate | >= 0.65 |
| Citation Coverage | >= 0.90 |
| p95 End-to-End Latency | <= 8s |
| Retrieval p95 | <= 3s |

Ablation dimensions:

- retrieval paths: graph, dense, sparse
- chunking strategy
- fusion method
- reranker on/off
- query rewriting on/off
- entity extraction on/off
- embedding model
- generation model
- prompt template
- context assembly strategy
- document grading on/off

MVP cần ít nhất 10 experiment đã chạy trước khi chốt production config.

***

## 17. Risk table

| Rủi ro | Tác động | Mitigation |
|-------|----------|------------|
| Gemini quota bị vượt | Full-corpus ingest hoặc request runtime bị gián đoạn | Dùng local-Kaggle artifact path cho ingest batch lớn; giữ Gemini cho baseline/spec và các run nhỏ hơn |
| Render cold start | Latency request đầu tăng mạnh | Loading state rõ, health ping nếu cần |
| Neo4j schema quá phức tạp | Khó maintain/debug | Giữ schema tối giản |
| OCR làm nhiễu dữ liệu | Retrieval quality giảm | Ưu tiên PDF text-based, sample review |
| RLS sai | Lộ dữ liệu user | Test policy trước deploy |
| Citation mapping không ổn định | Khó kiểm tra nguồn | Stable chunk hash + provenance |
| Graph duplicate | Tốn capacity, retrieval nhiễu | Canonicalization + `MERGE` |
| Trộn Gemini và BGE-M3 artifacts | Sai dimension/index, retrieval lỗi ngầm | Tách embedding slot/property/index/dim và giữ strategy phụ riêng cho BGE-M3 |
| Ablation tốn quota | Chậm evaluation | Batch nhỏ, chia nhiều ngày hoặc chuyển sang local-Kaggle artifact path |

***

## 18. MVP success boundary

MVP đạt khi:

1. Người dùng tạo được lá số Tử Vi từ ngày/giờ sinh, giới tính và tên gọi.
2. Người dùng xem được lá số 12 cung trên web.
3. Mỗi lá số có đúng một chat session.
4. Chat trả lời trong phạm vi lá số hiện tại, có citations.
5. Retrieval hoạt động theo hybrid graph + dense + sparse.
6. Evaluation đạt gần hoặc đạt target metrics.
7. Ít nhất 10 experiment có kết quả.
8. Production config được chọn dựa trên ablation evidence.

***

## 19. User flow và UI modules

```text
Đăng ký / đăng nhập
    ↓
Dashboard: danh sách lá số đã lưu
    ↓
Tạo lá số Tử Vi mới
    ↓
Xem /chart/[id]
    ↓
Nếu chưa có chat_session → tạo đúng 1 chat_session
    ↓
Người dùng hỏi đáp trong chat của lá số đó
    ↓
Hệ thống trả lời bằng Hybrid GraphRAG + citations
```

UI modules:

- `TuViBoard.tsx`
- `ChatInterface.tsx`
- `SourceCitationPanel.tsx`
- `ChartSummaryCard.tsx`

***

## 20. Delivery roadmap

| Week | Backend / Data | Frontend / Product |
|------|----------------|--------------------|
| W1 | Supabase schema Tử Vi-only + RLS + FastAPI skeleton | Next.js auth skeleton + routing |
| W2 | Tử Vi engine verify + chart schema + unit tests | TuViBoard + chart create flow |
| W3 | Ingestion pipeline + Strategy A + 1-2 sách đầu tiên | Dashboard + chart detail refinement |
| W4 | Neo4j graph/vector/fulltext + LangGraph + ExperimentConfig | Chat proxy + citation UI shell |
| W5 | Retrieval/fusion/rerank/generation integrated | Full chat UI + loading/error states |
| W6 | Golden dataset + ablation v1 | End-to-end integration test |
| W7 | Ablation v2 + chọn production config + deploy | QA, security, responsive polish |
| W8 | Final evaluation + ablation report | Demo prep + developer docs |

Scope rule để giữ timeline:

- Chỉ ingest 3-4 sách Tử Vi quan trọng ban đầu.
- Chưa bật LLM document grading trong production.
- Ưu tiên retrieval cho câu hỏi thường gặp nhất.
- Giới hạn ablation trong experiment matrix đã định.

***

## 21. Final stack summary

```text
FRONTEND (Vercel)
  Next.js 14 + TypeScript + Tailwind + shadcn/ui
  Plain SVG/React hoặc D3.js cho TuViBoard
  Zustand
  Supabase JS

BACKEND (Render)
  FastAPI (Python 3.11)
  doanguyen/lasotuvi
  LangGraph
  google-generativeai SDK
  neo4j Python driver
  reranker component
  AblationRunner

DATABASES
  Neo4j AuraDB Free
    - Knowledge graph Tử Vi
    - Vector index
    - Fulltext index
    - Chunk nodes có chunk_strategy_id

  Supabase PostgreSQL
    - profiles
    - la_so
    - chat_sessions
    - source_chunks
    - experiment_runs
```
