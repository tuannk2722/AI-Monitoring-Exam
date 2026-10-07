# DATA-EXPANSION-20261006 — Triển khai hướng mở rộng đã được owner duyệt

- Trạng thái / khu vực / ưu tiên: Release pilot B v5 local hoàn tất, accepted theo owner / dữ liệu / cao.
- Người chịu trách nhiệm và nghiệm thu: chủ repository (solo); Codex thực hiện và chuẩn bị bằng chứng.
- Phụ thuộc: E001 hoàn tất; candidate mới phụ thuộc archive đúng hash và bằng chứng nguồn/nhóm.

## Mục tiêu và bối cảnh
Ngày 2026-10-06, owner duyệt hướng hai luồng SCB/RF hiện có + thẩm định nguồn mới; cho phép mở thẩm định metadata Classroom-monitoring-dataset và tạo draft dataset pointer v5 sau khi có candidate. Giữ phone_use, looking_around và mask unknown. Ghi nhận quyết định này và tiến hành các phần có đủ đầu vào.

## Đọc trước / ADR đã được accept
Đã đọc trong lượt này: AGENTS.md; docs/00-INDEX.md; checkpoint trước; docs/templates/task-template.md; docs 01/02/04/08/09/19/21/25; ADR-012/013; candidate cards SCB5-supplied-20261003 và Roboflow-phone-use-20261004; kế hoạch data-expansion-20261006; source-research.json; config pilot_b_release_v4 và pilot_b_scb_proposals_v1; pyproject.toml; phần WORKLOG liên quan. Đã đọc thêm contract pilot B, script inventory, cấu hình release proposal, schema record hiện hành, repo checker và điều khoản/trang project/license nguồn công khai. Không đọc lại tài liệu không đổi.

## Input và phiên bản chính xác
Parent pilot-b-20261005-v4: 112 ledger, 84 manifest, 28 review_only; config accepted pilot_b_release_v4.yaml. Kế hoạch và evidence data-expansion-20261006 đã tồn tại nhưng chưa commit. V4/test/E001 bất biến; queue không phải membership v5.

## Yêu cầu / ràng buộc
Chỉ approval cho hướng triển khai và metadata, chưa chấp nhận nguồn/nhãn/split/release mới. Không tự tải media nguồn mới, không upload, không gửi liên hệ bên ngoài, không train E002. Không tự chuyển nhãn nguồn thành target; Discuss tiếp tục loại. Bảo toàn sửa AGENTS.md và file review bị xóa từ trước.

## Deliverables (đường dẫn artifact/contract)
- Bằng chứng phê duyệt trong artifacts/reports/data-expansion-20261006/ và đồng bộ kế hoạch/index/WORKLOG.
- Báo cáo thẩm định metadata Classroom-monitoring-dataset với URL, trạng thái xác minh và TBD có owner.
- Kiểm tra archive local đúng đường dẫn/hash; ghi rõ điều kiện tạo candidate/pointer v5 nếu thiếu đầu vào.

## Ảnh hưởng đến data-label-split / experiment / privacy
Không sửa raw/v4, semantics, labels, split hoặc test freeze. Pointer v5 chỉ được tạo ở trạng thái draft sau khi có candidate; quyền này không phải approval training/release. Không dùng kết quả test để chọn dữ liệu.

## Tiêu chí nghiệm thu và lệnh verify
Approval truy vết đúng bốn lựa chọn owner; metadata tách claim với xác minh archive; không tạo pointer giả khi chưa có candidate. Kiểm JSON/UTF-8/liên kết, inventory bằng parser canonical, hash parent, repository checker và git diff --check.

## Rủi ro / rollback / quyết định chưa giải quyết
Archive đã xác minh có tại path pin, 3/3 SHA PASS; không còn blocker thiếu archive. R2 đã có 48SCB/24RF mới; draft ban đầu chỉ có 28 review_only được giữ lịch sử. TBD-EXP-SOURCE: owner nghiệm thu nguồn sau bằng chứng quyền/provenance/version/group. TBD-EXP-V5: owner nghiệm thu membership/nhãn/group/split sau candidate, không suy từ approval hướng. Đã thêm workflow proposal canonical và hỗ trợ layout RF train; giữ raw/v4/E001 bất biến. Có thể hoàn tác riêng code/config/evidence R2.

