# DATA-V6-20261007 — Chuẩn bị release v6

- Trạng thái: HOÀN TẤT đóng release v6 local ngày2026-10-08 theo approval ngày2026-10-07.317train/50val/11test. Chưa train/upload.
- Owner: chủ repository; Codex chuẩn bị, kiểm tra và thực thi sau quyết định.
- Phụ thuộc: v5 accepted và E002 hoàn tất, giữ bất biến.

## Mục tiêu và authorization

Owner đã approve toàn bộ phương án nguồn trong pilot-b-v6-source-research-20261007, xác nhận toàn quyền ba RF mới và FPI, yêu cầu làm tới100%. Owner đã chốt **mở rộng train/val, giữ nguyên test v5**. Không hỏi lại quyền/scope. Approval nguồn và split lưu tại artifacts/reports/pilot-b-v6-preparation-20261007/{owner-scope-approval,split-scope-approval}.json. Phương án được duyệt nói owner nghiệm thu gói review tổng hợp trước release; không biến source approval thành nhãn/crop approval chưa tồn tại.

## Source of truth và tài liệu đã đọc

AGENTS.md; docs/00-INDEX.md; task-template; docs01/02/04/05/08/09/11/19/21/25; ADR012/013; pilot-b-release-contract-v1; label-spec-v1; source-audit; SCB/RF candidate/audit/review; E002-results; release v5; expansion20261006; FPI/SCB research; pilot-b-v6-source-proposal-20261007; scene-constraints của staging20261006-r2. Không đọc lại tài liệu không đổi. Canonical schema/builder/expansion và release proposals đã đối chiếu. Báo cáo mới: docs/data/pilot-b-v6-membership-review-20261007.md.

## Phạm vi và ràng buộc

Formulation B, phone_use/looking_around, unknown masked giữ nguyên. FPI ngoài đợt chính, Discuss vẫn loại. Raw/ZIP/v5/E002 bất biến. Không train/test inference/upload. Media local ignored, không commit. Nhóm thị giác bảo thủ, không suy subject/session/video metadata. Giữ13val lịch sử trong val mở rộng, không so metric khác tập trực tiếp E002.

## Artifact phương án trước (revision R2 thay thế)

- Nguồn nghiên cứu: artifacts/reports/pilot-b-v6-source-research-20261007/, snapshot đã pin bất biến.
- Candidate selection r1: configs/datasets/pilot_b_v6_preparation_r1.yaml,143candidate; đã xem24sheet toàn bộ ảnh/crop.
- Crop cuối: data/interim/pilot-b/v6-preparation-20261007-r4, sửa12crop; visual-review-r3.json pin source/r1crop. CA031 được sửa looking negative/work confirmed tại decisions-r2 sau xem lại đúng người.
- Quyết định cuối: artifacts/reports/pilot-b-v6-preparation-20261007/release-review-decisions-r2.json.
- Gói review cuối: data/interim/pilot-b/v6-release-review-20261007-r3; review.html,340crop,proposed-assignment.jsonl,summary/checksums. Không phải canonical accepted package.
- Proposal config: configs/datasets/pilot_b_v6_release_proposal_20261007.yaml; status draft, owner_release_approval null.
- Báo cáo/assignment bản metadata/provenance/verification/evaluation-preservation/rights-attribution: artifacts/reports/pilot-b-v6-preparation-20261007/.
- Code mới: src/ai_exam_monitoring/data/pilot_source_candidates.py, pilot_release_review.py; tests tương ứng. Không đổi trainer/model.

## Counts và lựa chọn phương án trước

351ledger; đề xuất235membership =193train/31val/11test,89review_only,27excluded. Thêm79crop mới và52promotion parent (44SCB+8RF).143candidate:79used,48review_only,16excluded. Parent208labels/crop/source giữ nguyên;104used cũ giữ nguyên usage/group. Student giảng đường vào train, cụm Classroom video áo tím/xanh vào val; không cắt frame cùng nhóm. Có32quan hệ (11kế thừa owner-approved).79/13/3 component train/val/test không phải số session độc lập. Cảnh liên quan RFval cách ly; duplicate ưu tiên crop parent.

## Verify hoàn tất

