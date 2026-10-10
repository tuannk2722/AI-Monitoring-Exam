# Thực hiện sau owner review pilot — 2026-10-10

**Đã nhập đủ125quyết định:51phản hồi riêng và74mục mặc định approve.** [Gói kết quả crop/source/input224 R3](../../../outputs/v7-owner-execution-20261010-r3/REVIEW.md), [receipt owner](owner-approval.json), [quyết định structured](../../../outputs/v7-owner-execution-20261010-r3/owner-decisions.jsonl).

**Đã hoàn tất chuẩn bị release local theo hướng owner vừa duyệt.** [Bản cụ thể R2](../../../outputs/v7-local-release-preparation-20261010-r2/REVIEW.md) có **900 quyết định; đề xuất 689 train / 49 val / 11 test, 122 review-only và 29 excluded**. [Assignment](../../../outputs/v7-local-release-preparation-20261010-r2/proposed-assignment.jsonl), [ledger có provenance](../../../outputs/v7-local-release-preparation-20261010-r2/proposed-ledger.jsonl), [whole-family](../../../outputs/v7-local-release-preparation-20261010-r2/whole-family-proposal.json), [validation](local-preparation-validation.json). Chưa ký release hoặc chạy training.

## Hướng local đã duyệt và điều kiện đã kiểm

Owner chốt **“Duyệt hướng v7 local; tiếp tục kiểm điều kiện và chuẩn bị release”**. [Receipt](local-preparation-approval.json) pin phương án 694/49/11 có điều kiện đã trình bày và review R3. Đã dùng approval này để hoàn tất rights/lineage/whole-family và preparation; không hỏi lại hướng local. Final crop/nhãn mới và release cụ thể vẫn phân biệt với approval hướng.

Đối chiếu [49 parent review đã duyệt](../pilot-b-v7-targeted-20261008/owner-label-decisions.json): 40 retain, 6 relabel, 2 domain note, 1 exclude. [Delta v7](parent-correction-proposals.jsonl) thay đổi 9 record; parent dự kiến còn 314 train/49 val/11 test, ba U/U chuyển review-only và một record excluded. V6 gốc giữ nguyên SHA; test11 không sửa. Validation v7 khác E003 về cohort/target support nên không so scalar BCE trực tiếp như cùng tập.

[Rights ledger 402 crop](local-rights-proposal.jsonl) giữ quyền nguồn đã xác nhận và notice approval R5, bổ sung credit/license/source page/changes notice. Đã kiểm từng ảnh cho 19 crop Open Images mới bằng công cụ Flickr chỉ đọc metadata: **15 đủ metadata phù hợp snapshot CC BY2.0, 4 còn blocker**. [Receipt](new-openimages-metadata-receipt.json), [attribution](new-openimages-attribution.jsonl). Không tải thêm media hoặc dùng credentials.

| Crop giữ ngoài proposed train | Lý do |
|---|---|
| V7-OE-S005-A01 | Landing Flickr 404 |
| V7-OE-S020-A01 | Landing Flickr 403 |
| V7-OE-S027-A01 | Metadata hiện tại không trả license; không tự thay license snapshot |
| V7-OE-S034-A01 | Landing Flickr 404 |
| V7-OE-S080-A01 | Cached neighbor tới parent review-only thuộc group có val; chưa đủ evidence giải phóng boundary |

S080 là quarantine bảo thủ, không kết luận dHash5 chứng minh cùng scene. [Triage toàn pool](lineage-fullpool-triage.json) dùng fingerprint evaluation đã cache; không mở media val/test. Đã xem **22 cặp nguồn với parent train trên 6 bảng**; [pairs](../../../outputs/v7-local-lineage-inspection-20261010-r1/pairs.json) và [relations](local-whole-family-relations.json) ghi evidence. Bảo toàn must-link/parent group cũ, nối exact source và các family đã review.

Sau nối parent, 900 record có **449 conservative component**, gồm cả review-only/excluded. Không component/source/crop SHA nào đi qua nhiều proposed split. **Số nhóm/session độc lập được chứng minh vẫn là 0**. Còn 375 crop bổ sung trong proposed train sau giữ 4 rights blocker và S080 ngoài train; U/U/evaluation quarantine vẫn có đủ quyết định trong ledger.

[Config preparation R2](../../../configs/datasets/pilot_b_v7_local_release_preparation_r2_20261010.yaml) pin input/provenance/builder/counts; [builder canonical](../../../src/ai_exam_monitoring/data/v7_release_preparation.py) xuất proposed ledger/assignment/group deterministic. Ba payload này khớp nguyên byte giữa R1/R2. Không tạo manifest sử dụng, không sao chép/mở evaluation media trong preparation. 11 test giữ identity/source/crop/target/usage/evidence gốc, chỉ kiểm integrity metadata.

**Bước owner cuối:** nghiệm thu batch crop/nhãn mới, rights/use scope local, whole-family và assignment 689/49/11 trong bản cụ thể này để ký release v7. Căn cứ [hợp đồng pilot B mục3.3,6,7](../../../docs/data/pilot-b-release-contract-v1.md) và [E004 preparation mục3](../../../docs/experiments/E004-preparation.md). Release dataset không tự là approval E004 training; recipe/compute/metric còn Draft, independent holdout chưa đủ payload/protocol.

