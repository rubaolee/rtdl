# Goal939 Current RTX Claim-Review Package

Date: 2026-04-25

This package is a current claim-review index. It does not run benchmarks, does not start cloud resources, does not promote held apps, and does not authorize public speedup claims.

## Summary

- ready claim-review rows: `16`
- reviewed public wording rows: `7`
- blocked public wording rows: `1`
- held or out-of-target rows: `2`
- source of truth: `rtdsl.optix_app_benchmark_readiness_matrix()` plus `rtdsl.rt_core_app_maturity_matrix()` plus `rtdsl.rtx_public_wording_matrix()`

## Ready Rows

| App | Performance class | Public wording status | Native-continuation required | Evidence/goals | Allowed claim | Non-claim boundary |
| --- | --- | --- | --- | --- | --- | --- |
| `database_analytics` | `python_interface_dominated` | `public_wording_not_reviewed` | `True` | Goal921/Goal941 | prepared DB compact-summary traversal/filter/grouping sub-path may enter claim review; no DBMS or SQL-engine speedup claim | DB claims must stay limited to compact-summary prepared sub-paths; no SQL engine, DBMS, full dashboard, row-materializing, or broad whole-app speedup claim is allowed |
| `graph_analytics` | `optix_traversal` | `public_wording_not_reviewed` | `True` | Goal889/Goal905/Goal929 | bounded graph visibility any-hit plus native BFS/triangle graph-ray candidate-generation sub-paths may enter claim review; no whole-app graph speedup claim | Goal929 covers bounded graph RT sub-paths only; CPU-side frontier bookkeeping, triangle set-intersection, shortest-path, graph database, distributed analytics, and whole-app graph-system acceleration remain outside the claim |
| `service_coverage_gaps` | `optix_traversal_prepared_summary` | `public_wording_reviewed` | `True` | Goal917 | bounded prepared gap-summary path may enter claim review; no whole-app service-coverage speedup claim | Goal917 covers the bounded prepared gap-summary path only; row output, nearest-clinic output, and whole-app service-coverage optimization remain outside the claim |
| `event_hotspot_screening` | `optix_traversal_prepared_summary` | `public_wording_not_reviewed` | `True` | Goal917/Goal919 | bounded prepared count-summary path may enter claim review; no whole-app hotspot-screening speedup claim | Goal917 and Goal919 cover the bounded prepared count-summary path only; neighbor-row output and whole-app hotspot analytics remain outside the claim |
| `facility_knn_assignment` | `optix_traversal_prepared_summary` | `public_wording_reviewed` | `True` | Goal887/Goal920 | bounded prepared facility service-coverage decision sub-path may enter claim review; no KNN assignment or ranking speedup claim | ranked nearest-depot assignment remains outside the OptiX claim; only the service-coverage decision sub-path is traversal-backed |
| `road_hazard_screening` | `optix_traversal_prepared_summary` | `public_wording_not_reviewed` | `True` | Goal933/Goal941 | prepared native road-hazard summary traversal sub-path may enter claim review; no full GIS/routing or default-app speedup claim | claim is limited to the prepared compact road-hazard summary gate; default public app behavior, full GIS/routing, and broad road-hazard speedup remain outside the claim |
| `segment_polygon_hitcount` | `optix_traversal_prepared_summary` | `public_wording_reviewed` | `True` | Goal933/Goal941 | prepared native segment/polygon hit-count traversal sub-path may enter claim review; no broad segment/polygon app speedup claim | claim is limited to prepared compact hit-count traversal; pair-row output, road-hazard whole-app behavior, and broad speedup remain outside the claim |
| `segment_polygon_anyhit_rows` | `optix_traversal` | `public_wording_reviewed` | `True` | Goal934/Goal941 | prepared bounded native pair-row traversal sub-path may enter claim review; no unbounded pair-row or broad app speedup claim | claim is limited to bounded prepared pair-row traversal at the reviewed output capacity; unbounded row-volume performance and default public app behavior remain outside the claim |
| `polygon_pair_overlap_area_rows` | `python_interface_dominated` | `public_wording_not_reviewed` | `True` | Goal877/Goal929 | native-assisted candidate-discovery path only; no full polygon-area speedup claim | exact area refinement remains CPU/Python-owned; only candidate discovery may enter claim review |
| `polygon_set_jaccard` | `python_interface_dominated` | `public_wording_not_reviewed` | `True` | Goal877/Goal929 | native-assisted candidate-discovery path only; no full Jaccard speedup claim | exact set-area/Jaccard refinement remains CPU/Python-owned, and larger chunk sizes are diagnostic failures until root-caused |
| `hausdorff_distance` | `optix_traversal_prepared_summary` | `public_wording_not_reviewed` | `True` | Goal887/Goal941 | prepared Hausdorff <= radius decision sub-path may enter claim review; no exact-distance speedup claim | exact Hausdorff distance, KNN-row output, nearest-neighbor ranking, and whole-app speedup remain outside the claim |
| `ann_candidate_search` | `optix_traversal_prepared_summary` | `public_wording_reviewed` | `True` | Goal887/Goal941 | prepared ANN candidate-coverage decision sub-path may enter claim review; no full ANN index or ranking speedup claim | full ANN indexing, nearest-neighbor ranking, FAISS/HNSW/IVF/PQ behavior, recall optimization, and whole-app speedup remain outside the claim |
| `outlier_detection` | `optix_traversal_prepared_summary` | `public_wording_reviewed` | `True` | Goal795/Goal992 | prepared fixed-radius scalar threshold-count sub-path may enter claim review; no per-point outlier-label or broad outlier-app speedup claim | RTX 4090 evidence covers the prepared scalar threshold-count sub-path only; full anomaly-detection app, per-point outlier labels, and row-returning paths remain outside the claim |
| `dbscan_clustering` | `optix_traversal_prepared_summary` | `public_wording_reviewed` | `True` | Goal795/Goal992 | prepared fixed-radius scalar core-count sub-path may enter claim review; no per-point core-flag or full DBSCAN clustering acceleration claim | RTX 4090 evidence covers the prepared scalar core-count sub-path only; per-point core flags and Python cluster expansion remain outside the native scalar path |
| `robot_collision_screening` | `optix_traversal` | `public_wording_blocked` | `True` | Goal795 | prepared ray/triangle any-hit scalar pose-count sub-path may enter claim review; no full robot-planning speedup claim | RTX 4090 evidence covers prepared scalar pose-count traversal only; full robot kinematics and witness-row output remain outside the claim |
| `barnes_hut_force_app` | `optix_traversal_prepared_summary` | `public_wording_not_reviewed` | `True` | Goal887/Goal941 | prepared Barnes-Hut node-coverage decision sub-path may enter claim review; no force-vector or opening-rule speedup claim | Barnes-Hut opening-rule evaluation, candidate-row output, force-vector reduction, N-body simulation, and whole-app speedup remain outside the claim |

