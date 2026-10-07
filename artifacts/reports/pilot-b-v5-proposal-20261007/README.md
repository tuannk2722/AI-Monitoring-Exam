# Đề xuất nghiệm thu release pilot B v5

Ngày 2026-10-07. **Đã hoàn tất kiểm kê hợp nhất và phương án cụ thể; chưa phát hành v5.** [Config](../../../configs/datasets/pilot_b_v5_release_proposal_20261007.yaml), [membership từng record](membership-proposals.json), [nhóm/quan hệ](group-components.json), [coverage](summary.json), [verification](verification.json).

## Phương án đề nghị

Hợp nhất metadata của 112 record v4, 72 candidate R2 và 24 Classroom thành 208 record. Giữ nguyên nhãn/crop/source/unknown đã duyệt. Bổ sung train đúng 20 mẫu: 19 Classroom có ít nhất một target biết và EXP-RF-019 nối vào nhóm train cũ theo EXP-LINK-10 đã duyệt. Không chọn mẫu từ kết quả test/model.

| Usage | Hiện tại | Đề xuất v5 |
|---|---:|---:|
| train | 60 | 80 |
| val | 13 | 13 |
| test | 11 | 11 |
| review_only | 113 | 93 |
| excluded | 11 | 11 |
| Ledger | 208 | 208 |

Manifest sử dụng dự kiến 104 mẫu. Train phone 17P/16N/47U, looking 25P/38N/17U; 10 normal. Thêm 6 phone positive từ Classroom, nhưng chúng thuộc cùng một nhóm nguồn. Không tuyên bố tăng 20 tình huống độc lập. Membership 208 là đề xuất release mới, không thay ledger 112 của v4.

## Nhóm và rò rỉ

Đã đối chiếu toàn 208 record bằng group đã duyệt, exact source SHA và 11 must-link R2; lan truyền quan hệ qua connected components. Không phát hiện component nối hai nhóm parent khác nhau hoặc hai split parent khác nhau. [Chi tiết](group-components.json) ghi đủ member, evidence và trạng thái mỗi component.

- CM-V2-SCENE-01 đã duyệt cho 150 ảnh nguồn. Đề xuất dành toàn nhóm cho train; chỉ 19 crop đã biết target tham gia loss, 5 cả hai unknown tiếp tục review_only. Mọi ảnh bổ sung sau từ 150 ảnh này phải giữ cùng ranh giới train.
- EXP-RF-019 nối nhóm PB-G-88e21db5e6c794bef0f2 vốn thuộc train. Thêm mẫu vào train không tạo nhóm độc lập mới.
- EXP-RF-007/009 và các anchor excluded liên quan nối nhóm validation PB-G-baf0e0aa45deba62941c; không đưa vào train. Giữ007/009 review_only để không đổi membership validation13.
- Các component SCB/RF chỉ có quan hệ nội bộ chưa đủ chứng minh ranh giới độc lập với các nhóm còn lại. Không gán singleton thành session mới hoặc split ngẫu nhiên; chúng ở review_only. ID V5-COMP chỉ là mã component metadata đề xuất, không phải group độc lập accepted.

Trong 93 review_only: 27 mẫu cả hai unknown; 66 mẫu có ít nhất một target biết nhưng không đưa vào manifest ở phương án này (gồm 2 mẫu liên hệ validation cần bảo toàn). R2 và 28 review_only cũ vẫn cần review nhóm rộng hơn nếu muốn khai thác tiếp. Phương án này là bản mở rộng thận trọng có thể nghiệm thu ngay, không tuyên bố đã giải quyết toàn bộ nhóm SCB/RF. Không hủy các candidate chưa sử dụng.

## Protocol đánh giá đề xuất

Giữ chính xác 13 val và 11 test v4: cùng ID, source/crop hash, nhãn/mask/group. Không chuyển ảnh cũ từ val/test sang train. Test v4 đã được evaluate trong E001, không gọi nó là holdout chưa nhìn hoặc tự chạy lặp để so model.

E002 cần experiment config và protocol riêng trước chạy; chưa tự chọn model, biến training, threshold hay acceptance metric mới. Đề nghị dùng val hiện có cho phát triển/chọn candidate; mọi final test chỉ theo protocol pin checkpoint/config và được duyệt riêng. Không dùng kết quả E001 test để tuyển dữ liệu. Không đặt metric promotion từ số lượng dữ liệu.

Classroom chỉ ở train nên validation/test hiện tại không đo được khả năng khái quát độc lập trên Classroom. Cần một nhóm/phiên thực tế độc lập cho mục tiêu đó; không tách 150 frame hiện có để tạo holdout giả.

## Nghiệm thu cần thiết

Đề nghị owner duyệt membership 208, usage 80/13/11/93/11, phần mở rộng nhóm theo approved links, dành nhóm Classroom cho train và bảo toàn val/test như trên, để Codex đóng gói release v5. Phê duyệt này chưa cho chạy E002 hoặc final test.

Đây là quyết định mới về dataset/split: [AGENTS.md](../../../AGENTS.md) yêu cầu “Mọi dataset mutation phải tạo version/pointer mới và có owner review được ghi lại”. Approval staging đã được ghi tại [continuation](continuation-approval.json); không dùng nó để tự nhận split/release mới. Quyền dữ liệu và crop/nhãn/nhóm Classroom không hỏi lại.

## Kiểm chứng/phạm vi

Metadata/proposal đã được kiểm: 208 ID duy nhất, đầu vào package khớp checksum, nhãn/crop không đổi, 20 mẫu train mới đủ target biết, exact/group/must-link không băng qua split, membership val/test bất biến, excluded vẫn excluded, unknown mask giữ nguyên. Chưa xuất manifest accepted hoặc sửa raw/v4/staging. Không đọc ảnh test hay metrics để lập đề xuất; không train/upload/commit/push.

Snapshot `source-record-snapshots.jsonl` giữ nguyên version mỗi record từ ba package nguồn, chỉ để đối chiếu; không đọc như một canonical package chung. Release sau nghiệm thu mới chuyển sang version thống nhất qua builder.
