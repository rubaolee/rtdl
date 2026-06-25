# Call For Review: V4 Goal4637 AABB Front-Door Catalog Promotion

Please critically review Goal4637. The question is whether the successful
Goal4636C AABB POD gate was correctly converted into a V4 front-door/catalog
surface without overclaiming release, LibRTS paper, whole-app, or broad V4
performance wording.

## Requested Verdict Labels

- `approve_goal4637_aabb_frontdoor_catalog_promotion`
- `approve_with_required_amendments`
- `reject_catalog_promotion_as_overclaim`
- `reject_implementation_as_not_frontdoor_or_not_generic`

## Files To Review

- `future/v4/v4_goal4637_aabb_frontdoor_catalog_promotion_2026-06-25.md`
- `future/v4/v4_goal4636c_aabb_index_pod_gate_decision_2026-06-25.md`
- `future/v4/evidence/v4_goal4636c_aabb_index_all_ops_pod_gate_2026-06-25/m30_all_ops.json`
- `src/rtdsl/v4_aabb_index.py`
- `src/rtdsl/v4.py`
- `src/rtdsl/v4_operator_catalog.py`
- `src/rtdsl/v4_coverage_audit.py`
- `src/rtdsl/v4_release_decision.py`
- `src/rtdsl/v4_scope.py`
- `future/v4/README.md`
- `future/v4/tier2_operator_catalog.md`
- `future/v4/examples/aabb_index_all_ops_count.py`
- `future/v4/examples/v4_frontdoor_quickstart.py`
- `scripts/v4_catalog_regression_gate.py`
- `tests/v4_aabb_index_frontdoor_test.py`
- `tests/v4_frontdoor_test.py`
- `tests/v4_operator_catalog_test.py`
- `tests/v4_goal4627_coverage_audit_test.py`
- `tests/v4_goal4632_release_decision_test.py`
- `tests/v4_catalog_regression_gate_test.py`
- `tests/v4_scope_gate_test.py`

## Validation Run

```text
py -m unittest <all tests matching v4>
Ran 149 tests
OK
```

## Review Questions

1. Is `v4_aabb_index_query_2d_all_ops_count_prepared_runner` a legitimate
   generic V4 front-door surface, or does it leak LibRTS app identity?
2. Is it correct to list the measured partner/scope as `rtdl_native` rather than
   Torch, CuPy, or Numba?
3. Is the catalog promotion justified by the Goal4636C POD gate, given the
   `264.822x` median and `115.007x` total same-contract-family ratios?
4. Is the coverage promotion for `librts_spatial_index` from deferred to strong
   measured operator coverage justified without making a whole-app or paper
   claim?
5. Are the claim boundaries complete and sufficiently conservative?
6. Do the updated docs, quickstart, scope gate, catalog gate, and release
   decision remain internally consistent?
7. Does this goal move V4 forward on the formal high-performance release path,
   or is it merely process/churn?

## Non-Authorization

This review must not authorize V4 release, release-candidate wording, broad V4
speedup claims, whole-app speedup claims, all-benchmark speedup claims, LibRTS
paper reproduction claims, authors-code comparison claims, public true-zero-copy
claims, Tier-3 callback support, raw OptiX callback support, CuPy performance
claims, C ABI, embedding, non-Python host claims, or app-specific native
kernels.
