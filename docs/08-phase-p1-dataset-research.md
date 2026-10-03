# 08 — P1 Dataset Research (Nghiên cứu Dataset)

P1 là điều kiện bắt buộc trước khi training chính thức. Các nguồn candidate là SCB5 và bộ Exam Cheating trên Roboflow; release và quyền sử dụng chính xác vẫn chưa được giải quyết.

## Audit bắt buộc cho mỗi nguồn

- URL có thẩm quyền, owner, release/version/ngày truy cập, citation;
- license/terms, quyền phân phối lại/tạo bản phái sinh/dùng cho training;
- SHA-256 của archive và hướng dẫn tải về;
- số lượng/loại media, độ phân giải, góc camera, số người mỗi cảnh;
- định dạng annotation, classes, định nghĩa, phân bố;
- mẫu bị hỏng/thiếu/orphan/bbox lỗi;
- mẫu trùng lặp/gần trùng/nhóm frame video và split hiện có;
- domain gap so với một camera classroom góc rộng;
- nguy cơ bảo mật dữ liệu cá nhân;
- đề xuất mapping sang canonical labels kèm các trường hợp unmapped/ignore.

Tạo một card từ `templates/dataset-candidate-template.md`, sau đó chạy:

```bash
python -m ai_exam_monitoring.data.audit --dataset data/raw/<source> --images images --labels labels --source-names source-names.json --output artifacts/reports/<source>-audit.json
```

Thay `images`, `labels` bằng subtree thực tế đã xác minh; cung cấp bảng ID/tên nguồn tường minh. Xem [contract audit](data/source-audit.md) và lệnh overlay trong README.

Output tự động là bằng chứng, không phải toàn bộ audit. Reviewer cần kiểm tra trực quan các mẫu phân tầng (stratified samples) và overlay. Không bao giờ suy ra group ID chỉ từ tên frame ngẫu nhiên nếu metadata video/session gốc có thể khôi phục được.

## Quyết định tính khả thi (Feasibility Decision)

Xây một subset nhỏ đã review cho formulation A (behavior detection) và B (person crop classification). So sánh công sức annotation, khả năng multi-label, hiệu năng trên người nhỏ và độ phức tạp tích hợp. Ghi quyết định vào ADR-002/003; không dùng test data.

## Deliverables

Dataset cards, bằng chứng license, `dataset-research.md`, label spec, annotation guideline, split spec, sample audit report, source manifest và cập nhật ADR. P1 chỉ kết thúc khi source/mapping/task/annotation unit chính xác có thể được review.
