# 10 — P3 AI Baseline cho Formulation B

E001 reviewed-crop classifier đã hoàn tất ngày 2026-10-06 theo [ADR-014](decisions/ADR-014-e001-local-linear-probe.md). ResNet18 pretrained cố định + linear head hai target, masked per-target BCE, CPU local; configs và trainer/evaluator nằm trong `configs/experiments` và `src/ai_exam_monitoring/training`. [Runbook](experiments/E001-runbook.md), [kết quả và giới hạn](experiments/E001-results.md).

E002 đã hoàn tất ngày2026-10-07 theo [ADR-015](decisions/ADR-015-e002-v5-preservation-linear-probe.md): cùng recipe E001 trên v5 local,80train/13val/11test, bestepoch7/27epoch; val reload exact. Primary validation BCE tăng0.547727→0.633363 nên H1 chưa được ủng hộ, dù macroAP và lookingF1 cải thiện; phone recall giảm. [Kết quả](experiments/E002-results.md), [runbook](experiments/E002-runbook.md). Loader xác minh freeze inline v4 hoặc preservation pointer v5; không sửa accepted package hoặc mở test.141tests PASS; chưa promotion hoặc real-world holdout.

Pipeline end-to-end vẫn cần detector/weights và S9 automatic crop policy/QA trước end-to-end. Normal là metadata đã review, không thêm output thứ ba; hai target không softmax độc quyền. Ngưỡng 0.5 trong E001 là diagnostic đã duyệt, không phải ngưỡng risk hoặc acceptance.

Smoke thực tế đã kiểm interruption/resume; 126 tests PASS trong fresh CPU environment/clean commit. E001 dừng sớm ở epoch32, chọn epoch12 chỉ theo validation. Final test chạy một lần theo protocol đã commit trước evaluation; không thay model/ngưỡng sau test. Trainer không tự gọi test. Không chạy detector adapter rồi báo đó là kết quả classifier B.

Khi gate đủ: một hypothesis/run, Git/data/split/label versions, seed, resolved config, environment; lưu interruption/OOM minh bạch. Loader dùng 84 records từ manifest, không quét 112 crop/ledger; loss/metrics chỉ target known, báo support/unknown từng target và denominator co-occurrence. Model/epoch/threshold selection dùng train/val; test chỉ evaluation cuối theo freeze. Detector/crop error và runtime được đo khi triển khai end-to-end. Thresholds/metrics acceptance chưa tự đặt.

Checkpoint và metrics có thật nhưng chất lượng chưa đạt trạng thái dùng cho demo: ở0.5, looking recall=0 trên val/test; phone báo nhầm mọi negative đã biết của val/test. AP cao không chứng minh generalization trên pilot nhỏ/source-confounded. TBD-METRIC-01 và real-world holdout vẫn mở; không tự đóng toàn P3/P4 hoặc triển khai web/tracking.
