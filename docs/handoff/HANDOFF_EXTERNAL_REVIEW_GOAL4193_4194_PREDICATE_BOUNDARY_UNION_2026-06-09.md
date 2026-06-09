# External Review Request: Goals4193-4194 Predicate-Aware Boundary Union

Date: 2026-06-09

## Context

RTDL is pursuing major runtime-level performance improvements without adding
app-specific logic to the native engine. Goal4190 showed that an RT-DBSCAN-style
counts-only shortcut can match counts signatures, but it does not solve the
policy-bound component-size contract. The intended reusable direction is a
generic primitive/contract for predicate-aware fixed-radius component union.

## Artifacts To Review

- `docs/reports/goal4190_rt_dbscan_counts_only_mixed_route_probe_rtx4000ada_2026-06-09.md`
- `docs/reports/goal4193_predicate_aware_boundary_union_candidate_primitive_2026-06-09.md`
- `docs/reports/goal4194_predicate_aware_boundary_union_reference_contract_2026-06-09.md`
- `src/rtdsl/primitive_hierarchy.py`
- `src/rtdsl/predicate_aware_boundary_union.py`
- `tests/goal4193_predicate_aware_boundary_union_candidate_test.py`
- `tests/goal4194_predicate_aware_boundary_union_reference_test.py`

## Questions

1. Does Goal4193 correctly register `continuation.predicate_aware_boundary_union`
   as a generic `candidate_behavior` primitive without encoding RT-DBSCAN or
   other app-specific policy in the primitive hierarchy?
2. Does Goal4194 provide a suitable deterministic reference contract for future
   native/partner implementations?
3. Is the `lowest_component_root` policy a reasonable first same-contract oracle
   for policy-bound component-size signatures?
4. Are the claim boundaries honest: no route promotion, no release wording, no
   public speedup claim, no true-zero-copy claim, no app-specific native-engine
   logic?
5. What should be required before this candidate can become a promoted native or
   partner-backed primitive?

## Required Output

Write a review under `docs/reviews/` with one of these verdicts:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Use a distinct reviewer identity in the filename, for example:

- `docs/reviews/goal4195_claude_review_goal4193_4194_predicate_boundary_union_2026-06-09.md`
- `docs/reviews/goal4196_gemini_review_goal4193_4194_predicate_boundary_union_2026-06-09.md`

Do not mutate source code. Running the focused tests is encouraged:

```powershell
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal4193_predicate_aware_boundary_union_candidate_test tests.goal4194_predicate_aware_boundary_union_reference_test
```
