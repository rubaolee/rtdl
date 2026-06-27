# Call For Review: V4 Goal4638 Formal Scorecard Freeze Amendment Closure

Please review only the required amendment from the prior Claude review:

- prior review file:
  `future/v4/reviews/claude_v4_goal4638_formal_release_scorecard_freeze_review_2026-06-25.raw.md`
- prior verdict:
  `approve_with_required_amendments_before_goal4639`
- required amendment:
  add a self-contained Performance Floor Reference Table so Goal4639 pass/fail
  does not depend on post-result interpretation of upstream evidence.

## Requested Verdict Labels

Choose exactly one:

- `approve_goal4638_amendment_closed_continue_goal4639`
- `approve_with_remaining_amendments_before_goal4639`
- `reject_goal4638_freeze_do_not_run_goal4639`

## Artifacts To Review

- `future/v4/v4_goal4638_formal_release_scorecard_freeze_2026-06-25.md`
- `src/rtdsl/v4_goal4638_formal_scorecard_freeze.py`
- `tests/v4_goal4638_formal_scorecard_freeze_test.py`
- `src/rtdsl/v4_release_decision.py`
- `tests/v4_goal4632_release_decision_test.py`

## Amendment Implemented

The freeze document now includes a `Performance Floor Reference Table` with one
row per measured surface:

1. `v4_fixed_radius_count_threshold_2d_device_arrays`
2. `v4_closest_hit_grouped_argmin_3d_device_arrays`
3. `v4_ray_triangle_any_hit_flags_2d_device_arrays`
4. `v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays`
5. `v4_point_group_nearest_witness_2d_device_arrays`
6. `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays`
7. `v4_fixed_radius_graph_component_union_3d_device_arrays`
8. `v4_aabb_index_query_2d_all_ops_count_prepared_runner`

For each surface the table states:

- minimum floor;
- observed anchor values;
- canonical source evidence.

The Python freeze module now exposes `V4_GOAL4638_PERFORMANCE_FLOORS` and
validates that:

- exactly one floor exists per measured surface;
- floor order matches measured-surface order;
- every row has `floor_kind`, `minimum_floor`, `observed_anchor`, and
  `canonical_source`;
- no placeholder numeric like `X.XX` remains.

## Verification

Targeted local tests:

```powershell
py -m unittest tests.v4_goal4638_formal_scorecard_freeze_test tests.v4_goal4632_release_decision_test
```

Result: `10 tests OK`.

Full local V4 sweep:

```powershell
$modules = rg --files tests | Where-Object { $_ -match 'v4' -and $_ -like '*.py' } | ForEach-Object { $_.Replace('\','.') -replace '/','.' -replace '\.py$','' } | Sort-Object
py -m unittest @modules
```

Result: `154 tests OK`.

## Review Questions

1. Does the new floor table close the required amendment from the prior review?
2. Are any floor rows still vague enough to permit post-result reinterpretation?
3. Are the weak/limited surfaces, especially any-hit flags, bounded honestly
   rather than overclaimed?
4. Is Goal4639 now allowed to start under the rule that any missing reviewer
   seat must be recorded as review debt?

## Non-Authorization

This review must not authorize V4 release, V4 release-candidate wording, broad
V4 speedup claims, whole-app speedup claims, all-benchmark speedup claims,
public true-zero-copy claims, Tier-3 callback support, raw OptiX callback
support, CuPy performance claims, C ABI, embedding, non-Python host claims, or
app-specific native kernels.
