# V6 mở rộng R2 — xét lại review_only và bổ sung crop

**Đề xuất mới: 317 train / 50 val / 11 test.** Gói này thay phương án 193/31/11 để owner nghiệm thu; chưa phải release accepted và chưa dùng để train. V5 và gói review trước được giữ nguyên.

- [Mở ảnh nguồn + crop + nhãn + nhóm + split](../../../data/interim/pilot-b/v6-release-review-expanded-20261007-r5/review.html).
- [Config proposal mới](../../../configs/datasets/pilot_b_v6_release_proposal_r2_20261007.yaml).
- [Quyết định xét lại toàn bộ 89 review_only](reconsideration.json), [assignment cuối](proposed-assignment.jsonl), [kiểm chứng](verification.json).

## Thay đổi thực tế

| Phần | Phương án trước | R2 |
|---|---:|---:|
| Train | 193 | 317 |
| Validation | 31 | 50 |
| Test v5 | 11 | 11 |
| Tổng dùng dự kiến | 235 | 378 |
| Review_only | 89 | 93 |
| Excluded | 27 | 27 |
| Ledger gồm mọi trạng thái | 351 | 498 |

R2 chuyển **46/89 review_only cũ** sang dùng: 33 train, 13 val; giữ lại 43. Đồng thời xem thêm **147 crop**, nhận 97 (91 train, 6 val), giữ 50 review_only. Vì vậy tổng review_only là 93 và thành phần đã đổi. Tổng tăng 143 mẫu dùng, không phải nhận hết 147 crop mới.

Trong 147 crop bổ sung: 93 crop lấy thêm người khác trong ảnh Student đã có (nhận 62); 54 crop từ ảnh ngoài SHA/export lineage đã chọn trước (nhận 35). 54 ảnh này **không đồng nghĩa 54 cảnh độc lập**; nhiều ảnh vẫn chung camera, người hoặc video. Đã kiểm ảnh nguồn/crop của toàn bộ hàng đợi, dựng lại và xem lại 5 crop thiếu ngữ cảnh người.

## Những mẫu owner chỉ ra

P = positive, N = negative, U = unknown. Nhãn dưới đây vẫn là đề xuất cho revision, không phải model prediction.

| ID | Phone | Looking | Đề xuất | Lý do chính |
|---|---|---|---|---|
| EXP-CM-008 | P | U | train | Điện thoại giữa hai bàn tay; không suy looking từ cúi đầu |
| EXP-CM-016 | U | N | train | Hướng xuống vùng tài liệu; tay dưới bàn bị che |
| EXP-CM-022 | P | U | train | Điện thoại cầm trước người |
| EXP-RF-003 | N | P | train | Giữ nhãn đã biết, bỏ cách giữ lại quá thận trọng |
| EXP-RF-004 | U | P | train | Một target rõ đủ để dùng masked supervision |
| EXP-RF-007 | U | P | val | Cùng nhóm RF-GREEN đã thuộc validation |
| EXP-RF-008 | U | P | val | Nhìn về người/bài bên cạnh; gom họ ghế màu về val |

EXP-CM-016 là mẫu cần chú ý khi nghiệm thu: đề xuất looking N dựa vùng tài liệu/hướng đầu trong ảnh, không khẳng định không có điện thoại hoặc normal. Crop mờ có thể gây bất đồng; owner có thể giữ U nếu không đồng ý bằng chứng. Toàn bộ 16 đề xuất điền nhãn unknown của parent được ghi trong [evaluation-preservation.json](evaluation-preservation.json); không sửa file v5, không thay nhãn parent đã biết.

## Vì sao phương án này có giá trị hơn

Phương án trước giữ lại một số mẫu quá thận trọng dù đã biết một target, hoặc vì cảnh liên quan val. R2 dùng một target rõ với mask cho target còn lại; cảnh liên quan val chỉ bổ sung vào val. Không đòi phải biết cả hai target mới được dùng.

Thêm người khác trong cùng camera tạo đối chứng cầm bút, đọc sách, dùng chuột/laptop, chống cằm và điện thoại. Đây là dữ liệu có thể giúp model bớt phụ thuộc phông nền. Tư thế khác biệt được giữ; các frame gần lặp, crop thiếu tay/mặt hoặc quá mờ vẫn ở review_only. Số phone positive/negative trong train tăng từ 49/61 lên **93/91**; looking positive/negative tăng từ 66/80 lên **117/112**. Unknown vẫn bị mask, không biến thành negative.

Vẫn còn giới hạn: dữ liệu ít cảnh độc lập, nhiều ảnh diễn xuất/stock, mất cân bằng theo nguồn và ảnh tĩnh. 103/14/3 nhóm train/val/test là nhóm kiểm soát leakage dự kiến, không phải số session độc lập đã chứng minh. Chưa có real-world holdout và chưa đo mức cải thiện model; chưa thể hứa tăng accuracy bao nhiêu. Validation 50 mẫu không so trực tiếp với metric E002 trên 13 mẫu; subset 13 cũ được bảo toàn để báo cáo riêng.

## QA và trạng thái nghiệm thu

- 498 assignment tái dựng khớp; 290 candidate kiểm lại pixels từ ảnh nguồn và tọa độ; 487 crop payload kiểm checksum; 1.171 tham chiếu HTML tồn tại.
- 104 membership v5, nhãn/crop/source/group được giữ nguyên; gồm 80 train, 13 val, 11 test. Tất cả crop/source của parent và checksum gói trước không đổi.
- Không xung đột image/crop/group qua split; không có crop SHA trùng trong tập dùng. Nearest dHash được dùng để triage, đã xem ảnh nguồn đối chiếu; không thay thế kiểm thị giác hoặc bảo đảm hết near-duplicate.
- 156 unittest PASS; Ruff/Mypy phạm vi sửa PASS. Không chạy model, test inference hoặc upload media.
- Quyền sử dụng và phạm vi train/val đã được owner xác nhận, không cần duyệt lại. **Chỉ còn nghiệm thu nội dung gói R2 cụ thể** trước khi materialize release v6 theo phương án đã duyệt và quy định repository. Không cần review tay từng dòng nếu owner chấp nhận báo cáo tổng hợp; có thể gửi ID cần sửa.

## Artifact và tái lập

[Decisions](release-review-decisions.json) pin candidate/parent/split approval; [visual MP](visual-review-mp.json), [visual ảnh bổ sung](visual-review-scenes.json), [QA redraw/nearest](redraw-and-neighbor-review.json), [nearest metadata](new-image-neighbors.json), [provenance](provenance.json).

Chạy builder canonical proposal với decisions trên và một `--output` **mới chưa tồn tại** trong `data/interim`:

```powershell
.venv/Scripts/python.exe -m ai_exam_monitoring.data.pilot_release_review --decisions artifacts/reports/pilot-b-v6-expansion-20261007-r2/release-review-decisions.json --output data/interim/pilot-b/v6-review-rebuild-local
```

Các file visual-review ghi lần quan sát ban đầu; target_overrides trong decisions ghi kết luận QA cuối (ví dụ CA-008 phone U). Assignment là kết quả cuối để nghiệm thu. Snapshot expanded-r2/r3/r4 đã được thay bằng expanded-r5 sau QA và chuẩn hóa ghi chú tiếng Việt. MP-003/033/064/088 về review_only vì vật thể chưa chắc là phone. Dùng assignment expanded-r5 để chốt.
