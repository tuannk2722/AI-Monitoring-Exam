# ADR-003 — SCB5 và Roboflow dataset candidates

- Status: Accepted as candidates; not accepted for training
- Date: 2026-09-19

**Quyết định**: khảo sát khả năng kết hợp SCB5 với đúng release Roboflow Exam Cheating được tham chiếu. Mỗi nguồn có thể bị từ chối độc lập. Không có training chính thức cho đến khi version/license/provenance/checksum/mapping/group leakage/domain gap được audit xong.

**Hệ quả**: không có dataset byte nào được đóng gói sẵn; trạng thái nguồn mặc định là `pending_audit`.
