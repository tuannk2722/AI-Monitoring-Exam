# Quy trình phát triển và vận hành repository

## 1. Mục đích và cách đọc tài liệu

Đọc khi bắt đầu/resume task, sửa code, kiểm tra, bàn giao hoặc tái lập dữ liệu/model. Bộ spec gồm bốn tài liệu: `system.md` cho phạm vi/kiến trúc/requirements/trạng thái end-to-end; `data.md` cho semantics/schema/nghiên cứu/releases/QA; `training.md` cho recipe/evaluation/results/E004; tài liệu này cho cách thực hiện. Kết quả/decisions cần cho coding nằm trong đúng spec, không cần một chuỗi results/ADR/research pages riêng.

`AGENTS.md` là hướng dẫn ngắn, `docs/00-INDEX.md` chỉ định tuyến. `.codex/TASK.md` là checkpoint của **một task hiện hành**, dùng mẫu duy nhất `docs/templates/task-template.md`; không là source of truth khoa học hoặc WORKLOG. Machine-readable approval JSON trong `docs/experiments/` giữ vì trainer pin digest, không phải thêm spec cần đọc mọi task.

Nguồn quyết định: owner approval đúng phạm vi + quyết định Accepted trong spec → config/receipt có phiên bản → implementation. Với số liệu thực nghiệm, manifest/run/metrics/checksum là bằng chứng gốc; nếu lệch với mô tả phải báo và cập nhật mô tả có traceability, không đổi payload/label/metric để khớp câu chữ. Draft/TBD không được suy thành approval; authorization hội thoại đúng scope được giữ qua task/resume.

## 2. Workflow một task

1. **Hiểu yêu cầu và hiện trạng:** đọc index/TASK, đúng phần spec, Git diff/files và code producer/consumer. Ghi đã đọc gì và requirement/version liên quan; không đọc lại tài liệu không đổi hoặc mọi thư mục research.
2. **Xác định đầu ra và gate:** hành vi trước/sau, artifact/path cần tạo/sửa, acceptance/checks. Đối chiếu trạng thái đã có/chưa có trong system/data/training; không train lại baseline hoặc mở web khi task còn ở data/model gate.
3. **Checkpoint trước sửa:** cập nhật TASK với mục tiêu, inputs/pins, constraints, changes, checks và bước tiếp. TASK cũ/mâu thuẫn phải sửa; proposal của agent không tự là quyết định Accepted.
4. **Thực hiện tập trung:** dùng conventions/modules/CLI hiện có; logic tái dùng trong src, experiment variables trong YAML. Draft được tự động hóa, owner nghiệm thu high-level; không bắt owner annotate từng ảnh. Không tạo script/config/Markdown cho từng câu hỏi hoặc vòng review.
5. **Kiểm đúng phạm vi:** test consumers và contracts bị ảnh hưởng, lint/type phần đổi, diff/links. Dataset/model kiểm theo protocol riêng; unit PASS không thay quality gate. Có lỗi/missing pins thì điều tra nguyên nhân thay vì bỏ guard.
6. **Bàn giao:** ghi thay đổi, evidence/checks/limitations, decision và việc tiếp trong đúng spec/TASK/config/run record. Khi research có kết luận mới, cập nhật data/training spec để task sau biết kết quả, không chỉ lưu một report link.
7. **Dọn sau task:** bỏ cache/checkout/preview/tooling tạm khi đã có kết quả/bằng chứng cần giữ; lịch sử lớn đưa vào storage có kiểm chứng. Không xóa accepted release/model/approval hoặc reseal originals. Stage/commit/push chỉ theo yêu cầu user, không làm để vượt checker.

Task có kiến trúc/schema/API/persistence/scope chưa rõ: chuẩn bị proposal cụ thể từ code/spec rồi hỏi owner đúng quyết định còn thiếu; phần độc lập tiếp tục. Không tự chốt label/split/source/license/pretrained/training variables/threshold/metrics/risk/test access. Solo owner tự review, không yêu cầu người thứ hai.

## 3. Môi trường và commands hiện có

Python >=3.11,<3.13, CI 3.11; `.venv` local hiện đã có. Setup mới chỉ khi thiếu môi trường, không tạo thêm bản env/checkout cho mỗi task:

