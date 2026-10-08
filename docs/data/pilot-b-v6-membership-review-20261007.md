# Phương án membership v6 đã chuẩn bị

Owner đã duyệt nguồn/quyền và yêu cầu mở rộng train/val, giữ test v5. Đã hoàn tất gói ảnh/crop/nhãn/nhóm để nghiệm thu: **193 train, 31 validation, 11 test**, tổng235 mẫu; 351 ledger, 89 review-only,27 excluded. Thêm79 crop từ ba RF mới và52 crop parent đã có nhãn/crop duyệt, sau kiểm nhóm. 143 candidate mới đều đã review ảnh nguồn/crop; FPI vẫn ngoài đợt chính.

[Báo cáo nghiệm thu và trang ảnh local](../../artifacts/reports/pilot-b-v6-preparation-20261007/README.md) là đầu mối chính. [Config](../../configs/datasets/pilot_b_v6_release_proposal_20261007.yaml) vẫn draft; **chưa có release v6 accepted**. V5, E002, raw và11 test không đổi; không training hoặc upload.

Validation31 có phone11P/14N/6U, looking8P/10N/13U; giữ13 val v5 thành subset lịch sử. Cần thí nghiệm/protocol riêng sau dataset acceptance; chưa có kết quả cải thiện model. Cụm thị giác chỉ là ranh giới chống leakage bảo thủ, chưa chứng minh session/subject độc lập. Dataset193 train vẫn nhỏ; runtime crop và holdout thực tế chưa được giải quyết bởi đợt này.

Owner còn nghiệm thu nội dung cụ thể của gói mới theo phương án nguồn đã duyệt và hợp đồng pilot B. Sau đó mới materialize canonical ledger/release/pointer v6; không coi approval nguồn cũ là approval nhãn/crop chưa tồn tại khi duyệt.
