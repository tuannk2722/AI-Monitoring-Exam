# 09 — P2 Dataset Preparation cho Formulation B

Kiến trúc: YOLO person → crop context → classifier multi-label (ADR-012). Nguồn, phạm vi và việc còn lại theo [dataset research](data/dataset-research.md).

Hợp đồng pilot hiện hành: [pilot B v1](data/pilot-b-release-contract-v1.md), owner decisions [ADR-013](decisions/ADR-013-pilot-b-packaging-contract.md). Preparation giới hạn 84 SCB candidates + 28 RF approved records; chỉ thiết kế trong task hiện tại, triển khai S1–S8 ở task sau. Crop runtime là S9 trước baseline B end-to-end.

## Hợp đồng chuẩn bị

- Giữ source image identity/hash, person bbox, context crop, target labels/unknown, reviewer, provenance và split/group.
- Tách person bbox khỏi crop context; không gán phone gần nhất. Không dùng annotation phone lúc inference nếu pipeline thực tế không có.
- Normal chỉ khi hai target vắng mặt và context làm bài đã review; positive đồng thời giữ cả hai. Ba trạng thái và masked supervision đã owner chốt: unknown không mã hóa thành negative, loss/metric chỉ trên known targets. Schema/codec thiết kế ở contract pilot, còn implementation/version review; model/head/loss cụ thể chưa chọn.
- Classifier crop đủ nhãn không bắt buộc annotate mọi người ngoài crop; train detector riêng cần dataset person đầy đủ theo hợp đồng riêng.
- Dedup/group evidence được owner review trước split; không dùng cùng ảnh/crop liên quan ở nhiều split. Không bịa session/video; thiếu group giữ split=null/review_only và chặn release training. Ratio/seed/assignment còn cần owner chốt sau actual coverage.
- Owner solo review và ký release; Codex triển khai/kiểm tra.

## Build hiện tại

`configs/datasets/exam_v0.1.yaml` khai báo B và pending_preparation. `data.build_dataset` là converter YOLO detection legacy, **từ chối config B**; không phải exporter multi-label. Không đổi status accepted hoặc điền mapping nguyên lớp để ép chạy.

Chưa có lệnh build classifier B được hỗ trợ. Công việc tiếp theo phải thiết kế exporter tái tạo từ manifest đã review, kèm schema version và tests. Layout final phụ thuộc schema này; không gọi labels/*.txt YOLO là nhãn classifier B.

## Điều kiện đóng gói release

1. Budget/unknown policy theo ADR-013; membership/schema cụ thể và actual coverage được owner review theo hợp đồng pilot.
2. Crop reviewed-context, provenance và target evidence có thể kiểm tra/rebuild để đóng gói pilot. Crop tự động từ person detector phải owner chốt/QA riêng trước baseline B end-to-end; packaging không chứng minh runtime readiness (ADR-013).
3. Split/group/dedup report, test freeze, mapping từng mẫu hoặc relabel đã được owner ký.
4. Build deterministic, validation/checksum/rebuild pass; dataset card nêu rõ giới hạn.
5. DVC pointers/version và push/pull từ checkout sạch xác minh nội dung giống nhau. Owner tự kiểm tra, không cần người thứ hai.

Không train để chứng minh đóng gói; không gọi audit snapshot là training release. P0 DVC round-trip vẫn chưa được kiểm chứng.
