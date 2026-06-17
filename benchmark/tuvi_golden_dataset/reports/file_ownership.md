# File Ownership & Conflict Management

Để tránh conflict khi làm việc trên cùng bộ dataset, mỗi thành viên chịu trách nhiệm chính (Owner) cho các nhóm file hoặc phân vùng dữ liệu sau:

| Area | File/Path Pattern | Owner | Notes |
|------|-------------------|-------|-------|
| Setup | `guideline/*`, `workplan.md` | A | Duy nhất A được phép chốt thay đổi |
| Charts | `charts/*` | A | A freeze registry, C export dữ liệu |
| Source | `corpus/*` | B | B chuẩn hóa, A review/freeze |
| Samples | `samples/question_slots.csv` | A | A chốt slot matrix |
| Annotations | `annotations/gold_sections_{A,B,C}.jsonl` | A/B/C | Mỗi người làm batch của mình |
| Final Release | `release/*` | A | Chỉ A merge và freeze |
| Reports | `reports/*` | A | A quản lý tổng, B/C cập nhật status |

**Nguyên tắc:**
- Không ai sửa file của người khác mà không thông qua PR/Merge từ Owner.
- Mọi annotation ban đầu phải tách file theo cá nhân (A, B, C) trước khi A merge.