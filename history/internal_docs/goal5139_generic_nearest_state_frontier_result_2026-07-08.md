# Goal5139 - Generic Nearest-State Frontier Result

## Verdict

`generic_nearest_state_frontier_reference_ready`

## Why This Goal Exists

Goal5138 created the first generic grid/cell candidate front door:

```text
point columns -> tight cell-MBR descriptors -> radius cell candidates
```

The next scalable X-HD gap from Goal5137 is the traversal state shape: the
author shader keeps per-query nearest state, prunes candidates whose lower
bound cannot improve the current best, and emits large/unresolved cells to a
continuation path.

Goal5139 defines that state/frontier contract without naming X-HD or Hausdorff.

## Implemented Public API

New public symbol:

```python
nearest_state_frontier_from_cell_candidates_numpy_columns(...)
```

Inputs:

- generic radius cell-MBR candidate columns from Goal5138;
- generic point-grid cell columns with `point_counts` and point spans;
- `query_point_ids`;
- optional `current_best_distances`;
- optional `current_best_item_ids`;
- `max_inline_points`.

Outputs:

```text
nearest_state
inline_frontier
offload_frontier
pruned_frontier
```

Each frontier row has:

```text
query_row_ids
query_point_ids
cell_ids
point_begin_offsets
point_counts
min_distances
max_distances
```

Rules:

```text
prune    if candidate_min_distance >= current_best_distance
offload  if not pruned and cell_point_count > max_inline_points
inline   otherwise
```

Metadata:

```text
contract = generic_nearest_state_cell_frontier
app_semantics = none
native_engine_row_contract = not_called_partner_reference_only
```

## Test Evidence

Command:

```text
py -m unittest tests.goal5139_generic_nearest_state_frontier_api_test tests.goal5138_generic_grid_cell_candidate_api_test
```

Result:

```text
Ran 7 tests in 1.135s
OK
```

Additional X-HD-adjacent regression command:

```text
py -m unittest tests.goal5111_xhd_author_json_gate_test tests.goal5115_xhd_rtdl_route_gate_test tests.goal5118_xhd_bounded3d_rtdl_route_gate_test tests.goal5127_xhd_generic_nearest_pipeline_extraction_test tests.goal5128_non_hausdorff_max_nearest_consumer_test tests.goal5133_xhd_ply_input_bridge_test tests.goal5134_xhd_ply_sample_gate_packet_test tests.goal5138_generic_grid_cell_candidate_api_test
```

Result:

```text
Ran 27 tests in 0.301s
OK
```

Machine-readable contract:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5139_generic_nearest_state_frontier_contract_2026-07-08.json
```

## Non-X-HD Fixture

The behavior test uses a facility/demand coverage scenario:

- target facilities are grouped into generic grid cells;
- demand points emit radius cell-MBR candidates;
- current best distances prune some candidates;
- small cells go to `inline_frontier`;
- large cells go to `offload_frontier`.

The asserted output includes all three categories:

```text
inline_frontier_row_count = 3
offload_frontier_row_count = 1
pruned_frontier_row_count = 2
```

This is deliberately not a Hausdorff fixture and not an X-HD paper fixture.

## What This Proves

Goal5139 proves that the second generic system contract in the scalable route
exists:

```text
cell candidates + current nearest state
-> inline frontier
-> offload frontier
-> pruned frontier
```

This gives a future RT traversal backend and a future CUDA/Numba continuation a
stable columnar handoff shape.

## What This Does Not Prove

This does not prove:

- native/OptiX traversal;
- in-shader payload state;
- exact point-distance evaluation inside cells;
- heavy-cell CUDA offload implementation;
- radius-growth controller;
- X-HD Figure 5 or performance reproduction;
- author-performance parity.

## Architectural Position

Goal5138 and Goal5139 now define the first two generic system blocks needed by
the X-HD scalable route:

```text
point columns
-> grid cell descriptors
-> radius cell candidates
-> nearest-state frontier split
```

The remaining blocks are traversal/backend work, not app-specific code.

## Recommended Next Goal

```text
Goal5140 - Generic RT cell-MBR traversal ABI design
```

That goal should define the native/RT-facing ABI for traversing query points
against cell-MBR descriptors and returning the same frontier schema defined
here. It must remain app-neutral and must not add an `xhd` or `hausdorff`
primitive to RTDL core.
