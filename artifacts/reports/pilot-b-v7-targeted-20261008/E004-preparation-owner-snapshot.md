# E004 — Từ mở rộng số crop đến targeted data và quyền xét promotion

Ngày 2026-10-08. Owner: chủ repository (solo). **Chuẩn bị/nghiên cứu Draft; chưa có release v7, test độc lập Accepted, training hoặc quyền promotion.** Owner đã chọn classifier trên crop đã review và tìm nguồn công khai mới. [Ma trận gates đề xuất](../decisions/ADR-017-e004-classifier-promotion-gates.md), [plan experiment](../../configs/experiments/E004-plan.yaml), [plan v7](../../configs/datasets/pilot_b_v7_targeted_plan.yaml).

## 1. Kết luận từ dữ liệu thật

E001/E002/E003 đều học **linear head mới trên cùng ResNet18 đóng băng**, không phải ba lần fine-tune toàn model. Thêm dữ liệu có thể học ranh giới tốt hơn nhưng chưa làm encoder thích nghi với phone nhỏ/desk-phone/hướng nhìn. `best.pt` E003 là checkpoint head cùng pins, không chứa standalone backbone đã thích nghi. Code hiện chỉ hỗ trợ frozen linear; không đổi tên config thành fine-tune để tuyên bố đã triển khai.

Audit lần này đọc predictions đã lưu train317/val50, join schema manifest/review ledger, tái lập error list ở 0.5, kiểm SHA mọi artifact run và pixel từng crop nhận xét với source. Đã xem crop/source/input224 cho **46 FN (21 phone,25 looking) và 3 FP val,49 lỗi theo target trên 48 ảnh**. Một người có thể có hai FN. [Bảng từng lỗi](../../artifacts/reports/E004-research-20261008/e003-audit/fn-audit.md), [audit JSON/pins](../../artifacts/reports/E004-research-20261008/e003-audit/audit.json), [support/source/group](../../artifacts/reports/E004-research-20261008/e003-audit/summary.json).

Các factor dưới đây là **quan sát/hypothesis, có thể đồng thời**, không là bằng chứng nhân quả hoặc annotation Accepted mới. Không có factor không có nghĩa đã chứng minh nó vắng mặt. Blur/low-detail được phân biệt: ảnh mềm/mất chi tiết không chứng minh motion blur; `source_noise` chỉ nói chấm noise quan sát được, không tự suy phiên quay mới.

| Nhóm lỗi | Quan sát cụ thể | Hệ quả cho E004/v7 |
|---|---|---|
| Phone val 8 FN | **6/8 desk-phone**, 6/8 vật nhỏ về thị giác, 4/8 chỉ lộ một phần, 4/8 pose nghỉ/chống đầu, 3/8 context có người khác; các tập có overlap | Thiếu dạng phone presence trên bàn/sách, không chỉ phone cầm. Không đổi semantics thành “chỉ cầm mới positive”. |
| Phone train 13 FN | 12 held-phone, 11 tay che một phần, 9 vật nhỏ, 6 ngoài exam domain, 2 phone áp tai, 2 source noise; chỉ 1 desk-phone | Lỗi ngay trên train cho thấy không thể quy hết sang nguồn validation mới. Cần negatives tay gần mặt/cầm bút và nhiều camera/người mới. |
| Looking val 7 FN | 7 đầu lệch/quay bên; 5 crowded context. 6 trường hợp nhìn bên khá rõ; 1 cần rà lại đọc sách so nhìn bên | Nhiều lỗi không do mặt hoàn toàn mất/che. Cần cặp hướng nhìn-vùng bài và representation thích nghi; không hạ threshold như lời giải duy nhất. |
| Looking train 18 FN | 10 low-detail, 8 small-evidence, 9 cần rà nhãn, 4 gáy/back view, 1 nhìn lên trước; counts overlap | Tách ambiguous khỏi clear positive, bổ sung front-up/back-side có context bài đủ. Không dùng mọi turn_head/cúi đầu làm looking P. |
| FP val 3 | EX042: nghiêng đầu viết; SB047: viết/noise,score 0.50043; R2EX008: cầm bút nhìn bên,phone score 0.72816 | Targeted expansion phải kèm negatives, gồm phone N/looking P. Tăng recall bằng “mọi tay/bút/đầu quay=phone” không đạt gates. |

