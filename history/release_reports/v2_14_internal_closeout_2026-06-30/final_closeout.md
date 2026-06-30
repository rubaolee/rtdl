# RTDL v2.14 Final Closeout

Status: release closeout complete for transition to V3.0 M1 design, with the
Goal4389 RTDBSCAN partner-dual supplement and Goal4390 app-author strategy
included.

Date: 2026-06-15

## Verdict

v2.14 is closed as the final V2.X cleanup/evidence packet. It freezes the promoted benchmark-app inventory, finalizes the same-contract OptiX-vs-Embree matrix, locks public wording boundaries, and records which rows are public-review-ready versus blocked from broader claims.

Goal4389 adds one post-closeout evidence supplement: RTDBSCAN now has a
same-contract CuPy-vs-Numba partner comparison for the current prepared-grid
component-continuation contract. That supplement does not start V3.0 and does
not broaden the backend speedup claim.

Goal4390 adds the v2.14 app-author implementation strategy: users should start
with RTDL primitives, add explicit partner continuation only when needed, keep
OptiX-vs-Embree comparisons same-contract, and treat raw OptiX callbacks as
native implementation details behind generic primitives rather than as the
v2.14 user API. Claude reviewed the strategy as `accept-with-boundary`, and
the required fixes are applied.

This closeout moves the source-tree version marker to v2.14 and supports the
v2.14 tag. It does not authorize broad public claims or start V3.0
implementation.

## Completed 1-7

| Step | Status | Output |
| ---: | --- | --- |
| 1 | done | `promoted_benchmark_inventory.md` freezes included rows and blocked broader claims. |
| 2 | done | `public_rt_vs_embree_comparison.md` records the final same-contract matrix; Goal4389 records the RTDBSCAN partner-dual supplement; Goal4390 records app-author implementation guidance. |
| 3 | done | `public_wording_boundaries.md` locks allowed and blocked wording. |
| 4 | done | Final local focused gates passed. |
| 5 | done | Final pod focused gates passed. |
| 6 | done | This closeout report records public-ready rows and blocked/deferred broader claims. |
| 7 | done-with-boundary | V3.0 may enter M1 design only; implementation remains blocked until the M1 IR design document is frozen. |

## Public-Review-Ready Rows

| Row | Public stance |
| --- | --- |
| RTNN | Large RTNN-shaped prepared aggregate row; no paper-dataset claim. |
| RTDBSCAN | Fair same-continuation engineering row; total speedup is small because Numba continuation dominates. Goal4389 also shows Numba is the current best measured partner for the prepared-grid contract. |
| RayJoin LSI | Prepared scalar-count row; not full paper reproduction. |
| RayJoin PIP | Modest prepared scalar-count row; CDB closest-hit face-id route deferred. |
| RayJoin overlay Section 5.7 | Available 2/8 exact CDB subset is public-review-ready; no full 8/8 Section 5.7 reproduction wording. |
| RayDB-style | Generated RayDB-style grouped reduction row. |
| LibRTS AABB | Prepared hot-query AABB row; cold total reported separately. |
| Triangle counting | Large synthetic RT-Graph-shaped prepared primitive row. |
| Barnes-Hut | Node-coverage traversal only. |
| Hausdorff | Threshold decision only. |
| Robot collision | Discrete sampled grouped-segment any-hit flags only. |
| Contact manifold | AABB broadphase/contact-witness primitive only. |

## Blocked Broader Claims

| Claim | Reason |
| --- | --- |
| Full RayJoin overlay Section 5.7 8/8 matrix | Only the 2/8 available exact CDB subset is present in the current public/pod artifact set. |
| Any author-hot-compute parity statement | Requires V3.0-class fused/device-resident phase accounting. |
| Any full app/paper reproduction row not listed as ready | Exact data, author timing basis, or phase evidence is missing. |

## Final Verification

Local Windows focused gate:

`py -3 -m unittest tests.goal4390_v2_14_app_author_strategy_test tests.goal4389_rtdbscan_partner_dual_implementation_test tests.goal4388_partner_dual_implementation_policy_test tests.goal4386_v2_14_final_closeout_test tests.goal4384_v3_0_preflight_consensus_gate_test tests.goal4383_contact_jittered_aabb_test tests.goal4382_v2_14_benchmark_app_cross_audit_test tests.goal4347_rt_dbscan_embree_numba_fair_mode_test tests.goal4383_librts_aabb_fp32_contract_test tests.goal4383_triangle_large_rt_graph_report_test tests.goal4383_barnes_hut_fixed_depth_node_coverage_test tests.goal4383_hausdorff_large_threshold_report_test tests.goal4383_robot_collision_large_prepared_buffers_test tests.goal504_barnes_hut_force_app_test tests.goal2563_barnes_hut_app_adapter_boundary_test tests.goal4379_v2_14_benchmark_cleanup_gates_test`

Result: 59 tests OK.

Pod Linux focused gate:

`python3 -m unittest tests.goal4390_v2_14_app_author_strategy_test tests.goal4389_rtdbscan_partner_dual_implementation_test tests.goal4388_partner_dual_implementation_policy_test tests.goal4386_v2_14_final_closeout_test tests.goal4384_v3_0_preflight_consensus_gate_test tests.goal4383_contact_jittered_aabb_test tests.goal4382_v2_14_benchmark_app_cross_audit_test tests.goal4347_rt_dbscan_embree_numba_fair_mode_test tests.goal4383_librts_aabb_fp32_contract_test tests.goal4383_triangle_large_rt_graph_report_test tests.goal4383_barnes_hut_fixed_depth_node_coverage_test tests.goal4383_hausdorff_large_threshold_report_test tests.goal4383_robot_collision_large_prepared_buffers_test tests.goal504_barnes_hut_force_app_test tests.goal2563_barnes_hut_app_adapter_boundary_test tests.goal4379_v2_14_benchmark_cleanup_gates_test`

Result: 59 tests OK.

## Transition Rule

V3.0 M1 design may begin after this closeout. V3.0 implementation remains blocked until:

- the M1 execution-graph IR design document is frozen;
- no app-specific public Python API names are introduced;
- partner-dependent benchmark claims include both the current best-performance partner and a same-contract Numba reference;
- no V3.0 public performance claim is made before M5 and fresh external review.
