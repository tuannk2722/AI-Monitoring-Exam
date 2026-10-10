# Public follow-up R2 — 2026-10-10

Đã tiếp tục research và **xác minh thêm một nguồn có payload public thực tế**: [Students’ Abnormal Behavior in Online Exam, Zenodo](https://zenodo.org/records/14606173). API mới trả **CC BY4/open**, giải quyết blocker license của snapshot trước. Giữ nguyên snapshot/R1 đã sealed, không sửa receipt504 cũ. Đã audit ZIP original bằng Range và tải/xem **38 ảnh train**; kết luận nguồn webcam cận mặt này **chưa bù được desk-phone classroom, matched-looking có workarea hoặc crowded attribution**. Không tăng dataset bằng ảnh dễ chỉ để tăng số.

## Funnel và evidence

| Chỉ tiêu | Measured | Giới hạn |
|---|---:|---|
| Requests metadata có config/payload receipt |5, nhận4, lỗi1| HCMUE/UCB HTML nhận200 nhưng không có usable file inventory |
| ZIP entries |11.079| Không gọi là11.079ảnh |
| Images trong original ZIP |5.575| Train4.395, valid1.099,test81; không tính augmented6,4GB |
| Annotation TXT entries / TXT payload scanned |5.495 /0| Chỉ đọc YAML class names; chưa scan bbox annotation |
| Selected / downloaded / visually screened |38 /38 /38| Chỉtrain, finite cap48, filename-prefix hints19 chưa là19session |
| CRC members kiểm / whole archive MD5 kiểm |38 /không| ChỉRange subset, không claim MD5 toàn833.824.026bytes |
| Bytes Range inventory / screening |1.286.751 /5.927.430| Bao gồm central-directory/headers, không toànarchive |
| Source SHA / pixel duplicates trong subset |0 /0| Cảnh lặp và phiên quay vẫn chưa xác minh độc lập |
| Remaining train images chưa tải |4.357| Remaining **visually eligible** pool unknown, source chưa exhausted |
| Targeted dataset additions / train-eligible |**0 /0**| Không tự approve membership hoặc split |

[Yield summary](yield-summary.json), [inventory receipts](inventory/source-receipts.json), [screening receipt](online-exam-screen/summary.json), [38observations](visual-observations.jsonl). Source YAML có `eye_movement/hand_move/mobile_use/side_watching/mouth_open`; không map chúng thành labels v7. YAML val path không đồng nhất layout ZIP, vì vậy chọn split từ member path train trực tiếp; không dùng YAML để mởvalid/test. Camera/session và privacy-use scope chưa đủ để nhập official dataset.

Đã xem đủ7contact sheets. Phần lớn image publisher đã resize/crop cận mặt, không có bài/bàn/monitor riêng. Head-turn hoặc eyes-side không chứng minh looking P theo v7; tay/phone ngoài khung không chứng minh phone N. 007 có own-held mobile bị cắt ở cạnh source, không phải desk phone; không dùng hình đó đóng classroom shortage. Không face-recognize hoặc nối danh tính các ảnh. Filename-prefix chỉ giúp chọn subset, không chứng minh participant/camera/session independence.

## QA-only để owner xem

[Hai ví dụ source/crop/input224](../../../outputs/v7-online-exam-qa-20261010-r1/review-index.html): QA-ONLINE-001 đề xuất phoneP/lookingU vì own-held mobile partial; QA-ONLINE-002 giữU/U dù mặt quay ngang vì thiếuworkarea. Đây là **QA-only, không dataset additions**, không fully-known/pair gain. Crop bằng source vì publisher đã mất vùng bàn; recrop không phục hồi pixels. Có author/title/license/change notice, masks0/targetsnull/splitnull/trainingfalse. Owner chưa nghiệm thu. Rendering38source/7sheets nằm ở [outputs](../../../outputs/v7-online-exam-screen-20261010-r1), không commit media; raw immutable.

## Nguồn mới/blocked và quyết định tiếp

| Nguồn sơ cấp | Kết quả R2 | Đề xuất |
|---|---|---|
| [HCMUE-SEGL](https://github.com/HungNguyenHcmue/HCMUE-SEGL) | Anonymous GET link publisher trả Google Drive Sign-in, không inventory | Access-blocked cho tool; không bypass/login hoặc nhận private inventory là public. Còn ưu tiên nếu có grant |
| [V-CL part1](https://zenodo.org/records/19363805) | API CC BY4 nhưng access_right=restricted,files=[] | Không tải/bypass; webcam individual online learning chưa giải quyết crowded/classroom anyway |
| [StudentAct, HUST/SigM](https://sigmlab.com/datasets/StudentAct/) | Primary page5camera/31.046frames/596.371boxes, yêu cầu ký commitment; cấm modification | Potential classroom phone/camera, **blocked access/rights** cho crop/224. Không suy5cameras thành5independent groups, không gửi request trùng thay owner |
| [Classroom-cell-phone v3](https://universe.roboflow.com/computervisionprojects-siakl/classroom-cell-phone-detection/dataset/3) | Web page CC BY4,253images/178train,51valid,24test; direct GET403, khôngpayload | Metadata-only; upstream/scene overlap/mirrors chưa verify. Không coi14versions hoặc mirror253 là14nguồn độc lập; không gọi model API |
| [UCB v2](https://data.mendeley.com/datasets/pz7y4bpfxy/2) | Pagemetadata biếtCCBY4; HTTP response genericFAQ/app không file listing | Inventory-blocked, useful pool unknown; không guessed API/export/token |
| [Invigilo](https://github.com/chandan-srinivas29031998/Invigilo) | Repository tự ghi self-recorded clips/scenarios nhưng tree công khai chủ yếuannotations/code | Source lead; codeMIT không tự chứng minh media license/access.0payload/0yield, chưa mở benchmark/testvideos |

Các search Commons bổ sung chủ yếu trả ảnh sản phẩm, biểu đồ, room trống, handheld-only hoặc cảnh đã screened; không tải các ảnh ấy để refill. Owner đã báo gửi access requests ở lượt trước; chưa biết chính xác list, không tự gửi thêm. CDED7 giữ scope-use blocker đã ghi ở R1, không tự nhập nguồn có điều khoản cấm surveillance vào exam monitoring.

**Ưu tiên tiếp:** classroom/exam public có room/session và bàn/bài thật; nguồn có nhiềucamera/annotation context chỉ khi access/crop rights rõ. Online-exam source hạ ưu tiên cho expansion hiện hành; nếu sau này nghiên cứu online-exam riêng thì cần scope/config/semantics mới. R1 vẫn là gói ownerreview13Draft hiện tại; resume không phê duyệt13crop hoặc2QA examples. Shortage, graph, rights, final split, release/gates E004 vẫn pending.

## Validation và preservation

235testsPASS; Ruff src/tests/scripts và mypy2module mới PASS, repository guard/diff/link/hash checks ở [validation](validation-final.json). [Pointer/checksums](review-pointer-final.json) pin riêngR2. R1 pointer/seal31reports/57reviewfiles vẫn nguyên; README R8 mismatch vẫn giữ expectedcba7e324…/actual929d140c…, chưa owner giải thích. Không tự reseal lịch sử, train E004, release v7, materialize split, đọc media projectholdout hoặc chạy model independentholdout.

Canonical logic: `public_source_inventory.py`, `public_zip_screening.py`; YAML chứaURLs/budgets/memberindices/QA cases. Config screenR1 là input đã chạy; module sau đó tách panels ra outputs, và rendering của run chưaseal được chuyển vàooutputs bằng đường dẫn đã kiểm. Config screenR2 ghi layout hợp lệ cho lầnchạy mới, **chưa chạy/tải lại**, không overwrite raw/runR1. Không claim module đã chạyR1 giống byte-for-byte module final sau layoutfix.
