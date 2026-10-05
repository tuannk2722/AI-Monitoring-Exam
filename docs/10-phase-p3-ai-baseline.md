# 10 — P3 AI Baseline cho Formulation B

Entry gate classifier trên reviewed crops: package B đã được owner ký, split/test freeze và encoding unknown đã review; model/weights/license, loss/normalization, transforms, hyperparameters và experiment config phải được owner chốt. Dataset gate đạt với pilot v4; model/config và trainer/evaluator B chưa có.

Pipeline end-to-end: YOLO tìm person → context crop → classifier multi-label. Ngoài classifier baseline, cần owner review detector/weights và S9 automatic crop policy/QA trước end-to-end. Masked supervision đã chốt tại ADR-013; model/head/loss/normalization/threshold chưa chọn. Normal là metadata đã review, không suy từ thiếu detection hoặc thêm output thứ ba. Không biến hai target thành softmax độc quyền.

Train/evaluate YOLO A, benchmark launcher và scaffold config/pipeline đã gỡ theo owner ngày 2026-10-05. Chưa có lệnh train/evaluate B cho đến khi model/config được duyệt và implementation được kiểm thử. Không chạy detector adapter rồi báo đó là kết quả classifier B.

Khi gate đủ: một hypothesis/run, Git/data/split/label versions, seed, resolved config, environment; lưu interruption/OOM minh bạch. Loader dùng 84 records từ manifest, không quét 112 crop/ledger; loss/metrics chỉ target known, báo support/unknown từng target và denominator co-occurrence. Model/epoch/threshold selection dùng train/val; test chỉ evaluation cuối theo freeze. Detector/crop error và runtime được đo khi triển khai end-to-end. Thresholds/metrics acceptance chưa tự đặt.

Không có kết quả model ở mốc Audit & Spec này.
