# Dataset Audit & Spec — trạng thái và phương án sử dụng

Ngày: 2026-10-04. Đây là đầu mối hiện hành sau consolidation; không mở thêm vòng review ảnh nhỏ lẻ. Kiến trúc và semantics theo ADR-011/012. **Audit & Spec đã được tổng hợp; dataset training chưa accepted, P1 preparation gates còn mở.** Không có benchmark/model kết quả để báo cáo.

## Vai trò hai nguồn trong Formulation B

| Nguồn/phần | Vai trò trong preparation | Không được làm |
|---|---|---|
| Roboflow v1 | Nguồn bổ sung phone_use; giữ 28 person/crop đã duyệt trên 21 ảnh và các quyết định loại/hold | Dùng nguyên 3.407 ảnh như dataset canonical; tự map No cheating thành normal |
| SCB5 Head / TurnHead | Nguồn ứng viên looking_around, relabel theo hướng nhìn/ngữ cảnh đã chốt | Map toàn bộ TurnHead trực tiếp hoặc suy thời lượng từ ảnh |
| SCB5 HRW / read, write | Nguồn ứng viên normal và cảnh đang làm bài; phải review từng target trên crop được chọn | Coi read/write tự động là normal |
| SCB5 BowHead, hand-raising | Ngoài mapping trực tiếp của release đầu; có thể dùng ảnh phù hợp sau review hai target | Suy cúi đầu/tay khuất là gian lận hoặc negative |
| SCB5 Discuss | Loại khỏi baseline theo owner | Dùng group box như person box |

SCB đã audit toàn bộ ba ZIP (10.138 ảnh, 8.116 SHA unique), không cần audit lại hay lặp toàn bộ chuỗi review Roboflow. Phần chưa làm là chọn một tập hữu hạn và relabel theo B, dùng **cùng manifest/quy trình preparation**, không tạo launcher từng batch. Roboflow đã làm sâu hơn vì phone_use thiếu trong taxonomy nguồn SCB; đó không có nghĩa SCB bị loại bỏ.

## Đã có, đã chốt

- B: YOLO person → crop có ngữ cảnh → classifier multi-label. Chưa chọn model/weights/loss.
- Normal là người đang làm bài với absence hai target đã review; unknown không phải negative.
- Đồng xuất hiện giữ hai nhãn; crop không làm thay đổi bbox visible-person.
- Roboflow: 74 ảnh trong queue = 29 excluded + 11 deferred + 13 held + 21 ảnh có người được duyệt. 28 person/crop: 24 phone positives, 5 looking positives, 1 co-occurrence; 27 người còn một target unknown. Không có normal/negative được duyệt trong 28 record này.
- SCB: Discuss loại; quyền sử dụng đã được owner xác nhận, không hỏi lại. Group/session từng mẫu vẫn thiếu. 961 nhóm exact duplicate có thành viên train/val khi xét chung archive; không giữ split cũ khi hợp nguồn.
- Roboflow nguồn có 3.407 cặp, 34 file geometry warning/35 dòng khoảng 0.005 pixel; full exact checks không thấy trùng nội bộ/cross-SCB. Similarity triage chỉ là ứng viên, chưa chứng minh độc lập split.

## Hồ sơ duy nhất cần đọc

- SCB: [card](candidates/SCB5-supplied-20261003.md), [audit lịch sử](candidates/SCB5-supplied-20261003-audit.md), [review](candidates/SCB5-supplied-20261003-review.md).
- Roboflow: [card](candidates/Roboflow-phone-use-20261004.md), [audit lịch sử](candidates/Roboflow-phone-use-20261004-audit.md), [toàn bộ quyết định](candidates/Roboflow-phone-use-20261004-review.md).
- Evidence: SCB audit.json; Roboflow audit.json và review.json. Historical records giữ nguyên text/hash, không phải trạng thái hiện hành; current_person_crops/image_queue trong review.json là snapshot cuối.
- Outputs media giữ nguyên local/ignored. Scripts theo phiên đã nghỉ; Git và snapshots trong review.json giữ provenance, không hứa replay các launcher đã bỏ.

## Các việc còn lại để phát hành dataset B

1. Đóng danh sách mẫu release hữu hạn từ hai nguồn theo vai trò trên, dựa coverage/nhóm thực tế; chưa bịa số lượng hoặc ngưỡng đủ dữ liệu.
2. Chuẩn bị crop và target labels cho tập đã chọn; bổ sung negative/normal được review. Crop classifier chỉ cần target và bằng chứng phù hợp, không bắt annotate mọi người ngoài crop. Nếu huấn luyện detector riêng mới cần hợp đồng completeness detector.
3. Chọn cơ chế lưu/huấn luyện với unknown trước exporter: loại mẫu thiếu nhãn hoặc masked supervision là quyết định còn mở, không tự mã hóa unknown thành 0.
4. Xác định crop inference không phụ thuộc annotation phone có sẵn; kiểm duplicate/group split và freeze test. Group không biết để trống ở audit, không tạo split độc lập giả.
5. Triển khai builder classifier B, chạy validation/checksum/rebuild, owner ký release rồi DVC push/pull từ checkout sạch.

Không train, build chính thức hoặc tự accepted trong đợt cleanup này. P0 DVC round-trip chưa kiểm chứng; không gọi P0/P1/P2 hoàn tất.
