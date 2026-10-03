# ADR-009 — Rule-based events và explainable risk baseline

- Status: Proposed framework; thresholds/formula pending P6 data
- Date: 2026-09-19

**Quyết định candidate**: aggregate prediction thành temporal event có version, sau đó tính bounded/decaying risk từ event history. Giữ model confidence tách biệt với risk. Không có GRU/TCN hay tự động kỷ luật trong MVP.

**Hệ quả**: triển khai chờ labeled event fixture; các giá trị không thể sao chép từ trực giác.
