# 20 — Functional Requirements (Yêu cầu Chức năng)

Các giá trị status: Accepted/Draft/TBD. Mỗi requirement đã được triển khai cần có một test hoặc evaluation artifact.

| ID | Yêu cầu | Phase | Điều kiện nghiệm thu |
|---|---|---|---|
| FR-VID-001 | Xử lý một video đã ghi sẵn và được cấp phép | P5 | session đạt completed/failed với source checksum |
| FR-VID-002 | Giữ nguyên frame index và video time | P5 | contract test và sample JSONL |
| FR-DET-001 | Emit structured prediction hành vi/người | P3/P5 | schema validate model/version/confidence/xyxy |
| FR-TRK-001 | Gán track ID tạm thời, cục bộ trong session | P5 | báo cáo stability trên fixed clip |
| FR-EVT-001 | Aggregate raw prediction qua versioned rule | P6 | unit fixture + event validation report |
| FR-RSK-001 | Tạo risk signal có giới hạn và giải thích được | P6 | contributing event/rule version có thể truy vết |
| FR-EVD-001 | Liên kết evidence đến source frame/time/event | P6 | các trường checksum/window/retention tồn tại |
| FR-REV-001 | Người dùng có thể acknowledge/dismiss/confirm behavior/add note | P7 | integration flow test |
| FR-UI-001 | Hiển thị session/track/event/risk/evidence thật | P7 | không có metric placeholder; recorded flow test |
| FR-EXP-001 | Liên kết model artifact đến code/data/config/metrics | P3 | experiment card/run JSON đầy đủ |

Webcam/live, seat mapping, clip evidence và CSV export là yêu cầu Should/Could, được kích hoạt qua issue riêng sau khi các yêu cầu Must pass.
