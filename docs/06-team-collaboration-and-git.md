# 06 — Cộng tác Nhóm và Git

## Quyền sở hữu và bàn giao (Ownership & Handoff)

### Data Lead

Chịu trách nhiệm: source audit, mapping, conversion, grouped split, QA và DVC data version. Bàn giao là contract `data/processed/exam/` cụ thể, không phải "dataset xong". Reviewer: Model Lead.

### Model Lead

Chịu trách nhiệm: config, training/evaluation, W&B/logs, metrics và model candidate. Bàn giao ghi rõ experiment/model artifact/checksum cụ thể. Reviewer: Pipeline Lead.

### Pipeline Lead

Chịu trách nhiệm: recorded inference, tracking, tích hợp event/risk, structured output và về sau là web. Sử dụng model artifact theo ID, không bao giờ dùng "some best.pt" tùy ý. Reviewer: Data Lead hoặc Model Lead.

Tất cả thành viên phải tái tạo được smoke run và hiểu dataset/split/metrics.

## GitHub Projects

Một board duy nhất: Backlog → Ready → In Progress → Review → Blocked → Done. Các trường: Assignee, Area (`Data/Model/Pipeline/Infra/Docs`), Priority (`P0/P1/P2`), Iteration. Mỗi issue chỉ có một owner chính; dependency và reviewer phải được ghi rõ ràng.

Tạo branch từ `main`: `data/12-canonical-dataset`, `model/18-e001-baseline`, `pipeline/24-jsonl-inference`. PR gồm `Closes #N`, data/experiment/privacy impact và bước verification. Bảo vệ `main`; yêu cầu CI + một lượt review.

## Thứ tự làm việc với artifact

Với thay đổi data/model: chạy kiểm tra → `dvc add` output lớn cần thiết → `dvc push` thành công → commit pointer/config/metrics → Git push/PR. Thứ tự này tránh Git trỏ đến artifact chưa có trên remote.

## Lịch họp hàng tuần

Họp 30 phút để lên kế hoạch/review: chuyển task Ready, kiểm tra bàn giao, review hypothesis/kết quả/blocker của experiment. Cập nhật async: Yesterday/Today/Blocked. Không có task chỉ ghi "train model"; phải ghi rõ input, config, output và DoD (Definition of Done).
