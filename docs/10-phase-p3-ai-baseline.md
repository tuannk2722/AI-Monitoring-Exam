# 10 — P3 AI Baseline cho Formulation B

Entry gate: package classifier B đã được owner ký, split/test freeze, crop inference và encoding unknown được review; license/weights và model config được chốt. Chưa đủ gate hiện tại.

Pipeline: YOLO tìm person → context crop → classifier multi-label. Chưa chọn trọng số detector, kiến trúc classifier, head/loss/threshold hoặc masked supervision. Normal là trạng thái đã review, không suy từ thiếu detection. Không biến hai target thành softmax độc quyền.

Các adapter train/evaluate YOLO legacy hiện tại không phải baseline B đã triển khai. Không chạy benchmark YOLO behavior detection rồi báo đó là kết quả formulation B. `configs/baseline.yaml` là scaffold blocked, chưa được phép train.

Khi gate đủ: một hypothesis/run, Git/data/split/label versions, seed, resolved config, environment; lưu interruption/OOM minh bạch. Đo per-target precision/recall/F1 và co-occurrence, coverage unknown, detector/crop error và runtime; thresholds/metrics acceptance chưa tự đặt. Không tune test.

Không có kết quả model ở mốc Audit & Spec này.
