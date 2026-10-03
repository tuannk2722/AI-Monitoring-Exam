# 04 — Chiến lược Hành vi và Nhãn (Behavior & Label Strategy)

## Trạng thái

Taxonomy candidate: `normal`, `looking_around`, `phone_use`. Tên canonical là `looking_around`; `head_turn` có thể là alias từ nguồn gốc và cần qua review trước khi dùng. Các nhãn `cheating`, `cheater`, `suspicious_person`, `no_cheating` bị cấm dùng làm nhãn model.

Nhiều hành vi có thể xảy ra đồng thời. Do đó, contract của domain/event cho phép nhiều prediction/event trên mỗi track/thời điểm. Việc baseline mã hóa chúng dưới dạng detection class hay multi-label classification vẫn là TBD-TASK-01.

## Yêu cầu nhãn

Mỗi nhãn được chấp nhận phải định nghĩa: ID/tên canonical; định nghĩa quan sát được; annotation unit; ví dụ positive/negative/ambiguous/ignore; quy tắc về occlusion/kích thước; quy tắc đồng xuất hiện (co-occurrence); thời lượng tối thiểu nếu là temporal; ánh xạ nguồn gốc (source mapping); version.

## Ngữ nghĩa các candidate

- `phone_use`: người cầm/tương tác điện thoại hoặc phone trên bàn gắn được với người bằng bằng chứng thị giác; unit person. Không rõ vật/người liên quan thì unknown/ignore. Owner đã chốt tại [ADR-011](decisions/ADR-011-person-unit-phone-definition.md).
- `looking_around`: mẫu định hướng đầu/mắt quan sát được theo guideline; không phải bằng chứng về ý định hay vi phạm.
- `normal`: absence đã review của cả hai target, unknown không phải normal. Biểu diễn còn mở: có thể là class negative tường minh cho classifier B, hoặc là absence/background cho detection A. Không được ép vào YOLO detection nếu điều đó tạo ra các box vô nghĩa.

## Ignore/unknown (bỏ qua/không xác định)

Mẫu quá nhỏ, bị che khuất nhiều, ngoài frame, không xác minh được hoặc nhãn mâu thuẫn phải được đánh dấu `ignore`/loại trừ với lý do, không được đoán mò. Quy tắc số về visibility/kích thước được quyết định từ thống kê audit.

Bản thảo làm việc canonical là `docs/data/label-spec-v1.md`.
