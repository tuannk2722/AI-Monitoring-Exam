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
4. Khởi tạo DVC và thêm folder ID Drive thật do owner kiểm soát.
5. Kiểm tra `dvc push/pull` bằng một fixture nhỏ không nhạy cảm.
6. Điền owner vào ADR/template/board.

## P0 Definition of Done (Điều kiện hoàn thành P0)

Owner có thể tái tạo từ clone sạch: clone repo, cài dependency base/dev, chạy tests, giải thích cây thư mục, tạo branch/PR, và push rồi khôi phục cùng một DVC artifact nhỏ bằng cache sạch và đối chiếu checksum. Chưa kiểm chứng DVC push/pull thì P0 chưa hoàn tất; xem WORKLOG. Không có credential hay binary lớn nào xuất hiện trong lịch sử Git.
