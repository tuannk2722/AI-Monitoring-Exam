# Split Specification v1 — Draft (Bản thảo Đặc tả Split)

**Ngoại lệ đã Accepted cho pilot B local v4:** `pilot-b-explicit-scene-split-v1`, whole-group assignment tường minh,seed=null,60train/13val/11test trên84used;28review_only. Ratio70/15/15 là mục tiêu mềm. Test đã freeze bằng manifest/split/config SHA vàowner evidence trong [release](../../artifacts/reports/pilot-b-release-acceptance-20261005/README.md). Cấu hình cụ thể này ưu tiên hơn stable-hash draft bên dưới; không chọn lại split khi training.

Pilot B áp dụng [ADR-013](../decisions/ADR-013-pilot-b-packaging-contract.md) và [hợp đồng pilot B](pilot-b-release-contract-v1.md): chỉ freeze split khi leakage groups đủ evidence được owner review; thiếu group giữ split=null/review_only và chặn release training. Không suy session từ filename hay coi mỗi ảnh là group độc lập. Ratio/seed/assignment ở tài liệu/config draft chưa phải owner approval cho pilot; phải chốt sau actual coverage/group review.

Tỷ lệ target 70/15/15 là thứ yếu so với tính độc lập. Ưu tiên nhóm theo: bối cảnh nguồn → room/session/video/person theo metadata hiện có. Tất cả frame/crop/augmentation sinh ra từ cùng một group phải nằm trong cùng một split.

Test set bị đóng băng, loại trừ khỏi training, lựa chọn epoch/model/augmentation/threshold. Local exam-like holdout được xác định riêng và không bao giờ được âm thầm merge vào train.

Triển khai dùng stable hash của `seed:group_id`; do đó thứ tự row không thay đổi assignment. Data Lead review phân bố class/source và có thể tạo versioned constrained split nếu mất cân bằng không chấp nhận được — không bao giờ được di chuyển thủ công từng frame gần trùng lặp mà không cập nhật split version.

Báo cáo bắt buộc: định nghĩa group, tỷ lệ/số lượng theo class/source, metadata trống/thiếu, kiểm tra trùng lặp/leakage, seed, script/commit, split version và reviewer.
