# Roboflow — QA 27 ảnh còn lại và completeness 8 ảnh đã duyệt

**Cập nhật mới nhất:** Owner chốt P042 **giữ ngoài subset đầu tiên, có thể dùng sau**. Queue v2: 29 loại + 11 deferred + 13 held ngoài train + 21 bbox-approved = 74, không còn pending lựa chọn trong lượt này. 24 bbox giữ nguyên, completeness chưa hoàn tất. [Queue hiện hành](../../../outputs/roboflow-remaining-reviewed-20261004-v2/queue.json), [quyết định](../../../artifacts/reports/roboflow-20261004/p042-owner-decision.json), [summary/hash](../../../artifacts/reports/roboflow-20261004/p042-reviewed-summary.json). Tái tạo một lần bằng `python -m scripts.audits.roboflow_defer_p042` (từ chối ghi đè output).

Owner đã chọn formulation B, normal đã review và multi-label tại [ADR-012](../../decisions/ADR-012-formulation-b-multilabel.md), đồng ý guideline looking_around ảnh tĩnh và crop có ngữ cảnh. Các mục pending kiến trúc/P042 dưới đây ghi trạng thái lịch sử; công việc tiếp là completeness/crop QA cho 21 ảnh, không hỏi lại quyết định đã chốt.

## Kết quả sau quyết định owner

Đã áp dụng hai câu trả lời bên dưới: **13 ảnh được duyệt thêm, tương ứng 14 bbox**; P023 được owner xác nhận là phone. Tổng hiện tại **21 ảnh / 24 bbox được duyệt**, vẫn cần completeness trước train. **13 ảnh thiếu bằng chứng giữ ngoài train** theo owner; đây không phải xóa ảnh hay gán normal. **P042 chưa duyệt**, chưa suy diễn thành loại vĩnh viễn hoặc yêu cầu sửa tọa độ.

Queue 74 ảnh: **29 loại + 10 tạm ngoài subset từ trước + 13 giữ ngoài train lần này + 21 duyệt bbox + 1 chờ (P042)**. Dataset chưa accepted, 0 ảnh training eligible. Câu trả lời nguyên văn được bảo toàn trong [decision manifest](../../../artifacts/reports/roboflow-20261004/remaining-qa-owner-decisions.json); [summary/hash mới](../../../artifacts/reports/roboflow-20261004/remaining-qa-reviewed-summary.json), [queue mới](../../../outputs/roboflow-remaining-reviewed-20261004-v1/queue.json), [24 bbox được duyệt](../../../outputs/roboflow-remaining-reviewed-20261004-v1/approved-boxes.json). 8 record đã duyệt trước giữ nguyên nội dung; các blockers trong proposal cũ là lịch sử, không phủ nhận xác nhận P023 mới.

Các bảng/overlay bên dưới giữ làm bằng chứng của proposal đã được xem; chữ pending trong ảnh là trạng thái lúc xuất v2. Trạng thái hiện hành nằm ở queue mới. Không cần trả lời lại các mục đã chốt.

```powershell
.venv/Scripts/python.exe -m scripts.audits.roboflow_remaining_review --base outputs/roboflow-remaining-qa-20261004-v2 --output outputs/roboflow-remaining-reviewed-20261004-v1
```

Chạy lại phải chọn output mới. Tool xác minh checksum toàn bộ artifact của bản owner đã xem trước khi áp dụng quyết định, không xuất YOLO training labels.

## Kết quả và giới hạn trước owner review (lịch sử)

Đã xem riêng từng ảnh của **27 ảnh train còn lại** và **8 ảnh đã duyệt** trong queue 74 ảnh. Có **15 bbox đề xuất trên 14 ảnh**, **13 ảnh giữ chờ bằng chứng**. Đã xem lại 14 overlay có bbox. Đây là đề xuất thủ công của Codex, **chưa được owner duyệt**; 10 bbox cũ trên 8 ảnh giữ nguyên từng byte. Không xem test để chốt nhãn trong lượt này.

Toàn queue vẫn **29 loại + 10 tạm ngoài subset + 8 đã duyệt bbox + 27 chờ duyệt = 74**. Không gọi 35 ảnh ứng viên là bộ nhãn hoàn chỉnh. Tất cả vẫn ngoài train; dataset chưa accepted. Chưa xác nhận group/session, near-duplicate hay split độc lập. Không có kết luận chất lượng model.

