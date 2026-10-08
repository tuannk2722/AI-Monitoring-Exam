# E003 — Kết quả baseline Pilot B v6

Trạng thái **FINISHED**, ngày2026-10-08. Owner/reviewer: chủ repository (solo); parent E002. Thực thi theo [ADR-016 Accepted](../decisions/ADR-016-e003-v6-local-linear-probe.md), [approval](E003-approval.json), [protocol đã review](E003-protocol.md) và [runbook](E003-runbook.md). [Bằng chứng thực thi](../../artifacts/reports/E003-execution-20261008/README.md).

**H1 được ủng hộ trong protocol phát triển:** macro masked BCE val50 **0.6107752323**, thấp hơn đối chứng prevalence train **0.6911010404**, Δ **−0.0803258081**. Không có kiểm định ý nghĩa thống kê hoặc promotion. Validation vừa chọn epoch vừa đánh giá nên kết quả không phải bằng chứng holdout độc lập.

## Experiment contract

- Giả thuyết: frozen ResNet18 linear probe trên317train v6 có BCE val50 thấp hơn đối chứng hằng tính chỉ từ known train. Giữ recipe E002 nhưng train80→317 và tập chọn epoch val13→50 cùng thay đổi; không cô lập hiệu ứng nhân quả mở rộng dữ liệu.
- Git thực thi `4e206a636024767dd86eb4e9238fd9d4642cd072`, **git_dirty=false**, clean detached `outputs/E003-code`. Normalized code SHA `f47a0d94e41e677076b17e25e25ff84ddc49afe93d445464ff08ceb9693eabfd`. Không sửa trainer/model.
- Dataset `pilot-b-20261007-v6`, split `pilot-b-v6-group-expansion-r2`, encoding `pilot-b-targets-v1`; checksum-list SHA `971e2a46c28839e0a3a13eb7f9a8eb39ed7d24fc2ce5d8225c1c64d51f563e3f`.317train/50val/11test; review_only/excluded không dùng. Test chỉ integrity.
- [Config](../../configs/experiments/E003.yaml) digest `a937009cd5d1cd9c1fbd7ba6867d79bbfe38ebbc4848eb2009b97c9ee071ca24`. ResNet18 IMAGENET1K_V1 frozen/BatchNorm eval; linear512→2 mới; RGB letterbox224; masked macro BCE, AdamW LR0.001/WD0.0001, seed42, extraction16/head full-batch317, CPU4threads, threshold0.5.
- Pretrained file local SHA `f37072fd47e89c5e827621c5baffa7500819f7896bbacec160b1a16c560e07ec`, nguồn/terms theo [runbook E001](E001-runbook.md), nghiên cứu local. Không random fallback/download/upload.
- Môi trường tái dùng Python3.11.9 Windows, torch2.8.0+cpu/torchvision0.23.0+cpu, exact closure khớp lock; [run record](../../artifacts/reports/E003/run.json) giữ environment/pip-freeze/commands. Không tuyên bố fresh install hoặc GPU.
- Smoke thực tế INTERRUPTED sau epoch1, resume cùng identity FINISHED3epoch, không chọn model từ smoke.
- Baseline bắt đầu **09:38:09**, kết thúc **09:38:39 ngày2026-10-08 (UTC+7)**. Routine29.1987723s gồm verify/extraction/optimization/artifacts, không gồm startup/import. Peak process RSS480571392byte (~458.31MiB), không benchmark video hay so tốc độ với run khác.
- Hoàn tất **64epoch**, early stopping; **best epoch45** theo raw minimum BCE val50, không theo AP/F1. Patience reference có min_delta riêng nên số epoch sau best không nhất thiết đúng20. Train BCE ở best0.4782176614, train-val gap0.1325575709. [History](../../artifacts/reports/E003/history.json), [đường loss](../../artifacts/reports/E003/learning-curve.svg).

## Kết quả validation50

Chỉ known targets tính metric; phone17P/20N/13U, looking18P/11N/21U. Normal không là output thứ ba. [Metrics trainer](../../artifacts/reports/E003/metrics.json), [đối chứng](../../artifacts/reports/E003/constant-baseline.json).

| Metric | Phone | Looking |
|---|---:|---:|
| BCE từ probability float64 | 0.594980 | 0.626570 |
| AP | 0.712507 | 0.863108 |
| Precision tại0.5 | 0.818182 | 0.916667 |
| Recall tại0.5 | 0.529412 | 0.611111 |
| F1 tại0.5 | 0.642857 | 0.733333 |
| TP/FP/FN/TN | 9/2/8/18 | 11/1/7/10 |

