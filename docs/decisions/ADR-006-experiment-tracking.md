# ADR-006 — Canonical experiment record và W&B tùy chọn

- Status: Accepted
- Date: 2026-09-19

**Quyết định**: YAML config, run JSON/experiment card, Git/DVC provenance và metrics là canonical. W&B là shared logging/visualization tùy chọn, disabled mặc định đến khi được cấu hình. Không tự host MLflow trong phase này.

**Hệ quả**: mất W&B không mất reproducibility; logging media nhạy cảm cần policy phê duyệt.
