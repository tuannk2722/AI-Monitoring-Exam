# Recorded-video pipeline gate

Pipeline end-to-end P5/P6 không được nối bằng mock. Hiện tại `inference.detect` tạo JSONL có provenance để Pipeline Lead phát triển tracking/event sau khi model được promote. Xem `docs/03-system-architecture.md`, `docs/12-phase-p5-p6-tracking-events-risk.md` và ADR-008/009.
