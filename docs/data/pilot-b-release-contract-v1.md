# Hợp đồng đóng gói pilot B v1

- Contract ID: `pilot-b-contract-v1`. Date: 2026-10-04 (Asia/Saigon).
- Owner/người chốt: chủ repository (solo); Codex hỗ trợ triển khai và kiểm tra.
- Status: **hợp đồng thiết kế Accepted theo ADR-013; đã hiện thực và nghiệm thu release pilot-b-20261005-v4, test đã freeze.** Training scope `local_classifier_research`; owner bổ sung quyền lưu đúng v4 trên Drive restricted ngày 2026-10-05. Evidence/phạm vi storage/round-trip theo [preparation runbook](pilot-b-preparation-v1.md); crop runtime vẫn gate riêng.
- Source of truth: [dataset research](dataset-research.md), [ADR-011](../decisions/ADR-011-person-unit-phone-definition.md), [ADR-012](../decisions/ADR-012-formulation-b-multilabel.md), [ADR-013](../decisions/ADR-013-pilot-b-packaging-contract.md). Khi triển khai, schema/config và membership cụ thể còn phải được owner review; không coi draft config hiện tại là đã được duyệt.

Checkpoint 2026-10-05: owner đã approve phương án release; canonical v4 có112 ledger/crops,84 manifest(60train/13val/11test),16 nhóm,28 review_only. Looking33P/56N/23U,phone24P/9N/79U,9normal. Crop/source/known approvals cũ giữ nguyên;9 phone/context vàranh giới cụm thị giác đã duyệt cho pilot local. [Release evidence](../../artifacts/reports/pilot-b-release-acceptance-20261005/README.md), config `pilot_b_release_v4.yaml`; không mở scope upload/runtime.

## 1. Mục đích và phạm vi hữu hạn

Một package classifier theo **YOLO person → crop có ngữ cảnh → multi-label classifier**. Hai target là `phone_use` và `looking_around`; detector không học lớp hành vi. Package dùng để chuẩn bị pilot/kiểm tra pipeline và coverage, chưa chứng minh chất lượng model hoặc độ tổng quát trên phòng thi thật.

Đầu vào review tối đa **112 record**: đúng 28 crop Roboflow đã duyệt + 84 SCB person candidates (28/28/28). SCB source box là anchor tìm người, chưa phải bbox person hay target canonical được duyệt. Một candidate có thể bị loại hoặc còn unknown; **112 không phải số crop training, 84 không phải số normal/positive**. Mọi record được giữ trong sổ quyết định; media/manifest sử dụng chỉ chứa crop đạt gate tương ứng.

Không tự refill khi có reject/unknown, không chuyển quota giữa strata, không lấy toàn nguồn. Nếu không đủ candidate hợp lệ cho một quota hoặc coverage sau QA không đạt mục đích pilot, ghi kết quả thiếu và dừng release liên quan; owner chỉ định task/version mới. Không mở lại chuỗi review Roboflow hoặc bổ sung detector-training/temporal/tracking/web.

## 2. Membership và coverage từng nguồn

| Phần | Đưa vào vòng preparation | Coverage đã có hoặc cần review | Không được suy ra |
|---|---|---|---|
| Roboflow v1 | Chính xác 28 ID ở phụ lục A trên 21 ảnh; lấy snapshot `current_person_crops` | Đã có 24 phone positive, 5 looking positive, một co-occurrence; 23 looking unknown + 4 phone unknown | Không có negative/normal được duyệt; duyệt crop không phải release acceptance |
| SCB Head / TurnHead (source ID 1) | 28 candidate từ strict-valid nguồn train | Tìm looking positives; review phone độc lập, có thể negative/unknown | Không map TurnHead hàng loạt; không suy thời lượng |
| SCB HRW / read (source ID 1) | 28 candidate từ strict-valid nguồn train | Tìm cảnh làm bài, negative từng target và normal đã review | read không tự là normal; thiếu phone label không phải phone negative |
| SCB HRW / write (source ID 2) | 28 candidate từ strict-valid nguồn train | Tương tự read; thêm coverage cảnh viết/bàn/tay | Cúi đầu/giữ bút không chứng minh absence hai target |
| Discuss / BowHead / hand-raising | Không có quota riêng trong v1; Discuss không được chọn | Các tư thế này có thể xuất hiện quanh người được chọn; target người đó vẫn cần review | Không thêm candidate vì thấy lớp ngoài quota hoặc dùng group box làm person box |

