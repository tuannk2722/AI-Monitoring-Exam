# Đặc tả training, evaluation và cải tiến model

## 1. Mục đích và trạng thái

Đọc khi sửa loader/preprocessing/model/loss/training/resume/evaluator, phân tích kết quả hoặc chuẩn bị experiment mới. Đối chiếu đến **2026-10-10** bằng config, approval, run/metrics và audit source/crop/input. Kết quả và các đề xuất nằm ngay trong tài liệu này; không cần một trang results hoặc E004 riêng để biết đã làm gì.

**E001–E003 đã FINISHED, decision `continue_research_only`; chưa model Selected.** Cả ba học linear head mới trên cùng ResNet18 pretrained đóng băng, không fine-tune backbone. E004 chưa triển khai/chạy; config/metrics/compute/comparator/holdout còn Draft. V7 accepted local chỉ giải quyết dataset scope, không cấp quyền train/test/promotion.

## 2. Recipe đã được duyệt và implementation hiện hành

ADR-014/015/016 và approval riêng lần lượt cho E001/v4, E002/v5, E003/v6. Ngoại lệ CPU chỉ ba run/smoke theo config đã pin; không kế thừa sang run mới. YAML cũ có comments pending từ lúc proposal nhưng receipt hiện `status=approved` và pin resolved config; giữ nguyên bytes/config lịch sử, không dùng comment để phủ nhận approval hoặc sửa pin.

| Thành phần | Contract hiện tại |
|---|---|
| Backbone | ResNet18 `IMAGENET1K_V1`, local weights `outputs/pretrained/resnet18-f37072fd.pth`; SHA `f37072fd47e89c5e827621c5baffa7500819f7896bbacec160b1a16c560e07ec` |
| Trainable | Linear head 512→2; encoder parameters frozen, BatchNorm eval/buffers giữ nguyên, feature forward no_grad |
| Output | Hai logits độc lập; sigmoid scores theo `[phone_use, looking_around]`; positive decision score ≥0.5 |
| Input | RGB, letterbox bilinear 224 giữ full context; resize cạnh dài 224 và round cạnh ngắn (tối thiểu 1), center padding `[124,116,104]` |
| Normalize | Mean `[0.485,0.456,0.406]`, std `[0.229,0.224,0.225]`; không stretch/silent crop/đổi EXIF sau annotation |
| Feature extraction | Batch 16, CPU 4 threads; cache 512 features pin source/crop/data/transform/encoder identity, không tái dùng sai version |
| Objective | `macro_masked_bce`: mean BCEWithLogits của known samples mỗi target, rồi mean hai target; unknown không denominator/gradient |
| Optimization | Head AdamW, LR 0.001, weight_decay 0.0001; full-batch update, seed 42, deterministic settings |
| Budget chính | Max 200 epochs, patience 20, min_delta 0.0001; smoke configs riêng 3 epochs/interruption-resume |
| Selection | Best theo raw minimum validation masked BCE, tie giữ epoch sớm. min_delta chỉ điều khiển early-stop reference/patience, không thay rule best checkpoint |

Các số trên là recipe lịch sử Accepted, **không default khoa học cho mọi model mới**. Biến nằm trong `configs/experiments/E001.yaml`/E002/E003 và smoke tương ứng. `ExperimentConfig` hiện từ chối keys thiếu/lạ, values unresolved/nonfinite, model/device/optimizer/loss/transform khác whitelist; chỉ hỗ trợ `resnet18_frozen_linear` CPU. Đổi tên YAML không triển khai fine-tune hoặc GPU.

Backbone chỉ load weights local đúng SHA; không tự download, random fallback hoặc đổi license. `best.pt` hiện chứa head/config/identity/epoch, không standalone backbone. Dùng lại model phải có đúng pretrained + preprocess/target order/threshold; model bundle tự chứa đủ backbone là việc chưa hoàn tất cho deployment/promotion.

## 3. Loader, loss và metrics phải bảo toàn

`training/data.py::verify_dataset` kiểm payload checksum/inventory, manifest versions/scope/usage, manifest–ledger membership, inline freeze hoặc preservation pointer. V5 cần thêm approval/membership/group/proposal/parent evidence ở original paths; ba metadata dependencies đã khôi phục exact SHA trong task handoff 2026-10-11 và giữ trong Git. Loader v4/v5/v6 đã verify trực tiếp; thiếu file về sau vẫn phải restore đúng pin, không bỏ guard. `select_records` chỉ train/val, test cần explicit final-test access. Không glob toàn crops hoặc đưa review-only/U-U vào supervision.

