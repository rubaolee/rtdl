# Goal2068 - Final v2.0 Release Matrix Candidate

Date: 2026-05-15

Status: `final-v2-0-release-matrix-candidate`

Goal2068 gives the v2.0 release lane a final-named matrix candidate after Goal2066's larger NVIDIA L4 pod evidence. It is a release-hardening artifact, not release authorization.

## Summary

- row count: `16`
- comparison status counts: `{"pod-evidence-collected": 11, "pod-evidence-collected-bounded": 4, "pod-evidence-collected-mixed": 1}`
- mixed apps: `["segment_polygon_anyhit_rows"]`
- bounded apps: `["database_analytics", "graph_analytics", "polygon_pair_overlap_area_rows", "polygon_set_jaccard"]`
- v2.0 release authorized: `False`
- all-app speedup claim authorized: `False`

## Post-Goal2066 Changes

- `robot_collision_screening` moves from mixed to positive at larger scale: `0.164x` at 32768x8192 and `0.084x` at 65536x8192.
- `road_hazard_screening` uses the larger prepared-only Goal2066 evidence: `0.085x` v2/v1.8 prepared.
- `segment_polygon_hitcount` uses the larger Goal2066 compact count-column evidence: `0.006x` prepared-reuse ratio.
- fixed-radius proxy rows use Goal2066's 16384x16384 evidence, all under `0.02x`.
- `segment_polygon_anyhit_rows` stays mixed: full witness-row materialization is `1.562x`, slower than v1.8 native rows.
- polygon overlap/Jaccard stay bounded: 2048/3072 evidence exists, but 4096 OptiX candidate discovery OOMs.

## App Rows

