# ADR-017 — Đề xuất điều kiện xét promotion classifier E004

- Trạng thái: **Draft, chưa Accepted; chưa cấp quyền train/final test/promotion**.
- Ngày: 2026-10-08. Owner/người chốt: chủ repository (solo), Codex chuẩn bị.
- Phạm vi đã được owner chọn: classifier trên crop đã review, hai target của ADR-011/012. Owner chưa có holdout, yêu cầu nguồn công khai mới.
- Bằng chứng nền: [E003](../experiments/E003-results.md), [audit từng lỗi](../../artifacts/reports/E004-research-20261008/e003-audit/fn-audit.md), [kế hoạch E004](../experiments/E004-preparation.md).

## Vấn đề cần quyết định

Doc11 và index còn `TBD-METRIC-01`; không có numerical promotion gates đã Accepted. E003 hoàn tất kỹ thuật nhưng không có independent holdout. Một `best.pt` hoặc BCE giảm trên validation không tự có quyền Selected. ADR này đề xuất đóng gate **trước chạy E004**, không đặt chuẩn sau thấy model/test mới.

Promotion chỉ là **Selected cho nghiên cứu classifier trên crop đã review trong scope nguồn đã duyệt**. Không đóng S9, end-to-end, tracking/event/risk/web hoặc cấp quyền giám sát cá nhân. Nguồn chỉ cho benchmark không tự cho phép demo media/deployment.

## Điều kiện vào E004 và điều kiện trước mở test

| ID | Điều kiện đề xuất | Trạng thái hiện tại / bằng chứng phải có |
|---|---|---|
| G0 | ADR/model acceptance và protocol E004 được owner duyệt; không có threshold/metric/source/split quan trọng còn TBD | OPEN. ADR này Draft; owner phải chốt trước training. |
| G1 | v7 và holdout riêng có owner release approval, rights/use scope, label/crop/group QA, payload/config/checksum; không unresolved overlap | OPEN. Chưa có v7/holdout Accepted. Source mới cần payload audit trước chọn test. |
| G2 | Holdout độc lập với toàn bộ dữ liệu đã dùng phát triển E001–E004 theo nguồn quay/lineage/group; không chọn test theo prediction; test11 và val50 chỉ lịch sử/phát triển | OPEN. SHA khác/project khác không đủ; lack provenance ⇒ chưa đạt. |
| G3 | Support test của mỗi target ≥100 known P, ≥100 known N; ≥10 nhóm độc lập có bằng chứng, mỗi target có P ở ≥5 nhóm và N ở ≥5 nhóm; primary domain có ≥2 bối cảnh camera/room đã xác minh | OPEN. Đây là **mức tối thiểu đề xuất**, không suy 100 frame=100 tình huống. Không ép split hoặc cân bằng lại test để đạt số. Không đủ nguồn ⇒ INCONCLUSIVE, chưa được promotion. |
| G4 | Một candidate E004 FINISHED, config/seed/code/data/model/environment pin; smoke/resume; evaluator val reload khớp quy tắc tái lập đã duyệt; package chứa/pin đủ backbone+head+preprocess+target order+threshold | OPEN. Trainer hiện chỉ hỗ trợ frozen linear; phải triển khai partial fine-tune sau approval và kiểm meaningful tests. Best E003 hiện giữ head và pin backbone ngoài, không là standalone model. |
| G5 | Candidate/config/checkpoint/protocol/holdout hashes freeze trước inference test; owner cho phép một evaluation; access receipt chặn chạy lần hai dù đổi output; không artifact test trong cache train/dev | OPEN. Guard evaluator hiện pin một candidate nhưng chưa quản lý độc lập holdout hoặc dùng-test-một-lần xuyên output. |

G0–G5 là gate về **đủ điều kiện xét**. Chưa qua toàn bộ thì trạng thái `eligible_for_promotion=false`, bất kể metrics development đẹp. Có thể chuẩn bị code/proposal độc lập; không train E004 với danh nghĩa promotion-ready khi G0–G3 chưa đóng. Approval E003 không áp dụng E004.

## Promotion gates bằng số — toàn bộ đang đề xuất

Áp dụng cùng ngưỡng đã freeze cho tất cả các gate; đề xuất lượt đầu giữ 0.5 cho cả hai target để giới hạn biến thay đổi. Unknown không vào denominator, report P/N/U và confusion đầy đủ. Gate dùng AND, không lấy macro tốt bù target yếu. Precision phụ thuộc sampling mix; chỉ kết luận trên mix/nguồn được protocol công bố, không suy precision triển khai từ challenge cân bằng.

