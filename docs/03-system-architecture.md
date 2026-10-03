# 03 — Kiến trúc Hệ thống

## Ranh giới của repository

```text
data/raw (bất biến, DVC)
  → src/data — audit + source converters
  → data/interim (có thể tái tạo)
  → data/processed/exam (canonical, grouped split, DVC)
  → src/training + evaluation
  → artifacts/models/<EXP> + metrics/plots
  → src/inference — structured predictions
  → P5 tracking
  → P6 events/risk/evidence
  → P7 FastAPI dashboard
```

Các module Data/ML không được import FastAPI/web code. Web tiêu thụ các contract có version từ `25-interface-and-data-contracts.md`.

## Formulation candidate A

`frame → bbox + behavior class`. Baseline kiểu YOLO đơn giản, dễ tích hợp, nhưng một bbox thường chỉ mang một class và có thể không biểu diễn tốt các hành vi xảy ra đồng thời.

## Formulation candidate B

`frame → person bbox → track/crop → multi-label behavior classifier`. Phù hợp hơn cho hành vi đồng thời nhưng cần nhãn person/crop và nhiều bước pipeline hơn. Kết quả benchmark P1 sẽ quyết định; code không được ép ngữ nghĩa `normal` trước khi có bằng chứng.

## Các trạng thái lỗi (failure states)

- Source/license/mapping thiếu hoặc không hợp lệ: build dataset thất bại; không có version "thành công một phần".
- Gián đoạn runtime/OOM: trạng thái run là FAILED/INTERRUPTED; không được âm thầm thay đổi config.
- Không rõ phiên bản model/label/rule: từ chối bản ghi tích hợp.
- Thiếu timestamp/FPS: inference có thể giữ frame index nhưng phải đánh dấu video time là không khả dụng.
- Mất tracking: tạo track tạm thời mới là chấp nhận được và cần được đo; không bao giờ suy diễn danh tính thật.

## Topology triển khai cho MVP

Batch job chạy local/Colab tạo ra các artifact portable. P7 FastAPI chạy local đọc processed output/SQLite trên máy demo. Không cần server công khai, Cloudinary, WebSocket hay IP camera.