## Checkpoint agent
- 2026-10-06: đã đối chiếu Git; có sửa/untracked từ task trước, không ghi đè công việc user.
- Sandbox exec và node lỗi khởi tạo; exec đọc repo ngoài sandbox đã chạy qua approval review. Đây là lỗi công cụ, không phải từ chối quyền dữ liệu.
- Trang project công khai vẫn hiển thị 150 ảnh, 2 versions, 7 lớp, CC BY 4.0; không có mô tả project. Chưa đủ chứng minh provenance/consent hoặc group.
- Đã tạo owner-approval.json, candidate-batch-v5-draft.json, classroom-monitoring-metadata-review.json, README.md và verification.json trong artifacts/reports/data-expansion-20261006/; pointer configs/datasets/pilot_b_expansion_v5_draft.yaml. Đồng bộ kế hoạch/index/WORKLOG.
- Candidate batch đúng 28 review_only hiện có (10 Head,13 HRW,5 RF); 0 media candidate mới. Kiểm source image/label ZIP và crop SHA 28/28 PASS; giữ target/crop/source/mask. Chưa review near-duplicate/nhóm; split=null, training_eligible=false, không tạo package/DVC release.
- Sửa hai thông tin sai ở kế hoạch: archive đang có và khớp SHA; SCB review_only là23, không phải16. Snapshot evidence inventory/queue/source-research ban đầu giữ nguyên; metadata review mới là phần bổ sung.
- Verification PASS: inventory tái lập112/84/28; toàn123 file trong checksum list v4 khớp, checksum list SHA dbc1bf90a5605cac39b5c96503e71097ecd1eaab5b35e14f311f966edd503f53; pins pointer/approval/batch; parse JSON/YAML/UTF-8/link mới; Ruff, repository checker và diff check. Hai link cũ tới file review đã bị owner xóa giữ nguyên. Không đổi code nghiệp vụ nên không chạy lại full suite.
- Bước tiếp sau resume: đối chiếu Git/checkpoint/index; khai thác shortlist SCB mới ngoài ledger từ archive đã pin, không dùng test E001 để chọn; hoàn thiện group/near-duplicate evidence và scope release v5. Nguồn Classroom-monitoring còn TBD quyền/provenance/version/unit/group; không nhận media trước gate. Không hỏi lại bốn quyết định đã duyệt, không tự nhận dataset/nhãn/split hoặc train E002.

## Tiếp tục sau owner review ngày 2026-10-06
- Owner đã review toàn bộ thay đổi và approve, yêu cầu tiến hành tới khi hoàn tất; cho phép hỏi thông tin còn thiếu. Bảo toàn snapshot draft ban đầu, tạo revision mới cho candidate/đề xuất mới.
- Owner xác nhận có thông tin quyền/provenance/consent Classroom-monitoring và sẽ cung cấp đường dẫn/thông tin; nguồn đó chờ bằng chứng, SCB/RF tiếp tục độc lập.
- Đang đọc pipeline selection, similarity và proposals để tái sử dụng; không delegation. Tuyển/QA bằng heuristics là Draft, không tự nâng thành target/split Accepted.

## Resume sau gián đoạn công cụ
- Đã đối chiếu lại index/TASK/Git: R2 có 48 SCB +24 RF mới, visual proposals cho72,11 đề xuất loại anchor,2 crop RF sửa và11 đề xuất nối cảnh; còn28 review_only parent.
- Đã triển khai pilot_expansion.py và hỗ trợ explicit RF train layout trong pilot_selection.py;131 tests, Ruff và repo checker PASS ở lượt trước. Chưa hoàn tất verification artifact, index/WORKLOG hoặc handoff R2.
- Lệnh kiểm cuối bị chặn do automatic approval review hết hạn mức (không phải kết luận hành động không an toàn); sau user resume, công cụ đã hoạt động lại.
- Xác nhận một số chuỗi tiếng Việt bị PowerShell chuyển thành dấu hỏi: README R2, scope note config RF/pointer R2 và reason của crop refinements. Sẽ sửa text, lưu bằng chứng hash config đã chạy và bảo toàn mọi identity/crop/nhãn/split.
- Thông tin quyền/provenance Classroom-monitoring owner hứa cung cấp vẫn chưa có nội dung/đường dẫn; không suy quyền từ lời hứa. Tiếp tục validation độc lập trước nghiệm thu cụ thể.

