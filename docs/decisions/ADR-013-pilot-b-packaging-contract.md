# ADR-013 — Phạm vi và gates đóng gói pilot B

- Status: Accepted **chỉ cho các lựa chọn owner xác nhận dưới đây**; không phê duyệt dataset cụ thể, model, loss, split assignment hoặc crop runtime.
- Date: 2026-10-04. Owner/người chốt: chủ repository (solo). Hỗ trợ: Codex.
- Extends: ADR-011/012; làm rõ gate đóng gói trong P2.
- Evidence: owner trả lời hai bộ câu hỏi trong task thiết kế pilot B ngày 2026-10-04. Nội dung lựa chọn được ghi dưới đây và ở `.codex/TASK.md`; không suy approval từ im lặng.

## Quyết định

1. Lượt này **chỉ thiết kế hợp đồng** và danh sách triển khai; chọn mẫu/cắt crop/build dataset thực hiện ở task sau. Hợp đồng duy nhất: [pilot B v1](../data/pilot-b-release-contract-v1.md).
2. Giữ đúng 28 person/crop Roboflow đã duyệt; lưu positive/negative/unknown và **cho phép masked supervision**: chỉ target đã biết tham gia loss/metric, unknown không biến thành negative. Chưa chọn model/head/loss/threshold.
3. Công việc SCB được giới hạn ở **84 person candidates**: 28 TurnHead, 28 read, 28 write; review một lần, ghi loại/unknown và không tự bổ sung vô hạn. Đây là budget công việc, không phải ngưỡng dataset đủ tốt hoặc cam kết 84 crop sẽ được dùng.
4. Pilot đóng gói **crop đã review**, giữ crop Roboflow đã duyệt và review/vẽ crop SCB theo cùng guideline, lưu tọa độ tái tạo được. Crop tự động từ YOLO ở inference là gate riêng chưa đạt; phải owner chốt và QA trước baseline B end-to-end. Không tự đặt padding mặc định.
5. Chỉ freeze train/val/test khi leakage groups đủ bằng chứng và được owner review. Thiếu group giữ `split=null`, `usage=review_only` và **chặn release training**. Không suy session từ filename hoặc coi mỗi ảnh là nhóm độc lập.

## Tác động và giới hạn

- P2 tách package crop được review khỏi trạng thái sẵn sàng cho baseline B end-to-end; crop runtime vẫn còn TBD có owner.
- Hợp đồng mô tả membership rule, schema thiết kế, eligibility, crop/split, acceptance và backlog hữu hạn. Task triển khai phải freeze manifest/schema/config/report và owner review trước release.
- Hai nguồn vẫn candidate; Roboflow review cũ giữ `training_eligible=false`; không sửa bằng chứng lịch sử. Split ratio/seed/assignment chưa được phê duyệt bằng ADR này.
- Không thêm output classifier `normal` độc quyền; không thay semantics của ADR-011/012, không build/train/upload và không đóng P0/P1/P2 bằng tài liệu thiết kế.
