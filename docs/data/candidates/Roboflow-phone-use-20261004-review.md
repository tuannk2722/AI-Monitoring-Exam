# Roboflow v1 — ảnh và câu hỏi owner review

Ngày: 2026-10-04. Ảnh là annotation nguồn, không phải prediction. Đã xem **16 ảnh train hợp lệ + 2 ảnh train cảnh báo**; R01–R06 qua contact sheets, R07–R16 và W01–W02 ở ảnh overlay đầy đủ. Không xem test để chọn policy/tune. Đây là mẫu có chủ đích, không ước lượng tỷ lệ sai nhãn toàn bộ.

Chọn min/median/max diện tích bbox theo mỗi lớp, rồi thêm mẫu Phone use trải theo thứ tự filename. Filename chỉ là cách chọn mẫu, không phải group/video ID. [Selection](../../../artifacts/reports/roboflow-20261004/review-selection.json), [warning selection](../../../artifacts/reports/roboflow-20261004/warning-selection.json), [quan sát đã ghi](../../../artifacts/reports/roboflow-20261004/visual-review.json).

**Ưu tiên R07, R09, R12, W01:** nhãn Phone use đang trộn object/person unit; một ảnh có phone nhưng mang ID0. Owner đã trả lời đủ 18 mục. Câu trả lời gốc giữ nguyên dưới đây; kết quả xử lý cuối trang. Raw/mapping chưa đổi; W02 có preview riêng.

| Mẫu | Quan sát | Câu hỏi cần chốt | Câu trả lời của tôi |
|---|---|---|---|
| [R01](../../../outputs/roboflow-v1-20261004-complete-v2/review/0001.png) | Box nhỏ nhất chỉ 1x4 pixel; nhiều box ID0 quanh mặt/đầu; có người không có box. | Box quá nhỏ có bằng chứng để giữ hay cần ignore/relabel? | ignore |
| [R02](../../../outputs/roboflow-v1-20261004-complete-v2/review/0002.png) | ID0 trên nhiều tư thế, gồm người nhìn xuống và nhìn ngang. | Định nghĩa looking_around có khớp những tư thế này không? | Không hoàn toàn là looking_around, dựa vào mức độ và hướng quay nữa |
| [R03](../../../outputs/roboflow-v1-20261004-complete-v2/review/0003.png) | ID0 bao gần toàn ảnh cận cảnh; ảnh có nhiễu chấm; người cầm vật giống điện thoại. | Xác nhận hành vi nguồn và nhãn còn thiếu; không map tự động. | Hành vi là sử dụng điện thoại và nhãn là phone_use |
| [R04](../../../outputs/roboflow-v1-20261004-complete-v2/review/0004.png) | Cảnh thi nhiều người; ID1 nhỏ quanh đầu, các ID0 có kích thước/unit khác. | ID1 có thể dùng làm negative đã review không? Chưa có đủ bằng chứng. | Không |
| [R05](../../../outputs/roboflow-v1-20261004-complete-v2/review/0005.png) | ID1 trên nhiều người, gồm người gục trên bàn; có watermark Alamy. | Phạm vi normal và nguồn/quyền asset này cần đối chiếu thế nào? | Phạm vi normal là không phải 2 nhãn looking_around và phone_use, sau này sẽ phát triển thêm; chấp nhận ảnh có watermark stock |
| [R06](../../../outputs/roboflow-v1-20261004-complete-v2/review/0006.png) | ID1 có box phủ toàn ảnh và box phủ người phía trước. | Box toàn ảnh gồm nhiều người có phù hợp person unit không? | Xóa bỏ |
| [R07](../../../outputs/roboflow-v1-20261004-complete-v2/review/0007.png) | ID2 nhỏ nhất 15x7 pixel tại vùng bàn/tay, không phải cả người. | Không nhìn đủ rõ để xác nhận phone; giữ, ignore hay annotate lại? | Loại bỏ (ignore) box này; không giữ box mờ dưới ngưỡng nhận diện và không đủ bằng chứng thị giác. |
| [R08](../../../outputs/roboflow-v1-20261004-complete-v2/review/0008.png) | ID2 bao thân trên của hai người đang cầm vật giống điện thoại. | Chốt annotation unit người hay điện thoại? | Chốt annotation unit là person (người có hành vi sử dụng điện thoại) để phục vụ bài toán tracking và phân loại hành vi. |
| [R09](../../../outputs/roboflow-v1-20261004-complete-v2/review/0009.png) | Cùng ID2: một box bao người/gần cả ảnh, box khác bao tay và điện thoại; ảnh có nhiễu chấm. | Hai box cùng nhãn nhưng khác unit: cần relabel thống nhất trước dùng. | Relabel lại: thống nhất đưa về person unit (chuẩn hóa box bao người, xóa/loại bỏ box chỉ bao tay và điện thoại). |
| [R10](../../../outputs/roboflow-v1-20261004-complete-v2/review/0010.png) | Người cầm điện thoại trong cảnh nói chuyện trước camera; ID2 bao người. | Có giữ ảnh ngoài domain phòng thi trong tập bổ sung không? | Loại ảnh này ra |
| [R11](../../../outputs/roboflow-v1-20261004-complete-v2/review/0011.png) | Ảnh chụp màn hình web/video với UI; ID2 bao người cúi đầu, phone khó xác minh. | Cần bằng chứng phone rõ hơn; không suy từ tư thế cúi đầu. | Cần bằng chứng rõ ràng |
| [R12](../../../outputs/roboflow-v1-20261004-complete-v2/review/0012.png) | ID2 bao tay/điện thoại dưới bàn; có vật giống phone trên bàn khác không có box. | Định nghĩa tương tác/cầm khác phone chỉ nằm trên bàn; kiểm completeness theo guideline. | Để điện thoại trên bàn và cầm điện thoại thì đều tính là vi phạm |
| [R13](../../../outputs/roboflow-v1-20261004-complete-v2/review/0013.png) | ID2 nhỏ quanh vùng tay phía sau; ID0 quanh đầu/người phía trước. | Có đủ bằng chứng thị giác cho từng box, có cần ignore khi che khuất? | ignore khi bị che khuất |
| [R14](../../../outputs/roboflow-v1-20261004-complete-v2/review/0014.png) | Góc nhìn từ trên xuống; ID2 bao tay/thiết bị cạnh laptop. | Unit và góc camera có phù hợp subset person-behavior không? | Không |
| [R15](../../../outputs/roboflow-v1-20261004-complete-v2/review/0015.png) | ID2 bao thân người nhìn/cầm điện thoại; ảnh có nhiễu chấm. | Cần xác minh nguồn ảnh/nhiễu; không suy xuất xứ augmentation từ ảnh. | Cần lưu ý chất lượng ảnh |
| [R16](../../../outputs/roboflow-v1-20261004-complete-v2/review/0016.png) | ID2 bao người cầm phone; có phụ đề trong ảnh. | Giữ hay loại UI/phụ đề/domain khác khi thiết kế subset? | Loại bỏ những ảnh có dính chữ phụ đề / giao diện web khỏi tập train |
| [W01](../../../outputs/roboflow-v1-20261004-complete-v2/review/warning-1.png) | BBox đỏ vượt biên rất nhỏ; người phía trước cầm phone nhưng được ID0. | Tách sửa geometry khỏi kiểm nhãn sai/thiếu phone; không sửa tự động. | Không được dùng công cụ tự động để sửa lỗi tọa độ pixel rồi coi là ảnh đã đạt; bức ảnh này cần được dán lại nhãn bằng tay cho đúng. |
| [W02](../../../outputs/roboflow-v1-20261004-complete-v2/review/warning-2.png) | BBox đỏ chạm cạnh phải, mức vượt chỉ khoảng 0.005 pixel. | Owner quyết định rule xử lý subpixel ở version mới; validator hiện giữ nguyên. | đồng ý cho phép viết 1 dòng code đơn giản để tự động ép tọa độ về mép ảnh |

