# Theo dõi W8-EVAL-01

Mở một PowerShell khác tại repository root và chạy:

```powershell
powershell -ExecutionPolicy Bypass -File benchmark/tuvi_golden_dataset/reports/w8_eval_01/watch_progress.ps1
```

Xem một lần, không refresh:

```powershell
powershell -ExecutionPolicy Bypass -File benchmark/tuvi_golden_dataset/reports/w8_eval_01/watch_progress.ps1 -Once
```

Các nguồn tiến độ độc lập:

- `production_full100/checkpoint/checkpoint_summary.json`: cập nhật atomically sau từng câu.
- `production_full100/stdout.log`: summary cuối của runner.
- `production_full100/stderr.log`: warning/error live.
- `production_full100/process.json`: PID và thời điểm bắt đầu.
- `production_full100/monitor_status.json`: heartbeat của monitor.
- `production_full100/evaluation_report.json`: xuất hiện khi run hoàn tất.

Dừng watcher bằng `Ctrl+C` không dừng benchmark.

Run hiện đã hoàn tất `100/100`, `failed=0`. Detached worker không đọc được exit code của venv launcher và để trường exit code rỗng; đây là telemetry limitation của wrapper. Canonical `evaluation_report.json` có `status=completed`, checkpoint có `100/100`, và direct resume verification trả exit code `0` với `executed=0`, `resumed=100`.