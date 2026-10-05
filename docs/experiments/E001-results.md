# E001 — Frozen ResNet18 reviewed-crop baseline

- Status: **FINISHED**, 2026-10-06 (Asia/Saigon). Owner/reviewer: repository owner; implementation and analysis: Codex. Parent experiment: none; smoke is a separate run.
- Hypothesis: pretrained frozen features can support a reproducible two-target masked linear probe on the accepted pilot.
- Approval: [ADR-014](../decisions/ADR-014-e001-local-linear-probe.md), [config approval](E001-approval.json). Config: [E001.yaml](../../configs/experiments/E001.yaml). [Runbook](E001-runbook.md).
- Code: `45240ea6234c70a80ecf3dc11f2e69eb8e253a53`, **git_dirty=false**, clean isolated checkout at `outputs/E001-code`. Source hash `6b295fd68c5e8e499b07d2ec046da1150026b6982b9bd4845a54948640a60bda` (UTF-8/LF normalized).
- Data/split/encoding: `pilot-b-20261005-v4` / `pilot-b-explicit-scene-split-v1` / `pilot-b-targets-v1`; original payload SHA unchanged. 60 train/13 validation/11 test; 28 review_only excluded.
- Environment: fresh Python 3.11.9 Windows venv, torch2.8.0+cpu/torchvision0.23.0+cpu, seed42, four CPU threads; i7-1255U. Exact closure in [lockfile](../../requirements/classifier-cpu-lock.txt) and [run record](../../artifacts/reports/E001/run.json). No CUDA or GPU training.
- Model: ResNet18 IMAGENET1K_V1, frozen encoder/BatchNorm, linear512→2 head (1,026 trainable parameters), full-batch masked per-target BCE. Model/weights provenance and terms in runbook.

## Measured execution

Smoke was intentionally interrupted after epoch1, persisted `INTERRUPTED`, then resumed unchanged to epoch3/`FINISHED`: [before](../../artifacts/reports/E001/smoke-interrupted.json), [after](../../artifacts/reports/E001/smoke-completed.json). Unit recovery test also matched uninterrupted weights/history exactly.

Baseline completed **32 epochs**, early stopping selected **epoch12**, the strict minimum validation macro masked BCE. The approved maximum was200; patience20/min_delta0.0001 were unchanged. Training routine measured **5.827 seconds** including local payload validation/feature extraction/head optimization/artifacts, excluding Python import/install/download startup. Peak process RSS **470,712,320 bytes (~449 MiB)**. These are one CPU run measurements, not end-to-end video latency or throughput.

At selected epoch12: train macro BCE0.5136202, validation0.5477270. At epoch32: train0.2781552, validation0.7055863. Train loss continued falling while validation worsened; the later checkpoint was not selected. [Learning curve](../../artifacts/reports/E001/learning-curve.svg), [history](../../artifacts/reports/E001/history.json).

The evaluator independently reloaded best.pt and reproduced all validation scores/metrics exactly. Candidate/config/code/data and threshold were frozen in [final protocol](E001-final-test-protocol.json), commit `84d4cf0d51564af971851e72cf4e37e3afe59fa4`, before final test. Test ran once; no training/config/threshold/model change followed it.

## Results and interpretation

Only known targets count. Threshold0.5 is fixed diagnostic behavior, not a deployment/risk threshold. AP measures ranking; it is not accuracy or evidence of useful decisions at0.5.

| Split / target | Known P/N | Unknown ignored | AP | Precision | Recall | F1 | TP/FP/FN/TN |
|---|---|---:|---:|---:|---:|---:|---|
| Train phone | 11/5 | 44 | 1.0000 | 0.6875 | 1.0000 | 0.8148 | 11/5/0/0 |
| Train looking | 17/33 | 10 | 0.8074 | 1.0000 | 0.3529 | 0.5217 | 6/0/11/33 |
| Validation phone | 7/1 | 5 | 0.9379 | 0.8750 | 1.0000 | 0.9333 | 7/1/0/0 |
| Validation looking | 3/3 | 7 | 0.9167 | undefined | 0.0000 | 0.0000 | 0/0/3/3 |
| Final test phone | 2/2 | 7 | 1.0000 | 0.5000 | 1.0000 | 0.6667 | 2/2/0/0 |
| Final test looking | 2/7 | 2 | 1.0000 | undefined | 0.0000 | 0.0000 | 0/0/2/7 |

Precision is undefined when no positive predictions exist; JSON uses null with a reason, not a fabricated0. Macro AP: train0.9037, validation0.9273, test1.0000. Test macro BCE0.5692188. Detailed [train/validation metrics](../../artifacts/reports/E001/metrics.json), [test metrics](../../artifacts/reports/E001/test-metrics.json).

