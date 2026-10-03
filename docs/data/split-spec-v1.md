# Split Specification v1 — Draft (Bản thảo Đặc tả Split)

Tỷ lệ target 70/15/15 là thứ yếu so với tính độc lập. Ưu tiên nhóm theo: bối cảnh nguồn → room/session/video/person theo metadata hiện có. Tất cả frame/crop/augmentation sinh ra từ cùng một group phải nằm trong cùng một split.

Test set bị đóng băng, loại trừ khỏi training, lựa chọn epoch/model/augmentation/threshold. Local exam-like holdout được xác định riêng và không bao giờ được âm thầm merge vào train.

Triển khai dùng stable hash của `seed:group_id`; do đó thứ tự row không thay đổi assignment. Data Lead review phân bố class/source và có thể tạo versioned constrained split nếu mất cân bằng không chấp nhận được — không bao giờ được di chuyển thủ công từng frame gần trùng lặp mà không cập nhật split version.

Báo cáo bắt buộc: định nghĩa group, tỷ lệ/số lượng theo class/source, metadata trống/thiếu, kiểm tra trùng lặp/leakage, seed, script/commit, split version và reviewer.
