# V7 có đáp ứng mục tiêu E004 không?

**Chưa đáp ứng đầy đủ. V7 đã đạt phần release dữ liệu cho pilot local và cải thiện tập train, nhưng mới đáp ứng một phần targeted expansion; chưa đủ bằng chứng đánh giá để kết luận E004 tạo “bước nhảy” hoặc có quyền xét promotion.**

Audit ngày 2026-10-10 theo yêu cầu owner. Đã kiểm actual manifest/ledger, pins/checksum release, 12cell corrections, P/N/U và tổ hợp, source/group concentration, domain/phenotype evidence, pair/224 joins, development comparator, E004 config và code model. Không sửa release/label/split, chạy training, tính prediction mới hoặc mở media test. [Số đo đầy đủ](measured-audit.json), [bổ sung targeted evidence](targeted-evidence-addendum.json), [input pins](input-pins.json).

## 1. Mục tiêu nào đã đạt?

Source of truth: [E004-preparation](../../../docs/experiments/E004-preparation.md), [plan E004](../../../configs/experiments/E004-plan.yaml), [acquisition v7 lịch sử](../../../configs/datasets/pilot_b_v7_targeted_plan.yaml), [R8 có điều kiện](../../../configs/datasets/pilot_b_v7_r8_conditional_plan_20261009.yaml), [ADR017 Draft](../../../docs/decisions/ADR-017-e004-classifier-promotion-gates.md).

| Mục tiêu | Kết quả v7 | Kết luận |
|---|---|---|
| Release/crop/annotation/rights/split có nghiệm thu và checksum | Accepted local, 689train/49val/11test; 749manifest/900ledger, U masked và blocker ngoài train | Đạt trong scope pilot local |
| Rà 12cell lỗi/ambiguous của E003, bảo toàn v6 | Cả 12 có owner decision; corrections/exclusion được materialize vào v7, source/crop giữ nguyên | Đạt |
| Tăng dữ liệu học đúng các failure modes | Thêm 375 crop train, phone141P/93N, looking97P/163N; có desk/held/at-ear, ownworkarea, crowded và bốn tổ hợp | Có tiến bộ, chưa chứng minh coverage đủ trong primary exam domain |
| Giảm nguồn quyết định nhãn, tăng nhãn đủ hai target | Counts tăng; tỷ lệ fully-known gần như giữ nguyên, polarity theo nguồn vẫn lệch | Đạt một phần |
| Cặp P/N cùng cảnh/camera/workarea | Có thêm same-image cases; phần lớn 162 pair lịch sử chỉ source-context | Đạt một phần, chưa giải quyết matched session/camera diversity |
| Người/phòng/camera/session độc lập mới |375 train groups đăng ký nhưng new independence proven=0; manifest session/video/room/subject đều null | Chưa đạt yêu cầu bằng chứng độc lập |
| Development bổ sung whole-group trước recipe chạy | 0 record validation mới; 49val là dữ liệu lịch sử sau sửa nhãn | Chưa có new-development như hướng E004 ban đầu |
| Holdout public độc lập đủ rights/provenance/support | E004 holdout_package=null; 11test vẫn historical integrity-only | Chưa đạt |
| Fine-tune layer4 + control matched recipe + cải thiện thật | Trainer hiện frozen encoder/linear head; chưa run E004 | Chưa triển khai/kiểm chứng |

Budget 80/80/100/40 ban đầu là budget review Draft, **không là quota accepted**. Owner đã duyệt R8 dùng actual yield/diversity/shortage, không bắt bù số crop. Audit không kết luận thất bại vì thiếu một số lượng tùy ý; kết luận dựa coverage/evidence/evaluation thật. Release local689/49/11 đã được owner ký hợp lệ; approval ấy không chứng minh diversity/holdout/model gain mà E004 muốn.

## 2. Train đã cải thiện gì, và cải thiện tới đâu?

Đếm lại từ actual manifests, không lấy summary proposal làm kết quả release:

