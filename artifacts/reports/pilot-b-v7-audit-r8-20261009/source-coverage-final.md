# Funnel tám nguồn sau R7 — 2026-10-09

**Sáu nguồn local chưa được visual screening toàn bộ và chưa chứng minh exhausted.** Exam đóng góp 2 crop từ 13 ảnh trong cap chung 300. Open Images có metadata 1.743.042 ảnh train, nhưng bbox mới scan 264.870 nhóm ảnh đầy đủ. COCO đã xem hết 185 phone-context theo bộ lọc hiện hành; còn 235 work hints chưa xem. Tổng dataset không phải pool mẫu có ích hoặc nhóm độc lập.

Trạng thái Draft để owner nghiệm thu. Dùng [JSON cuối](source-counter-r2/source-coverage-measured.json), [CSV](source-counter-r2/source-coverage-measured.csv), [13 screening Exam](source-counter-r2/source-exam-screening.json), [6.948 row metadata chưa xem](source-counter-r2/source-unused-metadata.csv), [config/pins](source-audit-config-r2.yaml), [R8 có điều kiện](source-r8-plan-final.md). Counter chỉ đọc metadata đã pin, không decode/download media, train hoặc quyết định nhãn/membership/split. Các `source-coverage.md`, counter cấp thư mục và `source-r8-plan.md` là snapshot trước bản cuối này.

## Funnel measured

| Source | Tổng ảnh có sẵn | Train nguồn | Annotation/index scanned | Payload đã tiếp nhận | Materialized/xem R7 | Ảnh chọn / không chọn | Crop Draft |
|---|---:|---:|---|---:|---:|---:|---:|
| Classroom Attitude v3 | 3.573 | 2.566 | Toàn 3.573 ảnh trong inventory/annotation audit lịch sử | ZIP 3.573 | 172 | 49 / 123 | 60 |
| Student Behaviour v6 | 4.065 | 3.192 | Toàn 4.065 ảnh/annotation | ZIP 4.065 | 42 | 11 / 31 | 14 |
| Exam Cheating v2 | 772 | 679 | Toàn 772 ảnh/annotation | ZIP 772 | 13 | 2 / 11 | 2 |
| RF v1 | 3.407 | 2.543 | Toàn 3.407 ảnh trong inventory | ZIP 3.407 | 73 | 18 / 55 | 23 |
| SCB Head | 2.410 | 1.905 | Toàn 2.410 ảnh/label audit lịch sử | ZIP 2.410 | 66 | 23 / 43 | 26 |
| SCB HRW | 6.864 | 5.193 | Toàn 6.864 ảnh/label audit lịch sử | ZIP 6.864 | 34 | 18 / 16 | 18 |
| COCO train2017 | 118.287 | 118.287 | Metadata train đầy đủ; lọc 185 phone-context và 355 work-without-phone-annotation hints | 305 ảnh; 0 failure | 305 | 37 / 268 | 39 |
| Open Images train | 1.743.042 | 1.743.042 | Full image-info index; prefix bbox đọc 1.954.110 rows, giữ 264.870 nhóm ảnh đầy đủ | 598 ảnh; 1 failure >10MB | 598 | 84 / 514 | 92 |
| **Tổng screening** | Không cộng thành useful pool | — | — | — | **1.303** | **242 / 1.061** | **274** |

“Không chọn” là không có crop trong R7 primary, **không phải owner rejected**. Một ảnh có thể đóng góp nhiều crop, nên 242 ảnh chọn tạo 274 crop. Scanned nghĩa là index/annotation/structural QA, không phải visual semantic review toàn nguồn. Payload local đã decode trong audit lịch sử; task này không đọc lại media evaluation.

R7 immutable ghi accepted=0, training-eligible=0. Receipt mới xác nhận owner đã xem toàn bộ nhưng `batch_acceptance_inferred:false`; chưa có crop accepted chính thức. Owner đã bác phone P hiện tại của V7-B-079 (Open Images), chưa bác toàn crop hoặc đổi target khác. Chín ngoại lệ phản hồi: Classroom 3, Head 3, HRW 1, Open Images 2. Không có chỉ thị coi 265 crop còn lại là accepted. Full-crop owner rejection được ghi nhận: 0; target-positive rejection: 1. Quyền nguồn/membership/release còn chờ owner.

