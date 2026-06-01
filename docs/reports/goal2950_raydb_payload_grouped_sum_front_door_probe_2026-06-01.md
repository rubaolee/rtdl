# Goal2950: RayDB Payload-Grouped Front-Door Probe

Date: 2026-06-01
Status: runner added; pod evidence pending

## Purpose

Goal2947 added a generic event-ordered RT hit-stream continuation that maps
`primitive_id` rows through caller-owned `primitive_group_ids` and
`primitive_values`, then uses an explicit CuPy partner to compute grouped sums.
Goal2948 scale-probed that continuation in isolation and found that the CuPy
consumer is not the immediate bottleneck at 1M rows.

Goal2950 moves the same front door into a benchmark-shaped path: RayDB-style
count and sum workloads. It asks a narrower design question:

Should a user force the new payload-mapped hit-stream continuation for RayDB
count/sum, or should the v2.5 planner keep using the existing primitive-first
fused grouped-reduction primitive?

## Implementation

Two changes matter:

- The generic payload-grouped front door now preserves packed RTDL ray and
  triangle buffers instead of unpacking them into Python `Ray3D`/`Triangle3D`
  objects before calling OptiX.
- `scripts/goal2950_raydb_payload_grouped_sum_front_door_probe.py` lowers
  RayDB count/sum into generic packed rays, packed triangles,
  `primitive_group_ids`, and `primitive_values`, then calls
  `rt.prepare_generic_ray_triangle_event_ordered_payload_grouped_sum_3d(...)`
  with explicit `partner="cupy"`.

Example pod command:

```text
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=build/librtdl_optix.so \
python3 scripts/goal2950_raydb_payload_grouped_sum_front_door_probe.py \
  --row-counts 250000,1000000 \
  --modes count,sum \
  --warmups 1 \
  --repeats 3 \
  --output /tmp/goal2950_raydb_payload_grouped_sum_front_door_probe.json
```

## Expected Outcome

For RayDB `count` and `sum`, primitive-first fused grouped reduction is still
expected to win because it already matches the app-agnostic operation exactly.
The payload-grouped front door is for workloads where the user needs a generic
post-RT partner continuation that is not already expressible as a fused RTDL
primitive.

This goal is therefore a planner/diagnostic hardening step, not a promotion
claim.

## Boundary

This is not a v2.5 release authorization, public speedup claim, whole-app
speedup claim, broad RT-core claim, true-zero-copy claim, automatic partner
selection claim, package-install claim, RayDB paper reproduction claim, or
app-specific native engine logic claim.
