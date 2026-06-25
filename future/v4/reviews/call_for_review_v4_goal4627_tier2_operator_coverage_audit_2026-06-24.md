# Call For Review: V4 Goal4627 Tier-2 Operator Coverage Audit

Date: 2026-06-24

Requested verdict labels:

- `accept_goal4627_coverage_audit`
- `accept_with_required_amendments`
- `reject_goal4627_coverage_audit_misleading`

## Review Request

Please critically review:

- `future/v4/v4_goal4627_tier2_operator_coverage_audit_2026-06-24.md`
- `src/rtdsl/v4_coverage_audit.py`
- `tests/v4_goal4627_coverage_audit_test.py`

Focused test:

- `py -m unittest tests.v4_goal4627_coverage_audit_test`
- Result: `OK`, 4 tests

## Current Audit Claim

The audited set is the 10 promoted benchmark apps. Current classification:

- `strong_measured_operator_coverage`: 1
- `partial_measured_operator_coverage`: 5
- `candidate_not_measured_release_coverage`: 1
- `deferred_or_uncovered_v4_0`: 3

This is explicitly not an 80% public coverage claim and not a release claim.

## Goal4628 Recommendation

Recommended second Tier-2 same-contract gate:

- app anchor: `raydb_style`
- operator:
  `v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays`
- reason: non-fixed-radius, generic grouped reduction, serious RTX A5000 POD
  evidence, prior external promotion review, and not tied to the weighted-sum
  candidate.

Goal4628 should be a scorecard reconciliation/acceptance gate over the existing
grouped-i64 evidence, with a fresh POD rerun only if review finds a
same-contract or product-boundary gap.

## Questions

1. Does the audit cover the right 10 promoted benchmark apps?
2. Are the coverage labels honest and conservative?
3. Is `triangle_counting` correctly kept as candidate-bound rather than treated
   as measured because weighted-sum remains candidate-only?
4. Are `barnes_hut`, `spatial_rayjoin`, and `librts_spatial_index` correctly
   kept deferred/uncovered for V4.0?
5. Is `raydb_style` / grouped-i64 the right Goal4628 recommendation, or should
   another operator be selected?
6. Is it acceptable for Goal4628 to reconcile existing serious POD evidence
   instead of rerunning POD immediately, provided the evidence passes review?
7. What amendments are required before Goal4627 can be marked complete?

## Non-Authorization

This review request does not authorize:

- V4 release
- V4 release-candidate status
- public broad speedup wording
- whole-application speedup wording
- public true-zero-copy wording
- Tier-3 callback support
- raw OptiX callback support
- CuPy performance claims
- C ABI / embedding / non-Python-host work
- app-specific native kernels
