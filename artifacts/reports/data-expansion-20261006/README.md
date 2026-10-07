# Mở rộng dữ liệu sau E001 — phê duyệt hướng và draft v5

Ngày: 2026-10-06. Owner: chủ repository (solo). Trạng thái: **đã duyệt hướng triển khai; candidate/pointer v5 là Draft, chưa nghiệm thu release**.

## Quyết định đã ghi nhận

[Approval của owner](owner-approval.json) ghi đúng bốn lựa chọn trong hội thoại: hai luồng SCB/RF + nguồn mới; thẩm định metadata Classroom-monitoring-dataset; cho phép draft pointer v5 sau candidate; giữ `phone_use`, `looking_around`, mask `unknown`. Discuss tiếp tục loại. Approval này không thay nhãn, group/split hoặc cấp quyền train/upload.

[Kế hoạch đã đồng bộ](../../../docs/data/data-expansion-20261006.md) giữ các gate còn mở. [Pointer draft v5](../../../configs/datasets/pilot_b_expansion_v5_draft.yaml) tham chiếu parent v4 và [batch candidate](candidate-batch-v5-draft.json) bằng SHA-256; chưa có package v5 hoặc DVC release.

## Luồng SCB/RF hiện có

Kiểm tra lại trực tiếp cho thấy **cả ba archive đang có tại đường dẫn đã pin và khớp SHA-256**. Nhận định thiếu archive trong báo cáo trước không đúng trạng thái kiểm tra lần này; không dùng nó làm blocker. Path/bytes/hash đầy đủ nằm trong `candidate-batch-v5-draft.json → archives`.

| Batch khởi đầu | Số record | Trạng thái |
|---|---:|---|
| SCB Head | 10 | review_only, split=null |
| SCB HRW | 13 | review_only, split=null |
| Roboflow v1 | 5 | review_only, split=null |
| Tổng | 28 | training_eligible=false |

Đây là toàn bộ hàng đợi tồn đọng v4, **0 candidate media mới ngoài ledger**. Đã kiểm hash ảnh/label trực tiếp trong ZIP và hash crop local cho 28/28 record; giữ nguyên target values/masks và bằng chứng review cũ. Không giải nén/sửa raw, không mở ảnh test. Exact image overlap với 84 record đang dùng là 0; chưa kết luận về near-duplicate hoặc độc lập cảnh.

Batch chưa tăng coverage so với ledger cũ và chưa giải source confounding. Bước khai thác tiếp theo là shortlist SCB HRW/Head ngoài ledger từ archive đã pin, giữ proposal riêng và kiểm liên hệ với toàn v4 trước group review. Không lấy source label thành target, không tuyển theo lỗi test. Batch khởi đầu không định nghĩa quota cho shortlist này.

## Luồng Classroom-monitoring-dataset

[Metadata evidence](classroom-monitoring-metadata-review.json) phân biệt claim trên trang và dữ liệu chưa xác minh. [Trang project](https://universe.roboflow.com/arijit-mukherjee-h4br2/classroom-monitoring-dataset) công bố 150 ảnh, 2 phiên bản, 7 lớp và CC BY 4.0; chưa đăng mô tả nguồn. Công cụ web không đọc được hai URL version đã thử nên chưa pin archive/version. Kết quả có thể qua cache của công cụ.

Tên `using_phone`/`turn_around` chỉ gợi ý phù hợp; chưa chứng minh annotation person-level hoặc nhãn đúng guideline. [Project khác cùng publisher](https://universe.roboflow.com/arijit-mukherjee-h4br2/classroom-behaviour-dataset) công bố 50 ảnh với cùng bộ tên lớp: cần kiểm overlap nếu sau này có archive, chưa kết luận có trùng.

[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) có nghĩa vụ ghi công/ghi thay đổi và không bảo đảm các quyền riêng tư khác. [Điều khoản Roboflow, mục 5](https://roboflow.com/terms) có điều kiện riêng về re-host. Hiện chưa có bằng chứng quyền gốc/consent, session/camera/group, completeness hoặc split; giữ nguồn ở metadata review, chưa nhận vào v5. Không tải media, không gửi liên hệ bên ngoài.

## TBD và điều kiện tiếp tục

| ID | Owner | Điều kiện chốt |
|---|---|---|
| TBD-CM-VERSION / RIGHTS | Chủ repository; Codex tổng hợp bằng chứng | Metadata phiên bản, provenance và phạm vi quyền cụ thể trước nhận archive nguồn mới |
| TBD-CM-UNIT / GROUP | Chủ repository; Codex audit/đề xuất | Sau quyền/version: review unit/crop/target, completeness, overlap và nhóm cảnh |
| TBD-V5-MEMBERSHIP | Chủ repository | Nghiệm thu batch và shortlist ảnh mới; 28 record hiện chỉ là ứng viên |
| TBD-V5-GROUP-SPLIT | Chủ repository | Bằng chứng nhóm, near-duplicate và cách ly liên hệ test v4; protocol đánh giá mới |
| TBD-V5-RELEASE | Chủ repository | Crop/nhãn/quyền/group/split và package validation đạt, ký release riêng |

Không cần duyệt lại hướng hai luồng hoặc semantics. Bằng chứng thẩm định còn thiếu được tổng hợp tại đây để owner nghiệm thu ở mức báo cáo; không yêu cầu vẽ/gán nhãn thủ công từng ảnh. V4/test/E001 bất biến, chưa train E002.

## Kiểm chứng

Kết quả cuối lưu tại [verification.json](verification.json). Inventory/queue gốc giữ nguyên để đối chiếu; `source-research.json` là snapshot sàng lọc trước approval, trạng thái mới của nguồn ưu tiên nằm trong metadata evidence ở trên.
