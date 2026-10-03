# 23 — Chiến lược Testing và Chất lượng

| Lớp | Kiểm tra bắt buộc |
|---|---|
| Data | media bị hỏng/thiếu/orphan; YOLO ranges; class mapping; trùng lặp/group leakage; tính toàn vẹn split |
| Unit | thứ tự bbox; schema validation; grouped split deterministic; temporal/risk rule |
| Contract | JSONL inference ↔ các trường tracker/event/web và version |
| Training | mini/smoke run, checkpoint/resume, bản ghi environment/run |
| Metric | fixture đã biết và per-class serialization |
| Model regression | validation/holdout slice cố định so với candidate được chọn |
| Integration | recorded video → prediction → track → event → review |
| UI | luồng upload/error/status/review; không có mock data |
| Performance | media/hardware/warm-up/repeat/percentile cố định |

CI chạy unit/compile/lint/repository check cơ bản mà không cần GPU/data. ML smoke phải thực hiện thủ công/Colab vì CI không sở hữu dataset/GPU. Code pass không đồng nghĩa với data/model quality gate pass.

Thay đổi dataset/model phải kèm report artifact và human review; client-side validation không bao giờ thay thế server/contract validation.

Solo: reviewer/human review là owner tự review và ghi quyết định; Codex hỗ trợ, không thay owner phê duyệt. Áp dụng workflow 06; các gate dữ liệu, test set và chất lượng giữ nguyên.
