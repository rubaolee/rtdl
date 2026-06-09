# External Review Request: Goals4201-4202 RT-DBSCAN Boundary Policy Decision

Date: 2026-06-09

Please perform an independent read-only review of the Goal4201/Goal4202 chain.

## Context

Goal4197 introduced an explicit `lowest_component_root_two_pass` policy for the
generic OptiX+Numba fixed-radius grouped-stream front door. Goal4198 proved the
policy executes on RTX hardware. Goals4201 and 4202 ask whether two-pass should
be promoted or whether the fast one-pass route already satisfies the deterministic
reference contract.

## Files To Inspect

- `docs/reports/goal4201_rt_dbscan_boundary_policy_fair_timing_2026-06-09.md`
- `docs/reports/goal4201_rt_dbscan_boundary_policy_fair_timing_rtx4000ada/fair_timing_repeat5.json`
- `docs/reports/goal4202_rt_dbscan_single_pass_reference_parity_2026-06-09.md`
- `docs/reports/goal4202_rt_dbscan_single_pass_reference_parity_rtx4000ada/reference_parity.json`
- `scripts/goal4201_rt_dbscan_boundary_policy_fair_timing.py`
- `scripts/goal4202_rt_dbscan_single_pass_reference_parity.py`
- `src/rtdsl/partner_adapters.py`
- `src/rtdsl/predicate_aware_boundary_union.py`
- `tests/goal4201_rt_dbscan_boundary_policy_fair_timing_evidence_test.py`
- `tests/goal4202_rt_dbscan_single_pass_reference_parity_evidence_test.py`

## Questions

1. Is the Goal4201 timing methodology fair enough to conclude that two-pass is
   correctness/reference machinery, not a default performance route?
2. Is the Goal4202 reference comparison valid: CPU candidate pairs, native
   predicate flags, Goal4194 reference labels, and native label comparison?
3. Does the evidence support the current decision: keep two-pass explicit and
   continue using one-pass as the performance route, pending broader parity?
4. Are there any claim-boundary leaks around speedup, release readiness,
   true-zero-copy, broad RT-core acceleration, hidden dispatch, or app-specific
   native engine logic?
5. What exact evidence is still required before renaming/promoting the one-pass
   route as a policy-bound deterministic route?

## Expected Output

Write one of:

- `docs/reviews/goal4203_claude_review_goal4201_4202_rtdbscan_policy_decision_2026-06-09.md`
- `docs/reviews/goal4204_gemini_review_goal4201_4202_rtdbscan_policy_decision_2026-06-09.md`

Use one verdict: `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`.

Do not mutate source code. Running focused tests is allowed.
