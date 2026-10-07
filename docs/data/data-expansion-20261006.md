# Đề xuất mở rộng dữ liệu sau E001

Ngày: 2026-10-06. Trạng thái: **owner đã duyệt hướng hai luồng, thẩm định metadata Classroom-monitoring-dataset và draft pointer v5 sau candidate**. Giữ semantics `phone_use`, `looking_around`, mask `unknown`. [Approval](../../artifacts/reports/data-expansion-20261006/owner-approval.json) và [báo cáo triển khai](../../artifacts/reports/data-expansion-20261006/README.md) ghi phạm vi cụ thể. Đã tạo draft pointer từ batch 28 review-only hiện có; chưa nhận nguồn mới hoặc phát hành/train dataset mới.

## Cập nhật triển khai R2 sau approval tiếp tục

Đã tuyển và review72 ảnh/anchor mới(48SCB +24RF) từ archive đã pin, ngoài ledger v4; tạo đề xuất giữ61/loại11 anchor,2 crop RF sửa và11 liên hệ cảnh. [Báo cáo R2](../../artifacts/reports/data-expansion-20261006-r2/README.md) và [pointer R2](../../configs/datasets/pilot_b_expansion_v5_r2_draft.yaml) là trạng thái proposal hiện tại; draft28 hồ sơ ban đầu được giữ làm lịch sử.

Target canonical mới vẫn unknown/mask0. Chưa có phone positive đủ bằng chứng trong48SCB; RF có đề xuất1positive/5negative. Chưa nhận nhãn/crop/group mới vào release. Owner cho biết sẽ cung cấp thông tin quyền/provenance Classroom-monitoring; hiện chưa có nội dung cụ thể. Cần nghiệm thu báo cáo R2 và giải group/quyền trước split/release; không chạy E002.

## Đề xuất chính

Nên dùng **cả nguồn hiện có lẫn nguồn mới**, theo hai luồng có thứ tự. Bắt đầu bằng các record SCB5/Roboflow đã có provenance và review, giải quyết bằng chứng nhóm cảnh và tạo candidate batch nhỏ theo từng người. Đồng thời thẩm định một bộ classroom behavior mới có cả phone và hướng quay đầu. Chỉ sau khi biết overlap, license, provenance và chất lượng annotation mới quyết định có nhận nguồn mới vào version không.

Chỉ khai thác nguồn cũ sẽ giữ nguyên giới hạn bối cảnh/nguồn đã thấy; chỉ thêm nguồn mới có thể tăng lượng ảnh nhưng vẫn để model phân biệt nguồn thay cho target. Vì thế mục tiêu là tăng **coverage hai trạng thái trong từng nguồn/cảnh độc lập**, không đặt quota ảnh hoặc tỷ lệ nguồn trước khi thấy audit đầy đủ. Những con số trong báo cáo là mô tả hiện trạng, không phải chỉ tiêu nghiệm thu model.

## Kiểm kê pilot v4

Script kiểm kê đọc `review-ledger.jsonl` và `manifest.jsonl` bằng parser canonical. Nó chỉ đọc metadata target/source/split/group và hash; không mở crop hoặc source image. Các giá trị dưới đây khớp `reports/coverage.json` của v4.

| Nguồn | Hồ sơ ledger | Train / val / test / review-only | Phone P/N/U | Looking P/N/U | Nhận xét |
|---|---:|---:|---:|---:|---|
| Roboflow v1 | 28 | 11 / 10 / 2 / 5 | 24 / 0 / 4 | 5 / 0 / 23 | Tất cả phone positives đã duyệt; chưa có negative. |
| SCB Head/TurnHead | 28 | 16 / 0 / 2 / 10 | 0 / 0 / 28 | 28 / 0 / 0 | Source class không thể thay nhãn target; looking dương chưa có âm trong nguồn này. |
| SCB HRW/read-write | 56 | 33 / 3 / 7 / 13 | 0 / 9 / 47 | 0 / 56 / 0 | Có phone âm và looking âm, không có dương trong nguồn này. |
| **Toàn ledger** | **112** | **60 / 13 / 11 / 28** | **24 / 9 / 79** | **33 / 56 / 23** | **10 hồ sơ đủ hai target, 102 chỉ biết ít nhất một target.** |

