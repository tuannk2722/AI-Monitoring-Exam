# ADR-012 — Formulation B và nhãn đồng thời

- Status: Accepted cho các quyết định owner dưới đây; chưa phê duyệt dataset/model.
- Date: 2026-10-04. Owner: chủ repository.
- Supersedes: phần chờ chọn A/B và normal/co-occurrence trong ADR-002, ADR-011.
- Evidence: owner quyết định trong hội thoại: “YOLO tìm người → Crop → Classifier”; normal là người đang làm bài không có bằng chứng hai hành vi và đã review thủ công; đồng xuất hiện gán cả hai nhãn.

Cập nhật theo [ADR-013](ADR-013-pilot-b-packaging-contract.md): unknown target vẫn ở ngoài supervision/metric, nhưng crop có target khác đã biết được phép masked supervision khi các gate khác đạt. Pilot đóng gói crop đã review; automatic runtime crop là gate riêng trước baseline B end-to-end. Các đoạn “schema sẽ thiết kế sau” bên dưới mô tả trạng thái lúc ADR-012 được chốt; thiết kế hiện hành ở [hợp đồng pilot B](../data/pilot-b-release-contract-v1.md), chưa có exporter/dataset accepted.

## Quyết định

1. Chọn **B: YOLO phát hiện người → crop theo người → classifier multi-label**. Detector tìm person, không dùng lớp hành vi làm lớp detector. Tracking/temporal chưa thuộc baseline này.
2. `normal` là người đang làm bài, đã được review thủ công và không có bằng chứng `looking_around` hoặc `phone_use`. Thiếu box, nhãn bị bỏ sót, người bị che hoặc chưa review không phải normal.
3. Khi cùng có bằng chứng, giữ cả `phone_use` và `looking_around` trên cùng người/crop. Không ép chọn một, không dùng hợp đồng single-label/softmax độc quyền để mã hóa hai hành vi.
4. Normal không đồng thời với hai target. Nhãn không xác định phải giữ unknown; không biến unknown thành 0/negative. Cách lưu vector/mask và head/loss classifier sẽ được thiết kế sau guideline/crop review; ADR này chưa chọn model/pretrained/threshold.
5. Bbox người vẫn chỉ bao phần nhìn thấy theo ADR-011. Owner xác nhận “Đồng ý crop có thêm ngữ cảnh”: crop classifier được bao thêm vùng bàn/phone liên quan và phải review. Không mở rộng bbox người thành bbox ngữ cảnh; không tự đặt padding cố định hoặc gán phone người bên cạnh.
6. Owner xác nhận “Chấp nhận quy tắc này” cho looking_around ảnh tĩnh: đầu/hướng nhìn thể hiện rõ đang nhìn sang người khác hoặc ra khỏi vùng bài làm thì positive; chỉ lệch đầu, cúi đọc/viết hoặc không rõ hướng nhìn giữ unknown ngoài train khi chưa đủ review. Không suy thời lượng từ ảnh tĩnh. Tư thế cúi đọc/viết một mình không đủ kết luận normal; normal vẫn phải có review cả hai target.
7. Quyết định B dựa trên lựa chọn owner sau audit, **không phải kết quả benchmark A/B**.

## Tác động

Các converter/build YOLO hiện tại không được gọi là pipeline dữ liệu classifier B. Config dataset/label-map cũ vẫn draft, mapping chưa điền và chưa được phép build dataset chính thức. Giữ tên/ID canonical; chưa tự chuyển toàn nguồn sang nhãn mới.

Cần hoàn thiện guideline, person/crop completeness, split/group chống leakage và P1 gate trước training. Chưa chọn trọng số YOLO, classifier, loss, crop margin hay tham số inference. Không thay đổi trạng thái accepted của nguồn dữ liệu.
