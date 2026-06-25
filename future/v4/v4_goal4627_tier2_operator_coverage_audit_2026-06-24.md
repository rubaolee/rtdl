# V4 Goal4627 Tier-2 Operator Coverage Audit

Date: 2026-06-24

Status: `goal4627_coverage_audit_not_release`

## Purpose

Goal4627 audits how the current V4 Tier-2 operator catalog maps to the promoted
benchmark/app set. It answers a narrower question than release readiness:

> Which benchmark continuations are already covered by measured generic V4
> operators, which are only candidates, and which remain deferred or uncovered?

This document does not authorize a V4 release or broad V4 speedup wording.

## Source Of Truth

Machine-checkable audit rows:

- `src/rtdsl/v4_coverage_audit.py`

Regression test:

- `tests/v4_goal4627_coverage_audit_test.py`

Supporting inventories and evidence:

- `future/v4/tier2_operator_catalog.md`
- `future/v4/v2_primitives_to_v4_tier2_inventory_2026-06-24.md`
- `future/v4/reviews/goal4626_completion_consensus_and_review_debt_2026-06-24.md`

## Summary

The audited set is the 10 promoted benchmark apps:

| Coverage class | Count | Meaning |
| --- | ---: | --- |
| `strong_measured_operator_coverage` | 1 | A non-fixed-radius generic V4 Tier-2 operator directly maps to the app's important continuation shape and has serious POD evidence. |
| `partial_measured_operator_coverage` | 5 | At least one measured V4 operator maps to a sub-contract, but the full app/release row is not covered. |
| `candidate_not_measured_release_coverage` | 1 | The relevant V4 operator exists only as a candidate and must not be treated as measured coverage. |
| `deferred_or_uncovered_v4_0` | 3 | No current V4 measured/candidate operator honestly covers the required generic continuation, or the route is app-identity/deferred. |

This is not an 80% coverage claim. It is a scoped audit over the currently
promoted benchmark set.

## Coverage Table

| Benchmark app | Coverage status | Mapped V4 operators | Release gap | Next action |
| --- | --- | --- | --- | --- |
| `hausdorff_xhd` | `partial_measured_operator_coverage` | `v4_point_group_nearest_witness_2d_device_arrays`; `v4_fixed_radius_count_threshold_2d_device_arrays` | Hausdorff app-level directed distance/threshold workflows are not yet a reviewed V4 release scorecard row. | Keep as partial coverage; do not use as the second release gate before a clearer same-contract operator target. |
| `spatial_rayjoin` | `deferred_or_uncovered_v4_0` | none | Spatial relation/topology and repeated PIP routes are not current V4 GPU-array Tier-2 surfaces. | Defer to a future generic relation/AABB operator audit; do not use as the second V4 gate. |
| `rt_dbscan` | `partial_measured_operator_coverage` | `v4_fixed_radius_count_threshold_2d_device_arrays` | DBSCAN needs 3D/self-query and component-union coverage beyond the measured 2D fixed-radius front door. | Keep fixed-radius as partial coverage; component-union remains a later generic operator target. |
| `robot_collision` | `partial_measured_operator_coverage` | `v4_ray_triangle_any_hit_flags_2d_device_arrays` | Collision app planning/setup and grouped segment lowering are not a full V4 release benchmark row. | Treat any-hit flags as partial generic coverage; do not claim whole-app collision acceleration. |
| `contact_manifold` | `partial_measured_operator_coverage` | `v4_point_group_nearest_witness_2d_device_arrays` | Bounded witness collection is adjacent to nearest-witness coverage but not a reviewed contact-manifold V4 gate. | Keep as partial nearest-witness coverage. |
| `raydb_style` | `strong_measured_operator_coverage` | `v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays`; `v4_closest_hit_grouped_argmin_3d_device_arrays`; `v4_ray_triangle_any_hit_flags_2d_device_arrays` | Needs Goal4628 scorecard reconciliation as the second non-fixed-radius same-contract gate. | Use grouped-i64 as the recommended Goal4628 second Tier-2 same-contract gate. |
| `barnes_hut` | `deferred_or_uncovered_v4_0` | none | Aggregate-tree weighted vector sum was rejected for V4.0 because it is Barnes-Hut/N-body specific rather than a generic RT-core operator. | Keep deferred; do not use Barnes-Hut as a V4.0 Tier-2 release gate. |
| `librts_spatial_index` | `deferred_or_uncovered_v4_0` | none | Generic AABB index query exists in earlier runtime code but is not a current V4 measured GPU-array Tier-2 surface. | Defer to a later AABB/relation operator promotion audit. |
| `rtnn` | `partial_measured_operator_coverage` | `v4_point_group_nearest_witness_2d_device_arrays` | RTNN ranked fixed-radius/top-k 3D summaries are not current V4 measured surfaces. | Keep nearest-witness as partial coverage; ranked/top-k remains deferred. |
| `triangle_counting` | `candidate_not_measured_release_coverage` | `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays`; `v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays` | The measured grouped-i64 operator covers an adjacent grouped-reduction dimension, but not triangle counting's dominant any-hit weighted/count continuation path. That primary route is the weighted-sum candidate and needs Goal4629 promotion/rejection review. | Do not use as Goal4628 while weighted-sum is still candidate; resolve in Goal4629. |

## Goal4628 Recommendation

Recommended Goal4628 target:

- app anchor: `raydb_style`
- V4 operator:
  `v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays`
- generic primitive:
  `RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D`
- continuation class:
  `grouped_i64_reduction`

Why this is the right second gate:

1. It is not fixed-radius.
2. It is generic: grouped count/sum/min/max/sum-count over ray/triangle
   primitive groups, not an app-identity kernel.
3. It already has serious RTX A5000 POD evidence against the older
   host-output primitive:
   - 32,768 rays: 7.933x same-contract ratio
   - 131,072 rays: 22.856x same-contract ratio
4. It also has multi-width evidence and external promotion review from
   `goal4617`.
5. It keeps weighted-sum candidate work out of Goal4628 so `goal4629` can decide
   that candidate explicitly.

Goal4628 should therefore be a scorecard reconciliation and acceptance gate over
the existing grouped-i64 evidence, with a fresh POD rerun only if review finds a
same-contract or product-boundary gap.

## Required Prerequisite Before Goal4628

Goal4626 carries the fixed-radius amendment-closure constraint:

`external_review_then_productize_fixed_radius_api_wrapper_before_second_primitive`

Goal4628 must not proceed until this prerequisite is explicitly checked. The
current repo appears to contain the fixed-radius wrapper, docs, example, tests,
and Claude wrapper review, but Goal4628 must state that check in its own packet
before accepting grouped-i64 as the second gate.

## Non-Authorization

Goal4627 does not authorize:

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