V4 có 105 ảnh nguồn duy nhất cho 112 crop và 16 leakage group đã được duyệt cho 84 record sử dụng. Bảy crop bổ sung trong năm ảnh Roboflow đã biết là nhiều người từ cùng ảnh; không phải bảy bối cảnh độc lập mới. Toàn bộ 28 record `review_only` chưa có leakage group: 23 từ SCB (10 Head dương looking; 12 HRW looking âm chưa biết phone và 1 HRW biết cả hai âm) và 5 người từ Roboflow (4 phone dương, 1 looking dương). Các mẫu này có thể được dùng làm hàng đợi để xem xét giải quyết bằng chứng cảnh; trạng thái hiện tại vẫn chưa đủ điều kiện vào split.

Không có `video_id`, `session_id`, `room_id` hoặc `subject_id` thực nào trong 112 hồ sơ. Group ID hiện là ranh giới thị giác thận trọng đã được owner chấp nhận cho pilot local; chúng không chứng minh đó là buổi quay hay người độc lập. Trên train/val/test, phone positive đều từ Roboflow và phone negative đều từ SCB. Nhãn looking dương hiện thuộc SCB Head và một phần Roboflow, trong khi looking âm ở SCB HRW. Đây là source confounding rõ trong release; thêm nhiều ảnh từ cùng phân bố mà không có cả positive/negative trong từng nguồn sẽ không khắc phục nó.

Chi tiết đủ để tái tạo nằm tại [inventory metadata](../../artifacts/reports/data-expansion-20261006/inventory.json) và [hàng đợi 28 hồ sơ review-only](../../artifacts/reports/data-expansion-20261006/review-queue.json). Hash payload của v4 là `dbc1bf90a5605cac39b5c96503e71097ecd1eaab5b35e14f311f966edd503f53`; script cũng ghi hash đầu vào config/approval/manifest/ledger để phát hiện thay đổi.

## Ứng viên từ nguồn hiện có

Ưu tiên đầu tiên là candidate batch mới, nhỏ và hữu hạn từ SCB HRW và Head đã audit, cộng 5 hồ sơ Roboflow review-only. Batch là **đề xuất để review**, không phải nhãn tự động hoặc quyền tự nhập vào v5.

1. Dùng đủ 28 `review_only` trong evidence queue làm danh sách việc cần xử lý: kiểm tra/hoàn thiện mối liên hệ scene-group, đối chiếu crop đúng hash, xác nhận quyền và quyết định giữ `review_only`, loại, hay đề nghị xét cho một split mới. Tập này không giải source confounding nếu chỉ giải group: nguồn Roboflow vẫn không có negative phone.
2. Tạo shortlist mới trong SCB HRW/read-write để tìm trường hợp `phone_use` dương có bằng chứng nhìn thấy thiết bị gắn với đúng người; không suy từ source class `read`/`write`, không suy người không có box là âm. Đây là hướng quan trọng nhất để có phone positives ngoài Roboflow, nhưng có thể không tìm được candidate phù hợp trong archive hiện tại.
3. Trong SCB Head/TurnHead và HRW, kiểm tra ứng viên cho `looking_around` ở cả trạng thái dương/âm theo định nghĩa đã duyệt. Không map toàn lớp TurnHead thành looking; không dùng BowHead thay thế và không suy duration từ ảnh tĩnh.
4. Nếu kiểm kê media được tái lập sau khi có đủ archive, deduplicate chính xác và near-duplicate, sau đó gán group ở mức ảnh/capture/scene bằng evidence. Giữ cả frame hay crop liên quan trong cùng group. Không dùng filename, lớp nguồn, hash khác nhau hoặc upstream split làm chứng cứ độc lập.