```powershell
py -3.11 -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements/base.txt -r requirements/dev.txt
```

`requirements/base.txt` cài package editable, dev thêm Ruff/Mypy; `classifier-cpu.txt` cho synthetic classifier tests, `classifier-cpu-lock.txt` là closure Python 3.11 Windows CPU đã đo ở E001. Historical lock gồm torch 2.8.0+cpu/torchvision 0.23.0+cpu và exact dependencies; tái lập run phải dùng environment đã ghi, không gọi lock đó là universal Linux/Colab lock. Nhóm ML/DVC chỉ cài khi task dùng, không tự tải weights.

Các CLI đã có đều dưới prefix `ai_exam_monitoring`: `data.audit`, `data.overlay`, `data.validate_labels`, `data.image_similarity`; `training.train`, `training.evaluate`, `training.error_audit`; `inference.detect`; `common.history`. Kiểm flags bằng `--help`/code khi thực hiện. Không có training `dvc.yaml`, vì vậy không dùng `dvc repro` thay trainer CLI.

Colab/GPU vẫn là hướng tương lai được scope approve riêng: exact checkout → dependencies → auth từ secret → pull đúng versions có quyền → verify → smoke → canonical CLI → sync last/best/status. Notebook không thay logic, runtime kết thúc/OOM giữ trạng thái; đổi variables tạo run identity mới.

## 4. Kiểm tra theo phạm vi thay đổi

| Thay đổi | Checks cần làm |
|---|---|
| Chỉ spec/AGENTS/TASK | Nội dung/trạng thái/traceability, links và diff; checker nếu đổi index/cấu trúc; không ML suite hoặc hash mọi media |
| Python module/test | Ruff/type phần đổi và unit tests trực tiếp; mở rộng consumers khi đổi helper/schema hoặc có failure |
| Codec/loader/preprocess/loss | Tests masks/versions/rights/freeze/group, preprocessing geometry/modes, consumers training/evaluation; kiểm pins của version liên quan |
| Dataset/experiment config | Parse/schema/digest và approval đúng scope; smoke/rebuild chỉ nếu task cần và inputs đủ; không tự chạy training |
| Binary release/model | QA/checksum/rebuild/evaluation theo protocol được duyệt; không sửa accepted bytes vì refactor |
| Trước merge / thay đổi rộng | Full base và classifier nếu liên quan ML, lint/compile/checker/diff; không model/test inference thật chỉ để kiểm phần mềm |

Chạy một nhóm, ví dụ checker:

```powershell
.venv/Scripts/python.exe -m unittest discover -s tests -p test_check_repo.py -q
.venv/Scripts/python.exe scripts/check_repo.py --require-git
```

Các lệnh đầy đủ khi phạm vi yêu cầu:

```powershell
.venv/Scripts/python.exe -m unittest discover -s tests -q
.venv/Scripts/python.exe -m unittest discover -s tests -p 'test_training*.py' -q
.venv/Scripts/python.exe -m ruff check src tests scripts
.venv/Scripts/python.exe -m compileall -q src tests scripts
.venv/Scripts/python.exe scripts/check_repo.py --require-git
```

CI quality dùng base/dev, classifier job dùng Torch CPU/training + preservation fixtures. Base skip đúng tests cần Torch; không dataset/GPU/weights download. Bộ active đã kiểm ở cleanup: 114 tests PASS, gồm 24 classifier; base mô phỏng 90 chạy/24 skipped. Đây là evidence tại thời điểm kiểm, không chứng minh task tương lai đã PASS.

Strict mypy là gate cho active source và repo checker: `.venv/Scripts/python.exe -m mypy src/ai_exam_monitoring scripts/check_repo.py`. Type debt 41 lỗi/9 file của snapshot trước đã được xử lý trong task handoff: khai báo JSON boundaries, thu hẹp optional crop/group, kiểu geometry/RNG và typed return; không đổi recipe. Torchvision chưa có marker typed được phân tích bằng `follow_untyped_imports`, không tắt strict toàn project. Classifier CI cài dev dependencies và chạy gate này.

