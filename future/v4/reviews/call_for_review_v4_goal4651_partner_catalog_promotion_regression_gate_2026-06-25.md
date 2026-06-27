# Call For Review: V4 Goal4651 Partner Catalog Promotion And Regression Gate

Date: 2026-06-25

## Review Target

Please critically review Goal4651:

- report: `future/v4/v4_goal4651_partner_catalog_promotion_regression_gate_2026-06-25.md`
- machine evidence: `future/v4/evidence/v4_goal4651_partner_catalog_promotion_2026-06-25.json`
- catalog/planner code: `src/rtdsl/v4_operator_catalog.py`
- front door exports: `src/rtdsl/v4.py`
- tests: `tests/v4_goal4651_partner_catalog_promotion_test.py`

Source goals:

- Goal4649 CuPy gate:
  - `future/v4/v4_goal4649_cupy_frontdoor_certification_gate_2026-06-25.md`
  - `future/v4/evidence/v4_goal4649_cupy_grouped_reduction_gate_2026-06-25/pod_live_summary.json`
  - `future/v4/reviews/goal4649_completion_consensus_2026-06-25.md`
- Goal4650 fixed Numba gate:
  - `future/v4/v4_goal4650_fixed_numba_continuation_certification_gate_2026-06-25.md`
  - `future/v4/evidence/v4_goal4650_fixed_numba_continuation_certification_2026-06-25.json`
  - `future/v4/reviews/goal4650_completion_consensus_2026-06-25.md`

## Context

Goal4651 needed to update the catalog/planner after CuPy and fixed Numba
certification while preserving Claude AM1:

> partner migration/parity must not support "V4 faster than V2.14".

The implementation keeps the 8-row Tier-2 RT-core/operator catalog unchanged and
adds a separate `certified_partner_catalog_v4()` for partner-certified surfaces.
The planner and pushdown recognizer can route certified partner surfaces, but
claim flags remain false.

## Verification Already Run

```text
py -m unittest tests.v4_goal4651_partner_catalog_promotion_test tests.v4_operator_catalog_test tests.v4_frontdoor_test tests.v4_goal4649_cupy_certification_gate_test tests.v4_goal4649_cupy_certification_pod_evidence_test tests.v4_goal4650_fixed_numba_continuation_certification_test
```

Result:

```text
Ran 35 tests
OK
```

## Questions

Please answer directly:

1. Is Goal4651 complete enough to proceed to Goal4652 app route binding?
2. Is the separate `certified_partner_catalog_v4()` design correct, or should
   certified partner rows have been appended to the 8-row measured Tier-2
   catalog?
3. Does the implementation satisfy "no stale declared_unmeasured wording after
   certification" without claiming unmeasured partners?
4. Does the planner route CuPy grouped-vector-sum correctly and fail closed for
   unmeasured partners?
5. Does pushdown recognition handle certified partner surfaces without treating
   them as formal V4 speed evidence?
6. Are denominator/scale/source-evidence fields sufficient?
7. Are all AM1 and non-authorization boundaries preserved?

## Acceptable Verdict Labels

- `accept_goal4651_complete`
- `accept_with_minor_edits`
- `reject_goal4651_incomplete`
- `blocked_missing_context`

If rejecting, please identify the exact blocking file/field/test.

## Non-Authorization

This review must not authorize release, broad V4 speedup claims, whole-app
claims, all-benchmark claims, arbitrary Numba callback support, raw OptiX
callback support, public CuPy performance claims, true-zero-copy claims, C
ABI/embedding claims, non-Python host claims, or app-specific native kernels.
