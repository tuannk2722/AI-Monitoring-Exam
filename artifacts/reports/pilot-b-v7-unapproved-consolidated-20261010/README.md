# Pilot tổng hợp ảnh/crop chưa được duyệt — 2026-10-10

**Bản để review: [PILOT R2 bằng Markdown và ảnh PNG](../../../outputs/v7-unapproved-consolidated-20261010-r2/REVIEW.md).** Gói gồm **125 mục từ 119 ảnh nguồn: 29 crop và 96 ảnh nguồn cần xem lại anchor**. Chỉ gom phần chưa được owner approve, theo câu trả lời “chỉ gom những ảnh chưa được tôi approve”. Không tạo HTML.

29 crop có ảnh nguồn đánh dấu người, crop và input224 đúng kích thước; 96 ảnh nguồn có ảnh đầy đủ và mô tả riêng người/vùng bài/bàn cần kiểm. Phần ảnh nguồn chưa có bbox/nhãn là ứng viên review, **không được tính như 96 crop có target**. Mỗi mục giữ nguồn gốc, SHA, credit khi có, lý do chọn và giới hạn về cùng cảnh/series.

| Phần | Số mục | Cách xử lý |
|---|---:|---|
| Crop R8 cuối chưa duyệt | 9 | Giữ crop/nhãn Draft R6 và media nguyên byte |
| Crop public follow-up cuối chưa duyệt | 13 | Giữ crop/nhãn Draft R4 và media nguyên byte |
| Crop bổ sung từ lượt rà lại | 7 | Đề xuất mới, chưa nghiệm thu; mô tả bên dưới |
| Ảnh nguồn bổ sung | 96 | Mô tả riêng từng ảnh; cần chốt anchor trước crop/nhãn |
| Crop R5 đã duyệt | 274 | Đối chiếu receipt và SHA, không đưa crop vào pilot |
| Media legacy v6 | 0 mục mới | Dùng fingerprint metadata để loại nguồn cũ |
| Hai ví dụ online-exam QA-only | 0 mục | [Ghi lý do loại](qa-only-excluded.jsonl), không chép media |

Thứ tự trong PILOT: 29 crop trước, rồi 96 ảnh nguồn; 21 bảng ảnh nhỏ để xem nhanh và panel lớn của từng mục để kiểm kỹ. Có thể dùng [template review](../../../outputs/v7-unapproved-consolidated-20261010-r2/owner-review-template.json); các ô còn null, không có approval tự điền.

## Đã rà những gì

Đối chiếu Git HEAD `8ae70f152984350babc124c7db1e69149f4b7ff8`, working tree hiện hành, accepted ADR/config, approval receipt, các bản selection/reserve/review, visual observations, intake receipts, nghiên cứu nguồn và lịch sử crop QA. [Audit thay đổi code](code-change-audit.md) mô tả từng nhóm logic và phân biệt thay đổi cũ với công việc lượt này.

| Phạm vi metadata screening/reference đã đối chiếu | Số dòng |
|---|---:|
| Local targeted ban đầu + SCB | 400 |
| COCO R1–R3 | 305 |
| Open Images R1–R4 | 598 |
| Local R8 + COCO R8 + Open Images R8 | 272 |
| Wikimedia: 65 frame sampling + 1 frame reference | 66 |
| Reference ảnh nguồn đã duyệt | 1 |
| Commons public follow-up R1–R4 | 95 |
| Online-exam subset train | 38 |
| **Tổng 21 registry** | **1.775** |

[Inventory pin từng registry](screening-registry-inventory.json) có **1.773 SHA nguồn khác nhau**, không gọi 1.775 dòng là 1.775 ảnh độc lập. Đã xem lại **77 bảng ảnh**, gồm 1.531 lượt hiển thị ngoài nguồn đã approved/legacy theo fingerprint; số này là lượt dòng, có reference/overlap, không phải count độc lập. Đã xem đủ 22 bảng pilot R1, mở panel lớn của cả 8 crop mới trước QA; sau chỉnh R2, kiểm thêm 6 bảng bị ảnh hưởng. [Receipt xem ảnh](visual-recheck-receipt.json) và [validation cuối](validation-final.json) ghi phạm vi riêng.

Lịch sử targeted có **1.745 lượt proposal, union 385 ID**; 111 ID không nằm trong batch R5 approved. Đã đối chiếu **source + bbox + states** từng revision, vì một ID có thể thay người hoặc crop qua các bản. Không phục hồi crop cũ đã QA sửa chỉ vì ID bị bỏ. [Ledger revision](revision-dispositions.jsonl), [ledger reserve](reserve-dispositions.json) và [ledger R8/public revisions](followup-revision-dispositions.jsonl) ghi đường đi đến bản cuối. 14 lượt reserve có 1 lượt nguồn được giữ lại để review; không lấy tất cả easy-phone reserve để tăng số.

