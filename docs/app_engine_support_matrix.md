# RTDL App Engine Support Matrix

Status: public app-level support map for current `main` after Goal970.

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

- `database_analytics`: Primary DB app exposes CPU/Embree/OptiX/Vulkan; HIPRT and Apple DB feature paths exist below the app layer but are not exposed by this app CLI. `--require-rt-core` is accepted only for `--backend optix --output-mode compact_summary` because full/row modes are interface/materialization dominated. Native-continuation metadata is active only when compact DB summaries avoid row/group materialization.
- `graph_analytics`: Primary graph app exposes CPU/Embree/OptiX/Vulkan for BFS and triangle-count scenarios, and exposes a bounded `visibility_edges` scenario that maps candidate graph edges to `rt.visibility_pair_rows(...)`. `visibility_rows(...)` remains the Cartesian observer-target matrix helper; graph candidate-edge workloads must use `visibility_pair_rows(...)` to avoid cross-copy Cartesian expansion. Embree BFS and triangle-count now use ray traversal over graph-edge primitives for candidate generation. OptiX `visibility_edges` summary mode uses prepared any-hit count to avoid row materialization. OptiX BFS and triangle-count now expose an explicit native graph-ray mode behind `--optix-graph-mode native` / `RTDL_OPTIX_GRAPH_MODE=native`; graph summary mode uses native C++ continuation after rows are produced. The default remains host-indexed until this mode passes an RTX cloud gate.
- `apple_rt_demo`: Primary Apple RT demo is Apple-specific; closest-hit has CPU reference parity, visibility-count is hardware-gated and may skip if Apple RT is unavailable.
- `service_coverage_gaps`: Spatial radius-join app exposes CPU, Embree, SciPy baseline, and an OptiX prepared gap-summary mode; Vulkan/HIPRT/Apple are not app CLI options.
- `event_hotspot_screening`: Spatial self-join app exposes CPU, Embree, SciPy baseline, and an OptiX prepared count-summary mode.
- `facility_knn_assignment`: Spatial KNN app exposes CPU, Embree, SciPy baseline, and an OptiX prepared coverage-threshold mode; ranked KNN assignment remains CPU/Embree/SciPy only.
- `road_hazard_screening`: Segment/polygon app exposes CPU, Embree, OptiX, and Vulkan; OptiX includes explicit auto/host_indexed/native mode selection, but native mode is still gated.
- `segment_polygon_hitcount`: Released segment/polygon example exposes CPU, Embree, OptiX, and Vulkan; OptiX includes explicit auto/host_indexed/native mode selection.
- `segment_polygon_anyhit_rows`: Released segment/polygon pair-emitting example exposes CPU, Embree, OptiX, and Vulkan; explicit `--backend optix --output-mode rows --optix-mode native` uses the bounded native OptiX pair-row emitter while auto mode remains conservative.
- `polygon_pair_overlap_area_rows`: Public script exposes CPU plus Embree/OptiX native-assisted modes: native LSI/PIP positive candidate discovery plus native C++ exact area continuation.
- `polygon_set_jaccard`: Public script exposes CPU plus Embree/OptiX native-assisted modes: native LSI/PIP positive candidate discovery plus native C++ exact set-area/Jaccard continuation.
- `hausdorff_distance`: KNN app exposes CPU, Embree, OptiX, and Vulkan.
- `ann_candidate_search`: Candidate-search app exposes CPU, Embree, OptiX, Vulkan, and SciPy baseline. Compact rerank summaries use native C++ continuation for row/query/rank counts after RTDL KNN rows are produced; ANN indexing, candidate construction, recall policy, and ranking speedup claims remain outside this continuation.
- `outlier_detection`: Density app exposes CPU, Embree, OptiX, Vulkan, and SciPy baseline.
- `dbscan_clustering`: DBSCAN app exposes CPU, Embree, OptiX, Vulkan, and SciPy baseline.
- `robot_collision_screening`: Discrete collision app exposes CPU, Embree, and OptiX; Vulkan is intentionally not exposed until a dedicated any-hit app gate exists.
- `barnes_hut_force_app`: Candidate-generation app exposes CPU, Embree, OptiX, and Vulkan. Compact candidate summaries use native C++ continuation for row/body/node counts after RTDL fixed-radius rows are produced; opening-rule evaluation, force-vector reduction, and N-body simulation remain outside this continuation.
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
| `examples/rtdl_database_analytics_app.py` | `python_interface_dominated` | Uses real OptiX DB BVH candidate discovery and native C++ exact filtering/grouping. App-level performance is still limited by Python/ctypes preparation, candidate bitset copy-back, grouped-row decoding, and row materialization unless materialization-free `compact_summary` is selected. The app supports `--require-rt-core` only for the bounded OptiX `compact_summary` claim path, and native-continuation metadata is active only when compact DB summaries avoid row/group materialization. |
| `examples/rtdl_graph_analytics_app.py` | `optix_traversal` | Explicit `visibility_edges` mode maps candidate graph edges to ray/triangle any-hit traversal; summary mode uses prepared any-hit count to avoid row materialization. Embree BFS/triangle-count are ray-traversal candidate-generation paths. OptiX BFS/triangle-count have explicit native graph-ray mode and Goal969 RTX evidence, and graph summary mode uses native C++ continuation after rows are produced, but graph-system, shortest-path, and distributed-analytics claims remain outside the scope. |
| `examples/rtdl_apple_rt_demo_app.py` | `not_optix_applicable` | Apple-specific app; OptiX is not an applicable app entry point. |
| `examples/rtdl_service_coverage_gaps.py` | `optix_traversal_prepared_summary` | Explicit `gap_summary_prepared` mode uses prepared OptiX fixed-radius scalar threshold-count traversal for covered/uncovered counts only; rows mode is not the RT-core claim path. Goal991 keeps the public OptiX prepared app path off count-row materialization; household IDs require rows or Embree summary mode. |
| `examples/rtdl_event_hotspot_screening.py` | `optix_traversal_prepared_summary` | Explicit `count_summary_prepared` mode uses prepared OptiX fixed-radius scalar threshold-count traversal for hotspot count only; rows mode is not the RT-core claim path. Goal991 keeps the public OptiX prepared app path off count-row materialization; hotspot event IDs require rows or Embree summary mode. |
| `examples/rtdl_facility_knn_assignment.py` | `optix_traversal_prepared_summary` | Explicit `coverage_threshold_prepared` mode uses prepared OptiX fixed-radius scalar threshold-count traversal for service-coverage decisions only; ranked nearest-depot assignment remains outside the OptiX claim. Goal991 keeps the public prepared app path off count-row materialization; uncovered customer IDs are not emitted in scalar mode unless all customers are covered. |
| `examples/rtdl_road_hazard_screening.py` | `optix_traversal_prepared_summary` | Default segment/polygon OptiX app path remains conservative, but the prepared road-hazard summary profiler reuses a polygon BVH and runs native OptiX custom-AABB segment/polygon traversal plus native threshold-count continuation for compact hazard summaries. |
| `examples/rtdl_segment_polygon_hitcount.py` | `optix_traversal_prepared_summary` | Default segment/polygon OptiX path remains conservative, but the prepared hit-count profiler reuses a polygon BVH and runs native OptiX custom-AABB traversal plus native aggregate continuation for compact hit-count summaries. |
| `examples/rtdl_segment_polygon_anyhit_rows.py` | `optix_traversal` | Default segment/polygon OptiX pair-row path remains conservative, but the prepared bounded pair-row profiler reuses a polygon BVH and runs native OptiX custom-AABB traversal with bounded output and overflow metadata. |
| `examples/rtdl_polygon_pair_overlap_area_rows.py` | `python_interface_dominated` | Public app exposes OptiX native-assisted LSI/PIP positive candidate discovery, then native C++ exact grid-cell area continuation. This is real traversal-assisted filtering plus native continuation, not a monolithic GPU polygon-area kernel. |
| `examples/rtdl_polygon_set_jaccard.py` | `python_interface_dominated` | Public app exposes OptiX native-assisted LSI/PIP positive candidate discovery, then native C++ exact grid-cell set-area/Jaccard continuation. This is real traversal-assisted filtering plus native continuation, not a monolithic GPU Jaccard kernel. |
| `examples/rtdl_hausdorff_distance_app.py` | `optix_traversal_prepared_summary` | Default exact-distance mode uses KNN rows through CUDA-style kernels; explicit `directed_threshold_prepared` mode uses prepared OptiX fixed-radius scalar threshold-count traversal for Hausdorff <= radius decisions only. Goal990 keeps the public app path off count-row materialization; exact violating source IDs are not emitted in scalar mode unless all sources are covered. |
| `examples/rtdl_ann_candidate_app.py` | `optix_traversal_prepared_summary` | Default candidate reranking emits KNN rows and now uses native C++ continuation for compact row/query/rank summaries. The explicit `candidate_threshold_prepared` mode uses prepared OptiX fixed-radius scalar threshold-count traversal for candidate-coverage decisions only; ANN indexing, candidate construction, quality policy, ranking, and uncovered-query witness claims remain outside the OptiX claim. Goal991 keeps the public prepared app path off count-row materialization. |
| `examples/rtdl_outlier_detection_app.py` | `optix_traversal_prepared_summary` | Default row path uses fixed-radius rows through CUDA-style kernels; explicit `rt_count_threshold_prepared` plus `--output-mode density_count` uses prepared OptiX scalar threshold-count continuation and avoids neighbor rows and per-point density rows, with RTX 4090 phase evidence preserved in Goals 793 and 795. Use `density_summary` when per-point outlier labels are required. |
| `examples/rtdl_dbscan_clustering_app.py` | `optix_traversal_prepared_summary` | Default row path uses fixed-radius rows through CUDA-style kernels; explicit `rt_core_flags_prepared` plus `--output-mode core_count` uses prepared OptiX scalar threshold-count continuation for core counts only. Use `core_flags` when per-point core labels are required; Python clustering expansion remains outside the native summary path. |
| `examples/rtdl_robot_collision_screening_app.py` | `optix_traversal` | Uses OptiX ray/triangle any-hit traversal and remains a real RT-core path. Goal1126 reviewed explicit normalized per-pose wording only; it is not a same-total-work wall-time claim and not a whole-app robot-planning claim. Pre-Goal748 OptiX robot evidence is superseded because a short-ray `optixReportIntersection` bug was fixed; use post-fix artifacts only. Compact row-output modes avoid returning full witness rows, while prepared OptiX scalar hit-count and pose-flag modes report native continuation and avoid per-ray row materialization; edge witnesses still require row mode. |
| `examples/rtdl_barnes_hut_force_app.py` | `optix_traversal_prepared_summary` | Default candidate rows use fixed-radius candidate generation and native C++ continuation for compact candidate summaries. The explicit `node_coverage_prepared` mode uses prepared OptiX fixed-radius scalar threshold-count traversal for node-coverage decisions only. Goal990 keeps the public app path off count-row materialization; uncovered body IDs are not emitted in scalar mode unless all bodies are covered. Python opening-rule and force reduction remain outside the claim. |
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
| `examples/rtdl_database_analytics_app.py` | `ready_for_rtx_claim_review` | Goal921/Goal969 | prepared DB compact-summary traversal/filter/grouping sub-path may enter claim review; no DBMS or SQL-engine speedup claim |
| `examples/rtdl_graph_analytics_app.py` | `ready_for_rtx_claim_review` | Goal889/905/Goal969 | bounded graph visibility any-hit plus native BFS/triangle graph-ray candidate-generation sub-paths may enter claim review; no whole-app graph speedup claim |
| `examples/rtdl_apple_rt_demo_app.py` | `exclude_from_rtx_app_benchmark` | none | Apple RT demo claim only, not NVIDIA OptiX |
| `examples/rtdl_service_coverage_gaps.py` | `ready_for_rtx_claim_review` | Goal917 | bounded prepared gap-summary path may enter claim review; no whole-app service-coverage speedup claim |
| `examples/rtdl_event_hotspot_screening.py` | `ready_for_rtx_claim_review` | Goal917/Goal919 | bounded prepared count-summary path may enter claim review; no whole-app hotspot-screening speedup claim |
| `examples/rtdl_facility_knn_assignment.py` | `ready_for_rtx_claim_review` | Goal887/Goal920/Goal1058/Goal1146 | Goal1146 reviewed narrow public wording for the prepared facility coverage-threshold query sub-path only; no ranked KNN assignment or ranking speedup claim. |
| `examples/rtdl_road_hazard_screening.py` | `ready_for_rtx_claim_review` | Goal933/Goal969 | prepared native road-hazard summary traversal sub-path may enter claim review; no full GIS/routing or default-app speedup claim |
| `examples/rtdl_segment_polygon_hitcount.py` | `ready_for_rtx_claim_review` | Goal933/Goal969 | prepared native segment/polygon hit-count traversal sub-path may enter claim review; no broad segment/polygon app speedup claim |
| `examples/rtdl_segment_polygon_anyhit_rows.py` | `ready_for_rtx_claim_review` | Goal934/Goal969 | prepared bounded native pair-row traversal sub-path may enter claim review; no unbounded pair-row or broad app speedup claim |
| `examples/rtdl_polygon_pair_overlap_area_rows.py` | `ready_for_rtx_claim_review` | Goal877/Goal969 | native-assisted candidate-discovery path only; no full polygon-area speedup claim |
| `examples/rtdl_polygon_set_jaccard.py` | `ready_for_rtx_claim_review` | Goal877/Goal969 | native-assisted candidate-discovery path only; no full Jaccard speedup claim |
| `examples/rtdl_hausdorff_distance_app.py` | `ready_for_rtx_claim_review` | Goal887/Goal969/Goal990 | prepared scalar Hausdorff <= radius decision sub-path may enter claim review; no exact-distance speedup claim and no violating-ID witness claim in scalar mode |
| `examples/rtdl_ann_candidate_app.py` | `ready_for_rtx_claim_review` | Goal887/Goal969 | prepared ANN candidate-coverage decision sub-path may enter claim review; no full ANN index or ranking speedup claim |
| `examples/rtdl_outlier_detection_app.py` | `ready_for_rtx_claim_review` | Goal795/Goal992 | prepared fixed-radius scalar threshold-count sub-path may enter claim review; no per-point outlier-label or broad outlier-app speedup claim |
| `examples/rtdl_dbscan_clustering_app.py` | `ready_for_rtx_claim_review` | Goal795/Goal992 | prepared fixed-radius scalar core-count sub-path may enter claim review; no per-point core-flag or full DBSCAN clustering acceleration claim |
| `examples/rtdl_robot_collision_screening_app.py` | `ready_for_rtx_claim_review` | Goal795/Goal1008/Goal1126 | Goal1126 reviewed only normalized per-pose wording for the prepared pose-count query sub-path; same-total-work wall-time, full kinematics, witness rows, continuous collision, and whole robot-planning speedup remain outside the claim. |
| `examples/rtdl_barnes_hut_force_app.py` | `ready_for_rtx_claim_review` | Goal887/Goal969/Goal990/Goal1146 | Goal1146 reviewed narrow public wording for the prepared Barnes-Hut node-coverage query sub-path only; no uncovered-ID witness, force-vector, opening-rule, or N-body speedup claim. |
| `examples/rtdl_hiprt_ray_triangle_hitcount.py` | `exclude_from_rtx_app_benchmark` | none | HIPRT validation only, not NVIDIA OptiX |

