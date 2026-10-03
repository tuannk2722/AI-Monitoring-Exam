# ADR-005 — DVC với Google Drive do owner kiểm soát

- Status: Accepted
- Date: 2026-09-19

**Quyết định**: Git lưu source/config/docs/metadata; DVC với folder Google Drive restricted do thành viên được chỉ định sở hữu sẽ lưu dataset/model/artifact lớn. Credential giữ local/secret.

**Hệ quả**: nhóm test push/pull nhỏ trước; `dvc push` phải đi trước khi publish Git pointer; khôi phục được verify từ tag/commit.
