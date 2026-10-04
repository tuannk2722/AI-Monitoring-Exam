# TASK — PILOT-B-CONTRACT-20261004

- Updated: 2026-10-04 (Asia/Saigon).
- Status: Done — task thiết kế hoàn tất; dataset implementation chưa bắt đầu.
- Owner/người chốt: chủ repository (solo). Hỗ trợ: Codex.
- Closeout: owner đã review các thay đổi và yêu cầu hoàn thiện task nếu không cần quyết định mới (2026-10-04). Không còn quyết định cần chốt để đóng task thiết kế; các TBD implementation vẫn giữ nguyên.

## Mục tiêu và phạm vi

Thiết kế một hợp đồng đóng gói pilot Formulation B từ tập SCB5 hữu hạn và đúng 28 person/crop Roboflow đã duyệt. Phải rõ membership/coverage, positive/negative/unknown, eligibility, crop/split policy, DoD và danh sách triển khai hữu hạn. User yêu cầu thêm TASK.md và quy tắc duy trì ngữ cảnh cho agent. Đây là checkpoint điều phối, không phải quyết định dataset/schema đã Accepted.

## Source of truth và ràng buộc

- Đọc `docs/00-INDEX.md` rồi docs theo loại task; đối chiếu trạng thái Git/artifact trước khi tiếp tục sau compaction.
- ADR-011/012 Accepted: visible-person bbox; crop có ngữ cảnh; hai target có thể cùng positive; normal phải review; unknown không phải negative. Không hỏi lại A/B, quyền SCB, R1–R3.
- Roboflow: 28 crops/21 ảnh; 24 phone positives, 5 looking positives, một co-occurrence; 27 crop thiếu một target; chưa training eligible/dataset accepted.
- SCB: Discuss loại; TurnHead/read/write chỉ là strata tìm candidate, không tự map target. Thiếu group từng mẫu; split cũ có exact overlap. Quyền SCB đã xác nhận.
- Không train, sửa raw, upload media, thay mapping legacy hoặc tự phê duyệt release. Quyết định còn thiếu phải ghi owner/lý do/điều kiện chốt.
- `data.build_dataset` từ chối B đúng theo docs; không có exporter B hiện hành. Không có xung đột code/docs cần sửa trong task này.

## Đã đọc (không đọc lại khi file không đổi)

Root: `AGENTS.md`, `.gitignore`, `pyproject.toml`.

Docs: 00, 01, 02, 04, 06, 08, 09, 16, 17, 19, 21, 23, 25; `docs/templates/task-template.md`; `docs/WORKLOG.md`; ADR-011/012; `docs/data/dataset-research.md`, `label-spec-v1.md`, `split-spec-v1.md`; cả ba tài liệu card/audit/review của SCB; Roboflow card/review.

Config/code: `configs/datasets/exam_v0.1.yaml`, `configs/label_map.yaml`; data `build_dataset.py`, `manifest.py`, `split.py`, `review.py`; `scripts/check_repo.py`.

Evidence đã kiểm tra cấu trúc/trạng thái: SCB `audit.json` (provenance và selection records); Roboflow `review.json` (`current_person_crops`); local SCB head/hrw audit reports. Không review ảnh hoặc tạo nhãn mới.

## Quyết định owner đã chốt (2026-10-04)

1. “Chỉ thiết kế hợp đồng; triển khai dataset ở task sau”.
2. “Lưu ba trạng thái và cho phép masked supervision”: known target tham gia loss/metric, unknown không phải negative.
3. “84 candidate SCB theo phân bổ trên”: 28 TurnHead + 28 read + 28 write; một đợt review, không tự refill. Tổng ledger đầu vào 112 record, chưa phải số crop train.
4. “Đóng gói crop đã review; ghi rõ gate crop runtime trước baseline end-to-end”. Không tự đặt padding hoặc yêu cầu lại approval RF crop đã có.
5. “Có split khi group đủ bằng chứng; thiếu group thì chặn release training”. Thiếu group: split=null, usage=review_only; không suy session từ filename/unique hash.

Các lựa chọn trên được lưu [ADR-013](../docs/decisions/ADR-013-pilot-b-packaging-contract.md), Accepted chỉ cho đúng phạm vi này. Model/loss/threshold chưa chọn; dataset/schema cụ thể/split config và runtime crop chưa được phê duyệt. Không có câu hỏi async còn chờ.

