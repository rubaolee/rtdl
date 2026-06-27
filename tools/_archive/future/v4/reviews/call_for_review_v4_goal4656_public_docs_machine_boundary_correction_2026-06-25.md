# Call For Review: V4 Goal4656 Public Docs And Machine Boundary Correction

Date: 2026-06-25

Requested verdict: one of

- `accept_goal4656_boundary_correction_complete_proceed_app_level_engineering`
- `accept_goal4656_with_required_amendments`
- `reject_goal4656_current_docs_or_machine_boundary_still_misleading`
- `blocked_missing_context`

## Files To Review

Primary report:

- `future/v4/v4_goal4656_public_docs_machine_boundary_correction_2026-06-25.md`

Current public/user docs:

- `README.md`
- `docs/current_v4_status.md`
- `docs/app_level_benchmark_summary.md`
- `docs/README.md`
- `docs/public_documentation_map.md`
- `docs/learn/performance_wording.md`
- `tutorials/current/README.md`
- `tutorials/current/05_measurement_boundaries.md`
- `examples/README.md`
- `future/v4/README.md`
- `future/v4/tier2_operator_catalog.md`
- `future/v4/v4_0_scope_gate.md`

Machine boundary files:

- `src/rtdsl/v4.py`
- `src/rtdsl/v4_release_decision.py`
- `src/rtdsl/v4_scope.py`
- `src/rtdsl/v4_goal4643_publication_decision.py`
- `src/rtdsl/v4_goal4644_post_release_guardrails.py`
- `scripts/v4_catalog_regression_gate.py`
- `scripts/v4_scope_gate.py`

Tests:

- `tests/v4_frontdoor_test.py`
- `tests/v4_catalog_regression_gate_test.py`
- `tests/v4_goal4632_release_decision_test.py`
- `tests/v4_goal4643_publication_decision_test.py`
- `tests/v4_goal4644_post_release_guardrails_test.py`
- `tests/v4_scope_gate_test.py`
- `tests/v4_goal4655_app_benchmark_analysis_test.py`

Upstream evidence:

- `future/v4/v4_goal4654_full_app_level_v2_14_v3_v4_pod_benchmark_2026-06-25.md`
- `future/v4/evidence/v4_goal4654_serious_20260625_2/summary.json`
- `future/v4/v4_goal4655_full_app_level_benchmark_analysis_2026-06-25.md`
- `future/v4/evidence/v4_goal4655_full_app_level_benchmark_analysis_2026-06-25.json`
- `future/v4/reviews/antigravity_v4_goal4655_full_app_benchmark_analysis_review_2026-06-25.md`

## Proposed Review Questions

1. Do the public docs now clearly state that current V4 evidence is
   operator-bounded and does not authorize formal app-level high-performance
   release wording?
2. Do the machine claim boundaries match the public docs?
3. Is it correct to mark Goal4643/Goal4644 publication records as superseded by
   Goal4655 rather than leaving `release_authorized: true` in current machine
   paths?
4. Do the tests lock the boundary strongly enough to prevent regression?
5. Is the right next step app-level V4 performance engineering rather than more
   release wording/process work?

## Verification To Check

The report records:

```text
59 tests OK
```

and a current wording scan with no matches for old release-authorized wording in
the scanned current/public/machine scope.

## Non-Authorization

This review request does not authorize formal app-level high-performance V4
release wording, broad speedup wording, whole-app speedup wording,
all-benchmark speedup wording, public true-zero-copy, Tier-3 callback support,
raw OptiX callback support, CuPy blanket performance claims, C ABI, embedding,
non-Python host binding, app-specific native kernels, or a release tag.
