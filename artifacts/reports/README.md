# Consolidated audit evidence

- `scb-20261003/audit.json`: 19 original SCB records.
- `roboflow-20261004/audit.json`: original source audit records.
- `roboflow-20261004/review.json`: review records, retired source/document snapshots, final person/crop and image queue.

Every historical record stores original UTF-8 `text` and SHA-256 of those exact bytes. Original JSON can be read with `json.loads(record["text"])`; its historical script paths/hashes refer to that run, not current code. Snapshots are evidence, not supported executable entrypoints. Tests verify all 54 original JSON records and final positive/unknown counts.

Current review data lives in `current_person_crops` and `image_queue`. Do not derive current state from intermediate summaries in `records`. Media remains in ignored outputs; raw/ZIPs are unchanged. Consolidation does not accept any dataset or approve training.