### Toàn bộ 8 phone FN validation

| ID | Score | Quan sát ưu tiên / việc cần làm |
|---|---:|---|
| P022-person-01 | 0.386997 | Phone nhỏ trong hai tay, chi tiết gốc ít; input224 phóng lớn, không tạo thêm thông tin. Tuyển camera xa nhưng phone còn đủ evidence. |
| V6-CA-015 | 0.488165 | Phone cầm cạnh sách, tay/sách che một phần, stock và looking đồng thời. Cần cùng dạng trong exam domain. |
| V6-CA-038 | 0.239411 | Phone trên sách sát mép dưới, người cúi nghỉ. Tuyển phone trên bàn khi không tương tác + negative nghỉ không phone. |
| V6-CA-041 | 0.421234 | Phone được approval ghi nhưng bị tay/đầu che nhiều. **Rà evidence trên crop trước**; không tự đổi P thành N hoặc U. |
| V6-CA-046 | 0.439725 | Phone ngang trên sách ở mép dưới, người chống đầu. Giữ phone presence theo ADR011. |
| V6-EX-015 | 0.390446 | Phone nhỏ trên bàn; crop cao có nhiều người. Review đúng anchor và context đủ evidence. |
| V6R2-CA-006 | 0.285788 | Phone trên bàn, tay che mặt, người khác trong crop. Cần negatives cùng pose/camera. |
| V6R2-CA-009 | 0.436952 | Phone trên giấy + quay nhìn bên; người tiền cảnh. Bổ sung cả bốn tổ hợp P/N của hai target khi đủ review. |

7/8 crop phone FN val có cạnh dài > 224 nên downsample; P022 có cạnh dài 139 nên upscale. Đây là geometry crop, **không là đo bbox phone hoặc threshold kích thước accepted**. Tăng 384 có thể giữ thêm detail của ảnh gốc lớn, nhưng không cứu crop gốc mờ hoặc attribution sai. Chưa chạy resolution ablation, chưa biết mức cải thiện.

### Group concentration và nhãn thiếu: nguyên nhân cần xử lý trước model lớn

- Train 317 có 103 leakage groups đã đăng ký, **không chứng minh 103 session/room độc lập**. Student 103 crop chỉ 12 group; một group chứa 91 crop (28.7% toàn train). Classroom Monitoring 24 crop cùng một nhóm. Bổ sung hàng chục người/frame cùng phòng có thể tăng crop count mà ít tăng đa dạng domain.
- Val50 có 14 group; hai group lớn chứa 21 và 11 crop (**64% val**). Phone 17 P chỉ nằm trong 4 group; looking 18 P nằm trong 7 group. Không tính CI như 50 mẫu iid hoặc gọi added 37 holdout.
- Train known phone 93P/91N, looking 117P/112N khá cân bằng toàn tập; không có căn cứ bắt đầu bằng class weight lớn. Confounding **trong nguồn** mới đáng lo: SCB Head looking 34P/1N; HRW 3P/59N. Student val không có P của cả hai target, trong khi train có 42 phone P và 44 looking P.
- 221/317 train và 34/50 val chỉ known một target; subject/session/room/video metadata đều null trong manifest train/val. Unknown phải mask, không tận dụng thiếu annotation làm negative. Tăng fully-known samples và provenance hữu ích hơn tăng annotation counts upstream.

## 2. Các mẫu cần owner rà lại — một gói review, không bắt owner vẽ từng bbox

**12cell:** phone val `V6-CA-041`; looking val `EXP-SCB-002`; phone train `EXP-RF-014`; looking train `EXP-SCB-032`, `SCB-turnhead-007/009/012/019/020/021/023`, `V6R2-MP-059`. Có 11 cell ambiguous-label và 1 crop/text conflict. Chưa xác nhận bất kỳ label nào sai.

`EXP-RF-014` có phụ đề trong crop train, trong khi ADR011/R16 quy định loại ảnh phụ đề/UI. Có approval crop R2 ngày2026-10-06 và release v6 sau đó, nhưng chưa thấy decision ghi rõ ngoại lệ đối với ADR. **Báo mâu thuẫn, không tự sửa ADR hoặc v6.** Đề xuất v7 recrop phần text nếu vẫn giữ visible person/phone evidence, hoặc quarantine record tới khi owner chốt. Source/parent và approval lịch sử giữ nguyên. Rà các mẫu khác phải xem đủ source, crop và scale model; sửa nhãn/crop cần version/pointer mới và owner quyết định.

