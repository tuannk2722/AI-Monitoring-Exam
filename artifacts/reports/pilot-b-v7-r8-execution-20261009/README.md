# Thực hiện R8 sau owner approve — 2026-10-09

Đã nhập approval cho **274 crop/nhãn/anchor R5**, thực hiện targeted screening và tìm nguồn Internet mới. Kết quả: **272 ảnh mới từ tám nguồn hiện có +65 frame của một video public**, dựng **9 crop Draft và 4 cặp P/N cùng ảnh**. **Desk-phone đủ điều kiện đề xuất train mới=0; nhóm độc lập mới được chứng minh=0.** Chưa train E004, release v7, materialize final split hoặc chạy model holdout.

Mở [review source/crop/input224](../../../outputs/v7-r8-owner-review-20261009-r6/review-index.html), [bảng quyết định owner](owner-decisions-r8.md), [research nguồn Internet](source-research.md), [yield measured](qa-r2/yield-summary.json). R7, package audit đã sealed, v4–v6 và historical evaluation giữ nguyên; mọi receipt/proposal mới dùng version riêng.

## Approval và phạm vi

[Receipt](owner-approval.json) pin đúng pointer audit và proposals R5 đã review. [274 decisions đã nhập](accepted-r5-review-decisions.jsonl) ghi approval crop/label, gồm U và recrop. Snapshot R5 cũ giữ nguyên status; receipt mới là bằng chứng nghiệm thu. Approval report không chứng minh independence, tự điền assignment null hoặc phê duyệt quyền release nguồn mới.

Owner chỉ thị tự tìm nguồn trên Internet và chọn tư cách **nghiên cứu cá nhân**. Đã research 12 nguồn/candidate sơ cấp, nhận video Wikimedia và chuẩn bị [yêu cầu truy cập IMPROVE/HCCB](source-access-drafts.md). Chưa gửi liên hệ/ký thỏa thuận. Những nguồn cần agreement hoặc inventory chưa đọc được ghi blocked, không exhausted.

## Funnel thực hiện

| Nguồn | Screen trước R8 | Screen mới / lũy kế | R5 crop/label approved | Crop Draft mới |
|---|---:|---:|---:|---:|
| Classroom |172|60 /232|60|2|
| Student |42|32 /74|14|0|
| Exam |13|34 /47|2|2|
| RF |73|24 /97|23|0|
| SCB Head |66|24 /90|26|3|
| SCB HRW |34|12 /46|18|0|
| COCO |305|64 /369|39|0|
| Open Images |598|22 /620|92|0|
| Video Wikimedia mới |0|65 frame|0|2|

Tám nguồn cũ lũy kế 1.575 ảnh screening; frame video không trộn vào số ảnh/index của các dataset cũ. Local caps 60/32/34/24/24/12 là giới hạn screening, không crop quota. R8 dùng 4 source images local mới, source D026 cũ và một frame video mới. 268/272 ảnh và 64/65 frame không shortlist; đây không phải owner reject hoặc nhãn N. [Registry 337 observations](qa-r2/screening-observations.jsonl) và [funnel kế thừa audit +delta](qa-r2/source-funnel-r8.json) giữ rõ measured và unknown.

Selector local loại 2.770 anchor hints đã screened theo SHA/name lineage và 13.561 near-previous hints; 9.129 unique SHA còn sau filter trước cap186. Đây là hint counts, không rejected crops hoặc independent groups. dHash chỉ tạo QA flag. Visual QA phát hiện họ RF-GREEN phải ngoài train dù distance có thể lớn hơn ngưỡng hint.

Open Images mở thêm 64MiB, đạt 369.098.752/2.258.447.590 bytes =16,3430%. Quét 2.388.134 annotation rows/317.459 complete image groups; bỏ whole tail image26483700c0fa2423. Bốn Range16MiB được kiểm ETag/Content-Range/overlap16MiB và old-prefix hash. Receipt đầu FAILED do lỗi finalization gọi `st_size()`; [recovery receipt](openimages-metadata-recovery.json) xác minh payload PASS, giữ nguyên raw và receipt cũ. Không còn desk-context hints mới qua filter; nhận/xem22 held-phone hints, 0crop/0download failure. Toàn source chưa exhausted.

COCO lọc 235 work-context hints chưa screened trước R8, nhận/xem64, còn 171 trong filter. 0failure/0shortlist; không refill bằng negative dễ. Phone filter cũ exhaust 185 eligible metadata, không toàn useful pool. Video Wikimedia nhận 127.660.962bytes ở 854×480, xem 65 frame mỗi 20 giây; chưa tải original hoặc có camera/session metadata.

## Quality, pairs và diversity

R8 phone **2P/2N/5U**, looking **4P/3N/2U**; fully-known2, PP0/PN0/NP1/NN1. [Ma trận source ×domain ×target ×P/N/U ×group](qa-r2/annotation-matrix-r8.json), [concentration](qa-r2/concentration-r8.json). Mỗi record có final reason/anchor/source/crop/native224, mask0, splitnull và owner_approved=false. Tất cả9 panel đã visual QA; R6 chỉ bổ sung title attribution, pixel/crop/label giống revision R5 đã xem. Preprocessing RGB letterbox bilinear/fill E003 giữ nguyên; không model QA.

Bốn pair gồm ba looking: C001/C002, C005/C006, C007/C008; một phone: D001/approved V7-D-026. Guard kiểm P/N, endpoint, same source SHA và external approved-review pin. Pair teacher không đếm lại crop nữ cũ. C004/pair002 bị loại vì hai anchor thử chưa đủ negative gaze. Các revision R1–R5 giữ lịch sử; **chỉ R6 là final proposal batch**.

SCB18/130 và IMG3485 có parent-train lineage; group gain0. Wikimedia là một visual-family lead mới, chưa chứng minh session independence; gom toàn video/cut thành một family bảo thủ, chưa chọn holdout role. A006 R5 filenameIMG_20220620 bị train quarantine theo RF-GREEN validation boundary v6, không đổi crop/label đã approved. [Membership constraints274](qa-r2/approved-r5-membership-constraints.jsonl):257 conditional,16 UU review_only,1 evaluation-family quarantine. 257 là upper pool có điều kiện, không train-eligible count.

Desk-phone trong classroom/exam, diversity camera/session và positive co-occurrence vẫn thiếu. R8 tăng matched-looking/ownership thật và low-light phone evidence; chưa thể kết luận giải quyết mọi failure mode E003. [Hướng mở tiếp](source-research.md) ưu tiên IMPROVE/HCCB, UCB inventory và targeted OI/COCO; không yêu cầu số crop bắt buộc.

## Validation và integrity

227 tests PASS trong classifier environment; Ruff src/tests/scripts PASS, mypy3 module mới PASS, check_repo0failure, git diff check PASS. Tests bao gồm output containment/no-overwrite, approval UU không promote/split, Range giữ old raw, same-image P/N/source checks và public frame không đọc processed/assigned holdout. Lần full-test đầu thiếu PYTHONPATH gây import errors; chạy lại với src PASS. Codec imageio-ffmpeg0.6.0 cài riêng outputs, không đổi dependency dự án.

[Validation receipt](validation-final.json), pointer và checksums final pin media/input/config/code. Kiểm lại sealed audit967files và v4–v6 metadata pins. README R7 mismatch đã báo được giữ nguyên, không hồi tố. Không đọc/rehash historical test media. Public Wikimedia có title/credit/license/change notice trong HTML; chưa approve release derivative hoặc nguồn mới vào final membership.
