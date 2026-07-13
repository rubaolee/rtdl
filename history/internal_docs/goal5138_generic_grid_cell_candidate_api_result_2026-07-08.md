# Goal5138 - Generic Grid-Cell Candidate API Result

## Verdict

`generic_grid_cell_candidate_api_reference_ready`

## Why This Goal Exists

Goal5137 showed that the scalable X-HD route is not the exact pairwise route.
The author algorithm first builds a target point grid, emits tight cell MBRs,
and then traverses radius-expanded cell descriptors before doing exact nearest
work. RTDL did not have a public, app-neutral contract for that first grid/cell
candidate stage.

Goal5138 implements the first system-level bridge:

```text
target point columns
-> generic point-grid tight cell MBR columns
-> generic query-to-cell candidate rows by radius
```

This is a NumPy reference/front-door contract. It is not a native or OptiX
backend and it does not claim X-HD performance.

## Implemented Public API

Two new symbols are exported from `rtdsl`:

```python
point_grid_cell_mbrs_numpy_columns(...)
radius_cell_mbr_candidate_rows_numpy_columns(...)
```

### `point_grid_cell_mbrs_numpy_columns`

Input:

- point columns with `ids` and caller-selected coordinate fields;
- `grid_shape`, with one positive entry per coordinate dimension.

Output:

- compact zero-based `cell_ids`;
- `original_cell_ids` preserving the encoded grid id;
- `point_begin_offsets` and `point_counts`;
- sorted `point_ids` and `point_row_indices`;
- tight per-cell MBR columns, e.g. `min_x`, `max_x`, `min_y`, `max_y`.

Metadata:

```text
contract = generic_point_grid_cell_mbr_columns
app_semantics = none
native_engine_row_contract = not_called_partner_reference_only
rt_core_speedup_claim_authorized = false
whole_app_speedup_claim_authorized = false
```

### `radius_cell_mbr_candidate_rows_numpy_columns`

Input:

- query point columns;
- generic cell-MBR columns;
- `radius`;
- caller-selected coordinate fields.

Output:

- `PartnerCandidateRows(query_row_id, cell_id, min_distance)`;
- `query_point_ids`, `query_row_ids`, `cell_ids`;
- `min_distances` and `max_distances`.

Candidate rule:

```text
point-to-tight-cell-MBR min distance <= radius
```

Metadata:

```text
contract = generic_radius_cell_mbr_candidate_rows
app_semantics = none
native_engine_row_contract = not_called_partner_reference_only
```

## Test Evidence

Command:

```text
py -m unittest tests.goal5138_generic_grid_cell_candidate_api_test tests.goal5127_xhd_generic_nearest_pipeline_extraction_test tests.goal5128_non_hausdorff_max_nearest_consumer_test
```

Result:

```text
Ran 9 tests in 1.094s
OK
```

The test covers:

1. tight cell MBR construction for a synthetic 2D point grid;
2. radius-based cell-MBR candidate rows for a non-X-HD facility/demand coverage
   scenario;
3. public export through `rtdsl.__all__`;
4. app-neutral source window scan with no `xhd`, `x-hd`, `hausdorff`, `paper`,
   or `hd_exec` tokens;
5. fail-closed behavior for bad `grid_shape` and negative `radius`.

Machine-readable contract:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5138_generic_grid_cell_api_contract_2026-07-08.json
```

## What This Proves

This proves that the first X-HD algorithmic gap from Goal5137 has been turned
into a generic RTDL reference API:

```text
point columns -> grid cell descriptors -> radius cell candidates
```

The API is not X-HD-specific. The proof fixture is a facility/demand coverage
scenario, not Hausdorff or paper reproduction.

## What This Does Not Prove

This does not prove:

- X-HD scalable algorithm implementation;
- native/OptiX grid-cell traversal;
- nearest-state payload fusion;
- heavy-cell offload queues;
- radius-growth controller;
- Figure 5 or any paper performance result;
- author-performance parity.

## Architectural Position

Goal5138 is a system extraction step. It gives RTDL a public, app-neutral schema
for the first part of the route that X-HD needs, while keeping X-HD itself as an
application.

The remaining scalable-route gaps are still:

1. nearest-state reducer over cell candidates;
2. RT traversal over radius-expanded cell descriptors;
3. continuation/offload frontier from traversal to CUDA partner;
4. radius-growth controller.

## Recommended Next Goal

```text
Goal5139 - Generic nearest-state reducer and offload-frontier contract design
```

That next goal should define how a traversal stage carries per-query nearest
state and emits unresolved `(query_id, cell_id)` work to a continuation queue,
again without naming X-HD or Hausdorff in RTDL core.
