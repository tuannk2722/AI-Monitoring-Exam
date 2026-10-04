# WORKLOG

## 2026-10-04 — Chốt B/multi-label và tạm hoãn P042

- Owner chọn YOLO person → crop → multi-label classifier; normal là người đang làm bài, vắng mặt hai target đã review; co-occurrence giữ cả hai nhãn. Hai câu hỏi bổ sung đã trả lời: đồng ý looking_around dựa hướng nhìn rõ trên ảnh tĩnh và crop thêm bàn/phone liên quan có review. ADR-012 ghi quyết định, không tuyên bố có benchmark A/B.
- Đồng bộ architecture, label strategy/spec, annotation guideline, index và ghi supersession ADR-002/011. Config chỉ sửa note draft, không đổi tên/ID/mapping/split hoặc build schema.
- P042 chuyển deferred_initial_subset trong output mới v2 bằng logic nhóm đã có: 29 loại + 11 deferred + 13 held + 21 bbox-approved = 74. 24 bbox giữ nguyên; chưa đủ completeness, chưa accepted/train. Raw không đổi.
- Đã chạy 52 unittest PASS và Ruff PASS. Tiếp tục cần crop/completeness QA, schema classifier và kiểm chứng crop inference; hiện chưa chọn model/head/loss/threshold hay suy group_id. P0 DVC push/pull chưa kiểm chứng; P1 chưa đóng.
- Kiểm cuối: compile/repo checker/diff check PASS; 70 links và output/code/decision hashes PASS; queue chỉ thay P042, approved boxes giữ nguyên byte. Git 10 modified + 13 untracked gồm các lượt chưa commit trước; chưa commit. Checker chỉ xét Git index, không coi đó là kiểm tra toàn bộ file untracked.

## 2026-10-04 — Áp dụng owner review remaining QA

- Đọc AGENTS/index, ADR-011, annotation guideline, review đã sửa và code/manifest. Giữ nguyên hai câu trả lời của owner trong decision manifest mới; xác nhận P023 là phone, duyệt 13 ảnh/14 bbox, P042 giữ pending vì chưa có chỉ dẫn sửa/loại cụ thể; 13 ảnh thiếu bằng chứng giữ ngoài train.
- Output mới remaining-reviewed-20261004-v1: 74 ảnh = 29 loại + 10 deferred cũ + 13 held mới + 21 bbox-approved + 1 pending. Tổng 24 bbox; 8 record cũ bảo toàn, không ghi đè báo cáo trước. Chưa train/accepted, không đổi mapping/split/ADR/raw. Những mục QA trước ở dưới là lịch sử.
- Thêm công cụ áp dụng quyết định có pin hash và regression bảo vệ coverage/identity, không duyệt proposal rỗng, không biến hold/pending thành normal. 52 unittest PASS; Ruff/compile/repository checker/diff check PASS (checker chỉ Git index). Hash input/output/code, nguyên văn owner, 8 approvals cũ, tọa độ 14 bbox mới, queue và 62 liên kết PASS. Ruff lần đầu báo lambda assignment; đã sửa trước khi xuất bản cuối.
- Git cuối lượt: 3 modified + 9 untracked, gồm cả phần QA lượt trước chưa commit; không phải tất cả đều mới tạo lượt này. Ảnh/output ignored không tính vào số Git này. Thay đổi qua công cụ patch để review; chưa commit.
- Tiếp theo: hoàn thiện completeness cho 21 ảnh, trình owner quyết định formulation A/B, normal/co-occurrence và quy tắc looking_around trước nhãn chính thức; group/split và P1 vẫn mở. P0 DVC push/pull chưa kiểm chứng. P042 có thể tiếp tục ở ngoài, không cần hỏi lại để hoàn tất lượt áp dụng này.

## 2026-10-04 — QA toàn bộ phần Roboflow còn lại