Nguồn SCB có thể cho phone positive nếu review có bằng chứng thật; không ép nguồn chỉ mang một target. Roboflow vẫn giữ cả 5 looking positives. Coverage báo cáo theo **target × state × source × split × leakage group**, không chỉ tổng crop; co-occurrence và normal có bảng riêng. Quy mô hoặc class nguồn không chứng minh các tình huống độc lập. Domain gap/nguồn phone positive lệch về Roboflow phải ghi trong dataset card.

### 2.1 Pin nguồn và bảo toàn provenance

- SCB dùng đúng hai ZIP đã audit: HRW SHA `46619af0c0dea011b09b8d50f4c0578420b881b5154e9d11f0447760193a208d`; Head SHA `a0fdd6637fb286cbc5d3de83c09f4143686eab0da4d92e4d8007b6b14b3ca828`. Discuss không tham gia. [Card SCB](candidates/SCB5-supplied-20261003.md) và [audit bundle](../../artifacts/reports/scb-20261003/audit.json) giữ tên archive/provenance.
- Roboflow dùng v1 ZIP SHA `70060bfe7d65dedcca6a72aaac423c95f402369eec08563b24ae8d962e666eed`; [review bundle](../../artifacts/reports/roboflow-20261004/review.json) là snapshot crop/target cuối, không lấy summary trung gian. Giữ source image/crop SHA, bbox/context và owner_answers từng record; pin SHA của bundle và toàn bộ input khi lập selection manifest.
- Quyền SCB đã owner xác nhận; không hỏi lại. Roboflow giữ attribution/license record của nguồn và review quyền cho phạm vi release cụ thể; quyết định watermark không thay thế consent/phạm vi phân phối. V1 triển khai cục bộ, không upload/phân phối media nếu chưa có policy cho hành động đó.
- Raw/archive bất biến. Audit giải nén hiện tại chỉ là input kiểm chứng; output mới đi vào version mới ở `data/interim`/`data/processed`. Không ghi đè media, review bundle hoặc manifest lịch sử.

### 2.2 Quy tắc chọn 84 SCB candidate

1. Tái sử dụng inventory strict-valid trong head/hrw audit; chỉ lấy `images/train/` và đúng source ID trong bảng. Không lấy source val/test, không cứu file geometry lỗi ở v1, không đổi epsilon/clip bbox nguồn. Bỏ source box không hợp lệ; không dùng tên/prefix để gán group.
2. Candidate identity là `(source_archive_sha256, source_image_relpath, source_label_relpath, source_label_line_1based)`. Kiểm lại bytes/hash và dòng anchor với audit trước selection. `source_label_line_1based` chỉ là provenance, không phải person ID.
3. Rank ổn định bằng SHA-256 UTF-8 của chuỗi `pilot-b-selection-v1|source_archive_sha256|source_image_sha256|source_label_relpath|source_label_line_1based`; dùng hash hex tăng dần, tie-break bằng candidate identity. Đây là quy tắc chọn candidate, **không phải seed/split algorithm hoặc quyết định training**.
4. Mỗi stratum giữ anchor có rank nhỏ nhất trên mỗi source image SHA. Chọn round-robin theo thứ tự TurnHead → read → write trong tối đa 28 vòng; mỗi lượt lấy candidate rank nhỏ nhất còn lại có image SHA chưa chọn ở bất kỳ stratum nào. Một ảnh exact unique chỉ đóng góp một SCB candidate v1. Nếu thiếu unique image, báo shortage, không âm thầm thay quota.
5. Freeze `selection.jsonl` đủ 84 candidate khi chọn đủ, kèm hash, anchor, stratum, rank/reason và mọi alias exact duplicate. Mỗi selected anchor chỉ tạo tối đa một person/crop record; không tự thêm người ngoài anchor. Near duplicates có thể còn trong selection; bước group/QA phải xử lý, không gọi 84 ảnh là 84 tình huống độc lập.
6. Review toàn bộ selection trong **một bộ preparation chung**; mỗi record nhận approved/unknown/excluded với evidence. Không sinh launcher theo batch. Nếu anchor không xác định được một người duy nhất, loại với lý do; bbox nguồn phải được vẽ lại thành visible-person khi cần. Không map source label thành target trong bước chọn.