**Xanh = person bbox đề xuất phone_use; cam = vùng xem bằng chứng, không phải nhãn.** Các crop chỉ phóng pixel gốc, không khôi phục chi tiết bị mất. Bbox chỉ bao phần người nhìn thấy; có thể chứa khoảng bàn che giữa những phần cơ thể còn thấy. Người không có bbox không có nghĩa là normal.

## Owner review — 14 ảnh có đề xuất

Với mỗi dòng: xác nhận đúng người/phone và mép bbox; ghi mã ảnh cần sửa. Có thể trả lời chung “duyệt các dòng trừ …”. Riêng P023 cần xác nhận vật thể, P042 cần quyết định phạm vi subset. Duyệt các dòng này chỉ duyệt positive/bbox, chưa xác nhận completeness hoặc acceptance.

| ID | Số bbox | Ảnh | Quan sát / cần kiểm |
|---|---:|---|---|
| P002 | 1 | [bbox](../../../outputs/roboflow-remaining-qa-20261004-v2/overlays/P002.png) · [chi tiết](../../../outputs/roboflow-remaining-qa-20261004-v2/details/P002.png) | Người áo trắng phía sau cầm phone; người phía sau bên phải chưa rõ vật ở tay. |
| P007 | 2 | [bbox](../../../outputs/roboflow-remaining-qa-20261004-v2/overlays/P007.png) · [chi tiết](../../../outputs/roboflow-remaining-qa-20261004-v2/details/P007.png) | Hai người bên trái có phone; kiểm mép bbox tại ghế che người. |
| P009 | 1 | [bbox](../../../outputs/roboflow-remaining-qa-20261004-v2/overlays/P009.png) · [chi tiết](../../../outputs/roboflow-remaining-qa-20261004-v2/details/P009.png) | Người áo caro phía trước cầm phone sát mép dưới ảnh. |
| P022 | 1 | [bbox](../../../outputs/roboflow-remaining-qa-20261004-v2/overlays/P022.png) · [chi tiết](../../../outputs/roboflow-remaining-qa-20261004-v2/details/P022.png) | Người áo xanh bên phải cầm phone; bbox gồm chân nhìn thấy. |
| P023 | 1 | [bbox](../../../outputs/roboflow-remaining-qa-20261004-v2/overlays/P023.png) · [chi tiết](../../../outputs/roboflow-remaining-qa-20261004-v2/details/P023.png) | Vật đen trong tay người phía trước giống phone; cần xác nhận vật thể trước khi duyệt. |
| P028 | 1 | [bbox](../../../outputs/roboflow-remaining-qa-20261004-v2/overlays/P028.png) · [chi tiết](../../../outputs/roboflow-remaining-qa-20261004-v2/details/P028.png) | Người áo sọc hàng giữa bên phải tương tác thiết bị; kiểm vùng E1. |
| P032 | 1 | [bbox](../../../outputs/roboflow-remaining-qa-20261004-v2/overlays/P032.png) · [chi tiết](../../../outputs/roboflow-remaining-qa-20261004-v2/details/P032.png) | Người áo tím phía trước chạm phone trên bàn. |
| P033 | 1 | [bbox](../../../outputs/roboflow-remaining-qa-20261004-v2/overlays/P033.png) · [chi tiết](../../../outputs/roboflow-remaining-qa-20261004-v2/details/P033.png) | Phone trên bàn của người phía sau; kiểm phần chân thuộc đúng người. |
| P035 | 1 | [bbox](../../../outputs/roboflow-remaining-qa-20261004-v2/overlays/P035.png) · [chi tiết](../../../outputs/roboflow-remaining-qa-20261004-v2/details/P035.png) | Người áo tím chạm phone trên bàn; phone có thể nằm ngoài person bbox. |
| P038 | 1 | [bbox](../../../outputs/roboflow-remaining-qa-20261004-v2/overlays/P038.png) · [chi tiết](../../../outputs/roboflow-remaining-qa-20261004-v2/details/P038.png) | Người phía trước cầm phone; kiểm phần quần nhỏ lộ sát mép dưới. |
| P039 | 1 | [bbox](../../../outputs/roboflow-remaining-qa-20261004-v2/overlays/P039.png) · [chi tiết](../../../outputs/roboflow-remaining-qa-20261004-v2/details/P039.png) | Người phía trước chạm phone; kiểm phần quần nhỏ lộ sát mép dưới. |
| P042 | 1 | [bbox](../../../outputs/roboflow-remaining-qa-20261004-v2/overlays/P042.png) · [chi tiết](../../../outputs/roboflow-remaining-qa-20261004-v2/details/P042.png) | Thấy phone dưới bàn, người bị cắt mạnh: cần chốt có giữ trong subset đầu tiên. |
| P043 | 1 | [bbox](../../../outputs/roboflow-remaining-qa-20261004-v2/overlays/P043.png) · [chi tiết](../../../outputs/roboflow-remaining-qa-20261004-v2/details/P043.png) | Người áo xanh phía trước cầm phone; người phía sau chưa đủ nhãn. |
| P047 | 1 | [bbox](../../../outputs/roboflow-remaining-qa-20261004-v2/overlays/P047.png) · [chi tiết](../../../outputs/roboflow-remaining-qa-20261004-v2/details/P047.png) | Người phía sau cầm phone; bbox gồm quần nhìn thấy dưới bàn, cần kiểm association. |

