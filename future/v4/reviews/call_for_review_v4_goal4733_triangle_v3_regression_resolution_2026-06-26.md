# Call For Review: V4 Goal4733 Triangle V3-Regression Resolution

Please review:

- `future/v4/v4_goal4733_triangle_v3_regression_resolution_2026-06-26.md`
- `future/v4/evidence/v4_goal4733_triangle_v3_regression_resolution_2026-06-26.json`
- `scripts/v4_goal4733_triangle_focused_pod.py`
- `future/v4/evidence/v4_goal4733_triangle_focused_20260626/summary.json`
- `future/v4/evidence/v4_goal4733_triangle_focused_20260626/summary.md`
- `future/v4/evidence/v4_goal4733_triangle_focused_20260626/raw/v2_14_triangle_counting.json`
- `future/v4/evidence/v4_goal4733_triangle_focused_20260626/raw/v3_0_2_triangle_counting.json`
- `future/v4/evidence/v4_goal4733_triangle_focused_20260626/raw/v4_current_triangle_counting.json`
- `tests/v4_goal4733_triangle_focused_rerun_test.py`

## Context

Goal4669 reported triangle counting as V4/V2.14 hot `4.055x` but V4/V3.0.2
hot `0.948x`. The underlying hot metric was about `0.2 ms`, measured with only
`repeat=7`.

Goal4733 reran the same serious fixture with `repeat=201`, `warmup=20`.

Focused result:

- V4/V2.14 hot: `6.380727131464089`
- V4/V3.0.2 hot: `1.0433948035922396`
- all rows correctness parity: `true`
- V4 residency metadata pass: `true`

## Questions For Reviewer

1. Is it correct to classify the old Goal4669 V4/V3 triangle regression as a
   low-repeat sampling artifact after this high-repeat focused rerun?
2. Is the focused rerun serious enough to update the next app-level matrix as a
   delta row without erasing the old frozen Goal4669 row?
3. Does the evidence show correctness parity for all three versions?
4. Does the V4 row preserve the intended generic prepared segment replay path
   and residency metadata?
5. Is it correct that no code optimization was required for Goal4733 after the
   rerun cleared the regression?
6. Are the non-authorization boundaries sufficient?

## Requested Verdict Labels

- `accept_goal4733_triangle_regression_cleared_by_high_repeat_rerun`
- `accept_with_required_amendments`
- `reject_goal4733_insufficient_or_not_comparable`

## Non-Authorization

This review must not authorize final V4 tag, public speed claims, whole-app
high-performance claims, all-benchmark speedups, geomean headlines, arbitrary
callbacks, raw OptiX callbacks, app-specific native kernels, true-zero-copy
wording, or erasure of the old Goal4669 frozen matrix row.
