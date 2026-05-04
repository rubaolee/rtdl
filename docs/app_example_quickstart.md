# RTDL App And Example Quickstart

This page is the short public route into RTDL apps and examples. Use it when
you want to run something quickly and understand what it proves without reading
the full catalog first.

## First Three Commands

Run these from the repo root:

```bash
PYTHONPATH=src:. python examples/rtdl_hello_world.py
PYTHONPATH=src:. python examples/rtdl_hello_world_backends.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/rtdl_hausdorff_distance_app.py --backend cpu_python_reference
```

What this shows:

- the checkout imports and runs
- a single RTDL kernel can be executed through a selected backend surface
- RTDL rows can be used inside a Python app

What this does not show:

- NVIDIA RT-core speedup
- whole-app acceleration
- full backend maturity

## Choose An App

| If you want to see... | Run first | What RTDL accelerates or models | Do not claim |
| --- | --- | --- | --- |
| First working command | `examples/rtdl_hello_world.py` | package/import smoke path | performance |
| Backend selection | `examples/rtdl_hello_world_backends.py` | same app idea through selected backend runners | backend speedup |
| Geometry/spatial joins | `examples/rtdl_segment_polygon_hitcount.py` | segment/polygon candidate traversal and refinement | full GIS engine |
| Spatial coverage app | `examples/rtdl_service_coverage_gaps.py` | fixed-radius household/clinic join | full service optimization |
| Hotspot app | `examples/rtdl_event_hotspot_screening.py` | fixed-radius event neighbor counts | full analytics pipeline |
| Facility coverage decision | `examples/rtdl_facility_knn_assignment.py` | KNN rows or prepared coverage-threshold decision | ranked assignment speedup |
| Hausdorff app | `examples/rtdl_hausdorff_distance_app.py` | KNN rows or prepared threshold-decision traversal | exact-distance RTX speedup unless reviewed mode is used |
| ANN candidate app | `examples/rtdl_ann_candidate_app.py` | KNN over a Python-selected candidate subset | full ANN index/ranking speedup |
| Outlier app | `examples/rtdl_outlier_detection_app.py` | fixed-radius density rows or scalar density count | production anomaly system |
| DBSCAN app | `examples/rtdl_dbscan_clustering_app.py` | fixed-radius core-count/core-flag phases | full cluster expansion speedup |
| Robot screening app | `examples/rtdl_robot_collision_screening_app.py` | ray/triangle any-hit pose flags/counts | whole robot-planning speedup |
| Barnes-Hut app | `examples/rtdl_barnes_hut_force_app.py` | node-candidate discovery or node-coverage decision | force-vector/opening-rule speedup |
| DB analytics app | `examples/rtdl_database_analytics_app.py` | bounded DB-style compact summaries | SQL engine or DBMS behavior |
| Graph analytics app | `examples/rtdl_graph_analytics_app.py` | bounded graph rows and native summaries | graph database/distributed analytics |

For the full inventory, read [Application Catalog](application_catalog.md) and
[v1.0 App Acceleration Inventory](v1_0_app_acceleration_inventory.md).

## Choose An Example Type

| Example type | Start here | Why |
| --- | --- | --- |
| Tutorial examples | [Quick Tutorial](quick_tutorial.md) | shortest path to the kernel shape |
| Feature recipes | `examples/rtdl_feature_quickstart_cookbook.py` | one runnable recipe per feature |
| Release-facing examples | [Release-Facing Examples](release_facing_examples.md) | canonical command list and setup notes |
| All examples | [Examples Index](../examples/README.md) | full directory inventory |
| App boundaries | [v1.0 App Acceleration Inventory](v1_0_app_acceleration_inventory.md) | what RTDL accelerates and what remains outside |
| RTX wording | [v1.0 RTX App Status](v1_0_rtx_app_status.md) | public NVIDIA wording state |

## RTX Rule For App Runs

Use this rule before publishing any performance wording:

```text
--backend optix is not a public NVIDIA RT-core speedup claim.
--require-rt-core only authorizes claim-sensitive runs when the selected
mode is documented and reviewed.
```

If an app returns full rows, Python labels, force vectors, ranked assignments,
or cluster labels, that output may include Python-owned continuation work. Only claim the exact prepared/native sub-path that the support matrix and review reports authorize.

## Recommended v1.0 Demo Path

For a short v1.0 demonstration sequence:

1. Run `examples/rtdl_hello_world.py`.
2. Run `examples/rtdl_feature_quickstart_cookbook.py`.
3. Run one app from the table above on `cpu_python_reference`.
4. If Embree is available, rerun the same app with `--backend embree`.
5. Read [Performance Model](performance_model.md) before interpreting timing.
6. Read [App Engine Support Matrix](app_engine_support_matrix.md) before using
   `--backend optix` or `--require-rt-core`.

This sequence demonstrates the v1.0 promise: RTDL can express real app-shaped RT workloads from Python, while the docs keep performance and claim boundaries explicit.