- Đọc AGENTS/index, label/annotation/split specs, remaining-review và code/manifest hiện hành. Bắt đầu từ Git sạch tại cbd5eeb trên D:/ai-exam-monitoring-final.
- Xem riêng 27 ảnh train còn lại và 8 ảnh đã duyệt. Tạo 15 bbox đề xuất trên 14 ảnh; 13 ảnh giữ chờ bằng chứng. Xem lại 14 overlay có bbox, chỉnh extent P047; không gọi proposal là owner-approved. [Gói review](data/candidates/Roboflow-remaining-qa-20261004.md) có ảnh, crop và câu hỏi cụ thể.
- Thêm validator review plan, script tái tạo và 4 regression tests. Output v2 pin source/code/plan hashes, bảo toàn byte của 10 bbox cũ, ghi reject dòng toàn cảnh P070 riêng; không xuất training labels, không giải nén thêm ZIP. Fixture chỉ phục vụ phần mềm.
- Kiểm tra: 50 unittest PASS; Ruff PASS; repository checker --require-git PASS (chỉ Git index, chưa gồm file mới untracked). Lần test đầu có 2 lỗi do kỳ vọng sai loại exception; đã sửa test theo DataContractError hiện có và chạy lại toàn bộ thành công.
- Chờ owner review 14 proposal và phạm vi P042/P048; các ignore cũ không hỏi lại. Completeness đã rà và ghi thiếu, chưa hoàn tất annotation mọi người. Chưa chốt looking_around/normal/co-occurrence/A-B, group/split hoặc P1 acceptance. P0 DVC push/pull vẫn chưa kiểm chứng. Không đổi raw/config/ADR, không build/train.
- Kiểm cuối: compileall và git diff --check PASS; 57 output hashes, 4 input hashes, 58 liên kết và bảo toàn approved bytes PASS. Summary tracked bằng nhau theo JSON (khác newline Windows, không yêu cầu byte-identical). Git có đúng 3 modified + 6 untracked; ảnh/outputs ignored không tính vào số này. Chưa commit lượt QA mới để owner review đề xuất.

## 2026-10-04 — Đã áp dụng hai quyết định nhóm sau batch 2

- Owner chốt “Loại cả 7 ảnh nhiễu” P058–P064 và “Giữ ngoài subset đầu tiên” cho 10 ảnh góc khác/thiếu phần người; lưu nguyên văn, không suy group_id hoặc threshold.
- Queue v2: 74 = 29 loại + 10 deferred + 8 bbox-approved/completeness-pending + 27 pending bbox. 10 bbox trên 8 ảnh được duyệt, training_eligible vẫn 0. Các quyết định cũ và raw giữ nguyên.
- Đã chạy consolidation với `--group-review`; 46 tests, Ruff/compile PASS. Link kế hoạch công việc và bằng chứng hiện hành trong `Roboflow-remaining-review-20261004.md`. Không cần hỏi lại owner trong lượt này; tiếp theo là QA bbox/phone evidence/completeness cho 27 ảnh, không train hoặc chốt A/B/split khi chưa đủ bằng chứng.

## 2026-10-04 — Áp dụng owner review batch 2

- Đọc AGENTS/index, label spec, batch 2 và công cụ apply_decisions. Owner trả lời 6 mục: P006 không bỏ sót phần người; P008/P030/P031/P034/P036 Okay. Record giữ nguyên văn, source identity và tọa độ từng box; không hỏi lại các mục này.
- Chạy `roboflow_batch2_review`: pin base summary/output hashes, đối chiếu đúng source/boxes trước approval; hợp nhất 10 bbox trên 8 ảnh. 22 ảnh loại, 44 chưa duyệt bbox; training_eligible vẫn 0 vì completeness/multilabel/split chưa chốt.
- Đã xem cả 44 ảnh còn lại qua 4 sheets và gom vấn đề để owner quyết định theo nhóm: 7 ảnh nhiễu chấm, 10 ảnh thiếu phần người/góc CCTV khác. Chưa tự áp dụng loại ảnh diện rộng.
- 44 tests, Ruff/compile/checker PASS. Lần đầu đọc JSON có tiếng Việt bị encoding Windows; đã sửa UTF-8 và chạy thành công trước khi báo hoàn tất. Raw/config/split/acceptance giữ nguyên; P0 DVC và P1 chưa đóng.

## 2026-10-04 — Sau commit pilot, batch 2