JSON unknown là null/mask 0; tensor có placeholder để tính nhưng loss/metric chỉ lấy known positions. Full-batch objective hiện yêu cầu mỗi target có known support. Khi thiết kế fine-tune mini-batch phải chốt aggregation/empty-target handling; không biến U thành N hoặc sửa loss ngầm để tránh batch lỗi.

Metrics giữ P/N/U, TP/FP/FN/TN, precision/recall/F 1/AP từng target, macro masked BCE và macro AP. AP non-interpolated, equal scores xử lý theo nhóm. Macro AP chỉ có khi cả hai target có AP hợp lệ. Thiếu P hoặc N thì metric unavailable/null; không positive predictions thì precision null, không fake 0 hoặc PASS. Co-occurrence báo fully-known denominator/support; pilot chưa đủ để công bố metric đồng xuất hiện đáng tin.

Đối chứng hằng dùng prevalence chỉ tính từ train; không fit prevalence/threshold trên val/test. Selection/hyperparameter dùng development; validation đã dùng chọn epoch không là holdout độc lập. Báo cùng cohort/labels/masks/protocol trước so delta; AP cao không bảo đảm operating point ở threshold 0.5.

## 4. Experiment contract và workflow chạy

Canonical logic ở `training/config.py`, `data.py`, `model.py`, `metrics.py`, `train.py`, `evaluate.py`, `artifacts.py`. Một run cần ID/owner/hypothesis/parent, config digest, code identity/Git commit+dirty, data/split/encoding/payload/weights versions, environment/dependencies/seed, command, start/end/status, metrics, artifacts/checksum và observation/decision. W&B optional disabled, không thay bản lưu local; không log media chưa có quyền.

Workflow cho **một experiment mới được duyệt**:

1. Xác định hypothesis và biến thay đổi từ lỗi/data đã biết; tạo ID/config/protocol/approval rõ scope. Không sửa E001–E003 hoặc reuse output để thử recipe khác.
2. Kiểm đủ dataset/split/label/rights/freeze/pretrained và version/pins, hardware/budget, source checkout/dependencies. Code khác historical SHA cần run identity mới hoặc restore source gốc; không sửa pin để hợp thức hóa.
3. Smoke riêng kiểm loader, objective, shapes/masks, optimizer trainable/frozen policy, memory và checkpoint interruption/resume. Không smoke lại run đã xong nếu không có thay đổi cần kiểm.
4. Chạy trainer vào output mới. Current CLI nhận `--config`, `--output`, `--workspace`; `--resume` chỉ cùng identity, `--interrupt-after` là recovery drill. Run train chỉ train/val, không test.
5. Kiểm status/last/best/history/config/environment/checksums; reload validation bằng evaluator và đối chiếu reproducibility. Phân tích errors/slices bằng score đã lưu trước khi quyết định bước sau.
6. Chỉ freeze candidate/protocol và mở final test khi có approval riêng, đủ support/rights/independence. Không đổi model/threshold/slice rồi thử lại cùng test sau thấy kết quả.
7. Ghi decision Continue/Rejected/Candidate/Selected có evidence và limitations. FINISHED là trạng thái kỹ thuật, không Selected; promotion cần owner nghiệm thu.

Output chính `outputs/<ID>/` có `run.json`, `resolved-config.json`, `best.pt`, `last.pt`, `history.json`, `metrics.json`, `predictions-train.json`, `predictions-val.json`, features/cache và `checksums.json`; reports nhỏ giữ trong Git khi cần bàn giao. Checkpoint last giữ head/optimizer/RNG/epoch/best/early-stop/history; writes atomic. Resume từ chối code/config/data/features khác. OOM/FAILED/INTERRUPTED phải ghi đúng status và lỗi; không giảm batch hoặc đổi config trong cùng identity.

Evaluator hiện yêu cầu run FINISHED, **code identity giống run**, resolved config và mọi artifact hash đúng; validation output mới dưới workspace outputs. Test cần protocol riêng pin một experiment/checkpoint/config/code/payload/threshold/best epoch. Guard hiện chưa quản lý holdout độc lập và use-once xuyên output, vì vậy không đủ để tự cấp quyền test mới.

Lệnh mẫu chỉ dùng với **config đã approved và output mới**, không phải lệnh yêu cầu chạy các run cũ lần nữa:

```powershell
.venv/Scripts/python.exe -X utf8 -m ai_exam_monitoring.training.train --config configs/experiments/<approved-id>.yaml --output outputs/<new-id> --workspace .
.venv/Scripts/python.exe -X utf8 -m ai_exam_monitoring.training.evaluate --run outputs/<new-id> --output outputs/<new-id>-val-evaluation --split val --workspace .
```

