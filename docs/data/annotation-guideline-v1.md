# Annotation Guideline — Formulation B

Owner solo là người chốt; Codex hỗ trợ. Quyết định semantics theo ADR-011/012, không mở lại A/B. Không bắt người thứ hai hoặc inter-annotator agreement để đóng pilot solo; đo consistency bằng kiểm tra lại tập mẫu có ghi nhận.

Codex tự động tạo crop/target proposals từ metadata/heuristics; owner nghiệm thu batch qua báo cáo và chỉ ra ngoại lệ. Không bắt owner vẽ từng crop hoặc dùng HTML/Canvas. Proposal source bbox/class chưa là approval visible-person, context, absence target hay normal.

- Person bbox bao phần người nhìn thấy; không đoán cơ thể dưới bàn. Crop context có thể thêm bàn/phone liên quan, là vùng riêng với person bbox.
- Phone_use: cầm/tương tác hoặc phone trên bàn liên kết rõ với target; không chọn người gần nhất.
- Looking_around trên ảnh tĩnh: nhìn rõ sang người khác/ra khỏi vùng bài làm. Chỉ nghiêng đầu, cúi đọc/viết hoặc mắt không rõ giữ unknown nếu chưa đủ review. Không suy duration.
- Normal: người làm bài với absence cả hai target được review. Không box không có nghĩa normal; unknown không thành negative.
- Co-occurrence giữ cả hai target positive. P033 đã được owner duyệt cả hai; P036 nhìn về phone bên trái vẫn unknown cho looking_around.
- Phải kiểm chứng bằng chứng trong crop thuộc target, không thuộc người khác. Không yêu cầu annotate toàn bộ người ngoài crop khi chỉ chuẩn bị classifier; detector training riêng có hợp đồng completeness riêng.
- UI/phụ đề và các ảnh nhiễu đã loại giữ nguyên. Watermark được owner cho phép trong chọn mẫu, không suy quyền từng asset.
- P029 là hai người chuyền một phone, cả hai phone_use; không đổi thành phone trên bàn.

Ghi source identity/hash, person/crop coordinates, target states và reviewer. Không sửa raw. Duyệt bbox/crop không tự duyệt mọi target hoặc release. Schema/config/targets của [pilot local v4](../../artifacts/reports/pilot-b-release-acceptance-20261005/README.md) đã owner nghiệm thu; positive/negative/unknown và mask theo ADR-013. Crop runtime còn gate riêng; không tự đặt padding, angle, visibility threshold hoặc model/loss.

Kết quả hiện hành nằm trong [review Roboflow tổng hợp](candidates/Roboflow-phone-use-20261004-review.md). SCB và Roboflow dùng chung quy trình preparation theo [dataset research](dataset-research.md), không tách script theo từng vòng review.
