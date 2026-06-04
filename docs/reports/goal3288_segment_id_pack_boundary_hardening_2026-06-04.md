# Goal3288 Segment ID Pack Boundary Hardening

Date: 2026-06-04

## Context

Claude's Goal3286 review accepted the Goal3278-3285 spatial-order and fused
pack chain with boundary, and flagged one required hardening item before the
fused path should be treated as a general-purpose tool:

> the NumPy fast path used `uint32` IDs during ordering, which could silently
> truncate wide caller IDs before packing.

## Change

Goal3288 hardens the segment-packing boundary:

- `segment_columns_2d(...)` now keeps segment IDs as signed 64-bit values in
  the column batch instead of narrowing them to `uint32`.
- The fused ordered pack path keeps IDs wide while sorting.
- `_segment_id_to_packed_u32(...)` validates every ID before writing the native
  `_RtdlSegment` packet.
- Out-of-range or negative IDs now fail closed with:
  `segment ids must fit the uint32 packed segment ABI`.

This preserves the existing native ABI while preventing silent wraparound.

## Validation

Local focused validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest `
  tests.goal3285_fused_segment_pack_order_mode_test `
  tests.goal3287_segment_columns_2d_layout_test `
  tests.goal3287_segment_columns_pod_evidence_test `
  tests.goal3285_fused_segment_pack_ordering_pod_evidence_test `
  tests.goal3073_v2_7_generated_primitive_catalog_test `
  tests.goal3090_v2_7_discovery_metadata_backfill_test `
  tests.goal3207_packed_left_rayjoin_compact_route_test `
  tests.goal3212_dense_left_id_count_rayjoin_route_test
```

Result: 40 tests passed.

Additional checks:

```powershell
py -3 -m py_compile src\rtdsl\segment_columns.py src\rtdsl\embree_runtime.py `
  tests\goal3285_fused_segment_pack_order_mode_test.py `
  tests\goal3287_segment_columns_2d_layout_test.py
git diff --check -- src\rtdsl\segment_columns.py src\rtdsl\embree_runtime.py `
  tests\goal3285_fused_segment_pack_order_mode_test.py `
  tests\goal3287_segment_columns_2d_layout_test.py
```

## Boundary

No native ABI changed. No performance claim changed. No release, RayJoin
reproduction, RTDL-beats-RayJoin, true-zero-copy, or broad RT-core claim is
authorized.