Ảnh review tái lập local ở `outputs/E004-research-20261008/review-final/`, 13 sheets và media-checksums. Đây là media ignored, không commit/upload. Codex tạo Draft nhận xét/geometry, owner nghiệm thu toàn batch và exceptions; không yêu cầu thao tác annotation thủ công.

**Kết quả review của onwer**: 

| ID | Kết luận | 
|---|---|
| `V6-CA-041` | U |
| `EXP-SCB-002` | N |
| `EXP-RF-014` | excluded |
| `EXP-SCB-032` | U |
| `SCB-turnhead-007` | P |
| `SCB-turnhead-009` | P |
| `SCB-turnhead-012` | P |
| `SCB-turnhead-019` | P |
| `SCB-turnhead-020` | N |
| `SCB-turnhead-021` | P |
| `SCB-turnhead-023` | U |
| `V6R2-MP-059` | P |

## 3. Targeted expansion v7

Budget đề xuất **300 candidate mới +12 cell re-review**, không là 300 crop chắc chắn accepted. Không có membership/split giả. Ưu tiên cảnh/camera độc lập, hai trạng thái P/N trong cùng ngữ cảnh; một ảnh có thể đóng góp nhiều target nhưng không được đếm hai lần thành cảnh độc lập.

| Bucket ưu tiên | Loại ảnh cần tuyển | Negative phải đi cùng | Budget review / ưu tiên nhóm |
|---|---|---|---|
| A — desk-phone presence | Phone ngang/dọc trên bàn/sách, người viết/nghỉ/chống đầu/quay ngang, màu phone gần giấy/bàn; evidence gắn đúng người | Cùng posture/bàn nhưng không phone; vật xác nhận là bút/tẩy/máy tính; phone người khác không gán anchor | 80 candidate, tìm ≥ 10 nhóm mới có bằng chứng; không lấy thêm họ hàng sleep/around validation hiện tại. |
| B — nhỏ/che một phần | Phone cầm thấp, áp tai, giữa hai tay, cạnh sách; camera cao/xa/xiên; cả phone tối/sáng | Tay chạm tai/mặt, bút/vở/vật khác rõ; bằng chứng không đủ thì U | 80 candidate, ưu tiên ≥ 10nhóm mới; không nhân bản noise/augmentation cùng ảnh. |
| C — hướng nhìn-vùng bài | Quay trái/phải nhẹ-vừa-rõ, nhìn trước/lên ngoài bài; profil/gáy có context đủ; vừa giữ bút/giấy | Đầu nghiêng khi đọc/viết, cúi nhìn trang lệch bên, tay che mặt nhưng vẫn nhìn bài; mơ hồ giữ U | 100 candidate, ưu tiên ≥ 12 nhóm mới, cân P/N trong cùng camera/room nếu có metadata. |
| D — co-occurrence/crowded | Người khác trong context nhưng anchor rõ; phone P/looking P và các tổ hợp còn lại | Phone N/looking P, phone P/looking N, cả hai N khi review được | 40 candidate, ưu tiên ≥ 6 nhóm mới; không gán phone gần nhất. |

Các mục≥group ở bảng là mục tiêu tuyển **Draft**, không tự chốt group từ filename/hashes và không là release guarantee. Thiếu bucket/group báo shortage cho owner; không bù bằng stock dễ, tách frame lẻ hoặc map nhãn nguồn. Nếu nguồn local còn dư chỉ cùng nhóm đã biết thì chưa giải quyết mục tiêu diversity.

V6 còn 93 review_only: Student 46, Classroom 18, Exam 15, Head 6, HRW6, RF2. Có thể khảo sát có chọn lọc, nhưng không tự promote 93 crop hoặc dùng cùng scene dev/test làm train. Head/HRW giúp hard negatives/looking, ba ZIP RF chỉ train pool đã pin và phần lineage còn mới. FPI/Discuss ngoài membership hiện hành; không mở lại chỉ để tăng số lượng.

