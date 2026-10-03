# Label Specification v1 — Draft (Bản thảo Đặc tả Nhãn)

Version: `label-map-v0.1-draft`. Owner: Data Lead. Reviewer: Model Lead. Chưa đóng băng.

## Quy tắc chung

- Chỉ annotate bằng chứng quan sát được; nhiều hành vi có thể cùng tồn tại.
- Không suy diễn ý định/vi phạm.
- Annotation unit và biểu diễn `normal` chờ quyết định formulation A/B.
- Nếu bằng chứng quá nhỏ/bị che/mơ hồ, dùng ignore/exclusion có lý do đã được review.

## `phone_use`

**Positive candidate**: tương tác/cầm điện thoại rõ ràng nhất quán với guideline cuối cùng.
**Negative candidate**: vật thể không liên quan, điện thoại chỉ xuất hiện mà không có hành vi cần thiết, hoặc vật thể quá nhỏ không xác minh được.
Các trường hợp mơ hồ cần review, không được đoán mò là positive.

## `looking_around`

**Positive candidate**: định hướng quan sát được của đầu/mắt lệch khỏi hướng làm việc dự kiến theo quy tắc pose/duration đã review.
**Negative candidate**: di chuyển mắt thông thường khi đọc giấy/điều chỉnh tư thế mà không thỏa quy tắc.
Nhãn này không trực tiếp có nghĩa là vi phạm.

## `normal`

Biểu diễn sự vắng mặt đã review của hành vi target chỉ khi formulation B cần một explicit negative class. Với formulation A, background/no target có thể không phải là một annotated person-behavior box. P1 phải chọn và tài liệu hóa.

## Source aliases (Ánh xạ từ nguồn gốc)

`head_turn` chỉ được map sang `looking_around` sau khi sample semantics khớp nhau. `Phone use` chỉ được map sang `phone_use` sau audit. `cheating`, `no_cheating` và các nhãn ý định khác yêu cầu re-review/relabel hoặc từ chối — không bao giờ map trực tiếp theo tên.
