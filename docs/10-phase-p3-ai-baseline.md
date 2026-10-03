# 10 — P3 AI Baseline

Entry gate: dataset/tag P2 đã tồn tại, `dataset.yaml` resolve được, ADR về label/task đã được accept, license model/weight đã review.

## Contract E001

- Một hypothesis và một `configs/baseline.yaml` đã review.
- Model candidate nhẹ (`yolo11n.pt` là candidate trong config, không được silently đóng băng).
- Git commit, dataset/split/label-map version và seed cố định.
- Lần chạy đầu là smoke benchmark 1–3 epoch; ghi lại GPU/RAM/disk/thời gian/epoch và hành vi resume.
- Full run lưu: config đã resolve, environment, status, validation metrics, plots, `best.pt` và tùy chọn `last.pt`.

```bash
python scripts/benchmark_training.py --experiment-id E001-smoke --owner <name> --epochs 1
python -m ai_exam_monitoring.training.train --config configs/baseline.yaml --experiment-id E001 --owner <name>
python -m ai_exam_monitoring.evaluation.evaluate --config configs/baseline.yaml --experiment-id E001
```

Không được tune trên test set. `evaluate --test` yêu cầu flag config cuối cùng đã review và được dành cho giao thức đánh giá cuối. Một run bị OOM/gián đoạn phải được ghi nhận là failed/interrupted; nếu batch size hay image size thay đổi thì phải tạo config/run mới.

## Báo cáo tối thiểu

Precision, recall, mAP50, mAP50-95 và kết quả per-class cho detection; precision/recall/F1/confusion matrix cho classification. Bao gồm mẫu false-positive/false-negative theo error category, runtime metadata và SHA-256 của artifact. Không có một metric nào đơn lẻ chứng minh model đã đủ tốt.
