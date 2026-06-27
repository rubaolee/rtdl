# Call For Review: V4 Goal4638 Catalog Regression GPU Gate After AABB

Please critically review Goal4638.

## Requested Verdict Labels

- `approve_goal4638_catalog_regression_gpu_gate`
- `approve_with_required_amendments`
- `reject_gate_as_too_weak`
- `reject_due_to_claim_boundary_or_catalog_inconsistency`

## Files To Review

- `future/v4/v4_goal4638_catalog_regression_gpu_gate_after_aabb_2026-06-25.md`
- `future/v4/evidence/v4_goal4638_catalog_regression_gpu_after_aabb_2026-06-25.json`
- `future/v4/evidence/v4_goal4638_catalog_regression_gpu_after_aabb_2026-06-25.md`
- `scripts/v4_catalog_regression_gate.py`
- `future/v4/examples/aabb_index_all_ops_count.py`
- `future/v4/examples/v4_frontdoor_quickstart.py`
- `src/rtdsl/v4_release_decision.py`
- `src/rtdsl/v4_goal4638_catalog_regression_decision.py`
- `tests/v4_catalog_regression_gate_test.py`
- `tests/v4_goal4632_release_decision_test.py`

## Review Questions

1. Is the GPU catalog regression gate a meaningful release-hardening gate after
   adding AABB, or is it too weak?
2. Does the gate correctly include 11 examples, including AABB and the
   quickstart/planner paths?
3. Is it acceptable that this gate confirms catalog/front-door runnable health
   but does not count as an all-application benchmark or release gate?
4. Are claim boundaries still enforced for nested example payloads, including
   `all_benchmark_speedup_claim_authorized`?
5. Is the release-decision update correct: G8 passes, final release still false,
   and review debt remains visible?

## Non-Authorization

This review must not authorize V4 release, release-candidate wording, broad V4
speedup claims, whole-app speedup claims, all-benchmark speedup claims, public
true-zero-copy claims, Tier-3 callback support, raw OptiX callback support, CuPy
performance claims, C ABI, embedding, non-Python host claims, or app-specific
native kernels.
