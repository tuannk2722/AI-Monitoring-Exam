# Annotation Guideline v1 — Draft (Bản thảo Hướng dẫn Annotation)

1. Chọn formulation/annotation unit trước; không trộn lẫn person box, phone-object box và behavior clip dưới cùng một class ID.
2. Annotator gán pseudonymous sample ID và giữ lại metadata source/group.
3. Annotation dựa trên định nghĩa quan sát được; đánh dấu rõ trường hợp mơ hồ (ambiguous) và lý do ignore.
4. Reviewer kiểm tra mẫu phân tầng (stratified samples) theo từng class/source/điều kiện camera, và toàn bộ item được gắn cờ ambiguous.
5. Các vấn đề phải được sửa và gửi lại; chỉ batch đã review mới trở thành dataset version được phê duyệt.

Báo cáo QA ghi lại: batch, annotator/reviewer, phiên bản guideline, tổng số đã review, phân loại vấn đề, số lần sửa và bất đồng chưa giải quyết. Cần đo inter-annotator agreement trên một subset chung trước khi annotation số lượng lớn.

Quy tắc số về kích thước tối thiểu/visibility/thời lượng là TBD sau khi có thống kê về resolution/bbox/time. Đến lúc đó, không được tự bịa threshold hay gán nhãn hàng loạt các trường hợp biên.
