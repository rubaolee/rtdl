# Goal3176 - Ray/Triangle Grouped-I64 Typed Producer Metadata

Date: 2026-06-03

Status: local implementation ready for focused validation.

## Purpose

The v2.8 grouped-reduction front door can already consume caller-supplied
partner columns. The RayDB-style runtime-gap row still correctly called out a
separate native producer issue: the generic ray/triangle grouped-i64 reduction
result did not expose a v2.8 typed producer contract.

Goal3176 adds typed producer metadata for
`ray_triangle_grouped_i64_reduction_3d` without changing native kernels or
changing app semantics.

## What Changed

- Added `make_v2_8_ray_triangle_grouped_i64_reduction_typed_stream_contract(...)`.
- Attached `typed_result_stream` and `v2_8_typed_producer_metadata` to generic
  ray/triangle grouped-i64 reduction outputs.
- Covered CPU reference output and the generic prepared Embree/OptiX wrapper
  paths through the shared metadata attachment.

## Boundary

This is a metadata/contract hardening goal. It does not change kernels,
promote a partner path, authorize release wording, authorize public speedup,
authorize broad RT-core wording, or authorize true zero-copy.

The current producer output is explicitly host-materialized grouped rows.
device-resident output remains future work.

Claim flags remain blocked:

- `release_authorized: False`
- `public_speedup_claim_authorized: False`
- `rt_core_speedup_claim_authorized: False`
- `true_zero_copy_claim_authorized: False`

## Validation

Focused local validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest `
  tests.goal3176_ray_triangle_grouped_i64_typed_producer_metadata_test `
  tests.goal3162_raydb_grouped_reduction_typed_stream_front_door_test `
  tests.goal2684_generic_rt_hit_stream_handoff_test
```

Result: 11 tests passed locally, 1 CUDA-gated test skipped.
