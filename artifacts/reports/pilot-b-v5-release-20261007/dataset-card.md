# Pilot B v5 — release local đã nghiệm thu

Version pilot-b-20261007-v5; scope local_classifier_research. Ledger208 record; manifest104 mẫu dùng:80 train/13 val/11 test.93 review_only và11 excluded không được dùng để train/evaluate. Chỉ đọc manifest.jsonl cho các tác vụ đó, không đọc toàn thư mục crops.

Xuất197 crop đã review, không xuất11 excluded. Thêm19 Classroom vàRF-019 vào train. Nhãn phone_use/looking_around theo crop SHA đã duyệt, unknown null/mask0. Geometry/source/crop/target cũ giữ nguyên.

Val13/test11 giữ ID, nhóm, crop/nhãn/mask của v4. Test đã evaluate ở E001; không phải holdout chưa nhìn. Không tự chạy final test hoặc E002 từ approval dataset.

Nhóm Classroom CM-V2-SCENE-01 dành cho train, gồm150 ảnh nguồn nhưng chỉ19 crop biết target trong manifest.5 crop Classroom cả hai unknown ở review_only. Không có holdout độc lập Classroom. V5-COMP chỉ giữ liên hệ trong metadata, chưa được coi nhóm độc lập để chia split.

release.json pin config/approval/parent/evidence. reports/ chứa QA, coverage, leakage; split-assignment.jsonl ghi split đã duyệt. Quyền/attribution theo từng record và source_attribution_refs; không thay tuyên bố license gốc.

Release chỉ local; chưa train, upload, commit hoặc push. Crop runtime và model promotion là các bước riêng.
