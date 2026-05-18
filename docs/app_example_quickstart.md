# RTDL App And Example Quickstart

This page is the short public route into RTDL apps and examples. Use it when
you want to run something quickly and understand what it proves without reading
the full catalog first.

Run source-tree examples from the repository root with `PYTHONPATH=src:.`.
Start with the portable `cpu_python_reference` backend; try native backends only
after the basic examples work.

## First Three Commands

```bash
PYTHONPATH=src:. python examples/v2_0/getting_started/rtdl_hello_world.py
PYTHONPATH=src:. python examples/v2_0/getting_started/rtdl_hello_world_backends.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py --backend cpu_python_reference
```

What this shows:

- the checkout imports and runs
- one RTDL kernel can execute through a selected runtime backend
- RTDL rows can be used inside a Python app

What this does not show:

- NVIDIA RT-core speedup
- whole-app acceleration
- full backend maturity

## Choose An App

| If you want to see... | Run first | What RTDL handles | Do not claim |
| --- | --- | --- | --- |
| First working command | `examples/v2_0/getting_started/rtdl_hello_world.py` | import and output smoke path | performance |
| Backend selection | `examples/v2_0/getting_started/rtdl_hello_world_backends.py` | same kernel idea through selected runners | backend speedup |
| Python+partner first path | `examples/v2_0/partners/rtdl_partner_anyhit.py --partner numpy --backend embree` | partner-owned columns staged into Embree any-hit | zero-copy or RT-core speedup |
| Advanced OptiX partner path | [OptiX Partner Column Any-Hit](tutorials/partner_optix_zero_copy_anyhit.md) | Torch/CuPy CUDA input-plus-output evidence for a prepared OptiX any-hit primitive | final release status or broad acceleration |
| Feature recipes | `examples/v2_0/getting_started/rtdl_feature_quickstart_cookbook.py` | one compact recipe per public feature | production readiness for every backend |
| Geometry/spatial joins | `examples/v2_0/features/spatial/rtdl_segment_polygon_hitcount.py` | segment/polygon candidate traversal and refinement | full GIS engine |
| Spatial coverage app | `examples/v2_0/apps/geospatial/rtdl_service_coverage_gaps.py` | fixed-radius household/clinic join | full service optimization |
| Hotspot app | `examples/v2_0/apps/geospatial/rtdl_event_hotspot_screening.py` | fixed-radius event neighbor counts | full analytics pipeline |
| Facility coverage decision | `examples/v2_0/apps/geospatial/rtdl_facility_knn_assignment.py` | KNN rows or prepared coverage-threshold decision | ranked assignment speedup |
| Hausdorff app | `examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py` | KNN rows or prepared threshold-decision traversal | exact-distance RTX speedup unless using a reviewed mode |
| Continuous Frechet learner app | `examples/v2_0/apps/trajectory/rtdl_continuous_frechet_distance_app.py` | segment/expanded-shape broadphase over free-space cells | whole-algorithm RTX speedup |
| ANN candidate app | `examples/v2_0/apps/ml/rtdl_ann_candidate_app.py` | KNN over a Python-selected candidate subset | full ANN index/ranking speedup |
| Outlier app | `examples/v2_0/apps/ml/rtdl_outlier_detection_app.py` | fixed-radius density rows or scalar density count | production anomaly system |
| DBSCAN app | `examples/v2_0/apps/ml/rtdl_dbscan_clustering_app.py` | fixed-radius core-count/core-flag phases | full cluster expansion speedup |
| Robot screening app | `examples/v2_0/apps/robotics/rtdl_robot_collision_screening_app.py` | ray/triangle any-hit pose flags/counts | whole robot-planning speedup |
| Barnes-Hut app | `examples/v2_0/apps/simulation/rtdl_barnes_hut_force_app.py` | node-candidate discovery or node-coverage decision | force-vector/opening-rule speedup |
| DB analytics app | `examples/v2_0/apps/analytics/rtdl_database_analytics_app.py` | bounded DB-style compact summaries | SQL engine or DBMS behavior |
| Graph analytics app | `examples/v2_0/apps/analytics/rtdl_graph_analytics_app.py` | bounded graph rows and native summaries | graph database/distributed analytics |
| Visual demo | `examples/visual_demo/rtdl_hidden_star_stable_ball_demo.py` | ray/triangle primary and shadow queries | RTDL renderer or graphics engine |

For the full app inventory, read [Application Catalog](application_catalog.md).
For backend support, read [App Engine Support Matrix](app_engine_support_matrix.md).
For implementation notes, use [Technical App Notes](research/app_notes/README.md).
For older version evidence, use [Learner Doc Version Notes](history/learner_doc_version_notes.md).

## Backend Names

RTDL uses the word "backend" in two places:

| Place | Meaning |
| --- | --- |
| `@rt.kernel(backend="rtdl")` | The kernel is written for the RTDL language/lowering contract. New kernels should use this spelling. |
| `--backend cpu_python_reference`, `embree`, `optix`, ... | The runtime execution engine selected by an app or example. |

Use `cpu_python_reference` first when learning. Use `cpu`, Embree, OptiX, HIPRT,
Vulkan, or Apple RT only when you intentionally want that runtime path and have
the needed local dependencies.

## Choose An Example Type

| Example type | Start here | Why |
| --- | --- | --- |
| Tutorial examples | [Quick Tutorial](quick_tutorial.md) | shortest path to the kernel shape |
| Feature recipes | `examples/v2_0/getting_started/rtdl_feature_quickstart_cookbook.py` | one runnable recipe per feature |
| App catalog | [Application Catalog](application_catalog.md) | current app inventory and boundaries |
| All examples | [Examples Index](../examples/README.md) | compact directory inventory |
| Command archive | [Release-Facing Examples](release_facing_examples.md) | large evidence-oriented command list |
| Technical app notes | [Technical App Notes](research/app_notes/README.md) | implementation boundaries and primitive groups |

## OptiX Rule For App Runs

Use this rule before publishing any performance wording:

```text
--backend optix is not a public NVIDIA RT-core speedup claim.
--require-rt-core only authorizes claim-sensitive runs when the selected
mode is documented and reviewed.
```

If an app returns full rows, Python labels, force vectors, ranked assignments,
or cluster labels, that output may include Python-owned continuation work. Only
claim the exact prepared/native sub-path that the support matrix and review
reports authorize.

## Recommended Demo Path

1. Run `examples/v2_0/getting_started/rtdl_hello_world.py`.
2. Run `examples/v2_0/getting_started/rtdl_feature_quickstart_cookbook.py`.
3. Run one app from the table above on `cpu_python_reference`.
4. If Embree is available, rerun the same app with `--backend embree`.
5. Read [Performance Model](performance_model.md) before interpreting timing.
6. Read [App Engine Support Matrix](app_engine_support_matrix.md) before using
   `--backend optix` or `--require-rt-core`.

This sequence demonstrates the RTDL user model: Python remains the app layer,
RTDL expresses the RT-shaped kernel, and backend-specific claims require exact
evidence.
