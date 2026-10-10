# Phân tích annotation/quality cuối — R7 so với proposal R5

Đo từ `annotation-r4/annotation-summary.json` và CSV đã pin. Không sửa R7, canonical target/mask hoặc split. P/N/U theo thứ tự phone/looking; support dưới đây là proposed support, không accepted samples hay independent groups.

## Fully-known và four combinations

| Source | Crop | Fully-known R7 → R5 | R5 PP | PN | NP | NN |
|---|---:|---:|---:|---:|---:|---:|
| Classroom | 60 | 7 → 8 | 2 | 2 | 0 | 4 |
| Student | 14 | 14 → 12 | 0 | 0 | 0 | 12 |
| Exam | 2 | 0 → 0 | 0 | 0 | 0 | 0 |
| RF | 23 | 8 → 8 | 0 | 0 | 1 | 7 |
| SCB Head | 26 | 0 → 0 | 0 | 0 | 0 | 0 |
| SCB HRW | 18 | 0 → 0 | 0 | 0 | 0 | 0 |
| COCO | 39 | 12 → 11 | 3 | 0 | 2 | 6 |
| Open Images | 92 | 32 → 30 | 5 | 1 | 4 | 20 |
| **Tổng** | **274** | **73 → 69** | **10** | **3** | **7** | **49** |

Không nguồn nào tự có đủ bốn tổ hợp. Final classroom/exam-context 143 crop chỉ có PP2/PN2/NP1/NN23 = 28 fully-known; 131 auxiliary có PP8/PN1/NP6/NN26 = 41. Tám trong mười PP nằm ngoài exam. NN chiếm 49/69 fully-known; count tổng không đóng desk-phone/gaze/crowded shortages đúng domain.

Final phone 95P/62N/117U, looking 65P/105N/104U. 16 U/U giữ review_only/quarantine; 258 record có ít nhất một target known là upper bound, chưa qua owner approval, rights, group và usability. Target U phải masked khi có release riêng sau nghiệm thu; package hiện tại mask cả hai bằng 0.

## Concentration và looking

OI 92/274 = 33,58%; Classroom 60/274 = 21,90%; hai nguồn chiếm 55,47%. Auxiliary COCO+OI chiếm 47,81%. 242 source images và 232 family-hint strings không chứng minh 242/232 cảnh độc lập. Source image lớn nhất đóng góp ba crop; family hint lớn nhất là SCB parent-train hint đóng góp bốn crop (1,46%). Hint concentration thấp không loại trừ nhiều image trong cùng camera/video/collage.

| Source của C98 | R7 looking P/N | Final P/N/U | Camera / room / registered group |
|---|---|---|---|
| RF | 11/3 | 11/2/1 | UNKNOWN |
| Head | 22/4 | 20/4/2 | UNKNOWN |
| HRW | 1/17 | 0/17/1 | UNKNOWN |
| Exam | 1/1 | 1/1/0 | UNKNOWN |
| COCO | 4/5 | 3/5/1 | UNKNOWN |
| OI | 10/19 | 10/19/0 | UNKNOWN |

R7 looking P chủ yếu Head, N chủ yếu HRW/OI. Cân bằng 49/49 tổng không tạo matched camera P/N. `annotation-looking.csv` có từng source/family/polarity và UNKNOWN thật cho camera/room/group; cả 274 record không có registered group/camera/room đã xác minh. Cần bổ sung provenance trước khi nói đã giải quyết nguồn/cảnh confounding.

## A, B và D

A57 vẫn phone32P/25N; đúng classroom/exam-context chỉ12 crop =6P/6N, còn45 auxiliary. Không tính45 ảnh public để đóng shortage classroom desk-phone. Final looking của A là11P/22N/24U; cropped mobile thuộc đúng anchor và own workarea cần owner nghiệm thu.

B80 input224 audit giữ snapshot R7: phone40P có32 clear/8 ambiguous;40N có31 clear/7 ambiguous/2 lost. Sau source review/recrop, final36P/34N/10U; gaze5P/28N/47U. Nguồn ambiguity/device identity và negative visibility được tách khỏi preprocessing loss. B048/B111 recrop giữ writing evidence; B066 mới U/U vì anchor background và own workarea chưa rõ. Không tạo pixel threshold hoặc suy source thiếu phone annotation thành N.

D39 R7 có PP2/PN1/PU29/UP2/UN5; final PP2/PN1/PU24/UP2/UN5/NN1/UU4. Chỉ D009/D021 là hai proposal visible phone+gaze co-occurrence cùng actor, còn pending owner. D026 nữ áo sọc viết bài là NN; phone thuộc teacher. D006 tablet, D025 thiết bị khó xác minh, D027 nhỏ/cắt, D033 camera giữ U/U. D050 PN là một proposal, không 39 co-occurrence. `annotation-crowded.csv` lưu evidence/anchor/state; `input224-r3/ownership-findings.json` lưu QA ownership R7.

## Pair và graph

162 R7 links gồm6 same-image,1 same-scene,155 context-only. Sau final140 đúng target polarity,22 invalid; polarity không đồng nghĩa same-camera/session. R7 metadata gợi ba same-image pair mới; kiểm ảnh giữ hai Draft: B039/B089 phone và B102/C131 looking. B066/B020 là cùng ảnh nhưng B066 thiếu workarea/visibility, finalUU nên không dùng pair hiện tại. Không tìm session matched pair mới đã xác minh. Cả hai pair giữ thuộc auxiliary và independent group gain0.

Graph final233 conservative components,0 independent groups proven. Sáu component/14 crop nối parent train bằng explicit PARENT-TRAIN scene hint; linkage vẫn unproven và cần owner. Không union mọi nearest similarity:548 nearest-parent/evaluation flags giữ riêng, không phải548 leakage confirmations. Không thấy exact evaluation component trong graph hiện tại không chứng minh toàn bộ lineage sạch.

Split proposal: component nối parent train phải review và giữ cùng train nếu approve; component evaluation-related phải quarantine; component mới chưa parent chờ owner chứng minh group rồi chốt train hoặc development validation mới theo toàn component. Không random split crop, không thay test/validation lịch sử, chưa official assignment.
