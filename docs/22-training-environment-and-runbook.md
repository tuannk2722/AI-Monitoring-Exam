# 22 — Environment và Runbook

## Quyết định về môi trường

- **Local IDE**: code/docs/test, metadata/sample audit nhỏ, web, CPU inference ngắn.
- **Colab Free**: GPU smoke/baseline/full experiment.
- **Demo benchmark**: chạy trên máy laptop trình bày thật sự.

Lưu ý: Colab local runtime không cung cấp GPU cloud.

## Thiết lập DVC một lần

Cài `requirements/dvc.txt`; `dvc init`; owner tạo folder Drive restricted; thêm `gdrive://<folder-id>` làm default remote; commit `.dvc/config`, không bao giờ commit credential JSON/token. Test với folder nhỏ không nhạy cảm: Member A `dvc push`, Member B `git pull && dvc pull` trước khi đưa data thật vào.

## Trước khi chạy experiment

Issue/owner/reviewer/hypothesis đã được phê duyệt; commit đã push sạch; `dvc pull`; verify dataset/split/config; cài nhóm requirement đã ghim; kiểm tra GPU/disk; chạy smoke 1–3 epoch; chọn artifact destination; xác nhận test set vẫn bị khóa.

## Colab bootstrap

Clone → checkout exact commit → cài requirements → authenticate Drive/DVC từ secret → pull version → ưu tiên copy dataset nhiều file nhỏ vào runtime scratch → chạy check/smoke → gọi module canonical. Notebook không chứa logic training thay thế.

## Trong và sau khi chạy

Lưu `last` checkpoint định kỳ và `best` cuối cùng; log config/status; sync artifact quan trọng trước khi runtime kết thúc. OOM/thay đổi config nghĩa là run identity mới. Sau run: verify checkpoint/metrics/plots/config/environment/checksum; `dvc add/push`; commit pointer và experiment record; reviewer chọn: reject/continue/candidate.

Ngân sách là 0 đồng. Nếu Colab không khả dụng, thu hẹp scope/model/config với experiment được tài liệu hóa; không phụ thuộc vào VM chạy thường xuyên.
