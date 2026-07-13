# Goal5203 NumPy Matrix Input Loader Result

Date: 2026-07-08

## Verdict

```text
completed_numpy_matrix_input_loader__route_frontdoor_repack_removed
```

## Purpose

Goal5202 removed repeated coordinate repacking inside generic RTDL seed and
frontier helpers by adding the app-neutral `coordinate_matrix` /
`coordinate_matrix_fields` convention.

Goal5203 attacks the next visible front-door cost: the X-HD paper app still
loaded full-public ASCII PLY inputs into Python `list[tuple[float,...]]` rows
and then repacked those rows into a NumPy coordinate matrix before entering the
RTDL columnar route.

This goal keeps the old row interface for bounded/reference gates, but moves the
current high-volume cell-MBR route to an app-owned NumPy matrix input front door.

## Implementation

Changed `Paper-reproduction-apps/x-hd-paper/scripts/xhd_input_loader.py`:

- added `load_ascii_ply_vertex_matrix(...)`;
- added `load_wkt_point_matrix(...)`;
- added `load_points_matrix(...)`;
- added `translate_point_matrix_to_min_bound(...)`;
- added `point_matrix_to_rows(...)`;
- preserved legacy `load_points(...)` and `translate_points_to_min_bound(...)`.

Changed `run_xhd_cell_mbr_frontier_route_gate.py`:

- uses `load_points_matrix(...)` for the hot full-public route;
- translates the matrix in place for the author min-bound preprocessing
  convention;
- builds point columns as views into the matrix;
- converts back to rows only when `validation_mode=exact-and-author` needs the
  existing exact reference oracle;
- records `point_input_representation = numpy_coordinate_matrix`.

Changed `run_xhd_full_public_subset_scaling_gate.py`:

- loads full source/target public PLY inputs as matrices;
- slices source subsets through NumPy indexing;
- converts subsets to rows only for optional exact subset oracle calls.

No RTDL core or native code was changed. This is app-owned input handling plus
adoption of the generic coordinate-matrix convention introduced in Goal5202.

## Validation

Local:

```text
py -m unittest \
  tests.goal5203_numpy_point_matrix_input_loader_test \
  tests.goal5202_packed_coordinate_matrix_reuse_test \
  tests.goal5133_xhd_ply_input_bridge_test \
  tests.goal5150_xhd_cell_mbr_frontier_route_gate_test \
  tests.goal5187_xhd_full_public_route_only_gate_test

Ran 18 tests OK

py_compile = OK
git diff --check = OK
```

POD:

```text
host = 213.173.108.24
port = 13502
gpu = NVIDIA RTX 4000 Ada Generation
driver = 550.127.05

python -m unittest \
  tests.goal5203_numpy_point_matrix_input_loader_test \
  tests.goal5202_packed_coordinate_matrix_reuse_test \
  tests.goal5150_xhd_cell_mbr_frontier_route_gate_test \
  tests.goal5187_xhd_full_public_route_only_gate_test

Ran 13 tests OK
```

The POD initially lacked `tests.goal5187_xhd_full_public_route_only_gate_test`,
so that historical adjacent test file was uploaded before the final focused
POD test run.

## Full-Public Evidence

Artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5203_numpy_matrix_loader_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5203_numpy_matrix_loader_warm2_graphics_dragon_happy_buddha_2026-07-08.json
```

Both full-public Dragon -> HappyBuddha Level-B runs:

```text
all_matched = true
author_abs_diff ~= 2.3849e-9
initial_query_coordinate_matrix_reused = true
initial_target_coordinate_matrix_reused = true
frontier_query_coordinate_matrix_reused = true
frontier_target_coordinate_matrix_reused = true
```

Primary Goal5203 run:

```text
load_full_inputs ~= 1.680s
select_source_subset ~= 0.214s
route_wall ~= 1.239s
case_total ~= 1.453s

source_columns ~= 0.0003s
target_columns ~= 0.0018s
grid_cell_mbrs ~= 0.101s
initial_state_seed ~= 0.233s
frontier_rows ~= 0.737s
nearest_continuation ~= 0.0009s
max_nearest_reduction ~= 0.072s
```

Warm confirmation:

```text
load_full_inputs ~= 1.682s
route_wall ~= 1.238s
case_total ~= 1.452s

source_columns ~= 0.0003s
target_columns ~= 0.0007s
initial_state_seed ~= 0.226s
frontier_rows ~= 0.745s
```

Same-POD comparison to Goal5202:

```text
Goal5202 route_wall        ~= 2.027s
Goal5203 route_wall        ~= 1.238-1.239s
delta                      ~= -0.788s

Goal5202 source+target columns ~= 0.535s
Goal5203 source+target columns ~= 0.001-0.002s

Goal5202 load_full_inputs      ~= 2.518s
Goal5203 load_full_inputs      ~= 1.681s
```

Interpretation: the biggest route-local win comes from removing the tuple-row
to matrix repack at the route front door. The total input loading phase also
improves because public PLY rows are now parsed directly into a NumPy matrix.

## Claim Boundary

This goal claims:

- an app-owned input-front-door cleanup for the X-HD paper app;
- route-local improvement for the Level-B full-public Dragon -> HappyBuddha
  RTDL route;
- continued use of generic RTDL grid/cell-MBR/frontier/nearest/max-reduction
  APIs.

This goal does not claim:

- exact paper dataset reproduction;
- full X-HD paper reproduction;
- author-vs-RTDL performance ratio;
- author performance parity;
- X-HD-specific RTDL primitive;
- native backend completion beyond the existing generic pieces.

## Next

After Goal5203, the current route-local floor is again dominated by:

```text
frontier_rows ~= 0.74s
initial_state_seed ~= 0.23s
grid_cell_mbrs ~= 0.10s
max_nearest_reduction ~= 0.07s
```

The removed front-door repack was large and worth doing. Further major
performance work should now return to the generic native inline-nearest
execution model / work ordering, or pause for review/provenance work. Do not
re-open PLY tuple-repack, scalar ray `tmax`, or prepared accel-build caching
without new evidence.
