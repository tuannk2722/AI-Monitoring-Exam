# Hướng dẫn coding agent

## Bắt đầu và quyết định

- Đọc `docs/00-INDEX.md` và `.codex/TASK.md`, đối chiếu Git/files và code trước sửa. Đọc đúng section trong bốn specs; system/data/training đã chứa trạng thái, decisions, nghiên cứu, results và next work. Không đọc lại docs không đổi hoặc mở/bung cả archive cho context thường ngày.
- Quyết định owner Accepted đúng scope/phiên bản, được ghi trực tiếp trong spec, có ưu tiên; config/approval/receipt pinned và code là bằng chứng triển khai. Draft/TBD không là approval. Code/spec/report khác nhau: báo conflict, không tự đổi labels/splits/metrics/scope hoặc sửa pin để qua gate.
- Tạo/cập nhật TASK trước sửa theo `docs/templates/task-template.md`. TASK chỉ một task hiện hành: mục tiêu, inputs/version, docs đã đọc, constraints, tiến độ/checks và bước tiếp. Resume đọc index/TASK, kiểm Git/artifacts và chỉ đọc docs đổi; sửa TASK cũ/mâu thuẫn. Không chứa media/credentials/danh tính, không thay approval/spec hoặc nối WORKLOG.

## Phạm vi và cách tiến hành

- Thứ tự hiện hành: dataset/annotation QA → baseline/evaluation → dữ liệu đánh giá độc lập/cải tiến model → runtime crop/video → tracking/events → web. V4–v7 và E001–E003 đã có; E004 và pipeline video B chưa xong. Không train lại/smoke lại hoặc mở downstream chỉ vì refactor/docs.
- Không tự chốt class/formulation, official sources/splits, pretrained/license, training variables, thresholds/metrics, risk/evidence/review hoặc test access. Thiếu decision: chuẩn bị proposal có owner/lý do/evidence/acceptance rồi hỏi đúng phần; tiếp tục phần độc lập. Authorization user đúng scope giữ qua turns/resume, không hỏi lại phần đã duyệt.
- Chủ động tự động hóa shortlist/draft annotation/group/QA bằng công cụ phù hợp đã có; owner nghiệm thu batch/high-level và ngoại lệ, không bị bắt annotate từng ảnh. Solo owner tự review/chốt, không yêu cầu người thứ hai.
- Giữ changes tập trung. Canonical logic trong src, notebook launcher/exploration; YAML chứa variables; core không import web. Dùng schema rõ, không prediction/metric/model giả ở production path. Kiểm conventions/imports trước thêm module/CLI/library.
- Expansion dùng bảng công cụ trong data §8; lifecycle và restore inputs trong development §6. TASK chỉ rõ output tạm/evidence giữ lại. Không copy script theo version/r1/r2; chỉ đưa phần tái dùng đã kiểm vào module theo trách nhiệm.

## Dữ liệu, experiment và bảo toàn

- Raw bất biến; derivative/version mới ở interim/processed. Mutation cần owner review/pointer/pins, không sửa/reseal release v4–v7 hoặc artifact đã ký. Missing historical inputs: truy/restore theo development spec, không bỏ integrity guards hoặc lấy version khác cùng tên.
- Git không chứa media/model/checkpoint/env/cache/credentials. Không real identity trong filenames/manifests; không upload người thật/W&B/API khi thiếu consent/use scope. DVC local/pointer không là remote backup; push chỉ scope được duyệt.
- Run có ID/hypothesis/owner/code/config/data/split/encoding/seed/environment/status/metrics/checksums/observation/decision. Đổi variables là identity mới; OOM/interruption không silent đổi batch/config. Unknown masked, test không dùng tuning hoặc mở lại nếu thiếu protocol/approval.
- Tái lập run/model cũ dùng original code/pins/environment; code identity đổi sau cleanup không được sửa hash cũ hoặc nới evaluator. Artifact restore chỉ để task cần, gỡ workspace tạm sau dùng.

## Bàn giao và giữ spec hữu ích

- Trước hoàn tất inspect diff, chạy checks đúng phạm vi trong development spec; docs-only không chạy full ML/data hashes. Pass software không thay data/model acceptance.
- Khi được yêu cầu commit: stage đúng source/spec/config/metadata, chạy checker `--require-git` kiểm đủ Git index và archive registry, kiểm staged diff; không force-add binary. Kiểm clean checkout khi thay cấu trúc rộng. Backup cùng ổ chỉ bảo vệ xóa/sửa nhầm, không gọi là backup chống hỏng ổ.
- Kết quả mới cập nhật đúng spec: data cho sources/releases/QA; training cho runs/metrics/errors/next hypothesis; system cho requirements/capabilities/gates. Ghi đã làm gì, kết quả/decision/limitations và next work với version/evidence cần thiết; không chỉ tạo report link hoặc giữ pending state cũ.
- Tài liệu tiếng Việt, dấu cách đầy đủ; không dàn trải results/E004/cleanup/ADR/card Markdown mỗi task khi section hiện có đáp ứng. Thêm file/script/config chỉ khi có trách nhiệm tái dùng thật; dọn preview/cache/checkout/tooling sau khi bảo toàn inputs/evidence/results.

Dừng phần liên quan nếu data/license/path/version không rõ, label/split mâu thuẫn, test có nguy cơ dùng sai, train thiếu config/experiment, cần scientific/scope/risk decision mới hoặc có nguy cơ lộ dữ liệu/credential. Phần độc lập vẫn tiến hành.
