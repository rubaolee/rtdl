# RTDL App Engine Support Matrix

Status: public app-level support map for current `main` after Goal922.

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
| `examples/rtdl_service_coverage_gaps.py` | `portable_cpu_oracle` | `direct_cli_native` | `direct_cli_native` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` |
| `examples/rtdl_event_hotspot_screening.py` | `portable_cpu_oracle` | `direct_cli_native` | `direct_cli_native` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` |
| `examples/rtdl_facility_knn_assignment.py` | `portable_cpu_oracle` | `direct_cli_native` | `direct_cli_native` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` |
| `examples/rtdl_road_hazard_screening.py` | `portable_cpu_oracle` | `direct_cli_native` | `direct_cli_compatibility_fallback` | `direct_cli_native` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` |
| `examples/rtdl_segment_polygon_hitcount.py` | `portable_cpu_oracle` | `direct_cli_native` | `direct_cli_compatibility_fallback` | `direct_cli_native` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` |
| `examples/rtdl_segment_polygon_anyhit_rows.py` | `portable_cpu_oracle` | `direct_cli_native` | `direct_cli_native` | `direct_cli_native` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` |
| `examples/rtdl_polygon_pair_overlap_area_rows.py` | `portable_cpu_oracle` | `direct_cli_native_assisted` | `direct_cli_native_assisted` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` |
| `examples/rtdl_polygon_set_jaccard.py` | `portable_cpu_oracle` | `direct_cli_native_assisted` | `direct_cli_native_assisted` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` |
| `examples/rtdl_hausdorff_distance_app.py` | `portable_cpu_oracle` | `direct_cli_native` | `direct_cli_native` | `direct_cli_native` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` |
| `examples/rtdl_ann_candidate_app.py` | `portable_cpu_oracle` | `direct_cli_native` | `direct_cli_native` | `direct_cli_native` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` |
| `examples/rtdl_outlier_detection_app.py` | `portable_cpu_oracle` | `direct_cli_native` | `direct_cli_native` | `direct_cli_native` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` |
| `examples/rtdl_dbscan_clustering_app.py` | `portable_cpu_oracle` | `direct_cli_native` | `direct_cli_native` | `direct_cli_native` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` |
| `examples/rtdl_robot_collision_screening_app.py` | `portable_cpu_oracle` | `direct_cli_native` | `direct_cli_native` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` |
| `examples/rtdl_barnes_hut_force_app.py` | `portable_cpu_oracle` | `direct_cli_native` | `direct_cli_native` | `direct_cli_native` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` |
| `examples/rtdl_hiprt_ray_triangle_hitcount.py` | `portable_cpu_oracle` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` | `not_exposed_by_app_cli` | `direct_cli_native` | `not_exposed_by_app_cli` |

## Notes

- `database_analytics`: Primary DB app exposes CPU/Embree/OptiX/Vulkan; HIPRT and Apple DB feature paths exist below the app layer but are not exposed by this app CLI. `--require-rt-core` is accepted only for `--backend optix --output-mode compact_summary` because full/row modes are interface/materialization dominated.
- `graph_analytics`: Primary graph app exposes CPU/Embree/OptiX/Vulkan for BFS and triangle-count scenarios, and exposes a bounded `visibility_edges` scenario that maps candidate graph edges to `rt.visibility_pair_rows(...)`. `visibility_rows(...)` remains the Cartesian observer-target matrix helper; graph candidate-edge workloads must use `visibility_pair_rows(...)` to avoid cross-copy Cartesian expansion. Embree BFS and triangle-count now use ray traversal over graph-edge primitives for candidate generation. OptiX BFS and triangle-count now expose an explicit native graph-ray mode behind `--optix-graph-mode native` / `RTDL_OPTIX_GRAPH_MODE=native`; the default remains host-indexed until this mode passes an RTX cloud gate.
- `apple_rt_demo`: Primary Apple RT demo is Apple-specific; closest-hit has CPU reference parity, visibility-count is hardware-gated and may skip if Apple RT is unavailable.
- `service_coverage_gaps`: Spatial radius-join app exposes CPU, Embree, SciPy baseline, and an OptiX prepared gap-summary mode; Vulkan/HIPRT/Apple are not app CLI options.
- `event_hotspot_screening`: Spatial self-join app exposes CPU, Embree, SciPy baseline, and an OptiX prepared count-summary mode.
- `facility_knn_assignment`: Spatial KNN app exposes CPU, Embree, SciPy baseline, and an OptiX prepared coverage-threshold mode; ranked KNN assignment remains CPU/Embree/SciPy only.
- `road_hazard_screening`: Segment/polygon app exposes CPU, Embree, OptiX, and Vulkan; OptiX includes explicit auto/host_indexed/native mode selection, but native mode is still gated.
- `segment_polygon_hitcount`: Released segment/polygon example exposes CPU, Embree, OptiX, and Vulkan; OptiX includes explicit auto/host_indexed/native mode selection.
- `segment_polygon_anyhit_rows`: Released segment/polygon pair-emitting example exposes CPU, Embree, OptiX, and Vulkan; explicit `--backend optix --output-mode rows --optix-mode native` uses the bounded native OptiX pair-row emitter while auto mode remains conservative.
- `polygon_pair_overlap_area_rows`: Public script exposes CPU plus Embree/OptiX native-assisted modes: native LSI/PIP positive candidate discovery plus CPU exact area refinement.
- `polygon_set_jaccard`: Public script exposes CPU plus Embree/OptiX native-assisted modes: native LSI/PIP positive candidate discovery plus CPU exact set-area/Jaccard refinement.
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
| `optix_traversal_prepared_summary` | An explicit prepared summary mode uses OptiX traversal and compact native output, while the app's default/full-row path may still be CUDA-through-OptiX or Python/postprocess dominated. |
| `cuda_through_optix` | App uses CUDA-style kernels through the OptiX backend library; useful GPU compute, but not an RT-core traversal claim. |
| `host_indexed_fallback` | OptiX-facing app path currently dispatches to host-indexed CPU-side logic. |
| `python_interface_dominated` | Real native/backend work exists, but app-level performance is currently dominated by Python packing, row materialization, grouped-row decoding, or host-side post-processing. |
| `not_optix_exposed` | Public app CLI does not expose OptiX today. |
| `not_optix_applicable` | App is for another engine family and OptiX is not an applicable entry point. |

| App | OptiX performance class | Note |
| --- | --- | --- |
| `examples/rtdl_database_analytics_app.py` | `python_interface_dominated` | Uses real OptiX DB BVH candidate discovery and native C++ exact filtering/grouping. App-level performance is still limited by Python/ctypes preparation, candidate bitset copy-back, grouped-row decoding, and row materialization unless `compact_summary` is selected. The app supports `--require-rt-core` only for the bounded OptiX `compact_summary` claim path. |
| `examples/rtdl_graph_analytics_app.py` | `optix_traversal` | Explicit `visibility_edges` mode maps candidate graph edges to ray/triangle any-hit traversal. Embree BFS/triangle-count are ray-traversal candidate-generation paths. OptiX BFS/triangle-count have explicit native graph-ray mode, but it remains gated and outside the NVIDIA RT-core claim until cloud-tested. |
| `examples/rtdl_apple_rt_demo_app.py` | `not_optix_applicable` | Apple-specific app; OptiX is not an applicable app entry point. |
| `examples/rtdl_service_coverage_gaps.py` | `optix_traversal_prepared_summary` | Explicit `gap_summary_prepared` mode uses prepared OptiX fixed-radius threshold traversal and compact summary output; rows mode is not the RT-core claim path. `--require-rt-core` enforces that prepared mode. |
| `examples/rtdl_event_hotspot_screening.py` | `optix_traversal_prepared_summary` | Explicit `count_summary_prepared` mode uses prepared OptiX fixed-radius count traversal and compact hotspot summaries; rows mode is not the RT-core claim path. `--require-rt-core` enforces that prepared mode. |
| `examples/rtdl_facility_knn_assignment.py` | `optix_traversal_prepared_summary` | Explicit `coverage_threshold_prepared` mode uses prepared OptiX fixed-radius threshold traversal for service-coverage decisions only; ranked nearest-depot assignment remains outside the OptiX claim. |
| `examples/rtdl_road_hazard_screening.py` | `host_indexed_fallback` | Default segment/polygon OptiX app path uses host-indexed candidate reduction. Explicit native mode is now exposed for hit-count execution, but remains separately gated before any RT-core claim; `--require-rt-core` rejects it until strict RTX validation passes. |
| `examples/rtdl_segment_polygon_hitcount.py` | `host_indexed_fallback` | Default segment/polygon OptiX path is host-indexed; explicit native OptiX mode exists and must pass Goal807 strict correctness/performance gating before promotion. `--require-rt-core` rejects it today. |
| `examples/rtdl_segment_polygon_anyhit_rows.py` | `host_indexed_fallback` | Default segment/polygon OptiX pair-row path remains conservative, but explicit `--output-mode rows --optix-mode native` now calls the bounded native OptiX pair-row emitter. This is a true traversal path that still needs a real RTX artifact and overflow-free phase review before speedup claims. |
| `examples/rtdl_polygon_pair_overlap_area_rows.py` | `python_interface_dominated` | Public app exposes OptiX native-assisted LSI/PIP positive candidate discovery, then CPU/Python exact grid-cell area refinement. This is real traversal-assisted filtering, not a fully native polygon-area kernel. |
| `examples/rtdl_polygon_set_jaccard.py` | `python_interface_dominated` | Public app exposes OptiX native-assisted LSI/PIP positive candidate discovery, then CPU/Python exact grid-cell set-area/Jaccard refinement. This is real traversal-assisted filtering, not a fully native Jaccard kernel. |
| `examples/rtdl_hausdorff_distance_app.py` | `optix_traversal_prepared_summary` | Default exact-distance mode uses KNN rows through CUDA-style kernels; explicit `directed_threshold_prepared` mode uses prepared OptiX fixed-radius threshold traversal for Hausdorff <= radius decisions only. |
| `examples/rtdl_ann_candidate_app.py` | `optix_traversal_prepared_summary` | Default candidate reranking uses KNN rows through CUDA-style kernels; explicit `candidate_threshold_prepared` mode uses prepared OptiX fixed-radius threshold traversal for candidate-coverage decisions only. |
| `examples/rtdl_outlier_detection_app.py` | `optix_traversal_prepared_summary` | Default row path uses fixed-radius rows through CUDA-style kernels; explicit `rt_count_threshold_prepared` summary uses prepared OptiX traversal to avoid neighbor-row materialization, with RTX 4090 phase evidence preserved in Goals 793 and 795. |
| `examples/rtdl_dbscan_clustering_app.py` | `optix_traversal_prepared_summary` | Default row path uses fixed-radius rows through CUDA-style kernels; explicit `rt_core_flags_prepared` summary uses prepared OptiX traversal for core flags only, while Python clustering expansion remains outside the native summary path. |
| `examples/rtdl_robot_collision_screening_app.py` | `optix_traversal` | Uses OptiX ray/triangle any-hit traversal and is the best current OptiX flagship candidate. Pre-Goal748 OptiX robot evidence is superseded because a short-ray `optixReportIntersection` bug was fixed; use Goal748 post-fix parity/timing for current OptiX robot discussion. Compact app output avoids returning full witness rows when only pose flags or hit counts are needed; OptiX now has prepared scalar hit-count and prepared native pose-flag summary modes, while edge witnesses still require row mode. |
| `examples/rtdl_barnes_hut_force_app.py` | `optix_traversal_prepared_summary` | Default candidate rows use radius-style GPU compute; explicit `node_coverage_prepared` mode uses prepared OptiX fixed-radius threshold traversal for node-coverage decisions only. Python opening-rule and force reduction remain outside the claim. |
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
| `needs_real_rtx_artifact` | Local dry-run and same-semantics baseline work are complete, but a real RTX optix-mode artifact still has to be collected and reviewed before promotion. |
| `needs_interface_tuning` | Native/backend work exists, but Python/interface, row materialization, or host-side reduction can dominate the app result. |
| `needs_native_kernel_tuning` | The public OptiX app path still needs native GPU/OptiX kernel work or must stay classified as fallback. |
| `needs_postprocess_split` | The accelerated sub-result exists, but app-level post-processing must be separated before performance claims. |
| `exclude_from_rtx_app_benchmark` | Do not include this app in NVIDIA RTX RT-core app claims today. It may still be a CPU, Embree, Apple, HIPRT, or GPU-compute app. |

| App | Readiness | Next goal | Allowed claim today |
| --- | --- | --- | --- |
| `examples/rtdl_database_analytics_app.py` | `needs_interface_tuning` | Goal706 | correctness-capable OptiX DB path only; no RTX app speedup claim yet |
| `examples/rtdl_graph_analytics_app.py` | `needs_real_rtx_artifact` | Goal889/905 | graph visibility-edge filtering plus explicit native BFS/triangle graph-ray candidate generation; no shortest-path, graph database, distributed graph analytics, or whole-app graph-system speedup claim |
| `examples/rtdl_apple_rt_demo_app.py` | `exclude_from_rtx_app_benchmark` | none | Apple RT demo claim only, not NVIDIA OptiX |
| `examples/rtdl_service_coverage_gaps.py` | `ready_for_rtx_claim_review` | Goal917 | bounded prepared gap-summary path may enter claim review; no whole-app service-coverage speedup claim |
| `examples/rtdl_event_hotspot_screening.py` | `ready_for_rtx_claim_review` | Goal917/Goal919 | bounded prepared count-summary path may enter claim review; no whole-app hotspot-screening speedup claim |
| `examples/rtdl_facility_knn_assignment.py` | `ready_for_rtx_claim_review` | Goal887/Goal920 | bounded prepared facility service-coverage decision sub-path may enter claim review; no KNN assignment or ranking speedup claim |
| `examples/rtdl_road_hazard_screening.py` | `needs_real_rtx_artifact` | Goal888 | no RTX road-hazard speedup claim today |
| `examples/rtdl_segment_polygon_hitcount.py` | `needs_real_rtx_artifact` | Goal807 | no RTX segment/polygon hit-count speedup claim today |
| `examples/rtdl_segment_polygon_anyhit_rows.py` | `needs_real_rtx_artifact` | Goal873 | native bounded pair-row traversal path only; no pair-row speedup claim today |
| `examples/rtdl_polygon_pair_overlap_area_rows.py` | `needs_real_rtx_artifact` | Goal877 | native-assisted candidate-discovery path only; no full polygon-area speedup claim |
| `examples/rtdl_polygon_set_jaccard.py` | `needs_real_rtx_artifact` | Goal877 | native-assisted candidate-discovery path only; no full Jaccard speedup claim |
| `examples/rtdl_hausdorff_distance_app.py` | `needs_real_rtx_artifact` | Goal879 | prepared Hausdorff <= radius decision sub-path only; no exact-distance speedup claim |
| `examples/rtdl_ann_candidate_app.py` | `needs_real_rtx_artifact` | Goal880 | prepared ANN candidate-coverage decision sub-path only; no full ANN index or ranking speedup claim |
| `examples/rtdl_outlier_detection_app.py` | `ready_for_rtx_claim_review` | Goal795 | prepared fixed-radius scalar threshold-count sub-path may enter claim review; no broad outlier-app speedup claim |
| `examples/rtdl_dbscan_clustering_app.py` | `ready_for_rtx_claim_review` | Goal795 | prepared fixed-radius core-threshold summary may enter claim review; no full DBSCAN clustering acceleration claim |
| `examples/rtdl_robot_collision_screening_app.py` | `ready_for_rtx_claim_review` | Goal795 | prepared ray/triangle any-hit scalar pose-count sub-path may enter claim review; no full robot-planning speedup claim |
| `examples/rtdl_barnes_hut_force_app.py` | `needs_real_rtx_artifact` | Goal882 | prepared Barnes-Hut node-coverage decision sub-path only; no force or opening-rule speedup claim |
| `examples/rtdl_hiprt_ray_triangle_hitcount.py` | `exclude_from_rtx_app_benchmark` | none | HIPRT validation only, not NVIDIA OptiX |

Cloud benchmark policy after Goal795: do not rent or keep a paid RTX instance
for broad app benchmarking until the next local optimization batch is ready.
The preserved RTX 4090 evidence is enough for claim-review discussion of the
three prepared scalar sub-paths above, but not enough for broad whole-app
speedup claims.

## RT-Core App Maturity Contract

Status: v1.0 direction contract.

The machine-readable source of truth is
`rtdsl.rt_core_app_maturity_matrix()`.

This table answers the direct product question: what must happen before each
public app can honestly be called a NVIDIA RT-core app? The target for general
apps is `rt_core_ready`. Engine-specific apps such as Apple RT and HIPRT remain
outside the NVIDIA RT-core target rather than being forced into the OptiX table.

Cloud policy: do not restart or stop a paid cloud pod per app. Finish local
implementation, local correctness, docs, manifests, and review packets first;
then run one batched cloud validation session for all eligible RT-core paths.
Use `/Users/rl2025/rtdl_python_only/docs/rtx_cloud_single_session_runbook.md`
for the actual paid-pod procedure: Goal824 local readiness first, bootstrap
OptiX, run the OOM-safe groups, copy artifacts after every group, then shut
down.

| Status | Meaning |
| --- | --- |
| `rt_core_ready` | Current app or bounded sub-path uses OptiX traversal over an acceleration structure and may enter RTX claim review with phase-clean evidence. |
| `rt_core_partial_ready` | Real RT-core work exists, but the whole app or public claim path is still dominated by interface/materialization/postprocess. |
| `needs_rt_core_redesign` | Current app path is host-indexed, CUDA-through-OptiX, or otherwise not a true RT-core traversal claim. |
| `needs_optix_app_surface` | Public app does not expose OptiX today; it needs an OptiX surface plus true RT traversal design before any NVIDIA claim. |
| `not_nvidia_rt_core_target` | Engine-specific app; keep it out of NVIDIA OptiX/RTX maturity and cloud batches. |

| App | Current RT-core status | Target status | Required action | Cloud policy |
| --- | --- | --- | --- | --- |
| `database_analytics` | `rt_core_partial_ready` | `rt_core_ready` | Use compact prepared-kernel outputs where the app needs counts/summaries, then review exported native phase totals proving Python/materialization is not dominant. | No broad DB speedup claim until `compact_summary` is rerun on RTX hardware and Goal921 native phase totals pass same-semantics baseline review. |
| `graph_analytics` | `rt_core_partial_ready` | `rt_core_ready` | Use `visibility_edges` any-hit plus explicit native BFS/triangle graph-ray candidate generation as the bounded graph-to-RT lowerings; keep CPU-side frontier bookkeeping and neighbor-set intersection outside the RT-core claim. | Cloud only in the combined Goal889/905 graph gate; no graph RT-core claim until visibility, native BFS, and native triangle-count row digests pass on RTX hardware. |
| `apple_rt_demo` | `not_nvidia_rt_core_target` | `not_nvidia_rt_core_target` | Keep as Apple Metal/MPS RT evidence; do not fold into NVIDIA OptiX claim tables. | Never include in NVIDIA cloud batches. |
| `service_coverage_gaps` | `rt_core_ready` | `rt_core_ready` | Keep the prepared OptiX gap-summary path as the RT-core claim path, and prevent row output or nearest-clinic output from being presented as the claim. | No new pod is needed for readiness; use the Goal917 artifact in claim-review packaging, and rerun only as part of a consolidated regression batch. |
| `event_hotspot_screening` | `rt_core_ready` | `rt_core_ready` | Keep the prepared OptiX count-summary path as the RT-core claim path, and prevent neighbor-row output or whole-app hotspot analytics from being presented as the claim. | No new pod is needed for readiness; use the Goal917 RTX artifact and Goal919 same-scale baseline in claim-review packaging, and rerun only as part of a consolidated regression batch. |
| `facility_knn_assignment` | `rt_core_ready` | `rt_core_ready` | Keep `coverage_threshold_prepared` as the traversal-backed service-coverage decision path; no ranked KNN assignment RT-core claim exists, and KNN ranking/fallback assignment remain outside the RT-core claim until a native ranking design exists. | No new pod is needed for readiness; use the Goal887 RTX artifact and Goal920 same-scale CPU oracle baseline in claim-review packaging, and rerun only as part of a consolidated regression batch. |
| `road_hazard_screening` | `rt_core_partial_ready` | `rt_core_ready` | Use the Goal888 native road-hazard summary gate to prove explicit native segment/polygon traversal parity before changing default OptiX behavior or claims. | Cloud only in the deferred Goal888 strict gate; no road-hazard speedup claim until that passes. |
| `segment_polygon_hitcount` | `rt_core_partial_ready` | `rt_core_ready` | Use Goal807 to prove explicit native hit-count correctness/performance against host-indexed and PostGIS where available before promotion. | Cloud only in the deferred Goal807 native-vs-host-indexed gate after local packaging is complete. |
| `segment_polygon_anyhit_rows` | `rt_core_partial_ready` | `rt_core_ready` | Run the explicit native bounded pair-row app mode through Goal873 strict RTX validation, then decide whether to promote the default public rows path or keep native mode as an explicit bounded gate. | Cloud only after the deferred Goal873 strict gate has a prepared batch slot; require row-digest parity, zero overflow, and independent review on RTX hardware. |
| `polygon_pair_overlap_area_rows` | `rt_core_partial_ready` | `rt_core_ready` | Keep OptiX native-assisted LSI/PIP candidate discovery split from CPU exact area refinement; add a phase profiler before any cloud claim. | Cloud only after a local phase contract exists for candidate traversal, copyback, and CPU exact refinement. |
| `polygon_set_jaccard` | `rt_core_partial_ready` | `rt_core_ready` | Keep OptiX native-assisted LSI/PIP candidate discovery split from CPU exact set-area/Jaccard refinement; add a phase profiler before any cloud claim. | Cloud only after a local phase contract exists for candidate traversal, copyback, and CPU exact refinement. |
| `hausdorff_distance` | `rt_core_partial_ready` | `rt_core_ready` | Use `directed_threshold_prepared` for traversal-backed Hausdorff decision workloads; exact-distance KNN rows remain outside the RT-core claim until a native ranking design exists. | Cloud only after the threshold-decision profiler and baselines are packaged; no exact Hausdorff distance RT-core claim. |
| `ann_candidate_search` | `rt_core_partial_ready` | `rt_core_ready` | Use `candidate_threshold_prepared` for traversal-backed candidate-coverage decisions; candidate-subset KNN ranking remains outside the RT-core claim until a native ranking design exists. | Cloud only after the candidate-threshold profiler and baselines are packaged; no full ANN or ranking RT-core claim. |
| `outlier_detection` | `rt_core_ready` | `rt_core_ready` | Keep prepared scalar threshold-count as the RT-core claim path and prevent default row mode from being presented as the claim. | Include in the next batched cloud run only with the prepared scalar profiler. |
| `dbscan_clustering` | `rt_core_ready` | `rt_core_ready` | Keep prepared scalar core-threshold summary as the RT-core claim path and split Python cluster expansion from native timing. | Include in the next batched cloud run only with the prepared scalar profiler. |
| `robot_collision_screening` | `rt_core_ready` | `rt_core_ready` | Keep prepared ray/triangle any-hit scalar pose-count as the flagship RT-core path and expand only with phase-clean profilers. | Include in the next batched cloud run with prepared packed input and scalar pose-count mode. |
| `barnes_hut_force_app` | `rt_core_partial_ready` | `rt_core_ready` | Use `node_coverage_prepared` for traversal-backed node-coverage decisions; candidate rows, opening-rule evaluation, and force reduction remain outside the RT-core claim until native reduction designs exist. | Cloud only after the Barnes-Hut node-coverage profiler and baselines are packaged; no force-vector or opening-rule RT-core claim. |
| `hiprt_ray_triangle_hitcount` | `not_nvidia_rt_core_target` | `not_nvidia_rt_core_target` | Keep as HIPRT-specific validation; do not fold into NVIDIA OptiX app maturity. | Never include in NVIDIA OptiX cloud batches. |
