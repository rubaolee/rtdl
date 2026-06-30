# Goal3704 Segment-Pair Prepared-Left Exact Count Route

Date: 2026-06-07

## Purpose

Goal3702 showed that the one-pass exact segment-pair scalar-count path removes candidate materialization and host exact refinement, but the repeated-query timing still pays left-segment upload inside each scalar-count call.

Goal3704 adds a generic prepared-left scalar-count route:

```text
prepare right once + prepare left once -> repeated one-pass exact scalar counts
```

## Change

Updated:

- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/rtdsl/optix_runtime.py`
- `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`
- `scripts/goal3612_rayjoin_safe_mixed_route_composite.py`

The native prepared-left handle now stores:

- the float candidate segment buffer,
- the exact double `RtdlSegment` buffer.

The new C ABI is:

```text
rtdl_optix_count_prepared_segment_pair_intersection_prepared_left
```

The Python runtime exposes:

```text
PreparedOptixSegmentPairIntersection.count_prepared_left(prepared_left)
```

The RayJoin benchmark helper opts into the route explicitly with `prepare_left_for_count=True` and records that choice in artifacts.

## Boundary

This is not a RayJoin-specific engine path. The engine sees only prepared generic segment-pair handles. RayJoin interpretation remains in Python.

This implementation note requires pod evidence before it is accepted.

It does not authorize:

- release,
- default-route promotion,
- RTDL-beats-RayJoin claims,
- RayJoin paper reproduction claims,
- public speedup claims,
- broad RT-core claims,
- true zero-copy claims.

