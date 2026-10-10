# Funnel tám nguồn sau R7 — snapshot kiểm toán 2026-10-09

Trạng thái: Draft để owner nghiệm thu. Các số dưới đây đo từ inventory/receipt local đã pin trong R7 và snapshot audit nguồn; không tải thêm ảnh, không đọc media test, không train, không sửa R7/v4–v6. **Tổng ảnh nguồn không phải pool mẫu có ích hoặc nhóm độc lập.** `measured` là số đếm bằng chứng, `estimated` là ước lượng nêu phương pháp, `unknown` là chưa đo/chưa chứng minh, `exhausted` chỉ áp dụng bộ lọc đã quét hết.

| Source | Tổng ảnh có sẵn — measured | Train nguồn — measured | Annotation/index scanned | Tải/tiếp nhận ảnh | Xem screening R7 | Crop Draft R7 | Owner accepted/rejected |
|---|---:|---:|---|---|---|---:|---|
| Classroom Attitude v3 | 3.573 | 2.566 | Toàn3.573 ảnh trong inventory; annotation strict+decode audit lịch sử | ZIP đầy đủ3.573; materialized R7 cần đếm riêng | Cần counter theo source trong300 RFscreening | 60 | Crop approval chính thức chưa materialize; receipt mới xử lý riêng |
| Student Behaviour v6 | 4.065 | 3.192 | Toàn4.065 ảnh; annotation/decode audit lịch sử | ZIP đầy đủ4.065; materialized R7 cần đếm riêng | Cần counter theo source trong300 RFscreening | 14 | Như trên |
| Exam Cheating v2 | 772 | 679 | Toàn772 ảnh; annotation/decode audit lịch sử | ZIP đầy đủ772; materialized R7 cần đếm riêng | Cần counter theo source trong300 RFscreening | 2 | Như trên |
| RF v1 | 3.407 | 2.521 | Toàn3.407 ảnh trong inventory | ZIP đầy đủ3.407; materialized R7 cần đếm riêng | Cần counter theo source trong300 RFscreening | 23 | Như trên |
| SCB Head | 2.410 | 1.905 | Toàn2.410 ảnh/label; strict geometry/decode audit lịch sử | ZIP đầy đủ2.410; materialized R7 cần đếm riêng | Cần counter theo source trong100SCBscreening | 26 | Như trên |
| SCB HRW | 6.864 | 5.193 | Toàn6.864 ảnh/label; strict geometry/decode audit lịch sử | ZIP đầy đủ6.864; materialized R7 cần đếm riêng | Cần counter theo source trong100SCBscreening | 18 | Như trên |
| COCO train2017 | 118.287 ảnh train trong metadata | 118.287 | Metadata train đọc đầy đủ; person+phone+context+CC BY tạo185phone hints và355work-without-phone-annotation hints | 305 tải thành công/0fail/0quarantine | 305 (=129+80+96) | 39 | Public rights/notice/membership vẫn chờ owner |
| Open Images train | Tổng publisher pool chưa đếm tại snapshot này — unknown | Unknown | Bbox chỉ prefix301.989.888bytes; bỏ image cuối; không exhaustive. Full image-info metadata đã tải nhưng không đồng nghĩa full bbox scan | 598 tải thành công (=181+18+200+199);1fail >10MB | 598 | 92 | Public rights/notice/membership vẫn chờ owner |

Các số crop trên dùng R7 bất biến (274crop,242ảnh nguồn), không phải kết quả sau owner feedback. 1.303 screening là400local+305COCO+598OI; không dùng cùng total cho từng source. 274 accepted hoặc274mẫu đủ train là diễn giải sai: R7 `accepted_crops:0`, `training_eligible:false`. Owner nói đã review toàn bộ phải được ghi receipt mới; không sửa status trong R7.

## Local supply, exclusion và caps

| Source | Strict train rows trong supply | Parent/SHA/lineage loại trước hint | Near-evaluation cách ly | Sau các exclusion đã đo | Hint anchors phone / looking / negative |
|---|---:|---:|---:|---:|---|
| Classroom | 2.565 | 67 | 80 | 2.418 | 1.723 /2.883 /952 |
| Student | 3.192 | 132 | 4 | 3.056 | 12.760 /2.366 /8.764 |
| Exam | 679 | 125 | 1 | 553 | 71 /387 /373 |
| RF | 2.521 | 50 | 14 | 2.457 | 57 /6.398 /1.488 |
| SCB Head | 1.767 | Đã loại ở `local_inventory`, không được báo0 | 16 | 1.751 | 0 /7.138 /3.717 |
| SCB HRW | 4.811 | Đã loại ở `local_inventory`, không được báo0 | 34 | 4.777 | 0 /0 /19.619 |

