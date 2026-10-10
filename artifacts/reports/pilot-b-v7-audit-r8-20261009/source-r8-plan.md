# R8 có điều kiện — ưu tiên theo failure mode, không quota crop

Trạng thái Draft; owner chốt các quyết định còn thiếu sau review package mới. R8 acquisition/visual expansion **chưa chạy**, actual new download/crop yield=0, diversity gain chưa đo. Yield R7 đo được274crop/242ảnh, không phải274accepted và không bảo đảm nhóm độc lập. Dùng `source-coverage.md` cho funnel; dùng group graph/report cùng package trước membership/split.

| Ưu tiên | Action khả thi | Điều kiện vào hàng đợi | Báo cáo bắt buộc / điều kiện dừng |
|---|---|---|---|
| 1 | Quét train Classroom/Student/Exam/RF chưa vào300screening, theo unused **group proposal** sau graphQA; ưu tiên đúng classroom/exam có phone flat trên bàn riêng và người head/hands/workarea đủ | Loại parent val/test relatives, augmented/re-export, cùng group đã dùng; mobile-only và person attribution rõ. Tìm phoneP vàN thực trong cùng nguồn/camera/session | Đếm scanned→downloaded→screened→eligibleP/N/U, grouped scene gain và shortage. Nếu không còn nhóm độc lập/thiết bị rõ: `blocked_independence` hoặc `exhausted_filter`, không lấy negative dễ để đủ80A |
| 2 | SCB Head/HRW+Classroom/Exam: đề xuất lookingP/N trong cùng ảnh/camera/room; crop phải chứa vùng bài/screen của người | BowHead/TurnHead/read/write chỉ hints; không suyP từ đầu nghiêng hoặcN từ tên nguồn; giữU khi workarea không đủ | Báo actual fully-known support và same-image/same-session pairs; không chuyển context-only thànhmatched. Dừng source/camera nếu group quen/evaluationfamily |
| 3 | Multi-person classroom/exam: anchor/head/hands/ownphone rõ; chọn cùng scene các actor P/P,P/N,N/P,N/N hoặc targetU được giải thích | Co-occurrence phải phoneP **và** lookingP của cùng người; không lấy phone teacher/neighbor cho anchor. Person/role owner chốt | Đếm actual ownership/co-occurrence trước/saurecrop; nếu chỉ crowd nhiều người mà evidence không đủ, reject/unknown có lý do |
| 4 | Chỉ bổ sung small/partial variations còn thiếu sau ownerinput224QA | So source/crop/input224 đúng preprocessing E003; mobile evidence không mất/nhầm calculator/tablet/camera. Không dùng proposed bbox nguồn làmlabel | Báo phần retained evidence/U/downgrade và diversity tăng thật. Không tự tạo size threshold hoặc tỷ lệaccepted mới |
| Public auxiliary | Open Images quét tiếp bbox phần chưa scan bằng train-only completeimagegroups; filters Person+mobile+desk/book/laptop, phone center trên bàn chỉrankhint, title classroom/exam/work hỗ trợ; lấy matched people trong cùngphoto/session khi có. COCO235workhint chưascreened xét có chọn lọc và positive thiếuannotation cầnreview | Pin metadata version/range/checksum và partial receipt; khửtrùng đãscreened/Flickr/crosssource; license/landing/notice rõ trướcprimary. Không đọc nguồnholdout hayupload media thật | OI report bytes/rows/imagegroupsscanned+eligiblefilters+actualyield; không gọi fullOIexhausted. COCO185phone-context filter hiệnhành exhausted; thayfilter tạo version riêng và công bố thay đổi, không tuyên bố chắc có235N |

Không đặt “phải tăng thêmNcrop”. Giá trị cần tăng là classroom/exam desk-phoneP/N thật, looking có workarea cùngcamera, ownership/co-occurrence đúngactor, và evidence nhận đượcở224. Sourcewide counts/sha/newimageIDs không chứng minhdiversity.

## Quyết định owner cần chốt

| ID / Owner | Đề xuất | Evidence để chốt |
|---|---|---|
| TBD-R8-LOCAL-SUPPLY /repository-owner | Tiếp khai thác Classroom/Student trước theo groupgraph; Exam retry source-specific vì jointcap đã làm yield2 không chứng minh exhausted; SCB ưu tiên matchedlooking | Funnel mới có per-source screened/unseen, independent unused groups và reviewpack source/crop/input224 |
| TBD-R8-MATCHED /repository-owner | Chỉ tính matchedstrong khi same-image/scene/session có bằng chứng; context-only là pairinghypothesis | Graph/pair audit và report strength; cặp sửa rõ anchor/gaze/workarea |
| TBD-V7-CASES /repository-owner | Nghiệm thu từngdevice/gaze/anchor flagged trong ownerfinalreview mới; không tựsửa canonical | V7-B-079/B-080 thiết bị, C025/C036workarea, A035/B040/C093/C094recrop, D026ownership; cácQAflags khác tách khỏiinstructionlabel |
| TBD-V7-MEMBERSHIP/SPLIT /repository-owner | Khóa uncertain/evaluation relatives ngoàitrainingproposal; groupeddevelopment assignment chỉDraft | Groupgraph có component/provenance; không độc lập theoSHA/sourceID; v4–v6/historypreserved |
| TBD-PUBLIC-NOTICE /repository-owner | Xác nhận phạmviuse/notices/rightspublic đủmetadata; giữ34ảnhquarantine ngoàiprimary | Ledger/license/landing/flickridentity/changesnotice; đủmetadata không thayownerapproval |
| TBD-E004-PROMOTION /repository-owner | Giữ chưaeligible; khôngtrain/hodlout | Datasetrelease approval, metrics/recipe/gates/protocol được chốt; independentholdoutfreeze riêng, khôngmodelrun |

Blocker trước v7release: ownerfinalannotation/crop/input224review; independence/lineage/parentgroup reconciliation; membership/split approval; publicrights/notice decisions; datasetversion/pins và integrity. Blocker trước E004promotioneligibility: cácgate datasettrên cộng E004recipe/numericalgates/protocol và independentholdoutnguồn/phạmvi/quyền/freeze chưađượcchốt. Không dùng publicauxiliary ngoàiexam thay independentexamholdout.