Macro AP0.787808. Đối chứng hằng phone93/184, looking117/229 đều trên0.5 nên dự đoán positive cho tất cả: macro AP0.540075, phoneF1=0.629630, lookingF1=0.765957. **Looking F1 E003 thấp hơn đối chứng hằng** dù BCE/AP tốt hơn; đổi lại số false positive giảm11→1, nhưng bỏ sót7positive. Không tuning threshold sau quan sát này.

Primary BCE lấy từ logits canonical; BCE probability float64 toàn val0.6107752262 chỉ khác số học khoảng6.1e−9. Slices và so historical dùng cùng đường tính probability float64, không clip. Metric thiếu positive/negative giữ null/reason; không thay null bằng0.

## Historical13 và added37

[Comparison cùng13ID](../../artifacts/reports/E003/comparison.json), [toàn bộ slices](../../artifacts/reports/E003/slices.json).

| Metric historical13 | E002 | E003 |
|---|---:|---:|
| Macro BCE probability float64 | 0.633363 | 0.413776 |
| Macro AP | 0.980867 | 1.000000 |
| Phone TP/FP/FN/TN | 4/0/3/1 | 6/0/1/1 |
| Looking TP/FP/FN/TN | 1/0/2/3 | 3/0/0/3 |
| Phone F1 | 0.727273 | 0.923077 |
| Looking F1 | 0.500000 | 1.000000 |

ΔBCE historical=−0.2195866283. Có5FN→TP và1TP→FN, còn4TP→TP/4TN→TN. Hai target cộng lại còn1lỗi thay vì5; vẫn có một positive từng đúng nay bị bỏ sót. Đây là hồi quy mô tả trên13mẫu đã dùng phát triển, không chứng minh E003 tốt hơn E002 ngoài mẫu hoặc chỉ do tăng train.

Added37: macro BCE0.662602, macro AP0.667577. Phone TP3/FP2/FN7/TN17, recall0.30/F1=0.40; looking TP8/FP1/FN7/TN7, recall0.533333/F1=0.666667. Không gọi đây là holdout vì cùng tham gia chọn epoch; không so thẳng E003 val50 với E002 val13.

## Error analysis và quyết định

[Danh sách đầy đủ FP/FN train/val](../../artifacts/reports/E003/error-analysis.json) giữ ID/source/group/target/score; slices lưu mọi source/group/normal với denominator. Train có42FP/31FN; val có3FP/15FN tính theo target, không phải số người riêng biệt.

- Classroom attitude val17: phone chỉ1/7positive được nhận diện,6FN; looking2TP/4FN, không có known negative nên metric tỷ lệ/AP target này null. Đây là nguồn yếu cần nghiên cứu tiếp.
- Exam cheating keaor val6: phone2TP/1FP/1FN/1TN; looking2TP/1FP/0FN/0TN. Support quá nhỏ để kết luận ổn định.
- Normal đã review val8: mỗi target có1FP/7TN; không có positive nên AP/F1 null. Không biến thành accuracy hay kết luận an toàn từ negative-only slice.
- Co-occurrence val16fully-known/2đồng dương; metric vẫn null theo protocol. Không đổi semantics hoặc relabel từ prediction.

**Quyết định: lưu E003 làm baseline nghiên cứu v6, không promotion.** H1 đạt nhưng phone recall của mẫu bổ sung thấp và có trade-off looking F1 với đối chứng. Chưa có real-world holdout độc lập; nhóm thị giác/source confounding, missing labels và một seed hạn chế kết luận. Không đóng P3/P4/S9 hoặc mở tracking/web. Hướng tiếp theo cần proposal mới cho phân tích lỗi/khả năng tổng quát, không tự chạy fine-tune hoặc sửa nhãn/test trong E003.

## Tái lập và bàn giao

Val evaluator reload best đạt **exact scores và metrics** trên50mẫu: [verification](../../artifacts/reports/E003-execution-20261008/validation-reproducibility.json). Fullsuite162PASS/0skip, lint/compile/pip/repo preflight PASS. Checksum outputs và dataset đã kiểm sau run; không có test feature/prediction.

Best local `outputs/E003/best.pt`, SHA `d90522fd413849593009a33bc2c5b75bbcc4e0f91233be5f887ff928fad46e67`. Last giữ optimizer/RNG/early-stop epoch64. DVC pointers [baseline](../../outputs/E003.dvc), [smoke](../../outputs/E003-smoke.dvc), [validation](../../outputs/E003-val-evaluation.dvc). Restore36files từ cache local đối chiếu SHA PASS; không remote/fresh-cache round-trip. [Summary](../../artifacts/reports/E003/summary.json) và checksums trong execution report.

Để tái lập: exact codecommit sạch, config/data/weights/environment pins, output mới và protocol runbook. Không sửa config trong identity E003, không chạy lại test. Các lần công cụ bị gián đoạn và preflight từ chối được lưu riêng; baseline không bị chạy lại để cải thiện metric.
