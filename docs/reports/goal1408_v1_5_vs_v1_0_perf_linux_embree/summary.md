# Goal1408 v1.5 vs v1.0 Performance Comparison

- current commit: `e76adc4c1bc4d05ede46bf4d6cde1d315769e01f`
- v1.0 commit: `b9c9620af78a2fab92083d43af312bb6310e452a`
- copies: `512`
- iterations: `3`

Same command and same scale are run against v1.0 and current v1.5 candidate. Cells with backend errors are unavailable, not zero-speedup results. This runner does not authorize public speedup wording by itself.

| App | Backend | Status | v1.0 sec | v1.5 sec | v1.0/v1.5 | Boundary |
| --- | --- | --- | ---: | ---: | ---: | --- |
| `database_analytics` | `embree` | v1_5_slower | 0.001488 | 0.001700 | 0.876x | DB compact-summary only; no SQL/DBMS or row-materialization speedup claim. |
| `service_coverage_gaps` | `embree` | roughly_equal | 0.011171 | 0.011730 | 0.952x | Service coverage gap summary only; no whole service-optimization claim. |
| `event_hotspot_screening` | `embree` | roughly_equal | 0.018273 | 0.018704 | 0.977x | Hotspot count summary only; no whole hotspot-analytics claim. |
| `facility_knn_assignment` | `embree` | v1_5_faster | 0.093146 | 0.086695 | 1.074x | Coverage-threshold/compact output only; ranked KNN remains outside. |
| `road_hazard_screening` | `embree` | v1_5_slower | 0.007889 | 0.012611 | 0.626x | Compact hazard summary only; GIS/routing and default-app behavior remain outside. |
| `segment_polygon_hitcount` | `embree` | roughly_equal | 0.022352 | 0.022415 | 0.997x | Compact hit-count summary only; pair-row output remains outside. |
| `polygon_pair_overlap_area_rows` | `embree` | roughly_equal | 0.088796 | 0.092176 | 0.963x | Candidate discovery plus exact-area summary only; broad polygon overlay remains outside. |
| `hausdorff_distance` | `embree` | roughly_equal | 0.093992 | 0.089602 | 1.049x | Threshold decision/directed summary only; exact Hausdorff rows remain outside. |
| `ann_candidate_search` | `embree` | roughly_equal | 1.095467 | 1.097309 | 0.998x | Candidate-coverage/compact output only; full ANN ranking/indexing remains outside. |
| `outlier_detection` | `embree` | roughly_equal | 0.011656 | 0.011946 | 0.976x | Density count summary only; per-point labels remain outside. |
| `dbscan_clustering` | `embree` | roughly_equal | 0.011325 | 0.011802 | 0.960x | Core-count summary only; cluster expansion remains outside. |
| `robot_collision_screening` | `embree` | roughly_equal | 0.346853 | 0.343838 | 1.009x | Robot any-hit/pose summary only; full robot planning remains outside. |
| `barnes_hut_force_app` | `embree` | roughly_equal | 0.086842 | 0.087414 | 0.993x | Node-coverage/candidate summary only; force-vector reduction remains outside. |

## Excluded Apps

- `apple_rt_demo`: excluded from v1.5 active Embree+OptiX scope; Apple RT frozen before v2.1
- `hiprt_ray_triangle_hitcount`: excluded from v1.5 active Embree+OptiX scope; HIPRT frozen before v2.1
- `polygon_set_jaccard`: excluded from v1.5 because COLLECT_K_BOUNDED is deferred to v1.5.1
- `segment_polygon_anyhit_rows`: excluded from v1.5 because COLLECT_K_BOUNDED is deferred to v1.5.1
