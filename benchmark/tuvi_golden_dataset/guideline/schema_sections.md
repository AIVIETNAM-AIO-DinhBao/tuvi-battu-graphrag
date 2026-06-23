# C. File 2 — `schema_sections.json`

> **Đề xuất đặt tại:**
```text
benchmark/tuvi_golden_dataset/guideline/schema_sections.json
```

## Lưu ý cực quan trọng
File `sections` thực tế nên là **JSONL**, tức mỗi dòng là một object.  
Vì vậy schema dưới đây là **schema cho mỗi record/line** trong `*_sections.jsonl`.

## Nội dung file

```json
{
  "description": "Schema for one section record in *_sections.jsonl. This is the canonical corpus artifact used for gold span selection.",
  "type": "object",
  "required": [
    "doc_id",
    "section_id",
    "metadata",
    "content_text",
    "qa_readiness"
  ],
  "properties": {
    "doc_id": {
      "type": "string",
      "description": "Canonical source id, e.g. TVKL, TVNL, TVHS, TVGM."
    },
    "section_id": {
      "type": "string",
      "description": "Canonical section id. Preferred: {doc_id}_CH{chapter_no}_SEC{section_no}; fallback: {doc_id}_P{start_page}_{end_page}_SEC{running_no}."
    },
    "metadata": {
      "type": "object",
      "required": [
        "page_pdf_start",
        "page_pdf_end",
        "page_book_start",
        "page_book_end",
        "section_order",
        "section_type",
        "source_page_ids"
      ],
      "properties": {
        "title": {
          "type": ["string", "null"],
          "description": "Section title if identifiable."
        },
        "page_pdf_start": {
          "type": "integer",
          "minimum": 1
        },
        "page_pdf_end": {
          "type": "integer",
          "minimum": 1
        },
        "page_book_start": {
          "type": ["integer", "null"]
        },
        "page_book_end": {
          "type": ["integer", "null"]
        },
        "section_order": {
          "type": "integer",
          "minimum": 1,
          "description": "Running section order within a source."
        },
        "heading_level": {
          "type": ["integer", "null"],
          "description": "1=chapter, 2=section, 3=subsection if recoverable."
        },
        "section_type": {
          "type": "string",
          "enum": [
            "chapter_heading",
            "section_heading",
            "subsection",
            "paragraph_block",
            "list_block",
            "table_block",
            "mixed_block",
            "unknown"
          ]
        },
        "source_page_ids": {
          "type": "array",
          "items": { "type": "string" },
          "description": "List of page_ids from raw_pages that contribute to this section."
        }
      },
      "additionalProperties": false
    },
    "content_text": {
      "type": "string",
      "description": "Canonical plain-text content used for annotation and gold quote extraction."
    },
    "content_char_count": {
      "type": "integer",
      "minimum": 0,
      "description": "Character count of content_text."
    },
    "normalization_log": {
      "type": "object",
      "properties": {
        "unicode_normalized": { "type": "boolean" },
        "headers_removed": { "type": "boolean" },
        "footers_removed": { "type": "boolean" },
        "linebreaks_fixed": { "type": "boolean" },
        "ocr_corrected_minimally": { "type": "boolean" }
      },
      "additionalProperties": false
    },
    "qa_readiness": {
      "type": "object",
      "required": [
        "can_quote_directly",
        "needs_manual_review"
      ],
      "properties": {
        "can_quote_directly": {
          "type": "boolean",
          "description": "True if annotator can safely quote directly from content_text."
        },
        "needs_manual_review": {
          "type": "boolean",
          "description": "True if this section still has formatting/noise issues."
        },
        "review_notes": {
          "type": ["string", "null"]
        }
      },
      "additionalProperties": false
    }
  },
  "additionalProperties": false
}
```

---

## `schema_sections.json` dùng để làm gì?
Đây là **schema quan trọng nhất cho annotation**.