152 unittest PASS (39.6s), Ruff/Mypy phạm vi mới PASS; checker repository --require-git failures0, git diff --check PASS. Verification độc lập recompute351assignment,143crop pixels,340crop payload,730HTML paths, checksum parent/package,13val+11testpreservation, không xung đột image/crop/group split. Full test chạy trước sửa chuỗi selection_reason mô tả, sau sửa chạy targeted11tests. Chưa metricmodel; release acceptance false.

## Câu hỏi đang chờ và bước tiếp

Đã gửi request_user_input_async cuối lượt: owner nghiệm thu gói193/31/11/crop/nhãn/group/membership hay muốn chỉnh. **Owner đã trả lời: “tôi cần thời gian để review.”** Chưa nghiệm thu; giữ trạng thái chờ owner review, không đóng release hoặc hỏi lại ngay. Tiếp nhận câu trả lời thật, không tự tạo owner evidence. Nếu approve: ghi nguyên lời/pin report+config+assignment+package; materialize canonical v6 mới bằng schema/builder hiện hành, kế thừa crop/target/group/test-freeze parent, dùng review evidence mới cho additions; kiểm toàn bộ gate và pointer. Phải giữ subset13val lịch sử và11test hash/nhãn/group. Builder release cũ có assumptions112/v5, không tái dùng mù hoặc giả approval. Không tự train/upload từ dataset approval.

## Lịch sử lỗi và môi trường

Sandbox mặc định lỗi; require_escalated qua auto-review hoạt động ở resume này. Không có rejection đang chặn. Browser runtime trước đó lỗi/HTTP403 nhưng localZIP đủ, không cần browser. Crop r2 dở do path; r3 thay bởi r4. Review r1 dở vì excluded crop chỉ có metadata; r2 split thay bởi r3. Không xóa/ghi đè các output lịch sử. Repository có untracked research từ cùng task, giữ lại; không commit media/model.

## Phản hồi owner và revision mở rộng

Owner yêu cầu cân nhắc lại review_only vì nhiều crop dùng được, đồng thời tăng crop có giá trị nhận diện. Đây là yêu cầu làm revision proposal, không acceptance gói cũ. Rà toàn bộ89review_only, kiểm nhãn đã biết/crop nhỏ có thể dựng lại/group, không tự biến unknown thành negative; ưu tiên negative cùng camera, tay gần mặt, nhiều người khác nhau trong một ảnh nguồn. Tạo output/report/config version mới; giữ snapshot đã trình trước. Đã hỏi tùy chọn ID owner thấy dùng được, không chờ mới làm. Phạm vi train/val, test11v5 và semantics giữ nguyên.

## Checkpoint revision R2 đang thực hiện

Owner nêu rõ EXP-CM-008/016/022, EXP-RF-003/004/007/008 và nhiều crop khác. Đã lưu owner-revision-request.json trong report expansion R2. Đã rà lại toàn bộ 89 review_only và 54 ảnh bổ sung; vừa xem đủ 16 sheet chứa 93 crop người khác cùng ảnh. 147 crop mới là hàng đợi đã xem, không phải 147 crop được nhận. Đang ghi quan sát/crop/split đề xuất, loại lặp tư thế và nối cùng cảnh. Code proposal mở rộng hẹp: chỉ cho điền unknown của parent review_only với crop SHA/lý do, không sửa nhãn đã biết hoặc membership đã dùng. Đang tạo snapshot mới; chưa nghiệm thu/release/train.


## Bàn giao revision R2 — chuẩn bị hoàn tất

Báo cáo artifacts/reports/pilot-b-v6-expansion-20261007-r2/README.md; config configs/datasets/pilot_b_v6_release_proposal_r2_20261007.yaml; gói ảnh/assignment cuối data/interim/pilot-b/v6-release-review-expanded-20261007-r5. R2/r3/r4 superseded nhưng giữ snapshot.

498ledger/487crop;317train/50val/11test=378used,93review_only27excluded. So proposal trước thêm46/89review_only cũ (33train13val) và97/147crop bổ sung (91train6val).93MP nhận62;54ảnh bổ sung nhận35, không phải54cảnh độc lập. Bảy ID owner nêu đều đề xuất dùng; RF007/008 ởval. CM016U/N cần chú ý hướng nhìn/tài liệu khi owner nghiệm thu.

