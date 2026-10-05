# Pilot B — phương án nghiệm thu cuối preparation

Ngày 2026-10-05. **Draft, chưa được owner duyệt.** Canonical vẫn là `pilot-b-20261005-v3`: 112 crop đã duyệt, tất cả `review_only`, `split=null`. Báo cáo này không thay 84 crop/looking SCB hoặc 28 crop/target Roboflow đã duyệt.

Đề xuất dùng **84 crop trong 16 nhóm**, giữ **28 crop thiếu bằng chứng nhóm ở review_only**. Ledger vẫn đủ 112; không bổ sung mẫu, không ép các ảnh chưa rõ thành nhóm độc lập. Chỉ cần nghiệm thu phương án này hoặc nêu ngoại lệ bằng ID; không có HTML, vẽ crop hoặc xuất JSON thủ công.

## Nhãn mới được đề xuất

Codex đã xem 88 crop phone-unknown và 105 ảnh nguồn tại máy local. Đề xuất **9 phone negative + confirmed_working** trên đúng crop SHA; cả 9 đã có looking negative được owner duyệt, nên nếu chấp nhận sẽ có 9 confirmed normal. Đây là quan sát tay/bút/sách/bàn trong crop, không phải suy negative từ class read/write. 79 phone-unknown còn lại giữ nguyên.

[Ảnh tổng hợp 9 crop](../../../data/interim/pilot-b/pilot-b-release-proposal-20261005-v2/phone-negative-proposals.png). [Config có từng crop SHA và observation](../../../configs/datasets/pilot_b_release_proposal_v1.yaml).

| ID | Bằng chứng được dùng | Usage dự kiến |
|---|---|---|
| SCB-read-015 | Tay/bút/giấy của target trên bàn; vật tối do người khác cầm không gán cho target | train |
| SCB-read-024 | Đọc sách giấy mở, tay làm việc với sách/trang | test |
| SCB-write-001 | Một tay cầm bút, tay kia giữ giấy; túi bút ở cạnh dưới | train |
| SCB-write-002 | Hai tay trên giấy/bút; vật đen có khóa kéo là hộp bút | val |
| SCB-write-006 | Tay viết và tay giữ trang vở; hộp hồng bên cạnh không là bằng chứng phone | review_only |
| SCB-write-009 | Tay viết/giữ sách bài tập mở trên bàn xanh tím | train |
| SCB-write-013 | Bút trên giấy, tay còn lại trên trang | train |
| SCB-write-014 | Bút/giấy và hai tay nhìn thấy; giữ chung cảnh với write-001 | train |
| SCB-write-026 | Tay bút và tay giữ trang; không dùng người phía trước làm evidence | test |

Tổng nếu duyệt: phone **24P/9N/79U**; looking giữ **33P/56N/23U**; 10 fully labeled, 102 partially labeled, 1 co-occurrence. Normal chỉ derive khi cả hai target negative và context confirmed_working. Unknown vẫn mask khỏi loss/metric.

## Nhóm chống leakage

Giữ mọi must-link của 14 nhóm đã duyệt, không yêu cầu duyệt lại các quyết định đó. Đề xuất thay đổi hữu hạn:

| Đề xuất | Membership bổ sung/gộp | Bằng chứng thị giác |
|---|---|---|
| RF-GREEN | Thêm P022-person-01 vào nhóm ghế xanh RF | Ghế xanh lưng tròn xếp tầng, bàn gỗ/tường kem; góc khác nhưng cùng kiểu bố cục |
| SCB-BLUE-CONSERVATIVE | Gộp BLUE-POSTER + DARK-SIDE-VIEW + CURTAIN-LANDSCAPE; thêm turnhead-027 | Bàn xanh tím/vàng, tranh phong cảnh, rèm/cửa/màn hình; gộp rộng để tránh chia các góc nghi liên quan |
| SCB-BLUE-WOOD | read-001, read-004, write-025 | Đồng phục xanh/trắng, bàn trắng/xanh, chân tường gỗ và panel kem |
| SCB-GREY-YELLOW | read-018, write-026 | Đồng phục sọc xám/trắng, bàn vàng, giáo viên áo đỏ/rèm xanh |
| SCB-RED-WHITE-STRIP | read-015, turnhead-013, write-013, write-017, write-023 | Đồng phục trắng/đỏ, bàn vàng, tường sọc sáng/cửa sổ; cụm bảo thủ |
| SCB-MIRROR-STRIP | read-027, write-018 | Đồng phục trắng/xanh đậm, bàn vàng nhạt, tường gương phía sau |

