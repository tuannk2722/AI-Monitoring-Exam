# Training readiness — 2026-10-06

Owner: chủ repository. Codex nghiên cứu/kiểm tra, không delegation. Git: `e1cf689` (`cleanup codebase`). Bỏ qua và giữ nguyên deletion chưa commit của `codebase-review-20261005.md` theo yêu cầu.

**Có thể bắt đầu P3 bằng việc triển khai baseline classifier trên crop đã duyệt. Chưa có trainer/evaluator B để chạy training ngay; chưa đủ bằng chứng để công bố model dùng được trên video phòng thi.**

Đây là assessment và đề xuất kỹ thuật, không phải ADR Accepted, config executable, approval cloud hoặc kết quả experiment. User giao Codex đề xuất/tự chọn kỹ thuật; các lựa chọn bên dưới được ghi rõ để không trở thành quyết định ngầm. Owner không phải tự nghiên cứu learning rate hoặc viết trainer.

## 1. Evidence hiện tại

| Hạng mục | Kiểm tra hiện tại | Ý nghĩa |
|---|---|---|
| Dataset v4 | accepted, local_classifier_research | Đạt data gate cho pilot reviewed-crop |
| Manifest | 84 records: 60 train/13 val/11 test | Loader đọc manifest, không quét 112 crops |
| Ledger | 112 records, 28 review_only | 28 record này không được thêm vào train |
| Encoding | phone_use, looking_around; unknown=null/mask=0 | Multi-label; normal là metadata |
| Integrity | Full payload/inventory, schema và freeze hashes/IDs PASS | Local payload khớp release |
| Leakage | 16 groups, zero cross-split image/crop/group overlap | Không chứng minh độc lập subject/session |
| DVC | Pointer local up to date; remote round-trip có evidence lịch sử | Lượt này không truy cập remote |
| Software | 113 tests, Ruff, compileall, repository checker PASS | Không phải model quality gate |
| Trainer/evaluator B | Chưa có; legacy A đã gỡ | Không có lệnh train B/dvc repro hợp lệ |
| Máy local | Python 3.11.9, i7-1255U, Intel UHD; không thấy NVIDIA trong inventory | Không giả định CUDA |
| Dependencies | torch/torchvision/sklearn chưa cài; DVC/Ruff có | Chưa xác minh ML install hoặc smoke thật |

Nguồn repository: [P3](../10-phase-p3-ai-baseline.md), [P2](../09-phase-p2-dataset-preparation.md), [runbook](../data/pilot-b-preparation-v1.md), [ADR-012](../decisions/ADR-012-formulation-b-multilabel.md), [ADR-013](../decisions/ADR-013-pilot-b-packaging-contract.md), [config release](../../configs/datasets/pilot_b_release_v4.yaml), [schema](../../src/ai_exam_monitoring/data/pilot_schema.py).

Snapshot acceptance local còn ghi DVC pending ở thời điểm tạo; runbook/WORKLOG mới hơn ghi storage scope và round-trip PASS. Đây là lịch sử có giải thích, không sửa snapshot immutable. Index ghi 109 tests của checkout bàn giao; suite hiện tại là 113.

## 2. Dữ liệu quyết định cách train

Tính lại từ manifest; P/N/U = positive/negative/unknown:

| Split | Crops | Phone P/N/U | Looking P/N/U |
|---|---:|---|---|
| Train | 60 | 11/5/44 | 17/33/10 |
| Validation | 13 | 7/1/5 | 3/3/7 |
| Frozen test metadata | 11 | 2/2/7 | 2/7/2 |

Train chỉ cung cấp 16 phone labels và 50 looking labels. Val phone chỉ có một negative: một false positive làm specificity đổi từ 100% xuống 0%. Có một co-occurrence ở train, không có positive co-occurrence ở val/test; chưa đủ đo khả năng phát hiện hai hành vi đồng thời. Không đánh đồng crops với người/tình huống độc lập.

**Confounding phone nghiêm trọng:** mọi phone positive đã biết ở train/val đến từ Roboflow; mọi negative đến từ SCB. Rule diagnostic bằng metadata `source == roboflow_v1` khớp 16/16 known labels train và 8/8 val. Đây không phải model dự đoán ảnh hoặc experiment metric, không được đưa vào production. Không chạy rule diagnostic trên test. Kết quả cho thấy split chưa phân biệt được học hành vi với học nguồn.

