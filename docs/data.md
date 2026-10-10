# Đặc tả dữ liệu và kết quả nghiên cứu

## 1. Mục đích, trạng thái và phạm vi

Đọc tài liệu này khi làm task tìm nguồn, audit, annotation/crop, group/split, release hoặc loader. Nội dung gồm contract đang chạy, nghiên cứu đã thực hiện, kết quả accepted và việc còn thiếu; không cần mở các báo cáo lịch sử để hiểu hướng làm tiếp. Đối chiếu đến **2026-10-10** từ actual manifests/ledgers, owner approvals, audit nguồn và audit v7/E004.

Hiện có bốn package classifier B v4–v7. V7 đã accepted cho `local_classifier_research`; chưa cho phép train E004, inference test mới, upload/redistribution hoặc remote DVC. Không nguồn nào đã cung cấp holdout phòng thi độc lập được nghiệm thu. Raw/interim lịch sử nằm trong archive; canonical processed packages vẫn ở repo local. Nguồn đã audit không đồng nghĩa toàn bộ nhãn/payload được chấp nhận cho training.

## 2. Unit và semantics đã chốt

ADR-011/012/013/018 Accepted: mỗi mẫu là **một person anchor và context crop đã review**. Thứ tự hai target cố định `[phone_use, looking_around]`; có thể đồng thời positive. Không thêm lớp `normal`, `cheating` hay map tên lớp nguồn thẳng sang target.

| Target/state | Điều kiện review | Trường hợp phải giữ unknown |
|---|---|---|
| Phone positive | Điện thoại **di động** được cầm/tương tác hoặc hiện trên bàn/sách, có evidence gắn đúng anchor | Device quá mờ/che, không phân biệt mobile với vật khác, không biết thuộc người nào |
| Phone negative | Vùng tay/bàn/bằng chứng đủ quan sát và owner xác nhận absence mobile của anchor | Không có source bbox, tay khuất hoặc thiếu annotation không là negative |
| Looking positive | Hướng đầu/nhìn rõ sang người khác hoặc ngoài vùng bài làm, có context để diễn giải | Chỉ lệch đầu, cúi đọc/viết, back view hoặc hướng nhìn/vùng bài không rõ |
| Looking negative | Review xác nhận không có hành vi trên trong vùng quan sát đủ evidence | Không lấy `read/write/normal` nguồn làm ground truth |
| Normal metadata | Cả hai target negative và work context `confirmed_working` | Hai negative nhưng thiếu context vẫn normal unknown; không tạo nhãn thứ ba |

Landline có dây không tạo phone positive. Calculator/book/badge/bút không tự là mobile. Không gán phone gần nhất hoặc device người khác cho anchor. Ảnh tĩnh không chứng minh duration/event. Positive một target không tự xác nhận target kia negative. Có positive hoặc context `confirmed_other` thì `normal_review=not_normal`; đủ hai negative + working mới `confirmed_normal`, còn lại `unknown`.

Person box bao phần nhìn thấy; context có thể thêm vùng bàn/thiết bị liên quan. Không tự ước lượng cơ thể bị che, thêm padding/gaze/visibility threshold chưa duyệt. V6/v7 đã review joint person/context regions theo phiên bản crop policy cụ thể; không sửa geometry cũ cho khớp một detector chưa được chọn. Crop runtime từ video là gate riêng. Classifier crop review không yêu cầu annotate mọi người trong ảnh; nếu train detector cần completeness contract khác.

## 3. Contract thực thi và trạng thái record

Codec ở `src/ai_exam_monitoring/data/pilot_schema.py`: `schema_version=pilot-b-manifest-v1`, `target_encoding_version=pilot-b-targets-v1`. Dùng `record_from_dict`, `read_records`, `validate_records`, `write_records`; không tạo parser dict permissive song song. Field lạ, derived mask/value sai, version/evidence không hợp lệ phải bị từ chối.

| State | Value JSON | Mask | Supervision |
|---|---|---:|---|
| positive | 1 | 1 | Có |
| negative | 0 | 1 | Có |
| unknown | null | 0 | Ngoài loss/metric |

Crop U/U không vào manifest supervision. `TargetReview` có state/reason/review; known target phải pin evidence đúng crop SHA. `ContextReview` dùng `confirmed_working/confirmed_other/unknown`. `ReviewEvidence` giữ reviewer, ngày review, evidence ref và crop SHA khi review crop. Chỉ ghi người/role kỹ thuật, không danh tính sinh viên.

