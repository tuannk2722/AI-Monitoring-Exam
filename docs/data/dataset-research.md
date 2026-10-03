# Dataset Research — Bản ghi làm việc

## Danh mục candidate

| ID | Candidate | Trạng thái hiện tại | Bằng chứng còn thiếu |
|---|---|---|---|
| DS-SCB5 | SCB5 | CANDIDATE / chưa được chấp nhận | Đã pin ba ZIP và audit; owner phê duyệt quyền/metadata. Còn QA/unit, group mapping thực tế, near-duplicate và mapping canonical |
| DS-RF-EXAM | Roboflow Exam Cheating CV export/model source | CANDIDATE / chưa được chấp nhận | Đã pin và audit v1 owner ZIP; còn unit/semantics, near-duplicate/grouping, phạm vi quyền theo asset và quyết định subset |

Không được ghi tên dataset và đánh dấu là đã chọn. Data Lead tạo candidate card riêng cho từng nguồn và đính kèm audit report/checksum/bằng chứng license.

## Hypothesis kết hợp nguồn

SCB5 có thể đóng góp mẫu hành vi giống kỳ thi; Roboflow có thể mở rộng mẫu đã annotate. Kết hợp hai nguồn chỉ hợp lệ khi: canonical semantics khớp nhau, provenance/trùng lặp đã rõ ràng, license cho phép sử dụng, và grouped split ngăn được source/video leakage. Source được giữ lại trong manifest để có thể báo cáo metrics per-source và domain bias.

## Decision gate (Điều kiện quyết định)

Chấp nhận/từ chối mỗi nguồn độc lập. Nếu một nguồn thất bại về quyền/chất lượng/mapping, baseline có thể dùng nguồn còn lại hoặc một subset đã review. Số lượng mẫu lớn hơn không phải lý do để giữ lại nhãn không tương thích.


## Audit phiên bản SCB owner cung cấp — 2026-10-03

Đã kiểm toàn bộ ba ZIP Discuss 2024-9-17, Handrise-Read-write 2024-9-17 và BowTurnHead 20250509, SHA-256 local khớp blob Hugging Face. [Candidate card](candidates/SCB5-supplied-20261003.md), [báo cáo](candidates/SCB5-supplied-20261003-audit.md), [ảnh cần review](candidates/SCB5-supplied-20261003-review.md).

10.138 ảnh/cặp nhãn; 546 file label bị flag; không ảnh hỏng/thiếu cặp. 8.116 SHA-256 ảnh duy nhất; 961 nhóm exact duplicate chéo train/val khi xét chung ba phần. Chưa kiểm tra gần trùng hoặc xác định video/session group. Không có class phone_use/normal nguồn; Discuss có box nhóm. Giữ CANDIDATE, chưa đủ bằng chứng chốt A/B. Không đổi status trong config hay mapping canonical.

## Cập nhật 2026-10-04

Owner loại Discuss, xác nhận phê duyệt quyền/metadata SCB; giữ quyết định đã ghi trong candidate SCB. Chưa có bảng group mapping từng file để thực thi split.

Roboflow v1 đã audit 3,407 cặp, pin SHA ZIP và lưu [bằng chứng](../../artifacts/reports/roboflow-20261004/provenance.json). [Báo cáo](candidates/Roboflow-phone-use-20261004-audit.md), [ảnh/câu hỏi review](candidates/Roboflow-phone-use-20261004-review.md), [candidate/mapping/P1](candidates/Roboflow-phone-use-20261004.md). Có 35 dòng vượt biên trong 34 file, mức khoảng 0.005 pixel; không tự repair. Phone use 120 raw annotations trên 98 ảnh, trong đó train 82 trên 66 ảnh; strict chỉ 117 trên 95 ảnh vì loại file có dòng lỗi ở lớp khác.

Đã xem 16 train samples + 2 warning images, thấy Phone use trộn phone/hand/person unit, có mẫu lớp 0/1 không khớp semantics dự kiến. Exact duplicate nội bộ/cross-split/cross-SCB đều 0; chưa near-duplicate hoặc group leakage. Giữ CANDIDATE để review/relabel subset train; chưa đủ bằng chứng chốt A/B. Không dùng thiếu box hoặc tên No cheating làm normal/negative.

Roboflow owner review 2026-10-04: đã trả lời 18 mục; person unit/phone_use theo [ADR-011](../decisions/ADR-011-person-unit-phone-definition.md). W02 có geometry preview; W01 và batch relabel/QA còn mở. Candidate/pending_audit, A/B và split chưa chốt.
