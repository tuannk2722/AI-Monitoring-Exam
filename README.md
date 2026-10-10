# AI Exam Monitoring

Nghiên cứu/demo hành vi quan sát được trên video phòng thi: person detector → context crop → classifier multi-label `[phone_use, looking_around]` → tracking/events → human review. Normal là metadata, unknown masked; không kết luận kỷ luật hoặc định danh sinh viên.

**Hiện tại:** bốn dataset releases v4–v7 trên crop đã review và ba frozen ResNet18 linear probes E001–E003 có kết quả thật. V7 local: 689 train / 49 val / 11 test; chưa có model Selected/independent holdout, chưa E004 fine-tune hoặc pipeline video B/tracking/web. Packaging/baseline PASS không thay model-quality gate.

Bộ spec tại [docs/00-INDEX.md](docs/00-INDEX.md):

| Tài liệu | Dùng để làm gì |
|---|---|
| [System](docs/system.md) | Phạm vi, trạng thái từng capability, architecture/FR/contracts, roadmap và quyết định |
| [Data](docs/data.md) | Semantics/schema, nguồn đã nghiên cứu, releases/corrections/coverage và workflow QA/holdout |
| [Training](docs/training.md) | Recipe, metrics/error analysis E001–E003, E004 Draft và gates/next work |
| [Development](docs/development.md) | Workflow agent, setup/checks, storage và reuse/reproduction lịch sử |

Agent bắt đầu từ AGENTS/index/TASK, đọc đúng phần spec và code liên quan; không cần mở cả archive/report history để biết context. Archive giữ exact input/code/evidence khi cần lấy dữ liệu hoặc tái lập, không là spec chính.

Python >=3.11,<3.13; setup base/dev và checks theo development spec. Classifier/ML/DVC dependencies chỉ khi cần. Git lưu source/spec/config/metadata; media/dataset/model local/DVC theo quyền, không commit binaries. V4 remote restricted đã kiểm; pointer/ZIP/archive local chưa là remote backup. Không có training dvc.yaml để chạy `dvc repro`.
