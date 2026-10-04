# Annotation Guideline v1 — Draft (Bản thảo Hướng dẫn Annotation)

1. Unit person đã chốt tại [ADR-011](../decisions/ADR-011-person-unit-phone-definition.md); formulation A/B còn mở; không trộn lẫn person box, phone-object box và behavior clip dưới cùng một class ID.
2. Annotator gán pseudonymous sample ID và giữ lại metadata source/group.
3. Annotation dựa trên định nghĩa quan sát được; đánh dấu rõ trường hợp mơ hồ (ambiguous) và lý do ignore.
4. Reviewer kiểm tra mẫu phân tầng (stratified samples) theo từng class/source/điều kiện camera, và toàn bộ item được gắn cờ ambiguous.
5. Các vấn đề phải được sửa và gửi lại; chỉ batch đã review mới trở thành dataset version được phê duyệt.

Báo cáo QA ghi lại: batch, annotator/reviewer, phiên bản guideline, tổng số đã review, phân loại vấn đề, số lần sửa và bất đồng chưa giải quyết. Cần đo inter-annotator agreement trên một subset chung trước khi annotation số lượng lớn.

Quy tắc số về kích thước tối thiểu/visibility/thời lượng là TBD sau khi có thống kê về resolution/bbox/time. Đến lúc đó, không được tự bịa threshold hay gán nhãn hàng loạt các trường hợp biên.

## Áp dụng owner review Roboflow v1

Owner chốt ngày 2026-10-04: person bbox chỉ bao phần người nhìn thấy, không ước lượng cơ thể khuất dưới bàn. Hình chữ nhật bao các phần nhìn thấy của cùng người có thể chứa vùng bị che ở giữa. Bbox vẽ thử bởi Codex là đề xuất chờ owner review, chưa phải annotation được accepted.

Ví dụ P029 đã được owner sửa và xác nhận: hai người truyền cùng một điện thoại cho nhau, `phone_use` cho cả hai người tham gia tương tác; không ghi là phone trên bàn. Phê duyệt bbox cụ thể không thay thế QA đầy đủ các người/hành vi còn lại trong ảnh. P053/P065 bị loại vì nhiễu; không suy threshold chất lượng toàn nguồn từ hai quyết định này.

Theo label spec draft v0.2: phone cầm/tương tác hoặc trên bàn liên kết rõ với người đều positive. Không đủ bằng chứng là unknown. Khi relabel cần kiểm mọi người trong ảnh, tránh bỏ sót positive. Vẽ person bbox bằng review thủ công, không suy bbox người từ bbox tay/phone. Quy tắc phần thân bị cắt/che, co-occurrence và looking_around ở trường hợp biên còn cần pilot QA; không tự đặt ngưỡng.

Ignore không phải xóa dòng YOLO rồi coi ảnh là negative. Trước khi có cơ chế ignore phù hợp formulation, giữ ngoài batch train các ảnh còn vùng/person chưa giải quyết. Xóa box toàn cảnh cũng cần kiểm completeness trước khi dùng ảnh.

UI web/phụ đề: loại khỏi train theo owner; rà toàn subset, chưa có detector tự động cho policy này. R15/ảnh nhiễu cần review riêng; watermark stock được owner chấp nhận trong chọn mẫu. W01 relabel thủ công; W02 chỉ preview clip geometry, semantics chưa pass. Không biến quyết định mẫu thành mapping toàn lớp nguồn.
