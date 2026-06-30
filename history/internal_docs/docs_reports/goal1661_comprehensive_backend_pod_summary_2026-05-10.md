# Goal1661 Comprehensive Pod Backend Comparison

## Verdict

`measured_evidence_only_no_release_claim`

This artifact compares the current v1.6.11 candidate against v1.0 where commands are runnable, and compares Embree single-thread, Embree auto-thread, and OptiX within each version where accepted rows exist.

## Environment

- Generated at: `2026-05-10T10:19:41Z`
- Host: `fbe4b81f5bba`
- Platform: `Linux-6.8.0-60-generic-x86_64-with-glibc2.35`
- Current ref: `main`
- Baseline ref: `v1.0`
- Current commit: `e9f3cbb73180b40e87e212bdfe09ebfee0ce085f`
- Baseline commit: `b9c9620af78a2fab92083d43af312bb6310e452a`

## Counts

- OK rows: `58`
- Failed rows: `0`
- Unsupported rows: `37`

## Cross-Version Timing

| App | Mode | v1.0 sec | v1.6.11 sec | Speedup |
| --- | --- | ---: | ---: | ---: |
| `ann_candidate_search` | `optix` | 1.568 | 1.808 | 0.867 |
| `barnes_hut_force_app` | `optix` | 3.506 | 3.645 | 0.962 |
| `database_analytics` | `embree_1t` | 2.174 | 2.044 | 1.064 |
| `database_analytics` | `embree_auto` | 2.037 | 2.288 | 0.890 |
| `database_analytics` | `optix` | 2.516 | 2.689 | 0.935 |
| `event_hotspot_screening` | `optix` | 1.779 | 1.670 | 1.065 |
| `facility_knn_assignment` | `optix` | 1.790 | 1.682 | 1.064 |
| `graph_analytics` | `optix` | 6.409 | 6.316 | 1.015 |
| `hausdorff_distance` | `optix` | 1.590 | 1.681 | 0.946 |
| `outlier_detection` | `optix` | 2.868 | 2.722 | 1.054 |
| `polygon_pair_overlap_area_rows` | `optix` | 3.887 | 3.786 | 1.027 |
| `polygon_set_jaccard` | `optix` | 5.433 | 5.178 | 1.049 |
| `road_hazard_screening` | `optix` | 3.170 | 3.206 | 0.989 |
| `robot_collision_screening` | `optix` | 1.240 | 1.385 | 0.895 |
| `segment_polygon_anyhit_rows` | `optix` | 1.272 | 1.484 | 0.857 |
| `segment_polygon_hitcount` | `optix` | 1.289 | 1.425 | 0.905 |
| `service_coverage_gaps` | `optix` | 1.383 | 1.586 | 0.872 |

## Backend Timing

| App | Version | Embree mode | Embree sec | OptiX sec | OptiX/Embree speedup |
| --- | --- | --- | ---: | ---: | ---: |
| `ann_candidate_search` | `v1_6_11` | `embree_1t` | 2.556 | 1.808 | 1.413 |
| `ann_candidate_search` | `v1_6_11` | `embree_auto` | 3.041 | 1.808 | 1.681 |
| `barnes_hut_force_app` | `v1_6_11` | `embree_1t` | 8.208 | 3.645 | 2.252 |
| `barnes_hut_force_app` | `v1_6_11` | `embree_auto` | 7.999 | 3.645 | 2.195 |
| `database_analytics` | `v1_0` | `embree_1t` | 2.174 | 2.516 | 0.864 |
| `database_analytics` | `v1_0` | `embree_auto` | 2.037 | 2.516 | 0.810 |
| `database_analytics` | `v1_6_11` | `embree_1t` | 2.044 | 2.689 | 0.760 |
| `database_analytics` | `v1_6_11` | `embree_auto` | 2.288 | 2.689 | 0.851 |
| `event_hotspot_screening` | `v1_6_11` | `embree_1t` | 1.187 | 1.670 | 0.711 |
| `event_hotspot_screening` | `v1_6_11` | `embree_auto` | 1.034 | 1.670 | 0.619 |
| `facility_knn_assignment` | `v1_6_11` | `embree_1t` | 2.972 | 1.682 | 1.767 |
| `facility_knn_assignment` | `v1_6_11` | `embree_auto` | 3.085 | 1.682 | 1.834 |
| `hausdorff_distance` | `v1_6_11` | `embree_1t` | 5.015 | 1.681 | 2.983 |
| `hausdorff_distance` | `v1_6_11` | `embree_auto` | 5.362 | 1.681 | 3.189 |
| `polygon_pair_overlap_area_rows` | `v1_6_11` | `embree_1t` | 48.598 | 3.786 | 12.835 |
| `polygon_pair_overlap_area_rows` | `v1_6_11` | `embree_auto` | 12.996 | 3.786 | 3.432 |
| `polygon_set_jaccard` | `v1_6_11` | `embree_1t` | 317.772 | 5.178 | 61.374 |
| `polygon_set_jaccard` | `v1_6_11` | `embree_auto` | 318.889 | 5.178 | 61.590 |
| `road_hazard_screening` | `v1_6_11` | `embree_1t` | 2.208 | 3.206 | 0.689 |
| `road_hazard_screening` | `v1_6_11` | `embree_auto` | 2.326 | 3.206 | 0.725 |
| `robot_collision_screening` | `v1_6_11` | `embree_1t` | 8.026 | 1.385 | 5.795 |
| `robot_collision_screening` | `v1_6_11` | `embree_auto` | 8.190 | 1.385 | 5.913 |
| `segment_polygon_anyhit_rows` | `v1_6_11` | `embree_1t` | 0.633 | 1.484 | 0.426 |
| `segment_polygon_anyhit_rows` | `v1_6_11` | `embree_auto` | 0.884 | 1.484 | 0.596 |
| `segment_polygon_hitcount` | `v1_6_11` | `embree_1t` | 0.715 | 1.425 | 0.502 |
| `segment_polygon_hitcount` | `v1_6_11` | `embree_auto` | 0.851 | 1.425 | 0.597 |
| `service_coverage_gaps` | `v1_6_11` | `embree_1t` | 1.165 | 1.586 | 0.735 |
| `service_coverage_gaps` | `v1_6_11` | `embree_auto` | 1.064 | 1.586 | 0.671 |

## Failing

No failed executed rows.

## Boundary

This report is measured evidence only. It does not publish v1.6.11, authorize a tag, or authorize public speedup wording. Unsupported rows remain unsupported rather than being counted as wins or losses.
