# Tổng hợp toàn bộ source research đã lưu

Đây là audit snapshot research đã làm ngày2026-10-09/10, không phải lần xác minh live mới. Trạng thái có thể thay đổi ở publisher; không mở rộng nhiệm vụ tổng hợp thành intake mới. Những nguồn không có media chưa được tạo ảnh/crop trong pilot.

Nguồn bằng chứng: [R8 research](../pilot-b-v7-r8-execution-20261009/source-research.md), [public follow-up research](../pilot-b-v7-public-followup-20261009/source-research.md), [funnel/shortage](../pilot-b-v7-public-followup-20261009/source-funnel-and-shortage.md), [R2 mới nhất](../pilot-b-v7-public-followup-20261010-r2/README.md), các metadata/HTTP/intake receipts pin tại mỗi report. Không lấy status snapshot cũ làm trạng thái mới nhất khi R2 đã xác minh thêm.

| Nguồn/nhánh đã nghiên cứu | Media đã có trong repository | Kết luận cho gói tổng hợp |
|---|---|---|
| Local Classroom Attitude / RF / Exam Cheating / SCB head-HRW | Local screening400+186 R8; có approved và Draft | Rà toàn source ngoài approved; giữ nguồn/crop thiếu gaze/page/ownership đáng xem; lineage43 vẫn quarantine; các mirror/frame/augmentation không group mới |
| COCO train2017 R1–R3/R8 | 369 dòng screening | Rà lại tất cả subset đã tải ngoài approved; không đưa easy held-phone/selfie/product/public scene vào shortage classroom chỉ vì có person+phone; reserve không tự phục hồi |
| Open Images train prefix R1–R4/R8 | 620 dòng screening | Có27source-only cuối và nguồn crop cũ đã approved được loại; giữ credit từng file.34source quyền unresolved giữ metadata quarantine, không crop mới |
| Knowledge for Everyone Wikimedia | Transcode854×480,65sample frame vàframe reference | Giữ2crop R8 gaze cùngframe; không thêm frame lặp/ngoài lớp/không workarea. Original1888×1062 chưa nhận; video chưa exhaustive |
| Wikimedia Commons classroom/learning/workshop | 367metadata/206whitelist/95media | Giữ13crop Draft cuối +3crop RAN24 bổ sung vàsource leads; 2original SHA1verified,93thumbnail declared.111whitelist metadata chưa tải không có visual eligibility kết luận |
| Online Exam Zenodo v2 | ZIP original inventory5.575images;38train đã xem | R2 đã xác minhCCBY4/open, supersede blocker license504 snapshot cũ.0targeted additions;2caseQA-only loại khỏipilot; không readvalid/test/augmented6.4GB |
| IMPROVE/BiDAlab | 0video | Access agreement/author request pending theo owner; desk-phone/session tiềm năng, domainMOOC. Không tạo crop hoặc gán possession label nghiên cứu thành target |
| HCCB/ODER-HSFNet | 0image | Controlled academic access; crowded classroom tiềm năng, cần camera/session/multi-target reannotation rights. Publisher796ảnh/50.229boxes chưa là usable crop count |
| UCB Mendeley v2 | 0payload | PageCCBY4 nhưng genericHTML/FAQ không usable file listing; inventory blocked, không exhausted hoặc guessed export |
| HCMUE-SEGL | 0payload | Publisher61students/1.663segments/4angles; GETlink trảGoogleSign-in. Access blocked cho tool; academic/noncommercial/redistribution restrictions; không coi4angles là4group |
| CStudentAct | 0payload | Cần commitment; no-modification/redistribution blocker cho crop/224/reannotation, chưa chốt quyền |
| StudentAct HUST/SigM | 0payload | R2lead5camera/31.046frames/596.371boxes theo publisher; cùng access/no-modification blocker. Không nhân group từ5camera |
| CDED-7/classroom-distraction | MetadataZIP129.771.362bytes/MD5,0video downloaded | R1 sau probe cũ đã thấy file inventory; scope research-only/cấmsurveillance-profiling-scoring vẫn blocked. Không mở evaluation videos để lấp pilot |
| BNU Student-Class-Behavior | 0payload | Primary repositoryComing soon, availability/license chưa đủ |
| SCBehavior/CCNUZFW và SCB upstream/Whiffe/STBD mirrors | Metadata/reference | Nguy cơ cùng SCB family; không nguồn độc lập mới nếu chưa upstream/license/scene graph; không lấy RF-GREEN validation family |
| Paper-based exam actions/Data7(9)122 | 0payload | Trang bài429 trong snapshot, dataset access/license chưa xác minh; license bài không cấp quyền media |
| Students suspicious behaviors Mendeley | Structured numeric records | Không rawRGB; không phù hợp crop classifier dù cóphone/gaze feature |
| Mobile Detection/sunnysul | 0payload reviewed | RepoMIT không đủ chứng minh từng stock/search-derived image; provenance blocked |
| Student using phone or not/Roboflow | Metadata-only | Upstream/session/original-vsaugmentation/export chưa verify; khôngsource độc lập |
| Classroom-cell-phone v3/Roboflow | PageCCBY4/253images; direct403,0payload | R2train178/valid51/test24 là publisher counts; mirror14versions không14source; không gọimodelAPI |
| Kattal Exam Cheating/Roboflow | Metadata152images/362transformed,0payload | License/upstream/scene/export cần verify; không mapcheating=P, không augmentedcount như originalpool |
| Classroom Objects/Roboflow | Metadata2.826images/320object combinations,0payload | Object count không target/anchor/workarea evidence |
| EduNet Classroom Monitoring Action | Metadata7.851clips/20actions,0payload | Request form; YouTube upstream/consent/license/camera chưa rõ; không gửi form trùng thay owner |
| V-CL part1/Zenodo | APIrestricted/filesempty,0media | CC license metadata không mở access; individualonline learning chưa bù crowded/classroom |
| Invigilo | Public annotations/code,0rawclips | CodeMIT không chứng minh media license; giữsourcelead, không mởbenchmark/testvideos |
| Devices-on-desk | Metadata restrictions,0media intake | Statement khôngAItraining/testing; không đưa vào candidate training |
| MERICE | Request/engagement-only lead,0payload | Chưa cóphone/gaze/workarea evidence phù hợp |
| Các kết quả Commons product/diagram/illustration/room trống/portraits/genericconference | Chỉ metadata khi không đủ targeted | Không tạo media/crop giả hoặc download để tăng số; chưa xem source không gọi visual reject |

Owner đã báo gửi requests truy cập nhưng chưa có danh sách receipt grant cụ thể. Không tự xác nhận quyền/access đã được cấp hoặc gửi email/form thay owner. Các author-access nguồn tiềm năng vẫn nằm trong audit để không bị bỏ quên, nhưng **không có ảnh để gom** khi chưa payload.

Các kết quả nghiên cứu E004/error-holdout lịch sử được rà ở mức báo cáo/config; không chuyển media evaluation/model mistakes thành nguồn pilot expansion. Không có official source/split/holdout mới được chọn trong lượt này.