Cloud benchmark policy after Goal1048/Goal1058, Goal1135/Goal1136, Goal1142,
Goal1164-Goal1177, and Goal1184: the consolidated RTX rerun is complete on an RTX A5000
from commit 0c79b64d1b71383080f2e8572612488796d1c16c, and Goal1058 added a
tracked-only archive rerun from commit 21fa036881bf9a0c806f69c15727d87b482ccfcf
with oracle parity for its validated diagnostic rows.
Goal1135/Goal1136 added changed-path RTX A5000 artifacts for DB compact
summary, graph visibility edges, road hazard, polygon pair overlap, polygon set
Jaccard, and Hausdorff threshold gates. Goal1142 added same-source replacement
evidence for the facility/robot/Barnes-Hut current-source packet, and
Goal1142/Goal1143 Gemini review accepted the evidence review. Goal1146
re-promoted facility and Barnes-Hut with bounded current-source public wording,
and Goal1126 promoted robot only with explicit normalized per-pose wording.
Goal1164 collected a newer RTX A5000 smoke/medium batch; all smoke rows passed,
ANN and robot exposed large-scale timing bottlenecks, and Jaccard passed at
chunk sizes 512-4096 while 256/8192 stayed diagnostic. Goal1165 fixed local
ANN/robot/Jaccard bottlenecks, and Goal1166 accepted the next pod packet by
Codex+Gemini review. Goal1177 accepted the recovered clean-source
staged-archive Goal1170 eight-row RTX A5000 batch as external-review input only
after documenting the initial missing-manifest failure and manifest-generation
recovery. Goal1184 accepted the newer Goal1182 RTX A4500 eight-row batch as
external-review input only after SHA-matched copy-back and valid local intake.
Most Groups D-H are bounded prepared sub-path or native-assisted
phase evidence, not whole-app speedup. Future pods should only be run after
local analyzer/intake work is complete for new functionality.

