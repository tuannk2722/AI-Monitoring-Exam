# 00 — Documentation Index

Snapshot owner R1–R3 của Roboflow: [crop ngữ cảnh và target labels](data/candidates/Roboflow-phone-use-20261004-review.md),28 bbox/crop đã duyệt. Approval training cho subset pilot hiện hành nằm trong release local bên dưới; snapshot lịch sử không sửa.

## Trạng thái hiện tại

[E002 đã được owner duyệt, đang triển khai](../artifacts/reports/E002-execution-20261007/README.md): [ADR-015 Accepted](decisions/ADR-015-e002-v5-preservation-linear-probe.md), [config v5](../configs/experiments/E002.yaml), [protocol](experiments/E002-protocol.md), [approval](experiments/E002-approval.json), [runbook](experiments/E002-runbook.md). Loader đã hỗ trợ freeze preservation v5; preflight v4/v5 và tamper tests PASS, đang hoàn tất full suite/clean checkout trước smoke/train/validation. Final test không thuộc approval này; [preparation snapshot](../artifacts/reports/E002-preparation-20261007/README.md) giữ lịch sử.

**Release hiện hành: [pilot B v5 local đã nghiệm thu](../artifacts/reports/pilot-b-v5-release-20261007/README.md)**, [config accepted](../configs/datasets/pilot_b_release_v5.yaml), [pointer/checksum](../artifacts/reports/pilot-b-v5-release-20261007/release-pointer.json). Package `data/processed/pilot-b/pilot-b-20261007-v5`:208 ledger,104 manifest(80 train/13 val/11 test),93 review_only,11 excluded,197 crop. Thêm19 Classroom +RF-019 vào train; val/test giữ nguyên v4. Verification PASS; chưa chạy E002/final test hoặc upload. [Proposal lịch sử](../artifacts/reports/pilot-b-v5-proposal-20261007/README.md) được bảo toàn.

Snapshot lịch sử: owner đã approve phương án và hoàn tất [release pilot B local v4](../artifacts/reports/pilot-b-release-acceptance-20261005/README.md). Canonical `data/processed/pilot-b/pilot-b-20261005-v4`,config `pilot_b_release_v4.yaml`,status accepted/local_classifier_research:112 ledger/crops, 84 manifest(60 train/13 val/11 test),16 nhóm;28 review_only. Test đã freeze; hash QA và DVC round-trip PASS, checkout bàn giao v4 đạt109 tests PASS (suite E001 hiện tại126). [Approval](../artifacts/reports/pilot-b-release-acceptance-20261005/owner-approval.json),[runbook](data/pilot-b-preparation-v1.md).

Toàn ledger phone 24P/9N/79U,looking 33P/56N/23U,9 normal và1 co-occurrence;crop/source/known approvals cũ giữ nguyên. Used84 phone 20P/8N/56U,looking 22P/43N/19U,8 normal. Nguồn phone còn confounding,val/test support nhỏ. [E001 đã chạy](experiments/E001-results.md): baseline reviewed-crop có metrics thật; chưa có real-world holdout hoặc model promotion.

Owner đã duyệt hướng mở rộng dữ liệu sau E001 (hai luồng SCB/RF + nguồn mới, thẩm định metadata Classroom-monitoring-dataset, draft v5 sau candidate, giữ semantics): [kiểm kê và phương án](data/data-expansion-20261006.md), [inventory metadata](../artifacts/reports/data-expansion-20261006/inventory.json), [hàng đợi review-only](../artifacts/reports/data-expansion-20261006/review-queue.json), [sàng lọc nguồn](../artifacts/reports/data-expansion-20261006/source-research.json). [Approval và draft ban đầu](../artifacts/reports/data-expansion-20261006/README.md) giữ nguyên. Sau owner approve tiếp tục: [báo cáo R2](../artifacts/reports/data-expansion-20261006-r2/README.md), [pointer v5 R2](../configs/datasets/pilot_b_expansion_v5_r2_draft.yaml) có 72 candidate mới(48SCB/24RF),đề xuất giữ61/loại11 anchor,2 crop RF sửa vàb11 liên hệ cảnh;28 review_only parent tiếp tục chờ group. Owner đã nghiệm thu R2 và xác nhận toàn quyền sử dụng dataset đang dùng. [Staging R2 hoàn tất](../artifacts/reports/data-expansion-staging-20261006-r2/README.md): 72 record mới, 61 review_only/crop, 11 excluded; nhãn/crop và 11 liên hệ cảnh đã duyệt, QA PASS. [Pointer staging](../configs/datasets/pilot_b_expansion_v5_r2_staging.yaml). Chưa split/release v5 hoặc train. Classroom-monitoring v2 đã tiếp nhận ZIP và hoàn tất [báo cáo nghiệm thu ngày 2026-10-07](../artifacts/reports/classroom-v2-20261007/README.md): 150 ảnh/750 bbox,24 crop draft (phone6P/10N/8U; looking7P/5N/12U), đề xuất gộp150 ảnh thành một nhóm chống rò rỉ; verification PASS. Owner đã duyệt 24 crop/nhãn và gộp150 ảnh thành nhóm CM-V2-SCENE-01. [Staging Classroom hoàn tất](../artifacts/reports/classroom-v2-staging-20261007/README.md):24 record/crop review_only, nhãn/group đã nhập, verification PASS; [pointer](../configs/datasets/classroom_monitoring_v2_staging.yaml). Chưa split/release/train; không mở lại quyền đã xác nhận.