Selection cụ thể84 ID/path/hash đã freeze ở S2 vàowner nghiệm thu trong release v4; đường dẫn/checksum trong runbook. Selection deterministic theo bytes/input đã pin; thứ tự filesystem không ảnh hưởng membership. Tăng đa dạng/đổi selection cần version/review mới; không thay tập v1 âm thầm.

## 3. Target encoding và điều kiện sử dụng

### 3.1 Lưu nhãn

Canonical lưu **state có tên**, mỗi target đúng một trong `positive`, `negative`, `unknown`. Mọi known state phải có owner review/evidence trên **crop được dùng**; unknown có lý do. Unknown không phải exclusion tự động và không phải negative. Exclusion là disposition riêng cho identity/geometry/rights/evidence không đạt.

| State | Giá trị nullable khi export | Mask | Ý nghĩa |
|---|---:|---:|---|
| positive | 1 | 1 | Bằng chứng target được owner duyệt |
| negative | 0 | 1 | Absence target đã review, vùng bằng chứng đủ quan sát |
| unknown | null | 0 | Chưa review, mơ hồ, che/mờ hoặc không gắn được bằng chứng |

Thứ tự thiết kế vector là **`[phone_use, looking_around]`**, lưu trong schema/label encoding version riêng; không lấy ID 0/1/2 trong label-map YOLO legacy làm vị trí. Canonical là state có tên; values/mask được derive và validator kiểm tương ứng. Khi loader cần dense tensor, placeholder cho unknown chỉ là chi tiết kỹ thuật nằm sau mask; không ghi unknown thành canonical 0 hoặc tính loss/metric trên nó.

Masked supervision chỉ nhận target có mask=1; loss được tính trên tập target đã biết, với normalization được Model Lead/owner chốt trong config training sau. Một crop known một target có thể cung cấp supervision cho target đó; crop `[unknown, unknown]` giữ `review_only`. Metric theo từng target lọc mask=1 và báo số positive/negative/unknown bị bỏ qua; báo unavailable nếu support không đủ cho metric. Metric joint/exact-match chỉ tính trên crop đủ hai target, báo denominator rõ; không lấp unknown để đánh giá co-occurrence.

### 3.2 Normal và review evidence

- `normal` là kết quả review/metadata, **không phải output thứ ba loại trừ hai target**: cần hai target negative **và** review xác nhận người đang làm bài.
- Lưu `work_context_review` với `confirmed_working`, `confirmed_other`, `unknown` và reviewer/evidence. `normal_review` là `confirmed_normal`, `not_normal` hoặc `unknown`: confirmed_normal chỉ khi cả hai negative + confirmed_working; có positive hoặc confirmed_other thì not_normal; phần còn lại unknown.
- Hai negative nhưng context làm bài chưa xác nhận không tự tạo normal. Cảnh ngoài scope không được giữ chỉ để thêm negative. Normal không cùng positive; source label read/write/No cheating không cung cấp absence review.
- Negative cần review target tương ứng với đủ thông tin quan sát; vật/tay bị che, người không có box hoặc chỉ cúi đọc/viết không đủ. Positive không chứng minh target kia negative. Nhãn theo ảnh tĩnh không suy thời lượng, ý định hoặc vi phạm.

### 3.3 Eligibility là các gate độc lập

Một crop được đưa vào **manifest sử dụng** khi: provenance/source rights cho phạm vi này hợp lệ; ảnh decode/hash khớp; person/crop QA được owner duyệt; target review trên đúng crop có ít nhất một known state; không bị excluded; group/split gate đạt cho usage yêu cầu. Approval crop cũ được bảo toàn, không tự nâng training_eligible trong snapshot lịch sử.

| Tình trạng | Usage | Split | Có dùng loss/metric? |
|---|---|---|---|
| Chưa QA, cả hai unknown, group/rights chưa đạt hoặc đang chờ quyết định | review_only | null | Không |
| Bị loại (disposition và reason bắt buộc) | excluded | null | Không |
| Crop đạt QA + có known target + group đủ evidence + dataset release owner ký + assignment train | train | train | Loss chỉ target known |
| Cùng gates, assignment val | val | val | Validation chỉ target known; không tham gia training |
| Cùng gates, assignment test đã freeze | test | test | Chỉ evaluation cuối theo protocol; không tuning |

