# E002-EXECUTION-20261007 — Triển khai và chạy thử nghiệm đã được owner duyệt

- Trạng thái / khu vực / ưu tiên: owner đã duyệt, preflight/tests PASS, chuẩn bị clean checkout để chạy / AI experiment / cao.
- Owner / người nghiệm thu: chủ repository (solo); Codex chuẩn bị cấu hình, protocol và bằng chứng kiểm tra.
- Phụ thuộc: release local Pilot B v5 đã accepted; E001 đã hoàn tất. Approval dataset không phải approval E002.

## Mục tiêu và bối cảnh

Theo yêu cầu ngày 2026-10-07: tạo configs/experiments/E002.yaml trỏ package pilot-b-20261007-v5; xây dựng giả thuyết nghiên cứu và protocol đánh giá chi tiết; bàn giao đề xuất và kiểm tra hợp lệ để owner nghiệm thu trước huấn luyện thực tế.

## Đọc trước / ADR đã được accept

Đã đọc: AGENTS.md; docs/00-INDEX.md; checkpoint task dữ liệu trước; docs/templates/task-template.md và experiment-template.md; docs 04/09/10/15/22/23/24; ADR-012 và ADR-014 (Accepted chỉ cho E001); runbook E001 và phần kết quả validation; WORKLOG liên quan. Đã đối chiếu config E001/accepted v5, README proposal/release v5, release-pointer/evaluation-preservation, release.json/dataset-card v5, requirements CPU/lockfile, pyproject và gitignore. Đã đọc training config/data/model/metrics/train/evaluate/artifacts, pilot_schema/verify_payload, checker và test guard/metrics; đối chiếu resolved-config/run/code-provenance/metrics val/weights receipt E001. Không coi ADR-014 là approval E002; không đọc lại docs không đổi.

## Input và phiên bản chính xác

- Package: data/processed/pilot-b/pilot-b-20261007-v5; dataset version pilot-b-20261007-v5; split pilot-b-v5-train-expansion-v1; targets phone_use, looking_around; unknown masked.
- Checksum list SHA-256: 2dc6a0f700c04276e8fb2b073e98fb050824d8839d398bd254b2297065f92f5a.
- Ledger 208; manifest 104 = train80/val13/test11; review_only93/excluded11; crop197.
- Val/test giữ nguyên v4. Test đã evaluate E001; không gọi là holdout chưa nhìn. Nhóm Classroom chỉ train, chưa có holdout độc lập.
- Git bắt đầu sạch. Không thay package accepted, E001 hoặc evidence release lịch sử.

## Yêu cầu / ràng buộc

Toàn bộ mô tả/spec bằng tiếng Việt. Owner đã review toàn bộ thay đổi/thông số E002.yaml và approve, yêu cầu tiếp tục tới khi xong hoặc có quyết định mới cần chốt. Được ghi approval, sửa loader theo hướng hẹp đã đề xuất, kiểm regression/tamper, chạy smoke/resume, E002 và validation theo protocol. Không đổi resolved config đã duyệt, dataset/nhãn/split, threshold hoặc acceptance metric; không final test/upload/push. Có thể tạo local commit/clean isolated checkout cần thiết cho provenance theo protocol đã duyệt. Không mở rộng dashboard/tracking/runtime detector hoặc hỏi lại approvals đã có.

## Deliverables (đường dẫn artifact/contract)

- configs/experiments/E002.yaml, tương thích config loader hiện hành và trỏ đúng version/pins.
- configs/experiments/E002-smoke.yaml: đề xuất smoke3 epoch sau nghiệm thu, chưa chạy.
- docs/experiments/E002-protocol.md: giả thuyết, biến kiểm soát, selection, metrics/masks, giới hạn, freeze và review gates.
- docs/experiments/E002-approval.json: pending_owner_review, configs rỗng, chỉ proposed_configs chứa digest; không phải approval.
- artifacts/reports/E002-preparation-20261007/: README đề xuất và verification/config comparison/evidence nhỏ; không chứa media/metric giả.

## Ảnh hưởng đến data-label-split / experiment / privacy

Không mutation dataset/labels/split; chỉ kiểm integrity metadata/hash. Chỉ manifest dùng cho train/val khi sau này được duyệt; không dùng review_only/excluded. E002 và môi trường CPU local phải được nghiệm thu riêng; test không thuộc đề nghị chạy trước mắt. Không log media hay gửi dữ liệu ra ngoài.

## Tiêu chí nghiệm thu và lệnh verify

Đối chiếu schema config, payload/weights pins, membership/support/leakage, val/test preservation, E001 controls; parse YAML/JSON/UTF-8 và links; chạy validation phù hợp, repository checker và git diff --check. Không cần training để xác nhận cấu hình.

## Rủi ro / rollback / quyết định chưa giải quyết

- TBD-E002-APPROVAL: đã resolve bằng owner approval ngày2026-10-07; phải pin exact config/protocol và ghi evidence trước chạy.
- TBD-E002-TEST: owner quyết định protocol final test sau freeze candidate; hiện không đề nghị inference test.
- TBD-E002-LOADER: owner đã duyệt toàn bộ đề xuất và yêu cầu tiếp tục; triển khai loader preservation pointer như protocol, kiểm regression/tamper/preservation PASS trước chạy, không sửa dataset hoặc bỏ gate.
- TBD-METRIC-01: numerical promotion gate chưa accepted; research metrics không tự thành model promotion.
- Số mẫu/nhóm nhỏ, source confounding và Classroom chỉ train hạn chế kết luận generalization.
- Có thể hoàn tác riêng config/protocol/report mới; không sửa dữ liệu accepted.