SCB đã audit trước đây 10,138 ảnh, 8,116 SHA ảnh duy nhất và 1,892 nhóm exact duplicate; 961 nhóm có bản sao qua train/val khi xét các archive cùng nhau. Near-duplicate chưa kiểm tra. Kiểm tra lại ngày 2026-10-06 sau approval: hai ZIP SCB Head/HRW và ZIP Roboflow v1 đều có tại đường dẫn đã pin, SHA khớp hồ sơ nguồn. Ghi chú trước đây về thiếu archive đã được đính chính bằng [evidence batch](../../artifacts/reports/data-expansion-20261006/candidate-batch-v5-draft.json). Bundle Git vẫn chỉ chứa summary/selection hữu hạn; chưa có shortlist mới ngoài ledger hoặc số chính xác lượng SCB chưa dùng. Không cần tải lại archive; bước tiếp theo có thể khai thác các archive đã xác minh, giữ Discuss ngoài scope.

Với Roboflow v1, 28 person/crop hiện hành đã được xem xét và 23 crop nằm trong manifest; 5 còn lại ở queue do chưa có group. Những crop khác trong nguồn không tự động là ứng viên: audit lịch sử có 3,407 ảnh, nhiều annotation unit không tương thích và thiếu metadata session/group. Chỉ xét thêm sau khi pin archive và đề xuất person-crop cụ thể; không dùng label `No cheating` thành negative.

## Sàng lọc nguồn mới

Đã sàng lọc các trang nguồn công khai, chưa tải ảnh hoặc export. Các số lượng/lớp/license dưới đây là tuyên bố hiển thị trên trang tại ngày nghiên cứu, không phải kiểm chứng archive hay quyền với từng ảnh. Bằng chứng và điều kiện được lưu trong [source research](../../artifacts/reports/data-expansion-20261006/source-research.json).

