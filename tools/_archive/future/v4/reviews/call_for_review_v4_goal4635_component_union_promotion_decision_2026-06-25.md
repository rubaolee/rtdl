# Call For Review: V4 Goal4635 Component-Union Promotion Decision

Please critically review the Goal4635 component-union promotion decision.

Requested verdict labels:

- `accept_goal4635_component_union_promotion_not_release`
- `accept_with_required_amendments`
- `reject_promotion_keep_partial`
- `blocked_need_more_evidence`

## Files To Review

- `future/v4/v4_goal4635_component_union_promotion_decision_2026-06-25.md`
- `future/v4/evidence/v4_goal4635_component_union_pod_gate_embree_2026-06-25/summary.json`
- `future/v4/evidence/v4_goal4635_component_union_pod_gate_embree_2026-06-25/README.md`
- `src/rtdsl/v4_goal4635_component_union_promotion_decision.py`
- `src/rtdsl/v4_operator_catalog.py`
- `src/rtdsl/v4_coverage_audit.py`
- `src/rtdsl/v4_release_decision.py`
- `tests/v4_goal4635_component_union_target_test.py`
- `tests/v4_operator_catalog_test.py`
- `tests/v4_goal4627_coverage_audit_test.py`
- `tests/v4_goal4632_release_decision_test.py`
- `future/v4/README.md`
- `future/v4/tier2_operator_catalog.md`

## Questions

1. Does the POD evidence justify promoting `fixed_radius_graph_component_union_3d`
   to measured V4 Tier-2 operator coverage?
2. Is the Numba-only partner boundary explicit enough?
3. Is it correct to move `rt_dbscan` from partial to strong measured operator
   coverage while still forbidding whole-app RTDBSCAN speedup wording?
4. Are the measured ratios material enough for this operator gate
   (`1.393x` hot vs Embree, `1.600x` wall vs Embree, `1.208x` wall vs legacy)?
5. Did the promotion avoid adding an app-specific DBSCAN-native kernel?
6. Do catalog, coverage, release decision, and docs preserve all non-release
   boundaries?
7. If accepted, what is the next highest-value V4 release-hardening goal?

## Non-Authorization To Preserve

This review must not authorize:

- V4 release
- V4 release candidate
- broad V4 speedup wording
- whole-application speedup wording
- all-benchmark speedup wording
- public true-zero-copy wording
- Tier-3 callback support
- raw OptiX callback support
- CuPy component-union performance
- Torch component-union performance
- C ABI / embedding / non-Python host claims
- application-specific native kernels
