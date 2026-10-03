# 19 — Bảng thuật ngữ và Domain Model

| Thuật ngữ | Định nghĩa |
|---|---|
| person/candidate | vùng người nhìn thấy trong frame; không phải danh tính đã xác minh |
| track ID | số nguyên tạm thời trong một session; không dùng ngoài phạm vi đó |
| prediction | một output của model gắn với frame/model/bbox/confidence |
| behavior | nhãn quan sát được (observable); không phải ý định hay vi phạm |
| event candidate | các observation đã aggregate nhưng chưa qua được rule |
| behavior event | event candidate đã qua một temporal rule có version |
| confidence | điểm output của model; không phải xác suất vi phạm đã được calibrate |
| risk | aggregate rule minh bạch từ các event; không phải confidence của model |
| alert | mục được đưa ra để con người xem xét |
| evidence | tham chiếu snapshot/clip kèm provenance và trạng thái retention |
| review | hành động/ghi chú của người xem xét trên alert/event |
| video time | offset trong media gốc; khác với processing time hay DB time |

Các entity cốt lõi: `ExamSession`, `ModelVersion`, `FrameRef`, `Prediction`, `Track`/`TrackObservation`, `BehaviorEvent`, `RiskSnapshot`, `Alert`, `Evidence`, `Review`. Các field cụ thể ở doc 25. Không được dùng một bảng `Detection` duy nhất thay thế chúng.
