# Classroom-monitoring v2 — báo cáo nghiệm thu candidate

Ngày 2026-10-07. **Đã hoàn tất tiếp nhận ZIP, audit kỹ thuật, review cảnh và đề xuất 24 crop/nhãn. Dừng trước staging theo yêu cầu owner.** Nhãn/group mới trong báo cáo là Draft, chưa phải quyết định owner.

## Kết luận đề xuất

Nguồn có ích để bổ sung phone positive ngoài SCB/RF hiện có, nhưng các ảnh có nền/cảnh rất giống nhau. Đề xuất giữ 24 crop để nhập staging review-only sau nghiệm thu; giữ unknown khi bằng chứng không rõ. Đề xuất gộp toàn bộ 150 ảnh nguồn vào một nhóm chống rò rỉ thận trọng, không dùng train/valid nguồn như hai nhóm độc lập. Chưa gán split project, chưa nghiệm thu release hoặc training.

Owner chỉ cần duyệt hoặc nêu ngoại lệ cho **24 candidate/crop/nhãn theo hash và đề xuất nhóm cảnh**. Không cần gửi thêm đường dẫn ZIP hoặc xác nhận quyền; đầu vào và quyền đã được cung cấp.

## Archive và audit

ZIP user cung cấp: `C:/Users/OS/Downloads/Classroom-monitoring-dataset.v2i.yolov8.zip`, 5.077.256 byte. Bản raw bất biến ở `data/raw/classroom-monitoring/v2/`; SHA-256 `59e4e301330d75dd77b2540722624c0104178e37ecae03a5d406738c6da9fb90`. Giải nén ở `data/interim/classroom-v2-20261007/extracted/`.

