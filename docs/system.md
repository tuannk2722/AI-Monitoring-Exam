# Đặc tả hệ thống AI Exam Monitoring

## 1. Mục đích và phạm vi

Tài liệu này quy định hệ thống cần làm gì, phần nào đã có và thứ tự triển khai tiếp. Agent đọc phần trạng thái và requirement liên quan trước khi coding; đặc tả dữ liệu, model và quy trình làm task nằm trong ba tài liệu cùng cấp. Trạng thái được đối chiếu code, release và kết quả đến ngày **2026-10-10**. Owner/người nghiệm thu: chủ repository, làm việc solo.

Sản phẩm là nghiên cứu/demo phát hiện **hành vi quan sát được** trong video phòng thi, hỗ trợ người xem xét. MVP xử lý video ghi sẵn, một phòng/camera, khoảng 10–15 người nhìn thấy. Kết quả mô tả hành vi và bằng chứng; không kết luận gian lận, định danh sinh viên hoặc tự động kỷ luật. Webcam/live, nhiều camera, cloud production, xác thực phức tạp và temporal neural model ngoài phạm vi hiện tại.

Hai hành vi đã chốt: `phone_use` và `looking_around`. Kiến trúc B đã được owner chọn; không mở lại A/B vì thiếu model đủ tốt. Chưa có benchmark chứng minh B tốt hơn A. Mục tiêu trước mắt là classifier trên crop đã review; automatic crop và pipeline video là bước riêng.

## 2. Trạng thái thực tế

| Thành phần | Đã có / đã kiểm chứng | Phần chưa đạt |
|---|---|---|
| Nghiên cứu và annotation | Audit nhiều nguồn; owner review crop/targets/rights/groups; schema masked multi-label | Provenance người/phòng/session còn thiếu; targeted coverage chưa đủ chứng minh generalization |
| Dataset | Bốn release local v4–v7; v7 có 689 train, 49 val, 11 test; schema/checksum/rebuild đã kiểm | Chưa có holdout phòng thi độc lập; v7 không tự cấp quyền training hoặc upload |
| Baseline | E001–E003 FINISHED: frozen ResNet18 + linear head; metrics/error analysis thật | Chưa Selected; ba run không phải fine-tune backbone |
| Cải tiến | Có phân tích lỗi E003, v7 và proposal E004 | Fine-tune layer 4, comparator, protocol/compute/metrics E004 chưa được chốt/chưa chạy |
| Inference | Adapter Ultralytics cho ảnh/video, JSONL metadata/prediction và FPS guards | Chưa person-only → crop → classifier B; chưa benchmark trên demo hardware |
| Domain contract | `BoundingBox`, `FrameRef`, `Prediction`, `TrackObservation`, `BehaviorEvent` đã có dataclass | Có schema không đồng nghĩa đã có tracker/event generator |
| Tracking/events/risk | Có hướng thiết kế và yêu cầu bên dưới | Chưa triển khai hoặc benchmark; ByteTrack và risk framework vẫn Proposed |
| Web/demo | Stack local đã chọn cho giai đoạn sau | Chưa có app/database/session workflow end-to-end |
| Công cụ | Python modules, unit tests, strict mypy/CI, Git completeness/archive registry checks; v4 đã kiểm remote round-trip | Binary backup trên D theo owner scope; chưa backup toàn bộ ở ổ/máy độc lập |

Trạng thái hiện tại là **đã hoàn thành pilot data engineering và baseline, đang ở bước cải tiến dữ liệu/model và thiết kế đánh giá**. Chạy được training, unit tests hay rebuild dataset không thay acceptance gate của model.

## 3. Kiến trúc và trách nhiệm module

Luồng đích:

```text
Video được phép sử dụng
  → frame + thời gian video
  → detector person
  → crop context đúng người
  → classifier [phone_use, looking_around]
  → track tạm thời trong session
  → temporal events
  → risk + evidence
  → giao diện human review
```

Luồng đã vận hành hiện nay: **source audit → crop/annotation được review → release dataset → frozen-feature training → validation/error analysis**. Không nối adapter detection hiện có vào web rồi coi đó là pipeline B đã hoàn tất.

