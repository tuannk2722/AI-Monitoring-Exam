# Quyết định sau thực hiện R8

Approval R5 đã nhập [receipt](owner-approval.json) cho274 crop/nhãn/anchor cuối và policy R8 có điều kiện. Không cần owner duyệt lại các sửa R5 đã nghiệm thu. Approval của package có điều kiện không tạo source/session evidence đang unknown, official split còn null hoặc E004 run identity chưa có dataset pin. [Constraints274 record](qa-r2/approved-r5-membership-constraints.jsonl) là đề xuất version mới, không sửa R5.

| Hạng mục | Bằng chứng hiện tại | Hành động / owner decision |
|---|---|---|
| Classroom | Thêm60screen, lũy kế232;2crop mới gồm source003 và teacher từ source cũD026 | Chỉ mở tiếp họ cảnh mới có evidence desk-phone; không quét bù stock/augmentation để đạt số. Pool hữu ích độc lập unknown. |
| Student | Thêm32screen, lũy kế74;0 shortlist; nhiều camera/cảnh SCB đã dùng | Chỉ thêm khi provenance chứng minh họ mới hoặc biến thể target còn thiếu; hiện nguồn chưa exhausted toàn bộ. |
| Exam | Thêm34screen, lũy kế47;2crop looking từ source107 cùng IMG3485-family | Giải thích2crop R7: source phone bị hand-only/collage; R8 cũng không tạo desk-phone train mới. Giữ cả cặp107 cùng parent train family nếu xác minh linkage, không táchval/test. |
| RF | Thêm24screen, lũy kế97;0 shortlist | Không dùng họ RF-GREEN validation làm train. A006 filenameIMG_20220620 là quarantine cụ thể; giữ nguyên crop/label đã approved. Các ảnh ghế xanh khác là QAflags, không tự union theo màu ghế. |
| SCB Head | Thêm24screen, lũy kế90;3crop Draft, một cặp looking cùng source155 | SCB18/130 nối parent train scenes, group gain0. Bỏ C004 và pair002 vì gaze negative chưa đủ. Không còn anchor dễ gây hiểu nhầm trong final. |
| SCB HRW | Thêm12screen, lũy kế46;0 shortlist | Chỉ mở tiếp nếu source/camera/workarea thiếu được xác định; large available pool không chứng minh diversity. |
| Open Images | Thêm64MiB bbox,2.388.134annotation rows/317.459complete image groups,16,3430%bytes;22ảnh mới, lũy kế620;0crop | Bỏ whole tail image. Tiếp targeted class/context/title filter ở prefix mới; không khai source exhausted. Device iPod không thành mobile P. |
| COCO | Thêm64ảnh work-filter, lũy kế369;0crop;171work hints còn trong filter | Chỉ tìm classroom/ownership hoặc khó tại224; không mặc định absent phone annotation=N. Filterphone đã exhaust subsetmetadata cũ, không full useful pool. |
| Nguồn Internet mới | Wikimedia1video/65 frame/2lookingcrop; IMPROVE/HCCB phải xin; UCB blocked file inventory | [Research nguồn](source-research.md), [bản yêu cầu](source-access-drafts.md). Owner đã chốt nghiên cứu cá nhân; publisher acceptance/signature/contact fields vẫn thiếu. |
| Desk-phone bucket | R5 classroom6P/6N; R8 đủ cho train mới0 | **Thiếu**, ưu tiên cao nhất. Không thêm phone-at-home thay classroom/exam. |
| Looking bucket | R8looking4P/3N/2U trong9 crop;3same-image P/Npairs; một pair từ source mới | Có evidence tốt hơn context-only; chưa đủ nhiều camera/session độc lập,7/9 crop còn ít nhất một U. |
| Crowded/ownership | TeacherP/femaleN cùng sourceD026, negative approvedR5, không đếm lại crop nữ;0 new PP | Coverage attribution tăng, co-occurrence dương độc lập vẫn thiếu. |
| Phone small/partial | R8phone2P/2N/5U;2phoneP là low-light nam003 và teacherD026 | Owner review source/crop/native224; không biến source P thành input224-usable mặc định. |
| Four-combination support | Fully-known2;PP0/PN0/NP1/NN1 trongR8 | Không đủ claim giải quyết mọi failure mode. Gộp R5/R8 counts chỉ sau owner review newbatch và eligibility QA. |
| Membership R5 | 257 conditional,16 UU review_only,1evaluationfamilyquarantine | 257 là **upper pool có điều kiện**, không train-ready. Whole-component constraints còn giữ; singleton graph không proof independence. A006 ngoàitrain bởi v6boundary Accepted. |
| Split / holdout | Official assignment null; không đọc historicaltestpixels, không model holdout | Chưa materialize release/split; chốt graph/source-role trước holdout intake. Không đặt cùng video/session vào development và independentholdout. |
| Public rights | Hồ sơR5 currentlocal đã ownerapprove;34quarantine cũ giữ nguyên;2WMFcrop cần scoped ownerdecision | WMF credit/license/changesnotice đã có; chưa cho release derivative với rights khác chưa chốt. Controlled-source agreements chưa ký. |
| Blocker release v7 | Newlabel/crop9chưaownerreview;group/quality/rightseligibility;desk-phone/classroomshortage;finalassignment/pointerchưacó | Không release chỉ vì274+9 crop. Duyệt newbatch không thay việc giải quyết shortage và group graph. |
| Blocker E004 promotion | Chưa v7release/split pin;chưa độc lập holdout freeze và kết quả đánh giá;chưa run contract accepted cụ thể | Không train/promote ở tasknày; approval báo cáo hiện tại không là promotion evidence. |

## Cases cần review mới

Mở [review9 crop](../../../outputs/v7-r8-owner-review-20261009-r6/review-index.html). Thứ tự nhãn luôn phone/looking. B001P/U(lowlight),C001N/P+C002N/N(sameimage),C003U/P(instructioncontext),C005U/P+C006U/N(sameimage),D001P/U(teacherownership),C007U/P+C008U/N(WMFsameimage). Static looking P là hướng nhìn ngoài own-workarea, không kết luận gian lận; việc đang nghe giáo viên vẫn phải owner kiểm semantics/evidence.

Pair004 tham chiếu nữV7-D-026N/N đã accepted trong receiptR5. Crop mớiD001chưa approved. Pair003SCB155cần xác nhận workarea/gaze, không dùng classBowHead/HandRaise làm nhãn. R8C004đã loại khỏi final vì chưa chắc nhìn trang, không âm thầm giữ N.

Owner actions còn lại: nghiệm thu batch mới9 crop, quyết định scope/member cho publicWMF và groups sau bằng chứng; truy cập IMPROVE/HCCB cần contact/thỏa thuận riêng. Chưa gửi thư vì user mới yêu cầu research và chọn tư cách cá nhân, chưa chỉ thị gửi thông tin tới publisher.