- Commit `4af4dac` đã lưu 11 file pilot/owner review sau 40 tests, lint, compile, checker index và diff check PASS. Không push remote.
- `roboflow_continue` xác minh hash base, áp 4 quyết định vào queue mới; 22 ảnh loại/52 còn QA, 3 bbox duyệt trên 2 ảnh nhưng training_eligible vẫn false. Giữ record/phân bố lịch sử bất biến.
- Đã mở 6 ảnh train rõ phone, vẽ 7 bbox đề xuất và xem cả 6 overlay. [Batch 2 và câu hỏi cụ thể](data/candidates/Roboflow-phone-use-batch2-20261004.md). Nhãn chưa được owner duyệt, chưa đủ completeness.
- Chạy CLI tạo `outputs/roboflow-batch2-20261004-v1`; 42 tests PASS, Ruff/compile/checker PASS. Không sửa raw, split, config mapping hoặc acceptance; không train. Bước tiếp: review annotation batch mới, rồi QA completeness/multilabel trước quyết định A/B. P0 DVC chưa đóng.

## 2026-10-04 — Owner chốt pilot và tiếp tục batch

- Đã đọc bốn câu trả lời owner, giữ nguyên văn trong `pilot-owner-review.json`, pin hash tài liệu lúc nhận và plan v3. P019/P029 duyệt 3 bbox; P029 là hai người truyền cùng phone (cả hai phone_use), nhận định phone trên bàn trước đó sai và đã được đính chính. P053/P065 loại vì nhiễu.
- Kết quả quyết định: 22/74 ảnh loại, 52 còn QA; approval bbox không phê duyệt completeness, mapping, split hay dataset. Pilot plan/summary gốc giữ nguyên để tái tạo lịch sử.
- Owner yêu cầu commit phần đạt kiểm tra và tiếp tục batch. Không cần thêm quyết định cho bốn mục này. Bước tiếp theo: áp dụng decision record vào queue version mới, chuẩn bị các ảnh phone rõ trên train; không dùng test cho policy.

## 2026-10-04 — Pilot person relabel và similarity triage

- Mốc audit đã được owner commit `806e08c`; working tree sạch khi bắt đầu. Thay đổi mới để chưa commit cho owner review trực tiếp.
- Đọc AGENTS/index, P1/split spec, annotation/label spec, ADR-011, audit code/source layout và CI. Owner chốt bbox chỉ bao phần người nhìn thấy; bổ sung ADR/guideline.
- Chạy `scripts/audits/roboflow_pilot.py` trên đúng ZIP RF v1 đã pin SHA. Kết quả cuối `outputs/roboflow-pilot-20261004-v3/`: 74 cặp train (66 Phone use + 8 mẫu bổ sung), không extract toàn ZIP; 20 loại theo quyết định/policy, 54 chờ QA. Raw và config/mapping không đổi.
- Xem 74 thumbnail qua 7 sheets, mở riêng W01/R12/R09/R03; vẽ 5 person boxes đề xuất trên 4 ảnh. Đã kiểm overlay, sửa R09 bao phần tay tới cạnh dưới. Chưa đầy đủ nhãn mọi người, chưa training-eligible.
- Fingerprint 3.407 ảnh RF, tìm nearest từng split cho 74 ảnh queue. Khoảng cách 0: 15/13/9 truy vấn tới train/valid/test; không đồng nghĩa duplicate/session/leakage xác nhận. Xem 2 cặp train thấy poses khác nhau dù cùng hash; không mở test cho policy. Chưa perceptual cross-SCB.
- Kiểm tra: 40 unittest PASS; Ruff, compileall, checker và diff check PASS. Lượt Ruff đầu bị chặn ghi cache, dùng `--no-cache` chạy thành công. Regression cho collision/tie/full-path/self exclusion và invalid bbox. Fixture không dùng đánh giá model.
- [Bốn ảnh và câu hỏi owner review](data/candidates/Roboflow-phone-use-pilot-20261004.md), [plan](../artifacts/reports/roboflow-20261004/pilot-plan.json), [summary/hash](../artifacts/reports/roboflow-20261004/pilot-summary.json). Cần owner review bbox/association/ảnh nhiễu trước khi nhân rộng; A/B/split/accepted chưa chốt, P0 DVC vẫn chưa kiểm chứng.

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


## SCB supplied audit — 2026-10-03