`check_repo.py --require-git` kiểm required paths/index links, archive registry/pointer và Git index kể cả staged/force-added. Required files và source/tests/scripts/docs/config/requirements/CI mới phải nằm trong index; staged deletion không được lấp bằng untracked file cùng path. Archive pointer mới phải khai báo trong `archive/index.json`, path/MD5/size hợp lệ; binary ZIP vẫn bị chặn. Checker không là content secret scanner hoặc model-quality gate. ZIP mode thiếu Git chỉ kiểm cấu trúc; `--require-git` phải fail. Trước commit review staged diff và chạy checker; sau commit kiểm clean checkout không có local binaries để chứng minh source/spec đầy đủ.

## 5. Storage, phiên bản và bằng chứng

| Vùng | Vai trò hiện tại |
|---|---|
| `src`, `tests`, `scripts` | Code tái dùng, regression fixtures và repo checker; không launcher mỗi phiên nghiên cứu |
| `configs/datasets` | Bốn config accepted v4–v7, giữ exact bytes/pins |
| `configs/experiments` | E001–E003/smoke lịch sử và E004-plan Draft; recipe mới có ID/approval riêng |
| `data/processed/pilot-b` | Bốn canonical releases; binaries ignored/DVC theo scope, không mutate bản đã ký |
| `outputs` | 11 DVC targets local cho pretrained/ba runs/smoke/evaluations thật; output tạm mới phải có mục đích và dọn sau task |
| `artifacts/reports` | Hồ sơ release/E001–E003/v7-fit audit và dependencies v5 được loader pin; originals sealed không gộp/rewrite |
| `archive` | History ZIP immutable, DVC pointer và index nhỏ; dùng lấy exact evidence/input, không là tài liệu onboarding |
| `docs` | Index + bốn specs + task template; JSON approval được giữ để code kiểm |

Git lưu code/spec/config/metadata nhỏ. Không commit raw/media/model/checkpoint/env/cache/credentials. Binary local cần archive/DVC và backup theo quyền; **commit Git pointer không lưu nội dung binary**. V4 remote restricted đã approve/round-trip; các model/releases/archive có bản sao riêng trên D theo §8, chưa là backup remote hoặc khác ổ. Không tự push lên teamdrive.

Raw version bất biến; derivative ở interim/processed với provenance/hash. Group/schema/label/split/config mutation tạo version/pointer mới và owner decision. Giữ metadata consent/rights/use scope/attribution/changes, không dùng real identity trong filenames/manifests. Chỉ cần spec/config/receipt đúng task; không đọc mọi report hoặc thêm WORKLOG/trang trạng thái trùng.

## 6. Sử dụng lại audit/research và tái lập bản cũ

### Vòng đời file trong mỗi task

| Loại | Vị trí và cách cập nhật | Khi kết thúc |
|---|---|---|
| Logic tái dùng | `src/ai_exam_monitoring/<responsibility>` + tests liên quan | Một implementation; revisions dùng Git, không thêm script tên ngày/r1/r2 |
| Variables được duyệt | `configs/datasets` hoặc `configs/experiments` theo version/ID | Draft có thể sửa trước pin; đã ký tạo version mới, không overwrite |
| Scratch/preview/checkout | `outputs/_scratch/<task-id>/` | Không tham chiếu từ accepted pins; xóa sau khi giữ kết quả cần thiết |
| Review batch còn làm | `data/interim/<task-id>/` với một current pointer | Revisions chưa ký có thể thay; revisions đã review/hash giữ immutable khi còn dependency |
| Evidence được giữ | `artifacts/reports/<release-or-run-id>/` chỉ metadata cần audit/reproduction | Giữ approval, inputs/pins, delta, QA, receipt/checksums; không chép lại spec/nhật ký mỗi lần |
| Dữ liệu/model | `data/processed/<family>/<version>` / `outputs/<run-id>` | DVC/backup theo scope; không Git binary, không mutate accepted artifacts |
| Kết luận và trạng thái | Section tương ứng trong bốn specs; một TASK hiện hành | Ghi kết quả/giới hạn/next work rồi thay TASK ở task sau |

TASK phải ghi ngay outputs nào là tạm, evidence nào cần giữ và tiêu chí dọn. Trước xóa, kiểm không có config/approval/receipt còn pin path đó, xác minh checksum bản lưu và cách restore; không xóa input độc nhất vì được gọi là cache. Archive mới dùng tên riêng, registry + `.dvc` metadata mới; không append/reseal ZIP cũ. Registry/checker cho phép nhiều bundle, chỉ metadata được Git lưu. Không lưu raw người thật/secrets trong report/TASK.