| Vị trí code | Trách nhiệm / giới hạn |
|---|---|
| `src/ai_exam_monitoring/data/` | Audit nguồn YOLO, overlay, similarity, codec `PilotRecord`, package và integrity; builder v7 historical có self-SHA pin |
| `src/ai_exam_monitoring/training/` | Config/approval, loader/freeze, RGB letterbox, frozen encoder/cache, head training/resume, metrics và evaluator |
| `src/ai_exam_monitoring/inference/` | Adapter generic đọc checkpoint có sẵn và xuất prediction theo taxonomy checkpoint; chưa lọc person hoặc suy luận classifier B |
| `src/ai_exam_monitoring/contracts/` | Dataclass producer/consumer dùng chung; không phụ thuộc web framework |
| `src/ai_exam_monitoring/common/` | Config/error/provenance và truy/khôi phục lịch sử theo SHA |
| `configs/` | Biến dataset/experiment cụ thể; config E004-plan vẫn Draft, không chạy được bằng trainer hiện tại |

Core không import FastAPI/UI/database. Notebook chỉ exploration/launcher; logic tái dùng ở `src`. Không tạo module rỗng, metric giả hoặc kiến trúc dịch vụ phân tán để chuẩn bị cho phần chưa đến gate.

## 4. Yêu cầu chức năng và cách nghiệm thu

| ID | Requirement | Trạng thái / bằng chứng nghiệm thu cần có |
|---|---|---|
| FR-DATA-01 | Dataset version rõ, có schema/ledger/manifest/rights/assignment/freeze/checksum và owner approval | Đã áp dụng v4–v7; mutation tạo release mới, không sửa bản cũ |
| FR-CLS-01 | Hai target độc lập, unknown masked; normal là metadata review | Đã có codec/trainer cho reviewed crops; không thêm output normal hoặc đổi thành softmax |
| FR-EXP-01 | Run có hypothesis, config/code/data/environment pins, status, checkpoints, metrics và decision | E001–E003 đã có; resume phải giữ identity, OOM/interruption không tự đổi config |
| FR-EVAL-01 | Model/epoch/threshold chọn bằng development; test chỉ mở theo protocol freeze riêng | Evaluator hiện kiểm code/config/checkpoint; chưa có guard dùng holdout một lần xuyên mọi output |
| FR-VID-01 | Recorded video có source checksum, frame index, video time và prediction có provenance | Adapter JSONL đã có; managed session và integration pipeline còn thiếu |
| FR-CROP-01 | Person/context crop giữ đúng bằng chứng thuộc anchor, preprocessing khớp training | Review crops đã có; runtime policy, detector/license và QA trên video cần owner chốt |
| FR-TRK-01 | Track ID tạm thời trong một session; có đo switch/fragmentation/loss/occlusion | Chưa triển khai; benchmark ByteTrack với phương án khả thi khác hoặc no-tracking baseline |
| FR-EVT-01 | Nhiều observation theo temporal rule có version mới tạo event | Chưa triển khai; cần fixtures/event validation và duration/gap/aggregation được duyệt |
| FR-RSK-01 | Risk giải thích được từ event history, bounded/decaying, tách model confidence | Proposed; chưa có công thức/threshold/reset được duyệt |
| FR-EVD-01 | Evidence trỏ exact source frame/time/checksum và model/rule/event versions | Chưa generator; retention/access/deletion phải chốt trước media người thật |
| FR-REV-01 | Người xem lại video/evidence, ghi chú, bác false positive hoặc xác nhận hành vi | Luồng review local dự kiến; không tự kết luận kỷ luật |
| FR-UI-01 | Chọn video → xử lý → xem kết quả thật và review; lỗi được hiển thị rõ | Chưa app; triển khai sau domain/event gate với FastAPI + Jinja 2 + JavaScript nhỏ + SQLite local |

Khi task liên quan requirement đã có, sửa producer/consumer và kiểm regression của đường đó. Khi liên quan requirement chưa có, ghi rõ gate còn thiếu trước implementation; agent vẫn được làm proposal hoặc phần độc lập được user yêu cầu, không tự suy quyền train/thu thập/upload.

## 5. Contract giữa các bước

Contract thực thi ở `contracts/domain.py`; field names dưới đây là hiện hành, không là schema DB đã triển khai.

