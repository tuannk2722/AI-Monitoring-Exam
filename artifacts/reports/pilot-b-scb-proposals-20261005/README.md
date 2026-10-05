# Pilot B — Batch tự động để nghiệm thu

Ngày 2026-10-05. Đã bỏ HTML/Canvas và thao tác vẽ crop. Batch local: `data/interim/pilot-b/pilot-b-scb-proposals-20261005-v2/`.

| Thành phần | Kết quả |
|---|---|
| SCB | 84 crop đề xuất tự cắt từ bbox nguồn: 28 TurnHead, 28 read, 28 write |
| Roboflow | 28 crop đã duyệt, giữ nguyên bytes/tọa độ/nhãn/evidence |
| Looking đề xuất SCB | 28 positive (TurnHead), 56 negative (read/write); weak source-class suggestions |
| Phone / normal SCB | 84 unknown cho mỗi mục; metadata không chứng minh absence |
| Canonical ledger | 112 records nguyên bản; 84 SCB vẫn unknown, split=null/review_only |

## Xem kết quả

- [28 TurnHead: nguồn bên trái, crop bên phải](../../../data/interim/pilot-b/pilot-b-scb-proposals-20261005-v2/reports/turnhead.png).
- [28 read](../../../data/interim/pilot-b/pilot-b-scb-proposals-20261005-v2/reports/read.png).
- [28 write](../../../data/interim/pilot-b/pilot-b-scb-proposals-20261005-v2/reports/write.png).
- [Tọa độ, SHA và nhãn gợi ý CSV](../../../data/interim/pilot-b/pilot-b-scb-proposals-20261005-v2/proposals.csv).

## Những trường hợp cần chú ý

| ID | Ghi chú QA của Codex |
|---|---|
| SCB-read-008 |Crop có nhiều người; xác nhận target thuộc bbox nguồn |
| SCB-read-012 |Hướng đầu có thể mâu thuẫn nhãn read; negative chưa có evidence |
| SCB-read-026, SCB-read-027 |Giơ tay/quay đầu; nhãn read không chứng minh looking negative |
| SCB-read-009, SCB-write-007 |Ảnh nguồn có nút play; kiểm tra ảnh hưởng trong crop |

Bbox nguồn được làm tròn bao ngoài, không padding; có thể thiếu phần người nhìn thấy/ngữ cảnh bàn. Nhãn looking là gợi ý từ source class, chưa phải absence/presence đã xác nhận. Canonical phone/normal không bị chuyển unknown thành negative. Owner chỉ cần duyệt/bác batch hoặc ghi ID ngoại lệ; không vẽ hay xuất crop. Nếu crop/target chưa đạt, Codex xử lý ngoại lệ, không yêu cầu owner làm tác vụ annotation.

Acceptance batch chưa chốt grouping độc lập/split/release training. 14 quyết định giữ chung đã được nhập và không cần làm lại; 42 records chưa gán nhóm, dark-side/curtain linkage còn unresolved. [Runbook](../../../docs/data/pilot-b-preparation-v1.md).

Code cleanup: bỏ editor crop/importer Canvas, HTML template, group-page generator, tests chỉ phục vụ các tool; bỏ HTML asset logic/option và package-data. Giữ selection/provenance/schema/packager/importer nhóm. Không thêm model/library/frontend. [Kiểm chứng](verification.json).
