# Goal1408 v1.5 vs v1.0 Performance Comparison

- current commit: `9cf1fdda71043ec992d232ccf0305e502d9e1ad8`
- v1.0 commit: `b9c9620af78a2fab92083d43af312bb6310e452a`
- copies: `512`
- iterations: `3`

Same command and same scale are run against v1.0 and current v1.5 candidate. Cells with backend errors are unavailable, not zero-speedup results. This runner does not authorize public speedup wording by itself.

| App | Backend | Status | v1.0 sec | v1.5 sec | v1.0/v1.5 | Boundary |
| --- | --- | --- | ---: | ---: | ---: | --- |
| `database_analytics` | `optix` | roughly_equal | 0.001760 | 0.001843 | 0.955x | DB compact-summary only; no SQL/DBMS or row-materialization speedup claim. |
| `graph_analytics` | `optix` | v1_5_faster | 0.461245 | 0.405026 | 1.139x | Graph visibility/count subpath only; graph-system analytics remain outside. |
| `facility_knn_assignment` | `optix` | roughly_equal | 0.000077 | 0.000078 | 0.982x | Prepared facility coverage-threshold query only; ranked KNN remains outside. |
| `road_hazard_screening` | `optix` | v1_5_faster | 0.010508 | 0.006612 | 1.589x | Compact hazard summary only; GIS/routing and default-app behavior remain outside. |
| `segment_polygon_hitcount` | `optix` | roughly_equal | 0.028254 | 0.027528 | 1.026x | Compact hit-count summary only; pair-row output remains outside. |
| `polygon_pair_overlap_area_rows` | `optix` | v1_5_faster | 0.878978 | 0.735516 | 1.195x | Candidate discovery plus exact-area summary only; broad polygon overlay remains outside. |
| `hausdorff_distance` | `optix` | roughly_equal | 0.000140 | 0.000139 | 1.004x | Threshold decision only; exact Hausdorff rows remain outside. |
| `ann_candidate_search` | `optix` | roughly_equal | 0.000078 | 0.000078 | 0.998x | Candidate-coverage decision only; full ANN ranking/indexing remains outside. |
| `robot_collision_screening` | `optix` | v1_5_faster | 0.000101 | 0.000092 | 1.089x | Prepared pose-count query only; full robot planning remains outside. |
| `barnes_hut_force_app` | `optix` | roughly_equal | 0.000076 | 0.000074 | 1.031x | Node-coverage decision only; force-vector reduction remains outside. |

## Excluded Apps

- `apple_rt_demo`: excluded from v1.5 active Embree+OptiX scope; Apple RT frozen before v2.1
- `hiprt_ray_triangle_hitcount`: excluded from v1.5 active Embree+OptiX scope; HIPRT frozen before v2.1
- `polygon_set_jaccard`: excluded from v1.5 because COLLECT_K_BOUNDED is deferred to v1.5.1
- `segment_polygon_anyhit_rows`: excluded from v1.5 because COLLECT_K_BOUNDED is deferred to v1.5.1
