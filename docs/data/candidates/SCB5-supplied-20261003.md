# Dataset Candidate — DS-SCB5-SUPPLIED-20261003

## Thông tin nhận dạng/provenance

- Tên: ba archive SCB do owner cung cấp; không phải toàn bộ SCB-Dataset. Maintainer Hugging Face: `wintonYF`; upstream liên kết: [Whiffe/SCB-dataset](https://github.com/Whiffe/SCB-dataset).
- URL đúng nguồn: [Hugging Face SCB-Dataset](https://huggingface.co/datasets/wintonYF/SCB-Dataset/tree/main). Ngày truy cập: **2026-10-03**. HEAD hiển thị `0fdc46fe393d251320def8c6d10cbc95d89f7da6`; tool không mở được trang pin commit, do đó không khẳng định đã tải snapshot commit. Phiên bản audit được định danh chính xác bằng **SHA-256 ZIP local khớp blob remote**.
- Thư mục archive gốc: `C:/Users/OS/Downloads/`; không sửa ZIP, không ghi vào `data/raw`. Bản giải nén chỉ phục vụ audit tại `outputs/scb-audit-20261003-v1/extracted/`.

| Archive chính xác | Bytes | SHA-256 |
|---|---:|---|
| SCB5-Discuss-2024-9-17.zip | 121619946 | `63aa029d04f8e9d5027cc2491aeca10785678750bdae4351835bfceaab95187f` |
| SCB5-Handrise-Read-write-2024-9-17.zip | 779384408 | `46619af0c0dea011b09b8d50f4c0578420b881b5154e9d11f0447760193a208d` |
| SCB_BowTurnHead_20250509.zip | 315224668 | `a0fdd6637fb286cbc5d3de83c09f4143686eab0da4d92e4d8007b6b14b3ca828` |

- Head ZIP có thư mục bên trong `SCB5-Turn-Bow-Head-2024-9-17`; giữ nguyên khác biệt tên/date, không đổi nó thành release 2024.
- Citation: Fan Yang, *SCB-Dataset: A Dataset for Detecting Student and Teacher Classroom Behavior*, [arXiv:2304.02488v7](https://arxiv.org/abs/2304.02488v7), 2025. Không coi mọi số liệu của bài báo là số liệu của ba ZIP này.
- Tái tạo: dùng đúng ZIP trên, kiểm hash; đọc [báo cáo và lệnh](SCB5-supplied-20261003-audit.md). URL từng blob/YAML, hash và môi trường được lưu trong [provenance](../../../artifacts/reports/scb-20261003/provenance.json) và [web-evidence](../../../artifacts/reports/scb-20261003/web-evidence.json). Không tải thêm nguồn cùng tên.

## Cập nhật owner — 2026-10-04

Các quyết định này cập nhật TBD của bản audit gốc bên dưới; giữ nguyên số liệu lịch sử.

- **Discuss: LOẠI BỎ khỏi baseline dự kiến**, giữ nguyên raw/archive/bằng chứng.
- **Quyền và metadata: owner xác nhận đã phê duyệt, yêu cầu tiếp tục.** Không hỏi lại phê duyệt này. Căn cứ là xác nhận owner; tài liệu gốc chưa đính kèm, không tuyên bố đã đọc văn bản tác giả.
- Bảng video/session từng file vẫn cần giá trị thực tế để dựng grouped split; không tự suy group_id từ việc phê duyệt.
- BowHead: đề xuất tín hiệu phụ cần kiểm chứng; owner chưa chốt thêm nhãn/rule. Cúi đầu + tay không thấy không chứng minh cheating, thiếu tín hiệu không chứng minh normal.
- Phone_use: owner chốt [audit Roboflow v1 tạm](Roboflow-phone-use-20261004.md) trong lúc chờ access nguồn khác.
- Sign-off hiện chỉ bao phủ các quyết định trên; QA/mapping/split/A-B và dataset acceptance chưa đóng.

## Quyền/Privacy — ghi nhận lịch sử tại audit 2026-10-03

- ZIP không kèm license/terms/consent. Hugging Face card không đủ thông tin về các quyền này.
- [README upstream, mục 4–5](https://github.com/Whiffe/SCB-dataset#4-commercial-use-restrictions) nêu mục đích nghiên cứu/học tập/phi thương mại và hạn chế thương mại; đồng thời bảo lưu quyền sao chép/phân phối/sửa đổi. Đây là bằng chứng điều kiện sử dụng cần review, **không phải kết luận đã được phép mọi hoạt động training/derivative**.
- Training/tạo bản phái sinh/phân phối lại, phân phối model weights và phạm vi attribution: **TBD-SCB-RIGHTS**, owner: chủ repository; chốt khi có điều khoản/cho phép áp dụng đúng ba ZIP. User cho biết có tài liệu và sẽ cung cấp sau; chưa nhận tài liệu để đối chiếu.
- Media có người thật, khuôn mặt và bối cảnh lớp học; chưa có evidence consent/provenance theo từng asset. Chỉ tạo file audit/overlay cục bộ trong thư mục ignored; không upload ảnh/weights hay xuất bản dataset.
- Attribution tối thiểu cần review theo hướng dẫn citation của upstream; không dùng license của bài báo arXiv như license dữ liệu.

## Nội dung

Xem [báo cáo cấu trúc, lớp, bbox, duplicate và nhóm](SCB5-supplied-20261003-audit.md). Audit máy bao phủ toàn bộ ba ZIP; review trực quan chỉ bao phủ tập mẫu có chủ đích được liệt kê, không chứng minh tỷ lệ lỗi toàn dataset. Không khảo sát phần Teacher/LLM/YOLO training artifacts trên remote.

- Định dạng: JPG + YOLO 5 cột normalized; `images/{train,val}` và `labels/{train,val}`. Không có test folder hay source manifest trong ba ZIP.
- ID có namespace riêng mỗi archive: không thể gộp trực tiếp ID 0 giữa Discuss, HRW và Head.
- Bảng ID/tên được chép tường minh theo thứ tự ID zero-based trong YAML YOLO chính nguồn, không lấy tên từ ảnh/tên ZIP. Các YAML này nằm ngoài ZIP và có URL ghi lại. Không đưa mapping này vào canonical config.
- Nhóm video/session/person/room: chưa có manifest liên kết từng file. Tên dạng số hoặc prefix_suffix chỉ là manh mối để hỏi tác giả; **không gán group_id**. Thông tin video-frame và split độc lập trong bài báo không thay thế metadata từng mẫu.
- Domain: ảnh lớp học, tương tác nhóm, góc nhìn/độ phân giải đa dạng; không đồng nhất với một camera phòng thi. Chất lượng/thiếu nhãn và leakage phải xử lý trước khi chọn nguồn chính thức.

## Canonical mapping (đề xuất, chưa phê duyệt)

| Phần / ID / tên nguồn | Ý nghĩa quan sát được hoặc điểm cần xác nhận | Đề xuất cho taxonomy hiện tại |
|---|---|---|
| Discuss / 0 / `discuss` | Mẫu D-R01–03 có box bao nhóm nhiều người quanh bàn; có thể gồm người hướng dẫn. Ảnh tĩnh không xác nhận lời nói/ý định. | Loại khỏi mapping trực tiếp theo người; không đổi thành `looking_around` hay `normal`. Cần annotation unit riêng hoặc loại nguồn này khỏi baseline đầu. |
| HRW / 0 / `hand-raising` | H-P01 có tay giơ cao và tay thấp gần thân; H-R03 có actor đứng trước lớp. Cần xác nhận tiêu chí/actor của nguồn. | Ngoài ba nhãn candidate hiện tại; không tự map `normal`. Có thể giữ như dữ liệu ngoài target chỉ sau review tính đầy đủ của nhãn. |
| HRW / 1 / `read` | H-P02/H-R05 thấy người nhìn xuống sách/bàn; khó phân biệt chỉ từ tư thế với viết. Cần kiểm tra tính đầy đủ của nhãn. | Cần kiểm tra thêm; không map tự động `normal`. |
| HRW / 2 / `write` | H-R09 thấy tay cầm bút trên giấy; toàn cảnh H-R07 nhỏ/che khuất hơn. Không đánh đồng mọi cúi đầu với viết. | Cần kiểm tra thêm; không map tự động `normal`. |
| Head / 0 / `BowHead` | T-R03 cúi đầu trong khi đang viết; BowHead là tư thế có thể đồng thời với hoạt động khác. | Không map `phone_use` hoặc `normal`; cân nhắc ngoài target/loại khỏi mapping trực tiếp. |
| Head / 1 / `TurnHead` | T-P01/P02 có đầu xoay khi giơ tay; chưa đủ duration/hướng nhìn/ngữ cảnh để xác nhận looking_around của phòng thi. | Candidate cần review cho `looking_around`, không phải alias được accepted. |

Không có class nguồn `phone_use` trong sáu ID/tên đã xác minh; điều đó không chứng minh không có điện thoại hoặc hành vi chưa annotate trong ảnh. Không có class `normal` được nguồn định nghĩa. Bảng này là đề xuất bằng văn bản, không phải converter/mapping thực thi.

## Quyết định

- **Status: CANDIDATE — chưa chọn làm dataset training đầu tiên.** Có ích cho nghiên cứu nguồn và review annotation; chưa đủ cho toàn bộ taxonomy của dự án.
- **A/B: chưa đủ bằng chứng để chốt.** A có lợi thế tái sử dụng bbox nguồn sau QA; nhưng group box Discuss không phù hợp person-behavior. B cần person/crop annotation nhất quán và nhãn đồng thời/negative được review, hiện chưa có bằng chứng đầy đủ. Có thể ưu tiên thiết kế kiểm chứng A trên phần Head đã review sau khi đóng quyền/split/unit, nhưng không coi đó là lựa chọn kiến trúc hoặc cho phép train.
- Owner/người chốt: chủ repository. Hỗ trợ audit/review: Codex. Ngày: 2026-10-03. Chưa có human sign-off.

## Việc cần hoàn thành để qua P1

1. **TBD-SCB-RIGHTS — owner:** cung cấp terms/trao đổi quyền dùng đúng release, quyền derivative/weights/redistribution và evidence privacy; chốt trước sử dụng chính thức.
2. **TBD-SCB-GROUP — owner + nguồn cung cấp:** lấy video/session/room mapping và cách trích frame/chia split; xử lý duplicate và đánh giá gần trùng. Không chọn prefix làm group khi chưa xác minh.
3. **TBD-SCB-QA — owner:** review các ảnh/câu hỏi trong gói mẫu; quyết định quy tắc bbox vượt biên, box nhóm/người và thiếu nhãn. Nếu cần sửa, tạo version bằng code + provenance; không sửa raw hay nới validator để pass.
4. **TBD-LABEL-01 / TBD-ANN-01 — owner:** xác nhận định nghĩa `normal`, `looking_around`, annotation unit, co-occurrence/ignore. Không mặc định read/write/BowHead là normal.
5. **TBD-SCB-COVERAGE — owner:** quyết định cách có bằng chứng cho `phone_use` và các negative đã review. Không tự mở rộng/thu hẹp taxonomy trong audit này.
6. **TBD-TASK-01 — owner:** thiết kế subset và tiêu chí A/B sau khi license, mapping, unit, grouped split được chốt; dùng dữ liệu được phép, không tune trên test. Cập nhật ADR-002/003 và canonical docs/config chỉ sau owner phê duyệt.

P1 chưa đạt exit gate; P0 DVC push/pull cũng không được coi hoàn tất bởi audit này.
