# Dataset Audit & Spec — trạng thái và phương án sử dụng

Ngày: 2026-10-05. Đây là đầu mối hiện hành sau consolidation; pilot dùng một workflow chung. Kiến trúc và semantics theo ADR-011/012. **Pilot B v4 đã accepted cho classifier nghiên cứu local; test đã freeze.** Không có benchmark/model kết quả; DVC remote và crop runtime vẫn là gate riêng.

Thiết kế theo [hợp đồng pilot B v1](pilot-b-release-contract-v1.md) và [ADR-013](../decisions/ADR-013-pilot-b-packaging-contract.md). Budget 84 SCB candidates (28 TurnHead + 28 read + 28 write) cùng đúng 28 RF crops; ba trạng thái và masked supervision. Owner đã duyệt membership/crop/target/group/config/split và scope của release local cụ thể; không chấp nhận toàn bộ nguồn SCB/RF.

[Release local đã nghiệm thu](../../artifacts/reports/pilot-b-release-acceptance-20261005/README.md): canonical `pilot-b-20261005-v4`, 112 ledger/crop evidence, 84 manifest trong 16 nhóm (60 train / 13 val / 11 test), 28 review_only. Phone24P/9N/79U, looking 33P/56N/23U, 9 normal. Scope `local_classifier_research`; [approval](../../artifacts/reports/pilot-b-release-acceptance-20261005/owner-approval.json). Phone còn source confounding và val/test support nhỏ; không có model/generalization claim.

## Vai trò hai nguồn trong Formulation B

| Nguồn/phần | Vai trò trong preparation | Không được làm |
|---|---|---|
| Roboflow v1 | Nguồn bổ sung phone_use; giữ 28 person/crop đã duyệt trên 21 ảnh và các quyết định loại/hold | Dùng nguyên 3.407 ảnh như dataset canonical; tự map No cheating thành normal |
| SCB5 Head / TurnHead | Nguồn ứng viên looking_around, relabel theo hướng nhìn/ngữ cảnh đã chốt | Map toàn bộ TurnHead trực tiếp hoặc suy thời lượng từ ảnh |
| SCB5 HRW / read, write | Nguồn ứng viên normal và cảnh đang làm bài; phải review từng target trên crop được chọn | Coi read/write tự động là normal |
| SCB5 BowHead, hand-raising | Ngoài mapping trực tiếp của release đầu; có thể dùng ảnh phù hợp sau review hai target | Suy cúi đầu/tay khuất là gian lận hoặc negative |
| SCB5 Discuss | Loại khỏi baseline theo owner | Dùng group box như person box |

SCB đã audit toàn bộ ba ZIP (10.138 ảnh, 8.116 SHA unique), không cần audit lại hay lặp chuỗi review Roboflow. Tập hữu hạn84 anchors đã được owner nghiệm thu theo B. RF cung cấp phone positives; SCB cung cấp looking positives/negatives và9 phone negatives đã review. Không tạo launcher từng batch hoặc suy nhãn từ taxonomy nguồn.

Workflow: Codex tự tạo proposals, owner nghiệm thu qua báo cáo; không HTML/Canvas. V3 giữ lịch sử batch crop/looking; v4 nhập9 phone/context reviews mới và các cụm/ranh giới nhóm thị giác đã chấp nhận cho pilot local. Giữ14 must-links cũ trong16 component cuối, metadata session/room/person vẫn null; không chứng minh độc lập bằng hash unique. [Runbook](pilot-b-preparation-v1.md) ghi CLI/config/lineage.

## Đã có, đã chốt

- B: YOLO person → crop có ngữ cảnh → classifier multi-label. Chưa chọn model/weights/loss.
- Normal là người đang làm bài với absence hai target đã review; unknown không phải negative.
- Đồng xuất hiện giữ hai nhãn; crop không làm thay đổi bbox visible-person.
- Roboflow: 74 ảnh trong queue = 29 excluded + 11 deferred + 13 held + 21 ảnh có người được duyệt. 28 person/crop: 24 phone positives, 5 looking positives, 1 co-occurrence; 27 người còn một target unknown. Không có normal/negative được duyệt trong 28 record này.
- SCB: Discuss loại; quyền sử dụng đã được owner xác nhận, không hỏi lại. Group/session từng mẫu vẫn thiếu. 961 nhóm exact duplicate có thành viên train/val khi xét chung archive; không giữ split cũ khi hợp nguồn.
- Roboflow nguồn có 3.407 cặp, 34 file geometry warning/35 dòng khoảng 0.005 pixel; full exact checks không thấy trùng nội bộ/cross-SCB. Similarity triage chỉ là ứng viên, chưa chứng minh độc lập split.

## Hồ sơ duy nhất cần đọc

- SCB: [card](candidates/SCB5-supplied-20261003.md), [audit lịch sử](candidates/SCB5-supplied-20261003-audit.md), [review](candidates/SCB5-supplied-20261003-review.md).
- Roboflow: [card](candidates/Roboflow-phone-use-20261004.md), [audit lịch sử](candidates/Roboflow-phone-use-20261004-audit.md), [toàn bộ quyết định](candidates/Roboflow-phone-use-20261004-review.md).
- Evidence: SCB audit.json; Roboflow audit.json và review.json. Historical records giữ nguyên text/hash, không phải trạng thái hiện hành; current_person_crops/image_queue trong review.json là snapshot cuối.
- Outputs media giữ nguyên local/ignored. Scripts theo phiên đã nghỉ; Git và snapshots trong review.json giữ provenance, không hứa replay các launcher đã bỏ.

## Hoàn tất và các gate ngoài release local

Selection/provenance, structured schema, reviewed crop/targets, group boundaries, scope/config, split/freeze và builder v4 đã qua nghiệm thu/checksum/rebuild. 108 tests pass; giữ đúng112 ledger và84 usage records. Unknown không mã hóa negative; không train từ28 review-only crops. Không cần quyết định owner mới để dùng version này trong phạm vi đã duyệt.

DVC đã cài/cấu hình; smoke push/pull qua cache sạch đạt. Owner đã bổ sung quyền lưu đúng v4 trên Drive restricted trong task bàn giao 2026-10-05; phạm vi và evidence round-trip theo runbook/WORKLOG, không sửa snapshot approval local hoặc mở quyền redistribution/W&B. Runtime crop S9 phải có policy/QA riêng trước baseline B end-to-end. Classifier training là task riêng với model/loss/experiment/config; real-world holdout và acceptance metrics chưa được chứng minh, không gọi mọi milestone P0/P1/P2 đã xong.

Task thiết kế và đóng gói pilot local đã hoàn tất. Bàn giao chốt implementation/config/evidence/pointer vào Git; commit và trạng thái cuối trong WORKLOG. Release giữ Git dirty/code SHA trung thực tại thời điểm build gốc. Evidence/lệnh ở runbook và [báo cáo release lịch sử](../../artifacts/reports/pilot-b-release-acceptance-20261005/README.md); checkpoint ở [`.codex/TASK.md`](../../.codex/TASK.md).