| Nhóm fields của `PilotRecord` | Nội dung và ràng buộc |
|---|---|
| Identity/version | `sample_id`, dataset/selection/crop-policy/schema/encoding versions; ID kỹ thuật an toàn cho filename, không tự đổi identity parent |
| Source | `SourceRef`: source ID, archive/image hashes, relative path, dimensions; label hash/line/class/split nguồn nếu có; taxonomy nguồn chỉ provenance |
| Crop | `CropRef`: anchor, person/context `PixelBox`, relative crop path/hash và crop review; XYXY integer, right/bottom exclusive, nằm trong ảnh; context chứa person region |
| Targets/context | Hai `TargetReview`, work-context review; value/mask/normal derive từ state, không fill unknown thành negative |
| Rights | License ID, attribution ref, approved scopes và owner review; scope sử dụng phải thuộc scope đã duyệt |
| Group | Leakage group ID, evidence refs/review, video/session/room/subject khi xác minh được; null không được bịa từ filename |
| Disposition/usage | Disposition `pending/approved/excluded`; usage `review_only/excluded/train/val/test`, assignment/version và lý do không đủ điều kiện |
| Acceptance/freeze | Owner decision, release review, use scope; test có freeze ref; các field này không thay owner approval thật |

`review_only` và `excluded` có split/version null. Review-only cần lý do còn thiếu; excluded cần reason và owner decision. `train/val/test` cần crop/person approved, ít nhất một target known, rights đúng scope, group đã review, release review và usage khớp split; không còn blocker. Known target/context evidence phải khớp crop hiện tại: recrop tạo SHA mới thì review cũ không tự áp dụng.

## 4. Nghiên cứu nguồn đã thực hiện và kết luận sử dụng

Các con số dưới đây là **audit đúng snapshot vào 2026-10-03–10**, không là inventory nhà cung cấp hiện nay hoặc số mẫu canonical. Khi tiếp nhận bản mới phải xác minh version/hash/terms lại; không lặp công việc đã có cho cùng snapshot và cùng scope.

| Nguồn/snapshot | Đã kiểm / phát hiện | Kết luận còn áp dụng |
|---|---|---|
| SCB ba ZIP Head/HRW/Discuss owner cung cấp | 10.138 ảnh, 8.116 SHA unique; 546 label files bị flag, 625 dòng lỗi; 961 nhóm duplicate có thành viên qua train/val nguồn; metadata video/session thiếu | Head/HRW dùng tuyển looking/negative sau relabel; Discuss đã loại theo owner. Không concat giữ split nguồn hoặc tự map TurnHead/read/write. Quyền SCB đã owner xác nhận, không hỏi lại cùng scope |
| Roboflow `Exam cheating` v1, project `exam-cheating-9iz1y-rrfsz` | 3.407 cặp; 35 dòng vượt biên rất nhỏ trong 34 file, không tự clip; 0 exact duplicate nội bộ/cross-SCB trong audit này. Unit box lẫn device/head/person, gồm UI/phụ đề/watermark; phone 120 raw/117 strict annotations không là accepted positives | Owner review queue 74 ảnh, chốt 28 person crops trên 21 ảnh: 24 phone P, 5 looking P, 1 co-occurrence, đa số target còn unknown. V4 dùng 23/28 crop sau group review. Không dùng toàn nguồn hoặc `No cheating` làm normal |
| Classroom Monitoring v2 | Acquisition/audit và owner review phục vụ v5; 24 ledger records được giữ qua các release | Chỉ membership được duyệt, không coi một project là một tập phòng/camera độc lập; lịch sử này tạo additional train, không holdout |
| Classroom Attitude v3, `classroom-attitude` | 3.573 ảnh, 16 lớp trộn object/behavior/person; 1.122 label rỗng, một dòng 9 trường; 39 lineage-name groups qua split; heuristic resize/re-export gần nguồn cũ | Tuyển person/context và hard negatives được review; empty labels không là negative, dòng sai phải quarantine/re-annotate có trace. 16 lớp không trở thành ontology dự án |
| Student Behaviour v6, `student-behaviour-detection-neazg` | 4.065 ảnh nhưng 2.469 filename lineages; blur/noise augmentation nguồn. 12.912 `Using_phone` bbox; bốn mẫu unit chỉ 9×9–36×25 pixel, không bao người. Similarity thấy nội dung SCB được resize/re-export | Dựng lại person crop/attribution. Nhiều bbox/augmentation không là nhiều tình huống độc lập; không nhập Discuss qua project khác hoặc coi tên mới là nguồn mới |
| Exam Cheating v2, `exam_cheating-keaor` | 772 ảnh/4 lớp; 57 nhóm exact/RGB duplicate với RF v1, 2 nhóm exact qua split nội bộ; video/phim/subtitles lặp; upstream test chỉ 3 `Use_phone` bbox | Bổ sung phần mới có giá trị sau group review; không dùng upstream test làm holdout hoặc nhập `Cheat_paper` thành target |
| FPI-Det | Đầu tiên audit metadata/code; sau đó audit ZIP đủ 22.879 ảnh (18.800/1.730/2.349), 460 label rỗng, 62 SHA duplicate groups, 1 qua val/test; 1.357 dòng bị validator từ chối trong 1.261 file, gồm 242 dòng sai field count | Owner chốt **ngoài membership v6 chính**. Còn annotation/person attribution/semantics/rights chưa giải quyết; không tự sửa/tách/clip nhãn hoặc train từ CSV đánh giá |
| COCO train 2017, Open Images train prefix, Commons/public video | Tuyển/review chọn lọc cho v7; lưu creator/title/source/license/changes và source provenance của từng record; không dùng eval pool để bù train | Chỉ accepted subset local; ảnh phụ trợ không thay domain thi hoặc independent holdout. Blocker rights/lineage vẫn ở ngoài supervision |