- Goal: audit đúng 3 ZIP local owner cung cấp, không chọn release khác. Đã đọc lại AGENTS/index, template candidate, docs 03/04/08/09/21/25, data specs/source-audit, ADR-002/003 và audit/overlay/source layout code. Worktree sạch khi bắt đầu; không thay code/config/ADR, không sửa raw, build hoặc train.
- Xác minh hash/bytes cả 3 archive với blob remote; quan sát HF HEAD nhưng trang pin commit không truy cập được. Định danh audit dùng SHA-256 ZIP, ghi hạn chế này trong provenance. Giải nén có kiểm path và CRC vào `outputs/scb-audit-20261003-v1/` mới.
- Chạy công cụ audit chuẩn trên toàn bộ 10.138 ảnh + 10.138 label: không ảnh hỏng/thiếu cặp; 546 file có cảnh báo, 625 dòng bbox lỗi; 68.882 raw rows và 63.505 annotations từ file strict hợp lệ. Giữ nguyên validator, không clip/nới epsilon.
- SHA-256 chéo archive: 8.116 ảnh bytes duy nhất; 1.892 nhóm duplicate, 2.022 bản dư; 961 nhóm chéo train/val. Không chạy near-duplicate; không suy ra group_id. Đã xem ví dụ cùng bytes HRW-val / Head-train nhưng bộ nhãn khác nhau.
- Visual review: 18 sample theo class qua contact sheets + 4 preview + 6 warning + 2 duplicate overlays (30 lượt render, có thể dùng lại nguồn ảnh); chỉ là mẫu có chủ đích. Tạo checklist câu hỏi theo ảnh, không dùng ảnh để kết luận model quality.
- Deliverables: 3 tài liệu candidate/audit/review trong `docs/data/candidates/`; JSON bằng chứng nhỏ trong `artifacts/reports/scb-20261003/`; báo cáo đầy đủ, scripts phiên audit và PNG local trong outputs ignored. Mục index và dataset-research đã liên kết.
- Checks: 34 tests PASS; Ruff/compile/check_repo PASS; đã đối chiếu dữ liệu thực tế và rà diff. Audit orchestration exit 0 = chạy xong; cả 3 report has_errors=true, không phải data pass. Chưa DVC push/pull; P0 chưa đóng.
- Decision đề xuất: giữ CANDIDATE, chưa chọn dataset training đầu tiên; thiếu phone_use/normal theo source, Discuss không cùng person unit, rights/group/QA chưa đóng; chưa đủ chứng cứ chốt A/B. Không thay config pending_audit.
- Owner nói đã có tài liệu quyền/metadata nhưng sẽ cung cấp sau; chưa có đường dẫn/nội dung để xác minh. Các TBD và điều kiện qua P1 ghi trong candidate card.

## Quyết định SCB và nguồn phone_use tạm — 2026-10-04

- Đã truy cập project mới tại D:/ai-exam-monitoring-final. Đọc AGENTS/index, docs 04/08/21, template candidate, source-audit, candidate SCB, dataset-research, config dataset và worklog.
- Owner loại Discuss, xác nhận quyền/metadata SCB đã phê duyệt; ghi cập nhật riêng trên candidate, giữ số liệu audit lịch sử. BowHead chỉ là đề xuất tín hiệu phụ, chưa đổi nhãn/rule. Metadata group từng file vẫn cần dữ liệu thực tế.
- Owner cung cấp project Roboflow trn-quang-tip/exam-cheating-9iz1y-rrfsz và chốt audit v1. Tạo candidate card; website công bố 3.407 ảnh và 3 lớp, CC BY 4.0. Đây là thông tin web, chưa kiểm chứng archive.
- Blocker thực tế: web browse/image/download Cache miss; shell mạng sandbox WinError 10013; sau khi cho phép truy cập mạng, API v1 trả HTTP 401 yêu cầu API key. Cần ZIP export YOLO v1 local từ owner; không yêu cầu gửi khóa.
- Chưa chạy data audit/overlay/duplicate vì chưa có export; chưa xem ảnh bbox; chưa kết luận dataset dùng train được. Không build/train/accepted hoặc sửa config, raw, canonical mapping, split/ADR.
- Kiểm tra tài liệu: git diff --check PASS; .venv/Scripts/python.exe scripts/check_repo.py --require-git PASS (0 failures). Không chạy lại unit tests vì chỉ sửa tài liệu. P0 DVC và P1 chưa đóng.
- Thay đổi của lượt này: thêm candidate Roboflow; cập nhật candidate SCB, index, dataset-research và WORKLOG. Các thay đổi audit SCB có sẵn được giữ nguyên.
- Tiếp theo: hash/inventory ZIP v1, xác minh ID từ data.yaml, audit split và duplicate chéo split/SCB, review ảnh train trước đề xuất mapping/subset.

