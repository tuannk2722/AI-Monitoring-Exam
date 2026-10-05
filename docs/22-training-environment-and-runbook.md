# 22 — Environment và Runbook

## Quyết định về môi trường

- **Local IDE**: code/docs/test, metadata/sample audit nhỏ, web, CPU inference ngắn.
- **Colab Free**: GPU smoke/baseline/full experiment.
- **Demo benchmark**: chạy trên máy laptop trình bày thật sự.

Lưu ý: Colab local runtime không cung cấp GPU cloud.

Ngoại lệ E001 được owner duyệt ngày 2026-10-06 tại [ADR-014](decisions/ADR-014-e001-local-linear-probe.md): frozen-feature linear probe chạy CPU local theo [runbook E001](experiments/E001-runbook.md), từ clean isolated Git checkout và exact dependency/config/data pins. Run local này không cần Git push hoặc mở quyền Colab; output vẫn local. Các GPU experiment sau tiếp tục áp dụng workflow bên dưới.

## Thiết lập DVC một lần

Cài `requirements/dvc.txt`; `dvc init`; owner tạo folder Drive restricted; thêm `gdrive://<folder-id>` làm default remote; commit `.dvc/config`, không bao giờ commit credential JSON/token. Test với folder nhỏ không nhạy cảm: owner `dvc push`, sau đó clone đúng commit sang thư mục khác với DVC cache mới rỗng (không dùng cache gốc/shared), chạy `dvc pull`, đối chiếu SHA-256; ghi commit/pointer/lệnh/checksum vào WORKLOG trước khi đưa data thật vào.

Repository hiện đã hoàn tất setup và smoke round-trip; không init/tạo fixture lại. Dataset hiện hành là pilot B v4; owner cho phép storage riêng trên remote `teamdrive` restricted. Pull có target `data/processed/pilot-b/pilot-b-20261005-v4.dvc`; kiểm checksum/schema/test freeze theo [runbook pilot](data/pilot-b-preparation-v1.md). Pipeline `dvc.yaml` legacy đã gỡ; DVC pull theo pointer vẫn hoạt động độc lập. Chưa có training pipeline B để chạy `dvc repro`.

## Trước khi chạy experiment

Issue/owner/reviewer/hypothesis đã được phê duyệt; commit đã push sạch; `dvc pull`; verify dataset/split/config; cài nhóm requirement đã ghim; kiểm tra GPU/disk; chạy smoke 1–3 epoch; chọn artifact destination; xác nhận test set vẫn bị khóa.

## Colab bootstrap

Clone → checkout exact commit → cài requirements → authenticate Drive/DVC từ secret → pull version → ưu tiên copy dataset nhiều file nhỏ vào runtime scratch → chạy check/smoke → gọi module canonical. Notebook không chứa logic training thay thế.

## Trong và sau khi chạy

Lưu `last` checkpoint định kỳ và `best` cuối cùng; log config/status; sync artifact quan trọng trước khi runtime kết thúc. OOM/thay đổi config nghĩa là run identity mới. Sau run: verify checkpoint/metrics/plots/config/environment/checksum; `dvc add/push`; commit pointer và experiment record; reviewer chọn: reject/continue/candidate.

Ngân sách là 0 đồng. Nếu Colab không khả dụng, thu hẹp scope/model/config với experiment được tài liệu hóa; không phụ thuộc vào VM chạy thường xuyên.