[Ledger toàn bộ 1.775 dòng](screening-dispositions.jsonl) ghi disposition và lý do, cùng tham chiếu về pilot. Dòng “không chọn” là quyết định screening của Codex cho lượt này, **không phải Owner Reject**, không tự biến unknown thành N. Nhiều observations cũ ghi “not shortlisted” chưa đủ để kết luận nguồn đã cạn; các ảnh nguồn có workarea đáng xem đã được mở lại trong pilot này.

## Bảy crop bổ sung và những sửa đổi sau kiểm ảnh

Thứ tự state: `phone_use / looking_around`; P/N/U chỉ là đề xuất.

| ID mới | State | Evidence và phần thiếu liên quan | Giới hạn |
|---|---|---|---|
| C001 | U/P | Nam áo caro quay khỏi trang riêng; giữ đầu/trang/tay | Tay phải/vùng bàn ngoài ảnh; cùng series, không group mới |
| C002 | N/P | Nam kính áo caro quay trái khỏi giấy, hai tay/bàn thấy được | Phone N cần owner chốt; cùng họ cảnh caro |
| C003 | P/U | Nữ giữa giữ own mobile xanh; crowded ownership có teacher chỉ tay | Vật xanh trên vở là **calculator**, không phone thứ hai; gaze/shared interaction giữ U |
| C004 | P/N | Nữ phải giữ own mobile đỏ, bút/tay và mắt hướng trang sách riêng | Không gán phone cho cả nhóm; cùng ảnh với C003 |
| C005 | P/P | Nam nhìn sang người bên trái, mobile vàng trên bàn phía trước có trang/tay riêng | RAN24 workshop auxiliary; không tính PP classroom |
| C006 | P/N | Nam áo cam hướng vùng viết riêng, mobile vàng dưới cẳng tay | Cần owner kiểm desk-phone attribution; cùng RAN24 series |
| C007 | P/U | Nữ denim giữ mobile nhỏ bằng hai tay, có trang ở mép bàn | Gaze giữa phone/trang chưa chốt; workshop auxiliary |

Các ID đầy đủ có tiền tố `V7-UNAPPROVED-`. Ứng viên C008 đã bị loại vì cùng người/cùng nguồn với `V7-PF-C-002` đang nằm trong 13 crop Draft; crop rộng hơn một chút không tạo thêm gain. Ba ảnh source-only bị loại ở bước cuối: S007 thiếu own-workarea trong cảnh kể chuyện, S016 là cắt tóc, S079 mất bài/bàn/device evidence. R1 giữ lại để trace; **chỉ R2 là bản bàn giao**. [15 blocker/loại cuối](../../../outputs/v7-unapproved-consolidated-20261010-r2/selection-blockers.json) gồm 8 quyền public chưa giải quyết, 3 lineage và 4 mục loại sau visual QA.

`V7-R8-D-001` dùng cùng ảnh nguồn với crop nữ `V7-D-026` đã approve, nhưng là **crop teacher chưa duyệt**. Pilot giữ crop teacher để review ownership, không chép lại crop nữ. Đây là đúng một trường hợp source pixel trùng nguồn approved; không có source-only trùng pixel approved, không có ID/crop SHA approved lọt vào gói.

## Ảnh nguồn nên xem trước

Các gợi ý dưới đây trỏ đến ID trong PILOT; chưa phải nhãn hay quota đã đạt.

| Phần thiếu | Các mục đáng xem trước | Điều cần kiểm |
|---|---|---|
| Desk-phone trong lớp/phòng thi | S066, S080, S109, S113, S115, S116 | Phân biệt calculator/mobile, đúng mặt bàn của anchor; một số ảnh cùng series |
| Looking so với bài riêng và cặp trong cùng ảnh | S068, S081, S085, S102, S109, S113, S114, S116 | Giữ đầu, tay, trang; crop hai anchor riêng; không suy gaze từ single-class label |
| Crowded phone ownership | S069–S071, S077, S083, S106 | Phone của người cầm khác người đang cùng nhìn; tablet/hard-negative riêng |
| Small/partial sau224 | S040, S049, S074, S080, S083 | Phone ở mép ảnh/thấp dưới bàn; crop không phục hồi pixel source đã mất |
| Auxiliary desk-phone/workshop | S042–S044, S051, S052, S056–S057 | Workarea/ownership có ích nhưng chưa bù strict classroom/exam |
| Hard-negative thiết bị/công cụ | S002, S006, S035, S053–S054, S106, S112, S114 | Tablet/laptop/calculator không mobile theo ADR-018 |

