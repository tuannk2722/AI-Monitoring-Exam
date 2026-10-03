# ADR-007 — Bỏ Django prototype; hoãn FastAPI web sang P7

- Status: Accepted
- Date: 2026-09-19

**Quyết định**: bỏ Django/Cloudinary/dashboard prototype vì không có AI core nào có thể tái sử dụng và mã hóa sai domain semantics. Tại P7 dùng FastAPI local + Jinja2 + JavaScript nhỏ + SQLite sau khi domain contract ổn định.

**Hệ quả**: repository hiện tại không có web giả. Pipeline và contract recorded sẽ được xây dựng trước.
