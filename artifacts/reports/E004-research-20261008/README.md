# E004 — Gói nghiên cứu và đề xuất nghiệm thu

Ngày2026-10-08; owner chủ repository. **Draft, không release/train/test/promotion approval.** Phạm vi owner chọn: classifier reviewed-crop, tìm nguồn public mới; không có holdout riêng sẵn.

- [Kết luận và kế hoạch](../../../docs/experiments/E004-preparation.md).
- [Từng FN/FP với nhận xét](e003-audit/fn-audit.md), [JSON +input pins](e003-audit/audit.json), [source/group support](e003-audit/summary.json), [nhận xét đầu vào Draft](visual-findings.json).
- [Gates ADR017 Draft](../../../docs/decisions/ADR-017-e004-classifier-promotion-gates.md).
- [Thẩm định holdout public](../../../docs/data/E004-public-holdout-research-20261008.md).
- [Plan v7](../../../configs/datasets/pilot_b_v7_targeted_plan.yaml), [plan E004](../../../configs/experiments/E004-plan.yaml). Đây không phải configs chạy; null pins giữ chưa giải quyết.

Đã audit49error cell trên48ảnh:46FNtrain/val và3FPval, đúng predictions frozen E003.6/8phone FNval là desk-phone; nhiều looking FN đầu quay rõ, nhưng12cell cần review label/crop. Val50chỉ14group, hai group chiếm64%; phone Pchỉ4group. Một train group91crop. Không kết luận causal hoặc label sai chỉ từ prediction.

Source/crop SHA và pixel context equality PASS; confusion tái lập. Mọi nhãn E003/v6 giữ nguyên. Test chỉ metadata/preservation pins, không mở ảnh/test features hoặc inference. Model metrics trong report lấy run E003 thật, không tạo predictions mới.

Media review local ignored: [thư mục](../../../outputs/E004-research-20261008/review-final),13sheets source/crop/input native-size, [SHA media](../../../outputs/E004-research-20261008/review-final/media-checksums.json). Media không commit/upload. Các bộ exploratory/review trong thư mục cha chỉ hỗ trợ lượt xem đầu; canonical render final là `training.error_audit.render_review`.

CLI tái lập (output/media mới, không ghi đè):

```powershell
$env:PYTHONPATH = 'src'
.venv/Scripts/python.exe -X utf8 -m ai_exam_monitoring.training.error_audit --run outputs/E003 --package data/processed/pilot-b/pilot-b-20261007-v6 --errors artifacts/reports/E003/error-analysis.json --findings artifacts/reports/E004-research-20261008/visual-findings.json --source-config configs/datasets/pilot_b_release_v6.yaml --output artifacts/reports/E004-audit-rebuild --media-output outputs/E004-audit-rebuild
```

Tool chỉ postprocess train/val và xác minh run checksums; không load model hoặc chạy inference. Checksum backbone/head không bị thay đổi; no overwrite guard bảo vệ report cũ. Code audit và6unit/integration tests kiểm unknown/threshold ties/test rejection/coverage/review semantics, không có mock production predictions.

Validation/checksums cuối được ghi trong `verification.json` và `checksums.json` của gói. V7/holdout/recipe/thresholds/gates vẫn cần owner nghiệm thu; chưa có public raw nào đã audit đủ để freeze test. Dừng phần liên quan tới release/train/final test tới khi quyết định và source gates đủ; các phần nghiên cứu/kiểm code độc lập đã làm.
