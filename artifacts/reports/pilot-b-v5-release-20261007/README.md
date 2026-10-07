# Pilot B v5 — bàn giao release local

Ngày 2026-10-07. **Release pilot-b-20261007-v5 đã hoàn tất theo approval owner.** [Config accepted](../../../configs/datasets/pilot_b_release_v5.yaml), [pointer và checksum](release-pointer.json), [approval](owner-approval.json), [dataset card](../../../data/processed/pilot-b/pilot-b-20261007-v5/dataset-card.md).

| Hạng mục | Số lượng |
|---|---:|
| Ledger | 208 |
| Manifest sử dụng | 104 |
| Train / val / test | 80 / 13 / 11 |
| Review-only / excluded | 93 / 11 |
| Crop xuất | 197 |

19 Classroom và EXP-RF-019 được thêm vào train. Train phone17P/16N/47U, looking25P/38N/17U;10 normal. Nhóm Classroom dành cho train;5 crop cả hai unknown vẫn review_only. Không suy208 record thành208 tình huống độc lập.

Dùng **manifest.jsonl** để train/evaluate; toàn thư mục crops còn chứa93 mẫu review_only nên không dùng nó làm danh sách training. Tất cả11 excluded không được xuất crop.

## Kiểm chứng

[Verification](verification.json) PASS: schema208, manifest104 đúng membership,197 crop SHA khớp, source/crop geometry/target/review/rights giữ nguyên so với3 package nguồn, val13/test11 không đổi ID/nhãn/crop/group/freeze,20 train mới đúng proposal,0 leakage qua image/crop/group và parent payload bất biến. Builder canonical đã kiểm source decode/dimension/label hash và crop pixel trước xuất; không sửa gate. Unknown null/mask0.

Cấu trúc version/selection/crop-policy được thống nhất cho package v5; policy mới chỉ gom provenance, không đổi geometry hoặc nhãn. V5-COMP giữ như component metadata trong group-boundaries; record tương ứng vẫn group ID null/review_only, không tự chấp nhận nhóm độc lập.

[Giữ nguyên đánh giá](evaluation-preservation.json) pin24 record val/test. Test v4 đã evaluate ở E001; lần này chỉ kiểm integrity cho packaging, không chạy model/test inference hoặc tuning.

README proposal đã được owner sửa khoảng trắng trước approval; approval pin bản hiện tại và hash lịch sử, artifact membership/config/nhóm không đổi. V4 và hai staging giữ nguyên.

## Tái tạo và phần còn lại

review-ledger.jsonl, selection.jsonl, build-inputs.json, build-metadata.json và dataset-card.md đi kèm đủ tái tạo bằng build_pilot_package vào output mới; thay card tiếng Việt rồi tính checksums.sha256 toàn payload. So SHA với release-pointer.json. Builder source/schema SHA được pin; code không thay đổi trong bước này.

Đã hoàn tất release local; chưa chạy E002/final test, chưa upload, commit hoặc push. Bước tiếp là chuẩn bị experiment config/protocol E002 để nghiệm thu riêng.93 mẫu review_only vẫn lưu evidence và lý do để review tiếp; chưa có holdout Classroom độc lập.
