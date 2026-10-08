# E003-PREP-20261008 — Chuẩn bị thử nghiệm Pilot B v6

- Trạng thái hiện hành: HOÀN TẤT E003 FINISHED và validation/báo cáo. Phạm vi: AI/classifier.
- Owner/người chốt: chủ repository; Codex chuẩn bị và kiểm chứng.
- Phụ thuộc: release v6 accepted, E002 hoàn tất; không kế thừa approval chạy E002.

## Mục tiêu và bối cảnh

### Checkpoint execution sau resume

Hậu kiểm cuối PASS: dataset/outputSHA,104parent, rawbest45/earlystop64, snapshot bảo toàn,45links/40filepins. Reports và DVC pointers local sẵn sàng; không còn việc model trong scope. Chỉ chốt commit bàn giao và Git status; không hỏi lại approval, không final test/upload/promotion. Report kết luận H1 ủng hộ nhưng phone added37recall0.30, giữ nghiên cứu. Fullsuite162PASS, valexact, localrestore36SHA. Các mô tả pending/preparation phía dưới chỉ là lịch sử.

Đã val reload exact và analyze PASS: primary0.6107752323, constant0.6911010404, delta−0.0803258081; historical13 delta−0.2195866283; added37phone recall0.30. Report artifacts/reports/E003, docs/experiments/E003-results.md và executionREADME đã viết. DVC add/cache restore3outputs/36filesSHA PASS, không remote. Còn final-verification/checksum/link/diff/repo và commit hồ sơ bàn giao; không rerun model. Training run source commit giữ4e206a6, report commit sau không thay identity.

Commit thực thi 4e206a6, clean detached outputs/E003-code.162tests PASS51.460s, preflight PASS. Smoke INTERRUPTEDepoch1/resume FINISHED3epoch. Baseline FINISHED64epoch/best45,29.1987723s; chưa kết luận metric trước val reload. Auto-review hết hạn mức ở lệnh ghi drift/đọc trạng thái, lệnh đó không thực thi; user resume, đọc run thật và tiếp tục val evaluator. Không rerun baseline. Script analyze.py/preflight.py và logs đang untracked, cần kiểm/checksums/bàn giao. Còn validation exact, slices/FPFN/comparison, DVC local restore, results/index/WORKLOG và final diff.

### Authorization hiện hành ngày 2026-10-08

Owner: “tôi đã review và approve, hãy thực hiện tiếp tới khi hoàn thành! trong quá trình thực hiện nếu có gì chưa rõ thì hãy hỏi lại tôi.” Approval bao gồm hồ sơ E003 đã review, ngoại lệ CPU local, local commit/clean checkout, smoke/resume, một baseline và validation/report. Không final test/upload/promotion. Các đoạn pending/chỉ chuẩn bị bên dưới là lịch sử, không còn là blocker. Không thay config/recipe hoặc dữ liệu từ kết quả model.

Deliverables thực thi: ADR-016, approval approved có snapshot pending, runbook E003, outputs/E003-code clean checkout, outputs/E003-smoke/E003/E003-val-evaluation; reports/E003 và E003-execution-20261008, E003-results.md, pointers/checksums local. Full suite và preflight phải PASS trước chạy. Ghi trạng thái thật nếu lỗi; không tự đổi identity.

User yêu cầu cấu hình E003, hypothesis và protocol chi tiết cùng báo cáo kiểm hợp lệ để nghiệm thu trước huấn luyện. Đề xuất giữ recipe frozen linear probe để đo baseline v6; validation đã thay nên không so toàn val50 trực tiếp với val13 E002.

## Đọc trước / ADR đã được accept

Đã đọc AGENTS.md, docs/00-INDEX.md, task-template; docs04/09/10/15/22/23/24; ADR014/015; E002 config/smoke/approval/protocol/runbook/results; release v6 README/config/pointer. Đã đối chiếu training config/evaluate/metrics và các điểm vào train/data, pyproject, manifest mẫu. ADR014/015 chỉ cho E001/E002. Không đọc lại tài liệu không đổi.

## Input và phiên bản chính xác

