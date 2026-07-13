# Goal5202 Packed Coordinate Matrix Reuse Result

Date: 2026-07-08

## Verdict

```text
completed_packed_coordinate_matrix_reuse__frontdoor_overhead_reduced
```

## Purpose

Goal5201 showed that the current full-public Dragon -> HappyBuddha Level-B
route has a route-level `frontier_rows ~= 0.920s` phase, while the native
frontier collector reports `native_total ~= 0.600s`. The next generic target was
therefore front-door / array-boundary overhead around seed and frontier calls,
not prepared cell-MBR accel build caching.

Goal5202 attacks one concrete front-door cost: repeated Python
`np.column_stack(...)` packing of the same point coordinate columns before
local-grid seed and native cell-MBR frontier calls.

## Implementation

Added a generic point-column convention:

```text
coordinate_matrix
coordinate_matrix_fields
```

and a helper:

```text
_point_matrix_for_fields(...)
```

The helper:

- validates `ids` and coordinate columns as before;
- reuses a supplied contiguous `coordinate_matrix` when its fields and shape
  match;
- proves consistency either by shared memory with the coordinate columns or by
  value equality;
- fails closed if the packed matrix is stale or inconsistent;
- falls back to `np.column_stack(...)` when no matrix is supplied.

The hot generic helpers now use this helper:

```text
seed_nearest_witness_from_local_grid_cell_numpy_columns
cell_mbr_nearest_frontier_native_3d_optix_columns
```

The X-HD app route now constructs point columns once with `x/y/z` as views into
the same packed matrix. This is app-side adoption of a generic convention, not
an X-HD-specific RTDL primitive.

## Validation

Local:

```text
py -m unittest \
  tests.goal5202_packed_coordinate_matrix_reuse_test \
  tests.goal5201_cell_mbr_frontier_phase_timing_test \
  tests.goal5200_native_local_grid_seed_test \
  tests.goal5148_native_3d_cell_mbr_frontier_test

Ran 13 tests OK

py -m unittest \
  tests.goal5149_cell_mbr_frontier_nearest_continuation_test \
  tests.goal5150_xhd_cell_mbr_frontier_route_gate_test \
  tests.goal5152_nearest_cell_mbr_seed_pruning_test \
  tests.goal5161_numba_nearest_cell_mbr_seed_test \
  tests.goal5163_numba_frontier_nearest_continuation_test \
  tests.goal5187_xhd_full_public_route_only_gate_test \
  tests.goal5202_packed_coordinate_matrix_reuse_test

Ran 25 tests OK

py_compile = OK
```

POD:

```text
host = 213.173.108.24
port = 13502
gpu = NVIDIA RTX 4000 Ada Generation
driver = 550.127.05

python3 -m unittest \
  tests.goal5202_packed_coordinate_matrix_reuse_test \
  tests.goal5201_cell_mbr_frontier_phase_timing_test \
  tests.goal5200_native_local_grid_seed_test \
  tests.goal5148_native_3d_cell_mbr_frontier_test

Ran 13 tests OK
```

## Full-Public Evidence

Artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5202_packed_coordinate_matrix_cold_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5202_packed_coordinate_matrix_warm2_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5202_packed_coordinate_matrix_no_timing_graphics_dragon_happy_buddha_2026-07-08.json
```

All three runs:

```text
matched = true
author_abs_diff ~= 2.3849e-9
initial_query_coordinate_matrix_reused = true
initial_target_coordinate_matrix_reused = true
frontier_query_coordinate_matrix_reused = true
frontier_target_coordinate_matrix_reused = true
```

Goal5202 no-timing performance run:

```text
route_wall ~= 2.027s
source_columns ~= 0.246s
target_columns ~= 0.289s
grid_cell_mbrs ~= 0.101s
initial_state_seed ~= 0.235s
frontier_rows ~= 0.753s
nearest_continuation ~= 0.0009s
max_nearest_reduction ~= 0.073s
```

Comparison to Goal5200 same-POD auto/Numba control:

```text
Goal5200 auto/Numba control route_wall ~= 2.258s
Goal5202 packed matrix route_wall      ~= 2.027s
delta                                  ~= -0.231s
relative route-local improvement       ~= 10%
```

Comparison to Goal5201 warm diagnostic:

```text
Goal5201 warm diagnostic route_wall ~= 2.229s
Goal5202 warm diagnostic route_wall ~= 2.011s
frontier_rows: 0.920s -> 0.734s / 0.753s
initial_state_seed: 0.545s -> 0.235s
```

The source/target column construction phase grows because the app now builds
the packed matrix once up front. The route still improves overall because seed
and frontier reuse that matrix rather than rebuilding large coordinate matrices
inside multiple helper calls.

## Claim Boundary

This goal claims a route-local generic RTDL front-door improvement for the
Level-B full-public Dragon -> HappyBuddha route. It does not claim:

- exact paper dataset reproduction;
- full X-HD paper reproduction;
- author-vs-RTDL performance ratio;
- author performance parity;
- X-HD-specific RTDL primitive;
- native backend completion beyond existing bounded pieces.

The improvement is generic because it introduces an app-neutral point-column
packing convention and keeps X-HD semantics in the app route.