## Roboflow v1 owner ZIP audit — 2026-10-04

- Đã đọc lại AGENTS, index, docs 04/08/21, template candidate, source-audit, candidate SCB/Roboflow, dataset-research, config dataset và audit/overlay/source-layout/YOLO code.
- Đúng file owner gửi: `C:/Users/OS/Downloads/Exam cheating.v1i.yolov8.zip`, 98,747,246 bytes; SHA-256 `70060bfe7d65dedcca6a72aaac423c95f402369eec08563b24ae8d962e666eed`; CRC test pass, 6,826 ZIP entries. `data.yaml` xác nhận version 1, ID/tên 0 Looking around, 1 No cheating, 2 Phone use; README export ghi 3,407 ảnh.
- Đã giải nén an toàn vào ignored `outputs/roboflow-v1-20261004/`. Audit công cụ hiện hành chạy trên 100% ảnh train/valid/test theo từng subtree: cặp đủ 3,407; 0 ảnh hỏng, missing/orphan/ambiguous, empty labels; 34 file label có bbox vượt biên (22 train, 11 valid, 1 test); không tự sửa dữ liệu. Phân bố từ file label hợp lệ: train 6558/1515/79; valid 1089/385/26; test 573/145/12 theo ID 0/1/2. Phone Use 117 annotation hợp lệ (~1.13% của tổng 10,382 annotations hợp lệ).
- Exact SHA trong v1: 0 nhóm duplicate nội bộ/cross-split. Đối chiếu toàn bộ ảnh với 8,116 SHA unique trong archive SCB: 0 trùng chính xác. Near duplicate và group/session chưa xác minh.
- Tạo 24 train overlays (8/lớp, selection theo đường dẫn, không đại diện) và warning contact sheet. Đã xem trực tiếp ba overlay cùng hai ví dụ cảnh báo. Ví dụ cho thấy lớp 0/1 box dày trong cảnh thi/semantics mơ hồ; ID2 gồm mẫu người cầm phone nhưng box cả người và một cảnh video nói chuyện ngoài thi. Không kết luận tỷ lệ sai toàn nguồn.
- Deliverables: candidate card cập nhật, audit report mới, index/dataset-research/worklog. Raw archive không sửa; config/mapping/split/ADR/status acceptance/build/train không đổi. Candidate phone_use vẫn chưa accepted.
- Kiểm tra tài liệu: `git diff --check` PASS. Không chạy test vì chỉ có audit dữ liệu và sửa docs/artifact; không có thay đổi code.
- Giới hạn/chốt tiếp: báo cáo chưa đánh giá gần trùng, completeness/semantics toàn cục, consent/chain of rights hay group leakage. Owner xem các overlay và cảnh báo; hoàn tất duplicate chéo SCB trước đề xuất kết hợp; có metadata video/session nếu lấy được.

## Hoàn thiện hồ sơ Roboflow v1 — 2026-10-04

Bản ghi này thay thế kết luận thiếu chi tiết/mâu thuẫn ở lượt audit Roboflow trước; giữ các mục trước làm lịch sử. Owner yêu cầu mức đầy đủ như hồ sơ SCB, kèm diff riêng để review.