Source pin quan trọng của audit đầu: RF v1 ZIP SHA `70060bfe7d65dedcca6a72aaac423c95f402369eec08563b24ae8d962e666eed`; SCB Head `a0fdd6637fb286cbc5d3de83c09f4143686eab0da4d92e4d8007b6b14b3ca828`, HRW `46619af0c0dea011b09b8d50f4c0578420b881b5154e9d11f0447760193a208d`, Discuss `63aa029d04f8e9d5027cc2491aeca10785678750bdae4351835bfceaab95187f`. Không thay ZIP mới cùng tên cho snapshot cũ. Các ZIP đầu do owner cung cấp từ Downloads; archive repo lưu phần input còn giữ, không mặc định có toàn bộ upstream ZIP.

FPI có hai vấn đề cần nhớ khi mở lại: annotation face/phone không cung cấp person bbox/association; CSV 4.079 tên chỉ phủ val/test, 0 tên train. Paper/code nói numeric 0 là phone-use nhưng join CSV/boxes gợi ý chiều ngược; chưa đủ bằng chứng để đảo nhãn. Active-use semantics cũng khác mobile presence đã chốt. MIT repo không tự xác minh rights từng ảnh/DataFountain terms. Không copy benchmark inner-join hoặc rule có face+phone vào production.

Cross-source v6 đã sàng lọc dHash 64 khoảng cách ≤4: 964 Classroom gần RF, 1.359 Student gần SCB, 358 Exam gần RF. Đây là **cờ review**, không số duplicate được xác nhận hoặc threshold independence Accepted. Chín cặp minh họa xác nhận resize/re-export ở những cặp đã xem; không suy mọi cặp ngoài ngưỡng đều độc lập. Các flag liên quan validation/test lịch sử phải quarantine hoặc owner chốt whole-family trước tuyển train.

## 5. Các release đã accepted và vì sao thay đổi

Package nằm dưới `data/processed/pilot-b/`; config tương ứng `configs/datasets/pilot_b_release_v4.yaml` đến `v7.yaml`. Manifest là danh sách supervision; ledger giữ tất cả decisions. Không train bằng cách glob thư mục crops.

| Release | Package suffix | Train / val / test | Manifest | Ledger | Review-only / excluded | Kết quả chính |
|---|---|---|---:|---:|---|---|
| v4 | `pilot-b-20261005-v4` | 60 / 13 / 11 | 84 | 112 | 28 / 0 | RF 28 + SCB84 reviewed; 16 group của used records; 9 normal metadata; local accepted, test freeze |
| v5 | `pilot-b-20261007-v5` | 80 / 13 / 11 | 104 | 208 | 93 / 11 | Train +20 sau review nguồn cũ/Classroom Monitoring; giữ val 13/test 11 và evaluation identity parent |
| v6 | `pilot-b-20261007-v6` | 317 / 50 / 11 | 378 | 498 | 93 / 27 | Nhập subset reviewed SCB/Student/Classroom Attitude/Exam; 471 crop files; bảo toàn 104 used parent và test 11; thêm validation development, không holdout |
| v7 | `pilot-b-20261010-v7` | 689 / 49 / 11 | 749 | 900 | 122 / 29 | 871 crop files; parent corrections +375 new train; whole-family/rights local accepted; không thêm validation mới |

