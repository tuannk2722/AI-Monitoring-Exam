# Coverage nhãn phải giải quyết failure mode E003

Trạng thái: Draft audit metadata. Không suy crop count thành model improvement hoặc promotion.

Desk-phone R7 có 57 candidate, 32P/25N, nhưng đúng classroom/exam-context chỉ có 12 (6P/6N). Vì vậy 26/32 phone positives (81,25%) và 19/25 negatives (76%) trong bucket A là public auxiliary ngoài exam. Đây là cảnh báo domain coverage cho lỗi desk-phone của E003: có điện thoại trên bàn trong ảnh public không chứng minh đủ điện thoại trên bàn thi, camera phòng thi hoặc matched negatives cùng cảnh. Owner review R4 sửa crop A035 nhưng không tăng group diversity hoặc số A.

Tất cả bucket phải đọc theo target và mức biết nhãn. 274 crop final chỉ có 70 fully-known; 15 crop U/U phải tiếp tục review_only, còn 189 crop biết một target. Cả bốn tổ hợp fully-known có support 10P/P, 3P/N, 8N/P, 49N/N. Riêng P/N ít không thể tự đặt quota mới hoặc tự chốt acceptance metric, nhưng cần nêu rõ khi owner nghiệm thu membership.

98 looking candidates R7 là 49P/49N theo proposal. Camera/room/session không được ghi nhận rõ thì báo unknown; không lấy tên source hoặc visual family làm camera/session. Cân bằng 49/49 chưa loại source/room confounding. Sau QA gaze/anchor, phải dùng final labels trong package R4 để xem matched pairs còn đúng target; 21/162 pair R7 không còn P/N, chưa được giữ làm supervision của pair.

Bucket crowded không có nghĩa mọi crop chứa co-occurrence. Chỉ proposed P/P của cùng anchor được đếm là target co-occurrence; U/P, P/U và U/U không được chuyển thành P/P vì ảnh có nhiều người hoặc phone của người bên cạnh. Cần owner nhìn nguồn/crop/input224 và ownership; bảng từng D crop trong annotation audit giữ trạng thái Draft này rõ ràng.

Pair strength và diversity là hai đại lượng khác nhau. Cặp cùng ảnh có bằng chứng camera/cảnh tại một thời điểm mạnh hơn source-context, nhưng thêm anchor cùng ảnh không tạo nhóm độc lập mới. Một negative dùng bởi nhiều positives cũng không tăng independent sample count. Nếu không có session metadata hoặc scene review rõ, không báo tìm được matched session pairs.

Ưu tiên R8 vẫn là classroom/exam desk-phone P/N mới với workarea và đúng người; looking P/N cùng camera/cảnh có own workarea; crowded ownership/co-occurrence thật; small/partial variation sau input224. Báo actual yield và independent diversity gain sau graph QA; nếu mới chỉ có unused metadata rows thì eligible independent pool vẫn unknown, không exhausted và không refill bằng crop dễ.
