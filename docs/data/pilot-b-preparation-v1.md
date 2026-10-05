# Pilot B — Preparation và release runbook

Ngày 2026-10-05. Owner: chủ repository (solo). [Contract](pilot-b-release-contract-v1.md), [ADR-013](../decisions/ADR-013-pilot-b-packaging-contract.md). Task đóng gói reviewed crops local đã hoàn tất; không train trong preparation.

## Pointer hiện hành

**Canonical `data/processed/pilot-b/pilot-b-20261005-v4/`, status `accepted`, scope `local_classifier_research`.** Config `configs/datasets/pilot_b_release_v4.yaml`; [báo cáo release](../../artifacts/reports/pilot-b-release-acceptance-20261005/README.md), [approval](../../artifacts/reports/pilot-b-release-acceptance-20261005/owner-approval.json), [verification](../../artifacts/reports/pilot-b-release-acceptance-20261005/verification.json).

112 ledger/crop evidence, 84 usage manifest trong 16 nhóm: **60 train / 13 val / 11 test**. 28 record thiếu evidence nhóm giữ review_only/split=null. Test đã freeze. Toàn ledger phone 24P/9N/79U, looking 33P/56N/23U, 9 normal, 1 co-occurrence, 10 fully/102 partially labeled. Used84 phone 20P/8N/56U, looking 22P/43N/19U, 8 normal.

Owner đã approve nguyên phương án release, không có ngoại lệ: 9 phone negative/context working, conservative groups/boundaries, split/config/schema và local use. 84 SCB crop/looking và28 RF approvals cũ không mở lại; source/crop/known target bytes/evidence được giữ nguyên. Không map source class toàn nguồn, không refill.

## Dùng dataset

Dùng `pilot_schema.read_records` trên **manifest.jsonl**, lọc usage train/val/test. Thứ tự target `[phone_use, looking_around]`; unknown=null/mask=0, chỉ target known tham gia loss/metric. Normal derive từ hai negative +confirmed_working; không là output thứ ba. Không quét toàn `crops/` hoặc train từ full review-ledger: còn28 crop review-only trong package làm evidence.

`reports/coverage.json` có counts/support theo source/split/group; `reports/leakage.json` ghi exact clusters và28 group-unresolved. `release.json#test_freeze` pin manifest/split/test-subset/config/Git,11 test IDs,owner decision/time/protocol. Seed=null, whole-group assignment tường minh;70/15/15 là mục tiêu mềm, actual71.43/15.48/13.10% trên84 used. Sau freeze không dùng test để chọn model/epoch/augmentation/threshold.

Phone positives ở RF/negatives ở SCB gây confounding; val chỉ1 phone negative, test chỉ4 phone labels known. Không có model metrics, real-exam generalization hoặc real-world holdout. Scope train/val/evaluate classifier offline local; giữ attribution/dẫn xuất, không redistribute/upload/log media ra ngoài hoặc dùng cho kỷ luật. Training model/loss/resize/augmentation/experiment là task riêng.

## Khôi phục package và dựng lại từ nguồn

Package v4 là immutable; khôi phục đúng bytes từ checkout đã bàn giao bằng `dvc pull data/processed/pilot-b/pilot-b-20261005-v4.dvc -r teamdrive`, rồi kiểm `checksums.sha256` bằng `pilot_owner_groups.verify_payload` và `pilot_schema.read_records`. Training consumer chỉ cần package v4; không cần kéo raw hoặc toàn bộ lịch sử preparation.

Từ repository root, destination mới/rỗng; parent packages, config chain và extracted sources đã pin phải còn nguyên:

```powershell
.venv/Scripts/python.exe -m ai_exam_monitoring.data.pilot_release_proposals --config configs/datasets/pilot_b_release_v4.yaml --accept-release --output-dir outputs/pilot-b-release-rebuild-new
```

Lần rebuild nghiệm thu ban đầu, cùng inputs/provenance/environment, mọi payload SHA identical. Payload checksum list v4 `dbc1bf90a5605cac39b5c96503e71097ecd1eaab5b35e14f311f966edd503f53`. CLI dựng lại ghi Git/environment tại thời điểm chạy: đổi commit/environment có thể đổi `release.json` và checksum package, dù manifest/split/crop không đổi. Không dùng output mới để overwrite v4 hoặc tự freeze lại test. Khôi phục artifact đã ký qua DVC và replay producer từ nguồn là hai phép kiểm khác nhau; source replay cần parent packages, config chain và extracted sources đã pin.

## Lineage và code còn dùng

