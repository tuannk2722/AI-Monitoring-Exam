# ADR-004 — Môi trường Hybrid: Local và Colab Free

- Status: Accepted
- Date: 2026-09-19

**Quyết định**: máy local xử lý development/test/audit nhỏ/inference; Colab Free xử lý GPU training; inference benchmark cuối dùng demo hardware thật. Module canonical nằm trong repo; notebook chỉ là launcher.

**Hệ quả**: checkpoint/resume/persistent artifact sync và 1–3 epoch preflight là bắt buộc vì runtime/GPU không được đảm bảo.
