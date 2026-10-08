# E003 — Đề xuất baseline trên Pilot B v6

Ngày 2026-10-08. Trạng thái **Draft — chờ owner nghiệm thu**, chưa cho phép chạy. Owner/reviewer: chủ repository (solo). Parent nghiên cứu: E002. [Cấu hình](../../configs/experiments/E003.yaml), [smoke](../../configs/experiments/E003-smoke.yaml), [approval pending](E003-approval.json), [báo cáo kiểm chứng](../../artifacts/reports/E003-preparation-20261008/README.md).

## 1. Câu hỏi và giả thuyết nghiên cứu

**H1:** Với recipe frozen ResNet18 và linear head giữ như E002, học trên 317 crop train v6 tạo ra best candidate có macro masked BCE trên 50 validation thấp hơn đối chứng dự đoán hằng bằng prevalence từng target tính chỉ từ train v6. Giả thuyết đối lập về mặt mô tả: chênh lệch BCE không âm. Đây không phải kiểm định thống kê hay gate promotion.

Cơ sở: E002 cho thấy AP tốt hơn nhưng BCE và phone recall xấu đi; mở rộng dữ liệu đã được nghiệm thu có thể bổ sung negative và ngữ cảnh hữu ích. Tuy nhiên, tăng dữ liệu không bảo đảm cải thiện. E003 cần lập baseline v6 trước khi đề xuất fine-tune, augmentation, class weighting hoặc calibration. Giữ nguyên recipe giúp tránh trộn thêm các thay đổi mô hình vào lần khảo sát này.

**Phân tích phụ đã định trước:** trên đúng 13 validation lịch sử, đối chiếu E003 với predictions E002 đã lưu, báo chênh lệch BCE/AP/confusion và các lỗi thay đổi. Đây là kiểm tra hồi quy mô tả, không phải H1 hay tiêu chí chọn epoch. E003 chọn epoch trên val50 còn E002 chọn trên val13; do đó ngay cả trên cùng 13 mẫu cũng không cô lập hiệu ứng nhân quả của mở rộng train.

Không so trực tiếp BCE/AP E003 trên val50 với E002 trên val13. Không gọi 37 val bổ sung là holdout mới độc lập: chúng thuộc tập chọn epoch. Một seed, nhiều crop cùng cảnh và validation đã được dùng phát triển không hỗ trợ tuyên bố ý nghĩa thống kê hoặc tổng quát hóa thực tế. Không chọn thêm seed/model sau xem kết quả.

## 2. Dữ liệu và ranh giới đánh giá

- Package accepted: `data/processed/pilot-b/pilot-b-20261007-v6`; split `pilot-b-v6-group-expansion-r2`; target encoding `pilot-b-targets-v1`.
- SHA của danh sách checksum payload: `971e2a46c28839e0a3a13eb7f9a8eb39ed7d24fc2ce5d8225c1c64d51f563e3f`. Release/owner/preservation pins theo [pointer v6](../../artifacts/reports/pilot-b-v6-release-20261007/release-pointer.json).
- Chỉ chọn từ manifest: train317, val50, test11. Không quét 471 crop để đưa 93 review_only vào học; 27 excluded ngoài manifest.
- Val50 gồm 13 mẫu lịch sử v5 và 37 mẫu bổ sung; danh sách ID lịch sử đóng trong `verification.json` của hồ sơ chuẩn bị. Chia slice để báo cáo, không thay membership/split.
- Giữ `[phone_use, looking_around]`, sigmoid độc lập, unknown null/mask0. `normal` là metadata đã review, không phải output thứ ba. Không relabel hay coi unknown là negative.
- Kiểm preservation toàn bộ 104 mẫu đã dùng ở v5, gồm test11/val13: ID, crop/source/group, nhãn/mask và usage. Không có image SHA/crop SHA/group đi qua split; nhóm thị giác không chứng minh độc lập subject/session hoặc hết near-duplicate.
- Test11 chỉ kiểm checksum/metadata/freeze. Bộ này đã được dùng trong E001; không inference, feature extraction, final-test hoặc tuning E003. Không mở FPI, runtime detector/crop hay holdout mới.

