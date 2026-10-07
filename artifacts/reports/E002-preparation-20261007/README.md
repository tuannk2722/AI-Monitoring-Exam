# E002 — Đề xuất cấu hình và protocol nghiệm thu

Ngày 2026-10-07. **Đã chuẩn bị đề xuất; chưa chạy huấn luyện.** Owner/reviewer: chủ repository (solo). E002 chưa được duyệt chạy và còn blocker loader v5; kiểm data/config PASS không đồng nghĩa training-ready.

## Đề xuất cần nghiệm thu

[E002.yaml](../../../configs/experiments/E002.yaml) trỏ đúng package `pilot-b-20261007-v5`, split `pilot-b-v5-train-expansion-v1`, encoding `pilot-b-targets-v1`, checksum-list SHA `2dc6a0f700c04276e8fb2b073e98fb050824d8839d398bd254b2297065f92f5a`. Package/release accepted và E001 không thay đổi.

**Giả thuyết đề nghị:** bổ sung đúng 20 crop train đã duyệt của v5, giữ recipe E001, làm giảm validation macro masked BCE trên cùng13 mẫu so E001. Primary tham chiếu E001 best epoch12: `0.5477269887924194`; tiêu chí nghiên cứu đề xuất `ΔBCE<0`, không phải numerical promotion gate hoặc kiểm định có ý nghĩa thống kê. Model vẫn frozen ResNet18 IMAGENET1K_V1 + linear head hai target; seed42, AdamW LR0.001/WD0.0001, CPU4 threads, tối đa200 epoch, patience20/min_delta0.0001, threshold0.5 cố định.

Biến có chủ đích duy nhất: train 60 → 80, thêm 19 Classroom và EXP-RF-019. Val 13/test 11 giữ nguyên v4; unknown mask 0; normal chỉ metadata. Source và số crop cùng thay đổi nên không tách hiệu ứng của chúng bằng experiment này. Toàn 19 Classroom thuộc một nhóm train, không phải 19 tình huống độc lập mới.

[Protocol chi tiết](../../../docs/experiments/E002-protocol.md) quy định: kiểm pins/approval; smoke kỹ thuật riêng 3 epoch có interruption/resume; baseline từ head mới; chọn best bằng raw minimum validation BCE, ties chọn sớm; evaluation val độc lập; AP/precision/recall/F1, confusion/support/unknown, prevalence baseline và error/source slices; artifact/checksum/status; test freeze và giới hạn kết luận. [E002-smoke.yaml](../../../configs/experiments/E002-smoke.yaml) là cấu hình đề xuất cho gate kỹ thuật sau nghiệm thu, không dùng để chọn model và chưa chạy.

Đề nghị nghiệm thu model/weights theo phạm vi nghiên cứu local hiện có, ngoại lệ CPU local riêng E002, configs chính/smoke, giả thuyết/metrics/protocol và output local. ADR-014 chỉ phê duyệt E001; không tự kế thừa approval đó. [Bản ghi pending](../../../docs/experiments/E002-approval.json) có `configs={}`, `proposed_configs` pin digest; trainer phải từ chối bản ghi này trước nghiệm thu.

| Digest resolved config theo trainer | SHA-256 |
|---|---|
| E002 | `7ffb2807d5602aaabc2bd95d44f3c7cc58d1341ca9d6eae4deef73de949c62bf` |
| E002-smoke | `393dd16d49e6658789f48fa69922af1a74ce06af307993c8e905ac53a6a175ed` |

Digest trên tính bằng `digest_json(config.to_dict())`, khác SHA bytes YAML. Pins của YAML/protocol/approval/code/weights/baseline nằm trong [verification](verification.json); [comparison](config-comparison.json) lưu toàn bộ proposed configs và 7 field khác E001, tất cả biến model/training/evaluation giữ nguyên. Đây không phải resolved config của một run đã chạy.

## Bằng chứng kiểm tra

