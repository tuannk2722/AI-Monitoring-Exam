# 09 — P2 Dataset Preparation (Chuẩn bị Dataset)

## Output chuẩn tắc

```text
data/processed/exam/
├── images/{train,val,test}/
├── labels/{train,val,test}/
├── dataset.yaml
├── manifest.csv
├── label_map.yaml
└── dataset_report.json
```

`data/raw` là bất biến. Conversion theo từng nguồn được thực hiện qua code/manifest đã review. `interim` và `processed` đều có thể tái tạo.

## Source manifest bắt buộc

Mỗi nguồn raw phải có `source_manifest.csv` với các cột canonical định nghĩa trong `25-interface-and-data-contracts.md`. `group_id` phải nhóm các frame/mẫu không được phép chia sang các split khác nhau. Metadata không biết được phép để trống; metadata bịa là không được phép.

## Build gate (Điều kiện mở khóa build)

`configs/datasets/exam_v0.1.yaml` cố tình để `sources` ở trạng thái `pending_audit` và mapping trống. Data Lead phải điền mapping nguyên class nguồn → class canonical (dưới dạng số nguyên) và chỉ đặt `accepted` sau khi reviewer phê duyệt. Nếu chưa đủ điều kiện, build sẽ fail.

```bash
python -m ai_exam_monitoring.data.build_dataset --config configs/datasets/exam_v0.1.yaml
python -m ai_exam_monitoring.data.validate_labels --labels data/processed/exam/labels --class-ids 0,1,2
dvc add data/raw data/processed/exam
dvc push
```

Commit các file pointer, config, các báo cáo JSON/CSV nhỏ và tag milestone được phê duyệt (`dataset-v0.1`). Không tạo `dataset_final2/`; Git commit + DVC hash quản lý version nội dung; `exam_v2` được dành riêng cho thay đổi schema/taxonomy có chủ đích.

## DoD (Điều kiện hoàn thành P2)

Build là deterministic; checksum và provenance tồn tại; kiểm tra group leakage pass; label mapping đã được đóng băng; phân bố split/QA đã được review; thành viên thứ hai có thể `git pull && dvc pull` và thu được version giống hệt.