## 3. Recipe đề nghị nghiệm thu

| Thành phần | Đề xuất |
|---|---|
| Encoder/head | ResNet18 IMAGENET1K_V1 frozen, encoder/BatchNorm ở eval; linear512→2 khởi tạo mới seed42 |
| Weights | File local `outputs/pretrained/resnet18-f37072fd.pth`; SHA `f37072fd47e89c5e827621c5baffa7500819f7896bbacec160b1a16c560e07ec` |
| Input | RGB letterbox bilinear224; mean `[0.485,0.456,0.406]`, std `[0.229,0.224,0.225]`, fill `[124,116,104]` |
| Augmentation/sampling | Không augmentation, class weight hoặc sampling bổ sung |
| Objective | BCE trung bình theo known của từng target, sau đó trung bình hai target |
| Optimizer | AdamW, LR0.001, weight_decay0.0001; default khác theo code và môi trường đã pin |
| Batch | Extraction16; tối ưu head full-batch317, một update mỗi epoch |
| Budget | max200 epoch, patience20, min_delta0.0001; smoke3 epoch riêng |
| Threshold | 0.5 cố định để chẩn đoán; không phải ngưỡng risk/promotion |
| Compute | CPU local, 4 threads; không GPU/cloud/upload |

Không warm-start head E002. Cache train/val tạo riêng cho E003, pin ID/crop/weights/preprocessing/code/environment. Không fallback weights ngẫu nhiên hoặc tải weights khác. Giữ provenance và phạm vi nghiên cứu học thuật local đã ghi trong [runbook E001](E001-runbook.md); không mở quyền phân phối/deployment. Đây là kế thừa hồ sơ nội bộ, không thẩm định license mới.

Đề nghị tái dùng Python3.11.9 Windows và exact dependency closure [classifier-cpu-lock.txt](../../requirements/classifier-cpu-lock.txt), gồm torch2.8.0+cpu/torchvision0.23.0+cpu. Kiểm installed versions và pip check; không cài lại/tải thư viện trong bước chuẩn bị.

CPU local cần owner chốt ngoại lệ riêng E003 đối với doc22; ADR014/015 không tự cấp quyền cho E003. Sau approve, ghi decision/ADR và approval bound với resolved config/protocol đã duyệt, tạo commit local và clean isolated checkout trước chạy; không cần push theo ngoại lệ đang đề xuất. Chuẩn bị này chưa tạo commit.

## 4. Trình tự thực nghiệm sau nghiệm thu

1. Kiểm lại approval/digest, payload/schema/freeze/preservation, weights, recipe, lock/environment, clean Git/code SHA, RAM/disk và output mới. Thiếu hoặc sai pin thì dừng, không sửa accepted data để vượt gate. Chạy full suite trước baseline trong checkout thực thi.
2. Một smoke `E003-smoke`: chủ động ngắt sau epoch1, ghi INTERRUPTED/last/optimizer/RNG, resume cùng identity đến epoch3. Chỉ kiểm kỹ thuật và tính liên tục checkpoint; không dùng smoke để đổi biến/chọn candidate. Smoke chưa chạy trong hồ sơ này.
3. E003 baseline dùng head mới, seed42 và một config. Train chỉ train317, đánh giá val50 mỗi epoch. Không chọn head/seed từ smoke hoặc E002.
4. **Best = raw minimum macro masked BCE val50**, bằng nhau giữ epoch sớm. Early stopping reset stale chỉ khi giảm hơn min_delta0.0001 so reference; stale20 hoặc epoch200 thì dừng. Quy tắc best và early stopping khác nhau, giữ implementation hiện hữu.
5. Freeze best/checksums, reload evaluator trên val50 với code/config/environment giống run. Yêu cầu exact scores và metrics như trainer trong cùng môi trường; mismatch là lỗi tái lập, không chọn lại checkpoint hoặc làm tròn để thông qua.
6. Từ predictions đã freeze, lập báo cáo val50, historical13 và added37; so historical13 với E002 bằng ID/mask/crop khớp, không rerun E002 trên val50. Chỉ phân tích, không quay lại train/tuning.
7. Ghi observation/decision, kể cả khi H1 không được ủng hộ, rồi dừng ở validation.

