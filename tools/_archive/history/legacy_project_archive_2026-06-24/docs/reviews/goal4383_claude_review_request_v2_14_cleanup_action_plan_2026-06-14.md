# Claude Review Request: Goal4383 v2.14 Benchmark Cleanup Results

Date: 2026-06-14

This is a post-implementation review request. The original plan was to learn from the RTNN failure mode and audit every benchmark app with three questions:

1. Is the RT-core side optimized enough for the stated primitive/app contract?
2. Is the Embree CPU side optimized enough for a fair same-contract comparison?
3. Is the data large or paper/application faithful, not just a tiny fixture repeated many times?

Codex has now implemented the highest-priority cleanup items and rerun the relevant local and pod gates. Please review whether the resulting evidence is strong enough for v2.14 internal publication wording, and where the public claims still need narrowing.

## Files To Review

- `docs/reports/goal4382_v2_14_benchmark_app_cross_audit_2026-06-14.md`
- `docs/reports/goal4383_v2_14_cleanup_action_plan_2026-06-14.md`
- `docs/reports/goal4383_rt_dbscan_embree_compact_threshold_2026-06-14.md`
- `docs/reports/goal4383_librts_large_aabb_2026-06-14.md`
- `docs/reports/goal4383_triangle_large_rt_graph_2026-06-14.md`
- `docs/reports/goal4383_barnes_hut_fixed_depth_node_coverage_2026-06-14.md`
- `docs/reports/goal4383_hausdorff_large_threshold_2026-06-14.md`
- `docs/reports/goal4383_robot_collision_large_prepared_buffers_2026-06-14.md`
- `docs/reports/goal4383_contact_jittered_aabb_2026-06-14.md`
- `docs/reports/goal4381_rtnn_aggregate_large_2026-06-14.md`
- `docs/release_reports/v2_14/public_rt_vs_embree_comparison.md`
- `docs/release_reports/v2_14/benchmark_app_phase_explanations.md`

## Key Completed Work

- RTDBSCAN: added a generic Embree prepared 3D fixed-radius count-threshold route so the CPU side no longer materializes neighbor rows or rebuilds through the stale row path. Large runs now go to 524,288 synthetic points. The full-app speedup remains small because the shared Numba continuation dominates.
- LibRTS AABB: aligned Embree fp32 envelope semantics with OptiX/authors-code-style counts and reran 100K and 1M box rows. Hot AABB query speedup remains strong.
- Triangle counting: added large RT-Graph-shaped synthetic fixture rows up to 1,048,576 rays and 2,621,440 triangles.
- Barnes-Hut: added fixed-depth quadtree-cell node fixtures and reran up to 1,000,000 bodies x 65,536 nodes. The claim remains node-coverage traversal only.
- Hausdorff: reran prepared threshold-decision rows up to 1,048,576 points per side. The claim remains `Hausdorff <= r` decision only, not exact witness-distance.
- Robot collision: reran prepared-buffer same-contract grouped-segment any-hit rows up to 1,048,576 groups and 9,437,184 query segments.
- Contact manifold: added `jittered_grid_65536`, giving 4,294,967,296 possible pairs and 65,536 validated witness rows. The claim remains AABB broadphase/contact-witness rows only, not full contact-manifold physics.

## Latest Gate Results

Local Windows:

`py -3 -m unittest tests.goal4383_contact_jittered_aabb_test tests.goal4382_v2_14_benchmark_app_cross_audit_test tests.goal4347_rt_dbscan_embree_numba_fair_mode_test tests.goal4383_librts_aabb_fp32_contract_test tests.goal4383_triangle_large_rt_graph_report_test tests.goal4383_barnes_hut_fixed_depth_node_coverage_test tests.goal4383_hausdorff_large_threshold_report_test tests.goal4383_robot_collision_large_prepared_buffers_test tests.goal504_barnes_hut_force_app_test tests.goal2563_barnes_hut_app_adapter_boundary_test`

Result: 29 tests OK.

Pod Linux:

`python3 -m unittest tests.goal4383_contact_jittered_aabb_test tests.goal4382_v2_14_benchmark_app_cross_audit_test tests.goal4347_rt_dbscan_embree_numba_fair_mode_test tests.goal4383_librts_aabb_fp32_contract_test tests.goal4383_triangle_large_rt_graph_report_test tests.goal4383_barnes_hut_fixed_depth_node_coverage_test tests.goal4383_hausdorff_large_threshold_report_test tests.goal4383_robot_collision_large_prepared_buffers_test tests.goal504_barnes_hut_force_app_test tests.goal2563_barnes_hut_app_adapter_boundary_test`

Result: 29 tests OK.

## Review Questions

1. Does the cross-audit matrix now correctly separate optimized prepared-primitive evidence from full benchmark-app or paper-reproduction claims?
2. Are any rows still unfair to Embree because the CPU side has avoidable materialization, stale primitives, or missing thread policy?
3. Are any rows still unfair to OptiX because the RT-core side is not using the best available prepared/device-resident route for the stated contract?
4. Is the data-readiness classification honest, especially for synthetic large rows such as triangle counting, Barnes-Hut, contact, and Hausdorff threshold?
5. Should v2.14 remain internal-only for any row currently marked GREEN/GREEN/YELLOW?
6. Are the remaining v3.0 debts correctly named: fused RayJoin overlay/PIP, RTDBSCAN device-side continuation, exact/paper datasets, and app-level force/physics loops?

## Requested Verdict

Please answer with one of:

- Approve.
- Approve with required changes.
- Block.

If blocking or requiring changes, list the minimum changes needed before v2.14 closeout wording is accepted.
