# Public follow-up trong lúc chờ access — v7/E004

Bắt đầu 2026-10-09, bàn giao 2026-10-10. Owner: chủ repository, nghiên cứu cá nhân. **Đã tìm nguồn, tải và xem 95 ảnh mới; tạo 13 crop Draft từ 11 ảnh nguồn.** Chưa đủ để đóng shortage classroom/exam hoặc chứng minh nhóm độc lập. Owner đã báo gửi request access; [receipt mới](pending-author-requests-owner-receipt.json) ghi sent/pending theo lời owner, chưa xác minh từng nguồn/ngày gửi. Receipt lịch sử giữ nguyên.

Mở [final owner review R4](../../../outputs/v7-public-followup-review-20261009-r4/review-index.html): source có bbox, crop, input224 đúng kích thước, anchor, nhãn **phone / looking**, reason và credit/license. R1–R3 giữ lại lịch sử; chỉ R4 là đề xuất cuối của lượt này. Các crop mới chưa được approve: canonical targets null, masks0, split null, training false.

## Yield đo được

| Chỉ tiêu | Kết quả | Diễn giải |
|---|---:|---|
| Metadata Commons scan, union theo title | 367 | Bốn lượt query có cap; không exhaustive |
| Đủ whitelist license/dimension/byte | 206 | Eligibility metadata, chưa phải ảnh có ích |
| Tải thành công / đã xem | 95 / 95 | 2 original kiểm publisher SHA1; 93 thumbnail từ API publisher |
| Bytes ảnh thành công | 71.918.449 | Không tính metadata; 11 original-request HTTP429 giữ receipt lỗi |
| Ảnh shortlisted / không chọn lượt này | 11 / 84 | 13 crop; không chọn khác owner reject |
| SHA/pixel duplicate trong lượt mới | 0 / 0 | Scene repetition vẫn có; hash không chứng minh independence |
| Metadata đủ whitelist nhưng chưa tải | 111 | Không được gọi là 111 candidate có ích |
| Crop Draft / owner accepted mới | 13 / 0 | A6/B1/C4/D2 là bucket chính, không quota |
| Phone P/N/U | 7 / 2 / 4 | Bao gồm auxiliary và domain chưa xác minh |
| Looking P/N/U | 2 / 5 / 6 | Có own-paper/computer evidence trong shortlist |
| Fully-known / PP–PN–NP–NN | 3 / 1–1–0–1 | PP, PN nằm ở auxiliary; không bù strict classroom |
| Đúng classroom: desk-phone P/N | **1 / 2** | A002 P; A006 tablet-hard-negative, A007 N; cần owner review |
| Đúng classroom: looking P/N/U | 1 / 3 / 4 | C003 P, C002/C004/A006 N; không gán N chỉ từ cúi đầu |
| Same-image looking pair | 1 | A004/C001 trong workshop auxiliary |
| Same-room/session pair đề xuất | 1 | C003/C004 Kiwix, chưa xác minh camera/session ID |
| Visual families / independent groups proven | 10 / **0** | Family lớn nhất3crop; tất cả cùng publisher Commons |
| Train-eligible crop mới | **0** | Chờ label/unit/rights và graph QA, không final membership |

Số liệu tái lập ở [measurement summary](measurement-final/measurement-summary.json), [source × domain × target × PNU × group](measurement-final/matrix.json), [group constraints](measurement-final/group-constraints.json) và [95 observations](visual-observations-final.jsonl). Total available source pool và remaining **visually eligible** pool vẫn **unknown**; không có số estimated hữu ích đáng tin để điền. Không tuyên bố Commons hay cả nguồn đã exhausted.

## Những gì thực sự bổ sung

A002 đưa thêm phone nằm trên bàn sát người làm bài trong nhóm đồng phục; calculator hồng là confuser, eyes bị khăn che nên looking U. A006 đưa tablet-hard-negative lớp học. A007 có cả hai tay và trang/bàn máy, phone N đề xuất; gaze giữ U vì screen dùng chung. A001 là computer-room với mô tả people-at-work chưa xác minh giáo dục, A004 workshop, A005 home learning: **không tính ba positive này vào strict classroom desk-phone**.

C003/C004 có room/window/uniform tương ứng, publisher metadata cùng ngày 2021-04-12 cách21phút37giây. C003 quay khỏi vùng computer bên trái, C004 mắt/bút vào trang; đây là pair cùng cảnh/buổi học **đề xuất**, không phải same-image, same-person hoặc camera ID đã chứng minh. A004/C001 là P/N gaze thực cùng ảnh, chỉ bổ sung auxiliary. Giơ tay/tương tác lớp không là kết luận gian lận.

D001 là teacher giữ own phone thấp; student cùng xem không thành phone P. D002 đã đổi anchor sang người phải giữ mobile và recrop giữ trọn phone; device đen người giữa chưa xác minh mobile. Cả hai giữ looking U khi không có own-workarea. Crowded attribution thêm evidence có ích nhưng chưa thêm classroom PP chắc chắn. Xem [QA deltas](crop-qa-deltas-final.json) để tránh lý do cũ: A003 bỏ ownership yếu; suffix ngày không có căn cứ ở A002 đã bỏ.

## Nguồn và bước tiếp theo

[Source research](source-research.md) ghi primary URLs, license/access và vì sao không nhập các nguồn chỉ có size/link. [Funnel/shortage](source-funnel-and-shortage.md) ghi caps, cảnh lặp và kế hoạch chọn lọc; [owner decisions](owner-decisions.md) tách nghiệm thu crop khỏi source-use/split/release. HCMUE-SEGL đáng ưu tiên về group/camera/workarea nhưng đường Drive chuyển đăng nhập qua web tool; online-exam Zenodo có original/augmented riêng nhưng cần kiểm license và domain; classroom-distraction video có phạm vi research riêng, chưa mặc nhiên phù hợp exam monitoring. Không gửi thêm liên hệ hoặc upload media.

Lượt này **bù được một phần**, chưa đủ diverse classroom desk-phone P/N, crowded co-occurrence và small/partial224. Scene series Pabna15ảnh không yield crop cuối, không refill bằng ảnh dễ. Những nguồn controlled-access owner đã liên hệ vẫn chờ; nguồn public khác giữ trạng thái blocked/unknown đúng evidence.

## Validation và bảo toàn

[Validation](validation-final.json) ghi tests/lint/type/repository, hash/link QA và kiểm seal lịch sử. **Phát hiện thêm README R8 execution mismatch**: expected`cba7e324…`, actual`929d140c…`; chưa rõ nguồn thay đổi, đã hỏi owner. Giữ file hiện tại và seal cũ, không tự khôi phục/reseal; vì vậy không claim toàn bộ seal R8 cũ PASS. Mismatch README R7 đã biết cũng giữ nguyên. [Pointer cuối](review-pointer-final.json) pin riêng gói mới. V4–v6 và historical evaluation không sửa. Không train E004, release v7, materialize final split, chạy model independent holdout hoặc đọc media test lịch sử.
