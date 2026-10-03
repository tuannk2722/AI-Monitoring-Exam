# 14 — P8/P9 Evaluation, Demo và Report

## Giao thức đánh giá đóng băng (Frozen Evaluation Protocol)

Ghi lại: phiên bản code/data/model/rule; phần cứng/OS để test; độ phân giải input/FPS/thời lượng; warm-up; số lần chạy lặp lại; latency mean và percentile; throughput; RAM/VRAM đỉnh; model metrics; tracking switch/loss; event matching tolerance; false-alert/missed-alert. Target được đặt ra sau baseline, không phải bịa trước.

Test set chỉ được dùng một lần cho cấu hình cuối cùng được chọn. Exam-like simulation giữ độc lập theo participant/session/room ở mức khả thi và tuân theo consent policy.

## Demo

Luồng chính: video ghi sẵn → predictions → tracks → events → risk/evidence → review. Chuẩn bị offline fallback recording và frozen artifact phòng trường hợp Colab/mạng/camera live thất bại. Phần trình bày phân biệt rõ: đã triển khai, đã đo lường, đã lên kế hoạch và chưa hỗ trợ.

## Report (Báo cáo)

Vấn đề/phạm vi; governance; source/license/audit; label/split; formulation/model; khả năng tái tạo; experiments; model/system metrics; error/domain analysis; tracking/event/risk; tích hợp web; limitations/bias/privacy; future work. Không được báo cáo tám hành vi nếu chỉ triển khai được candidate Tier 1.