### Inputs tối thiểu để dùng lại kết quả

| Nhu cầu | Inputs cần có | Cách kiểm / giới hạn |
|---|---|---|
| Đọc kết quả E001–E003 | `artifacts/reports/E00N/metrics.json`, training §5–6 | Không cần restore source hoặc chạy inference |
| Verify package v4/v6/v7 | Package đầy đủ + `checksums.sha256`, manifest/ledger/release/split/freeze | `integrity.verify_payload` + codec; không tự cấp test access |
| Verify loader v5 | Package v5 và v4; v5 release approval/preservation; ba pins membership/groups/proposal | Ba metadata dependencies đã khôi phục exact bytes vào paths trong owner approval; không cần bung archive để verify loader |
| Evaluate/reproduce E001–E003 | Exact Git commits `45240ea` / `0825239` / `4e206a6`; configs/approvals; package v4/v5/v6; pretrained đúng weights SHA; run artifacts và environment của `run.json` | Original package-wide code identity; evaluator đòi output mới. Scope final test giữ nguyên, restore không là approval mở lại test |
| Rebuild v7 | Snapshot source trước cleanup, exact config v7, parent v6/source inputs, ledger/assignment/whole-family/rights/provenance/review pointer và dependencies chúng trỏ tới | Dùng restore recipe bên dưới trong workspace riêng; current builder đã đổi self-SHA nên không chạy để reseal |
| Tái dùng shortlist/review | Data §8 mapping → Git module gốc/import closure → exact source/config pins | Read-only `git show` trước; chỉ thích nghi phần cần dùng cho task mới, có tests |

Thiếu path: kiểm active → `common.history list/show` đúng prefix → `git show <commit>:<path>` cho tracked text/code → backup được kiểm. Không dùng output của `git show` qua PowerShell text redirection để restore bytes có pin; dùng subprocess bytes và đối chiếu SHA trước ghi. Raw không có trong inventory/backup thì báo thiếu và reacquire đúng snapshot theo quyền, không đoán version. Restore không được ghi đè file khác content.

**Kết luận nghiên cứu/decisions/results cần cho coding đã ở data/training/system spec.** Chỉ vào archive khi cần original IDs/full evidence/source media/code/config bytes. Có thể lấy một file text hoặc khôi phục một nhánh; không bung 12.820 file vào active cho mỗi task.

Archive `archive/history-20261010.zip` có manifest original path/size/SHA, content dedup; không dùng Extract-All thông thường để tạo workspace. `common.history` hỗ trợ `list`, `show`, `verify`, `restore`; verify blobs/inventory/path và restore từ chối overwrite khác content. Index `archive/index.json` pin SHA/container/verification. ZIP 2,47 GB trong workspace là readonly hardlink với blob DVC cache: cùng một nội dung local, **không hai bản backup độc lập**; không sửa ZIP/cache trực tiếp. Bản copy riêng tại thư mục backup §8 không dùng hardlink.

Ví dụ tra đúng nhánh evidence, không đọc whole archive:

```powershell
.venv/Scripts/python.exe -m ai_exam_monitoring.common.history list archive/history-20261010.zip --prefix artifacts/reports/pilot-b-v6-source-research-20261007
.venv/Scripts/python.exe -X utf8 -m ai_exam_monitoring.common.history show archive/history-20261010.zip docs/data/fpi-scb-research-20261007.md
```

`show` kiểm file SHA/size và dành cho text nhỏ; binary/JSON lớn dùng restore. Windows có source filenames dài, dùng destination ngắn + extended path:

```powershell
$historyPin = (Get-Content -Raw -Encoding UTF8 archive/index.json | ConvertFrom-Json).bundles[0].sha256
$historyWorkspace = '\\?\' + (Join-Path (Get-Location).Path 'archive/restore')
.venv/Scripts/python.exe -m ai_exam_monitoring.common.history restore archive/history-20261010.zip --destination $historyWorkspace --prefix artifacts/reports/pilot-b-v6-source-research-20261007 --sha256 $historyPin
```

