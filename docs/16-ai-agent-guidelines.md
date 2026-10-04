# 16 — Hướng dẫn cho AI Coding Agent

Quy tắc canonical nằm trong `AGENTS.md` ở root. Với mỗi task, agent đọc index này và chỉ đọc docs/ADR accepted liên quan, nêu rõ assumptions/acceptance criteria, và báo cáo tests/TBD sau khi hoàn thành.

Agent được phép: triển khai script/test/docs/config đã được phân công. Agent không được: tự chọn data/class/split/model/metric/threshold/risk/scope, thay đổi raw data, upload media cá nhân, commit secret, hoặc coi notebook output là source of truth.

Với code conversion/split/metric của dataset, yêu cầu reviewer và fixture. Strip notebook output chứa media/token/path. Nếu một quyết định còn thiếu, duy trì tiến độ trên các phần độc lập và tạo TBD chính xác thay vì bịa một con số trông hợp lý.

Solo: reviewer/human review là owner tự review và ghi quyết định; Codex hỗ trợ, không thay owner phê duyệt. Áp dụng workflow 06; các gate dữ liệu, test set và chất lượng giữ nguyên.

## Bộ nhớ task và tiếp tục sau compaction

Theo rule canonical [Task checkpoint trong AGENTS.md](../AGENTS.md), mỗi task dùng [`.codex/TASK.md`](../.codex/TASK.md) làm checkpoint hiện hành. Agent đọc index và checkpoint khi bắt đầu/resume, kiểm chứng Git/files/artifacts, rồi tiếp tục bước còn lại; không mở lại quyết định đã chốt hoặc đọc lại docs không đổi chỉ vì context bị compact.

Checkpoint theo [task template](templates/task-template.md), ghi cả docs đã đọc, trạng thái thực tế, câu hỏi chưa trả lời, validation và bước tiếp theo. Cập nhật sau mốc quan trọng và trước bàn giao; đưa quyết định/kết quả bền vững về ADR/spec/WORKLOG tương ứng. TASK không có quyền ghi đè source of truth, phê duyệt data hoặc lưu credentials/media/danh tính thật.
