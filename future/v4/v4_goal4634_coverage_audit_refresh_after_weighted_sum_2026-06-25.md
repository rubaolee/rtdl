# V4 Goal4634 Coverage Audit Refresh After Weighted-Sum Promotion

Date: 2026-06-25

Status: `goal4634_coverage_refreshed_not_release`

## Purpose

Refresh the ten benchmark-family V4 coverage audit after Goal4633 promoted
`v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays` from candidate to
measured Torch CUDA Tier-2 surface.

## Result

Previous split from Goal4627:

- strong measured: `1`
- partial measured: `5`
- candidate: `1`
- deferred: `3`

Current split after Goal4634:

- strong measured: `2`
- partial measured: `5`
- candidate: `0`
- deferred: `3`

The moved row is:

- `triangle_counting`: `candidate_not_measured_release_coverage` ->
  `strong_measured_operator_coverage`

Reason:

- triangle counting's dominant any-hit weighted/count continuation path now has
  a measured Torch CUDA weighted-sum operator after Goal4633;
- grouped-i64 remains measured adjacent grouped-reduction coverage;
- this is operator coverage, not whole-app triangle-counting speedup evidence.

## Current Remaining Coverage Gaps

Partial measured rows:

- `hausdorff_xhd`
- `rt_dbscan`
- `robot_collision`
- `contact_manifold`
- `rtnn`

Deferred rows:

- `spatial_rayjoin`
- `barnes_hut`
- `librts_spatial_index`

There are no current candidate rows.

## Next Actions

For Goal4635 and Goal4636, choose generic operators that can move partial or
deferred rows without app-identity kernels. Candidate directions include:

- component-union or connected-component continuation for `rt_dbscan`;
- ranked/top-k summary for `rtnn`;
- AABB/relation prefilter only if expressible as a generic operator, not
  `spatial_rayjoin` app logic.

## Code And Tests

Code:

- `src/rtdsl/v4_coverage_audit.py`

Tests:

- `tests/v4_goal4627_coverage_audit_test.py`

## Non-Authorization

Goal4634 does not authorize:

- V4 release;
- V4 release candidate;
- whole-app speedup claims;
- all-benchmark speedup claims;
- CuPy performance claims;
- Tier-3 support;
- public true-zero-copy wording;
- C ABI / embedding / non-Python host claims;
- app-specific native kernels.
