# Audit sau R7 và chuẩn bị R8 có điều kiện — 2026-10-09

**R7 chưa đủ bằng chứng để kết luận v7 đã giải quyết các failure modes của E003.** Audit và gói nghiệm thu mới đã hoàn tất; nhãn, membership, split và quyền vẫn là Draft. Không train E004, release v7, materialize final split hoặc chạy model trên independent holdout.

[Mở final owner review R5](../../../outputs/v7-owner-review-r5-20261009/review-index.html): 274 record, 31 delta đề xuất, đủ ảnh nguồn/crop/input224. Reason hiện hành hiển thị trước; QA R7 cũ chỉ nằm trong phần lịch sử. [Bảng quyết định owner](owner-decisions.md), [receipt phản hồi](owner-feedback-receipt.json), [QA flags](owner-qa-flags.md), [pointer cuối](review-pointer-final.json), [mẫu ghi quyết định](owner-review-template.json).

## Kết quả theo failure mode

| Hạng mục | R7 đo được | Sau QA và phần còn thiếu |
|---|---|---|
| Desk-phone A57 | Phone 32P/25N; 12 classroom/exam-context chỉ 6P/6N; 45 auxiliary | Chưa đủ P/N đúng domain và chưa chứng minh camera/session mới. A035 sửa bbox; A002/A061 giữ state với reason thiết bị rõ. |
| Looking C98 | 49P/49N; Head 22P/4N, HRW 1P/17N, RF 11P/3N, Exam 1P/1N, COCO 4P/5N, OI 10P/19N | Final 45P/48N/5U. Polarity lệch giữa nguồn; camera, room, group chưa xác minh. C025/C036/C089/C092/C117 thiếu evidence workarea/gaze. |
| Crowded D39 | PU29, PP2, PN1, UP2, UN5 | Chỉ hai proposal co-occurrence cùng anchor. D026 nữ writer N/N; teacher sở hữu phone. Final phone 27P/1N/11U; looking 4P/7N/28U. |
| Small/partial B80 | 40P/40N. Input224: P32 clear/8 ambiguous; N31 clear/7 ambiguous/2 lost do bbox | Final phone 36P/34N/10U. B048/B111 sửa crop; B066 thiếu workarea/phone visibility nên U/U. Source rõ nhưng 224 yếu không tự thành N. |
| Fully-known / bốn tổ hợp | 73/274: PP10, PN3, NP9, NN51 | Final 69/274: PP10, PN3, NP7, NN49; 16U/U đề xuất review_only. 258 record có ít nhất một target known chỉ là upper bound trước quyền/group/usability. |
| 162 pair links | 6 same-image, 1 same-scene, 155 source-context | Final 140 đúng polarity, 22 invalid. Hai same-image pair bổ sung qua kiểm ảnh; chưa tìm session pair mới đã xác minh, independent group gain bằng 0. |

Mọi record vẫn có mask `[0,0]`, targets null, split null và training-eligible false. Clear/ambiguous/lost là qualitative, không threshold hay acceptance metric mới. Không cộng U vào quota P/N.

## Coverage nguồn và annotation

[Funnel tám nguồn cuối](source-coverage-final.md) có pool/scan/payload/screening/selection/rejection/exclusion/caps/remaining, [JSON đo được](source-counter-r2/source-coverage-measured.json), [CSV](source-counter-r2/source-coverage-measured.csv) và [metadata chưa xem](source-counter-r2/source-unused-metadata.csv). Có 1.303 ảnh screening, chọn 242 ảnh tạo 274 crop Draft; 1.061 ảnh không chọn không phải owner rejected. Không suy batch acceptance từ phản hồi đã review toàn bộ.

Sáu nguồn local chưa exhausted. Exam chỉ có 13 ảnh screening trong cap chung: ba phone hints thiếu person attribution, bảy ảnh thuộc collage family, một reserve thiếu final rejection reason và hai crop được giữ. Còn 474 hint rows chưa xem, useful independent groups unknown. Classroom/Student/RF còn 1.390/2.700/2.384 hint rows; SCB remaining useful pool chưa đo. Total dataset size không thay số mẫu có ích.

OI có 1.743.042 train image IDs, nhưng bbox chỉ scan prefix 1.954.110 rows/264.870 complete image groups, tương đương 13,3716% bytes; không ngoại suy yield. COCO exhausted riêng bộ lọc 185 phone-context đã xem; còn 235 work hints chưa xem, không phải 235 phone N. Các số đo dùng snapshot đã pin; không có estimated useful counts.