OOM/interruption/failed giữ trạng thái thật và artifacts. Resume chỉ khi code/config/data/features/environment/identity khớp và last hợp lệ. Đổi batch/recipe/seed cần identity và proposal mới; không ghi đè hoặc âm thầm giảm budget. Không checkpoint hợp lệ thì không resume giả.

## 5. Metric, đối chứng và quy tắc kết luận

Với target c, K_c là các mẫu có mask1. `BCE_c = mean[-y*ln(p) - (1-y)*ln(1-p)]` trên K_c; primary `L = (BCE_phone + BCE_looking)/2`. Tính loss model từ logits bằng `masked_loss` canonical để ổn định số. Không gộp tất cả known cells thành một trung bình vì support hai target khác nhau.

Đối chứng: `q_c = số positive train_c / số known train_c`, cùng một q_c cho mọi mẫu val. `L_const` tính bằng công thức BCE trên đúng known val50, không dùng prevalence val/test để fit. File `verification.json` lưu support, q và BCE đối chứng bằng log tự nhiên, precision đầy đủ. Đây là thống kê nhãn có thể tính trước training, không phải metric model giả.

**Primary contrast:** `Δ = L_E003,val50 - L_const,val50`. Δ<0 là tín hiệu ủng hộ H1 trong tập phát triển này; Δ>=0 là H1 chưa được ủng hộ. Không tự đổi primary sang AP/F1 nếu BCE không cải thiện. Không đặt mức cải thiện tối thiểu hoặc diễn giải thống kê từ chênh lệch nhỏ. Nonfinite/thiếu known target/artifact không tái lập: chưa có run hợp lệ để kết luận.

Secondary: BCE từng target; AP từng target/macro AP; precision/recall/F1 tại0.5; P/N/U và TP/FP/FN/TN; train-val BCE gap ở best; epoch/budget, thời gian, peak process RSS. Dùng `evaluate_scores` canonical: AP không nội suy và gộp ties; thiếu positive hoặc negative thì AP/precision/recall/F1 null kèm reason; không positive prediction nhưng đủ P/N thì precision null, recall/F1 có thể0. Macro AP chỉ khi hai AP có nghĩa.

Trainer đã xuất BCE model toàn split và metric threshold/AP của đối chứng, nhưng **chưa xuất BCE đối chứng hoặc BCE/slices historical13/added37**. Báo cáo sau run tính BCE đối chứng theo công thức ở trên; BCE slices từ probabilities đã freeze dùng float64 và log tự nhiên, không clip ngầm. Nếu p đúng0/1 gây loss vô hạn, ghi rõ và đối chiếu logits từ checkpoint, không bịa epsilon để làm đẹp số. So historical13 với E002 bằng cùng cách tính từ predictions cho cả hai; không lấy BCE slice xác suất trừ BCE logits khác đường tính rồi gọi exact regression. Đây là postprocessing có kiểm chứng sau approve, không cần thay trainer/schema để chạy baseline.

## 6. Error analysis và giới hạn

Liệt kê mọi FP/FN known ở 0.5 trên train/val với ID, source, group, target và score. Báo source/group slices, historical13/added37, normal đã review và fully-known/co-positive support. Cho từng slice phải kèm denominator và null/reason; không chọn slice đẹp để kết luận. Historical13 join E002 bằng ID và báo TP→FN, FN→TP, FP→TN, TN→FP cùng delta score. Pin predictions/metrics E002 trước sử dụng.

Co-occurrence giữ fully-known count, positive count và metric null theo implementation `insufficient_pilot_support`; không tự đổi định nghĩa metric. Phân tích nhãn/crop sai nghi ngờ chỉ thành đề xuất dữ liệu phiên bản sau, không sửa v6 trong E003. Không đo detector mAP, tracking/event/risk hoặc video latency bằng reviewed-crop classifier.

