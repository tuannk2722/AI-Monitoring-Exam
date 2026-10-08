# E003 — Bàn giao thực thi local

Ngày2026-10-08. **FINISHED** theo owner approval/[ADR-016](../../../docs/decisions/ADR-016-e003-v6-local-linear-probe.md). [Kết quả và diễn giải](../../../docs/experiments/E003-results.md), [runbook](../../../docs/experiments/E003-runbook.md), [metrics thật](../E003/metrics.json), [summary](../E003/summary.json).

## Kết quả

Smoke ngắt epoch1/resume đến3 thành công. Baseline64epoch/best45; BCE val50=0.6107752323 so constant0.6911010404, Δ−0.0803258081. H1 được ủng hộ trong tập phát triển, chưa promotion. Val reload exact. Phone recall added37 chỉ0.30; không che hạn chế bằng kết quả historical13 tốt hơn. Test11 chỉ integrity, không upload hoặc đổi dataset/recipe.

## Bằng chứng

- [Approval trước owner review](approval-before-owner-review.json); approval hiện hành ở docs/experiments. [Drift protocol](reviewed-file-drift.json) chỉ thay khoảng trắng, [attempt notes](attempt-notes.json) ghi lần đối chiếu đầu chưa đạt và preflight đầu bị chặn. Không đổi hypothesis/metric sau kết quả.
- [Preflight](preflight.json): clean commit4e206a636024767dd86eb4e9238fd9d4642cd072, config/protocol/weights/package/environment/closure, RAM/disk; pip check/Ruff/compile/repo PASS.
- [Fullsuite log](full-tests.log):162tests PASS51.460s, không skip. [Smoke interrupted](smoke-interrupted.json)/[checksums](smoke-interrupted-checksums.json), [smoke completed](smoke-completed.json); interruption là chủ đích, không đổi recipe.
- [Baseline log](baseline.log), [validation log](validation.log), [exact reload](validation-reproducibility.json). Run giữ command/environment/start/end/Git và checksum/cache. [Hậu xử lý](analyze.py) chỉ đọc predictions đã freeze; không train/select model lại.
- [DVC local restore](local-cache-restore.json):36fileSHA khớp từ shared cache vào outputs/E003-cache-restore; không network/fresh remote cache. Binary giữ local, chỉ pointer và metadata nhỏ trong Git.
- [Kiểm cuối](final-verification.json), [checksum hồ sơ bàn giao](handoff-checksums.json). Metadata E001/E002/release không sửa; proposal/preparation giữ snapshot cũ, approval mới có snapshot riêng.

## Giới hạn kiểm chứng

Full suite thực thi ở checkout sạch trong CPU environment đã có, không fresh install/Linux/GPU. Scripts báo cáo được lint và kiểm output/denominator/checksum, không thay canonical trainer. Source/group slices null khi thiếuP/N; không tuyên bố chất lượng model từ software tests. Runtime29.2s chỉ routine một lần, không benchmark end-to-end.

Auto-review hết hạn mức đã chặn lệnh kiểm trạng thái sau khởi chạy baseline; khi user resume, đọc run FINISHED rồi chạy validation, không retrain. Trạng thái approval không cần hỏi lại. Không còn blocker trong scope đã duyệt; nghiên cứu cải thiện/holdout/final test cần scope riêng.