`training_eligible=true` **chỉ cho usage=train** sau release acceptance; val/test có evaluation eligibility riêng. Review-only/excluded vẫn nằm trong decision ledger nhưng không xuất media vào split training. Một RF crop có target unknown vẫn có thể dùng target positive đã biết khi mọi gate còn lại đạt; không yêu cầu biến target còn lại thành negative hoặc review lại 28 approval.

## 4. Schema và layout package dự kiến

Schema JSONL thiết kế `pilot-b-manifest-v1` phải được hiện thực bằng structured schema trong `src/`, kèm producer/consumer/fixture trong cùng task. Các field bắt buộc:

| Nhóm | Field/contract |
|---|---|
| Identity/version | schema_version, sample_id unique toàn package, dataset_version, selection_version, target_encoding_version, crop_policy_version, split_version nullable |
| Source | source_id, archive SHA, image/label relative path và SHA; image width/height; source annotation line/class khi có; aliases exact duplicate |
| Person/crop | person_id cục bộ ảnh, visible-person XYXY; context-crop XYXY; crop relative path/SHA; person/crop approval, reviewer, reviewed_at và evidence reference |
| Targets | Hai target state có tên; reviewer/evidence cho từng known state, reason cho unknown; work_context_review và normal_review; values/mask chỉ derive từ state |
| Group/split | leakage_group_id nullable, group evidence và owner review; video/session/room/subject nullable nếu không biết; split nullable, usage, lý do không eligible |
| Decision/rights | disposition, exclusion reason nếu có, owner decision reference, license/attribution record, approved use scope |

XYXY theo pixel nguồn, integer, gốc trên trái, half-open `[xmin,ymin,xmax,ymax)`, `0 ≤ xmin < xmax ≤ width`, tương tự y; không trộn tọa độ crop với tọa độ source. `leakage_group_id` là nhóm chống leakage có evidence, **không phải danh tính hoặc session bị bịa**. Tên/path package dùng ID kỹ thuật, không tên/mã sinh viên; mọi đường dẫn package là relative, không hard-code đường dẫn máy owner.

Layout mục tiêu ở `data/processed/pilot-b/<dataset_version>/` (ignored, DVC khi được phép):

```text
dataset-card.md
release.json                 # state, versions, owner decision, scope, limitations
manifest.jsonl               # records được dùng với train/val/test
review-ledger.jsonl          # toàn bộ 112 candidate/approved-input decisions
selection.jsonl              # 84 SCB candidates + provenance; RF exact ID set được pin
crop-policy.json
target-encoding.json
split-assignment.jsonl       # chỉ xuất/freeze khi group gate đạt
crops/<sample_id>.png
reports/qa.json
reports/coverage.json
reports/leakage.json
checksums.sha256
```

Layout này đã được exporter B hiện thực; CLI staging/API reviewed export ở preparation runbook. Không sử dụng YOLO `labels/*.txt` hay `dataset.yaml` detection làm nhãn classifier. Package staging được ghi `prepared_pending_gates`, manifest sử dụng/split chưa có nếu gate chưa đạt; không gắn label “release training” cho staging. Rebuild phải từ pinned raw/review/config, không cần các launcher lịch sử; hash payload/config/membership phải giống nhau, timestamps thao tác ghi ngoài payload deterministic.

## 5. Crop policy `pilot-b-reviewed-context-v1`

Workflow cập nhật theo yêu cầu owner 2026-10-05: Codex tự tạo crop/target **đề xuất** từ source class/bbox/metadata, owner nghiệm thu batch và ngoại lệ qua báo cáo. Không yêu cầu owner thao tác HTML/Canvas hoặc vẽ từng crop. Rule đề xuất hiện tại cắt bbox nguồn với tọa độ integer bao ngoài, không padding; đây chưa phải visible-person/context policy đã duyệt. Source-class suggestions nằm riêng, không thay target canonical/normal hoặc bỏ các gate bên dưới.

