# Audit nhãn và group/pairs v7

Trạng thái: Draft. R7 bất biến; final R4 là đề xuất review, chưa là canonical labels.

Group registered, camera và room missing giữ UNKNOWN; không suy từ source/visual hint. Whole-component graph dùng các hint bảo thủ để tránh tách họ hàng, không chứng minh independence.

| Version | Crop | Fully-known | U/U | Phone P/N/U | Looking P/N/U |
|---|---:|---:|---:|---|---|
| R7 | 274 | 73 | 0 | 104/67/103 | 70/106/98 |
| R4-final | 274 | 70 | 15 | 95/63/116 | 66/105/103 |

Các file CSV gồm source × domain × target × P/N/U × registered group và bảng visual family hint riêng; bảng combinations không gộp U thành N. Looking có camera/room/group thực tế hoặc UNKNOWN. Crowded đếm P/P từ proposed states; phenotype crowded không chứng minh co-occurrence hoặc ownership.

Pair mới chỉ đề xuất khi cùng source hash/pixels và person_unit_hint khác nhau, có target P/N. Cần owner xem anchor, không tạo group gain. Không tuyên bố tìm thêm session pair nếu session/camera chưa được ghi nhận.

Không có official split. Component có exact evaluation link cách ly bảo thủ; component parent phải review linkage và giữ cùng split đã chốt; component chưa có parent chờ owner chốt group và train hoặc new-development-val. Giữ historical validation/test nguyên trạng. Nearest similarity là cờ chưa chứng minh.

CLI: `python -m ai_exam_monitoring.data.v7_annotation_audit --config <config-yaml> --root <repo-root>`.
