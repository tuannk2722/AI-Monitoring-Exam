# Pilot B v6 — release local đã hoàn tất

Owner nghiệm thu ngày 2026-10-07; hoàn tất kiểm chứng/bàn giao ngày 2026-10-08 sau gián đoạn hạn mức công cụ. Giữ dataset ID **pilot-b-20261007-v6** theo phương án đã duyệt.

[Config accepted](../../../configs/datasets/pilot_b_release_v6.yaml) · [Pointer/checksum](release-pointer.json) · [Approval](owner-approval.json) · [Dataset card](../../../data/processed/pilot-b/pilot-b-20261007-v6/dataset-card.md).

| Nội dung | Số lượng |
|---|---:|
| Train | 317 |
| Validation | 50 |
| Test v5 giữ nguyên | 11 |
| Manifest dùng | 378 |
| Review_only | 93 |
| Excluded | 27 |
| Ledger | 498 |
| Crop xuất trong release | 471 |

**Dùng `manifest.jsonl` làm danh sách dữ liệu**, không lấy toàn thư mục crops: 93 crop review_only nằm ngoài training/evaluation. 27 excluded chỉ giữ metadata. Gói review có 487 crop vì còn 16 crop mới đã quyết định excluded; canonical exporter không xuất 16 crop này. Đây là cách đóng gói đúng trạng thái đã duyệt, không đổi membership.

Release nằm tại `data/processed/pilot-b/pilot-b-20261007-v6`. Scope `local_classifier_research`; target order `[phone_use, looking_around]`, unknown vẫn null/mask0. FPI và Discuss ngoài đợt này như phương án đã duyệt.

## Bảo toàn và kiểm chứng

[Verification](verification.json), [evaluation preservation](evaluation-preservation.json) và [nhóm đã nghiệm thu](group-boundaries.json):

- 498 record khớp từng usage, target, mask, group, source SHA và crop SHA/tọa độ của assignment đã duyệt. Manifest đúng 378 record; không xung đột image/crop/group giữa các split.
- 104 mẫu đã dùng của v5 giữ nguyên source/crop/nhãn/context/rights/group/split và test-freeze evidence; version đóng gói và release review chuyển sang v6. Bao gồm 80 train, 13 val lịch sử, 11 test. Payload v5 và gói review owner đã duyệt không đổi.
- 16 parentreview_only có nhãn unknown được điền đúng approval. Những mẫu parent trước đây chỉ có scope preparation hoặc scope trống được gắn approval local classifier cho membership mới, giữ license/attribution đã kiểm; không đổi quyền của104mẫu đã dùng.
- Canonical exporter kiểm source decode/dimension/label hash và pixels crop. Schema, checksum 471 crop và public loader `verify_dataset` PASS. Loader check chỉ integrity, không inference hoặc chạy experiment.
- 162 unittest PASS; Ruff/Mypy phạm vi mới PASS; `git diff --check` PASS; repository checker failures0 (chỉ Git index).

Inline test freeze v6 pin hash serializer của manifest/split version mới bằng helper hiện có. Danh sách 11 test, crop, nhãn và evidence gốc được đối chiếu riêng với v5; không chọn lại test, không mở quyền inference mới. Validation 50 bao gồm 13 val v5 lịch sử; không so metric toàn bộ 50 với E002 trên 13.

## Provenance và tái tạo

Approval pin nguyên báo cáo, config proposal, assignment, decisions, candidate, parent và checksum gói review. [Provenance](provenance.json) ghi code/config hash và Git commit nền; workspace có thay đổi chưa commit. Các snapshot proposal đã duyệt được giữ nguyên.

Logic materialize nằm trong `src/ai_exam_monitoring/data/pilot_review_acceptance.py`, dùng schema/exporter canonical hiện có, có guard bảo toàn parent và pin approval. CLI:

```powershell
.venv/Scripts/python.exe -X utf8 -m ai_exam_monitoring.data.pilot_review_acceptance --config configs/datasets/pilot_b_release_v6.yaml
```

Lệnh từ chối ghi đè package đã tồn tại. Tái lập chỉ chạy trong workspace phục hồi có inputs/evidence/cache nguồn đúng pin và chưa có output; không xóa release hiện hành để chạy lại. Dataset card tiếng Việt và checksum được hoàn thiện trước khi phát hành pointer.

**Hoàn tất phạm vi đóng release local.** Chưa train model mới, chưa tính metric, chưa upload hoặc commit/push. Chất lượng model và khả năng tổng quát thực tế chưa được chứng minh bởi việc tăng dữ liệu. Bước AI tiếp theo là chuẩn bị experiment trên v6 với config và protocol đánh giá riêng; approval dataset không tự cho phép thay recipe hoặc chạy test.