| Chỉ số train | V6 | V7 |
|---|---:|---:|
| Crop train |317|689|
| Phone P / N / U |93 /91 /133|233 /184 /272|
| Looking P / N / U |117 /112 /88|210 /277 /202|
| Fully-known |96 (30,3%)|215 (31,2%)|
| Chỉ known một target |221 (69,7%)|474 (68,8%)|
| PP / PN / NP / NN |16 /3 /23 /54|36 /16 /32 /131|
| Registered groups |103|375|
| Nhóm train lớn nhất |91crop (28,7%)|91crop (13,2%)|

V7 có tăng bằng chứng supervision thật; không chỉ thêm unknown. 375 crop mới có 119fully-known/256partially-known/0U-U trong train. PN tăng3→16 và PP16→36 có ích cho disentangling hai target. Tuy nhiên, **fully-known tăng về số nhưng chỉ tăng khoảng 0,9 điểm phần trăm về tỷ lệ**; gần 69% train vẫn chỉ supervised một target. Không dùng những target unknown còn lại làm negative.

Nhóm Student91crop không giảm hay tách; tỷ trọng giảm do mẫu khác tăng. Đây là cải thiện concentration theo số crop, không chứng minh 291 nhóm mới độc lập. 375 crop mới nằm trong 289 component đã đăng ký; nhiều ảnh/person/series vẫn chung scene hoặc liên hệ parent.

Trong 375 newtrain, metadata ghi 196 `classroom_or_exam_context`,127 `auxiliary_out_of_exam`, 52 học tập/workshop/home/public-context khác hoặc pending domain. 189 crop đến từ COCO/OI/Commons/video public. Nguồn public không đồng nghĩa ngoài classroom, còn tagclassroom cũng **không chứng minh cảnh thi thật/CCTV/camera mới**: stock và mô phỏng nằm trong tag rộng. Phần auxiliary có ích cho representation nhưng không được dùng để tuyên bố đã lấp domain gap của E004.

## 3. Source confounding vẫn chưa được giải quyết

| Source, train v7 | Phone P / N / U | Looking P / N / U | Điểm cần lưu ý |
|---|---|---|---|
| SCB Head65 |0 /4 /61|53 /12 /0|Looking vẫn thiên positive; tốt hơn34P/1N của v6 nhưng chưa cân ngữ cảnh |
| SCB HRW87 |0 /23 /64|3 /81 /3|Looking vẫn gần như toàn negative:81/84known |
| Classroom Attitude108 |83 /16 /9|15 /21 /72| Phone 83/99 known là P; looking phần lớn U |
| Student115 |42 /35 /38|44 /38 /33| Số P không tăng so v6; thêm N nhưng nhóm 91 crop vẫn giữ |
| Open Images104 |27 /36 /41|24 /53 /27| CóP/N hỗ trợ đa dạng, phần lớn auxiliary, không thay exam holdout |

Overall P/N khá đầy đủ không xóa lệch **bên trong nguồn**. Nhận xét ở đây là rủi ro confounding từ distribution, không là kết luận causal rằng model đã học shortcut. Cần matched P/N theo đúng room/workarea và kiểm slice trên dữ liệu mới trước khi khẳng định đã xử lý nguyên nhân E003.

## 4. Desk-phone, small/partial, crowded và matched pairs

Có thêm đúng những kiểu cần học: PF-A002 phone trên bàn cạnh người viết; S066-A02 mobile/page của đúng nữ; S102-A02 và S116-A01 mobile trên bàn của anchor; phone cầm thấp/áp tai/che tay và các crop ownpage-negative. Đã mở lại 6 native 224 boards 01/03/04/05/06/07 chứa các case này và workshop/lab/stock variants. Owner annotations giữ nguyên.

Nhưng các phone-on-desk của bootcamp/YIRWA là workshop/lab; homework là auxiliary home. S102/S116 thuộc cùng desk-simulation family đã nối parent, không phải camera/session mới. S066 hai người cùng ảnh và PF-A002 learning scene giúp evidence nhưng không tự đóng independence. **Có gain về kiểu evidence; chưa đủ căn cứ nói thiếu desk-phone trong domain thi thật đã hết.**

