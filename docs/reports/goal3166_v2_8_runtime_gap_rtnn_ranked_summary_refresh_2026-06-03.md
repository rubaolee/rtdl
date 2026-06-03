# Goal3166 - RTNN v2.8 Runtime-Gap Refresh After Ranked-Summary Front Door

Date: 2026-06-03

Status: local validation complete; pod validation pending.

## Purpose

Goal3165 added the generic
`execute_ranked_summary_typed_stream_partner_columns(...)` front door and the
RTNN benchmark wrapper
`run_rtnn_v2_8_ranked_summary_typed_stream_preview(...)`. Goal3166 updates the
v2.8 benchmark runtime-gap matrix so RTNN neighbor search status matches that
new surface.

## Matrix Change

The RTNN row previously said that top-k/ranked-summary handoff still needed to
be first-class. That is no longer precise. The matrix now records:

Goal3165 establishes a ranked-summary typed-stream front door for the RTNN
neighbor-search continuation shape.

- current best path: prepared fixed-radius ranked-summary primitives with
  batched request hardening, plus the v2.8 ranked-summary typed-stream front
  door for explicit grouped top-k/arg continuation;
- partner position: `torch`/`triton` are current `grouped_topk_f64`
  continuation partners, `numba` supports grouped argmin/argmax, and CuPy
  remains an all-pairs baseline;
- current bottleneck: the ranked-summary handoff front door exists, but
  prepared packed-column residency, native typed producer evidence, and
  replay/chunking at serious scale remain unresolved;
- evidence refs: `Goal3165` is added alongside `Goal2821`, `Goal2822`, and
  `Goal2958`.

## Boundary

This refresh does not authorize RTNN paper reproduction, public speedup wording,
broad RT-core claims, true-zero-copy wording, hidden partner selection, release
packaging, or app-specific native-engine behavior.

The matrix continues to enforce:

- `release_authorized: False`
- `public_speedup_claim_authorized: False`
- `rt_core_speedup_claim_authorized: False`
- `true_zero_copy_claim_authorized: False`

## Local Validation

Command:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest `
  tests.goal3166_v2_8_runtime_gap_rtnn_ranked_summary_refresh_test `
  tests.goal3105_v2_8_benchmark_runtime_gap_map_test
```

Result: 8 tests pass.
