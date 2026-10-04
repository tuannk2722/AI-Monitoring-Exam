# Roboflow v1 — báo cáo audit hoàn thiện 2026-10-04

> Audit gốc: giữ số liệu/quan sát lịch sử. Formulation B đã chốt và quyền SCB đã được owner xác nhận. Các kết luận chưa chốt A/B/quyền bên dưới chỉ thuộc thời điểm audit, không phải yêu cầu hỏi lại. Candidate card và dataset-research.md là trạng thái hiện hành.


**Đề xuất: giữ CANDIDATE để review/relabel subset; chưa dùng nguyên trạng cho training.** Điểm quan trọng là nhãn Phone use trộn box người và điện thoại/tay, lớp 0/1 chưa khớp semantics của dự án, thiếu grouping. Các cảnh báo geometry chỉ khoảng 0.005 pixel; không dùng số 34 file bị flag để suy ra có 34 lỗi lớn.

## Phạm vi, công cụ và bằng chứng

Đúng archive owner gửi: `C:/Users/OS/Downloads/Exam cheating.v1i.yolov8.zip`, 98,747,246 bytes; SHA-256 `70060bfe7d65dedcca6a72aaac423c95f402369eec08563b24ae8d962e666eed`. CRC pass. 6,826 ZIP entries gồm 9 directories + 6,817 files (3,407 JPG, 3,407 labels, 3 metadata); không nhầm file source-names.json bổ sung của audit với nội dung gốc ZIP.

[Metadata nguyên văn](../../../artifacts/reports/roboflow-20261004/audit.json) xác nhận project/version 1, source names, CC BY 4.0 và dates. [Provenance](../../../artifacts/reports/roboflow-20261004/audit.json) ghi code_commit, hash source code/script, Python/dependencies, ZIP và output hashes. Chưa có remote ZIP checksum độc lập để đối chiếu; kết luận áp dụng đúng bytes owner cung cấp.

Lần hoàn thiện **tái sử dụng ba full-decode reports** đã chạy bằng `audit_dataset` trên tất cả 3,407 ảnh. Script đọc lại ZIP nguyên bản, kiểm CRC/hash, quét **mọi dòng label**, đối chiếu số ảnh/label, tập file lỗi và counts strict với từng report. Hash reports tái sử dụng được lưu; không tuyên bố chạy lại toàn bộ image decode. Hash ảnh nội bộ/cross-SCB được tính lại trực tiếp từ ZIP. Chỉ trích 16 cặp train cho overlay mới, không giải nén lại toàn bộ.

[Script tái tạo](../../../scripts/audits/roboflow_v1.py) gọi công cụ audit/overlay/YOLO hiện có; thống kê bổ sung không thay parser, threshold hay acceptance. Output mới: `outputs/roboflow-v1-20261004-complete-v2/`; JSON nhỏ có thể review bằng Git: `artifacts/reports/roboflow-20261004/`.

## Cấu trúc và kiểm tra tự động

| Split | Ảnh / label | File lỗi / dòng lỗi | Ảnh 416×416 | Ảnh 640×640 |
|---|---:|---:|---:|---:|
| Train | 2,543 / 2,543 | 22 / 22 | 1,983 | 560 |
| Valid | 582 / 582 | 11 / 12 | 457 | 125 |
| Test | 282 / 282 | 1 / 1 | 212 | 70 |
| Tổng | 3,407 / 3,407 | 34 / 35 | 2,652 | 755 |

Layout `{train,valid,test}/images` ↔ `{train,valid,test}/labels`; pairing theo relative path. Không có missing/orphan/ambiguous, ảnh decode lỗi hay label rỗng. Quét lại từng dòng không thấy class ID ngoài 0..2, NaN/Infinity, width/height không dương. README/classes metadata không bị coi là label. Test chỉ được kiểm cấu trúc/nhãn/hash; không dùng ảnh test để chọn policy hoặc tuning.

