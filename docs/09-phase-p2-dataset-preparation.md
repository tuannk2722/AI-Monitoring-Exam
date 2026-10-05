# 09 — P2 Dataset Preparation cho Formulation B

Kiến trúc: YOLO person → crop context → classifier multi-label (ADR-012). Nguồn, phạm vi và việc còn lại theo [dataset research](data/dataset-research.md).

Hợp đồng [pilot B v1](data/pilot-b-release-contract-v1.md), thiết kế [ADR-013](decisions/ADR-013-pilot-b-packaging-contract.md). Release v4 đã nghiệm thu: 112 ledger/crops, 84 used (60 train/13 val/11 test), 16 nhóm, 28 review_only, test frozen. Owner đã cho phép bàn giao đúng package qua Drive restricted; pointer và trạng thái round-trip theo [runbook](data/pilot-b-preparation-v1.md). S9 crop runtime là gate riêng trước end-to-end.

## Hợp đồng chuẩn bị

- Giữ source image identity/hash, person bbox, context crop, target labels/unknown, reviewer, provenance và split/group.
- Tách person bbox khỏi crop context; không gán phone gần nhất. Không dùng annotation phone lúc inference nếu pipeline thực tế không có.
- Normal chỉ khi hai target vắng mặt vàcontext làm bài đã review;positive đồng thời giữ cả hai. Schema/config pilot v4 đã duyệt:unknown không mã hóa negative,loss/metric chỉ trên known targets. Model/head/loss của E001 được owner duyệt riêng tại ADR-014; không đổi hợp đồng dữ liệu.
- Classifier crop đủ nhãn không bắt buộc annotate mọi người ngoài crop; train detector riêng cần dataset person đầy đủ theo hợp đồng riêng.
- Dedup/group evidence và ranh giới thị giác đã owner review cho84used; không có same image/crop/group qua split. Không bịa session/video;28 thiếu group giữ split=null/review_only. Explicit whole-group assignment60/13/11,seed=null,70/15/15soft đã chốt/freeze; không chọn lại khi training.
- Owner solo review và ký release; Codex triển khai/kiểm tra.

## Build hiện tại

`configs/datasets/exam_v0.1.yaml` khai báo B và pending_preparation. `data.build_dataset` là converter YOLO detection legacy, **từ chối config B**; không phải exporter multi-label. Không đổi status accepted hoặc điền mapping nguyên lớp để ép chạy.

Pilot B dùng config riêng `configs/datasets/pilot_b_v1.yaml`: `data.pilot_inputs` pin/select, `data.pilot_prepare` tạo ledger/staging, `data.pilot_owner_groups` nhập quyết định nhóm đã duyệt. `data.pilot_scb_proposals` tự tạo 84 crop/nhãn đề xuất theo source metadata; owner nghiệm thu batch qua báo cáo, không cần vẽ crop bằng HTML/Canvas. `data.pilot_schema` là codec/consumer/validator; `data.pilot_package.build_pilot_package` export từ records đã review và chặn thiếu release gates. Proposal không tự thành canonical approval. Không gọi labels/*.txt YOLO là nhãn classifier B.

## Điều kiện đóng gói release

1. Budget/unknown policy theo ADR-013; membership/schema cụ thể và actual coverage được owner review theo hợp đồng pilot.
2. Crop reviewed-context, provenance và target evidence có thể kiểm tra/rebuild để đóng gói pilot. Crop tự động từ person detector phải owner chốt/QA riêng trước baseline B end-to-end; packaging không chứng minh runtime readiness (ADR-013).
3. Split/group/dedup report, test freeze, mapping từng mẫu hoặc relabel đã được owner ký.
4. Build deterministic, validation/checksum/rebuild pass; dataset card nêu rõ giới hạn.
5. DVC pointers/version và push/pull từ checkout sạch xác minh nội dung giống nhau. Owner tự kiểm tra, không cần người thứ hai.

Không train để chứng minh đóng gói; audit snapshot không thay accepted release. DVC đã cài/cấu hình; smoke và v4 push/pull/cache sạch đạt. Quyền lưu trữ v4 bổ sung ngày 2026-10-05 chỉ áp dụng remote restricted hiện có, không thay scope train hoặc quyền phân phối. S8 đã đóng: full immutable payload khôi phục từ exact commit/cache sạch, schema/pins/test freeze PASS; 109 tests trên clean checkout PASS. Bằng chứng cuối trong WORKLOG/runbook. Runtime readiness/model acceptance và toàn bộ P0/P1/P2 không tự đạt bằng storage handoff.
