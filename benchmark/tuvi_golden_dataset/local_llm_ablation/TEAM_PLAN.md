# Phân công A/B/C/D

## A — integration owner

- Chạy notebook 00 hai lần và tạo hai private model datasets.
- Chạy notebook 01 local, freeze bundle 300 cases.
- Upload/share context dataset và gửi notebook 02 cho B/C/D.
- Nhận ba judge-shard ZIP từ B/C/D, chạy notebook 03 `ACTION='merge'` và freeze kết quả.
- Viết report/slide; gửi ba thành viên review.

## B — `graph_dense_rrf`

```python
RUNNER = 'B'
```

Chạy Qwen/Gemma, tải hai ZIP về local, sau đó notebook 03 `ACTION='judge', RUNNER='B'` để chấm 200 answers. Giao A judge-shard ZIP.

## C — `semantic_gs_rrf_rerank_k40`

```python
RUNNER = 'C'
```

Chạy hai model, judge 200 answers với `RUNNER='C'`, giao judge-shard ZIP. Review phần quality-first và reranker-on.

## D — `semantic_gs_rrf_no_rerank_reference`

```python
RUNNER = 'D'
```

Chạy hai model, judge 200 answers với `RUNNER='D'`, giao judge-shard ZIP. Review phần no-rerank, latency và limitations.

## Format bàn giao

Mỗi lần giao artifact phải ghi:

- runner/config key;
- model ID và revision;
- Kaggle GPU type;
- completed/failed count;
- tên/link prediction ZIP và judge-shard ZIP;
- warning hoặc retry đã xảy ra.

## Definition of done

- [ ] Bundle 300/300, zero failed.
- [ ] Qwen 300/300, zero failed.
- [ ] Gemma 300/300, zero failed.
- [ ] Judge shard B/C/D: mỗi shard 200/200, zero failed.
- [ ] A merge 3 shards thành 600/600, zero failed, không gọi API lại.
- [ ] CSV có đúng 6 rows.
- [ ] Ba thành viên review report và slide.
- [ ] Limitations ghi 4-bit, Gemini judge bias, GPU latency và thiếu exact chunk hit.
