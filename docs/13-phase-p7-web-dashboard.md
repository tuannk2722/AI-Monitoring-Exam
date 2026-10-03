# 13 — P7 Minimal Web Dashboard

ADR-007 đã loại bỏ Django prototype vì nó không có khả năng AI/backend nào có thể tái sử dụng và đã mã hóa sai ngữ nghĩa "cheating". Target P7 là FastAPI + Jinja2/HTML + JavaScript nhỏ + SQLite chạy local; chỉ bắt đầu triển khai sau khi các contract P6 ổn định.

## Luồng recorded session

1. Chọn video/session đã ghi và được cấp phép.
2. Hiển thị trạng thái xử lý (`queued/running/completed/failed`) và chỉ dùng metadata thật.
3. Hiển thị video, bbox/track ID tạm thời, event timeline, risk signal và evidence.
4. Reviewer thực hiện hành động review trung lập và ghi chú.
5. Export structured summary nếu còn thời gian.

Cấm: FPS/metric/alert giả, validation chỉ ở client-side, route trả về `None`, IP-camera URL hack. Server phải tự tạo tên file, validate MIME/extension/size/duration, enforce local access và render các trường không khả dụng đúng như không khả dụng.

Live Start/Pause/Stop/WebSocket và sơ đồ ghế ngồi trong lớp học không thuộc phần web slice đầu tiên. Nếu dashboard chạy vượt ra ngoài localhost, bắt buộc phải có basic authentication/access guard và privacy review.
