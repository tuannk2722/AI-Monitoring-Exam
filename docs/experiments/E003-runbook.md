# E003 — Runbook thực thi đã được duyệt

Owner nghiệm thu ngày 2026-10-08 theo [ADR-016](../decisions/ADR-016-e003-v6-local-linear-probe.md) và [approval](E003-approval.json). Dùng đúng [protocol đã review](E003-protocol.md); các mô tả pending trong proposal là snapshot trước nghiệm thu.

Chạy từ clean detached checkout `outputs/E003-code`; Python tuyệt đối `D:\ai-exam-monitoring-final\outputs\E001-env\Scripts\python.exe`, PYTHONPATH là `src` của checkout, workspace dữ liệu/approval `D:\ai-exam-monitoring-final`. Hai config lấy từ checkout. Mọi lệnh Python có `-X utf8`. Không download/upload hay gọi test evaluator.

Trước chạy: full unittest trong CPU environment, Ruff/compile/repository check, pip check, byte/resolved config/protocol pins, dataset/preservation/weights/lock, dung lượng và Git sạch. Lệnh train/evaluate đúng mục7 protocol; output đích chưa tồn tại. Smoke `--interrupt-after 1` dự kiến thoát với KeyboardInterrupt và record INTERRUPTED; lưu snapshot/checksum trước `--resume`. Chỉ baseline khi smoke FINISHED3epoch.

Baseline đúng một run, val reload phải exact predictions và metrics. Báo cáo hậu xử lý dùng predictions đã freeze, canonical `evaluate_scores`, BCE probability float64 theo protocol, không clip/tuning. So historical13 với E002 đã pin; source/group/normal slices và tất cả FP/FN train/val. Primary lấy BCE logits trainer trên val50, đối chứng hằng từ train.

Giữ run/cache/checkpoints/binary local. Ghi checksums, DVC local pointers và kiểm cache restore local; không remote push. Sau chạy xác minh lại payload, approval/config, checkpoint, môi trường/code và không có test features/predictions. Kết quả thật nằm tại [experiment card](E003-results.md) và [execution report](../../artifacts/reports/E003-execution-20261008/README.md) sau hoàn tất.
