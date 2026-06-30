# Goal1125 Unresolved RTX Public-Wording Prioritization

Date: 2026-04-29

Valid: `True`

Goal1125 is a prioritization audit only. It does not edit public wording, authorize speedup claims, start cloud resources, or release v1.0.

## Summary

- unresolved_nvidia_public_wording_apps: `4`
- public_wording_blocked: `2`
- public_wording_not_reviewed: `2`
- local_optimization_first: `4`
- needs_same_scale_or_normalized_baseline_review: `0`
- needs_larger_nontrivial_scale_contract: `0`

## Recommended Order

- `database_analytics`
- `graph_analytics`
- `polygon_pair_overlap_area_rows`
- `polygon_set_jaccard`

## Unresolved Rows

| App | Status | Bucket | Priority | Performance class | Pod policy | Next action |
| --- | --- | --- | --- | --- | --- | --- |
| `database_analytics` | `public_wording_not_reviewed` | `local_optimization_first` | `p1` | `python_interface_dominated` | `no_pod_until_code_or_contract_changes` | Profile prepared DB compact-summary transfer and aggregation overhead; reduce Python row materialization before a broader RTX rerun. |
| `graph_analytics` | `public_wording_blocked` | `local_optimization_first` | `p1` | `optix_traversal` | `no_pod_until_phase_split_or_code_changes` | Split RT traversal timing from BFS/triangle bookkeeping and reduce host-side frontier or set-intersection overhead before retesting on RTX. |
| `polygon_pair_overlap_area_rows` | `public_wording_blocked` | `local_optimization_first` | `p2` | `python_interface_dominated` | `no_pod_until_candidate_chunking_changes` | Fix candidate discovery/chunking and exact-area handoff. Public wording can only cover candidate discovery unless exact-area refinement becomes native. |
| `polygon_set_jaccard` | `public_wording_not_reviewed` | `local_optimization_first` | `p2` | `python_interface_dominated` | `no_pod_until_candidate_chunking_changes` | Fix Jaccard candidate discovery/chunking and document that exact set-area/Jaccard refinement remains CPU/Python-owned until a native reducer exists. |

## Evidence Notes

### `database_analytics`

Both compact-summary RTX rows are slower than Embree compact-summary baselines in Goal1060, so another paid pod run would mostly remeasure known overhead.

Goal1060 rejected rows:

- `prepared_db_session_sales_risk`: RTX `0.101725s`, fastest baseline `embree_compact_summary` `0.061593s`, ratio baseline/RTX `0.605485`.
- `prepared_db_session_regional_dashboard`: RTX `0.138423s`, fastest baseline `embree_compact_summary` `0.127206s`, ratio baseline/RTX `0.918964`.

### `graph_analytics`

Goal1060 shows the graph visibility RTX gate slower than the Embree graph-ray baseline, and graph bookkeeping phases are not cleanly separated enough for wording.

Goal1060 rejected rows:

- `graph_visibility_edges_gate`: RTX `1.316055s`, fastest baseline `embree_graph_ray_bfs_and_triangle_when_available` `0.567219s`, ratio baseline/RTX `0.431000`.

### `polygon_pair_overlap_area_rows`

The native-assisted RTX candidate-discovery phase loses badly to the PostGIS same-unit-cell contract in Goal1060.

Goal1060 rejected rows:

- `polygon_pair_overlap_optix_native_assisted_phase_gate`: RTX `2.407473s`, fastest baseline `postgis_when_available_for_same_unit_cell_contract` `0.001471s`, ratio baseline/RTX `0.000611`.

### `polygon_set_jaccard`

The native-assisted RTX Jaccard candidate phase is slower than the Embree candidate baseline in Goal1060.

Goal1060 rejected rows:

- `polygon_set_jaccard_optix_native_assisted_phase_gate`: RTX `2.613548s`, fastest baseline `embree_native_assisted_candidate_discovery` `0.013214s`, ratio baseline/RTX `0.005056`.

## Boundary

Goal1125 is a prioritization audit only. It does not edit public wording, authorize speedup claims, start cloud resources, or release v1.0.

