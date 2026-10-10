# Triage lineage local R3 — Draft, 2026-10-08

Đã đối chiếu metadata của 300 ảnh RF, 100 ảnh SCB, 248 crop R3 và manifest v6. Đã xem riêng một số ảnh nguồn **val** và **train** để xác minh các liên hệ bên dưới. Không mở, đọc bytes, decode hay suy luận trên ảnh/crop test; các tên, SHA, group và dHash test trong báo cáo chỉ lấy từ manifest và cache metadata có sẵn. Đây là đề xuất cách ly/gộp để owner nghiệm thu; không sửa group/split v6 và không xác nhận độc lập subject/session.

## Các crop R3 cần cách ly

| Crop R3 | Screening | Bằng chứng | Đề xuất |
|---|---|---|---|
| V7-C-029 | scb:033, `0006004.jpg` | Cùng lớp, người, bàn, logo và vệt màu với ảnh val EXP-SCB-005 (`1307017.jpg`) và EXP-SCB-024 (`0006005.jpg`); đã xem full source val và candidate | Cách ly họ hàng val; không tính quota/train |
| V7-C-067 | rf:192, `20220616_140727` | Cùng người, phòng, cột, đồng hồ, khăn/mask và bàn với val V6-CA-006 (`20220616_140640`); đã xem hai full source. rf:210 và rf:227 cũng được observations cũ ghi cùng scene192 | Cách ly cả family192/210/227; không tính quota/train |
| V7-C-037 | scb:041, `12_001586.jpg` | Cùng tiền tố video `12_` với bảy crop trong test group PB-G-2bfd674c05ef8b6e2ea6 (có cả series `11_`); cached nearest test distance9 tới SCB-write-015. Group evidence lịch sử gọi family `VIS-SCB-GREY-WINDOWS` | Cách ly vì có lineage test đáng nghi; không cần mở test để bù chứng cứ |
| V7-C-014 | scb:068, `3005262.jpg` | Tên thuộc vùng số `30051/52xx`, gần test `3005291/3005298`; chưa có upstream video/session lineage độc lập | Cách ly bảo thủ **pending**, không khẳng định cùng scene test |
| V7-C-022 | scb:076, `3005199.jpg` | Như trên; đã xem candidate, chưa có bằng chứng độc lập từ upstream | Cách ly bảo thủ pending |
| V7-C-034 | scb:084, `3005150.jpg` | Như trên | Cách ly bảo thủ pending |
| V7-C-040 | scb:090, `3005204.jpg` | Như trên | Cách ly bảo thủ pending |

Bốn crop `30051/52xx` là quyết định quản lý rủi ro Draft, **không phải phát hiện leak đã chứng minh**. Tên số chỉ là hint yếu: `0006004` và `0006012` thực tế khác lớp; `3004157` và `3004160` cũng khác lớp. dHash xa không chứng minh độc lập, dHash gần không tự xác định subject/session. Nếu có provenance upstream đủ rõ, có thể review lại bốn record pending mà không mở test. Parent train `SCB-read-003/3005249` cũng có vùng tên gần số; báo cáo không suy ra v6 đã leak chỉ bằng tên, và giữ v6 bất biến.

## Không loại chỉ vì gần tên số

- scb:003 (`0006012`, V7-C-005) là lớp đồng phục đỏ/đen, bàn vàng ghép nhóm, rèm đỏ và màn chiếu; khác rõ với val `0006005/1307017` lớp trẻ áo sọc, bàn xám riêng. Không đủ lý do quarantine vì tiền tố `00060`.
- scb:067 (`3004160`, chưa có crop R3) là lớp người lớn áo mùa đông, bàn trắng/đen và tường nhạt; khác với val `3004157` lớp trẻ bàn viền xanh. Không quarantine chỉ vì hai số cách nhau3.
- scb:093/094/099 (`0009048/0009033/0024054`) khác rõ với các full source val `0009039/0009035/0024070` đã xem. Điều này chỉ bác bỏ liên hệ thị giác cụ thể, không chứng minh độc lập toàn bộ người/cảnh/lineage.

## Family cần gộp hoặc nối parent train

| Screening mới | Crop R3 | Family/parent đề xuất | Mức bằng chứng |
|---|---|---|---|
| scb:002/016/032/053/056 | C003/C049/C093 | EXP-SCB-034, PB-G-7adf3e797f0d4d4978d9 | Đã so full source scb002 với parent train `18_000764`: cùng người, giáo viên, tường xanh, bàn nhóm và gương; các frame còn lại theo observations đã có |
| scb:006 | C007 | EXP-SCB-021, V6-G-6af358955ba8ec5f1bd9 | Đã so full source `6_001587/6_000942`, cùng người/phòng/giáo viên |
| scb:027 | C025 | EXP-SCB-032, V6-G-7f8137444d3c846d0587 | Đã so `49_000959/49_001017`, cùng lớp, bàn tím, logo và người |
| scb:018/081 | C017 | SCB-turnhead-021, V6-G-666a2ea0ed4f708dbff2 | Đã so `9_000749/9_001110`, cùng phòng, người và giáo viên;081 theo observations cũ |
| scb:012/023/036/043/052 | C011/C033/C041/C047 | SCB-turnhead-012, PB-G-f0b75b5ac12d58228355 | Đã xem012/036/043/052 và parent `130_000222`, cùng người/bàn/rèm/giáo viên;023 theo observations. Parent group Accepted có phạm vi rộng hơn một room, không tự thu hẹp |
| rf:295 | B038 | SCB-read-020 (`0013019`), V6-G-55c6b431fc5ea84e0bd0 | Tên gốc trùng `0013019`, cached dHash0; RF là re-export/noise của nguồn SCB. Không tính nguồn/frame/cảnh mới. Nếu person khác parent crop thì cần xác minh unit riêng |
| scb:093 + rf:281 | C044 + B022 | Một family trắng/đen, bàn trắng và ghế xanh | Đã xem hai full source: cùng người, phòng và dãy bàn, camera/frame khác. Không tính hai nhóm mới |
| rf:163/196 | A006 | Một family computer-red-shirt | Observations cũ ghi cùng người/cảnh; không tự xác nhận độc lập với tất cả parent/test |
| rf:093/127 | B039/B040 | Một family stock grey-shirt-white-desk | Selection/pair R3 và observations đã ghi cùng cảnh/người; phải cùng family |

Các liên hệ train-only thêm từ tiền tố và cached neighbors (ví dụ scb:059/062 với SCB-read-015, scb:080 với SCB-write-023, scb:082 với SCB-write-001) được giữ ở mức hint trong JSON; chưa thành group Accepted. Mọi crop khác vẫn `UNPROVEN` về độc lập; filename mới, SHA mới, source_id khác hoặc detector bbox khác không làm tăng số nhóm độc lập.

## Phạm vi kiểm và việc còn lại

JSON đi kèm có pin SHA input, disposition cho toàn400 screening local và join candidate theo `(screening_set, screening_id)` để tránh trùng ID giữa RF/SCB. Quarantine RF đã có trong observations được kế thừa có ghi nguồn bằng chứng; không giả vờ agent đã xem lại toàn bộ400 full source trong lượt này. Không có fingerprint test mới.

Owner cần nghiệm thu family/group theo ảnh nguồn và provenance trước split/release. Có thể tiếp tục bổ sung candidate public độc lập với những nguồn này trong khi các family pending bị cách ly. Report này không tính số nhóm mới đạt budget của plan và không thay thế independent holdout.
