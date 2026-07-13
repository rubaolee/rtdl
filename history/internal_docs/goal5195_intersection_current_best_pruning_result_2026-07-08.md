# Goal5195 - Intersection-Stage Current-Best Pruning

## Status

`implemented_review_pending`

Goal5195 moves the Goal5194 dynamic nearest-state prune one stage earlier in
the generic native 3-D cell-MBR OptiX route.

Goal5194 taught any-hit to classify later cells against the updated payload
current best before scanning points. Goal5195 also lets the intersection program
skip reporting a cell when:

```text
inline_nearest == true
emit_pruned_rows == false
payload has a finite current best
cell min-distance-squared > payload current best squared distance
```

This avoids invoking any-hit for cells that the payload state has already made
provably irrelevant. Equal-distance cells are still reported, preserving the
lower-target-id tie-break opportunity.

This is generic nearest-state traversal work, not an X-HD-specific primitive.

## Implementation

Files changed:

```text
src/native/optix/rtdl_optix_workloads.cpp
src/rtdsl/optix_runtime.py
src/rtdsl/partner_continuations.py
tests/goal5195_intersection_current_best_pruning_test.py
```

Native behavior:

```text
__intersection__cell_mbr_frontier3d_exact
  first rejects by global radius;
  then, when inline_nearest and no pruned rows are requested,
  decodes payload current best and returns before optixReportIntersection
  if min_sq > payload best.
```

Metadata now includes:

```text
intersection_pruning =
  payload_current_best_before_report_intersection
```

## Validation

Local focused tests:

```text
py -m unittest \
  tests.goal5195_intersection_current_best_pruning_test \
  tests.goal5194_payload_current_best_pruning_test \
  tests.goal5192_inline_nearest_telemetry_test \
  tests.goal5191_inline_frontier_fastpath_test \
  tests.goal5148_native_3d_cell_mbr_frontier_test
```

Result:

```text
Ran 15 tests in 1.609s
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
  tests.goal5195_intersection_current_best_pruning_test \
  tests.goal5194_payload_current_best_pruning_test \
  tests.goal5192_inline_nearest_telemetry_test \
  tests.goal5191_inline_frontier_fastpath_test \
  tests.goal5148_native_3d_cell_mbr_frontier_test
```

Result:

```text
Ran 15 tests in 0.717s
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
initial_state = local-grid-cell
max_inline_points = 512
frontier_inline_nearest = true
frontier_row_capacity = 0
skip_exact_oracle = true
```

The explicit zero frontier capacity remains fail-closed.

### No-Telemetry Route Timing

The first no-telemetry run after rebuild had a cold/noisy seed phase
(`initial_state_seed ~= 5.21s`) and is retained as an artifact but not used as
the route comparison. Two warmed no-telemetry reruns are used:

```text
run2:
  matched = true
  route_wall = 2.644254930317402s
  seed = 0.9241094589233398s
  frontier/native inline = 0.9598596319556236s

run3:
  matched = true
  route_wall = 2.6167483627796173s
  seed = 0.9194225892424583s
  frontier/native inline = 0.9279986843466759s

warmed no-telemetry median route_wall = 2.6305016465485096s
warmed no-telemetry median frontier/native inline = 0.9439291581511497s
```

Artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_local_grid_seed_inline512_intersection_pruning_run2_goal5195_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_local_grid_seed_inline512_intersection_pruning_run3_goal5195_graphics_dragon_happy_buddha_2026-07-08.json
```

After the full-public wrapper was updated to preserve the pruning metadata in
the top-level route summary, an additional warm confirmation run produced:

```text
final4:
  matched = true
  route_wall = 2.5525703504681587s
  seed = 0.855375275015831s
  frontier/native inline = 0.9321393966674805s
  inline_nearest_pruning = payload_current_best_min_cell_distance_gt_best
  intersection_pruning = payload_current_best_before_report_intersection
```

Artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_local_grid_seed_inline512_intersection_pruning_final4_goal5195_graphics_dragon_happy_buddha_2026-07-08.json
```

Comparison against Goal5194 warmed no-telemetry median:

```text
Goal5194 route_wall median = 3.456139959394932s
Goal5195 route_wall median = 2.6305016465485096s

Goal5194 frontier/native inline median ~= 1.7923314683139324s
Goal5195 frontier/native inline median ~= 0.9439291581511497s
```

Observed route-local delta:

```text
route_wall:            3.456s -> 2.631s  (~23.9% lower, ~1.31x)
frontier/native inline 1.792s -> 0.944s  (~47.3% lower, ~1.90x)
```

Comparison against Goal5192 no-telemetry control:

```text
Goal5192 route_wall = 3.7021561563014984s
Goal5195 route_wall median = 2.6305016465485096s

Goal5192 frontier/native inline = 2.0371295884251595s
Goal5195 frontier/native inline median ~= 0.9439291581511497s
```

### Telemetry

Artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_local_grid_seed_inline512_intersection_pruning_telemetry_goal5195_graphics_dragon_happy_buddha_2026-07-08.json
```

Result:

```text
matched = true
route_wall = 2.6184759438037872s
frontier/native inline = 0.9357573315501213s
inline_cell_hit_count = 3641962
inline_point_evaluation_count = 400610300
```

The telemetry point-evaluation counters are unchanged from Goal5194 because
Goal5195 prunes before `optixReportIntersection` / any-hit; it reduces
intersection/any-hit overhead for cells that would no longer scan points. The
timing improvement therefore appears in `frontier_rows / native inline`, not in
the inline point-evaluation counter.

## Interpretation

Goal5195 confirms that after Goal5194, a large part of the native collector
floor was traversal/any-hit overhead over cells already excluded by the updated
payload current best. Moving the same generic nearest-state prune to the
intersection stage removes that overhead.

This is a bigger improvement than Goal5194 in timing terms, while preserving the
same correctness gate:

```text
author_abs_diff ~= 2.38e-9
frontier_rows = 0
```

The route is still not an author performance comparison. It is Level-B
same-source representative route evidence on public Stanford inputs.

## Claim Boundary

Authorized claims:

- intersection-stage current-best pruning is implemented in the generic native
  3-D cell-MBR route;
- local and POD tests pass;
- full-public Level-B Dragon/HappyBuddha route still matches author HDResult;
- warmed route wall is about `2.6s`;
- native frontier / inline time is about `0.93-0.94s`;
- this improves the current RTDL route-local timing relative to Goal5194 and
  Goal5192.

Not authorized:

- no author-vs-RTDL performance ratio;
- no author performance parity;
- no exact paper dataset reproduction;
- no full X-HD paper reproduction;
- no claim that telemetry timing is the performance headline;
- no X-HD-specific primitive or copied author implementation.

## Decision

Goal5195 should become the current default native inline-nearest behavior.

The remaining measured route floor is now roughly:

```text
local-grid seed ~= 0.92s
native frontier / inline ~= 0.94s
load / route orchestration / reduction ~= remaining route wall
```

Future route work should be selected from this new profile. The obvious next
targets are no longer Python continuation or small inline thresholds; they are
the local-grid seed, native traversal/index structure, or broader exact-dataset
/ review work.
