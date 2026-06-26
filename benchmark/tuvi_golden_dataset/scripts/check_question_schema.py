import json
import sys
EXPECTED_SCHEMA = {
    "slot_id": str,
    "chart_id": str,
    "question_complexity": str,
    "question_family": str,
    "topic": str,
    "owner": str,
    "reviewer": str,
    "question": str,
}


def validate_jsonl(file_path):
    total_lines = 0
    valid_lines = 0
    errors = []
    seen_slot_ids = set()

    print(f"Đang tiến hành quét file: '{file_path}'...\n")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                raw_line = line.strip()
                if not raw_line:
                    continue  # Bỏ qua dòng trống

                total_lines += 1
                line_errors = []

                # 1. Kiểm tra cú pháp JSON
                try:
                    data = json.loads(raw_line)
                except json.JSONDecodeError as e:
                    errors.append(f"Dòng {line_num}: Lỗi cú pháp JSON -> {e}")
                    continue

                if not isinstance(data, dict):
                    errors.append(f"Dòng {line_num}: Dữ liệu không phải là JSON Object")
                    continue

                current_keys = set(data.keys())
                required_keys = set(EXPECTED_SCHEMA.keys())

                # 2. Kiểm tra thiếu Key
                missing_keys = required_keys - current_keys
                if missing_keys:
                    line_errors.append(f"Thiếu key: {', '.join(missing_keys)}")

                # 3. Kiểm tra thừa Key lạ
                extra_keys = current_keys - required_keys
                if extra_keys:
                    line_errors.append(f"Thừa key lạ: {', '.join(extra_keys)}")

                # 4. Kiểm tra kiểu dữ liệu và chuỗi rỗng
                for key, expected_type in EXPECTED_SCHEMA.items():
                    if key in data:
                        val = data[key]
                        if not isinstance(val, expected_type):
                            line_errors.append(
                                f"Key '{key}' sai kiểu (Kỳ vọng chuỗi, nhận {type(val).__name__})"
                            )
                        elif isinstance(val, str) and not val.strip():
                            line_errors.append(f"Key '{key}' bị để trống giá trị")

                # 5. Kiểm tra trùng lặp slot_id
                s_id = data.get("slot_id")
                if s_id:
                    if s_id in seen_slot_ids:
                        line_errors.append(f"Bị trùng lặp slot_id: '{s_id}'")
                    else:
                        seen_slot_ids.add(s_id)

                # Ghi nhận kết quả dòng
                if line_errors:
                    errors.append(f"Dòng {line_num}: " + " | ".join(line_errors))
                else:
                    valid_lines += 1

    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file tại đường dẫn '{file_path}'")
        return

    # --- IN BÁO CÁO TỔNG HỢP ---
    print("=" * 50)
    print("                 KẾT QUẢ KIỂM TRA")
    print("=" * 50)
    print(f"• Tổng số dòng đã quét : {total_lines}")
    print(f"• Số dòng CHUẨN        : {valid_lines} ")
    print(f"• Số dòng LỖI          : {len(errors)} ")
    print("-" * 50)

    if errors:
        print("\nCHI TIẾT CÁC DÒNG BỊ LỖI:")
        for err in errors[:25]:  # Hiển thị tối đa 25 lỗi đầu
            print(f"  -> {err}")

        if len(errors) > 25:
            print(f"\n... và còn {len(errors) - 25} lỗi khác bị ẩn đi.")
    else:
        print("\nTuyệt vời! 100% file đúng chuẩn cấu trúc Schema.")


if __name__ == "__main__":
    # Nhận tên file từ Terminal hoặc dùng mặc định
    target_file = sys.argv[1] if len(sys.argv) > 1 else "final_questions.jsonl"
    validate_jsonl(target_file)