V4/v5/v6 có DVC pointers riêng; v7 giữ local package/release pointer và có snapshot trong archive, chưa có `.dvc` riêng. Chỉ v4 có remote-storage approval/round-trip đã kiểm; không suy quyền remote cho version/model khác. Budget v1 28 RF +84 SCB (28 TurnHead/28 read/28 write) là lựa chọn thiết kế ADR-013 lịch sử, không quota mỗi release.

V7 xuất phát từ 498 parent records và pool 402 crop bổ sung. Final pool: 375 new train, 21 U/U review-only, 5 blocker review-only, 1 evaluation-family excluded. Bản preparation 694 train là upper bound cũ; accepted đúng **689**, không lấy proposal làm canonical.

Owner đã review đủ 12 cell được audit E003 nêu. Trong v7: `V6-CA-041` phone U và rời val; `EXP-SCB-002` looking N; `EXP-RF-014` excluded vì crop/text conflict; `EXP-SCB-032` và `SCB-turnhead-023` U; `SCB-turnhead-020` N; các `SCB-turnhead-007/009/012/019/021` và `V6R2-MP-059` giữ P theo review. Tổng 49 parent reviews dẫn tới 9 record changes: 6 target corrections, 2 domain notes, 1 exclusion. V6 trên đĩa giữ nguyên; correction chỉ trong v7, không mở lại nhãn đã được chốt thiếu bằng chứng mới.

Bốn rights blockers `V7-OE-S005-A01/S020-A01/S027-A01/S034-A01` vẫn review-only do landing/metadata license chưa đủ ở thời điểm chốt; `V7-OE-S080-A01` còn boundary liên quan parent val. Crop/label approved không xóa blocker quyền/group. Source reserve ngoài pool giữ lý do, không tự tuyển lại để bù quota.

## 6. Coverage hiện tại và giới hạn đánh giá

P/N/U = positive/negative/unknown. Các số dưới đây tính từ accepted v7 manifest, không cả ledger/crop folder.

| Split | Phone P / N / U | Looking P / N / U | Fully-known | Registered groups |
|---|---|---|---:|---:|
| Train 689 | 233 / 184 / 272 | 210 / 277 / 202 | 215 | 375 |
| Val 49 | 16 / 20 / 13 | 17 / 12 / 20 | 16 | 14 |
| Test 11 | 2 / 2 / 7 | 2 / 7 / 2 | 2 | 3 |

Toàn ledger 900 thuộc 449 conservative components; manifest 749 có 392 groups. Exact image/crop/group không qua nhiều split đã được kiểm. **Không có proof independence mới** theo person/session/room; group IDs và SHA unique không chứng minh độc lập. Metadata subject/session/room/video của train/val còn null.

Train v6→v7: 317→689; fully-known 96→215 (30,3%→31,2%), 474/689 vẫn chỉ known một target. Bốn tổ hợp fully-known PP/PN/NP/NN từ 16/3/23/54 thành 36/16/32/131. Largest group Student 91 giữ nguyên, tỷ trọng giảm 28,7%→13,2%; không phải 91 tình huống mới.

Source confounding còn: train v7 SCB Head looking 53 P/12 N; HRW 3 P/81 N; Classroom Attitude phone 83 P/16 N; Student phone 42 P/35 N, looking 44 P/38 N. Cân bằng P/N toàn tập không loại lệch trong từng nguồn. Đây là rủi ro distribution, chưa phải kết luận causal model học shortcut.

375 new train gồm 196 `classroom_or_exam_context`,127 `auxiliary_out_of_exam`,52 context khác/pending; tag classroom không chứng minh CCTV/phòng thi/session mới. Có 22 raw P/N pairs trên 19 exact-source images (phone 5/5 images; looking 17/16 images), không 22 independent sessions. Trong 162 pair R5 lịch sử chỉ 138 vẫn đúng P/N và cả hai train: 132 source-context, 5 same-image, 1 same-scene; không cộng các bảng pair có overlap.

