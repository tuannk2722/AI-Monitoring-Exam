# WORKLOG

## 2026-10-04 — Thiết kế hợp đồng release pilot B

- Owner chốt chỉ thiết kế, triển khai dataset ở task sau; 84 SCB candidates (28 TurnHead/28 read/28 write) + exact 28 RF approved crops; positive/negative/unknown với masked supervision. Budget không phải số crop training hoặc acceptance metric.
- Owner chốt package reviewed-context crops, runtime crop gate riêng trước baseline B end-to-end; group evidence trước train/val/test freeze, thiếu group giữ split=null/review_only và chặn release training. Quyết định lưu ADR-013; không hỏi lại A/B/quyền SCB/R1–R3.
- Hợp đồng canonical `docs/data/pilot-b-release-contract-v1.md`: RF membership 28 ID/target states, SCB deterministic selection rule chưa chạy, schema/codec thiết kế, eligibility, crop/split policy, DoD, TBD có owner và backlog S1–S9 hữu hạn.
- Tạo `.codex/TASK.md` và rule checkpoint trong AGENTS; đồng bộ guidelines/task template/index. TASK là bộ nhớ điều phối sau resume/compaction, không thay ADR/spec/config hoặc biến câu hỏi thành approval.
- Đồng bộ dataset research/P2/doc25/label-split specs/ghi chú ADR-012. Không sửa src/config/media/raw, không trích xuất/select SCB, build/train/upload/commit hoặc accepted dataset. P0/P1/P2 còn mở.
- Validation PASS: inspect diff, `git diff --check` theo Git config repository, `.venv/Scripts/python.exe scripts/check_repo.py --require-git` (failures=0), check local links/whitespace toàn 15 Markdown files gồm untracked (60 link cuối), RF exact 28-ID/target table khớp review bundle và backlog S1–S9. Inventory strict train: Head ID1 1.576, HRW read 2.708, write 1.103 ảnh; chưa chọn/relabel và không coi các ảnh là nhóm độc lập. Không cần rerun ML tests cho docs-only.
- Task thiết kế Done; dependency triển khai/TBD còn ở contract, P0/P1/P2 chưa đóng. Shell sandbox lỗi `setup refresh`, read-only check chạy được qua execution fallback được auto-review cho phép; không có action bị auto-review từ chối. Chưa commit/push.
- Closeout 2026-10-04: owner đã review thay đổi và yêu cầu hoàn thiện nếu không cần quyết định mới. Không có blocker của task thiết kế; ghi nhận bàn giao Done, giữ TBD cho task triển khai và bản AGENTS owner đã rút gọn. Kiểm lại diff/repository checker PASS; không bắt đầu build dataset hoặc train trong closeout.

## 2026-10-04 — Consolidate Dataset Audit & Spec theo B

- Dừng review ảnh nhỏ lẻ theo owner. Không đọc lại ảnh, không tạo annotation mới, không train/build/accepted.
- Đối chiếu docs/config/src/tests và Git. Mốc đã commit gần nhất: 57b2efb; bảo toàn cả quyết định/crop chưa commit sau mốc đó.
- Roboflow còn đúng 3 tài liệu: card, audit gốc, review tổng hợp. SCB giữ 3 tài liệu. Dataset research là trạng thái/vai trò hai nguồn; không lặp chuỗi review Roboflow cho SCB.
- 54 JSON gốc gom thành 3 bundle: SCB audit.json, Roboflow audit.json/review.json. Mỗi record giữ text UTF-8 và SHA gốc; review.json giữ snapshots tài liệu/script đã nghỉ và current_person_crops/image_queue. 28 crops/21 ảnh, 24 phone positives, 5 looking positives, 1 co-occurrence; 27 unknown targets bảo toàn.
- Bỏ 10 launcher theo phiên, giữ roboflow_v1.py để audit lại đúng archive và CLI audit/overlay/validator nguồn dùng chung. Gom reusable review validation/decision logic về data/review.py; giữ regression semantics, bỏ test orchestration/repair chỉ dành launcher đã nghỉ.
- Đồng bộ B trong README/architecture/P1/P2/P3/contracts/config/ADR. Build/train/evaluate YOLO legacy không được nhận config B; chưa triển khai exporter/classifier trong cleanup.
- Lịch sử WORKLOG đầy đủ giữ trong review.json → retired_files; số liệu audit gốc không thay đổi. Outputs/media/raw không xóa hoặc sửa.
- Chưa hoàn tất: release sample scope, coverage/unknown policy, crop inference, group/split, builder B và DVC round-trip. P0/P1/P2 chưa tự đóng. Không hỏi lại kiến trúc/quyền SCB/R1–R3.
- Kiểm tra thực tế: 56 unittest PASS (57 trước cleanup, bỏ 3 test orchestration/repair đã nghỉ và thêm 2 test consolidation/gate B); Ruff/compile/diff check PASS. 111 liên kết local hợp lệ; checksum 54 JSON gốc và snapshots được bảo toàn, 28 crop/27 unknown giữ nguyên. Audit CLI còn lại chạy --help PASS; không audit/review ảnh lại. Repository checker PASS cho index hiện tại, chưa bao gồm nội dung untracked.
- Sau resume: đã xử lý 27 trạng thái modified giả bằng đối chiếu filtered Git hash với index, không stage nội dung. Git thực tế: 30 modified + 62 deleted + 9 untracked, gồm phần trước cleanup chưa commit. Lần gián đoạn do hạn mức công cụ đã được khắc phục; chưa commit/push cleanup.
