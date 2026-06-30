# Goal3177 - RayDB Runtime-Gap Refresh After Typed Producer Metadata

Date: 2026-06-03

Status: local and pod validation complete.

## Purpose

Goal3176 added typed producer metadata for the generic
`ray_triangle_grouped_i64_reduction_3d` output rows. Goal3177 refreshes the
RayDB-style grouped aggregates runtime-gap row so it no longer implies native
typed producer metadata is wholly missing.

## Matrix Change

The RayDB-style row now records:

- primitive-first fused grouped reductions remain the preferred path when the
  primitive exactly matches;
- the v2.8 grouped-reduction typed-stream front door exists for explicit
  unfused continuation;
- generic ray/triangle grouped-i64 typed producer metadata exists.

The remaining gap is narrower: device-resident output stream evidence and
broader partner conformance without overriding fused primitive-first paths.

## Boundary

This refresh does not authorize release packaging, public speedup wording,
broad RT-core claims, true-zero-copy wording, automatic partner selection, or
app-specific native-engine behavior.

The current grouped-i64 producer metadata still records host-materialized output
rows. Device-resident output stream evidence remains future work.

The matrix continues to enforce:

- `release_authorized: False`
- `public_speedup_claim_authorized: False`
- `rt_core_speedup_claim_authorized: False`
- `true_zero_copy_claim_authorized: False`

## Validation

Focused local validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest `
  tests.goal3177_v2_8_runtime_gap_raydb_typed_producer_refresh_test `
  tests.goal3163_v2_8_runtime_gap_raydb_typed_stream_refresh_test `
  tests.goal3105_v2_8_benchmark_runtime_gap_map_test
```

Result: 10 tests passed locally.

Focused pod validation:

```bash
cd /root/rtdl_goal3151
git fetch origin main
git reset --hard origin/main
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so \
  /root/venvs/rtdl_goal3154/bin/python -m unittest \
  tests.goal3177_v2_8_runtime_gap_raydb_typed_producer_refresh_test \
  tests.goal3163_v2_8_runtime_gap_raydb_typed_stream_refresh_test \
  tests.goal3105_v2_8_benchmark_runtime_gap_map_test
```

Pod result: commit `3079637b`, 10 tests passed.
