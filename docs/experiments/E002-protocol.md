# E002 — Protocol đề xuất cho Pilot B v5

Ngày 2026-10-07. Trạng thái **PLANNED — đề xuất, chờ owner nghiệm thu, chưa chạy**. Owner/reviewer: chủ repository (`repository-owner`, solo); Codex chuẩn bị. Parent: E001. [Cấu hình chính](../../configs/experiments/E002.yaml), [smoke kỹ thuật](../../configs/experiments/E002-smoke.yaml), [bản ghi chờ duyệt](E002-approval.json), [báo cáo và kiểm chứng](../../artifacts/reports/E002-preparation-20261007/README.md).

## 1. Câu hỏi và giả thuyết nghiên cứu

Khi chỉ bổ sung đúng 20 crop train đã duyệt của Pilot B v5, liệu linear probe với đặc trưng ResNet18 cố định có giảm lỗi dự đoán trên cùng 13 mẫu validation so với E001?

- **H1 đề xuất:** `ΔBCE = BCE_val(E002 best) − BCE_val(E001 best) < 0`, với macro masked BCE và quy tắc chọn checkpoint giống nhau.
- **H0 mô tả:** `ΔBCE >= 0`; chưa có bằng chứng cải thiện theo tiêu chí nghiên cứu này. Đây không phải kiểm định thống kê hoặc mức ý nghĩa đã được phê duyệt.
- Cơ sở dữ liệu: train phone tăng từ 11P/5N/44U lên 17P/16N/47U; looking tăng từ 17P/33N/10U lên 25P/38N/17U. Nguồn Classroom bổ sung cả positive và negative đã review, có thể thay đổi cách head sử dụng đặc trưng. Hiệu quả cần đo, không giả định trước.
- Biến duy nhất có chủ đích là **membership train**: 60 → 80, gồm 19 Classroom và EXP-RF-019. Không tách hiệu ứng tăng số crop khỏi hiệu ứng nguồn/nhãn bằng thiết kế này; không suy thêm 20 tình huống độc lập.

E001 đối chứng là artifact đã hoàn tất, không retrain hoặc chọn lại epoch từ lịch sử: best epoch12, validation BCE `0.5477269887924194`, macro AP `0.9272959183673469`. Phone ở 0.5 có TP/FP/FN/TN = 7/1/0/0; looking = 0/0/3/3. Nguồn đối chứng: [metrics train/val](../../artifacts/reports/E001/metrics.json), [resolved config](../../artifacts/reports/E001/resolved-config.json), [run record](../../artifacts/reports/E001/run.json). Chỉ lấy trường `val`, không dùng metrics test để thiết kế hoặc chọn model.

Validation dùng để chọn epoch rồi so E001 nên kết quả là tín hiệu phát triển trên dữ liệu đã dùng lại, có selection bias; không phải ước lượng khái quát độc lập. Không đặt khoảng tin cậy từ bootstrap crop hoặc kết luận có ý nghĩa thống kê với hai nhóm validation.

## 2. Dataset và ranh giới đánh giá

[Release accepted](../../configs/datasets/pilot_b_release_v5.yaml): `data/processed/pilot-b/pilot-b-20261007-v5`; dataset version `pilot-b-20261007-v5`; split `pilot-b-v5-train-expansion-v1`; encoding `pilot-b-targets-v1`. SHA-256 của **file danh sách checksum**: `2dc6a0f700c04276e8fb2b073e98fb050824d8839d398bd254b2297065f92f5a`. Đây là `payload_sha256` theo convention trainer; vẫn phải kiểm từng file trong danh sách.

| Split | Crop trong manifest | Nhóm đã duyệt | Phone P/N/U | Looking P/N/U | Vai trò |
|---|---:|---:|---|---|---|
| train | 80 | 12 | 17/16/47 | 25/38/17 | Fit head, tính prevalence đối chứng |
| val | 13 | 2 | 7/1/5 | 3/3/7 | Early stopping, chọn checkpoint, so sánh E001 |
| test | 11 | 3 | 2/2/7 | 2/7/2 | Chỉ integrity ở bước chuẩn bị; chưa cấp quyền inference |