| Kiểm tra | Kết quả |
|---|---|
| Strict schema `load_config` | PASS cho E002 và E002-smoke |
| Payload/schema/membership | PASS: ledger208, manifest104 =80train/13val/11test,93review_only/11excluded;197 crop khớp SHA |
| Split/preservation | PASS: toàn60 train cũ và24 val/test giữ source/crop/geometry/nhãn/mask/group/rights;20 train mới đúng proposal |
| Leakage / Classroom | PASS:0 exact image/crop/group qua split; Classroom24 cùng1 nhóm,19train/5fully-unknown review_only |
| Weights / E001 controls | PASS: local weights SHA/receipt đúng; các training module khớp provenance E001; không download |
| Approval/test guard | PASS: pending approval bị từ chối; test selection không explicit bị từ chối; loader v4/E001 vẫn PASS |
| Tests phù hợp scope | PASS:8 test có sẵn về schema/mask/metrics/selection/final-protocol/approval; không chạy train thực tế |
| Repository / văn bản / diff | PASS: checker `--require-git`, UTF-8/JSON/YAML/local links và whitespace/diff check |
| Loader trainer trên v5 | **BLOCKED: `KeyError: 'status'`**; chưa training-ready |

[Data checks](data-checks.json) lưu coverage và pins; [verification](verification.json) tách rõ PASS integrity với blocker chạy. Kiểm payload chỉ đọc bytes/metadata, không xem ảnh test hoặc inference. Review-only/excluded không được thêm vào manifest; excluded vẫn có crop metadata trong ledger nhưng không có file crop xuất.

Audit local có thể chạy lại từ repo bằng `outputs/E001-env/Scripts/python.exe outputs/E002-preparation-tools/verify.py` với `PYTHONPATH=src`; script được pin trong verification, nằm local/ignored, không phải production logic hoặc artifact cần upload. Tám test đã chạy là các test `TrainingTests` về config; unknown loss; missing support/nonfinite; AP ties/confusion; undefined metrics; selection; final-test protocol; approval. Không chạy lại full suite vì src/tests không đổi.

## Blocker bắt buộc trước huấn luyện

`training.data.verify_dataset` đang đòi `release.json.test_freeze` inline với `status=frozen`, manifest/split/test hashes và test-ID list. V5 accepted pin `{path,sha256}` tới `evaluation-preservation.json`, nên loader lỗi trước feature extraction. Config YAML không thể khắc phục format này. Dataset hợp schema/package và checksum vẫn PASS; không sửa accepted release hoặc bỏ freeze gate để ép chạy.

Đề nghị sửa hẹp loader để hỗ trợ preservation pointer có xác minh path/hash/owner/parent freeze và semantic preservation, đồng thời kiểm manifest/ledger/split/leakage. Cần regression v4 và tamper tests v5 rồi preflight PASS trước chạy. Chi tiết và điều kiện chốt `TBD-E002-LOADER` nằm trong protocol; **chưa sửa src trong đợt chuẩn bị này**. Owner cần chốt scope sửa khi nghiệm thu; approval config đơn thuần chưa đủ để chạy.

## Giới hạn và điểm dừng

Val chỉ 13 crop/2 nhóm; phone có 7P/1N nên một FP thay đổi tỷ lệ rất lớn. Val/test không có Classroom, không đo được generalization độc lập trên nguồn mới. Validation đã dùng để chọn epoch và dùng lại so baseline nên không có kết luận thống kê/generalization/promotion. Co-occurrence validation1fully-known/0positive không đủ metric; giữ null/reason.

Test11 đã evaluate ở E001, chỉ kiểm integrity lần này. Đề nghị hiện tại **không bao gồm final-test inference**; nếu cần sau này phải freeze một candidate rồi nghiệm thu protocol riêng. Numerical promotion gate và real-world holdout vẫn TBD có owner; không mở runtime detector/tracking/web từ kết quả chuẩn bị.

Đợt này chỉ tạo config/protocol/bản ghi pending/báo cáo và cập nhật checkpoint/index/worklog. Chưa smoke, train, model inference, final test, upload, commit hoặc push; không có metric E002/checkpoint/timing giả. Bước tiếp sau nghiệm thu là giải quyết loader, kiểm lại toàn pins/guards trên clean checkout, rồi mới thực hiện phạm vi chạy đã được duyệt.
