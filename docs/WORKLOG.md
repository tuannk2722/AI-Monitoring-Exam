# WORKLOG

## 2026-10-08 — Hoàn tất release v6 theo owner approval

- [Bàn giao v6](../artifacts/reports/pilot-b-v6-release-20261007/README.md), [config accepted](../configs/datasets/pilot_b_release_v6.yaml):317train/50val/11test;378manifest,498ledger,471crop;93review_only27excluded. Owner approve báo cáo expansionR2 ngày2026-10-07; gián đoạn hạn mức auto-review, tiếp tục và hoàn tất ngày2026-10-08, không hỏi lại approval.
- Canonical schema/exporter materialize đúng assignment; evidence nhãn/crop/group/rights/release được gắn approval. Test11 và val13lịch sử, toàn104usedv5 giữ identity/evidence; v5 và proposal bất biến. Unknownmasked; FPI/Discuss không nhập.
- QA pixel/hash/membership/group, publicloader integrity PASS;162tests66.686sPASS, Ruff/Mypy/diff/repo checksPASS. Không train/testinference/upload/commit/push. Pointer local và provenance đã ghi; bước tiếp là experiment config/protocol riêng.


## 2026-10-07 — E002 FINISHED, báo cáo validation và artifact local

- [E002 results](experiments/E002-results.md): codecommit082523947f5bb045622740bf6279fbc44c65130d, git_dirty=false từ checkout outputs/E002-code, exact resolvedconfig/seed/env/data/weights theo approval. Smoke interruptepoch1/resume đến3 PASS; baseline27epoch/earlystop, bestepoch7, routine5.26748s/peak454.13MiB.
- Independent val reload exact scores/metrics. Attempt đầu lỗi default Windows encoding đọc JSON UTF-8 hypothesis, bị approval guard chặn trước output/inference; `python -X utf8` trên cùng code/candidate/config giải quyết, không retrain hoặc sửa code identity. Runbook ghi mode này.
- PrimaryvalBCE0.6333627105 so E0010.5477269888, delta+0.0856357217: H1 chưa được ủng hộ. MacroAP0.980867 so0.927296; lookingF1 tăng0→0.5, phone recall giảm1→4/7/F1 giảm0.933→0.727. Errors/slices/support/constantbaseline báo đầy đủ, không tuning sau run hoặc promotion.
-141tests/0skip, Ruff/compile/pip/repo checks PASS; checkpoint/config/code/data/artifact checksums và val/test preservation kiểm sau chạy. Local DVC pointers baseline/smoke/val/QA, restore37fileSHA từ shared cache vào verificationrepo mới PASS; không remote/fresh-cache roundtrip/upload. Binary/media ignored, chỉ metrics/docs/pointer nhỏ vàoGit.
- Hoàn tất phạm vi E002 smoke/train/validation/report. Test chỉ integrity, không finaltest/model inference trên test/Gitpush/E003; numerical promotion và real-world holdout vẫn mở. Proposal/preparation/package/E001 giữ snapshot lịch sử; checkpoint/index/docs10/22 đồng bộ.

## 2026-10-07 — Owner approve E002, triển khai preservation loader

- Owner review toàn bộ thay đổi/thông số E002.yaml, approve và yêu cầu thực hiện tiếp tới khi hoàn tất. [ADR-015 Accepted](decisions/ADR-015-e002-v5-preservation-linear-probe.md), approval hiện hành và snapshot pending lịch sử; exact config digests không đổi. Phạm vi local CPU/smoke/train/validation, không final test/upload.
- training/data.py hỗ trợ pointer preservation v5 có containment/SHA/owner/parent inline freeze/semantic val-test và manifest-ledger-split consistency; giữ freeze v4/leakage/test guard. Không sửa package accepted hoặc recipe; các runtime functions giữ AST, training module khác giữ normalizedSHA E001.
-23tests targeted và full141tests PASS/0skip, gồm10tamper/regression tests mới. Ruff, pip check, compile/repo/diff PASS. Preflight thật E00184/E002104/smoke104 và approval guards PASS; blocker loader đã giải quyết. QA20croptrain mới giữ ngữ cảnh qua letterbox; media local ignored.
- [Execution evidence](../artifacts/reports/E002-execution-20261007/README.md), [runbook](experiments/E002-runbook.md); đang chốt local commit/clean checkout để smoke/resume và một baseline/val evaluation. Chưa điền metric E002 trước run, không dùng test để tuning.

## 2026-10-07 — Chuẩn bị E002 để owner nghiệm thu

- Theo yêu cầu owner: tạo [config E002](../configs/experiments/E002.yaml) và smoke kỹ thuật3 epoch trỏ accepted Pilot B v5, [protocol](experiments/E002-protocol.md), [bản ghi pending](experiments/E002-approval.json), [báo cáo đề xuất](../artifacts/reports/E002-preparation-20261007/README.md). Không tự phê duyệt experiment hoặc ngoại lệ CPU từ ADR-014 của E001.
- H1 đề xuất: thêm20 train crops, giữ recipe E001, giảm macro masked BCE trên val13 cố định. Chỉ biến dữ liệu thay đổi; chọn raw minimum val BCE, threshold0.5 cố định, AP/F1/confusion/support và baseline prevalence kèm giới hạn source/nhóm. Test11 đã dùng E001 không phải holdout mới; chưa xin quyền final test.
- Audit độc lập PASS: checksum payload v5/v4, schema208/manifest104,197cropSHA, membership80/13/11/93/11,20 train mới, source/crop/geometry/target/mask/group/rights cũ bất biến,24val/testpreserved,0 exact image/crop/group leakage. Local weights và training modules đúng E001 provenance; config digest/bytes/protocol pins trong verification.
- Phát hiện xung đột: loader `verify_dataset` đòi inline test_freeze kiểu E001, v5 accepted dùng preservation pointer; lỗi `KeyError: 'status'` cho cả E002/smoke. Ghi TBD-E002-LOADER và hướng sửa hẹp có verify/tamper/regression; không sửa src hoặc package accepted để ép chạy. Training-ready=false.
-8test sẵn có về schema/mask/metrics/selection/protocol/approval PASS; repository checker PASS. Kiểm văn bản/liên kết/diff ở bàn giao. Approval pending bị trainer từ chối như yêu cầu. Không chạy smoke/train/model inference/test/upload/commit/push; không có metric E002 giả. Checkpoint/index đồng bộ task chuẩn bị; owner nghiệm thu trước phạm vi chạy tiếp theo.

## 2026-10-07 — Release pilot B v5 accepted/local

Owner review/approve proposal v5; [bàn giao](../artifacts/reports/pilot-b-v5-release-20261007/README.md), [config](../configs/datasets/pilot_b_release_v5.yaml). Builder canonical tạo208 ledger,104 manifest(80train/13val/11test),93review_only/11excluded,197crop.19Classroom +RF019 thêmtrain; val/test giữ ID/crop/nhãn/group/freeze cũ. Policy/version metadata thống nhất, source/crop geometry/target/review/rights của208 records giữ nguyên.

