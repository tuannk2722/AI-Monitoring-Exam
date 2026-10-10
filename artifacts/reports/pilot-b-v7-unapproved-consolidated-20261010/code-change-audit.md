# Rà soát các thay đổi code/config hiện hành

Đối chiếu working tree với HEAD `8ae70f152984350babc124c7db1e69149f4b7ff8`. Phần lớn module/config/report v7 hiện untracked là kết quả nhiều lượt trước. Không gộp chúng thành thay đổi mới của lượt tổng hợp; [inventory có SHA và public functions](code-state-inventory.json) ghi từng module để có thể đối chiếu lại chính xác. Không commit trong lượt này.

| Nhóm thay đổi đã có | Module | Hành vi hiện hành và ý nghĩa cho pilot |
|---|---|---|
| Khai thác source local | `pilot_targeted_expansion.py` | Dùng cached fingerprint metadata, hạn chế nguồn train/review, tránh decode evaluation để bù fingerprint; label nguồn chỉ hint; shortlist còn Draft |
| COCO/Open Images targeted | `coco_targeted_candidates.py`, `openimages_targeted_candidates.py` | COCO train2017; Open Images finite prefix/intake; budget/quarantine/SHA, không gán missing annotation=N; total dataset size khác actual crop yield |
| Review qua nhiều revision | `targeted_review_package.py` | Proposal có bbox/PNU/evidence/pair guards; crop review-only; evaluation-family quarantine; cặp context chưa tự là matched-workarea |
| Quyền nguồn public | `public_attribution_audit.py` | Giữ title/author/license/source riêng ảnh; report quyền không tự approve source-use; 34 source quarantine được bảo toàn |
| Audit annotation, graph và funnel | `v7_annotation_audit.py`, `v7_source_coverage_audit.py` | PNU/fully-known/cell matrices, conservative graph/funnel; component/hash novelty không chứng minh độc lập; missing group metadata vẫn pending |
| Evidence input224 | `v7_input_evidence.py` | RGB letterbox bilinear224 từ E003; anchor/workarea/device QA tại input thật, không suy nhìn rõ ảnh lớn là đủ224 |
| Owner review R1–R5 | `v7_owner_review.py` | Áp phản hồi/crop delta vào proposal version mới; manifest `owner_approved:false` lịch sử không phủ nhận receipt approval sau đó; authority approve nằm ở receipt R8 pin exact R5 |
| R8 execution và reporting | `v7_r8_execution.py`, `v7_r8_reporting.py` | Nhập274 crop/label R5 có receipt; unused local/public screening mới;9crop Draft R6; role/split/train chưa assigned; novelty ranking chỉ hint |
| Video Wikimedia | `v7_public_video_audit.py` | Pin transcode đã tải, sample65frame,2crop cùngframe; không claim original pixels hoặc independent cut/session |
| Commons photo follow-up | `v7_public_photo_gapfill.py` | Discovery/license whitelist/cap/intake/thumbnail declared; recovery response offline; hiện dừng batch khi429 và ghi Retry-After;13crop Draft R4 với crop/source/credit224 |
| Public inventory/ZIP subset | `public_source_inventory.py`, `public_zip_screening.py` | Metadata receipt, HTTP Range/central-directory/CRC/budget guards, train-only subset38; không verify whole ZIP MD5 hoặc cộng augmented size thành diversity;2case QA-only |
| E003 error research | `training/error_audit.py` | Đọc predictions đã lưu để kiểm lỗi theo threshold run; không inference/tuning, không mở test; các evidence lỗi val lịch sử không nhập làm ảnh source của pilot này |

ADR-018 **Accepted** chốt mobile-only; tablet/laptop/calculator là đối chứng, không tự map annotation object hoặc class `cheating` thành nhãn target. ADR-017/gates E004 vẫn Draft; config E004-plan còn TBD/pins chưa chốt. Không đổi task formulation, metric, threshold, canonical release hoặc train để phù hợp proposal.

Các YAML cũ lưu budgets, URLs, phiên bản selection và output mới; config revision cũ đã chạy không tự đổi pin theo code sửa sau đó. `.gitattributes` hiện có quy tắc LF cho E004/v7/ADR/modules liên quan từ công việc trước; không sửa thêm trong lượt này. `docs/00-INDEX.md`, `docs/WORKLOG.md` và `.codex/TASK.md` được nối thông tin gói mới, giữ lịch sử cũ.

## Thay đổi mới của lượt tổng hợp

Thêm `src/ai_exam_monitoring/data/v7_unapproved_pilot.py`, hai config consolidated R1/R2, sáu guard tests và báo cáo tổng hợp. Builder pin approval/input SHA, chặn crop/ID approved và trùng crop, giữ masks0/splitnull/trainingfalse, phân biệt source-only không có nhãn với crop có bbox/PNU. Output bắt buộc version mới trong `outputs`, không ghi đè. Chép22crop cuối nguyên byte, render7crop mới và96source, ưu tiên crop trước ảnh nguồn; không có HTML.

R1 là kết quả kiểm đầu tiên. R2 sửa mô tả calculator của C003, sửa family RAN24 theo metadata, loại C008 gần trùng PF-C002 và ba source không phù hợp;96ảnh còn lại có mô tả riêng. Đã kiểm pixels nguồn so metadata R5: chỉ teacher R8-D001 dùng chung nguồn approved nhưng anchor/crop mới; source-only approved pixel overlap0. Crop SHA approved overlap0, crop pixel duplicate0.

Các helper inventory/contact-sheet/audit nằm dưới ignored `outputs`; chúng phục vụ qualitative review và ledger metadata. Logic tạo pilot tái lập nằm trong `src`, variables/pins trong YAML. Không thay trainer, production prediction, dataset mutation/version pointer chính thức hoặc dashboard.

## Kiểm tra và giới hạn kết luận

Full suite241PASS, Ruff toàn `src/tests/scripts` PASS, mypy module mới PASS; six guard tests kiểm nguồn nhiều người không tự có nhãn, approval/duplicate masks, đường dẫn evaluation/escape, adapter split và output mới. Sau thay đổi thứ tự hiển thị đã chạy lại6guardPASS. Output được kiểm toàn hash/decode/input224/links/media-preservation và visual QA.

Repository guard mặc định chỉ kiểm Git index; vì code/config/report mới còn untracked, lượt này còn kiểm chúng bằng Ruff/mypy/tests, đọc file/diff và [inventory pin](code-state-inventory.json). Không gọi `git diff --stat` là toàn bộ thay đổi: untracked không nằm trong diff tracked. Các README seal lịch sử mismatch giữ như finding riêng, không tuyên bố tất cả lịch sử checksum PASS.
