# RTDL v1.5 Support Matrix

Status: released support matrix for standalone Embree+OptiX.

This matrix is narrower than the general current-main support matrix. It
records only the v1.5 standalone language/runtime scope: 14 included app
contracts and 4 excluded rows.

The matrix is also an architecture boundary. The supported primitive layer is
app-name-free where listed, but v1.5 does not claim that the native Embree/OptiX
engine is app-agnostic internally. Rows classified as `wrapper-backed` or
`scalar-only` may still rely on workload-shaped native entry points or Python
continuations.

## Included Apps

| App | Classification | v1.5 surface | Boundary |
| --- | --- | --- | --- |
| `database_analytics` | wrapper-backed | `DB_COMPACT_SUMMARY + REDUCE_INT(COUNT|SUM)` | compact summary only; no SQL/DBMS behavior |
| `graph_analytics` | scalar-only | `ANY_HIT + COUNT_HITS` | visibility any-hit/count only; graph-system analytics outside |
| `service_coverage_gaps` | fully generic | `FIXED_RADIUS_COUNT_THRESHOLD_2D + REDUCE_INT(COUNT)` | gap summary only; no whole service-optimization claim |
| `event_hotspot_screening` | fully generic | `FIXED_RADIUS_COUNT_THRESHOLD_2D + REDUCE_INT(COUNT)` | hotspot count summary only |
| `facility_knn_assignment` | scalar-only | `FIXED_RADIUS_COUNT_THRESHOLD_2D + REDUCE_INT(COUNT)` | coverage-threshold decision only; ranked KNN outside |
| `road_hazard_screening` | wrapper-backed | segment/polygon compact count summary | compact hazard summary only; GIS/routing outside |
| `segment_polygon_hitcount` | wrapper-backed | segment/polygon hit-count summary | compact hit-count summary only; pair rows outside |
| `polygon_pair_overlap_area_rows` | wrapper-backed | `POLYGON_PAIR_EXACT_AREA_SUMMARY + REDUCE_FLOAT(SUM)` | candidate discovery plus exact-area summary only |
| `hausdorff_distance` | scalar-only | `FIXED_RADIUS_COUNT_THRESHOLD_2D + REDUCE_INT(COUNT)` | threshold decision only; exact distance rows outside |
| `ann_candidate_search` | scalar-only | `FIXED_RADIUS_COUNT_THRESHOLD_2D + REDUCE_INT(COUNT)` | candidate coverage decision only; ranking/indexing outside |
| `outlier_detection` | scalar-only | `FIXED_RADIUS_COUNT_THRESHOLD_2D + REDUCE_INT(COUNT)` | density count summary only; per-point labels outside |
| `dbscan_clustering` | scalar-only | `FIXED_RADIUS_COUNT_THRESHOLD_2D + REDUCE_INT(COUNT)` | core-count summary only; cluster expansion outside |
| `robot_collision_screening` | wrapper-backed | `ANY_HIT + COUNT_HITS + REDUCE_INT(COUNT)` | prepared count/pose flags only; robot planning outside |
| `barnes_hut_force_app` | scalar-only | `FIXED_RADIUS_COUNT_THRESHOLD_2D + REDUCE_INT(COUNT)` | node-coverage decision only; force-vector reduction outside |

These 14 included app contracts require Embree and OptiX coverage in the v1.5
gate. They do not create no whole-app speedup authorization.

## Excluded Apps

| App | Reason | Follow-up |
| --- | --- | --- |
| `segment_polygon_anyhit_rows` | row-returning `COLLECT_K_BOUNDED` contract | v1.5.1 collect-k promotion track |
| `polygon_set_jaccard` | row-returning `COLLECT_K_BOUNDED` plus Jaccard positive-speedup boundary | v1.5.1 collect-k promotion track |
| `apple_rt_demo` | Apple RT is frozen before v2.1 | preserve proof surface only |
| `hiprt_ray_triangle_hitcount` | HIPRT is frozen before v2.1 | preserve proof surface only |

## Backend Boundary

- Active v1.5 standalone backends: Embree and OptiX.
- Frozen before v2.1: Vulkan, HIPRT, Apple RT.
- Source-tree usage: `PYTHONPATH=src:. python ...`.
- The `v1.5` annotated tag has been published after explicit release
  authorization. Do not move or retag it without a new explicit release action.
- Any future explicit release/tag action must be separate from this support
  matrix.
- Native app-agnostic cleanup is future work: v1.5.1 handles
  `COLLECT_K_BOUNDED`, and v1.6-v2.0 formalize partner mechanisms.