Geirhos và cộng sự phân tích việc model học dấu hiệu dễ nhưng không đúng mục tiêu rồi thất bại khi đổi phân bố. Áp dụng vào đây là suy luận từ cấu trúc source/labels, chưa chứng minh một model cụ thể đã mắc lỗi. [Shortcut Learning in Deep Neural Networks](https://arxiv.org/abs/2004.07780).

Mục tiêu E001: kiểm chứng pipeline, tạo mốc so sánh và phân tích lỗi. Muốn cải thiện chất lượng, ưu tiên thêm positive/negative trong cùng miền, hard negatives và cảnh khác biệt đã review. Không bịa mốc 500/1.000 ảnh; kế hoạch bổ sung phải dựa coverage. Thay đổi thành dataset version/review mới, không sửa frozen v4/test.

## 3. Model nên bắt đầu

PyTorch mô tả hai cách transfer learning: fine-tune backbone và giữ backbone cố định chỉ học head. Với dữ liệu ít, cách thứ hai cho baseline đơn giản, ít tham số học. Tutorial minh họa single-label nên không chép CrossEntropyLoss/ImageFolder sang hợp đồng B. [PyTorch transfer learning](https://docs.pytorch.org/tutorials/beginner/transfer_learning_tutorial.html).

| Phương án | Cơ sở/trade-off | Đề xuất |
|---|---|---|
| ResNet18 pretrained, frozen backbone, linear head | Model ImageNet gốc 11,69M parameters, 1,81 GFLOPs; implementation đơn giản | E001 đầu tiên |
| MobileNetV3-Small pretrained | Model gốc 2,54M parameters, 0,06 GFLOPs | Candidate khi ưu tiên inference cost |
| DINOv2 ViT-S/14 frozen features | Khoảng 21M parameters; đặc trưng chuyển giao nhiều tác vụ; standard DINOv2 code/weights Apache-2.0 | Challenger hợp lý sau baseline/error analysis |
| Train từ đầu hoặc unfreeze toàn mạng ngay | Nhiều tham số tự do với chỉ 16 phone labels | Không chọn cho E001 |

Số của model gốc không phải model sau thay head hoặc benchmark laptop/dataset dự án. Không suy accuracy dự án từ ImageNet. Nguồn: [ResNet18](https://docs.pytorch.org/vision/stable/models/generated/torchvision.models.resnet18.html), [MobileNetV3-Small](https://docs.pytorch.org/vision/stable/models/generated/torchvision.models.mobilenet_v3_small.html), [DINOv2 paper](https://arxiv.org/abs/2304.07193), [DINOv2 repo](https://github.com/facebookresearch/dinov2).

ResNet18 là lựa chọn cho bước kiểm chứng đầu, chưa được chứng minh tốt hơn DINOv2 ở bài toán này. Model mạnh hơn không tự sửa confounding; không mở hyperparameter search lớn trên 13 val crops.

## 4. E001 đề xuất cụ thể

Các giá trị là lựa chọn khởi đầu của Codex, chưa là config đã chạy hoặc tối ưu thực nghiệm. Implementation phải chuyển thành reviewed config và experiment card.

| Thành phần | Giá trị đề xuất |
|---|---|
| Hypothesis | Frozen pretrained features cho phép học hai target từ known labels, tạo pipeline đo được/tái lập được |
| Data | Exact v4 manifest/split; không re-split |
| Weights | ResNet18_Weights.IMAGENET1K_V1; pin URL/version/SHA-256 khi lấy weights; không dùng DEFAULT |
| Head | Pooled 512 features → Linear(512,2), tổng 1.026 trainable parameters |
| Freeze | Backbone requires_grad=False và luôn eval(), BatchNorm không cập nhật |
| Input | RGB; resize giữ tỷ lệ, cạnh dài 224; pad đối xứng thành 224x224, bilinear/antialias, fill gần ImageNet mean |
| Normalize | mean [0.485,0.456,0.406], std [0.229,0.224,0.225] |
| Augment | Không stochastic augmentation ở E001; không random crop/cutout |
| Extract | Batch 16, FP32, workers=0; cache train/val riêng, pin hashes crop/weights/transforms; không extract test khi train |
| Train head | Full batch 60 cached feature vectors; AdamW lr=0.001, weight_decay=0.0001; không scheduler/class weighting/sampler |
| Budget | Tối đa 200 epochs, mỗi epoch một optimizer update trên cached features; smoke 3 epochs bằng ID riêng |
| Early stop | Patience 20 epochs không cải thiện ít nhất 0.0001 val macro masked BCE |
| Checkpoint | Best raw val macro masked BCE; tie giữ epoch sớm hơn; không chọn bằng test |
| Seed | 42 cho run đầu; không tìm seed score đẹp |
| Threshold | 0.5 cố định chỉ cho diagnostic precision/recall/F1; không tune threshold pilot |
| Logging | JSON/Markdown local, W&B off, không media upload |

Pooled feature/head đối chiếu [source ResNet chính thức](https://raw.githubusercontent.com/pytorch/vision/main/torchvision/models/resnet.py). Resize+pad là đề xuất dự án, khác Resize+CenterCrop mặc định của weights, nhằm giữ phone/desk trong reviewed crop. Cần visual QA trên train/val trước run; chưa chứng minh tốt hơn default. Transform thuộc experiment version, không thay bytes/annotation v4.

Frozen features giúp CPU chỉ extract ảnh một lượt rồi tối ưu head nhỏ. Chưa đo thời gian/RAM; nếu OOM không tự đổi batch trong cùng run identity. Cache phải invalidated khi weights/transform/crop đổi; không tái dùng frozen cache cho fine-tuning backbone.

### Loss/unknown

Dùng BCEWithLogitsLoss không reduce, chỉ entries known. Với full-batch head, train loss là `0.5 * (sum(phone_known_BCE)/16 + sum(looking_known_BCE)/50)`; val tương tự với denominators 8 và 6. Tính denominators từ split/manifest và assert, không hard-code count trong src. Hai target có trọng số ngang nhau.

Dùng indexing hoặc finite placeholder nội bộ kèm mask; không đưa NaN/null vào BCE rồi kỳ vọng nhân 0 sẽ sửa được. Placeholder không đổi unknown trong manifest. Không pseudo-label unknown. Đây là masked BCE baseline của dự án, không tuyên bố tái hiện thuật toán partial-BCE của Durand. Paper cho thấy partial labels cần xử lý riêng; PyTorch cung cấp BCE logits ổn định và reduction none. [Durand et al., CVPR 2019](https://arxiv.org/abs/1902.09720), [BCEWithLogitsLoss](https://docs.pytorch.org/docs/main/generated/torch.nn.BCEWithLogitsLoss.html).

### Evaluation

Báo per-target AP, precision/recall/F1 ở 0.5, TP/FP/FN/TN, P/N/unknown counts, loss curves và errors local. Macro AP chỉ khi cả hai target có support hợp lệ. Slice thiếu P/N ghi không xác định/lý do theo protocol, không bịa 0 thành kết quả đo. Co-occurrence val/test ghi support 0. Sigmoid scores chưa được chứng minh calibrated.

AP đo chất lượng xếp hạng qua precision-recall; không cần chọn một decision threshold. Val rất nhỏ nên không tune threshold hàng loạt. [scikit-learn AP](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html), [threshold selection](https://scikit-learn.org/stable/modules/classification_threshold.html).

Đối chứng trivial: constant score lấy prevalence train (phone 11/16, looking 17/50), cùng evaluation protocol; không nhầm model production. Source-only rule ở mục 2 là diagnostic metadata riêng. Chốt candidate list/protocol trước final test evaluation; train CLI không tự test sau mỗi run. Không dùng test để chọn model/epoch/threshold/augmentation. [Leakage guidance](https://scikit-learn.org/stable/common_pitfalls.html).

TBD-METRIC-01 vẫn do owner repository chốt sau baseline/error analysis và coverage phù hợp. Threshold 0.5 không phải risk threshold hoặc promotion gate; không tự đặt AP mục tiêu từ web benchmark.

## 5. Môi trường và scope

**Đề nghị E001 frozen-feature chạy CPU local trước.** Đây là ngoại lệ hẹp đề xuất so với phân công ADR-004 local-development/Colab-GPU; cần ghi experiment/runbook khi implementation, không âm thầm sửa ADR. Chưa benchmark thời gian. Fine-tuning GPU vẫn theo hướng Colab khi đủ scope.

ADR-004 chọn kiến trúc Colab nhưng approval v4 là local research; bổ sung 2026-10-05 chỉ cho storage/restore trên restricted Drive. Không suy ra quyền xử lý crops trên Colab. Khi muốn cloud, Codex chuẩn bị scope addendum về đúng v4/runtime/access/cache/output/cleanup để owner chốt trước copy data; không sửa immutable release. [ADR-004](../decisions/ADR-004-compute-environment.md), [governance](../21-data-governance-privacy-and-security.md), [storage scope](../data/pilot-b-preparation-v1.md).

Colab Free không đảm bảo GPU/model GPU/thời lượng. Cần checkpoint ngoài runtime, không cam kết T4 hay thời gian train. [Google Colab FAQ](https://research.google.com/colaboratory/faq.html).

TorchVision code là BSD-3-Clause; README lưu ý pretrained weights có thể có terms riêng từ dữ liệu pretraining. ImageNet download nêu research phi thương mại; không suy blanket weights license từ software license. Đề xuất weights cho academic local research, giữ attribution; Codex phải ghi exact provenance/terms review trước download/run. Quyền redistribute weights/deploy thương mại chưa được xác lập bởi assessment. [TorchVision LICENSE](https://raw.githubusercontent.com/pytorch/vision/main/LICENSE), [pretrained terms](https://raw.githubusercontent.com/pytorch/vision/main/README.md), [ImageNet](https://www.image-net.org/download.php).

Cài cặp torch/torchvision stable tương thích Python 3.11/OS từ official source; freeze exact versions sau import/clean-install check. Hiện requirements/ml.txt trỏ extra ml có broad ranges, thiếu torchvision và kéo ultralytics/W&B; implementation cần dependencies đúng classifier scope. Chưa chọn/pin package version; rolling docs không phải lockfile. [Compatibility](https://raw.githubusercontent.com/pytorch/vision/main/README.md).

Seed không đảm bảo bitwise identical giữa CPU/GPU/library releases. Ghi environment đầy đủ; save model, optimizer, epoch, best loss, early-stop và RNG states để resume. [Reproducibility](https://docs.pytorch.org/docs/main/notes/randomness.html), [checkpoint/resume](https://docs.pytorch.org/tutorials/beginner/saving_loading_models.html).

## 6. Bắt đầu theo thứ tự

1. Chuẩn bị reviewed E001 config/experiment card, weights provenance/license record, CPU pilot runbook và dependency pins. Việc giao Codex chọn kỹ thuật không phải approval đổi dataset/upload cloud.
2. Triển khai canonical src: manifest/mask loader, model/transform/cache, masked loss/metrics, trainer/evaluator và structured run record; test path tách khỏi train. Notebook chỉ launcher. Tên module/CLI chưa tồn tại, không đưa lệnh giả để user copy.
3. Test unknown gradient bằng 0; denominator; train loại test/review_only; backbone/BatchNorm không đổi; metrics fixture có ties/missing support; transform giữ crop; stale cache; save/load/resume/interruption. Synthetic fixtures chỉ kiểm phần mềm, không thành model metrics.
4. Smoke thật 1–3 epochs với train/val, ID riêng: finite loss, head cập nhật/backbone giữ nguyên, checkpoint nạp được. Smoke pass không là model acceptance.
5. E001 full với exact config/code/data; best/last, metrics/environment/checksums và error report. OOM hoặc thay config phải ghi đúng run identity/status theo contract.
6. Review evidence: pipeline lỗi thì sửa; coverage yếu thì ưu tiên dataset version mới; chỉ thử unfreeze/model khác khi lỗi gợi ý có ích. Final test sau khi protocol/candidates chốt. S9 YOLO→automatic crop và real-world holdout còn là gates riêng trước end-to-end.

Run contract bắt buộc: ID/owner/hypothesis, code commit+dirty, dataset/split/encoding, config resolved, seed/environment, status/start/end, metrics/artifacts/checksum, observation và decision. Official run từ implementation/config đã chốt; deletion hiện có chỉ được bỏ qua cho assessment, không tự restore/commit file user. [Experiment management](../15-ml-experiment-management.md).

Cho người mới: train là bộ bài model học; validation là bộ bài dùng kiểm tra lựa chọn lúc phát triển; test là bài thi giữ kín tới cuối. Epoch là một lượt qua train; với cached full-batch ở đây mỗi epoch có một update head. Checkpoint là trạng thái lưu/nạp lại. Baseline là mốc đầu tiên, không mặc nhiên là model cuối.

## 7. Verification và thay đổi

- unittest discover: 113 PASS, 19.921 giây.
- Ruff, compileall, check_repo.py --require-git: PASS; checker dùng Git index, không kiểm mọi link untracked.
- dvc status đúng pointer v4: up to date (local only).
- Read-only verify_payload/read_records; recompute manifest/split/test-subset SHA/IDs; P/N/U, cross-split intersections, source counts: PASS. Test chỉ dùng metadata/hash integrity, không prediction/tuning.
- Checksum list SHA: dbc1bf90a5605cac39b5c96503e71097ecd1eaab5b35e14f311f966edd503f53.

Các lệnh chạy: `.venv/Scripts/python.exe -m unittest discover -s tests`; `-m ruff check src tests scripts`; `-m compileall -q src tests scripts`; `.venv/Scripts/python.exe scripts/check_repo.py --require-git`; `.venv/Scripts/dvc.exe status data/processed/pilot-b/pilot-b-20261005-v4.dvc` và read-only Python assertions dùng schema/package functions đã kiểm tra.

Task chỉ đổi report này và .codex/TASK.md; không src/config/data/ADR, không install/train/upload/commit. Chưa có model metrics, timing/RAM benchmark, visual transform QA, fresh ML environment hay real-world holdout. Nguồn web là tài liệu chính thức/nghiên cứu gốc; hyperparameters và ưu tiên model là đề xuất cho dự án, chưa được chứng minh thực nghiệm.
