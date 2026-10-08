# Bằng chứng nghiên cứu và đề xuất nguồn v6

Ngày 2026-10-07. [Báo cáo tổng hợp](../../../docs/data/pilot-b-v6-source-proposal-20261007.md). Đây là audit/proposal, chưa là dataset accepted hoặc kết quả model.

- `source-metadata.json`: snapshot web và đối chiếu đúng version/payload, không dùng số project thay số export.
- `roboflow-payload-audit.json`: SHA ZIP, YAML/README nguồn, counts từng class/split, lỗi validator, lineage hint và receipt ảnh mẫu.
- `roboflow-duplicates.json`: exact SHA byte/RGB trong ba ZIP mới và RF cũ, kể cả trùng qua split.
- `cross-source-triage.json`, `cross-source-visual-receipts.json`: nearest dHash với RF cũ/SCB và chín cặp đã xem. Chỉ triage, không tự gán group.
- `v5-near-triage.json`: cờ tương tự với ảnh nguồn ledger v5, không model inference.
- `fpi-payload-audit.json`, `fpi-followup.json`: audit ZIP FPI và lỗi định dạng/hình học; raw_class_counts không là bbox hợp lệ.
- `target-unit-review.json`: 28 bbox train minh họa và nhận xét unit; chưa phải nhãn/crop được nghiệm thu.
- `preview-evidence.json`: sáu thumbnail công khai xem trước khi owner xác nhận ZIP, không đại diện toàn bộ dữ liệu.
- `provenance.json`: hash inputs/artifacts/scripts/media local cần để truy vết.
- `verification.json`: kết quả kiểm bằng chứng và bảo toàn v5.

Script exploration và media ở `outputs/pilot-b-v6-source-research-20261007/`, không commit. Để chạy lại audit local: `.venv/Scripts/python.exe -X utf8 outputs/pilot-b-v6-source-research-20261007/audit_roboflow_payloads.py`; script đọc ZIP ở Downloads, không sửa raw. Những script này là exploration, không phải logic production/importer. Hash script và inputs được pin trong provenance.

Không đồng nhất project images, export images, dòng bbox, person crop và số nhóm độc lập. Một dòng sai không được âm thầm sửa. Mẫu xem semantics chọn theo tên và heuristic, không phải sampling để ước lượng error rate. Chưa review toàn bộ nhãn/crop/group; chưa đủ điều kiện build release v6.
