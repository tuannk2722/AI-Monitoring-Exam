# E002 — Kết quả thử nghiệm Pilot B v5

Trạng thái **FINISHED**, ngày 2026-10-07. Owner/reviewer: chủ repository (solo); Codex triển khai và chạy theo [ADR-015 Accepted](../decisions/ADR-015-e002-v5-preservation-linear-probe.md)/[approval](E002-approval.json). Parent: E001. [Protocol đã review](E002-protocol.md), [config giữ nguyên](../../configs/experiments/E002.yaml), [runbook](E002-runbook.md), [execution verification](../../artifacts/reports/E002-execution-20261007/README.md).

**H1 chưa được ủng hộ theo primary metric đã duyệt:** validation macro masked BCE tăng từ E001 `0.5477269888` lên E002 `0.6333627105`, delta `+0.0856357217`. AP tăng và looking cải thiện tại0.5, nhưng phone recall/F1 giảm. Không promotion, không đổi threshold hoặc retrain sau xem kết quả.

## Experiment contract và thực thi

- Giả thuyết: thêm20 crop train đã duyệt của v5, giữ recipe E001, làm giảm macro masked BCE trên cùng13validation. Biến duy nhất có chủ đích: membership train60→80; số crop/nguồn cùng thay đổi, không tách riêng hiệu ứng.
- Code commit: `082523947f5bb045622740bf6279fbc44c65130d`, **git_dirty=false**, clean detached checkout `outputs/E002-code`. Normalized code SHA `f8e58956a9918d0fddffa04ac2d59ca8da837931e0deeab0128fef4c3cacfee5`. Chỉ verifier data/freeze đổi; các runtime functions có cùng AST và training module khác cùng SHA E001.
- Dataset/split/encoding: `pilot-b-20261007-v5` / `pilot-b-v5-train-expansion-v1` / `pilot-b-targets-v1`; checksum-list SHA `2dc6a0f700c04276e8fb2b073e98fb050824d8839d398bd254b2297065f92f5a`.80train/13val/11test;93review_only/11excluded không dùng. Dataset và val/test/crop/nhãn/mask/group accepted bất biến.
- Config digest: `7ffb2807d5602aaabc2bd95d44f3c7cc58d1341ca9d6eae4deef73de949c62bf`. Frozen TorchVision ResNet18 IMAGENET1K_V1 + linear512→2; masked macro BCE, AdamW LR0.001/WD0.0001, seed42, CPU4threads, RGB letterbox224, threshold0.5 cố định. Weights SHA giữ E001; provenance/terms theo runbook E001, chỉ nghiên cứu local.
- Môi trường tái dùng đã pin: Python3.11.9 Windows, torch2.8.0+cpu, torchvision0.23.0+cpu, numpy2.4.6, Pillow12.3.0, PyYAML6.0.3, psutil7.0.0. Không tuyên bố fresh install; exact packages/pip-freeze/commands nằm trong [run record](../../artifacts/reports/E002/run.json).
- Smoke thực tế bị interrupt sau epoch1, trạng thái `INTERRUPTED`, rồi resume cùng identity đến3epoch/`FINISHED`: [trước](../../artifacts/reports/E002-execution-20261007/smoke-interrupted.json), [sau](../../artifacts/reports/E002-execution-20261007/smoke-completed.json). Smoke không dùng để chọn model/tuning.
- E002 chính chạy **27epoch**, early stopping, chọn **epoch7** bằng raw minimum validation BCE; giữ budget max200/patience20/min_delta0.0001. Bắt đầu10:52:01 và kết thúc10:52:06 (UTC+7), ngày2026-10-07. Thời gian routine `5.2674807s` gồm verify/extraction/optimization/artifacts, không gồm startup/import/setup. Peak process RSS `476192768byte` (~454.13MiB); đây là một lần đo, không benchmark tốc độ/video hoặc chứng minh nhanh hơn E001.

Ở best epoch7: train BCE `0.6381784678`, val `0.6333627105`. Epoch27: train `0.4210734069`, val `0.6608796120`; checkpoint muộn không được chọn. [History](../../artifacts/reports/E002/history.json), [learning curve](../../artifacts/reports/E002/learning-curve.svg).

## Validation và đối chứng

Chỉ known targets tính metric. Phone8known/5unknown, looking6known/7unknown trên13crop; unknown không thành negative, normal không là output thứ ba. Bảng so đúng cùng ID/nhãn/mask/crop, cùng threshold0.5, không rerun E001 hoặc dùng test metrics.

| Metric trên validation | E001 best | E002 best |
|---|---:|---:|
| Macro masked BCE, thấp hơn tốt hơn | 0.547727 | 0.633363 |
| Macro AP | 0.927296 | 0.980867 |
| Phone AP | 0.937925 | 0.961735 |
| Phone precision / recall / F1 | 0.875 / 1.000 / 0.933 | 1.000 / 0.571 / 0.727 |
| Phone TP/FP/FN/TN | 7/1/0/0 | 4/0/3/1 |
| Looking AP | 0.916667 | 1.000000 |
| Looking precision / recall / F1 | null / 0.000 / 0.000 | 1.000 / 0.333 / 0.500 |
| Looking TP/FP/FN/TN | 0/0/3/3 | 1/0/2/3 |