Con số 6P/6N trong audit R5 là một subset lịch sử, không phải tổng v7. Join current release cho subset bucketA/classroom của R5 còn 11crop=6P/5N, do A006 bị evaluation-family exclusion. New R3 có thêm desk cases ngoài subset đó. Toàn 375 newtrain chưa có taxonomy phenotype/phone-context/ownworkarea/camera-session được đo và pin đầy đủ theo schema phân tích E004; vì vậy tổng support final của từng targeted slice và independent-group support còn **chưa đo đủ**, không bịa một con số đủ gate.

[Pair join](pair-join.json) kiểm labels/usage mới: 162 R5 pair chỉ còn 138 pair cả hai endpointtrain và đúng P/N. Trong 138: 132 source-context,5 same-image,1 same-scene. Source-context chỉ là giống bút/giấy/tay/ngữ cảnh rộng, không cùng session/camera. Có 2 R5 extra pairs,4 R8 pairs (3 còn hợp lệ, C005U/U làm 1 cặp mất polarity), 1 publicsame-image pair và 1 Kiwixsame-room/sessionproposal lịch sử; không cộng các nhóm này vì có overlap với exact-image pairs.

Derive từ 375 newtrain có 22 cặp P/N raw trên 19 exact-source images (phone 5 pair/ 5 images; looking 17 pair/ 16 images). Đây là gain thật về tương phản trong cùng ảnh, **không là 22 session độc lập hoặc 22 matchedpairs trong primary exam domain**. Chi tiết endpoint/target ở [addendum](targeted-evidence-addendum.json).

Input224 generation/pixel equality đã PASS trong release. Quality tại 224 là chuyện riêng: 119 finding lịch sử B/D chỉ 104 finding có crop SHA khớp current train; trong 104 có 94 clear/ 10 ambiguous. 4 recrop SHA khác không được gán annotation 224 cũ sang crop mới. Các recrop có QA/ ownerapproval mới, nhưng audit không coi historical 119 field là coverage toàn 375. Việc thêm hardcases và file 224 khớp không chứng minh encoder nhận được phone nhỏ tốt hơn; cần controlled run/slice result để kiểm.

## 5. Evaluation vẫn là điểm thiếu quan trọng nhất

V7 không thêm validation mới. Val49 kế thừa v6 val50: V6-CA041 chuyển phone U và review-only; EXP-SCB002 looking P→N. 49val vẫn 14 groups; hai nhóm 21+10 crop chiếm **63,3%**. Phone 16P chỉ 4 groups; looking 17 P chỉ 6 groups. Không có evidence mới cho camera/session độc lập từ schema group.

E004 ban đầu đề xuất new-development whole-groups có targeted P/N trước recipe chạy. Owner sau đó chốt policylocal train-expansion, không thêm dev; release đã thực hiện đúng policy đó. Hệ quả là **phần new-development của mục tiêu nghiên cứu ban đầu chưa được giải quyết**, không phải exporter tự làm sai split. Không chuyển train sangval hoặc dùngtest11 để bù trong audit này.

Comparator cần chốt riêng. 48val IDs còn nguyên source/crop/target/mask/context/rights; EXP-SCB002 là retained record đổi nhãn, CA041 rời val. Group ID/reviewrefs được version theo whole-family v7 nên **literal evaluation identity gồmgroupreview không khớp**; oldval14 groups ánh xạ 1–1 sang 14 new group IDs. [Comparator 48 proposal](comparator-proposal.json) có IDs/support/mapping nhưng chưa là protocol freeze đượcduyệt.

Đã dùng cached E003 scores đúng SHA, không loadmodel/ inference, chỉ tái tính confusion để minh họa:

| Cùng model và cùng cached scores | Phone recall | Looking recall |
|---|---:|---:|
| V6labels/cohort50 |0,529|0,611|
| V7labels/cohort49 |0,563|0,647|

**Model không thay đổi mà recall đã tăng vì nhãn/cohort thay đổi.** Đây không làm etric E004 hoặc cải thiện model; [cache illustration](cached-score-comparator-illustration.json) ghi rõ scope. Trước train phải freeze comparatorIDs/group mapping/protocol, report annotation delta riêng và đối chiếu hai model trên cùng labels/ masks. Không so trực tiếp scalar BCE/AP trên 50 và 49 rồi quy toàn bộ delta cho fine-tuning.

