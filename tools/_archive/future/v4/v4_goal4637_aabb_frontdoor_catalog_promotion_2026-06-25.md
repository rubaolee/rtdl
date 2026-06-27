# V4 Goal4637 AABB Front-Door Catalog Promotion

Status: `goal4637_aabb_frontdoor_catalog_promoted_not_release`

Decision: `promote_aabb_index_to_measured_v4_frontdoor_catalog_not_release`

## Summary

Goal4637 turns the successful Goal4636C AABB POD gate into a user-visible V4
front-door/catalog surface.

- API surface: `v4_aabb_index_query_2d_all_ops_count_prepared_runner`
- import path: `rtdsl.v4`
- operator: `aabb_index_query_2d_all_ops_count`
- primitive: `AABB_INDEX_QUERY_2D`
- measured partner/scope: `rtdl_native`
- validated backends: `optix`, `embree`
- target coverage row: `librts_spatial_index`

## Evidence Carried Forward

Goal4636C POD gate:

- fixture: 1,000,000 boxes x 1,000 queries
- repeats: Embree 240, OptiX 240
- cross-backend count parity: pass
- accepted contract family: pass
- Embree / OptiX query median: `264.822x`
- Embree / OptiX query total: `115.007x`

Evidence files:

- `future/v4/evidence/v4_goal4636c_aabb_index_all_ops_pod_gate_2026-06-25/m30_all_ops.json`
- `future/v4/v4_goal4636c_aabb_index_pod_gate_decision_2026-06-25.md`
- `future/v4/reviews/goal4636c_aabb_index_target_protocol_review_record_2026-06-25.md`

## Implementation

- Added `src/rtdsl/v4_aabb_index.py` with:
  - `aabb_index_query_2d_all_ops_count_claim_boundary_v4`
  - `prepare_aabb_index_query_2d_all_ops_count_prepared_runner_v4`
  - `V4AabbIndexQuery2DAllOpsCountPreparedRunner`
- Exported the surface through `src/rtdsl/v4.py`.
- Added the measured operator row to `src/rtdsl/v4_operator_catalog.py`.
- Added planner aliases:
  - `aabb`
  - `aabb_index`
  - `aabb_index_query`
  - `aabb_index_query_2d`
  - `aabb_index_all_ops`
  - `aabb_index_all_ops_count`
  - `aabb_index_query_2d_all_ops_count`
- Promoted `librts_spatial_index` in `src/rtdsl/v4_coverage_audit.py` from
  deferred to strong measured operator coverage.
- Updated V4 front-door docs, Tier-2 catalog docs, scope gate, quickstart, and
  catalog regression gate.

## Validation

Focused/front-door tests:

```text
py -m unittest tests.v4_aabb_index_frontdoor_test tests.v4_frontdoor_test tests.v4_operator_catalog_test tests.v4_goal4627_coverage_audit_test tests.v4_goal4632_release_decision_test tests.v4_goal4636_aabb_index_target_test
Ran 35 tests
OK
```

Broader V4 test sweep:

```text
py -m unittest <all tests matching v4>
Ran 149 tests
OK
```

## Current V4 State After Goal4637

- measured surfaces: `8`
- candidate surfaces: `0`
- measured partners: `numba`, `rtdl_native`, `torch`
- coverage split: `4 strong / 4 partial / 0 candidate / 2 deferred`
- release authorized: `false`
- whole-app speedup authorized: `false`
- broad V4 speedup authorized: `false`

## Claim Boundary

This goal authorizes measured V4 operator-catalog coverage for the generic
`AABB_INDEX_QUERY_2D` all-ops count surface only.

It does not authorize:

- V4 release
- release-candidate wording
- broad V4 speedup wording
- whole-application speedup wording
- all-benchmark speedup wording
- LibRTS paper reproduction
- authors-code comparison
- public true-zero-copy claims
- Tier-3 callback support
- raw OptiX callback support
- CuPy performance claims
- C ABI / embedding / non-Python host claims
- app-specific native kernels

## Next Work

Move to the next release-hardening goal:

1. Run/update the catalog regression gate on the POD if the release path needs a
   fresh hardware-mode gate after the AABB addition.
2. Continue expanding measured operator coverage or proceed to the promoted
   benchmark release gate, depending on external review.
3. Keep external review debt visible until Claude/Antigravity/third-seat
   completion review is recorded.
