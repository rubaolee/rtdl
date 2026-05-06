# Goal1408 v1.5 vs v1.0 Performance Comparison

- current commit: `e76adc4c1bc4d05ede46bf4d6cde1d315769e01f`
- v1.0 commit: `b9c9620af78a2fab92083d43af312bb6310e452a`
- copies: `512`
- iterations: `3`

Same command and same scale are run against v1.0 and current v1.5 candidate. Cells with backend errors are unavailable, not zero-speedup results. This runner does not authorize public speedup wording by itself.

| App | Backend | Status | v1.0 sec | v1.5 sec | v1.0/v1.5 | Boundary |
| --- | --- | --- | ---: | ---: | ---: | --- |
| `database_analytics` | `optix` | roughly_equal | 0.004171 | 0.004254 | 0.980x | DB compact-summary only; no SQL/DBMS or row-materialization speedup claim. |
| `graph_analytics` | `optix` | v1_5_faster | 0.531221 | 0.411316 | 1.292x | Graph visibility/count subpath only; graph-system analytics remain outside. |
| `facility_knn_assignment` | `optix` | v1_5_slower | 0.000097 | 0.000111 | 0.875x | Prepared facility coverage-threshold query only; ranked KNN remains outside. |
| `road_hazard_screening` | `optix` | v1_5_faster | 0.007960 | 0.007451 | 1.068x | Compact hazard summary only; GIS/routing and default-app behavior remain outside. |
| `segment_polygon_hitcount` | `optix` | roughly_equal | 0.033669 | 0.034314 | 0.981x | Compact hit-count summary only; pair-row output remains outside. |
| `polygon_pair_overlap_area_rows` | `optix` | roughly_equal | 0.748401 | 0.736527 | 1.016x | Candidate discovery plus exact-area summary only; broad polygon overlay remains outside. |
| `hausdorff_distance` | `optix` | roughly_equal | 0.000155 | 0.000160 | 0.969x | Threshold decision only; exact Hausdorff rows remain outside. |
| `ann_candidate_search` | `optix` | roughly_equal | 0.000085 | 0.000086 | 0.998x | Candidate-coverage decision only; full ANN ranking/indexing remains outside. |
| `robot_collision_screening` | `optix` | roughly_equal | 0.000106 | 0.000103 | 1.028x | Prepared pose-count query only; full robot planning remains outside. |
| `barnes_hut_force_app` | `optix` | roughly_equal | 0.000083 | 0.000081 | 1.022x | Node-coverage decision only; force-vector reduction remains outside. |

## Excluded Apps

- `apple_rt_demo`: excluded from v1.5 active Embree+OptiX scope; Apple RT frozen before v2.1
- `hiprt_ray_triangle_hitcount`: excluded from v1.5 active Embree+OptiX scope; HIPRT frozen before v2.1
- `polygon_set_jaccard`: excluded from v1.5 because COLLECT_K_BOUNDED is deferred to v1.5.1
- `segment_polygon_anyhit_rows`: excluded from v1.5 because COLLECT_K_BOUNDED is deferred to v1.5.1
