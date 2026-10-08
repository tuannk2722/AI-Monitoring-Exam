# Đề xuất nguồn cho pilot B v6 — 2026-10-07

Trạng thái: **đã kiểm payload bốn ZIP mới; đề xuất nguồn, chưa phải release accepted**. Owner: chủ repository. Người nghiên cứu: Codex. Release hiện hành vẫn là `pilot-b-20261007-v5`.

## Kết luận đề xuất

V6 nên mở rộng **số người/cảnh độc lập đã được review**, có cả positive và negative trong cùng nguồn. Đề xuất giữ SCB Head/HRW làm nền; ưu tiên tuyển phần bổ sung có phone/person rõ từ Student Behaviour và Classroom Attitude sau dựng lại crop, loại overlap; dùng Exam Cheating cho các trường hợp bổ sung có giá trị. Không nguồn mới nào đủ điều kiện nhập nguyên bbox. **FPI chưa nhập đợt v6 chính**: cần một nhánh xử lý annotation và person attribution trước. Không cộng nguyên các ZIP rồi train.

Đây là kết luận về thành phần nguồn và cách chuẩn bị. Số crop, membership, group và split v6 chưa được nghiệm thu. Yêu cầu “chốt v6” không được biến thành nhãn/split đã duyệt khi chưa có bằng chứng theo AGENTS.md và hợp đồng pilot B. Config [đề xuất](../../configs/datasets/pilot_b_v6_source_proposal_20261007.yaml) cố ý không có số lượng/split giả.

## Phạm vi kiểm tra

Đã đọc trực tiếp ba ZIP mới trong Downloads do owner cung cấp, xác nhận project/version từ `data.yaml`, hash toàn ZIP, đọc ảnh/annotation, decode toàn bộ ảnh, kiểm từng dòng bằng validator YOLO canonical, kiểm orphan/missing label, SHA byte và RGB sau decode. Đọc thêm ZIP RF cũ để đối chiếu. Không thực thi mã upstream. Bảng dưới là **số ảnh nguồn**, chưa phải số person crop hoặc mẫu train của dự án.

| Nguồn thực tế | Train / valid / test nguồn | Tổng ảnh | Lớp trong ZIP | Preprocess và augmentation theo README ZIP |
|---|---:|---:|---:|---|
| Classroom Attitude v3 | 2.566 / 665 / 342 | 3.573 | 16 | Auto-orient, stretch 512×512; không augmentation |
| Student Behaviour v6 | 3.192 / 581 / 292 | 4.065 | 12 | Auto-orient, stretch 640×640; 2 biến thể/ảnh train, blur và noise |
| Exam Cheating v2 | 679 / 63 / 30 | 772 | 4 | Auto-orient, stretch 640×640; không augmentation |

Cả ba ZIP không thiếu/orphan label, không lỗi decode ảnh. Điều này chỉ chứng minh cấu trúc đọc được, **không chứng minh nhãn đúng**. Annotation counts dưới đây đếm dòng hợp lệ; lớp trong cùng ảnh/người không được coi là mẫu độc lập. Bằng chứng đầy đủ: [payload audit](../../artifacts/reports/pilot-b-v6-source-research-20261007/roboflow-payload-audit.json).

Trang project công khai và export không đồng nhất: Classroom giới thiệu 4.079 ảnh/9 lớp nhưng v3 có 3.573 ảnh/16 lớp; Exam giới thiệu 1.017 ảnh/5 lớp nhưng v2 có 772 ảnh/4 lớp. Student project có 2.471 ảnh, export v6 4.065 ảnh; ZIP cho 2.469 nhóm tên trước `.rf.`. Không kết luận hai ảnh còn lại bị lỗi vì chưa có lịch sử generation. Trang Student v6 nêu saturation ±25%, README ZIP chỉ nêu blur/noise: lưu cả hai bằng chứng, không tự khẳng định saturation đã chạy.

## 1. Classroom Attitude v3