QA input 224/pixel equality đã PASS; không đồng nghĩa phone nhỏ nhìn rõ hoặc model đã học. 119 finding lịch sử chỉ 104 khớp current train crop SHA (94 clear/10 ambiguous); recrop SHA khác không kế thừa review 224 cũ. Chưa có taxonomy đo/pin đầy đủ phone context/visibility/own-workarea/domain/camera-session cho toàn 375 new train.

Val 49 không có mẫu mới: từ val 50 E003 sau correction/exclusion, 14 group, hai group 21+10 crop chiếm 63,3%. Phone 16 P chỉ 4 groups, looking 17 P chỉ 6 groups. Test 11 đã dùng E001, support nhỏ và không quyền inference mới. Không chuyển train sang val/test để vá thiếu đánh giá nếu chưa có policy/version approval.

## 7. Workflow dữ liệu cho task tiếp theo

1. **Chốt mục tiêu hữu hạn:** failure mode/domain/target cần cải thiện, scope local và vai trò train/development/holdout. Dùng nghiên cứu/coverage phía trên, không audit lại mọi source hoặc đặt quota tùy ý.
2. **Tìm input hiện có:** xác minh snapshot/hash và phần archive còn giữ; nếu thiếu toàn payload nguồn thì ghi rõ, tiếp nhận/reacquire đúng version/terms khi được phép. Raw bất biến; không chạy code upstream.
3. **Audit cấu trúc:** decode, image/label pairing, geometry/class IDs, duplicates bytes/RGB, lineage/near-duplicate cross-source. Không sửa raw hoặc dùng filename/hash để invent session.
4. **Tự động shortlist và draft review:** đề xuất anchor/person/context, hai state/reasons, rights/provenance/group flags; dùng heuristics/công cụ đã có. Model/pretrained mới cần scope/license decision. Owner nghiệm thu batch và ngoại lệ, không phải tự vẽ mọi bbox.
5. **QA source → crop → model input:** đúng anchor, geometry/attribution, evidence hiển thị còn đủ tại input size, difficult negatives/co-occurrence; U giữ mask 0. Review gắn SHA exact crop.
6. **Group trước split:** cùng image/video/session/augmentation/scene-family cùng ranh giới; thiếu evidence giữ review-only/quarantine. Whole-family không tự chứng minh independent holdout.
7. **Owner chốt membership/rights/assignment:** eligibility đầy đủ mới vào train/val/test. Giữ parent evaluation identity; đổi nhãn/crop/assignment tạo version mới và report delta riêng.
8. **Đóng package mới:** ledger, used manifest, selection/provenance, split assignment, release metadata/card, coverage/leakage/QA reports, approval/config/hash, test freeze và checksums. Exporter `pilot_package.py` và codec là logic tái dùng; không tạo một script cho mỗi vòng review.
9. **Kiểm và bàn giao:** schema/usage/pins, exact inventory/crop bytes, cross-split leakage, parent preservation/test serialization và deterministic rebuild theo scope. Report limitations và quyền storage; không reseal package cũ hoặc tự train sau release.

`train/val/test` assignment phải tường minh/versioned, không chia lại random ratio/seed trong loader. Unknown không tham gia loss/metric, test không dùng cho tuning/quota/selection. Holdout có package/protocol riêng, không nhập vào train.

## 8. Contract công cụ audit nguồn đang dùng

### Đường thực thi cho expansion/release mới

Không có lệnh “tạo v8” đã được duyệt. Agent bắt đầu bằng một task có mục tiêu/failure mode và parent version, rồi lập bảng inputs → công cụ → outputs → checks theo bảng sau. Không cần dựng lại quy trình từ đầu, cũng không chạy config v7 với tên mới.

