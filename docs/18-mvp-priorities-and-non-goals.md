# 18 — MVP và Non-goals

## Checklist MVP

- [ ] source/license/provenance được audit đầy đủ;
- [ ] label/annotation/formulation đã được accept;
- [ ] grouped split bất biến và dataset version DVC;
- [ ] baseline có thể tái tạo + báo cáo per-class/error;
- [ ] model được chọn đã test trên bản ghi giống kỳ thi thật độc lập;
- [ ] track tạm thời và tracking report;
- [ ] event rule/timeline có version;
- [ ] risk signal có giới hạn và giải thích được;
- [ ] evidence có thể truy vết;
- [ ] dashboard recorded-session local và hành động review trung lập;
- [ ] đánh giá model/system cuối cùng và nêu rõ limitations thật sự.

**Non-goals**: quyết định kỷ luật thật, nhận diện danh tính/mặt người, đa camera, scale sản xuất/cloud, ứng dụng di động, toàn bộ tám hành vi, auth phức tạp, mạng temporal nâng cao theo mặc định.

**Phòng ngừa thất bại**: không chia split ngẫu nhiên trên cùng video, không tune trên test, không thay đổi label chưa review, không có `best.pt` chưa versioned, không có metric/UI giả, không mutation raw data, không commit credential, không mở rộng web quá sớm.
