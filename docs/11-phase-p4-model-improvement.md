# 11 — P4 Model Improvement (Cải tiến Model)

Chỉ bắt đầu sau khi E001 có thể tái tạo được. Vòng lặp: đánh giá → phân loại lỗi thực tế → hypothesis → thay đổi một biến quan trọng → experiment mới → review.

Ưu tiên: sửa label/data → dữ liệu giống domain thật → cân bằng dữ liệu → augmentation → độ phân giải → kích thước model → hyperparameter. Không thêm model lớn hơn để che giấu label leakage hay domain mismatch.

Duy trì giao thức validation cố định và một exam-like holdout riêng biệt không dùng cho training/tuning. So sánh hành vi per-class, error slice (người nhỏ, occlusion, ánh sáng, khoảng cách camera, trường hợp mơ hồ), chi phí tài nguyên và hành vi trên holdout.

Sau E001, nhóm ghi lại các ngưỡng (gate) candidate bằng số vào một model-acceptance ADR. Cho đến khi đó, "đủ tốt" được ghi rõ là TBD-METRIC-01. Trạng thái promotion: Rejected (bị loại), Continue (tiếp tục), Candidate (ứng viên), Selected (đã chọn), Archived (lưu trữ). Artifact được Selected cần: experiment ID, phiên bản code/data/config, metrics, limitations và checksum.
