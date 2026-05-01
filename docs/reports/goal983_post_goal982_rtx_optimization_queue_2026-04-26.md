# Goal983 Post-Goal982 RTX Optimization Queue

Date: 2026-04-26

Goal983 summarizes the current app-performance state after Goal982. It does not authorize public speedup claims and does not change app code.

## Current Claim State

- Public RTX speedup claims authorized: `0`
- Candidate rows for separate 2-AI public-claim review: `7`
- Internal-only margin/scale rows: `1`
- Rejected current public-speedup rows: `9`
- Timing-repair rows: `0`
- Graph-correctness-repair rows: `0`

## Candidate Rows

These rows are not public claims. They require separate larger-scale repeat evidence and 2-AI claim review before promotion.

| App | Path | Fastest baseline | Baseline / RTX ratio |
| --- | --- | --- | ---: |
| `robot_collision_screening` | `prepared_pose_flags` | `embree_anyhit_pose_count_or_equivalent_compact_summary` | 1585.066368 |
| `outlier_detection` | `prepared_fixed_radius_density_summary` | `cpu_scalar_threshold_count_oracle` | 5.325816 |
| `dbscan_clustering` | `prepared_fixed_radius_core_flags` | `cpu_scalar_threshold_count_oracle` | 29.128064 |
| `facility_knn_assignment` | `coverage_threshold_prepared` | `cpu_oracle_same_semantics` | 121.980502 |
| `segment_polygon_hitcount` | `segment_polygon_hitcount_native_experimental` | `embree_same_semantics` | 1.536281 |
| `segment_polygon_anyhit_rows` | `segment_polygon_anyhit_rows_prepared_bounded_gate` | `postgis_when_available_for_same_pair_semantics` | 3.930470 |
| `ann_candidate_search` | `candidate_threshold_prepared` | `cpu_oracle_same_semantics` | 5.805503 |

## Internal-Only Row

This row is not slower than its fastest baseline, but the margin is below the candidate threshold and should not be marketed.

| App | Path | Fastest baseline | Baseline / RTX ratio | Immediate interpretation |
| --- | --- | --- | ---: | --- |
| `service_coverage_gaps` | `prepared_gap_summary` | `embree_summary_path` | 1.022860 | Marginal positive result; needs larger-scale repeat evidence or optimization before claim review. |

## Rejected Rows Needing Performance Work

These rows should not enter public speedup review without new implementation or performance evidence.

| App | Path | Fastest baseline | Baseline / RTX ratio | Immediate interpretation |
| --- | --- | --- | ---: | --- |
| `database_analytics` | `prepared_db_session_sales_risk` | `embree_compact_summary` | 0.614881 | OptiX path slower than Embree compact summary. |
| `database_analytics` | `prepared_db_session_regional_dashboard` | `embree_compact_summary` | 0.938299 | Near parity but still slower than Embree. |
| `event_hotspot_screening` | `prepared_count_summary` | `embree_summary_path` | 0.786862 | OptiX summary path needs tuning before claim review. |
| `road_hazard_screening` | `road_hazard_native_summary_gate` | `embree_same_semantics` | 0.019586 | Current RTX path is far slower than Embree. |
| `graph_analytics` | `graph_visibility_edges_gate` | `embree_graph_ray_bfs_and_triangle_when_available` | 0.358306 | Correctness repaired, but same-scale Embree is faster than RTX. |
| `hausdorff_distance` | `directed_threshold_prepared` | `cpu_oracle_same_semantics` | 0.018452 | Current RTX phase is slower than small CPU oracle; needs larger-scale/tuned path. |
| `barnes_hut_force_app` | `node_coverage_prepared` | `cpu_oracle_same_semantics` | 0.453908 | Current RTX phase is slower than CPU oracle. |
| `polygon_pair_overlap_area_rows` | `polygon_pair_overlap_optix_native_assisted_phase_gate` | `postgis_when_available_for_same_unit_cell_contract` | 0.000419 | Current OptiX-assisted phase is not competitive. |
| `polygon_set_jaccard` | `polygon_set_jaccard_optix_native_assisted_phase_gate` | `embree_native_assisted_candidate_discovery` | 0.003627 | Current OptiX-assisted phase is not competitive. |

## Next Coding Priority

The next coding work should target rejected rows where the bottleneck is most likely in RTDL/native implementation rather than unavoidable workload semantics:

1. `graph_analytics`: correctness is repaired and same-scale evidence exists; next step is OptiX graph traversal performance profiling and reducing per-ray/per-record overhead.
2. `road_hazard_screening`: large rejection margin suggests the OptiX path is doing too much setup, transfer, or postprocess work relative to Embree.
3. `polygon_pair_overlap_area_rows` and `polygon_set_jaccard`: current OptiX-assisted path is dominated by candidate/refinement overhead and should not be marketed until redesigned.
4. `database_analytics` and `event_hotspot_screening`: investigate compact-summary kernel overhead and compare whether Embree-style compact result emission can be mirrored in OptiX.

Candidate rows should be kept separate: they need claim-review scale hardening, not immediate broad redesign.
