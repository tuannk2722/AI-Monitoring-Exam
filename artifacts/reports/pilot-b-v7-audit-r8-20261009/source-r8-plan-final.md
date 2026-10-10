# R8 có điều kiện — theo failure mode, không quota crop

Trạng thái Draft. R8 acquisition/visual expansion chưa chạy: actual new download/crop yield=0, diversity gain chưa đo. R7 measured yield là 274 crop/242 ảnh, không phải 274 accepted hoặc nhóm độc lập. Dùng [funnel cuối](source-coverage-final.md) và group graph cùng package trước membership/split.

| Ưu tiên | Action khả thi | Điều kiện / bằng chứng cần | Báo cáo hoặc dừng |
|---|---|---|---|
| 1 — Desk-phone | Quét Classroom/Student/Exam/RF train chưa screening theo unused group proposals sau graph QA; Exam dùng shortlist riêng để tránh bị cap nguồn lớn lấn át | Đúng classroom/exam; mobile flat trên bàn riêng; head/hands/workarea đủ. Loại parent val/test relatives, augmentation/re-export và nhóm đã dùng. Tìm P/N thật trong cùng camera/session | Báo scanned→screened→eligible P/N/U, scene gain, actual yield và shortage. Không còn nhóm độc lập: `blocked_independence`; hết filter phù hợp: `exhausted_filter`; không refill bằng negatives dễ |
| 2 — Looking | SCB Head/HRW+Classroom/Exam: tìm P/N cùng ảnh/camera/room, crop chứa bài/screen của người | BowHead/TurnHead/read/write chỉ hints. Không suy P từ đầu nghiêng hoặc N từ tên nguồn; giữ U khi thiếu workarea | Báo fully-known support và same-image/session pairs. Context-only vẫn pairing hypothesis, không nâng strength bằng tên source |
| 3 — Crowded | Tìm multi-person classroom/exam với anchor/head/hands/own phone rõ và các tổ hợp target trong cùng cảnh | Co-occurrence cần phone P và looking P của cùng người. Không lấy phone teacher/neighbor cho anchor; actor/ownership owner chốt | Đếm ownership/co-occurrence trước và sau recrop; chỉ đông người nhưng thiếu evidence thì unknown/reject có lý do |
| 4 — Small/partial | Chỉ bổ sung variation thiếu sau owner input224 QA | So source/crop/input224 đúng preprocessing E003; mobile không mất hoặc nhầm calculator/tablet/camera; bbox nguồn không thay canonical label | Báo retained evidence/U/downgrade, variation và diversity tăng thật. Không tạo size threshold/acceptance gate mới |
| Public auxiliary | Open Images quét tiếp bbox train chưa scan bằng complete image groups; Person+mobile+desk/book/laptop và title work/classroom/exam chỉ là filters/rank hints. COCO xét chọn lọc 235 work hints còn lại hoặc filter version mới | Pin metadata range/checksum; khử trùng ID/SHA/Flickr/cross-source; license/landing/notice rõ. Ưu tiên phone/person/work hints và same-photo actors/session hơn negatives thiếu annotation | OI báo bytes/rows/groups scanned, filter supply và actual yield; không gọi toàn nguồn exhausted. COCO 185 phone-context filter đã hết, nhưng 235 work hints không phải 235 N |

Không bắt tăng một số crop cụ thể. Chỉ thêm khi tăng classroom/exam desk-phone supervision, looking có workarea cùng camera, ownership/co-occurrence đúng actor hoặc evidence small/partial tại 224. SHA unique, image ID mới và số nguồn không chứng minh diversity. Nếu group graph chưa chứng minh unused independent groups, giữ `independence_pending` dù metadata còn nhiều.

## Owner decisions

| Quyết định / Owner | Đề xuất | Điều kiện chốt |
|---|---|---|
| TBD-R8-LOCAL-SUPPLY / repository-owner | Tiếp Classroom/Student theo group graph; retry Exam riêng; SCB ưu tiên matched looking | Funnel per-source, unused groups có bằng chứng, source/crop/input224 review |
| TBD-R8-MATCHED / repository-owner | Chỉ tính matched mạnh khi same-image/scene/session có bằng chứng | Pair/graph audit; anchor/gaze/workarea rõ |
| TBD-V7-CASES / repository-owner | Nghiệm thu từng device/gaze/anchor trong owner final review mới | Không coi QA flags là chỉ thị relabel; giữ R7 immutable |
| TBD-V7-MEMBERSHIP/SPLIT / repository-owner | Khóa uncertain/evaluation relatives ngoài training proposal; assignment theo component vẫn Draft | Graph/provenance, parent reconciliation, approval riêng; không random split theo SHA |
| TBD-PUBLIC-NOTICE / repository-owner | Chốt phạm vi use/rights/notices của các ảnh có metadata; giữ 34 ảnh quarantine ngoài primary | Attribution/license/landing/Flickr identity/changes notice; metadata đủ không thay approval |
| TBD-E004-PROMOTION / repository-owner | Giữ chưa eligible; không train hoặc model run trên holdout | Dataset release approval, recipe/gates/protocol được chốt; independent holdout freeze riêng |

Blocker v7 release: owner final annotation/crop/input224 review; independence/lineage/parent group reconciliation; membership/split approval; public rights/notice decisions; version/pins/integrity. Blocker E004 promotion eligibility: các gate dataset trên cộng recipe/numerical gates/protocol và independent holdout source/scope/rights/freeze chưa chốt. Public auxiliary ngoài exam không thay independent exam holdout. Việc chọn quota/train/split hoặc numerical gate mới vẫn thuộc owner.
