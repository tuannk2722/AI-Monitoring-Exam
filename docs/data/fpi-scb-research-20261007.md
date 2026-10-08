# FPI-Det và SCB5 — nghiên cứu mở rộng sau E002

Ngày nghiên cứu: 2026-10-07. Owner: chủ repository. Trạng thái: **báo cáo nghiên cứu và đề xuất; không phải approval dataset, mapping, split hoặc training**.

## Kết luận phục vụ quyết định

**Nên tiếp tục khai thác SCB Head/HRW ở quy mô lớn hơn và xem FPI-Det là nguồn bổ sung phone có tiềm năng, nhưng chưa nhập nguyên nhãn FPI vào classifier.** Nút thắt là chuyển nguồn lớn thành crop theo người có nhãn đúng, nhóm độc lập và đánh giá đáng tin; số lượng file tải về không tự giải quyết được việc này.

- SCB hiện không hề chỉ có vài chục ảnh. Đã kiểm lại 10.138 JPG trong ba ZIP; v5 mới sử dụng **49 crop SCB để train**, 3 val và 9 test. Có 67 crop SCB review-only, 4 excluded. Không suy số ảnh nguồn thành số mẫu đã review hoặc số cảnh độc lập.
- FPI công bố 22.879 ảnh; annotation công khai đã kiểm đủ **18.800 train và 1.730 val**. Đó là box mặt/điện thoại, không phải person bbox hoặc nhãn multi-label của dự án. CSV hành vi có **4.079 dòng**, không phủ train.
- FPI có mâu thuẫn về chiều mã hóa nhãn và phạm vi benchmark; phải giải quyết trước conversion. Không tuyên bố CSV chắc chắn sai hay tự đảo 0/1.
- Các lớp SCB liên quan phải dùng để tìm ứng viên relabel, không tự map `TurnHead` thành positive hoặc `read/write` thành normal. Không mở lại quyết định loại Discuss hoặc quyền SCB owner đã xác nhận.
- Cả hai nguồn chưa chứng minh cung cấp holdout phòng thi độc lập. Nếu gom FPI thành phone-positive và SCB thành phone-negative, nguồn ảnh vẫn có thể thay thế hành vi trong quá trình học.

## Phạm vi kiểm tra và khả năng tái lập

| Nguồn | Đã thực hiện | Chưa thực hiện |
|---|---|---|
| FPI GitHub | Pin commit `83c452d1a1e5b1bac88afe1a6834cb9c25e036eb`; đọc README/LICENSE/YAML, hai COCO JSON, CSV và code đánh giá; đếm lại geometry, class, overlap tên, polarity và duplicate prediction | Chưa tải/decode toàn payload ảnh; chưa kiểm SHA ảnh/gần trùng/session; chưa xác minh nhãn trên mẫu raw |
| FPI trực quan | Xem figure công khai `figure_mopho/datasetsample.png` của tác giả: 8 khung minh họa | Figure có chọn lọc, không đại diện tỷ lệ lỗi/domain và không thay audit raw |
| SCB local | Hash đúng ba ZIP đã dùng; đọc toàn bộ member qua ZIP/CRC; decode 10.138 JPG; kiểm từng dòng bằng `YoloAnnotation.parse`; đếm duplicate SHA toàn nguồn | Không relabel toàn bộ người; chưa chạy gần trùng toàn nguồn; chưa phục hồi metadata session |
| SCB upstream | Pin Hugging Face `0fdc46fe393d251320def8c6d10cbc95d89f7da6`; đọc bốn YAML lớp, cây file; central directory YOLO.zip và hai ZIP LLM | Không tải toàn bộ các archive khác; central directory không thay kiểm payload/CRC/SHA |
| SCB trực quan | Xem lại hai contact sheet lịch sử Head/HRW, tổng 15 ô train được chọn theo class/kích thước | Không phải mẫu ngẫu nhiên; không ước lượng tỷ lệ sai nhãn từ thumbnail |