Verification PASS: schema/pins/manifest/crop SHA, builder preflight pixel/source,0 leakage image/crop/group qua split,3parent payload bất biến. Test chỉ integrity trong packaging, không inference/tuning. README proposal sửa khoảng trắng được pin bản hiện tại, không ghi đè lịch sử. Không đổi code, không train/upload/commit/push.93 review_only giữ evidence; E002 cần config/protocol riêng.


## 2026-10-07 — Đề xuất v5 sau nghiệm thu staging

Owner approve staging và yêu cầu tiếp tục. Đã đối chiếu208 record,17 group đã duyệt và11 must-link R2 bằng metadata, không mở test pixel/metric. [Báo cáo nghiệm thu](../artifacts/reports/pilot-b-v5-proposal-20261007/README.md) đề nghị80train/13val/11test/93review_only/11excluded: thêm19 Classroom có target biết vàRF-019 nối train cũ. RF-007/009 liên hệ val giữ review_only; các component chưa đủ bằng chứng độc lập không tự vào train.

Verification PASS:208 snapshot giữ nguyên crop/nhãn,20 train mới đủ gate nhãn/quyền/crop,11 must-link không băng split, exact/group/crop không xung đột,3 package parent khớp checksum, val/test bất biến. Snapshot nguồn giữ version riêng từng record, không giả thành package đơn version. Chưa release/train; cần nghiệm thu membership/split/protocol cụ thể mới. Không thay implementation.


## 2026-10-07 — Staging Classroom v2 sau owner nghiệm thu

Owner duyệt24 crop/nhãn và trả lời riêng “Duyệt gộp 150 ảnh thành một nhóm”. Đã ghi approval pin artifact hiện tại, giữ hash README lịch sử (README được sửa khoảng trắng, dữ liệu/nhãn/group/config không đổi). [Bàn giao](../artifacts/reports/classroom-v2-staging-20261007/README.md), [pointer](../configs/datasets/classroom_monitoring_v2_staging.yaml).

Builder canonical xuất24 record/crop review_only; phone6P/10N/8U,looking7P/5N/12U,5 normal/2 co-occurrence/5 fullyunknown. Group CM-V2-SCENE-01 được ghi trên24 record, quyết định nhóm kèm SHA đủ150 ảnh để áp dụng mẫu nhập sau. Chưa split/release/train. Verification PASS: source/label/crop24 đúng hash/pixel, nhãn/mask/schema/pins, nhóm150, v4/R2 bất biến. Không đổi implementation, không upload/commit/push; raw/interim Git ignore.


## 2026-10-07 — Classroom v2 hoàn tất báo cáo nghiệm thu, chưa staging

Owner cung cấp ZIP/version2 và yêu cầu audit → review → báo cáo, dừng trước staging. Đã giữ ZIP raw SHA59e4e301330d75dd77b2540722624c0104178e37ecae03a5d406738c6da9fb90; kiểm303 file giải nén,150 ảnh/750 bbox (120train/600box,30valid/150box), không lỗi cấu trúc hoặc exact byte/pixel duplicate. Số810 từng báo trong hội thoại được sửa thành750 theo inventory.

Đã xem150 ảnh ở mức cảnh,24 crop train ở mức target; đề xuất phone6P/10N/8U, looking7P/5N/12U,5 normal/2 co-occurrence,5 cả hai unknown. Canonical candidate vẫn unknown/mask0. Đề xuất giữ150 ảnh trong một nhóm chống rò rỉ vì cùng phòng và cảnh lặp qua train/valid; không dùng split nguồn làm split độc lập. So với177 ảnh v4/R2 không exact SHA overlap; không suy độc lập từ hash/dHash.

[Báo cáo nghiệm thu](../artifacts/reports/classroom-v2-20261007/README.md), [config pin](../configs/datasets/classroom_monitoring_v2_review.yaml), [verification](../artifacts/reports/classroom-v2-20261007/verification.json) PASS. Audit canonical tái lập,24 crop hash/pixel/geometry/target đúng evidence, v4/R2 payload giữ nguyên; không đổi code, không train/upload/commit/push. Media raw/interim được Git ignore. Chờ nghiệm thu24 proposal và nhóm trước staging, không hỏi lại quyền.


## 2026-10-06 — Hoàn tất staging mở rộng R2

Owner duyệt 72 proposal R2/11 excluded/nhãn-crop/11 liên hệ và xác nhận toàn quyền sử dụng dataset đang dùng. Đã ghi approval theo hash, đóng blocker quyền SCB/RF, không hỏi lại. [Bàn giao](../artifacts/reports/data-expansion-staging-20261006-r2/README.md), [pointer](../configs/datasets/pilot_b_expansion_v5_r2_staging.yaml).

Builder canonical tạo gói riêng 72 record mới, 61 review_only/crop, 11 excluded. 39 mẫu có target biết, 22 cả hai unknown, 13 normal; unknown null/mask0. Verification PASS: 72 nguồn/label/hash, 61 crop pixel/hash, nhãn đúng proposal, 11 quan hệ, pins và parent123 payload files bất biến. Code không đổi sau131 tests/Ruff/repo checker PASS ở R2; diff check PASS. Media được Git ignore, không upload/commit/push. Chưa split/release/training. Classroom-monitoring dừng đúng phạm vi metadata của đợt này; nhập nguồn là bước tiếp theo khi có version/unit/group.


## 2026-10-06 — Tuyển và review mở rộng R2 sau owner approve tiếp tục

- Lưu continuation-approval.json, giữ snapshot draft/approval trước. Triển khai canonical pilot_expansion.py, tái sử dụng selector/dHash/parser/payload verifier; selector hỗ trợ explicit RF train/images/ và chặn val/test.
- Kiểm source/archive/audit pins; từ pool strict train mới3.801SCB/2.502RF chọn48/24 ảnh bằng dHash diversity và anchor lớn nhất, không dùng metrics/test media. Budget chỉ là proposal review, không quota release.
- Review local72 source/crops; đề xuất SCB phone0P18N30U,looking18P11N19U; RF phone1P5N18U,looking5P3N16U. Tất cả canonical target mới vẫn unknown/mask0; chưa nhập proposal thành approved.
- Đề xuất giữ61/loại11 anchor, tạo2 crop RF theo người/context và11 must-link cảnh; bổ sung triage28review_only cũ. Không khẳng định ảnh khác SHA hoặc dHash xa là cảnh độc lập.
- [Báo cáo R2](../artifacts/reports/data-expansion-20261006-r2/README.md), [pointer R2](../configs/datasets/pilot_b_expansion_v5_r2_draft.yaml); chưa split/release/train. Classroom-monitoring chờ owner cung cấp thông tin quyền/provenance đã hứa; không tải media mới.
-131 tests PASS, Ruff toàn src/tests/scripts PASS, repo checker failures=0 ở lượt triển khai. Lượt chốt bị gián đoạn vì automatic approval review hết hạn mức; user resume, công cụ hoạt động lại. Sửa mô tả bị lỗi encoding bằng UTF-8, lưu config thực thi cũ/hash trong encoding-repair.json, không sửa dữ liệu/crop/target/thuật toán.
- Verification cuối và giới hạn trong report R2; index/checkpoint/kế hoạch được đồng bộ. Approval R2 và bằng chứng nguồn còn chờ, không coi user review thay đổi trước R2 là approval nhãn/crop/group vừa tạo.

