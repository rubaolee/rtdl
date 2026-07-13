# Goal5199 Trace-Tmax Bound No-Go Result

Date: 2026-07-08

## Goal

Test a generic native OptiX cell-MBR traversal hypothesis:

```text
Instead of tracing each point query with tmax = infinity, bound ray tmax by
min(global radius, initial current-best distance) + epsilon.
```

The intended effect was to let OptiX broadphase skip far +x cell AABBs before
the custom intersection / any-hit programs run. This is a generic traversal
extent idea for point-to-cell-MBR nearest frontier, not an X-HD special case.

## Implementation Attempt

Temporarily changed `__raygen__cell_mbr_frontier3d` in
`src/native/optix/rtdl_optix_workloads.cpp` so the trace extent was:

```text
trace_tmax = min(params.radius, initial_current_best) + 1e-6
```

when an initial best witness existed, otherwise:

```text
trace_tmax = params.radius + 1e-6
```

Temporary metadata and tests were added only to validate the experiment.

## Validation

Local focused tests before the POD run:

```text
py -m unittest \
  tests.goal5199_trace_tmax_bound_test \
  tests.goal5197_intersection_attribute_lazy_row_distance_test \
  tests.goal5195_intersection_current_best_pruning_test \
  tests.goal5194_payload_current_best_pruning_test \
  tests.goal5148_native_3d_cell_mbr_frontier_test

Ran 13 tests in 1.878s
OK
```

POD:

```text
host = 213.173.108.24
port = 13502
preflight = POD_OK
GPU = NVIDIA RTX 4000 Ada Generation
build-optix = OK
POD focused tests = 13 OK
```

Full-public Level-B Dragon/HappyBuddha route was run with the same route family
as Goal5198:

```text
initial_state = local-grid-cell
grid_shape = 32,32,32
max_inline_points = 512
frontier_inline_nearest = true
collect_inline_stats = true
frontier_row_capacity = 0
skip_exact_oracle = true
```

## POD Evidence

Artifact 1:

```text
Paper-reproduction-apps/x-hd-paper/results/
  xhd_full_public_all_source_goal5199_trace_tmax_graphics_dragon_happy_buddha_2026-07-08.json

matched = true
route_wall ~= 6.824s
initial_state_seed ~= 4.959s  # cold/noisy run; not used as performance claim
native frontier / inline ~= 1.099s
inline_cell_hit_count = 3,641,962
inline_point_evaluation_count = 400,610,300
frontier_rows = 0
```

Artifact 2:

```text
Paper-reproduction-apps/x-hd-paper/results/
  xhd_full_public_all_source_goal5199_trace_tmax_final2_graphics_dragon_happy_buddha_2026-07-08.json

matched = true
route_wall ~= 2.320s
initial_state_seed ~= 0.599s
native frontier / inline ~= 0.951s
inline_cell_hit_count = 3,641,962
inline_point_evaluation_count = 400,610,300
frontier_rows = 0
```

## Result

No-go.

The key counters are unchanged from Goal5198's 32^3 telemetry:

```text
Goal5198 32^3:
  inline_cell_hit_count       = 3,641,962
  inline_point_evaluation_count = 400,610,300

Goal5199 trace-tmax final2:
  inline_cell_hit_count       = 3,641,962
  inline_point_evaluation_count = 400,610,300
```

The attempted trace extent bound did not reduce the OptiX hit set or the inline
point scan work. The warm run remained slightly slower than the current best
Goal5198 / Goal5197 line.

## Disposition

The code change was reverted locally and on the POD, and the POD native library
was rebuilt back to the mainline implementation.

Post-revert local validation:

```text
py -m unittest \
  tests.goal5197_intersection_attribute_lazy_row_distance_test \
  tests.goal5195_intersection_current_best_pruning_test \
  tests.goal5194_payload_current_best_pruning_test \
  tests.goal5148_native_3d_cell_mbr_frontier_test

Ran 11 tests in 1.685s
OK
```

Post-revert POD:

```text
build-optix = OK
```

The current default route remains unchanged:

```text
32^3 dense-lookup local-grid-cell
max_inline_points = 512
payload-current-best pruning
intersection-stage current-best pruning
intersection attribute min-distance reuse
lazy row distance computation
empty-frontier passthrough
```

## Interpretation

The remaining native inline-nearest floor is not solved by simply shortening the
ray `tmax`. Either the expanded AABB / ray configuration already yields the
same hit set, or the hit set is governed by y/z overlap and cell traversal
structure more than by far +x ray extent.

The next meaningful implementation target should not be more scalar ray extent
tuning. It should be a stronger generic inline-nearest execution model or
spatial index strategy that changes either:

- the number of inline cell hits;
- the amount of point scanning per accepted cell; or
- the ordering / grouping of work so current-best pruning becomes materially
  more effective.

## Claim Boundary

This goal does not claim:

- a performance improvement;
- author parity;
- an author-vs-RTDL performance ratio;
- exact paper dataset reproduction;
- full X-HD paper reproduction.

It is route-local no-go evidence for one generic traversal hypothesis.
