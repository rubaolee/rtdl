# V4 Goal4651 Partner Catalog Promotion And Regression Gate

Date: 2026-06-25
Status: `goal4651_partner_catalog_promotion_regression_gate_pass_pending_review`

## Purpose

Goal4651 updates the V4 catalog/planner after Goal4649 CuPy certification and
Goal4650 fixed Numba certification. The important design choice is deliberate:

- keep `measured_operator_catalog_v4()` as the 8-row Tier-2 RT-core/operator
  catalog;
- add `certified_partner_catalog_v4()` as a separate partner-certification
  catalog;
- update `plan_operator_request_v4()` and `recognize_pushdown_request_v4()` so
  certified partner surfaces are reachable without being counted as formal V4
  speed wins.

This avoids the AM1 failure mode: partner migration or partner parity must not
become a fake "V4 is faster than V2.14" claim.

## Implemented Changes

Code:

- `src/rtdsl/v4_operator_catalog.py`
  - added `V4_CERTIFIED_PARTNER_OPERATOR_SURFACES`;
  - added `certified_v4_partner_operator_catalog()`;
  - added planner status `certified_partner_measured_ready`;
  - added fail-closed status `certified_partner_declared_unmeasured`;
  - taught pushdown recognition to accept certified partner surfaces only for
    measured partners.
- `src/rtdsl/v4.py`
  - exported `certified_partner_catalog_v4()`;
  - added `certified_partners`, `certified_partner_surfaces`, and
    `certified_partner_surface_count` to `claim_boundary_v4()`.

Tests:

- `tests/v4_goal4651_partner_catalog_promotion_test.py`

Machine evidence:

- `future/v4/evidence/v4_goal4651_partner_catalog_promotion_2026-06-25.json`

## Certified Partner Catalog

Goal4651 promotes two certified partner surfaces:

| Operator | Partner | Route | Claim Class |
| --- | --- | --- | --- |
| `grouped_vector_sum_f64x2` | `cupy` | `prepare_grouped_vector_sum_2d_partner_columns_session(partner='cupy')` | partner-certified surface, not formal V4 speed win |
| `fixed_radius_graph_component_union_3d` | `numba` | `v4_fixed_radius_graph_component_union_3d_device_arrays` | fixed Numba certified Tier-2 operator surface, not whole-app speed win |

The CuPy row is intentionally not appended to the 8-row Tier-2 RT-core catalog:
it is a partner continuation/front-door certification row. Treating it as a
ninth RT-core V4 operator would blur the boundary that Claude AM1 required.

## Regression Rules

Goal4651 enforces:

- measured partners match raw evidence;
- unmeasured partners fail closed;
- baseline denominator and scale are recorded for every certified partner row;
- broad speedup wording remains unauthorized;
- app-identity kernels remain unauthorized;
- partner migration/parity rows cannot support formal V4 speed claims.

Planner behavior:

| Request | Expected |
| --- | --- |
| `grouped_vector_sum`, partner `cupy` | `certified_partner_measured_ready` |
| `grouped_vector_sum`, partner `torch` | `certified_partner_declared_unmeasured` |
| `grouped_vector_sum`, partner `numba` | `certified_partner_declared_unmeasured` |
| `component_union`, partner `numba` | `tier2_measured_ready` |

Pushdown behavior:

- measured CuPy grouped vector sum: `pushdown_recognized_certified_partner_surface`;
- unmeasured partner grouped vector sum: `pushdown_fail_closed_unmeasured_certified_partner`;
- app-identity kernels remain rejected by the existing app-identity guard.

## Verification

Command:

```text
py -m unittest tests.v4_goal4651_partner_catalog_promotion_test tests.v4_operator_catalog_test tests.v4_frontdoor_test tests.v4_goal4649_cupy_certification_gate_test tests.v4_goal4649_cupy_certification_pod_evidence_test tests.v4_goal4650_fixed_numba_continuation_certification_test
```

Result:

```text
Ran 35 tests
OK
```

Note: local Windows Python emitted the known startup warning
`Could not find platform independent libraries <prefix>`, but tests exited
successfully.

## Goal-Level Decision Audit

Decision:

Create a separate certified-partner catalog rather than appending CuPy grouped
vector sum to the Tier-2 measured RT-core catalog.

1. Was I stupid?
   No. This is the conservative path that preserves the AM1 boundary.

2. What action would have made the decision stupid?
   Counting the CuPy grouped-vector-sum row as a ninth measured RT-core V4
   operator or using its partner CPU denominator speedup as a formal V4-vs-V2.14
   claim.

3. Was there another path?
   Yes: append every certified partner surface to `measured_operator_catalog_v4()`
   directly. That would simplify one API but risk misrepresenting partner
   certification as V4 operator superiority.

4. Can I now take a better path?
   Yes. Keep the 8-row Tier-2 catalog intact, expose certified partner rows
   explicitly, and feed both into Goal4652 route binding.

## Non-Authorization

Goal4651 does not authorize release, broad V4 speedup claims, whole-app claims,
all-benchmark claims, arbitrary Numba callback support, raw OptiX callback
support, public CuPy performance claims, true-zero-copy claims, C ABI/embedding
claims, non-Python host claims, or app-specific native kernels.