## 2026-10-06 — Owner duyệt hướng mở rộng, thẩm định metadata và draft v5

- Ghi [approval](../artifacts/reports/data-expansion-20261006/owner-approval.json) đúng bốn lựa chọn owner; cập nhật kế hoạch/index/checkpoint. Giữ semantics và mask unknown.
- Đính chính ghi chú thiếu archive trước đây: SCB Head/HRW và RF v1 đều hiện diện ở đường dẫn đã pin, cả ba SHA khớp. Sửa lỗi cộng số SCB review-only trong kế hoạch: 23, không phải 16.
- Tạo [batch khởi đầu](../artifacts/reports/data-expansion-20261006/candidate-batch-v5-draft.json) từ đúng 28 review-only (23 SCB + 5 RF); kiểm image/label ZIP và crop local 28/28 PASS, không xem ảnh test. 0 media candidate mới, group/near-duplicate vẫn pending.
- Tạo [pointer v5 Draft](../configs/datasets/pilot_b_expansion_v5_draft.yaml) pin parent/approval/batch; split_version=null, training_eligible=false, chưa package/DVC release.
- [Thẩm định metadata](../artifacts/reports/data-expansion-20261006/classroom-monitoring-metadata-review.json): đọc claim project, chưa đọc được version; quyền/provenance/consent/group còn TBD. Chưa tải nguồn mới hoặc gửi liên hệ.
- [Báo cáo và validation](../artifacts/reports/data-expansion-20261006/README.md) phân biệt approval hướng và release. Shortlist mới ngoài ledger, group/split/release và thẩm định nguồn chưa hoàn tất; không train E002.

## 2026-10-06 — Kiểm kê và đề xuất mở rộng dữ liệu

- Đọc v4 bằng parser canonical: 112 ledger, 84 usage (60/13/11), 28 review-only, 105 ảnh nguồn/112 crop và 16 leakage group; tổng/source/split/target khớp `reports/coverage.json`.
- Tạo [inventory metadata](../artifacts/reports/data-expansion-20261006/inventory.json), [queue 28 hồ sơ review-only](../artifacts/reports/data-expansion-20261006/review-queue.json) và [sàng lọc nguồn](../artifacts/reports/data-expansion-20261006/source-research.json). Hash config, approval, manifest, ledger và payload checksum list được pin trong evidence.
- Báo cáo [đề xuất mở rộng](data/data-expansion-20261006.md) khuyến nghị cả nguồn hiện có lẫn nguồn behavior mới; không đặt quota, đổi nhãn/split, tạo version/pointer hoặc train. Không tải/upload media.
- Kiểm tra parser 112/84 PASS; payload v4 vẫn có checksum `dbc1bf90a5605cac39b5c96503e71097ecd1eaab5b35e14f311f966edd503f53`. Giới hạn: archive SCB gốc không có tại path đã pin nên chưa đếm shortlist chưa dùng; nguồn mới chưa audit archive/quyền theo từng asset; 28 review-only chưa có group.
- Xác minh queue JSON khớp chính xác 28 ID canonical và mọi record tiếp tục `training_eligible=false`, chưa có group. Ruff, `check_repo.py --require-git`, UTF-8, link mới và `git diff --check` PASS. Hai link lịch sử tới file review owner đã xóa giữ nguyên; test suite không chạy vì không có code nghiệp vụ/model thay đổi.
- Script từ chối chạy nếu config `accepted`, owner approval, verification report và payload checksum của v4 không khớp hash/pin lẫn nhau.

## 2026-10-06 — E001 implemented and executed locally

- Owner approved the complete training-readiness proposal. ADR014/config/approval pin frozen ResNet18 IMAGENET1K_V1, masked macro BCE, seed42, CPU local; no dataset mutation/cloud upload. Implementation commit45240ea6234c70a80ecf3dc11f2e69eb8e253a53; clean isolated checkout and fresh pinned CPU environment. 126 tests, pip check, lint/compile/repo checks PASS; user deletion of old codebase review preserved.
- Actual smoke interrupted at epoch1 and resumed unchanged to3; checkpoint recovery PASS. Full E001 early stopped at32; best epoch12, validation loss0.54772699, measured routine5.827s/peakRSS470712320bytes. Independent checkpoint reload reproduced validation predictions/metrics exactly.
- Candidate/protocol frozen in84d4cf0d51564af971851e72cf4e37e3afe59fa4 before one final test evaluation. No model/threshold changes afterward. At0.5 val/test phone false positives on all known negatives; looking recall0. AP high on tiny/source-confounded support does not establish quality. Recommend continue data research, no promotion claim; owner remains reviewer.
- E001/smoke/final-test/pretrained pointers and local DVC cache created;38 files restored from cache to a fresh folder and all MD5/SHA verified. No remote push or Git push. V4 payload/test freeze unchanged; model artifacts are local-only. Detailed evidence: [results](experiments/E001-results.md), artifacts/reports/E001.

## 2026-10-05 — Hoàn tất bàn giao pilot B v4 và closeout codebase