Model run lịch sử không evaluate bằng code đã cleanup/refactor: `code_identity` hash toàn Python package (UTF-8 LF), nên retire modules/đổi imports cũng đổi identity. Restore exact source/commit và environment theo development spec khi cần tái lập, không nới evaluator.

## 5. Kết quả đã thực hiện

| Run / dataset | Train / val | Best / completed epochs | Val masked BCE | Val macro AP | Kết luận |
|---|---|---|---:|---:|---|
| E001 / v4 | 60 / 13 | 12 / 32 | 0.547727 | 0.927296 | Baseline frozen probe hoàn tất; chưa promotion |
| E002 / v5 | 80 / 13 | 7 / 27 | 0.633363 | 0.980867 | H 1 chưa được ủng hộ: BCE tăng 0.085636 so E001 trên cùng val 13; AP/looking tốt hơn nhưng phone recall giảm |
| E003 / v6 | 317 / 50 | 45 / 64 | 0.610775 | 0.787808 | H 1 development được ủng hộ so train-prevalence control BCE 0.691101; chưa chứng minh cải thiện nhân quả/generalization |

Confusion validation tại threshold 0.5; precision/recall dưới đây trên known labels:

| Run | Phone TP/FP/FN/TN | Phone precision / recall | Looking TP/FP/FN/TN | Looking precision / recall |
|---|---|---|---|---|
| E001 | 7/1/0/0 | 0.875 / 1.000 | 0/0/3/3 | null / 0.000 |
| E002 | 4/0/3/1 | 1.000 / 0.571 | 1/0/2/3 | 1.000 / 0.333 |
| E003 | 9/2/8/18 | 0.818 / 0.529 | 11/1/7/10 | 0.917 / 0.611 |

Val 13 support phone 7 P/1 N/5 U, looking 3 P/3 N/7 U. Val 50 phone 17 P/20 N/13 U, looking 18 P/11 N/21 U. Val 50 có thêm 37 development crops; không so scalar BCE/AP E003 trên 50 với E001/E002 trên 13 để kết luận model gain. E003 train/val gap BCE 0.132558, val 15 FN/3 FP; source/group concentration và labels còn hạn chế.

**E001 final test đã thực hiện đúng một protocol approved**, không còn là tập test mới: 11 crops, BCE 0.569219, macro AP 1.0; phone 2 P/2 N/7 U có TP 2/FP 2/FN 0/TN 0, precision 0.5/recall 1; looking 2 P/7 N/2 U có TP 0/FP 0/FN 2/TN 7, precision null/recall 0. AP 1.0 ở support rất nhỏ không chứng minh operating point hoặc generalization. E002/E003 không test inference mới.

Ba run và pretrained/metrics/checkpoints thật ở outputs với DVC local pointers. Frozen config/approval nằm trong `configs/experiments/` và `docs/experiments/E001-approval.json`/E002/E003; final protocol E001 ở `E001-final-test-protocol.json`. Primary metrics/confusion ở `artifacts/reports/E001|E002|E003/metrics.json`, E001 test riêng `test-metrics.json`; run/code/environment/checksums là authority cho exact reproduction. Không cần Markdown card riêng cho từng lần chạy để biết kết quả trên.

## 6. Phân tích lỗi E003 đã làm và hệ quả

Audit source/crop/input 224 của **46 FN (21 phone/25 looking) và 3 FP validation**, 49 target errors trên 48 ảnh; số lỗi có thể overlap trên cùng crop. Các factors dưới đây là quan sát/hypothesis, chưa kết luận nhân quả hoặc tỷ lệ lỗi toàn dataset.

| Failure mode đã quan sát | Bằng chứng | Hành động hợp lý |
|---|---|---|
| Phone trên bàn/sách | 6/8 phone FN val là desk-phone, 6/8 visually small, 4/8 partial; nhiều pose nghỉ/chống đầu/crowded | Tuyển desk/partial-phone trong primary domain, đi kèm negatives cùng pose/workarea; giữ mobile-presence semantics |
| Phone train vẫn bỏ sót | 13 FN, 12 held-phone, 11 partially occluded, 9 visually small; có auxiliary/non-exam | Không quy mọi lỗi cho unseen source hoặc chỉ hạ threshold; kiểm representation/224 evidence |
| Looking side/context | 7 FN val đều head-side/turn, 5 crowded; 1 cần review đọc sách vs nhìn bên | Review gaze/vùng bài đúng anchor; matched positives/negatives đọc/viết, không mọi turn_head là P |
| Ambiguous/low detail | Looking train 18 FN: 10 low-detail, 8 small-evidence, 9 cần rà label; factors overlap | Tách clear/unknown theo evidence, cải thiện provenance và nguồn trước model lớn |
| FP khó | `V6-EX-042` nghiêng viết,`V6-SB-047` viết/noise score 0.50043,`V6R2-EX-008` cầm bút nhìn bên nhưng phone score 0.72816 | Hard negatives, cả phone N/looking P; không đặt mọi tay gần mặt là phone |

