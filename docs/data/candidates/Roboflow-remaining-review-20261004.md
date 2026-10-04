# Roboflow — toàn bộ phần việc còn lại sau batch 2

Batch 2 và hai quyết định nhóm đã được owner chốt, không cần trả lời lại. Kết quả hiện hành: **29 ảnh loại, 10 ảnh tạm giữ ngoài subset đầu tiên, 35 ảnh ứng viên gồm 8 ảnh đã duyệt 10 bbox và 27 ảnh chưa duyệt bbox**. Cả 8 ảnh có bbox vẫn cần QA đầy đủ các người/hành vi trước train. Không có dataset accepted hoặc model đã train.

Đã xem 44 ảnh qua bốn sheets để phân loại công việc, không phải đã kiểm đầy đủ từng nhãn: [sheet 1](../../../outputs/roboflow-batch2-reviewed-20261004-v1/remaining-01.png), [sheet 2](../../../outputs/roboflow-batch2-reviewed-20261004-v1/remaining-02.png), [sheet 3](../../../outputs/roboflow-batch2-reviewed-20261004-v1/remaining-03.png), [sheet 4](../../../outputs/roboflow-batch2-reviewed-20261004-v1/remaining-04.png). Source path/hash vẫn ở [remaining manifest](../../../outputs/roboflow-batch2-reviewed-20261004-v1/remaining.json).

## Hai quyết định theo nhóm đã nhận và áp dụng

| Nhóm | Mã ảnh | Đề xuất / lý do | Trạng thái |
|---|---|---|---|
| Nhiễu chấm | P058–P064 (7 ảnh) | Loại theo owner, không tạo ngưỡng tự động cho ảnh khác | Owner: “Loại cả 7 ảnh nhiễu”; đã áp dụng |
| Thiếu phần người / góc khác | P020, P021, P071; P049, P051, P052, P054–P057 (10 ảnh) | Tạm giữ ngoài subset đầu tiên; không kết luận nguồn ảnh không hợp lệ | Owner: “Giữ ngoài subset đầu tiên”; đã áp dụng |

[Record nguyên văn](../../../artifacts/reports/roboflow-20261004/remaining-owner-decisions.json) và [summary/hash mới](../../../artifacts/reports/roboflow-20261004/remaining-reviewed-summary.json). [Queue hiện hành](../../../outputs/roboflow-batch2-reviewed-20261004-v2/queue.json) tách `excluded_owner_noise` khỏi `deferred_initial_subset`. V1/sheets 44 ảnh phía trên giữ làm bằng chứng trước quyết định; v2 còn [27 ảnh](../../../outputs/roboflow-batch2-reviewed-20261004-v2/remaining.json) chờ bbox QA. Đây là nhóm công việc, không phải group_id dùng chia split.

## 27 ảnh còn lại cần công việc kỹ thuật

| Nhóm công việc | Mã ảnh | Cần làm |
|---|---|---|
| Cảnh lớp học/nhóm người, bbox và completeness | P002, P003, P004, P005, P007, P009, P022–P028 (13 ảnh) | Kiểm rõ phone/tay/người, vẽ person boxes; các cảnh nhỏ/mơ hồ giữ ignore, không tự làm negatives. P004 là W02: geometry preview không tự duyệt semantics. |
| Cảnh hai người, phone/association/occlusion | P032, P033, P035, P037–P040 (7 ảnh) | Không lan nhãn qua ảnh tương tự; kiểm tương tác/desk cho từng ảnh. P040 có quyết định ignore phần bị che, không xóa label rồi gọi normal. |
| Phone rõ hoặc cần nhìn ảnh đầy đủ | P041, P042, P043, P047 (4 ảnh) | Kiểm phần người thấy được, phone và completeness; watermark stock không tự loại theo quyết định owner trước đó. |
| Nhãn toàn cảnh/khác bối cảnh/chữ trong ảnh | P048, P069, P070 (3 ảnh) | P048 rà chữ/cảnh và bằng chứng; P069/P070 không tự map No cheating thành normal; xử lý box toàn cảnh P070 theo quyết định cũ. |

Đây là hàng đợi QA, không phải các nhóm video/session hay split. 27 ảnh chưa được vẽ lại/duyệt trong lượt này. Các ảnh có bối cảnh tương tự có thể không độc lập; kết quả similarity cũ chỉ xếp hạng cặp cần kiểm, chưa xác nhận leakage.

## Vì sao chưa train

Duyệt bbox mới giải quyết vị trí người và positive phone_use cho một số mẫu. Chưa có bộ nhãn đầy đủ cho mọi người; chưa chốt cách biểu diễn normal/co-occurrence và trường hợp biên looking_around; chưa có split/group độc lập được review. Không được coi người thiếu nhãn là normal. Không cần chọn kiến trúc vội để vượt các bước này.

Đã áp dụng hai quyết định vào queue version mới; bước tiếp ưu tiên QA các cảnh phù hợp còn lại và completeness trên các ảnh đã có bbox. Chưa có câu hỏi mới bắt buộc owner trả lời ở lượt này. A/B, mapping và split sẽ được đưa ra với kết quả QA cụ thể. P0 DVC push/pull vẫn chưa kiểm chứng.

Lệnh thực tế (output mới khi chạy lại):

```powershell
.venv/Scripts/python.exe -m scripts.audits.roboflow_batch2_review --base outputs/roboflow-batch2-20261004-v1 --output outputs/roboflow-batch2-reviewed-20261004-v2 --group-review artifacts/reports/roboflow-20261004/remaining-owner-decisions.json
```

46 tests PASS, Ruff/compile PASS; regression giữ khác biệt loại/tạm hoãn, không ghi đè trạng thái đã review, không nâng dataset acceptance. Media/source/archive không đổi; outputs mới chỉ gồm JSON/ảnh review, chưa có official training labels.