1. **Person bbox** bao các phần nhìn thấy của đúng người, không ước lượng cơ thể dưới bàn; giữ riêng **context crop** có thể gồm bàn/tay/phone liên quan. Crop phải chứa person bbox và bằng chứng được dùng để duyệt target; không làm bbox person phình thành vùng bàn.
2. RF giữ nguyên 28 approved person/context coordinates và target approvals từ snapshot. SCB review visible-person và context cho người anchor ở độ phân giải gốc; không biến source action box thành person box bằng padding. Bằng chứng liên quan người khác không được gán cho anchor; context có người khác cần review attribution từng target.
3. Bbox/crop phải có geometry hợp lệ, không zero/out-of-bounds; crop bytes/hash và provenance kiểm được. Với source box warning, v1 không tự sửa/clip; với context mới reviewer xác định rectangle trong ảnh. Không đặt ngưỡng pixel/occlusion hoặc margin số khi chưa có evidence được owner duyệt.
4. Target được review trên **đúng crop**, có thể mở source để kiểm attribution. Nếu target chỉ thấy ngoài crop, sửa crop và review version mới hoặc giữ target unknown; không dùng full-image label cho crop làm mất evidence. Không reshape/cắt thêm trước review làm thay target. Resize/normalization/augmentation là config training sau, chưa chốt ở contract này.
5. Owner duyệt crop/evidence tại preparation; record không cần annotate mọi người ngoài crop. Dataset train detector person riêng cần hợp đồng completeness khác, không thuộc pilot.

**Gate runtime `TBD-PB-CROP-RUNTIME`:** package này là crop đã review, không chứng minh thuật toán crop tự động. Owner phải duyệt quy tắc lấy context từ person detector, QA coverage bằng chứng/attribution và lưu version trước baseline B end-to-end. Runtime rule không được dùng annotation phone hoặc target ground truth, không được gán phone gần nhất. Không tự chọn model/weights detector hoặc padding để đóng TBD. Khi runtime crop khác crop đã duyệt, tạo crop version mới và re-review target; không mang nhãn sang vô điều kiện. Pilot packaging hoàn tất và runtime readiness là hai trạng thái riêng theo ADR-013.

## 6. Split policy và test freeze

1. Không giữ split cũ khi hợp nguồn; original split chỉ giữ trong provenance và giới hạn pool selection, không phải split mới. Exact image duplicates/aliases giữa Head/HRW phải dedup trước selection; mọi crop từ cùng ảnh, near-duplicate liên quan, cùng video/session/room/person theo metadata đáng tin và augmentation liên quan không được vắt qua split.
2. Lập leakage graph: node là source image identity; edge có evidence cho exact duplicate, near-duplicate được review hoặc quan hệ group đã xác minh. Connected component dùng chung leakage_group_id. Quan hệ cross-source cũng phải kiểm. Exact hash/triage similarity không tự chứng minh independence; similarity threshold và công cụ mới nếu cần phải có config/review, không tự đặt ngưỡng như đã approved.
3. Group evidence ghi nguồn metadata hoặc quyết định owner về cluster chống leakage. Session/video thực chưa biết để null. **Không suy nhóm từ filename, không coi mỗi hash unique là một group độc lập.** Chưa chứng minh được tính độc lập thì split=null, usage=review_only; thiếu group là blocker release training, không là cớ random-split crop.
4. Sau group QA, owner review coverage theo source/target/state/group và chốt `TBD-PB-SPLIT-CONFIG`: ratio, seed, assignment algorithm/config và split version. 70/15/15, seed 42 đang xuất hiện ở draft/legacy **chỉ là đề xuất**, không được dùng như quyết định accepted. Có thể tái sử dụng stable-hash grouping hiện có khi config và output đã review; constrained assignment phải là version mới có evidence, không di chuyển frame lẻ.
5. Assignment xác định theo toàn group, deterministic với config đã pin; thứ tự rows không đổi output. Mọi RF người cùng P006/P007/P008/P029/P047 ở một split; các ảnh cùng group cũng vậy. Report kiểm identity/crop/group overlap và gần trùng giữa mọi cặp split; unresolved leakage chặn freeze.
6. Owner ký freeze test bằng manifest/split/config SHA, Git commit, thời điểm và protocol truy cập. Test không dùng cho epoch/model/augmentation/threshold, chọn quota hay điều chỉnh selection sau khi freeze; thay đổi cần version mới và không được coi test đã dùng là holdout chưa nhìn. Audit/annotation QA trước freeze không phải model tuning. Local exam-like holdout là artifact riêng, không merge vào pilot train.

