# Đề xuất membership/split sau audit nhãn

**Snapshot R4:** dùng [quyết định owner cuối](owner-decisions.md) và `annotation-r4/` để nghiệm thu R5; giữ bảng dưới để truy vết.

Trạng thái: Draft, owner chưa duyệt. Không đổi R7 hoặc accepted v4–v6, không tạo official manifest/split và không train.

| Thành phần cuối R4 | Số crop đo được | Đề xuất có điều kiện |
|---|---:|---|
| Hai target đều U | 15 | Giữ review_only, recrop/xác minh thiết bị/workarea nếu còn bằng chứng; chưa dùng cho supervised training |
| Ít nhất một target P/N | 259 | Chỉ là upper bound membership; từng target U vẫn masked. Cần chốt label/crop, quyền, group và tránh evaluation lineage trước nghiệm thu |
| Cả hai target P/N | 70 | Chỉ là fully-known support, không đồng nghĩa 70 nhóm độc lập hoặc đủ cả failure mode |
| P/P | 10 | Giữ co-occurrence nếu đúng cùng anchor; kiểm source/domain và ownership |
| P/N | 3 | Bucket supervision còn tập trung và ít support; ưu tiên mobile positive trong lớp/phòng thi với workarea rõ |
| N/P | 8 | Cần gaze evidence và vùng làm việc riêng; không suy P từ đầu nghiêng |
| N/N | 49 | Không refill bằng negative dễ để tăng count; ưu tiên matched same-image/scene/session có bằng chứng |

162 pair R7 chỉ có 7 liên hệ mạnh hơn source-context (6 same-image, 1 same-scene). Sau final R4, 21 pair mất target P/N và 141 còn đúng polarity; các pair còn đúng target vẫn cần xem anchor/ownership. Một negative có thể được dùng bởi nhiều pair nên count pair không phải số mẫu độc lập.

Graph proposal dùng exact source byte/pixel hash, Flickr photo ID, registered parent group và các family/scene hint bảo thủ. Nearest similarity có sẵn chỉ được ghi thành cờ, không tự union mọi nearest. Whole-component là đơn vị xem xét split; component count theo hints không phải số group độc lập đã chứng minh.

- Component nối trực tiếp parent evaluation bằng exact evidence: quarantine/review_only, không tuyển vào train.
- Component nối parent train: owner xác nhận scene lineage và giữ toàn component cùng train nếu membership được duyệt.
- Component không có parent: chờ owner chốt group, sau đó đề xuất train hoặc validation phát triển mới theo cả component; không chia ngẫu nhiên crop.
- Camera, room, session không có metadata thì giữ unknown. Cùng source không chứng minh cùng camera/session, khác image ID không chứng minh độc lập.

Giữ validation/test lịch sử nguyên trạng. Nếu owner muốn validation phát triển mới, phải có protocol/split version mới; chưa tạo validation hoặc dùng independent holdout trong audit này.

Blocker release: label/anchor/device/gaze Draft, rights/notice public chưa nghiệm thu, independence và group graph chưa chốt, matched pairs chủ yếu yếu, thiếu desk-phone đúng classroom/exam và small/partial evidence input224 còn cần nghiệm thu. Blocker E004 promotion còn gồm numerical gates/recipe/holdout policy được yêu cầu ở hồ sơ E004; crop audit không đóng các quyết định đó.
