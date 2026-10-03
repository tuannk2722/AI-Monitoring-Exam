# 02 — Phạm vi và Nguyên tắc

## Must/Should/Could (Bắt buộc/Nên có/Có thể có)

| Mức | Nội dung |
|---|---|
| Must | dữ liệu được tài liệu hóa và versioned; contract về label/split; baseline và evaluation có khả năng tái tạo; inference trên video đã ghi; tracking; event timeline; demo risk/evidence/review đơn giản |
| Should | bộ holdout giống kỳ thi thật (local); track ID đủ ổn định; error analysis; báo cáo hiệu năng |
| Could | webcam/live; evidence clip ngắn; hỗ trợ pose; thêm hành vi mới |
| Won't (MVP) | nhiều camera, nhận diện mặt/danh tính, triển khai cloud sản xuất, ứng dụng di động, tự động kỷ luật, auth phức tạp, GRU/TCN (trừ khi baseline chứng minh cần thiết) |

## Nguyên tắc

1. Chất lượng dữ liệu trước độ phức tạp của model.
2. Hành vi quan sát được (observable behavior), không bao giờ gán nhãn đạo đức/kỷ luật.
3. Chia split theo nhóm (grouped split) trước khi tối ưu số lượng mẫu; test set phải luôn bị khóa (locked).
4. Mọi experiment đủ khả năng tái tạo để truy vết code + data + config + artifact.
5. Chế độ video ghi sẵn (recorded mode) trước chế độ live.
6. Code chuẩn tắc trong `src/`; notebook chỉ là launcher có thể bỏ.
7. Web là lớp tích hợp cuối cùng; không để DB schema điều khiển ML contract.
8. Metadata chưa biết để trống/TBD; không được bịa.

## Quy tắc thay đổi phạm vi

Bất kỳ thay đổi nào về class, formulation, dataset, split, metric, risk hay evidence đều cần owner, reviewer, impact statement và cập nhật ADR/config. Nếu deadline bị rút ngắn, ưu tiên cắt giảm UI nâng cao/live/pose/class bổ sung trước khi cắt data/evaluation/tracking cơ bản.
