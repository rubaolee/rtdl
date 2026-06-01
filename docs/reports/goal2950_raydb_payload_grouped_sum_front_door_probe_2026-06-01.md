# Goal2950: RayDB Payload-Grouped Front-Door Probe

Date: 2026-06-01
Status: pod diagnostic passed

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

## Pod Results

Pod target: `root@69.30.85.171 -p 22167`

Source commit: `38f7302cf7e4cf91d5ae02aaae09eecb318d244c`

Artifact:

`docs/reports/goal2950_raydb_payload_grouped_sum_front_door_probe_pod/goal2950_raydb_payload_grouped_sum_front_door_probe.json`

| Rows | Mode | Query rays | Payload front door sec | Primitive-first sec | Payload / primitive-first | Consumer sec | Native enqueue sec |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `250000` | `count` | `110592` | `0.009484` | `0.000345` | `27.460x` | `0.001856` | `0.006886` |
| `250000` | `sum` | `4755456` | `0.291365` | `0.000938` | `310.743x` | `0.023817` | `0.264591` |
| `1000000` | `count` | `110592` | `0.006293` | `0.000287` | `21.914x` | `0.001371` | `0.003824` |
| `1000000` | `sum` | `4755456` | `0.309383` | `0.001589` | `194.724x` | `0.029135` | `0.275000` |

All rows matched the CPU reference, and the pod source tree was clean.

## Design Decision

The packed-input fix is valuable: `query_pack` is now effectively zero in the
payload front-door timing. But this benchmark also confirms the planner rule:
RayDB `count` and `sum` should not force the generic hit-stream continuation
when an exact fused RTDL primitive already exists. The fused primitive is one to
two orders of magnitude faster for this workload.

The next performance work should therefore not be "make RayDB count/sum use the
payload front door." It should be:

- keep primitive-first selection for count/sum/min/max/sum-count reductions;
- use payload-mapped hit streams for richer continuations that cannot be fused;
- add a planner guard so users get an explanation when they request a slower
  hit-stream continuation for an operation already covered by a fused primitive.

## Boundary

This is not a v2.5 release authorization, public speedup claim, whole-app
speedup claim, broad RT-core claim, true-zero-copy claim, automatic partner
selection claim, package-install claim, RayDB paper reproduction claim, or
app-specific native engine logic claim.
