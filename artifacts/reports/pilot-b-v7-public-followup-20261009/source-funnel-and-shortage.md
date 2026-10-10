# Funnel và shortage sau public follow-up

Đo ngày2026-10-10 cho intake ngày2026-10-09; canonical [measurement](measurement-final/measurement-summary.json). Những summary intake cũ ghi pending_visual_QA là receipt tại thời điểm tải; [ledger95](visual-observations-final.jsonl) là trạng thái QA sau đó, không sửa receipt raw.

| Lượt | Pages metadata riêng | Đủ whitelist riêng | Cap ảnh | Attempt / success / visually screened | Asset / lỗi |
|---|---:|---:|---:|---:|---|
| R1 | 121 | 57 | 20 | 13 / 2 / 2 | Original, 11 HTTP429 |
| R2 recovery | 95 | 85 | 60 | 57 / 57 / 57 | API thumbnail; metadata recovery từ response đã nhận |
| R3 | 111 | 54 | 30 | 22 / 22 / 22 | API thumbnail,0failure |
| R4 | 70 | 35 | 20 | 14 / 14 / 14 | API thumbnail,0failure |
| Union | **367** | **206** | Không cộng cap thành pool | **106 / 95 / 95** | 95title/source SHA/pixel hashes khác nhau |

R1 metadata excludes 11small/ 50nonraster/ 2license/ 1byte-cap; R2 4license/2nonraster/4small; R3 56nonraster/1small; R4 35nonraster. Union excludes139nonraster/6license/15small/1byte-cap. Metadata union theo title; bảng riêng có overlap, không cộng121+95+111+70 làm available pool. R2 chưa complete vì metadata429; recovery offline giữ mọi raw đã nhận và pin checksum.

R1 đã tiếp tục request sau 429 trước khi guard được sửa: lỗi có thật, receipt bảo toàn. Code hiện dừng batch khi429, ghi Retry-After và remaining deferred; discovery không tiếp seed sau429. Theo phản hồi publisher, các batch sau dùng thumbnail URL do API sinh ở kích thước chuẩn1920, pacing2s, hữu hạn. Không đổi host hay giả original. Chỉ2original được kiểm publisher SHA1;93thumbnail có local SHA256/pixelhash và khai original dimensions riêng. Xem [kích thước thumbnail chuẩn của MediaWiki](https://www.mediawiki.org/wiki/Common_thumbnail_sizes/en).

## Scene concentration và phần còn lại

95ảnh đều đã xem; 11 ảnh có 13 proposal, 84 ảnh không shortlisted. Owner chưa accepted/rejected crop mới. Bootcamp110–115 gộp bảo thủ toàn series/ngày, chọn 111 hai anchor; Tabletunterricht 153–155 chọn 154 một anchor. Các ảnh Kiwix khác phòng không tự tách thành independent session;306/310 cùng room được ràng buộc cùng family trong proposals. Pabna208–222:15ảnh của cùng workshop,0crop cuối; group/crowding không đủ nếu mắt/bài/ownership chưa thấy. Không gọi toàn publisher Pabna/Kiwix exhausted chỉ vì lượt hữu hạn này không yield.

111metadata đủ whitelist chưa tải gồm ảnh sản phẩm/illustration/room trống, team portraits/graduation, conference/table và vài lớp học generic. Chưa visual-screen nên **remaining eligible pool unknown**, không gọi111 cơ hội train. Tên file/keyword classroom không chứng minh domain, workarea hoặc independent group. Nearest dHash chỉ là hint đối chiếu ảnh đã screening, không là scene graph/split. Không mở lại holdout hoặc face-recognize người để chứng minh independence.

## Quyết định tiếp theo theo actual yield

| Priority | Gain hiện có | Shortage / hành động có điều kiện |
|---|---|---|
| Classroom/exam desk phone | 1P/2N Draft từ3family hints | Còn thiếu nhiều cảnh/session độc lập và exam thật. Tìm public classroom BYOD/lab/worksheet có phone trên bài; chỉ tiếp metadata/gallery khi có camera/room/session hoặc contact-sheet hint phù hợp. Không dùng workshop/home để đóng bucket |
| Looking cùng source/camera/workarea | 1same-image pair auxiliary;1Kiwix same-room proposal | Xác minh family306/310 và workspace; cần P/N của nhiều room/camera khác. Không forced N từ head-down; screens/chung bàn giữ U khi unclear |
| Crowded attribution/co-occurrence | D001/D002 có own-held phone;A004 PP auxiliary | Chưa có PP classroom đủ chắc, cần anchor riêng và own-workarea. Pabna15ảnh không tự thành gain |
| Small/partial sau224 | B001 vàD001 handheld trong lớp để review224 | Phone hiện còn tương đối dễ; chưa đóng tiny/partial desk-phone hoặc góc CCTV. Chỉ nhập variant có device/ownership còn đủ sau224 |

Nguồn public ưu tiên bổ sung ngoài Commons: HCMUE-SEGL cho group/camera nếu lấy được payload và quyền local research; UCB để inventory nếu file listing mở được; online-exam original Zenodo chỉ auxiliary sau license/provenance QA, không download augmented để nhân số. Classroom-distraction videos cần chốt mục đích sử dụng vì license giới hạn research và cấm surveillance. Những nguồn không có payload/rights/independence giữ blocked, không refill bằng source dễ. Open Images/COCO đã có partial scan trong sealed R8: chỉ tiếp targeted classroom/workarea/source-scene filters; nhận diện generic phone/laptop không đủ. Không hard-code số crop phải tăng.
