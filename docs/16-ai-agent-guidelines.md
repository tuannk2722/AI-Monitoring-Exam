# 16 — Hướng dẫn cho AI Coding Agent

Quy tắc canonical nằm trong `AGENTS.md` ở root. Với mỗi task, agent đọc index này và chỉ đọc docs/ADR accepted liên quan, nêu rõ assumptions/acceptance criteria, và báo cáo tests/TBD sau khi hoàn thành.

Agent được phép: triển khai script/test/docs/config đã được phân công. Agent không được: tự chọn data/class/split/model/metric/threshold/risk/scope, thay đổi raw data, upload media cá nhân, commit secret, hoặc coi notebook output là source of truth.

Với code conversion/split/metric của dataset, yêu cầu reviewer và fixture. Strip notebook output chứa media/token/path. Nếu một quyết định còn thiếu, duy trì tiến độ trên các phần độc lập và tạo TBD chính xác thay vì bịa một con số trông hợp lý.