## Checkpoint R2 hiện tại
- Đã đọc thêm source-audit, label-spec-v1, pilot_inputs/selection/scb_proposals/owner_groups/image_similarity/yolo, tests selector/similarity, fingerprint/scene proposals lịch sử; không đọc lại canonical docs không đổi.
- Hai config selection R2, code pilot_expansion và tests đã chạy thành công; output SCB/RF ở data/interim/pilot-b/expansion[-rf]-20261006-r2; evidence ở artifacts/reports/data-expansion[-rf]-20261006-r2. Proposal nhãn có 72 observations/hash,11 anchor đề xuất loại,2 crop RF sửa và 11 liên hệ cảnh. Canonical target mới vẫn unknown; split/group null, training_eligible=false.
- Vòng trước đã chạy 131 tests PASS, Ruff toàn src/tests/scripts PASS, repo checker PASS. Sau resume sửa mô tả UTF-8; encoding-repair lưu chính xác text/hash RF config thực thi, chứng minh chỉ khác selection.scope_note; summary phân biệt config_sha256 lúc chạy với current_config_sha256.
- Đã đồng bộ index/kế hoạch/WORKLOG; verification R2 PASS (72 candidate, 74 crop tái tạo đúng pixel, 11 quan hệ, pins và parent payload). Không tạo release, không train, không upload/commit/push. User sửa AGENTS và xóa review cũ được giữ nguyên.
- Phụ thuộc còn thiếu: owner nghiệm thu báo cáo R2 mới; quyền RF mới theo phạm vi release; metadata quyền/provenance Classroom-monitoring owner chưa gửi; group independence/split/holdout chưa có quyết định. Chỉ hỏi trên báo cáo cụ thể, không hỏi lại hướng hai luồng/semantics/quyền SCB.

## Owner nghiệm thu R2 và staging
- Owner trả lời: “Duyệt proposal R2, tiếp tục staging review-only”. Phạm vi 72 candidate, 11 anchor loại, nhãn/crop theo hash và 11 liên hệ cảnh; chưa duyệt split/release/training. Approval này thay trạng thái chờ nghiệm thu ở checkpoint trước.
- Tạo snapshot approval pin evidence R2; staging riêng đúng 72 candidate mới (61 review_only, 11 excluded), dùng schema/builder hiện có. Parent 112 record và queue 28 cũ giữ nguyên, chưa chốt membership release v5 hợp nhất.
- Nhập target/crop đã duyệt, unknown vẫn mask 0. Lưu quan hệ cảnh như ràng buộc đã duyệt; không suy nhóm độc lập/split. Không upload hoặc train.
- Đã hỏi bằng chứng Classroom-monitoring và scope quyền RF mới; chưa có trả lời. Công cụ đã hoạt động lại sau resume; lần sửa checkpoint trước không được thực thi vì automatic approval review hết hạn mức.

## Xác nhận quyền của owner
- Owner xác nhận toàn quyền sử dụng mọi dataset đang dùng trong project, yêu cầu không hỏi lại hoặc giữ quyền sử dụng làm blocker. Áp dụng cho SCB/RF của staging R2; không yêu cầu thêm bằng chứng quyền. Phê duyệt staging R2 vẫn hiệu lực.
- Tiếp tục hoàn tất staging, kiểm checksum/pixel/schema và bàn giao; split/release/training chưa nằm trong approval R2.

## Bàn giao cuối cùng — trạng thái hiện hành thay checkpoint lịch sử
- Hoàn tất staging `data/interim/pilot-b/pilot-b-expansion-20261006-r2-staging`: 72 record mới, 61 review_only/crop, 11 excluded; target theo proposal đã duyệt, unknown null/mask0. Parent112/manifest84/queue28 bất biến.
- Approval/rights confirmation/ledger/selection/scene constraints/build metadata/result/verification/README ở `artifacts/reports/data-expansion-staging-20261006-r2/`; pointer `configs/datasets/pilot_b_expansion_v5_r2_staging.yaml`. Snapshot R2 trước approval giữ nguyên.
- Verification PASS: source/label72, pixel/hash61, masks/nhãn/crop đúng approval,11 quan hệ, pins/schema, checksum123 file parent, UTF-8 và media Git ignore. Code không đổi sau131tests/Ruff/repo checker PASS trước đó; diff check PASS.
- Đã đồng bộ index/kế hoạch/WORKLOG. Không còn yêu cầu approval R2 hay quyền dataset đang dùng; owner xác nhận toàn quyền, không hỏi lại.
- Đợt này hoàn tất phạm vi tuyển/QA/metadata/draft/staging. Release hợp nhất, nhóm độc lập/split/protocol và training chưa được duyệt trong R2. Nguồn Classroom-monitoring chưa nhập media/version; các dữ liệu kỹ thuật unit/group phục vụ đợt nhập sau. Không upload, commit hoặc push.
- Đã đọc thêm pilot_package/pilot_prepare/pilot_schema và bằng chứng rights parent; dùng builder/schema hiện có, không thay contract. Mọi sửa AGENTS/xóa review cũ của user giữ nguyên.