**Trả lời owner:** Duyệt tất cả trừ P042, trong đó P023 tôi xác nhận vật người đó cầm có tính là phone.

## 13 ảnh chưa đủ bằng chứng

Đề xuất tiếp tục giữ ngoài dữ liệu train khi chưa giải quyết được. Không bắt owner xác nhận vật thể từ ảnh mờ; có thể giữ chờ. P005/P025/P040 bảo toàn ignore đã chốt. P070 bảo toàn reject đã chốt, không hỏi lại.

| ID | Ảnh | Lý do |
|---|---|---|
| P003 | [bbox](../../../outputs/roboflow-remaining-qa-20261004-v2/overlays/P003.png) · [chi tiết](../../../outputs/roboflow-remaining-qa-20261004-v2/details/P003.png) | Vật giống phone trên bàn chung; chưa chắc gắn với người nào. |
| P004 | [bbox](../../../outputs/roboflow-remaining-qa-20261004-v2/overlays/P004.png) · [chi tiết](../../../outputs/roboflow-remaining-qa-20261004-v2/details/P004.png) | Vật ở mép dưới bị cắt; sửa geometry W02 không chứng minh semantics. |
| P005 | [bbox](../../../outputs/roboflow-remaining-qa-20261004-v2/overlays/P005.png) · [chi tiết](../../../outputs/roboflow-remaining-qa-20261004-v2/details/P005.png) | Vật trên bàn chung chưa rõ association; giữ quyết định ignore R01. |
| P024 | [bbox](../../../outputs/roboflow-remaining-qa-20261004-v2/overlays/P024.png) · [chi tiết](../../../outputs/roboflow-remaining-qa-20261004-v2/details/P024.png) | Vật ở tay/ngăn bàn quá nhỏ; phóng pixel vẫn chưa xác nhận được. |
| P025 | [bbox](../../../outputs/roboflow-remaining-qa-20261004-v2/overlays/P025.png) · [chi tiết](../../../outputs/roboflow-remaining-qa-20261004-v2/details/P025.png) | Giữ ignore R07, không cần duyệt lại quyết định cũ. |
| P026 | [bbox](../../../outputs/roboflow-remaining-qa-20261004-v2/overlays/P026.png) · [chi tiết](../../../outputs/roboflow-remaining-qa-20261004-v2/details/P026.png) | Tay/vật ở đùi bị che, chưa đủ bằng chứng. |
| P027 | [bbox](../../../outputs/roboflow-remaining-qa-20261004-v2/overlays/P027.png) · [chi tiết](../../../outputs/roboflow-remaining-qa-20261004-v2/details/P027.png) | Vùng tay người bên trái chưa rõ vật thể. |
| P037 | [bbox](../../../outputs/roboflow-remaining-qa-20261004-v2/overlays/P037.png) · [chi tiết](../../../outputs/roboflow-remaining-qa-20261004-v2/details/P037.png) | Vật đen tròn có thể không phải phone; không lan nhãn từ ảnh tương tự. |
| P040 | [bbox](../../../outputs/roboflow-remaining-qa-20261004-v2/overlays/P040.png) · [chi tiết](../../../outputs/roboflow-remaining-qa-20261004-v2/details/P040.png) | Giữ ignore R13 phần bị che, không cần duyệt lại quyết định cũ. |
| P041 | [bbox](../../../outputs/roboflow-remaining-qa-20261004-v2/overlays/P041.png) · [chi tiết](../../../outputs/roboflow-remaining-qa-20261004-v2/details/P041.png) | Vật đen dạng bao gập chưa phân biệt phone/ví; vật trên bàn sau chưa rõ association. |
| P048 | [bbox](../../../outputs/roboflow-remaining-qa-20261004-v2/overlays/P048.png) · [chi tiết](../../../outputs/roboflow-remaining-qa-20261004-v2/details/P048.png) | Ảnh có chữ và số chèn; chưa xác nhận phone. Đề xuất giữ ngoài subset đầu tiên, chờ owner. |
| P069 | [bbox](../../../outputs/roboflow-remaining-qa-20261004-v2/overlays/P069.png) | Người gục đầu, chưa có phone rõ; không tự chuyển No cheating thành normal. |
| P070 | [bbox](../../../outputs/roboflow-remaining-qa-20261004-v2/overlays/P070.png) | Đã ghi reject dòng bbox toàn cảnh theo R06; chưa đủ nhãn từng người, không xuất nhãn rỗng. |