Đã xem89cũ+147mới,5redraw,9sheet nearest. Native crop check MP003/033/064/088 không chắcphone nên giữreview_only; CA008 chỉ lookingN. Target_overrides và assignment là kết luận cuối, visual-review ghi quan sát ban đầu.16parentpending điềnunknown; không đổi knownlabel hayfilev5.104usedv5 giữ nguyên80/13/11.

156unittestPASS41.485s; Ruff/Mypy3module/2testPASS; check_repo --require-git failures0 chỉtracked. QA độc lập:498assignment,290candidatepixel,487cropchecksum,1171HTMLrefs; test11/val13 và gói cũ bất biến, không xung image/crop/group split hoặc cropSHAtrùng. Nearest không chứng minh hết near-duplicate.

Chỉ còn owner nghiệm thu nội dung crop/nhãn/nhóm/membership revision R2; quyền/phạm vi đã duyệt không hỏi lại. Sau nghiệm thu materializecanonicalv6 theo schema/evidence, không tựtrain/upload. Docs mới docs/data/pilot-b-v6-expanded-review-20261007.md; report có config/summary/assignment/reconsideration/visual-review/verification/evaluation-preservation/provenance.

Scripts local ignored trong outputs: prepare_v6_revision_r2.py,assemble_v6_revision_r2.py,audit_v6_nearest_r2.py,verify_v6_revision_r2.py,document_v6_revision_r2.py. Assemble ban đầu chưa chứa QAoverride cuối; rebuild bằng modulepilot_release_review với decisions cuối. Unicode PowerShell pipe mặc định gây dấu hỏi trong ghi chú QA, đã sửa bằng UTF8file và dựng r5. Không dùng utf8-sig alias, Python đúng utf-8-sig.

## Approval đóng release v6 — 2026-10-07

Owner đã review và approve báo cáo expansion R2, yêu cầu đóng release v6. Nghiệm thu gói317/50/11 và nội dung crop/nhãn/nhóm/membership đã hoàn tất; không còn chờ approval. Đang pin bằng chứng owner, materialize canonical v6 bằng schema/builder, kiểm bảo toàn v5/test và ghi pointer/config accepted. Không train hoặc upload trong task này. Các đoạn chờ review phía trên chỉ là lịch sử.


## Kết thúc task — release v6 accepted local (2026-10-08)

Đã ghi owner-approval/configaccepted và canonical data/processed/pilot-b/pilot-b-20261007-v6. Report artifacts/reports/pilot-b-v6-release-20261007/README.md; pointer/checksum, verification, evaluation-preservation, group-boundaries và provenance trong cùng thư mục.317train50val11test=378manifest,498ledger,471crop,93review_only27excluded.16crop mới excluded chỉ ởreviewpackage, canonical không xuất. Nguồn/v5/proposal bất biến.

Code mới pilot_review_acceptance.py materialize đúngassignment, canonicalbuilder kiểm source/pixel/schema, guard parentknownlabels/usedmembership.25parent được promotion từscopepreparation/trống sanglocalclassifier theoapproval; license/attribution giữ nguyên.104usedv5 bảo toàn cả quyền/evidence, test11 vàval13lịch sử giữ nguyên. Inline freeze v6 dùnghelperhiệncó, không đổi membershiptest hoặc cho inference. Fullsuite162PASS66.686s; Ruff/Mypy phạmvimớiPASS; QA độc lập vàpublicloaderverify_datasetPASS. Không modeltrain/inference/upload/commit/push.

Lượt trước auto-review hitusage limit; patchfinalizer chưa được thực hiện khibịchặn. Resume đã xác minh rồi áp dụng, datasetcard tiếngViệt/checksum được hoàn thiện trướcpointer. Module/codehashpin trongrelease; kiểm cuốipointer/provenance saudocs. Index/WORKLOG đã trỏv6hiệnhành. Không còn câu hỏi cầnowner cho taskđóngrelease. Bước AI sau làthiếtkếexperimentv6riêng khiuser yêu cầu, khôngtựtrain.
