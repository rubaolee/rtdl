# RTDL v0.9.4 Apple RT Support Matrix

Date: 2026-04-19

Status: released support matrix.

## Apple RT Dispatch Matrix

| Predicate | `run_apple_rt` mode | Native-only contract | CPU-side work still disclosed |
| --- | --- | --- | --- |
| `bfs_discover` | `native_metal_compute` | `supported_for_csr_frontier_vertex_set` | dedupe and sorted row materialization |
| `bounded_knn_rows` | `native_mps_rt_2d_3d` | `supported_for_point2d_and_point3d` | distance ranking |
| `conjunctive_scan` | `native_metal_compute` | `supported_for_numeric_predicates` | row-id materialization only |
| `fixed_radius_neighbors` | `native_mps_rt_2d_3d` | `supported_for_point2d_and_point3d` | exact distance filter and sort |
| `grouped_count` | `native_metal_filter_cpu_aggregate` | `supported_for_numeric_predicates_cpu_aggregation` | CPU group aggregation after Metal filter |
| `grouped_sum` | `native_metal_filter_cpu_aggregate` | `supported_for_numeric_predicates_cpu_aggregation` | CPU group aggregation after Metal filter |
| `knn_rows` | `native_mps_rt_2d_3d` | `supported_for_point2d_and_point3d` | distance ranking |
| `overlay_compose` | `native_mps_rt` | `supported_for_polygon2d_polygon2d` | full pair row materialization |
| `point_in_polygon` | `native_mps_rt` | `supported_for_point2d_polygon2d` | exact point-in-polygon |
| `point_nearest_segment` | `native_mps_rt` | `supported_for_point2d_segment2d` | exact distance ranking |
| `polygon_pair_overlap_area_rows` | `native_mps_rt` | `supported_for_polygon2d_polygon2d` | exact unit-cell area |
| `polygon_set_jaccard` | `native_mps_rt` | `supported_for_polygon2d_polygon2d` | exact unit-cell set Jaccard |
| `ray_triangle_closest_hit` | `native_mps_rt` | `supported_for_3d` | row materialization only |
| `ray_triangle_hit_count` | `native_mps_rt_2d_3d` | `supported_for_2d_and_3d` | count accumulation |
| `segment_intersection` | `native_mps_rt` | `supported_for_2d` | exact intersection point |
| `segment_polygon_anyhit_rows` | `native_mps_rt` | `supported_for_segment2d_polygon2d` | exact segment-polygon refinement |
| `segment_polygon_hitcount` | `native_mps_rt` | `supported_for_segment2d_polygon2d` | exact segment-polygon refinement |
| `triangle_match` | `native_metal_compute` | `supported_for_csr_edge_seeds` | uniqueness and sorted row materialization |

## Honesty Boundary

`native_mps_rt` and `native_mps_rt_2d_3d` use Apple MPS ray-intersection paths.
`native_metal_compute` and `native_metal_filter_cpu_aggregate` use Apple Metal
compute kernels rather than MPS ray traversal. CPU-side refinement,
aggregation, sorting, or materialization remains part of the implementation
where stated above.

Therefore, current RTDL DB workloads on Apple Silicon (`conjunctive_scan`,
`grouped_count`, and `grouped_sum`) and current graph workloads
(`bfs_discover` and `triangle_match`) are Apple GPU compute/native-assisted
paths. They are not Apple ray-tracing-hardware traversal paths and must not be
marketed as MPS RT acceleration.

Do not claim broad Apple speedup, mature Apple backend status, or non-macOS
support from this matrix.