**Trả lời owner (nếu có bằng chứng bổ sung hoặc muốn chốt P048):** Đồng ý giữ ngoài dữ liệu train.

## Completeness — 8 ảnh đã duyệt bbox

| ID | Đã quan sát | Còn thiếu |
|---|---|---|
| P006 | Bốn người; hai positive đã duyệt | Tay người phía sau bị che; nhãn những người khác |
| P008 | Hai người chính, thêm người bị cắt bên phải | Người bị cắt và nhãn người không có phone rõ |
| P019 | Positive phía trước, người phía sau và người bị cắt bên trái | Vùng tay bị che và nhãn người còn lại |
| P029 | Hai người chuyền một phone; cả hai positive theo owner | Co-occurrence và biểu diễn task; không đổi thành phone trên bàn |
| P030 | Người bên phải positive; bên trái viết | Nhãn người bên trái, không tự gọi normal |
| P031 | Người trước positive, người sau viết | Nhãn người phía sau |
| P034 | Phone trên bàn người trước; người sau viết | Nhãn người phía sau; phone không bắt buộc nằm trong person bbox |
| P036 | Người trước phone trên bàn, đầu quay | Co-occurrence và nhãn người phía sau |

Đây là rà completeness bằng mắt và ghi điểm thiếu, **không phải xác nhận nhãn đã đầy đủ**. [Bbox đã duyệt giữ nguyên](../../../outputs/roboflow-remaining-qa-20261004-v2/approved-boxes.json), [completeness](../../../outputs/roboflow-remaining-qa-20261004-v2/completeness.json).

## Tái tạo và kiểm chứng

Nguồn ảnh/hash lấy từ queue v2 đã pin; dùng lại 74 ảnh trích trước đó, không giải nén thêm archive. [Plan](../../../artifacts/reports/roboflow-20261004/remaining-qa-plan.json), [summary/hash](../../../artifacts/reports/roboflow-20261004/remaining-qa-summary.json), [review có source path/hash](../../../outputs/roboflow-remaining-qa-20261004-v2/review.json), [reject P070 theo dòng/hash](../../../outputs/roboflow-remaining-qa-20261004-v2/source-rejections.json).

```powershell
.venv/Scripts/python.exe -m scripts.audits.roboflow_remaining_qa --base outputs/roboflow-batch2-reviewed-20261004-v2 --images outputs/roboflow-pilot-20261004-v3/images --output outputs/roboflow-remaining-qa-20261004-v2
```

Khi chạy lại phải chọn output mới. Tool kiểm checksum base, ảnh, source label P070; kiểm coverage/geometry; từ chối ghi đè; không xuất YOLO training labels. Fixture chỉ kiểm phần mềm. V1 là preview, v2 là bản cuối sau khi chỉnh extent P047.

## Việc tiếp theo

1. Review đã được áp dụng; P048 cùng 12 ảnh thiếu bằng chứng giữ ngoài train. P042 còn chưa duyệt nhưng không chặn công việc trên 21 ảnh đã duyệt. Nếu muốn đưa P042 trở lại, owner cần nói rõ sửa bbox hay chấp nhận phạm vi người bị cắt; hiện chưa đưa vào subset.
2. Chốt quy tắc biên looking_around, cách biểu diễn normal/co-occurrence và A/B bằng ADR trước khi hoàn thiện nhãn mọi người. Owner là người chốt; chưa đổi config/mapping.
3. Hoàn thiện annotation/completeness, xác minh nhóm và split chống leakage, rồi đánh giá gate P1. Không suy group_id từ ảnh giống nhau. P0 DVC push/pull vẫn chưa kiểm chứng.
