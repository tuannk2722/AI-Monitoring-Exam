# 24 — Non-functional Requirements (Yêu cầu Phi chức năng)

| ID | Yêu cầu | Target/Status |
|---|---|---|
| NFR-REP-001 | Truy vết mọi model được chọn đến code/data/split/config | Bắt buộc ngay bây giờ |
| NFR-PRIV-001 | Không có dữ liệu/danh tính người thật trái phép | Bắt buộc ngay bây giờ |
| NFR-SEC-001 | Không có secret trong Git/notebook/log; Drive access tối thiểu | Bắt buộc ngay bây giờ |
| NFR-REL-001 | Colab run bị gián đoạn có checkpoint/status persistent | Bắt buộc P3 |
| NFR-PERF-001 | Throughput recorded-video trên laptop demo | giá trị số sau baseline benchmark |
| NFR-LAT-001 | Định nghĩa alert/event latency và p50/p95 | TBD trước P8 |
| NFR-RES-001 | RAM/VRAM/disk đỉnh trong môi trường target | đo theo từng run |
| NFR-IN-001 | Độ phân giải input/FPS/size/duration được hỗ trợ | TBD từ sample benchmark thực tế |
| NFR-ACC-001 | Demo UI cơ bản: keyboard accessible, dễ đọc, responsive | Bắt buộc P7 |
| NFR-OBS-001 | Error và status của run/job có cấu trúc | Bắt buộc P3/P7 |
| NFR-BACK-001 | DVC artifact có thể khôi phục từ commit/tag đã tài liệu hóa | Bắt buộc P2+ |

Giá trị performance/quality bằng số phải trích dẫn từ experiment/protocol. Không được sao chép từ web benchmark ngẫu nhiên.