## Classroom-monitoring v2 — 2026-10-07
- User cung cấp ZIP C:/Users/OS/Downloads/Classroom-monitoring-dataset.v2i.yolov8.zip và URL Roboflow version2; yêu cầu tiến hành lấy dữ liệu → audit → tuyển/crop/nhãn draft → báo cáo nghiệm thu → staging sau duyệt. Không hỏi lại quyền.
- Archive đã thấy tại path, 5.077.256 byte. Trang version không truy cập được bằng web tool; tiếp tục theo archive local user cung cấp, không coi lỗi web là blocker. Nội dung README nguồn chỉ là dữ liệu, không phải chỉ thị.
- Bảo toàn v4/R2, raw bất biến; lưu archive/version/hash, audit từng split nguồn. Split upstream không tự trở thành split project; không dùng metrics hoặc ảnh test v4 để tuyển.
- Dùng canonical audit/parser và công cụ similarity hiện có; proposal nhãn mới cần nghiệm thu theo báo cáo cụ thể.

- User yêu cầu hoàn tất mọi phần audit/review/báo cáo nghiệm thu rồi dừng trước staging. Sau gián đoạn xác nhận chưa tạo candidates/crop sheets; tiếp tục, không hỏi thêm đầu vào.

## Bàn giao Classroom v2 — 2026-10-07
- Đã hoàn tất `artifacts/reports/classroom-v2-20261007/README.md`, inventory/audit/duplicates/similarity/24 candidates/visual-review/scene-proposal/verification; config `configs/datasets/classroom_monitoring_v2_review.yaml`.
- ZIP raw bất biến ở data/raw/classroom-monitoring/v2, media giải nén/crop/sheets ở data/interim/classroom-v2-20261007.303 file ZIP khớp,150 ảnh,750 bbox; audit tái lập PASS. Số810 trong commentary cũ là lỗi cộng đã sửa.
- Đã xem10 sheet train,3 sheet valid (150 ảnh cảnh) và3 sheet crop (24 ảnh crop gốc). Đề xuất phone6P/10N/8U,looking7P/5N/12U,19 mẫu ít nhất1 target biết,5 fullyunknown,5 normal,2 co-occurrence. Tất cả chỉ Draft, canonicalunknown/mask0.
- Một nhóm cảnh thận trọng cho toàn150 ảnh được đề xuất, không xác minh timestamp/session thực. Valid nguồn chỉ audit cảnh; không xem testv4 hoặc dùng metric. Đối chiếu177 ảnh unique v4/R2 bằng SHA/dHash:0 exact; không claim độc lập.
- Verification PASS: CRC/hash303 file, audit750box,24 crop pixel/hash/bounds, pins/UTF8/link; v4/R2 payload bất biến. Không đổi implementation nên không chạy lại unit suite; diff check/repo checker cuối bàn giao.
- User yêu cầu chỉ dừng khi báo cáo nghiệm thu hoàn tất và trước staging: đã đạt điểm dừng này. Chưa staging Classroom, chưa release/split/train/upload/commit/push; không hỏi lại quyền. Nếu owner approve báo cáo cụ thể, nhập quyết định theo hash và tạo staging mới.
- Đã đọc thêm source-audit và đối chiếu label-spec phần phone/looking trước review; không suy label nguồn.

## Tiếp tục sau nghiệm thu24 crop/nhãn
- Owner đã review toàn24 proposal và approve, yêu cầu tiếp tục. Tạo staging review-only bằng builder canonical; pin approval/report/candidate/visual theo hash.
- Approval nêu crop/nhãn; đã hỏi riêng đề xuất nhóm150 ảnh CM-V2-SCENE-01. Trong lúc chờ, group null và không split/train. Quyền nguồn đã xác nhận, không hỏi lại.
- Bảo toàn raw/v4/R2 và evidence Classroom trước approval; tạo report/pointer/package mới.

