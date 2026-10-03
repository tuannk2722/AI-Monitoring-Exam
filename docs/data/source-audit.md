# Source audit và overlay — S1

Owner/người chốt: chủ repository; Codex hỗ trợ triển khai/review. Đây là contract công cụ kiểm tra phần mềm, không thay label spec, split spec hoặc phê duyệt dataset.

## Input và pairing

- CLI `audit`/`overlay` bắt buộc `--dataset`, `--images`, `--labels`, `--source-names`; các subtree phải tồn tại và nằm dưới dataset root. Dùng `.` cho nguồn colocated nếu đã xác minh; không auto-detect.
- Ghép theo đường dẫn tương đối bỏ extension, phân biệt chữ hoa/thường. Cùng stem ở các thư mục khác nhau là các khóa khác nhau. Nhiều extension cùng khóa là ambiguous và không xuất overlay.
- Ảnh hỗ trợ JPG/JPEG/PNG/BMP/WEBP. Label là `.txt` trong subtree labels trừ `classes.txt` và `README*.txt` (không phân biệt hoa/thường). Các tên này dành riêng cho metadata. Metadata khác cần nằm ngoài subtree label hoặc phải chuẩn hóa bằng quy trình riêng, không sửa raw trong audit.
- Nguồn kiểu `images/{train,val,test}` + `labels/{train,val,test}`: chọn `images`/`labels` để kiểm tra cùng một lượt. Kiểu `{split}/images` + `{split}/labels`: chạy từng split; không tuyên bố đã kiểm tra duplicate chéo split từ các báo cáo riêng.
- Source names: JSON object ID → tên; hoặc YAML `names` là mapping ID → tên. ID nguyên không âm, tên không rỗng, không có ID trùng. Không chấp nhận danh sách tên để tránh tự gán ID theo thứ tự. Không chuyển ID/tên sang canonical hay tạo group_id.

## Report JSON schema_version = 2

Thay report v1 ghép global stem bằng schema v2. DVC audit stage và README đã cập nhật tham số; pipeline vẫn bị gate dataset chưa accepted.

- `source_layout`, `source_names`: input và quy tắc ghép đã sử dụng.
- `image_count`, `label_file_count`, `ignored_metadata`, `resolution_counts`: inventory/ảnh decode được.
- `missing_labels`: đường dẫn ảnh thiếu label; `orphan_labels`: label thiếu ảnh; `ambiguous_pairs`: khóa và mọi đường dẫn trùng khóa.
- `invalid_images`, `invalid_labels`: file và lỗi; YOLO error có số dòng. File label lỗi không đóng góp một phần vào thống kê.
- `empty_label_files`: nhãn rỗng hợp lệ về cấu trúc; không tự kết luận background/normal.
- `annotation_count_by_class_id`: tất cả label file hợp lệ, kể cả orphan; có lớp đếm 0. `bbox_sizes`: count/min/max/mean width, height, area normalized trên các file đó; pixel chỉ tính cặp duy nhất có ảnh decode được. Không áp threshold chất lượng/kích thước. Tập rỗng có count 0 và các giá trị null.
- `exact_duplicate_groups`: SHA-256 và toàn bộ đường dẫn file có bytes giống nhau, kể cả file hỏng nhưng đọc được; `duplicate_file_copies` là tổng bản dư. Không phải so sánh pixel, ảnh gần trùng hoặc bằng chứng group leakage.
- `samples`: cặp duy nhất hợp lệ, kích thước ảnh và annotation nguồn dùng cho overlay. Không có prediction/metric model.
- `checks`: liệt kê kiểm tra tự động, chưa thực hiện và việc cần human review. `errors` ghi nguồn không ảnh/không label; `has_errors` tổng hợp lỗi cấu trúc/file, không là dataset acceptance. Duplicate là thông tin cần review, không tự làm fail.

## Output và review

Output ngoài source và repository `data/raw`; overlay không ghi đè thư mục đã có nội dung. Ảnh dùng hướng pixel gốc (không tự xoay theo EXIF) giống tọa độ YOLO. Bbox cực nhỏ hiển thị tối thiểu một pixel, không sửa annotation.

Overlay chọn N cặp hợp lệ đầu tiên theo đường dẫn. Manifest schema_version 1 ghi phương pháp chọn, số cặp đủ điều kiện, từng output và nguồn, legend ID/tên; audit đi kèm ghi lỗi/loại trừ. Không gọi đây là mẫu phân tầng, không bảo đảm bao phủ mọi lớp. Owner phải bổ sung review theo lớp/camera/occlusion và xác minh unit, độ khớp box, nhãn sai/thiếu, label rỗng, gần trùng và metadata nhóm. Không dùng test set cho tuning.

Exit 0: các check được thực hiện pass; exit 1: có lỗi cấu trúc/file hoặc không xuất được mẫu; exit 2: tham số/input/output không hợp lệ. Lỗi file đơn lẻ không dừng toàn bộ audit. Chưa kiểm tra gần trùng, leakage, license/consent, ngữ nghĩa hoặc canonical mapping; vẫn cần P1 owner review.
