-- Một người dùng không thể lưu hai lá số có cùng họ tên, không phân biệt hoa/thường
-- hoặc khoảng trắng ở đầu/cuối. Cần xử lý các bản ghi trùng hiện có trước khi áp dụng.
CREATE UNIQUE INDEX IF NOT EXISTS uq_la_so_user_label_normalized
  ON la_so (user_id, lower(btrim(label)));
