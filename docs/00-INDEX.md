# 00 — Documentation Index

## Trạng thái hiện tại

Ngày cập nhật: 2026-09-19. Owner tài liệu: team. Phase: **P0 → P1**.

`Accepted` = implementation contract (hợp đồng triển khai); `Draft` = hướng dẫn đang hoàn thiện; `TBD` = không được tự bịa giá trị.

| File | Status | Nội dung |
|---|---|---|
| `01-project-overview.md` | Accepted | Product mode, actor, processing mode |
| `02-scope-and-principles.md` | Accepted | MVP/non-goal/thứ tự ưu tiên |
| `03-system-architecture.md` | Accepted | Ranh giới hệ thống và hai formulation candidate |
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

## Bản đồ đọc (Reading map)

- Data: 01, 02, 04, 08, 09, 19, 21, 25.
- Training: 04, 09, 10, 15, 22, 23, 24.
- Inference/tracking/events: 03, 11, 12, 19, 24, 25.
- Web: 03, 12, 13, 19, 20, 21, 25.
- Nhóm/quy trình: 05, 06, 15, 16, 17, 22.

## ADR records và quyết định hiện tại

1. ADR-001 nghiên cứu học thuật/demo; không dùng cho quyết định kỷ luật.
2. ADR-002 taxonomy candidate và multi-label-safe domain design; biểu diễn cuối chờ P1.
3. ADR-003 SCB5 + Roboflow là candidate, chưa được chấp nhận đến khi audit xong.
4. ADR-004 local development + Colab Free GPU.
5. ADR-005 DVC + Google Drive do thành viên được chỉ định kiểm soát.
6. ADR-006 YAML/JSON artifact là canonical; W&B là visualization/logger tùy chọn.
7. ADR-007 bỏ Django prototype; FastAPI/Jinja/SQLite tại P7.
8. ADR-008 ByteTrack là candidate, cần benchmark P5.
9. ADR-009 event/risk baseline rule-based; threshold chờ event data.
10. ADR-010 không thu thập/upload người thật trước khi có consent/policy được phê duyệt.

## Quyết định chưa giải quyết

| ID | Câu hỏi | Owner | Chốt khi |
|---|---|---|---|
| TBD-DATA-01 | Release/URL/license/checksum chính xác của SCB5/Roboflow | Data Lead | P1 audit |
| LABEL-01 (đã chốt ngữ nghĩa) | Normal đã review; hai target đồng thời giữ cả hai, ADR-012 | Owner | Schema classifier còn cần thiết kế |
| TASK-01 (đã chốt) | YOLO person → crop → multi-label classifier B, ADR-012 | Owner | Không phải kết quả benchmark A/B |
| TBD-ANN-01 | Person unit và crop có ngữ cảnh đã chốt; còn quy tắc crop tự động | Owner | crop QA và kiểm chứng inference |
| TBD-EVT-01 | Ngưỡng duration/gap/event | Pipeline Lead | event validation set |
| TBD-METRIC-01 | Gate promotion bằng số | Team | sau E001 baseline/error analysis |
| TBD-RET-01 | Thời gian retention media/evidence thật | Giáo viên/team | trước khi thu thập |

Mọi quyết định lớn: ADR → canonical docs/config → code. Không sửa ngược thứ tự.

Audit Roboflow v1 owner cung cấp (hoàn thiện 2026-10-04): [candidate](data/candidates/Roboflow-phone-use-20261004.md), [báo cáo](data/candidates/Roboflow-phone-use-20261004-audit.md), [ảnh/câu hỏi review](data/candidates/Roboflow-phone-use-20261004-review.md), [provenance](../artifacts/reports/roboflow-20261004/provenance.json). Trạng thái CANDIDATE, chưa accepted. Quyết định SCB của owner được ghi tại mục cập nhật trong candidate SCB.

Owner review Roboflow đã chốt 18 mục: [ADR-011](decisions/ADR-011-person-unit-phone-definition.md), [manifest](../artifacts/reports/roboflow-20261004/owner-decisions.json). Relabel/QA subset và P1 acceptance còn mở.

Pilot Roboflow: [74 ảnh và kết quả owner review](data/candidates/Roboflow-phone-use-pilot-20261004.md). Đã chốt bốn mục: 3 bbox duyệt trên 2 ảnh, 2 ảnh nhiễu loại. Có similarity triage, chưa xác nhận group/split hoặc accepted.

[Batch 2 đã duyệt](data/candidates/Roboflow-phone-use-batch2-20261004.md): tổng 10 bbox trên 8 ảnh; sau quyết định nhóm, 29 loại, 10 ngoài subset đầu tiên, 35 ảnh ứng viên vẫn cần completeness QA, chưa accepted.

[Toàn bộ phần việc còn lại](data/candidates/Roboflow-remaining-review-20261004.md): hai quyết định nhóm đã áp dụng, còn 27 ảnh chưa duyệt bbox; không phải đã có group/session IDs.

[QA toàn bộ 27 ảnh còn lại](data/candidates/Roboflow-remaining-qa-20261004.md): tổng 24 bbox / 21 ảnh. 13 ảnh giữ ngoài train, 11 ảnh deferred gồm P042; completeness còn mở, chưa training eligible.

[ADR-012](decisions/ADR-012-formulation-b-multilabel.md): owner chọn B, normal đã review, multi-label đồng thời; chốt guideline looking_around ảnh tĩnh và crop có ngữ cảnh. Chưa chọn model/loss, chưa dataset accepted.