| Ưu tiên | Ứng viên | Dấu hiệu phù hợp | Điều kiện trước khi nhận |
|---:|---|---|---|
| 1 | [Classroom-monitoring-dataset](https://universe.roboflow.com/arijit-mukherjee-h4br2/classroom-monitoring-dataset), 150 ảnh, trang nêu `using_phone`, `turn_around`, `writing`; CC BY 4.0 | Khớp gần nhất với cả phone và hướng quay quanh trong lớp. | Xác minh bản gốc/consent/quyền, unit, group/session/split, completeness, trùng với các dataset khác; review lại target theo định nghĩa dự án. |
| 2 | [Classroom Student Dataset](https://universe.roboflow.com/classroom-na2vo/classroom-student-dataset), trang nêu 1,778 ảnh, 5 version và lớp `Using Phone`, `Reading`, `Writing`; CC BY 4.0 | Có vẻ rộng hơn và có nhiều loại hoạt động học tập có thể làm ngữ cảnh âm. | Pin đúng version; điều tra provenance và khả năng là bản fork/trộn nguồn; kiểm tra overlap, quyền gốc/riêng tư, frame correlation, group/split và nhãn mơ hồ. |
| 3 | [classroom phone detection](https://universe.roboflow.com/mds-workspace-nsjro/classroom-phone-detection), 200 ảnh, `person`/`cell-phones`; CC BY 4.0 | Có thể hỗ trợ candidate crop hoặc QA đối tượng phone. | Detection box không chứng minh một người đang dùng điện thoại. Chỉ dùng sau khi review gắn phone với person; cần xác minh quyền gốc, scene và trùng lặp. |

Roboflow hiển thị license theo project, nhưng terms của nền tảng cũng nói không được host lại dataset tải xuống nếu chưa có phép rõ ràng của tác giả. Do đó ưu tiên kiểm tra metadata/preview và hỏi quyền đúng scope trước khi export/nhập; giữ attribution và biến đổi nếu được chấp thuận. License dòng trang không tự chứng minh quyền tác giả, consent, quyền riêng tư hay quyền dùng mọi asset bên trong. Không upload ảnh người thật lên Roboflow/W&B/API hoặc dịch vụ ngoài.

Không đưa Discuss trở lại ứng viên. Tập đó đã bị owner loại vì annotation unit là nhóm, không tương thích person-level; task mới này không mở lại quyết định ấy.

## Kế hoạch thực hiện theo hướng owner đã duyệt

1. Chốt một đợt nguồn hiện có trước: dùng archive SCB hiện có đã xác minh, sinh pool candidate có provenance/hash, loại duplicate, chọn một batch review hữu hạn qua heuristics theo target × source × scene. Người duyệt xác nhận từng target/crop cần thay đổi; unknown tiếp tục là unknown. Không áp quota lớp nguồn.
2. Cùng lúc thẩm định ưu tiên 1 qua metadata/điều khoản chính thức. Bước này đã mở, kết quả còn thiếu quyền/provenance/version; dừng nhập nguồn liên quan và tổng hợp TBD. Việc gửi liên hệ bên ngoài cần chỉ dẫn riêng; chưa tự thay nguồn.
3. Sau khi có candidate, tạo draft pointer v5 từ parent v4 theo approval mới nhất. Đã tạo [pilot_b_expansion_v5_draft.yaml](../../configs/datasets/pilot_b_expansion_v5_draft.yaml), đề xuất tên `pilot-b-20261006-v5`, tham chiếu batch 28 hồ sơ review-only hiện có đã kiểm hash. Chưa có group mới: split_version=null, chưa có package/release/training; tên dự kiến v1 trước đây được thay bằng v5 theo yêu cầu owner. Chỉ import approval có source/crop/hash cụ thể khi owner nghiệm thu release.
4. Lập split mới theo **scene/session/person group** bằng metadata hoặc evidence thị giác được review. Không giữ split cũ theo crop; không tách các bản gần nhau. Nếu không có group evidence, giữ record ở review-only và báo không đủ điều kiện đánh giá.
5. Tạo tập phát triển nội bộ để chọn model/threshold nếu cần; tạo holdout độc lập từ session/camera/source/capture khác để đánh giá một lần theo protocol định trước. Không dùng lại test E001 vì đã quan sát. Với ảnh có source confounding, báo metric theo nguồn/nhóm và thiếu support thay vì gộp che khuất vấn đề.
6. Trước khi chạy experiment tiếp theo, chủ repository nghiệm thu version, labels, group/split, scope/quyền và kế hoạch đánh giá; model/config/metric chấp nhận phải có quyết định thí nghiệm riêng. Không huấn luyện trong bước tạo dataset.

**Chưa chốt quota, tỷ lệ nguồn, cỡ holdout hoặc ngưỡng promotion.** Cần biết số group độc lập và support label sau candidate review; owner nghiệm thu thiết kế dựa trên bằng chứng đó. Dataset holdout dự kiến phải là bối cảnh mới được thu theo policy đã duyệt hoặc nguồn độc lập có quyền rõ; không thể gọi các crop còn lại trong v4 là real-world holdout.

## Quyết định owner đã duyệt ngày 2026-10-06

1. Duyệt hướng hai luồng SCB/RF hiện có + thẩm định nguồn mới.
2. Cho phép mở thẩm định metadata Classroom-monitoring-dataset.
3. Cho phép tạo draft dataset pointer v5 sau khi có candidate; pointer đã được tạo với batch khởi đầu 28 review-only, không phải release.
4. Giữ semantics `phone_use`, `looking_around`, mask `unknown`; Discuss tiếp tục loại.

Bằng chứng: [owner-approval.json](../../artifacts/reports/data-expansion-20261006/owner-approval.json). Membership/nhãn/quyền/group/split/release mới và experiment tiếp theo vẫn cần nghiệm thu riêng. Không hỏi lại approval hướng.

## Nguồn tham khảo

- Roboflow, [Classroom-monitoring-dataset](https://universe.roboflow.com/arijit-mukherjee-h4br2/classroom-monitoring-dataset): 150 ảnh/lớp/license hiển thị.
- Roboflow, [Classroom Student Dataset](https://universe.roboflow.com/classroom-na2vo/classroom-student-dataset): số ảnh, version, lớp và license hiển thị.
- Roboflow, [classroom phone detection](https://universe.roboflow.com/mds-workspace-nsjro/classroom-phone-detection): 200 ảnh/person và cell-phones.
- Roboflow, [điều khoản sử dụng](https://roboflow.com/terms): quyền nội dung public/private và giới hạn re-host dataset tải xuống.
- Yang, [SCB-Dataset5 paper](https://arxiv.org/abs/2304.02488): công bố 7,428 ảnh/20 lớp cho dataset nghiên cứu; con số này không được coi là thống kê ba archive SCB owner đã cung cấp.
- Open Images, [README chính thức](https://github.com/openimages/dataset/blob/main/READMEV1.md): metadata có URL/license theo ảnh và cảnh báo người dùng tự xác minh license ảnh. Nguồn này không được xếp ưu tiên vì nhãn vật thể/image-level không trực tiếp giải quyết thiếu nhãn hành vi person-level.


## Hoàn tất staging R2 sau nghiệm thu

Owner đã duyệt toàn bộ proposal R2 cho staging review-only và xác nhận toàn quyền sử dụng các dataset đang dùng. Trạng thái quyền/nhãn chờ duyệt ở các phần lịch sử phía trên được thay bằng quyết định này; không yêu cầu lại bằng chứng quyền.

[Bàn giao staging](../../artifacts/reports/data-expansion-staging-20261006-r2/README.md), [pointer](../../configs/datasets/pilot_b_expansion_v5_r2_staging.yaml): 72 record mới, 61 crop review_only, 11 excluded; nhãn theo hash đã duyệt, 11 quan hệ cảnh được lưu, unknown vẫn mask 0. Kiểm source/label 72 mẫu, pixel/hash 61 crop, pins/schema và parent payload PASS. V4/queue28 giữ nguyên.

Task mở rộng tới staging đã hoàn tất. Release hợp nhất/split/training là bước tiếp theo cần protocol và nhóm hoàn chỉnh, chưa tự phê duyệt. Classroom-monitoring hoàn tất thẩm định metadata theo phạm vi đợt này; chưa nhập media/version, không giữ câu hỏi quyền làm blocker.

## Classroom v2 — cập nhật 2026-10-07

Owner đã cung cấp ZIP/version2; nhánh nguồn mới đã tiếp tục qua tiếp nhận raw, audit150 ảnh/750 bbox và review24 crop. [Báo cáo nghiệm thu](../../artifacts/reports/classroom-v2-20261007/README.md) cùng config/hash/evidence đã hoàn tất; verification PASS.24 proposal target/crop và đề xuất nhóm gộp150 ảnh chờ nghiệm thu. Không dùng split nguồn như nhóm độc lập. Theo yêu cầu mới nhất, dừng trước staging Classroom; quyền sử dụng không phải blocker.

## Classroom v2 đã nhập staging theo approval

Owner đã duyệt24 crop/nhãn và nhóm150 ảnh. [Staging Classroom](../../artifacts/reports/classroom-v2-staging-20261007/README.md) hoàn tất,24 record review_only, group CM-V2-SCENE-01, verification PASS. Snapshot proposal trước approval giữ nguyên. Nhóm Classroom phải ở cùng một split khi xét release; chưa chọn split, membership hợp nhất hoặc train E002.

## Release v5 local — 2026-10-07

Owner đã duyệt membership/split của [proposal v5](../../artifacts/reports/pilot-b-v5-proposal-20261007/README.md). [Release v5](../../artifacts/reports/pilot-b-v5-release-20261007/README.md) accepted tại data/processed/pilot-b/pilot-b-20261007-v5; [config](../../configs/datasets/pilot_b_release_v5.yaml).208 ledger/104manifest(80train/13val/11test),93review_only/11excluded,197crop; verification PASS. Train chỉ đọc manifest, không glob crops. V4/staging bất biến; không chạy E002 hoặc final test từ approval dataset. Chưa upload/commit/push.
