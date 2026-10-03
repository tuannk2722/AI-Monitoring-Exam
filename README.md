# AI Exam Monitoring

Hệ thống nghiên cứu/demo phân tích video phòng thi bằng Computer Vision. AI chỉ tạo dự đoán hành vi quan sát được, sự kiện, mức rủi ro và bằng chứng để con người review; hệ thống không tự kết luận hay dùng cho quyết định kỷ luật thật.

## Trạng thái hiện tại

- Phase: **P0 Project Foundation → P1 Dataset Research**.
- MVP đầu tiên: **recorded video end-to-end**; webcam/live làm sau.
- Candidate labels: `normal`, `looking_around`, `phone_use`.
- Candidate sources: SCB5 và bộ Exam Cheating trên Roboflow; chưa được dùng chính thức trước khi audit license, provenance, annotation và leakage.
- Task formulation: benchmark detection trực tiếp (A) với person detection + crop classification (B); P1 quyết định.
- Dữ liệu/model thật không nằm trong Git. Git lưu code/config/docs/pointer; DVC remote Google Drive lưu binary lớn.

## Kiến trúc làm việc

```text
raw sources -> audit/convert -> canonical processed dataset
              -> train/evaluate -> versioned model candidate
              -> recorded-video inference -> tracking -> event timeline
              -> risk/evidence -> human review (P7)
```

Ba owner chính:

| Vai trò | Contract bàn giao |
|---|---|
| Data Lead | `data/processed/exam/` + `dataset.yaml` + `manifest.csv` + `label_map.yaml` + audit report |
| Model Lead | experiment config + metrics + plots + DVC-tracked `best.pt` + run metadata |
| Pipeline Lead | annotated video + structured JSON predictions/tracks/events + performance report |

Xem [docs/00-INDEX.md](docs/00-INDEX.md) trước khi làm task.

## Thiết lập local

Yêu cầu: Python 3.11 (khuyến nghị), Git. Máy local hiện chỉ cần chạy code, test và audit mẫu nhỏ; Colab Free dùng cho GPU training.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements/base.txt
pip install -r requirements/dev.txt
```

Cài ML/DVC khi cần:

```bash
pip install -r requirements/ml.txt
pip install -r requirements/dvc.txt
```

Kiểm tra repository:

```bash
python -m unittest discover -s tests -v
python -m compileall -q src tests
python scripts/check_repo.py
```

## DVC + Google Drive

Người sở hữu Drive tạo folder và team cấu hình một lần (không commit credential):

```bash
dvc init
dvc remote add -d teamdrive gdrive://<FOLDER_ID>
dvc remote modify teamdrive gdrive_use_service_account false
```

Chỉ commit `.dvc/config` và pointer `.dvc`; authentication cục bộ nằm ngoài Git. Test với folder nhỏ trước khi đưa dataset thật vào. Chi tiết: [docs/22-training-environment-and-runbook.md](docs/22-training-environment-and-runbook.md).

## Luồng làm việc ngắn

```bash
git switch -c data/12-canonical-dataset
dvc pull
python -m ai_exam_monitoring.data.audit --dataset data/raw/scb --output artifacts/reports/scb-audit.json
python -m ai_exam_monitoring.data.build_dataset --config configs/datasets/exam_v0.1.yaml
python -m unittest discover -s tests -v
```

Training chỉ được chạy khi `dataset_version`, `split_version`, config và experiment ID đã có:

```bash
python -m ai_exam_monitoring.training.train --config configs/baseline.yaml --experiment-id E001 --owner member-b
python -m ai_exam_monitoring.evaluation.evaluate --config configs/baseline.yaml --experiment-id E001
```

## Những gì repository này không giả vờ đã có

- Không kèm dataset SCB5/Roboflow, model weights hoặc video người thật.
- Không có số metric giả, threshold giả hay `best.pt` giả.
- Chưa coi taxonomy/task formulation là frozen cho tới khi P1 hoàn tất.
- Tracking/event/risk có contract và code nền, nhưng chỉ được tích hợp với model đã promote ở P5/P6.
- Web FastAPI được quyết định cho P7 nhưng chưa phải critical path hiện tại.

Các quyết định còn thiếu dữ liệu để chốt được ghi rõ trong [docs/00-INDEX.md](docs/00-INDEX.md), không bị che bằng mock UI.
