# tuviqa_v1_release.jsonl Schema

This document describes the schema for the `tuviqa_v1_release.jsonl` dataset after the `gold_chunk_ids` and `required_entities` fields have been removed. The dataset consists of a series of JSON objects, where each object represents a question-answer pair related to a "Tử Vi" chart.

## Top-Level Object Structure

Each entry in the `jsonl` file is a JSON object with the following structure:

```json
{
  "id": "string",
  "chart_id": "string",
  "birth_info": {
    // ... details about birth information ...
  },
  "chart_repr": {
    // ... details about the "Tử Vi" chart representation ...
  },
  "question": "string",
  "question_complexity": "string",
  "gold_answer": "string",
  "expected_answer_summary": "string",
  "gold_context_spans": "array",
  "labels": {
    // ... details about labels ...
  }
}
```

## Field Descriptions

*   **`id`** (string): A unique identifier for the question-answer pair.
*   **`chart_id`** (string): An identifier linking to the specific "Tử Vi" chart used for the question.
*   **`birth_info`** (object): Contains details about the individual's birth.
    *   **`date_solar`** (string): Solar date of birth (e.g., "YYYY-MM-DD").
    *   **`time`** (string): Time of birth (e.g., "HH:MM").
    *   **`timezone`** (string): Timezone of birth (e.g., "Asia/Ho_Chi_Minh").
    *   **`gender`** (string): Gender of the individual ("Nam" or "Nữ").
*   **`chart_repr`** (object): Represents the "Tử Vi" chart details.
    *   **`chart_type`** (string): Type of chart (e.g., "TUVI").
    *   **`schema_role`** (string): Role of the schema (e.g., "chart_repr").
    *   **`schema_version`** (string): Version of the chart schema (e.g., "2.0").
    *   **`menh_position`** (string): Earthly branch of the "Mệnh" (Destiny) house.
    *   **`than_position`** (string): Earthly branch of the "Thân" (Body) house.
    *   **`ban_menh`** (string): Elemental destiny (e.g., "Thành Đầu Thổ").
    *   **`ngu_hanh_ban_menh`** (string): Five elements of "Ban Mệnh" (e.g., "Thổ").
    *   **`cuc`** (string): "Cục" of the chart (e.g., "Hỏa lục cục").
    *   **`am_duong_nam_nu`** (string): Yin-Yang harmony and gender (e.g., "Thuận Lý Nam").
    *   **`houses`** (array of objects): An array representing the 12 houses of the "Tử Vi" chart.
        *   Each house object contains:
            *   **`house_index`** (integer): Index of the house (1-12).
            *   **`house_name`** (string): Name of the house (e.g., "Thiên Di", "Tật Ách").
            *   **`earthly_branch`** (string): Earthly branch associated with the house.
            *   **`is_than_resident`** (boolean): True if "Thân" resides in this house.
            *   **`house_element`** (string): Elemental property of the house.
            *   **`yin_yang`** (string): Yin or Yang property of the house.
            *   **`dai_han_age`** (integer): Starting age for the Đại Hạn (Major Cycle).
            *   **`tieu_han_branch`** (string): Earthly branch for the Tiểu Hạn (Minor Cycle).
            *   **`trang_sinh`** (string): Tràng Sinh cycle status.
            *   **`tuan_khong`** (boolean): True if Tuan Khong applies.
            *   **`triet_khong`** (boolean): True if Triet Khong applies.
            *   **`major_stars`** (array of objects): Major stars in the house.
                *   Each major star object contains:
                    *   **`name`** (string): Name of the star (e.g., "Thiên Lương").
                    *   **`status`** (string or null): Status of the star (e.g., "Vượng", "Đắc", "Hãm").
            *   **`aux_stars`** (array of objects): Auxiliary stars in the house.
                *   Each auxiliary star object contains:
                    *   **`name`** (string): Name of the star.
                    *   **`status`** (string or null): Status of the star.
    *   **`derived_tags`** (array of strings): Tags derived from the chart (e.g., "dien-trach_co_hoa_loc").
*   **`question`** (string): The question posed for the chart.
*   **`question_complexity`** (string): Complexity level of the question (e.g., "Direct").
*   **`gold_answer`** (string): The golden answer to the question.
*   **`expected_answer_summary`** (string): A summary of the expected answer.
*   **`gold_context_spans`** (array): An array of objects, likely describing spans of text relevant to the answer from a context document. (Although empty in the provided sample, this field is part of the schema.)
*   **`labels`** (object): Categorical labels for the question.
    *   **`topic`** (string): Topic of the question (e.g., "identity").
    *   **`question_family`** (string): Family/category of the question (e.g., "core_identity").