# Đọc spec và thực hiện task

Bộ spec gồm **bốn tài liệu tự chứa thông tin làm task**. Đọc AGENTS/TASK, phần trạng thái và section phù hợp; không cần đọc archive/ADR/report gốc để biết dự án đã làm gì hoặc cần làm gì tiếp.

| Task | Đọc chính | Thông tin có ngay trong tài liệu |
|---|---|---|
| Phạm vi, kiến trúc, schema liên bước, video/tracking/events/web | [System](system.md) | Hiện trạng từng capability, FR/contracts, luồng end-to-end, gate/next work và decisions ADR |
| Tìm/audit nguồn, annotation/crop, group/split, dataset/loader | [Data](data.md) | Semantics/schema, nghiên cứu nguồn đã làm, releases v4–v7, corrections/coverage, QA workflow và holdout research |
| Training/evaluation, kết quả/error analysis, cải tiến E004 | [Training](training.md) | Recipe/code contract, metrics E001–E003, failure modes, E004 proposal/gates và việc phải chốt |
| Coding/resume, setup/checks, storage/reuse/reproduction, bàn giao | [Development](development.md) | Quy trình agent, checks theo diff, commands, lấy lại input lịch sử và cách cập nhật spec |

Quyết định Accepted nằm ngay trong spec liên quan với ID/phạm vi; Draft không cấp approval. Inputs/metrics/receipts có pin là bằng chứng kiểm/tái lập, chỉ mở khi task cần chi tiết cụ thể. Checkpoint task: `.codex/TASK.md`; [mẫu duy nhất](templates/task-template.md).
