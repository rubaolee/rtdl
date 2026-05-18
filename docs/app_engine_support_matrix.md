# RTDL App Engine Support Matrix

Status: public app-level support map for the v2.0 release source
tree.

This matrix answers which engines each public app entry point exposes today.
It is app-level, not just primitive-level: a primitive may support an engine
even when a particular app CLI does not expose it.

The machine-readable source of truth is `rtdsl.app_engine_support_matrix()`.
For OptiX performance classification, use
`rtdsl.optix_app_performance_matrix()`.

## Status Legend

- `direct_cli_native`: the app CLI exposes this engine and uses native backend
  support for its RTDL core.
- `direct_cli_native_assisted`: the app exposes this engine and uses native or
  native-assisted backend work.
- `direct_cli_compatibility_fallback`: the app exposes this engine through a
  documented compatibility path; this is not an acceleration claim.
- `portable_cpu_oracle`: the app has a portable CPU/Python correctness path.
- `partial_cpu_oracle`: part of the app has a CPU/Python oracle, but another
  scenario is hardware-gated or may skip.
- `not_exposed_by_app_cli`: the public app file does not expose this engine.
- `apple_specific`: the app is specifically an Apple RT demo.

## Matrix

| App | cpu_python_reference | embree | optix | vulkan | hiprt | apple_rt |
| --- | --- | --- | --- | --- | --- | --- |
| `examples/v2_0/apps/analytics/rtdl_database_analytics_app.py` | `portable_cpu_oracle` | `direct_cli_native` | `direct_cli_native` | `direct_cli_native` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` |
| `examples/v2_0/apps/analytics/rtdl_graph_analytics_app.py` | `portable_cpu_oracle` | `direct_cli_native` | `direct_cli_compatibility_fallback` | `direct_cli_native` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` |
| `examples/legacy_or_backend_proofs/rtdl_apple_rt_demo_app.py` | `partial_cpu_oracle` | `apple_specific` | `apple_specific` | `apple_specific` | `apple_specific` | `direct_cli_native_assisted` |
| `examples/v2_0/apps/geospatial/rtdl_service_coverage_gaps.py` | `portable_cpu_oracle` | `direct_cli_native` | `direct_cli_native` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` |
| `examples/v2_0/apps/geospatial/rtdl_event_hotspot_screening.py` | `portable_cpu_oracle` | `direct_cli_native` | `direct_cli_native` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` |
| `examples/v2_0/apps/geospatial/rtdl_facility_knn_assignment.py` | `portable_cpu_oracle` | `direct_cli_native` | `direct_cli_native` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` |
| `examples/v2_0/apps/geospatial/rtdl_road_hazard_screening.py` | `portable_cpu_oracle` | `direct_cli_native` | `direct_cli_compatibility_fallback` | `direct_cli_native` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` |
| `examples/v2_0/features/spatial/rtdl_segment_polygon_hitcount.py` | `portable_cpu_oracle` | `direct_cli_native` | `direct_cli_compatibility_fallback` | `direct_cli_native` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` |
| `examples/v2_0/features/spatial/rtdl_segment_polygon_anyhit_rows.py` | `portable_cpu_oracle` | `direct_cli_native` | `direct_cli_native` | `direct_cli_native` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` |
| `examples/v2_0/features/spatial/rtdl_polygon_pair_overlap_area_rows.py` | `portable_cpu_oracle` | `direct_cli_native_assisted` | `direct_cli_native_assisted` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` |
| `examples/v2_0/features/spatial/rtdl_polygon_set_jaccard.py` | `portable_cpu_oracle` | `direct_cli_native_assisted` | `direct_cli_native_assisted` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` |
| `examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py` | `portable_cpu_oracle` | `direct_cli_native` | `direct_cli_native` | `direct_cli_native` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` |
| `examples/v2_0/apps/ml/rtdl_ann_candidate_app.py` | `portable_cpu_oracle` | `direct_cli_native` | `direct_cli_native` | `direct_cli_native` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` |
| `examples/v2_0/apps/ml/rtdl_outlier_detection_app.py` | `portable_cpu_oracle` | `direct_cli_native` | `direct_cli_native` | `direct_cli_native` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` |
| `examples/v2_0/apps/ml/rtdl_dbscan_clustering_app.py` | `portable_cpu_oracle` | `direct_cli_native` | `direct_cli_native` | `direct_cli_native` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` |
| `examples/v2_0/apps/robotics/rtdl_robot_collision_screening_app.py` | `portable_cpu_oracle` | `direct_cli_native` | `direct_cli_native` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` |
| `examples/v2_0/apps/simulation/rtdl_barnes_hut_force_app.py` | `portable_cpu_oracle` | `direct_cli_native` | `direct_cli_native` | `direct_cli_native` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` |
| `examples/legacy_or_backend_proofs/rtdl_hiprt_ray_triangle_hitcount.py` | `portable_cpu_oracle` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` | `direct_cli_native` | `not_exposed_by_app_cli` |

## v2.0 Reading Guide

- Embree rows are the CPU RT implementation path.
- OptiX rows are the NVIDIA RT implementation path, but only reviewed
  traversal-heavy subpaths should use RT-core wording.
- Vulkan, HIPRT, and Apple RT rows document preserved public app exposure; they
  are not the release-performance focus.
- Partner acceleration is app code layered on top of RTDL outputs. PyTorch,
  CuPy, NumPy, or app-owned native extensions can implement non-RT work without
  becoming RTDL engine customization.
- Full witness rows, compact summaries, and streaming witness pages are
  different contracts. Compare performance only when the contracts match.

## Boundaries

- `not_exposed_by_app_cli` does not mean the underlying primitive can never run
  on that engine.
- `--backend optix` is not automatically an NVIDIA RT-core acceleration claim.
- CUDA-style kernels launched from partner code are GPU compute, not RT-core
  traversal.
- App-specific logic belongs in Python or partner code, not in native RTDL
  engine symbols.