[Train summary](../../../artifacts/reports/roboflow-20261004/audit.json), [valid summary](../../../artifacts/reports/roboflow-20261004/audit.json), [test summary](../../../artifacts/reports/roboflow-20261004/audit.json) giữ min/max/mean bbox, resolution, counts và đường dẫn full report. Các full report vẫn có `has_errors=true`; quá trình audit chạy xong không có nghĩa dữ liệu pass.

## Lỗi geometry: mức độ thực tế

- **35 dòng lỗi trong 34 file**: 22 horizontal, 13 vertical. Script kiểm từng dòng độc lập; khác với report gốc chỉ trả lỗi đầu tiên của mỗi file.
- Mức vượt normalized từ `7.812499999815259e-6` tới `1.201923076932232e-5`; quy về kích thước ảnh đều khoảng **0.005 pixel**. Đây là subpixel nhỏ, không phải lỗi bbox lớn. Kiểm Decimal trực tiếp từ text cũng cho phần vượt dương; chưa xác minh nguyên nhân làm tròn/export, không gọi đây chỉ là sai số máy 1e-16.
- Không dòng nào có overflow ≤1e-12 normalized. Con số này chỉ mô tả, **không phải epsilon được áp dụng**.
- [Diagnostics](../../../artifacts/reports/roboflow-20261004/audit.json); [toàn bộ raw line lỗi](../../../outputs/roboflow-v1-20261004-complete-v2/invalid-rows.json). W01/W02 trong checklist vẽ box gốc, đỏ là dòng bị flag, vàng là các dòng khác.
- Không tự clip/repair. Nếu owner chốt cách xử lý, phải tạo version derivative/provenance riêng, giữ raw bất biến.

## Phân bố lớp: raw, từng dòng hợp lệ và strict

Raw đếm tất cả dòng theo ID nguồn. Strict chỉ tính **file hoàn toàn hợp lệ**; khi một dòng sai, các dòng đúng cùng file cũng không vào counts strict.

| Source ID / tên | Raw train | Raw valid | Raw test | Raw tổng | Strict tổng |
|---|---:|---:|---:|---:|---:|
| 0 Looking around | 6,647 | 1,105 | 576 | 8,328 | 8,220 |
| 1 No cheating | 1,544 | 390 | 146 | 2,080 | 2,045 |
| 2 Phone use | 82 | 26 | 12 | 120 | 117 |
| Tổng | 8,273 | 1,521 | 734 | 10,528 | 10,382 |

Có **10,493 dòng geometry hợp lệ** nếu kiểm riêng từng dòng, nhưng chỉ 10,382 thuộc file hoàn toàn hợp lệ: chênh 146 raw−strict gồm 35 dòng lỗi + 111 dòng đúng bị loại theo file. Cả **120 dòng Phone use đều geometry hợp lệ**; 3 dòng mất khỏi counts strict vì lỗi nằm ở annotation khác trong cùng file. Điều này không xác nhận 120 nhãn đúng semantics.

| Phone use | Train | Valid | Test | Tổng |
|---|---:|---:|---:|---:|
| Annotation raw / strict | 82 / 79 | 26 / 26 | 12 / 12 | 120 / 117 |
| Ảnh có class raw / strict | 66 / 63 | 23 / 23 | 9 / 9 | 98 / 95 |

Phone use khoảng 1.14% raw annotations và 1.13% strict annotations. Mất cân bằng rõ, nhưng chưa có ngưỡng đủ dữ liệu/đánh giá model. 98 ảnh không đồng nghĩa 98 session hay tình huống độc lập. Nên ưu tiên review 66 ảnh positive train và các negative/nhãn thiếu có chủ đích trước quyết định subset.

## Kích thước bbox theo lớp

Thống kê dưới đây trên **train strict**. Width/height là các phân bố riêng, không ghép thành một box giả. Full min/p10/p50/p90/max và diện tích normalized nằm trong diagnostics.

