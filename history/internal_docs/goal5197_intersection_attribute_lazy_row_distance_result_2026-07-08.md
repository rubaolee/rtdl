# Goal5197 - Intersection Attribute And Lazy Row Distance

## Status

`implemented_review_pending`

Goal5197 tests a generic native OptiX cell-MBR traversal micro-optimization.
The intersection program already computes the query-to-cell minimum squared
distance (`min_sq`) for pruning. Before this goal, the any-hit program computed
the same `min_sq` again, and it also computed row-only values (`max_sq` and
`sqrt(min_sq)`) before knowing whether it would emit a row.

Goal5197 changes the generic 3-D cell-MBR route so that:

```text
intersection program:
  computes min_sq
  reports min_sq to any-hit as two OptiX intersection attributes

any-hit program:
  reconstructs min_sq from optixGetAttribute_0/1
  computes max_sq and row min distance only if a row will be emitted
```

This is generic native traversal work, not an X-HD-specific primitive.

## Implementation

Files changed:

```text
src/native/optix/rtdl_optix_workloads.cpp
src/rtdsl/optix_runtime.py
src/rtdsl/partner_continuations.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_subset_scaling_gate.py
tests/goal5197_intersection_attribute_lazy_row_distance_test.py
```

Metadata now includes:

```text
intersection_attribute_min_distance_sq = reported_by_intersection_reused_by_anyhit
anyhit_row_distance_computation = lazy_row_output_only
```

## Validation

Local focused tests:

```text
py -m unittest \
  tests.goal5197_intersection_attribute_lazy_row_distance_test \
  tests.goal5195_intersection_current_best_pruning_test \
  tests.goal5194_payload_current_best_pruning_test \
  tests.goal5148_native_3d_cell_mbr_frontier_test
```

Result:

```text
Ran 11 tests in 1.770s
OK
```

POD:

```text
host = 213.173.108.24
port = 13502
workspace = /root/rtdl_goal5093
```

POD build:

```text
make build-optix
```

POD focused tests:

```text
python -m unittest \
  tests.goal5197_intersection_attribute_lazy_row_distance_test \
  tests.goal5195_intersection_current_best_pruning_test \
  tests.goal5194_payload_current_best_pruning_test \
  tests.goal5148_native_3d_cell_mbr_frontier_test
```

Result:

```text
Ran 11 tests in 0.720s
OK
```

## Full-Public Level-B Evidence

Input:

```text
source = public Stanford Dragon, 437645 points
target = public Stanford HappyBuddha, 543652 points
author_hd_result = 0.12572988867759705
```

Route:

```text
backend = optix
grid_shape = 32,32,32
source_limits = all
initial_state = dense local-grid-cell
max_inline_points = 512
frontier_inline_nearest = true
frontier_row_capacity = 0
skip_exact_oracle = true
payload-current-best pruning = true
intersection-stage current-best pruning = true
intersection min_sq attribute reuse = true
lazy row distance computation = true
```

The first POD route after rebuild had a cold seed phase and is retained as an
artifact but not used as the performance comparison:

```text
run1:
  matched = true
  route_wall = 6.815880194306374s
  seed = 4.9666261076927185s
  native frontier / inline = 1.0867086499929428s
```

Two warm runs:

```text
final2:
  matched = true
  route_wall = 2.282611295580864s
  seed = 0.5615862682461739s
  native frontier / inline = 0.952098660171032s
  intersection_attribute_min_distance_sq = reported_by_intersection_reused_by_anyhit
  anyhit_row_distance_computation = lazy_row_output_only

final3:
  matched = true
  route_wall = 2.2462014481425285s
  seed = 0.5566430613398552s
  native frontier / inline = 0.925519160926342s
  intersection_attribute_min_distance_sq = reported_by_intersection_reused_by_anyhit
  anyhit_row_distance_computation = lazy_row_output_only
```

Artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_intersection_attribute_lazy_row_distance_goal5197_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_intersection_attribute_lazy_row_distance_final2_goal5197_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_intersection_attribute_lazy_row_distance_final3_goal5197_graphics_dragon_happy_buddha_2026-07-08.json
```

Comparison against Goal5196:

```text
Goal5196 run1 route_wall = 2.275638982653618s
Goal5196 final2 route_wall = 2.256376951932907s

Goal5197 final2 route_wall = 2.282611295580864s
Goal5197 final3 route_wall = 2.2462014481425285s
```

The observed timing is essentially neutral / within small run-to-run variation.
The best Goal5197 run is slightly lower than the best Goal5196 run, but the
median is not a clear route-local win.

## Interpretation

Goal5197 is a correctness-preserving generic native implementation cleanup:
it removes duplicate `min_sq` computation in any-hit and avoids row-only
distance work when no row is emitted. The full-public route still matches the
author HDResult.

Performance should be described conservatively:

```text
route remains about 2.25-2.28s
native frontier / inline remains about 0.93-0.95s
```

This goal does not justify a new performance headline beyond "no regression
observed in warm runs".

## Claim Boundary

Authorized claims:

- intersection `min_sq` is carried to any-hit via OptiX attributes;
- row-only distance values are computed lazily only when a row is emitted;
- local and POD tests pass;
- full-public Level-B Dragon/HappyBuddha route still matches author HDResult;
- warm route wall remains about `2.25-2.28s`.

Not authorized:

- no author-vs-RTDL performance ratio;
- no author performance parity;
- no exact paper dataset reproduction;
- no full X-HD paper reproduction;
- no strong speedup claim over Goal5196;
- no X-HD-specific primitive or copied author implementation.

## Decision

Goal5197 can be reviewed as a generic native cleanup / neutral optimization.
It should not displace Goal5196 as the major performance result. The current
best route should continue to be described as:

```text
dense local-grid seed
+ inline512
+ payload-current-best pruning
+ intersection-stage current-best pruning
+ intersection attribute min_sq reuse / lazy row distance
```

with the caveat that Goal5197's timing delta is not decisive.
