# Bàn giao staging mở rộng R2

Ngày 2026-10-06. **Đã hoàn tất staging review-only theo phê duyệt R2 của owner.**

[Approval](owner-approval.json) pin đúng báo cáo/pointer/proposal đã review. [Xác nhận quyền sử dụng](owner-rights-confirmation.json) ghi quyết định mới nhất của owner cho các dataset đang dùng; điều kiện chặn quyền SCB/RF được đóng. Các snapshot R2 trước approval được giữ nguyên để truy vết, không phản ánh trạng thái hiện hành.

## Gói bàn giao

[Pointer staging](../../../configs/datasets/pilot_b_expansion_v5_r2_staging.yaml) trỏ tới [package cục bộ](../../../data/interim/pilot-b/pilot-b-expansion-20261006-r2-staging/dataset-card.md), trạng thái `prepared_pending_gates`.

- 72 record mới: 48 SCB, 24 RF; 61 review_only, 11 excluded.
- 61 crop xuất đúng hash/pixel được duyệt; hai crop RF-003/RF-014 dùng refinement.
- Nhãn được nhập theo từng crop SHA; unknown vẫn null/mask 0.
- [11 liên hệ cảnh](scene-constraints.json) đã nghiệm thu; group ID/split vẫn null. Không suy độc lập từ việc không có cạnh.
- Parent v4 gồm 112 ledger/84 manifest và queue 28 review_only giữ nguyên. Staging chỉ chứa 72 candidate mới; không tự quyết membership release v5 hợp nhất.

| Coverage trong 61 mẫu giữ | Positive | Negative | Unknown |
|---|---:|---:|---:|
| phone_use | 1 | 23 | 37 |
| looking_around | 23 | 14 | 24 |

Có 39 mẫu biết ít nhất một target, 22 mẫu cả hai unknown, 13 normal xác nhận. Số mẫu không tương đương số tình huống độc lập; phone positive mới vẫn thuộc RF.

## Kiểm chứng và tái tạo

[Kết quả kiểm chứng](verification.json), [kết quả build/checksum](build-result.json), [ledger đã duyệt](review-ledger.jsonl), [metadata build](build-metadata.json). Schema/builder canonical được tái sử dụng; không thay code để bỏ gate.

Để tái tạo, dùng Python environment của repo và `build_pilot_package` trong `ai_exam_monitoring.data.pilot_package`: đọc ledger bằng `read_records`, đọc selection JSONL và build-metadata/build-inputs đi kèm; truyền output mới, source_roots/crop_inputs/expected_sample_ids từ build-inputs. Builder từ chối ghi đè gói cũ. Sau build, dùng dataset-card.md tiếng Việt đi kèm thay card mặc định, tính lại checksums.sha256 cho mọi file payload (không bao gồm chính checksum list). So sánh checksum với pointer trước khi sử dụng.

## Phạm vi hoàn tất và phần sau

Đợt này hoàn tất tuyển candidate, QA thị giác, nghiệm thu nhãn/crop/liên hệ, draft pointer và staging. Không còn chờ owner duyệt lại proposal R2 hoặc quyền các dataset đang dùng. Chưa phát hành v5, chưa train E002, chưa upload/commit/push. Bước release riêng cần chốt nhóm toàn bộ/membership, split và protocol đánh giá; không dùng test E001 để tuning.

Luồng Classroom-monitoring đã hoàn tất [thẩm định metadata trong phạm vi ban đầu](../data-expansion-20261006/classroom-monitoring-metadata-review.json). Nguồn này chưa nhập media vào project. Đường dẫn/version cụ thể và dữ liệu unit/group chưa được cung cấp; các thông tin kỹ thuật đó cần khi mở đợt nhập nguồn mới. Không mở lại câu hỏi quyền sử dụng đã được owner xác nhận.