[Metrics đầy đủ](../../artifacts/reports/E002/metrics.json), [comparison/delta](../../artifacts/reports/E002/comparison.json), [summary/pins](../../artifacts/reports/E002/summary.json). Precision E001 looking null do không có positive prediction; không thay bằng0. Source/group slices thiếu P hoặc N giữ null/reason như implementation.

E002 đã loại phone FP trên mẫu negative duy nhất nhưng bỏ sót3/7positive, làm F1 giảm. Looking có1/3TP và0FP, cải thiện từ0TP của E001. AP là metric xếp hạng, không thay primary BCE hoặc chứng minh calibration/generalization. Tại threshold này tổng lỗi known target tăng từ4(E001) lên5(E002), có đánh đổi giữa hai target.

Constant train-prevalence baseline E002 tính từ phone17/33, looking25/63, không từ val/test: macro AP0.6875; phone TP/FP/FN/TN7/1/0/0, looking0/0/3/3. E002 tăng ranking so đối chứng hằng, nhưng phone F1 thấp hơn baseline hằng0.933. Không chọn lại threshold để sửa đánh đổi.

## Error analysis và giới hạn

Validation E002 còn5false-negative target, không false-positive known target:

| Target | ID | Score E002 | Score E001 |
|---|---|---:|---:|
| phone_use | P002-person-01 | 0.456521 | 0.641997 |
| phone_use | P006-person-02 | 0.434788 | 0.636217 |
| phone_use | P007-person-02 | 0.492163 | 0.689349 |
| looking_around | P006-extra-01 | 0.427860 | 0.376163 |
| looking_around | P007-extra-01 | 0.412696 | 0.366069 |

[Error analysis](../../artifacts/reports/E002/error-analysis.json) lưu toàn bộ train/val FP/FN, score changes trên13val và slices theo group/normal metadata; source slices trong metrics. Không relabel, thêm dữ liệu, tuning hoặc retrain sau phân tích này.

Val13crop chỉ2nhóm và nguồn confounded; phone negative chỉ1mẫu. Classroom19train cùng1nhóm, không có val/test/holdout độc lập trên nguồn đó. Co-occurrence validation chỉ1fully-known/0positive, metric vẫn null/insufficient_pilot_support. Kết quả không có ý nghĩa thống kê hoặc chứng minh giảm confounding. Validation vừa dùng chọn epoch vừa dùng so model; không gọi đây là holdout độc lập.

Test11 đã dùng E001 được kiểm integrity, **không model inference/test evaluation trong E002**. Chưa có real-world holdout hoặc numerical promotion gate; không đóng P3/P4/S9 hoặc mở runtime/tracking/web từ run này.

## Tái lập và artifact

Evaluator độc lập reload best tái lập **exact scores và metrics** trên13val: [evaluation](../../artifacts/reports/E002/validation-evaluation.json), [reproducibility](../../artifacts/reports/E002-execution-20261007/validation-reproducibility.json). Lần đầu bị từ chối approval digest vì code `read_text()` mặc định Windows đọc sai hypothesis UTF-8 tiếng Việt, trước tạo output/inference. Chạy lại bằng **`python -X utf8`** trên cùng commit/checkpoint/config thành công; không sửa code hash hoặc checkpoint để vượt guard. [Attempt record](../../artifacts/reports/E002-execution-20261007/validation-first-attempt.json).

Run local `outputs/E002`; best SHA `5c45de5d8e02ee6f48babb6c9331dced061240adbdd50c5baff1ce7b239609d8`, last giữ optimizer/RNG/early-stop epoch27. [Run artifact checksums](../../artifacts/reports/E002/run-artifact-checksums.json), [val checksums](../../artifacts/reports/E002/validation-artifact-checksums.json). Checkpoint/cache/media không commit; DVC pointers local cho baseline/smoke/val/QA. [Local cache restore](../../artifacts/reports/E002-execution-20261007/local-cache-restore.json) đối chiếu37fileSHA, không remote/fresh-cache round-trip hoặc upload.

Để tái lập, dùng exact code commit/clean checkout và environment/config/data/weights pins, output mới; trên Windows evaluator commit này cần `-X utf8`. Không rerun test hoặc thay biến trong E002. Toàn141tests/0skip, Ruff/compile/pip-check/repo checks PASS; package/candidate/artifact kiểm lại sau chạy trong execution verification.

## Nhận xét và quyết định

E002 hoàn tất kỹ thuật nhưng H1 chưa được ủng hộ theo primary đã duyệt. **Giữ kết quả nghiên cứu, không promotion hoặc thay E001 bằng E002 dựa trên AP tăng.** Recommendation: tiếp tục nghiên cứu bằng proposal mới có owner chốt; ưu tiên ranh giới nguồn/holdout độc lập và phân tích train/val đã lưu. Không chạy E003, fine-tune, calibration hoặc final test tự động trong đợt này.