Validation vừa chọn epoch vừa đo H1 nên lạc quan; nhiều mẫu cùng group và source confounding tiếp tục hạn chế. H1 được ủng hộ vẫn không chứng minh E003 tốt hơn E002 trên quần thể thực tế. Nếu target/slice xấu đi dù macro giảm, nêu trade-off. Không promotion, không đóng P3/P4/S9 hay mở web từ kết quả này.

## 7. Artifacts và thao tác dự kiến

Mỗi run giữ ID/owner/hypothesis/parent E002, start/end/status/commands, commit/dirty flag/code SHA, resolved config/digest, dataset/split/encoding/payload/weights pins, seed/environment/pip-freeze, best/last, optimizer/RNG, caches/checksums, history/curve, predictions/metrics, báo cáo/slices/observation/decision. Binary/media giữ local trong outputs hoặc DVC local; không upload. Không điền model metrics hoặc checkpoint SHA trước khi chạy thật.

Lệnh kiểm chuẩn bị không train (từ repository root):

```powershell
$env:PYTHONPATH = 'src'
outputs/E001-env/Scripts/python.exe -X utf8 artifacts/reports/E003-preparation-20261008/verify_preparation.py
outputs/E001-env/Scripts/python.exe -m pip check
.venv/Scripts/python.exe scripts/check_repo.py --require-git
git diff --check
```

Script kiểm chuẩn bị cố ý yêu cầu pending approval bị từ chối; là evidence trước nghiệm thu, không dùng thay preflight sau approve. Không chạy Python `-O` vì audit dùng assertions.

Lệnh **chỉ sau owner approve**, từ clean isolated checkout và dùng Python/workspace tuyệt đối:

```powershell
$env:PYTHONPATH = Join-Path (Get-Location) 'src'
$e003Python = 'D:\ai-exam-monitoring-final\outputs\E001-env\Scripts\python.exe'
$e003Workspace = 'D:\ai-exam-monitoring-final'
& $e003Python -X utf8 -m ai_exam_monitoring.training.train --config configs/experiments/E003-smoke.yaml --workspace $e003Workspace --output "$e003Workspace/outputs/E003-smoke" --interrupt-after 1
& $e003Python -X utf8 -m ai_exam_monitoring.training.train --config configs/experiments/E003-smoke.yaml --workspace $e003Workspace --output "$e003Workspace/outputs/E003-smoke" --resume
& $e003Python -X utf8 -m ai_exam_monitoring.training.train --config configs/experiments/E003.yaml --workspace $e003Workspace --output "$e003Workspace/outputs/E003"
& $e003Python -X utf8 -m ai_exam_monitoring.training.evaluate --workspace $e003Workspace --run "$e003Workspace/outputs/E003" --split val --output "$e003Workspace/outputs/E003-val-evaluation"
```

`-X utf8` tránh lỗi đọc hypothesis tiếng Việt ở evaluator Windows đã gặp E002. Không có lệnh final-test trong scope này.

## 8. Nội dung owner cần chốt

| Mục | Owner / lý do / điều kiện chốt |
|---|---|
| TBD-E003-APPROVAL | Chủ repository nghiệm thu hai config, H1/primary đối chứng hằng, các phân tích phụ và protocol theo hash trước smoke/train |
| TBD-E003-CPU | Chủ repository chấp thuận ngoại lệ CPU local/clean local commit, exact recipe/pretrained và môi trường kế thừa; không mở cloud/upload |
| TBD-METRIC-01 / holdout | Chủ repository chốt trong task riêng sau evidence và nhóm/phiên thực tế độc lập; chưa có numerical promotion gate |
| Final test | Ngoài đề xuất; nếu cần phải freeze một candidate và có protocol/approval riêng, không coi test cũ là holdout mới |

Theo AGENTS.md, “Không được tự quyết âm thầm” training variables, thresholds và acceptance metrics. Vì user yêu cầu nghiệm thu trước chạy, approval giữ pending/configs rỗng; dataset approval không thay experiment approval. Chỉ cập nhật accepted/approved khi có lời nghiệm thu thật của owner, không tạo bằng chứng phê duyệt thay owner.