| ID | Boxes | Width pixel min / p50 / max | Height pixel min / p50 / max |
|---|---:|---|---|
| 0 | 6,558 | 1 / 44 / 630 | 4 / 87 / 640 |
| 1 | 1,515 | 17 / 177 / 416 | 27 / 246 / 564 |
| 2 | 79 | 15 / 98 / 514.17 | 7 / 150 / 640 |

R01 (ID0) có box 1×4 pixel; R07 (ID2) có box 15×7 pixel. Kích thước lớn khác biệt còn liên quan unit: phone object, tay+phone, thân người, gần cả ảnh. Không tự đặt ngưỡng loại box nhỏ.

## Duplicate và video/session

SHA-256 được tính cho **mọi ảnh**, kể cả ảnh có label file lỗi: 3,407 ảnh / 3,407 hash duy nhất; 0 exact groups, 0 cross-split exact groups. So với 10,138 ảnh / 8,116 hash unique của đúng ba ZIP SCB đã kiểm lại SHA archive: 0 cross-source matches. [Kết quả](../../../artifacts/reports/roboflow-20261004/audit.json), [image hash manifest](../../../outputs/roboflow-v1-20261004-complete-v2/image-hashes.json).

**Chưa chạy thuật toán gần trùng.** Không có manifest frame→video/session/person/room trong ZIP. Filename `_mp4-`, timestamp và chuỗi đánh số là gợi ý liên hệ tác giả, không đủ căn cứ tạo group_id. Một số ảnh trông là frame/video screenshot hoặc ảnh đã xử lý; zero exact matches không chứng minh split độc lập, không phát hiện được re-encode/crop/noise variants. Chưa chấp nhận split website làm official split.

## Review trực quan và phát hiện

[Checklist có link từng ảnh](Roboflow-phone-use-20261004-review.md), [selection](../../../artifacts/reports/roboflow-20261004/audit.json), [quan sát đã xem](../../../artifacts/reports/roboflow-20261004/audit.json).

Đã xem **16 ảnh train hợp lệ + 2 ảnh train warning**: 3 mẫu min/median/max bbox area cho mỗi lớp và 7 mẫu Phone use bổ sung trải theo filename. R01–R06 được xem qua contact sheets, R07–R16 và W01–W02 qua overlay đầy đủ. Đây là 18 ảnh có chủ đích; không dùng để ước lượng tỷ lệ nhãn sai, không tuyên bố đã review toàn bộ 24 overlay cũ. V2 renders đã so hash và giống bản được mở xem trong lần hoàn thiện này.

- **Unit không đồng nhất được quan sát trực tiếp:** R07/R12/R13 bao phone/tay nhỏ; R08/R10/R16 bao người; R09 trên cùng ảnh có một box gần toàn người và một box tay/phone cùng ID2. Chỉ đổi tên Phone use→phone_use không giải quyết mâu thuẫn này.
- **Semantics/completeness cần review:** R01/R02 có ID0 trên người nhìn xuống/làm bài; W01 thấy phone trong tay người mang ID0. Đây là bằng chứng cần đối chiếu guideline/nhãn thiếu, không phải kết luận tự động mọi box đó sai.
- R05 có người gục trên bàn mang ID1; tên No cheating không chứng minh normal/negative. R06 có box ID1 bao gần cả cảnh.
- Domain: R10 talking-head, R11 screenshot web/UI, R14 góc từ trên xuống cạnh laptop, R16 phụ đề. R03/R09/R15 có nhiễu chấm; README nói không augmentation ở export, không cho phép suy cách tạo ảnh upstream. R05 có watermark Alamy: ghi nhận bằng chứng để đối chiếu nguồn, không suy license asset đã được xác minh hoặc vi phạm.

## Mapping, A/B và P1

Bảng ID nguồn→quan sát→đề xuất, owner/TBD và điều kiện P1 nằm trong [candidate card](Roboflow-phone-use-20261004.md). Đề xuất **chưa chọn A/B**: A cần person-behavior unit đồng nhất; B cần person crops, liên kết phone và labels/negative đầy đủ. Cả hai chưa có đủ bằng chứng ở export hiện tại. Không benchmark/train hoặc đóng dataset acceptance.

