# ADR-015 — E002 local linear probe trên Pilot B v5

- Trạng thái: **Accepted** cho phạm vi owner đã duyệt dưới đây.
- Ngày: 2026-10-07. Owner/reviewer: chủ repository (solo); triển khai: Codex.
- Bằng chứng: owner đã review toàn bộ thay đổi và thông số E002.yaml, “Approve bản này, hãy thực hiện tiếp! Chỉ dừng lại khi xong hoặc có gì cần hỏi hay review/chốt lại.”
- Proposal đã review: [E002 protocol](../experiments/E002-protocol.md), [báo cáo](../../artifacts/reports/E002-preparation-20261007/README.md), [config E002](../../configs/experiments/E002.yaml) và smoke kỹ thuật trong hồ sơ.

## Quyết định và phạm vi

1. Chạy E002 theo exact resolved config đã duyệt: Pilot B v5, frozen ResNet18 IMAGENET1K_V1, linear head hai target, masked macro BCE, optimizer/transforms/seed/budget/threshold kế thừa E001. Chỉ thay membership train từ60 lên80; giữ val13/test11 và semantics accepted. Config digest/pins và lời phê duyệt đầy đủ nằm trong [approval](../experiments/E002-approval.json).
2. Bổ sung ngoại lệ CPU local riêng E002 cho hướng Colab/GPU ở doc22, cùng môi trường CPU đã pin. Chạy từ clean isolated Git checkout; có thể tạo local commit phục vụ provenance, không cần Git push hoặc cloud. Weights local được xác minh lại; không random fallback, download hoặc mở rộng quyền phân phối pretrained.
3. Sửa loader theo hướng đã review: đọc inline freeze v4 hoặc pointer preservation v5; xác minh path/hash/owner/parent freeze, semantic preservation, manifest/ledger/split/leakage; từ chối thiếu hoặc thay evidence. Không sửa package accepted, không bỏ freeze gate hoặc tự tạo split/test mới. Kiểm v4 regression và tamper v5 trước chạy.
4. Chạy smoke3 epoch riêng có interruption/resume để kiểm kỹ thuật, sau đó một E002 chính từ head mới. Chọn candidate bằng raw minimum validation macro masked BCE, ties chọn sớm; threshold0.5 cố định. Reload best trên val để xác minh scores/metrics; so E001 và báo trade-offs từng target/source theo protocol.
5. Giả thuyết/tiêu chí nghiên cứu là Δvalidation BCE<0 so E001. Không tuning trên test; không tự đặt numerical promotion gate. Một run không đạt giả thuyết vẫn là kết quả cần lưu, không sửa E002 để đạt metric.

## Giới hạn

Approval này **không gồm final-test inference**, upload/media/weights ra ngoài, model promotion, runtime detector/crop, tracking/events/risk hoặc web. Test đã dùng E001; nếu có final evaluation sau này cần một protocol/candidate freeze và owner approval riêng. Classroom chỉ ở train, validation nhỏ và source-confounded; chưa có holdout thực tế độc lập.

Artifact/checksum và statuses phải có thật. OOM/interruption không cho phép đổi config trong cùng identity; resume cần code/config/data/environment/checkpoint khớp. Proposal/preparation evidence giữ làm snapshot lịch sử; kết quả chạy và verification mới được ghi riêng.