Nếu `raw_pages` là dữ liệu “thô theo trang”, thì `sections` là:
- dữ liệu **đã section hóa**
- đã đủ sạch để **annotator chọn gold spans**
- là **ground truth pháp điển gốc** trước khi map sang `chunk_id`

### Đây là file mà B/C/A sẽ dùng nhiều nhất khi chọn `gold_context_spans`
Tức là:
- câu hỏi xong
- rồi mở `*_sections.jsonl`
- tìm section phù hợp
- chọn quote
- tạo `span_id`
- điền vào sample release

---

## Step-by-step: từng field được tạo thế nào?

### `doc_id`
- lấy từ `source_registry.json`
- do script carry over từ raw pages
- human chỉ review [source_registry.json](https://www.genspark.ai/api/files/s/8GwBz0Yg)

### `section_id`
- do **A chốt convention**
- do **B/C hoặc script** generate
- nếu parse heading tốt:
  - `TVGM_CH03_SEC04`
- nếu không parse chắc:
  - `TVGM_P007_007_SEC02`

### `metadata.title`
- nếu detect được title/heading, điền vào
- nếu không chắc, để `null`

### `page_pdf_start`, `page_pdf_end`
- do script + human review lấy từ các page nguồn
- section có thể nằm trong 1 trang hoặc nhiều trang

### `page_book_start`, `page_book_end`
- nếu xác định được thì điền
- nếu không thì `null`

### `section_order`
- số thứ tự section chạy trong toàn sách
- do script generate

### `heading_level`
- nếu recover được:
  - 1 = chapter
  - 2 = section
  - 3 = subsection
- nếu không chắc, để `null`

### `section_type`
- do script hoặc human gán
- giúp biết section này là:
  - block văn xuôi
  - heading
  - list
  - bảng
  - mixed

### `source_page_ids`
- script nối từ `raw_pages`
- ví dụ:
  - `["TVGM_P0007"]`
  - `["TVGM_P0007", "TVGM_P0008"]`

### `content_text`
- đây là text canonical để annotate
- do script normalize ra
- human review nếu cần

### `content_char_count`
- script đếm

### `normalization_log`
- script điền
- giúp biết section này đã qua xử lý gì

### `qa_readiness`
- human hoặc reviewer điền
- cực hữu ích để biết section nào dùng ngay được, section nào phải xem lại

---

## Ví dụ record thật theo schema này

Ví dụ dưới đây lấy cảm hứng trực tiếp từ phần “tam hợp” trong `TVGM_raw_pages.json` mà bạn upload. [TVGM_raw_pages.json](https://www.genspark.ai/api/files/s/pZ31EmCY)

```json
{
  "doc_id": "TVGM",
  "section_id": "TVGM_P007_007_SEC01",
  "metadata": {
    "title": "Các tam hợp",
    "page_pdf_start": 7,
    "page_pdf_end": 7,
    "page_book_start": null,
    "page_book_end": null,
    "section_order": 7,
    "heading_level": 2,
    "section_type": "paragraph_block",
    "source_page_ids": ["TVGM_P0007"]
  },
  "content_text": "Mỗi tam hợp có một hành, đó là hành của cung trong tứ chính. Như vậy: Dần Ngọ Tuất hành Hỏa; Tỵ Dậu Sửu hành Kim; Thân Tý Thìn hành Thủy; Hợi Mão Mùi hành Mộc. Trong phép giải đoán, khi xét một cung, phải xét cả 2 cung kia trong tam hợp (gọi là cung tam hợp chiếu) coi cả 3 cung như nhau. Như Mạng đóng ở Tuất, thì phải xét cả 2 Cung Dần và Ngọ cũng quan trọng như Tuất.",
  "content_char_count": 452,
  "normalization_log": {
    "unicode_normalized": true,
    "headers_removed": true,
    "footers_removed": true,
    "linebreaks_fixed": true,
    "ocr_corrected_minimally": false
  },
  "qa_readiness": {
    "can_quote_directly": true,
    "needs_manual_review": false,
    "review_notes": null
  }
}
```

---