| ID | Điều kiện trên primary holdout độc lập | Lý do đề xuất sau E003 |
|---|---|---|
| M1 | Mỗi target precision≥0.85 **và** recall≥0.80 **và** FPR≤0.10 (`FP/(FP+TN)`) | Giảm bỏ sót rõ rệt nhưng bảo vệ negative; E003 val recall phone0.529/looking0.611 chưa đáp ứng. Không phải giá trị lấy từ benchmark web. |
| M2 | AP từng target≥0.80; macro AP≥0.85 | Kiểm ranking song song operating point; AP cao không thay M1. |
| M3 | Macro masked BCE thấp hơn đối chứng hằng train-prevalence ít nhất 10%: `BCE_model ≤ 0.90×BCE_constant` | Giữ đường loss proper và đối chứng không dùng prevalence test để fit; không lấy primary development khác tập làm reference. |
| M4 | Các slice bắt buộc đã chốt trước train: desk-phone context, small/partial-phone context, looking-side/forward context, crowded context và đọc/viết/chống đầu negatives; mỗi slice ứng với target cần ≥20P và≥20N, từ ≥3group có bằng chứng. Recall≥0.70, precision≥0.80, FPR≤0.15 trên slice đủ support | Điều kiện enrollment phải dựa ngữ cảnh/geometry đã annotate trước prediction, có đối chứng N phù hợp. Không tạo positive-only slice theo nhãn rồi báo precision/FPR. Slice bắt buộc thiếu support ⇒ INCONCLUSIVE. |
| M5 | Cluster-bootstrap 95% CI: lower recall≥0.65, lower precision≥0.70, upper FPR≤0.20 cho mỗi target. Resample whole leakage groups 5.000 lần, seed42; percentile 2.5/97.5; ≥95% resamples có denominator hợp lệ cho từng metric | Kiểm độ bất định do nhiều crop cùng cảnh. Sample-level Wilson chỉ là chẩn đoán giả định iid, không thay CI nhóm. Phải pin implementation và fixture trước run; bootstrap không chứng minh provenance/session independence. |
| M6 | Benchmark classifier trên máy local đã pin: batch1, 4CPUthreads, 10warm-up, 500lượt đo trên bộ crop development đã freeze; p95≤200ms/crop, peak process RSS≤1GiB; timing gồm decode/letterbox/normalize/forward, verify hashes trước loop và startup báo riêng | Budget nghiên cứu laptop đề xuất để owner chốt, không là kết quả đã đo hoặc video latency/FPS. Count ảnh/phần xử lý, OS/CPU/Python/startup và phương pháp RSS phải công bố. |
| M7 | License/software/source use scope, restoration/checksums/model bundle và owner promotion record PASS | Binary giữ local/DVC theo quyền; Selected có experiment/config/limitations/SHA đầy đủ, không bàn giao head `best.pt` thiếu backbone. |

Không có positive predictions thì precision null ⇒ chưa đạt; missing P/N hoặc CI/support không đủ ⇒ INCONCLUSIVE, không mặc định0/PASS. Nonfinite hoặc protocol/integrity sai ⇒ run/evaluation không hợp lệ. Bootstrap CI ở đây là đề xuất thực dụng; coverage/tính đại diện cần QA riêng, không đủ chỉ vì qua số.

## Bằng chứng “bước nhảy” trong development

Đề xuất freeze một bảng đối chiếu E003 trên **đúng các crop/labels/masks vẫn giữ nguyên của val50**. Báo delta BCE/AP/P/R/FPR và FN→TP/TP→FN. Target development: recall tăng ≥0.20 phone và ≥0.15 looking, precision mỗi target không giảm quá 0.05, FPR không tăng quá 0.05; added 37 phone recall ≥0.60. Các mức này là Draft cho owner, không là bằng chứng independent improvement.

Nếu owner duyệt sửa một nhãn/crop của validation trong v7 thì version mới và report separately; đối chiếu E003 chỉ trên intersection **evaluation identity không đổi** và công bố support/ID bị loại khỏi comparison. Không xóa mẫu để làm đẹp metric, không dùng predictions E003 với label mới rồi gọi comparison cùng contract. Freeze comparator IDs trước training. Không chạy E003 trên test mới trong proposal này: một final candidate, test dùng một lần theo doc14.

## Quy tắc quyết định

1. G0–G5 đủ, training hợp lệ và development review đạt ⇒ Candidate, freeze bản duy nhất trước final test.
2. Final evaluation có đủ support/provenance và M1–M7 đều PASS ⇒ **được phép đề nghị Selected**, owner ký record; không auto-promote.
3. Gate quality thất bại ⇒ Continue/Rejected có observation. Gate evidence chưa đủ ⇒ INCONCLUSIVE/Continue, không gọi là quality PASS.
4. Sau mở test, không đổi threshold/model/metric/slice/split rồi thử lại cùng test. Artifact phải có receipt; crash/interruption ghi trạng thái, review riêng trước resume để tránh tận dụng metrics đã thấy. Model iteration dùng train/dev; test đã dùng trở thành evidence lịch sử và cần holdout mới cho final promotion lần sau.

## Owner cần chốt

Owner review high-level toàn đề xuất gate, scope promotion nghiên cứu và ngân sách; không phải annotate thủ công mọi crop. **TBD-METRIC-01**, **TBD-E004-HOLDOUT-SOURCE**, **TBD-V7-MEMBERSHIP/SPLIT**, **TBD-E004-RECIPE/COMPUTE** chỉ resolved khi có quyết định thật và exact config/evidence được pin. Bản Draft không thay quyết định Accepted hiện hữu.