Manifest có 104 mẫu; ledger208, review_only93, excluded11, crop197. Loader chọn theo `manifest.jsonl` và usage, không quét thư mục `crops/` chứa cả review_only. Mọi train record phải có ít nhất một target known; excluded không có crop xuất. Normal là metadata đã review, không có output thứ ba. Unknown giữ `null`/mask0, không thành negative.

Giữ nguyên ID/source hash/crop hash/geometry/target/mask/group của cả 24 mẫu val/test v4. Dataset/split/crop-policy version của package v5 thay đổi do packaging, nên không yêu cầu toàn bộ manifest v4/v5 bằng byte. Reference freeze từng record test vẫn `release.json#test_freeze`; phần đó trong release v5 trỏ evidence riêng thay vì inline hashes kiểu E001. Kiểm semantic preservation theo [evidence đã duyệt](../../artifacts/reports/pilot-b-v5-release-20261007/evaluation-preservation.json). Mọi checksum/metadata của package accepted giữ nguyên; không thêm trường freeze vào package cũ để ép loader chạy.

Nhóm `CM-V2-SCENE-01` chỉ thuộc train; 19 crop vào manifest, 5 crop cả hai unknown ở review_only. EXP-RF-019 nằm trong nhóm train có sẵn. Hai nhóm val và ba nhóm test không chứa Classroom. Val có phone positive từ Roboflow và negative từ SCB; looking cũng phân bố positive/negative theo nguồn. So sánh này chưa chứng minh giảm source confounding hoặc khái quát trên Classroom.

Test v4 đã evaluate ở E001; không gọi là holdout chưa nhìn. Không xem media test, extract features test hoặc đọc metrics test trong E002 preparation/smoke/train/validation. Hash bytes và metadata test chỉ phục vụ integrity. Holdout thực tế độc lập là task sau với version/group và approval riêng; không chia 150 ảnh Classroom hiện có thành holdout mới.

## 3. Cấu hình kiểm soát và môi trường đề nghị

Các giá trị dưới đây là **đề xuất cho E002**, kế thừa đối chứng để cô lập biến dữ liệu; ADR-014 chỉ accepted cho E001 và không cấp quyền E002.

| Thành phần | Đề xuất E002 |
|---|---|
| Encoder/head | TorchVision ResNet18 IMAGENET1K_V1 cố định, chế độ eval; linear 512→2 trainable, sigmoid độc lập |
| Weights | Dùng file local đã pin `outputs/pretrained/resnet18-f37072fd.pth`; SHA `f37072fd47e89c5e827621c5baffa7500819f7896bbacec160b1a16c560e07ec` |
| Preprocessing | RGB letterbox bilinear224, giữ toàn crop; mean `[0.485,0.456,0.406]`, std `[0.229,0.224,0.225]`, fill `[124,116,104]`; không augmentation |
| Loss | Trung bình hai BCE theo từng target known; không class weight hoặc sampling mới |
| Optimizer | AdamW; learning_rate0.001; weight_decay0.0001; các default khác giữ implementation/environment đã pin |
| Seed/budget | seed42; tối đa200 epoch; patience20; min_delta0.0001 |
| Batch/CPU | Feature extraction batch16, threads4, CPU; head cập nhật full-batch80 mỗi epoch, không nhầm batch16 là optimizer batch |
| Threshold | 0.5 cố định, chẩn đoán; không tuning hoặc calibration, không phải ngưỡng risk/promotion |
| Môi trường | Python3.11.9 Windows; torch2.8.0+cpu, torchvision0.23.0+cpu; cùng closure E001 nếu kiểm tra khớp |

Không warm-start head E001; khởi tạo head mới bằng seed42. Cache E001 không tái dùng trong output E002; cache mới pin ID/crop/weights/code/preprocessing/environment. Không tải weights mới hoặc fallback sang weights random.

[Lockfile E001](../../requirements/classifier-cpu-lock.txt) là đề xuất tái dùng cho E002 sau review, không đổi nhãn approval của file lịch sử. Provenance/terms weights theo [runbook E001](E001-runbook.md) và [receipt local](../../outputs/pretrained/receipt.json): license phần mềm và quyền pretrained được ghi riêng; đề nghị cùng phạm vi nghiên cứu học thuật local, không tự mở quyền phân phối/deployment.

