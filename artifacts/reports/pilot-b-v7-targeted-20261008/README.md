# Targeted expansion v7 — Gói review cuối, 2026-10-09

**Đã chuẩn bị 274 crop Draft sau khi xem 1.303 ảnh screening. Còn thiếu 26 so với budget 300.** Đây là gói để owner nghiệm thu, chưa phải release v7 hoặc dữ liệu đã được phép training. Các proposal dùng đúng thứ tự `phone_use / looking_around`; canonical targets vẫn null, masks `[0,0]`, split/group null và `training_eligible:false`.

[Mở review có attribution](../../../outputs/v7-public-attribution-r7-review-20261009/review-index.html) để xem ảnh nguồn, khung crop và crop. [Review unit/phenotype/pairs](../../../data/interim/pilot-b/v7-targeted-review-20261008-r7/review/index.html) có liên kết giữa các cặp. Media chỉ có trong workspace local. [Pointer cuối](review-pointer-final.json), [coverage](coverage-r7.json), [QA](crop-qa-r7.json), [verification](verification-final.json), [config](../../../configs/datasets/pilot_b_v7_targeted_review_r7.yaml).

## Coverage thực tế

| Bucket | Budget gồm cả negative | Crop Draft | Thành phần chính | Thiếu | Lớp/phòng thi theo ngữ cảnh | Public bổ trợ ngoài phòng thi |
|---|---:|---:|---|---:|---:|---:|
| A — Desk-phone và negative | 80 | 57 | 32 phone P, 25 phone N | 23 | 12 | 45 |
| B — Mobile cầm tay nhỏ/che một phần và negative | 80 | 80 | 40 phone P, 40 phone N | 0 | 50 | 30 |
| C — Looking-side/forward và read/write/computer negative | 100 | 98 | 49 looking P, 49 looking N | 2 | 60 | 38 |
| D — Crowded/co-occurrence | 40 | 39 | Nhiều người, ownership/che khuất, có cả P/U và các tổ hợp target khác | 1 | 21 | 18 |
| **Tổng** | **300** | **274** | **Mỗi crop chỉ tính một bucket chính** | **26** | **143** | **131** |

Budget là số candidate cần tìm/review theo [plan đã review](../../../configs/datasets/pilot_b_v7_targeted_plan.yaml), không phải số positive hoặc số accepted. Cân bằng tối đa nửa budget cho từng polarity là heuristic shortlist, không phải acceptance gate mới. Các cột ngữ cảnh không chứng minh camera/người/session độc lập, hoặc tính đại diện phòng thi thật. Riêng phenotype nhỏ/partial của B vẫn cần owner nghiệm thu trên crop cuối; không bịa ngưỡng pixel “small” đã được duyệt.

274 crop đến từ 242 ảnh nguồn, tám source ID: Classroom60, RF v1 23, Student14, Exam2, SCB Head26, SCB HRW18, COCO39, Open Images92. Có 232 family hints, **không phải 232 nhóm độc lập đã nghiệm thu**. Accepted và training-eligible hiện đều bằng 0.

## Tuyển theo lỗi và sửa annotation/crop

- A giữ mobile trên giấy, bên keyboard/laptop, màu trắng/bạc/đen, flip/keypad và phone thiếu annotation nguồn. Negative có paper/keyboard, tay sát mặt, calculator/stationery và landline; phải xem đúng tay/bàn của người. RF149 có **mobile thật trên giấy cạnh calculator**, vì vậy A002 là phone P, không phải calculator negative.
- B tuyển mobile cầm tay ở góc nghiêng, gần tai, thấp gần lap/desk hoặc bị tay/đầu che một phần. Negative có bút, headphones/earbud, tay trống gần mặt và thao tác paper/keyboard. Không suy N từ annotation thiếu mobile.
- C giữ head và bài/screen riêng để phân biệt nhìn ra ngoài với đọc/viết. Đã sửa các source “read/write” nhưng người thực tế nhìn sang bạn/người đối diện; giữ phone U khi target đó chưa đủ bằng chứng.
- D chọn đúng người trong crowd; gộp alias cùng person/source thay vì tính crop mới. Đã loại phone của người bên cạnh, device có thể là compact camera và các crop không đủ head/hands/context.

Owner đã chốt **phone_use chỉ gồm điện thoại di động**: [ADR-018 Accepted](../../../docs/decisions/ADR-018-v7-mobile-phone-boundary.md). Landline không tạo phone P; N vẫn cần bằng chứng vùng quan sát của đúng người. Các mẫu không chốt được gaze/ownership hoặc toàn unknown nằm ngoài quota. Các revision/loại mẫu được giữ trong [QA R3](crop-qa-r3.json), [R4](crop-qa-r4.json), [R5](crop-qa-r5.json), [R6](crop-qa-r6.json).

Đã nhập đầy đủ 49 cell owner review E003 thành [delta cho version sau](owner-label-decisions.json): 40 giữ target, 6 relabel target, 1 đề xuất exclude, 2 đổi metadata domain. Riêng V6R2-EX-008: phone N giữ nguyên, looking P theo owner xác nhận. Delta chưa materialize; không viết lại release v6, metrics hoặc kết luận E003. Hai Markdown owner đã review được giữ nguyên byte trong các snapshot của thư mục này.

