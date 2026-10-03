# 05 — Roadmap và Exit Gate

| Phase | Deliverable | Exit gate |
|---|---|---|
| P0 Foundation | repo/docs/config/CI/DVC smoke setup | cả 3 thành viên clone + test pass; DVC push/pull nhỏ hoạt động |
| P1 Research | dataset cards/audit/label/formulation/split quyết định | license và mapping đã biết; ADR dataset/task được review |
| P2 Preparation | `dataset-v0.1` bất biến | manifest/checksum/grouped split/QA/DVC pointer pass |
| P3 Baseline | model E001 + metrics + artifacts | smoke có thể tái tạo; báo cáo validation/error; provenance đầy đủ |
| P4 Improvement | các so sánh E002+ có chủ đích | candidate được chọn dùng val+holdout, không dùng test |
| P5 Tracking | track trên video ghi sẵn | báo cáo ID stability/switch/loss trên fixed clips |
| P6 Events/Risk | event timeline/evidence | rule evaluation có version và báo cáo false-alert |
| P7 Web | dashboard review local | luồng recorded session và thao tác của người dùng hoạt động |
| P8 Evaluation | giao thức đánh giá cuối cùng được đóng băng | model + system metrics trên data/hardware đã khóa |
| P9 Report/Demo | demo/report có thể tái tạo | video/artifact dự phòng offline đã chuẩn bị; claim khớp bằng chứng |

Target là cuối tháng 11–tháng 12/2026, nhưng exit gate — không phải lịch — mới là điều kiện cho phép làm việc downstream. Tuần 1 song song: Data Lead audit; Model Lead chuẩn bị trainer/pretrained smoke; Pipeline Lead xây dựng structured inference contract với sample/pretrained output. Không ai đợi nhàn rỗi, nhưng cũng không ai gọi placeholder là "xong".
