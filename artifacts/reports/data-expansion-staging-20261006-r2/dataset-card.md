# Pilot B — staging mở rộng R2

Trạng thái: `prepared_pending_gates`. Owner đã duyệt proposal R2, nhãn/crop theo hash, 11 anchor loại và 11 liên hệ cảnh.

Gói chứa 72 record mới: 61 review_only, 11 excluded; xuất 61 crop đã duyệt. Parent v4 có 112 record và queue 28 review_only được giữ nguyên ở package parent, không nhập lặp vào staging này. Đây chưa phải membership release v5 hợp nhất.

Target theo thứ tự `[phone_use, looking_around]`; unknown giữ giá trị null và mask 0. Trong 61 mẫu giữ: phone 1P/23N/37U, looking 23P/14N/24U; 39 mẫu có ít nhất một target biết, 22 mẫu cả hai unknown, 13 normal đã xác nhận. Không suy nhãn từ lớp nguồn.

Owner xác nhận toàn quyền sử dụng các dataset đang dùng. Bằng chứng ở `release.json#rights_confirmation`; không còn điều kiện chặn về quyền SCB/RF.

Nhóm độc lập/split/release chưa chốt; không có manifest train/val/test. Liên hệ cảnh đã duyệt được pin trong `release.json#scene_constraints`, chưa chứng minh các cảnh còn lại độc lập. Phone positive vẫn tập trung ở RF; ảnh tĩnh không chứng minh thời lượng hoặc ý định.

Ledger: `review-ledger.jsonl`; provenance anchor: `selection.jsonl`; QA/coverage/leakage: `reports/`. Crop excluded không được xuất. Hai crop RF-003/RF-014 dùng refinement đã duyệt. Crop runtime vẫn là bước riêng.

Gói chỉ lưu cục bộ; chưa train, upload hoặc phát hành dataset.
