# 1) Kiến trúc chuẩn cuối cùng của 3 loại chart

## 1.1. Vai trò của từng lớp

### `chart_full`
Đây là **source-of-truth kỹ thuật** lấy từ pipeline hiện tại `lasotuvi -> lasotuvi_service -> tuvi_calculator -> router -> storage`. Nó phải giữ đủ thông tin để frontend vẽ lá số, backend debug, và hệ thống có thể tái sinh các lớp rút gọn sau này. Theo mô tả hiện tại, `TuViCalculator` đã normalize ra các khối như `metadata`, `palaces`, `stars`, `thien_can`, `dia_chi`, `lunar_date`, `raw_data`. [Source](https://www.genspark.ai/api/files/s/KkeWIW7d)

### `chart_repr`
Đây là **contract cho team data** và cũng là chart context gọn nhất để benchmark. Nó phải nhỏ, ổn định, đọc được bằng mắt, không phụ thuộc cấu trúc render. Mục tiêu là 1 annotator nhìn vào là hiểu chart cần hỏi gì, nhưng không bị ngập trong `raw_data`, `star_color`, `saoID`, metadata render, v.v. [Source](https://www.genspark.ai/api/files/s/rFIg2yuh)

### `chart_semantic`
Đây là **contract cho retrieval / reasoning**. Nó không phải bản vẽ lá số, mà là bản “đọc hiểu được bằng máy”: quan hệ cung, index sao, tag mẫu hình, các fact đã tiền xử lý, các hook cho Tứ Hóa/Phi Hóa. Theo feedback, chính khối này đang thiếu nhiều mắt xích quan trọng như `heavenly_stem`, `phi_hoa`, `giap_branches`, `luc_hai_branch`, `tuan_khong`, `triet_khong`, `cách_cục`. [Source](https://www.genspark.ai/api/files/s/OhfRg6g2)

---

# 2) Schema chuẩn cuối cùng của `chart_full`

## 2.1. Mục tiêu
- dùng cho backend/system
- lưu được trong DB
- đủ để tái sinh `chart_repr` và `chart_semantic`
- không ép team data phải làm việc trực tiếp với nó

## 2.2. Required top-level fields

```json
{
  "chart_type": "TUVI",
  "version": "1.0",
  "metadata": {},
  "palaces": {},
  "stars": {},
  "thien_can": null,
  "dia_chi": null,
  "lunar_date": null
}
```

## 2.3. Schema khuyến nghị

```json
{
  "chart_type": "TUVI",
  "version": "1.0",
  "metadata": {
    "label": "string",
    "birth_date": "YYYY-MM-DD",
    "birth_time": "HH:MM[:SS]",
    "gender": "male|female|nam|nu",
    "timezone": "Asia/Ho_Chi_Minh",
    "nam_xem_han": "integer|null",
    "can_chi_nam_xem": "string|null",
    "calculated_at": "ISO8601 UTC string",
    "personal_info": "object|null",
    "destiny_info": "object|null"
  },
  "palaces": {
    "Mệnh": {
      "name": "Mệnh",
      "stars": ["Tử Vi", "Thiên Phủ"],
      "star_details": [],
      "star_groups": {
        "chinh_tinh": [],
        "phu_tinh": [],
        "khac": []
      },
      "position": 5,
      "attributes": {
        "dia_chi": "Thìn",
        "element": "Thổ",
        "yin_yang": "Dương",
        "dai_han": 24,
        "dai_han_age": 24,
        "tieu_han": "Tý",
        "luu_nien_dai_van": "string|null",
        "trang_sinh": "Mộ|null",
        "tuan_khong": false,
        "triet_khong": false,
        "khong_vong": [],
        "has_than": false,

        "heavenly_stem": "string|null"
      }
    }
  },
  "stars": {
    "Tử Vi": {
      "name": "Tử Vi",
      "palace": "Mệnh",
      "brightness": "Miếu|Vượng|Đắc|Bình|Hãm|null",
      "category": "Chính Tinh|Phụ Tinh|Khác",
      "attributes": {
        "id": "string|integer|null",
        "brightness_code": "M|V|Đ|B|H|null",
        "color": "string|null",
        "quality": "string|null",
        "is_luu": false,
        "source": "string|null",
        "nam_xem_han": "integer|null"
      }
    }
  },
  "thien_can": "object|string|array|null",
  "dia_chi": "object|string|array|null",
  "lunar_date": "object|string|null",
  "raw_data": "object|null"
}
```

## 2.4. Bắt buộc vs tùy chọn

### Required
- `chart_type`
- `version`
- `metadata.birth_date`
- `metadata.birth_time`
- `metadata.gender`
- `metadata.calculated_at`
- `palaces`
- `stars`

### Strongly recommended
- `metadata.destiny_info`
- `palaces[*].attributes.trang_sinh`
- `palaces[*].attributes.tuan_khong`
- `palaces[*].attributes.triet_khong`
- `palaces[*].attributes.has_than`
- `palaces[*].attributes.heavenly_stem`

### Optional
- `raw_data`
- `color`
- `quality`
- `luu_nien_dai_van`
- `nam_xem_han`

## 2.5. Ghi chú thực thi
`chart_full` nên tiếp tục được tạo ở `backend/app/services/tuvi_calculator.py`, vì đây là lớp normalize trực tiếp từ engine. Không nên nhồi logic semantic sâu vào đây quá nhiều; chỉ nên bảo đảm output kỹ thuật đầy đủ, canonical, và ổn định. [Source](https://www.genspark.ai/api/files/s/KkeWIW7d)

---

# 3) Schema chuẩn cuối cùng của `chart_repr`

## 3.1. Mục tiêu
- dùng cho team data
- dùng làm `chart context` trong benchmark release
- nhỏ hơn `chart_full` rất nhiều
- fixed structure, đúng 12 cung

## 3.2. Schema cuối cùng

```json
{
  "chart_type": "TUVI",
  "schema_role": "chart_repr",
  "schema_version": "2.0",

  "menh_position": "Tý|Sửu|Dần|Mão|Thìn|Tỵ|Ngọ|Mùi|Thân|Dậu|Tuất|Hợi",
  "than_position": "Tý|Sửu|Dần|Mão|Thìn|Tỵ|Ngọ|Mùi|Thân|Dậu|Tuất|Hợi|null",

  "ban_menh": "string",
  "ngu_hanh_ban_menh": "Kim|Mộc|Thủy|Hỏa|Thổ|null",
  "cuc": "string|null",
  "am_duong_nam_nu": "Dương Nam|Âm Nam|Dương Nữ|Âm Nữ|string|null",

  "houses": [
    {
      "house_index": 1,
      "house_name": "Mệnh|Phụ Mẫu|Phúc Đức|Điền Trạch|Quan Lộc|Nô Bộc|Thiên Di|Tật Ách|Tài Bạch|Tử Tức|Phu Thê|Huynh Đệ",
      "earthly_branch": "Tý|Sửu|Dần|Mão|Thìn|Tỵ|Ngọ|Mùi|Thân|Dậu|Tuất|Hợi",
      "is_than_resident": true,
      "house_element": "Kim|Mộc|Thủy|Hỏa|Thổ|null",
      "yin_yang": "Dương|Âm|null",
      "dai_han_age": 24,
      "tieu_han_branch": "Tý|Sửu|Dần|Mão|Thìn|Tỵ|Ngọ|Mùi|Thân|Dậu|Tuất|Hợi|null",
      "trang_sinh": "string|null",
      "tuan_khong": false,
      "triet_khong": false,

      "major_stars": [
        { "name": "Tử Vi", "status": "Miếu|Vượng|Đắc|Bình|Hãm|null" }
      ],
      "aux_stars": [
        { "name": "Hóa Lộc", "status": "Miếu|Vượng|Đắc|Bình|Hãm|null" }
      ]
    }
  ],

  "derived_tags": [
    "than_cu_tai_bach",
    "menh_vo_chinh_dieu",
    "tai_bach_co_hoa_loc"
  ]
}
```

## 3.3. Required fields

### Top-level required
- `chart_type`
- `schema_role`
- `schema_version`
- `menh_position`
- `than_position`
- `ban_menh`
- `ngu_hanh_ban_menh`
- `cuc`
- `am_duong_nam_nu`
- `houses`

### Required per house
- `house_index`
- `house_name`
- `earthly_branch`
- `is_than_resident`
- `house_element`
- `yin_yang`
- `dai_han_age`
- `tieu_han_branch`
- `trang_sinh`
- `tuan_khong`
- `triet_khong`
- `major_stars`
- `aux_stars`

## 3.4. Vì sao thêm `trang_sinh`, `tuan_khong`, `triet_khong` vào `chart_repr`
Mình khuyên thêm luôn 3 field này vào `chart_repr`, dù trước đó có thể mới để ở lớp full/semantic, vì:

- team data sẽ gặp nhiều câu hỏi liên quan
- chúng là fact hiển nhiên của chart, không phải derived reasoning sâu
- nếu để tận semantic mới có thì chart_repr hơi “mù” với annotator

Điều này cũng phù hợp với feedback rằng Tuần/Triệt và Trường Sinh không nên bị chìm trong flags mơ hồ. [Source](https://www.genspark.ai/api/files/s/OhfRg6g2)

---

# 4) Schema chuẩn cuối cùng của `chart_semantic`

## 4.1. Mục tiêu
- chỉ dùng JSON
- retrieval-friendly
- deterministic
- không chứa prose dài
- có chỗ cho rule-based semantic nâng cao

## 4.2. Schema cuối cùng

```json
{
  "chart_type": "TUVI",
  "schema_role": "chart_semantic",
  "schema_version": "2.0",

  "core_identity": {
    "name": "string|null",
    "birth_date": "YYYY-MM-DD",
    "birth_time": "HH:MM[:SS]",
    "gender": "string",
    "timezone": "Asia/Ho_Chi_Minh",

    "menh_branch": "Tý|Sửu|Dần|Mão|Thìn|Tỵ|Ngọ|Mùi|Thân|Dậu|Tuất|Hợi|null",
    "than_branch": "Tý|Sửu|Dần|Mão|Thìn|Tỵ|Ngọ|Mùi|Thân|Dậu|Tuất|Hợi|null",

    "ban_menh": "string|null",
    "ngu_hanh_ban_menh": "Kim|Mộc|Thủy|Hỏa|Thổ|null",
    "cuc": "string|null",
    "ngu_hanh_cuc": "Kim|Mộc|Thủy|Hỏa|Thổ|null",
    "am_duong_nam_nu": "string|null",
    "menh_cuc_relation": "sinh|khắc|đồng_hành|string|null",

    "chu_menh": "string|null",
    "chu_than": "string|null",
    "lai_nhan_cung": "string|null",
    "than_cu": "string|null",
    "can_chi_menh": "string|null",
    "can_luong": "string|null"
  },

  "birth_year_tu_hoa": {
    "Hóa Lộc": { "house_name": "string", "earthly_branch": "string" },
    "Hóa Quyền": { "house_name": "string", "earthly_branch": "string" },
    "Hóa Khoa": { "house_name": "string", "earthly_branch": "string" },
    "Hóa Kỵ": { "house_name": "string", "earthly_branch": "string" }
  },

  "focus_relations": {
    "menh": {
      "tam_hop_branches": ["string", "string", "string"],
      "xung_chieu_branch": "string|null",
      "nhi_hop_branch": "string|null",
      "luc_hai_branch": "string|null",
      "giap_branches": ["string", "string"]
    },
    "than": {
      "tam_hop_branches": ["string", "string", "string"],
      "xung_chieu_branch": "string|null",
      "nhi_hop_branch": "string|null",
      "luc_hai_branch": "string|null",
      "giap_branches": ["string", "string"]
    }
  },

  "palace_semantics": [
    {
      "house_name": "string",
      "earthly_branch": "string|null",
      "heavenly_stem": "string|null",
      "house_element": "Kim|Mộc|Thủy|Hỏa|Thổ|null",
      "yin_yang": "Dương|Âm|null",

      "is_menh": false,
      "is_than_resident": false,

      "dai_han_age": "integer|null",
      "tieu_han_branch": "string|null",
      "trang_sinh": "string|null",
      "tuan_khong": false,
      "triet_khong": false,

      "major_stars": [
        { "name": "string", "status": "string|null" }
      ],
      "aux_stars": [
        { "name": "string", "status": "string|null" }
      ],

      "house_relations": {
        "tam_hop_branches": ["string", "string", "string"],
        "xung_chieu_branch": "string|null",
        "nhi_hop_branch": "string|null",
        "luc_hai_branch": "string|null",
        "giap_branches": ["string", "string"]
      },

      "elemental_flags": [
        "cung_sinh_sao",
        "cung_khac_sao",
        "sao_tuong_sinh_ban_menh",
        "sao_khac_ban_menh"
      ],

      "tu_hoa_birth_year": [
        { "name": "Hóa Lộc", "status": null }
      ],

      "phi_hoa": {
        "available": false,
        "note": "string|null",
        "hoa_loc_to": "string|null",
        "hoa_quyen_to": "string|null",
        "hoa_khoa_to": "string|null",
        "hoa_ky_to": "string|null"
      },

      "tu_hoa_self": [],

      "yearly_transit": {
        "nam_xem_han": "integer|null",
        "stars": ["string"]
      }
    }
  ],

  "star_index": {
    "Tử Vi": [
      {
        "house_name": "Mệnh",
        "earthly_branch": "Thìn",
        "status": "Miếu",
        "star_group": "major",
        "star_element": "Thổ"
      }
    ]
  },

  "notable_patterns": [
    {
      "pattern_code": "tu_phu_vu_tuong_present",
      "evidence": ["Tử Vi", "Thiên Phủ", "Vũ Khúc", "Thiên Tướng"]
    }
  ],

  "retrieval_hints": {
    "career": {
      "priority_houses": ["Quan Lộc", "Mệnh", "Thiên Di"],
      "priority_relations": {},
      "key_stars": ["Tử Vi", "Thiên Phủ"]
    },
    "finance": {},
    "marriage": {},
    "health": {},
    "family": {},
    "query_strategy": [
      "Ưu tiên core_identity + cung đích + tam hợp/xung chiếu",
      "Nếu câu hỏi nhắc sao cụ thể thì tra star_index trước"
    ]
  }
}
```

## 4.3. Required vs optional

### Required top-level
- `chart_type`
- `schema_role`
- `schema_version`
- `core_identity`
- `focus_relations`
- `palace_semantics`
- `star_index`
- `notable_patterns`
- `retrieval_hints`

### Required trong `core_identity`
- `birth_date`
- `birth_time`
- `gender`
- `menh_branch`
- `than_branch`
- `ban_menh`
- `ngu_hanh_ban_menh`
- `cuc`
- `am_duong_nam_nu`

### Required per `palace_semantics` item
- `house_name`
- `earthly_branch`
- `house_element`
- `is_menh`
- `is_than_resident`
- `trang_sinh`
- `tuan_khong`
- `triet_khong`
- `major_stars`
- `aux_stars`
- `house_relations`
- `elemental_flags`
- `phi_hoa`

### Optional nhưng nên có
- `heavenly_stem`
- `birth_year_tu_hoa`
- `yearly_transit`
- `tu_hoa_self`

## 4.4. Quy tắc rất quan trọng cho `phi_hoa`
Nếu team hệ thống **chưa code xong engine/rule table Phi Hóa**, thì:

- **vẫn giữ field `phi_hoa`**
- nhưng set:
  - `available = false`
  - các trường đích = `null`
  - có `note`

Như vậy schema không đổi sau này, chỉ đổi logic tính. Đây là cách mở rộng an toàn nhất. Feedback cũng chỉ rõ Phi Hóa/Tứ Hóa là khối quan trọng, nhưng không nên bịa khi chưa đủ quy tắc. [Source](https://www.genspark.ai/api/files/s/OhfRg6g2)

---

# 5) Mapping chuẩn giữa 3 lớp

## 5.1. Từ `chart_full` sang `chart_repr`

### Top-level
- `metadata.destiny_info.banMenh` -> `chart_repr.ban_menh`
- `metadata.destiny_info.menhNguHanh` -> `chart_repr.ngu_hanh_ban_menh`
- `metadata.destiny_info.cucMenh` -> `chart_repr.cuc`
- `metadata.destiny_info.amDuongLy` + `metadata.gender` -> `chart_repr.am_duong_nam_nu`
- `palaces["Mệnh"].attributes.dia_chi` -> `chart_repr.menh_position`
- cung có `has_than = true` -> `chart_repr.than_position`

### Per-house
- `palaces[*].position` -> `house_index`
- `palaces[*].name` -> `house_name`
- `palaces[*].attributes.dia_chi` -> `earthly_branch`
- `palaces[*].attributes.element` -> `house_element`
- `palaces[*].attributes.yin_yang` -> `yin_yang`
- `palaces[*].attributes.dai_han_age` -> `dai_han_age`
- `palaces[*].attributes.tieu_han` -> `tieu_han_branch`
- `palaces[*].attributes.trang_sinh` -> `trang_sinh`
- `palaces[*].attributes.tuan_khong` -> `tuan_khong`
- `palaces[*].attributes.triet_khong` -> `triet_khong`
- `star_details` -> tách thành `major_stars` và `aux_stars`

## 5.2. Từ `chart_repr` sang `chart_semantic`

### `core_identity`
- `menh_position` -> `core_identity.menh_branch`
- `than_position` -> `core_identity.than_branch`
- `ban_menh` -> `core_identity.ban_menh`
- `ngu_hanh_ban_menh` -> `core_identity.ngu_hanh_ban_menh`
- `cuc` -> `core_identity.cuc`

### `focus_relations`
- tính từ `menh_position`, `than_position`

### `palace_semantics`
- mỗi `houses[i]` -> một semantic item
- cộng thêm:
  - `heavenly_stem`
  - `elemental_flags`
  - `house_relations`
  - `phi_hoa`
  - `tu_hoa_birth_year`
  - `yearly_transit`

### `star_index`
- invert từ `houses[*].major_stars + houses[*].aux_stars`

### `notable_patterns`
- derive từ toàn bộ chart

---

# 6) Danh sách helper functions cần thiết cho team hệ thống

Mình khuyên **không nhét tất cả vào `tuvi_calculator.py`**.  
Nên chia thành 3 tầng service rõ ràng:

## 6.1. Vị trí nên bổ sung

### Giữ nguyên vai trò của file hiện có
- `backend/app/services/tuvi_calculator.py`
  - chỉ lo gọi engine và normalize ra `chart_full` [Source](https://www.genspark.ai/api/files/s/KkeWIW7d)

### Tạo file mới
- `backend/app/services/tuvi_chart_projection_service.py`
  - build `chart_repr`
  - build `chart_semantic`

### Tạo file rule/helper riêng
- `backend/app/services/tuvi_semantic_rules.py`
  - toàn bộ rule deterministic: quan hệ cung, ngũ hành, tứ hóa, phi hóa, cách cục

### Tạo validator
- `backend/app/services/tuvi_chart_validator.py`
  - validate 3 schema trước khi lưu hoặc export

Đây là cách dễ bàn giao nhất giữa team data và team hệ thống.

---

## 6.2. Nhóm helper P0 — bắt buộc có ngay

### A. Normalization helpers
1. `strip_accents(text) -> str`
2. `normalize_key(text) -> str`
3. `title_case_vn(text) -> str`
4. `canonical_house_name(name) -> str`
5. `canonical_star_name(name) -> str`
6. `canonical_branch(branch) -> str|None`
7. `normalize_status(value) -> str|None`

**Mục đích**  
Đồng nhất key, house names, star names, status codes.

---

### B. Extraction helpers
8. `get_destiny_info(chart_full) -> dict`
9. `get_personal_info(chart_full) -> dict`
10. `find_menh_house(chart_full) -> dict|None`
11. `infer_menh_branch(chart_full) -> str|None`
12. `infer_than_house_name(chart_full) -> str|None`
13. `infer_than_branch(chart_full) -> str|None`
14. `extract_birth_info(chart_full) -> dict`

**Mục đích**  
Tách các fact cốt lõi từ `chart_full`.

---

### C. Star classification helpers
15. `is_major_star(star_name) -> bool`
16. `split_major_aux_stars(star_details) -> (major_stars, aux_stars)`
17. `compact_star(star) -> dict`
18. `build_star_index(chart_repr) -> dict`

**Mục đích**  
Xây dựng `chart_repr` và `star_index`.

---

### D. Chart projection helpers
19. `build_chart_repr(chart_full) -> dict`
20. `build_chart_semantic(chart_full, chart_repr) -> dict`

**Mục đích**  
Hai hàm chính để xuất 2 loại chart data team cần.

---

## 6.3. Nhóm helper P1 — rất nên có

### E. Quan hệ cung
21. `find_tam_hop(branch) -> list[str]`
22. `find_xung_chieu(branch) -> str|None`
23. `find_nhi_hop(branch) -> str|None`
24. `find_luc_hai(branch) -> str|None`
25. `find_giap(branch) -> list[str]`
26. `compute_house_relations(branch) -> dict`

**Mục đích**  
Đây là lõi của semantic reading, và feedback nhấn mạnh hiện đang thiếu `giap_branches` + `luc_hai_branch`. [Source](https://www.genspark.ai/api/files/s/OhfRg6g2)

---

### F. Ngũ hành
27. `extract_element_from_ban_menh(ban_menh) -> str|None`
28. `extract_element_from_cuc(cuc) -> str|None`
29. `relation_between_elements(source, target) -> str|None`
30. `compute_elemental_flags(house_element, ban_menh_element, stars) -> list[str]`

**Mục đích**  
Tạo `ngu_hanh_cuc`, `menh_cuc_relation`, `elemental_flags`.

---

### G. Tứ Hóa năm sinh
31. `detect_birth_year_tu_hoa(chart_repr) -> dict`
32. `extract_tu_hoa_in_house(house) -> list`
33. `build_birth_year_tu_hoa_summary(chart_repr) -> dict`

**Mục đích**  
Tạo `birth_year_tu_hoa` và `tu_hoa_birth_year`.

---

### H. Palace semantic assembly
34. `build_palace_semantics(chart_full, chart_repr) -> list[dict]`
35. `extract_yearly_transit_stars(full_house) -> list[str]`
36. `annotate_house_semantic_flags(house_item) -> list[str]`

**Mục đích**  
Tổng hợp toàn bộ semantic cấp cung.

---

## 6.4. Nhóm helper P2 — hook nâng cao, nên thiết kế từ bây giờ

### I. Phi Hóa / Tự Hóa
37. `resolve_heavenly_stem_for_palace(chart_full, house_name) -> str|None`
38. `compute_phi_hoa_for_house(chart_full, house_name, rule_table) -> dict`
39. `compute_tu_hoa_self(chart_full, house_name, rule_table) -> list`
40. `build_phi_hoa_map(chart_full, rule_table) -> dict`

**Mục đích**  
Hiện để hook. Khi chưa đủ rule thì return khung rỗng, không bịa.

---

### J. Cách cục / pattern detection
41. `detect_tu_phu_vu_tuong(chart_repr) -> dict|None`
42. `detect_sat_pha_tham(chart_repr) -> dict|None`
43. `detect_co_nguyet_dong_luong(chart_repr) -> dict|None`
44. `detect_cu_nhat(chart_repr) -> dict|None`
45. `detect_vo_chinh_dieu(chart_repr) -> dict|None`
46. `detect_notable_patterns(chart_repr, chart_full) -> list[dict]`

**Mục đích**  
Phục vụ câu hỏi tổng quan, multi-hop, retrieval intent routing.

---

### K. Retrieval helpers
47. `build_retrieval_hints(chart_repr, chart_semantic) -> dict`
48. `select_priority_houses(topic, chart_semantic) -> list[str]`
49. `get_related_houses_from_question_intent(topic) -> list[str]`
50. `slice_semantic_for_query(chart_semantic, entities, topic) -> dict`

**Mục đích**  
Đây là lớp cầu nối sang agent/chatbot.

---

### L. Validation & export
51. `validate_chart_full(chart_full) -> list[str]`
52. `validate_chart_repr(chart_repr) -> list[str]`
53. `validate_chart_semantic(chart_semantic) -> list[str]`
54. `export_chart_bundle(chart_full, chart_repr, chart_semantic, output_path) -> None`

---

# 7) Hướng dẫn bổ sung cụ thể cho team hệ thống

## 7.1. Nơi cần sửa
### File giữ nguyên nhiệm vụ
- `backend/app/services/tuvi_calculator.py`
  - normalize output engine thành `chart_full`
  - không viết sâu logic retrieval vào đây

### File mới nên tạo
- `backend/app/services/tuvi_chart_projection_service.py`
- `backend/app/services/tuvi_semantic_rules.py`
- `backend/app/services/tuvi_chart_validator.py`

## 7.2. Luồng gọi hàm nên là
```text
tuvi_calculator.calculate(...)
-> chart_full
-> projection_service.build_chart_repr(chart_full)
-> projection_service.build_chart_semantic(chart_full, chart_repr)
-> validator.validate_all(...)
-> save / export
```

## 7.3. Vì sao không nên nhét hết vào `tuvi_calculator.py`
Nếu dồn hết mọi thứ vào một file thì:
- khó review
- khó test đơn vị
- data team không biết chỗ nào là raw normalize, chỗ nào là derived semantic
- sau này thêm Phi Hóa/Cách Cục sẽ rất rối

---

# 8) Tài liệu bổ sung mình thấy **rất cần** cho team data và giao tiếp hai bên

Đây là phần mình nghĩ quan trọng không kém schema.

## 8.1. `CHART_DATA_CONTRACT.md`
**Mục đích**  
Làm tài liệu “luật chơi” giữa data team và system team.

**Nội dung phải có**
- định nghĩa 3 loại chart
- field nào bên hệ thống chịu trách nhiệm
- field nào data team chỉ đọc, không sửa
- format file xuất
- naming conventions
- versioning rules

**Tại sao cần**
Nếu không có file này, hai bên sẽ tranh luận lặp lại:
- “field này ai derive?”
- “bản nào là canonical?”
- “data team có được sửa sao không?”

---

## 8.2. `CHART_FIELD_DICTIONARY.md`
**Mục đích**  
Giải thích từng field, ví dụ:
- `cuc`
- `ban_menh`
- `trang_sinh`
- `tuan_khong`
- `phi_hoa.hoa_ky_to`

**Mỗi field nên có**
- tên field
- loại dữ liệu
- bắt buộc hay không
- nguồn lấy từ đâu
- ví dụ giá trị hợp lệ
- ai chịu trách nhiệm sinh

**Tại sao cần**
Đây là tài liệu giúp annotator và dev nói cùng một ngôn ngữ.

---

## 8.3. `DERIVATION_RULEBOOK.md`
**Mục đích**  
Ghi rõ rule cho các field derived.

**Ví dụ**
- `menh_position` lấy thế nào
- `than_position` lấy từ đâu
- `elemental_flags` tính ra sao
- `tam_hop_branches` table nào
- `luc_hai_branch` table nào
- khi nào `phi_hoa.available = false`

**Tại sao cần**
Tránh việc mỗi dev tự suy diễn semantic khác nhau.

---

## 8.4. `TEAM_HANDOFF_CHECKLIST.md`
**Mục đích**  
Checklist giao nhận chart từ system sang data.

**Mỗi chart trước khi giao phải pass**
- đủ 12 cung
- `house_name` chuẩn hóa
- `major_stars` / `aux_stars` đã tách
- `menh_position` / `than_position` không null
- `chart_repr` và `chart_semantic` validate pass
- file bundle lưu đúng folder

---

## 8.5. `ANNOTATOR_GUIDE_FOR_CHART_READING.md`
**Mục đích**  
Cho data team biết cách dùng `chart_repr` và `chart_semantic` để tạo câu hỏi.

**Phải có**
- nên nhìn `chart_repr` khi nào
- nên nhìn `chart_semantic` khi nào
- dùng `focus_relations` ra sao
- dùng `star_index` ra sao
- với câu Direct / One-hop / Two-hop thì ưu tiên field nào

---

## 8.6. `SEMANTIC_QUERY_PLAYBOOK.md`
**Mục đích**  
Tài liệu cho system team hoặc prompt team về cách dùng `chart_semantic`.

**Ví dụ**
- hỏi về tài lộc -> lấy `Tài Bạch`, `Mệnh`, `Quan Lộc`, `tam_hop`, `star_index`
- hỏi về hôn nhân -> lấy `Phu Thê`, `Mệnh`, `Thiên Di`
- hỏi về sao X ở đâu -> tra `star_index`

**Tại sao cần**
Đây là cầu nối giữa semantic schema và retrieval pipeline.

---

## 8.7. `KNOWN_LIMITATIONS.md`
**Mục đích**  
Công khai các giới hạn hiện tại để data team không kỳ vọng sai.

**Ví dụ cần ghi rõ**
- Phi Hóa chưa fully implemented
- Can cung có thể null ở một số chart nếu engine không cấp
- Cách cục mới ở mức rule cơ bản
- Không dùng `chart_semantic` để thay thế sách luận

---

## 8.8. `CHANGELOG_CHART_SCHEMA.md`
**Mục đích**  
Theo dõi thay đổi schema.

**Ví dụ**
- v1.0: chart_repr cơ bản
- v2.0: thêm `trang_sinh`, `tuan_khong`, `triet_khong`
- v2.1: thêm `phi_hoa` hook

**Tại sao cần**
Dataset dài ngày mà không version hóa thì sau này rất khó audit.

---

# 9) Tài liệu bổ sung riêng cho workflow team data

## 9.1. `CHART_SELECTION_REGISTRY.md`
Ghi:
- vì sao chọn chart này
- diversity dimensions
- chart nào test điểm nào

## 9.2. `QUESTION_DESIGN_MATRIX.md`
Map:
- chart_id
- topic
- complexity
- entities
- semantic fields liên quan

## 9.3. `CHART_TO_QUESTION_TRACE.csv`
Mỗi question nên trace được:
- dùng chart nào
- nhà/cung nào liên quan
- semantic fields nào liên quan
- nguồn sách nào liên quan

## 9.4. `ANNOTATION_DISPUTE_PROTOCOL.md`
Nếu B và C không đồng ý:
- ai adjudicate
- khi nào escalate cho A
- có được sửa chart semantic không hay chỉ sửa QA
- sửa chart thì phải mở issue cho system team thế nào

---

# 10) Bộ tài liệu tối thiểu mình khuyên phải có ngay

Nếu cần ưu tiên thực dụng, mình khuyên chốt 6 tài liệu này trước:

1. `CHART_DATA_CONTRACT.md`
2. `CHART_FIELD_DICTIONARY.md`
3. `DERIVATION_RULEBOOK.md`
4. `TEAM_HANDOFF_CHECKLIST.md`
5. `ANNOTATOR_GUIDE_FOR_CHART_READING.md`
6. `KNOWN_LIMITATIONS.md`

Chỉ cần 6 file này là việc phối hợp đã đỡ rối rất nhiều.

---

# 11) Khuyến nghị cuối cùng để bàn giao cho team hệ thống

## Chốt kỹ thuật
- `chart_full` là canonical kỹ thuật
- `chart_repr` là canonical cho data/benchmark
- `chart_semantic` là canonical cho retrieval
- không dùng Markdown semantic trong workflow chính thức

## Chốt code
- giữ `tuvi_calculator.py` cho normalize raw engine
- tách projection + semantic rules ra file mới
- viết validator cho cả 3 schema

## Chốt phối hợp
- data team **không sửa tay** `chart_full`
- data team có thể report bug ở `chart_repr` / `chart_semantic`
- mọi derived field phải có rulebook
- mọi thay đổi schema phải có changelog