Metadata ZIP xác nhận project/workspace/version2 khớp [URL owner cung cấp](https://universe.roboflow.com/arijit-mukherjee-h4br2/classroom-monitoring-dataset/dataset/2). Web tool không mở được trang version; không tuyên bố đã xác minh nội dung trang live. README export ghi resize stretch 640×640, không augmentation; đã decode ảnh và kiểm resolution trong audit.

| Split nguồn | Ảnh | Bbox hợp lệ | Lỗi cấu trúc/ảnh/nhãn |
|---|---:|---:|---:|
| train | 120 | 600 | 0 |
| valid | 30 | 150 | 0 |
| Tổng | 150 | 750 | 0 |

Con số 810 trong cập nhật hội thoại ban đầu là lỗi cộng; inventory/nhãn xác minh tổng 750. `data.yaml` khai báo đường dẫn test nhưng ZIP không có thư mục test; không tạo tập test giả. Không thiếu label, không orphan hoặc cặp mơ hồ; không có ảnh trùng byte hoặc RGB pixel trong 150 ảnh. Đây là kết quả kỹ thuật, không chứng minh toàn 750 bbox đúng ngữ nghĩa.

| Class nguồn | Train | Valid | Tổng |
|---|---:|---:|---:|
| hand_raising | 15 | 3 | 18 |
| looking_forward | 210 | 54 | 264 |
| reading | 157 | 39 | 196 |
| sleeping | 56 | 16 | 72 |
| turn_around | 59 | 16 | 75 |
| using_phone | 65 | 8 | 73 |
| writing | 38 | 14 | 52 |

Bằng chứng: [summary](summary.json), [train audit](train-audit.json), [valid audit](valid-audit.json), [inventory150](images.json), [duplicate checks](duplicates.json).

## Crop và đề xuất target

Đã xem toàn 120 ảnh train, chọn thủ công 24 anchor ở 24 ảnh để bao phủ phone, hướng nhìn, đọc/viết, giơ tay, gục đầu và tình huống nhỏ/mơ hồ. Đây là batch review đại diện về tình huống nhìn thấy, không phải mẫu xác suất hay cam kết đủ dữ liệu train. Mỗi crop lấy bbox nguồn làm đề xuất vùng người/context, làm tròn ra ngoài tới pixel; đã review crop thực tế. Chưa chứng minh chất lượng detector cho toàn bộ nguồn.

[Candidate theo nguồn/dòng label/hash/box](candidates.json), [review theo từng crop](visual-review-proposals.json), [config pin](../../../configs/datasets/classroom_monitoring_v2_review.yaml).

| Target đề xuất /24 | Positive | Negative | Unknown |
|---|---:|---:|---:|
| phone_use | 6 | 10 | 8 |
| looking_around | 7 | 5 | 12 |

19 mẫu có ít nhất một target được đề xuất biết; 5 mẫu cả hai unknown. 5 mẫu được đề xuất normal qua hai target âm và context làm bài; 2 mẫu đồng thời phone/looking dương. Không coi 24 mẫu là 24 tình huống độc lập. Tất cả candidate canonical vẫn unknown/null/mask0 cho đến nghiệm thu.

- Phone dương: EXP-CM-001/002/003/004/007/017; có thiết bị thấy được gắn với người, không lấy tên class làm nhãn.
- EXP-CM-022/023 dù mang class using_phone vẫn đề xuất unknown do crop nhỏ/tối, chưa phân biệt chắc thiết bị.
- EXP-CM-010 giơ tay và EXP-CM-021 gục đầu không tự thành normal.
- EXP-CM-003/004 đề xuất đồng thời phone và looking dương.
- Crop không được upscale để tạo bằng chứng; sheet chỉ phục vụ xem, SHA/pixel kiểm trên PNG gốc.

Xem trực tiếp [crop sheet1](../../../data/interim/classroom-v2-20261007/review/crops-01.jpg), [sheet2](../../../data/interim/classroom-v2-20261007/review/crops-02.jpg), [sheet3](../../../data/interim/classroom-v2-20261007/review/crops-03.jpg). Toàn cảnh tại cùng thư mục: train-01…10 và valid-01…03. Media chỉ lưu cục bộ, không commit/upload.

## Cảnh và rò rỉ

Đã xem toàn 150 ảnh để audit cảnh: cùng phòng bậc thang, máy chiếu/dây/rèm/bàn; bố trí chỗ ngồi và tư thế lặp lại qua cả train và valid. Đề xuất [CM-V2-SCENE-01](scene-proposal.json) gộp cả 150 ảnh để chống rò rỉ. Đây là gộp thận trọng, không xác nhận tất cả thuộc một phiên có timestamp đã biết. Không suy danh tính hoặc session từ filename.

[Similarity triage](similarity-triage.json) có nearest cross-split cho mọi ảnh, khoảng cách dHash0–18. dHash0 không có nghĩa pixel trùng; không dùng khoảng cách làm threshold nghiệm thu. Valid nguồn chỉ xem để audit cảnh, không tuyển crop, không dùng metrics hoặc tuning; không gọi nó là holdout chưa nhìn.

Đối chiếu 150 SHA với 177 ảnh unique thuộc 112 record v4 và 72 candidate R2: không trùng byte. Top3 dHash neighbor được lưu; chưa có bằng chứng liên hệ cảnh với v4/R2, nhưng hash khác không chứng minh độc lập. Phạm vi so sánh là ledger/candidate hiện có, chưa phải toàn ảnh trong các archive SCB/RF chưa tuyển. Chỉ dùng fingerprint parent đã lưu, không mở ảnh test v4 hoặc đọc kết quả test để tuyển.

## Kiểm chứng và tái tạo

[Verification](verification.json) kiểm ZIP CRC/member hash, audit counts, source/label/crop hash, crop pixel/bounds/rounding, nhãn proposal và pin config, bảo toàn v4/R2. Công cụ canonical: `audit_dataset`, YOLO parser, `difference_hash`; không thay code nghiệp vụ hoặc cài model mới.

Tái tạo audit từ root repo bằng `.venv/Scripts/python.exe -m ai_exam_monitoring.data.audit --dataset data/interim/classroom-v2-20261007/extracted --images train/images --labels train/labels --source-names artifacts/reports/classroom-v2-20261007/source-names.json --output <đường-dẫn-report-mới>`; chạy tương tự cho valid. Selection thủ công được freeze theo file/dòng trong config; tái tạo crop bằng RGB crop theo context_xyxy trong candidates.json rồi so SHA. Review target là quyết định thị giác được ghi theo hash, không phải thuật toán source-class mapping.

Sau nghiệm thu báo cáo này mới nhập quyết định và tạo staging version mới; không yêu cầu review lại quyền. Release v5/split/E002 là các bước riêng.
