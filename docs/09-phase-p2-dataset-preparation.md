# 09 — P2 Dataset Preparation cho Formulation B

Kiến trúc: YOLO person → crop context → classifier multi-label (ADR-012). Nguồn, phạm vi và việc còn lại theo [dataset research](data/dataset-research.md).

## Hợp đồng chuẩn bị

- Giữ source image identity/hash, person bbox, context crop, target labels/unknown, reviewer, provenance và split/group.
- Tách person bbox khỏi crop context; không gán phone gần nhất. Không dùng annotation phone lúc inference nếu pipeline thực tế không có.
- Normal chỉ khi hai target vắng mặt đã review; positive đồng thời giữ cả hai. Unknown không mã hóa thành zero. Schema vector/mask và cơ chế loss còn cần quyết định trước exporter.
- Classifier crop đủ nhãn không bắt buộc annotate mọi người ngoài crop; train detector riêng cần dataset person đầy đủ theo hợp đồng riêng.
- Dedup/group trước split; không dùng cùng ảnh/crop liên quan ở nhiều split. Không bịa session/video.
- Owner solo review và ký release; Codex triển khai/kiểm tra.

## Build hiện tại

`configs/datasets/exam_v0.1.yaml` khai báo B và pending_preparation. `data.build_dataset` là converter YOLO detection legacy, **từ chối config B**; không phải exporter multi-label. Không đổi status accepted hoặc điền mapping nguyên lớp để ép chạy.

Chưa có lệnh build classifier B được hỗ trợ. Công việc tiếp theo phải thiết kế exporter tái tạo từ manifest đã review, kèm schema version và tests. Layout final phụ thuộc schema này; không gọi labels/*.txt YOLO là nhãn classifier B.

## Điều kiện đóng gói release

1. Phạm vi mẫu và target encoding/unknown policy được review, đủ coverage theo mục đích pilot/baseline đã công bố.
2. Crop policy dùng được ở inference, provenance và labels có thể kiểm tra.
3. Split/group/dedup report, test freeze, mapping từng mẫu hoặc relabel đã được owner ký.
4. Build deterministic, validation/checksum/rebuild pass; dataset card nêu rõ giới hạn.
5. DVC pointers/version và push/pull từ checkout sạch xác minh nội dung giống nhau. Owner tự kiểm tra, không cần người thứ hai.

Không train để chứng minh đóng gói; không gọi audit snapshot là training release. P0 DVC round-trip vẫn chưa được kiểm chứng.