## NVIDIA RTX Public Wording Status

The machine-readable source of truth is `rtdsl.rtx_public_wording_matrix()`.
This table is deliberately separate from readiness and maturity. An app can
have a real RT-core path and still be blocked from public speedup wording when
the reviewed evidence is too short, too broad, or not yet packaged for public
claims.

| Status | Meaning |
| --- | --- |
| `public_wording_reviewed` | Exact bounded sub-path speedup wording passed Goal1009 review and may be used with its stated boundary. |
| `public_wording_blocked` | Real RT-core work exists, but public speedup wording is blocked by the current evidence gate. |
| `public_wording_not_reviewed` | The app or bounded sub-path is RT-core ready, but no exact public speedup wording has been reviewed. |
| `not_nvidia_public_wording_target` | Engine-specific app; keep it out of NVIDIA RTX public wording. |

Current reviewed public wording rows after Goal1224: `12`. Goal1146 re-promoted
`facility_knn_assignment / coverage_threshold_prepared_recentered` and
`barnes_hut_force_app / node_coverage_prepared_rich` using current-source
Goal1142 evidence and 2-AI promotion review. Goal1126 reviewed
`robot_collision_screening / prepared_pose_flags` normalized per-pose wording
only; it is not a same-total-work wall-time claim and not a whole-app
robot-planning speedup claim. Goal1177 and Goal1184 do not add any new reviewed
public wording row. Goal1177 does not add any new reviewed public wording row.
Goal1177 and Goal1184 do not add any new reviewed public wording row.
Goal1208 adds exactly one reviewed public wording row for
`road_hazard_screening / prepared_native_compact_summary_40k`, limited to the
prepared native compact-summary traversal/count sub-path at 40k copies.
Goal1224 adds reviewed Hausdorff threshold-decision wording and keeps graph
public speedup wording blocked because current same-contract evidence shows
OptiX slower than Embree. Goal1263 promotes bounded polygon-pair wording for
RT-assisted LSI/PIP positive candidate discovery plus native C++ exact area
continuation; monolithic polygon overlay, broad GIS acceleration, arbitrary
polygon geometry, and whole-app polygon-overlap speedup remain outside the
claim.

