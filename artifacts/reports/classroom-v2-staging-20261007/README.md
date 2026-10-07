# Classroom v2 — bàn giao staging

Ngày 2026-10-07. **Đã nhập phê duyệt 24 crop/nhãn và gộp 150 ảnh nguồn thành nhóm CM-V2-SCENE-01; staging hoàn tất.**

[Approval](owner-approval.json) ghi nguyên ý kiến owner và pin artifact. [Quyết định nhóm](group-decision.json) liệt kê SHA toàn 150 ảnh: các mẫu nhập sau từ cùng danh sách cũng phải cùng nhóm, không chia sang nhiều split. Đây là nhóm gộp thận trọng, không khẳng định timestamp/session thực.

[Pointer staging](../../../configs/datasets/classroom_monitoring_v2_staging.yaml), [package cục bộ](../../../data/interim/pilot-b/classroom-v2-20261007-staging/dataset-card.md). Gói chứa 24 record/crop review_only, chưa phải release v5 hợp nhất.

| Target đã duyệt | Positive | Negative | Unknown |
|---|---:|---:|---:|
| phone_use | 6 | 10 | 8 |
| looking_around | 7 | 5 | 12 |

19 mẫu biết ít nhất một target; 5 mẫu cả hai unknown, 5 normal, 2 co-occurrence. Unknown giữ null/mask0. Quyền nguồn theo xác nhận owner, không yêu cầu lại.

[Verification](verification.json) PASS: 24 source/label/crop SHA và pixel, nhãn đúng proposal theo hash, schema/mask, quyết định nhóm150 ảnh, pins; v4/R2 payload bất biến. Không sửa code nghiệp vụ nên không chạy lại unit suite; sử dụng kiểm chứng dữ liệu và builder canonical.

README proposal đã được sửa khoảng trắng sau verification cũ; chỉ README khác hash, các artifact dữ liệu/nhãn/crop/group/config vẫn khớp. Approval mới pin README hiện tại và lưu hash lịch sử; không sửa evidence cũ hoặc ghi đè thay đổi owner.

## Tái tạo

Đọc review-ledger.jsonl bằng read_records, selection.jsonl, build-inputs.json và build-metadata.json đi kèm; truyền vào build_pilot_package với output mới, không ghi đè. Sau build thay dataset-card.md bằng bản tiếng Việt đi kèm và tái lập checksums.sha256 cho toàn payload trừ chính checksum list. So checksum với pointer. Logic nằm trong src/ai_exam_monitoring/data/pilot_package.py; metadata pin implementation và Git dirty.

## Bước tiếp theo

Crop/nhãn/nhóm Classroom đã duyệt, không còn chờ nghiệm thu lại. Để phát hành v5 cần hoàn thiện nhóm SCB/RF, chọn membership hợp nhất và split/protocol đánh giá; toàn Classroom phải nằm cùng một split nếu được dùng. Chưa chọn train/val/test, chưa train E002, upload, commit hoặc push.