Contact sheets: [ID 0](../../../outputs/roboflow-v1-20261004-complete-v2/review/class-0-contact.png), [ID 1](../../../outputs/roboflow-v1-20261004-complete-v2/review/class-1-contact.png), [ID 2](../../../outputs/roboflow-v1-20261004-complete-v2/review/class-2-contact.png). Mở ảnh riêng khi thumbnail quá nhỏ.

Các 24 overlay cũ trong outputs/roboflow-v1-20261004/review/ được giữ làm lịch sử; báo cáo này chỉ khẳng định phạm vi 18 ảnh vừa nêu. Bbox cảnh báo được vẽ theo tọa độ nguồn; canvas không thể hiển thị phần ngoài ảnh, không phải dữ liệu đã được sửa.
## Kết quả chốt owner review — 2026-10-04

Đã ghi đủ 18 câu trả lời vào [manifest quyết định](../../../artifacts/reports/roboflow-20261004/owner-decisions.json), kèm source path và trạng thái công việc. R12 được owner làm rõ trong hội thoại: **“Mở rộng phone_use: cầm/tương tác hoặc điện thoại trên bàn gắn được với người”**. [ADR-011](../../decisions/ADR-011-person-unit-phone-definition.md) và label spec draft v0.2 đã đồng bộ.

- Chốt policy person unit; normal là absence đã review của hai target; loại UI/phụ đề khỏi train; không map thẳng ID0/1/2 theo tên.
- R01/R07/R13 ignore phần thiếu bằng chứng; R03 phone_use; R04 không làm reviewed negative; R06 bỏ box toàn cảnh; R09 vẽ lại person; R10/R14 loại khỏi subset đề xuất; R11 cần bằng chứng và thuộc policy loại UI. R15 còn QA, R02 còn guideline hướng/mức quay.
- W01 còn relabel thủ công. W02 đã có [preview sau clip](../../../outputs/roboflow-owner-review-20261004-v1/review/0001.png), [bằng chứng biến đổi](../../../artifacts/reports/roboflow-20261004/w02-preview.json). Chỉ sửa dòng 4 ở bản sao và giữ source ID; geometry pass không phải semantic pass.
- Manifest là hàng đợi QA, **chưa vẽ lại bbox hay tạo subset train**. Ảnh còn ignore không được biến thành negatives bằng cách xóa dòng label.

Không cần trả lời lại checklist này. Bước kỹ thuật tiếp: pilot relabel person trên train (66 ảnh có Phone use raw và các mẫu sai/thiếu đã phát hiện), rà completeness/UI/chất lượng, rồi review batch. Metadata nhóm/near-duplicate, looking_around/co-occurrence và quyết định A/B vẫn cần hoàn thành trước P1 acceptance. Không suy group_id từ filename; không tune test.