Nguồn: `data/interim/pilot-b/v7-targeted-screening-20261008-r2/supply.json`, `v7-targeted-scb-screening-20261008-r1/supply.json`. Với SCB, trường `strict_train_images` trong supply **đã qua lọc local parent/SHA/lineage**; vì vậy không so trực tiếp với train1905/5193 như một rate độc lập. Unknown phải giữ unknown, không điền0. Các hint anchors là dòng bbox, có nhiều bbox/ảnh và bbox chỉ phone/head; chúng không phải canonical person samples.

Caps R7 local là300ảnh chung bốn RF sources:160phone_hint+90looking_hint+50negative_hint. SCB100ảnh chung:60looking_hint+40negative_hint. Shortlist chọn một SHA ảnh mỗi lượt, rank farthest-first/dHash; không có quota đảm bảo Exam hoặc từng nguồn, không chứng minh các ảnh chưa chọn thiếu giá trị. Các con số2565/3192/679/2521 không phải đã xem visual toàn nguồn. Chưa có phép đo semantic usefulness/exhaustion cho sáu nguồn local.

## Vì sao Exam chỉ đóng góp2crop?

Exam còn553train rows sau125parent/lineage+1near-evaluation exclusion, và71phone/387looking/373negative bbox hints. R7 dùng cap300ảnh **chung** với ba nguồn lớn, rồi visual/anchor/domain/crop/lineage QA;2crop chỉ là yield cuối từ hàng đợi bị cap, không phải source exhausted. Exact duplicate với RF cũ:57nhóm giữa nguồn,2nhóm duplicate qua split Exam (audit lịch sử); source chứa phim/video/watermark và không phải mọi ảnh đều classroom/exam domain. Muốn giải thích tỷ lệ rejected chính xác phải join từng screening Exam với selection/QA/receipt; không bịa “770ảnh đã bị loại”.

## Remaining pool và trạng thái

- Classroom/Student/Exam/RF: đã scan index toàn export, nhưng chỉ visual screening một phần theo caps. Các row train còn lại và nhóm tên chưa xem cần measured counter; **remaining useful eligible independent groups: unknown**, trạng thái `not_exhausted_independence_pending`.
- SCB Head/HRW: kho lớn và có looking/read/write hints còn nhiều; scene/video duplication và group graph là blocker. 625bbox bị flag trong546label file của ba SCB archive audit lịch sử; không cứu/clip âm thầm. **Unknown useful remaining**, không exhausted.
- COCO:185eligible phone-context theo bộ lọc hiện hành đã được visual screening toàn bộ; **exhausted cho bộ lọc185này**, không exhausted COCO. Work-without-phone-annotation hints:355total,120screened→235chưa screening (measured metadata), không235phone N. Quét tiếp có chọn lọc hoặc đề xuất thay filters mới công khai; không refill bằng ảnh stock/easy.
- Open Images: prefix bbox chưa exhaustive; full pool và useful yield phần chưa scan unknown. R1 chỉ desk-context/held+work; R2 title-hints có18payload thường product/hand-only; R3/R4 có399work hints. Số1.128Mobile phone boxes trong prefix không phải1.128positive. Không suy N khi thiếu annotation phone.

Duplicate/lineage counts có thể giao nhau: không cộng train exclusion, full-source duplicate, screening lineage và rights quarantine thành một unique rejected total. R7 lineage triage cách ly43screening keys; public rights quarantine34ảnh nguồn ngoài primary; cả hai chưa phải owner rejected. R2 exact-crop dedupe212→192 là20bản dư đã merge alias; không dùng20để khẳng định đã đo hết duplication ở R7.

## Bằng chứng và giới hạn

Đã đọc: AGENTS.md, docs/00-INDEX.md, .codex/TASK.md, R7README/plan/config/supply/summary/screening inventory, `docs/data/pilot-b-v6-source-proposal-20261007.md`, `docs/data/fpi-scb-research-20261007.md`, `docs/data/v7-public-auxiliary-rights-20261008.md`; code `pilot_targeted_expansion.py`, `coco_targeted_candidates.py`, `openimages_targeted_candidates.py`. Snapshot nguồn: `artifacts/reports/pilot-b-v6-source-research-20261007/roboflow-payload-audit.json`, `roboflow-duplicates.json`; `fpi-scb-research-20261007/scb-local-reaudit.json`; `outputs/pilot-b-v6-source-research-20261007/roboflow-image-inventory.json`.

Snapshot này ghi ngay dữ kiện đã đo để không mất checkpoint sau phiên ngắt. Các cell ghi “cần counter” hoặcunknown phải được cập nhật bằng artifact bổ sung, không gọi audit hoàn tất khi còn chúng. Không dùng test bytes/decode/inference hoặc số metric giả. R7/v4–v6 và historical evaluation artifacts giữ nguyên.
