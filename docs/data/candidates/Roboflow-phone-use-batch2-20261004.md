# Roboflow — kết quả pilot đã duyệt và batch 2

## Đã hoàn tất

Commit `4af4dac` lưu pilot, công cụ similarity và bốn câu trả lời owner. [Record nguyên văn](../../../artifacts/reports/roboflow-20261004/pilot-owner-review.json): P019/P029 duyệt 3 bbox; P029 là hai người truyền phone cho nhau, không phải phone trên bàn. P053/P065 loại vì nhiễu.

Đã áp dụng record vào [queue version mới](../../../outputs/roboflow-batch2-20261004-v1/queue.json): 74 ảnh, 22 loại, 52 còn QA. Trong 52 ảnh, 2 ảnh có bbox đã duyệt nhưng completeness còn mở. [Ba bbox đã duyệt](../../../outputs/roboflow-batch2-20261004-v1/approved-boxes.json) giữ tọa độ và đính chính evidence P029. Không thay bản raw, không tự thêm normal/negative hoặc làm official build.

## Batch 2 đã chuẩn bị

**Trạng thái mới hơn sau hai quyết định nhóm:** 29 ảnh loại, 10 ngoài subset đầu tiên, 35 ảnh ứng viên (8 ảnh/10 bbox duyệt + 27 chưa duyệt bbox). Xem [bảng tổng hợp hiện hành](Roboflow-remaining-review-20261004.md). Số 22/44 bên dưới là mốc trước khi owner chốt hai nhóm.

**Cập nhật sau owner review:** sáu mục dưới đây đã trả lời và được áp dụng. “Không” ở P006 trả lời câu hỏi có phần người nhìn thấy bị bỏ sót không; được ghi là không bỏ sót, bbox phù hợp. Năm mục còn lại “Okay”. [Record nguyên văn và đúng tọa độ được duyệt](../../../artifacts/reports/roboflow-20261004/batch2-owner-review.json).

Kết quả hiện hành: **10 bbox duyệt trên 8 ảnh**, 22 ảnh loại, 44 ảnh chưa được duyệt bbox. Tổng 52 ảnh vẫn cần QA completeness/hành vi còn lại, không phải đã training-ready. Bảng và số liệu trước bên dưới giữ làm lịch sử; không cần owner trả lời lại batch 2. [Queue mới](../../../outputs/roboflow-batch2-reviewed-20261004-v1/queue.json), [bbox đã duyệt hợp nhất](../../../outputs/roboflow-batch2-reviewed-20261004-v1/approved-boxes.json), [summary/hash](../../../artifacts/reports/roboflow-20261004/batch2-reviewed-summary.json).

Đã mở riêng sáu ảnh train, vẽ 7 bbox mới, kiểm geometry và xem toàn bộ overlay. Nhãn mới là đề xuất theo guideline đã chốt, chưa owner-approved. Không phải đã relabel xong 52 ảnh. Chọn các ảnh phone rõ/camera classroom để kiểm cách vẽ; không đại diện phân bố hay tình huống độc lập.

| Ảnh | Đề xuất và điểm cần review | Owner trả lời |
|---|---|---|
| [P006](../../../outputs/roboflow-batch2-20261004-v1/P006.png) | Hai người phía trái cầm phone. Kiểm bbox nhỏ/phần thân bị ghế che; có phần người nhìn thấy nào bị bỏ sót không? | Không |
| [P008](../../../outputs/roboflow-batch2-20261004-v1/P008.png) | Người trái cầm phone hai tay; bbox tới cánh tay. Người phải chưa được gán normal. | Okay |
| [P030](../../../outputs/roboflow-batch2-20261004-v1/P030.png) | Người phải chạm phone trên bàn tương ứng; box gồm chân nhìn thấy. | Okay |
| [P031](../../../outputs/roboflow-batch2-20261004-v1/P031.png) | Người trước đặt tay lên phone trên bàn; box tới phần tay nhìn thấy. | Okay |
| [P034](../../../outputs/roboflow-batch2-20261004-v1/P034.png) | Phone trên bàn người trước; xác nhận liên kết và bbox. Phone ngoài person box được phép vì unit là người. | Okay |
| [P036](../../../outputs/roboflow-batch2-20261004-v1/P036.png) | Phone trên bàn người trước. Không tự thêm looking_around chỉ từ hướng đầu. | Okay |

Bạn có thể trả lời chung nếu toàn bộ phù hợp và chỉ ghi mã ảnh cần sửa. Đây là review annotation mới, không yêu cầu chọn lại unit/phone_use đã chốt. Người không có box trong các preview **chưa phải negative**; cần QA mọi người/hành vi trước training. Hai ảnh nhiễu đã bị loại không xuất hiện trong batch này; các ảnh nhiễu khác vẫn cần QA, chưa suy ngưỡng tự động.

## Kiểm tra và tái tạo

```powershell
.venv/Scripts/python.exe -m scripts.audits.roboflow_continue --base outputs/roboflow-pilot-20261004-v3 --output outputs/roboflow-batch2-20261004-v1
```

Đã chạy lệnh trên; chạy lại dùng output mới. Kiểm checksum toàn bộ base artifacts theo pilot-summary trước khi áp dụng decisions; pin plan/decision/code và checksum output. Không decode/extract lại ZIP hoặc đổi báo cáo audit cũ. [Plan](../../../artifacts/reports/roboflow-20261004/batch2-plan.json), [summary](../../../artifacts/reports/roboflow-20261004/batch2-summary.json). 42 tests PASS; Ruff/compile/repository checker PASS. Regression ngăn acceptance ngầm, sửa queue nguồn, áp decision vào test, action lạ/trùng và hồi sinh ảnh đã loại.

Batch mới chưa được dùng train, chưa accepted. P1 còn completeness/looking_around/co-occurrence, kiểm leakage/group và chốt A/B/split. Chưa chạy thêm similarity ngoài phạm vi pilot trước; P0 DVC push/pull vẫn chưa kiểm chứng.

Lệnh đã chạy để áp dụng câu trả lời (output phải mới khi chạy lại):

```powershell
.venv/Scripts/python.exe -m scripts.audits.roboflow_batch2_review --base outputs/roboflow-batch2-20261004-v1 --output outputs/roboflow-batch2-reviewed-20261004-v1
```

44 tests PASS, Ruff/compile/checker PASS. Kiểm mới từ chối sửa source path/hash/boxes, thiếu/trùng câu trả lời hoặc biến bbox approval thành acceptance. Đã sửa đọc UTF-8 rõ ràng trên Windows sau lần chạy đầu dừng trước tạo output. Không sửa raw hoặc báo cáo lịch sử.
