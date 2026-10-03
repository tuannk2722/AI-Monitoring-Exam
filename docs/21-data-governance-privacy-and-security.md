# 21 — Quản trị Dữ liệu, Quyền riêng tư và Bảo mật

Dự án chỉ là demo học thuật. Không được ghi, upload hoặc chia sẻ video giống kỳ thi của người thật (identifiable) cho đến khi giáo viên/nhóm phê duyệt bằng văn bản về: consent, storage, access, retention và deletion procedure.

## Chính sách tối thiểu trước khi thu thập dữ liệu

- mục đích, consent tự nguyện và đầu mối rút consent;
- không dùng cho kỳ thi/kỷ luật thật;
- pseudonym cho participant; không có tên/mã sinh viên trong filename;
- danh sách chính xác người thu thập/xem được và quyền Drive/Colab/W&B;
- liệu có được phép xử lý bởi bên thứ ba không;
- thời hạn retention raw/processed/evidence và owner deletion;
- phương án xử lý nếu share link/credential bị lộ;
- giới hạn domain/bias (camera, occlusion, ánh sáng, quần áo, vị trí ngồi).

Áp dụng least access (quyền tối thiểu cần thiết); shared Drive chỉ giới hạn cho nhóm, do thành viên được chỉ định sở hữu. Credential nằm trong config local/Colab secret, không vào Git/notebook/log. W&B logging mặc định off; không bao giờ log ảnh/video cá nhân trừ khi policy cho phép rõ ràng.

Khi một participant rút consent: xác định asset qua manifest/provenance pseudonym, xóa các bản sao được ủy quyền/cache/remote artifact theo yêu cầu policy, rebuild dataset version bị ảnh hưởng và ghi lại supersession mà không lộ danh tính.

Đây là governance của project, không phải tư vấn pháp lý; vẫn cần có sự phê duyệt của giáo viên/cơ sở đào tạo.