29crop đã được owner review được tiếp nhận; R8-C005 sửa looking thànhU theo nhận xét ảnh mờ. Đã thực hiện hướng crop/annotation cho96ảnh nguồn: **99crop mới từ82nguồn**,14nguồn được giữ ở reserve vì không đủ anchor/workarea hữu ích. Mọi nguồn vẫn ghi ownerapprove; reserve là quyết định usability có lý do, không phải ownerreject. R3 có128crop/source/input224,22bảng ảnh,7bảng native224; không HTML.

## Approval và phạm vi đã thực hiện

User xác nhận đã review `REVIEW.md`, giao tiếp tục thực hiện, và mặc định approve phần không ghi riêng. Snapshot [owner-reviewed-input.md](owner-reviewed-input.md) giữ nguyên byte phản hồi; ảnh trong snapshot dùng relativebase của [file owner gốc](../../../outputs/v7-unapproved-consolidated-20261010-r2/REVIEW.md), không phải media được chép vào report. Chỉ file `REVIEW.md` thay đổi so seal consolidated; đây là owneredit được xác nhận, có SHA mới và receipt mới. Các media/pin còn lại khớp seal. Không sửa/reseal package cũ.

Đối với29crop đã nhìn thấy, receipt nghiệm thu crop/nhãn hoặc correctionU. Đối với96ảnh chưa có bbox, approval ghi cho **source và hướng phân tích/annotation được giao thực hiện**.99rectangle/nhãn cụ thể phát sinh ở bước này còn được phân biệt trong manifest, không bịa rằng owner đã trực tiếp xem ảnh crop mới. Không tự đổi approval ấy thành release/split/train.

Đã dựng mới `data/interim/pilot-b/v7-owner-staging-20261010-r3/review-ledger.jsonl`, trỏ media versionR3. V6 và mọi crop/release cũ không bị ghi đè. 29crop kế thừa giữ nguyên87file source/crop/input224, chỉ nhãn C005 được sửa ở record mới.

## Các phản hồi riêng đã xử lý

| Mục | Kết quả thực hiện |
|---|---|
| R8-C005 | PhoneU giữ nguyên, lookingP→U; ảnh/crop không đổi, cả hai targetU ngoài supervision |
| S006 | Xác nhận laptop, không theo phonebbox Open Images; crop có head/tay/laptop, đề xuấtN/N |
| S042 | Tách nam áo xanh cầm ownphone và nam trái cầm tài liệu; phoneP/U-gaze vàN/N theo evidence riêng |
| S043/S044 | Mỗi nguồn4anchor: nam áo xám phone thật, badge đỏ/hồng không phone; nữ và nam áo đen có own-desk phone; nam kính vật trên bàn unknown. Giữ chung bootcamp family, không gán phone cho cả ảnh |
| S052 | Chọn học sinh tiền cảnh có ownlaptop và ownphone trên bàn, giữ đầu/tay/workarea |
| S056 | Tách2crop phone trên own-desk cạnh laptop; cùng ảnh/group |
| S057 | Chọn2anchor theo chi tiết owner: phone-like ở nam tiền cảnh giữU khi type chưa chắc, phone cạnh tay nam đứng giữP; sharedscreen gaze chưa chắc giữU |
| S066 | Hai anchor nữ, giữ mobile/calculator/page/tay của đúng người; cùngsource/component. Looking của nữ thao tácphone giữU khi ownpaper chưa chốt; nữ viết bàiN |
| S077 | Nam phải lookingP so ownmonitor; không gán phone của nam trái cho nam phải, vật chưa rõ giữU |
| S083 | Theo owner phoneU; source mất đầu nên lookingU, giữ reserveQA-only, không forcecroptrain |
| S109/S113 | [Clarification](phone-underdesk-clarification.json): **P nếu thấy điện thoại và đúng người cầm**. S109 giữ underdeskphone cùng tay hai anchor có tương tác; không dùng tabletoppen làmP. S113 không thấy device/ownership dưới bàn đủ nênU. Hai người/các góc cùngfamily |
| S112 | Vật xanh làsách, khôngcalculator; crop writing/page/hands, đề xuấtN/N |
| S114 | Nữ calculator khôngmobile; nam sau nhìn ngoài page, vật mép nguồn quápartial sau224 nênphoneU |
| S115 | Sleeping không suy lookingN từheadhướnglaptop; devicekhó xác nhận→U/U, QA-only |
| S116 | Cắt2anchor riêng: foregroundphone sát tay/desk vàlookingP; background viết ownpage. Giữ cùngfamily vớiS102/S109/S113 |
| Những ghi chú approve khác | Đã giữ nguyên verbatim trong decision và nối vào mỗi crop xuất phát từ nguồn đó |

