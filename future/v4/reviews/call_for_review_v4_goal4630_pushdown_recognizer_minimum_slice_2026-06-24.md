# Call For Review: V4 Goal4630 Push-Down Recognizer Minimum Slice

Date: 2026-06-24

Requested verdict labels:

- `accept_goal4630_pushdown_recognizer_minimum_slice`
- `accept_with_required_amendments`
- `reject_incomplete_fail_closed_boundary`
- `reject_overclaiming_or_route_drift`

Primary document:

- `future/v4/v4_goal4630_pushdown_recognizer_minimum_slice_2026-06-24.md`

Code and tests:

- `src/rtdsl/v4_operator_catalog.py`
- `src/rtdsl/v4.py`
- `tests/v4_goal4630_pushdown_recognizer_test.py`
- `tests/v4_operator_catalog_test.py`

Supporting context:

- `future/v4/rtdl_v4_0_three_tier_fused_architecture_design_2026-06-24.md`
- `future/v4/callback_and_operator_planning.md`
- `future/v4/reviews/goal4629_completion_consensus_and_review_debt_2026-06-24.md`

Focused test result:

```text
py -m unittest tests.v4_operator_catalog_test tests.v4_goal4630_pushdown_recognizer_test tests.v4_goal4629_weighted_sum_candidate_decision_test
Ran 23 tests
OK
```

Review objective:

Check whether Goal4630 implements the minimum V4 push-down recognizer required before final release decision work. The review should verify that recognized generic operators route to existing Tier-2 catalog plans and that unsupported/action-shaped/app-identity requests fail closed.

Questions:

1. Does `recognize_v4_pushdown_request` correctly implement a minimal recognizer rather than a full compiler?
2. Does it route measured generic operators to measured Tier-2 plans?
3. Does it preserve weighted-sum as candidate, not measured?
4. Does it fail closed for CuPy/unmeasured partner requests?
5. Does it fail closed for app-identity kernels and action-shaped callbacks?
6. Does it keep Tier-3 scalar callbacks spike-only, not V4.0 push-down support?
7. Are all non-authorization boundaries preserved?

Non-authorization requirements:

- Do not authorize V4 release.
- Do not authorize measured-catalog promotion.
- Do not authorize broad V4 speedup claims.
- Do not authorize whole-application speedup claims.
- Do not authorize true-zero-copy wording.
- Do not authorize Tier-3 callback support.
- Do not authorize raw OptiX callback support.
- Do not authorize C ABI / embedding claims.
- Do not authorize app-specific native kernels.

