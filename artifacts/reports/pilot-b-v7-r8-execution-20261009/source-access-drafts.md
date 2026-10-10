# Yêu cầu truy cập nguồn — bản chuẩn bị, chưa gửi

Owner: chủ repository. Owner xác nhận **nghiên cứu cá nhân** ngày2026-10-09. Đây là nội dung có thể review trước khi liên hệ. Không chứa thông tin cá nhân được suy đoán; các trường TBD phải được owner điền. Không tự ký hoặc gửi email. Khả năng cấp controlled academic access cho cá nhân còn unknown, cần publisher xác nhận.

## IMPROVE — ưu tiên desk-phone

Đích theo [hướng dẫn publisher](https://github.com/BiDAlab/IMPROVE#instructions-for-downloading-improve): atvs@uam.es. Subject yêu cầu: `[DATABASE: IMPROVE]`. [Thỏa thuận v3](https://github.com/BiDAlab/IMPROVE/blob/main/License/IMPROVE_License_Agreement_v3.pdf) cần owner đọc/ký; bản ký chưa có.

Nội dung đề xuất:

> Tôi là [TBD: tên người xin], thực hiện nghiên cứu cá nhân, không đại diện đơn vị. Email [TBD], điện thoại [TBD], địa chỉ bưu chính [TBD]. Tôi chuẩn bị nghiên cứu classifier trên crop từng người với hai target quan sát được: mobile phone presence/interaction và hướng nhìn ra khỏi vùng làm việc riêng; không suy ý định gian lận, không định danh hoặc áp dụng quyết định kỷ luật. Đề nghị xác nhận có thể cấp truy cập cho người nghiên cứu cá nhân, và cung cấp development subset RGB gồm phone trên bàn và trường hợp không phone, metadata camera/session, liên kết thời gian hành vi và điều kiện sử dụng cho trích frame, crop, resize224 và tái annotation P/N/U. Tôi không upload raw media lên dịch vụ công khai. Vui lòng xác nhận phạm vi nghiên cứu này, điều kiện công bố các ví dụ đã xử lý và giới hạn phát hành annotation/derivative. Thỏa thuận đã ký gửi lúc [TBD: ngày/giờ], nếu được owner hoàn tất.

Các nhóm possession/use của IMPROVE khác mobile-only presence semantics ADR018. Cần tự annotation lại; không dùng nhãn thí nghiệm làm canonical. Nếu được cấp subset, khai báo development role trước khi xem; metadata các session chưa xem có thể dành nghiên cứu holdout sau quyết định riêng.

## HCCB — ưu tiên crowded/co-occurrence

Đích theo [publisher](https://github.com/FX-CMX/ODER-HSFNet): corresponding author chu52_2004@163.com; first author24210811000473@stu.ustl.edu.cn. Owner chọn người nhận; chưa gửi. [Thỏa thuận data-use](https://github.com/FX-CMX/ODER-HSFNet/blob/main/docs/data_use_agreement.md) cần nghiệm thu cụ thể.

> Tôi là [TBD], thực hiện nghiên cứu cá nhân, xin xác nhận khả năng cấp controlled academic access cho cá nhân để nghiên cứu multi-target phone/gaze trên crop được review, không định danh, chấm điểm học sinh hoặc giám sát thương mại. Đề nghị subset development có camera/room/session/lineage metadata; raw hoặc ảnh đã desensitized vẫn giữ đủ evidence phone ownership và own-workarea. Tôi cần tái annotation P/N/U, gồm phone+looking cùng một người, vì annotation single-class priority hiện tại không thể biểu diễn co-occurrence. Vui lòng xác nhận quyền crop/letterbox224/tái nhãn và điều kiện đưa các ví dụ cần thiết vào báo cáo local/nghiên cứu.

## Quyết định còn thiếu

| Trường | Owner | Điều kiện chốt |
|---|---|---|
| Tư cách nghiên cứu | Owner | **Đã chốt: cá nhân**, chưa chứng minh publisher chấp nhận |
| Người đứng tên và contact fields | Owner | Thông tin thật được cung cấp cho đúng publisher |
| Chấp nhận/ký thỏa thuận nguồn access-controlled | Owner | Đã đọc phạm vi data-use và crop/tái annotation |
| Gửi nội dung đến publisher | Owner | Chỉ sau lệnh gửi rõ ràng của user; hiện yêu cầu chỉ tìm nguồn |
| Chọn development/holdout metadata partition | Owner | Metadata nhóm đủ, quyết định trước khi xem holdout |
