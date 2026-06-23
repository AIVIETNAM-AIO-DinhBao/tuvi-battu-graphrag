Dưới đây là **bộ nội dung bạn có thể copy trực tiếp vào repo**.  
Mình chia làm 2 phần:

1. **3 file schema chi tiết + ví dụ**
   - `schema_raw_pages.json`
   - `schema_sections.json`
   - `schema_chart_repr.json`

2. **Giải thích kỹ các file trong `annotations/` và `release/`**
   - file nào bắt buộc
   - file nào chỉ là workflow staging
   - file nào nên giữ để giảm conflict
   - file nào có thể lược bỏ nếu quá gấp

---

# A. Ghi chú quan trọng trước khi copy file

Dựa trên file `TVGM_raw_pages.json` bạn upload, hiện trạng dữ liệu đang có đặc điểm:

- tên file là `raw_pages`
- nhưng bên trong đã có `section_id`
- `content` không đồng nhất:
  - có chỗ là string
  - có chỗ là array
  - có chỗ là object
- `page_book` đang thường là `null` [TVGM_raw_pages.json](https://www.genspark.ai/api/files/s/pZ31EmCY)

=> Vì vậy, để cả team không loạn, mình khuyến nghị:

## Khuyến nghị chuẩn hóa mới
- `schema_raw_pages.json` dùng cho **bản raw thật sự theo trang**
- `schema_sections.json` dùng cho **bản đã section hóa để annotate**
- file `TVGM_raw_pages.json` hiện tại nên xem là **bản draft trung gian**, cần normalize lại trước khi dùng đại trà [TVGM_raw_pages.json](https://www.genspark.ai/api/files/s/pZ31EmCY)

---

# B. File 1 — `schema_raw_pages.json`

> **Đề xuất đặt tại:**
```text
benchmark/tuvi_golden_dataset/guideline/schema_raw_pages.json
```

## Nội dung file

```json
{
  "description": "Schema for raw per-page extracted text from source PDFs before section splitting and QA annotation.",
  "type": "array",
  "items": {
    "type": "object",
    "required": [
      "doc_id",
      "page_id",
      "page_pdf",
      "source_file",
      "extract_method",
      "raw_text",
      "raw_text_char_count",
      "status"
    ],
    "properties": {
      "doc_id": {
        "type": "string",
        "description": "Canonical source id, e.g. TVKL, TVNL, TVHS, TVGM."
      },
      "page_id": {
        "type": "string",
        "description": "Unique page key, recommended format: {doc_id}_P{page_pdf_zero_padded}. Example: TVGM_P0007."
      },
      "page_pdf": {
        "type": "integer",
        "minimum": 1,
        "description": "Page number in the actual PDF file."
      },
      "page_book": {
        "type": ["integer", "null"],
        "description": "Printed page number inside the book if identifiable. Null if unknown."
      },
      "source_file": {
        "type": "string",
        "description": "Original PDF file name or repo path."
      },
      "extract_method": {
        "type": "string",
        "enum": ["pdf_text", "ocr", "mixed", "manual_fix"],
        "description": "How this page text was obtained."
      },
      "raw_text": {
        "type": "string",
        "description": "Raw extracted text for this page. Keep as close as possible to original extraction."
      },
      "raw_text_char_count": {
        "type": "integer",
        "minimum": 0,
        "description": "Character count of raw_text for quick quality checks."
      },
      "quality_flags": {
        "type": "object",
        "properties": {
          "has_ocr_noise": { "type": "boolean" },
          "has_header_footer_repetition": { "type": "boolean" },
          "has_broken_linewrap": { "type": "boolean" },
          "low_text_density": { "type": "boolean" },
          "contains_structured_list_or_table": { "type": "boolean" }
        },
        "additionalProperties": false,
        "description": "Quick flags for downstream cleaning."
      },
      "extraction_notes": {
        "type": ["string", "null"],
        "description": "Optional note by dev/reviewer, e.g. 'page has heavy OCR noise'."
      },
      "status": {
        "type": "string",
        "enum": ["raw", "reviewed", "cleaned"],
        "description": "Pipeline status of this page artifact."
      }
    },
    "additionalProperties": false
  }
}
```

---

## Giải thích kỹ file này

## `schema_raw_pages.json` dùng để làm gì?
Đây là schema cho **artifact đầu tiên sau khi bóc text từ PDF**.  
Nó chưa phục vụ annotate trực tiếp. Nó phục vụ:

- lưu lại dữ liệu thô ban đầu
- audit khi cleaning sai
- hỗ trợ kiểm tra PDF nào noise nặng
- làm input cho bước tạo `clean_pages` hoặc `sections` sau này

### Nó không phải file benchmark cuối
Nó là **artifact nội bộ của pipeline xử lý corpus**.

---

## Step-by-step: từng field được tạo thế nào?

### `doc_id`
- do **human/lead A** định nghĩa từ trước trong `source_registry.json`
- ví dụ: `TVGM`
- lấy từ registry, **không tự đoán từ PDF mỗi lần** [source_registry.json](https://www.genspark.ai/api/files/s/8GwBz0Yg)

### `page_id`
- do **script/dev C** generate
- format khuyến nghị:
  - `TVGM_P0001`
  - `TVGM_P0007`

### `page_pdf`
- do **script extract** sinh ra trực tiếp từ PDF parser
- đây là số trang thật của file PDF

### `page_book`
- do **human B** hoặc **script + human verify** điền nếu xác định được
- nếu chưa chắc, để `null`
- hiện dữ liệu của bạn đang thiên về `null`, điều này là bình thường ở giai đoạn đầu [TVGM_raw_pages.json](https://www.genspark.ai/api/files/s/pZ31EmCY)

### `source_file`
- do **human/dev** điền từ file gốc trong repo
- ví dụ:
  - `data/tuvi/Tử Vi Giảng Minh.pdf`

### `extract_method`
- do **script/dev** gán
- nếu đọc text trực tiếp được: `pdf_text`
- nếu phải OCR: `ocr`
- nếu trang có cả text đọc được và phần phải fix: `mixed`
- nếu có sửa tay: `manual_fix`

### `raw_text`
- do **script extract** sinh
- giữ gần với text gốc nhất
- chưa normalize mạnh ở bước này

### `raw_text_char_count`
- do **script** đếm tự động
- giúp phát hiện:
  - trang trắng
  - trang quá ít text
  - extraction lỗi

### `quality_flags`
- do **script heuristics** gán
- human có thể review lại
- mục tiêu: đánh dấu sớm vấn đề

### `extraction_notes`
- **human hoặc dev** điền thêm nếu thấy trang có bất thường

### `status`
- ban đầu là `raw`
- sau khi có người review sơ qua có thể là `reviewed`
- nếu artifact này đã được chuyển hóa sạch đủ thì `cleaned`

---

## Ví dụ record thật theo schema này

```json
[
  {
    "doc_id": "TVGM",
    "page_id": "TVGM_P0007",
    "page_pdf": 7,
    "page_book": null,
    "source_file": "data/tuvi/Tử Vi Giảng Minh.pdf",
    "extract_method": "pdf_text",
    "raw_text": "Tử Vi Giảng Minh - Thiên Phúc Vũ Tiến Phúc\n\n2. Tỵ Dậu Sửu: Hoả Tỵ bao gồm Thổ sinh cho Kim Dậu...",
    "raw_text_char_count": 1180,
    "quality_flags": {
      "has_ocr_noise": false,
      "has_header_footer_repetition": true,
      "has_broken_linewrap": true,
      "low_text_density": false,
      "contains_structured_list_or_table": false
    },
    "extraction_notes": "Có header lặp ở đầu trang, cần bỏ khi clean.",
    "status": "raw"
  }
]
```

---

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

# D. File 3 — `schema_chart_repr.json`

> **Đề xuất đặt tại:**
```text
benchmark/tuvi_golden_dataset/guideline/schema_chart_repr.json
```

## Lưu ý
Schema này là **schema cho object `chart_repr`** dùng trong release dataset.  
Nó không phải schema cho cả file `CHART-001.json` wrapper. Nếu cần, file `CHART-001.json` có thể có cấu trúc:

```json
{
  "chart_id": "CHART-001",
  "birth_info": { ... },
  "chart_repr": { ... }
}
```

Còn file schema dưới đây chỉ mô tả phần `{ ... }` của `chart_repr`.

## Nội dung file

```json
{
  "description": "Schema for chart_repr object used inside release dataset. This is the RAG-friendly normalized Tử Vi chart context.",
  "type": "object",
  "required": [
    "menh_position",
    "than_position",
    "ban_menh",
    "ngu_hanh_ban_menh",
    "cuc",
    "am_duong_nam_nu",
    "houses"
  ],
  "properties": {
    "menh_position": {
      "type": "string",
      "description": "Earthly branch position of Mệnh, e.g. Tý, Sửu, Dần..."
    },
    "than_position": {
      "type": "string",
      "description": "Earthly branch position of Thân."
    },
    "ban_menh": {
      "type": "string",
      "description": "Canonical bản mệnh string."
    },
    "ngu_hanh_ban_menh": {
      "type": "string",
      "enum": ["Kim", "Mộc", "Thủy", "Hỏa", "Thổ"],
      "description": "Main element of bản mệnh."
    },
    "cuc": {
      "type": "string",
      "description": "Canonical cục string, e.g. Thủy Nhị Cục, Mộc Tam Cục..."
    },
    "am_duong_nam_nu": {
      "type": "string",
      "enum": ["Dương Nam", "Âm Nam", "Dương Nữ", "Âm Nữ"],
      "description": "Combined âm dương + gender descriptor."
    },
    "houses": {
      "type": "array",
      "minItems": 12,
      "maxItems": 12,
      "items": {
        "type": "object",
        "required": [
          "house_index",
          "house_name",
          "earthly_branch",
          "is_than_resident",
          "house_element",
          "yin_yang",
          "dai_han_age",
          "tieu_han_branch",
          "major_stars",
          "aux_stars"
        ],
        "properties": {
          "house_index": {
            "type": "integer",
            "minimum": 1,
            "maximum": 12
          },
          "house_name": {
            "type": "string",
            "enum": [
              "Mệnh",
              "Phụ Mẫu",
              "Phúc Đức",
              "Điền Trạch",
              "Quan Lộc",
              "Nô Bộc",
              "Thiên Di",
              "Tật Ách",
              "Tài Bạch",
              "Tử Tức",
              "Phu Thê",
              "Huynh Đệ"
            ]
          },
          "earthly_branch": {
            "type": "string",
            "enum": [
              "Tý",
              "Sửu",
              "Dần",
              "Mão",
              "Thìn",
              "Tỵ",
              "Ngọ",
              "Mùi",
              "Thân",
              "Dậu",
              "Tuất",
              "Hợi"
            ]
          },
          "is_than_resident": {
            "type": "boolean",
            "description": "True if Cung Thân ký cư tại cung này."
          },
          "house_element": {
            "type": "string",
            "enum": ["Kim", "Mộc", "Thủy", "Hỏa", "Thổ"]
          },
          "yin_yang": {
            "type": "string",
            "enum": ["Dương", "Âm"]
          },
          "dai_han_age": {
            "type": ["integer", "null"],
            "description": "Starting age of đại hạn for this house if available."
          },
          "tieu_han_branch": {
            "type": ["string", "null"],
            "enum": [
              "Tý",
              "Sửu",
              "Dần",
              "Mão",
              "Thìn",
              "Tỵ",
              "Ngọ",
              "Mùi",
              "Thân",
              "Dậu",
              "Tuất",
              "Hợi",
              null
            ]
          },
          "major_stars": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["name"],
              "properties": {
                "name": { "type": "string" },
                "status": {
                  "type": ["string", "null"],
                  "enum": ["Miếu", "Vượng", "Đắc", "Hãm", null]
                }
              },
              "additionalProperties": false
            }
          },
          "aux_stars": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["name"],
              "properties": {
                "name": { "type": "string" },
                "status": {
                  "type": ["string", "null"],
                  "enum": ["Miếu", "Vượng", "Đắc", "Hãm", null]
                }
              },
              "additionalProperties": false
            }
          }
        },
        "additionalProperties": false
      }
    },
    "derived_tags": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Optional normalized tags such as 'tam_hop_thai_tue', 'vo_chinh_dieu', 'hoa_loc_present'."
    }
  },
  "additionalProperties": false
}
```

---

## `schema_chart_repr.json` dùng để làm gì?
Đây là schema khóa phần **chart context** để:
- mọi sample dùng một format thống nhất
- LLM input ổn định
- reviewer biết chính xác chart_repr phải có gì
- không để mỗi người tự nhét chart JSON theo kiểu riêng [Guideline benchmark](https://www.genspark.ai/api/files/s/fvJx9CFu)

---

## Step-by-step: từng field được tạo thế nào?

### `menh_position`, `than_position`
- do **engine + script** lấy ra từ chart gốc
- A review chuẩn hóa
- không nhập tay nếu có thể

### `ban_menh`, `ngu_hanh_ban_menh`, `cuc`, `am_duong_nam_nu`
- lấy từ engine nếu engine có
- nếu engine chưa xuất đủ, phải có bước derive/normalize nội bộ
- human review lần cuối

### `houses`
- do **script** map từ raw engine output
- phải đủ đúng 12 cung
- mỗi house phải chuẩn hóa:
  - `house_name`
  - `earthly_branch`
  - `house_element`
  - `yin_yang`
  - `major_stars`
  - `aux_stars`

### `major_stars` và `aux_stars`
- raw engine hiện có xu hướng cho danh sách sao chung
- nên cần **taxonomy nội bộ** để tách major/aux
- script/dev làm việc này
- A review

### `derived_tags`
- không bắt buộc
- nếu team có thời gian thì hữu ích để:
  - chọn coverage matrix
  - generate question slots
  - làm stats sau này

---

## Ví dụ `chart_repr` điền thật

> **Lưu ý:** ví dụ dưới đây là ví dụ minh họa format, không phải chart thực đầy đủ 12 cung.  
> Khi làm thật, `houses` phải đủ 12 items.

```json
{
  "menh_position": "Thìn",
  "than_position": "Dần",
  "ban_menh": "Lộ Bàng Thổ",
  "ngu_hanh_ban_menh": "Thổ",
  "cuc": "Thủy Nhị Cục",
  "am_duong_nam_nu": "Dương Nam",
  "houses": [
    {
      "house_index": 1,
      "house_name": "Tài Bạch",
      "earthly_branch": "Tý",
      "is_than_resident": false,
      "house_element": "Thủy",
      "yin_yang": "Dương",
      "dai_han_age": 84,
      "tieu_han_branch": "Dần",
      "major_stars": [
        { "name": "Cự Môn", "status": "Vượng" }
      ],
      "aux_stars": [
        { "name": "Tướng Quân", "status": null },
        { "name": "Tuế Phá", "status": null },
        { "name": "Thiên Hư", "status": "Đắc" },
        { "name": "Thiên Khốc", "status": "Đắc" }
      ]
    },
    {
      "house_index": 2,
      "house_name": "Tử Tức",
      "earthly_branch": "Sửu",
      "is_than_resident": false,
      "house_element": "Thổ",
      "yin_yang": "Âm",
      "dai_han_age": 94,
      "tieu_han_branch": "Mão",
      "major_stars": [
        { "name": "Thiên Tướng", "status": "Đắc" }
      ],
      "aux_stars": [
        { "name": "Tấu Thư", "status": null },
        { "name": "Long Đức", "status": null }
      ]
    }
  ],
  "derived_tags": [
    "hoa_loc_present",
    "than_cu_dan"
  ]
}
```

---

# E. Giải thích chi tiết các file trong `annotations/` và `release/`

Bạn hỏi rất đúng, vì đây là phần nhiều team dễ làm thừa hoặc không hiểu file nào là “bắt buộc”, file nào chỉ là “workflow staging”.

---

## 1) `annotations/gold_sections_A.jsonl`
### Ý nghĩa
File A dùng để lưu **gold section selection** cho batch sample do A phụ trách.

### Nội dung nên là gì?
Mỗi dòng là 1 sample, chứa tối thiểu:
- `id`
- `chart_id`
- `question`
- `question_complexity`
- `gold_context_spans`
- có thể thêm `required_entities_draft`

### Có cần không?
**Không bắt buộc về mặt logic**, nhưng **rất nên có** nếu 3 người làm song song.  
Nó giúp:
- giảm conflict file
- A/B/C không đụng nhau
- merge sau dễ hơn

### Khi nào có thể bỏ?
Nếu chỉ có 1 người annotate toàn bộ hoặc team dùng tool DB/canvas khác.  
Nhưng với nhóm bạn, **nên giữ**.

---

## 2) `annotations/gold_sections_B.jsonl`
Giống hệt file của A, nhưng cho batch B.

### Có cần không?
**Nên có** để B làm độc lập.

---

## 3) `annotations/gold_sections_C.jsonl`
Giống hệt file của A/B, nhưng cho batch C.

### Có cần không?
**Nên có** để C làm độc lập.

---

## 4) `annotations/gold_sections.jsonl`
### Ý nghĩa
Đây là file **merge chính thức** của toàn bộ gold section selection.

### Vai trò
Nó là **canonical evidence selection file** trước khi viết full `gold_answer`.

### Có cần không?
**Có, rất cần.**
Đây là file:
- thống nhất toàn bộ 100 sample
- làm đầu vào cho draft answer generation
- làm mốc kiểm tra “sample nào đã có evidence, sample nào chưa”

### Nếu bỏ file này?
Bạn sẽ phải merge trực tiếp từ A/B/C mỗi lần, rất rối.

---

## 5) `annotations/golden_candidates_A.jsonl`
### Ý nghĩa
File A dùng để lưu **candidate sample gần hoàn chỉnh** cho batch A.

Thông thường file này sẽ chứa:
- toàn bộ release fields draft
- kèm một phần ops fields
- nhưng chưa phải release final

### Khác `gold_sections_A.jsonl` thế nào?
- `gold_sections_A.jsonl`: mới có evidence selection
- `golden_candidates_A.jsonl`: đã có question, spans, gold_answer draft/final, summary, labels...

### Có cần không?
**Rất nên có** nếu 3 người làm song song.  
Nếu không có file này, A/B/C sẽ phải sửa chung một file lớn rất dễ conflict.

---

## 6) `annotations/golden_candidates_B.jsonl`
Tương tự cho batch của B.

### Có cần không?
**Nên có**.

---

## 7) `annotations/golden_candidates_C.jsonl`
Tương tự cho batch của C.

### Có cần không?
**Nên có**.

---

## 8) `annotations/golden_candidates.jsonl`
### Ý nghĩa
File merge toàn bộ candidate samples trước khi release.

### Vai trò
Đây là **staging area cuối** trước khi:
- cross-review hoàn tất
- adjudication xong
- map chunk_ids
- export release

### Có cần không?
**Có.**
Đây là file:
- A review tổng
- B/C cross-review dễ
- script validate sơ bộ dễ
- chưa “khóa release” nên vẫn an toàn để sửa

---

## 9) `annotations/sentence_span_map.jsonl`
### Ý nghĩa
Map từng câu hoặc từng mệnh đề trong `gold_answer` về span support.

### Ví dụ record
```json
{
  "id": "TVQA-078",
  "sentence_map": [
    {
      "sentence_no": 1,
      "sentence_text": "Khi luận cung Mệnh ở Tuất, ngoài hai cung tam hợp là Dần và Ngọ...",
      "supported_by_span_ids": ["TVGM_P7_7_SEC07_SP01"]
    },
    {
      "sentence_no": 2,
      "sentence_text": "còn phải xét thêm quan hệ nhị hợp nếu cung đó được sinh nhập...",
      "supported_by_span_ids": ["TVGM_P9_9_SEC09_SP01"]
    }
  ]
}
```

### Có cần không?
### Câu trả lời thực tế:
- **Không tuyệt đối bắt buộc để release chạy**
- nhưng **rất đáng giữ**, đặc biệt với One-hop / Two-hop

### Khi nào nên giữ?
- khi muốn audit groundedness kỹ
- khi sợ answer vượt source
- khi nhiều sample khó
- khi A muốn review nhanh xem câu nào unsupported

### Nếu sprint quá gấp thì sao?
Có thể hạ yêu cầu:
- chỉ làm `sentence_span_map` cho:
  - tất cả Two-hop
  - các sample bị reviewer flag
  - hoặc 20–30 sample khó nhất

### Kết luận
- **Recommended mạnh**
- nhưng không bắt buộc 100% nếu timeline quá căng

---

## 10) `release/golden_v1_release.jsonl`
### Ý nghĩa
Đây là **bản release benchmark chính thức**.

### Có cần không?
**Bắt buộc.**
Không có file này thì chưa có benchmark release.

### Ai được sửa?
- chỉ A hoặc script freeze cuối

### Nội dung
Phải đúng `schema_release.json` [schema_release.json](https://www.genspark.ai/api/files/s/seXZhhes)

---

## 11) `release/gold_with_chunk_map.jsonl`
### Ý nghĩa
Đây là bản release hoặc near-release đã có thêm `gold_chunk_ids`, tức đã map:
- `gold_context_spans`
→ `chunk_id(s)`

### Có cần không?
**Rất cần nếu bạn muốn chấm retrieval nghiêm túc**:
- hit@k
- MRR
- overlap chunk

### Khi nào có thể chưa cần?
Nếu team mới chỉ muốn thử generation trước, chưa chấm retrieval.  
Nhưng theo benchmark plan của bạn, retrieval là phần rất quan trọng, nên file này **thực tế là bắt buộc**. [Guideline benchmark](https://www.genspark.ai/api/files/s/fvJx9CFu)

---

# F. Kết luận rất ngắn cho team

## 1. Ba schema mới này dùng để khóa pipeline đầu vào
- `schema_raw_pages.json`: khóa artifact extract theo trang
- `schema_sections.json`: khóa artifact section hóa cho annotation
- `schema_chart_repr.json`: khóa chart context cho release sample

## 2. Trong thư mục `annotations/`
### Bắt buộc / gần bắt buộc
- `gold_sections.jsonl`
- `golden_candidates.jsonl`

### Nên có để giảm conflict
- `gold_sections_A/B/C.jsonl`
- `golden_candidates_A/B/C.jsonl`

### Khuyến nghị mạnh nhưng có thể co giãn
- `sentence_span_map.jsonl`

## 3. Trong thư mục `release/`
### Bắt buộc
- `golden_v1_release.jsonl`

### Bắt buộc nếu chấm retrieval đúng nghĩa
- `gold_with_chunk_map.jsonl`

---

Nếu bạn muốn, ở tin nhắn tiếp theo mình có thể làm tiếp cho bạn **3 file mẫu thực tế** theo các schema này:

1. `TVGM_raw_pages.sample.json`
2. `TVGM_sections.sample.jsonl`
3. `CHART-001.sample.json`

để B/C cầm vào là code/annotate được ngay, không phải tự đoán format nữa.