Nếu chỉ có staging review-only, báo đúng trạng thái; không tạo split giả để đủ ba thư mục hoặc tuyên bố test độc lập. Phone positives có thể tập trung ở nguồn/group Roboflow; không tách group để ép tỷ lệ hay class coverage.

## 7. Tiêu chí hoàn thành và trạng thái

**Task thiết kế hiện tại hoàn tất** khi hợp đồng ghi rõ scope/coverage, encoding/eligibility, crop/split, các gate và backlog; owner choices được lưu ADR/TASK; liên kết tài liệu/diff được kiểm. Không cần model result, media build hoặc DVC để hoàn thành thiết kế.

**Preparation hữu hạn hoàn tất** khi ledger có quyết định cho đúng 28 RF + 84 SCB, không record mất/được thêm; selection/provenance và crop/target QA có owner evidence; mọi unknown/reject/shortage được báo. Thiếu crop dùng được không tự kéo dài review. Có thể kết thúc preparation với kết luận **không đủ điều kiện release** và backlog/blocker cụ thể; không biến thất bại gate thành thành công release.

**Dataset pilot release cho classifier chỉ được ký** khi tất cả điều kiện sau đạt:

- Scope/schema/encoding/config và mọi record sử dụng đã owner review; provenance/rights theo use scope, crop/evidence và nullable-mask validation pass. Giữ đúng RF membership ledger và positives; SCB targets hoàn toàn từ review.
- Coverage report có actual counts: eligible/review-only/excluded; P/N/U mỗi target/source/split/group; normal, co-occurrence, fully/partially labeled và domain slices. Có positive và negative được review cho mỗi target được train; **không dùng 24/84/112 như acceptance metric model**. Nếu thiếu coverage cần thiết cho mục đích pilot, owner ghi chưa release thay vì đổi semantics/threshold để chạy.
- Group evidence, dedup/near-duplicate review, split config/assignment owner chốt; test freeze và leakage checks pass. Val/test metric thiếu support phải được báo không đánh giá được, không điền số giả hoặc ép split. Dataset card phải nêu rõ giới hạn đánh giá của pilot; chưa là gate promotion model.
- Builder B và schema/consumer tests kiểm được unknown, co-occurrence, normal, geometry, identity, eligibility và group leakage; rebuild/checksum payload deterministic pass. Không gọi builder YOLO legacy với config B để export.
- Dataset card/release.json ghi owner decision, Git/config/dataset/selection/target/crop/split versions, hashes và limitations. Pointer/version mới; DVC push/pull từ checkout/cache sạch chứng minh payload identical **khi remote/privacy policy cho phép**. Nếu chưa cho phép remote, ghi blocker; không upload để vượt gate.

Baseline classifier trên reviewed crops chỉ được xét ở task training có config/experiment đầy đủ; **baseline B end-to-end còn phải đạt crop runtime gate**. P0 round-trip, P1/P2 và model acceptance không tự đóng bằng hợp đồng hoặc test code pass.

## 8. Backlog triển khai hữu hạn

Một workflow preparation chung, canonical logic trong `src/`; không script theo ngày/batch. Task sau chỉ làm S1–S8, kết thúc bằng report/release hoặc kết luận blocked có evidence; S9 là gate độc lập trước end-to-end baseline.

| ID | Công việc / owner | Dependency | Output và điều kiện xong |
|---|---|---|---|
| S1 | Pin input/provenance/use scope — owner + Codex | ADR-013 | Hash archives/bundles/crop inputs; exact 28 RF; quyền SCB giữ nguyên; Roboflow/remote scope có decision hoặc blocker |
| S2 | Select 84 SCB anchors deterministic — Codex, owner review selection | S1 | selection.jsonl 28/28/28, source row/hash/aliases; không mutate raw/refill; shortage báo rõ |
| S3 | Hiện thực structured schema, codec/validator và config B riêng — Codex, owner review | S1–S2 | Versioned schema/config/fixtures cho state/null/mask/normal/geometry/usage; legacy builder giữ gate B |
| S4 | Tự tạo một batch crop/target proposals — Codex thực hiện, owner nghiệm thu | S2–S3 | Đúng 84 SCB đề xuất + 28 RF giữ approvals; báo cáo/ngoại lệ một lần, owner Approve/Reject; known/unknown/excluded chỉ nhập canonical sau xác nhận |
| S5 | Dedup/leakage graph và group review — Codex + owner | S4 | group manifest + evidence/report; unresolved records review_only; không session giả |
| S6 | Chốt split config, coverage review và freeze test — owner, Codex hỗ trợ | S5 | Owner decisions/assignment/version/hashes/protocol; hoặc report chặn release do group/coverage |
| S7 | Builder classifier B và validation/rebuild — Codex | S3–S6 | Package layout/checksums/card/report; meaningful tests/masked fixtures và rebuild deterministic pass; không train |
| S8 | Owner ký release/pointer + DVC round-trip — owner + Codex | S7 và remote/privacy gate | Release decision/version; push/pull sạch có evidence hoặc blocker ghi rõ; không tự Accepted |
| S9 | Chốt và QA crop runtime không phụ thuộc target annotation — owner + Codex | Trước baseline B end-to-end | Crop runtime version/QA và re-review crop đổi; cần decision model/config riêng, chưa train trong preparation |

