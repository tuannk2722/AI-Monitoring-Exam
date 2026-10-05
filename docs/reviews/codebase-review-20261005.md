# Review codebase và vòng đời artifact — 2026-10-05

Owner: chủ repository. Review/implementation: Codex, không delegation. Base commit `3a103a43f71f6947677d7ba25e1b075117bb9bdf`. Phạm vi: spec → config/code → tests → lineage và dung lượng local. Đây là review kỹ thuật, không nghiệm thu lại nhãn hay đánh giá model.

## Kết luận

Hướng AI-first và formulation B phù hợp các ADR đã Accepted: schema ba trạng thái/mask, crop review, group/split gate và test freeze đã được hiện thực; không có dashboard/mock model thay cho AI core. Điểm cần cải thiện là loại bỏ đường train A, đồng bộ tài liệu hiện hành và quản lý các bản sao evidence. Chưa có trainer/evaluator B, crop runtime được duyệt, model metrics hoặc real-world holdout; không coi tests pass là đạt những milestone đó.

Cây `src/`, `configs/`, `tests/`, `docs/` phù hợp quy mô hiện tại. Không cần thêm tầng framework, frontend hoặc di chuyển hàng loạt module. Các module `pilot_*` là từng bước có trách nhiệm riêng và được dùng trong chuỗi approval; không phải tất cả là script thừa. `outputs/` hiện trộn extracted inputs, evidence và scratch; không được xóa cả cây theo tên gọi.

## Phát hiện và xử lý

| Mức | Bằng chứng / ảnh hưởng | Xử lý |
|---|---|---|
| P1 | Evaluator A chỉ kiểm khóa test khi `use_test=True`, nhưng nhánh mặc định đọc `validation.split`; `split=test` vượt gate. Config B hiện hành đã chặn entrypoint nên không có bằng chứng test v4 từng bị dùng sai. | Gỡ evaluator cùng train A theo owner; không giữ một nhánh train không còn được chọn. |
| P1 | `detect.py` mở output bằng `w`; output trùng source/checkpoint hoặc kết quả trước có thể phá dữ liệu. | Từ chối file đã tồn tại trước load model; mở bằng `x` để bảo vệ cả trường hợp file xuất hiện giữa kiểm tra và ghi. Regression test bảo toàn source bytes. |
| P2 | `detector.py` ghi `video_time_ms=0` cho mọi frame khi thiếu FPS; FPS âm/NaN/Infinity chưa bị chặn. | Owner duyệt yêu cầu FPS hữu hạn, dương. CLI yêu cầu `--fps`; API kiểm trước model prediction. Giữ schema timestamp hiện có. |
| P2 | BoundingBox nhận NaN/Infinity và coordinate_space ngoài enum do annotation Literal không tự validate. | Kiểm finite và enum; regression ở cả bốn tọa độ. |
| P2 | Split helper bỏ lọt NaN vì phép so sánh với NaN đều false; có thể đẩy rows vào test. | Từ chối số không hữu hạn trước assignment. Không sửa seed/ratio hoặc split v4. |
| P2 | Spec 04 cấm `suspicious_person`, nhưng Prediction chỉ cấm ba nhãn khác. | Thêm nhãn thiếu và kiểm cả bốn nhãn cấm. |
| P2 | Checker bắt buộc có train/config legacy thay vì core pilot B; docs/notebook dẫn tới launcher cũ. | Checker chuyển sang schema/exporter/release config/pointer hiện hành; đồng bộ hướng dẫn. |
| P3 | Overview còn ghi team 3 người, doc 04 còn nói schema chưa thiết kế. | Đồng bộ workflow solo và schema pilot đã accepted; không sửa ADR/evidence lịch sử. |
| P2 | Bốn preparation copies lặp gần như toàn bộ media; chỉ release.json khác r5. | Owner duyệt archive metadata rồi dọn; chi tiết bên dưới. |

Train A còn cho phép tái dùng experiment destination (`exist_ok=True`), khởi tạo model ngoài khối xử lý lỗi và không ghi INTERRUPTED cho KeyboardInterrupt. Những đường này được loại bỏ, không mang sang trainer B. Khi triển khai B cần test run identity/status/resume, khóa actual evaluation split và masking bằng fixture riêng.

## Những gì đã gỡ và giữ

Gỡ 8 file: `training/train.py`, `training/__init__.py`, `evaluation/evaluate.py`, `evaluation/__init__.py`, `scripts/benchmark_training.py`, `configs/baseline.yaml`, `params.yaml`, `dvc.yaml`. Gỡ validator training A và hai tests chỉ phục vụ code đã xóa. Caller search cho thấy không có dependency từ pipeline pilot B; cập nhật checker/docs/notebook cùng thay đổi. DVC pointer/remote không cần `dvc.yaml` để pull package.