## RT-Core App Maturity Contract

Status: v1.0 direction contract.

The machine-readable source of truth is
`rtdsl.rt_core_app_maturity_matrix()`.

This table answers the direct product question: what must happen before each
public app can honestly be called a NVIDIA RT-core app? The target for general
apps is `rt_core_ready`. Engine-specific apps such as Apple RT and HIPRT remain
outside the NVIDIA RT-core target rather than being forced into the OptiX table.

Cloud policy: do not restart or stop a paid cloud pod per app. Goal1048
completed the required consolidated RTX rerun; Goal1135/Goal1136 added the
current changed-path artifact batch and intake; Goal1164 added the latest RTX
A5000 smoke/medium batch; Goal1165 fixed local bottlenecks before the next pod;
Goal1166 prepared the accepted next-pod runner, Goal1177 accepted the
recovered clean-source staged-archive Goal1170 batch as external-review input
only, and Goal1184 accepted the newer Goal1182 RTX A4500 batch as
external-review input only. Future runs must similarly carry `RTDL_SOURCE_COMMIT` traceability and explicit validation. Only
validated/strict bounded paths may be described as claim-grade.
Use `/Users/rl2025/rtdl_python_only/docs/rtx_cloud_single_session_runbook.md`
for the actual paid-pod procedure: Goal824 local readiness first, bootstrap
OptiX, run the OOM-safe groups, copy artifacts after every group, then shut
down.

