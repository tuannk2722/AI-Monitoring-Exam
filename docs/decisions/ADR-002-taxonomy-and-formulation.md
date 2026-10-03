# ADR-002 — Candidate taxonomy và formulation gate

- Status: Accepted as a research constraint; final formulation pending P1
- Date: 2026-09-19

**Quyết định**: tên canonical candidate là `normal`, `looking_around`, `phone_use`; hành vi đồng thời phải vẫn biểu diễn được. So sánh detection trực tiếp A với person crop classification B; không có temporal model trong baseline. Biểu diễn `normal` và annotation unit chỉ được quyết định sau khi có bằng chứng audit/feasibility.

**Hệ quả**: config là draft và build fail nếu mapping chưa được review tường minh.
