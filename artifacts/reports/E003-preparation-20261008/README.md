# E003 — Hồ sơ chuẩn bị để owner nghiệm thu

Ngày 2026-10-08. **Hoàn tất chuẩn bị; đề xuất chưa được duyệt chạy.** Không train, smoke hoặc inference trên dữ liệu thật; không upload hay sửa release. Owner/reviewer: chủ repository (solo).

Đọc [protocol chi tiết](../../../docs/experiments/E003-protocol.md), [config chính](../../../configs/experiments/E003.yaml), [config smoke](../../../configs/experiments/E003-smoke.yaml) và [approval pending](../../../docs/experiments/E003-approval.json). Các liên kết trong báo cáo tính từ thư mục này.

## Đề xuất nghiệm thu

Giữ recipe E002: frozen ResNet18 IMAGENET1K_V1 + linear512→2 khởi tạo mới, masked macro BCE, AdamW LR0.001/WD0.0001, seed42, RGB letterbox224, CPU4threads. Extraction batch16; head full-batch317. Max200 epoch, patience20/min_delta0.0001, best bằng minimum BCE val50, ties giữ sớm. Threshold0.5 cố định. Một smoke3 epoch có interruption/resume sau approve, rồi một baseline và reload validation.

**H1:** BCE E003 trên val50 thấp hơn đối chứng hằng dùng prevalence từng target từ train317. Đối chứng có BCE **0.6911010403687807**, tính từ nhãn; chưa có BCE của mô hình E003. Δ<0 chỉ là tín hiệu trong tập phát triển, không có ngưỡng promotion hoặc kiểm định thống kê.

Val đã tăng13→50, nên không so metric toàn val50 trực tiếp với E002/val13. So hồi quy E003–E002 trên đúng13ID lịch sử là phân tích phụ; 37val bổ sung báo riêng. Cả hai slice vẫn thuộc tập chọn epoch, không là holdout độc lập. Việc tăng train80→317 và đổi tập chọn epoch cùng xảy ra, không cô lập hiệu ứng tăng dữ liệu.

## Support đã kiểm từ manifest

P/N/U là positive/negative/unknown. Unknown bỏ khỏi loss và metric của target tương ứng.

| Tập | Crop / nhóm | Phone P/N/U | Looking P/N/U | Fully-known / đồng dương |
|---|---|---|---|---|
| Train v6 | 317 / 103 | 93/91/133 | 117/112/88 | 96/16 |
| Validation v6 | 50 / 14 | 17/20/13 | 18/11/21 | 16/2 |
| Val lịch sử | 13 / 2 | 7/1/5 | 3/3/7 | 1/0 |
| Val bổ sung | 37 / 13 | 10/19/8 | 15/8/14 | 15/2 |

Hai slice val có một group chung, nên số group không cộng thành15 nhóm độc lập. Group là ranh giới thị giác đã duyệt, không bằng chứng độc lập subject/session. Train prevalence: phone93/184, looking117/229. Validation không có nguồn classroom_monitoring_v2; source confounding và thiếu holdout thực tế vẫn còn. Co-occurrence metric giữ null theo implementation; chỉ báo support.

## Kết quả kiểm hợp lệ

[Verification máy đọc](verification.json), [script tái lập](verify_preparation.py), [kết quả lệnh](validation-commands.json), [pins hồ sơ](proposal-checksums.json).

| Kiểm tra | Kết quả / phạm vi |
|---|---|
| Strict config + recipe | PASS; E003 giữ toàn bộ biến recipe E002, khác identity/hypothesis/approval và dataset/split/payload |
| Loader v6 và parent v5 | PASS; checksum/schema/manifest-ledger-split/freeze; không cần sửa trainer/loader |
| Preservation | PASS;104 mẫu v5 giữ crop/source/group/nhãn/mask/usage, gồm13val/11test |
| Leakage theo identity | PASS; không image SHA/crop SHA/group qua split; không chứng minh hết near-duplicate |
| Weights + environment | PASS; SHA pretrained khớp; Python3.11.9 và installed closure khớp lock CPU, pip check sạch |
| Approval guard | PASS; cả E003/E003-smoke bị từ chối khi pending, configs approved rỗng |
| Regression phần mềm | 23 tests training/preservation PASS, không skip; chỉ fixture tổng hợp, không chạy E003 |
| Ruff / repository | PASS; checker repository chỉ kiểm Git index, không bao gồm untracked; file mới được audit riêng |

Weights local SHA `f37072fd47e89c5e827621c5baffa7500819f7896bbacec160b1a16c560e07ec`; payload-list v6 SHA `971e2a46c28839e0a3a13eb7f9a8eb39ed7d24fc2ce5d8225c1c64d51f563e3f`. Predictions E002 lịch sử có pin và kiểm ID/target/mask trong verification; không rerun E002.

Git nền `9c85299ce5d0205d56073aaf55d7e097485cfd54`; hồ sơ là thay đổi chưa commit. Chưa có clean execution checkout, smoke v6, kết quả quality/model hoặc kiểm hiệu năng E003. Những bước này chỉ thực hiện sau owner approve; full suite và preflight phải kiểm lại trong checkout thực thi. Môi trường tái dùng, không tuyên bố fresh install.

## Nội dung cần owner chốt

Nghiệm thu một gói: hai YAML, H1/primary đối chứng hằng, đánh giá val50 + hai slice, giữ test11 chỉ integrity, và ngoại lệ CPU local với recipe/pretrained/môi trường nêu trên. Quyền sau nghiệm thu dự kiến gồm local commit/clean checkout, smoke/resume, một baseline và validation/report; không upload/final test/promotion.

Việc chờ nghiệm thu đúng yêu cầu user và AGENTS.md về không tự chốt training variables/thresholds/metrics. Approval dataset v6 đã đủ; không yêu cầu duyệt lại dữ liệu hoặc quyền nguồn. Promotion gate/holdout vẫn TBD riêng, không ngăn owner nghiệm thu baseline phát triển này. Không tự chuyển pending thành approved hoặc ghi lời phê duyệt thay owner.
