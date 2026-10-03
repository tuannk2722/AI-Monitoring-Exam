# 15 — ML Experiment Management (Quản lý Experiment)

## Nguồn chuẩn tắc (Canonical Source)

YAML config + Git commit + DVC data/model pointer + bản ghi experiment JSON/Markdown là canonical. W&B là tùy chọn shared visualization/logger khi tất cả thành viên có thể sử dụng; project vẫn có thể tái tạo nếu W&B không khả dụng. Không upload media nhạy cảm lên W&B khi chưa có policy phê duyệt.

## Định danh Experiment

Dùng `E001`, `E002`... trên board/báo cáo, có thể kèm dated slug. Mỗi run gồm: owner, reviewer, hypothesis, parent run, start/end/status, lệnh chạy, code commit/dirty flag, environment, phiên bản dataset/split/label, config đã resolve, metrics, artifact/checksum, observations và decision.

## Lưu trữ

- **Git**: code/config/docs/metrics nhỏ/experiment card.
- **DVC Drive remote**: dataset, `best.pt` được select, `last.pt` cần thiết, plots/media lớn.
- **W&B**: params/metrics/link; không phải bản sao duy nhất của model/data.
- Không giữ mọi checkpoint theo từng epoch vô thời hạn.

## Promotion Review (Phê duyệt đề xuất model)

Reviewer xác minh: provenance, không dùng sai test set, hành vi per-class/error/holdout, chi phí tài nguyên và license model/software. Đường dẫn candidate rõ ràng, ví dụ `artifacts/models/E003/weights/best.pt`; không được bàn giao thủ công bằng file `best_final_v2.pt` tùy tiện.

Solo: reviewer/human review là owner tự review và ghi quyết định; Codex hỗ trợ, không thay owner phê duyệt. Áp dụng workflow 06; các gate dữ liệu, test set và chất lượng giữ nguyên.