7/8 phone FN val bị downsample ở 224; `P022-person-01` cạnh dài 139 nên upscale. Tăng 384 là hypothesis riêng, chưa ablation và không cứu ảnh gốc thiếu evidence. V7 đã materialize owner decisions của 12 ambiguous/conflict cells; không tự review lại/relabel v6 hoặc coi toàn 375 new train đã có measured targeted slice support.

V7 cải thiện supervision train nhưng chưa có new validation/independence/holdout; gần 69% train vẫn chỉ known một target. Targeted train gain và packaging PASS không là model-quality gain. Các số source/group/pair/224 coverage hiện hành ở data spec.

## 7. E004: đề xuất hiện hành, chưa được chạy

Owner chọn tiếp tục classifier trên reviewed crops, tìm nguồn holdout công khai mới. Proposal `configs/experiments/E004-plan.yaml` chưa có approved ExperimentConfig, data/split/payload/holdout pins vẫn null; `training_approved=false`, `final_test_approved=false`, `eligible_for_promotion=false`. Phần dataset gate v7 đã hoàn tất local; recipe/metrics/compute/holdout chưa chốt.

Hypothesis: sau targeted data/QA, mở layer 4 có thể thích nghi desk-phone và hướng nhìn tốt hơn frozen probe trên **cùng v7/protocol**, rồi kiểm độc lập trước xét promotion. Không hứa mức gain hoặc suy recipe được approve vì config đã tồn tại.

| Biến | Control đề xuất | Candidate đề xuất |
|---|---|---|
| Model | `E004-LP-control`: encoder frozen + head mới | E004: layer 4 + head trainable, các phần trước frozen |
| BN / initialization | Running statistics eval; head seed 42 mới | Cùng BN/head policy; không warm-start head E003 |
| Input/loss/threshold | RGB letterbox 224, no augmentation, masked macro BCE, 0.5 | Giữ cùng control để đo adaptation |
| Optimizer/budget | AdamW head LR 0.001, decay 0.0001, batch 16, max 50 epochs/patience 10/min_delta 0.0001 | Head LR 0.001, layer 4 LR 0.0001, cùng budget/seed/batch |
| Selection/compute | Raw minimum masked val BCE; CPU 4 threads proposed | Cùng policy; CPU ngoại lệ/budget phải owner duyệt mới |

**Toàn bảng là Draft.** Trainer hiện feature-cache/frozen-head nên không chạy candidate chỉ bằng sửa YAML. Sau khi owner chốt design, cần trainable/BN policy thật, mini-batch masked objective, optimizer groups, checkpoint đủ backbone+head/optimizer/RNG/scheduler nếu có, resume/cache invalidation/evaluator và model bundle. Kiểm frozen vs trainable weights/buffers, uninterrupted–resumed parity và metrics reload bằng fixtures; smoke local trước run thật. Input 384/resolution ablation là experiment riêng chưa approved.

Comparator development chưa Accepted: v7 val 49 từ val 50 sau `V6-CA-041` rời val và `EXP-SCB-002` đổi label. 48 retained IDs giữ source/crop/target/mask/context/rights nhưng literal group/review identity versioned; 14 old groups ánh xạ 1–1 sang new groups. Phải owner freeze IDs/label contract/group mapping và protocol trước run; không tự dùng intersection tùy ý hoặc gọi 49 là cùng 50.

Audit dùng **cached E003 scores**, không model inference, minh họa recall phone 0.529→0.563 và looking 0.611→0.647 khi đổi labels/cohort sang v7. Cùng model mà metric đổi: đây là annotation/cohort effect, không E004 gain. Không chạy E003 trên final holdout mới để dựng comparison.

## 8. Acceptance/promotion gates đang đề xuất

ADR-017 vẫn **Draft**. Nội dung proposal được giữ ở đây để owner/agent tiếp tục chốt, không phải metrics Accepted hoặc quyền execution. Scope nếu được chốt chỉ Selected cho nghiên cứu classifier trên reviewed crops/nguồn được phép; không tự đóng runtime/video/web/giám sát cá nhân.

