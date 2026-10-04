# 08 — P1 Dataset Research

Audit & Spec được tổng hợp cho Formulation B theo ADR-011/012. Không tiếp tục benchmark A/B hoặc vòng review ảnh nhỏ lẻ. [Dataset research](data/dataset-research.md) là trạng thái/vai trò SCB5 và Roboflow hiện hành.

Bằng chứng đã có: archive identity/hash, class namespaces, structure/geometry, exact duplicates, mẫu trực quan và owner decisions. Audit tự động không chứng minh annotation đầy đủ. Hai nguồn vẫn candidate, chưa accepted cho train.

P1 còn gate preparation: phạm vi mẫu release, labels/crop policy thực thi được, coverage normal/negative/unknown, group/split và quyền dùng trong phạm vi release. Không đòi owner xác nhận lại quyền SCB hoặc kiến trúc đã chốt.

Mỗi nguồn giữ ba tài liệu: candidate card, audit lịch sử, consolidated review. Raw bất biến; historical evidence hợp nhất giữ nội dung/hash. Không thêm script theo từng câu hỏi review.

Chuyển sang [P2](09-phase-p2-dataset-preparation.md) để tạo package B sau khi gate còn thiếu được xử lý. Chưa có dataset training hoặc kết quả model để tuyên bố hoàn thành P1.
