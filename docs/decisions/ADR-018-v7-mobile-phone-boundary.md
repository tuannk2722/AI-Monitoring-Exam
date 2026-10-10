# ADR-018 — Phone_use chỉ bao gồm điện thoại di động

- Trạng thái: **Accepted**, chỉ cho ranh giới loại thiết bị được owner xác nhận.
- Ngày: 2026-10-09. Owner/reviewer: chủ repository (solo).
- Bằng chứng owner: trả lời “Chỉ điện thoại di động” khi được hỏi phone_use có bao gồm điện thoại bàn có dây hay không. [Receipt](../../artifacts/reports/pilot-b-v7-targeted-20261008/mobile-only-owner-decision-20261009.json).

## Bối cảnh

Nguồn public bổ trợ có điện thoại bàn tại bàn làm việc. Quy tắc trước đó dùng từ “điện thoại”, chưa phân biệt thiết bị này với mobile. Cần chốt ranh giới trước khi đề xuất nhãn v7.

## Quyết định

Phone_use chỉ bao gồm điện thoại di động. Điện thoại bàn có dây không tự tạo positive. Mobile trên bàn vẫn là positive khi liên kết đúng người, theo ADR-011. Với crop có điện thoại bàn, chỉ đề xuất mobile negative nếu vùng quan sát của đúng người đủ bằng chứng; nếu tay/bàn bị che hoặc thiết bị chưa rõ thì giữ unknown. Quyết định loại thiết bị không biến annotation thiếu phone thành negative.

Áp dụng vào proposal v7 và công việc tiếp theo. Nếu phát hiện nhãn lịch sử cần sửa, ghi delta cho version mới và owner review; không sửa các release v4–v6 hoặc kết quả E001–E003.

## Giới hạn

ADR này không nghiệm thu crop, attribution/quyền public, membership, nhóm, split, release, training recipe, holdout hoặc promotion. Các gate đó vẫn có hồ sơ/quyết định riêng.
