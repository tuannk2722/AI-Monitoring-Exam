# Mở rộng pilot B — báo cáo nghiệm thu đề xuất R2

Ngày: 2026-10-06. Owner: chủ repository (solo); Codex tuyển candidate và hỗ trợ review. **Đã tuyển và review đợt R2; chưa phát hành dataset v5.**

## Kết quả

Theo [approval tiếp tục](../data-expansion-20261006/continuation-approval.json), R2 bổ sung **72 ảnh/anchor mới**: 48 SCB và 24 RF. Đã bổ sung bằng chứng cho 28 record review-only của v4. [Pointer v5 R2](../../../configs/datasets/pilot_b_expansion_v5_r2_draft.yaml) pin các proposal; v4 và draft ban đầu giữ nguyên.

| Nguồn | Pool train hợp lệ sau loại ảnh trùng byte với v4 | Tuyển review | Đề xuất giữ / loại anchor |
|---|---:|---:|---:|
| SCB Head + HRW | 3.801 ảnh unique | 48 | 44 / 4 |
| RF v1 | 2.502 ảnh unique | 24 | 17 / 7 |
| Tổng | 6.303 ảnh trong hai pool | 72 | 61 / 11 |

Trước loại ảnh trùng v4, SCB có 29.319 anchor trên 3.885 ảnh unique; RF có 8.152 anchor trên 2.521 ảnh. Lần lượt loại 84 và 19 ảnh. Đây là các lớp trong pool upstream train đã cấu hình, không phải toàn archive hoặc số cảnh độc lập. Mỗi ảnh lấy anchor nguồn lớn nhất; dHash farthest-first ưu tiên đa dạng ảnh cho review, không tự tạo nhóm cảnh. Budget 48/24 chỉ giới hạn công việc đợt này.

## Crop và nhãn đề xuất

Đã xem source-overlay và crop của toàn bộ 72 candidate. Target canonical mới vẫn `unknown`, values `[null,null]`, mask `[0,0]`. Bảng dưới là **đề xuất từ review thị giác, chưa phải nhãn owner nghiệm thu**.

| Nguồn | Phone P / N / U | Looking P / N / U |
|---|---:|---:|
| SCB 48 | 0 / 18 / 30 | 18 / 11 / 19 |
| RF 24 | 1 / 5 / 18 | 5 / 3 / 16 |

Evidence theo ID/crop hash/quan sát: [SCB](visual-review-proposals.json), [RF](../data-expansion-rf-20261006-r2/visual-review-proposals.json).

- RF-001/006/010: bút, giấy, hai tay và hướng nhìn nằm trong crop; đề xuất hai target âm, có thể bổ sung phone negative trong RF sau quyền/group review.
- RF-003/RF-014 cùng cảnh tủ xám/bàn trắng: đề xuất phone âm/dương tương ứng. [Hai crop sửa](../data-expansion-rf-20261006-r2/crop-refinements.json) tách bbox người khỏi context; box nguồn RF-014 chỉ bao điện thoại. Không coi hai mẫu là hai tình huống độc lập.
- Chưa thấy phone positive đủ bằng chứng trong 48 SCB; không kết luận toàn SCB không có phone. Có source `read` nhìn khỏi bài và source `TurnHead` đang viết; không map nguyên lớp.
- Đề xuất loại 11 anchor: SCB-029/036/038/046 và RF-002/005/011/012/018/020/024. Lý do theo từng ID: box nhiều người, chỉ đầu, quá mờ, screenshot/web hoặc thiếu bối cảnh phù hợp. Không xóa raw hoặc tự bổ sung thay thế.
- RF-013/022/023 có watermark stock; quyền gốc chưa xác minh. Ảnh ngủ/giơ tay/dàn dựng không tự thành normal hoặc negative.

Giữ 61 anchor không có nghĩa 61 mẫu đủ điều kiện train. Target unknown, crop QA, quyền và group là các điều kiện riêng. Phone positive mới vẫn thuộc RF, nên chưa khắc phục đầy đủ lệch nguồn.

## Nhóm cảnh và test

