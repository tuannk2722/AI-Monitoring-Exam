# Roboflow v1 — pilot chuẩn bị relabel

Phạm vi: train của đúng ZIP đã audit; không build dataset chính thức, không train.
Mốc trước task: `806e08c` (dataset audit), working tree sạch.

## Kết quả thực hiện

- 74 ảnh train trong queue: 66 ảnh có Phone use nguồn + 8 mẫu bổ sung từ checklist. Sao chép đúng 74 cặp; không giải nén lại toàn ZIP.
- Đã xem 74 ảnh qua 7 contact sheets để sàng lọc UI/domain; không coi đó là annotation QA đầy đủ. Đã mở riêng W01/R12/R09/R03 để vẽ bbox.
- 20 ảnh được giữ ngoài ứng viên train: 4 quyết định loại ảnh có sẵn và 16 ảnh bổ sung theo policy UI/phụ đề. 54 ảnh còn chờ QA, không phải 54 ảnh đã accepted. Danh sách quyết định trong [pilot plan](../../../artifacts/reports/roboflow-20261004/pilot-plan.json); queue giữ cả ảnh loại để truy vết, không phải folder training.
- Vẽ thủ công 5 bbox đề xuất trên 4 ảnh, theo quyết định owner: chỉ bao phần người nhìn thấy, không suy cơ thể bị che. Bbox hình chữ nhật có thể chứa bàn/vùng bị che ở giữa các phần nhìn thấy. Không copy source class thành canonical mapping toàn nguồn.
- [Summary và checksum](../../../artifacts/reports/roboflow-20261004/pilot-summary.json), [queue](../../../outputs/roboflow-pilot-20261004-v3/queue.json), [tọa độ đề xuất](../../../outputs/roboflow-pilot-20261004-v3/proposals.json).

## Bốn ảnh cần owner review

**Đã nhận đủ câu trả lời ngày 2026-10-04.** [Decision record](../../../artifacts/reports/roboflow-20261004/pilot-owner-review.json) giữ nguyên lời owner. Bảng dưới giữ cả nhận định ban đầu để truy vết: P029 ban đầu bị diễn giải sai là phone trên bàn; owner xác nhận **hai người truyền phone cho nhau, phone_use cho cả hai**, bbox phù hợp. Nhận định cũ không còn là bằng chứng về phone trên bàn.

P019/P029: duyệt 3 bbox đề xuất, chưa duyệt completeness cả ảnh. P053/P065: loại ảnh vì nhiễu, kể cả bbox P053 hợp lý. Tổng queue sau quyết định: 22 ảnh loại, 52 ảnh còn QA; không tự áp dụng quyết định hai ảnh nhiễu thành threshold hay loại mọi ảnh khác. Pilot plan/summary cũ giữ bất biến làm lịch sử; record mới là quyết định hiện hành.

Bbox xanh là đề xuất của Codex, không phải prediction. Chưa xuất nhãn YOLO canonical; các người chưa review không được hiểu là negative. Chủ repository điền cột cuối trước khi áp dụng cách vẽ này cho batch tiếp.