Holdout độc lập vẫn chưa có (`holdout_package:null`).11test lịch sử chỉ2P/2Nknownphone,2P/7Nknownlooking,3registeredgroups; không có quyền inference mới và không thay independent holdout. Các gates 100P/100N/10groups/camera trong ADR017 là **Draft cho test**, không là ngưỡng train đã Accepted; không dùng 233 train phone P để nói test gate đạt.

## 6. Fine-tune và gates E004 chưa sẵn sàng

[Code FrozenEncoder](../../../src/ai_exam_monitoring/training/model.py) đặt `requires_grad_(False)`, giữ eval và forward `torch.no_grad()`; feature cache 512 dùng encoder đóng băng. [ExperimentConfig](../../../src/ai_exam_monitoring/training/config.py) chỉ nhận `resnet18_frozen_linear`. Vì vậy recipe mở layer4/head củaE004 chưa thể chạy chỉ bằng thay tên/model trong YAML.

Cần partial fine-tune implementation, BNpolicy, fullback bone+head checkpoint/optimizer/RNG, masked mini-batch objective và resume/evaluation tests đúng recipe, sau design approval. Control frozen và candidate phải cùng data/preprocessing/headinit/seed/budget/protocol để kiểm phần adaptation. Chưa có E004 run/metrics ⇒ mức model gain và target recall/precision chưa kiểm chứng.

| Gate ADR017 đề xuất | Thực trạng |
|---|---|
| G0 — accepted metrics/recipe/protocol | ADR017/recipe còn Draft; không đóng từ approval dataset |
| G1 — v7 và holdout Accepted, rights/QA/pins | Phần v7 local đạt; holdout còn thiếu |
| G2 — independent holdout lineage | Chưa đạt |
| G3 — testP/N/group/camera support | Chưa đạt; numeric minimum vẫn Draft |
| G4 — candidateFINISHED/fullbundle | Chưa implementation/ run E004 |
| G5 — candidate/holdoutfreeze/use-onceguard | Chưa đạt |

E004 plan vẫn Draft/null dataset pins dù release v7 đã tồn tại; đây là experiment proposal chưa resolve, không phải lỗi release. Các M1–M7/chỉ tiêu “bướcnhảy” cũng chưa Accepted/ đo; không coi 257 unit tests hoặc 883 file rebuild PASS là quality model PASS.

## 7. Việc nên ưu tiên để đạt đúng mục tiêu

1. **Đóng ma trận targeted thực tế cho 375 newtrain**: phone context/visibility/ownworkarea/primarydomain/camera-session/224 quality/matched P-N; tách auxiliary và parent family variants. Khi chưa đo support, không đặt quota mới hoặc gọi thiếu nguồn exhausted.
2. **Bổ sung bằng chứng đánh giá mới**: new-development whole-groups và holdout riêng theo policy owner chốt, đủ rights/lineage/known P-N; không đưa họ hàng eval vào train, không random split frame. Đây là phần v7 hiện chưa cung cấp.
3. **Chốt E004 protocol/recipe/metric/compute và comparator 48/groupmapping**, pin config thật; triển khai/QA fine-tune rồi chạy control+candidate. Dùng development kiểm failure modes, freeze candidate trước final holdout.

Nếu chỉ muốn thử học trên dữ liệu v7 hiện có, có thể chuẩn bị một experiment local chẩn đoán với recipe/config/approval riêng và claim giới hạn. Đó chưa hoàn tất mục tiêu E004 gồm độc lập/generalization/promotion; không tự thu hẹp mục tiêu hoặc đổi các gate để chạy.

**Kết luận nghiệm thu:** V7 là nền dữ liệu local đã hợp lệ để chuẩn bị thực nghiệm; không phải bằng chứng rằng các failure modes của E003 đã được giải quyết. Theo đúng mục tiêu E004 lưu trong repo, trạng thái là **đạt phần dataset engineering, targeted train đạt một phần, evaluation/model improvement chưa đạt**. Không cần hủy release; cần đóng những phần thiếu trên để claim đúng.
