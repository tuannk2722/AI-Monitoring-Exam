# Snapshot audit nhãn R7 và review cuối R4

**Snapshot R4 đã được thay thế cho nghiệm thu:** dùng [báo cáo cuối](README.md), review R5 và `annotation-r4/`. Giữ số đo R4 bên dưới để truy vết.

Trạng thái: Draft, không thay đổi R7, không release hoặc train. Snapshot này dùng số đo đã được root xác minh; bảng chi tiết và graph bổ sung được tạo từ CLI audit khi metadata đọc được.

| Phạm vi | R7 | Review cuối R4 |
|---|---:|---:|
| Crop | 274 | 274 |
| Fully-known, cả hai target P/N | 73 | 70 |
| P/P | 10 | 10 |
| P/N | 3 | 3 |
| N/N | 51 | 49 |
| N/P | 9 | 8 |
| U/U | Chưa đo trong snapshot | 15 |

R4 có phone 95P/63N/116U; looking 66P/105N/103U. Đây là proposed labels, không phải canonical labels đã duyệt. Upper bound membership có ít nhất một target known là 259, fully-known là 70; owner còn phải quyết định nhãn, group, quyền, membership và split.

Bucket A R7 có 57 candidate: 32 phone P/25 phone N. Trong 12 crop classroom/exam-context, có 6P/6N. 45 crop còn lại là auxiliary ngoài exam; không được cộng để chứng minh shortage classroom đã đóng.

R7 có 162 pair links: 6 same-image, 1 same-scene, 155 source-context. Root kiểm R4 được 141 pair còn đúng polarity target, 21 pair invalid sau sửa đề xuất nhãn. Số pair đúng polarity không chứng minh matched camera/session. Phải lọc target và kiểm lại anchor/ownership trước dùng pair.

242 ảnh nguồn và 232 visual family hints không phải nhóm độc lập. Registered group, camera và room không được suy từ source hay family hints. Không tự tạo official split từ các đếm này.

Pin final R4: `outputs/v7-owner-review-r4-20261009/review-proposals.jsonl`, SHA256 `5485145d85fcacc6488fc3eaedce14053bba0531db97e220e5aad06c2063ee3a`.

Một cơ hội R8 cần review: ảnh nguồn của V7-D-026 có teacher sở hữu mobile và anchor nữ viết bài. Có thể đề xuất thêm teacher P/U để tạo phone P/N cùng ảnh với anchor nữ N/N. Đây là đề xuất crop mới, chưa materialize hoặc owner approve, và diversity gain theo nhóm độc lập bằng 0.
