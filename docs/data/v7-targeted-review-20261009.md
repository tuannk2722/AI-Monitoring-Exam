# V7 — Targeted expansion để owner nghiệm thu

Ngày: 2026-10-09. Trạng thái: **Draft có shortage, chưa release/train**. [Báo cáo và bằng chứng](../../artifacts/reports/pilot-b-v7-targeted-20261008/README.md), [pointer cuối](../../artifacts/reports/pilot-b-v7-targeted-20261008/review-pointer-final.json), [review có attribution](../../outputs/v7-public-attribution-r7-review-20261009/review-index.html), [config R7](../../configs/datasets/pilot_b_v7_targeted_review_r7.yaml).

Sau khi xem 1.303 ảnh screening, đã dựng/QA274crop: desk-phone57/80, phone cầm tay nhỏ/partial cùng negative80/80, looking98/100, crowded39/40. Còn thiếu 26 crop; không đưa ảnh sai thiết bị/ownership, gaze mơ hồ, họ hàng evaluation hoặc quyền chưa kiểm vào quota. 143 crop có ngữ cảnh lớp/phòng thi và 131 crop public bổ trợ ngoài phòng thi. Đây là phân loại ngữ cảnh, không xác nhận độc lập scene/person hoặc số đã accepted.

Nhãn P/N/U là proposal, canonical mask vẫn 0, split/group null và training-eligible false. [ADR-018](../decisions/ADR-018-v7-mobile-phone-boundary.md) chỉ chốt mobile; không approve membership hoặc train.49 cell owner review E003 được lưu delta riêng cho version sau; v4–v6 và E001–E003 giữ nguyên. Hai tài liệu owner review gốc vẫn có snapshot/pins trong báo cáo.

Mở trang review để xem đúng người, head/tay/phone/workarea. Trang unit/pairs được liên kết từ đó. Owner có thể chấp nhận batch crop/nhãn/phenotype, kèm ngoại lệ ID; không phải tự annotate 274 ảnh. Quyết định quyền/notice từng nguồn public và family graph chưa tự được chốt bởi việc đồng ý dữ liệu bổ trợ. 131 crop public có attribution/license khớp metadata quan sát;34 ảnh khác còn blocker nằm ngoài primary.

162 pair links chỉ có 6 cùng ảnh và 1 cùng cảnh; 155 cặp chỉ match ngữ cảnh, chưa cùng camera/session. 232 family hints không là 232 nhóm độc lập. Các thiếu hụt matching/lineage/domain cần giải quyết trước split và E004; số lượng crop đủ budget không tự đóng promotion gates.

Canonical CLI nằm trong `ai_exam_monitoring.data`: `pilot_targeted_expansion`, `coco_targeted_candidates`, `openimages_targeted_candidates`, `targeted_review_package`, `public_attribution_audit`. YAML chứa pins, pool/budget và output identity. Ví dụ launcher builder:

```powershell
$env:PYTHONPATH='src'
.venv/Scripts/python.exe -m ai_exam_monitoring.data.targeted_review_package --config configs/datasets/pilot_b_v7_targeted_review_r7.yaml
```

R7 đã tồn tại nên lệnh này sẽ từ chối ghi đè theo thiết kế. Muốn sửa/rebuild phải tạo config/output version mới, giữ pins input và bằng chứng cũ. Không chạy builder/trainer lên accepted release để sửa nhãn. Source downloads chỉ original train, kiểm TLS/bytes/MD5 khi có/parent fingerprints trước decode; ảnh và checkpoint không được commit hoặc upload.

203 tests, Ruff, mypy6module mới, integrity/checksum và repo/diff checks PASS. Full mypy còn66lỗi legacy; báo cáo validation ghi rõ phạm vi. Holdout công khai độc lập vẫn là task riêng theo [hồ sơ E004](../experiments/E004-preparation.md) và [thẩm định holdout](E004-public-holdout-research-20261008.md).
