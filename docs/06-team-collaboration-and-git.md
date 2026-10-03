# 06 — Workflow solo và Git

## Trách nhiệm và review

Chủ repository là owner và người chốt cho cả ba vai trò Data Lead, Model Lead, Pipeline Lead. Codex hỗ trợ triển khai/review; không tự phê duyệt dataset, label, split, metric hay model promotion. Reviewer trong docs/template là owner tự review có bằng chứng, có thể được Codex hỗ trợ; không yêu cầu người thứ hai.

- Data: source/license audit, mapping, conversion, grouped split, QA và DVC version; bàn giao dataset contract có phiên bản.
- Model: config, experiment, metrics và model artifact/checksum có định danh.
- Pipeline: inference/tracking/events và web đúng milestone; dùng model artifact theo ID.

## Quy trình task

Backlog → Ready → In Progress → Review → Blocked hoặc Done. GitHub Projects tùy chọn; có thể theo dõi bằng WORKLOG. Mỗi task có một owner, một mục tiêu, input/output, dependency và tiêu chí nghiệm thu.

Tạo branch từ `main`, ví dụ `infra/s0-foundation`. Trước merge: xem diff, chạy CI checks, ghi kết quả/giới hạn, owner tự review và chốt. Nếu dùng PR, ghi issue (nếu có), owner/người chốt, hỗ trợ review và data/experiment/privacy impact. Bảo vệ `main` bằng CI; không yêu cầu approval từ người thứ hai. Owner vẫn phải human review dữ liệu/model, license/consent, provenance, fixture, chống leakage và không tune trên test set.

## Artifact và nhịp làm việc

Thay đổi data/model: kiểm tra → version/pointer mới → `dvc add` → `dvc push` thành công → commit pointer/config/metrics → Git push/PR. Không sửa raw data hoặc công bố pointer chưa có artifact trên remote. Owner ghi quyết định review và vấn đề còn mở.

Cập nhật WORKLOG với kết quả/blocker và bước tiếp theo. Task train phải có input, config, experiment, output và DoD. P0 chỉ hoàn tất khi clone/cài/check và DVC push/pull bằng cache sạch có bằng chứng.
