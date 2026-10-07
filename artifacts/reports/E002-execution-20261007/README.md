# E002 — Thực hiện sau owner approval

Ngày 2026-10-07. Owner đã review và approve toàn bộ hồ sơ E002, yêu cầu tiếp tục tới khi hoàn tất. [ADR-015](../../../docs/decisions/ADR-015-e002-v5-preservation-linear-probe.md), [approval hiện hành](../../../docs/experiments/E002-approval.json), [runbook](../../../docs/experiments/E002-runbook.md). [Pending snapshot trước review](approval-before-owner-review.json) giữ nguyên lịch sử; không coi trạng thái proposal cũ là blocker approval mới.

Loader đã được bổ sung verification preservation pointer v5, giữ freeze v4 và xác minh owner/parent payload, semantic val/test, manifest/ledger/split. Exact E002 configs, weights/transforms/objective/selection và dataset accepted không đổi. Thay đổi chỉ phục vụ validation trước extraction, không đổi training recipe.

**Đã hoàn tất E002 thật:** smoke interruption/resume PASS; baseline FINISHED27epoch, bestepoch7; independent validation reload exact. [Experiment card](../../../docs/experiments/E002-results.md), [summary](../E002/summary.json), [comparison](../E002/comparison.json), [metrics](../E002/metrics.json), [error analysis](../E002/error-analysis.json), [verification cuối](verification.json).

Primary val BCE0.633363 so E0010.547727, delta+0.085636: **H1 chưa được ủng hộ**. Macro AP tăng0.927296→0.980867; looking F1 tăng0→0.5, phone recall giảm1→4/7 và F1 giảm0.933→0.727. Không promotion hoặc thay threshold/retrain sau kết quả; tiếp tục nghiên cứu cần proposal mới.

Codecommit082523947f5bb045622740bf6279fbc44c65130d, clean isolated checkout; [preflight](preflight.json), [clean-checkout proof](clean-checkout.json), [smoke trước/sau](smoke-interrupted.json)/[completed](smoke-completed.json), [validation exact match](validation-reproducibility.json). Full141tests/0skip, Ruff/compile/pip/repo checks PASS. QA20trainadditions và mọi package/artifact SHA được kiểm; [DVC local restore](local-cache-restore.json) tái tạo37fileSHA, không upload.

Validation attempt đầu lỗi encoding mặc định Windows khi đọc hypothesis JSON tiếng Việt, trước tạo output/inference; [attempt](validation-first-attempt.json). Retry bằng `python -X utf8` trên exact code/candidate/config thành công, không sửa identity hoặc model. Runbook ghi rõ mode này.

Scope đã hoàn tất: approval/sửa loader/preflight/clean commit/smoke/baseline/val/erroranalysis/artifact/checksum/report. Không final-test inference, upload, Git push, model promotion hoặc E003. Test chỉ integrity; Classroom chưa có holdout độc lập. Preparation snapshot giữ trạng thái lịch sử lúc chuẩn bị, approval đã thay bằng bản hiện hành.
