# 25 — Interface và Data Contracts

Python dataclass trong `src/ai_exam_monitoring/contracts/domain.py` là contract thực thi được.

## Dataset manifest legacy (YOLO detection)

Các cột: `sample_id,image_path,label_path,source,video_id,session_id,room_id,subject_id,group_id,split,dataset_version,label_map_version,license_id,sha256`. `sample_id` phải unique toàn cục; `group_id` là bắt buộc; một group không được phép vắt qua train/val/test. Metadata nguồn chưa biết để trống.

## Classifier B — phần cần triển khai

Manifest legacy trên không biểu diễn target multi-label/unknown. Snapshot audit dùng person/crop/source SHA và target states, không phải schema training đã freeze. Trước exporter cần chốt schema version, encoding positive/negative/unknown và crop inference, rồi cập nhật producer/consumer/tests cùng lúc. Không tự chuyển unknown thành 0 hoặc dùng class ID detector làm target classifier. Detector person và behavior predictions là các task khác nhau.

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