## Deliverable và files đã đổi

- Hợp đồng duy nhất: [pilot-b-release-contract-v1.md](../docs/data/pilot-b-release-contract-v1.md). RF exact 28 ID/target table; SCB 84-anchor selection rule deterministic chưa chạy; encoding/state/null/mask, eligibility, schema/layout thiết kế, crop/split/DoD và backlog S1–S9.
- Tạo: contract, ADR-013 và TASK này. Đổi: `AGENTS.md`; docs 00, 09, 16, 17, 25; dataset research, label/split specs; ghi chú ADR-012; task template và WORKLOG. Tổng 15 Markdown files. Không sửa src/config/raw/media hoặc evidence bundles.
- Rule TASK canonical trong AGENTS; đọc checkpoint sau resume/compaction, kiểm chứng Git/files/evidence, cập nhật trước bàn giao; kết quả bền vững lưu spec/ADR/WORKLOG. Checkpoint không tự cấp approval.

## Validation và kết quả

- Đã inspect tracked diff và nội dung contract/ADR/TASK; `git diff --check`: PASS.
- `.venv/Scripts/python.exe scripts/check_repo.py --require-git`: PASS (failures=0); checker chỉ xét Git index, phần untracked được kiểm riêng bằng script read-only.
- Kiểm Markdown local links/whitespace của toàn bộ 15 file thay đổi (gồm untracked): PASS, 60 link ở checkpoint cuối. `git diff --check` theo Git config repository cuối cùng exit 0; một invocation tạm `core.autocrlf=false` tạo false positive CRLF, không đổi config hoặc file, đã kiểm lại theo policy thực.
- Đối chiếu RF appendix với current_person_crops: PASS, đúng 28 ID, 24 phone positives, 5 looking positives, 1 co-occurrence, 27 partial labels; historical training_eligible=false giữ nguyên. Backlog đúng S1–S9.
- Đọc inventory strict train (không chọn mẫu): Head ID1 1.576 ảnh; HRW ID1 2.708 ảnh; HRW ID2 1.103 ảnh. Chưa đếm group độc lập/unique selected; không suy ra đủ coverage từ số pool.
- Shell sandbox gặp lỗi khởi tạo `helper_unknown_error: setup refresh had errors`; read-only commands chạy được qua require_escalated được auto-review cho phép. Không có action bị auto-review từ chối; không có validation bị bỏ vì lỗi này.
- Docs-only: không cần thêm unit test/rerun ML suite; không select/extract/relabel/build/train/upload/DVC/commit/push. P0/P1/P2 vẫn mở; không có experiment impact hoặc model result.
- Git ban đầu sạch; HEAD `660c9f7`. Files mới/đổi chưa commit trong task này.
- Closeout sau owner review: đọc lại index/checkpoint và AGENTS đã được owner rút gọn; bảo toàn bản AGENTS hiện tại. `git diff --check` và repository checker `--require-git` tiếp tục PASS; không mở rộng scope hoặc nâng dataset/schema/split thành Accepted.

## Phần mở và bước triển khai tiếp theo

- TBD-PB-MEMBERSHIP/GROUP/SPLIT-CONFIG/CROP-RUNTIME/COVERAGE/EXPORT/RELEASE-SCOPE có owner, lý do và điều kiện chốt ở contract. Đây là dependency task triển khai, không phải blocker của task thiết kế đã xong.
- Khi user giao task triển khai: đọc index/contract/ADR-013 và checkpoint này; cập nhật trạng thái cho task mới, bắt đầu S1 pin source/provenance/use scope rồi S2 freeze SCB selection; không bỏ group/runtime gates hoặc lấy draft ratio/seed làm approved.
- S1–S8 là preparation hữu hạn; S9 là gate riêng trước baseline B end-to-end. Không bắt đầu triển khai chỉ vì resume/compaction của task thiết kế.

## Resume checkpoint

Task thiết kế đã Done. Đối chiếu Git/deliverable/validation nếu tiếp tục bàn giao; chỉ triển khai dataset khi user giao task sau. Không mở lại A/B/quyền SCB/R1–R3, không lấy checkpoint cũ ghi đè source of truth và không chuyển sang train.
