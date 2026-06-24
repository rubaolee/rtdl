# Goal2068 - Final v2.0 Release Matrix Candidate

Date: 2026-05-15

Status: `final-v2-0-release-matrix-candidate`

Goal2068 gives the v2.0 release lane a final-named matrix candidate after Goal2066's larger NVIDIA L4 pod evidence. It is a release-hardening artifact, not release authorization.

This current matrix also incorporates the post-streaming witness-column update from Goal2085/Goal2088, which supersedes the older full Python witness-row materialization result.

## Summary

- row count: `16`
- comparison status counts: `{"pod-evidence-collected": 12, "pod-evidence-collected-bounded": 4}`
- mixed apps: `[]`
- bounded apps: `["database_analytics", "graph_analytics", "polygon_pair_overlap_area_rows", "polygon_set_jaccard"]`
- v2.0 release authorized: `False`
- all current OptiX/RT rows have measured v2 ratios below 1.0: `True`
- whole-app speedup claim authorized: `False`

## Post-Goal2066 / Post-Goal2085 Changes

- `robot_collision_screening` moves from mixed to positive at larger scale: `0.164x` at 32768x8192 and `0.084x` at 65536x8192.
- `road_hazard_screening` uses the larger prepared-only Goal2066 evidence: `0.085x` v2/v1.8 prepared.
- `segment_polygon_hitcount` uses the larger Goal2066 compact count-column evidence: `0.006x` prepared-reuse ratio.
- fixed-radius proxy rows use Goal2066's 16384x16384 evidence, all under `0.02x`.
- `segment_polygon_anyhit_rows` now uses streaming exact witness columns instead of the old full Python row-table contract.
- polygon overlap/Jaccard use the current generic tiled AABB candidate-summary path, while arbitrary polygon overlay remains outside the claim.

## App Rows

| App | Status | Claim class | Evidence | Boundary |
| --- | --- | --- | --- | --- |
| `database_analytics` | `pod-evidence-collected-bounded` | `bounded-implemented` | `docs/reports/goal2079_current_commit_optix_rt_perf_refresh_pod/goal1955_database_cupy_default.json` | current-commit pod refresh; user-approved Python+CuPy+RTDL vs Python+RTDL app-wall comparison, not absolutely fair |
| `graph_analytics` | `pod-evidence-collected-bounded` | `bounded-implemented` | `docs/reports/goal2058_graph_rawkernel_cupy_optix_l4_512.json` | app-wall Python+RTDL vs Python+CuPy+RTDL; not absolutely fair, but user-approved v2 app comparison |
| `service_coverage_gaps` | `pod-evidence-collected` | `implemented` | `docs/reports/goal1903_fixed_radius_batch_pod.json` | prepared fixed-radius count/threshold output; compact partner-owned columns |
| `event_hotspot_screening` | `pod-evidence-collected` | `implemented` | `docs/reports/goal1903_fixed_radius_batch_pod.json` | prepared fixed-radius count/threshold output; compact partner-owned columns |
| `facility_knn_assignment` | `pod-evidence-collected` | `implemented` | `docs/reports/goal2079_current_commit_optix_rt_perf_refresh_pod/goal1925_fixed_radius_cupy_16384x8192.json` | current-commit pod refresh; prepared fixed-radius count/threshold output; richer semantics remain bounded where documented |
| `road_hazard_screening` | `pod-evidence-collected` | `implemented` | `docs/reports/goal2066_road_hazard_cupy_l4_12288_prepared_only.json` | prepared reusable witness output plus partner priority flags |
| `segment_polygon_hitcount` | `pod-evidence-collected` | `implemented` | `docs/reports/goal2066_segment_polygon_hitcount_cupy_l4_131072_capacity67108864.json` | compact partner-owned count columns; strongest segment/polygon v2 shape |
| `segment_polygon_anyhit_rows` | `pod-evidence-collected` | `implemented` | `docs/reports/goal2081_streaming_witness_page_pod/goal2081_streaming_witness_page_perf_pod_16384_cupy_capacity.json` | Streaming exact witness columns supersede the old slower full Python row-table contract; the old full-row path remains documented separately and is not the v2.0 release contract. |
| `polygon_pair_overlap_area_rows` | `pod-evidence-collected-bounded` | `bounded-implemented` | `docs/reports/goal2079_current_commit_optix_rt_perf_refresh_pod/goal1955_polygon_pair_cupy_extent_4096.json` | current-commit pod refresh using Goal2075 generic tiled AABB candidate-summary source; legacy OptiX candidate path at copies=3072 measured ratio=1.990x and remains slower |
| `polygon_set_jaccard` | `pod-evidence-collected-bounded` | `bounded-implemented` | `docs/reports/goal2079_current_commit_optix_rt_perf_refresh_pod/goal1955_polygon_jaccard_cupy_extent_4096.json` | current-commit pod refresh using Goal2075 generic tiled AABB candidate-summary source; legacy OptiX candidate path at copies=3072 measured ratio=1.263x and remains slower |
| `hausdorff_distance` | `pod-evidence-collected` | `implemented` | `docs/reports/goal2079_current_commit_optix_rt_perf_refresh_pod/goal1925_fixed_radius_cupy_16384x8192.json` | current-commit pod refresh; prepared fixed-radius count/threshold output; richer semantics remain bounded where documented |
| `ann_candidate_search` | `pod-evidence-collected` | `implemented` | `docs/reports/goal2079_current_commit_optix_rt_perf_refresh_pod/goal1925_fixed_radius_cupy_16384x8192.json` | current-commit pod refresh; prepared fixed-radius count/threshold output; richer semantics remain bounded where documented |
| `outlier_detection` | `pod-evidence-collected` | `implemented` | `docs/reports/goal2079_current_commit_optix_rt_perf_refresh_pod/goal1925_fixed_radius_cupy_16384x8192.json` | current-commit pod refresh; prepared fixed-radius count/threshold output; richer semantics remain bounded where documented |
| `dbscan_clustering` | `pod-evidence-collected` | `implemented` | `docs/reports/goal2079_current_commit_optix_rt_perf_refresh_pod/goal1925_fixed_radius_cupy_16384x8192.json` | current-commit pod refresh; prepared fixed-radius count/threshold output; richer semantics remain bounded where documented |
| `robot_collision_screening` | `pod-evidence-collected` | `implemented` | `docs/reports/goal2079_current_commit_optix_rt_perf_refresh_pod/goal1928_robot_collision_cupy_16384x1024.json` | current-commit pod refresh; prepared generic any-hit flags to partner-owned pose flags |
| `barnes_hut_force_app` | `pod-evidence-collected` | `implemented` | `docs/reports/goal2079_current_commit_optix_rt_perf_refresh_pod/goal1925_fixed_radius_cupy_16384x8192.json` | current-commit pod refresh; prepared fixed-radius count/threshold output; richer semantics remain bounded where documented |

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
- final Gemini v2.0 release review over current post-streaming packet missing
- final v2.0 release consensus missing
- explicit user-requested release action missing
