# Bằng chứng nghiên cứu FPI-Det / SCB5

Ngày 2026-10-07; nghiên cứu, chưa approval release/training. [Báo cáo và đề xuất](../../../docs/data/fpi-scb-research-20261007.md).

- `fpi-metadata-audit.json`: kiểm hai COCO JSON, CSV, geometry, polarity và prediction upstream. Nhãn 0/1 giữ nghĩa số, chưa chốt nghĩa hành vi.
- `scb-local-reaudit.json`: quét lại đủ ba ZIP local, khớp hash/audit lịch sử; dữ liệu nguồn vẫn có lỗi geometry và overlap split.
- `scb-upstream-inventory.json`: kiểm central directory và một YAML nhúng; CRC/size/name overlap không thay SHA payload.
- `current-usage.json`: đếm source/usage từ ledger v5 đã pin.
- `provenance.json`: commit nguồn, URL, checksum các bản tải và script audit local.
- `verification.json`: kiểm tính nhất quán của báo cáo; PASS không có nghĩa dataset đã đạt gate.

Snapshot/script ở `outputs/fpi-scb-research-20261007/` (ignored). `audit_scb.py` gọi validator canonical; `audit_fpi.py` chỉ parse/tính toán annotation/CSV; `summarize.py` bổ sung join/overlap. Có thể đọc và chạy hai audit vào output mới sau khi điều chỉnh đường dẫn output; không chạy script trong `fpi/classification_task` tải từ upstream. Bản bổ sung targeted YAML/provenance được ghi riêng; không coi chạy lại script ban đầu là tái tạo mọi field hậu kiểm.

Không có training, inference E001/E002 trên nguồn mới hoặc upload media. Chưa tải payload ảnh FPI; chưa kiểm gần trùng toàn nguồn; không dùng kết quả metric upstream để tuning model dự án.
