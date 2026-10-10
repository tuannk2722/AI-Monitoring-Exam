# QA flags và phản hồi owner sau R7

Ngày 2026-10-09. Các trạng thái dưới đây là **final proposal của đợt audit**, chưa là canonical target hay owner approval. Thứ tự `phone_use / looking_around`. R7 được giữ nguyên. [Receipt phản hồi](owner-feedback-receipt.json), [delta R1](owner-final-overrides.json), [sửa thêm R2](owner-recrop-extra-r2.json).

Đã xem source local, crop R7 và input224 của cả 15 ID trong bảng; đã xem thêm crop/input224 mới của A035, B040, C093, C094 và D026. Native224 dùng đúng RGB letterbox bilinear/fill E003; phóng nearest chỉ phục vụ nhìn pixel, không phục hồi thông tin. Các crop mới còn phải được owner nghiệm thu. Lỗi hoặc ca chưa rõ được giữ trong package để review, không bù quota bằng candidate dễ.

| ID | R7 phone/looking | Proposal hiện hành | Kết luận QA / điều kiện owner chốt |
|---|---|---|---|
| V7-A-002 | P/N | P/N | Mobile trắng trên own workarea cạnh calculator có phím. Giữ nhãn đề xuất; bỏ narrative calculator/neighbor gây hiểu nhầm. |
| V7-A-035 | P/N | P/N, recrop | Mở mép phải để giữ cả mobile đen và tay nữ foreground, mở trên để giữ đầu. Không lấy mobile xanh của nam kế bên làm evidence của nữ. |
| V7-A-061 | N/N | N/N | Vật đen có đế/cần kim loại là dụng cụ bấm giấy; tay đang giữ bản nhạc. Reason hiện hành không gọi vật này là phone. |
| V7-B-079 | P/U | U/U, recrop | Tay chạm má, không mobile rõ; crop cũ còn cắt người. Không dùng P, cũng không suy thiếu evidence thành N. |
| V7-B-080 | P/U | U/U | Thiết bị trong lab chưa chứng minh mobile. Nguồn local1024 chưa là bằng chứng đã kiểm ảnh nguyên gốc độ phân giải cao; pending xác minh device. |
| V7-B-040 | N/N | N/N, recrop | Tập trung nam áo xám ở giữa, nhìn xuống sách/giấy. Foreground arm còn chồng lấn vật lý, anchor được nêu rõ. |
| V7-C-025 | U/P | U/U, recrop | Nam áo trắng/khăn đỏ ở bàn nhóm; gaze đối với sách chung chưa rõ. Group activity không tự chứng minh nhìn ra khỏi bài. |
| V7-C-036 | U/P | U/U, recrop | Mở workarea nhưng ghế/người vẫn che bài riêng. Head tilt không đủ P. |
| V7-C-089 | U/N | U/U | Nam plaid phía sau không có own paper rõ như QA cũ ghi. Gaze so với người foreground/bàn chưa đủ P/N. |
| V7-C-090 | U/P | U/P | Nữ tóc vàng giữ tờ bài trước người, nhìn rõ sang nữ ở giữa. Giữ P theo static semantics; không suy vi phạm từ hoạt động nhóm. |
| V7-C-092 | U/P | U/U, recrop | Nữ áo vàng foreground, đầu xuống trái; workarea/gaze chưa đủ phân biệt giấy với người bên cạnh. |
| V7-C-093 | U/N | U/N, recrop | Chỉ rõ nam ngồi cạnh trái bàn foreground, tay/bút và vùng viết; giảm người đứng/background trong crop. |
| V7-C-094 | U/N | U/N, recrop/reanchor | Chỉ rõ nữ kính phía phải bàn foreground, giữ đầu/tay/trang. Unit R7 chưa rõ; cần owner xác nhận người, không khẳng định cùng unit đã được duyệt. |
| V7-C-117 | U/P | U/U | Screen và người đối diện cùng hướng nhìn; chưa đủ xác nhận P/N. Bỏ hai câu own-laptop/ngoài-laptop mâu thuẫn. |
| V7-D-026 | P/U | N/N, recrop | Mobile ở tay nam teacher; nữ áo sọc viết bút. Nữ là anchor, không co-occurrence P/P; useful crowded ownership negative. |

Các thay đổi đề xuất tới U dựa vào kiểm evidence mới; QA flag không tự tạo nhãn mới được duyệt. Không sửa target/mask/split của R7 hoặc parent v6. Những ID U/U được đề xuất `review_only/quarantine` cho đến khi đủ evidence; không tính làm support supervised hoặc negative matched pair.

QA bổ sung ở bucket B/D phát hiện B048 crop sai vùng người, B096/B100 negative chưa đủ evidence và B111 cắt tay viết. [Delta R2](owner-recrop-extra-r2.json) ghi geometry/labels/reason đề xuất rõ. Device ambiguity ở D006/D025/D033 và evidence phone nhỏ/partial tại224 được lưu trong báo cáo input224 riêng. Đây là ngoại lệ mới cần owner review, không tự đóng từ phản hồi chín ID ban đầu.

Owner là chủ repository; điều kiện đóng từng case: xem đúng source/crop/input224 theo final pointer, xác nhận anchor/device/gaze và accept/reject proposal hoặc giữ U. Quyết định này không đồng thời approve membership, nhóm/split, public rights, release hoặc E004 execution.

## Bổ sung từ pair QA cuối R5

V7-B-066 có cùng source với B020, nhưng anchor là nam áo trắng/khăn đỏ ở giữa phía sau; crop chứa foreground và không đủ own workarea/phone visibility. Đề xuất U/U thay N/P sau xem source/crop/input224; không dùng làm looking matched pair hiện tại. V7-C-131 giữ U/N, reason mới chỉ rõ nam áo đen bên phải đang nhìn tờ giấy cầm. Hai proposal same-image khác còn pending owner: B039/B089 phone, B102/C131 looking; đều auxiliary, không tăng nhóm độc lập.

Final dùng [review R5](../../../outputs/v7-owner-review-r5-20261009/review-index.html) và [delta bổ sung](owner-pair-visibility-extra-r4.json); tổng31delta, không phải31approval. [Annotation cuối](annotation-analysis-final.md) thay snapshot R4.
