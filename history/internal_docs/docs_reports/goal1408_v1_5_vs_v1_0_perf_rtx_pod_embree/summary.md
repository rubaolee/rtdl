# Goal1408 v1.5 vs v1.0 Performance Comparison

- current commit: `9cf1fdda71043ec992d232ccf0305e502d9e1ad8`
- v1.0 commit: `b9c9620af78a2fab92083d43af312bb6310e452a`
- copies: `512`
- iterations: `3`

Same command and same scale are run against v1.0 and current v1.5 candidate. Cells with backend errors are unavailable, not zero-speedup results. This runner does not authorize public speedup wording by itself.

| App | Backend | Status | v1.0 sec | v1.5 sec | v1.0/v1.5 | Boundary |
| --- | --- | --- | ---: | ---: | ---: | --- |
| `database_analytics` | `embree` | roughly_equal | 0.001099 | 0.001149 | 0.956x | DB compact-summary only; no SQL/DBMS or row-materialization speedup claim. |
| `service_coverage_gaps` | `embree` | roughly_equal | 0.013891 | 0.014300 | 0.971x | Service coverage gap summary only; no whole service-optimization claim. |
| `event_hotspot_screening` | `embree` | roughly_equal | 0.019873 | 0.019986 | 0.994x | Hotspot count summary only; no whole hotspot-analytics claim. |
| `facility_knn_assignment` | `embree` | roughly_equal | 0.044091 | 0.044597 | 0.989x | Coverage-threshold/compact output only; ranked KNN remains outside. |
| `road_hazard_screening` | `embree` | v1_5_slower | 0.006733 | 0.010865 | 0.620x | Compact hazard summary only; GIS/routing and default-app behavior remain outside. |
| `segment_polygon_hitcount` | `embree` | roughly_equal | 0.018680 | 0.018843 | 0.991x | Compact hit-count summary only; pair-row output remains outside. |
| `polygon_pair_overlap_area_rows` | `embree` | v1_5_slower | 0.080925 | 0.085677 | 0.945x | Candidate discovery plus exact-area summary only; broad polygon overlay remains outside. |
| `hausdorff_distance` | `embree` | roughly_equal | 0.025291 | 0.025492 | 0.992x | Threshold decision/directed summary only; exact Hausdorff rows remain outside. |
| `ann_candidate_search` | `embree` | roughly_equal | 0.951182 | 0.949120 | 1.002x | Candidate-coverage/compact output only; full ANN ranking/indexing remains outside. |
| `outlier_detection` | `embree` | roughly_equal | 0.014001 | 0.013547 | 1.034x | Density count summary only; per-point labels remain outside. |
| `dbscan_clustering` | `embree` | roughly_equal | 0.013796 | 0.013915 | 0.991x | Core-count summary only; cluster expansion remains outside. |
| `robot_collision_screening` | `embree` | roughly_equal | 0.318840 | 0.323507 | 0.986x | Robot any-hit/pose summary only; full robot planning remains outside. |
| `barnes_hut_force_app` | `embree` | roughly_equal | 0.091615 | 0.091168 | 1.005x | Node-coverage/candidate summary only; force-vector reduction remains outside. |

## Excluded Apps

- `apple_rt_demo`: excluded from v1.5 active Embree+OptiX scope; Apple RT frozen before v2.1
- `hiprt_ray_triangle_hitcount`: excluded from v1.5 active Embree+OptiX scope; HIPRT frozen before v2.1
- `polygon_set_jaccard`: excluded from v1.5 because COLLECT_K_BOUNDED is deferred to v1.5.1
- `segment_polygon_anyhit_rows`: excluded from v1.5 because COLLECT_K_BOUNDED is deferred to v1.5.1
