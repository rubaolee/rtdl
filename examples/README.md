# RTDL Examples

This directory is the runnable v2.0-facing example inventory. It is organized
for a new reader first: start with the short path, then pick an app by workload.

Run source-tree examples from the repository root with `PYTHONPATH=src:.`.

## Short Path

| Step | Run or read | Purpose |
| --- | --- | --- |
| 1 | `PYTHONPATH=src:. python examples/rtdl_hello_world.py` | prove the checkout imports and runs |
| 2 | `PYTHONPATH=src:. python examples/rtdl_hello_world_backends.py --backend cpu_python_reference` | see backend selection without performance claims |
| 3 | `PYTHONPATH=src:. python examples/rtdl_partner_anyhit.py --partner numpy --backend embree` | see Python+partner column handoff on the CPU RT fallback |
| 4 | `PYTHONPATH=src:. python examples/rtdl_feature_quickstart_cookbook.py` | see one compact recipe per public feature |
| 5 | [App And Example Quickstart](../docs/app_example_quickstart.md) | choose one app by job instead of scanning filenames |
| 6 | [Performance Model](../docs/performance_model.md) | interpret timing and speedup wording safely |

Quick rule: examples show runnable RTDL shapes. Public speedup wording comes
only from the support matrix and reviewed evidence for an exact bounded path.

## Directory Map

| Location | Reader meaning |
| --- | --- |
| root `rtdl_*.py` files | current public examples and app wrappers |
| `visual_demo/` | visual Python apps that use RTDL for geometric query work |
| `reference/` | canonical kernels and helper generators used by tests and docs |
| `generated/` | preserved generated bundles for inspection and audit |
| `internal/` | internal experiments, compatibility helpers, and archived app helpers |

If a file is under `internal/`, it is not a first-run learner entry point.

## Public Examples By Job

### First Runs

| Job | Start with |
| --- | --- |
| smallest runnable program | `rtdl_hello_world.py` |
| one idea across runtime backends | `rtdl_hello_world_backends.py` |
| one recipe per feature | `rtdl_feature_quickstart_cookbook.py` |
| Python+partner column handoff | `rtdl_partner_anyhit.py` |

### Core Primitive Shapes

| Job | Start with |
| --- | --- |
| ray/triangle any-hit | `rtdl_ray_triangle_any_hit.py` |
| visibility rows | `rtdl_visibility_rows.py` |
| row reductions | `rtdl_reduce_rows.py` |
| fixed-radius neighbors | `rtdl_fixed_radius_neighbors.py` |
| KNN rows | `rtdl_knn_rows.py` |
| HIPRT hit-count proof path | `rtdl_hiprt_ray_triangle_hitcount.py` |

### Application Examples

| Job | Start with |
| --- | --- |
| Hausdorff-style nearest-neighbor composition | `rtdl_hausdorff_distance_app.py` |
| user-owned native continuation example | `rtdl_hausdorff_user_cpp_continuation.py` |
| continuous Frechet learner app | `rtdl_continuous_frechet_distance_app.py` |
| approximate nearest-neighbor candidate search | `rtdl_ann_candidate_app.py` |
| outlier screening | `rtdl_outlier_detection_app.py` |
| DBSCAN-style density clustering | `rtdl_dbscan_clustering_app.py` |
| robot collision screening | `rtdl_robot_collision_screening_app.py` |
| Barnes-Hut force candidate discovery | `rtdl_barnes_hut_force_app.py` |
| graph analytics wrapper | `rtdl_graph_analytics_app.py` |
| database analytics wrapper | `rtdl_database_analytics_app.py` |
| Apple RT wrapper | `rtdl_apple_rt_demo_app.py` |

### Spatial And Polygon Workloads

| Job | Start with |
| --- | --- |
| service coverage gaps | `rtdl_service_coverage_gaps.py` |
| event hotspot screening | `rtdl_event_hotspot_screening.py` |
| facility assignment | `rtdl_facility_knn_assignment.py` |
| road hazard screening | `rtdl_road_hazard_screening.py` |
| segment/polygon hit counts | `rtdl_segment_polygon_hitcount.py` |
| segment/polygon witness rows | `rtdl_segment_polygon_anyhit_rows.py` |
| polygon-pair overlap summaries | `rtdl_polygon_pair_overlap_area_rows.py` |
| polygon-set Jaccard summaries | `rtdl_polygon_set_jaccard.py` |

### Partner Continuation Examples

| Job | Start with |
| --- | --- |
| CuPy RawKernel continuation examples | `rtdl_control_apps_cupy_rawkernel.py` |

This file is intentionally a current example, but it is an advanced one. It
shows user-owned partner continuation around RTDL; it is not a claim that RTDL
accelerates arbitrary CuPy programs.

## Backend And Claim Boundaries

- Start with `cpu_python_reference`; it is the portable learning backend.
- Use `cpu` when you intentionally want the native/oracle validation path.
- Use Embree, OptiX, HIPRT, Vulkan, or Apple RT only when the host has the
  needed dependencies and the selected feature supports that backend.
- `--backend optix` is not by itself a public NVIDIA RT-core speedup claim.
- Visual demos are Python applications that use RTDL for geometric queries;
  RTDL is not a renderer or graphics engine.

For guided learning and support boundaries, prefer:

- [Project Front Page](../README.md)
- [Docs Index](../docs/README.md)
- [Quick Tutorial](../docs/quick_tutorial.md)
- [Tutorial Ladder](../docs/tutorials/README.md)
- [App And Example Quickstart](../docs/app_example_quickstart.md)
- [Application Catalog](../docs/application_catalog.md)
- [App Engine Support Matrix](../docs/app_engine_support_matrix.md)
- [Current Support Matrix](../docs/current_main_support_matrix.md)
- [Performance Model](../docs/performance_model.md)