Restore chọn nhánh cho research rồi tạo derivative/version mới theo data spec. Tái lập historical release/run cần dependency closure đủ original paths/source/config/approval/parent, không chỉ report một file. Builder v7 có **self-SHA pin**; evaluator/model run có package-wide code identity. Current source đã retire modules/refactor imports, nên **không dùng current source với hash cũ hoặc sửa pin cho qua**. Snapshot trong archive là source trước lượt active/archive; exact E001–E003 code dùng Git commit/environment trong run evidence (E001: `45240ea`, E002: `0825239`, E003: `4e206a6`) khi cần tái lập.

Ví dụ v7 integrity-only rebuild đã được kiểm byte-exact; chỉ chạy trong workspace riêng khi thực sự cần, output/cache chưa tồn tại:

```powershell
.venv/Scripts/python.exe -m ai_exam_monitoring.common.history restore archive/history-20261010.zip --destination $historyWorkspace --exclude data/processed/pilot-b/pilot-b-20261010-v7 --exclude outputs/pilot-b-v7-release-sources-20261010-r1 --sha256 $historyPin
$env:PYTHONPATH = $historyWorkspace + '\src'
.venv/Scripts/python.exe -X utf8 -m ai_exam_monitoring.data.v7_release_acceptance --workspace $historyWorkspace --config configs/datasets/pilot_b_release_v7.yaml
Remove-Item Env:PYTHONPATH
```

Đã verify archive, restore 10.617 paths và original v7 rebuild 883 file byte-exact; accepted packages/models giữ SHA. Đây là bằng chứng khả năng khôi phục, không yêu cầu rebuild mỗi task. Gỡ workspace restore sau dùng. Nếu mất ZIP nhưng DVC cache còn, `dvc checkout archive/history-20261010.zip.dvc` lấy lại; nếu mất cả binary/cache và chưa remote backup thì Git metadata không khôi phục media.

Cleanup đầu đã xóa unused acquisition/preview/cache/staging và source checkouts: ignored bytes đã xóa không nằm trong archive mới, không hứa restore toàn nguồn. Code/docs tracked lịch sử còn Git `ab34b32`; original cleanup receipt `outputs/cleanup-20261010.json.gz` trong archive, không là media backup. Kiểm manifest inventory/availability trước reuse audit data, không download version khác cùng tên để lấp missing pins.

## 7. Cập nhật spec để task sau không mất context

Mỗi kết quả mới cần ghi vào đúng phần: nguồn/release/QA/group/coverage ở data; run/metrics/error/hypothesis/decision ở training; capability/FR status/gate/contract ở system. Viết **đã làm gì → kết quả gì → quyết định/giới hạn gì → việc tiếp theo** với version/date/owner và evidence location cần thiết. Không chỉ thêm link hoặc giữ proposal pending sau khi đã Accepted.

Khi owner chốt quyết định mới, ghi ID/status/date/scope và nội dung trực tiếp vào spec; Draft tách rõ, config/approval machine-readable pin đúng artifact. Nguyên bản ADR/receipt cũ vẫn traceable nhưng không buộc agent mở lại cả lịch sử. Không tạo thêm ADR/Markdown cho điều chỉnh nhỏ đã có section phù hợp; thêm file chỉ khi nội dung có trách nhiệm độc lập thật sự và user/task cần.

TASK được thay cho task mới, checkpoint gọn sau resume/compaction; không chứa credentials/media/danh tính. Trước kết thúc inspect diff và report checks/limitations. Nếu code/spec/report mâu thuẫn, ghi conflict và hỏi đúng phần cần decision; không thay semantics/metric/test policy âm thầm.

Owner giao task bằng mục tiêu và giới hạn sử dụng, không phải tự chọn module: ví dụ “Bổ sung desk-phone train từ parent v7; tái dùng nghiên cứu; chuẩn bị batch để tôi review; chưa train”. Agent phải chuyển thành inputs/output/acceptance và hỏi đúng scientific decision còn thiếu. Khi hoàn tất, bàn giao behavior/result, checks thực chạy, limitation/next work và commit nếu được yêu cầu; không bắt owner lặp lại toàn bộ AGENTS trong mỗi prompt.

## 8. Audit khả năng tiếp tục sau cleanup — 2026-10-11

