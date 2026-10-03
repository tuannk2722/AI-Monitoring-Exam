# Dataset Research — Bản ghi làm việc

## Danh mục candidate

| ID | Candidate | Trạng thái hiện tại | Bằng chứng còn thiếu |
|---|---|---|---|
| DS-SCB5 | SCB5 | CANDIDATE / chưa được chấp nhận | URL/version/license/checksum chính xác; định nghĩa class; metadata nhóm; sample audit |
| DS-RF-EXAM | Roboflow Exam Cheating CV export/model source | CANDIDATE / chưa được chấp nhận | project/version/license/export chính xác; nguồn gốc; mapping; trùng lặp/domain gap |

Không được ghi tên dataset và đánh dấu là đã chọn. Data Lead tạo candidate card riêng cho từng nguồn và đính kèm audit report/checksum/bằng chứng license.

## Hypothesis kết hợp nguồn

SCB5 có thể đóng góp mẫu hành vi giống kỳ thi; Roboflow có thể mở rộng mẫu đã annotate. Kết hợp hai nguồn chỉ hợp lệ khi: canonical semantics khớp nhau, provenance/trùng lặp đã rõ ràng, license cho phép sử dụng, và grouped split ngăn được source/video leakage. Source được giữ lại trong manifest để có thể báo cáo metrics per-source và domain bias.

## Decision gate (Điều kiện quyết định)

Chấp nhận/từ chối mỗi nguồn độc lập. Nếu một nguồn thất bại về quyền/chất lượng/mapping, baseline có thể dùng nguồn còn lại hoặc một subset đã review. Số lượng mẫu lớn hơn không phải lý do để giữ lại nhãn không tương thích.