## Supply, exclusion và caps

| Source | Strict train rows trong supply | Parent/SHA/lineage loại | Near-evaluation cách ly | Sau exclusion đã đo | Hint anchors phone / looking / negative |
|---|---:|---:|---:|---:|---|
| Classroom | 2.565 | 67 | 80 | 2.418 | 1.723 / 2.883 / 952 |
| Student | 3.192 | 132 | 4 | 3.056 | 12.760 / 2.366 / 8.764 |
| Exam | 679 | 125 | 1 | 553 | 71 / 387 / 373 |
| RF | 2.521 | 50 | 14 | 2.457 | 57 / 6.398 / 1.488 |
| SCB Head | 1.767 | 61 trước supply | 16 | 1.751 | 0 / 7.138 / 3.717 |
| SCB HRW | 4.811 | 105 trước supply | 34 | 4.777 | 0 / 0 / 19.619 |

RF có 2.543 ảnh train nguồn; 2.521 là strict train supply, không phải tổng train. Với SCB, supply đã qua `local_inventory` lọc parent/SHA/lineage. Strict metadata train trước lọc là Head 1.828, HRW 4.916; chênh lệch 61/105 là combined exclusion, chưa tách phần SHA và lineage. Head 77/HRW 277 train label files không strict; không tự cứu/clip. Hint anchors là dòng bbox, có nhiều bbox/ảnh và bbox chỉ phone/head; không phải canonical person samples. 0 phone-hint SCB chỉ phản ánh namespace không có lớp phone.

Cap local R7 là 300 ảnh chung: 160 phone, 90 looking, 50 negative. Actual theo nguồn là Classroom 145/26/1, Student 9/4/29, Exam 3/5/5, RF 3/55/15. SCB cap chung 100: Head 60 looking+6 negative, HRW 34 negative. Farthest-first/dHash chọn một SHA ảnh mỗi lượt, không có quota đảm bảo từng source. Ảnh chưa chọn không mặc định thiếu giá trị.

## Vì sao Exam 13→2?

Sau 125 parent/lineage và 1 near-evaluation exclusion, còn 553 train rows trước hint selection. Trong 13 screening:

- Phone hints 014/024/063: cả ba chỉ tay/thiết bị, thiếu person attribution; visual receipt ghi loại unit.
- Looking 214/215/248 và negative 252/267/272/274: bảy ảnh cùng collage/simulation family, có overlay và không tạo bảy cảnh độc lập mới. Chúng không vào R7 primary, chưa phải owner rejected.
- Looking 221: receipt từng đề xuất C pair nhưng chưa được chọn cuối. **Chưa có final rejection reason riêng đã pin**; đây là reserve cần review lại nếu độc lập, không bịa lý do loại.
- 224→V7-C-079 và 277→V7-C-087: hai ảnh/hai crop được giữ. Receipt của 277 có same-frame P/N potential, nhưng hiện chỉ negative anchor được giữ; chưa có strong pair đủ điều kiện.

Audit lịch sử có 57 nhóm exact duplicate giữa Exam/RF cũ, 2 nhóm trùng qua split Exam. Nguồn có phim/video/watermark; tên “Exam” không chứng minh đúng domain hay độc lập. Không diễn giải 2 crop thành 770 ảnh bị reject hoặc source exhausted.

## Remaining: measured metadata, useful/independent unknown

Sau lọc original train, strict label, parent SHA/lineage, supply evaluation quarantine và SHA đã screening:

| Source | Row hint chưa xem | SHA ảnh duy nhất | Lineage tên gốc | Useful independent groups |
|---|---:|---:|---:|---|
| Classroom | 1.390 | 1.390 | 1.388 | Unknown |
| Student | 2.700 | 2.700 | 1.371 | Unknown |
| Exam | 474 | 472 | 354 | Unknown |
| RF | 2.384 | 2.384 | 2.377 | Unknown |
| SCB Head/HRW | Chưa đo SHA pool còn lại | Unknown | Unknown | Unknown |

