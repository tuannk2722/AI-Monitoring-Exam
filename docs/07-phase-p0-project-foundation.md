# 07 — P0 Project Foundation (Nền tảng Dự án)

## Đã được triển khai trong repository này

- Một repo chuẩn tắc với `src/`, `configs/`, `tests/`, `docs/`, `data/`, `artifacts/`, `.github/`.
- Đã xóa Django/Cloudinary/mock dashboard; không có kết quả AI giả.
- Python packaging và tách riêng các nhóm dependency base/dev/ml/DVC.
- Unit test, kiểm tra compile/repository và GitHub Actions.
- DVC pipeline skeleton và tài liệu setup Google Drive cụ thể.
- Task/PR template thật sự và các contract có version.

## Các hành động nhóm vẫn cần thực hiện

1. Tạo remote repository và GitHub Project.
2. Bảo vệ `main`, yêu cầu CI/reviewer.
3. Cài đặt dependencies trên cả ba máy.
4. Khởi tạo DVC và thêm folder ID Drive thật do owner kiểm soát.
5. Kiểm tra `dvc push/pull` bằng một fixture nhỏ không nhạy cảm.
6. Điền owner vào ADR/template/board.

## P0 Definition of Done (Điều kiện hoàn thành P0)

Cả ba thành viên đều có thể: clone repo, cài dependency base/dev, chạy tests, giải thích cây thư mục, tạo branch/PR, và trao đổi cùng một DVC artifact nhỏ. Không có credential hay binary lớn nào xuất hiện trong lịch sử Git.