| Bước | Công cụ / nơi tái dùng | Input → output và kiểm bắt buộc |
|---|---|---|
| Audit nguồn | Active `data.audit`, `data.validate_labels`, `data.overlay` | Snapshot đã pin → audit/overlay; kiểm decode, pairing, bbox, taxonomy; không tự repair raw |
| Fingerprints/triage | Active `image_similarity.difference_hash`, `nearest_by_split` | Image metadata → nearest candidates; kết quả chỉ là cờ review, không auto group |
| Shortlist/anchor/context | Git `ab34b32`, `pilot_selection.inventory_anchors/select_round_robin`, `pilot_source_candidates.context_proposal/build_candidates` | Source audit + scope/budget được duyệt → candidates có provenance; kiểm anchor/device attribution, không auto label |
| Targeted screening | Git `ab34b32`, `pilot_targeted_expansion.collect/build_screening` | Cached parent/evaluation fingerprints + source pins → screening; `validate_fingerprints` chặn thiếu evaluation evidence; không đọc test predictions |
| Batch review | Git `ab34b32`, `targeted_review_package.build/check_pairs` | Draft selection → crop/contact sheet/review metadata; code lịch sử có ID/bucket v7 cố định, chỉ dùng tham khảo hoặc chạy đúng phiên bản gốc |
| Owner groups | Git `ab34b32`, `pilot_owner_groups.import_group_decisions/ingest_owner_groups` | Explicit reviewed group decisions → records; không dùng proximity/filename để tự xác nhận independence |
| Canonical records | Active `pilot_schema.record_from_dict/read_records/validate_records` | Decisions có reviewer/scope/crop SHA → strict `PilotRecord`; U giữ mask 0, blockers ngoài supervision |
| Export | Active `pilot_package.build_pilot_package` | Records + source roots + crop inputs + selection + metadata + exact expected IDs → package mới; hàm không tự cấp approval hoặc chọn split |
| Nghiệm thu | Active `integrity.verify_payload`, schema, parent/evaluation comparisons và owner receipt của version mới | Exact inventory/checksums, coverage, delta, leakage, parent preservation → quyết định release; không sửa receipt cũ |

Các module lịch sử được xác định ở Git commit trên, không cam kết tất cả đều nằm trong ZIP. Dùng `git show ab34b32:src/ai_exam_monitoring/data/<module>.py` để đọc đúng file, xem imports trước tái dùng. Không import code trực tiếp từ archive trong production. Nếu cần chức năng cho version mới: chuyển phần tổng quát vào module theo trách nhiệm (`selection`, `review`, `groups` khi thực sự cần), truyền variables bằng config và đưa regression fixtures liên quan trở lại; bỏ hard-code ID/quota của v7 chỉ trong implementation mới. Không khôi phục cả cây công cụ chỉ để có nhiều CLI, không sao chép module thành `v8_r1/v8_r2`.

Exporter nhận `records`, `output_dir`, `source_roots`, `crop_inputs`, `selection_rows`, `metadata`, `expected_sample_ids`; schema và fixtures ở `tests/test_pilot_package.py` là mẫu thực thi. Output phải mới; source/crop SHA phải đúng review. Acceptance layer của release mới là công việc của task release, cần explicit approval/config, parent delta và test-preservation checks; exporter PASS chưa là owner acceptance. Builder `v7_release_acceptance` giữ vai trò lịch sử, không là acceptance layer chung.

Trước coding, TASK ghi rõ bước nào dùng active API, bước nào cần phục hồi/thích nghi, test nào bảo vệ behavior và output nào sẽ giữ. Sau task cập nhật kết quả vào §5/§6/§9 tương ứng; evidence máy đọc và vòng đời revisions theo development §5. Không tạo thêm bộ hướng dẫn expansion song song.

Generic CLI `python -m ai_exam_monitoring.data.audit` và `.overlay` bắt buộc `--dataset`, `--images`, `--labels`, `--source-names`; subtrees tồn tại dưới dataset root, không auto-detect. Layout `images/{split}` + `labels/{split}` có thể audit chung; layout `{split}/images` + `{split}/labels` audit từng split rồi đối chiếu duplicate riêng.

Pairing theo relative path bỏ extension, case-sensitive. Same stem khác thư mục là khác key; nhiều extension cùng key ambiguous, không overlay. Images JPG/JPEG/PNG/BMP/WEBP; label TXT trừ `classes.txt`/`README*.txt`. Names JSON ID→name hoặc YAML `names` mapping ID→name; không nhận list để tự gán ID. Không tự chuyển source IDs thành targets.

Audit schema v2 giữ input/layout/names, decode/resolution, missing/orphan/ambiguous, invalid files/lines, empty labels, class counts, normalized bbox stats, exact duplicate SHA và valid samples. Label file lỗi không đóng góp partial statistics; orphan hợp lệ có thể vào class count nhưng pixel stats chỉ dùng unique decoded pairs. Empty/missing annotation không xác nhận negative. Near duplicate/license/semantics/group acceptance cần QA riêng.