## Checkpoint agent

- Tiếp tục2026-10-07: owner “tôi đã review toàn bộ thay đổi và thông số được cấu hình trong E002.yaml. Approve bản này, hãy thực hiện tiếp! Chỉ dừng lại khi xong hoặc có gì cần hỏi hay review/chốt lại.” Approval này thay trạng thái chờ duyệt trong checkpoint lịch sử bên dưới. Chưa cho phép final test; protocol chỉ smoke/train/validation.
- Đã đọc lại index/TASK và Git: base1e1a31a, branch data/pilot-b-preparation, đúng11 file preparation modified/untracked; không có thay đổi owner khác. Đọc thêm doc06, approval release/parent freeze và fixtures. Sandbox tiếp tục lỗi khởi tạo; exec ngoài sandbox auto-review hoạt động.
- Bước tiếp: pin approval hiện hành, Accepted ADR riêng E002/loader scope; bảo toàn preparation snapshot; triển khai loader/tests; kiểm và commit scope E002, tạo clean local checkout để chạy đúng config/seed/env. Không dừng ở readiness nếu mọi gate đủ.
- Loader đã triển khai trong training/data.py: verify pointer containment/SHA/owner/membership/parent inline freeze và semantic val/test; manifest/ledger/split nhất quán, schema leakage gate giữ nguyên; lỗi malformed đổi thành DataContractError. Signature và runtime select/letterbox/image_tensor/labels/crop_path giữ nguyên (AST proof); các training module khác khớp E001 provenance.
-23 training/preservation tests và full141tests PASS/0skip; Ruff toànsrc/tests/scripts, pip check, compileall, repo checker và diff check PASS. Preflight E00184/E002104/E002-smoke104 và approval/test guard PASS. Evidence mới ở execution/preflight.json; proposal/preparation cũ không ghi đè.
- Đã xem QA sheet20train additions (original/letterbox pairs); RGB224 giữ đầy đủ crop/không center-crop, không xem test hoặc đổi nhãn. Sheet local ignored outputs/E002-transform-qa/new-train-transforms.png; ghi metadata/hash riêng.
- Bước hiện hành: commit implementation và approvals local trên branch experiment riêng; detached clean worktree outputs/E002-code. Dùng env E001 đã pin (không tuyên bố fresh install), dataset/weights workspace gốc; exact config digests không đổi. Sau smoke interruption/resume phải tiếp tục baseline/val, xuất report thật rồi hoàn tất.
- 2026-10-07: đối chiếu index/checkpoint/Git; task release cũ đã hoàn tất và được thay bằng task E002 hiện hành.
- exec trong sandbox và node REPL lỗi khởi tạo. exec ngoài sandbox qua auto-review đọc repo thành công; không có rejection approval.
- Đã xác nhận release accepted, training_run_approved=false, new_test_inference_authorized=false. Tiếp tục đọc implementation trước chọn đề xuất có thể nghiệm thu.
- Bước sau resume: đọc index/TASK, đối chiếu Git và artifact; chỉ đọc lại docs thay đổi. Hoàn tất đề xuất/verification rồi dừng trước huấn luyện và chờ nghiệm thu E002.
- Đã tạo config/protocol/pending/report/comparison/data-checks/verification; H1 giảm val macro BCE so E001 với chỉ20croptrain bổ sung; mọi training controls giữ E001. Protocol không cấp quyền test hoặc promotion, đề xuất ngoại lệ CPU local riêng E002.
- Audit read-only hoàn tất:208ledger/104manifest/197cropSHA và checksum toàn payload,80/13/11/93/11,60train cũ và24val/test semantics giữ nguyên,20 train mới,0 exact/group/crop leakage, Classroom19train/5review_only, weights/env/trainingmodules khớp E001. Không decode media/test inference.
- verify_dataset v4 PASS84; v5 bị KeyError status. Đây là xung đột loader với accepted release, không phải hỏng hash/schema. Không đổi src/data; hướng fix fail-closed ghi protocol. Approval pending bị từ chối cho cả E002/smoke; test selection guard PASS.
-8test sẵn có về schema/mask/metrics/selection/protocol/approval PASS; checker/diff trước báo cáo PASS. Kiểm cuối UTF-8/JSON/YAML/link/pins/diff sau chốt docs; không chạy fullsuite hoặc huấn luyện thật vì src/tests không đổi.
- Verifier một lần nằm local ignored outputs/E002-preparation-tools/verify.py, được pin trong report; chỉ audit metadata/bytes và guard. Không chứa media/credentials; không commit/upload.
- Điểm dừng: bàn giao để owner nghiệm thu đề xuất cụ thể; chưa smoke/train/test/upload/commit/push. Sau approval vẫn phải sửa/kiểm loader rồi clean checkout/pins và smoke trước baseline; không coi approval dataset hoặc checkpoint là approval E002.
- Bàn giao cuối 2026-10-07: UTF-8/JSON/YAML/whitespace và 29 local links PASS; pins config/protocol/approval/verifier khớp; checker failures0 và diff check PASS. 8 tests PASS/0skip. 11 file trong scope đề xuất; src/tests/data/E001 không đổi. Training-ready=false, cần nghiệm thu và giải quyết TBD-E002-LOADER trước chạy.
