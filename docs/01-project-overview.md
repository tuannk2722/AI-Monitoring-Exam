# 01 — Project Overview (Tổng quan Dự án)

## Product statement (Tuyên bố sản phẩm)

Đồ án nghiên cứu/demo phân tích **một video của một phòng thi với một camera**, theo dõi khoảng 10–15 candidate track và mô tả các hành vi quan sát được. Output hỗ trợ giám thị review, không phải kết luận vi phạm.

## Actor chính và các chế độ

- Actor chính: người thực hiện demo/giám thị review.
- MVP mode: batch recorded video (video ghi sẵn xử lý theo batch).
- Later mode: webcam/live, chỉ sau khi batch pipeline đạt system gate.
- Track ID là định danh kỹ thuật trong một session, không phải danh tính thật.

## Outcome chain (Chuỗi kết quả)

```text
recorded video
→ frame/prediction
→ temporary track ID
→ behavior candidate
→ filtered event timeline
→ versioned risk signal
→ evidence
→ human review
```

AI output: label hành vi, confidence, bbox, model/version, frame/time; về sau thêm track/event/risk/evidence. Không được đổi `confidence` thành "xác suất gian lận".

## Target success (Điều kiện thành công)

Demo có thể truy vết ngược mỗi alert/event về source video, frame/time, model artifact, dataset/split/config/experiment và rule version. Nhóm giải thích được limitations/domain gap/false positive thay vì chỉ trình bày UI.

## Ràng buộc

- Owner solo đảm nhiệm ba vai trò theo [workflow hiện hành](06-team-collaboration-and-git.md), ngân sách compute/storage 0 đồng.
- Máy yếu nhất: i7-1255U, RAM 8/16 GB, Intel UHD; local không phải full-training target.
- Colab Free có runtime không ổn định; checkpoint/resume/persistent storage là bắt buộc.
- Không lưu danh tính thật trong MVP; không face recognition.
