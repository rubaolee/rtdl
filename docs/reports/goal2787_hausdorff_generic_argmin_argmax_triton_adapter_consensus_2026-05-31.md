# Goal2787 Consensus - Hausdorff Generic Argmin/Argmax Triton Adapter

Date: 2026-05-31

## Inputs

- Codex implementation and validation report:
  `docs/reports/goal2787_hausdorff_generic_argmin_argmax_triton_adapter_2026-05-31.md`
- Pod artifact:
  `docs/reports/goal2787_pod_artifacts/goal2787_hausdorff_generic_argmin_argmax_pod_69_30_85_171_2026-05-31.json`
- Gemini independent review:
  `docs/reviews/goal2787_gemini_review_hausdorff_generic_argmin_argmax_triton_adapter_2026-05-31.md`

## Consensus

Codex + Gemini agree on `accept-with-boundary`.

Goal2787 is accepted as a v2.5 wiring and correctness step: the Python-side
Hausdorff/X-HD wrapper now composes the generic continuation operations
`grouped_argmin_f64` and `grouped_argmax_f64` through
`group_argmin_then_global_argmax_partner_columns(...)`. The reusable Triton
continuation substrate remains app-name-free and does not contain
Hausdorff/X-HD vocabulary.

The consensus boundary is negative performance evidence. The pod artifact on
the NVIDIA RTX A5000 measured the generic two-kernel Triton path as 31.880x to
45.145x slower than the Torch same-contract branch for dense exact
Hausdorff-style witness reductions. Therefore Goal2787 blocks blind automatic
Triton selection for that workload shape and keeps optimized Torch, CuPy, CUDA,
or another explicitly selected same-contract partner as the current performance
path until a fused or tiled generic witness-reduction design earns better
evidence.

## Non-Claims

This consensus does not authorize:

- public speedup claims;
- RT-core speedup claims;
- true zero-copy claims;
- whole-app speedup claims;
- v2.5 release readiness;
- Hausdorff-specific native or Triton continuation code.

This is not a v2.5 release gate closure. It is a reviewed v2.5 substrate and
partner-selection guidance update.
