# Label Specification v1 — Draft (Bản thảo Đặc tả Nhãn)

Version: `label-map-v0.2-draft`. Owner/người chốt: chủ repository. Review hỗ trợ: Codex. Chưa đóng băng.

## Quy tắc chung

- Chỉ annotate bằng chứng quan sát được; nhiều hành vi có thể cùng tồn tại.
- Không suy diễn ý định/vi phạm.
- Unit **person** theo [ADR-011](../decisions/ADR-011-person-unit-phone-definition.md); formulation B và multi-label theo [ADR-012](../decisions/ADR-012-formulation-b-multilabel.md). Config runtime/mapping chưa nâng version; còn cần hoàn thiện guideline/crop và schema classifier.
- Nếu bằng chứng quá nhỏ/bị che/mơ hồ, dùng ignore/exclusion có lý do đã được review.

## `phone_use`

**Positive**: người cầm/tương tác rõ với điện thoại, hoặc điện thoại trên bàn có bằng chứng thị giác gắn được với người tương ứng (owner xác nhận R12 ngày 2026-10-04). Box bao người, không bao riêng phone/tay.
**Negative candidate**: đã review không có bằng chứng thuộc hai tình huống trên; vật thể xác nhận không phải phone.
**Unknown/ignore**: quá nhỏ, bị che hoặc không xác định được người liên quan. Không gán phone cho người gần nhất, không suy quyền sở hữu hay biến unknown thành negative. Nhãn gồm phone presence có liên kết với người; không tự kết luận vi phạm.

## `looking_around`

**Positive trên ảnh tĩnh**: đầu/hướng nhìn thể hiện rõ đang nhìn sang người khác hoặc ra khỏi vùng bài làm, theo owner tại ADR-012.
**Unknown**: chỉ lệch đầu, cúi đọc/viết hoặc không rõ hướng nhìn khi chưa có đủ bằng chứng review; giữ ngoài train, không tự coi là negative. Tư thế đọc/viết một mình không chứng minh normal. Ảnh tĩnh không xác nhận được thời lượng; không tự đặt ngưỡng góc/thời gian.
Nhãn này không trực tiếp có nghĩa là vi phạm.

## `normal`

Người đang làm bài, đã review thủ công và không có bằng chứng `looking_around` hoặc `phone_use`. Không có box không có nghĩa normal; người chưa review hoặc thiếu bằng chứng do che/mờ giữ unknown. Normal không đồng thời với hai target.

## Co-occurrence và formulation

YOLO tìm người → crop → classifier multi-label. Khi cùng có bằng chứng, gán cả `phone_use` và `looking_around` cho cùng người. Chưa chọn head/loss hoặc schema vector/mask; không tự biến target unknown thành negative. Detector chỉ tìm người, không dùng lớp hành vi làm lớp detector.

## Source aliases (Ánh xạ từ nguồn gốc)

`head_turn` chỉ được map sang `looking_around` sau khi sample semantics khớp nhau. `Phone use` chỉ được map sang `phone_use` sau audit. `cheating`, `no_cheating` và các nhãn ý định khác yêu cầu re-review/relabel hoặc từ chối — không bao giờ map trực tiếp theo tên.
