# Goal3163: v2.8 Runtime-Gap RayDB Typed-Stream Refresh

Date: 2026-06-03

Status: `implemented`

## Purpose

Goal3162 added a generic
`execute_grouped_reduction_typed_stream_partner_columns(...)` front door and
wired a RayDB-style typed-stream preview through it. The v2.8 runtime-gap matrix
needed to distinguish what is now solved from the remaining work.

## Change

Updated the `raydb_style` row in `src/rtdsl/v2_8_benchmark_runtime_gap.py`:

- `current_best_path` now records both primitive-first fused grouped reductions
  and the v2.8 grouped-reduction typed-stream front door for explicit unfused
  partner continuation.
- `current_bottleneck` now points to native typed producer/residency evidence and
  broader partner conformance.
- `evidence_refs` now includes `Goal3162`.

## Boundary

This is a status/matrix refresh only. It does not promote partner continuation
over fused primitive-first paths and does not authorize release, speedup,
RT-core, true-zero-copy, hidden dispatch, or automatic partner-selection claims.

## Validation

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3163_v2_8_runtime_gap_raydb_typed_stream_refresh_test tests.goal3105_v2_8_benchmark_runtime_gap_map_test
.......
----------------------------------------------------------------------
Ran 7 tests in 0.016s

OK
```

Clean pod validation:

```text
POD_HEAD=2b726d71
RUN_GOAL3163_RAYDB_GAP_REFRESH
.......
----------------------------------------------------------------------
Ran 7 tests in 0.001s

OK
```
