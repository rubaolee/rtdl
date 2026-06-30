# Goal1408 v1.5 vs v1.0 Performance Comparison

- current commit: `7f3551549c53ae80f6f14565e20620a886d100dd`
- v1.0 commit: `b9c9620af78a2fab92083d43af312bb6310e452a`
- copies: `512`
- iterations: `3`

Same command and same scale are run against v1.0 and current v1.5 candidate. Cells with backend errors are unavailable, not zero-speedup results. This runner does not authorize public speedup wording by itself.

| App | Backend | Status | v1.0 sec | v1.5 sec | v1.0/v1.5 | Boundary |
| --- | --- | --- | ---: | ---: | ---: | --- |
| `database_analytics` | `embree` | v1_5_slower | 0.001386 | 0.001992 | 0.696x | DB compact-summary only; no SQL/DBMS or row-materialization speedup claim. |
| `service_coverage_gaps` | `embree` | v1_5_faster | 0.016500 | 0.010349 | 1.594x | Service coverage gap summary only; no whole service-optimization claim. |
| `event_hotspot_screening` | `embree` | v1_5_faster | 0.041416 | 0.029571 | 1.401x | Hotspot count summary only; no whole hotspot-analytics claim. |
| `facility_knn_assignment` | `embree` | v1_5_faster | 0.118480 | 0.081636 | 1.451x | Coverage-threshold/compact output only; ranked KNN remains outside. |
| `road_hazard_screening` | `embree` | v1_5_faster | 0.013402 | 0.011527 | 1.163x | Compact hazard summary only; GIS/routing and default-app behavior remain outside. |
| `segment_polygon_hitcount` | `embree` | v1_5_slower | 0.023694 | 0.027400 | 0.865x | Compact hit-count summary only; pair-row output remains outside. |
| `polygon_pair_overlap_area_rows` | `embree` | roughly_equal | 0.081721 | 0.079281 | 1.031x | Candidate discovery plus exact-area summary only; broad polygon overlay remains outside. |
| `hausdorff_distance` | `embree` | v1_5_faster | 0.072686 | 0.066866 | 1.087x | Threshold decision/directed summary only; exact Hausdorff rows remain outside. |
| `ann_candidate_search` | `embree` | v1_5_slower | 1.089309 | 1.482698 | 0.735x | Candidate-coverage/compact output only; full ANN ranking/indexing remains outside. |
| `outlier_detection` | `embree` | v1_5_faster | 0.014220 | 0.012098 | 1.175x | Density count summary only; per-point labels remain outside. |
| `dbscan_clustering` | `embree` | v1_5_slower | 0.011672 | 0.015022 | 0.777x | Core-count summary only; cluster expansion remains outside. |
| `robot_collision_screening` | `embree` | v1_5_slower | 0.307391 | 0.341128 | 0.901x | Robot any-hit/pose summary only; full robot planning remains outside. |
| `barnes_hut_force_app` | `embree` | v1_5_slower | 0.092665 | 0.101339 | 0.914x | Node-coverage/candidate summary only; force-vector reduction remains outside. |

## Excluded Apps

- `apple_rt_demo`: excluded from v1.5 active Embree+OptiX scope; Apple RT frozen before v2.1
- `hiprt_ray_triangle_hitcount`: excluded from v1.5 active Embree+OptiX scope; HIPRT frozen before v2.1
- `polygon_set_jaccard`: excluded from v1.5 because COLLECT_K_BOUNDED is deferred to v1.5.1
- `segment_polygon_anyhit_rows`: excluded from v1.5 because COLLECT_K_BOUNDED is deferred to v1.5.1