- Đọc/đối chiếu AGENTS/index, docs 04/08 và template candidate, label spec, ADR-002/003, báo cáo/card/review SCB, source audit/overlay/YOLO và provenance/diagnostics. Snapshot trước task: outputs/reviews/roboflow-completion-before.json; không lẫn các thay đổi audit cũ vào diff của task.
- Thêm scripts/audits/roboflow_v1.py để tái tạo có pin SHA, CRC, quét raw rows, dùng audit/overlay hiện có và check SHA cross-SCB. Lần này tái sử dụng 3 full-decode reports đã chạy, kiểm checksum và đối chiếu mọi label từ ZIP; không tuyên bố decode lại. Chỉ trích 16 cặp cho overlay; không giải nén lại toàn bộ ZIP. Output/evidence phải mới, không ghi đè input.
- Số liệu sửa/hoàn thiện: 10,528 raw rows; 10,493 dòng geometry hợp lệ; 10,382 strict annotations. 35 dòng lỗi/34 file đều khoảng 0.005 pixel, khác đánh giá mơ hồ “bbox lỗi” trước đó. Phone use 120 raw/117 strict trên 98 raw/95 strict images; cả 120 phone rows đều geometry hợp lệ, 3 bị loại strict do lỗi ở lớp khác trong file. Train phone: 82 raw annotations trên 66 ảnh. Không thay epsilon/repair/mapping.
- Đo resolution, bbox min/p10/p50/p90/max từng lớp; kiểm lại hash toàn ảnh từ 4 ZIP: 0 exact duplicates nội bộ RF/cross-split/cross-SCB. Chưa near duplicate; chưa group metadata, không suy group_id từ filename.
- Đã xem 16 ảnh train hợp lệ + 2 ảnh warning; R01–R06 qua contact sheets, R07–R16/W01–W02 đầy đủ. Mixed unit Phone use xác nhận ở R07/R09/R12: điện thoại/tay và person; W01 có người cầm phone mang ID0. Không kết luận tỷ lệ lỗi toàn tập. 24 overlay cũ không bị gọi là 24 ảnh đã review.
- Deliverables: 12 JSON nhỏ ở artifacts/reports/roboflow-20261004 (10 output script + visual-review + verification), script tái tạo, checklist review có link ảnh/câu hỏi; viết lại candidate/audit, đồng bộ index/dataset-research. Provenance ghi code/hash/env/command và reports reuse. Full reports/raw invalid rows/image hashes/PNG ở outputs ignored, không commit media.
- Checks thực tế: 34 unittest PASS; Ruff PASS; compileall PASS sau khi cấp quyền ghi __pycache__ (lần sandbox đầu bị PermissionError); check_repo --require-git PASS; git diff --check PASS; 60 local links và tính nhất quán số liệu/hash PASS. Render final v2 giống bytes bản đã mở xem. Không chạy mode full-extract/decode lần nữa; lệnh tái tạo cả full/reuse được ghi rõ.
- Kết luận: hoàn thiện bộ hồ sơ audit, nguồn vẫn CANDIDATE. Đề xuất review/relabel subset train; chưa đủ chốt A/B vì unit/negative semantics/grouping. Owner xem checklist và chốt unit/repair/mapping, không tự build/train/accepted. P0 DVC push/pull và P1 chưa đóng.

## 2026-10-04 — Chốt owner review Roboflow

- Đã giữ nguyên 18 câu trả lời, ghi [manifest](../artifacts/reports/roboflow-20261004/owner-decisions.json) và [ADR-011](decisions/ADR-011-person-unit-phone-definition.md). Owner làm rõ R12: phone cầm/tương tác hoặc trên bàn gắn được với người; chốt person unit và normal là absence đã review. Label spec draft v0.2; runtime config/mapping chưa đổi.
- W02: preview version riêng, chỉ clip dòng 4; strict geometry pass, đã xem overlay. W01 vẫn cần relabel thủ công. Raw/ZIP và báo cáo gốc giữ nguyên. Decision queue không phải bộ nhãn đã sửa.
- [Kiểm chứng](../artifacts/reports/roboflow-20261004/owner-review-verification.json): 36 tests PASS, Ruff/compile/repo checker/diff check PASS; 18 câu trả lời bảo toàn; hash preview/script/ảnh và 79 local links PASS trước khi thêm mục worklog này.
- Chưa hoàn tất: manual relabel/completeness/quality cho subset, looking_around/co-occurrence, near-duplicate và session metadata, quyết định A/B/mapping/split. P1 chưa đạt; P0 DVC push/pull vẫn chưa kiểm chứng.
- Tiếp: pilot person relabel theo policy mới trên train (66 ảnh Phone use raw cùng mẫu thiếu/sai đã phát hiện), giữ ignore ngoài train đến khi xử lý được, review batch rồi đánh giá khả thi A/B. Không cần owner trả lời lại checklist cũ.
- Review thay đổi riêng lượt này: [diff](../outputs/reviews/roboflow-owner-review.diff), [danh sách file và Git status](../outputs/reviews/roboflow-owner-review-files.json). Không commit tự động.
