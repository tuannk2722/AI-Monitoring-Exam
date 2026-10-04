# Roboflow v1 — tổng hợp quyết định owner

Đây là hồ sơ review duy nhất, thay thế pilot/batch2/remaining/crop/context riêng lẻ. Không có câu hỏi review ảnh mới. Các câu trả lời nguyên văn và nội dung các file cũ được giữ trong [review.json](../../../artifacts/reports/roboflow-20261004/review.json) tại records và retired_files.

## Trạng thái hiện hành

- 74 ảnh: 29 loại, 11 deferred (gồm P042), 13 held ngoài train, 21 ảnh có người đã duyệt.
- **28 person bbox/crop đã duyệt** trên 21 ảnh; 24 phone_use positives, 5 looking_around positives, P033-person-01 có cả hai.
- 23 looking_around unknown và 4 phone_use unknown; không normal/negative mới.
- Person/crop approval không phải dataset acceptance; training_eligible=false cho tất cả.
- Current records: review.json → current_person_crops và image_queue. Các source/crop SHA và owner_answers nằm trong từng record. Không dùng một summary trung gian làm trạng thái cuối.

## Quyết định đã áp dụng

| Giai đoạn | Quyết định |
|---|---|
| Review nguồn R01–R16/W01–W02 | Person unit; phone cầm/tương tác hoặc trên bàn liên kết rõ; ignore vùng R01/R07/R13; reject box toàn cảnh R06; relabel R09/W01; UI/phụ đề loại; watermark được owner cho phép trong chọn mẫu |
| Pilot | Bbox visible-person; P029 là hai người chuyền cùng một phone, cả hai positive; không phải phone đặt trên bàn. P053/P065 loại nhiễu |
| Batch 2 | Duyệt positives/bbox được ghi trong batch2-owner-review; không duyệt completeness bằng việc duyệt bbox |
| Quyết định nhóm | P058–P064 loại nhiễu; P020/P021/P071/P049/P051/P052/P054–P057 deferred |
| Remaining | Duyệt thêm 13 ảnh/14 bbox; P023 owner xác nhận phone; 13 ảnh thiếu bằng chứng giữ ngoài train |
| P042 | Deferred khỏi subset đầu tiên, có thể dùng sau; không loại vĩnh viễn |
| Context R1 | “duyệt tất cả các crop và target đã đúng.” |
| Context R2 | “duyệt thêm looking_around cho P033, với P036 không suy looking_around chỉ từ quay đầu.” |
| Context R3 | “Duyệt cả 4 người bổ sung với nhãn looking_around, phone_use để unknown.” |

Bốn người mới: P006-extra-01, P007-extra-01, P008-extra-01, P047-extra-01. Phone positives cũ được bảo toàn; P036 looking_around vẫn unknown.

## Cách truy vết và xem lại

[Manifest/ảnh đã review](../../../outputs/roboflow-context-reviewed-20261004-v1/approved-person-crops.json) chứa crop_path và hash; [bằng chứng ảnh trước approval](../../../outputs/roboflow-context-review-20261004-v2/review.json) định danh panel theo target. Outputs là media local ignored, không phải bản phân phối dataset. Các ảnh có chữ pending là render lịch sử trước câu trả lời, không phủ nhận approval trong manifest cuối.

review.json giữ nguyên từng JSON gốc cùng SHA và snapshots tài liệu đã gom, kể cả câu trả lời chưa commit trước cleanup. Các script theo ngày/batch đã được bỏ; logic validation/owner decision dùng lại nằm trong src/ai_exam_monitoring/data/review.py và có regression tests. Không chạy lại các launcher lịch sử để cập nhật trạng thái.

## Phần đã chốt và phần preparation

Kiến trúc/ngữ nghĩa theo [ADR-012](../../decisions/ADR-012-formulation-b-multilabel.md). Không hỏi lại A/B, normal, co-occurrence, crop context hoặc R1–R3. Công việc preparation tiếp theo được giới hạn trong [phương án hai nguồn](../dataset-research.md); không tạo thêm chuỗi review ảnh nhỏ lẻ ở giai đoạn Audit & Spec.
