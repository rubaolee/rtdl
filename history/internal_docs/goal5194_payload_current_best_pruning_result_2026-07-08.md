# Goal5194 - Payload Current-Best Pruning In Native Inline-Nearest

## Status

`implemented_review_pending`

Goal5194 fixes a generic native traversal inefficiency in the 3-D cell-MBR
inline-nearest collector. The native OptiX any-hit program updated the nearest
state payload after scanning an inline cell, but later cell classification still
used the original query seed distance. That meant a closer witness found inside
the traversal did not tighten pruning for subsequent cells.

This goal changes the inline-nearest path to classify later cells against the
payload current best distance. It is generic nearest-state traversal work, not
an X-HD-specific shortcut.

## Implementation

Files changed:

```text
src/native/optix/rtdl_optix_workloads.cpp
src/rtdsl/partner_continuations.py
tests/goal5194_payload_current_best_pruning_test.py
```

Native change:

```text
__anyhit__cell_mbr_frontier3d_emit
  before: prune inline cells using query.current_best_distance
  after : when inline_nearest is enabled and payload has a finite best,
          prune using payload current best squared distance
```

The dynamic prune uses a strict `min_sq > best` comparison. Equal-distance
cells are still evaluated so the lower target-id tie-break is not silently
skipped.

Python metadata now exposes:

```text
inline_nearest_pruning =
  payload_current_best_min_cell_distance_gt_best
```

## Validation

Local focused tests:

```text
py -m unittest \
  tests.goal5194_payload_current_best_pruning_test \
  tests.goal5192_inline_nearest_telemetry_test \
  tests.goal5191_inline_frontier_fastpath_test \
  tests.goal5148_native_3d_cell_mbr_frontier_test
```

Result:

```text
Ran 13 tests in 1.325s
OK
```

POD:

```text
host = 213.173.108.24
port = 13502
workspace = /root/rtdl_goal5093
```

POD preflight:

```text
POD_OK
45c502cfccb5
NVIDIA RTX 4000 Ada Generation, 550.127.05
```

Build:

```text
make build-optix
```

POD focused tests:

```text
python -m unittest \
  tests.goal5194_payload_current_best_pruning_test \
  tests.goal5192_inline_nearest_telemetry_test \
  tests.goal5191_inline_frontier_fastpath_test \
  tests.goal5148_native_3d_cell_mbr_frontier_test
```

Result:

```text
Ran 13 tests in 0.513s
OK
```

## Full-Public Level-B Route Evidence

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

The explicit zero frontier capacity remains fail-closed: if the native
collector emits any frontier rows, the run fails.

### Performance Control

The first no-telemetry run after rebuild had a cold/noisy seed phase
(`initial_state_seed ~= 5.23s`) and is retained as an artifact but not used as
the route comparison. Two warmed no-telemetry reruns are used for the route
comparison:

```text
rerun1:
  matched = true
  route_wall = 3.4648774936795235s
  seed = 0.9059246927499771s
  frontier/native inline = 1.7929501608014107s

rerun2:
  matched = true
  route_wall = 3.44740242511034s
  seed = 0.8980220928788185s
  frontier/native inline = 1.7917127758264542s

warmed no-telemetry median route_wall = 3.456139959394932s
```

Artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_local_grid_seed_inline512_payload_pruning_rerun_goal5194_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_local_grid_seed_inline512_payload_pruning_rerun2_goal5194_graphics_dragon_happy_buddha_2026-07-08.json
```

Historical comparison point:

```text
Goal5192 no-telemetry control route_wall = 3.7021561563014984s
Goal5192 no-telemetry frontier/native inline = 2.0371295884251595s
```

Observed route-local delta:

```text
route_wall:            3.702s -> 3.456s  (~6.6% lower, ~1.07x)
frontier/native inline 2.037s -> 1.792s  (~12.0% lower, ~1.14x)
```

This is a modest timing improvement. It is not an author-vs-RTDL speedup ratio.

### Telemetry

Artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_local_grid_seed_inline512_payload_pruning_telemetry_goal5194_graphics_dragon_happy_buddha_2026-07-08.json
```

Result:

```text
matched = true
route_wall = 3.413866713643074s
frontier/native inline = 1.7787858694791794s
inline_cell_hit_count = 3641962
inline_point_evaluation_count = 400610300
```

Historical telemetry comparison:

```text
Goal5192 inline_cell_hit_count = 12003138
Goal5192 inline_point_evaluation_count = 1242677739
```

Work reduction:

```text
inline cell hits:   12.00M -> 3.64M  (~69.7% lower, ~3.30x)
inline point evals: 1.24B  -> 0.40B  (~67.8% lower, ~3.10x)
```

The telemetry run uses atomic counters and remains diagnostic. The warmed
no-telemetry reruns are the route timing evidence.

## Interpretation

Goal5194 validates the suspected structural gap: the generic native
inline-nearest collector was doing real work, but it was not fully exploiting
the nearest-state payload it already carried. Updating the payload best inside
the traversal now tightens later cell pruning.

This closes one genuine generic system defect:

```text
found closer witness in traversal
-> update payload best
-> use that updated best to prune later cells
```

It does not close the whole X-HD performance gap. The route still spends about
`1.79s` in native frontier / inline-nearest work and about `0.90s` in local-grid
seeding on this Level-B full-public candidate.

## Claim Boundary

Authorized claims:

- native inline-nearest now prunes later cells against payload current best;
- the change is app-neutral nearest-state traversal behavior;
- local and POD tests pass;
- the full-public Level-B route still matches author HDResult;
- inline point-distance evaluations drop by about 68%;
- warmed route wall improves modestly to about 3.46s.

Not authorized:

- no author-vs-RTDL performance ratio;
- no author performance parity;
- no exact paper dataset reproduction;
- no full X-HD paper reproduction;
- no claim that telemetry timing is the performance headline;
- no X-HD-specific primitive or author-code copy.

## Decision

Goal5194 is a real generic route improvement and should become the current
default native inline-nearest behavior.

The next route work, if any, should again be profile-led. After this change, the
remaining measured costs are still native inline work and local-grid seed cost;
small seed-budget and threshold tweaks have already been measured as no-go.