- Frozen selection `data/interim/pilot-b/pilot-b-20261004-v1`: exact84 anchors28 TurnHead/read/write, không transfer/refill.
- V2 `data/processed/pilot-b/pilot-b-20261005-v2`: nhập14 must-links; [group evidence](../../artifacts/reports/pilot-b-owner-groups-20261005-v1/owner-review.json).
- V3 `data/processed/pilot-b/pilot-b-20261005-v3`: nhập84 SCB crop/looking approvals; [batch evidence](../../artifacts/reports/pilot-b-scb-acceptance-20261005/owner-approval.json). Lịch sử v3 phone 24P/0N/88U, chưa split; giữ immutable.
- [Đề xuất release gốc](../../artifacts/reports/pilot-b-release-proposal-20261005/README.md), `data/interim/pilot-b/pilot-b-release-proposal-20261005-v2`, config `pilot_b_release_proposal_v1.yaml`: giữ nguyên Draft trong snapshot lịch sử; owner acceptance nằm trong v4 evidence, không sửa file đã pin.
- V4 hiện hành nhập9 phone/context reviews và84 assignments từ đúng đề xuất đã duyệt. Cụm được owner chấp nhận theo evidence thị giác cho pilot local; session/room/video/subject metadata vẫn null, không suy độc lập từ filename/hash.

`pilot_schema`/`pilot_package` là codec/validator/exporter. `pilot_inputs`/`pilot_selection` pin/select; `pilot_prepare` tạo ledger; `pilot_owner_groups` nhập must-links; `pilot_scb_proposals` tạo/import batch; `pilot_release_proposals --accept-release` nhập release approval vàfreeze. Dùng module hiện có, không thêm module src/frontend/dependency/model trong bước release. HTML/Canvas đã bỏ; deck nhóm owner đã dùng giữ làm evidence lịch sử, không là bước thao tác bắt buộc.

## Scope lưu trữ Drive và bàn giao

Owner yêu cầu rõ ngày 2026-10-05: “Hoàn tất bàn giao qua Drive: chốt scope upload v4, rồi push/pull đúng version từ checkout/cache sạch.” Quyết định này bổ sung quyền **lưu và khôi phục đúng package v4 bằng DVC trên remote `teamdrive` hiện có, do owner kiểm soát**, phục vụ nghiên cứu classifier đã duyệt. Drive ACL được kiểm qua API trước upload: chỉ một user/owner, không public/domain/group. Không đổi sharing; không cấp quyền bên thứ ba, không redistribute, không upload raw/parent packages/media lên W&B. Owner quản lý quyền truy cập và việc xóa bản lưu khi không còn sử dụng; không tự đặt thời hạn retention cho thu thập phòng thi thật.

Quyền lưu trữ được ghi ngoài payload v4 tại runbook/WORKLOG; `release.json` và approval/report cũ giữ nguyên như snapshot thời điểm nghiệm thu local. Scope train vẫn `local_classifier_research`, không thay label/split/test freeze. Pointer v4 có 124 files, MD5 directory `563958778204fa60d6015656595c19dd.dir`. **S8 storage handoff PASS:** targeted push 125 objects; exact-commit/cache mới rỗng pull 125 objects và restore 124 files. Full inventory/checksums, 14 config/producer/approval pins, schema/usage/split/test freeze PASS.

Commit implementation `97b90ebfe0e8f5457ac5c783205c98be02925866`; commit sửa portability tests và được xác minh cuối `d99d1f5c08be467e05f6c7ee27dba8138bc779a5`. Clone sau dùng cache riêng mới rỗng và không có dataset trước pull; 109 tests, lint, compile, repository checker PASS bằng cloned source. Dùng môi trường Python đã cài ở máy gốc, chưa phải fresh dependency installation hoặc remote Linux CI. Pointer trong Git SHA-256 `f9f249f1f7bee62690e24f8bb437952c855866c9f7828da5af195d8c770564ef`; payload list SHA giữ nguyên ở trên. Clone/cache thử đã dọn; WORKLOG lưu bằng chứng, không cần tạo lại smoke fixture.

## Gate trước phase tiếp theo

S1–S8 hoàn tất cho release pilot và storage scope bổ sung trên. S9 automatic runtime crop cần owner policy/QA riêng trước baseline B end-to-end; không chặn chuẩn bị experiment classifier trên reviewed crops. Model/weights/license/loss/config và trainer/evaluator B là task tiếp theo; không train trong task bàn giao.

Release gốc ghi design/base commit `1f7757bfee5a20dad393ba80064769851e5ccd6a`, dirty=true và implementation SHA đúng lúc tạo. Commit bàn giao chứa implementation/config/evidence/pointer và cleanup, được ghi trong WORKLOG; không sửa provenance cũ để giả release được build ở commit mới. Không tự tuyên bố toàn P0/P1/P2 đã đạt mọi gate.
