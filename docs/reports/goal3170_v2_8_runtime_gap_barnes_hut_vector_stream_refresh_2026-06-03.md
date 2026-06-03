# Goal3170 - Barnes-Hut v2.8 Runtime-Gap Refresh After Grouped Vector Front Door

Date: 2026-06-03

Status: local validation complete; pod validation pending.

## Purpose

Goal3169 added the generic
`execute_grouped_vector_sum_typed_stream_partner_columns(...)` front door and
the Barnes-Hut benchmark wrapper
`run_barnes_hut_v2_8_grouped_vector_sum_typed_stream_preview(...)`. Goal3170
updates the v2.8 benchmark runtime-gap matrix so the Barnes-Hut /
RT-BarnesHut-style row reflects that new generic continuation surface.

Display row: Barnes-Hut / RT-BarnesHut style.

## Matrix Change

The Barnes-Hut row previously said that frontier rows and app-owned force
vectors needed a reusable grouped-vector continuation contract. That is now too
coarse. The matrix now records:

- current best path: aggregate-frontier collect primitive plus v2.8
  grouped-vector typed-stream front door for app-owned force/vector
  continuation;
- partner position: CuPy remains the current force-vector continuation
  reference, while `torch`/`triton` are also supported by the generic front
  door;
- current bottleneck: grouped vector continuation has a generic front door, but
  native typed aggregate-frontier producer/residency evidence and force-law
  ownership boundaries at serious scale remain unresolved;
- evidence refs: `Goal3169` is added alongside the Goal2905 lineage.

## Boundary

This refresh does not authorize RT-BarnesHut paper reproduction, authors-code
comparison, public speedup wording, broad RT-core claims, true-zero-copy
wording, hidden partner selection, release packaging, native force-law math, or
app-specific native-engine behavior.

The matrix continues to enforce:

- `release_authorized: False`
- `public_speedup_claim_authorized: False`
- `rt_core_speedup_claim_authorized: False`
- `true_zero_copy_claim_authorized: False`

## Local Validation

Command:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest `
  tests.goal3170_v2_8_runtime_gap_barnes_hut_vector_stream_refresh_test `
  tests.goal3105_v2_8_benchmark_runtime_gap_map_test
```

Result: 8 tests pass.
