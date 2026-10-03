# 12 — P5/P6 Tracking, Events và Risk

Entry gate: model đã được select và đang emit bản ghi `Prediction` trên fixed recorded-video fixtures.

## P5 Tracking

ByteTrack là candidate, không phải sự thật đã được đo. Cần benchmark: ID switch, track fragmentation/loss, stability và occlusion recovery. Track ID chỉ có phạm vi local trong một exam session; không được lưu dài hạn như danh tính. Seat mapping là tùy chọn/TBD.

## P6 Event state flow (luồng trạng thái sự kiện)

`prediction → aggregate candidate → lọc qua temporal rule → behavior event đã xác nhận → alert/review tùy chọn`.

Một frame đơn lẻ không tự động trở thành event. Các rule có version và định nghĩa: số observation tối thiểu, thời lượng, khoảng gap cho phép và cách aggregation confidence. Giá trị số giữ `TBD_BY_EVENT_DATA` cho đến khi có tập validation event được gán nhãn.

## Risk (Mức độ rủi ro)

Risk là tín hiệu demo minh bạch, được aggregate từ loại/tần suất/thời lượng/lịch sử event có version. Risk không phải là model confidence hay xác suất vi phạm. Engine ban đầu là rule-based, có giới hạn trên và decays theo thời gian. Công thức/mức độ/điều kiện reset/hành vi audit cần được cập nhật vào ADR-009 trước khi triển khai.

## Evidence/Review (Bằng chứng/Xem xét)

Evidence tham chiếu đến frame/time/checksum nguồn chính xác, phiên bản event/rule/model và trạng thái retention. Các hành động review nên trung lập: `needs_review` (cần xem xét), `acknowledged` (đã ghi nhận), `dismissed_false_positive` (bác bỏ vì false positive), `confirmed_behavior` (xác nhận hành vi), `note_added` (thêm ghi chú). Phạm vi học thuật phải tránh đưa ra kết luận pháp lý/kỷ luật.
