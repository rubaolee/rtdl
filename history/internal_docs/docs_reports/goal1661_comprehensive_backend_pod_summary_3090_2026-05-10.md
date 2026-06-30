# Goal1661 Comprehensive Pod Backend Comparison

## Verdict

`measured_evidence_only_no_release_claim`

This artifact compares the current v1.6.11 candidate against v1.0 where commands are runnable, and compares Embree single-thread, Embree auto-thread, and OptiX within each version where accepted rows exist.

## Environment

- Generated at: `2026-05-10T11:00:31Z`
- Host: `9e31a1d29724`
- Platform: `Linux-6.8.0-110-generic-x86_64-with-glibc2.35`
- Current ref: `main`
- Baseline ref: `v1.0`
- Current commit: `9b54159fb07cdcdc0d99ac89aff3484a0bbf61b2`
- Baseline commit: `b9c9620af78a2fab92083d43af312bb6310e452a`

## Counts

- OK rows: `58`
- Failed rows: `0`
- Unsupported rows: `37`

## Cross-Version Timing

| App | Mode | v1.0 sec | v1.6.11 sec | Speedup |
| --- | --- | ---: | ---: | ---: |
| `ann_candidate_search` | `optix` | 1.943 | 2.233 | 0.870 |
| `barnes_hut_force_app` | `optix` | 4.731 | 4.818 | 0.982 |
| `database_analytics` | `embree_1t` | 2.599 | 2.712 | 0.958 |
| `database_analytics` | `embree_auto` | 2.430 | 2.713 | 0.896 |
| `database_analytics` | `optix` | 3.441 | 3.664 | 0.939 |
| `event_hotspot_screening` | `optix` | 1.952 | 2.024 | 0.965 |
| `facility_knn_assignment` | `optix` | 2.135 | 2.018 | 1.058 |
| `graph_analytics` | `optix` | 8.097 | 7.643 | 1.059 |
| `hausdorff_distance` | `optix` | 2.042 | 2.161 | 0.945 |
| `outlier_detection` | `optix` | 3.518 | 3.366 | 1.045 |
| `polygon_pair_overlap_area_rows` | `optix` | 5.246 | 5.656 | 0.927 |
| `polygon_set_jaccard` | `optix` | 6.287 | 6.760 | 0.930 |
| `road_hazard_screening` | `optix` | 3.602 | 4.098 | 0.879 |
| `robot_collision_screening` | `optix` | 1.550 | 1.857 | 0.835 |
| `segment_polygon_anyhit_rows` | `optix` | 1.796 | 2.229 | 0.806 |
| `segment_polygon_hitcount` | `optix` | 1.478 | 2.097 | 0.705 |
| `service_coverage_gaps` | `optix` | 1.847 | 2.144 | 0.862 |

## Backend Timing

| App | Version | Embree mode | Embree sec | OptiX sec | OptiX/Embree speedup |
| --- | --- | --- | ---: | ---: | ---: |
| `ann_candidate_search` | `v1_6_11` | `embree_1t` | 3.553 | 2.233 | 1.591 |
| `ann_candidate_search` | `v1_6_11` | `embree_auto` | 4.297 | 2.233 | 1.924 |
| `barnes_hut_force_app` | `v1_6_11` | `embree_1t` | 9.328 | 4.818 | 1.936 |
| `barnes_hut_force_app` | `v1_6_11` | `embree_auto` | 9.574 | 4.818 | 1.987 |
| `database_analytics` | `v1_0` | `embree_1t` | 2.599 | 3.441 | 0.755 |
| `database_analytics` | `v1_0` | `embree_auto` | 2.430 | 3.441 | 0.706 |
| `database_analytics` | `v1_6_11` | `embree_1t` | 2.712 | 3.664 | 0.740 |
| `database_analytics` | `v1_6_11` | `embree_auto` | 2.713 | 3.664 | 0.740 |
| `event_hotspot_screening` | `v1_6_11` | `embree_1t` | 1.446 | 2.024 | 0.715 |
| `event_hotspot_screening` | `v1_6_11` | `embree_auto` | 1.548 | 2.024 | 0.765 |
| `facility_knn_assignment` | `v1_6_11` | `embree_1t` | 4.376 | 2.018 | 2.168 |
| `facility_knn_assignment` | `v1_6_11` | `embree_auto` | 3.675 | 2.018 | 1.821 |
| `hausdorff_distance` | `v1_6_11` | `embree_1t` | 6.828 | 2.161 | 3.160 |
| `hausdorff_distance` | `v1_6_11` | `embree_auto` | 7.266 | 2.161 | 3.362 |
| `polygon_pair_overlap_area_rows` | `v1_6_11` | `embree_1t` | 59.297 | 5.656 | 10.483 |
| `polygon_pair_overlap_area_rows` | `v1_6_11` | `embree_auto` | 10.708 | 5.656 | 1.893 |
| `polygon_set_jaccard` | `v1_6_11` | `embree_1t` | 378.002 | 6.760 | 55.915 |
| `polygon_set_jaccard` | `v1_6_11` | `embree_auto` | 399.070 | 6.760 | 59.031 |
| `road_hazard_screening` | `v1_6_11` | `embree_1t` | 2.819 | 4.098 | 0.688 |
| `road_hazard_screening` | `v1_6_11` | `embree_auto` | 3.113 | 4.098 | 0.760 |
| `robot_collision_screening` | `v1_6_11` | `embree_1t` | 9.074 | 1.857 | 4.887 |
| `robot_collision_screening` | `v1_6_11` | `embree_auto` | 9.068 | 1.857 | 4.883 |
| `segment_polygon_anyhit_rows` | `v1_6_11` | `embree_1t` | 0.771 | 2.229 | 0.346 |
| `segment_polygon_anyhit_rows` | `v1_6_11` | `embree_auto` | 0.937 | 2.229 | 0.420 |
| `segment_polygon_hitcount` | `v1_6_11` | `embree_1t` | 0.736 | 2.097 | 0.351 |
| `segment_polygon_hitcount` | `v1_6_11` | `embree_auto` | 0.829 | 2.097 | 0.396 |
| `service_coverage_gaps` | `v1_6_11` | `embree_1t` | 1.158 | 2.144 | 0.540 |
| `service_coverage_gaps` | `v1_6_11` | `embree_auto` | 1.533 | 2.144 | 0.715 |

## Failing

No failed executed rows.

## Boundary

This report is measured evidence only. It does not publish v1.6.11, authorize a tag, or authorize public speedup wording. Unsupported rows remain unsupported rather than being counted as wins or losses.
