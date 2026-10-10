# Nguồn mới để bù thiếu hụt — research ngày2026-10-09/10

Đây là source triage, không là approval dataset. Nguồn sơ cấp được đối chiếu qua publisher/repository, không dùng số tổng ảnh/clip làm useful sample count. Các quyền và đường tải có thể thay đổi; raw API receipts pin snapshot, [receipt2026-10-10](primary-source-receipts-20261010.json) ghi rõ request thành công/lỗi. Các nguồn owner đã gửi yêu cầu truy cập giữ pending theo [lời owner](pending-author-requests-owner-receipt.json), không xác nhận Codex đã gửi.

## Có payload và visual QA mới

**Wikimedia Commons, các ảnh classroom/learning do tác giả công bố.** Query targeted phone/table/writing/classroom, Kiwix và workshop. Đã scan367unique file-page metadata,206đủ whitelist; tải/xem95ảnh và tạo13Draft từ11ảnh. License whitelist CC0/CC BY/CC BY-SA với title/artist/source/license URL riêng từng file; không suy quyền người thật từ CC. 2original kiểm SHA1;93APIthumbnail khai rõ. Total pool hữu ích unknown,0owner-accepted mới. Đây là10visual family hints, chưa chứng minh nhóm độc lập. [Metadata/observations](visual-observations-final.jsonl), [review](../../../outputs/v7-public-followup-review-20261009-r4/review-index.html).

Nguồn classroom hữu ích cụ thể:

- [Nhóm students làm bài, phone viền xanh và calculator](https://commons.wikimedia.org/wiki/File:Inbound5488457748832502414.jpg): A002 PU; classroom nhìn từ trên, desk-phone P mới. Publisher timestamp2023-08-03, không suy session từ ngày upload/tên file.
- [Kiwix4Schools training](https://commons.wikimedia.org/wiki/File:Kiwix4Schools_Training_session.jpg) và [Q&A session](https://commons.wikimedia.org/wiki/File:Question_and_answers_session_on_kiwix4schools_training.jpg): A007 NU/C004 UN và C003 UP. Shared screen làm một gaze U; room/session link có timestamp, camera ID còn unknown.
- [Tabletunterricht06](https://commons.wikimedia.org/wiki/File:Tabletunterricht_06.jpg): A006 NN tablet-hard-negative, publisher CC0 và ghi consent người xuất hiện/người giám hộ để công bố. Chỉ áp dụng statement cho file này, không generalize cho mọi Commons photo hay train/release scope.
- [Teacher cho nhóm students xem phone](https://commons.wikimedia.org/wiki/File:A_teacher_showing_some_students_something_on_a_phone.jpg): D001 PU, phone của teacher, không phone P của cả nhóm.
- [Student trong classroom](https://commons.wikimedia.org/wiki/File:Africa_student_in_classroom.jpg): B001 PU own-held phone, partial/native224 cần nghiệm thu.
- [Students St Peters](https://commons.wikimedia.org/wiki/File:Students_Of_St_Peters_Anglican_School_2.jpg): C002 UN giữ trang/bút/mắt riêng.

Các file auxiliary vẫn hữu ích để kiểm confounding, **không bù shortage classroom**: [computer room people-at-work](https://commons.wikimedia.org/wiki/File:African_Women_working_on_computers.jpg) chưa purpose giáo dục; [bootcamp](https://commons.wikimedia.org/wiki/File:Bootcamp_-_Exploiter_Wikipedia_en_classe_journ%C3%A9e_3-06.jpg) có looking same-image pair nhưng workshop; [homework](https://commons.wikimedia.org/wiki/File:Mengerjakan_PR.jpg) có PN; [Kolkata event](https://commons.wikimedia.org/wiki/File:Students_Play_Mobile_Game_-_Kolkata_2016-10-23_1582.JPG) có ownership mobile ở người phải, device giữa không xác minh.

## Nguồn ngoài Commons cần follow-up

| Nguồn sơ cấp | Evidence đo / publisher công bố | Hiện trạng và phù hợp bucket |
|---|---|---|
| [HCMUE-SEGL](https://github.com/HungNguyenHcmue/HCMUE-SEGL) | Publisher61students/1663segments/4angles, body+context; non-commercial academic research, cấm redistribution/re-identify | Tốt cho group/workarea/camera nếu payload phù hợp. Link Drive qua web tool chuyển login, chưa có local file inventory/media;0screened/0yield. Không coi4angles là4independent groups, engagement labels không map trực tiếp phone/gaze. Không public-release derivatives |
| [UCB v2, Mendeley](https://data.mendeley.com/datasets/pz7y4bpfxy/2) | Page9June2026, CC BY4; mô tả student classroom behavior | File listing chưa đọc được, pool/phone/workarea/session unknown,0payload/0yield. Giữ inventory-blocked; public size/license page không đủ kết luận useful |
| [Online Exam Zenodo v2](https://zenodo.org/records/14606173) | Publisher có original833.8MB và augmented6.4GB; mobile/eye/sideways classes | Online assessment khác classroom CCTV; API license request504, webpage không đọc ra value license.0media. Giữ rights/provenance-blocked, ưu tiên original nếu quyền rõ, không cộng augmentation thành diversity hoặc map mobile-device thành mobile-only P |
| [CDED-7 / classroom-distraction](https://github.com/fangsheng223/classroom-distraction-tracker/blob/main/DATA_AVAILABILITY.md) và [license](https://github.com/fangsheng223/classroom-distraction-tracker/blob/main/DATASET_LICENSE.md) | Zenodo v2API xác minh1ZIP129771362bytes/MD5, publisher7classroomvideos+annotations; [record](https://zenodo.org/records/21207208) | Metadata có payload link nhưng chưa tải. Research-only, cấm surveillance/profiling/scoring, public/raw redistribution hạn chế. Phải xác định phạm vi nghiên cứu exam-monitoring hiện tại có phù hợp; chưa tự nhập. Tác giả gọi evaluation set của paper không tự trở thành independent holdout dự án, chưa mở media/model |
| [EduNet](https://github.com/vijetait/Classroom-Monitoring-Action-Dataset) | Publisher7851clips/20actions, nguồn YouTube và classroom; form request | Không phải tải ngay trong lúc chờ. Consent/upstream/license/camera groups chưa xác minh;0payload/0yield. Không gửi form hoặc dùng class using-phone làm nhãn reviewed-crop |
| [Kattal Exam Cheating](https://universe.roboflow.com/kattal/exam-cheating) | Page152images; version có362ảnh sau transforms, class cheating/not-cheating/person | Potential exam domain, nhưng upstream/scene graph/export payload chưa verify;0localmedia. Không map cheating=P hoặc augmented362 thành originalpool/useful count |
| [Classroom Objects](https://universe.roboflow.com/classroom-objects/classroom-objects-66fzh) | Page2826images/320object combinations | Person-workarea/mobile evidence chưa verify; chưa payload/0yield. Object counts không là nhãn anchor |
| [SCB upstream](https://github.com/Whiffe/SCB-dataset) | Catalog nhiều bộ SCB/STBD; source đang dùng đã có lineage audit | Không xem mirror/version mới là independent source. SCB/RF room-family overlap phải group QA theo accepted v6/R5; không refill train từRF-GREEN validation family |

Nghiên cứu cá nhân là lời owner, không tự nhận institutional affiliation hoặc chứng minh mọi điều khoản academic access. HCMUE link-tool blocked không chứng minh Drive private toàn cục; UCB inventory unknown không đồng nghĩa dataset exhausted. Dataset online exam có file tải công khai không tự chứng minh quyền reannotation/crop/training.

## Không dùng để tăng số

Các bộ engagement-only/face-only/synthetic/illustration/product phones không đóng bucket desk-phone/workarea/crowded attribution. [Devices-on-desk](https://github.com/orderedperceptron/devices-on-desk-dataset) có statement không cho AI training/testing; không đưa vào candidate training. MERICE cần request và engagement semantics, chưa là phone/gaze payload. Public mirrors SCB có cùng upstream/room cần group graph, không tính như nguồn độc lập mới. COCO/Open Images vẫn là public auxiliary theo policy cũ; tiếp có chọn lọc classroom/source/session, không lấy ảnh selfie/phone sản phẩm để lấp shortage.

Không nguồn mới nào đã được chọn làm official dataset/split hoặc independent holdout. Trước crop bổ sung phải có payload/licensing/path/version rõ; sau đó local visual evidence, input224, lineage/graph và owner nghiệm thu. Nếu không còn match trong **subset được kiểm**, báo yield0 của subset; không suy source exhausted toàn cục.
