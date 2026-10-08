# Gói nghiệm thu crop, nhãn, nhóm và membership v6

Trạng thái: **đã dựng gói review; chờ owner nghiệm thu nội dung cụ thể**. Phương án nguồn, quyền sử dụng và mở rộng train/val đã được owner duyệt. Release hiện hành vẫn là v5; chưa train, chưa test inference, chưa upload.

## Phương án cụ thể

| Thành phần | V5 | V6 đề xuất |
|---|---:|---:|
| Train | 80 | **193** |
| Validation | 13 | **31** |
| Test | 11 | **11, bảo toàn** |
| Tổng membership | 104 | **235** |
| Review-only | 93 | 89 |
| Excluded | 11 | 27 |
| Tổng ledger | 208 | 351 |

143 candidate mới đã xem ảnh nguồn và crop; 12 crop được dựng lại, vòng sau sửa attribution CA031 (người được crop nhìn xuống bài, không phải người cạnh bên). Chọn 79 crop mới; 48 còn review-only và 16 đề xuất excluded. Bổ sung 52 mẫu parent đã được duyệt nhãn/crop (44 SCB + 8 RF) sau review nhóm. Không import nguyên annotation, không đổi nhãn/crop v5.

## Mở để nghiệm thu

- [Trang ảnh nguồn–crop và từng quyết định](../../../data/interim/pilot-b/v6-release-review-20261007-r3/review.html): mở local trong trình duyệt. Media chỉ ở máy này; trang không gọi dịch vụ ngoài. Không hiển thị lại train/val/test v5.
- [Assignment 351 dòng](proposed-assignment.jsonl): tất cả trạng thái là draft, `training_eligible=false`; trường `proposed_usage` mô tả release sau nghiệm thu.
- [Quyết định và 32 quan hệ nhóm](release-review-decisions-r2.json): gồm 11 quan hệ lịch sử đã được owner duyệt, các liên hệ mới và lý do split. Đây là bản dùng cho gói cuối; file không hậu tố/r2 package là revision trước, không dùng release.
- [Config proposal](../../../configs/datasets/pilot_b_v6_release_proposal_20261007.yaml), [thống kê](summary.json), [bảo toàn test/val](evaluation-preservation.json), [verification](verification.json).
- [Quyền và attribution](rights-attribution.json); [approval nguồn](owner-scope-approval.json), [phạm vi split](split-scope-approval.json). Không hỏi lại các quyền đã chốt.

## Nhãn và split

| Split | Phone P/N/U | Looking P/N/U | Đồng xuất hiện P/P |
|---|---|---|---:|
| Train | 49 / 61 / 83 | 66 / 80 / 47 | 6 |
| Validation | 11 / 14 / 6 | 8 / 10 / 13 | 1 |
| Test v5 | 2 / 2 / 7 | 2 / 7 / 2 | 0 |

Giữ nguyên formulation B và unknown masking. Cụm Student giảng đường được đưa trọn vào train để bổ sung phone trong lớp; cụm Classroom video áo tím/xanh giữ trọn trong validation. Các cảnh SCB/stock khác bổ sung validation theo nhóm, không cắt ngẫu nhiên frame của một cảnh. 13 val v5 còn nguyên trong validation31 để làm subset lịch sử khi có thí nghiệm riêng. Không so trực tiếp metric validation31 với E002 validation13.

Các trường hợp gần cảnh RF validation được cách ly khỏi bổ sung membership. Cùng ảnh đổi kích thước/cùng crop ưu tiên bản parent; các frame lặp giảm đại diện. `proposed_group_id` là thành phần thị giác bảo thủ dùng chống leakage, **không phải xác minh danh tính/phòng/phiên**. 79 nhóm train/13 nhóm val/3 nhóm test là số thành phần của proposal, không được báo là số session độc lập. Toàn bộ video/session/subject metadata chưa biết vẫn không suy đoán.

## Giới hạn chất lượng

193 train vẫn là pilot nhỏ. Có ảnh stock, cảnh diễn, augmentation nguồn và nhiều unknown; chưa phải bộ phòng thi thực tế đại diện. Student phone train mới vẫn ít phone-negative cùng camera; không coi việc cân P/N toàn tập là đã hết học lệch nguồn. Validation31 và test11 còn nhỏ, test phone chỉ có 4 nhãn biết. Không hứa model cải thiện bao nhiêu. FPI và SCB Discuss tiếp tục ngoài đợt chính theo phương án owner đã duyệt. Runtime person/context crop và real-world holdout vẫn là các gate riêng.

## Phạm vi nghiệm thu còn lại

Owner chỉ cần chốt một lần ở mức gói: crop/nhãn mới, các nhóm cảnh, 52 promotion parent, membership193/31/11 và schema/config proposal. Căn cứ: [AGENTS.md](../../../AGENTS.md) yêu cầu “Mọi dataset mutation phải tạo version/pointer mới và có owner review được ghi lại”; [phương án đã duyệt](../../../docs/data/pilot-b-v6-source-proposal-20261007.md) ghi “Owner nghiệm thu gói review tổng hợp”. Phương án nguồn được duyệt trước khi có 143 crop này, nên không dùng nó làm bằng chứng owner đã xem nhãn/membership mới.

Sau nghiệm thu: ghi đúng lời owner và pin các artifact trên; tạo canonical ledger/release v6 với builder hiện hành, kiểm schema/coverage/leakage/checksum và pointer. Không thay raw/v5 và không tự chạy training. Gói review đã có đủ ảnh và từng quyết định để bước này không phụ thuộc owner annotate thủ công.

## Tái dựng và bằng chứng kỹ thuật

```powershell
.venv/Scripts/python.exe -X utf8 -m ai_exam_monitoring.data.pilot_release_review --decisions artifacts/reports/pilot-b-v6-preparation-20261007/release-review-decisions-r2.json --output data/interim/pilot-b/v6-release-review-20261007-NEW
```

Output phải mới; không ghi đè revision đã tồn tại. Candidate selection dùng largest matching anchor trong mỗi ảnh + farthest-first dHash để đa dạng hàng đợi, một đại diện mỗi lineage; class nguồn chỉ là gợi ý. `selection_reason` kế thừa trong snapshot r1/r4 ghi round-robin không mô tả đúng thuật toán selector mới; provenance authoritative là code `pilot_source_candidates.build_candidates`, config preparation và receipts, không sử dụng chuỗi này để quyết định nhãn/split. Hạn chế mô tả này được ghi rõ để không sửa snapshot đã pin. Code đã sửa trường mô tả cho những lần tạo candidate mới; membership/nhãn/crop gói cuối không phụ thuộc chuỗi này.

Các lần build dở/r2/r3 crop và review r1/r2 trước đó được giữ lại làm lịch sử, không phải pointer chính. Gói cuối duy nhất của báo cáo này là `v6-release-review-20261007-r3`, candidate crop từ `v6-preparation-20261007-r4`.

Kiểm tra cuối: 152 tests PASS; Ruff/Mypy phạm vi mới PASS; repository checker failures=0; `git diff --check` PASS. Verification độc lập đã recompute assignment, kiểm340 file crop,730 tham chiếu HTML local và mọi checksum gói; không có xung đột split theo image/crop/group đã khai báo. Đây là QA preparation, không phải acceptance release hoặc benchmark model.
