# V7 — Quyền và attribution cho dữ liệu public bổ trợ

Ngày kiểm: 2026-10-08. Trạng thái **Draft, chờ owner nghiệm thu từng nguồn/ảnh và phạm vi dùng**. Owner đã cho phép nghiên cứu dữ liệu bổ trợ ngoài phòng thi; điều đó chưa tạo release v7 hoặc quyền training. Tài liệu này chỉ áp dụng COCO train2017 và Open Images train đã tuyển cho targeted expansion, không dùng các nguồn này thay holdout phòng thi độc lập.

## Những điều đã kiểm ở nhà cung cấp

| Thành phần | Điều khoản đã kiểm | Cách xử lý trong v7 |
|---|---|---|
| COCO annotation | Annotation và website của COCO dùng CC BY4.0; COCO không sở hữu bản quyền ảnh, người sử dụng chịu trách nhiệm với ảnh và bản sao. | License annotation không thay license ảnh. [Điều khoản COCO](https://raw.githubusercontent.com/cocodataset/cocodataset.github.io/master/dataset/termsofuse.htm). |
| Open Images | Google cấp annotation theo CC BY4.0; ảnh được liệt kê là CC BY2.0. Publisher không bảo đảm license từng ảnh và yêu cầu người dùng tự kiểm. | Metadata đủ để shortlist, chưa đủ để ghi `Accepted`. [Điều khoản Open Images V7](https://storage.googleapis.com/openimages/web/factsfigures_v7.html#licenses). |
| Ảnh CC BY2.0 | Khi phân phối/hiển thị, credit cần tên hoặc pseudonym tác giả và title nếu được cung cấp, URI liên quan và license; crop phải có ghi nhận sử dụng ảnh gốc. | Giữ tác giả, title, landing, URL license, các thông báo được cung cấp và ghi rõ crop/RGB/PNG. [Legal code CC BY2.0, mục4](https://creativecommons.org/licenses/by/2.0/legalcode.en). |
| Phạm vi quyền | CC không bảo đảm mọi quyền cần cho mục đích sử dụng; quyền riêng tư, hình ảnh cá nhân hoặc quyền tinh thần có thể vẫn liên quan. | Owner nghiệm thu use scope theo [doc21](../21-data-governance-privacy-and-security.md); không suy consent từ một dòng CC BY. [Deed CC BY2.0](https://creativecommons.org/licenses/by/2.0/). |

Không tự nâng license ảnh từ2.0 lên4.0. Cite paper/dataset và attribution từng ảnh là hai việc khác nhau. Không ghi COCO hoặc Google là tác giả ảnh khi metadata không nói vậy.

## Kiểm tự động được mà không cần credentials

COCO metadata train cung cấp `flickr_url`, image ID và license nhưng thiếu tên tác giả/title. Tên file static Flickr chứa photo ID; từ ID có thể dựng short URL rồi theo redirect tới trang ảnh. Cấu trúc source/photo/short URL được Flickr công bố, gồm thuật toán base58 của short URL. [Tài liệu URL Flickr](https://www.flickr.com/services/api/misc.urls.html), [hướng dẫn của admin Flickr API](https://www.flickr.com/groups/api/discuss/72157616713786392).

Probe thực tế từ môi trường local ngày 2026-10-08 xác nhận Flickr oEmbed công khai trả `author_name`, `title`, `web_page`, `license_url` và `license_id` cho ảnh truy cập được. Ví dụ COCO image451324 resolve đúng Flickr photo3668798024; Open Images02ec1f0836bd6d3c resolve đúng photo6435743685. Script chỉ nhận response có photo ID khớp; không dùng HTML embed/script hoặc tải ảnh từ Flickr. Đây là quan sát HTTP có receipt, không là cam kết endpoint luôn khả dụng.

`flickr.photos.getInfo` là hướng API khác: tài liệu nói không cần user authentication nhưng vẫn bắt buộc application API key. Task này không dùng endpoint đó, không xin key, đăng nhập hoặc tìm credentials. [Tài liệu getInfo](https://www.flickr.com/services/api/flickr.photos.getInfo.html).

Open Images đã có `Author`, `AuthorProfileURL`, `Title`, `OriginalLandingURL` và `License` trong snapshot image information. Script giữ metadata này và so với oEmbed hiện tại; không dùng thiếu object annotation để suy label negative. Author/title là credit người tạo ảnh, không là nhãn hay định danh người đang xuất hiện trong crop.

## Công cụ và bằng chứng có thể nghiệm thu

[Công cụ canonical public_attribution_audit.py](../../src/ai_exam_monitoring/data/public_attribution_audit.py) chỉ đọc candidate Draft trong `data/interim`, kiểm COCO train metadata SHA, và ghi **thư mục version mới** dưới `outputs`. Không đọc/decode media release, val/test hoặc thay candidate/label/split. Không tạo canonical attribution hay owner approval. Bản helper ở `outputs` là lịch sử exploration, không phải entry point để tiếp tục task.

Mỗi dòng `attribution.jsonl` gồm candidate/screening/source ID, source/crop SHA, creator/title/landing/license nếu có, trạng thái kiểm từng ảnh, thiếu trường, blocker và changes notice gắn đúng XYXY. `flickr-observations.json` lưu trường metadata cần dùng, UTC, HTTP status, URL resolve và hash response đã quan sát. Receipt không lưu toàn HTML trang ảnh hoặc toàn JSON oEmbed; hash response được tính lúc truy vấn. Cache receipt dùng lại phải pin SHA và khớp photo ID. Output có `training_eligible:false`, `rights_status:pending_individual_attribution_and_owner_review` cho tất cả record.

Lệnh đã chạy cho trang review R7 có attribution, dùng receipt đã pin và không truy vấn lại mạng:

```powershell
$env:PYTHONPATH='src'
.venv/Scripts/python.exe -m ai_exam_monitoring.data.public_attribution_audit --candidates data/interim/pilot-b/v7-targeted-review-20261008-r7/candidates.jsonl --output outputs/v7-public-attribution-r7-review-20261009 --coco-metadata data/raw/coco/coco-2017-metadata-20261008-r2/annotations_trainval2017.zip --coco-metadata-sha256 113a836d90195ee1f884e704da6304dfaaecff1f023f49b6ca93c4aaae470268 --receipt-cache outputs/v7-public-attribution-r7-audit-20261009/flickr-observations.json --receipt-cache-sha256 1abaf5a9d20ec901e193cdf40db83f11bdf2e93847081a25f0ec07eef6f63eb3
```

Output trên đã tồn tại, không chạy lại để ghi đè. Với candidate/version mới, `--verify-public` cho phép kiểm metadata mạng; nếu không có receipt phù hợp và bỏ cờ này, các ảnh chưa kiểm vẫn có blocker. `--max-network-images` chỉ dành cho probe hữu hạn, không được gọi probe là kiểm đầy đủ. HTTP trong metadata Flickr chỉ được chuẩn hóa sang HTTPS, không thực hiện request HTTP. Landing ngoài whitelist hoặc khác photo ID bị chặn theo record, không làm toàn batch mất kết quả.

## Kết quả cuối R7, 2026-10-09

[Gói targeted](../../artifacts/reports/pilot-b-v7-targeted-20261008/README.md) có 131 crop public từ 121 Flickr photo ID: 39 COCO và 92 Open Images. Cả 131 có creator/title/landing/license kiểm được và license quan sát khớp snapshot CC BY2.0; 0 blocker trong primary cuối. [Ledger](../../artifacts/reports/pilot-b-v7-targeted-20261008/public-attribution-r7.jsonl), [receipt](../../artifacts/reports/pilot-b-v7-targeted-20261008/public-metadata-receipt-r7.json), [summary](../../artifacts/reports/pilot-b-v7-targeted-20261008/public-attribution-summary-r7.json), [review có credit từng ảnh](../../outputs/v7-public-attribution-r7-review-20261009/review-index.html).

34 ảnh nguồn khác còn blocker nằm ngoài primary, giữ trong [quarantine](../../artifacts/reports/pilot-b-v7-targeted-20261008/public-rights-quarantine.json). Đây là số ảnh nguồn, không phải số crop accepted hoặc số quyết định owner Reject. Đủ metadata không tạo approval quyền/notices/membership. Phạm vi nghiên cứu public bổ trợ ngoài phòng thi đã được owner chấp thuận; không yêu cầu xác nhận lại phạm vi đó. Use scope cho release/training và notices được nghiệm thu cùng package cụ thể.

## Kết quả kiểm R3 trước final selection

Snapshot này join [candidate R3](../../data/interim/pilot-b/v7-targeted-review-20261008-r3/candidates.jsonl), SHA `481bd377e7fcff640e05eae886c9dc202db64c7fa5258095ff32af19b29c44e5`. Có89crop public:60COCO và29Open Images, tương ứng86Flickr photo ID. Đã thử toàn86ID:69đọc được metadata public,17chưa kiểm được.70crop có đủ các trường attribution chính và license hiện tại khớp metadata; **70không là số đã được owner duyệt**.19crop có blocker,14crop thiếu creator/title. [Summary](../../outputs/v7-public-attribution-r3-audit-20261008/summary.json), [ledger attribution](../../outputs/v7-public-attribution-r3-audit-20261008/attribution.jsonl).

| Crop R3 | Bằng chứng hiện tại | Xử lý Draft đề xuất |
|---|---|---|
| A021, C098 | Redirect yêu cầu login; script dừng trước identity/login. | Giữ riêng review quyền; không dùng credentials để tiếp tục. |
| A033, A039, A041, A020, A045, A048, C096, C101, D032, D037, D040, D041 | Short URL trả `/photos///`; không có landing đúng ID hoặc creator/title có thể kiểm. | Quarantine quyền; chưa đủ bằng chứng để training. HTTP200 này không là PASS. |
| B072 | Landing HTTP403. | Quyền từng ảnh chưa kiểm được. |
| C112, C113 | Landing HTTP404. | Quyền từng ảnh chưa kiểm được; metadata tác giả có sẵn không thay receipt license. |
| A044 | COCO metadata CC BY2.0; Flickr hiện trả CC0. | Owner giải quyết evidence/license scope trước nhận; không tự đổi config license. |
| B075 | Open Images metadata CC BY2.0; Flickr hiện trả Public Domain Mark. | Owner giải quyết evidence/license scope; Public Domain Mark không được ghi thành CC BY2.0. |

Các ID trên viết tắt `V7-` và thuộc R3; R4 có thể loại/sửa/giữ candidate khác. Quarantine quyền không tự sửa nhãn P/N/U hoặc nhóm. Nhãn tốt và crop đúng vẫn có thể chưa đủ quyền. License hiện tại thay đổi không tự chứng minh quyền lịch sử đã mất: CC BY2.0 quy định quyền đã cấp tiếp tục nếu tuân thủ; record khác license phải giữ cả snapshot cũ/mới để owner giải quyết, không tự kết luận. [Legal code CC BY2.0, mục7](https://creativecommons.org/licenses/by/2.0/legalcode.en).

## Ma trận owner review cho package cuối

| Gate | Có thể tự động chuẩn bị | Điều kiện owner chốt |
|---|---|---|
| Từng ảnh và attribution | Landing đúng photo ID, tác giả/title nếu cung cấp, license URL và receipt; thiếu trường được liệt kê rõ. | Accept/reject nhóm record đủ bằng chứng; record thiếu/login/403/404/license khác được giữ riêng hoặc bổ sung evidence hợp lệ. |
| Notice và crop | Changes notice theo XYXY/source SHA; credit không ngụ ý tác giả bảo trợ project. | Xác nhận các copyright/license/disclaimer notice được cung cấp trên nguồn đã được giữ khi áp dụng; oEmbed không kiểm đầy đủ phần này. |
| Use scope public bổ trợ | Domain ngoài phòng thi rõ, lưu local, không upload media. | Xác nhận phạm vi nghiên cứu classifier crop theo doc21; quyền ảnh không tự cho phép demo giám sát/kỷ luật người thật. |
| Membership v7 | Candidate/label/pair/group và rights ledger có pins, blocker riêng; có thể nghiệm thu theo batch. | Quyết định membership/group/split riêng, có owner review ghi lại theo [AGENTS.md](../../AGENTS.md). |

Không yêu cầu owner gõ tay credit từng ảnh: script đã điền trường có bằng chứng và chỉ tách ngoại lệ. TBD-V7-PUBLIC-RIGHTS có owner là chủ repository; đóng theo ledger final/pins và quyết định use scope được ghi lại. Cho đến đó không ghi nguồn public là Accepted hoặc tính crop có blocker thành training-ready.

Kiểm công cụ canonical hiện tại: Ruff/mypy PASS và 11 tests PASS, gồm identity/HTTPS/domain/port, landing không hợp lệ theo record, train-only, unknown credit, license conflict, receipt cache scope, candidate eligibility trước mutation và HTML credit được escape. Toàn suite classifier của gói cuối có 203 tests PASS. Đây là kiểm công cụ, không thay owner review quyền/nhãn hoặc chứng minh group independence.
