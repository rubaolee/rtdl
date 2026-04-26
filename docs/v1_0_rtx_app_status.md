# v1.0 RTX App Status

Date: 2026-04-25

This page is the public v1.0 RTX app status index. It lists bounded NVIDIA OptiX/RTX claim-review candidates and non-claim boundaries. It is not release authorization and not a public speedup claim.

## Summary

- public app rows: `18`
- NVIDIA-target rows ready for claim review: `16`
- non-NVIDIA target rows: `2`
- reviewed public RTX sub-path wording rows: `7`
- broad or whole-app public speedup claim authorized: `False`

Use this page as the release-facing source of truth for app-level RTX claim review. For engine-by-engine details, see `docs/app_engine_support_matrix.md`.

## Goal1009 Reviewed Public RTX Sub-Path Wording

The following rows have passed the Goal1009 wording review for bounded prepared
RTX A5000 query/native sub-path wording. These are not whole-app, default-mode,
Python-postprocess, or broad RT-core acceleration claims:

| App/path | RTX phase (s) | Ratio | Scope |
| --- | ---: | ---: | --- |
| `service_coverage_gaps / prepared_gap_summary` | `0.136545` | `1.61x` | prepared gap-summary query/native sub-path only |
| `outlier_detection / prepared_fixed_radius_density_summary` | `0.122348` | `4.64x` | prepared fixed-radius scalar threshold-count sub-path only |
| `dbscan_clustering / prepared_fixed_radius_core_flags` | `0.122921` | `6.62x` | prepared fixed-radius scalar core-count sub-path only |
| `facility_knn_assignment / coverage_threshold_prepared` | `0.157368` | `22.81x` | prepared service-coverage decision sub-path only |
| `segment_polygon_hitcount / segment_polygon_hitcount_native_experimental` | `0.146860` | `1.71x` | prepared native segment/polygon hit-count traversal only |
| `segment_polygon_anyhit_rows / segment_polygon_anyhit_rows_prepared_bounded_gate` | `0.192639` | `3.03x` | prepared bounded native pair-row traversal only |
| `ann_candidate_search / candidate_threshold_prepared` | `0.105215` | `4.86x` | prepared ANN candidate-coverage decision sub-path only |

`robot_collision_screening / prepared_pose_flags` remains excluded from public
RTX speedup wording because its larger RTX repeats stayed below the 100 ms
public-review timing floor. Other `ready_for_rtx_claim_review` rows remain
engineering-ready or claim-review-ready, but do not yet have Goal1009 public
speedup wording.

## Status Table