| Status | Meaning |
| --- | --- |
| `rt_core_ready` | Current app or bounded sub-path uses OptiX traversal over an acceleration structure and may enter RTX claim review with phase-clean evidence. |
| `blocked_for_public_speedup_wording` | Real RT-core work exists, but public speedup wording is blocked by the current evidence gate. |
| `rt_core_partial_ready` | Real RT-core work exists, but the whole app or public claim path is still dominated by interface/materialization/postprocess. |
| `needs_rt_core_redesign` | Current app path is host-indexed, CUDA-through-OptiX, or otherwise not a true RT-core traversal claim. |
| `needs_optix_app_surface` | Public app does not expose OptiX today; it needs an OptiX surface plus true RT traversal design before any NVIDIA claim. |
| `not_nvidia_rt_core_target` | Engine-specific app; keep it out of NVIDIA OptiX/RTX maturity and cloud batches. |

| App | Current RT-core status | Target status | Required action | Cloud policy |
| --- | --- | --- | --- | --- |
| `database_analytics` | `rt_core_ready` | `rt_core_ready` | Keep compact_summary prepared DB outputs as the only RT-core claim path; row materialization, SQL-engine behavior, and whole-dashboard claims remain outside the RT-core claim. | Goal1048/Goal1058 and Goal1135/Goal1136 RTX A5000 evidence remain historical validation context. Goal1164 collected a newer RTX A5000 smoke/medium batch, Goal1165 fixed local ANN/robot/Jaccard bottlenecks, Goal1166 prepared the next pod packet, Goal1177 accepted the recovered clean-source Goal1170 batch as external-review input only, and Goal1184 accepted newer Goal1182 RTX A4500 batch evidence as external-review input only. This is not whole-app speedup evidence and does not authorize new public wording. |
| `graph_analytics` | `rt_core_ready` | `rt_core_ready` | Keep `visibility_edges` prepared any-hit count plus explicit native BFS/triangle graph-ray candidate generation as the bounded graph-to-RT lowerings; graph summary mode uses native C++ continuation, while multi-step BFS orchestration and whole-graph analytics remain outside the RT-core claim. | Goal1048/Goal1058 RTX A5000 evidence remains historical validation context; Goal1135/Goal1136 added changed-path RTX A5000 artifacts from source marker 21fa036881bf9a0c806f69c15727d87b482ccfcf. Goal1177 accepted recovered clean-source graph evidence as external-review input only, and Goal1184 accepted newer Goal1182 RTX A4500 graph evidence as external-review input only. claim-grade only for validated or strict bounded sub-path evidence, not whole-app speedup. |
| `apple_rt_demo` | `not_nvidia_rt_core_target` | `not_nvidia_rt_core_target` | Keep as Apple Metal/MPS RT evidence; do not fold into NVIDIA OptiX claim tables. | Never include in NVIDIA cloud batches. |
| `service_coverage_gaps` | `rt_core_ready` | `rt_core_ready` | Keep the prepared OptiX gap-summary path as the RT-core scalar count claim path, and prevent household-id, row output, or nearest-clinic output from being presented as the claim. | Goal1048/Goal1058 RTX A5000 evidence remains historical validation context; Goal1135/Goal1136 added changed-path RTX A5000 artifacts from source marker 21fa036881bf9a0c806f69c15727d87b482ccfcf. Goal1177 is follow-up batch context, not new public wording. claim-grade only for validated or strict bounded sub-path evidence, not whole-app speedup. |
| `event_hotspot_screening` | `rt_core_ready` | `rt_core_ready` | Keep the prepared OptiX count-summary path as the RT-core scalar hotspot-count claim path, and prevent hotspot IDs, neighbor-row output, or whole-app hotspot analytics from being presented as the claim. | Goal1048/Goal1058 RTX A5000 evidence remains historical validation context; Goal1135/Goal1136 added changed-path RTX A5000 artifacts from source marker 21fa036881bf9a0c806f69c15727d87b482ccfcf. Goal1177 is follow-up batch context, not new public wording. claim-grade only for validated or strict bounded sub-path evidence, not whole-app speedup. |
| `facility_knn_assignment` | `rt_core_ready` | `rt_core_ready` | Keep `coverage_threshold_prepared` as the traversal-backed scalar service-coverage decision path; no ranked KNN assignment RT-core claim exists, and KNN ranking/fallback assignment/uncovered-ID witnesses remain outside the RT-core claim until a native ranking or witness design exists. | Goal1146 reviewed narrow public wording for the prepared coverage-threshold query sub-path only. |
| `road_hazard_screening` | `rt_core_ready` | `rt_core_ready` | Keep the prepared native road-hazard compact-summary gate separate from default app behavior and full GIS/routing claims. | Goal1208 reviewed narrow public wording for the prepared native compact-summary traversal/count sub-path at 40k copies only. Default app behavior, full GIS/routing, row output, Python orchestration, and whole-app road-hazard speedup remain outside the wording. |
| `segment_polygon_hitcount` | `rt_core_ready` | `rt_core_ready` | Keep the prepared native hit-count gate separate from pair-row output and broader segment/polygon app claims. | Goal1048/Goal1058 RTX A5000 evidence remains historical validation context; Goal1135/Goal1136 added changed-path RTX A5000 artifacts from source marker 21fa036881bf9a0c806f69c15727d87b482ccfcf. Goal1177 is follow-up batch context, not new public wording. claim-grade only for validated or strict bounded sub-path evidence, not whole-app speedup. |
| `segment_polygon_anyhit_rows` | `rt_core_ready` | `rt_core_ready` | Keep the prepared bounded pair-row gate separate from unbounded row-volume performance and default app behavior. | Goal1048/Goal1058 RTX A5000 evidence remains historical validation context; Goal1135/Goal1136 added changed-path RTX A5000 artifacts from source marker 21fa036881bf9a0c806f69c15727d87b482ccfcf. Goal1177 is follow-up batch context, not new public wording. claim-grade only for validated or strict bounded sub-path evidence, not whole-app speedup. |
| `polygon_pair_overlap_area_rows` | `rt_core_ready` | `rt_core_ready` | Keep OptiX native-assisted LSI/PIP positive candidate discovery split from native C++ exact area continuation; claim only the Goal1263 bounded sub-path unless broader same-semantics app timing is reviewed. | Goal1263 promotes bounded polygon-pair wording for RT-assisted LSI/PIP positive candidate discovery plus native C++ exact area continuation at 40k, 80k, and 160k copies on RTX A5000; candidate-count mismatch remains a v1.2 diagnostic boundary. Monolithic GPU polygon overlay, broad GIS acceleration, arbitrary polygon geometry, and whole-app polygon-overlap speedup remain outside the wording. |
| `polygon_set_jaccard` | `rt_core_ready` | `rt_core_ready` | Keep OptiX native-assisted LSI/PIP candidate discovery split from native C++ exact set-area/Jaccard continuation; claim only the reviewed chunked candidate-discovery sub-path unless same-semantics app timing is reviewed. | Goal1048/Goal1058 RTX A5000 evidence remains historical validation context; Goal1135/Goal1136 added changed-path RTX A5000 artifacts from source marker 21fa036881bf9a0c806f69c15727d87b482ccfcf. Goal1177 accepted recovered clean-source Jaccard evidence as external-review input only; candidate-count mismatch remains a boundary. claim-grade only for validated or strict bounded sub-path evidence, not whole-app speedup. |
| `hausdorff_distance` | `rt_core_ready` | `rt_core_ready` | Use `directed_threshold_prepared` as the only RT-core Hausdorff claim path; exact-distance KNN rows and scalar-mode violating-ID witnesses remain outside the claim. | Goal1048/Goal1058 RTX A5000 evidence remains historical validation context; Goal1135/Goal1136 added changed-path RTX A5000 artifacts from source marker 21fa036881bf9a0c806f69c15727d87b482ccfcf. Goal1177 accepted recovered clean-source Hausdorff evidence as external-review input only. claim-grade only for validated or strict bounded sub-path evidence, not whole-app speedup. |
| `ann_candidate_search` | `rt_core_ready` | `rt_core_ready` | Use `candidate_threshold_prepared` as the only RT-core ANN claim path. Native C++ rerank-summary continuation is allowed as an app postprocess improvement, but KNN ranking, candidate construction, quality policy, uncovered-query witnesses, and full ANN indexing remain outside the RT-core claim. Goal1165 replaced the tiled validation path with a single-tile analytic expectation so large prepared timing runs do not accidentally validate an O(copies^2) fixture. | Goal1048/Goal1058 and Goal1135/Goal1136 RTX A5000 evidence remain historical validation context. Goal1164 collected a newer RTX A5000 smoke/medium batch, Goal1165 fixed local ANN/robot/Jaccard bottlenecks, Goal1166 prepared the next pod packet, Goal1177 accepted the recovered clean-source ANN timing row as timing-only external-review input, and Goal1184 accepted newer Goal1182 RTX A4500 ANN timing as timing-only external-review input. This is not whole-app speedup evidence and does not authorize new public wording. |
| `outlier_detection` | `rt_core_ready` | `rt_core_ready` | Keep `--output-mode density_count --optix-summary-mode rt_count_threshold_prepared` as the scalar RT-core claim path and prevent default rows or per-point labels from being presented as the claim. | Goal1048/Goal1058 RTX A5000 evidence remains historical validation context; Goal1135/Goal1136 added changed-path RTX A5000 artifacts from source marker 21fa036881bf9a0c806f69c15727d87b482ccfcf. Goal1177 is follow-up batch context, not new public wording. claim-grade only for validated or strict bounded sub-path evidence, not whole-app speedup. |
| `dbscan_clustering` | `rt_core_ready` | `rt_core_ready` | Keep `--output-mode core_count --optix-summary-mode rt_core_flags_prepared` as the scalar RT-core claim path and split per-point core flags plus Python cluster expansion from native timing. | Goal1048/Goal1058 RTX A5000 evidence remains historical validation context; Goal1135/Goal1136 added changed-path RTX A5000 artifacts from source marker 21fa036881bf9a0c806f69c15727d87b482ccfcf. Goal1177 is follow-up batch context, not new public wording. claim-grade only for validated or strict bounded sub-path evidence, not whole-app speedup. |
| `robot_collision_screening` | `rt_core_ready` | `rt_core_ready` | Keep prepared ray/triangle any-hit scalar pose-count as a real RT-core path. Do not present it as same-total-work wall-time, full kinematics, witness-row, continuous collision, or whole robot-planning speedup. Goal1165 removed avoidable CPU validation from prepared timing paths; skip-validation artifacts remain timing-only, not correctness evidence. | Goal1126 reviewed explicit normalized per-pose wording only. Goal1164/Goal1165/Goal1166/Goal1177/Goal1184 are follow-up engineering and clean-source batch evidence, not new public wording. Goal1177 and Goal1184 robot evidence is timing-only. |
| `barnes_hut_force_app` | `rt_core_ready` | `rt_core_ready` | Use `node_coverage_prepared` as the only RT-core Barnes-Hut claim path. Native C++ candidate-summary continuation is allowed as an app postprocess improvement, but uncovered-ID witnesses, opening-rule evaluation, force-vector reduction, and N-body simulation remain outside the RT-core claim. | Goal1146 reviewed narrow public wording for the prepared node-coverage query sub-path only. |
| `hiprt_ray_triangle_hitcount` | `not_nvidia_rt_core_target` | `not_nvidia_rt_core_target` | Keep as HIPRT-specific validation; do not fold into NVIDIA OptiX app maturity. | Never include in NVIDIA OptiX cloud batches. |