Giữ audit/overlay/YOLO parsing, converters/build gate, review helpers, schema/package/proposal/importer. YOLO source annotations vẫn cần cho audit và chọn anchor; xóa cả nhóm này sẽ phá preparation. Builder legacy chưa phải builder classifier B. Generic detector còn là adapter, chưa chứng minh crop/classifier end-to-end. Config events/tracking là draft, không tự biến thành runtime accepted.

Không đổi `pilot_*.py`, các config pilot đã pin hoặc report nghiệm thu. Producer SHA lịch sử và payload v4 giữ nguyên. Không tái cấu trúc chúng chỉ vì file dài; có thể tách module khi thêm tính năng thực sự, với provenance/version được kiểm riêng.

## Dung lượng và chính sách giữ

Số liệu logical bytes ở workspace; không tính `.venv`, `.git`, DVC cache hoặc archive nguồn nằm ngoài repo. MiB = 2^20 bytes.

| Phần | Trước cleanup | Vai trò / quyết định |
|---|---:|---|
| `data/raw` | 1 placeholder | Không chứa ZIP gốc; không xóa hoặc chuyển nguồn vào đây âm thầm. |
| `data/interim` | 134 files, 11,74 MiB | Frozen selection và proposals; giữ vì approval/config tham chiếu. |
| `data/processed` | 1.155 files, 469,10 MiB | Sau dọn còn 551 files, khoảng 163 MiB; giữ r5/v2/v3/v4. |
| `.../pilot-b-20261005-v4` | 124 files, 5,12 MiB | Package training consumer duy nhất; 112 ledger/crops nhưng chỉ 84 manifest dùng train/val/test. |
| `outputs/scb-audit-20261003-v1` | 20.382 files, 1.214,51 MiB | Có extracted source dùng bởi config đã pin, không phải cache tùy ý. |
| `outputs/roboflow-v1-20261004` | 6.901 files, 103,26 MiB | Có extracted RF source; giữ cho producer replay. |
| `artifacts/reports` | 21 files, 0,82 MiB | Evidence nhỏ trong Git; giữ. |
| Các outputs review khác | Nhiều batch/sheets | Giữ evidence owner, inputs đã pin và lịch sử; tên v1/v2 không đủ chứng minh trùng. |

Riêng r5: `reports/` có 116 files khoảng 74,27 MiB; `crops/` 28 files chỉ 1,90 MiB. Vì vậy nhiều dung lượng đến từ ảnh review bị sao chép giữa revisions, không phải dataset classifier cuối quá lớn.

### Cleanup owner đã duyệt

Owner trả lời: **“Duyệt: lưu metadata rồi dọn 4 bản trùng”**. Đã xóa đúng bốn cây dưới `data/processed/pilot-b/`:

- `pilot-b-20261004-v1`
- `pilot-b-20261004-v1-preparation-r2`
- `pilot-b-20261004-v1-preparation-r3`
- `pilot-b-20261004-v1-preparation-r4`

Tổng 604 files, 320.971.311 bytes. Trước xóa đã verify full payload của cả bốn bản và r5; inventory/hashes chỉ khác `release.json` và checksum list tương ứng. Archive local [pilot-b-preparation-history-20261005.zip](../../outputs/pilot-b-preparation-history-20261005.zip) lưu nguyên byte hai file này cho mỗi version, inventory và hướng dẫn RESTORE; 42.579 bytes, SHA-256 `af71803ebc46ea89f3f38f5925246f748ea373f8128a208526e9117ce147969c`. Archive là snapshot chuẩn bị trước approval; quyết định thực thi được ghi tại đây/WORKLOG, không rewrite archive.

Đã kiểm CRC archive và mô phỏng khôi phục bằng bytes trong archive + r5 cho từng payload SHA. **Archive cần r5 để khôi phục media**, không phải bản backup độc lập. Giữ cả archive và r5. Không upload archive hoặc các parent; phạm vi Drive hiện có chỉ cho v4. Muốn mở lại đường dẫn lịch sử đã dọn, làm theo RESTORE vào destination mới rồi verify toàn bộ inventory/hash; không overwrite version có sẵn.

Chuỗi cần giữ: **r5 → v2 → v3 → v4**. Payload checksum r5 `c41bace184a46f06b6326e2be4d4792ea4016c00c8eeec4398e97033f32c7c67`; v2/v3 release pin parent tương ứng. Frozen inputs ở `data/interim/pilot-b/pilot-b-20261004-v1` là cây khác, không xóa.