Nhìn vào mobile của mình chưa tự chứng minh nhìn đúng **vùng bài làm**; các trường hợp thiếu ownpaper/workarea dùngU theo ADR012. Không giới thiệu semantics mới “mọi nhìnphone làlookingN”, không dùng nhãn nguồn hoặc annotation phone/person tự suytarget.

## QA đã thực hiện

Đã xem12bảng nguồn, mở native5nguồn ownership phức tạp, xem đủ7bảng128input224R1. R2 mở12rectangle giữ head/tay/device/workarea và chuyển mộtphone mép ảnh thànhU; [13delta](crop-qa-r2.json). Đã xem lại6bảng R2 có tất cả99crop mới. R3 giữ3cropU/U do chưa xác định ownworkarea/gaze (S011,S059,S095); [delta](crop-qa-r3.json). Pixel/geometryR3 giữR2, chỉ đổi3state/reason; đã xem lại bảng native R3 02/04/06 chứa delta cuối.

Staging có **123crop ít nhất một targetknown,54fully-known và5U/U**; đây là count annotation/evidence, không count train. State: PU27,NP3,NN31,UP20,UU5,UN21,PP10,PN10,NU1. Targets canonical vẫnnull,mask0,splitnull,trainingfalse; những proposedstates có riêng trong record.

[14nguồn reserve](../../../outputs/v7-owner-execution-20261010-r3/source-reserve.json) đều có lý do cụ thể: góc sau, bàn chung, mất đầu hoặc không có ownworkarea. Không lấy thêm ảnh/crop dễ để bù quota, không gọi sourceexhausted. Raw/ảnh nguồn bị cắt/mờ không được nội suy/superresolution để tạo evidence.

## Đã chuẩn bị dữ liệu cho bước tiếp theo

[Pool402crop](v7-pool-preparation.jsonl) gồm274R5 đã được duyệt trước +128crop thực hiện lần này. Tổng303crop có receipt nghiệm thu trực tiếp;99crop mới có nguồn/hướng đãduyệt và AI thực hiện, có provenance khác biệt. 76must-link component trong batch mới và [graph whole-component hợp nhất](v7-whole-component-preparation.json) nối các componentR5/same-source. Component khác nhau không chứng minh scene/session độc lập.

Giữ constraintsR5:257conditional,16U/U review-only,1evaluation-family quarantine. Trong batchmới:28cropknown đã review cònconditional;95cropknown mới còn chờ chốt annotation cụ thể;5U/U review-only. Cảpool: **285conditional đãreview,95knowncrop mới,21U/U và1evaluation-quarantine**. Upperbound380cropknown khôngquarantine chưa là380traineligible. [Validation/counts](validation-final.json).

[Near flags](source-similarity-flags.json) giữ riêng nearest-parent/evaluation metadata, không dùng khoảng cách làm independence/must-link proof, không mởtestmedia. Cùngảnh/cùngseries S066,S109/S113/S116,S043/S044 vàcác cặp R8/public được giữ chungcomponent; chưa officialsplit.

Các [gate tiếp theo](next-gates.json) được ghi rõ để chốt từ dữ liệu thật:

1. Chốt batch99crop/nhãn cụ thể từ những hướng nguồn đãduyệt, gồm cácU/QA-only đãxửlý; không bắt owner vẽbbox thủ công.
2. Nghiệm thu whole-family/membership/rights và proposed assignment 689/49/11 trong release preparation R2; hướng local đã chốt, không random-split hoặc tự thêm development-val.
3. Sau dataset gate, chốt E004 recipe/CPU/ADR017 metrics cònDraft/nullpin trước triểnkhai/chạytraining; independentholdout vẫn cần payload/rights/protocol riêng.

Sau staging, owner đã chốt hướng local và preparation cụ thể đã hoàn tất như phần đầu báo cáo. Còn nghiệm thu batch crop/nhãn mới và final release assignment; `configs/experiments/E004-plan.yaml` vẫn cóTBD/pinsnull cho training. Không suy approval125mục hoặc approval hướng local thành việc ký release/training cụ thể.

## Validation và bàn giao

**253 tests PASS**, Ruff `src/tests/scripts` PASS, mypy hai module mới PASS. 12 guard tests mới kiểm inventory/default approval, source/crop distinction, bounds, parent correction/test freeze, unknown masks, rights và cross-split whole-family. Hash/decode512media,128native224,29inheritedmedia nguyênbyte, stagingledger, pixelduplicate vàlinks kiểm trong [validation](validation-final.json). Rebuild assignment, hashes/pins/seals, original owner review và v6/test metadata PASS trong [release validation](local-preparation-validation.json). Không chạy inference/model, không upload, không đọc evaluationmedia.

[Config R3](../../../configs/datasets/pilot_b_v7_owner_execution_r3_20261010.yaml) · [Builder](../../../src/ai_exam_monitoring/data/v7_owner_execution.py) · [Staging](../../../data/interim/pilot-b/v7-owner-staging-20261010-r3/review-ledger.jsonl) · [Pointer](review-pointer-final.json). R1/R2 là checkpoints QA; chỉR3 bàn giao. Những mismatch seal lịch sử đã biết giữ nguyên và không tự xem receipt mới là câu trả lời nguyên nhân.