Bằng chứng nhỏ: [FPI](../../artifacts/reports/fpi-scb-research-20261007/fpi-metadata-audit.json), [SCB quét lại](../../artifacts/reports/fpi-scb-research-20261007/scb-local-reaudit.json), [upstream](../../artifacts/reports/fpi-scb-research-20261007/scb-upstream-inventory.json), [mức dùng v5](../../artifacts/reports/fpi-scb-research-20261007/current-usage.json), [provenance](../../artifacts/reports/fpi-scb-research-20261007/provenance.json). Snapshot tải và script kiểm kê ở `outputs/fpi-scb-research-20261007/`, Git ignored. Không thực thi code tải từ tác giả.

## FPI-Det: mức phù hợp và những điều cần xử lý

### 1. Annotation thực tế khác đầu vào classifier B

[Repo chính thức](https://github.com/KvCgRv/FPI-Det/tree/83c452d1a1e5b1bac88afe1a6834cb9c25e036eb) công bố nguồn cho phone-use. [Paper v1](https://arxiv.org/html/2509.09111v1) mô tả nhiều bối cảnh, có 22.879 ảnh và split 18.800/1.730/2.349; đây là thống kê tác giả, chưa phải audit toàn payload phiên này.

Kết quả đọc file tại commit đã pin:

- `Phone.yaml`: detection ID **0 = phone, 1 = face**. COCO JSON chỉ ghi `class_0/class_1`, nên phải giữ liên kết YAML khi diễn giải; không dùng ID detection làm target classifier.
- Trường annotation chỉ có `id,image_id,category_id,bbox,area,iscrowd`; metadata ảnh có `id,width,height,file_name`. Không thấy person bbox, person/phone association, session/camera ID hoặc trường bốn hành vi trong hai JSON đã kiểm. Không kết luận các trường đó chắc chắn vắng trong ZIP chưa tải.
- Train có 4.199 ảnh nhiều hơn một face; tối đa 37 face. Suy phone thuộc người nào bằng “cùng ảnh” hoặc “gần nhất” sẽ tạo nhãn sai trong tình huống đông người.
- `label.csv` chỉ có `image_name,class_id`: 4.079 tên duy nhất, khớp đủ 1.730 tên val, còn 2.349 tên ngoài train/val; **0 tên khớp train**. Phần 2.349 phù hợp số test tác giả công bố, chưa có JSON test để xác minh trực tiếp. Không lấy CSV đánh giá làm bộ nhãn train.

Muốn giữ kiến trúc B đã accepted, cần tạo person bbox/crop có ngữ cảnh, review liên kết điện thoại với người và relabel target. Face box không đủ thay person box; phone box chỉ là bằng chứng tuyển mẫu. Nếu đề xuất detector phone/face hoặc mô hình quan hệ như kiến trúc mới thì cần ADR riêng, không phải thay đổi ngầm của task dữ liệu.

### 2. Mâu thuẫn polarity: dừng mapping tự động

[Paper §3.3](https://arxiv.org/html/2509.09111v1#S3.SS3) và mô tả trong [script phân loại](https://github.com/KvCgRv/FPI-Det/blob/83c452d1a1e5b1bac88afe1a6834cb9c25e036eb/classification_task/simple_classify_images.py) nói **0 = dùng phone, 1 = không dùng**. Nhưng kết quả join theo tên giữa CSV và annotation val là:

| Loại box trong ảnh val | CSV 0 | CSV 1 |
|---|---:|---:|
| Chỉ face | 532 | 16 |
| Cả face và phone | 64 | 379 |
| Chỉ phone | 60 | 292 |
| Không có box | 383 | 4 |

Bảng này **gợi ý CSV có thể dùng 1 = có phone-use**, trái mô tả. Tuy nhiên detection có thể thiếu nhãn hoặc các file thuộc phiên bản không đồng nhất; metadata không đủ xác định nguyên nhân. CSV toàn bộ có 2.425 số 0 và 1.654 số 1; chưa gọi đó là số positive/negative canonical.

Semantics cũng khác: paper phân biệt active use với chỉ cầm. Target dự án bao gồm cầm/tương tác phone hoặc phone trên bàn gắn được với người. Vì vậy, kể cả giải quyết chiều 0/1, negative của FPI vẫn không tự thành negative của dự án.

### 3. Mã benchmark không nên đưa vào production

Đọc tĩnh [calculate_metrics.py](https://github.com/KvCgRv/FPI-Det/blob/83c452d1a1e5b1bac88afe1a6834cb9c25e036eb/classification_task/calculate_metrics.py) thấy dùng mặc định positive label 1; không chỉ định `pos_label=0`. Do đó kết quả không thể đồng thời mang nghĩa positive 0 như phần mô tả nếu không có giải thích bổ sung.

Tính độc lập từ CSV đã lưu, không chạy code upstream:

- `8x.csv` đủ 4.079 tên: accuracy 0,892130; F1 với numeric positive 1 là 0,870283, với numeric positive 0 là 0,907679. Hai con số là hai cách tính trên cùng dự đoán, không phải hiệu năng của hai model mới.
- `11x.csv` có 4.698 dòng nhưng chỉ 2.349 tên, mỗi tên lặp hai lần cùng giá trị; thiếu 1.730 tên so label.csv. Các CSV YOLO khác đã kiểm có đủ 4.079 tên. Không xếp hạng trực tiếp chúng trên tập khác nhau.
- Script merge mặc định inner join nên có thể bỏ tên thiếu hoặc nhân đôi bản ghi mà không fail. Script `simple_classify_images.py` tìm vùng màu đỏ/xanh trên ảnh đã vẽ dự đoán và dùng quy tắc đồng xuất hiện; đây không phải bộ suy luận quan hệ person–phone đáng tin cho ảnh raw.

Không sao chép rule “có face + phone là đang dùng” sang project. Báo cáo metric upstream cần được đọc cùng vấn đề polarity, join và phạm vi mẫu; không dùng các số này để hứa chất lượng E003.

### 4. Geometry, số lượng và split

| File COCO công khai | Ảnh | Face theo YAML | Phone | Box vượt biên strict | Trong đó vượt > 1e-6 pixel |
|---|---:|---:|---:|---:|---:|
| train | 18.800 | 24.992 | 8.358 | 1.100 | 1.087 |
| val | 1.730 | 1.318 | 795 | 7 | 6 |

Train có thêm 1 box width/height không dương; mức vượt biên lớn nhất 36 pixel. Val lớn nhất 0,4655 pixel. Các nhóm lỗi có thể giao nhau, không cộng thành số box lỗi duy nhất. `1e-6` chỉ là thống kê chẩn đoán để phân biệt sai số rất nhỏ, **không phải epsilon đã được phê duyệt để sửa dữ liệu**. Chưa đối chiếu dimensions JSON với pixel ảnh, nên đây là lỗi tương đối với kích thước khai báo.

Train đếm ít hơn bảng paper 1 face (paper: 24.993). Không có ID ảnh/annotation trùng trong từng JSON; tên train/val không giao nhau. Không có ảnh để kết luận byte/pixel/scene leakage bằng 0. YAML có comment số ảnh khác paper; dùng actual inventory, không lấy comment làm contract. Không tự clip box hoặc sửa count nguồn.

Tỷ lệ kiểu ảnh cũng lệch: train chỉ 11 phone-only và 48 null; val có 352 phone-only và 387 null. Cần giải thích split và báo slices trước khi dùng metric tổng; split có sẵn chưa chứng minh độc lập camera/người/session.

### 5. Truy cập và quyền

README tuyên bố dataset dùng MIT; file LICENSE là MIT cho software/documentation. COCO `licenses` rỗng, không có bằng chứng quyền từng ảnh trong metadata đã kiểm. Paper nói lấy dữ liệu từ DataFountain và đã có phép. [Trang dữ liệu cuộc thi 506](https://www.datafountain.cn/competitions/506/datasets) yêu cầu đăng ký và đồng ý điều khoản tải; phiên này chưa đọc được toàn bộ thỏa thuận. Đây là các bằng chứng khác nhau, không kết luận giấy phép chắc chắn không hợp lệ hoặc đã đủ cho mọi hình thức tái phân phối.

Link Drive mở được trang preview `reorganized_phone_dataset_yolo.zip` qua HTTP; web reader không mở được. [Issue #3](https://github.com/KvCgRv/FPI-Det/issues/3) báo lỗi tải, không chứng minh link hiện tại luôn hỏng. Chưa xác minh tải hoàn chỉnh/checksum ZIP. Chưa sử dụng tài khoản hay đồng ý điều khoản thay owner; chưa nhập media FPI vào raw/release. Chỉ tải figure công khai để xem minh họa.

TBD-FPI-RIGHTS: owner chốt phạm vi sử dụng local/train/lưu trữ khi tiếp nhận đúng payload và terms; không cần hỏi lại quyền SCB đang dùng. TBD-FPI-PAYLOAD: checksum/version, README và label-map thực tế trong ZIP, group evidence, annotation test và chất lượng ảnh.

## SCB5: nguồn đang dùng và nguồn còn có thể khai thác

### 1. Phân biệt mô tả lịch sử với bản tải hiện hành

[Mô tả arXiv v6](https://arxiv.org/abs/2304.02488v6) nhắc 7.428 ảnh, 20 lớp, gồm phone/computer. [Bản v7](https://arxiv.org/html/2304.02488v7) đã chuyển cấu trúc detection/classification; có cả phần thống kê/class chưa nhất quán. Không dùng tên SCB5 làm định danh bất biến hay lấy con số bài báo làm actual inventory.

Ở [Hugging Face snapshot đã pin](https://huggingface.co/datasets/wintonYF/SCB-Dataset/tree/0fdc46fe393d251320def8c6d10cbc95d89f7da6), bốn YAML detection công khai có 14 tên nguồn: Discuss 1, HRW 3, Head 2, Teacher 8. **Không có lớp phone hoặc computer trong bốn YAML này.** Điều này không chứng minh mọi ảnh SCB đều không có điện thoại.

`YOLO.zip` không nên được hiểu là bộ 20 lớp còn thiếu. Central directory có 27.815 file, nhiều checkout YOLO, weights/kết quả; 12.224 JPG nằm dưới gói Teacher (8.984 train, 3.240 val), còn có ZIP Teacher lồng bên trong. Đã đọc riêng YAML dataset nhúng của YOLOv13: vẫn đúng 8 lớp Teacher, không có phone. Chưa kiểm toàn payload hay tất cả YAML nhúng; lần đọc hàng loạt YAML trước đó gặp lỗi kết nối sau khi central directory đã lưu.

### 2. Quét lại ba ZIP local

Hash cả ba ZIP khớp audit ngày 2026-10-03 và LFS upstream. Không có ảnh decode lỗi, thiếu/orphan cặp ảnh–label trong phép kiểm này.

| Gói | Ảnh | File nhãn bị flag | Dòng bbox bị flag | Lớp và số dòng raw |
|---|---:|---:|---:|---|
| Discuss | 864 | 32 | 37 | discuss 5.392 |
| HRW | 6.864 | 412 | 466 | hand-raising 13.453; read 24.078; write 9.841 |
| Head | 2.410 | 102 | 122 | BowHead 4.962; TurnHead 11.156 |
| Tổng | 10.138 | 546 | 625 | 68.882 dòng |

Có 8.116 SHA ảnh duy nhất, 1.892 nhóm exact duplicate, 2.022 bản dư. Trong đó 1.891 nhóm vắt qua archive và **961 nhóm có cả train/val nguồn**. Đây là vấn đề của nguồn khi concat, không phải bằng chứng v5 đang rò rỉ; v5 đã có split/group riêng được review.

Không gọi mọi dòng trong 546 file đều sai. Validator strict loại cả file khi có một dòng lỗi nên số annotations strict là 63.505; bước cứu từng box hợp lệ là quyết định khác. Không tự clip, đổi tolerance hoặc sửa raw.

Paper v7 giải thích các phần được annotate/chia split riêng, read/write không được gán exhaustive ở mọi ảnh. Vì vậy không gán người ngoài box thành negative; không giữ split nguồn khi hợp nhất. Nguồn từ frame video nên exact dedup vẫn chưa đủ chống gần trùng. Metadata session/camera/người độc lập còn thiếu.

### 3. Các lớp nên dùng thế nào — đề xuất, không phải mapping được duyệt

| Lớp/gói nguồn | Giá trị cho task hiện hành | Cách xử lý đề xuất |
|---|---|---|
| TurnHead | Ưu tiên cho looking_around | Tìm crop có hướng nhìn rõ ra ngoài vùng bài làm; review cả mẫu quay đầu nhưng nhìn bài/không rõ; không auto-positive |
| BowHead | Tư thế dễ nhầm, có thể tìm phone hoặc đọc/viết | Không suy phone/normal; xác minh vật thể, hướng nhìn và hai target |
| read, write | Bối cảnh làm bài và mẫu âm hữu ích | Chỉ xác nhận âm khi đủ bằng chứng; crop rõ cả hai target mới xét normal |
| hand-raising | Mẫu nhiễu về tay/đầu, đa dạng tư thế | Khai thác có chọn lọc; không ưu tiên lượng lớn vì khác bối cảnh thi |
| discuss | Không sử dụng trong baseline hiện hành | Giữ quyết định loại: nhiều box theo nhóm, không nhập thẳng person-level |
| guide, answer, On-stage interaction, blackboard-writing | Phần lớn khác hoạt động làm bài tại bàn | Ưu tiên thấp; không coi là looking positive hoặc normal theo tên |
| teacher, stand | Actor/tư thế không phải target | Chưa bổ sung output; chỉ xét mẫu khi hợp phạm vi người/cảnh và có nhãn review |
| screen, blackBoard | Đối tượng nền | Không chuyển thành mẫu người hoặc hành vi |
| LLM đọc–viết / nghe giảng | Có ảnh lớp học, nhãn cấp ảnh | Cần person proposal và relabel; không lấy nhãn cấp ảnh gán mọi người |
| LLM các lớp còn lại | Phần lớn nhóm/giáo viên/đứng trình bày | Ưu tiên thấp hơn Head/HRW; nhiều class không tự tăng coverage hai target |
| using phone/computer, talk, clap, yawn, leaning on desk trong danh sách lịch sử | Có thể liên quan nếu có đúng phiên bản | Chưa xác minh gói annotation tương ứng trong snapshot hiện tại; không ghi thành dữ liệu đã có |

Các gói LLM có tên cho 14 chủ đề: tương tác trên bục, trình bày trên bục, nghe giảng, trả lời câu hỏi, giơ tay, học sinh viết bảng, tuần tra, ứng đáp, hướng dẫn, giáo viên viết bảng, đọc thành tiếng, thảo luận, giảng dạy, đọc–viết. Đây là thư mục/nhãn ảnh tổng thể, không phải 14 target mới của dự án.

Kiểm central directory hai gói ưu tiên:

- `读写.zip`: 912 JPG, không TXT bbox; **524** file trùng tên + CRC32 + kích thước với ba ZIP local.
- `听讲.zip`: 2.451 JPG, không TXT bbox; **496** file trùng ba dấu vết đó.

CRC32 không thay SHA-256; chưa tải/decode payload nên đây là chỉ báo overlap mạnh, chưa là kết luận byte độc lập. Không dùng hai gói này làm holdout mới chỉ vì đường dẫn khác.

### 4. Vì sao SCB lớn nhưng train nhỏ?

[Ledger v5](../../artifacts/reports/fpi-scb-research-20261007/current-usage.json) cho thấy SCB HRW train 33, Head train 16. Review-only còn 41 HRW + 26 Head. Việc tăng từ v4 lên v5 không tăng SCB train; 20 crop thêm thuộc Classroom và Roboflow.

Do đó E002 chưa kiểm nghiệm giả thuyết “khai thác SCB ở quy mô lớn có cải thiện không”. Nút thắt là số crop đã có nhãn canonical, quyền/nhóm/crop review và membership đủ điều kiện; không phải hết ảnh nguồn SCB. 67 mẫu review-only chỉ là hàng đợi hiện tại, không phải trần lượng dữ liệu có thể tuyển từ archive.

## Đề xuất bước kế tiếp có thể nghiệm thu

1. **Chuẩn bị đợt SCB rộng hơn theo coverage.** Tự động hash/gom trùng, đề xuất nhóm gần trùng/cảnh bằng công cụ hiện có; đối chiếu nhóm val/test v4–v5 để khóa các ảnh có liên hệ. Chọn mẫu đa dạng scene/góc/kích thước/tư thế từ Head và HRW, không chỉ lấy ảnh liên tiếp. Tên/prefix chỉ là manh mối, không tự thành session ID.
2. **Tạo nhãn/crop draft tự động rồi review theo batch.** Dùng bbox nguồn làm proposal và heuristics tìm ngữ cảnh; gán P/N/U theo hai target với evidence. AI chuẩn bị bảng và contact sheet; owner nghiệm thu high-level, không yêu cầu tự annotate lại toàn bộ. Pretrained model mới dùng hỗ trợ cần pin weights/license và approval thích hợp; chưa chọn trong báo cáo này.
3. **Tiếp nhận FPI có kiểm soát.** Xác minh payload/terms, đối chiếu vài mẫu raw với numeric CSV để giải polarity; kiểm cả phone-only/null, multi-person và table-phone. Dừng conversion liên quan nếu mapping chưa rõ. Giữ evaluation CSV/test nguồn riêng; không lấy chúng làm train hoặc tuning cho benchmark đó.
4. **Tạo coverage report trước quota/split mới.** Đếm P/N/U theo nguồn và nhóm độc lập, crop nhỏ/che/điện thoại của người bên cạnh/đọc viết/quay đầu. Cần cả phone-positive và phone-negative trong nguồn FPI, và bổ sung positive SCB nếu có bằng chứng; looking của FPI mặc định chưa biết, không gán âm theo nguồn. Chỉ sau thống kê mới đề xuất quota thực tế để owner chốt.
5. **Thiết kế version mới và đánh giá trước training.** V5 và test lịch sử giữ bất biến; draft grouped development split, holdout độc lập và tiêu chí acceptance cần quyết định riêng. Không tái sử dụng nhóm cũ làm holdout mới; không dùng holdout để chọn threshold/epoch.

FPI có thể mở rộng đáng kể nguồn phone, SCB có thể mở rộng đáng kể supervision looking và negative khó. Chưa có bằng chứng để dự đoán mức tăng accuracy/F1. Sau khi có dataset đủ coverage và protocol được duyệt, mới so frozen baseline/fine-tuning trên cùng dữ liệu để tách ảnh hưởng của training recipe.

## TBD và điều kiện chốt

| ID | Owner | Lý do / bằng chứng cần để chốt |
|---|---|---|
| TBD-FPI-POLARITY | Owner nghiệm thu, Codex chuẩn bị đối chiếu | Paper/code/CSV chưa đồng nhất; cần ảnh đúng version và mapping rõ, không tự đảo 0/1 |
| TBD-FPI-PAYLOAD | Owner + Codex | ZIP SHA/version, actual image/label inventory, group/near-duplicate và chất lượng crop |
| TBD-FPI-RIGHTS | Owner | Chốt phạm vi dùng nguồn mới dựa README/LICENSE/terms payload; không phủ nhận quyền SCB đã có |
| TBD-SCB-EXTRA | Owner + Codex | Nếu muốn phone/class lịch sử: cần archive + YAML/version tương ứng; hiện chưa xác minh được |
| TBD-EXPANSION-RELEASE | Owner | Nghiệm thu membership, nhãn, nhóm, split mới sau proposal coverage; báo cáo này chưa cấp approval |

## Kiểm tra và giới hạn bàn giao

Các số local dựa trên phép tính đã lưu, không dựa riêng vào README. [Verification](../../artifacts/reports/fpi-scb-research-20261007/verification.json) ghi kiểm hash/JSON/liên kết/repo/diff; không chạy lại training vì code production và config không đổi. Chưa có model inference hoặc tuning từ dữ liệu nghiên cứu. Không thay dataset accepted, nhãn, split, semantics hoặc architecture; không commit/push/upload media.
