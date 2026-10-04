# ADR-011 — Person unit và định nghĩa phone_use sau owner review

Cập nhật 2026-10-04: [ADR-012](ADR-012-formulation-b-multilabel.md) chốt B, normal/co-occurrence và crop context. Các ghi chú A/B pending dưới đây là lịch sử; person unit/phone definition giữ nguyên.

- Status: Accepted cho quyết định dưới đây; dataset acceptance và A/B vẫn pending.
- Date: 2026-10-04. Decision owner: chủ repository. Hỗ trợ triển khai/review: Codex.
- Evidence: [18 câu trả lời owner](../data/candidates/Roboflow-phone-use-20261004-review.md), [manifest](../../artifacts/reports/roboflow-20261004/owner-decisions.json).

## Context

Roboflow v1 trộn person/head/hand/phone boxes. Owner trả lời toàn bộ checklist và xác nhận thêm: “Mở rộng phone_use: cầm/tương tác hoặc điện thoại trên bàn gắn được với người”.

## Decision

1. Unit là **person**, không phải phone/tay hoặc toàn cảnh nhiều người. Box nguồn phải QA/vẽ lại nếu không khớp; không suy person box bằng cách phóng đại phone box.
2. `phone_use`: người cầm/tương tác rõ với điện thoại **hoặc điện thoại trên bàn có bằng chứng gắn được với người tương ứng**. Không gán cho người gần nhất; không rõ liên kết/vật thể thì unknown/ignore. Tên nhãn giữ nguyên nhưng bao gồm phone presence theo điều kiện này.
3. `normal`: vắng mặt **đã review** của cả `looking_around` và `phone_use`. Thiếu bằng chứng không phải normal. Cách mã hóa normal chờ A/B; nhiều hành vi có thể đồng xuất hiện.
4. R01/R07/R13 ignore phần thiếu bằng chứng; R06 loại box toàn cảnh; R09 relabel person; R10/R14 loại khỏi subset đề xuất; ảnh phụ đề/UI web loại khỏi train (R16, gồm R11 đã quan sát). R15 cần QA, chưa pass. R03 chốt phone_use cho mẫu cụ thể, không map toàn bộ ID0.
5. W01 relabel thủ công. W02 được clip biên ở preview mới, chỉ dòng đã review; không nới validator hay áp dụng hàng loạt warning khác.
6. Owner chấp nhận watermark stock khi chọn mẫu; đây không phải bằng chứng độc lập về quyền từng asset.
7. Owner xác nhận tiếp ngày 2026-10-04: bbox chỉ bao phần người nhìn thấy; không ước lượng cơ thể bị che dưới bàn. Box là hình chữ nhật bao các phần nhìn thấy của cùng người, có thể chứa khoảng che ở giữa; chưa đủ bằng chứng xác định người/hành vi thì giữ ngoài train.

## Consequences / giới hạn

Bổ sung ADR-002 về unit/semantics; **không chọn A/B**, không phê duyệt dataset, split, mapping toàn nguồn hay threshold. Không biến nhãn thành kết luận gian lận/kỷ luật. Label spec chuyển draft v0.2; config runtime chưa nâng version vì dataset/converter chưa phê duyệt.

Không đơn thuần xóa box ignore rồi giữ ảnh làm negative: cần mask/ignore được pipeline hỗ trợ, hoặc giữ ảnh ngoài batch train đến khi relabel đầy đủ. Hàng đợi quyết định không phải nhãn YOLO để train.