| Entity | Fields và invariants |
|---|---|
| `BoundingBox` | `xmin,ymin,xmax,ymax,coordinate_space`; tọa độ hữu hạn, min < max; pixel không âm, normalized trong [0,1] |
| `FrameRef` | `session_id,frame_index,video_time_ms,source_uri`; index/time không âm; thời gian video khác thời gian xử lý/DB |
| `Prediction` | `prediction_id,frame,model_version,task,label,confidence,bbox,class_id?`; confidence trong [0,1], label mô tả quan sát; không dùng cheating/cheater/no_cheating/suspicious_person |
| `TrackObservation` | `session_id,track_id,frame,bbox,source_prediction_ids`; track ID không là danh tính ngoài session |
| `BehaviorEvent` | Event/session/track/behavior, frame/time window, aggregated confidence, model/rule versions, prediction refs; end không trước start; status hiện `candidate/confirmed/dismissed` |

`Prediction` hiện biểu diễn một label/score/bbox. Adapter classifier B chưa có: khi nối hai score với person/crop/frame phải thiết kế producer/consumer tường minh và review nếu mở schema; không nhét dict tùy ý hoặc coi detection class ID là target order. `PilotRecord` là contract dataset riêng, được mô tả đầy đủ trong data spec.

Adapter hiện yêu cầu source/checkpoint tồn tại, output mới và FPS dương/hữu hạn trước predict; không tạo timestamp 0 để che metadata thiếu. JSONL mở đầu bằng metadata source/checkpoint SHA và FPS, tiếp theo là predictions. CLI confidence mặc định 0.25 là giá trị của adapter generic, không phải threshold hành vi hoặc risk được owner duyệt. Không có classifier video integration/session status persistence ở đường này.

Các entity dự kiến cho phần sau: session/job, model version, risk snapshot, evidence và human review. Chỉ định fields/persistence cụ thể khi thực hiện slice tương ứng; chưa cần database schema hoặc service phụ ngay bây giờ.

## 6. Luồng người dùng đích và yêu cầu vận hành

Sau khi đủ gate, slice đầu là local recorded-video: chọn video có quyền → server kiểm input → session queued/running → lưu output/evidence → completed hoặc failed → người xem timeline và review. Không thêm live/WebSocket/seat mapping vào slice đầu. Server tạo tên file kỹ thuật, validate loại/kích thước/thời lượng; không chỉ dựa validation client. Các limit cụ thể chưa chốt, không hard-code số giả như acceptance target.

Nghiệm thu end-to-end phải dùng video được phép, model đã chọn, crop policy/rule versions và kết quả thật. Đo trên hardware/OS/dependencies đã pin: resolution/FPS/duration, startup/warm-up/repeats, throughput, mean/p50/p95 latency, peak RAM/VRAM, tracking loss/switch và false/missed events. **Chưa có SLA FPS/latency toàn video hoặc quality threshold hệ thống Accepted.** Các chỉ tiêu classifier E004 là proposal riêng, không chuyển thành SLA video.

Ngân sách 0 đồng; local i 7-1255 U, RAM 8/16 GB, Intel UHD là môi trường tham chiếu lịch sử, không bảo đảm hiệu năng. Local cho development/audit/inference; Colab Free là hướng GPU đã chốt. E001–E003 có ngoại lệ CPU riêng, không cấp ngoại lệ mặc định cho E004. Cloud/realtime/auth chỉ thêm khi requirement/gate và user yêu cầu thực sự cần.

Media người thật cần policy văn bản cho consent, access, third-party processing, retention/deletion và incident handling trước thu nhận/ghi/upload. Retention cụ thể chưa chốt. Không real identity trong tên file/manifest, không credential trong Git/TASK/log; không upload media vào API/W&B khi thiếu quyền. Nguồn đã có approval giữ đúng scope, không hỏi lại phần không đổi.

## 7. Thứ tự triển khai tiếp và điểm chốt