## Bàn giao staging Classroom — checkpoint hiện hành
- Owner đã trả lời duyệt gộp150 ảnh thành một nhóm; không còn chờ nhóm/crop/nhãn.
- Package `data/interim/pilot-b/classroom-v2-20261007-staging`, report `artifacts/reports/classroom-v2-staging-20261007/`, pointer `configs/datasets/classroom_monitoring_v2_staging.yaml`.24 record/crop review_only, group CM-V2-SCENE-01, nhóm150 ảnh được pin bằng SHA.
- Verification PASS:24 source/label/crop hash/pixel, targets đúng proposal, unknown mask0, schema/pins, nhóm150, parent v4/R2 bất biến. README proposal khác hash do sửa khoảng trắng, đã đọc đối chiếu và pin bản hiện hành trong approval mới, giữ hash lịch sử; mọi file dữ liệu giữ hash cũ.
- Đã cập nhật index/WORKLOG/kế hoạch; không đổi implementation, không chạy lại suite không liên quan. Diff/repo checker/media ignore kiểm cuối.
- Staging hoàn tất. Phần release v5 còn cần nhóm SCB/RF toàn bộ, membership hợp nhất/split/protocol riêng; chưa tự chốt hoặc train/upload/commit/push. Quyền và approval Classroom đã đủ, không hỏi lại.

## Tiếp tục v5 sau duyệt staging
- Owner “approve and continue!”: nghiệm thu bàn giao Classroom, tiếp tục lập đề xuất membership/nhóm/split/protocol v5. Không tự suy approval release mới chưa tồn tại.
- Hợp nhất kiểm kê112 parent +72 R2 +24 Classroom thành208 record metadata; bảo toàn nhãn/crop/unknown và test v4. Chỉ dùng approved group/must-link và metadata; chưa có bằng chứng độc lập thì giữ review_only. Chuẩn bị phương án cụ thể, kiểm constraints và coverage trước nghiệm thu.

## Đề xuất v5 đã hoàn tất — chờ nghiệm thu cụ thể
- Báo cáo `artifacts/reports/pilot-b-v5-proposal-20261007/README.md`, membership208, group-components, summary, source-record-snapshots, continuation-approval,verification; config `configs/datasets/pilot_b_v5_release_proposal_20261007.yaml`.
- Đề xuất train80/val13/test11/review_only93/excluded11;20 train mới gồm19 Classroom +RF-019. Nhãn/crop bất biến, Classroom cùng1 splittrain, val/test giữ nguyên. Group chưa đủ độc lập giữreview_only; không tuyên bố hoàn tất mọi groupSCB/RF.
- Verification PASS:208 nguồn,20 bổ sung,11 links,0 xung đột exact/group/crop qua split,3 parent payload bất biến. Canonical schema đơn version vẫn giữ nguyên; snapshot nhiều nguồn validate từng record, không phải manifest hợp nhất.
- Đã đọc phần liên quan E001-runbook, release-contract và pilot_release_proposals; chưa đổi code/cấu hình training.
- Bước tiếp: sau owner duyệt membership/split/release đề xuất cụ thể, tạo accepted package version mới với builder hiện có, ghi approval/hash/review evidence. Không suy “approve and continue” trước khi proposal tồn tại thành duyệt proposal này. Không hỏi lại quyền/nhãn/nhómClassroom.

## Owner approve release v5
- User đã review/approve báo cáo proposal v5 và yêu cầu tiếp tục. Đóng gói accepted version pilot-b-20261007-v5:208 ledger,80train/13val/11test/93review_only/11excluded. Không chạy E002.
- Pin approval/config/membership; bảo toàn mọi crop/target và parent; test chỉ kiểm integrity khi packaging, không inference/tuning. Dùng builder/schema hiện có.

## Bàn giao cuối — release v5 local accepted
- Package data/processed/pilot-b/pilot-b-20261007-v5; config configs/datasets/pilot_b_release_v5.yaml; report artifacts/reports/pilot-b-v5-release-20261007/README.md và release-pointer.json pin checksum.
-208 ledger/104 manifest:80train/13val/11test,93review_only/11excluded,197crop. Thêm19Classroom +RF019 train; toàn source/crop/target/review/rights giữ nguyên, val/test group/freeze giữ nguyên. Parent3 payload bất biến. V5-COMP không tự thành group độc lập, record giữ null/review_only.
-Approval pin README proposal hiện tại (sửa khoảng trắng) và hash lịch sử; các membership/config/evidence dữ liệu khớp snapshot. Builder canonical gate accepted PASS; verify schema/hash/pixel/pins/leakage/parent PASS. Không đổi implementation.
-Đồng bộ index/WORKLOG/kế hoạch/runbook; diff/repo/media ignore kiểm cuối. Không train, finaltest inference, upload, commit hoặc push. Test chỉ kiểm integrity trong packaging.
-Bước kế tiếp ngoài release: chuẩn bị E002 experiment config/protocol để nghiệm thu trước chạy; không hỏi lại approval dataset/rights/crop/nhómClassroom.
