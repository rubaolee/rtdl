# Call For Review - Goal5196 Local-Grid Dense Lookup

Please strictly review Goal5196:

```text
history/internal_docs/goal5196_local_grid_dense_lookup_result_2026-07-08.md
```

Relevant implementation:

```text
src/rtdsl/partner_continuations.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_subset_scaling_gate.py
tests/goal5196_local_grid_dense_lookup_test.py
```

Relevant artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_local_grid_seed_dense_lookup_goal5196_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_local_grid_seed_dense_lookup_final2_goal5196_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_grid_cell_budget1_dense_lookup_goal5196_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_grid_cell_budget2_dense_lookup_goal5196_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_grid_branch_bound_dense_lookup_goal5196_graphics_dragon_happy_buddha_2026-07-08.json
```

## Context

Goal5195 reduced the native frontier / inline phase to about `0.93-0.94s`.
The local-grid seed remained about `0.85s` in the final metadata-confirmation
run. Goal5196 targets the generic local-grid seed lookup path: instead of doing
a binary search over occupied `original_cell_ids` for each probed grid cell, it
uses a dense encoded-cell -> compact-cell-position table when the grid volume is
below `dense_lookup_max_cells`. The same generic lookup path is also applied to
the grid-cell-budget and grid-branch-bound seed helpers, then retested as route
controls.

This must be reviewed as a generic grid-seed lookup optimization, not as an
X-HD-specific shortcut.

## Review Questions

1. Is the dense lookup implementation app-neutral and free of X-HD / paper /
   author identity?
2. Does the dense table preserve the same occupied-cell lookup semantics as the
   previous binary search over `original_cell_ids` for local-grid,
   grid-cell-budget, and grid-branch-bound seeds?
3. Is the fallback to `binary_search_original_cell_ids` sufficient to avoid
   unbounded dense allocation for large grids?
4. Do the tests prove both default dense lookup and forced binary-search
   fallback, and do they compare output equality across the affected seed
   helpers?
5. Are the metadata fields (`cell_lookup_strategy`,
   `dense_lookup_cell_capacity`, `dense_lookup_max_cells`) sufficient for later
   evidence review?
6. Does the POD evidence show the full-public Level-B route still matches the
   author HDResult?
7. Is the claimed route-local timing delta sound for the default local-grid
   route:
   seed about `0.855s -> 0.555s` and route about `2.553s -> 2.256s`?
8. Is it correct that native frontier / inline time is essentially unchanged,
   because this goal only targets seed lookup?
9. Does the budget/branch-bound retest support keeping dense local-grid as the
   default route, with budget and branch-bound remaining optional controls?
10. Are the claim boundaries correct: no author-vs-RTDL ratio, no exact paper
   dataset reproduction, no full X-HD paper reproduction, and no author RT-core
   algorithm claim?
11. Should Goal5196 close as `implemented_review_pending` with verdict
    `local_grid_dense_lookup_approved`, or are amendments required?

## Expected Answer Shape

```text
Verdict: <label>

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Answers:
1. ...
...
11. ...
```
