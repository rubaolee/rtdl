# RTDL App Engine Support Matrix

Status: public app-level support map for current `main` after Goal688.

This matrix answers which engines each public app entry point exposes today. It is intentionally app-level, not just feature-level: an underlying RTDL primitive may support an engine while a particular app CLI does not expose that engine yet.

The machine-readable source of truth is `rtdsl.app_engine_support_matrix()`.
For OptiX performance classification specifically, use
`rtdsl.optix_app_performance_matrix()`.

## Status Legend

- `direct_cli_native`: the app CLI exposes this engine and the app uses native backend support for its RTDL core.
- `direct_cli_native_assisted`: the app CLI or app path exposes this engine and uses native/native-assisted backend work.
- `direct_cli_compatibility_fallback`: the app exposes this engine but the path is a documented compatibility path, not an acceleration claim.
- `portable_cpu_oracle`: the app has a portable CPU/Python correctness path.
- `partial_cpu_oracle`: only part of the app has a CPU/Python oracle; another scenario is hardware-gated or may skip.
- `not_exposed_by_app_cli`: the app does not expose this engine today, even if the underlying feature matrix may support related primitives.
- `apple_specific`: the app is specifically an Apple RT demo; non-Apple engines are not applicable entry points.

## Matrix

| App | CPU/Python | Embree | OptiX | Vulkan | HIPRT | Apple RT |
| --- | --- | --- | --- | --- | --- | --- |
| `examples/rtdl_database_analytics_app.py` | `portable_cpu_oracle` | `direct_cli_native` | `direct_cli_native` | `direct_cli_native` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` |
| `examples/rtdl_graph_analytics_app.py` | `portable_cpu_oracle` | `direct_cli_native` | `direct_cli_compatibility_fallback` | `direct_cli_native` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` |
| `examples/rtdl_apple_rt_demo_app.py` | `partial_cpu_oracle` | `apple_specific` | `apple_specific` | `apple_specific` | `apple_specific` | `direct_cli_native_assisted` |
| `examples/rtdl_service_coverage_gaps.py` | `portable_cpu_oracle` | `direct_cli_native` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` |
| `examples/rtdl_event_hotspot_screening.py` | `portable_cpu_oracle` | `direct_cli_native` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` |
| `examples/rtdl_facility_knn_assignment.py` | `portable_cpu_oracle` | `direct_cli_native` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` |
| `examples/rtdl_road_hazard_screening.py` | `portable_cpu_oracle` | `direct_cli_native` | `direct_cli_compatibility_fallback` | `direct_cli_native` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` |
| `examples/rtdl_segment_polygon_hitcount.py` | `portable_cpu_oracle` | `direct_cli_native` | `direct_cli_compatibility_fallback` | `direct_cli_native` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` |
| `examples/rtdl_segment_polygon_anyhit_rows.py` | `portable_cpu_oracle` | `direct_cli_native` | `direct_cli_compatibility_fallback` | `direct_cli_native` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` |
| `examples/rtdl_polygon_pair_overlap_area_rows.py` | `portable_cpu_oracle` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` |
| `examples/rtdl_polygon_set_jaccard.py` | `portable_cpu_oracle` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` |
| `examples/rtdl_hausdorff_distance_app.py` | `portable_cpu_oracle` | `direct_cli_native` | `direct_cli_native` | `direct_cli_native` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` |
| `examples/rtdl_ann_candidate_app.py` | `portable_cpu_oracle` | `direct_cli_native` | `direct_cli_native` | `direct_cli_native` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` |
| `examples/rtdl_outlier_detection_app.py` | `portable_cpu_oracle` | `direct_cli_native` | `direct_cli_native` | `direct_cli_native` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` |
| `examples/rtdl_dbscan_clustering_app.py` | `portable_cpu_oracle` | `direct_cli_native` | `direct_cli_native` | `direct_cli_native` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` |
| `examples/rtdl_robot_collision_screening_app.py` | `portable_cpu_oracle` | `direct_cli_native` | `direct_cli_native` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` |
| `examples/rtdl_barnes_hut_force_app.py` | `portable_cpu_oracle` | `direct_cli_native` | `direct_cli_native` | `direct_cli_native` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` |
| `examples/rtdl_hiprt_ray_triangle_hitcount.py` | `portable_cpu_oracle` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` | `direct_cli_native` | `not_exposed_by_app_cli` |

## Notes

- `database_analytics`: Primary DB app exposes CPU/Embree/OptiX/Vulkan; HIPRT and Apple DB feature paths exist below the app layer but are not exposed by this app CLI.
- `graph_analytics`: Primary graph app exposes CPU/Embree/OptiX/Vulkan for BFS and triangle-count scenarios.
- `apple_rt_demo`: Primary Apple RT demo is Apple-specific; closest-hit has CPU reference parity, visibility-count is hardware-gated and may skip if Apple RT is unavailable.
- `service_coverage_gaps`: Spatial radius-join app currently exposes CPU, Embree, and SciPy baseline; other RT engines are not app CLI options.
- `event_hotspot_screening`: Spatial self-join app currently exposes CPU, Embree, and SciPy baseline.
- `facility_knn_assignment`: Spatial KNN app currently exposes CPU, Embree, and SciPy baseline.
- `road_hazard_screening`: Segment/polygon app exposes CPU, Embree, OptiX, and Vulkan.
- `segment_polygon_hitcount`: Released segment/polygon example exposes CPU, Embree, OptiX, and Vulkan.
- `segment_polygon_anyhit_rows`: Released segment/polygon pair-emitting example exposes CPU, Embree, OptiX, and Vulkan.
- `polygon_pair_overlap_area_rows`: Current public script is CPU-reference only.
- `polygon_set_jaccard`: Current public script is CPU-reference only.
- `hausdorff_distance`: KNN app exposes CPU, Embree, OptiX, and Vulkan.
- `ann_candidate_search`: Candidate-search app exposes CPU, Embree, OptiX, Vulkan, and SciPy baseline.
- `outlier_detection`: Density app exposes CPU, Embree, OptiX, Vulkan, and SciPy baseline.
- `dbscan_clustering`: DBSCAN app exposes CPU, Embree, OptiX, Vulkan, and SciPy baseline.
- `robot_collision_screening`: Discrete collision app exposes CPU, Embree, and OptiX; Vulkan is intentionally not exposed until a dedicated any-hit app gate exists.
- `barnes_hut_force_app`: Candidate-generation app exposes CPU, Embree, OptiX, and Vulkan.
- `hiprt_ray_triangle_hitcount`: Scenario-specific HIPRT hit-count demo; HIPRT evidence is SDK/Orochi on tested hosts, not AMD GPU validation.

## OptiX Performance Classification

This table is separate from the app engine matrix. `direct_cli_native` means
the app exposes an OptiX-backed path; it does not automatically mean the
dominant operation is NVIDIA RT-core traversal.

The machine-readable source of truth is `rtdsl.optix_app_performance_matrix()`.

| Class | Meaning |
| --- | --- |
| `optix_traversal` | Dominant RTDL operation uses OptiX ray traversal/custom primitives and is eligible for RTX hardware acceleration on RTX-class GPUs. |
| `cuda_through_optix` | App uses CUDA-style kernels through the OptiX backend library; useful GPU compute, but not an RT-core traversal claim. |
| `host_indexed_fallback` | OptiX-facing app path currently dispatches to host-indexed CPU-side logic. |
| `python_interface_dominated` | Real native/backend work exists, but app-level performance is currently dominated by Python packing, row materialization, reduction, or CPU post-processing. |
| `not_optix_exposed` | Public app CLI does not expose OptiX today. |
| `not_optix_applicable` | App is for another engine family and OptiX is not an applicable entry point. |

| App | OptiX performance class | Note |
| --- | --- | --- |
| `examples/rtdl_database_analytics_app.py` | `python_interface_dominated` | Uses real OptiX DB BVH candidate discovery, but app-level performance is still dominated by Python/ctypes preparation, candidate copy-back, CPU exact filtering/grouping, and dict-row materialization. |
| `examples/rtdl_graph_analytics_app.py` | `host_indexed_fallback` | Current OptiX-facing BFS and triangle routines are host-indexed correctness paths, not dominant OptiX ray traversal or RT-core acceleration paths. |
| `examples/rtdl_apple_rt_demo_app.py` | `not_optix_applicable` | Apple-specific app; OptiX is not an applicable app entry point. |
| `examples/rtdl_service_coverage_gaps.py` | `not_optix_exposed` | Public app CLI does not expose OptiX today. |
| `examples/rtdl_event_hotspot_screening.py` | `not_optix_exposed` | Public app CLI does not expose OptiX today. |
| `examples/rtdl_facility_knn_assignment.py` | `not_optix_exposed` | Public app CLI does not expose OptiX today. |
| `examples/rtdl_road_hazard_screening.py` | `host_indexed_fallback` | Default segment/polygon OptiX app path uses host-indexed candidate reduction unless native OptiX mode is explicitly enabled and separately gated. |
| `examples/rtdl_segment_polygon_hitcount.py` | `host_indexed_fallback` | Default segment/polygon OptiX path is host-indexed; native OptiX mode must be promoted only after correctness and performance gates. |
| `examples/rtdl_segment_polygon_anyhit_rows.py` | `host_indexed_fallback` | Default segment/polygon OptiX pair-row path is host-indexed and can also be row-volume dominated. |
| `examples/rtdl_polygon_pair_overlap_area_rows.py` | `not_optix_exposed` | Public script is CPU-reference only today. |
| `examples/rtdl_polygon_set_jaccard.py` | `not_optix_exposed` | Public script is CPU-reference only today. |
| `examples/rtdl_hausdorff_distance_app.py` | `cuda_through_optix` | Uses KNN rows through CUDA-style kernels in the OptiX backend library; useful GPU compute, but not an RT-core traversal claim. |
| `examples/rtdl_ann_candidate_app.py` | `cuda_through_optix` | Uses KNN rows through CUDA-style kernels in the OptiX backend library; recall metrics remain app/Python work. |
| `examples/rtdl_outlier_detection_app.py` | `cuda_through_optix` | Default path uses fixed-radius rows through CUDA-style kernels; optional `rt_count_threshold` summary uses OptiX traversal to avoid neighbor-row materialization, but RTX-class measurements are still pending. |
| `examples/rtdl_dbscan_clustering_app.py` | `cuda_through_optix` | Default path uses fixed-radius rows through CUDA-style kernels; optional `rt_core_flags` summary uses OptiX traversal for core flags only, while Python clustering expansion remains outside the native summary path. |
| `examples/rtdl_robot_collision_screening_app.py` | `optix_traversal` | Uses OptiX ray/triangle any-hit traversal and is the best current OptiX flagship candidate; compact app output avoids returning full witness rows when only pose flags or hit counts are needed, but native pose-level OptiX summaries are still future ABI work. |
| `examples/rtdl_barnes_hut_force_app.py` | `cuda_through_optix` | Candidate generation uses KNN/radius-style GPU compute; Python tree/opening-rule/force reduction dominates the end-to-end app. |
| `examples/rtdl_hiprt_ray_triangle_hitcount.py` | `not_optix_exposed` | HIPRT-specific app; OptiX is not exposed by this public app CLI. |

Retired compatibility helpers:

- `examples/rtdl_sales_risk_screening.py`, `examples/rtdl_v0_7_db_app_demo.py`, and `examples/rtdl_v0_7_db_kernel_app_demo.py` remain runnable for compatibility and historical tests, but the public DB app row is now only `examples/rtdl_database_analytics_app.py`.
- `examples/rtdl_apple_rt_closest_hit.py` and `examples/rtdl_apple_rt_visibility_count.py` remain runnable helper/scenario files, but the public Apple app row is now only `examples/rtdl_apple_rt_demo_app.py`.

## Boundaries

- `not_exposed_by_app_cli` is not a claim that the underlying primitive can never run on that engine. It means this public app file does not expose that engine today.
- `--backend optix` is not automatically a NVIDIA RT-core acceleration claim. A NVIDIA RT-core app claim requires a measured path that uses OptiX traversal over an OptiX acceleration structure on RTX-class hardware.
- CUDA-style kernels compiled or launched inside the OptiX backend library are GPU compute through the OptiX backend, not RT-core traversal.
- Embree native paths are real CPU BVH / ray / point-query execution paths. They are RT-style CPU acceleration, not GPU RT-core execution.
- HIPRT evidence remains bounded by the documented HIPRT SDK/Orochi validation path and is not AMD GPU validation unless explicitly stated elsewhere.
- Apple RT DB and graph support in the lower-level feature matrix is native-assisted/Metal-compute scoped, not Apple MPS ray-tracing traversal for DB/graph.
- App-level Python orchestration and `rt.reduce_rows(...)` remain Python-owned unless a native backend helper is explicitly named.

## OptiX RTX Benchmark Readiness

Status: conservative gate before paying for another RTX cloud benchmark.

The machine-readable source of truth is
`rtdsl.optix_app_benchmark_readiness_matrix()`.

This table answers a narrower question than the app engine matrix: which apps
are actually ready for a serious NVIDIA RTX performance claim review after the
current tuning work? The answer is intentionally conservative. A CLI exposing
`--backend optix` is not enough; the measured path must isolate the native
OptiX traversal or native summary work from Python packing, dict-row
materialization, validation, and post-processing.

| Status | Meaning |
| --- | --- |
| `ready_for_rtx_claim_review` | The app has enough phase-clean RTX evidence to enter claim review. This is not automatic release authorization. |
| `needs_phase_contract` | The app is a credible RTX candidate, but timing must split preparation, traversal, materialization, postprocess, and validation before a cloud benchmark is trusted. |
| `needs_interface_tuning` | Native/backend work exists, but Python/interface, row materialization, or host-side reduction can dominate the app result. |
| `needs_native_kernel_tuning` | The public OptiX app path still needs native GPU/OptiX kernel work or must stay classified as fallback. |
| `needs_postprocess_split` | The accelerated sub-result exists, but app-level post-processing must be separated before performance claims. |
| `exclude_from_rtx_app_benchmark` | Do not include this app in NVIDIA RTX RT-core app claims today. It may still be a CPU, Embree, Apple, HIPRT, or GPU-compute app. |

| App | Readiness | Next goal | Allowed claim today |
| --- | --- | --- | --- |
| `examples/rtdl_database_analytics_app.py` | `needs_interface_tuning` | Goal706 | correctness-capable OptiX DB path only; no RTX app speedup claim yet |
| `examples/rtdl_graph_analytics_app.py` | `needs_native_kernel_tuning` | Goal707 | no RTX graph acceleration claim today |
| `examples/rtdl_apple_rt_demo_app.py` | `exclude_from_rtx_app_benchmark` | none | Apple RT demo claim only, not NVIDIA OptiX |
| `examples/rtdl_service_coverage_gaps.py` | `exclude_from_rtx_app_benchmark` | none | CPU/Embree/SciPy baseline app only until an OptiX path is added |
| `examples/rtdl_event_hotspot_screening.py` | `exclude_from_rtx_app_benchmark` | none | CPU/Embree/SciPy baseline app only until an OptiX path is added |
| `examples/rtdl_facility_knn_assignment.py` | `exclude_from_rtx_app_benchmark` | none | CPU/Embree/SciPy baseline app only until an OptiX path is added |
| `examples/rtdl_road_hazard_screening.py` | `needs_native_kernel_tuning` | Goal708 | no RTX road-hazard speedup claim today |
| `examples/rtdl_segment_polygon_hitcount.py` | `needs_native_kernel_tuning` | Goal708 | no RTX segment/polygon hit-count speedup claim today |
| `examples/rtdl_segment_polygon_anyhit_rows.py` | `needs_native_kernel_tuning` | Goal708 | no RTX pair-row speedup claim today |
| `examples/rtdl_polygon_pair_overlap_area_rows.py` | `exclude_from_rtx_app_benchmark` | none | CPU correctness app only |
| `examples/rtdl_polygon_set_jaccard.py` | `exclude_from_rtx_app_benchmark` | none | CPU correctness app only |
| `examples/rtdl_hausdorff_distance_app.py` | `exclude_from_rtx_app_benchmark` | Goal709 | GPU-compute comparison only; no RT-core acceleration claim |
| `examples/rtdl_ann_candidate_app.py` | `exclude_from_rtx_app_benchmark` | Goal709 | GPU-compute comparison only; no RT-core acceleration claim |
| `examples/rtdl_outlier_detection_app.py` | `needs_phase_contract` | Goal710 | candidate fixed-radius summary speedup claim only after phase-clean RTX rerun and review |
| `examples/rtdl_dbscan_clustering_app.py` | `needs_postprocess_split` | Goal711 | core-flag summary claim only; no full DBSCAN acceleration claim yet |
| `examples/rtdl_robot_collision_screening_app.py` | `needs_phase_contract` | Goal712 | flagship candidate; no final app speedup claim until RTX rerun |
| `examples/rtdl_barnes_hut_force_app.py` | `exclude_from_rtx_app_benchmark` | Goal709 | no RT-core Barnes-Hut claim today |
| `examples/rtdl_hiprt_ray_triangle_hitcount.py` | `exclude_from_rtx_app_benchmark` | none | HIPRT validation only, not NVIDIA OptiX |

Cloud benchmark policy after Goal705: do not rent or keep a paid RTX instance
for broad app benchmarking until Goal706 through Goal712 either close or
explicitly exclude their app from RTX RT-core claims. The only acceptable early
cloud reruns are narrow confirmation runs for a single app whose phase contract
has already been fixed locally.
