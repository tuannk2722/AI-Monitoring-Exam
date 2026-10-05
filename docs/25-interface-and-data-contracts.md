# 25 — Interface và Data Contracts

Python dataclass trong `src/ai_exam_monitoring/contracts/domain.py` là contract thực thi được.

## Dataset manifest legacy (YOLO detection)

Các cột: `sample_id,image_path,label_path,source,video_id,session_id,room_id,subject_id,group_id,split,dataset_version,label_map_version,license_id,sha256`. `sample_id` phải unique toàn cục; `group_id` là bắt buộc; một group không được phép vắt qua train/val/test. Metadata nguồn chưa biết để trống.

## Classifier B — schema và release pilot local v4 đã nghiệm thu

Manifest legacy trên không biểu diễn target multi-label/unknown. Snapshot audit vẫn là lịch sử; schema/encoding/config và manifest sử dụng của [pilot local v4](../artifacts/reports/pilot-b-release-acceptance-20261005/README.md) đã owner duyệt/freeze. [ADR-013](decisions/ADR-013-pilot-b-packaging-contract.md) và [contract](data/pilot-b-release-contract-v1.md) quy định nullable values/mask, normal metadata, eligibility, crop và group/split gates.

Thứ tự vector `[phone_use, looking_around]` không lấy từ class ID YOLO legacy; unknown lưu null/mask=0 và không tham gia loss/metric. Implementation `pilot-b-manifest-v1`/`pilot-b-targets-v1` ở [pilot_schema.py](../src/ai_exam_monitoring/data/pilot_schema.py): `PilotRecord`, các dataclass source/crop/target/context/rights/group/review; `record_to_dict`, `record_from_dict`, `read_records`, `write_records`, `validate_records`. Values/mask/normal được derive; codec từ chối field lạ hoặc giá trị không khớp state. Known evidence phải gắn đúng crop SHA; split/usage cần các gate độc lập.

Producer `pilot_prepare.create_ledger` tạo ledger ban đầu; batch/release importers nhập approval theo đúng pins. `pilot_package.build_pilot_package` kiểm bytes/pixels/provenance/membership/gates; pending không có usage manifest, accepted v4 có84 usage records và112 review-ledger records. Consumer `read_records` kiểm state/null/mask/normal và usage; test freeze trong release.json pin manifest/split/test subset. Code/schema/usage tests cập nhật cùng implementation; [runbook](data/pilot-b-preparation-v1.md) ghi config/evidence/lệnh. Crop inference tự động còn gate riêng trước baseline B end-to-end.

## Prediction

`prediction_id`, FrameRef (`session_id`, `frame_index`, `video_time_ms`, `source_uri`), `model_version`, `task`, `label`, `confidence`, `bbox` (`xmin,ymin,xmax,ymax,coordinate_space`), tùy chọn `class_id`. Confidence ∈ [0,1]; thứ tự bbox là XYXY có tên; label phải là hành vi quan sát được.

## TrackObservation

`session_id`, `track_id`, FrameRef, bbox, `source_prediction_ids`. Track ID chỉ có phạm vi trong session.

## BehaviorEvent

`event_id`, `session_id`, `track_id`, `behavior`, `start/end_frame`, `start/end_time_ms`, `aggregated_confidence`, `model_version`, `rule_version`, `source_prediction_ids`, `status`.

## Contract về sau

- **ModelVersion**: model ID, experiment ID, Git commit, phiên bản data/split/label, metrics, artifact URI/checksum, license record.
- **RiskSnapshot**: session/track/time, bounded score/level, engine version, contributing event ID.
- **Evidence**: event/alert, loại snapshot/clip, source checksum, cửa sổ frame/time, artifact checksum, trạng thái retention.
- **Review**: alert/event, hành động trung lập, pseudonym/account của reviewer, ghi chú, thời gian review.

## Experiment artifacts

`artifacts/models/<EXP>/run.json`, `weights/best.pt`; `metrics/<EXP>/{metrics,evaluation}.json`; `plots/<EXP>/...`. Binary lớn dùng DVC. Bất kỳ thay đổi schema contract nào đều phải tăng `schema_version` và cập nhật producer, consumer và test trong một lần change có review.
