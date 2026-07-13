# Goal5201 Cell-MBR Frontier Native Phase Timing Result

Date: 2026-07-08

## Verdict

```text
completed_cell_mbr_frontier_phase_timing__inline_launch_dominates__prepared_accel_not_next
```

## Purpose

Goal5201 was a diagnostic goal, not an optimization goal. Its purpose was to
decompose the remaining `frontier_rows ~= 0.92s` floor in the current X-HD
Level-B full-public Dragon -> HappyBuddha route.

The specific question was whether the next generic RTDL attack should be a
prepared/reused cell-MBR acceleration structure. The answer is no: native
acceleration build time is already about `0.0004s`, while the native OptiX
launch / inline nearest scan is about `0.377s` and the Python/front-door wrapper
around the native call accounts for the remaining gap between native total and
route-level `frontier_rows`.

## Implementation

Added optional native phase timing instrumentation for the generic 3-D
cell-MBR nearest-frontier collector:

```text
native getter:
  rtdl_optix_cell_mbr_nearest_frontier_3d_get_last_phase_timings

Python low-level flag:
  collect_native_phase_timings

Partner/front-door flag:
  collect_native_phase_timings

X-HD route CLI:
  --collect-frontier-native-phase-timings
```

The ABI is diagnostic-only. It does not change the route semantics and does not
replace the existing frontier row production ABI.

## POD Evidence

POD:

```text
host = 213.173.108.24
port = 13502
gpu = NVIDIA RTX 4000 Ada Generation
driver = 550.127.05
```

Build/test validation on POD:

```text
make build-optix
python3 -m unittest \
  tests.goal5201_cell_mbr_frontier_phase_timing_test \
  tests.goal5200_native_local_grid_seed_test \
  tests.goal5148_native_3d_cell_mbr_frontier_test \
  tests.goal5195_intersection_current_best_pruning_test

Ran 11 tests OK
```

Local validation:

```text
py -m unittest \
  tests.goal5201_cell_mbr_frontier_phase_timing_test \
  tests.goal5200_native_local_grid_seed_test \
  tests.goal5148_native_3d_cell_mbr_frontier_test

Ran 9 tests OK

py -m py_compile \
  src/rtdsl/optix_runtime.py \
  src/rtdsl/partner_continuations.py \
  Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py \
  Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_subset_scaling_gate.py
```

## Full-Public Diagnostic Artifacts

Cold/noisy first run:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5201_frontier_phase_timing_graphics_dragon_happy_buddha_2026-07-08.json
```

Warm confirmation run:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5201_frontier_phase_timing_warm2_graphics_dragon_happy_buddha_2026-07-08.json
```

Both runs:

```text
matched = true
author_abs_diff ~= 2.3849e-9
source points = 437645
target points = 543652
```

The cold/noisy first run had a `4.967s` seed phase, so it is not a route
headline. It is useful only because the native frontier phase timing matches
the warm confirmation run.

## Warm Confirmation Breakdown

From `xhd_full_public_all_source_goal5201_frontier_phase_timing_warm2_...json`:

```text
route_wall ~= 2.229s
direction_total ~= 1.900s

source_columns ~= 0.055s
target_columns ~= 0.080s
grid_cell_mbrs ~= 0.182s
radius_selection ~= 0.031s
initial_state_seed ~= 0.545s
frontier_rows ~= 0.920s
nearest_continuation ~= 0.015s
max_nearest_reduction ~= 0.072s
```

Native frontier timing:

```text
native_total ~= 0.600s
optix_launch ~= 0.377s
query_pack ~= 0.014s
cell_pack_aabb ~= 0.0001s
accel_build ~= 0.0004s
device_alloc_upload ~= 0.0054s
nearest_download ~= 0.0028s
count_download ~= 0.000008s
row_download = 0
host_sort_pack ~= 0
attempted_rows = 0
emitted_rows = 0
mode = inline_nearest, no pruned-row emission, no sort, no inline stats
```

## Interpretation

The important result is not the `2.229s` route wall. The important result is
the internal frontier decomposition:

```text
route-level frontier_rows ~= 0.920s
native total              ~= 0.600s
native OptiX launch/scan  ~= 0.377s
native accel build        ~= 0.0004s
```

This means:

- prepared/reused cell-MBR acceleration structure build is not the next large
  target;
- the native inline nearest scan / launch is a real remaining floor;
- the gap from route-level `frontier_rows` to native total is about `0.32s`,
  which points to front-door / wrapper / array-boundary overhead around the
  native call;
- future work should target a generic inline-nearest execution model, stronger
  generic spatial work ordering, or device-resident route state, not an
  acceleration-build cache.

## Claim Boundary

This goal does not claim:

- a performance improvement;
- author-vs-RTDL performance ratio;
- exact paper dataset reproduction;
- full X-HD paper reproduction;
- native backend completion beyond the existing bounded generic collector;
- X-HD-specific primitive or author-specific shortcut.

This is diagnostic evidence for choosing the next generic RTDL system target.
