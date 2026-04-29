# Goal1063 Pre-Pod Local Completion Audit

Date: 2026-04-28

Valid: `True`

Goal1063 is a local planning/audit artifact. It does not run a pod, change public wording, authorize release, or authorize speedup claims.

## Summary

- reviewed_public_wording_apps: `9`
- blocked_public_wording_apps: `1`
- not_reviewed_public_wording_apps: `6`
- rejected_current_speedup_rows: `8`
- blocked_rows_ready_for_one_pod: `2`
- local_only_blockers_before_broader_pod: `8`

## Pod-Ready Scope

Only currently blocked Goal1062 validation plus large timing repeats are pod-ready now. Do not rerun rejected not-reviewed rows on paid cloud until their listed local work changes code or scale.

### Goal1062 Rows

| App | Path | Phase | Skip validation | Timing floor |
| --- | --- | --- | --- | ---: |
| `robot_collision_screening` | `prepared_pose_flags` | `correctness_validation` | `False` | `` |
| `robot_collision_screening` | `prepared_pose_flags` | `large_timing_repeat` | `True` | `0.100` |

## Rejected Rows Requiring Local Work Before Broader Pod Use

| App | Path | Ratio baseline/RTX | Fastest baseline | Pod policy | Local next |
| --- | --- | ---: | --- | --- | --- |
| `database_analytics` | `prepared_db_session_sales_risk` | `0.605485` | `embree_compact_summary` | `no_pod_until_code_or_scale_changes` | Profile and optimize the OptiX prepared DB compact-summary query path against Embree/PostgreSQL baselines before another pod run. |
| `database_analytics` | `prepared_db_session_regional_dashboard` | `0.918964` | `embree_compact_summary` | `no_pod_until_code_or_scale_changes` | Profile grouped dashboard aggregation and reduce Python/native transfer overhead before another pod run. |
| `graph_analytics` | `graph_visibility_edges_gate` | `0.431000` | `embree_graph_ray_bfs_and_triangle_when_available` | `no_pod_until_code_or_scale_changes` | Audit graph visibility/BFS/triangle RT mapping and separate RT traversal time from graph bookkeeping before another pod run. |
| `road_hazard_screening` | `road_hazard_native_summary_gate` | `0.036668` | `embree_same_semantics` | `no_pod_until_code_or_scale_changes` | Root-cause why Embree same-semantics summary is much faster; optimize segment/polygon OptiX native summary locally first. |
| `polygon_pair_overlap_area_rows` | `polygon_pair_overlap_optix_native_assisted_phase_gate` | `0.000611` | `postgis_when_available_for_same_unit_cell_contract` | `no_pod_until_code_or_scale_changes` | Fix native-assisted candidate discovery/chunking before rerun; current OptiX candidate phase is orders slower than PostGIS baseline. |
| `polygon_set_jaccard` | `polygon_set_jaccard_optix_native_assisted_phase_gate` | `0.005056` | `embree_native_assisted_candidate_discovery` | `no_pod_until_code_or_scale_changes` | Fix Jaccard candidate discovery/chunking and exact-area handoff before rerun; current OptiX candidate phase loses badly. |
| `hausdorff_distance` | `directed_threshold_prepared` | `0.005733` | `cpu_oracle_same_semantics` | `no_pod_until_scale_contract_changes` | Define a larger nontrivial threshold-decision scale where CPU oracle is not microsecond trivial, then validate dry-run semantics before pod. |
| `barnes_hut_force_app` | `node_coverage_prepared` | `0.392413` | `cpu_oracle_same_semantics` | `no_pod_until_scale_contract_changes` | Define a larger Barnes-Hut node-coverage decision contract and avoid trivial CPU-baseline scale before pod. |

## Boundary

Goal1063 is a local planning/audit artifact. It does not run a pod, change public wording, authorize release, or authorize speedup claims.