| Bước | Hiện tại | Exit gate / việc tiếp theo |
|---|---|---|
| Nền tảng | Code/CI/DVC, strict typing và hướng dẫn reuse/restore đã có | Giữ checks đúng scope và cập nhật backup sau release/run mới; backup cùng D không chống hỏng ổ |
| Data research + release | V4–v7 đã hoàn tất local; v7 targeted train đạt một phần | Đo coverage 375 new train, bổ sung provenance; thiết kế development/holdout riêng nếu owner chọn |
| Baseline | E001–E003 FINISHED, chưa Selected | Dùng lỗi thật để chốt hypothesis; không train lại chỉ vì docs đổi |
| Model improvement + evaluation | E004 Draft; chưa fine-tune/holdout/comparator Accepted | Chốt recipe/compute/protocol/metrics; triển khai và smoke/resume phần được duyệt; đánh giá cùng cohort |
| Runtime crop + video | Chưa pipeline B | Chốt detector/license/crop policy; QA source → crop → input; fixed-video integration có provenance |
| Tracking/events/risk | Proposed/chưa implementation | Model Selected phát prediction thật; benchmark tracker; event fixtures/rules và risk semantics được duyệt |
| Web + system evaluation + demo | Chưa implementation | Local UI đọc output thật, recorded-session integration; freeze protocol/measure hardware; demo offline và báo giới hạn |

Owner phải chốt những phần còn mở: holdout source/use scope/independence; recipe/compute/comparator/numerical gates E004; detector/runtime crop; tracker/rule/risk thresholds; media policy; video performance targets. Agent chuẩn bị đề xuất có bằng chứng và bước nghiệm thu, không bắt owner làm annotation thủ công hay tự thay gate để chạy được.

## 8. Quyết định kiến trúc đang có hiệu lực

Nội dung quyết định cần cho coding được giữ ngay trong bộ spec này. ID dưới đây dùng traceability, **không yêu cầu mở từng ADR trong archive cho task thường ngày**. Đổi quyết định cần owner chốt phạm vi và cập nhật đúng phần spec; nguyên bản/approval có checksum vẫn dùng khi cần kiểm chứng lịch sử hoặc tái lập.

| ID | Trạng thái / nội dung còn hiệu lực | Phần thực hiện |
|---|---|---|
| ADR-001 | Accepted: research/demo recorded, một camera, human review; ngoài scope identity/production | System §1, §6 |
| ADR-002 | Superseded phần formulation/normal bởi 011/012; không là lựa chọn A/B đang mở | System §1; Data semantics |
| ADR-003 | Accepted cho candidate SCB/RF; Discuss loại, nhãn nguồn không tự accepted | Data nghiên cứu nguồn |
| ADR-004 | Accepted local + Colab, canonical modules, checkpoint/resume/sync; CPU E001–E003 là ngoại lệ | System §6; Development môi trường |
| ADR-005 | Accepted Git metadata/DVC binary/Drive restricted; push đúng quyền trước publish remote pointer | Development storage |
| ADR-006 | Accepted config/run/Git/DVC/metrics canonical; W&B optional disabled, không tự host MLflow | Training provenance |
| ADR-007 | Accepted bỏ Django/Cloudinary prototype, hoãn web; stack local FastAPI/`Jinja2`/JS/SQLite | System §4, §6 |
| ADR-008 | Proposed ByteTrack, phải benchmark; chưa threshold/tracker Accepted | System FR-TRK-01 |
| ADR-009 | Proposed temporal events/risk framework, chưa numerical rules/formula | System FR-EVT/RSK |
| ADR-010 | Accepted privacy gate; retention cụ thể chưa được duyệt | System §6 |
| ADR-011 | Accepted person unit/phone attribution; review evidence, không nearest-device labels | Data semantics/QA |
| ADR-012 | Accepted B, multi-label, normal metadata, unknown mask; không tự dataset/model approval | Data schema; Training loss |
| ADR-013 | Accepted thiết kế reviewed-crop pilot/masked supervision/group gates; budget v1 không quota v7 | Data workflow/releases |
| ADR-014 | Accepted riêng E001 CPU frozen probe v4 và final protocol | Training E001 |
| ADR-015 | Accepted riêng E002 train expansion v5, bảo toàn val/test; không test mới/promotion | Training E002 |
| ADR-016 | Accepted riêng E003 v6/protocol/CPU/smoke/resume; không holdout/promotion | Training E003 |
| ADR-017 | Draft gates E004, chưa quyền train/final test/Selected | Training E004/gates |
| ADR-018 | Accepted phone chỉ mobile; landline không positive, không relabel hàng loạt thiếu review | Data semantics/corrections |

Các kết quả và quyết định dataset/model cụ thể ở data/training spec; chúng đã được cập nhật từ bằng chứng gốc thay vì giữ trạng thái pending của các đề xuất cũ.