Overlay dùng `--output-dir`, `--limit` (font tùy chọn); lấy N valid pairs đầu theo path và ghi manifest/audit, không gọi là mẫu đại diện/phân tầng. Dùng tọa độ pixel gốc, không tự xoay EXIF hoặc repair annotation. Output ngoài nguồn/raw; overlay từ chối directory đã có nội dung. Exit 0 pass checks thực hiện, exit 1 lỗi cấu trúc/không xuất mẫu, exit 2 input/output/arguments không hợp lệ.

## 9. Holdout research đã làm và việc còn mở

Ngày 2026-10-08 đã thẩm định metadata nguồn công khai theo yêu cầu owner; chưa có holdout payload/package Accepted. Kết quả này là snapshot nghiên cứu, phải kiểm availability/terms/version khi tiếp nhận thực tế.

| Nguồn | Đã biết | Kết luận/bước tiếp |
|---|---|---|
| CDED-7 / classroom-distraction-tracker | Tác giả mô tả 7 original videos; derived labels Focused/Distracted không trùng targets. Terms nghiên cứu giới hạn, không surveillance/profiling/redistribution raw tùy ý; raw chưa ở local | Ưu tiên thẩm định acquisition/use scope benchmark, original videos/provenance/phone support; không map Distracted→looking hoặc gọi 7 video là 7 independent groups |
| POCO | Công bố 1.903 images/137.960 instances/10 classes; link sample, quyền research riêng, không chia sẻ dataset | Dự phòng có điều kiện; cần đủ payload/terms/two-target evidence và lineage |
| Exam cheat detection ECD | Provider metadata 3.119 images/7 classes/CC BY 4.0, chưa raw/version/source provenance được xác minh | Kiểm re-export/overlap với nguồn đã dùng trước chọn holdout |
| Hashemite paper-based exam actions | Bài báo mô tả 8 actors/cảnh phòng thi; chưa payload/version/license dataset usable | Tiếp tục availability nếu cần; license paper không thay dataset permission |
| MSU OEP | Remote-exam webcam/wearcam/audio/phone, camera khác phòng thi nhiều người | Có thể challenge phone phụ, chưa primary holdout hai target |
| BNU SCB / EduNet / Invigilo | Chưa có raw release/terms/lineage đủ kiểm ở thời điểm nghiên cứu; EduNet cần form, có nguồn YouTube và tự quay | Không coi public repo/code/paper là public usable dataset; không gửi form/email thay owner nếu chưa được yêu cầu |

Tiếp nhận holdout: pin source/version/terms/SHA → quarantine lineage/cross-source overlap → crop/two-target QA không cho reviewer xem candidate scores → sampling/protocol chốt trước prediction → package riêng/freeze/access receipt. Không lấy test 11, val 49/50, upstream test hoặc random frame split gọi là independent holdout. Không cân lại/loại mẫu khó sau thấy metrics.

Việc ưu tiên hiện tại: (1) đo targeted matrix thật cho 375 new train và phân biệt primary/auxiliary/parent variants; (2) đề xuất policy new-development whole-groups + holdout độc lập với đủ rights/provenance/P/N support; (3) freeze comparator/recipe/metric theo training spec. Owner chốt high-level; không tự hạ gate hoặc ép thêm crop cho đẹp số.

## 10. Vị trí bằng chứng khi cần kiểm/tái lập

Số liệu accepted lấy từ `data/processed/pilot-b/<package>/manifest.jsonl`, `review-ledger.jsonl`, `reports/coverage.json`, `release.json`, `checksums.sha256`; acceptance/provenance ở `artifacts/reports/pilot-b-...release.../`. Audit hiện hành v7/E004 ở `artifacts/reports/E004-v7-fit-audit-20261010/` có measured audit, pair/comparator proposals và cached-score illustration. Agent chỉ mở đúng JSON khi task cần IDs/pins/chi tiết máy đọc.

Nghiên cứu SCB/RF/FPI/v6/v7 gốc còn trong snapshot history hoặc Git `ab34b32`; kết luận cần dùng đã được tích hợp phía trên. Một số report R7/R8/source-funnel có mismatch seal lịch sử, không được reseal hoặc lấy yield/proposal đó thay accepted v7; kiểm exact input khi tái sử dụng. Truy/restore theo development spec, không bắt agent đọc archive để hiểu domain. Bytes raw/upstream đã bị xóa ở cleanup đầu không tự trở lại bằng Git; kiểm inventory thực tế trước hứa reuse/rebuild nguồn. Config/receipt/sealed originals không sửa để hợp thức hóa tài liệu mới.
