# AI Exam Monitoring

Hệ thống nghiên cứu/demo phân tích video phòng thi bằng Computer Vision. AI chỉ tạo dự đoán hành vi quan sát được, sự kiện, mức rủi ro và bằng chứng để con người review; hệ thống không tự kết luận hay dùng cho quyết định kỷ luật thật.

## Trạng thái hiện tại

- Phase: **P0 Project Foundation → P1 Dataset Research**.
- MVP đầu tiên: **recorded video end-to-end**; webcam/live làm sau.
- Candidate labels: `normal`, `looking_around`, `phone_use`.
- Candidate sources: SCB5 và bộ Exam Cheating trên Roboflow; chưa được dùng chính thức trước khi audit license, provenance, annotation và leakage.
- Formulation B đã chốt: YOLO person → crop context → classifier multi-label (ADR-012).
- Dữ liệu/model thật không nằm trong Git. Git lưu code/config/docs/pointer; DVC remote Google Drive lưu binary lớn.

## Kiến trúc làm việc

```text
raw sources -> audit/convert -> canonical processed dataset
              -> train/evaluate -> versioned model candidate
              -> recorded-video inference -> tracking -> event timeline
              -> risk/evidence -> human review (P7)
```

Chế độ solo: chủ repository đảm nhiệm cả ba vai trò và là người chốt; Codex hỗ trợ triển khai/review.

| Vai trò | Contract bàn giao |
|---|---|
| Data Lead | Package classifier B có version, manifest/target states/split/provenance; exporter còn cần triển khai |
| Model Lead | experiment config + metrics + plots + DVC-tracked `best.pt` + run metadata |
| Pipeline Lead | annotated video + structured JSON predictions/tracks/events + performance report |

Xem [docs/00-INDEX.md](docs/00-INDEX.md) trước khi làm task.

## Thiết lập local

Yêu cầu: Python 3.11 (khuyến nghị), Git. Máy local hiện chỉ cần chạy code, test và audit mẫu nhỏ; Colab Free dùng cho GPU training.

```bash
# Windows: py -3.11 -m venv .venv
# Linux/macOS: python3.11 -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements/base.txt
python -m pip install -r requirements/dev.txt
```

Dự án hỗ trợ Python >=3.11,<3.13; CI dùng 3.11. Kiểm tra `python --version` sau activate. Nếu không activate được, dùng `.venv\Scripts\python.exe` thay `python` trong mọi lệnh.

Cài ML/DVC khi cần:

```bash
python -m pip install -r requirements/ml.txt
python -m pip install -r requirements/dvc.txt
```

Kiểm tra repository:

```bash
python -m unittest discover -s tests -v
python -m compileall -q src tests scripts
python -m ruff check src tests scripts
python scripts/check_repo.py --require-git
```

Checker dùng Git index, kể cả staged/force-added; bỏ qua file ignored/untracked. Stage file cần kiểm tra trước commit. Đây là kiểm tra đường dẫn theo policy, không phải secret scanner nội dung hoặc audit lịch sử Git.

Bản ZIP: `python scripts/check_repo.py` chỉ kiểm tra cấu trúc và index tài liệu, cảnh báo tracking chưa xác minh; exit 0 nếu cấu trúc hợp lệ. `--require-git` trả lỗi khi thiếu `.git` và được CI sử dụng. Clone bằng Git hoặc khởi tạo Git rồi stage file dự định commit để kiểm tra tracking. Nếu `.git` tồn tại nhưng Git lỗi, checker luôn trả lỗi.

## DVC + Google Drive

