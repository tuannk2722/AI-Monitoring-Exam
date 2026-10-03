# SCB supplied — báo cáo audit 2026-10-03

**Kết luận: chưa chọn làm dataset training đầu tiên; giữ CANDIDATE.** Ba ZIP có dữ liệu hữu ích để nghiên cứu annotation, nhưng chưa đủ quyền sử dụng/metadata nhóm, có lỗi bbox, trùng chéo split và thiếu lớp phone_use. Không build, train, sửa raw, đổi mapping hoặc đánh dấu accepted.

## Phạm vi và nhận dạng

Audit máy đọc toàn bộ **10.138 JPG + 10.138 TXT** trong đúng ba ZIP owner cung cấp, kiểm CRC khi giải nén và SHA-256 archive khớp blob Hugging Face. Chỉ giải nén vào thư mục output mới, không sửa archive. Không kiểm tra phần Teacher/LLM/YOLO.zip còn lại. Tên/hash/URL chính xác nằm trong [candidate card](SCB5-supplied-20261003.md) và [provenance](../../../artifacts/reports/scb-20261003/provenance.json).

Công cụ chuẩn: `ai_exam_monitoring.data.audit.audit_dataset` và `data.overlay.export_overlays` tại commit `6203be99fce8f9036bcbf2218d8f04cc2ede2ed1`, Python 3.11.9. Script phiên audit [run_audit.py](../../../outputs/scb-audit-20261003-v1/run_audit.py) gọi công cụ hiện có và bổ sung hashing chéo archive; [review_samples.py](../../../outputs/scb-audit-20261003-v1/review_samples.py) chọn mẫu và đo lỗi dòng nhãn. Không thay code production hoặc threshold.

## Cấu trúc và chất lượng tự động

| Phần | Train ảnh | Val ảnh | Tổng ảnh / label | File label bị flag | Dòng bbox lỗi | Cặp có toàn bộ label hợp lệ |
|---|---:|---:|---:|---:|---:|---:|
| discuss | 605 | 259 | 864 / 864 | 32 (3.70%) | 37 | 832 |
| hrw | 5193 | 1671 | 6864 / 6864 | 412 (6.00%) | 466 | 6452 |
| head | 1905 | 505 | 2410 / 2410 | 102 (4.23%) | 122 | 2308 |

Tổng: **546/10.138 file label (5,39%) bị validator flag**, gồm 625 dòng bbox lỗi. Không có missing/orphan/ambiguous pair, ảnh không decode được, label rỗng hay ID ngoài tập tên nguồn. Không thấy NaN/Infinity trong lần quét này. Pass cấu trúc không chứng minh nhãn đúng hoặc đầy đủ.

Đều là `images/{train,val}` ↔ `labels/{train,val}`, không có test hoặc metadata manifest trong ZIP. Root phần Head có thêm thư mục lồng `SCB5-Turn-Bow-Head-2024-9-17`. Tất cả file là JPG/TXT; không có bảng video/session, license hoặc guideline kèm ZIP.

### Chi tiết cảnh báo bbox

| Phần | Mức vượt biên normalized lớn nhất | Nhận xét |
|---|---:|---|
| discuss | 0.00347222222222 | 37 dòng vượt biên trong 32 file |
| hrw | 0.265626436782 | 466 dòng lỗi; có 2 bbox width/height không dương, 2 dòng center ngoài [0,1], còn lại bounds |
| head | 0.0138888888889 | 122 dòng vượt biên trong 102 file |

Có một số cảnh báo float cực nhỏ (ví dụ Head: 2,22e-16); có lỗi HRW vượt tới 0,265626 và bbox suy biến nên không thể gom mọi cảnh báo thành rounding. Thống kê phụ không thay đổi rule validation: không clip/sửa tọa độ, không đổi epsilon. Ảnh warning hiển thị box gốc; phần vượt ngoài canvas không có pixel để vẽ. Danh sách mọi dòng lỗi và raw line được lưu local `*-invalid-rows.json`.

## Phân bố lớp