Đã tạo [triage cho 28 review-only cũ](existing-group-triage.json) và [11 đề xuất nối cảnh](scene-link-proposals.json). Ví dụ SCB-001/028 và SCB-005/024 liên quan thị giác; SCB-015/021/027/032 liên hệ record review-only của parent. RF-003/014, RF-005/006/010 cần ranh giới nhóm thận trọng; hai crop P047 có cùng source SHA.

Cảnh RF ghế xanh/hai bàn trắng liên quan nhóm parent mô tả trong evidence lịch sử. Đối chiếu parent train/val/test chỉ dùng metadata/fingerprint hoặc mô tả đã review; không xem lại ảnh test, không dùng metrics E001 tuyển candidate. SHA khác, dHash xa hoặc không có cạnh không chứng minh độc lập.

Mọi quan hệ mới chờ owner chốt; candidate mới giữ `leakage_group_id=null`, `split=null`, `training_eligible=false`. **Chưa có split/release hoặc real-world holdout được nghiệm thu.** Dữ liệu liên quan test E001 không được gọi là holdout chưa nhìn.

## Classroom-monitoring-dataset

[Thẩm định metadata](../data-expansion-20261006/classroom-monitoring-metadata-review.json) còn thiếu quyền/provenance/version/unit/group. Owner đã trả lời có thông tin và sẽ cung cấp; chưa có đường dẫn/nội dung cụ thể trong hội thoại. Nguồn này chờ bằng chứng; chưa tải media hoặc nhập nguồn mới. Không hỏi lại quyền SCB đã xác nhận.

## Nghiệm thu tiếp theo

Owner duyệt hoặc nêu ngoại lệ cho candidate, 11 anchor đề xuất loại, nhãn/crop thị giác và liên hệ cảnh theo báo cáo này. Codex nhập quyết định theo hash/version mới. Approval cho thay đổi trước R2 không được suy thành approval nhãn mới chưa tồn tại lúc đó.

Phát hành v5 còn cần quyền dùng RF mới theo phạm vi dự án, nghiệm thu proposal R2, bằng chứng nhóm đủ để lập split/protocol đánh giá và quyết định release riêng. Đóng gói review-only chỉ là staging, không phải dataset train. Chưa chạy E002.

## Media cục bộ

Media ở data/interim, không commit/upload:

- [SCB sheet đầu](../../../data/interim/pilot-b/expansion-20261006-r2/review/sheet-01.jpg): 8 source sheets và 4 crop sheets.
- [RF sheet đầu](../../../data/interim/pilot-b/expansion-rf-20261006-r2/review/sheet-01.jpg): 4 source sheets, 2 crop sheets; hai crop sửa trong refined-crops/.
- [28 review-only cũ](../../../data/interim/pilot-b/expansion-existing-review-20261006-r2/sheet-01.jpg): 5 sheets, không có ảnh test parent.

## Tái tạo và kiểm chứng

Logic trong [pilot_expansion.py](../../../src/ai_exam_monitoring/data/pilot_expansion.py), tái sử dụng selector/dHash/parser/verifier hiện có. Selector nhận tường minh images/train/ hoặc train/images/, từ chối val/test. Config pin archive/audit/parent/fingerprint/approval. Không dùng model/pretrained mới.

```powershell
.venv/Scripts/python.exe -m ai_exam_monitoring.data.pilot_expansion --config configs/datasets/pilot_b_expansion_selection_r2.yaml
.venv/Scripts/python.exe -m ai_exam_monitoring.data.pilot_expansion --config configs/datasets/pilot_b_expansion_rf_selection_r2.yaml
```

Lệnh từ chối output đã tồn tại; tái tạo dùng revision/output mới và lưu hash config mới. Nhãn thị giác là review riêng, không được sinh bằng source-class mapping. Sửa mã hóa chỉ ở mô tả, không đổi selection/crop/target: [encoding-repair.json](encoding-repair.json) lưu text/hash config thực thi cũ và phần sửa. Kết quả kiểm code/payload/proposal/pins/link nằm trong [verification.json](verification.json).
