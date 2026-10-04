# Dataset Candidate — DS-SCB5-SUPPLIED-20261003

## Thông tin nhận dạng/provenance

- Tên: ba archive SCB do owner cung cấp; không phải toàn bộ SCB-Dataset. Maintainer Hugging Face: `wintonYF`; upstream liên kết: [Whiffe/SCB-dataset](https://github.com/Whiffe/SCB-dataset).
- URL đúng nguồn: [Hugging Face SCB-Dataset](https://huggingface.co/datasets/wintonYF/SCB-Dataset/tree/main). Ngày truy cập: **2026-10-03**. HEAD hiển thị `0fdc46fe393d251320def8c6d10cbc95d89f7da6`; tool không mở được trang pin commit, do đó không khẳng định đã tải snapshot commit. Phiên bản audit được định danh chính xác bằng **SHA-256 ZIP local khớp blob remote**.
- Thư mục archive gốc: `C:/Users/OS/Downloads/`; không sửa ZIP, không ghi vào `data/raw`. Bản giải nén chỉ phục vụ audit tại `outputs/scb-audit-20261003-v1/extracted/`.

| Archive chính xác | Bytes | SHA-256 |
|---|---:|---|
| SCB5-Discuss-2024-9-17.zip | 121619946 | `63aa029d04f8e9d5027cc2491aeca10785678750bdae4351835bfceaab95187f` |
| SCB5-Handrise-Read-write-2024-9-17.zip | 779384408 | `46619af0c0dea011b09b8d50f4c0578420b881b5154e9d11f0447760193a208d` |
| SCB_BowTurnHead_20250509.zip | 315224668 | `a0fdd6637fb286cbc5d3de83c09f4143686eab0da4d92e4d8007b6b14b3ca828` |

- Head ZIP có thư mục bên trong `SCB5-Turn-Bow-Head-2024-9-17`; giữ nguyên khác biệt tên/date, không đổi nó thành release 2024.
- Citation: Fan Yang, *SCB-Dataset: A Dataset for Detecting Student and Teacher Classroom Behavior*, [arXiv:2304.02488v7](https://arxiv.org/abs/2304.02488v7), 2025. Không coi mọi số liệu của bài báo là số liệu của ba ZIP này.
- Tái tạo: dùng đúng ZIP trên, kiểm hash; đọc [báo cáo và lệnh](SCB5-supplied-20261003-audit.md). URL từng blob/YAML, hash và môi trường được lưu trong [provenance](../../../artifacts/reports/scb-20261003/audit.json) và [web-evidence](../../../artifacts/reports/scb-20261003/audit.json). Không tải thêm nguồn cùng tên.

## Trạng thái hiện hành và vai trò

**Candidate đã audit; chưa training accepted.** Owner xác nhận quyền sử dụng/metadata đã phê duyệt và yêu cầu tiếp tục. Không hỏi lại phê duyệt quyền; văn bản nguồn chưa đính kèm không được trình bày thành đã đọc. Group từng file vẫn chưa có giá trị thực tế.

- Discuss: loại khỏi baseline, không thay đổi raw.
- TurnHead: ứng viên looking_around cho classifier B, phải relabel theo hướng nhìn/ngữ cảnh.
- Read/write: ứng viên normal sau khi cả hai target được review, không auto-map.
- BowHead/hand-raising: không map trực tiếp; không suy gian lận/normal từ tư thế.
- Phone_use: nguồn bổ sung Roboflow v1. Không thiếu class nguồn thì kết luận không có phone trong ảnh.

Formulation B đã chốt theo ADR-012. SCB **không cần lặp chuỗi pilot/batch/remaining/crop của Roboflow**. Dùng audit đã có để chọn tập hữu hạn, dedup và relabel qua quy trình preparation chung.

## Bằng chứng audit

10.138 cặp ảnh/nhãn trong ba ZIP, 8.116 SHA unique; 546 file label bị flag/625 dòng lỗi. 961 nhóm exact duplicate có thành viên train/val khi xét chung archive. Không concat rồi giữ split nguồn. Namespace class ID riêng từng archive. Không có frame→session/video manifest, không suy group_id từ tên file.

[Báo cáo audit gốc](SCB5-supplied-20261003-audit.md), [review mẫu](SCB5-supplied-20261003-review.md), [evidence hợp nhất](../../../artifacts/reports/scb-20261003/audit.json). Audit giữ lịch sử số liệu, không thay thế approval release. License/citation chi tiết nằm trong bằng chứng nguồn và owner confirmation, không upload/phân phối media trong cleanup này.

## Việc còn lại

Theo [kế hoạch sử dụng hai nguồn](../dataset-research.md): chọn mẫu, relabel target/crop cho B, xử lý duplicate/group split, bổ sung nhãn negative và xây package classifier. Không mở lại quyết định Discuss/quyền/B. Chưa training dataset, chưa model, chưa P0 DVC round-trip.