6.948 row chỉ là hàng đợi metadata có thể kiểm tiếp. Student có augmentation: 2.700 SHA chỉ 1.371 name lineages. Exam 474 row chỉ 472 SHA. Scene/camera/room/video cần graph QA, kể cả tên khác hoặc ngoài ngưỡng dHash. Chưa chứng minh nhóm mới độc lập để chốt split; sáu nguồn local ở trạng thái `not_exhausted; independence_pending`.

Duplicate/exclusion có thể giao nhau, không cộng thành rejected total. Trong từng source, metadata SHA cho Classroom/Student/RF không có exact-byte duplicate; Exam có 4 nhóm/4 bản dư. SCB audit riêng: Head 0, HRW 1 nhóm/1 bản dư. Các số 0 không loại trừ augmentation, re-encode hoặc cùng video/cảnh. Roboflow snapshot tổng: 58 byte/RGB duplicate groups, 61 extra copies, 57 cross-source groups, 2 cross-split Exam groups. SCB ba archive: 10.138 ảnh/8.116 SHA, 1.892 duplicate groups, 2.022 extra copies, 961 cross-split groups. R7 lineage triage cách ly 43 screening keys; public rights quarantine có 34 ảnh ngoài primary. R2 crop dedupe 212→192 merge 20 bản dư; đó không phải total duplication cho mọi revision hoặc R7.

## Public filters và phần chưa quét

**COCO:** 185 eligible phone-context CC BY train đã xem hết qua R1/R3. Exhausted chỉ áp dụng bộ lọc này. Trong 355 work-without-phone-annotation hints, đã xem 120, còn 235 chưa xem; không suy chúng thành phone N. Có thể xét 235 có chọn lọc hoặc tạo version filter mới để tìm phone thiếu annotation/scene match. 305 ảnh đã xem không đại diện 118.287 train. Không refill bằng ảnh stock/tay-only/negative dễ.

**Open Images:** metadata có 1.743.042 unique train IDs; prefix 301.989.888/2.258.447.590 bytes=13,3716% bytes. Đọc 1.954.110 annotation rows, bỏ toàn nhóm ảnh cuối, giữ 264.870 nhóm đầy đủ. Prefix không random/exhaustive; không ước lượng tuyến tính useful yield phần còn lại. 1.128 Mobile phone boxes trong prefix không phải 1.128 person phone P. R1–R4 xem 181+18+200+199=598 payload; 1 failure quá 10MB. Title hints có nhiều product/hand-only; 399 work hints R3/R4 thường thiếu desk-phone P. Missing phone annotation không tạo N.

Quét tiếp train bbox range mới, nối nhóm ảnh đầy đủ ở boundary; pin range/length/checksum/partial receipt. Ưu tiên Person+Mobile phone+Desk/Book/Laptop và title classroom/exam/work, geometry chỉ rank hint. Trong prefix đã scan, ưu tiên phone/person/work hints chưa xem thay tăng work negatives thiếu thiết bị. Khử trùng source ID/SHA/Flickr và graph trước visual; báo actual P/N/U, rights, groups và yield. Useful eligible remaining của Open Images và từng group vẫn unknown, không exhausted.

## Bằng chứng và giới hạn

Config R2 pin 14 JSON/JSONL inputs, 9 screening ledgers và 2 CSV public. Counter trả 8 sources/1.303 screened/274 crop/6.948 unused metadata rows. [Public/duplicate evidence bổ sung](source-public-evidence.json) pin summary COCO, prefix receipt và lịch sử duplicate/caps/lineage/rights. Validation scope ghi trong [receipt](source-validation.json): 5 unittest PASS, Ruff PASS, mypy module audit PASS, diff check PASS. Counter metadata, receipt và source docs là bằng chứng; total counts kế thừa archive snapshot đã pin, không tuyên bố publisher hiện nay không đổi.

Đã đọc AGENTS/index/TASK; R7 README/plan/config/supply/summary/screening inventory; docs nguồn v6, FPI/SCB và quyền public; code targeted expansion/COCO/OI. Không có estimated useful counts; thuộc tính chưa chứng minh giữ null/unknown. Không đọc test media/features/predictions, upload hoặc materialize release. R7/v4–v6 và historical evaluation artifacts giữ nguyên.
