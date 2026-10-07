# AGENTS.md

## Source of truth

1. Đọc `docs/00-INDEX.md`.
2. Đọc đúng tài liệu được index cho loại task.
3. Chỉ coi ADR `Accepted` và config đã review là quyết định triển khai.
4. Khi code khác docs, báo xung đột; không tự đổi label/split/metric/scope để làm code chạy.
5. Không đọc lại tài liệu không đổi trong cùng task; ghi lại danh sách đã đọc.

Thứ tự ưu tiên: accepted ADR → canonical docs → configs → code → notebook.

## Task checkpoint (`.codex/TASK.md`)

- Mỗi task đang hoạt động phải có `.codex/TASK.md`; tạo hoặc cập nhật trước khi sửa artifact/code. Format theo `docs/templates/task-template.md`, bổ sung checkpoint khi cần.
- Khi bắt đầu hoặc tiếp tục sau resume/compaction, đọc `docs/00-INDEX.md` và `.codex/TASK.md` nếu có; đối chiếu Git, files/artifacts và chỉ đọc lại docs đã thay đổi. TASK cũ hoặc mâu thuẫn phải được sửa theo yêu cầu user và source of truth, không được dùng như authority.
- TASK là bộ nhớ điều phối cho một task hiện hành, không thay ADR/spec/config, không tự biến đề xuất thành Accepted hoặc câu hỏi chưa trả lời thành approval. Không chứa credentials, dữ liệu định danh hoặc media.

## AI-first order

`dataset → annotation QA → baseline → evaluation → real-world holdout → model improvement → tracking/events → web`.

Không mở rộng dashboard, realtime, cloud hoặc authentication khi milestone AI hiện tại chưa đạt exit gate.

## Không được tự quyết âm thầm

- class semantics, task formulation, official dataset hoặc split;
- pretrained model/license, training variable, thresholds hoặc acceptance metrics;
- risk/evidence/review semantics;
- dùng test set để tuning;
- upload dữ liệu người thật lên dịch vụ ngoài khi chưa có consent/policy.

Nếu thiếu quyết định, thêm `TBD` có owner, lý do và điều kiện chốt; không bịa giá trị mặc định trông như đã được phê duyệt.

Không tự quyết âm thầm KHÔNG có nghĩa là bắt Owner làm thủ công mọi việc. AI phải chủ động dùng tự động hóa (heuristics, thuật toán, pre-trained models) để tạo ra các đề xuất (Draft Proposals). Owner chỉ đóng vai trò nghiệm thu, xác nhận (Approve/Reject) ở mức high-level qua báo cáo hoặc 1 lệnh CLI.

## Data/privacy

- `data/raw` bất biến; transform bằng code sang `interim/processed`.
- Không commit ảnh/video/model/checkpoint/credential/notebook output lớn.
- Không đưa tên/mã sinh viên thật vào filename/manifest.
- Không log ảnh/video người thật lên W&B nếu policy chưa cho phép.
- Mọi dataset mutation phải tạo version/pointer mới và có owner review được ghi lại; Codex hỗ trợ, không yêu cầu người thứ hai.

## Experiment contract

Mỗi run phải có: experiment ID, owner, hypothesis, Git commit, dataset/split/label-map version, resolved config, seed, environment, status, metrics, artifacts/checksum, observation và decision. OOM/interruption là trạng thái run, không được âm thầm đổi batch/config trong cùng identity.

## Coding rules

- Canonical logic nằm trong `src/`; notebook chỉ exploration/launcher.
- Config YAML chứa experiment variables; code không hard-code chúng.
- Core modules không phụ thuộc web framework.
- Dùng structured schemas thay dict không định nghĩa cho prediction/track/event.
- Không tạo mock metric/model prediction trong production path.
- Mỗi PR có một owner và một mục tiêu chính. Solo: owner tự review/chốt, Codex hỗ trợ; ghi bằng chứng kiểm tra, không yêu cầu người thứ hai.

## Spec and document rules

- Toàn bộ đều phải được viết bằng tiêngs việt.

## Stop conditions

Dừng thay đổi có liên quan nếu: data/license/path/version không rõ; label/split mâu thuẫn; test set có nguy cơ bị dùng sai; task train thiếu config/experiment; cần scope/metric/risk decision mới; hoặc có nguy cơ lộ dữ liệu/credential. Các phần độc lập khác vẫn có thể tiếp tục.
