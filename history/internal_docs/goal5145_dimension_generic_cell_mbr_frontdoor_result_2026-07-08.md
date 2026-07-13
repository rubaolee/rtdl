# Goal5145 - Dimension-Generic Cell-MBR Front Door

## Verdict

`dimension_generic_cell_mbr_frontdoor_reference_ready`

## Why This Goal Exists

Goal5144 verified the 2-D backend-assisted cell-MBR route on POD with OptiX.
That is useful but not enough for X-HD graphics samples, which are 3-D. Rather
than pretending the 2-D AABB route is a 3-D backend, this goal adds a stable
dimension-generic reference front door:

```text
query points + generic cell MBR columns
-> radius cell-MBR candidate rows
-> nearest-state frontier split
-> Goal5140 ABI-shaped row table
```

This gives future native/RT backends a public 2-D/3-D oracle.

## Public API Added

```text
cell_mbr_nearest_frontier_numpy_columns(...)
```

It is exported from `rtdsl.__all__`.

Metadata contract:

```text
contract = generic_cell_mbr_nearest_frontier_reference
native_abi_contract = generic_cell_mbr_nearest_frontier_native_abi_v1
native_engine_row_contract = not_called_dimension_generic_reference_only
app_semantics = none
native_backend_complete = false
```

`plan_cell_mbr_traversal_lowering("dimension_generic")` now reports:

```text
status = implemented_dimension_generic_reference_row_table
executable = true
native_backend_complete = false
```

## 3-D Fixture Evidence

Synthetic non-X-HD fixture:

```text
query_count = 3
cell_count = 2
candidate_row_count = 6
row_count = 6
```

Expected row table:

```text
query_point_ids      = [100, 101, 102, 102, 100, 101]
cell_ids             = [0, 0, 0, 1, 1, 1]
frontier_kind_codes  = [1, 1, 1, 2, 3, 3]
point_counts         = [2, 2, 2, 3, 3, 3]
```

The test proves this public front door matches the manual composition of:

```text
radius_cell_mbr_candidate_rows_numpy_columns
nearest_state_frontier_from_cell_candidates_numpy_columns
cell_mbr_frontiers_to_row_table_numpy_columns
```

## Tests

```text
py -m unittest tests.goal5145_dimension_generic_cell_mbr_frontdoor_test
```

Result:

```text
Ran 4 tests OK
```

Regression:

```text
py -m unittest \
  tests.goal5142_generic_cell_mbr_backend_assisted_frontdoor_test \
  tests.goal5140_generic_cell_mbr_traversal_abi_test \
  tests.goal5139_generic_nearest_state_frontier_api_test \
  tests.goal5138_generic_grid_cell_candidate_api_test
```

Result:

```text
Ran 15 tests OK
```

## What This Does Not Claim

This does not implement:

- a native Goal5140 backend;
- a 3-D OptiX cell-MBR backend;
- the X-HD RT-core algorithm;
- X-HD performance improvement;
- full paper reproduction.

It is a system/API correctness step: the generic 3-D reference front door now
exists and can serve as the oracle for a future native 3-D backend.