QA v7 phải lưu taxonomy lỗi bổ sung **metadata phân tích**, không đổi canonical targets: `phone_context`(held/desk/at-ear), qualitative visibility/partial-evidence, phone/head ROI draft nếu đo, crop/input projected size, low-detail/noise, head direction và work-area visibility, crowded-anchor attribution, source/original-video/scene/augmentation lineage. Numeric size/visibility bin cần owner duyệt từ distribution thật; không hard-code “<16px là loại” như đã approved.

Codex tự shortlist đa dạng bằng metadata/geometry/similarity đã pin, dựng person/context Draft và labels reasons; không chạy classifier trên test để chọn quota. Owner review batch. Chỉ materialize v7 sau membership/label/crop/group/split approval và QA/checksums/pointer. Bảo toàn v4–v6; correction parent có bảng supersession, không ghi đè.

## 4. Test độc lập và development protocol

[Thẩm định nguồn công khai](../data/E004-public-holdout-research-20261008.md) có shortlist và blocker cụ thể. **Chưa có public payload đã kiểm đủ để gọi test độc lập.** CDED-7 có provenance tự thu thập đáng khảo sát nhưng nhãn Focused/Distracted không dùng trực tiếp, terms research-only và download hiện chưa kiểm được. POCO/ECD là dự phòng cần audit rights/lineage/support. Không gửi yêu cầu cho người khác nếu owner chưa chỉ thị.

Giữ test 11 historical integrity-only. Val 50 là development lịch sử đã bị dùng cho selection/error analysis. Đề xuất development v7 bổ sung whole groups mới có P/N cả hai target và targeted context, được freeze trước recipe chạy; dataset release phải nêu riêng historical50/new-development để report. Không thay val/test qua từng run. Source holdout giữ hoàn toàn ngoài v7 train/dev, có package riêng và protocol đúng một candidate.

Rà annotation trước freeze test không phải model tuning, nhưng không dùng candidate scores để chọn ảnh. Primary test sampling/mixture công bố trước, giữ đủ negative và uncertain thực tế; challenge paired P/N cho từng bucket là phụ, không suy deployment precision từ mix cân bằng. Public classroom/remote-exam challenge không tự là real-world holdout của camera/phòng thi Việt Nam; acceptance claim phải giới hạn domain đã đo.

Nếu public nguồn mới không đạt support/independence/terms, **E004 chưa đủ điều kiện được phép promotion** dù val tốt; không tạo “test mới” bằng random-split v6 hoặc đổi tên source. Mục tiêu này đòi hoàn tất nguồn/QA/gates trước execution, không thể giải quyết chỉ bằng train thêm.

## 5. Recipe và thứ tự thực nghiệm đề xuất

1. Giải quyết targeted data + 12cell QA + group/source confounding; chốt v7, development và holdout protocol.
2. Owner chốt ADR017 gates và [recipe plan](../../configs/experiments/E004-plan.yaml), CPU/use scope; tạo exact configs/approval theo pins của dataset thật. Hai plan YAML hiện có null pins và không là trainer configs.
3. `E004-LP-control`: frozen ResNet18/input224 trên v7 nhưng **match optimizer head, mini-batch16, epochs50/patience10/min_delta, head init/seed, BN policy, data order và evaluation protocol với E004**. Khác candidate ở layer4 không trainable. Một identity có hypothesis/config/artifacts riêng; không đưa control vào final test. Không gọi control này exact recipe E003 hoặc quy delta E003→control chỉ do dataset; lịch sử có khác dữ liệu/val/optimization budget. Nếu cần isolate recipe E003 trên v7, phải có run data-control được duyệt riêng, ngoài hai run đề xuất chính.
4. `E004`: cùng v7/protocol/input224/seed/head init/preprocessing, mở `layer4` và head; BatchNorm running stats giữ eval. Đề xuất AdamW/head LR1e-3/layer4 LR1e-4/WD1e-4,batch16,max 50 epoch,patience10,min_delta1e-4,threshold0.5,CPU4threads. Đây là **training variables Draft**, không đã approved. So control để cô lập phần adaptation; không thêm augmentation/sampling/class weight/backbone mới trong cùng run.
5. Implement partial fine-tune trong canonical src **sau approval thiết kế**, với mini-batch loss xử lý known support đúng macro objective, trainable-state/BN tests, full encoder+head checkpoint/optimizer/RNG, config/data/code/environment cache identity và resume/evaluation. Trainer linear hiện tại không dùng được bằng thay config model; feature cache frozen 512 không hợp lệ cho layer4 trainable. Windows JSON luôn UTF8.
6. Development review/error slices/compare trên cùng evaluation identity; freeze candidate duy nhất. Chỉ sau G0–G5 mới test một lần và xét M1–M7. Không chọn thêm seed/head theo test.

