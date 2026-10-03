# Tracking module gate

Không có tracker giả trong production path. Module Python chỉ được thêm ở P5 sau khi:

1. model candidate đã được promote và có structured predictions;
2. `ADR-008` được review bằng benchmark ByteTrack trên video holdout;
3. các trường `TBD_BY_P5_BENCHMARK` trong config tracking được chốt;
4. metric ID switches/lost tracks/occlusion recovery được định nghĩa.

Contract đầu vào/đầu ra nằm ở `docs/25-interface-and-data-contracts.md` và `contracts/domain.py`.