Đề nghị owner chấp nhận CPU local cho frozen linear probe này như một ngoại lệ riêng bổ sung cho E002 đối với hướng Colab/GPU của doc22; không mặc định kế thừa ngoại lệ E001. Sau nghiệm thu cần checkpoint/config/protocol/approval trong một Git commit sạch, checkout đúng commit để chạy; không yêu cầu push hoặc cloud cho ngoại lệ local đề xuất. Chưa tạo commit trong bước chuẩn bị.

## 4. Protocol train và chọn candidate

1. Ghi approval E002 theo resolved config digest và protocol đã nghiệm thu; kiểm package, weights, code, environment, khả năng loader, disk/RAM và output đích còn mới. Không chạy khi blocker freeze chưa được giải quyết.
2. Sau duyệt, chạy một smoke riêng `E002-smoke`, max3 epoch, đúng dataset/weights/train/val. Chủ động interruption sau epoch1 rồi resume cùng identity đến epoch3 để kiểm checkpoint/RNG/optimizer/checksums. Smoke chỉ kiểm kỹ thuật; không chọn candidate hoặc thay tham số từ metrics smoke. Lỗi phải được báo và xử lý trước baseline.
3. Chạy E002 chính từ head mới, output mới `outputs/E002`, đúng một config/seed; không sweep model/LR/threshold/seeds. Mỗi epoch một optimizer update full-batch train; encoder/BatchNorm cố định; loss/metrics bỏ unknown theo từng target.
4. **Chọn best bằng minimum validation macro masked BCE thô**; bằng nhau giữ epoch sớm hơn. Không chọn bằng AP/F1 hoặc train loss. Early stopping có reference riêng: val BCE phải giảm hơn min_delta0.0001 để reset stale; dừng khi stale20 hoặc epoch200. Best có thể thay đổi khi giảm nhỏ hơn min_delta; không nhầm hai quy tắc.
5. Trainer ghi train/val metrics và predictions của best. Eval độc lập trên val bằng cách reload best; so từng score và metrics với report của trainer. Mismatch là lỗi tái lập, không chọn lại checkpoint hoặc làm tròn để coi khớp.
6. So E001/E002 đúng cùng 13 ID/mask/crop và threshold0.5. Ghi delta metric và các thay đổi TP/FP/FN/TN, không chỉ tỷ lệ tổng. Bàn giao kết luận rồi dừng; không gọi test từ trainer hoặc thêm test vào loop.

OOM/interruption giữ trạng thái `OOM`/`INTERRUPTED`/`FAILED`, không đổi batch/config trong cùng run. Chỉ resume khi last checkpoint hoàn chỉnh và code/config/payload/features/environment khớp; không có checkpoint thì tạo identity/output mới và báo owner. Config hoặc biến nghiên cứu mới cần một proposal/run identity mới, không ghi đè E002 để tối ưu trên val đã dùng.

## 5. Metrics, denominator và error analysis

Primary đề xuất: validation `macro_masked_bce`, thấp hơn tốt hơn. Với target c và tập K_c có mask1, tính BCE trung bình trên K_c, sau đó lấy trung bình hai target; không trung bình tất cả known cells làm lệch trọng số target. Val phone K=8, looking K=6. Không đưa unknown hoặc normal như lớp thứ ba vào loss.

Secondary mô tả, không chọn lại epoch: AP từng target và macro AP; precision/recall/F1 ở0.5; TP/FP/FN/TN và P/N/U; train-val gap ở best; epoch/budget, thời gian và peak process RSS. AP dùng thuật toán không nội suy, gộp các score bằng nhau trước cập nhật precision/recall theo implementation hiện có. Macro AP chỉ có khi cả hai AP có nghĩa.

Theo implementation canonical: khi thiếu P hoặc N, AP/precision/recall/F1 là `null` kèm reason; khi không có positive prediction nhưng đủ P/N, precision là `null`, recall/F1 có thể0. Không bịa0 cho metric không xác định. Với mỗi slice phải in support và confusion dù metric null; không dùng macro AP để che target yếu.

