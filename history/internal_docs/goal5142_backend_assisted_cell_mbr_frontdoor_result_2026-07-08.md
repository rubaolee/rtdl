# Goal5142 - Backend-Assisted Cell-MBR Front Door Result

## Verdict

`implemented_backend_assisted_2d_frontdoor__native_symbol_still_missing`

## What Was Implemented

New public API:

```python
rtdsl.cell_mbr_nearest_frontier_aabb_membership_2d_numpy_columns(...)
```

This is a generic 2-D route:

```text
query points + cell MBRs
-> generic expanded-AABB membership backend (cpu/embree/optix)
-> exact point-to-cell-MBR distance filter
-> nearest-state inline/offload/pruned split
-> Goal5140 ABI row table
```

It is intentionally app-neutral. It does not mention X-HD, Hausdorff, paper
artifacts, author code, or benchmark semantics.

## What This Is Not

This is **not** the final native Goal5140 backend.

Still missing:

```text
rtdl_optix_collect_cell_mbr_nearest_frontier
```

The new route is a backend-assisted front door. Existing AABB row output can
provide broadphase rows, including OptiX on a POD with a current native library,
but exact distance filtering and frontier classification remain in generic
NumPy.

## Why This Is Still Useful

Goal5141 showed that existing RTDL native assets were reusable patterns, not a
drop-in Goal5140 backend. Goal5142 makes that intermediate layer executable:
the ABI row table is no longer only a paper contract, and the same front door
can exercise `backend="optix"` where available.

This gives the project a safer next gate:

1. validate the route locally with CPU backend;
2. validate the same route on POD with OptiX AABB rows;
3. then decide whether to implement a true native symbol or extend the assisted
   route to 3-D first.

## Public API Contract

```python
cell_mbr_nearest_frontier_aabb_membership_2d_numpy_columns(
    query_point_columns,
    cell_columns,
    *,
    radius,
    current_best_distances=None,
    current_best_item_ids=None,
    max_inline_points,
    row_capacity=None,
    broadphase_row_capacity=None,
    backend="cpu",
    resolution=32,
    return_metadata=False,
)
```

Metadata fields include:

```text
contract = generic_cell_mbr_nearest_frontier_aabb_membership_2d
native_abi_contract = generic_cell_mbr_nearest_frontier_native_abi_v1
broadphase_contract = generic_expanded_aabb_point_membership_rows_2d_v1
state_split_contract = generic_nearest_state_cell_frontier
row_table_contract = generic_cell_mbr_nearest_frontier_row_table
app_semantics = none
rt_core_speedup_claim_authorized = false
whole_app_speedup_claim_authorized = false
```

`plan_cell_mbr_traversal_lowering("aabb_membership_2d")` now reports:

```text
status = implemented_backend_assisted_2d_frontdoor
executable = true
native_backend_complete = false
backend_options = cpu, embree, optix
```

The existing `plan_cell_mbr_traversal_lowering("optix")` remains ABI-only and
non-executable because the dedicated native symbol still does not exist.

## Correctness Checks

Local tests:

```text
py -m unittest tests.goal5142_generic_cell_mbr_backend_assisted_frontdoor_test
```

Result:

```text
Ran 4 tests OK
```

The tests cover:

1. row-table equality against the Goal5140 NumPy reference;
2. exact filtering of expanded-AABB broadphase corner false positives;
3. fail-closed row-capacity overflow;
4. public surface and app-neutral source window.

Regression tests:

```text
py -m unittest \
  tests.goal5140_generic_cell_mbr_traversal_abi_test \
  tests.goal5139_generic_nearest_state_frontier_api_test \
  tests.goal5138_generic_grid_cell_candidate_api_test \
  tests.goal5127_xhd_generic_nearest_pipeline_extraction_test \
  tests.goal5128_non_hausdorff_max_nearest_consumer_test
```

Result:

```text
Ran 16 tests OK
```

Current X-HD light regression:

```text
py -m unittest \
  tests.goal5110_xhd_paper_app_scaffold_test \
  tests.goal5111_xhd_author_json_gate_test \
  tests.goal5113_xhd_bounded2d_author_gate_test \
  tests.goal5114_xhd_bounded3d_author_gate_test \
  tests.goal5115_xhd_rtdl_route_gate_test \
  tests.goal5117_generic_3d_hausdorff_column_route_test \
  tests.goal5118_xhd_bounded3d_rtdl_route_gate_test \
  tests.goal5127_xhd_generic_nearest_pipeline_extraction_test \
  tests.goal5128_non_hausdorff_max_nearest_consumer_test \
  tests.goal5133_xhd_ply_input_bridge_test \
  tests.goal5134_xhd_ply_sample_gate_packet_test \
  tests.goal5138_generic_grid_cell_candidate_api_test \
  tests.goal5139_generic_nearest_state_frontier_api_test \
  tests.goal5140_generic_cell_mbr_traversal_abi_test \
  tests.goal5142_generic_cell_mbr_backend_assisted_frontdoor_test
```

Result:

```text
Ran 48 tests OK
```

## What Was Not Validated Yet

This local run did not exercise `backend="optix"`. It validated the same
front-door contract using the CPU AABB membership backend. A POD/native-library
run is required to validate the OptiX broadphase path.

This result also does not implement or test a 3-D backend. X-HD representative
graphics inputs remain 3-D, so Goal5142 is a system stepping stone, not paper
performance evidence.

## Claim Boundary

Allowed:

- Generic 2-D backend-assisted front door exists.
- It can request CPU/Embree/OptiX AABB membership backends.
- It emits Goal5140-compatible row tables.
- It keeps app semantics outside RTDL core.

Not allowed:

- Native Goal5140 backend exists.
- X-HD RT algorithm is reproduced.
- X-HD performance improved.
- Author performance parity.
- 2-D assisted route is sufficient for 3-D graphics paper performance.

## Recommended Next Goal

Goal5143 should run the new route on POD with `backend="optix"` and decide the
next implementation fork:

```text
optix_2d_assisted_route_verified__extend_to_3d_or_native_symbol
```

or:

```text
optix_2d_assisted_route_blocked__fix_backend_binding_first
```