Git nền 9c85299ce5d0205d56073aaf55d7e097485cfd54, lúc bắt đầu working tree sạch. Pilot B v6: data/processed/pilot-b/pilot-b-20261007-v6; split pilot-b-v6-group-expansion-r2; encoding pilot-b-targets-v1; checksum-list SHA 971e2a46c28839e0a3a13eb7f9a8eb39ed7d24fc2ce5d8225c1c64d51f563e3f.

## Yêu cầu / ràng buộc

Chỉ chuẩn bị và kiểm không train/inference; không sửa dataset, label, split, trainer, E001/E002; không upload. Test11 chỉ integrity. Tài liệu tiếng Việt. Giữ trạng thái pending và guard approval.

## Deliverables

configs/experiments/E003.yaml, E003-smoke.yaml; docs/experiments/E003-protocol.md, E003-approval.json; artifacts/reports/E003-preparation-20261008/ chứa báo cáo và evidence kiểm không train; index/WORKLOG cập nhật.

## Ảnh hưởng đến data-label-split / experiment / privacy

Không mutation; dùng manifest378, không quét crop471. Train317/val50, giữ subset13val lịch sử và test11. Recipe/metrics/CPU local là đề xuất cần owner nghiệm thu.

## Tiêu chí nghiệm thu và lệnh verify

Load config strict; verify_dataset/hash/schema/leakage/preservation; weights local SHA; verify_approval phải từ chối pending; thống kê support train/val và subset lịch sử; kiểm recipe diff E002; targeted training tests, check_repo và git diff --check. Không gọi train/smoke/evaluator trên dataset thật.

## Rủi ro / rollback / quyết định chưa giải quyết

Owner chốt hypothesis/recipe/CPU local/protocol trước chạy. Promotion gate/holdout vẫn TBD. Val dùng chọn epoch không là holdout; nguồn/group confounded. Rollback chỉ bỏ các file đề xuất mới, không đụng release.

## Checkpoint agent

- Ngày 2026-10-08: đang kiểm source và soạn proposal. Chuẩn bị đủ hồ sơ trước xin nghiệm thu.
- Sandbox process lỗi helper_unknown_error; lệnh đọc thực hiện qua escalation sau lỗi, không bị auto-review từ chối.
- Sau resume đọc index/TASK, đối chiếu files/Git và kết quả kiểm thực tế; không chạy training từ task chuẩn bị.

### Tiếp tục sau gián đoạn

- Đã đối chiếu index/TASK/Git ngày2026-10-08: bản ghi approval chưa được tạo trong lượt bị ngắt; đã tạo pending, configs rỗng, training/test false. User yêu cầu tiếp tục chuẩn bị, không approve chạy.
- Đã viết E003-protocol.md, báo cáo README; giữ recipe E002. H1 primary so BCE val50 với constant train-prevalence, historical13 chỉ hồi quy phụ; chưa train. Đã đọc thêm CI, lock/runbook E001, loader/train chi tiết, predictions/checksum E002 và đầu WORKLOG.
- Kiểm metadata/payload v6/v5 và support PASS; train phone93P91N133U,looking117P112N88U; val phone17P20N13U,looking18P11N21U. BCE constant0.6911010403687807.23training/preservation tests PASS11.364s; pip/Ruff/repo PASS. Không cần sửa src.
- Kiểm cuối: pin protocol/proposed configs; kiểm prediction lịch sử/smoke diff, Markdown links, diff/file hashes, hoàn thiện command evidence và proposal-checksums. Chờ owner nghiệm thu sau bàn giao; không mở training từ pending.

- Bàn giao: verification bổ sung PASS,23tests/pip/Ruff đã PASS; diff reviewed. .gitattributes bổ sung LF cho E003 theo quy ước E002 để giữ byte pins qua checkout. Không sửa src/data/E002/CI. Protocol/report/config/approval pending hoàn tất. Bước tiếp theo duy nhất về execution là nhận nghiệm thu thật; không tự train. Các pins cuối và link-check lưu trong proposal-checksums.json / validation-commands.json.