Các ID SCB rút gọn trong bảng đều có prefix `SCB-`. Membership đầy đủ và evidence của 16 nhóm nằm trong config; [assignment từng mẫu](../../../data/interim/pilot-b/pilot-b-release-proposal-20261005-v2/proposed-assignment.jsonl). Source sheets đã dùng cho QA: [01](../../../outputs/pilot-b-group-review-20261005-v3/sheet-01.jpg), [02](../../../outputs/pilot-b-group-review-20261005-v3/sheet-02.jpg), [03](../../../outputs/pilot-b-group-review-20261005-v3/sheet-03.jpg), [04](../../../outputs/pilot-b-group-review-20261005-v3/sheet-04.jpg), [05](../../../outputs/pilot-b-group-review-20261005-v3/sheet-05.jpg), [06](../../../outputs/pilot-b-group-review-20261005-v3/sheet-06.jpg), [07](../../../outputs/pilot-b-group-review-20261005-v3/sheet-07.jpg), [08](../../../outputs/pilot-b-group-review-20261005-v3/sheet-08.jpg), [09](../../../outputs/pilot-b-group-review-20261005-v3/sheet-09.jpg).

Đây là **cluster chống leakage theo evidence thị giác**, không phải metadata session/room/person đã tìm lại. Những trường đó giữ null. Ranh giới giữa các nhóm đi qua split cần owner nghiệm thu cho phạm vi pilot nghiên cứu; chưa có xác nhận độc lập thực tế. 28 record không đủ evidence giữ review_only, kể cả write-006 có phone negative được đề xuất. Danh sách đầy đủ ở summary, không loại mất khỏi ledger.

## Split/config được đề xuất

Assignment tường minh theo toàn nhóm, không random theo crop, không dùng filename để suy session. Seed **null** vì không có RNG; 70/15/15 là mục tiêu mềm, actual **71.43% / 15.48% / 13.10%** trên 84 crop dự kiến sử dụng.

| Usage | Crop | Phone P/N/U | Looking P/N/U | Normal dự kiến |
|---|---:|---|---|---:|
| train | 60 | 11/5/44 | 17/33/10 | 5 |
| val | 13 | 7/1/5 | 3/3/7 | 1 |
| test | 11 | 2/2/7 | 2/7/2 | 2 |
| review_only | 28 | 4/1/23 | 11/13/4 | 1 |

Val: RF-GREEN + SCB-GREEN-TABLES. Test: RF-WINDOW + SCB-GREY-WINDOWS + SCB-GREY-YELLOW. Các nhóm còn lại train. RF cùng ảnh/cảnh và mọi crop thuộc cùng group ở cùng usage; exact image/crop SHA không đi qua group/split. Report có counts theo source/split/group.

Giữ schema `pilot-b-manifest-v1`, encoding `pilot-b-targets-v1`, crop policy `pilot-b-reviewed-context-v1`, masked supervision. Không đổi crop bytes/tọa độ hoặc known target cũ. Test **chưa freeze**: QA hiện tại là trước freeze; sau nghiệm thu và build version mới sẽ pin assignment/config/manifest/checksums và decision evidence, không dùng test để chọn model/epoch/augmentation/threshold.

Scope đề xuất: **local_classifier_research** — train/val/evaluation classifier offline tại máy local, giữ attribution và ghi nhận dẫn xuất. Không cho phép redistribute, upload/log media ra ngoài hoặc quyết định kỷ luật. SCB rights đã duyệt không mở lại; RF vẫn giữ license declaration/citation, không coi đó là metadata consent từng ảnh. Baseline B end-to-end còn gate runtime crop S9 riêng.

Phone positives ở RF, phone negatives ở SCB tạo source confounding. Val chỉ có 1 phone negative; test chỉ có 4 phone labels known. Có support hai chiều để thử pipeline, nhưng không đủ chứng minh generalization, promotion model hoặc real-world exam holdout. Không có model metrics trong báo cáo này.

## Kiểm tra và quyết định cần chốt

[Summary](summary.json), [verification](verification.json). 105 unit tests, Ruff, compileall, repository checker và diff check PASS; rebuild proposal identical; canonical v3/payload/RF/crop/known labels giữ nguyên. Không train/upload/commit thêm trong lượt này.

Owner có thể trả lời **“approve phương án release pilot B”** để nghiệm thu cùng lúc 9 phone/context proposals, các cụm/ranh giới nhóm thị giác, assignment/config, scope local và cho phép build version canonical mới với test freeze theo assignment đã pin. Hoặc nêu ID/nhóm cần sửa; Codex tự xử lý version mới. Approval này không đồng nghĩa baseline/model đạt chất lượng. Không cần duyệt lại 84 crop/looking hoặc 14 must-links.

Việc cần owner chốt xuất phát từ [AGENTS.md](../../../AGENTS.md), mục “Không được tự quyết âm thầm” về label/split/scope, và [contract](../../../docs/data/pilot-b-release-contract-v1.md), §6–7 về group evidence, test freeze và release acceptance. Hiện chỉ trình đề xuất; chưa tự ký release.

Tái tạo vào destination mới/rỗng:

```powershell
.venv/Scripts/python.exe -m ai_exam_monitoring.data.pilot_release_proposals --config configs/datasets/pilot_b_release_proposal_v1.yaml --output-dir outputs/pilot-b-release-proposal-rebuild-new
```