| Mẫu / ảnh mới | Thay đổi đề xuất | Câu hỏi cụ thể | Owner trả lời |
|---|---|---|---|
| [P019 / W01](../../../outputs/roboflow-pilot-20261004-v3/proposals/P019.png) | Box người phụ nữ phía trước, phone ở tay thấp; vẽ thủ công thay vì sửa overflow tự động | Box đã bao đủ phần người nhìn thấy chưa? Các người còn lại sẽ review riêng; ảnh vẫn chưa pass completeness. | Box đã bao đủ phần người rồi |
| [P029 / R12](../../../outputs/roboflow-pilot-20261004-v3/proposals/P029.png) | Hai person boxes; người trái có phone trên bàn, người phải có phone ở tay dưới bàn | Xác nhận phone trên bàn gắn với người trái và phone giữa hai bàn gắn với người phải? Bbox gồm chân nhìn thấy đã phù hợp chưa? | Người trái không có phone nào trên bàn cả, ảnh này đang là 2 người đang truyền phone cho nhau thì phone_use gắn cho cả hai người. Bbox đã phù hợp rồi |
| [P053 / R09](../../../outputs/roboflow-pilot-20261004-v3/proposals/P053.png) | Một person box bao tay cầm phone, bỏ cách trộn box phone/tay với người | Bbox hợp lý chưa; ảnh nhiễu này giữ để QA tiếp hay loại? | Bbox đã hợp lý, ảnh nhiễu này loại đi |
| [P065 / R03](../../../outputs/roboflow-pilot-20261004-v3/proposals/P065.png) | Person box cho phone_use đã được owner xác nhận | Bbox có bỏ sót phần người không; ảnh nhiễu này giữ để QA tiếp hay loại? | Loại ảnh nhiễu |

## Kiểm gần trùng và split

Đã decode/fingerprint toàn 3.407 ảnh RF v1; với từng ảnh trong queue train, tìm một ảnh khác gần nhất ở mỗi split bằng 64 so sánh độ sáng ngang trên ảnh grayscale 9×8. Đây là xếp hạng để tìm ảnh cần kiểm, **không có threshold tự kết luận duplicate**, không suy group_id.

74 truy vấn có lần lượt 15/13/9 trường hợp khoảng cách 0 tới train/valid/test. Đây là số truy vấn, không phải số cặp/nhóm trùng độc lập hoặc leakage đã xác nhận. Exact SHA audit trước vẫn không có ảnh trùng bytes.

Đã xem cặp train [1](../../../outputs/roboflow-pilot-20261004-v3/contact-sheets/pair-01.png) và [3](../../../outputs/roboflow-pilot-20261004-v3/contact-sheets/pair-03.png): UI/cảnh giống nhưng tư thế người khác nhau dù khoảng cách hash bằng 0. Chưa mở ảnh valid/test để review policy; các kết quả cross-split là cảnh báo cần audit leakage riêng. Chưa so perceptual với SCB, chưa rà mọi cặp toàn nguồn, thuật toán có thể bỏ sót hoặc nhầm ảnh gần trùng. [Bảng khoảng cách](../../../outputs/roboflow-pilot-20261004-v3/similarity.json).

## A/B và bước kế tiếp

Chưa đủ bằng chứng chốt A/B. Cả A (detect hành vi trên person bbox) và B (person crop classification) đều cần bbox người, labels đầy đủ và xử lý đồng xuất hiện. Pilot này có 5 positive boxes, chưa có negatives được review, chưa đo accuracy/công sức annotation đại diện. Không dùng nó để kết luận chất lượng model.

Owner review bốn ảnh trên; tiếp đó hoàn thiện person annotations/ignore/completeness trên batch train, pilot quy tắc looking_around và co-occurrence; rà cross-split similarity để thiết kế split có bằng chứng. Metadata video/session còn thiếu, không khôi phục từ tên file. P1 acceptance, build/train chính thức và P0 DVC push/pull vẫn chưa đóng.

## Tái tạo và kiểm tra

```powershell
.venv/Scripts/python.exe scripts/audits/roboflow_pilot.py --archive "C:/Users/OS/Downloads/Exam cheating.v1i.yolov8.zip" --output outputs/roboflow-pilot-20261004-v3
```

Đó là lệnh đã chạy; chạy lại cần tên output mới. Script pin ZIP/hash quyết định/plan/code, lưu hash ảnh và label. V1 là lượt chuẩn bị; v2 là preview đầu; v3 là kết quả cuối sau chỉnh bbox R09 bao tay tới cạnh dưới. Media local ignored. 40 unittest PASS, Ruff/compile/repo checker PASS; regression kiểm fingerprint collision, path/self/tie và proposal bbox không hợp lệ. Fixture chỉ kiểm phần mềm. Raw/config/mapping/split không đổi.