## 9. TBD còn lại (không phải giá trị mặc định)

Release local v4 đã chốt S1–S7 vàký pointer local S8. Bảng dưới phân biệt gate đã resolved cho subset sử dụng với remote/runtime chưa được phép.

| ID | Owner | Lý do / điều kiện chốt | Chặn gì |
|---|---|---|---|
| TBD-PB-MEMBERSHIP (resolved v4) | Owner | Exact SCB84 + RF28 ledger;84 used/28review_only đã duyệt | Không chặn release local |
| TBD-PB-GROUP (resolved cho84used) | Owner | 16 conservative visual components/boundaries đã chấp nhận, giữ14 must-links;28 unresolved không sử dụng | Không chặn84used;28 record vẫn review_only |
| TBD-PB-SPLIT-CONFIG (resolved v4) | Owner | Explicit whole-group60/13/11,seed=null,soft70/15/15;test freeze hashes/protocol trong release.json | Không chặn release local |
| TBD-PB-CROP-RUNTIME | Owner | Chưa có automatic context policy/QA; S9 không dùng annotation phone | Baseline B end-to-end; không chặn package reviewed-crop theo ADR-013 |
| TBD-PB-COVERAGE (resolved cho local classifier pilot) | Owner | Phone24P9N79U,looking33P56N23U,9normal;train/val/test có P/N cho cả hai target;support nhỏ/confounding được báo | Không là model promotion/generalization gate |
| TBD-PB-EXPORT (resolved v4) | Owner + Codex | Schema/config/release đã duyệt;108 tests/pixels/hash/rebuild/freeze pass | Không chặn release local |
| TBD-PB-RELEASE-SCOPE (local/storage scope resolved) | Owner | local_classifier_research + attribution đã duyệt; owner cho phép DVC storage đúng v4 trên teamdrive restricted, evidence/runbook ghi ngoài immutable payload | S8 round-trip theo WORKLOG; không cho redistribution/W&B hoặc thu thập mới |

## Phụ lục A — Đúng 28 RF record được đưa vào ledger

P = positive đã owner duyệt; U = unknown; không có negative. Toàn bộ source paths/SHA/person bbox/crop bbox/crop SHA/owner answers lấy nguyên từ `current_person_crops` trong review bundle. ID table là membership contract; bảng không nâng training eligibility của evidence cũ.

| ID | phone_use | looking_around |
|---|---|---|
| P002-person-01 | P | U |
| P006-person-01 | P | U |
| P006-person-02 | P | U |
| P006-extra-01 | U | P |
| P007-person-01 | P | U |
| P007-person-02 | P | U |
| P007-extra-01 | U | P |
| P008-person-01 | P | U |
| P008-extra-01 | U | P |
| P009-person-01 | P | U |
| P019-person-01 | P | U |
| P022-person-01 | P | U |
| P023-person-01 | P | U |
| P028-person-01 | P | U |
| P029-person-01 | P | U |
| P029-person-02 | P | U |
| P030-person-01 | P | U |
| P031-person-01 | P | U |
| P032-person-01 | P | U |
| P033-person-01 | P | P |
| P034-person-01 | P | U |
| P035-person-01 | P | U |
| P036-person-01 | P | U |
| P038-person-01 | P | U |
| P039-person-01 | P | U |
| P043-person-01 | P | U |
| P047-person-01 | P | U |
| P047-extra-01 | U | P |
