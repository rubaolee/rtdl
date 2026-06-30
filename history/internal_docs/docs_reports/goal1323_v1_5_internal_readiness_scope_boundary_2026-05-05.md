# Goal1323: v1.5 Internal Readiness Scope Boundary

Date: 2026-05-05

## Decision

The current v1.5 generic migration inventory is internally ready at the
subpath-primitive level. Every row in
`v1_5_generic_migration_inventory()` has status `pod_verified_generic`.

This does not mean every application is fully generic end-to-end. Several rows
intentionally retain app-level work outside the verified primitive subpath
boundary.

## Verified Generic Subpaths

- `graph_analytics / visibility_edges_reusable_batches`
- `service_coverage_gaps / gap_summary_prepared`
- `event_hotspot_screening / count_summary_prepared`
- `ann_candidate_search / candidate_threshold_prepared`
- `facility_knn_assignment / coverage_threshold_prepared`
- `outlier_detection / density_count`
- `dbscan_clustering / core_count`
- `barnes_hut_force_app / node_coverage_prepared`
- `hausdorff_distance / directed_threshold_prepared`
- `robot_collision_screening / prepared_count`
- `robot_collision_screening / prepared_pose_flags`
- `database_analytics / sales_risk_compact_summary`
- `polygon_pair_overlap_area_rows / candidate_discovery_and_exact_area`
- `polygon_set_jaccard / chunked_candidate_scoring`

## Remaining App-Level Work Outside v1.5 Primitive Scope

These items remain explicit, but they are outside the verified subpath claim:

- ANN indexing and nearest-neighbor ranking.
- Facility ranked KNN assignment.
- Outlier neighbor row materialization and broad outlier analytics.
- DBSCAN cluster expansion and connected components.
- Barnes-Hut opening rule and force-vector reduction.
- Hausdorff exact-distance rows.
- Older robot-collision prepared-count follow-on work, superseded for the
  verified `prepared_pose_flags` subpath.

## Pod Evidence

After Goal1322, the pod synced from GitHub `origin/main` at commit `b9c57bd`
and ran the focused v1.5/Jaccard status regression:

```text
RTDL_OPTIX_LIB=/workspace/rtdl_goal1292/build/librtdl_optix.so PYTHONPATH=src:. python3 -m unittest \
  tests.goal1304_v1_5_generic_migration_inventory_test \
  tests.goal1308_v1_5_polygon_float_sum_contract_test \
  tests.goal1310_v1_5_jaccard_collect_k_bounded_contract_test \
  tests.goal1312_v1_5_jaccard_optix_slower_reason_test \
  tests.goal1321_v1_5_native_polygon_pair_area_summary_abi_test \
  tests.goal1320_v1_5_jaccard_generic_score_reduction_test \
  tests.goal1318_v1_5_jaccard_native_collection_routing_test
```

Result:

```text
Ran 25 tests in 0.112s
OK
```

## Boundary

This is not public release authorization and not public NVIDIA speedup wording.
Before public v1.5 release text, keep the wording exact:

- v1.5 verifies generic traversal/reduction subpaths, not full app rewrite.
- Active backends before v2.1 are Embree and OptiX.
- Vulkan, HIPRT, and Apple RT remain frozen before v2.1.
- OptiX Jaccard remains slower than Embree even though its primitive subpath is
  internally generic and pod-verified.
- Public speedup wording still requires a separate reviewed wording packet.
