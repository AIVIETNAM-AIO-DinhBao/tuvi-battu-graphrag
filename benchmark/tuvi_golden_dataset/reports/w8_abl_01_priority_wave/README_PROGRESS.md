# Theo dõi W8-ABL-01 Priority Wave

Từ repository root, mở PowerShell khác và chạy:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File benchmark/tuvi_golden_dataset/reports/w8_abl_01_priority_wave/watch_progress.ps1
```

Xem một lần:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File benchmark/tuvi_golden_dataset/reports/w8_abl_01_priority_wave/watch_progress.ps1 -Once
```

Milestones:

- `100/400`: sparse-only hoàn tất.
- `200/400`: dense+sparse hoàn tất.
- `300/400`: no-reranker hoàn tất.
- `400/400`: weighted-sum và toàn wave hoàn tất.

Nguồn tiến độ:

- `full100/checkpoint/checkpoint_summary.json`
- `full100/monitor_status.json`
- `full100/stdout.log`
- `full100/stderr.log`
- `full100/evaluation_report.json`

Dừng watcher không dừng benchmark.