Nguồn: [project](https://universe.roboflow.com/nguyenducmanhs-workspace/classroom-attitude), [version 3](https://universe.roboflow.com/nguyenducmanhs-workspace/classroom-attitude/dataset/3). YAML xác nhận đúng workspace/project/version và CC BY 4.0.

Class ID thực tế: 0 Cheating; 1 CheatingDevice; 2 Exam Device; 3 Leaning Down; 4 Leaving Seat; 5 Looking around; 6 Phone; 7 Phone use; 8 Sleeping; 9 Standing; 10 Turning head; 11 Turning_Around; 12 Walking; 13 cell-phones; 14 invigilator; 15 person.

Có 1.386 bbox `Phone use`, 3.570 `Looking around`, 390 `Turning_Around`, 4 `Turning head`; `Phone` chỉ 7 bbox. Ngoài ra 1.135 `cell-phones` và 1.103 `person`. Đây là ontology trộn đối tượng/hành vi/vai trò. Không gộp `Phone`, `cell-phones`, `CheatingDevice` vào positive person-level bằng phép đổi tên.

Có **1.122 file nhãn rỗng** (787 train, 216 valid, 119 test). Không biến chúng thành negative: có thể thiếu annotation hoặc là ảnh nền, phải xem người và ngữ cảnh. Một dòng train có 9 trường, không đúng định dạng detection 5 trường; cần cách ly/re-annotate, không cắt lấy 5 trường đầu. Chi tiết tên/dòng ở audit.

Có 3.500 nhóm tên gốc, **39 nhóm tên xuất hiện qua split**. Đây là cảnh báo lineage dựa tên, chưa đồng nghĩa 39 nhóm duplicate đã xác nhận. Ảnh mẫu train cho thấy cả ảnh lớp học nhiều người, camera phòng thi và crop học sinh; có nhiều biến thể cùng cảnh. Nên tuyển người/cảnh thực sự mới và hard negatives, không nhập cả 3.573 ảnh.

## 2. Student Behaviour v6

Nguồn: [project](https://universe.roboflow.com/mywork-lkwz4/student-behaviour-detection-neazg), [version 6](https://universe.roboflow.com/mywork-lkwz4/student-behaviour-detection-neazg/dataset/6). YAML: CC BY 4.0.

Class ID: 0 Using_phone; 1 bend; 2 book; 3 bow_head; 4 hand-raising; 5 phone; 6 raise_head; 7 reading; 8 sleep; 9 turn_head; 10 upright; 11 writing.

Có 12.912 bbox `Using_phone`, 3.361 `turn_head`, 5.070 `phone`. Toàn bộ dòng qua validator hình học/ID. 2.469 nhóm tên gốc gồm 1.596 nhóm train, 581 valid, 292 test; không có tên gốc chung qua split theo heuristic `.rf.`. Tuy nhiên, **không có tên trùng không chứng minh khác video/phòng/người**. Ảnh mẫu nhiều người trong cùng giảng đường, annotation head/posture/person/object chồng lên nhau; phải kiểm unit bbox khi làm person crop.

Đề xuất ưu tiên thẩm định phần còn mới vì có phone và các hành vi dễ nhầm trong bối cảnh lớp học; ưu tiên này phụ thuộc khả năng dựng crop đúng người. Chọn một đại diện phù hợp mỗi lineage để review trước; các biến thể cùng ảnh thuộc cùng group. Không cộng v5 và v6 export, không coi 12.912 bbox là 12.912 người/cảnh độc lập. Chỉ dùng bbox person/context đã kiểm; `reading`, `writing`, `bow_head`, `upright` không tự động là negative của cả hai target. Cần chủ động lấy negative cùng phòng/camera với phone positive để tránh học nền.

## 3. Exam Cheating v2

Nguồn: [project](https://universe.roboflow.com/behavior-cheating/exam_cheating-keaor), [version 2](https://universe.roboflow.com/behavior-cheating/exam_cheating-keaor/dataset/2). YAML: CC BY 4.0. Đây là nguồn khác project RF cũ của v5, nhưng **không độc lập về ảnh**.

Class ID: 0 Cheat_paper; 1 Look_around; 2 Normal; 3 Use_phone. Không có class `exam-cheating` trong export này. Có 515 bbox `Look_around`, 571 `Normal`, 166 `Use_phone`, 112 `Cheat_paper`. Phone phân bố 159/4/3 bbox train/valid/test: test nguồn có rất ít phone, không đủ để tự tuyên bố đánh giá phone đáng tin cậy. Không lỗi validator ở các dòng.

Có 482 nhóm tên gốc, 55 nhóm tên qua split. Kiểm SHA byte và RGB đều phát hiện **57 nhóm ảnh trùng giữa nguồn này và RF cũ**; **2 nhóm exact duplicate qua split trong Exam v2**. Xem [duplicate evidence](../../artifacts/reports/pilot-b-v6-source-research-20261007/roboflow-duplicates.json). Không dùng nguyên test của nguồn làm holdout độc lập.

Ảnh train mẫu có khung hình phim/video với watermark/phụ đề và cùng nhân vật/cảnh lặp; một số cảnh lớp học gần nguồn cũ. Do đó chỉ ưu tiên phần mới/các trường hợp khó hữu ích, không ưu tiên theo chữ “exam” trong tên. `Normal` phải review lại hai target, `Cheat_paper` không là target dự án; media thuộc lớp này vẫn có thể xét lại nhãn quan sát được, không suy ý định gian lận.

## 4. FPI và SCB trong quyết định tổng hợp

Báo cáo [FPI/SCB trước đó](fpi-scb-research-20261007.md) giữ nguyên như snapshot lịch sử. Lần này đã tìm được `reorganized_phone_dataset_yolo.zip`, kiểm trực tiếp **22.879 ảnh**: 18.800 train, 1.730 val, 2.349 test. Không lỗi decode/missing label; 460 file nhãn rỗng. Có 62 nhóm trùng SHA, trong đó một nhóm val/test. Chi tiết [FPI payload](../../artifacts/reports/pilot-b-v6-source-research-20261007/fpi-payload-audit.json) và [follow-up](../../artifacts/reports/pilot-b-v6-source-research-20261007/fpi-followup.json).

**1.357 dòng bị validator từ chối trong 1.261 file**, gồm 242 dòng sai số trường và các lỗi hình học. Một số dòng có nhiều annotation nối chung; không tự tách/cắt/sửa rồi coi là đã đúng. Có box vượt biên lớn, không thể quy hết cho sai số float. Trường `raw_class_counts` trong audit chỉ đếm token đầu mỗi dòng, **không phải tổng bbox hợp lệ**. COCO check mới đối chiếu tên/kích thước/số dòng, chưa chứng minh tọa độ và mọi bbox tương đương.

Đã xem trực tiếp bốn mẫu val có numeric CSV 0/1: có mẫu CSV 0 không thấy bằng chứng phone rõ, mẫu CSV 1 cầm phone rõ; có mẫu che khuất. Chúng hỗ trợ nghi vấn polarity từ báo cáo trước nhưng không đủ đổi hàng loạt nhãn. Không dùng CSV val/test để train hoặc chọn threshold. Annotation face/phone không cung cấp person box/quan hệ phone–person; bối cảnh đường phố khác phòng thi. **Đề xuất để FPI ngoài membership đợt v6 chính**, chỉ nhập subset phụ trợ sau sửa có truy vết, review người/nhãn/group và quyền nguồn gốc. MIT repo không tự giải quyết quyền toàn bộ ảnh nguồn.

SCB Head/HRW vẫn hữu ích cho looking và negative khó sau review. Ba ZIP SCB trước đó có 10.138 ảnh nhưng 8.116 SHA unique, 961 nhóm trùng qua split nguồn, 546 file nhãn bị flag. V5 mới dùng 49 SCB train; còn 67 SCB review_only. Không thiếu ảnh nguồn theo nghĩa đơn thuần; đang thiếu person crop/nhãn/ngữ cảnh/nhóm được nghiệm thu. Discuss vẫn loại theo quyết định hiện hành; không mở lại quyền SCB owner đã xác nhận. Lớp cúi đầu/đọc/viết không tự sinh phone negative hoặc looking negative.

## Kiểm unit bbox trực tiếp: điều kiện quan trọng trước v6

Đã cắt và xem 28 bbox train (bốn mẫu/class theo SHA, khác lineage tên; không phải sampling ước lượng tỷ lệ lỗi). Bốn Student `Using_phone` chỉ 9×9, 18×20, 36×25, 10×9 px: **không bao người**. `phone` cũng là crop nhỏ; `turn_head` chủ yếu bao đầu. `upright`/`writing` có bbox người/phần thân. Vì thế 12.912 bbox `Using_phone` không thể nhập trực tiếp thành 12.912 person crop positive. Cần ghép bằng chứng với đúng người và vùng ngữ cảnh; không dùng nearest phone–person làm nhãn accepted.

Classroom `Phone use` và Exam `Use_phone` cũng không đồng nhất unit: mẫu có bbox chỉ tay/thiết bị hoặc phần thân, bên cạnh mẫu gần person crop. Không sửa lỗi này chỉ bằng resize lên input model. Các mẫu quá nhỏ/mơ hồ phải giữ unknown hoặc loại có lý do; không bịa ngưỡng kích thước loại tự động. [Receipt và nhận xét 28 mẫu](../../artifacts/reports/pilot-b-v6-source-research-20261007/target-unit-review.json) là căn cứ để **giữ cả ba nguồn mới ở candidate** đến khi có crop/nhãn/group cụ thể.

## Kiểm overlap bổ sung sau khi có ZIP

Không có SHA ảnh mới khớp ba ZIP SCB, nhưng resize/re-encode làm SHA thay đổi. Sàng lọc dHash 64-bit lấy nearest nguồn RF cũ/SCB với khoảng cách ≤4 cho thấy 964 ảnh Classroom gần RF cũ, 1.359 ảnh Student gần SCB (1.299 HRW, 60 Discuss), 358 ảnh Exam gần RF cũ. **Đây là số cờ cần review, không phải số duplicate đã xác nhận**; mỗi ảnh chỉ lấy một nearest, kết quả phụ thuộc tập reference và không chứng minh mọi cặp khác ngưỡng là độc lập.

Đã xem chín cặp minh họa (ba/nguồn), đều quan sát được cùng nội dung cảnh/khung hình, khác resize/biến đổi. Vì vậy Student cần ưu tiên phần phone/negative thật sự bổ sung, không coi toàn bộ project là nguồn mới tách biệt SCB. Không nhập lại Discuss chỉ vì nó xuất hiện dưới tên project khác. Classroom cũng không thể được coi là nguồn độc lập với RF cũ.

Đối chiếu SHA với ledger v5 có một ảnh Exam khớp `P019-person-01`, hiện `review_only`; **không phải bằng chứng ảnh đó đã vào train/test v5**. Sàng lọc gần với ảnh nguồn ledger v5 còn flag Classroom gần ảnh val (5) và test (3); cần review group/quarantine trước khi tuyển train, không tự kết luận rò rỉ chỉ bằng dHash. Báo cáo [cross-source](../../artifacts/reports/pilot-b-v6-source-research-20261007/cross-source-triage.json) và [v5 triage](../../artifacts/reports/pilot-b-v6-source-research-20261007/v5-near-triage.json) lưu phạm vi, counts và receipts. Không thay membership/nhãn v5 từ các heuristic này.

## 5. Phương án v6 để owner chốt một lần

| Thành phần | Vai trò đề xuất | Điều kiện nhập | Quyết định của tôi |
|---|---|---|
| V5 accepted | Bảo toàn gốc và đối chứng lịch sử | Không sửa nhãn/crop hoặc membership lịch sử âm thầm | Approve |
| SCB Head/HRW | Mở rộng looking và negative khó | Hoàn tất review_only phù hợp, rồi cảnh/người mới; kiểm leakage | Approve |
| Student Behaviour v6 | Tuyển phần phone/negative còn mới, có điều kiện | Dựng person crop từ ảnh gốc; không lấy Using_phone bbox trực tiếp; deduplicate/nhóm cảnh | Approve |
| Classroom Attitude v3 | Bổ sung chọn lọc độ đa dạng/hard negatives | Loại overlap, cách ly lỗi nhãn; review nhãn rỗng | Approve |
| Exam Cheating v2 | Bổ sung chọn lọc, không làm holdout mặc định | Loại/nhóm overlap với RF cũ và phim/video | Approve |
| FPI | Tạm ngoài đợt v6 chính | Xử lý annotation/person attribution/semantics/quyền trước | Approve |

Giữ formulation B, hai target `phone_use`, `looking_around`, unknown masked. Không đổi sang train detector 16 lớp hoặc softmax cheating/normal vì bộ nguồn có nhiều lớp. Mapping chỉ là **tín hiệu chọn hàng đợi**: `Using_phone`/`Phone use`/`Use_phone` cần review phone gắn đúng người; `turn_head`/`Looking around`/`Look_around` cần review hướng nhìn và vùng bài. Giữ co-occurrence khi có bằng chứng.

Quy trình tiếp theo là tự động tạo candidate ledger có source/hash/lineage, đề xuất group trước split, chọn person/context crop rồi draft hai nhãn với lý do và unknown rõ ràng. Owner nghiệm thu gói review tổng hợp; không phải tự annotate mọi bbox trong ZIP. Chỉ sau khi có membership/group cụ thể mới chốt số lượng train/val và build pointer v6. Không đặt quota nhìn đẹp hoặc chia random 80/10/10 trước khi biết số nhóm độc lập.

Bảo toàn val/test v5 như mốc lịch sử; các ảnh/cảnh liên quan không được đi vào train mới. Nếu mở rộng development validation, tạo protocol/split version mới được review, không giả vờ metric so trực tiếp với E002 trên tập khác. Holdout thực tế phải độc lập nguồn/cảnh và có policy thu thập; chưa nguồn nào ở đây được chứng minh là holdout thực tế độc lập. Không inference/tuning trên test v5 trong task này.

Cần ghi phạm vi quyền các nguồn mới theo CC BY 4.0 và attribution version/URL/tác giả được cung cấp, thay đổi đã làm; không bịa tác giả khi README chỉ ghi Roboflow user. [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) không tự bao phủ quyền riêng tư/hình ảnh của người trong ảnh. Chưa upload media, train hoặc chuyển bản quyền của nguồn cũ thành câu hỏi mới.

## 6. Tác động kỳ vọng tới model

Mở rộng có cơ sở tốt hơn v4→v5 nếu tăng thật số cảnh/người/positive và negative được review. V5 chỉ có 80 train, 13 val, 11 test; E001/E002 dùng backbone đóng băng với linear head và E002 chưa cải thiện primary BCE. Không thể từ một ảnh sai hoặc tên dataset kết luận thuật toán là nguyên nhân duy nhất, cũng không hứa tăng bao nhiêu phần trăm.

V6 nên giải quyết coverage, confounding, nhãn mơ hồ và độ độc lập trước. Sau release, thí nghiệm mới giữ một baseline có thể so sánh, rồi thử fine-tune theo config/ADR riêng nếu cần. Kết quả cần phân tích theo target, nguồn, nhóm cảnh và loại lỗi; dataset lớn lên do augmentation hoặc lặp video không bảo đảm generalization. Ảnh người dùng gửi có tay gần mặt và tư thế viết là loại hard negative/unknown theo từng target cần bổ sung có review, không suy phone hoặc looking chỉ từ tư thế.

## Giới hạn và bằng chứng

Toàn bộ ảnh được kiểm cấu trúc/decode, nhưng chỉ các contact sheet và 28 crop target được xem semantics; không tuyên bố đã review hàng nghìn nhãn. `.rf.` lineage và dHash là đề xuất review, không phải session ID đã nghiệm thu. Source split không được coi là split dự án. Quy trình crop/runtime trên ảnh thực tế vẫn là gate riêng.

[Thư mục bằng chứng](../../artifacts/reports/pilot-b-v6-source-research-20261007/README.md) lưu kết quả, checksum, receipt ảnh mẫu, đối chiếu overlap và verification. Media và script exploration ở `outputs/`, không commit. Không thay raw, accepted v5, trainer, model hoặc test predictions.