Đối chứng phụ `constant_train_prevalence` tính riêng từng target từ known train của mỗi version, không từ val/test: E002 phone17/33, looking25/63; E001 phone11/16, looking17/50. Báo delta so E001 và so baseline prevalence của E002. Baseline này là thống kê train, không phải fake model prediction.

Error analysis chỉ train/val: tất cả FP/FN của best tại0.5, ID/source/group/known target/score và delta score so predictions validation E001 đã lưu; tách Roboflow/SCB, normal đã review và co-occurrence. Source slices do trainer đã xuất; group/normal slices là báo cáo từ predictions đã freeze, không loop chọn model. Không relabel, chọn thêm dữ liệu hoặc tuning E002 sau xem lỗi; việc đó thuộc proposal sau.

Co-occurrence chỉ báo fully-known denominator và positive count; val chỉ1 fully-known,0 đồng dương. Metric co-occurrence giữ `null`/`insufficient_pilot_support`; không tuyên bố đã đánh giá khả năng đồng xuất hiện. Không tính detector mAP, tracking/events/risk, video latency hoặc end-to-end metrics cho reviewed-crop classifier.

## 6. Quy tắc kết luận nghiên cứu đề xuất

| Quan sát trên val cố định | Kết luận dự kiến |
|---|---|
| ΔBCE<0 | Tín hiệu ủng hộ H1 trong protocol phát triển này; ghi đầy đủ per-target/slices và trade-off AP/F1 |
| ΔBCE>=0 | H1 chưa được ủng hộ; lưu kết quả và đề xuất nghiên cứu tiếp theo, không sửa E002/test để đạt tiêu chí |
| Primary null/nonfinite hoặc artifact/score không tái lập | Run không hợp lệ để kết luận; điều tra lỗi kỹ thuật |
| Một target hoặc slice xấu đi dù primary giảm | Ghi trade-off; không che bằng macro hoặc tự promotion |

Đây là tiêu chí nghiên cứu **đề xuất chờ review**, không có yêu cầu số tối thiểu để promotion. `TBD-METRIC-01` vẫn mở, owner chốt sau evidence validation và holdout độc lập. E002 hoàn tất kỹ thuật không đồng nghĩa đóng P3/P4/S9, model sẵn sàng demo hoặc mở web/tracking.

## 7. Test freeze và nghiệm thu tiếp theo

Đề xuất hiện tại chỉ xin nghiệm thu chuẩn bị/smoke/train/validation local, **không xin quyền final test**. Không tạo file `E002-final-test-protocol.json` với checkpoint hash giả.

Nếu owner muốn final test sau này: freeze đúng một best candidate bằng checkpoint SHA, resolved config digest, normalized code SHA, payload/checksum/manifest/split/test-ID SHA, threshold0.5, Git commit, environment và decision reference; lập protocol riêng tương thích evaluator rồi owner duyệt. Test cũ chỉ là kiểm tra hồi quy trên bộ đã dùng E001; không nâng thành holdout độc lập. Nếu được duyệt, evaluate một lần; không tune/chọn biến hoặc retrain dựa trên test. Candidate/threshold mới không được thử lặp trên bộ này.

| TBD | Owner | Lý do / điều kiện chốt |
|---|---|---|
| TBD-E002-APPROVAL | Chủ repository | Nghiệm thu E002/E002-smoke, giả thuyết, metrics, CPU local và protocol theo hash; hiện status pending |
| TBD-E002-LOADER | Chủ repository nghiệm thu; Codex thực hiện sau khi thống nhất phạm vi | `verify_dataset` E001 đòi inline freeze nhưng v5 pin preservation pointer; phải giải quyết và kiểm tamper/fail-closed trước chạy |
| TBD-E002-TEST | Chủ repository | Chỉ xem xét sau freeze một candidate và protocol test riêng; không thuộc approval chuẩn bị |
| TBD-METRIC-01 / holdout | Chủ repository | Promotion gate và nhóm/phiên thực tế độc lập chưa có quyết định; không bịa threshold từ pilot |

## 8. Blocker loader và hướng xử lý đề nghị

Kiểm trực tiếp trên package đã pin tái lập `KeyError: 'status'` trong `training.data.verify_dataset`: code đòi `test_freeze.status=frozen`, manifest/split/test-subset hashes và danh sách ID inline. V5 hiện có `{path, sha256}` tới `evaluation-preservation.json`, trạng thái preservation nằm ở evidence riêng. Đây là xung đột code với artifact release accepted; YAML hợp schema không giải quyết được nó.

