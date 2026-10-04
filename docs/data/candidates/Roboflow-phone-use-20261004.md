# Dataset Candidate — DS-RF-EXAM-V1-20261004

## Quyết định hiện tại

**CANDIDATE — hoàn thành bộ hồ sơ audit, chưa ACCEPT cho training.** Owner chọn audit v1 làm nguồn phone_use tạm. Đề xuất sau audit: giữ để review/relabel một subset train; không dùng nguyên trạng toàn nguồn. Vấn đề chính là annotation unit và semantics không đồng nhất, không phải 34 cảnh báo geometry nhỏ tự chúng chứng minh chất lượng kém.

Owner/người chốt: chủ repository. Audit kỹ thuật và xem mẫu: Codex. Ngày: 2026-10-04. [Báo cáo](Roboflow-phone-use-20261004-audit.md), [ảnh/câu hỏi review](Roboflow-phone-use-20261004-review.md).

## Thông tin nhận dạng/provenance

- Nguồn owner chỉ định: [trn quang tip / Exam cheating v1](https://universe.roboflow.com/trn-quang-tip/exam-cheating-9iz1y-rrfsz/dataset/1).
- File owner gửi: `C:/Users/OS/Downloads/Exam cheating.v1i.yolov8.zip`, **98,747,246 bytes**.
- SHA-256: `70060bfe7d65dedcca6a72aaac423c95f402369eec08563b24ae8d962e666eed`. ZIP CRC pass, 6,826 entries gồm directories; đúng 3,407 JPG + 3,407 label TXT + 3 file metadata.
- `data.yaml` xác nhận workspace/project/version 1 và names; README ghi version date 2024-09-18, export date 2024-09-30 10:40 GMT. Phân biệt ngày export với ngày audit 2026-10-04. Không thay bằng phiên bản 7 của model hay con số 3,799 của toàn project.
- [Provenance](../../../artifacts/reports/roboflow-20261004/audit.json) ghi hash source, code/script, commit, Python/dependencies, reports tái sử dụng và hash outputs; [metadata nguyên văn](../../../artifacts/reports/roboflow-20261004/audit.json) giữ data.yaml và hai README trong ZIP. Định danh bằng ZIP local, chưa so hash với một bản tải remote độc lập.
- Citation: *Exam cheating Dataset*, trn quang tip, Roboflow Universe, version 1, URL ở trên. Lệnh tái tạo cụ thể trong báo cáo audit.

## Quyền/Privacy

- `data.yaml` và README.dataset.txt trong ZIP ghi **CC BY 4.0**, cùng thông tin công bố trước đó trên project. Đây là khai báo license của nguồn; giữ citation/attribution và ghi thay đổi khi tạo derivative.
- Chưa nhận hợp đồng/metadata consent theo từng ảnh; ảnh mẫu có watermark stock-photo, UI trình duyệt/video và phụ đề. Không tự kết luận các asset đó không được phép dùng, cũng không coi dòng license là bằng chứng đã đối chiếu mọi quyền tác giả, consent hoặc điều kiện riêng về weights.
- Phạm vi hiện tại: audit cục bộ, ảnh ở outputs ignored. Không upload media để chạy API inference. Phê duyệt SCB mà owner đã xác nhận được giữ nguyên; không hỏi lại hoặc dùng nó để suy ra metadata video/group còn thiếu của Roboflow.

## Nội dung và giới hạn

- 3,407 cặp ảnh/nhãn: train 2,543, valid 582, test 282; YOLO 5 trường, `{split}/images` ↔ `{split}/labels`. 2,652 ảnh 416×416 và 755 ảnh 640×640.
- Không ảnh hỏng/missing/orphan/ambiguous/label rỗng; quét từng dòng không thấy NaN/Infinity, ID ngoài 0..2 hoặc kích thước không dương. Có **35 dòng vượt biên trong 34 file**, tất cả khoảng **0.005 pixel**. Chưa đổi epsilon/clip/repair.
- Raw: 10,528 annotations; strict (file label hoàn toàn hợp lệ): 10,382. Phone use **120 raw / 117 strict**, nằm trong **98 raw / 95 strict images**. Riêng train: 82 raw / 79 strict annotations, 66 raw / 63 strict images. Ảnh/frame này không được coi là 98 tình huống độc lập.
- Exact duplicate: 0 trong v1/cross-split và 0 cross-SCB khi so toàn bộ ảnh của đúng ba ZIP SCB. Near duplicate chưa chạy. ZIP không có frame→video/session/person/room manifest; `_mp4-`/timestamp trong filename chỉ là gợi ý tìm metadata, không được gán group_id.
- Đã xem 16 ảnh train hợp lệ + 2 ảnh warning theo checklist. Mẫu có cảnh thi, cận cảnh, talking-head, screenshot web, watermark và ảnh nhiễu chấm. Export ghi không augmentation; điều đó không chứng minh ảnh upstream chưa từng xử lý. Không suy ra cách sinh ảnh nhiễu.

## Canonical mapping (đề xuất, chưa phê duyệt)

ID chép tường minh từ thứ tự names zero-based trong YAML YOLO nguồn, có [JSON ID/tên](../../../artifacts/reports/roboflow-20261004/audit.json). Không phải config converter.

| Source ID/tên | Ý nghĩa quan sát được | Đề xuất |
|---|---|---|
| 0 `Looking around` | R01–R03 và W01: box đầu/thân/cả ảnh; có người nhìn xuống và cầm vật giống phone | Chưa map trực tiếp `looking_around`; review nhãn sai/thiếu, unit, định nghĩa và ignore |
| 1 `No cheating` | R04–R06: box nhỏ quanh đầu, cả người hoặc gần toàn cảnh; người làm bài và người gục trên bàn | Không dùng tên mang kết luận vi phạm làm nhãn model; không tự map `normal` hoặc biến thành negative |
| 2 `Phone use` | R07–R16: box điện thoại/tay hoặc người; R09 cùng một ảnh có cả hai unit | Candidate cho `phone_use` sau review/relabel theo một unit thống nhất; không copy mapping theo tên |

117 strict annotations không phải bằng chứng 117 positive đã được con người xác nhận. Người/vật không có box không mặc định là negative/background.

## Vai trò đã chốt theo Formulation B

Nguồn bổ sung phone_use sau relabel theo người/crop; không dùng nguyên trạng hoặc map lớp nguồn tự động. Snapshot cuối: 28 người/crop trên 21 ảnh đã duyệt, 24 phone positives + 5 looking positives (1 co-occurrence); 27 người còn target unknown. [Tổng hợp review](Roboflow-phone-use-20261004-review.md) là trạng thái hiện hành.

B đã được owner chọn tại ADR-012; không cần benchmark A/B để quyết định lại. P036 giữ unknown, normal không suy từ thiếu box. Source status vẫn candidate, dataset chưa accepted. Công việc còn lại là [preparation chung với SCB](../dataset-research.md), không mở lại chuỗi pilot/batch review. Metadata group và coverage negative còn thiếu; quyền SCB đã xác nhận không tự thay thế quyền/metadata nguồn Roboflow.

Số liệu audit ở trên thuộc ZIP bất biến; mô tả chưa near-duplicate là lịch sử audit nguồn. Sau đó đã có similarity triage trên pilot, không phải chứng minh leakage đã giải quyết.
