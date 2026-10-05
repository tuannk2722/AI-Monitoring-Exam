# PILOT-B-HANDOFF-20261005 - Commit and Drive handoff

- Status / area / priority: In progress / release closeout / high.
- Owner: repository owner; Codex implements without delegation.
- Latest request: fix checker/current docs, commit approved implementation and smoke cleanup, authorize restricted Drive upload of v4 and verify exact-commit clean-cache pull, leave Git clean.

## Goal and scope
Finish the existing pilot release handoff. Preserve immutable v4, labels/splits/test freeze and pinned historical evidence. No new trainer, model choices, dashboard or generic framework; no Git remote push requested.

## Sources read
AGENTS, docs index/previous TASK/template; ADR-005/013 and governance 21, environment 22; current README/architecture/P2/P3/runbook; checker/tests, Git inventory, DVC pointer/config and installed DVC/PyDrive code. Prior whole-codebase audit recorded in WORKLOG.

## Input and versions
HEAD d8599b588140d4847a8e1a07878274e4d6cb87c3. Approved canonical data/processed/pilot-b/pilot-b-20261005-v4; configs/datasets/pilot_b_release_v4.yaml. Payload list SHA dbc1bf90a5605cac39b5c96503e71097ecd1eaab5b35e14f311f966edd503f53. Local pointer MD5 563958778204fa60d6015656595c19dd.dir. Existing remote teamdrive. Smoke fixture already removed locally, tracked deletions pending.

## Deliverables and acceptance
Narrow checker exception/tests, current-status docs and scoped operational upload approval outside immutable payload, reviewed staged source/config/docs/evidence/pointer without media/secrets, release commit, targeted DVC push and exact-commit clone with fresh empty independent cache pull. Verify full payload/checksums/schema/freeze; record concise evidence in existing WORKLOG/runbook, commit final closeout and require empty git status.

## Decisions and limits
User now explicitly requests Drive handoff for v4; record scoped authorization for restricted existing teamdrive only, not redistribution/W&B/raw/history uploads. Check Drive ACL before media upload; if public/domain-wide or uncertain, ask owner while completing independent changes. Retain immutable approvals and v4 scope snapshot, document later storage permission separately. No silent data version or model decisions.

## Plan / checkpoint
1. Inspect references and staging candidates; fix checker and current docs. 2. Verify unchanged v4 and remote access; stage exact intended files, validate, commit. 3. Targeted upload; clone exact commit/cache-empty pull and verify; remove temporary clone only after evidence recorded. 4. Commit final evidence/checkpoint; confirm Git clean.
Cleanup considers references: sources/parents/history used by pinned builds are preserved; remove only proven disposable duplicates and transient artifacts. Do not erase Git history or remote cache with GC. Completed: restricted Drive ACL verified (single user/owner); narrow checker regression test and current docs updated; .gitattributes preserves receipt/report bytes and pilot code/config LF across checkouts. Seven checksum-identical ignored rebuild copies removed (~262.8 MB), source/config references checked; canonical parents/source inputs preserved.
Validation PASS: 109 unittest, Ruff, compileall, pip check, staged checker/diff checks, 24 staged Markdown link checks, report JSON parsing. Staged set 68 files: reviewed source/config/docs/evidence/metadata + smoke tracked deletions, no media/credential. Fourteen staged exact SHA pins (producer/config/approval/report) match unchanged v4. Payload/schema/freeze/source/crop pixel/hash preflight and local DVC status PASS.
Resume checkpoint: implementation committed at 97b90ebfe0e8f5457ac5c783205c98be02925866; root Git clean. Targeted upload completed: 125 files pushed. Clone outputs/pilot-b-dvc-roundtrip-20261005-v4 at exact commit, new independent .dvc/cache confirmed empty and dataset absent before pull; cloned config/approval pins passed. Pull completed: 125 files fetched and 124 files added. Full payload/checksum inventory, schema/usage/split/test freeze, config/approval/8 cloned producer pins, restored Git clean and DVC status all PASS at commit 97b90eb.
Clean-clone tests exposed two SCB tests assuming ignored outputs/ exists. Fixed two test fixtures to use TemporaryDirectory(dir=workspace), avoiding any ignored outputs/ prerequisite; producer/data/approved config bytes unchanged. Rerun complete tests and lint, commit fix, then verify a fresh checkout at that commit. Commit test fix/current evidence; verify final exact commit via clean checkout/cache before removing temporary clone. No owner question pending. Previous interruption was auto-review usage-limit failure, no unsafe-action ruling; resumed tool access works.