- Commit implementation/cleanup `97b90ebfe0e8f5457ac5c783205c98be02925866`; test portability fix `d99d1f5c08be467e05f6c7ee27dba8138bc779a5`. Clone cuối checkout đúng d99d1f5 bằng `git clone --no-hardlinks`; trước pull xác nhận `.dvc/cache` riêng mới rỗng và dataset chưa có. Auth copy vào config.local ignored; không đổi Drive ACL hoặc publish Git remote.
- Upload targeted v4 **125 files pushed**; fresh-cache pull tại cả 97b90eb và d99d1f5 **125 files fetched and 124 files added**. Full 124-file inventory/byte SHA, schema/usage/group gates, 14 code/config/approval pins, 112 ledger/84 manifest (60/13/11), original frozen split/test attestation PASS; `dvc status` up to date. Payload list SHA `dbc1bf90a5605cac39b5c96503e71097ecd1eaab5b35e14f311f966edd503f53`; Git pointer SHA `f9f249f1f7bee62690e24f8bb437952c855866c9f7828da5af195d8c770564ef`; MD5 directory `563958778204fa60d6015656595c19dd.dir`. Producer/config/approval/payload không sửa bytes.
- Clean-checkout imports lấy cloned src, không dùng editable code gốc; 109 tests, Ruff, compileall và repo checker PASS. Hai tests không còn cần ignored outputs/ tồn tại; thư mục đó vẫn absent sau tests. Clone Git clean sau pull/checks. Môi trường Python tái sử dụng .venv gốc; không tuyên bố fresh dependency installation hoặc remote Linux CI đã chạy.
- Đã dọn 7 checksum-identical rebuild copies (~262.8 MB); clone round-trip/copy credential/cache thử được dọn sau verify. Giữ canonical parents, raw/extracted sources và historical evidence đang được pin; không GC cache gốc/remote hoặc rewrite Git history. Current docs đồng bộ S8 PASS, P3 classifier config/trainer và S9 runtime crop pending. Closeout commit chỉ đổi docs/checkpoint, giữ pointer và producer/config/approval blobs nguyên như tested commit.
- Task handoff/cleanup hoàn tất; next task là draft E001 reviewed-crop classifier config để owner chốt model/weights/license/loss/transforms/hyperparameters rồi triển khai masked loader/train/eval. Không mở lại review dataset hoặc tạo web tool; không train/Git push trong task này. Git clean là tiêu chí cuối sau commit closeout.

## 2026-10-05 — Round-trip v4 đạt; sửa test setup cho clean checkout

- Implementation + pointer + scope/docs + smoke cleanup đã commit tại `97b90ebfe0e8f5457ac5c783205c98be02925866`; staged checker/14 SHA-pinned blob checks PASS, Git sạch sau commit. Targeted `dvc push data/processed/pilot-b/pilot-b-20261005-v4.dvc -r teamdrive` thành công: **125 files pushed** (124 payload files + directory object).
- Clone `--no-hardlinks` checkout chính xác commit trên tại `outputs/pilot-b-dvc-roundtrip-20261005-v4`; `.dvc/cache` riêng mới rỗng, khác cache gốc, dataset chưa tồn tại trước pull. Credential copy chỉ vào ignored `.dvc/config.local`. `dvc pull` thành công: **125 files fetched and 124 files added**. Full inventory/checksums, schema/usage, config/approval/8 producer SHA, split và test freeze PASS; restored Git clean và `dvc status` up to date. Payload list SHA vẫn `dbc1bf90a5605cac39b5c96503e71097ecd1eaab5b35e14f311f966edd503f53`.
- Chạy tests bằng cloned `src` phát hiện 2 lỗi setup: `TemporaryDirectory(dir=workspace / "outputs")` giả định ignored directory có sẵn. Sửa hai tests tạo temporary directory trực tiếp dưới workspace (để inputs vẫn workspace-relative); tự cleanup, không đổi producer/data/config/approval bytes. Đây là lỗi portability của tests, không phải payload/Drive lỗi. Commit bản sửa, kiểm clone/cache mới tại commit có tests đã sửa, rồi ghi closeout cuối.
- Lượt trước gián đoạn do auto-review hết usage, không có kết luận unsafe action; resume đã khôi phục tool access. Không bypass approval hoặc cần quyết định owner mới.

## 2026-10-05 — Chốt implementation và scope bàn giao DVC v4

- Owner yêu cầu sửa checker/docs, commit implementation đã duyệt + smoke cleanup, hoàn tất Drive push/pull đúng version từ checkout/cache sạch và để Git sạch. Authorization: “Hoàn tất bàn giao qua Drive: chốt scope upload v4, rồi push/pull đúng version từ checkout/cache sạch.” Chỉ lưu/khôi phục đúng immutable v4 trên `teamdrive` hiện có phục vụ local_classifier_research; không raw/history uploads, redistribution, W&B media, share quyền mới hoặc training. Quyết định storage bổ sung nằm ngoài payload/approval local đã pin.
- Drive ACL kiểm qua PyDrive2 API: folder hợp lệ, không trashed; đúng một permission user/owner, không public/domain/group. Không lưu email/token trong report hoặc thay ACL. Owner quản lý bản lưu/quyền/xóa khi không còn sử dụng; policy thu thập người thật mới vẫn theo ADR-010/21.
- Checker chỉ cho phép pointer `.dvc` và `.gitignore` bên dưới data/raw/interim/processed; vẫn chặn media, payload JSONL, secrets, cache/venv/model metadata. Mở rộng test safe nested pointer và regression forbidden paths. Đồng bộ README/index/architecture/P0/P1/P2/P3/environment/runbook/current source card; không thay config đã pin, immutable payload hoặc evidence lịch sử. Làm rõ restore DVC vs replay producer ở commit/environment khác.
- `core.autocrlf=true` có thể đổi SHA input khi stage/checkout: receipt release approval hiện dùng CRLF, code/config pilot dùng LF. Thêm `.gitattributes`: giữ exact bytes reports bằng `-text`, LF cho pilot code/config và DVC pointers; không sửa receipt đã pin. Kiểm staged blob và clean-clone bytes với các SHA canonical là gate bàn giao.
- Dọn đúng 7 ignored rebuild copies, full inventory/checksum identical với bản canonical tương ứng: owner-groups v2, preparation r3/r5, approved v3, release v4, release proposal v2, SCB proposals v2 (khoảng 262.8 MB). Không có config/src tham chiếu các target; mọi absolute path nằm dưới outputs và không reparse points. Giữ canonical parents, extracted build inputs, historical review evidence. Các đường dẫn rebuild trong report cũ ghi thao tác lịch sử đã hoàn tất; bản sao thử đã xóa.
- Tiếp theo: kiểm v4/pins/pixels và staged source/docs/config/evidence/pointer; targeted push trước publish pointer, commit local implementation, exact-commit fresh independent cache pull, đối chiếu full payload/schema/freeze rồi ghi evidence và commit closeout. Không Git push hoặc train trong task này.

## 2026-10-05 — Rà soát codebase và thứ tự công việc tiếp theo

