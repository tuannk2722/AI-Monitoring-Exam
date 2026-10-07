# E002 — Runbook đã được owner duyệt

Ngày 2026-10-07. Owner/reviewer: chủ repository (solo). [ADR-015 Accepted](../decisions/ADR-015-e002-v5-preservation-linear-probe.md), [approval](E002-approval.json), [protocol đã review](E002-protocol.md). Proposal/preparation giữ snapshot lịch sử; trạng thái pending/blocker trong snapshot không thay approval hiện hành.

## Phạm vi thực hiện

Giữ exact resolved configs E002/E002-smoke và package accepted Pilot B v5; chạy CPU local bằng môi trường E001 đã pin. Loader hỗ trợ inline freeze v4 hoặc preservation pointer v5 có xác minh owner/parent/semantic/manifest/ledger/split; không đổi recipe hoặc dữ liệu. Full suite, Ruff, dependency check và preflight phải PASS trước chạy.

Tạo local implementation commit trên branch experiment riêng, rồi clean detached worktree `outputs/E002-code`. Code/import/cwd lấy checkout đó; workspace dữ liệu/weights/approval là repository gốc. EOL của config/protocol/approval E002 giữ LF để bảo toàn byte pins qua checkout; logical config digest cũng phải giữ nguyên. Không Git push hoặc upload.

## Lệnh chạy

Từ clean worktree `D:\ai-exam-monitoring-final\outputs\E002-code`, dùng Python CPU environment đã có. Output phải chưa tồn tại trước start; resume chỉ cùng identity.

```powershell
$env:PYTHONPATH = Join-Path (Get-Location) 'src'
$e002Python = 'D:\ai-exam-monitoring-final\outputs\E001-env\Scripts\python.exe'
$e002Workspace = 'D:\ai-exam-monitoring-final'
& $e002Python -m ai_exam_monitoring.training.train --config configs/experiments/E002-smoke.yaml --workspace $e002Workspace --output "$e002Workspace/outputs/E002-smoke" --interrupt-after 1
& $e002Python -m ai_exam_monitoring.training.train --config configs/experiments/E002-smoke.yaml --workspace $e002Workspace --output "$e002Workspace/outputs/E002-smoke" --resume
& $e002Python -m ai_exam_monitoring.training.train --config configs/experiments/E002.yaml --workspace $e002Workspace --output "$e002Workspace/outputs/E002"
& $e002Python -m ai_exam_monitoring.training.evaluate --workspace $e002Workspace --run "$e002Workspace/outputs/E002" --split val --output "$e002Workspace/outputs/E002-val-evaluation"
```

Smoke interruption sau epoch1 phải ghi `INTERRUPTED`, giữ last/checksums; resume đến3 epoch phải `FINISHED`. Không dùng metrics smoke để tuning/chọn candidate. E002 giữ seed42/max200/patience20/min_delta0.0001; best bằng raw minimum val BCE và tie sớm. Evaluator val phải tái lập predictions/metrics của best.

## Kiểm chứng và bàn giao

Lưu code commit/hash và clean state, environment/pip-freeze, config/dataset/split/encoding/weights pins, start/end/status/commands, best/last/cache/history/metrics/predictions/checksums và observation/decision. Báo cáo so E001 chỉ train/val; error analysis dùng predictions đã freeze, không relabel/tuning. Metrics E002 chỉ được ghi sau run thật.

Kiểm mọi checksum artifact và package v5/v4 sau run, không có test feature/prediction; dừng ở validation theo protocol. Nếu dùng DVC, chỉ add/cache/restore local và pointer để bảo toàn binary; quyền upload vẫn chưa có. Model promotion/holdout/final-test là quyết định riêng. Báo cáo triển khai/kiểm chứng tại [E002 execution](../../artifacts/reports/E002-execution-20261007/README.md); experiment card `docs/experiments/E002-results.md` được tạo sau khi hoàn tất.
