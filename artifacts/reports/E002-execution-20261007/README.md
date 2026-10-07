# E002 — Thực hiện sau owner approval

Ngày 2026-10-07. Owner đã review và approve toàn bộ hồ sơ E002, yêu cầu tiếp tục tới khi hoàn tất. [ADR-015](../../../docs/decisions/ADR-015-e002-v5-preservation-linear-probe.md), [approval hiện hành](../../../docs/experiments/E002-approval.json), [runbook](../../../docs/experiments/E002-runbook.md). [Pending snapshot trước review](approval-before-owner-review.json) giữ nguyên lịch sử; không coi trạng thái proposal cũ là blocker approval mới.

Loader đã được bổ sung verification preservation pointer v5, giữ freeze v4 và xác minh owner/parent payload, semantic val/test, manifest/ledger/split. Exact E002 configs, weights/transforms/objective/selection và dataset accepted không đổi. Thay đổi chỉ phục vụ validation trước extraction, không đổi training recipe.

Preflight thật PASS cho v4/E00184 mẫu và v5/E002104 mẫu.23 tests training/preservation PASS, gồm10 tests mới về checksum/path/approval/membership/parent freeze/ID/mask/nhãn/crop/group/malformed metadata. Ruff và dependency checker PASS. Full suite/clean checkout/smoke/baseline/validation đang thực hiện; chưa có metric E002 được điền trước run.

Tiếp theo: chốt implementation commit local và clean checkout, smoke interruption/resume, một baseline E002 và val reload; xuất metrics thật/so sánh/error analysis/checksum/decision. Không final test hoặc upload. Kết quả và verification cuối được bổ sung khi hoàn tất.