Resolution 384 là ablation riêng nếu sau QA/model adaptation vẫn có phone loss do downsample; không hứa super-resolution phục hồi bằng chứng gốc. Nếu run OOM/budget không phù hợp, giữ FAILED/INTERRUPTED; đổi batch/device/recipe ⇒ identity/config/approval mới. Không giả sử quyền upload Colab/W&B từ local scope, không cài model/library mới trong task nghiên cứu này.

## 6. Các việc kỹ thuật còn thiếu để E004 có quyền xét promotion

| Việc | Bằng chứng xong / owner |
|---|---|
| QA12cell +targeted batch | Crop/labels/group decisions, actual coverage, unknown/shortage và supersession — owner duyệt, Codex tự chuẩn bị. |
| Dữ liệu v7 và holdout riêng | License/privacy/lineage graph, deterministic package/checksums/pointer, restore đúng use scope — owner ký release. |
| Model acceptance | ADR017 Accepted +numeric config/protocol pins **trước training**, không dùng approval E003 — owner. |
| Training/evaluation hỗ trợ recipe | Partial fine-tune/full bundle/resume/known-mask smoke và integration checks; không production fake metrics — Codex sau thiết kế được chốt. |
| Guard holdout | Package/split độc lập, final protocol/candidate hashes, receipt dùng-một-lần xuyên output và training cache không có test — Codex, owner final protocol. |
| Evidence uncertainty/performance | Metric fixtures, AP tie/null, whole-group bootstrap CI, local classifier benchmark protocol — Codex, owner gate. |
| Promotion record | Từng gate PASS hoặc reason thiếu, limitation/domain/use scope/artifact SHA, owner Selected/Continue/Rejected — owner. |

## 7. Nghiên cứu sơ cấp hỗ trợ hướng đề xuất

PyTorch phân biệt feature extractor đóng băng với fine-tuning backbone; đề xuất mở layer4 là **suy luận cho project sau audit**, không cam kết mức tăng từ tutorial. [Tài liệu PyTorch](https://docs.pytorch.org/tutorials/beginner/transfer_learning_tutorial.html).

WILDS cho thấy đánh giá thay đổi phân bố cần domain ngoài training; paper về spurious features phân tích học shortcut từ dữ liệu lệch. Đây là cơ sở kiểm source/scene, **không chứng minh E003 thực sự học một shortcut cụ thể**. [WILDS](https://proceedings.mlr.press/v139/koh21a.html), [spurious features](https://proceedings.mlr.press/v139/zhou21g.html).

Tài liệu sklearn cảnh báo preprocessing/model selection dùng test gây leakage; GroupShuffleSplit chia theo nhóm và không tự chứng minh nhóm độc lập. Giữ test khóa và giải quyết lineage trước split phù hợp nguyên tắc này. [Leakage](https://scikit-learn.org/stable/common_pitfalls.html), [group splitting](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupShuffleSplit.html). Không thêm sklearn làm dependency.

## 8. Trạng thái bàn giao và quyết định cần review

Đã hoàn tất mổ lỗi/pins/canonical audit và gói đề xuất. **Chưa hoàn tất dataset v7 hoặc test độc lập; E004 chưa promotion-ready.** Mọi số gate/budget/recipe mới là Draft có owner. Nghiệm thu hướng/gates không tự nghiệm thu300candidate chưa có, quyền source chưa kiểm hoặc config null pins. Bước tiếp theo cần owner review gói này, chốt ngoại lệ crop/text và hướng tiếp nhận nguồn; Codex tiếp tục tự động hóa shortlist/crop/QA thay vì yêu cầu owner annotate hàng trăm ảnh.