Owner yêu cầu khép findings và commit toàn bộ cleanup/handoff; cho phép backup trong thư mục gốc D. Approval này không đổi recipe, labels/splits, test access hoặc mở E004. Bộ bốn spec được giữ; hướng dẫn thực thi được bổ sung trực tiếp ở data §8 và development §4–6.

Bằng chứng audit ban đầu: 114 unit tests PASS; bốn package v4–v7 qua checksum/inventory và codec, số liệu khớp data; 42 run artifacts E001–E003 khớp, gồm ba best.pt; metrics khớp training. Ba Git commit gốc còn; SHA archive khớp index. Sau khôi phục ba dependencies, 709 tracked paths bị loại đều có trong archive hoặc Git ab34b32. Không chạy lại training/inference hoặc rebuild historical release; byte-exact rebuild trong §6 vẫn là evidence của lượt trước.

Kết quả khắc phục:

- **Git/checker:** strict mode kiểm required/managed files nằm trong Git index; archive pointers được registry xác nhận thay vì hard-code một ngày. Tests có untracked source/spec, future bundle, unregistered pointer và binary rejection. Bàn giao dùng staged snapshot sạch và commit theo yêu cầu owner.
- **Backup đã tạo:** `D:/ai-exam-monitoring-backup-20261011`, 1.917 file/2.778.275.362 bytes của processed datasets, outputs, evidence và archive; copy riêng không hardlink, SHA từng file khớp manifest. Git bundle của commit bàn giao được bổ sung sau commit. Đây là bản sao cùng ổ D, bảo vệ sửa/xóa nhầm; không là backup ở ổ/máy độc lập hoặc remote. Không upload thêm.
- **Expansion:** data §8 định tuyến từng bước đến API active hoặc module/commit lịch sử, nêu input/output/checks và giới hạn hard-code; không khôi phục hàng loạt code v7 thành production. Implementation cho release mới vẫn theo scope/approval của task đó; không có shortcut tự ký v8.
- **Tái lập:** §6 liệt kê inputs theo nhu cầu. Ba v5 metadata dependencies đã restore đúng SHA, giữ Git để loader dùng trực tiếp; loader v4/v5/v6 đã verify package thật. Historical model vẫn cần original code identity; không sửa pins để chạy bằng source mới.
- **Vòng đời/quality:** quy định scratch/review/evidence/canonical artifacts và điều kiện dọn; TASK template/AGENTS dẫn tới quy trình. Strict mypy 32 source files và Ruff PASS; typing/optional boundaries đã sửa, CI classifier chạy mypy. Dataset/model/recipe giữ nguyên; unit tests bảo vệ preprocessing, masks, resume và frozen behavior.

Restore drill từ backup đã PASS cho toàn package v7 và artifacts E003, kiểm checksums, không inference. Metadata v5 CRLF được `.gitattributes` giữ exact bytes; checker so SHA cả workspace và Git index để chặn normalization drift. Mypy và full software suite được kiểm trong staged checkout riêng chỉ có Git files, import trực tiếp source của checkout, không dựa dataset/model local.

Khôi phục từ backup: verify SHA trong `backup-manifest.json` trước copy vào workspace mới, không overwrite release khác content; Git source dùng `git clone D:/ai-exam-monitoring-backup-20261011/repository.bundle <new-workspace>`. Copy đúng subtrees `data/processed/pilot-b`, `outputs`, `archive` theo nhu cầu, rồi kiểm checksum package/run; inputs raw lịch sử dùng `common.history restore` và pin archive. `git bundle verify` chỉ kiểm Git, không thay kiểm binary manifest. Backup snapshot mới sau task lớn phải có tên riêng và receipt, không ghi đè bản này.

Sau handoff tiếp tục data/holdout/E004 theo gates đã có, không housekeeping vô hạn. Khi có release/run mới, cập nhật spec, backup snapshot mới có manifest và kiểm restore theo scope; không overwrite backup đã xác minh. Muốn bảo vệ hỏng ổ cần owner chọn ổ/máy khác. Các model-quality/generalization/runtime gates còn mở trong system/training không phải lỗi cleanup được tự động chốt bởi task này.
Final clean staged checkout: 119 unit tests PASS; Ruff/checker PASS; strict mypy 32 files PASS; source import xác nhận từ checkout sạch. Các checks này không thay data/model acceptance.
