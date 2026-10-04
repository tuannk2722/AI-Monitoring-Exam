# Supported audit entrypoints

`roboflow_v1.py` reproduces the full source audit for the pinned owner ZIP, including source metadata and cross-SCB exact hashes. See the three canonical Roboflow documents under docs/data/candidates. Choose new output/evidence paths; never overwrite historical output.

Generic CPU source tools: `python -m ai_exam_monitoring.data.audit`, `.overlay`, `.validate_labels` (full module prefix for each). They support verified SCB or Roboflow subtrees; names come from explicit source metadata, not inferred mappings.

One-off pilot/batch/crop/approval launchers were retired after the consolidated owner snapshot. Their source and original decisions remain in artifacts/reports/roboflow-20261004/review.json for provenance. Shared validators/decision functions live in ai_exam_monitoring.data.review with regression tests. No separate script per future review batch.

No classifier B exporter or training runner is claimed here; those are preparation work, not audit.
