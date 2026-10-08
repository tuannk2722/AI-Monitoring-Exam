# Phương án v6 mở rộng sau owner review — R2

Đề xuất **317 train / 50 val / 11 test**, tổng 378 mẫu dùng; chưa accepted. Thay proposal 193/31/11 sau yêu cầu owner tận dụng review_only và tăng crop có giá trị. Không thay dataset v5.

[Báo cáo đầy đủ](../../artifacts/reports/pilot-b-v6-expansion-20261007-r2/README.md) và [review ảnh](../../data/interim/pilot-b/v6-release-review-expanded-20261007-r5/review.html). [Config](../../configs/datasets/pilot_b_v6_release_proposal_r2_20261007.yaml) pin gói, decisions và assignment.

Đã xét lại 89 review_only cũ, đề xuất nhận 46; rà thêm 147 crop, nhận 97. Tăng cả positive và negative cùng camera; dùng masked supervision khi chỉ một nhãn rõ. Cảnh liên quan validation chỉ vào val. Giữ nguyên 104 mẫu đã dùng của v5, gồm 13 val lịch sử và 11 test. Nhãn unknown của 16 parent review_only có đề xuất bổ sung; file v5 và nhãn parent đã biết không đổi.

156 tests, lint/type checks và kiểm checksum/pixel/membership PASS. Chưa train, chưa đo chất lượng model. FPI/Discuss vẫn ngoài đợt chính. Owner đã duyệt quyền/phạm vi; còn nghiệm thu nội dung crop/nhãn/nhóm/membership của gói R2 trước release.
