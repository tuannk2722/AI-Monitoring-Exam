# ADR-003 — SCB5 và Roboflow candidates

- Status: Accepted as source candidates, not accepted training data.
- Updated: 2026-10-04, owner solo.

Nguồn đã pin bằng archive hash. SCB Head/HRW cung cấp ứng viên looking_around/normal sau relabel; Discuss loại. Roboflow v1 bổ sung phone_use với subset đã review. [Dataset research](../data/dataset-research.md) quy định vai trò và preparation. Quyền SCB đã được owner xác nhận; group từng ảnh không được suy từ xác nhận quyền.

Formulation B theo ADR-012; config nguồn pending_preparation. Không tự map lớp nguồn sang canonical, không dùng nguyên split có duplicate overlap. Chưa accepted/build/train; không mở lại lựa chọn A/B.
