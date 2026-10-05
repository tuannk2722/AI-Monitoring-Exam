# REVIEW-20261005 — Codebase and artifact lifecycle review

- Status / area / priority: Done / repository quality and dataset lifecycle / high.
- Owner: repository owner; Codex implements without delegation.
- Base commit: 3a103a43f71f6947677d7ba25e1b075117bb9bdf; initially clean.

## Goal and result
Deep review against AGENTS/spec, code organization and generated artifacts, with justified fixes and cleanup. Durable findings and storage map: docs/reviews/codebase-review-20261005.md. Evidence/owner approvals also in docs/WORKLOG.md.

## Sources read
AGENTS/index/previous TASK/task template; canonical docs01–25 (P2 relevant scope), ADR001–013; pilot contract/runbook; label/split/annotation specs and dataset research; README/pyproject/CI/requirements/ignore attributes; Git inventory and caller searches; data schema/package/input/selection/preparation/group/proposal/importers, audit/review/overlay/source/YOLO/conversion/split/manifest; contracts/config/provenance, legacy train/evaluate/benchmark and inference; affected tests; real v4 payload and preparation inventories/hash lineage. No visual relabel or new license audit.

## Owner decisions and constraints
Owner explicitly chose removal of train/eval A after dependency checks; required finite positive FPS without schema change; approved metadata archive then deletion of four duplicate preparation trees. No new dataset/label/split/model/threshold decisions, training or upload. Frozen v4/source/evidence/config unchanged.

## Deliverables / files changed
Removed 8 legacy train/eval/benchmark/config/pipeline files and unused validator/tests. Fixed FPS/no-overwrite, bbox finite/space, split finite and missing prohibited label. Checker now requires B schema/package/release config/pointer. Updated current docs and added review report/inference tests. No pilot producer/config/approval changes.

## Artifact cleanup and restore
Removed four versions under data/processed/pilot-b: pilot-b-20261004-v1 and preparation-r2/r3/r4 (604 files,320971311 bytes). Archived release.json/checksums verbatim per version plus inventory/RESTORE in outputs/pilot-b-preparation-history-20261005.zip (42579 bytes, SHA af71803ebc46ea89f3f38f5925246f748ea373f8128a208526e9117ce147969c). Full original payload verification and virtual restore PASS. Archive depends on retained r5; preserve r5→v2→v3→v4 and frozen interim. Additional synthetic fixtures/evidence duplicate cleanup79211 bytes. No remote/cache/source deletion.

## Validation
Baseline109 tests; final113 PASS (2 obsolete removed,6 regressions added). Ruff/compileall/check_repo --require-git/diff check PASS. DVC target status up to date. V4 verify_payload/read_records/manifest/split/test subset/test IDs PASS;112 ledger84used60/13/11,28review_only. Payload checksum SHA dbc1bf90a5605cac39b5c96503e71097ecd1eaab5b35e14f311f966edd503f53. Git pointer SHA f9f249f1f7bee62690e24f8bb437952c855866c9f7828da5af195d8c770564ef; worktree CRLF semantically/normalized byte-identical. Final diff inspected. No commit/push.

## Risks / unresolved / next task
No pending owner questions. ML B trainer/config/model/license/loss and runtime S9 remain separate gates. Dependency lock/fresh install/Linux/GPU not verified. Other historical evidence/extracted sources retained; source replay paths are machine-dependent. Report distinguishes technical tests from model quality. New task/resume must reread index/checkpoint and verify Git/artifacts rather than reopening approved decisions.
