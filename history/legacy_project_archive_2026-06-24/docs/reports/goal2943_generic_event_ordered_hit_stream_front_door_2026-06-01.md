# Goal2943: Generic Event-Ordered Hit-Stream Front Door

Date: 2026-06-01
Status: implemented and pod-smoked

## Purpose

Goal2943 makes the existing v2.5 event-ordered hit-stream grouped-reduction
runtime easier for users to reach from the public Python language surface.

The new front door is:

`rt.run_generic_ray_triangle_event_ordered_grouped_ray_id_reduction_3d(...)`

It accepts generic 3-D rays and triangles, runs RTDL/OptiX traversal, and
executes the existing event-ordered CuPy grouped reduction over generic
`ray_id` and `primitive_id` columns. This is the user-facing version of the
runtime direction we keep discussing: RT cores produce generic primitive
payloads, then an explicit Python partner consumes them under a bounded contract.

## Design

The function is deliberately app-agnostic:

- grouping key: `ray_id`
- reduced value: `primitive_id`
- operation: `hit_stream_grouped_ray_id_primitive_i64`
- backend: `optix`
- executable partner today: `cupy` / `cupy_conformance`

Typical call shape:

`rt.run_generic_ray_triangle_event_ordered_grouped_ray_id_reduction_3d(..., partner='cupy')`

Triton and Numba fail closed for this operation because the v2.5 support matrix
does not yet declare executable kernels for this event-ordered hit-stream
consumer. That is important: the user may choose partners, but RTDL must not
silently reroute through a different partner or hide a copy.

The front door can optionally return the device buffers:

`return_device_buffers=True`

When enabled, the caller owns and must close the returned hit-stream and grouped
reduction buffers. This makes the path useful for advanced users who want to
continue with their own partner code after the RTDL primitive.

## Boundary

This is a user-facing front door and pod-validation target, not a release claim.
It is not a true-zero-copy claim.
It is not a public speedup claim.
It is not a whole-app acceleration claim.
It is not a paper-reproduction claim.
It does not add app-specific logic to the native engine.

The producer and consumer are event ordered, and the partner reads
device-resident hit-stream status and rows before host scalar or row
materialization. The final summary still materializes to the host, and the
claim remains scoped to the bounded CuPy event-ordered grouped consumer.

## Validation Plan

Local focused gate:

```text
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal2943_generic_event_ordered_hit_stream_front_door_test tests.goal2771_hit_stream_event_ordered_grouped_reduction_consumer_test tests.goal2772_hit_stream_event_ordered_grouped_richer_reductions_test
```

Pod smoke:

```text
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=build/librtdl_optix.so \
python3 scripts/goal2943_generic_event_ordered_hit_stream_front_door_smoke.py \
  --output /tmp/goal2943_front_door_smoke.json
```

Expected smoke result:

- row count: `4`
- group hit counts: `[2, 0, 2]`
- group primitive-id sums: `[1, 0, 1]`
- selected partner: `cupy_conformance`
- stream ordering: `cuda_event_cross_stream`
- true-zero-copy/public-speedup flags: `false`

## Validation

Local focused gate:

```text
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal2943_generic_event_ordered_hit_stream_front_door_test tests.goal2771_hit_stream_event_ordered_grouped_reduction_consumer_test tests.goal2772_hit_stream_event_ordered_grouped_richer_reductions_test tests.goal2806_v2_5_internal_readiness_packet_test

Ran 24 tests
OK (skipped=3)
```

Pod smoke:

- SSH target: `root@69.30.85.171 -p 22167`
- source commit: `1a487903ab10812b192879b1be3ab211a7628dd4`
- source dirty entries: `0`
- artifact: `docs/reports/goal2943_generic_event_ordered_hit_stream_front_door_pod/goal2943_front_door_smoke.json`
- status: `pass`
- row count: `4`
- group hit counts: `[2, 0, 2]`
- group primitive-id sums: `[1, 0, 1]`
- selected partner: `cupy_conformance`
- stream ordering: `cuda_event_cross_stream`

The pod smoke validates that a user can call the public RTDL front door and get
the event-ordered RT producer plus CuPy grouped consumer without using the
lower-level prepared-scene methods directly.
