# WORKLOG

## S0 — 2026-10-03

Owner/người chốt: chủ repository. Triển khai/review kỹ thuật: Codex. **P0 → P1; P0 chưa hoàn tất.**

### Đã đối chiếu

Đã đọc: AGENTS.md, docs/00-INDEX.md; docs 05–07, 15–17, 22–23; ADR-004/005; README, requirements, pyproject, CI, task/PR templates, checker và tests. Không đổi ADR, dataset approval, label/mapping/split, kiến trúc AI hay experiment config.

### Hiện trạng và hoàn thành

- Windows; Python mặc định 3.14.2 ngoài phạm vi hỗ trợ, không import được package dự án/Ruff. `.venv` có Python 3.11.9, editable package 0.1.0 và Ruff 0.16.10; dùng interpreter này cho kết quả bên dưới.
- Checker cũ báo nhầm hai file `.pth` trong venv. Checker mới kiểm tra Git index (staged/force-added kể cả đã xóa trên disk), bỏ qua untracked/ignored. Kiểm tra đường dẫn nhạy cảm/media/model và vùng dữ liệu/venv; không phải secret scanner nội dung/lịch sử.
- ZIP: kiểm tra cấu trúc/docs, cảnh báo tracking chưa xác minh; `--require-git` fail khi thiếu Git metadata. Git lỗi không được coi là ZIP hợp lệ.
- Đồng bộ README/CI; workflow, AGENTS và template hỗ trợ owner tự review/chốt, Codex hỗ trợ. Giữ gate dữ liệu/license/consent/test isolation/chất lượng.
- Giữ nguyên việc xóa `MIGRATION.md` có sẵn trước S0; không train, tải dataset hay triển khai web.

### Kết quả thực tế

Các lệnh Python dưới đây dùng `.venv/Scripts/python.exe`:

| Kiểm tra | Kết quả |
|---|---|
| `-m unittest discover -s tests -v` | PASS 19 tests (12 cũ + 7 hồi quy checker); không skip |
| `-m compileall -q src tests scripts` | PASS |
| `-m ruff check src tests scripts` | PASS |
| `scripts/check_repo.py --require-git` | PASS, 0 failures |
| `-m pip check` | PASS, không có dependency conflict |
| `git diff --check` | PASS; đã xem diff |
| `-m pip install --retries 0 --timeout 15 -r requirements/base.txt -r requirements/dev.txt` | BLOCKED: PyPI socket WinError 10013 khi lấy setuptools>=75 |
| Cài cùng requirements với `--no-index --no-build-isolation` | FAIL: thiếu wheel (`invalid command bdist_wheel`); không hạ build requirements để né lỗi |
| `-m pip show dvc` | Chưa cài DVC; không có `.dvc/config` |

Test hồi quy: ignored/untracked không gây lỗi; force-add và file tracked đã xóa vẫn bị chặn; template/pointer/.gitkeep hợp lệ; ZIP thường/strict; thiếu cấu trúc/index; Git lỗi/không có executable; `.git` dạng worktree và tên file phân cách NUL.

### Blocker và tiếp theo

1. **TBD-S0-INSTALL — owner:** cho phép môi trường truy cập package index, cài base/dev từ clone và venv sạch theo README, chạy lại CI checks. Test trên venv có sẵn không chứng minh cài mới thành công.
2. **TBD-P0-DVC — owner:** cài DVC; cung cấp folder Drive restricted và authentication local; push fixture nhỏ không nhạy cảm, clone đúng commit với cache rỗng, pull và so SHA-256 theo docs 22. Chưa chạy push/pull; không được đóng P0.
3. Remote Git origin đã cấu hình; GitHub Actions thực tế, branch protection và lịch sử secret/binary chưa được xác minh trong phiên này. Owner kiểm tra trước đóng P0.
4. Sau các gate P0, tiếp tục P1 audit nguồn/license/provenance; dataset/model vẫn chưa chính thức.


## S1 — 2026-10-03

Owner/người chốt: chủ repository; Codex triển khai/review kỹ thuật. Hoàn thành công cụ kiểm tra bằng fixture CPU; **chưa audit/accepted dataset thật**, P0 vẫn chưa đóng.

- Đã đọc: AGENTS, index; docs 01/02/04/08/09/19/21/23/25; ADR-002/003; bốn data specs hiện có; mã data, README, pyproject, DVC pipeline. Phát hiện validator trả pass cho thư mục thiếu, NaN lọt parser, audit ghép global stem và tính metadata là label.
- Sửa `data/yolo.py`, `validate_labels.py`, `audit.py`; thêm `source_layout.py`, `overlay.py`. Từ chối NaN/Infinity/bbox/class ID lỗi; phân biệt thiếu label với label rỗng. Ghép đường dẫn tương đối rõ ràng; báo thiếu/hỏng/ambiguous, phân bố lớp, kích thước bbox, nhóm trùng SHA-256. Overlay ID/tên nguồn có manifest; source không bị sửa.
- Thêm `tests/fixtures/make_audit_fixture.py` và `tests/test_data_audit.py` (15 test mới); fixture sinh trong temp/outputs, chỉ kiểm chứng phần mềm, không là dữ liệu/model evidence. Cập nhật README, docs 08/index, `docs/data/source-audit.md`, tham số DVC audit.
- Validation dùng `.venv/Scripts/python.exe`: **34 tests PASS**, Ruff PASS, compileall `src tests scripts` PASS, checker `--require-git` PASS, `git diff --check` PASS. Đã rà diff; DVC YAML parse được, chưa chạy DVC pipeline.
- CLI thực tế: fixture hợp lệ audit exit 0, validator exit 0, overlay exit 0 với 2 PNG; đã mở ảnh và thấy bbox/ID/tên đúng vị trí. Fixture lỗi audit exit 1 với missing/orphan, 1 ảnh hỏng, 2 label lỗi và 1 nhóm exact duplicate; validator exit 1 cho NaN/class lạ. Validator thư mục không tồn tại exit 1.
- Artifact local ignored: `outputs/s1-valid-report.json`, `outputs/s1-broken-report.json`, `outputs/s1-overlays/{0001.png,0002.png,manifest.json,audit.json}`; tái tạo theo README bằng thư mục output mới.
- Impact: report audit schema v2 thay v1 global-stem; overlay manifest v1. Không thay ADR, label/mapping/split, group_id, config acceptance hoặc experiment/model. Near-duplicate, leakage và ngữ nghĩa chưa được kiểm tra; báo cáo ghi rõ human review. Overlay đầu N theo đường dẫn không là mẫu phân tầng.
- Tiếp theo: owner cung cấp cấu trúc và bảng ID/tên nguồn xác minh cùng provenance/license để audit một mẫu nguồn thật; xem ảnh theo lớp/điều kiện rồi ghi đề xuất mapping. Chưa suy ra canonical mapping. Blocker cài sạch/DVC push-pull của S0 vẫn giữ nguyên.
