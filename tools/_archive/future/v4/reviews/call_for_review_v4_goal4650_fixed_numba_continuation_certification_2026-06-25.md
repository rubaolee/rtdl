# Call For Review: V4 Goal4650 Fixed Numba Continuation Certification

Date: 2026-06-25

## Review Target

Please critically review Goal4650:

- report: `future/v4/v4_goal4650_fixed_numba_continuation_certification_gate_2026-06-25.md`
- machine evidence: `future/v4/evidence/v4_goal4650_fixed_numba_continuation_certification_2026-06-25.json`
- code: `src/rtdsl/v4_numba_fixed_continuation_certification.py`
- exports: `src/rtdsl/v4.py`
- tests: `tests/v4_goal4650_fixed_numba_continuation_certification_test.py`

Source evidence reused by Goal4650:

- `future/v4/evidence/v4_goal4635_component_union_pod_gate_embree_2026-06-25/summary.json`
- `src/rtdsl/v4_goal4635_component_union_promotion_decision.py`
- `tests/v4_goal4635_component_union_target_test.py`

## Context

Goal4650 is part of the revised V4 Goals4647-4658 chain. Goal4648 defined the
partner promotion contract. Goal4649 certified a narrow CuPy grouped-reduction
front-door route. Goal4650 should certify only the fixed Numba continuation
already measured in Goal4635:

- `fixed_radius_graph_component_union_3d`
- partner `numba`
- API `v4_fixed_radius_graph_component_union_3d_device_arrays`
- target row `rt_dbscan`

This must not become arbitrary Numba callback support.

## Verification Already Run

```text
py -m unittest tests.v4_goal4650_fixed_numba_continuation_certification_test tests.v4_goal4635_component_union_target_test tests.v4_operator_catalog_test tests.v4_goal4648_partner_promotion_contract_test
```

Result:

```text
Ran 30 tests
OK
```

## Questions

Please answer directly:

1. Is Goal4650 complete enough to proceed to Goal4651 partner catalog promotion?
2. Does it correctly reuse Goal4635 POD evidence without pretending this is a new
   POD result?
3. Are the numeric bars and correctness/parity gates explicit enough?
4. Does it preserve fixed-operator-only Numba support and block arbitrary Numba
   callback claims?
5. Does the planner fail closed for unmeasured `torch` and `cupy` component-union
   routes?
6. Does the Tier-3 custom callback path remain spike-only / rejected as
   appropriate?
7. Are all non-authorization boundaries preserved?

## Acceptable Verdict Labels

- `accept_goal4650_complete`
- `accept_with_minor_edits`
- `reject_goal4650_incomplete`
- `blocked_missing_context`

If rejecting, please identify the exact blocking file/field/test.

## Non-Authorization

This review must not authorize release, broad V4 speedup claims, whole-app
claims, all-benchmark claims, arbitrary Numba callback support, raw OptiX
callback support, CuPy performance claims, true-zero-copy claims, C ABI/embedding
claims, non-Python host claims, or app-specific native kernels.
