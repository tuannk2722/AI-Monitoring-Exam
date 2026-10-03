# Label Specification v1 — Draft (Bản thảo Đặc tả Nhãn)

Version: `label-map-v0.2-draft`. Owner/người chốt: chủ repository. Review hỗ trợ: Codex. Chưa đóng băng.

## Quy tắc chung

- Chỉ annotate bằng chứng quan sát được; nhiều hành vi có thể cùng tồn tại.
- Không suy diễn ý định/vi phạm.
- Unit **person** theo [ADR-011](../decisions/ADR-011-person-unit-phone-definition.md); biểu diễn normal/formulation A/B còn mở. Đây là version tài liệu; config runtime/mapping chưa nâng version.
- Nếu bằng chứng quá nhỏ/bị che/mơ hồ, dùng ignore/exclusion có lý do đã được review.

## `phone_use`

**Positive**: người cầm/tương tác rõ với điện thoại, hoặc điện thoại trên bàn có bằng chứng thị giác gắn được với người tương ứng (owner xác nhận R12 ngày 2026-10-04). Box bao người, không bao riêng phone/tay.
**Negative candidate**: đã review không có bằng chứng thuộc hai tình huống trên; vật thể xác nhận không phải phone.
**Unknown/ignore**: quá nhỏ, bị che hoặc không xác định được người liên quan. Không gán phone cho người gần nhất, không suy quyền sở hữu hay biến unknown thành negative. Nhãn gồm phone presence có liên kết với người; không tự kết luận vi phạm.

## `looking_around`

**Positive candidate**: định hướng quan sát được của đầu/mắt lệch khỏi hướng làm việc dự kiến theo quy tắc pose/duration đã review.
**Negative candidate**: di chuyển mắt thông thường khi đọc giấy/điều chỉnh tư thế mà không thỏa quy tắc.
Nhãn này không trực tiếp có nghĩa là vi phạm.

## `normal`

Biểu diễn sự vắng mặt đã review của cả `looking_around` và `phone_use` (không gồm unknown/occluded) chỉ khi formulation B cần một explicit negative class. Với formulation A, background/no target có thể không phải là một annotated person-behavior box. P1 phải chọn và tài liệu hóa.

## Source aliases (Ánh xạ từ nguồn gốc)

`head_turn` chỉ được map sang `looking_around` sau khi sample semantics khớp nhau. `Phone use` chỉ được map sang `phone_use` sau audit. `cheating`, `no_cheating` và các nhãn ý định khác yêu cầu re-review/relabel hoặc từ chối — không bao giờ map trực tiếp theo tên.
