# Pilot B — release local đã nghiệm thu

Ngày 2026-10-05. **Hoàn tất đóng gói classifier reviewed-crop cho scope `local_classifier_research`.** Owner đã trả lời “approve phương án release pilot B”, không có ngoại lệ. [Approval](owner-approval.json) pin đúng báo cáo/config/assignment đã trình; bản đề xuất gốc được giữ nguyên làm lịch sử.

Canonical: **`data/processed/pilot-b/pilot-b-20261005-v4/`**, status `accepted`. [Config](../../../configs/datasets/pilot_b_release_v4.yaml), [dataset card](../../../data/processed/pilot-b/pilot-b-20261005-v4/dataset-card.md), [verification](verification.json).

Ledger giữ đúng RF28 + SCB84,112 crop đã duyệt; nguồn/tọa độ/bytes và mọi looking approval cũ không đổi. Manifest dùng23 RF +61 SCB crops trong16 nhóm có owner evidence;28 record thiếu evidence nhóm giữ review_only/split=null. Chỉ9 phone negative/context working approvals mới được nhập, không map source class toàn nguồn hoặc refill.

| Usage | Crop | Phone P/N/U | Looking P/N/U | Normal |
|---|---:|---|---|---:|
| train | 60 | 11/5/44 | 17/33/10 | 5 |
| val | 13 | 7/1/5 | 3/3/7 | 1 |
| test | 11 | 2/2/7 | 2/7/2 | 2 |
| review_only | 28 | 4/1/23 | 11/13/4 | 1 |
| Toàn ledger | 112 | 24/9/79 | 33/56/23 | 9 |

Có10 fully labeled/102 partially labeled trong ledger;1 co-occurrence. Unknown=null/mask=0, target order `[phone_use, looking_around]`; normal derive từ hai negative +confirmed_working, không thêm head classifier.

## Dùng và tái tạo

Đọc **[manifest.jsonl](../../../data/processed/pilot-b/pilot-b-20261005-v4/manifest.jsonl)** bằng `pilot_schema.read_records`; lọc usage train/val/test và áp dụng mask cho loss/metric. Manifest có84 crop, package còn giữ112 crop làm evidence: không quét toàn `crops/` hoặc dùng toàn review-ledger để train. Model/loss/resize/augmentation/threshold thuộc task training riêng.

[Coverage theo source/split/group](../../../data/processed/pilot-b/pilot-b-20261005-v4/reports/coverage.json), [leakage](../../../data/processed/pilot-b/pilot-b-20261005-v4/reports/leakage.json), [split assignment](../../../data/processed/pilot-b/pilot-b-20261005-v4/split-assignment.jsonl), [release và freeze](../../../data/processed/pilot-b/pilot-b-20261005-v4/release.json).

Tái tạo từ repository root vào destination mới/rỗng; giữ parent/input đã pin và config chain:

```powershell
.venv/Scripts/python.exe -m ai_exam_monitoring.data.pilot_release_proposals --config configs/datasets/pilot_b_release_v4.yaml --accept-release --output-dir outputs/pilot-b-release-rebuild-new
```

Mở rộng module hiện có với `--accept-release`, tái sử dụng exporter/schema; không thêm module src, frontend, model hoặc dependency. Rebuild thực tế ở `outputs/pilot-b-release-rebuild-20261005-v4/` bằng process/destination mới cho toàn payload identical.

## Freeze và kiểm tra

Test **đã freeze** theo `pilot-b-explicit-scene-split-v1`: whole-group assignment tường minh,seed=null;70/15/15 là mục tiêu mềm,actual71.43/15.48/13.10% trên84 used. Evidence thị giác được owner chấp nhận cho pilot local; video/session/room/subject metadata vẫn null, không suy độc lập từ tên/hash unique.

`release.json#test_freeze` lưu11 test IDs,protocol,owner decision/time,config/Git vàhash manifest/split/test subset. Sau freeze không dùng test để chọn model/epoch/augmentation/threshold. Thay đổi label/crop/group/split cần version/review mới; không gọi tập đã dùng để tuning là holdout chưa nhìn.

- Payload checksum list SHA: `dbc1bf90a5605cac39b5c96503e71097ecd1eaab5b35e14f311f966edd503f53`.
- Manifest SHA: `d83115300a15f807bdf35685cc2dbf2e21cd9bc5c9c4d86c0a2d163b951d877b`.
- Split assignment SHA: `8e6bf6f5e16232f69268ac9b6b2410a0571ba6dc3a8a9517be9465ca96ce33d3`.
- Test subset SHA: `b1ae787f1d513118accfe5ae1793693e53924d0d6a6fec14defeacf786a33406`.

PASS 108 unit tests,Ruff,compileall,repo checker,diff/link/UTF-8/media checks. Source/label/crop pixel/hash preflight; exact112 membership/84 selection,9 scoped imports,14 old must-links,16 final groups,zero exact image/crop/group overlap qua split,rights/mask/normal/freeze hashes đã kiểm. Parent v3/RF snapshots giữ nguyên. Verification ghi Git base commit +git_dirty=true +implementation SHA; implementation chưa commit, không giả commit thiết kế chứa code mới.

Phone positives ở RF vànegatives ở SCB gây source confounding. Val chỉ1 phone negative;test chỉ4 phone labels known. Dataset dùng thử classifier pipeline, chưa chứng minh model quality/generalization hoặc real-world holdout; không có model metrics.

## Ranh giới hoàn thành

S1–S7 vàphần ký release/pointer local của S8 hoàn tất cho tập hữu hạn này. Scope chỉ train/val/evaluate classifier offline local, giữ [SCB attribution](../../../docs/data/candidates/SCB5-supplied-20261003.md), [RF attribution/license declaration](../../../docs/data/candidates/Roboflow-phone-use-20261004.md) vàghi nhận dẫn xuất; không redistribute/upload/log media ra ngoài hoặc dùng cho kỷ luật.

DVC chưa cài, chưa có pointer/remote round-trip. S8 remote vàP0/P2 DVC gates vẫn mở vì nằm ngoài scope upload đã duyệt; không install/push để ép đóng gate. S9 crop runtime chưa đạt vàkhông nằm trong task reviewed-crop packaging. Không tuyên bố P0/P1/P2 toàn dự án hoàn tất; không train model/upload media trong task.