**Operational predictions at0.5 are weak:** on validation/test phone predicts every known example positive; looking predicts every known example negative. The simple train-prevalence constant baseline makes the same thresholded decisions on these splits. The learned scores improve ranking, but the model has not demonstrated useful decision behavior. Do not present test AP1.0 as a deployable model.

Validation failures, also visually checked against local transformed crops:

- `P006-extra-01`, `P007-extra-01`, `P008-extra-01`: looking false negatives, scores0.3762/0.3661/0.4721.
- `SCB-write-002`: phone false positive, score0.7024.

[Error JSON](../../artifacts/reports/E001/validation-errors.json). The local error contact sheet is `outputs/E001-validation-errors.png`; no media committed/uploaded. All73 train/val transforms were visually reviewed for full-context preservation; [QA evidence](../../artifacts/reports/E001/transform-qa.json). This did not reopen label approval.

Phone known positives/negatives still confound source; val looking positives/negatives also segregate by source. Per-source slices lack both classes, so their binary aggregate metrics are explicitly unavailable. No positive co-occurrence exists in val/test. Pilot has no real-world holdout, no reliable calibration evidence and too little support to infer generalization or promotion thresholds. No confidence intervals based on falsely independent crops are claimed.

## Artifacts / reproduction

- Local run: `outputs/E001/`; best.pt SHA-256 `0f71fb19bb1524058fcc670b12067653b111527bfab62c1b6e5e2911c11eda74`. Last checkpoint retains epoch32 optimizer/RNG/early-stop state; best retains epoch12 head/config.
- Required frozen encoder: `outputs/pretrained/resnet18-f37072fd.pth`, SHA `f37072fd47e89c5e827621c5baffa7500819f7896bbacec160b1a16c560e07ec`. Do not load head without this exact backbone/transform.
- DVC local pointers: [E001](../../outputs/E001.dvc), [smoke](../../outputs/E001-smoke.dvc), [test](../../outputs/E001-final-test.dvc), [pretrained](../../outputs/pretrained.dvc). All up to date; **not pushed to remote**. Dataset remote permission does not expand to new artifacts automatically.
- Restored38 files from DVC cache objects into fresh `outputs/E001-cache-restore`, checked object MD5 and every restored file SHA against originals: [PASS evidence](../../artifacts/reports/E001/local-cache-restore.json). This is local-cache recovery, not a remote/empty-cache round-trip.
- Small metrics/provenance/curves in `artifacts/reports/E001/`. `run-artifact-checksums.json` and `test-artifact-checksums.json` refer to their source output directories, not the report directory.

Actual execution used the clean checkout as cwd, its src on PYTHONPATH, and `outputs/E001-env/Scripts/python.exe`:

```powershell
python -m ai_exam_monitoring.training.train --config configs/experiments/E001-smoke.yaml --workspace D:/ai-exam-monitoring-final --output D:/ai-exam-monitoring-final/outputs/E001-smoke --interrupt-after 1
python -m ai_exam_monitoring.training.train --config configs/experiments/E001-smoke.yaml --workspace D:/ai-exam-monitoring-final --output D:/ai-exam-monitoring-final/outputs/E001-smoke --resume
python -m ai_exam_monitoring.training.train --config configs/experiments/E001.yaml --workspace D:/ai-exam-monitoring-final --output D:/ai-exam-monitoring-final/outputs/E001
```

Separate evaluator calls used `--split val` and `--split test --protocol .../E001-final-test-protocol.json`. Full argv and UTC timestamps are in run/evaluation JSON. Existing output directories deliberately cannot be overwritten. For reproduction, use a fresh workspace with the same commit/config/weights/data; do not rerun final test to tune variants. DVC checkout can recover local cached outputs; another machine needs an explicitly authorized artifact transfer or weights download from the recorded official URL.

## Validation / decision

Fresh environment pip check,126 tests, repository checker PASS; local Ruff/compileall/diff checks PASS. Meaningful tests cover mask gradients/normalization, tied AP/undefined support, transform preservation, frozen backbone/buffers, stale-cache rejection, exact resume, approval hashes, no-overwrite/failure status, and final test protocol binding. CI now has a CPU ML fixture job; remote Linux CI has not been run in this task.

**Implementation and finite E001 experiment complete. Recommendation: continue data research; do not promote this model for demo/end-to-end use.** Owner remains promotion reviewer; no numeric acceptance gate is invented. Next task should propose a reviewed data version addressing within-source positive/negative coverage and independent contexts, then define the next training/evaluation contract. Any calibration/threshold work uses suitable development data; the E001 test has now been observed and must not be treated as unseen tuning feedback. Runtime S9 and real-world holdout remain separate gates.
