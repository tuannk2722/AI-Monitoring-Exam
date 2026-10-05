# E001-IMPLEMENT-20261006 — Approved local classifier baseline

- Status / area / priority: Done / P3 reviewed-crop baseline implementation and execution / high.
- Owner/reviewer: repository owner; Codex implementation/research/analysis, no delegation.
- Authorization: user explicitly approved the complete training-readiness proposal and requested persistence to completion. ADR014 records the bounded model/config/local CPU decision.

## Goal and result
Implemented E001 contract/config/approval, frozen ResNet18 masked two-label classifier, transform/cache, train/eval, metrics, checkpoint/resume, provenance, tests and runbook. Ran actual smoke with interruption/resume, full baseline and one final test after hash-bound candidate/protocol freeze. Results: docs/experiments/E001-results.md; detailed evidence artifacts/reports/E001. Implementation complete; no model quality/promotion claim.

## Source of truth / docs read
Index/TASK, AGENTS, approved readiness report; training map04/09/10/15/22/23/24,ADR004/012/013,governance21,release contract/runbook, experiment/task templates; current config/provenance/errors/inference/schema/package/test conventions, requirements/pyproject/CI/ignore/checker. Official torch/torchvision supported pair and versioned source/license; previous primary-source research retained. ADR014/config/approval added from explicit current user authorization, not inferred from silence.

## Exact inputs / identities
Pilot-b-20261005-v4 / pilot-b-explicit-scene-split-v1 / pilot-b-targets-v1:112ledger,84manifest60/13/11,28review_only,16groups. Payload SHA dbc1bf90a5605cac39b5c96503e71097ecd1eaab5b35e14f311f966edd503f53 unchanged. Pretrained SHA f37072fd47e89c5e827621c5baffa7500819f7896bbacec160b1a16c560e07ec.
Code commit45240ea6234c70a80ecf3dc11f2e69eb8e253a53, clean detached worktree outputs/E001-code, fresh env outputs/E001-env. Run records git_dirty=false. Final protocol committed84d4cf0d51564af971851e72cf4e37e3afe59fa4 before test. No Git push. User deletion docs/reviews/codebase-review-20261005.md remains uncommitted/preserved.

## Deliverables / changed files
src/ai_exam_monitoring/training modules; tests/test_training.py; configs/experiments/E001+smoke; classifier optional dependencies and CPU requirements/lock; CPU ML CI job; ADR014, approval/final protocol/runbook/results; current README/index/04/09/10/22/preparation runbook/WORKLOG; small evidence artifacts/reports/E001; four outputs/*.dvc pointers. Ignore permits only root outputs/*.dvc while binaries/media/env/worktree stay ignored. Original readiness proposal preserved as approved snapshot.

## Execution / verification
Fresh CPU environment pip check and126 tests PASS (13 ML); local Ruff/compile/repo/diff checks PASS. Full payload/schema/freeze and source/artifact SHA checks PASS.73 train/val transformed crops visually QAed; no relabel. Smoke interrupted epoch1, resumed identically to3; independent unit resume matches uninterrupted state/history. Full E001 early stopped32, best12;5.827s routine/470712320bytes peak RSS. Validation checkpoint reload scores/metrics exact. Final test once, no subsequent model/config/threshold changes. Test metadata/label/split bytes unchanged.
Local DVC status PASS; restored38 files (baseline/smoke/test/pretrained) from local cache objects into outputs/E001-cache-restore; MD5/SHA exact. No remote push/upload or claim of remote recovery. Remote Linux CI not executed.

## Observation / decision / remaining scope
At0.5 val/test phone predicts all known records positive; looking predicts all known records negative. AP is high with tiny/source-confounded support, not evidence of usable decisions. Recommend continue data research; owner remains promotion reviewer. TBD-METRIC-01, within-source coverage, independent holdout and automatic crop S9 remain later gates, not incomplete E001 engineering work. E001 test has been observed: never treat it as unseen tuning feedback.

## Resume / handoff
Updated2026-10-06. Read index/TASK and inspect Git/artifacts before new work. Do not rerun E001/test or tune thresholds to improve the report. Existing outputs intentionally reject overwrite. Next separately scoped task should propose data improvements and evaluation plan; dataset mutations need new version/review. Preserve outputs/E001, E001-smoke, E001-final-test and pretrained plus DVC cache/pointers. Cache-restore and isolated env/checkout are task-generated verification resources; no unrelated historical artifacts removed.
