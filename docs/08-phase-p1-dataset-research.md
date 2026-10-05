# 08 — P1 Dataset Research

Audit & Spec được tổng hợp cho Formulation B theo ADR-011/012. Không tiếp tục benchmark A/B hoặc vòng review ảnh nhỏ lẻ. [Dataset research](data/dataset-research.md) là trạng thái/vai trò SCB5 và Roboflow hiện hành.

Bằng chứng: archive identity/hash,class namespaces,structure/geometry,exact duplicates,mẫu trực quan vàowner decisions. Audit tự động không chứng minh annotation đầy đủ. Subset [pilot B local v4](../artifacts/reports/pilot-b-release-acceptance-20261005/README.md) đã accepted; không chấp nhận toàn bộ hai nguồn cho train.

Phạm vi112 ledger/84used,reviewed crop/targets,normal/negative/unknown coverage,group boundaries/split vàquyền local của pilot đã được owner chốt. Runtime crop,model/loss vàremote storage chưa được chốt bằng approval dataset; không hỏi lại quyền SCB hoặc kiến trúc.

Mỗi nguồn giữ ba tài liệu: candidate card, audit lịch sử, consolidated review. Raw bất biến; historical evidence hợp nhất giữ nội dung/hash. Không thêm script theo từng câu hỏi review.

[P2](09-phase-p2-dataset-preparation.md) đã có package reviewed-crop v4 và test freeze; DVC pointer có sẵn, smoke round-trip đạt. Owner đã cho phép storage v4 trên Drive restricted; trạng thái handoff/cache sạch theo runbook/WORKLOG. Không tuyên bố toàn P0/P1/P2 hoặc model quality bằng release/storage handoff.