Ngày cập nhật: 2026-10-07. Owner: chủ repository (solo). DVC đã cấu hình; smoke và v4 push/pull/cache sạch đạt. V4 lưu trên teamdrive restricted theo yêu cầu owner; ACL chỉ user/owner đã kiểm. Implementation, pointer và smoke cleanup đã commit; clone/cache thử đã dọn, bằng chứng theo [runbook](data/pilot-b-preparation-v1.md)/[WORKLOG](WORKLOG.md). E001 trainer/model/config, smoke/resume và final evaluation đã hoàn tất theo ADR-014;126 tests PASS trong fresh CPU environment/clean commit. Crop runtime S9 và quality/promotion gates vẫn mở; P0/P1/P2 toàn dự án chưa tự đóng.

`Accepted` = implementation contract (hợp đồng triển khai); `Draft` = hướng dẫn đang hoàn thiện; `TBD` = không được tự bịa giá trị.

| File | Status | Nội dung |
|---|---|---|
| `01-project-overview.md` | Accepted | Product mode, actor, processing mode |
| `02-scope-and-principles.md` | Accepted | MVP/non-goal/thứ tự ưu tiên |
| `03-system-architecture.md` | Accepted | Ranh giới hệ thống và formulation B đã chọn |
| `04-behavior-and-label-strategy.md` | Draft | Taxonomy candidate; đóng băng tại P1 |
| `05-roadmap-and-timeline.md` | Accepted | P0–P9 entry/exit gate |
| `06-team-collaboration-and-git.md` | Accepted | Workflow solo, owner tự review/chốt, artifact handoff |
| `07-phase-p0-project-foundation.md` | Accepted | Foundation DoD |
| `08-phase-p1-dataset-research.md` | Active | SCB5 + Roboflow audit |
| `09-phase-p2-dataset-preparation.md` | Draft | DVC/canonical dataset |
| `10-phase-p3-ai-baseline.md` | Draft | Baseline run contract |
| `11-phase-p4-model-improvement.md` | Draft | Evidence-driven loop |
| `12-phase-p5-p6-tracking-events-risk.md` | Draft | P5/P6 contract, không có fake implementation |
| `13-phase-p7-web-dashboard.md` | Draft | FastAPI web sau khi core ổn định |
| `14-phase-p8-p9-evaluation-demo-report.md` | Draft | Protocol/demo/report |
| `15-ml-experiment-management.md` | Accepted | YAML + W&B tùy chọn + DVC artifact |
| `16-ai-agent-guidelines.md` | Accepted | Ranh giới agent |
| `17-task-and-pr-templates.md` | Accepted | Link canonical template |
| `18-mvp-priorities-and-non-goals.md` | Accepted | Checklist MVP |
| `19-glossary-and-domain-model.md` | Accepted | Thuật ngữ canonical/entity |
| `20-functional-requirements.md` | Draft | FR ID có thể truy vết |
| `21-data-governance-privacy-and-security.md` | Accepted | Consent/access/retention gate |
| `22-training-environment-and-runbook.md` | Accepted | Local + Colab + DVC procedure |
| `23-testing-and-quality-strategy.md` | Accepted | Các tầng test/gate |
| `24-non-functional-requirements.md` | Draft | NFR đo được; giá trị target TBD |
| `25-interface-and-data-contracts.md` | Accepted | Schema Prediction/track/event/artifact |

Công cụ audit nguồn (schema/report, giới hạn kiểm tra): [data/source-audit.md](data/source-audit.md).

Audit ba ZIP SCB owner cung cấp: [candidate card](data/candidates/SCB5-supplied-20261003.md), [báo cáo](data/candidates/SCB5-supplied-20261003-audit.md), [ảnh/câu hỏi review](data/candidates/SCB5-supplied-20261003-review.md). Trạng thái CANDIDATE, chưa accepted.

Sổ công việc và bằng chứng hiện tại: [WORKLOG.md](WORKLOG.md).

Checkpoint task đang hoạt động cho agent: [`.codex/TASK.md`](../.codex/TASK.md); lifecycle theo [AGENTS.md](../AGENTS.md) và [guidelines 16](16-ai-agent-guidelines.md). TASK không thay canonical docs/ADR.

Review kỹ thuật và vòng đời thư mục: [codebase review 2026-10-05](reviews/codebase-review-20261005.md). Train/evaluate A và pipeline legacy đã gỡ theo owner; dataset v4/pointer/evidence không đổi.

## Bản đồ đọc (Reading map)

