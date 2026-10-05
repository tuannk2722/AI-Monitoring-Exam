# 07 — P0 Project Foundation (Nền tảng Dự án)

## Đã được triển khai trong repository này

- Một repo chuẩn tắc với `src/`, `configs/`, `tests/`, `docs/`, `data/`, `artifacts/`, `.github/`.
- Đã xóa Django/Cloudinary/mock dashboard; không có kết quả AI giả.
- Python packaging và tách riêng các nhóm dependency base/dev/ml/DVC.
- Unit test, kiểm tra compile/repository và GitHub Actions.
- DVC pipeline skeleton và tài liệu setup Google Drive cụ thể.
- Task/PR template thật sự và các contract có version.

## Các hành động owner vẫn cần thực hiện

1. Xác minh remote repository; GitHub Project tùy chọn, có thể theo dõi bằng WORKLOG.
2. Bảo vệ `main`, yêu cầu CI và owner tự review có bằng chứng; không yêu cầu người thứ hai.
3. Clone sạch, cài base/dev trên Python 3.11 và chạy các lệnh CI.
4. DVC đã cấu hình remote `teamdrive`; credential local/ignored.
5. Smoke push/pull từ exact commit/cache sạch đã đạt; fixture và clone thử đã dọn, evidence trong WORKLOG. Không tạo lại fixture để đóng cùng gate.
6. Điền owner vào ADR/template/board.

## P0 Definition of Done (Điều kiện hoàn thành P0)

Owner có thể tái tạo từ clone sạch: clone repo, cài dependency base/dev, chạy tests, giải thích cây thư mục, tạo branch/PR, và push rồi khôi phục cùng một DVC artifact nhỏ bằng cache sạch và đối chiếu checksum. Storage smoke gate đã đạt; fresh Python installation/remote CI/main protection còn cần evidence riêng, không tự đóng toàn P0. Không commit credential hoặc binary lớn; checker kiểm index hiện tại, không thay audit lịch sử Git.