ID **riêng từng phần**, lấy từ YAML nguồn được ghi URL trong [web-evidence](../../../artifacts/reports/scb-20261003/web-evidence.json). Đây là transcription thứ tự `names` theo YOLO zero-based, không phải mapping canonical. Raw là số dòng có class token, bao gồm dòng/file bị lỗi; strict là annotations từ **file hoàn toàn hợp lệ** theo công cụ audit.

| Phần / ID / tên | Raw train | Raw val | Raw tổng | Strict tổng |
|---|---:|---:|---:|---:|
| discuss / 0 / discuss | 3607 | 1785 | 5392 | 5181 |
| hrw / 0 / hand-raising | 10538 | 2915 | 13453 | 12611 |
| hrw / 1 / read | 17539 | 6539 | 24078 | 21543 |
| hrw / 2 / write | 6447 | 3394 | 9841 | 8785 |
| head / 0 / BowHead | 4422 | 540 | 4962 | 4716 |
| head / 1 / TurnHead | 7943 | 3213 | 11156 | 10669 |

**68.882 raw rows**, **63.505 annotations strict**. Chênh lệch 5.377 không phải 5.377 bbox đều sai: tool loại cả file khi một dòng lỗi; quét phụ tìm 625 dòng lỗi và 68.257 dòng geometry hợp lệ, chưa có quyết định cứu/loại từng dòng. Read nhiều hơn write/hand-raising; không suy ra mức đủ dữ liệu/model quality từ số lượng.

### Kích thước ảnh và bbox

| Phần | Range width ảnh | Range height ảnh | Width bbox pixel min / mean / max | Height bbox pixel min / mean / max |
|---|---|---|---|---|
| discuss | 576–3645 | 332–1908 | 42.43 / 226.96 / 2439.11 | 31.34 / 169.28 / 1297.50 |
| hrw | 373–3775 | 246–1974 | 17.33 / 155.12 / 2865.30 | 20.72 / 192.51 / 1608.50 |
| head | 373–2880 | 376–1553 | 15.11 / 98.70 / 960.55 | 15.00 / 121.69 / 985.76 |

Các cực trị width/height có thể thuộc các ảnh/box khác nhau; không ghép thành một resolution hoặc box giả. Bbox thống kê trên cặp strict hợp lệ. Quantile p10/p50/p90 theo class trên train nằm trong `*-diagnostics.json`; chưa đặt ngưỡng “quá nhỏ”. Head có box hẹp khoảng 15 pixel, cần xem độ rõ trước quyết định annotation/ignore.

## Duplicate và nhóm video/session

- SHA-256 toàn bộ ảnh của ba phần: **8.116 file bytes duy nhất**, **1.892 nhóm trùng**, **2.022 bản dư**.
- **1.891 nhóm trùng giữa archive**; **961 nhóm có cả train và val**. Đây là exact duplicate overlap xác nhận trên byte, không phải suy đoán gần trùng.
- Trong riêng từng archive: Discuss 0 nhóm; Head 0; HRW có một nhóm hai ảnh đều thuộc val (`3001001.jpg`, `3001049.jpg`). Không thấy exact duplicate chéo train/val nội bộ từng archive; điều này không chứng minh split độc lập theo video.
- Ví dụ xác minh: `images/val/0001081.jpg` của HRW có cùng hash với `images/train/0001081.jpg` của Head; overlay lần lượt có 3 và 4 annotations, do hai phần annotate các lớp khác nhau. [Bằng chứng hash/member](../../../artifacts/reports/scb-20261003/duplicate-review-example.json).
- Danh sách đầy đủ nhóm/member: [cross-duplicates.json](../../../outputs/scb-audit-20261003-v1/cross-duplicates.json). **Chưa chạy thuật toán gần trùng**. Ảnh nối tiếp trong mẫu Head-P01/P02 trông cùng cảnh nhưng không được dùng để gán video_id hay kết luận số nhóm.

