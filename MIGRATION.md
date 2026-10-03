# Migration từ prototype cũ

Repository này là bản thay thế có chủ đích, không phải patch incremental Django.

## Đã xóa

- Django `config/`, `detection/`, migration và templates.
- Dependency/config/placeholder Cloudinary.
- Bảng `Session`/`Detection` thiếu frame/time/track/model provenance.
- Placeholder `detect_cheating()` và logic `phone_use → Cheating` trực tiếp.
- Mock detections/FPS/runtime/alert và browser-only webcam/IP camera preview.
- Route không trả về HTTP response và client-only upload validation.

## Đã thêm/thay thế

- Một repo canonical chứa docs/config/code/tests/workflow.
- Data Lead pipeline: source manifest, YOLO validation/remap, grouped deterministic split, canonical dataset builder/audit.
- Model Lead pipeline: Ultralytics training/evaluation qua YAML, run status/environment/provenance, DVC artifact layout, W&B tùy chọn.
- Pipeline Lead contract: structured frame/time/model/bbox prediction và inference JSONL.
- P5/P6 gate tường minh thay vì code tracker/event/risk giả.
- DVC + Google Drive workflow, GitHub Projects/issue/PR/CI setup.
- Bộ tài liệu đầy đủ 01–25, data spec và ADR-001–010.

## Chưa được migrate như khả năng hoạt động

Visual dashboard cũ không được giữ lại vì nó biểu diễn kết quả không được hỗ trợ như kết quả thật. P7 sẽ xây dựng một FastAPI review UI nhỏ dựa trên stable event contract. Dataset/model/video binary cũng cố ý vắng mặt và phải được thêm vào qua DVC workflow có review.

## Input người dùng cần cung cấp

URL/license/checksum/mapping chính xác của SCB5/Roboflow; formulation A/B; annotation unit; biểu diễn `normal`; gate model/event/performance bằng số; consent và retention period media thật. Mỗi item có owner/exit condition trong `docs/00-INDEX.md`.
