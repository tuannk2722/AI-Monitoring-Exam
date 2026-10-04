# SCB supplied — ảnh cần owner review

> Checklist mẫu lịch sử. Discuss đã loại, quyền SCB đã xác nhận và B đã chốt. Không mở lại vòng review; preparation theo dataset-research.md.


Gói local: `outputs/scb-audit-20261003-v1/`. Ảnh là annotation gốc, không phải prediction. Không gửi ảnh lên dịch vụ ngoài hay commit binary. Các ảnh `R` được chọn có chủ đích theo class và diện tích box nhỏ nhất/trung vị/lớn nhất trong train hợp lệ; các ảnh `warning` dùng tọa độ gốc bị flag. Không đại diện ngẫu nhiên cho toàn nguồn, không suy ra tỷ lệ sai nhãn từ tập mẫu này.

## Ưu tiên xem

| Mẫu và link ảnh đầy đủ | Quan sát khi audit | Câu hỏi cần owner xác nhận |
|---|---|---|
| [D-R02](../../../outputs/scb-audit-20261003-v1/review/discuss/0002.png), [D-R03](../../../outputs/scb-audit-20261003-v1/review/discuss/0003.png) | Một box bao nhiều người quanh bàn; D-R03 gần như cả crop. | Đồng ý loại `discuss` khỏi mapping trực tiếp person-behavior? Nếu muốn giữ, annotation unit nhóm cần một task khác hoặc re-annotation. |
| [D-warning-2](../../../outputs/scb-audit-20261003-v1/review/discuss/warning-2.png) | Box nhóm vượt đáy ảnh, gồm người hướng dẫn và nhiều học sinh. | Box này nên được đánh dấu invalid để review nguồn, hay tạo quy tắc sửa ở một version riêng? Chưa áp dụng cách nào. |
| [H-P01](../../../outputs/scb-audit-20261003-v1/preview/hrw/0001.png) | Box #3 ID0 có bàn tay thấp gần thân, khác các tay giơ cao; box read lấy cả thân và bàn. | `hand-raising` nguồn có tính cả tay thấp như vậy không? Unit cần full person, upper body hay vùng hành động? |
| [H-P02](../../../outputs/scb-audit-20261003-v1/preview/hrw/0002.png) | Các tư thế nhìn xuống/giữ bút giống nhau nhưng có ID1 và ID2; một số người ngoài box vẫn đang làm việc tại bàn. | Có guideline phân biệt read/write và quy tắc bỏ nhãn không? Không mặc định người không có box là negative. |
| [H-R03](../../../outputs/scb-audit-20261003-v1/review/hrw/0003.png) | Một người đứng giơ tay trước lớp, khác bối cảnh học sinh ngồi. | Nhãn hand-raising có giới hạn actor không? Có cần loại trường hợp này khỏi scope phòng thi? |
| [H-R07](../../../outputs/scb-audit-20261003-v1/review/hrw/0007.png), [H-R08](../../../outputs/scb-audit-20261003-v1/review/hrw/0008.png) | Nhiều box nhỏ/che khuất trong toàn cảnh; cần mở ảnh gốc để xem tay/bút. | Trường hợp không nhìn đủ bằng chứng được giữ, ignore hay cần review thêm? Chưa đặt ngưỡng kích thước. |
| [H-warning-1](../../../outputs/scb-audit-20261003-v1/review/hrw/warning-1.png), [H-warning-2](../../../outputs/scb-audit-20261003-v1/review/hrw/warning-2.png) | Bao gồm bbox kích thước bằng 0 và box vượt biên lớn, không chỉ sai số float. | Có annotation gốc để phục hồi không? Nếu không, owner chọn loại/relabel ở version mới sau review. |

## Head và duplicate

Các link/câu hỏi bổ sung được ghi ở phần kết quả cuối của [báo cáo](SCB5-supplied-20261003-audit.md). Không coi TurnHead tương đương looking_around trước khi xác nhận bằng chứng hướng đầu, ngữ cảnh và temporal requirement.

## Bằng chứng chọn mẫu

Các file `artifacts/reports/scb-20261003/*-review-selection.json` và `*-warning-selection.json` ghi source image/label, class focus và lý do chọn. `preview/hrw/source-provenance.json` truy vết hai mẫu H-P. Mỗi thư mục review có `manifest.json`, report của subset và `contact-sheet.png`. Report toàn ZIP nằm ngoài subset tại `outputs/scb-audit-20261003-v1/*-audit.json`; không dùng report subset thay report toàn bộ.

Owner có thể ghi đáp án theo ID mẫu; chưa có quyết định mapping/repair nào được thực thi. License và metadata nhóm do owner cung cấp sau, chưa dùng lời xác nhận miệng để đóng gate.


## Head và cặp trùng đã kiểm tra

| Ảnh | Quan sát | Câu hỏi |
|---|---|---|
| [T-P01](../../../outputs/scb-audit-20261003-v1/preview/head/0001.png), [T-P02](../../../outputs/scb-audit-20261003-v1/preview/head/0002.png) | Cùng bố cục lớp; có người vừa giơ tay vừa xoay đầu, BowHead nhìn từ phía sau. | `looking_around` của dự án có bao gồm quay đầu trong tương tác lớp như vậy không? Có cần ngữ cảnh/thời lượng mà ảnh tĩnh thiếu không? |
| [T-R03](../../../outputs/scb-audit-20261003-v1/review/head/0003.png) | Người cúi đầu đang viết trong box BowHead. | Đồng ý không map BowHead thành phone_use/normal chỉ từ tư thế? Cần nhãn đồng thời thế nào? |
| [T-R04](../../../outputs/scb-audit-20261003-v1/review/head/0004.png) | Box TurnHead nhỏ ở phía xa, lớp nhìn từ sau. | Có đủ độ rõ để xác nhận hướng đầu không? Cần guideline ignore và review ở độ phân giải gốc. |
| [T-warning-1](../../../outputs/scb-audit-20261003-v1/review/head/warning-1.png), [T-warning-2](../../../outputs/scb-audit-20261003-v1/review/head/warning-2.png) | Cảnh báo đầu có mức 2,22e-16; cảnh báo sau vượt trái rõ hơn (0,01389). | Tách quy tắc sai số biểu diễn và lỗi annotation thực thế nào? Chưa áp epsilon hoặc clip. |
| [Duplicate HRW/val](../../../outputs/scb-audit-20261003-v1/review/duplicate/hrw/0001.png), [Duplicate Head/train](../../../outputs/scb-audit-20261003-v1/review/duplicate/head/0001.png) | Cùng bytes ảnh, 3 nhãn HRW và 4 nhãn Head ở các người khác nhau. | Cần gộp annotations theo unit sau review và tạo split mới theo group? Giữ split hiện tại sẽ rò rỉ nếu concat. Chưa thực hiện dedup/merge/split. |

Contact sheets: [Discuss](../../../outputs/scb-audit-20261003-v1/review/discuss/contact-sheet.png), [HRW](../../../outputs/scb-audit-20261003-v1/review/hrw/contact-sheet.png), [Head](../../../outputs/scb-audit-20261003-v1/review/head/contact-sheet.png). Mở từng PNG đầy đủ qua selection JSON nếu thumbnail không đủ rõ.