| App | Status | Claim class | Evidence | Boundary |
| --- | --- | --- | --- | --- |
| `database_analytics` | `pod-evidence-collected-bounded` | `bounded-implemented` | `docs/reports/goal2056_database_rawkernel_cupy_optix_l4_4096.json` | The RawKernel v2 row is fast and correct, but the next generalization is a reusable partner grouped-reduction adapter rather than app-local DB code. |
| `graph_analytics` | `pod-evidence-collected-bounded` | `bounded-closed-form` | `docs/reports/goal2058_graph_rawkernel_cupy_optix_l4_512.json` | The authored app is fast, but this remains the largest semantic debt: no reusable partner graph primitive for frontier traversal, triangle counting, or visibility-edge aggregation. |
| `service_coverage_gaps` | `pod-evidence-collected` | `implemented` | `docs/reports/goal1903_fixed_radius_batch_pod.json` | Positive rows are expected when prepared reuse and partner-owned threshold outputs amortize dispatch and transfer cost. |
| `event_hotspot_screening` | `pod-evidence-collected` | `implemented` | `docs/reports/goal1903_fixed_radius_batch_pod.json` | This row should track the fixed-radius primitive shape; small cases can still be setup-bound. |
| `facility_knn_assignment` | `pod-evidence-collected` | `implemented` | `docs/reports/goal2066_fixed_radius_family_cupy_l4_16384.json` | The honest row is coverage/threshold. Ranked KNN ordering is outside this adapter. Goal2066 strengthens this row at 16384x16384, still bounded to the documented threshold/proxy semantics. |
| `road_hazard_screening` | `pod-evidence-collected` | `implemented` | `docs/reports/goal2066_road_hazard_cupy_l4_12288_prepared_only.json` | Goal2066 shows the prepared reusable witness-output path is a clear speedup at 12288 roads; small rows remain setup-sensitive. |
| `segment_polygon_hitcount` | `pod-evidence-collected` | `implemented` | `docs/reports/goal2066_segment_polygon_hitcount_cupy_l4_131072_capacity67108864.json` | Goal2066 shows compact partner-owned count columns are the strongest segment/polygon v2 shape at 131072 rows. |
| `segment_polygon_anyhit_rows` | `pod-evidence-collected-mixed` | `implemented-needs-optimization` | `docs/reports/goal2066_segment_polygon_anyhit_cupy_l4_4096_capacity16777216.json` | Goal2066 confirms full witness-row materialization remains slower than v1.8 native rows at 4096; this row is correct but the wrong performance shape for large outputs. |
| `polygon_pair_overlap_area_rows` | `pod-evidence-collected-bounded` | `bounded-implemented` | `docs/reports/goal2066_polygon_rawkernel_cupy_optix_l4_2048.json; docs/reports/goal2066_polygon_rawkernel_cupy_optix_l4_3072.json; docs/reports/goal2066_polygon_rawkernel_cupy_optix_l4_4096_oom.log` | Still bounded: v2 preserves semantics at 2048/3072 but remains slower, and 4096 OOMs in current OptiX candidate discovery. |
| `polygon_set_jaccard` | `pod-evidence-collected-bounded` | `bounded-implemented` | `docs/reports/goal2066_polygon_rawkernel_cupy_optix_l4_2048.json; docs/reports/goal2066_polygon_rawkernel_cupy_optix_l4_3072.json; docs/reports/goal2066_polygon_rawkernel_cupy_optix_l4_4096_oom.log` | Still bounded: v2 is near parity/slightly faster at 2048/3072, but 4096 shares the same current OptiX candidate-discovery OOM boundary. |
| `hausdorff_distance` | `pod-evidence-collected` | `implemented` | `docs/reports/goal2066_fixed_radius_family_cupy_l4_16384.json` | This is a thresholded nearest-candidate workload. Exact directed Hausdorff max-distance remains a different app continuation. Goal2066 strengthens this row at 16384x16384, still bounded to the documented threshold/proxy semantics. |
| `ann_candidate_search` | `pod-evidence-collected` | `implemented` | `docs/reports/goal2066_fixed_radius_family_cupy_l4_16384.json` | The row tests candidate coverage, not arbitrary nearest-neighbor indexing. Goal2066 strengthens this row at 16384x16384, still bounded to the documented threshold/proxy semantics. |
| `outlier_detection` | `pod-evidence-collected` | `implemented` | `docs/reports/goal2066_fixed_radius_family_cupy_l4_16384.json` | The v2 output should be compact flags/counts; host materialized row lists would erase much of the point. Goal2066 strengthens this row at 16384x16384, still bounded to the documented threshold/proxy semantics. |
| `dbscan_clustering` | `pod-evidence-collected` | `implemented` | `docs/reports/goal2066_fixed_radius_family_cupy_l4_16384.json` | Only the RTDL neighbor/core test is accelerated; transitive cluster labeling is not yet a partner graph algorithm. Goal2066 strengthens this row at 16384x16384, still bounded to the documented threshold/proxy semantics. |
| `robot_collision_screening` | `pod-evidence-collected` | `implemented` | `docs/reports/goal2066_robot_collision_cupy_l4_32768x8192.json; docs/reports/goal2066_robot_collision_cupy_l4_65536x8192.json` | Goal2066 turns the earlier small-row negative into a large-scale speedup; the row remains an any-hit flag output, not arbitrary whole-app planning acceleration. |
| `barnes_hut_force_app` | `pod-evidence-collected` | `implemented` | `docs/reports/goal2066_fixed_radius_family_cupy_l4_16384.json` | This covers spatial node coverage, not a full Barnes-Hut force-vector GPU solver. Goal2066 strengthens this row at 16384x16384, still bounded to the documented threshold/proxy semantics. |

## Release Boundary

Allowed:

- use this as the final-named v2.0 matrix candidate for external review;
- cite compact count/flag/threshold outputs as the strongest v2.0 performance shape;
- cite robot collision and road hazard as large-scale positive after Goal2066;
- cite polygon overlap/Jaccard and graph/database control rows only with their boundaries.

Not allowed:

- v2.0 release readiness;
- all-app speedup;
- broad RT-core speedup;
- arbitrary partner-program acceleration;
- package-install readiness;
- full witness-row materialization solved;
- scalable arbitrary polygon overlay solved.

## Final Blockers

- final Claude v2.0 release review missing
- final Gemini v2.0 release review over post-Goal2066 packet missing
- final v2.0 release consensus missing
- explicit user-requested release action missing