## Tái tạo

Từ repository root, dùng Python của venv và **output/evidence mới chưa tồn tại**. Script không tải dataset; phải có đúng 4 ZIP local theo checksum. Thay đường dẫn archive khi chuyển máy.

Chạy đầy đủ từ ZIP, gồm giải nén và image decode audit:

```powershell
.venv/Scripts/python.exe scripts/audits/roboflow_v1.py --archive "C:/Users/OS/Downloads/Exam cheating.v1i.yolov8.zip" --scb-archives "C:/Users/OS/Downloads" --output outputs/rf-reproduce-full --evidence outputs/rf-reproduce-full/evidence
```

Lần này đã chạy chế độ tái sử dụng full-decode reports, rồi kiểm raw labels/hash và tạo review mới:

```powershell
.venv/Scripts/python.exe scripts/audits/roboflow_v1.py --archive "C:/Users/OS/Downloads/Exam cheating.v1i.yolov8.zip" --scb-archives "C:/Users/OS/Downloads" --existing-reports outputs/roboflow-v1-20261004 --output outputs/roboflow-v1-20261004-complete-v2 --evidence outputs/roboflow-v1-20261004-complete-v2/evidence
```

Lệnh thứ hai là lệnh đã thực thi; chạy lại cần tên output mới. Chế độ full được cung cấp nhưng chưa chạy lại trong lần hoàn thiện này. Script exit 0 nghĩa là hoàn tất tạo bằng chứng; các report vẫn geometry FAIL. Cặp raw đã chọn được copy nguyên bytes; overlay gọi `export_overlays`, không phải model prediction.

Các JSON sinh ra được sao chép nguyên bytes vào `artifacts/reports/roboflow-20261004/`; `visual-review.json` ghi thêm quan sát con người/assistant, không phải output suy diễn tự động. Gói output cũ được giữ nguyên để truy vết.

## Kiểm tra và giới hạn

Kiểm tra cuối: **34 tests PASS**, Ruff PASS, compileall PASS, repository checker PASS (0 failures), git diff --check PASS; đối chiếu raw/strict/row counts, hash reports/script và links PASS. [Verification](../../../artifacts/reports/roboflow-20261004/audit.json) ghi phạm vi và giới hạn. Compile lần đầu bị sandbox chặn ghi __pycache__; đã chạy lại với quyền ghi và PASS. Audit kỹ thuật và hồ sơ hoàn thiện không thay thế owner quyết định unit/mapping/repair/accepted. Near duplicate, metadata groups, review exhaustive, consent theo asset và model quality chưa được kiểm chứng. P0 DVC push/pull chưa đóng; P1 chưa đạt exit gate.

## Hậu kiểm sau owner trả lời — 2026-10-04

Đã chốt [ADR-011](../../decisions/ADR-011-person-unit-phone-definition.md) và [18 quyết định có source path](../../../artifacts/reports/roboflow-20261004/review.json). Unit/phone_use không còn chờ trả lời; công việc relabel và acceptance vẫn còn. Số liệu/verification ở phần audit phía trên là lịch sử trước sửa thử, không được hiểu là toàn dataset đã sửa.

Đã chạy preview W02 riêng bằng lệnh:

```powershell
# Launcher W02 đã nghỉ; script và evidence lịch sử nằm trong review.json.
```

Chạy lại phải dùng tên output mới dưới outputs/. Script pin SHA-256 và đúng dòng nguồn, chỉ copy một ảnh/label, clip hai cạnh rồi tính lại center/width; strict validator giữ nguyên. [Repair evidence](../../../artifacts/reports/roboflow-20261004/review.json), [overlay](../../../outputs/roboflow-owner-review-20261004-v1/review/0001.png). Một dòng W02 đổi; những dòng còn lại giữ nguyên bytes; ảnh copy giữ hash. Đã xem overlay mới. W01 không sửa; raw/ZIP không đổi. Preview geometry pass không xác nhận semantics hay chất lượng model. Không thêm full extraction, không dùng test để chọn policy.
