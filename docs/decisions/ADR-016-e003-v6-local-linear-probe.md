# ADR-016 — E003 local linear probe trên Pilot B v6

- Trạng thái: **Accepted** cho phạm vi owner đã review và approve.
- Ngày: 2026-10-08. Owner/reviewer: chủ repository (solo); Codex thực thi.
- Bằng chứng owner: “tôi đã review và approve, hãy thực hiện tiếp tới khi hoàn thành! trong quá trình thực hiện nếu có gì chưa rõ thì hãy hỏi lại tôi.”
- Hồ sơ: [protocol E003](../experiments/E003-protocol.md), [cấu hình](../../configs/experiments/E003.yaml), [smoke](../../configs/experiments/E003-smoke.yaml), [báo cáo chuẩn bị](../../artifacts/reports/E003-preparation-20261008/README.md). Exact pins và snapshot pending nằm trong [approval](../experiments/E003-approval.json).

## Quyết định

1. Chạy đúng frozen ResNet18 IMAGENET1K_V1 + head mới trên accepted v6 train317/val50. Giữ optimizer, preprocessing, loss, seed42, budget và threshold0.5 theo config đã duyệt; không sweep hoặc fine-tune encoder.
2. Chấp thuận ngoại lệ CPU local riêng E003 theo closure E001/E002 và weights đã pin, local commit/clean isolated checkout, không cần Git push/cloud. Giữ phạm vi nghiên cứu local và attribution pretrained đã ghi, không mở quyền phân phối.
3. Chạy full suite/preflight, smoke3epoch có interruption/resume, một baseline chọn raw minimum val50 macro masked BCE, rồi reload validation để kiểm exact scores/metrics. Không dùng smoke để chọn model/tuning.
4. H1 dùng delta BCE E003 trên val50 so đối chứng prevalence chỉ từ train317. Historical13/added37 là slices mô tả; so E002 trên historical13, không so trực tiếp metric khác tập hoặc suy cải thiện nhân quả. Báo trade-off và mọi FP/FN/source/group/normal slices.
5. Ghi experiment contract, artifacts/checksums, runtime/status, observation/decision; giữ binary local hoặc DVC local. OOM/interruption không cho phép đổi recipe trong cùng identity.

## Giới hạn

Test11 chỉ integrity; không final-test inference hoặc feature extraction. Không upload, mutation dataset/label/split, promotion, runtime crop, tracking/events/web. Holdout độc lập và gate promotion vẫn TBD. Proposal/preparation là lịch sử trước duyệt; trạng thái pending trong các snapshot không thay approval hiện hành. Protocol đã review giữ nguyên nội dung, không viết lại giả thuyết sau kết quả.