| Gate điều kiện | Trạng thái hiện tại / điều kiện đề xuất |
|---|---|
| G0 | Metrics/recipe/protocol được owner approve trước training; hiện còn Draft |
| G1 | V7 và holdout riêng accepted với rights/QA/pins/không unresolved overlap; v7 local đã đạt, holdout thiếu |
| G2 | Holdout independent với E001–E004 theo provenance/lineage/person/session/room; chưa có |
| G3 | Đề xuất mỗi target test≥100 known P và 100 N; ≥10 independent groups, P/N mỗi loại ở≥5 groups; ≥2 camera/room contexts xác minh. Không lấy train 233 phone P hoặc 100 consecutive frames thay test support |
| G4 | Candidate FINISHED, smoke/resume/reload PASS, full bundle đủ backbone+head/preprocess/targets/threshold và version pins; hiện chưa E004 implementation/run |
| G5 | Một candidate/config/checkpoint/protocol/holdout freeze; owner cấp một final evaluation, guard chặn lặp kể cả đổi output; chưa triển khai cross-output holdout access |

G0–G5 đủ mới đủ điều kiện xét; proposal quality gates dùng AND:

| Gate quality Draft | Giá trị đề xuất, chưa Accepted |
|---|---|
| M1 | Mỗi target precision≥0.85, recall≥0.80, FPR=`FP/(FP+TN)`≤0.10 |
| M2 | AP mỗi target≥0.80, macro AP≥0.85 |
| M3 | Macro masked BCE≤0.90×constant train-prevalence control BCE trên cùng holdout |
| M4 | Predefined slices desk/small-partial phone, looking-side-forward, crowded, đọc/viết/chống đầu negatives; mỗi target/slice đủ≥20 P/20 N từ≥3 evidenced groups; recall≥0.70, precision≥0.80, FPR≤0.15 |
| M5 | Cluster bootstrap 95% CI: lower recall≥0.65, lower precision≥0.70, upper FPR≤0.20; resample whole groups 5.000 lần seed 42, percentiles 2.5/97.5,≥95% resamples có valid denominators |
| M6 | Classifier benchmark local pinned: batch 1/4 CPU threads, 10 warm-up/500 lượt trên development crops frozen; p95≤200 ms/crop, peak RSS≤1 GiB. Timing decode/letterbox/normalize/forward, startup riêng; không video SLA hoặc số đã đo |
| M7 | Rights/license/scope, restore/checksums/full model bundle và owner promotion record PASS |

Support/independence/CI thiếu hoặc precision null ⇒ INCONCLUSIVE/Continue, không quality PASS. Nonfinite/integrity/protocol sai ⇒ evaluation không hợp lệ. Không chọn slice theo predictions/đổi sampling để đủ số hoặc dùng macro bù target yếu. Bootstrap không chứng minh provenance independence.

Proposal development “bước nhảy” trước đây: phone recall+0.20, looking+0.15, precision không giảm>0.05, FPR không tăng>0.05; added 37 phone recall≥0.60. Đây là Draft trên cohort/comparator cần freeze lại theo v7; không Accepted hoặc independent-gain claim. Gates phải chốt trước nhìn kết quả mới, không hạ sau test để promotion.

## 9. Việc cần làm tiếp theo

1. Đóng targeted matrix/QA/provenance cho 375 new train; thiết kế dữ liệu evaluation mới theo policy owner, không random-split lại release. Đây là bước data, không tự sửa recipe để bỏ qua thiếu evidence.
2. Owner chốt comparator, recipe/compute, numerical gates và holdout/use scope với exact versions/pins. Có thể đề xuất experiment local chẩn đoán giới hạn nếu owner chọn, nhưng không tự thu hẹp mục tiêu E004/generalization.
3. Triển khai phần fine-tune/checkpoint/resume/evaluator đã duyệt, meaningful synthetic tests và smoke; chạy matched control/candidate với approval riêng.
4. Review development evidence theo cùng labels/masks, freeze một candidate trước final evaluation riêng. Selected chỉ sau đủ evidence/gates và owner ký decision.

TBD owners đều là chủ repository: `TBD-E004-RECIPE/COMPUTE` (biến/compute chưa duyệt), `TBD-E004-COMPARATOR` (cohort/group mapping chưa freeze), `TBD-E004-HOLDOUT-SOURCE` (data rights/provenance/support chưa đạt), `TBD-METRIC-01` (numerical gates chưa Accepted). Agent chuẩn bị proposal có phương án/chi phí/evidence/acceptance, không bắt owner làm thủ công hoặc coi bản Draft là approval.