Bài báo nguồn mô tả ảnh trích từ video, một số lớp được annotate có chọn lọc và các phần có thể chia split riêng; xem [§3.1, §3.4](https://arxiv.org/html/2304.02488v7). Đây chỉ là mô tả upstream; tỷ lệ quan sát của từng ZIP ở bảng trên mới là số liệu phiên này. Không có mapping frame → video/session/room trong ZIP. Tên số/prefix chỉ là manh mối, chưa suy ra group_id. Metadata bổ sung owner sẽ cung cấp sau.

**Hệ quả:** không concat ba phần rồi giữ split cũ; không coi người không có box là negative; không tự hợp nhất annotations khác unit. Cần policy dedup/merge-labels có review và grouped split version mới khi đủ provenance, nhưng audit này chưa làm mutation đó.

## Xem ảnh và giới hạn ngữ nghĩa

Đã xem 18 mẫu theo 6 class qua contact sheets, 4 preview đầy đủ, 6 warning overlays và 2 overlay của ví dụ duplicate. Một số nguồn ảnh có thể trùng nhau; đây là **30 lượt ảnh render**, không phải 30 mẫu ngẫu nhiên độc lập. Không dùng tập này để ước lượng phần trăm sai semantics. Các mẫu class/preview lấy train; ví dụ duplicate cố ý chứa một val để kiểm tra cấu trúc/leakage, không phục vụ tuning.

- Discuss: nhiều box nhóm, không phù hợp gán thẳng cho person track.
- HRW: có bối cảnh tay giơ cao/thấp, actor đứng trước lớp, nhìn xuống và viết; bbox có lúc toàn thân, có lúc thân trên. Có người ngoài box trông vẫn đang làm việc; cần xác minh exhaustive annotation, không tự kết luận tất cả là lỗi.
- Head: thấy vùng đầu/thân trên khác kích thước, có người vừa giơ tay vừa quay đầu; ảnh tĩnh không cung cấp duration hoặc ý định. BowHead và write có thể đồng thời; không tự gán normal.
- Ảnh từ góc trước/sau, toàn cảnh/cận cảnh, watermark/player UI và độ nét khác nhau; có domain gap so với một camera phòng thi.

Danh sách câu hỏi và link mẫu: [review checklist](SCB5-supplied-20261003-review.md). Bảng source → ý nghĩa → đề xuất canonical và quyết định A/B: [candidate card](SCB5-supplied-20261003.md#canonical-mapping-đề-xuất-chưa-phê-duyệt). **Chưa đủ bằng chứng chốt A/B hoặc accepted**.

## Tái tạo và bằng chứng kiểm tra

Sau khi giải nén đúng root theo provenance, mỗi phần chạy cùng lệnh (thay SOURCE_ROOT và SOURCE_ID, dùng output mới):

```powershell
 .venv/Scripts/python.exe -m ai_exam_monitoring.data.audit --dataset SOURCE_ROOT --images images --labels labels --source-names artifacts/reports/scb-20261003/SOURCE_ID-source-names.json --output outputs/NEW-AUDIT.json
```

Phiên này gọi cùng API để không bỏ qua lỗi mà vẫn hoàn tất cả ba phần. Mỗi report `has_errors=true` do bbox; CLI tương đương sẽ trả 1. Script orchestration kết thúc exit 0 nghĩa là **audit đã chạy hết**, không phải dataset pass. `run_audit.py` kiểm hash và từ chối thư mục extract đã tồn tại; để tái tạo dùng version output mới, không ghi đè. `review_samples.py` copy nguyên bytes một subset có source manifest rồi gọi overlay; warning renderer chỉ minh họa lỗi gốc. Các script local được giữ cùng gói output, không thêm production API.

Đã chạy lại **34 tests PASS**, Ruff PASS, compileall PASS và repository checker `--require-git` PASS. Report/data validation riêng vẫn FAIL geometry như trên; code tests pass không đóng data gate. Không chạy DVC/build/train.

Artifact phân tách: summary/provenance/selection JSON nhỏ ở `artifacts/reports/scb-20261003/`; full reports, giải nén và PNG ở `outputs/scb-audit-20261003-v1/` (Git ignored). Bản quyền/nhóm chưa xác minh; không có media thật được commit/upload.

## P1 còn thiếu

Xem danh sách TBD có owner/điều kiện chốt trong [candidate card](SCB5-supplied-20261003.md#việc-cần-hoàn-thành-để-qua-p1): rights/privacy, group mapping và near-duplicate, QA/unit, canonical semantics/coverage phone_use, rồi feasibility A/B và owner sign-off. P0 chưa được đóng thay bằng kết quả này.