- Task phân tích theo yêu cầu owner; không triển khai trainer, chọn model/config, sửa dataset, xóa thêm artifact, commit/push hoặc upload. Đọc index/checkpoint, các ADR Accepted liên quan, docs kiến trúc/P0/P2/P3/experiment/governance/testing/contracts, contract/runbook và source/tests/configs/CI/DVC hiện hành.
- HEAD `d8599b588140d4847a8e1a07878274e4d6cb87c3` chỉ chứa bước setup/smoke DVC. Cả 8 module pilot, 7 test files, 6 configs và evidence release mới vẫn untracked; các thay đổi docs và cleanup smoke chưa commit. Git index trống staging. Clone HEAD hiện tại chưa có implementation pilot để dùng/tái tạo release.
- Xác minh read-only actual v4: payload/inventory, schema/usage/group gates, config/approval/producer pins và test freeze PASS; checksum list vẫn `dbc1bf90a5605cac39b5c96503e71097ecd1eaab5b35e14f311f966edd503f53`. Recompute proposal/approval từ parent + pinned batch/report cho đúng cả 112 record canonical. Preflight nguồn/crop trên 105 source images kiểm image/label/crop hashes, dimensions, crop pixels PASS. 84 manifest = 60 train/13 val/11 test; 28 review_only; 16 nhóm. `dvc status` pointer v4 local PASS; không kiểm hoặc upload v4 remote.
- Check hiện tại PASS: 108 unittest, Ruff `src tests scripts`, compileall, `pip check`, repository checker trên Git index. Direct probe phát hiện `scripts/check_repo.py:30–42` cấm cả `.dvc` và `.gitignore` trong `data/processed`; khi stage pointer v4 sẽ fail. Checker PASS hiện tại không bao gồm files untracked, không chứng minh commit release sắp tới hợp lệ. Cần ngoại lệ metadata DVC có phạm vi hẹp + regression test, vẫn chặn media/credential.
- ML chưa triển khai: `validate_training_config` chủ động từ chối B; train/evaluate và `dvc.yaml` còn YOLO detection legacy. Baseline config là scaffold pending/TBD; môi trường chưa có torch/ultralytics/OpenCV. Không chạy `dvc repro` hoặc legacy train để báo baseline B. S9 runtime crop là gate trước end-to-end; không chặn chuẩn bị experiment classifier trên reviewed crops đã accepted.
- Current docs còn trạng thái cũ: README/architecture mô tả release chưa accepted/freeze; P2/P3/runbook/dataset research còn “DVC chưa cài/pointer” hoặc masked supervision chưa chọn. Đồng bộ tài liệu hiện hành theo bằng chứng mới, giữ nguyên report/config/approval đã pin. Rebuild CLI lấy Git/environment hiện tại; sau đổi HEAD, `release.json`/freeze Git metadata và payload checksum sẽ khác dù manifest/split/crops vẫn nguyên. Cần phân biệt lấy lại package immutable bằng DVC với dựng lại từ nguồn; không overwrite v4 hoặc hứa checksum toàn payload identical qua commit/environment khác.
- 8 module pilot phục vụ schema/validator/packager và lineage được pin, không phải web tools; không xóa gộp trong task phân tích. `outputs/` khoảng 1.87 GB chủ yếu extracted sources/audit; `data/processed/pilot-b/` khoảng 492 MB gồm các snapshots, trong đó v4 chỉ khoảng 5.37 MB. Một số nguồn đang ở ignored outputs là input build; muốn dọn tiếp phải kiểm tham chiếu/pins và phân biệt bản rebuild dư với cha/evidence cần giữ.
- Thứ tự đề nghị: (1) sửa gate Git metadata DVC, đồng bộ current-status docs và làm rõ cách tái lập, commit phần release đã duyệt + cleanup, kiểm đúng staged contents/CI; (2) chốt scope upload nếu muốn kết thúc P2 remote, targeted v4 push/pull qua exact commit + cache sạch, hoặc giữ training local; (3) một draft E001 reviewed-crop classifier với model/weights/license, loss normalization, transforms, seed/hyperparameters, validation/metric protocol để owner nghiệm thu; (4) loader manifest/mask + trainer/evaluator B tối thiểu, run contract/checkpoint/interruption, train/val và evaluation test cuối theo freeze. Không mở lại review 84 crops/14 groups, không thêm web/tracking/events trước baseline.
- Giới hạn pilot: phone positives ở RF, negatives ở SCB; val có 1 phone negative, test chỉ 4 phone labels known. Không có model metrics/holdout/generalization claim; green data tests không phải training acceptance. Chưa xác minh CI Linux/clean Python installation hoặc full-source rebuild ở HEAD hiện tại. Ghi kết quả vào WORKLOG/TASK hiện có, không sinh report/module mới.

## 2026-10-05 — DVC smoke push/pull đạt; dọn artifact thử nghiệm local

- Owner báo `Authentication successful`, `2 files pushed`; clone mới tại `outputs/dvc-smoke-roundtrip-v1` checkout đúng commit `d8599b588140d4847a8e1a07878274e4d6cb87c3`, cache riêng mới tại `.dvc/cache` của clone, pull `data/dvc-smoke-v1.dvc` từ remote `teamdrive`: `2 files fetched and 1 file added`.
- Đối chiếu thực tế trước dọn: root/clone cùng commit; clone không có tracked modifications; pointer cùng SHA-256 `7e18cc31ac6c4f738303105c599ab2c6a10fdb6f87a8b514600ec3e79bde9fea`; probe gốc và tải về cùng SHA-256 `8b310e5da1456915de69006a6d3be6492449844db37e862481dce0d434a5d742`. Đây là bằng chứng smoke round-trip, dùng môi trường Python gốc đã sửa và cache mới, không phải kiểm tra cài môi trường Python mới.
- Theo yêu cầu owner dọn codebase: bỏ fixture `data/dvc-smoke-v1`, pointer `data/dvc-smoke-v1.dvc`, `data/.gitignore` chỉ chứa rule fixture, clone thử nghiệm và `.gitignore_test` nháp rule DVC. Xóa đúng hai cache objects fixture: MD5 file `e085042316f680509943eea46bed437e`, directory `9231bff947aa9109343947eb3cf6c523.dir`; preflight xác nhận không được cached directory khác tham chiếu.
- Giữ cấu hình DVC/OAuth local, dependency fix, dataset/cache/pointer v4 và bằng chứng release. Xóa local không rewrite commit lịch sử hoặc xóa objects trên Drive; không commit/push trong task dọn.
- Sau dọn PASS: cả bảy target không còn; hash cấu hình/OAuth/dependency/pointer v4 giữ nguyên; full v4 `verify_payload` và `dvc status` đạt; không còn fixture cache references; credential vẫn Git ignored; diff check và repository checker (Git index, không bao gồm untracked) đạt. Gate smoke storage đã đạt; remote release v4/media upload và baseline training chưa được hoàn tất hoặc mở scope bởi phép thử này.

## 2026-10-05 — Sửa dependency DVC Google Drive gây lỗi GEN_EMAIL

