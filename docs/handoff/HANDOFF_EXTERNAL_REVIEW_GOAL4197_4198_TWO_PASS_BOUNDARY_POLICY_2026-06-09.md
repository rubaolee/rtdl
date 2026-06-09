# External Review Request: Goals4197-4198 Two-Pass Boundary Policy

Date: 2026-06-09

Please perform an independent read-only review of the Goal4197/Goal4198 chain.

## Context

RTDL is trying to improve RT-DBSCAN-style fixed-radius component signatures
without reintroducing app-specific native engine logic. Goal4193 registered a
candidate generic primitive, `continuation.predicate_aware_boundary_union`.
Goal4194 added a deterministic Python reference contract. Goal4197 then threaded
an explicit `boundary_assignment_policy="lowest_component_root_two_pass"` option
through the generic OptiX+Numba fixed-radius grouped-stream front door. Goal4198
added RTX 4000 Ada pod evidence that the policy executes and records native pass
count `2`.

## Files To Inspect

- `docs/reports/goal4197_predicate_boundary_lowest_root_two_pass_policy_2026-06-09.md`
- `docs/reports/goal4198_predicate_boundary_two_pass_policy_pod_evidence_2026-06-09.md`
- `docs/reports/goal4198_predicate_boundary_two_pass_policy_pod_rtx4000ada/two_pass_clustered_smoke.stdout.json`
- `src/native/optix/rtdl_optix_core.cpp`
- `src/rtdsl/partner_adapters.py`
- `src/rtdsl/v2_8_fixed_radius_graph_component_front_door.py`
- `tests/goal4197_predicate_boundary_lowest_root_two_pass_policy_test.py`
- `tests/goal4198_predicate_boundary_two_pass_policy_pod_evidence_test.py`

## Review Questions

1. Does Goal4197 keep the native engine app-agnostic, with no DBSCAN/clustering
   policy embedded in native ABI or native semantic names?
2. Is the `lowest_component_root_two_pass` policy explicit and user-selected,
   not hidden dispatch or auto-partner selection?
3. Does Goal4198 prove only RTX execution and metadata integrity, not speedup,
   release readiness, true zero-copy, or broad RT-core claims?
4. Is the clustered pod artifact credible evidence that the native route reports
   pass count `1` for the default policy and `2` for the two-pass policy while
   preserving the counts-only signature?
5. What should be required before this policy can become a promoted default or
   release-facing RT-DBSCAN route?

## Expected Output

Write a review file under `docs/reviews/` named either:

- `goal4199_claude_review_goal4197_4198_two_pass_boundary_policy_2026-06-09.md`
- `goal4200_gemini_review_goal4197_4198_two_pass_boundary_policy_2026-06-09.md`

Use one of these verdict values: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.

Do not mutate source code. Running focused tests is allowed.
