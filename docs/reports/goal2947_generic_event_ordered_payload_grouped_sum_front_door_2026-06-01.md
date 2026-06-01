# Goal2947: Generic Event-Ordered Payload Grouped-Sum Front Door

Date: 2026-06-01
Status: implemented and pod-smoked

## Purpose

Goal2947 adds the next generic v2.5 RT-stream continuation after Goal2943. Goal
2943 exposed event-ordered grouped reductions over raw `(ray_id, primitive_id)`
hit rows. Goal2947 lets a user provide generic primitive payload columns:

- `primitive_group_ids[primitive_id]`
- `primitive_values[primitive_id]`

RTDL/OptiX still produces the generic hit stream. A bounded CuPy consumer waits
on the producer CUDA event, maps each hit `primitive_id` through the payload
columns, and writes dense grouped outputs:

- `group_hit_counts`
- `group_payload_sums`

No app terms are added to the native engine. This is a generic payload-mapped
row-stream continuation that apps can use for RayJoin-style, physics-style, or
other user-defined reductions outside the engine.

## Public Surface

New front doors:

- `rt.prepare_generic_ray_triangle_event_ordered_payload_grouped_sum_3d(...)`
- `rt.run_generic_ray_triangle_event_ordered_payload_grouped_sum_3d(...)`

New partner continuation operation:

- `hit_stream_primitive_payload_grouped_sum_f64`

Current executable partner:

- `cupy` / `cupy_conformance`

Triton and Numba fail closed for this operation until their own executable
same-contract kernels exist.

## Boundary

This is not a v2.5 release authorization, public speedup claim, broad RT-core
claim, whole-app speedup claim, true-zero-copy claim, automatic partner
selection claim, package-install claim, paper-reproduction claim, or
app-specific native engine logic claim.

The implementation proves a bounded event-ordered CuPy continuation shape. It
does not prove arbitrary partner continuation, broad zero-copy, or large-scale
performance superiority.

## Validation

Local focused gate:

```text
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal2947_generic_event_ordered_payload_grouped_sum_front_door_test tests.goal2662_v2_5_partner_continuation_contract_test tests.goal2671_v2_5_preview_gate_test tests.goal2774_v2_5_grouped_hit_stream_support_matrix_test tests.goal2794_v2_5_determinism_policy_test tests.goal2873_v2_5_partner_conformance_matrix_test
```

Pod smoke command:

```text
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=build/librtdl_optix.so \
python3 scripts/goal2947_generic_event_ordered_payload_grouped_sum_front_door_smoke.py \
  --output /tmp/goal2947_payload_grouped_sum_smoke.json
```

Expected pod smoke:

- row count: `4`
- group hit counts: `[2, 0, 2]`
- group payload sums: `[21.0, 0.0, 2.5]`
- operation: `hit_stream_primitive_payload_grouped_sum_f64`
- selected partner: `cupy_conformance`
- stream ordering: `cuda_event_cross_stream`
- claim flags: all false

Imported pod artifact:

`docs/reports/goal2947_generic_event_ordered_payload_grouped_sum_front_door_pod/goal2947_payload_grouped_sum_smoke.json`

Observed pod result:

- SSH target: `root@69.30.85.171 -p 22167`
- source commit: `c3c7f7c494068f6bac936a931b3b281f96ba3cbc`
- source dirty entries: `0`
- status: `pass`
- elapsed: `2.792s`
- row count: `4`
- group hit counts: `[2, 0, 2]`
- group payload sums: `[21.0, 0.0, 2.5]`
- selected partner: `cupy_conformance`
- producer/consumer ordering: `cuda_event_cross_stream`
- device status read before host scalar: `true`
- host row materialization before consumer: `false`
- true-zero-copy/public-speedup/release/whole-app flags: `false`
