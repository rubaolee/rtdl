# Examples

This directory is the runnable example inventory. If you are new, use the short
path first, then return here when you need a specific app or backend boundary.

Run source-tree examples from the repository root with `PYTHONPATH=src:.`.

## Short Path

| Step | Run or read | Purpose |
| --- | --- | --- |
| 1 | `PYTHONPATH=src:. python examples/rtdl_hello_world.py` | prove the checkout imports and runs |
| 2 | `PYTHONPATH=src:. python examples/rtdl_hello_world_backends.py --backend cpu_python_reference` | see backend selection without performance claims |
| 3 | `PYTHONPATH=src:. python examples/rtdl_feature_quickstart_cookbook.py` | see one compact recipe per public feature |
| 4 | [App And Example Quickstart](../docs/app_example_quickstart.md) | choose one app by job instead of scanning the directory |
| 5 | [Performance Model](../docs/performance_model.md) | interpret any timing or speedup wording safely |

The quick rule: examples show runnable RTDL shapes; public speedup wording comes only from the support matrix and reviewed evidence for an exact bounded sub-path.

## How To Read Examples In v1.8

Each public example is a Python application wrapped around an RTDL kernel:

| In the example | Meaning |
| --- | --- |
| app name, JSON fields, labels, command flags | Python-owned application surface |
| `@rt.kernel(backend="rtdl")` | RTDL language contract |
| `rt.input -> rt.traverse -> rt.refine -> rt.emit` | RTDL-owned kernel shape |
| `--backend cpu_python_reference`, `embree`, `optix` | runtime engine selection |

Do not infer that an app name in `examples/` means the native engine has an
app-customized implementation. The v1.8 release-prep boundary keeps app logic
in Python and keeps native runtime symbols generic.

## Directory Contents

This directory contains:

- current public examples you can run first
- visual demos that show RTDL inside Python applications
- reference kernels and helper generators used by examples and tests
- preserved generated bundles and internal artifacts for auditability

For history, old release boundaries, and evidence trails, use
[History Index](../docs/history/README.md), [Release Reports](../docs/release_reports/),
and [Benchmark And Audit Reports](../docs/reports/).

## Start Here

For a shorter user-facing route through the app demos, read
[`docs/app_example_quickstart.md`](../docs/app_example_quickstart.md). This
directory index is the compact inventory; the quickstart is the cleaner first
path.

| If you want to see... | Start with | What data becomes |
| --- | --- | --- |
| the smallest runnable program | `rtdl_hello_world.py` | one script becomes a known output |
| one kernel across backends | `rtdl_hello_world_backends.py` | one query becomes backend-comparable rows |
| one recipe for every feature | `rtdl_feature_quickstart_cookbook.py` | each feature input becomes expected output rows |
| nearest-neighbor search | `rtdl_fixed_radius_neighbors.py` | points/queries become neighbor rows |
| KNN rows | `rtdl_knn_rows.py` | query points become ranked neighbor rows |
| app-level Hausdorff distance | `rtdl_hausdorff_distance_app.py` | two point sets become directed nearest-neighbor rows and one distance |
| continuous Frechet distance learner app | `rtdl_continuous_frechet_distance_app.py` | two polylines become a distance estimate and optional threshold decision |
| app-level ANN candidate search | `rtdl_ann_candidate_app.py` | queries plus a Python-selected candidate subset become approximate nearest rows |
| app-level outlier detection | `rtdl_outlier_detection_app.py` | points become fixed-radius neighbor rows and outlier labels |
| app-level DBSCAN clustering | `rtdl_dbscan_clustering_app.py` | points become fixed-radius neighbor rows and density-cluster labels |
| app-level robot collision screening | `rtdl_robot_collision_screening_app.py` | link edge rays become any-hit rows and reduced pose collision flags |
| bounded any-hit ray queries | `rtdl_ray_triangle_any_hit.py` | rays and triangles become per-ray `any_hit` rows |
| visibility / line-of-sight rows | `rtdl_visibility_rows.py` | observers, targets, and blockers become visibility rows |
| emitted-row reductions | `rtdl_reduce_rows.py` | emitted rows become grouped app summary rows |
| app-level Barnes-Hut force approximation | `rtdl_barnes_hut_force_app.py` | bodies and quadtree nodes become force-candidate rows |
| graph traversal | `rtdl_graph_bfs.py` | frontier vertices become discovered vertices |
| graph intersection | `rtdl_graph_triangle_count.py` | graph edges become triangle rows |
| unified graph app | `rtdl_graph_analytics_app.py` | graph inputs become BFS discovery rows and triangle rows |
| DB-style filtering | `rtdl_db_conjunctive_scan.py` | rows plus predicates become matching row IDs |
| DB-style aggregation | `rtdl_db_grouped_count.py` / `rtdl_db_grouped_sum.py` | rows plus predicates become grouped aggregates |
| unified database app | `rtdl_database_analytics_app.py` | order rows become regional dashboard rows and sales-risk summaries |
| road/polygon screening | `rtdl_road_hazard_screening.py` | road segments plus hazard polygons become per-road hit counts |
| spatial join apps | `rtdl_service_coverage_gaps.py`, `rtdl_event_hotspot_screening.py`, `rtdl_facility_knn_assignment.py` | locations become coverage gaps, event hotspots, or nearest facility assignments |
| HIPRT example | `rtdl_hiprt_ray_triangle_hitcount.py` | 3D rays and 3D triangles become per-ray hit-count rows |
| unified Apple RT demo | `rtdl_apple_rt_demo_app.py` | Apple closest-hit and visibility-count scenarios become one app JSON result |
| visual lit ball | `visual_demo/rtdl_lit_ball_demo.py` | camera rays and sphere triangles become a shaded text/image demo |
| hidden-star visual demo | `visual_demo/rtdl_hidden_star_stable_ball_demo.py` | primary rays and shadow rays become a Python-rendered frame sequence |
| chunked hidden-star video | `visual_demo/render_hidden_star_chunked_video.py` | repeated visual-demo frames become a streamed video artifact |

