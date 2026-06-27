# V4 Goal4652 App Route Binding Or Blocker Declaration

Date: 2026-06-25
Status: goal completed locally, pending/recorded review seats

## Purpose

Goal4652 binds every benchmark app to a concrete V4 route class before
Goal4653 freezes the full app-level V2.14/V3/V4 benchmark protocol. The point is
to prevent a fake all-app benchmark where an app silently falls back to V2/V3
while being counted as V4.

This goal does not authorize app-level speed claims. It only declares which apps
have a current V4 route, which apps have partial operator coverage, and which
apps are blocked or deferred.

## Files Changed

- `src/rtdsl/v4_app_route_binding.py`
- `src/rtdsl/v4.py`
- `tests/v4_goal4652_app_route_binding_test.py`

## Evidence

- Route-binding matrix:
  `future/v4/evidence/v4_goal4652_app_route_binding_matrix_2026-06-25.json`
- Test command:
  `py -m unittest tests.v4_goal4652_app_route_binding_test tests.v4_goal4651_partner_catalog_promotion_test tests.v4_operator_catalog_test tests.v4_goal4627_coverage_audit_test`
- Test result:
  `27 tests OK`

## Route Binding Summary

| Class | Count | Meaning |
| --- | ---: | --- |
| `v4_fused_operator_addressable` | 4 | Current V4 generic operator route exists and planner dry-run passes. |
| `requires_new_generic_operator` | 4 | V4 operator coverage exists, but whole-app route is not complete. |
| `no_v4_app_route_blocker` | 1 | No current V4 route; must be counted as blocker. |
| `deferred_excluded_with_reason` | 1 | Excluded from V4.0 generic Tier-2 because it is app-identity shaped. |
| `partner_migration_or_parity` | 0 | No app is being promoted through partner migration in this goal. |
| `backend_bound_parity_control` | 0 | No app is being hidden as backend-bound parity in this goal. |
| `requires_cupy_promotion` | 0 | No app is blocked on a new CuPy promotion in this goal. |
| `requires_fixed_numba_continuation` | 0 | No app is blocked on a new fixed Numba promotion in this goal. |

## App Matrix

| App | Route class | V4 code used? | Full route? | Goal4653 action |
| --- | --- | ---: | ---: | --- |
| `rt_dbscan` | `v4_fused_operator_addressable` | yes | yes | Freeze with correctness parity and app-level timing. |
| `raydb_style` | `v4_fused_operator_addressable` | yes | yes | Freeze grouped-i64 / grouped-argmin / any-hit route. |
| `triangle_counting` | `v4_fused_operator_addressable` | yes | yes | Freeze weighted-sum + grouped-i64 route. |
| `librts_spatial_index` | `v4_fused_operator_addressable` | yes | yes | Freeze generic AABB all-ops count route with explicit denominator. |
| `hausdorff_xhd` | `requires_new_generic_operator` | yes | no | Freeze as partial V4 coverage unless a full route is built before protocol freeze. |
| `robot_collision` | `requires_new_generic_operator` | yes | no | Freeze as partial any-hit coverage with full-route blocker. |
| `contact_manifold` | `requires_new_generic_operator` | yes | no | Freeze as partial nearest-witness coverage with full-route blocker. |
| `rtnn` | `requires_new_generic_operator` | yes | no | Freeze as partial nearest-witness coverage with ranked-summary/top-k blocker. |
| `spatial_rayjoin` | `no_v4_app_route_blocker` | no | no | Freeze as no-route blocker; no silent V2/V3 fallback. |
| `barnes_hut` | `deferred_excluded_with_reason` | no | no | Freeze as deferred/excluded; no Barnes-Hut app-identity kernel. |

## Planner Dry-Run Lock

The test suite calls `validate_v4_goal4652_app_route_bindings()` through the V4
front door and verifies every declared planner dry-run. For every full route,
the expected planner status is `tier2_measured_ready`, and all release/broad
speedup/whole-app/CuPy/app-specific-kernel flags remain false.

This keeps Goal4652 from being a prose-only declaration.

## Claim Boundaries

Goal4652 explicitly keeps these false:

- `release_claim_authorized`
- `broad_v4_speedup_claim_authorized`
- `whole_app_speedup_claim_authorized`
- `cupy_performance_claim_authorized`
- `app_specific_native_kernel_authorized`
- silent V2/V3 fallback

## Goal-Level Decision Audit

1. Was I being stupid?
   - The earlier failure mode would have been to start Goal4653 protocol freeze
     without a route matrix. This goal avoids that.
2. If yes, what action made it stupid?
   - The stupid action would be treating operator coverage as whole-app
     readiness. This report separates full routes, partial routes, blockers, and
     deferred rows.
3. Is there another path that avoids getting stuck on a bad premise?
   - Yes: freeze the route truth first, then build the app-level protocol only
     from declared routes and blockers.
4. Can I now try the different path that actually solves the problem?
   - Yes: proceed to Goal4653 with this matrix as input, not with a broad V4
     assumption.

## Result

Goal4652 is locally complete. The project now has a test-backed route-binding
matrix for all ten benchmark apps. Goal4653 can freeze the full app-level
benchmark protocol without pretending that every app already has a V4 route.

## Non-Authorization

This goal does not authorize public V4 speed claims, full app-level performance
claims, POD all-app benchmark spend, CuPy blanket support, arbitrary Numba
callbacks, C ABI, embedding, true-zero-copy, non-Python host support, or
app-identity native kernels.
