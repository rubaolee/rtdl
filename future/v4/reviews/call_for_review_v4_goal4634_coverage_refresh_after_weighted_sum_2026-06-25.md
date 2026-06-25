# Call For Review: V4 Goal4634 Coverage Refresh After Weighted-Sum Promotion

Date: 2026-06-25

Requested verdict labels:

- `accept_goal4634_coverage_refresh_not_release`
- `accept_with_required_amendments`
- `reject_goal4634_overclaims_or_invalid_coverage`
- `blocked_review_unavailable`

## Context

Goal4633 promoted `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays` from
candidate to measured Torch CUDA Tier-2 surface, with POD evidence:

- `future/v4/evidence/v4_goal4633_weighted_sum_promotion_gate_2026-06-25.json`
- `future/v4/evidence/v4_goal4633_weighted_sum_promotion_gate_2026-06-25.md`

Goal4634 refreshes the coverage audit after that promotion.

## Files To Review

- `src/rtdsl/v4_coverage_audit.py`
- `src/rtdsl/v4_release_decision.py`
- `tests/v4_goal4627_coverage_audit_test.py`
- `tests/v4_goal4629_weighted_sum_candidate_decision_test.py`
- `tests/v4_goal4632_release_decision_test.py`
- `future/v4/v4_goal4634_coverage_audit_refresh_after_weighted_sum_2026-06-25.md`
- `future/v4/reviews/goal4633_completion_consensus_and_review_debt_2026-06-25.md`

## Claimed Goal4634 Result

The coverage split moved from:

- strong measured: `1`
- partial measured: `5`
- candidate: `1`
- deferred: `3`

to:

- strong measured: `2`
- partial measured: `5`
- candidate: `0`
- deferred: `3`

The only moved row is:

- `triangle_counting`: candidate -> strong measured operator coverage.

Rationale:

- the dominant any-hit weighted/count continuation path now has measured Torch
  CUDA weighted-sum operator evidence after Goal4633;
- grouped-i64 remains adjacent measured grouped-reduction coverage;
- this is operator coverage only, not whole-app triangle-counting speedup.

## Test Evidence

The following command passed locally:

```powershell
py -m unittest tests.v4_goal4626_section8_scorecard_protocol_test tests.v4_goal4627_coverage_audit_test tests.v4_goal4628_second_gate_scorecard_test tests.v4_goal4629_weighted_sum_candidate_decision_test tests.v4_goal4630_pushdown_recognizer_test tests.v4_goal4631_tier3_spike_decision_test tests.v4_goal4632_release_decision_test tests.v4_catalog_regression_gate_test tests.v4_frontdoor_test tests.v4_operator_catalog_test tests.v4_goal4633_weighted_sum_promotion_gate_protocol_test tests.v4_goal4633_weighted_sum_promotion_decision_test tests.v4_ray_triangle_device_array_api_test
```

Result:

- `Ran 74 tests`
- `OK`

## Specific Questions

1. Is it valid for Goal4634 to classify `triangle_counting` as strong measured
   operator coverage after Goal4633?
2. Does the code preserve the distinction between historical Goal4629
   candidate decision and current Goal4633/4634 measured coverage state?
3. Does `v4_release_decision.py` keep V4 blocked from release despite the
   weighted-sum promotion?
4. Are the remaining release blockers correct and sufficiently explicit?
5. Does the refresh avoid whole-app speedup, all-benchmark speedup, CuPy,
   Tier-3, true-zero-copy, C ABI, and app-specific kernel overclaims?
6. Is Goal4634 complete enough to proceed to Goal4635 coverage expansion?

## Required Non-Authorization

This review must not authorize:

- V4 release;
- V4 release candidate;
- broad V4 speedup;
- whole-app speedup;
- all-benchmark speedup;
- CuPy performance;
- Tier-3 support;
- public true-zero-copy;
- C ABI / embedding / non-Python host claims;
- app-specific native kernels.