| App | Status | RT-core subpath | Native-continuation contract | Claim command | Evidence | What is not claimed | Cloud action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `examples/rtdl_database_analytics_app.py` | `rt_core_ready` / `ready_for_rtx_claim_review` | prepared DB compact-summary traversal/filter/grouping | native continuation only for materialization-free compact DB summaries | `PYTHONPATH=src:. python examples/rtdl_database_analytics_app.py --backend optix --output-mode compact_summary --require-rt-core` | Goal921/Goal941 | DB claims must stay limited to compact-summary prepared sub-paths; no SQL engine, DBMS, full dashboard, row-materializing, or broad whole-app speedup claim is allowed | no readiness pod needed; rerun only in a consolidated regression/tuning batch |
| `examples/rtdl_graph_analytics_app.py` | `rt_core_ready` / `ready_for_rtx_claim_review` | bounded visibility any-hit plus native graph-ray BFS/triangle candidate generation | top-level metadata aggregates selected native graph sections; visibility_edges uses optix_visibility_pair_rows on OptiX | `PYTHONPATH=src:. python examples/rtdl_graph_analytics_app.py --backend optix --scenario visibility_edges --require-rt-core` | Goal889/Goal905/Goal929 | Goal929 covers bounded graph RT sub-paths only; CPU-side frontier bookkeeping, triangle set-intersection, shortest-path, graph database, distributed analytics, and whole-app graph-system acceleration remain outside the claim | no readiness pod needed; rerun only in a consolidated regression/tuning batch |
| `examples/rtdl_apple_rt_demo_app.py` | `not_nvidia_rt_core_target` / `exclude_from_rtx_app_benchmark` | Apple Metal/MPS RT demo, outside NVIDIA RTX table | outside NVIDIA RTX app table | `not a NVIDIA RTX target` | none | OptiX is not an applicable app entry point | never include in NVIDIA RTX cloud batch |
| `examples/rtdl_service_coverage_gaps.py` | `rt_core_ready` / `ready_for_rtx_claim_review` | prepared fixed-radius gap-summary traversal | native continuation only for Embree gap_summary or OptiX gap_summary_prepared threshold-count paths | `PYTHONPATH=src:. python examples/rtdl_service_coverage_gaps.py --backend optix --optix-summary-mode gap_summary_prepared --require-rt-core` | Goal917 | Goal917 covers the bounded prepared gap-summary path only; row output, nearest-clinic output, and whole-app service-coverage optimization remain outside the claim | no readiness pod needed; rerun only in a consolidated regression/tuning batch |
| `examples/rtdl_event_hotspot_screening.py` | `rt_core_ready` / `ready_for_rtx_claim_review` | prepared fixed-radius count-summary traversal | native continuation only for Embree count_summary or OptiX count_summary_prepared threshold-count paths | `PYTHONPATH=src:. python examples/rtdl_event_hotspot_screening.py --backend optix --optix-summary-mode count_summary_prepared --require-rt-core` | Goal917/Goal919 | Goal917 and Goal919 cover the bounded prepared count-summary path only; neighbor-row output and whole-app hotspot analytics remain outside the claim | no readiness pod needed; rerun only in a consolidated regression/tuning batch |
| `examples/rtdl_facility_knn_assignment.py` | `rt_core_ready` / `ready_for_rtx_claim_review` | prepared fixed-radius service-coverage decision | native continuation only for OptiX coverage_threshold_prepared service-coverage decisions | `PYTHONPATH=src:. python examples/rtdl_facility_knn_assignment.py --backend optix --optix-summary-mode coverage_threshold_prepared --require-rt-core` | Goal887/Goal920 | ranked nearest-depot assignment remains outside the OptiX claim; only the service-coverage decision sub-path is traversal-backed | no readiness pod needed; rerun only in a consolidated regression/tuning batch |
| `examples/rtdl_road_hazard_screening.py` | `rt_core_ready` / `ready_for_rtx_claim_review` | prepared native segment/polygon road-hazard summary traversal | app native OptiX hit-count mode is metadata-gated; accepted claim surface remains prepared road-hazard summary traversal | `PYTHONPATH=src:. python examples/rtdl_road_hazard_screening.py --backend optix --output-mode summary --optix-mode native --require-rt-core` | Goal933/Goal941 | claim is limited to the prepared compact road-hazard summary gate; default public app behavior, full GIS/routing, and broad road-hazard speedup remain outside the claim | no readiness pod needed; rerun only in a consolidated regression/tuning batch |
| `examples/rtdl_segment_polygon_hitcount.py` | `rt_core_ready` / `ready_for_rtx_claim_review` | prepared native segment/polygon hit-count traversal | app native OptiX hit-count mode is metadata-gated; accepted claim surface remains prepared hit-count traversal | `PYTHONPATH=src:. python scripts/goal933_prepared_segment_polygon_optix_profiler.py --backend optix --scenario segment_polygon_hitcount_prepared` | Goal933/Goal941 | claim is limited to prepared compact hit-count traversal; pair-row output, road-hazard whole-app behavior, and broad speedup remain outside the claim | no readiness pod needed; rerun only in a consolidated regression/tuning batch |
| `examples/rtdl_segment_polygon_anyhit_rows.py` | `rt_core_ready` / `ready_for_rtx_claim_review` | prepared bounded native pair-row traversal | native continuation is RT-core accelerated only for explicit bounded OptiX native rows mode | `PYTHONPATH=src:. python scripts/goal934_prepared_segment_polygon_pair_rows_optix_profiler.py --backend optix --scenario segment_polygon_anyhit_rows_prepared_bounded` | Goal934/Goal941 | claim is limited to bounded prepared pair-row traversal at the reviewed output capacity; unbounded row-volume performance and default public app behavior remain outside the claim | no readiness pod needed; rerun only in a consolidated regression/tuning batch |
| `examples/rtdl_polygon_pair_overlap_area_rows.py` | `rt_core_ready` / `ready_for_rtx_claim_review` | native-assisted LSI/PIP candidate discovery | native C++ exact area continuation follows RT-assisted LSI/PIP candidate discovery | `PYTHONPATH=src:. python examples/rtdl_polygon_pair_overlap_area_rows.py --backend optix --require-rt-core` | Goal877/Goal929 | exact area refinement remains CPU/Python-owned; only candidate discovery may enter claim review | no readiness pod needed; rerun only in a consolidated regression/tuning batch |
| `examples/rtdl_polygon_set_jaccard.py` | `rt_core_ready` / `ready_for_rtx_claim_review` | native-assisted LSI/PIP candidate discovery | native C++ exact set-area continuation follows RT-assisted LSI/PIP candidate discovery | `PYTHONPATH=src:. python examples/rtdl_polygon_set_jaccard.py --backend optix --require-rt-core` | Goal877/Goal929 | exact set-area/Jaccard refinement remains CPU/Python-owned, and larger chunk sizes are diagnostic failures until root-caused | no readiness pod needed; rerun only in a consolidated regression/tuning batch |
| `examples/rtdl_hausdorff_distance_app.py` | `rt_core_ready` / `ready_for_rtx_claim_review` | prepared fixed-radius Hausdorff threshold decision | native continuation only for Embree directed_summary or OptiX directed_threshold_prepared decision paths | `PYTHONPATH=src:. python examples/rtdl_hausdorff_distance_app.py --backend optix --optix-summary-mode directed_threshold_prepared --require-rt-core` | Goal887/Goal941 | exact Hausdorff distance, KNN-row output, nearest-neighbor ranking, and whole-app speedup remain outside the claim | no readiness pod needed; rerun only in a consolidated regression/tuning batch |
| `examples/rtdl_ann_candidate_app.py` | `rt_core_ready` / `ready_for_rtx_claim_review` | prepared fixed-radius ANN candidate-coverage decision | native C++ rerank summaries follow candidate KNN rows; OptiX prepared threshold path covers candidate-coverage decision only | `PYTHONPATH=src:. python examples/rtdl_ann_candidate_app.py --backend optix --optix-summary-mode candidate_threshold_prepared --require-rt-core` | Goal887/Goal941 | full ANN indexing, nearest-neighbor ranking, FAISS/HNSW/IVF/PQ behavior, recall optimization, and whole-app speedup remain outside the claim | no readiness pod needed; rerun only in a consolidated regression/tuning batch |
| `examples/rtdl_outlier_detection_app.py` | `rt_core_ready` / `ready_for_rtx_claim_review` | prepared fixed-radius scalar threshold-count traversal | native continuation only for OptiX density_count scalar path or Embree/OptiX per-point threshold summary paths | `PYTHONPATH=src:. python examples/rtdl_outlier_detection_app.py --backend optix --optix-summary-mode rt_count_threshold_prepared --output-mode density_count` | Goal795/Goal992 | RTX 4090 evidence covers the prepared scalar threshold-count sub-path only; full anomaly-detection app, per-point outlier labels, and row-returning paths remain outside the claim | no readiness pod needed; rerun only in a consolidated regression/tuning batch |
| `examples/rtdl_dbscan_clustering_app.py` | `rt_core_ready` / `ready_for_rtx_claim_review` | prepared fixed-radius scalar core-count traversal | native continuation only for OptiX core_count scalar path or Embree/OptiX per-point core-flag summary paths, not full cluster expansion | `PYTHONPATH=src:. python examples/rtdl_dbscan_clustering_app.py --backend optix --optix-summary-mode rt_core_flags_prepared --output-mode core_count` | Goal795/Goal992 | RTX 4090 evidence covers the prepared scalar core-count sub-path only; per-point core flags and Python cluster expansion remain outside the native scalar path | no readiness pod needed; rerun only in a consolidated regression/tuning batch |
| `examples/rtdl_robot_collision_screening_app.py` | `rt_core_ready` / `blocked_for_public_speedup_wording` | prepared ray/triangle any-hit scalar pose-count traversal | native continuation only for prepared OptiX count or pose-flag summaries | `PYTHONPATH=src:. python examples/rtdl_robot_collision_screening_app.py --backend optix --optix-summary-mode prepared_count` | Goal795/Goal1008 | RT-core path exists, but Goal1008 larger RTX repeats kept the median query phase below the 100 ms public-review timing floor; full robot kinematics and witness-row output remain outside the claim | no readiness pod needed; redesign/reprofile only if robot public speedup wording is important |
| `examples/rtdl_barnes_hut_force_app.py` | `rt_core_ready` / `ready_for_rtx_claim_review` | prepared fixed-radius Barnes-Hut node-coverage decision | native C++ candidate summaries follow candidate rows; OptiX prepared threshold path covers node-coverage decision only | `PYTHONPATH=src:. python examples/rtdl_barnes_hut_force_app.py --backend optix --optix-summary-mode node_coverage_prepared --require-rt-core` | Goal887/Goal941 | Barnes-Hut opening-rule evaluation, candidate-row output, force-vector reduction, N-body simulation, and whole-app speedup remain outside the claim | no readiness pod needed; rerun only in a consolidated regression/tuning batch |
| `examples/rtdl_hiprt_ray_triangle_hitcount.py` | `not_nvidia_rt_core_target` / `exclude_from_rtx_app_benchmark` | HIPRT-specific hit-count validation, outside NVIDIA RTX table | outside NVIDIA RTX app table | `not a NVIDIA RTX target` | none | public app CLI does not expose OptiX | never include in NVIDIA RTX cloud batch |

## Allowed Wording

RTDL includes a bounded NVIDIA OptiX/RTX-backed subpath for `<app>`: `<allowed claim>`. The claim covers that named traversal/summary phase only; excluded Python, validation, postprocess, exact refinement, ranking, row-materialization, or whole-app work remains outside the claim.

## Forbidden Wording

- RTDL accelerates the whole app.
- RTDL beats CPU, Embree, PostGIS, or another baseline for an app unless a later same-semantics review explicitly authorizes that specific wording.
- All graph, database, or spatial work is RT-core accelerated.
- Polygon area or Jaccard refinement is fully native OptiX.
- `--backend optix` alone means RT cores were used.

## Source Of Truth

- `apps`: `rtdsl.public_apps()`
- `engine_support`: `rtdsl.app_engine_support_matrix()`
- `readiness`: `rtdsl.optix_app_benchmark_readiness_matrix()`
- `maturity`: `rtdsl.rt_core_app_maturity_matrix()`
- `public_wording`: `rtdsl.rtx_public_wording_matrix()`