- Tái hiện lỗi import `pydrive2.auth`: `pyOpenSSL 22.0.0` + `cryptography 50.0.2` lỗi tại `OpenSSL.crypto.X509Extension`. `pip check` vẫn PASS vì metadata bản pyOpenSSL cũ thiếu giới hạn trên; kiểm tra import thực tế là bắt buộc cho lỗi này.
- Ghim `pyOpenSSL==24.2.1` trong optional dependency `dvc` của `pyproject.toml`, phù hợp [PyDrive2 1.21.2](https://github.com/iterative/PyDrive2/blob/1.21.2/setup.py). [pyOpenSSL 24.2.1](https://github.com/pyca/pyopenssl/blob/24.2.1/setup.py) yêu cầu `cryptography>=41.0.5,<44`.
- Chạy `.venv/Scripts/python.exe -m pip install -r requirements/dvc.txt`: pyOpenSSL 24.2.1, cryptography 43.0.3; resolver đồng bộ asyncssh 2.24.1 → 2.23.1. Không sửa logic ML hoặc thêm module.
- PASS: `pip check`, fresh-process imports OpenSSL/PyDrive2/DVC gdrive/asyncssh, TOML/pin validation, local smoke `dvc status`, scoped diff checks. SHA-256 probe giữ `8b310e5da1456915de69006a6d3be6492449844db37e862481dce0d434a5d742`; checksum list v4 giữ `dbc1bf90a5605cac39b5c96503e71097ecd1eaab5b35e14f311f966edd503f53`.
- DVC/pointer/remote local đã tồn tại, thay cho trạng thái chưa cài của checkpoint release trước. Không chạy push/authentication, không upload fixture/media, không commit trong lượt sửa này. Owner tiếp tục smoke push; OAuth client riêng và clean-clone/cache pull vẫn là các bước cần hoàn tất trước gate remote.

## 2026-10-05 — Owner approve phương án release, hoàn tất pilot B local v4

Owner trả lời “approve phương án release pilot B”, yêu cầu thực hiện đến khi xong hoặc có quyết định mới. Lưu nguyên thông điệp UTF-8 vàpin report/config/proposal/assignment ở `artifacts/reports/pilot-b-release-acceptance-20261005/owner-approval.json`. Không hỏi lại các approval đã có. Scope gồm9 phone/context reviews,16 conservative components/boundaries,schema/config/explicit split/local research vàtest freeze; không mở runtime/model/upload.

Mở rộng `pilot_release_proposals` với `--accept-release`, dùng schema/packager hiện có; không thêm module src, frontend hoặc dependency. New canonical `data/processed/pilot-b/pilot-b-20261005-v4`, config `pilot_b_release_v4.yaml`,statusaccepted/local_classifier_research. Giữ112ledger/crop bytes/source/looking/RF approvals và84 selection;84 usage records60train/13val/11test,28group-unresolved review_only. Phone24P9N79U,looking33P56N23U,9normal;used84 phone20P8N56U,looking22P43N19U,8normal. Giữ14 must-links trong16 reviewed groups;metadata session/room/person/video null,không random crop/singleton independence/refill.

Freeze attestation trong release.json pin11 test IDs,owner/time/protocol/config/Git,manifest/split/test-subset SHA;serializer-exact assertions pass. PayloadSHA `dbc1bf90a5605cac39b5c96503e71097ecd1eaab5b35e14f311f966edd503f53`. Fresh-process/destination rebuild identical;108 tests,Ruff,compileall,repo/diff/link/UTF-8/media QA pass. Từngrecord đối chiếu exact approved proposal,parent unchanged,pixels/preflight,masks/normal/scope/must-link/leakage/freeze/producer hashes pass. Git dirty vàimplementation SHA ghi trung thực;không commit thêm trong lượt này.

[Báo cáo release](../artifacts/reports/pilot-b-release-acceptance-20261005/README.md) ghi counts/usage/rebuild/limitations. DVC chưa cài/pointer/remote round-trip; scope local không cho upload nên S8 remote/P0/P2 DVC gates vẫn mở. S9 runtime crop làtask riêng. Đóng task packaging local, không tuyên bố toànmilestone P0/P1/P2/model generalization. Không train/upload;28review-only không vào manifest train/eval.

## 2026-10-05 — QA và phương án release hữu hạn, chờ nghiệm thu

User yêu cầu tiếp tục. Visual QA local88 phone-unknown crops và105 source images;9 crop có tay/bút/sách/bàn rõ được đề xuất phone negative + confirmed_working,79 unknown giữ nguyên. Không suy absence từ source class. Crop/looking/RF approvals đã duyệt không đổi. Canonical vẫn v3/review_only/split=null.

Draft release `pilot-b-release-proposal-20261005-v2`: giữ14 owner must-links, gộp3 cụm blue/purple nghi liên quan và thêm các liên kết thị giác hữu hạn;16 nhóm84 records dự kiến60train/13val/11test,28 chưa đủ group evidence review_only. Seed null, explicit whole-group assignment,70/15/15 chỉ mục tiêu mềm. Test/scope/schema/config/boundaries chưa accepted. Phone dự kiến24P/9N/79U,looking33P/56N/23U,9normal; val/test support nhỏ và nguồn phone bị confounding, không có model metrics/generalization claim.

Một CLI report-only + config +2 tests về unknown/hash/must-link/leakage; không web/model/dependency mới. [Báo cáo nghiệm thu](../artifacts/reports/pilot-b-release-proposal-20261005/README.md) và verification pin parent/config/assignment/payload;105 tests,Ruff,compileall,repo/diff checks PASS, rebuild identical,canonical v3 payload unchanged. Chờ một quyết định owner high-level cho toàn phương án hoặc ID ngoại lệ rồi mới build canonical release/freeze; không mở lại84 crops/14 must-links. Không train/upload/commit thêm.

## 2026-10-05 — Owner approve SCB batch, nhập canonical v3

User trả lời `approve` cho batch đã bàn giao, không có ngoại lệ. Lưu owner message/role/date cùng exact batch/proposal SHA ở `artifacts/reports/pilot-b-scb-acceptance-20261005/owner-approval.json`. Import qua CLI hiện có sang `data/processed/pilot-b/pilot-b-20261005-v3/`; config derivation `pilot_b_approved_v3.yaml`. Cả112 crop reviewed;84 looking approvals mới gắn đúng crop SHA, giữ RF28/phone unknown/context unknown/group/rights/split. Không coi approval batch là group independence, split, runtime hoặc training release approval.

Tổng looking33P/56N/23U;phone24P/0N/88U;113 known entries,111 partial,1 co-occurrence,0 normal. Scope source-anchor geometry/label acceptance hữu hạn, không map toàn nguồn. Actual package/rebuild checksum và validation ở report acceptance; remaining gates vẫn giữ review_only/null split.

## 2026-10-05 — Bỏ manual web tool, tự động SCB proposals

Theo yêu cầu owner, bỏ crop editor/importer/HTML template, group-page generator và các tests chỉ phục vụ tool; bỏ HTML assets/API option khỏi packager và package-data entry. Giữ selector/input pins/schema/packager/group importer cùng evidence 14 quyết định đã duyệt. Không thay đổi AGENTS do owner vừa bổ sung.

Thêm một CLI/config nhỏ tạo đúng 84 crop từ source bbox và nhãn đề xuất theo metadata, gộp 28 RF crop nguyên bytes. Output hiện hành: `data/interim/pilot-b/pilot-b-scb-proposals-20261005-v2/`; owner review qua báo cáo/static PNG/CSV, không vẽ hoặc export crop thủ công. Proposed looking28P/56N; phone/normal84U; canonical ledger vẫn nguyên v2/review_only/null split. Sáu trường hợp cần chú ý được ghi theo ID. Chưa ký release hoặc train; docs/runbook/checkpoint chuyển sang nghiệm thu high-level. Những ghi chép UI dưới đây là lịch sử, không phải workflow hiện hành.

## 2026-10-05 — Nhập owner group review và chuẩn bị crop QA

Đã xác minh JSON owner gửi từ Downloads, lưu nguyên bytes/evidence và nhập 14 keep_together vào version mới `data/processed/pilot-b/pilot-b-20261005-v2`. 70 records/64 ảnh thuộc 14 nhóm; 42 records/41 ảnh chưa gán nhóm. Không suy session hoặc độc lập giữa nhóm; không chia split. Crop/target RF giữ nguyên, 84 SCB chưa được duyệt.

Thêm importer group, công cụ review crop thủ công (RF chỉ đọc), config revision pin cha và tests. Trang owner: `outputs/pilot-b-crop-review-20261005-v1/index.html`. PASS 105 tests, Ruff, compileall, repo checker, diff check và JavaScript syntax. Rebuild khớp toàn bộ payload; evidence `artifacts/reports/pilot-b-owner-groups-20261005-v1/verification.json`. Chưa có browser visual QA, training hoặc release. Task tiếp tục chờ crop/target review và các gate còn lại theo contract; không yêu cầu owner review lại 14 quyết định đã gửi.

## 2026-10-05 — Triển khai preparation pilot B, chờ owner review

- Theo user, đã commit thiết kế `1f7757bfee5a20dad393ba80064769851e5ccd6a`, mở branch `data/pilot-b-preparation` rồi triển khai; chưa commit implementation hoặc push. User xác nhận không có metadata và yêu cầu chuẩn bị cụm ảnh review. Không mở lại quyền SCB/RF approvals/A–B.
- Pin ZIP/audit/review/config; kiểm extracted source image/label bytes với archive. Freeze deterministic 84 SCB anchors train strict-valid (28 TurnHead/28 read/28 write), không refill/transfer. Ledger nhập đúng 28 RF crops/21 ảnh và giữ nguyên bytes/geometry/known approval/27 partial targets. Source annotations không tự thành target hoặc person bbox.
- Thêm config B preparation-only, structured schema/codec/validator, selector, input CLI, preparation CLI, exporter và group-review CLI trong src. Source/crop hashes/dimensions/pixel equality, target mask/null/normal, identity/path/scope/group/split/test/release gates có tests. Sửa importer reject invalid RF state và đối chiếu label bytes ZIP trước ghi label SHA. Build provenance ghi Git dirty/code SHA/environment, không giả design commit chứa implementation chưa commit.
- Preparation pointer hiện hành `data/processed/pilot-b/pilot-b-20261004-v1-preparation-r5/`: 112 review-only records, 28 reviewed PNG, SCB 84 crop/target pending; không manifest train hoặc split assignment. Input version/SHA/membership giữ nguyên; revisions trước không overwrite. Staging còn thiếu negatives/normal đã duyệt. CLI từ chối config formulation/status/target encoding không được hỗ trợ thay vì bỏ qua field.
- Đã xem scene thumbnails toàn bộ 105 ảnh qua 9 contact sheets; chuẩn bị 14 scene proposals (pending owner) và 238 nearest relation pairs, gồm cross-source retrieval. Owner review ở `outputs/pilot-b-group-review-20261005-v3/index.html`, có export draft cục bộ. User chưa hiểu câu hỏi nhóm; đã giải thích bằng hai ảnh minh họa và đổi UI sang tiếng Việt/từng nhóm với lựa chọn Giữ chung/Cần sửa/Chưa rõ. Chưa có owner approval. Đây là scene relation inspection, không phải review crop/targets SCB hoặc proof session/independence. Hai góc dark-side/curtain-landscape có possible linkage được ghi rõ.
- Validation PASS: 99 unittest, Ruff, compileall, repository checker; actual staging/rebuild cùng 150 payload SHA, checksum list SHA `c41bace184a46f06b6326e2be4d4792ea4016c00c8eeec4398e97033f32c7c67`. Review bundle 120 payload hash pass. Verification/scene proposals media-free trong `artifacts/reports/pilot-b-preparation-20261005/`; runbook/docs/contracts đồng bộ. JavaScript syntax/navigation/draft export PASS qua software fixture, không lưu quyết định giả. Browser preview thất bại hai lần do sandbox helper nên chưa có screenshot QA. Diff/UTF-8/whitespace/55+ local links và untracked media-path safety đã kiểm.
- Owner review pending: selection/schema/config; SCB visible-person/context và target known/unknown/excluded; evidence leakage groups; actual coverage rồi split ratio/seed/assignment/test freeze; use scope/release/DVC. User trả lời chưa hiểu group question; đó không phải approval hoặc thay policy. Không train/upload hoặc đóng S4–S8/P0/P1/P2. Crop runtime S9 giữ riêng.
- Resume checkpoint cập nhật, sửa lỗi Unicode bằng native UTF-8 write. Agents phụ dừng do usage limit; root hoàn thiện phần độc lập. Sandbox setup lỗi; workspace fallback require_escalated đã auto-review cho phép, không có rejection. TASK không biến staging/proposals/câu hỏi thành approval.

## 2026-10-04 — Thiết kế hợp đồng release pilot B

- Owner chốt chỉ thiết kế, triển khai dataset ở task sau; 84 SCB candidates (28 TurnHead/28 read/28 write) + exact 28 RF approved crops; positive/negative/unknown với masked supervision. Budget không phải số crop training hoặc acceptance metric.
- Owner chốt package reviewed-context crops, runtime crop gate riêng trước baseline B end-to-end; group evidence trước train/val/test freeze, thiếu group giữ split=null/review_only và chặn release training. Quyết định lưu ADR-013; không hỏi lại A/B/quyền SCB/R1–R3.
- Hợp đồng canonical `docs/data/pilot-b-release-contract-v1.md`: RF membership 28 ID/target states, SCB deterministic selection rule chưa chạy, schema/codec thiết kế, eligibility, crop/split policy, DoD, TBD có owner và backlog S1–S9 hữu hạn.
- Tạo `.codex/TASK.md` và rule checkpoint trong AGENTS; đồng bộ guidelines/task template/index. TASK là bộ nhớ điều phối sau resume/compaction, không thay ADR/spec/config hoặc biến câu hỏi thành approval.
- Đồng bộ dataset research/P2/doc25/label-split specs/ghi chú ADR-012. Không sửa src/config/media/raw, không trích xuất/select SCB, build/train/upload/commit hoặc accepted dataset. P0/P1/P2 còn mở.
- Validation PASS: inspect diff, `git diff --check` theo Git config repository, `.venv/Scripts/python.exe scripts/check_repo.py --require-git` (failures=0), check local links/whitespace toàn 15 Markdown files gồm untracked (60 link cuối), RF exact 28-ID/target table khớp review bundle và backlog S1–S9. Inventory strict train: Head ID1 1.576, HRW read 2.708, write 1.103 ảnh; chưa chọn/relabel và không coi các ảnh là nhóm độc lập. Không cần rerun ML tests cho docs-only.
- Task thiết kế Done; dependency triển khai/TBD còn ở contract, P0/P1/P2 chưa đóng. Shell sandbox lỗi `setup refresh`, read-only check chạy được qua execution fallback được auto-review cho phép; không có action bị auto-review từ chối. Chưa commit/push.
- Closeout 2026-10-04: owner đã review thay đổi và yêu cầu hoàn thiện nếu không cần quyết định mới. Không có blocker của task thiết kế; ghi nhận bàn giao Done, giữ TBD cho task triển khai và bản AGENTS owner đã rút gọn. Kiểm lại diff/repository checker PASS; không bắt đầu build dataset hoặc train trong closeout.

## 2026-10-04 — Consolidate Dataset Audit & Spec theo B

- Dừng review ảnh nhỏ lẻ theo owner. Không đọc lại ảnh, không tạo annotation mới, không train/build/accepted.
- Đối chiếu docs/config/src/tests và Git. Mốc đã commit gần nhất: 57b2efb; bảo toàn cả quyết định/crop chưa commit sau mốc đó.
- Roboflow còn đúng 3 tài liệu: card, audit gốc, review tổng hợp. SCB giữ 3 tài liệu. Dataset research là trạng thái/vai trò hai nguồn; không lặp chuỗi review Roboflow cho SCB.
- 54 JSON gốc gom thành 3 bundle: SCB audit.json, Roboflow audit.json/review.json. Mỗi record giữ text UTF-8 và SHA gốc; review.json giữ snapshots tài liệu/script đã nghỉ và current_person_crops/image_queue. 28 crops/21 ảnh, 24 phone positives, 5 looking positives, 1 co-occurrence; 27 unknown targets bảo toàn.
- Bỏ 10 launcher theo phiên, giữ roboflow_v1.py để audit lại đúng archive và CLI audit/overlay/validator nguồn dùng chung. Gom reusable review validation/decision logic về data/review.py; giữ regression semantics, bỏ test orchestration/repair chỉ dành launcher đã nghỉ.
- Đồng bộ B trong README/architecture/P1/P2/P3/contracts/config/ADR. Build/train/evaluate YOLO legacy không được nhận config B; chưa triển khai exporter/classifier trong cleanup.
- Lịch sử WORKLOG đầy đủ giữ trong review.json → retired_files; số liệu audit gốc không thay đổi. Outputs/media/raw không xóa hoặc sửa.
- Chưa hoàn tất: release sample scope, coverage/unknown policy, crop inference, group/split, builder B và DVC round-trip. P0/P1/P2 chưa tự đóng. Không hỏi lại kiến trúc/quyền SCB/R1–R3.
- Kiểm tra thực tế: 56 unittest PASS (57 trước cleanup, bỏ 3 test orchestration/repair đã nghỉ và thêm 2 test consolidation/gate B); Ruff/compile/diff check PASS. 111 liên kết local hợp lệ; checksum 54 JSON gốc và snapshots được bảo toàn, 28 crop/27 unknown giữ nguyên. Audit CLI còn lại chạy --help PASS; không audit/review ảnh lại. Repository checker PASS cho index hiện tại, chưa bao gồm nội dung untracked.
- Sau resume: đã xử lý 27 trạng thái modified giả bằng đối chiếu filtered Git hash với index, không stage nội dung. Git thực tế: 30 modified + 62 deleted + 9 untracked, gồm phần trước cleanup chưa commit. Lần gián đoạn do hạn mức công cụ đã được khắc phục; chưa commit/push cleanup.


## 2026-10-05 — Review codebase và cleanup sau pilot B

- User yêu cầu review sâu AGENTS/spec/code/file organization rồi sửa/xóa. Base `3a103a43f71f6947677d7ba25e1b075117bb9bdf`, Git sạch lúc bắt đầu. Không delegation. [Báo cáo đầy đủ](reviews/codebase-review-20261005.md) có findings, inventory, retention và giới hạn.
- Owner duyệt ba quyết định trong hội thoại: loại bỏ train/evaluate A nếu không còn dependency; yêu cầu FPS hợp lệ; lưu metadata rồi dọn 4 preparation copies trùng. Caller search xác nhận B không phụ thuộc train/eval A; đã gỡ 8 files gồm train/eval, benchmark, baseline/params/DVC pipeline legacy và cập nhật checker/docs/tests.
- Sửa inference thiếu/sai FPS, output overwrite; validator bbox NaN/Infinity/coordinate space; split NaN; nhãn cấm suspicious_person theo spec04. Không sửa shape schema, pilot producers/configs/approval hoặc split/test freeze. Đồng bộ hai mô tả spec lỗi thời (solo/schema đã duyệt).
- Dọn v1 gốc + preparation-r2/r3/r4: 604 files, 320.971.311 bytes. Full inventory/hash chỉ khác release.json so với r5. Archive local outputs/pilot-b-preparation-history-20261005.zip giữ nguyên metadata/checksums, CRC và virtual restore từng SHA PASS; 42.579 bytes, SHA af71803ebc46ea89f3f38f5925246f748ea373f8128a208526e9117ce147969c. Archive cần r5 để restore; giữ r5→v2→v3→v4 và toàn frozen interim. Approval cleanup này nằm ngoài archive snapshot chuẩn bị.
- Dọn thêm 79.211 bytes fixture tổng hợp và evidence rebuild trùng byte; không xóa nguồn raw/extracted, review evidence thật hay cache/remote. Native PowerShell kiểm absolute containment/reparse points trước recursive delete. Không upload dữ liệu.
- Validation cuối: 113 unittest PASS, Ruff PASS, compileall PASS, repository checker --require-git PASS, diff --check PASS; DVC status đúng pointer v4: up to date. V4 payload/schema/manifest/split/test-subset/test IDs giữ nguyên,112 ledger/84used/60train13val11test/28review_only. Git pointer blob SHA giữ nguyên; raw working tree hash khác do CRLF, normalized bytes/YAML bằng Git blob.
- Giới hạn: local Python hiện có; chưa fresh install/Linux CI/GPU/model evaluation. Model/experiment B và S9 runtime vẫn pending; không nâng acceptance milestone. Không commit/push trong task này.