[Annotation analysis cuối](annotation-analysis-final.md) và [audit CLI](annotation-r4/annotation-audit.md): [ma trận source × domain × target × P/N/U × group](annotation-r4/annotation-matrix.csv), [family hints riêng](annotation-r4/annotation-hint-matrix.csv), [four combinations](annotation-r4/annotation-combinations.csv), [looking source/camera/room/group](annotation-r4/annotation-looking.csv), [concentration](annotation-r4/annotation-concentration.csv), [crowded ownership](annotation-r4/annotation-crowded.csv). Tất cả 274 camera/room/registered group vẫn UNKNOWN; không giả thành nhóm độc lập.

[Graph proposal](annotation-r4/group-whole-component-proposal.json) có 233 conservative components, 0 nhóm độc lập đã chứng minh; sáu component/14 crop liên hệ parent train qua explicit scene hints cần owner review. Không tìm thấy exact evaluation-linked component, nhưng nearest flags chưa giải quyết nên không chứng minh sạch lineage. Component count không thay independence hoặc official split.

## Evidence và owner review

[Input224 audit R7 cuối](input224-r3/input224-audit.md), [ownership audit](input224-r3/ownership-audit.md), [receipt/pins](input224-final-receipt.json). Đã xem toàn bộ 80B/39D qua 30 sheets; 119 finding có source/crop/input SHA. 274 input224 dùng preprocessing E003 RGB/bilinear/letterbox; không load weights/model. Audit R7 này giữ nguyên; recrop/proposal hiện hành ở R5.

Root đã kiểm 15 flags, các source bổ sung, recrop và sáu endpoint của ba cơ hội same-image pair; hai panel B066/C131 mới đã xem. [Pair visual receipt](pair-visual-review-final.json), [822 media hashes và review integrity](owner-review-verification-r5.json). B066/B020 cùng ảnh thật nhưng không đủ P/N; hai cặp giữ Draft là B039/B089 (phone) và B102/C131 (looking), đều auxiliary. D026 còn cơ hội crop teacher P/U mới, chưa materialize, không group gain.

Mobile-only theo [ADR-018 Accepted](../../../docs/decisions/ADR-018-v7-mobile-phone-boundary.md). B080 ảnh local chưa xác minh thiết bị là mobile; ảnh nguyên gốc độ phân giải cao chưa thu nhận/kiểm. Không suy đầu nghiêng thành looking P hoặc group activity thiếu workarea thành P.

## R8, quyền và blockers

[R8 có điều kiện](source-r8-plan-final.md), [YAML](../../../configs/datasets/pilot_b_v7_r8_conditional_plan_20261009.yaml): desk-phone P/N đúng classroom/exam → looking cùng camera/workarea → crowded ownership/co-occurrence → small/partial thiếu evidence tại224. Không quota crop bắt buộc. Acquisition R8 chưa chạy: actual new yield 0; independent diversity gain chưa đo. Hết filter đã kiểm thì exhausted_filter; thiếu group evidence thì blocked_independence; không refill bằng ảnh dễ.

131 public crop R7 có metadata license khớp; 34 source images khác giữ quarantine. Owner cần chốt rights/notice/use scope, label/anchor/device/gaze, 224 usability, graph, membership/split và provenance tài liệu. Quyền nghiên cứu auxiliary đã có được giữ; không suy thành approval release/train. [Public rights](../../../docs/data/v7-public-auxiliary-rights-20261008.md).

E004 vẫn chưa promotion-eligible: gates/recipe/protocol còn Draft/TBD và independent holdout chưa đủ source/support/domain/lineage/rights/freeze. Crop count hoặc validation gain không đóng [ADR-017](../../../docs/decisions/ADR-017-e004-classifier-promotion-gates.md).

## Validation và lịch sử

[Validation receipt](validation.json): full suite 221 tests PASS trước chỉnh parent graph, sau đó sáu annotation/graph tests PASS; Ruff toàn repository PASS, mypy bốn module mới PASS; repository/diff/path/link/hash checks theo scope ghi trong receipt. Không tuyên bố toàn repository mypy PASS.

[Historical integrity cuối](historical-integrity-final.json): R7 input/pointer pins khớp, 11 metadata file mỗi v4/v5/v6 khớp, historical E001–E003 tracked không diff. Không đọc hoặc rehash historical test crop bytes. **README R7 khác SHA trong checksum-final cũ; 51 file khác khớp.** Giữ nguyên README/checksum; nguyên nhân chưa xác minh cần owner chốt provenance.

Review R1–R4, annotation R1–R3 và các source snapshot trước giữ để truy vết; chỉ dùng R5 / annotation-r4 / source-counter-r2 cùng pointer cuối để nghiệm thu. Không tự approve hay materialize final release.
