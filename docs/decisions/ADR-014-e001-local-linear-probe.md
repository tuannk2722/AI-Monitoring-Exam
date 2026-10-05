# ADR-014 — E001 reviewed-crop local linear probe

- Status: Accepted for the explicitly approved E001 proposal.
- Date: 2026-10-06. Owner: repository owner; implementation: Codex.
- Evidence: owner message: “Đồng ý cho AI agent triển khai E001 theo đúng đề xuất trong training-readiness-20261006.md”; requested execution through completion.
- Scope: the [approved proposal](../reviews/training-readiness-20261006.md), including local CPU pilot, ResNet18 IMAGENET1K_V1 frozen encoder, two-label linear head, masked per-target BCE, fixed train/val/test, seed and optimizer/budget/transforms/evaluation described there.

This supplements ADR-004 for this small CPU experiment. It does not replace the GPU/Colab direction for subsequent work. Model selection uses validation only; no test-driven changes. No automatic runtime crop, model promotion threshold, cloud processing, dataset mutation or expanded remote media permission is granted.

Codex may resolve routine implementation details, pin a compatible CPU dependency pair, validate exact model provenance, and run smoke/baseline locally. A single final E001 candidate may be evaluated only after recording its checkpoint/config/code/data hashes and the fixed evaluation protocol; no subsequent tuning using that test result.

Weights implementation: TorchVision BSD-3-Clause. Pretrained terms are separately documented in the E001 runbook; academic local research only, no new assertion of redistribution/commercial deployment rights. Do not train random weights if the pretrained download is unavailable or corrupted.