Ngoài ra đã dọn `outputs/s1-valid`, `s1-broken`, `s1-overlays`, hai JSON s1 reports và `pilot-b-owner-groups-rebuild-evidence-20261005-v1`: tổng 79.211 bytes. Hai fixture so hash với generator; overlay/report xác nhận source names tổng hợp; rebuild evidence trùng byte với tracked owner evidence. Không xóa source/media review thật.

### Quy trình từ đây

- Training consumer chỉ pull pointer v4 và đọc `manifest.jsonl`; không cần toàn bộ `outputs` hoặc history preparation.
- Producer replay cần config chain, frozen inputs, parent và source roots đã pin. Không chuyển extracted sources hoặc đổi paths trong frozen config để làm đẹp cây thư mục.
- Scratch/test dùng TemporaryDirectory như tests hiện có; chỉ giữ evidence cần dẫn chứng. Trước dọn mỗi version: kiểm references/parent hashes, so payload, lưu metadata riêng, verify restore và ghi quyết định.
- Không gom/xóa ADR hoặc report theo ngày; chúng có chức năng quyết định/provenance khác code. Không chạy `git clean -fdx` hay DVC GC như cách dọn workspace.

## Giới hạn và việc tiếp theo

1. **B training còn chưa triển khai:** owner cần chốt model/weights/license/loss/transforms/hyperparameters và experiment; chưa có căn cứ cho metrics hoặc promotion. S9 crop runtime vẫn là gate riêng. Không mở rộng tracking/web trong review này.
2. **Portability replay:** config nguồn pin absolute archive paths ngoài repo và extracted roots trong outputs. DVC restore v4 portable; replay từ raw trên máy mới cần cung cấp đúng inputs/đường dẫn hoặc thiết kế operational root override trong task riêng. Không sửa frozen config.
3. **Dependency reproducibility:** pyproject dùng version ranges; base/dev/ml/dvc txt chỉ là entrypoints cài extras, không phải lockfile. Không nâng dependencies hoặc tự chọn version ML trong task này. Fresh Python/Linux CI/GPU inference chưa được thực thi ở đây.
4. **Inference còn giới hạn:** FPS do caller cung cấp, không chứng minh FPS đó khớp video hay hỗ trợ variable-frame-rate. Regression dùng test doubles, không tải weights/đọc video người thật. Generic detector chưa có model/label-map approval gate end-to-end. Thiết kế gate đó cùng model artifact contract trước runtime.
5. **Retention:** historical review outputs khác chưa chứng minh là bản trùng nên giữ. DVC cache/remote, source ZIP và media người thật không bị xóa/upload. Đây không phải secret scan toàn lịch sử Git, audit license mới hoặc re-review ngữ nghĩa từng ảnh.

## Validation và ảnh hưởng

Kết quả cuối sau cleanup: unittest/Ruff/compileall/repository checker/diff check đều PASS; `dvc status data/processed/pilot-b/pilot-b-20261005-v4.dvc` báo up to date.

Baseline: 109 unittest PASS. Sau thay đổi: 113 tests (bỏ 2 legacy-only, thêm 6 regression tests; các ca finite values/labels được parameterize). Lệnh từ repo root:

```powershell
.venv/Scripts/python.exe -m unittest discover -s tests -q
.venv/Scripts/python.exe -m ruff check src tests scripts
.venv/Scripts/python.exe -m compileall -q src tests scripts
.venv/Scripts/python.exe scripts/check_repo.py --require-git
git diff --check
```

V4 verify_payload/read_records PASS; ledger112, manifest84, 60/13/11 và28review_only; manifest/split/test subset hashes + test IDs giữ freeze. Payload list SHA `dbc1bf90a5605cac39b5c96503e71097ecd1eaab5b35e14f311f966edd503f53`. Git pointer blob SHA `f9f249f1f7bee62690e24f8bb437952c855866c9f7828da5af195d8c770564ef`; working-tree pointer CRLF khác raw hash nhưng normalized bytes và YAML bằng blob. Không coi checkout EOL là dataset corruption.

Diff đã kiểm; không thay label/encoding/split/threshold/experiment, không nâng Accepted ADR. Spec chỉ đồng bộ trạng thái và ghi owner choice FPS; dataclass shape không đổi. Chưa commit/push. Repository checker kiểm index hiện tại; file mới chưa stage được kiểm trực tiếp và qua test/lint, không tuyên bố đã kiểm một Git index sau commit.

Nguồn đọc: AGENTS/index/task/template; canonical docs 01–25 (P2 phần liên quan release); ADR-001–013; pilot contract/runbook, annotation/label/split specs, dataset research; config/CI/requirements/ignore rules; source/data/contract/inference và legacy train/eval, tests/caller search; release payload/parent hashes và inventory local. Báo cáo phân biệt read/static review, executable tests và artifact verification; không tuyên bố chứng minh mọi đường chạy chỉ từ suite pass.
