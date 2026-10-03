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
| TBD-LABEL-01 | `normal` là class tường minh hay absence/background | Team + Data Lead | A/B feasibility audit |
| TBD-TASK-01 | Detection A hay detector+classifier B | Model Lead | benchmark trên dữ liệu đã audit |
| TBD-ANN-01 | Annotation unit: person bbox/frame, crop hay clip | Data Lead | label spec review |
| TBD-EVT-01 | Ngưỡng duration/gap/event | Pipeline Lead | event validation set |
| TBD-METRIC-01 | Gate promotion bằng số | Team | sau E001 baseline/error analysis |
| TBD-RET-01 | Thời gian retention media/evidence thật | Giáo viên/team | trước khi thu thập |

Mọi quyết định lớn: ADR → canonical docs/config → code. Không sửa ngược thứ tự.