- Data: 01, 02, 04, 08, 09, 19, 21, 25; [hợp đồng pilot B](data/pilot-b-release-contract-v1.md) khi chuẩn bị release.
- Training: 04, 09, 10, 15, 22, 23, 24.
- Inference/tracking/events: 03, 11, 12, 19, 24, 25.
- Web: 03, 12, 13, 19, 20, 21, 25.
- Nhóm/quy trình: 05, 06, 15, 16, 17, 22.

## ADR records và quyết định hiện tại

1. ADR-001 nghiên cứu học thuật/demo; không dùng cho quyết định kỷ luật.
2. ADR-002 research history; ADR-011/012 chốt person unit, B và multi-label.
3. ADR-003 SCB5 + Roboflow là candidate, chưa được chấp nhận đến khi audit xong.
4. ADR-004 local development + Colab Free GPU.
5. ADR-005 DVC + Google Drive do thành viên được chỉ định kiểm soát.
6. ADR-006 YAML/JSON artifact là canonical; W&B là visualization/logger tùy chọn.
7. ADR-007 bỏ Django prototype; FastAPI/Jinja/SQLite tại P7.
8. ADR-008 ByteTrack là candidate, cần benchmark P5.
9. ADR-009 event/risk baseline rule-based; threshold chờ event data.
10. ADR-010 không thu thập/upload người thật trước khi có consent/policy được phê duyệt.
11. [ADR-013](decisions/ADR-013-pilot-b-packaging-contract.md): thiết kế pilot 84 SCB candidates + 28 RF crops, ba trạng thái/masked supervision, reviewed-crop package trước runtime gate và group evidence trước split/release training. Không phê duyệt dataset cụ thể.

12. [ADR-014](decisions/ADR-014-e001-local-linear-probe.md): owner duyệt E001 frozen ResNet18/masked linear probe CPU local. [Runbook](experiments/E001-runbook.md), [kết quả](experiments/E001-results.md); test đã evaluate một lần sau freeze candidate/protocol, không tuning.

13. [ADR-015](decisions/ADR-015-e002-v5-preservation-linear-probe.md): owner duyệt E002 local CPU trên accepted v5, smoke/validation và sửa loader preservation pointer có verification. Giữ exact recipe E001 và chỉ thêm20 train crop; không final test/upload/promotion.

## Quyết định chưa giải quyết

| ID | Câu hỏi | Owner | Chốt khi |
|---|---|---|---|
| TBD-DATA-01 (resolved cho pilot local v4) | Membership112,16 nhóm84 used,28 review_only đã owner duyệt | Owner | Evidence release v4; không chấp nhận toàn bộ nguồn |
| LABEL-01 (resolved cho pilot local v4) | Normal/co-occurrence vàP/N/U/masked supervision; schema/config/crop/targets v4 đã duyệt | Owner | Không chốt model/loss/runtime bằng approval dataset |
| TASK-01 (đã chốt) | YOLO person → crop → multi-label classifier B, ADR-012 | Owner | Không phải kết quả benchmark A/B |
| TBD-ANN-01 | Pilot đóng gói crop đã review; crop tự động còn là gate riêng | Owner | S9 trước baseline B end-to-end |
| TBD-EVT-01 | Ngưỡng duration/gap/event | Pipeline Lead | event validation set |
| TBD-METRIC-01 | Gate promotion bằng số | Team | sau E001 baseline/error analysis |
| TBD-RET-01 | Thời gian retention media/evidence thật | Giáo viên/team | trước khi thu thập |

Mọi quyết định lớn: ADR → canonical docs/config → code. Không sửa ngược thứ tự.

## Đầu mối Dataset Audit & Spec

[Phương án hai nguồn và việc còn lại](data/dataset-research.md), [P2 preparation B](09-phase-p2-dataset-preparation.md), [ADR-012](decisions/ADR-012-formulation-b-multilabel.md).

[Hợp đồng đóng gói pilot B v1](data/pilot-b-release-contract-v1.md) giữ exact RF membership, SCB quota/selection rule, target encoding/eligibility, crop/split gates và backlog S1–S9. [ADR-013](decisions/ADR-013-pilot-b-packaging-contract.md) chốt thiết kế; [release v4](../artifacts/reports/pilot-b-release-acceptance-20261005/README.md) là snapshot nghiệm thu local/freeze. Quyền storage Drive bổ sung và trạng thái S8 theo runbook/WORKLOG; S9 vẫn gate riêng trước end-to-end.

Roboflow: [card](data/candidates/Roboflow-phone-use-20261004.md),[audit gốc](data/candidates/Roboflow-phone-use-20261004-audit.md),[quyết định tổng hợp](data/candidates/Roboflow-phone-use-20261004-review.md). Giữ28 reviewed records; release v4 dùng23 crop vàgiữ5 review_only; unknown vẫn mask.

SCB5: [card](data/candidates/SCB5-supplied-20261003.md), [audit gốc](data/candidates/SCB5-supplied-20261003-audit.md), [review](data/candidates/SCB5-supplied-20261003-review.md). Discuss loại; Head/HRW là nguồn ứng viên relabel theo B.