Owner tạo folder Drive restricted và cấu hình một lần (không commit credential):

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
python -m ai_exam_monitoring.data.audit --dataset data/raw/scb --images images --labels labels --source-names source-names.json --output artifacts/reports/scb-audit.json
python -m unittest discover -s tests -v
```

Build/train/evaluate YOLO legacy từ chối config B hiện hành. Chưa có exporter hay trainer classifier B được hỗ trợ. [Trạng thái hai nguồn và gate release](docs/data/dataset-research.md) là đầu mối hiện hành; không chạy train hoặc coi audit snapshot là dataset accepted.

## Audit nguồn và ảnh mẫu bbox (CPU)

Chỉ định cấu trúc đã xác minh: `--images` và `--labels` là thư mục tương đối dưới `--dataset`. `images/a/x.jpg` ghép với `labels/a/x.txt`, không ghép với `labels/b/x.txt`. Với nguồn `train/images` + `train/labels`, truyền đúng hai đường dẫn đó; báo cáo chỉ bao phủ subtree đã chọn, không kiểm tra chéo các split khác. Không tự đoán cấu trúc SCB5/Roboflow.

Cung cấp `source-names.json` dạng `{"0": "tên lớp nguồn đã xác minh", "7": "tên lớp nguồn khác"}`; đây là ID → tên của nguồn, **không phải mapping canonical**. Có thể dùng YAML với trường `names` là mapping ID → tên (như `dataset.yaml` do builder xuất). Không tự suy ra tên hay ID từ thứ tự một danh sách.

```bash
python -m ai_exam_monitoring.data.validate_labels --labels data/raw/<source>/labels --class-ids 0,7
python -m ai_exam_monitoring.data.audit --dataset data/raw/<source> --images images --labels labels --source-names source-names.json --output artifacts/reports/source-audit.json
python -m ai_exam_monitoring.data.overlay --dataset data/raw/<source> --images images --labels labels --source-names source-names.json --output-dir outputs/source-overlays-v1 --limit 20
```

ID `0,7` chỉ minh họa cách truyền tham số; phải thay bằng ID thật từ nguồn. Tên ngoài ASCII cần `--font <font.ttf>` có đủ glyph (Windows ví dụ `C:/Windows/Fonts/arial.ttf`). Output phải nằm ngoài nguồn và `data/raw`; thư mục overlay phải mới hoặc rỗng. Mỗi ảnh có bbox, ID và bảng tên nhãn; `manifest.json` truy ngược ảnh/nhãn và `audit.json` liệt kê các cặp bị loại.

Chạy thử bằng fixture phần mềm tự sinh, không chứa người thật:

```bash
python tests/fixtures/make_audit_fixture.py --output outputs/audit-fixture
python -m ai_exam_monitoring.data.audit --dataset outputs/audit-fixture --images images --labels labels --source-names outputs/audit-fixture/source-names.json --output outputs/audit-fixture-report.json
python -m ai_exam_monitoring.data.overlay --dataset outputs/audit-fixture --images images --labels labels --source-names outputs/audit-fixture/source-names.json --output-dir outputs/audit-fixture-overlays --limit 2
```

Thêm `--broken` khi tạo fixture ở thư mục mới để kiểm tra các lỗi đã biết. Fixture chỉ kiểm chứng phần mềm, không phải dataset được accepted hay bằng chứng chất lượng model.

Audit tự động: thiếu/orphan, ghép mơ hồ, decode ảnh, cú pháp/bbox/class ID, nhãn rỗng, phân bố lớp, kích thước bbox và nhóm SHA-256 trùng byte. `README*.txt`/`classes.txt` là metadata, không tính là label. Không có label file là lỗi; file label rỗng hợp lệ về cấu trúc nhưng phải xem ảnh để xác nhận ngữ nghĩa.

Chưa kiểm tra gần trùng, group/split leakage, license/consent hoặc ngữ nghĩa nhãn. Owner cần xem độ khớp bbox, annotation unit, nhãn sai/thiếu và mapping đề xuất. Overlay lấy tối đa N cặp hợp lệ theo đường dẫn, **không phải mẫu phân tầng/đại diện**. Exit code: 0 = các kiểm tra đã thực hiện pass, 1 = có lỗi audit (report vẫn được ghi; overlay vẫn xuất các cặp hợp lệ), 2 = đầu vào/output không hợp lệ. Pass không phê duyệt dataset. Contract chi tiết: [source-audit.md](docs/data/source-audit.md).

## Những gì repository này không giả vờ đã có

- Không kèm dataset SCB5/Roboflow, model weights hoặc video người thật.
- Không có số metric giả, threshold giả hay `best.pt` giả.
- B/person unit/semantics đã chốt; classifier schema/crop inference và dataset release chưa freeze.
- Tracking/event/risk có contract và code nền, nhưng chỉ được tích hợp với model đã promote ở P5/P6.
- Web FastAPI được quyết định cho P7 nhưng chưa phải critical path hiện tại.

Các quyết định còn thiếu dữ liệu để chốt được ghi rõ trong [docs/00-INDEX.md](docs/00-INDEX.md), không bị che bằng mock UI.