Các ảnh quay lưng, bàn chung hoặc bị che vẫn ở phần dự phòng khi có ích để owner đối chiếu mức evidence; lý do từng ảnh nêu rõ thiếu mặt/workarea. 96 ảnh này không được tính fully-known, pair gain hoặc training support.

## Shortage sau tổng hợp

29 crop có **9 fully-known Draft** và 20 crop chứa U. Phân bố state: PU9, NP2, NN2, UP5, UN5, PP2, PN3, NU1. Hai PP hiện đều auxiliary; không gọi chúng là PP classroom chắc. Có 21 crop mang domain đề xuất `classroom_or_exam_context`; đây chưa phải 21 cảnh classroom độc lập được xác minh. Các domain còn lại: computer room chưa xác minh mục đích1, workshop2+3, homework1, educational event1. [Số liệu chi tiết](audit-summary.json).

**Số nhóm độc lập đã chứng minh vẫn 0.** Cùng actor, room, cut video, session timestamp, góc máy hoặc photo series được ghi là family hint/quan hệ cần kiểm; không tự chia thành group độc lập. Những crop mới không đóng shortage classroom desk-phone đa session, matched looking có own-workarea, ownership đông người hay phone tiny sau224. Tất cả record còn targets null, mask0, split null, training false; gói này chỉ để nghiệm thu ảnh/crop, chưa là dataset version/release hoặc E004 run.

## Nghiên cứu nguồn đã rà và phần không có ảnh để gom

[Tổng hợp research và trạng thái bằng chứng](research-coverage.md) đối chiếu cả R8, public follow-up và R2. Các nguồn chỉ có metadata/link, bị access/rights/availability blocked được liệt kê đầy đủ; không tạo ảnh minh họa thay payload chưa nhận. Không tải lại Internet trong lượt tổng hợp này; trạng thái được ghi theo snapshot research 2026-10-09/10.

Giới hạn cụ thể: Commons đã scan367 trang metadata nhưng chỉ tải/xem95 ảnh; 111 metadata đủ whitelist chưa tải không là 111 ảnh hữu ích. Video Wikimedia chỉ có65 frame sampling, không đã xem toàn video. COCO full train annotation scan khác full media scan; còn171 work-context hint theo R8 chưa tải. Open Images chỉ scan prefix, không gọi toàn nguồn exhausted. Online-exam chỉ xem38train/4.395train; 4.357 ảnh chưa tải chưa có kết luận visual. Không đọc publisher valid/test hoặc project holdout để tìm crop bổ sung.

## Validation và lịch sử được bảo toàn

**241 tests PASS**, Ruff `src/tests/scripts` PASS, mypy module mới PASS, repository guard và `git diff --check` PASS; sau chỉnh thứ tự R2, 6 guard tests liên quan chạy lại PASS. [Validation](validation-final.json) kiểm 28 pin inputs, 308 media SHA/decode, 29 input224 RGB, 146 links ảnh Markdown, approval exclusion, trùng pixels crop và inherited media nguyên byte. Đã xem riêng cả29input ở native224; các phone nhỏ/dark/partial vẫn cần owner nghiệm thu evidence, không suy visual QA thành train eligibility.

Giữ 34 source quyền public và 43 screening key lineage trong [quarantine metadata](historical-quarantines.json), không chép media của chúng vào pilot. [Đối chiếu seals lịch sử](historical-integrity-check.json) ghi ba mismatch: README R7/R8 đã biết và `source-funnel-and-shortage.md` public follow-up mới phát hiện (expected `907ff1c6…`, actual `f860a137…`). Owner trả lời **“Không, tôi không chỉnh”**; nguyên nhân vẫn chưa xác định, không quy cho owner và không sửa/reseal lịch sử để làm PASS. [Receipt trả lời](historical-mismatch-owner-response.json). Pilot mới có pin/checksum riêng. Chưa thay raw, release, official labels/split, ngưỡng/metrics, model, training, web hoặc upload dữ liệu.

[Pointer bàn giao](review-pointer-final.json) · [Config R2](../../../configs/datasets/pilot_b_v7_unapproved_consolidated_r2_20261010.yaml) · [Manifest125](../../../outputs/v7-unapproved-consolidated-20261010-r2/review-items.jsonl) · [Checksum media/review](../../../outputs/v7-unapproved-consolidated-20261010-r2/checksums.sha256).