## Quyền public và lineage

131 crop public tương ứng 121 Flickr photo ID: 39 crop COCO và 92 Open Images. Đã xác minh creator/title/landing/license qua metadata công khai có photo ID khớp; license quan sát khớp snapshot CC BY2.0 cho toàn bộ 131 crop. [Ledger từng crop](public-attribution-r7.jsonl), [receipt](public-metadata-receipt-r7.json), [summary](public-attribution-summary-r7.json). **Đủ metadata không đồng nghĩa owner đã nghiệm thu quyền, notices hoặc membership.** Credit/changes notice được đưa vào trang review riêng.

34 ảnh nguồn khác có attribution/license chưa giải quyết nằm trong [quarantine quyền](public-rights-quarantine.json), ngoài primary. Có trường hợp login/403/404/landing sai và license hiện tại khác snapshot. Không dùng credentials hoặc tự đổi license để nhận ảnh. [Hồ sơ quyền](../../../docs/data/v7-public-auxiliary-rights-20261008.md) phân biệt license ảnh với annotation và nêu giới hạn của oEmbed.

[Triage lineage](lineage-triage-r3.md) cách ly 43 screening keys có họ hàng evaluation hoặc nghi vấn chưa giải quyết; bảy crop R3 liên quan đã bị loại. Bốn crop theo numeric series chỉ là cách ly bảo thủ, không phải leak đã chứng minh. Các liên hệ parent train/same-scene và cùng Flickr photo được giữ trong [group triage cuối](group-triage-final.json). Không mở/đọc bytes/decode ảnh test11; chỉ dùng manifest và cache fingerprints có sẵn. Source mới chỉ lấy original train/train2017.

## Matched negatives và phần chưa đạt

Có 162 pair links: 6 cùng ảnh, 1 cùng cảnh, 155 chỉ match ngữ cảnh nguồn/paper/book/computer/tay gần mặt. Một negative có thể nối nhiều positive nhưng chỉ tính một crop vào quota. **155 cặp yếu không được coi là matched camera/session.** Số lượng B đủ budget chưa đóng gate matching, source balance hoặc independence. Những pair/gaze/crop này vẫn là đề xuất cho owner, không là ground truth đã accepted.

A thiếu 23, C thiếu 2, D thiếu 1 sau QA và kiểm quyền. Không bù bằng augmentation/re-export, họ hàng val/test, crop toàn unknown, hoặc thiết bị chưa chắc là mobile. 1.303 ảnh đã xem gồm RF 300, SCB 100, COCO 129+80+96, Open Images 181+18+200+199; [inventory/pins](screening-inventory-final.json), [receipt 774 ảnh followup](followup-screening-visual-review.json). Open Images R4 có 1/200 download vượt 10 MB, receipt failure được giữ. Bbox Open Images chỉ là prefix 301.989.888 bytes với image groups hoàn chỉnh, **chưa exhaustive**; không tuyên bố đã hết dữ liệu public.

Ưu tiên đợt tiếp theo là source có **mobile flat trên bàn riêng cùng paper/keyboard và người đủ head/hands**, có negative trong cùng ảnh/session; sau đó bù 2 looking và 1 crowded có supervision rõ. Có thể mở tiếp phần Open Images train chưa audit hoặc nguồn public mới có license/landing kiểm được, ưu tiên classroom/workdesk. Phải nối family theo người/cảnh/source, không tính image ID mới thành nhóm độc lập. Thêm negative dễ chỉ để đủ 80 A không giải quyết thiếu desk-phone/camera mới.

## Kiểm tra và nghiệm thu

203 tests trong environment classifier PASS; toàn repo Ruff PASS; mypy 6 module mới PASS với `--follow-imports=silent`; `check_repo --require-git` và `git diff --check` PASS. Full `mypy src` vẫn có 66 lỗi trong 16 file legacy, nên **không ghi toàn repo type PASS**. Source/crop SHA, geometry, unique crop/person trên full pixels, pair contract, pins và checksum toàn package PASS. Kiểm tra này xác nhận preparation integrity, không xác nhận group independence hay chất lượng mô hình. [Bằng chứng validation](validation-final.json).

Owner có thể nghiệm thu batch crop/nhãn/phenotype và nêu ID cần sửa/loại; [mẫu quyết định cuối](owner-review-template-final.json) pin đúng package. Quyền nguồn public và family graph cần quyết định riêng trước membership/split. Phạm vi nghiên cứu public bổ trợ ngoài phòng thi đã được owner cho phép; không hỏi lại quyết định đó.

[AGENTS.md](../../../AGENTS.md) yêu cầu: “Mọi dataset mutation phải tạo version/pointer mới và có owner review được ghi lại”. Vì vậy package này dừng ở Draft có thể review. Release v7, split, training E004 và promotion chưa được thực hiện. Holdout độc lập và các quyết định recipe/numerical gates của E004 vẫn nằm ngoài package này; COCO/Open Images bổ trợ không thay holdout phòng thi.