Đề nghị một sửa đổi hẹp ở loader, giữ package accepted bất biến: hỗ trợ có phân biệt format inline v4 và preservation pointer v5; xác minh containment/path/SHA của pointer và owner approval, parent payload/freeze, cùng ID/nhãn/mask/source/crop/geometry/group/freeze semantics, manifest/ledger/split consistency và leakage hiện hành. Pointer thay đổi, thiếu evidence hoặc semantic khác phải từ chối bằng lỗi contract rõ ràng. Cần regression v4 và tamper tests v5; không catch KeyError rồi bỏ freeze gate. **Chưa triển khai sửa loader trong task đề xuất này**; scope cụ thể và implementation phải được review trước khi chạy, không tự thay persistence contract để làm E002 chạy.

## 9. Artifact bắt buộc và lệnh sau nghiệm thu

Run phải giữ owner/hypothesis/parent reference (ở experiment card), Git commit/dirty state, resolved config, dataset/split/encoding/payload và weights pins, code provenance/environment/pip-freeze, command/start/end/status, seed, best/last checkpoint, feature cache receipts, history/curve, train/val metrics/predictions, observation/decision và checksums. Binary/media nằm local trong outputs hoặc DVC local; không upload, commit media hoặc coi quyền storage v4 là quyền upload E002/v5.

Trước chạy, đối chiếu training modules với E001 provenance; sửa loader phải ghi code SHA mới và chứng minh preprocessing/objective/selection không đổi. Nếu thay môi trường/model recipe, không còn thiết kế chỉ đổi dữ liệu và phải review lại. Sau run xuất báo cáo metrics thật theo [template experiment](../templates/experiment-template.md); không điền metric/elapsed/checkpoint giả trước chạy.

Các lệnh sau chỉ là protocol dự kiến, **chưa thực thi**; chỉ dùng khi E002 được owner duyệt, blocker được kiểm xong và đang ở clean code checkout. `--workspace` chỉ tới workspace local chứa package/weights/approval; `--config` lấy đúng checkout.

```powershell
$env:PYTHONPATH = Join-Path (Get-Location) 'src'
outputs/E001-env/Scripts/python.exe -m ai_exam_monitoring.training.train --config configs/experiments/E002-smoke.yaml --output outputs/E002-smoke --interrupt-after 1
outputs/E001-env/Scripts/python.exe -m ai_exam_monitoring.training.train --config configs/experiments/E002-smoke.yaml --output outputs/E002-smoke --resume
outputs/E001-env/Scripts/python.exe -m ai_exam_monitoring.training.train --config configs/experiments/E002.yaml --output outputs/E002
outputs/E001-env/Scripts/python.exe -m ai_exam_monitoring.training.evaluate --run outputs/E002 --split val --output outputs/E002-val-evaluation
```

Nếu chạy từ checkout riêng, dùng đường dẫn tuyệt đối Python của môi trường local và `--workspace D:\ai-exam-monitoring-final`; các output cũng chỉ tới `D:\ai-exam-monitoring-final\outputs\...`. Environment/Git provenance phải phản ánh checkout thực tế. Không chạy lệnh pip/download hoặc test inference để nghiệm thu cấu hình.

Lệnh kiểm không huấn luyện có thể tái lập blocker hiện tại (đặt PYTHONPATH tới src, dùng môi trường E001 có Torch):

```powershell
outputs/E001-env/Scripts/python.exe -c "from pathlib import Path; from ai_exam_monitoring.training.config import load_config; from ai_exam_monitoring.training.data import verify_dataset; c=load_config('configs/experiments/E002.yaml'); verify_dataset(Path(c.dataset), c)"
.venv/Scripts/python.exe scripts/check_repo.py --require-git
git diff --check
```

`verify_approval` phải tiếp tục từ chối bản ghi pending. Chỉ sau owner nghiệm thu mới tạo snapshot approval theo digest hiện hành; mọi thay đổi substantive config/protocol sau review phải được chốt lại, không tự đổi `pending` thành `approved`.