## Held Rows

| App | Readiness | RT-core status | Boundary |
| --- | --- | --- | --- |
| `apple_rt_demo` | `exclude_from_rtx_app_benchmark` | `not_nvidia_rt_core_target` | OptiX is not an applicable app entry point |
| `hiprt_ray_triangle_hitcount` | `exclude_from_rtx_app_benchmark` | `not_nvidia_rt_core_target` | public app CLI does not expose OptiX |

## Public Wording Pattern

Every ready app must expose native_continuation_active and native_continuation_backend in the relevant app payloads. These fields describe the native traversal/summary continuation and do not by themselves authorize a speedup claim.

Only rows with `public_wording_reviewed` may use a reviewed public speedup wording. Rows with `public_wording_blocked` or `public_wording_not_reviewed` remain technical claim-review rows only.

RTDL includes a bounded NVIDIA OptiX/RTX-backed sub-path for <app>: <allowed_claim>. The claim covers that native traversal/summary phase only; excluded work remains outside the claim.

Forbidden wording:

- RTDL accelerates the whole app
- RTDL beats CPU/PostGIS/Embree
- All graph/database/spatial work is RT-core accelerated
- Polygon area/Jaccard is fully native OptiX

## Boundary

This package is an index for review. It is not release authorization and not a benchmark result.