## Public Example Files

- `rtdl_hello_world.py`
- `rtdl_hello_world_backends.py`
- `rtdl_feature_quickstart_cookbook.py`
- `rtdl_fixed_radius_neighbors.py`
- `rtdl_knn_rows.py`
- `rtdl_hausdorff_distance_app.py`
- `rtdl_continuous_frechet_distance_app.py`
- `rtdl_ann_candidate_app.py`
- `rtdl_outlier_detection_app.py`
- `rtdl_dbscan_clustering_app.py`
- `rtdl_robot_collision_screening_app.py`
- `rtdl_ray_triangle_any_hit.py`
- `rtdl_visibility_rows.py`
- `rtdl_reduce_rows.py`
- `rtdl_barnes_hut_force_app.py`
- `rtdl_graph_bfs.py`
- `rtdl_graph_triangle_count.py`
- `rtdl_graph_analytics_app.py`
- `rtdl_db_conjunctive_scan.py`
- `rtdl_db_grouped_count.py`
- `rtdl_db_grouped_sum.py`
- `rtdl_database_analytics_app.py`
- `rtdl_hiprt_ray_triangle_hitcount.py`
- `rtdl_apple_rt_demo_app.py`
- `rtdl_service_coverage_gaps.py`
- `rtdl_event_hotspot_screening.py`
- `rtdl_facility_knn_assignment.py`
- `rtdl_segment_polygon_hitcount.py`
- `rtdl_segment_polygon_anyhit_rows.py`
- `rtdl_polygon_pair_overlap_area_rows.py`
- `rtdl_polygon_set_jaccard.py`
- `rtdl_road_hazard_screening.py`
- `visual_demo/rtdl_lit_ball_demo.py`
- `visual_demo/rtdl_hidden_star_stable_ball_demo.py`
- `visual_demo/render_hidden_star_chunked_video.py`

## Learning Boundaries

- Start with `cpu_python_reference`; it is the portable learning backend.
- Use `cpu` when you intentionally want the native/oracle validation path.
- Use Embree, OptiX, HIPRT, Vulkan, or Apple RT only when the host has the
  needed dependencies and the selected feature supports that backend.
- `--backend optix` is not by itself a public NVIDIA RT-core speedup claim.
- `rt.reduce_rows(...)` is a deterministic helper over emitted rows unless a
  specific backend summary contract says otherwise.
- Visual demos are Python applications that use RTDL for geometric queries;
  RTDL is not a renderer or graphics engine.

## Reference, Generated, And Internal Material

Files under `reference/` contain canonical kernels and helper generators used
by examples, tests, and bounded evaluation paths.

Files under `generated/` are preserved generated output artifacts. They are
useful for inspection and handoff workflows, but they are not the primary
release-facing start points for new users.

Files under `internal/` are preserved for development history, evaluation, or
LLM-authoring experiments. They are not the primary release-facing entry points
for external users.

For guided learning and support boundaries, prefer:

- [Project Front Page](../README.md)
- [Docs Index](../docs/README.md)
- [Quick Tutorial](../docs/quick_tutorial.md)
- [Tutorial Ladder](../docs/tutorials/README.md)
- [App And Example Quickstart](../docs/app_example_quickstart.md)
- [Application Catalog](../docs/application_catalog.md)
- [App Engine Support Matrix](../docs/app_engine_support_matrix.md)
- [Performance Model](../docs/performance_model.md)
