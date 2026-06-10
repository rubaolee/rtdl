# RTDL v2.10 Tutorials

Start with the [Current RTDL Tutorial Track](current/README.md) if you are new.
It is the ordered path from first run to a Python+RTDL+CuPy/Numba benchmark app.

Use the rest of this page as reference navigation after you finish that track.

RTDL is a Python eDSL. You write the surrounding Python application, describe
the traversal-heavy kernel in RTDL, and choose a backend such as the portable
CPU reference path, Embree, or OptiX. In the v2.10 track, NumPy, CuPy, and
selected Numba continuations can own or continue columns around supported RTDL
primitives.

This page is intentionally single-surface. Runtime examples teach the current
v2.10 source-tree surface; primitive discovery and prepared execution are current
source-tree guidance and do not change release or performance claim boundaries.

## Guided Track

| Step | Tutorial | What you learn |
| --- | --- | --- |
| 1 | [Run From The Source Tree](current/01_source_tree_first_run.md) | Source-tree setup and first example run |
| 2 | [Kernel Shape And Backends](current/02_kernel_shape_and_backends.md) | Input, traversal, refine, emit, and backend choice |
| 3 | [Primitive Discovery](current/03_primitives_and_discovery.md) | Search before creating new app code |
| 4 | [Python App Structure](current/04_python_app_structure.md) | Keep app meaning in Python and engine contracts generic |
| 5 | [Partner Columns With CuPy Or Numba](current/05_partner_columns_cupy_numba.md) | Explicit partner choice for custom continuation |
| 6 | [Prepared Execution And Measurement](current/06_prepared_execution_measurement.md) | Setup, prepare, warmup, steady-state, validation |
| 7 | [Benchmark App Walkthrough](current/07_benchmark_app_python_rtdl_partner.md) | CPU oracle, RTDL rows, CuPy, Numba, and optional OptiX |

## Reference Tutorials

| Step | Tutorial | What you learn |
| --- | --- | --- |
| 0 | [Quick Tutorial](../quick_tutorial.md) | First run, kernel anatomy, and the `input -> traverse -> refine -> emit` pattern |
| 1 | [Hello World](hello_world.md) | The smallest complete RTDL program |
| 2 | [Python+Partner+RTDL App Building](v2_app_building.md) | How Python, RTDL, and partner arrays divide work |
| 3 | [Python Partner Any-Hit](partner_anyhit.md) | Partner-owned columns with Embree as the CPU RT fallback |
| 4 | [OptiX Partner Column Any-Hit](partner_optix_column_anyhit.md) | The GPU partner-column shape and its claim boundary |
| 5 | [Feature Quickstart Cookbook](feature_quickstart_cookbook.md) | Which RTDL primitive shape to choose for a workload |
| 6 | [Primitive Discovery Workflow](../learn/primitive_discovery_workflow.md) | How to search primitives, recipes, and explain-only plans |
| 7 | [Prepared Execution Pattern](../learn/prepared_execution_pattern.md) | Setup, cache, warmup, steady-state, and validation timing |
| 8 | [Prepared Session Reuse](../learn/prepared_session_reuse.md) | Explicit prepare-once/query-many reuse with visible invalidation |
| 9 | [Segment And Polygon Workloads](segment_polygon_workloads.md) | Count rows, witness rows, and streaming witness summaries |
| 10 | [Nearest-Neighbor Workloads](nearest_neighbor_workloads.md) | Fixed-radius, K-closest, and Hausdorff-style composition |
| 11 | [Graph Workloads](graph_workloads.md) | Frontier/edge traversal rows and graph-summary continuation |
| 12 | [Database Workloads](db_workloads.md) | Columnar-payload scans, grouped summaries, and DB-style boundaries |
| 13 | [RTDL Plus Python Rendering](rendering_and_visual_demos.md) | RTDL as the compute/query core inside a Python visual program |

## Learning Tracks

### Language Basics

- [Quick Tutorial](../quick_tutorial.md)
- [Hello World](hello_world.md)
- [Primitive Discovery Workflow](../learn/primitive_discovery_workflow.md)
- [Prepared Execution Pattern](../learn/prepared_execution_pattern.md)
- [Prepared Session Reuse](../learn/prepared_session_reuse.md)
- [Sorting Demo](sorting_demo.md)

### Python+Partner+RTDL

- [Python+Partner+RTDL App Building](v2_app_building.md)
- [Python Partner Any-Hit](partner_anyhit.md)
- [OptiX Partner Column Any-Hit](partner_optix_column_anyhit.md)
- [Choosing A Partner For Custom Logic](../learn/partner_choice_for_custom_logic.md)
- [Benchmark Partner Reference Matrix](../learn/benchmark_partner_reference_matrix.md)
- [Partner Acceleration Boundaries](../partner_acceleration_boundaries.md)

### Workload Families

- [Feature Quickstart Cookbook](feature_quickstart_cookbook.md)
- [Segment And Polygon Workloads](segment_polygon_workloads.md)
- [Nearest-Neighbor Workloads](nearest_neighbor_workloads.md)
- [Graph Workloads](graph_workloads.md)
- [Database Workloads](db_workloads.md)

## Current Claim Boundary

The v2.10 tutorial path teaches the source-tree Python+partner+RTDL surface.
Use it from the source tree with `PYTHONPATH=src:.`.

Allowed tutorial wording:

- RTDL can run the documented Python+RTDL examples from source.
- v2.10 has partner-column paths for documented primitives.
- v2.10 has explicit CuPy/Numba partner-choice guidance.
- OptiX evidence exists for specific measured contracts.
- Python or partner frameworks own app continuation outside the RTDL primitive.

Not allowed:

- package-install promises;
- broad RT-core speedup claims;
- arbitrary CuPy/Numba acceleration claims;
- arbitrary polygon overlay, graph analytics, or database acceleration claims;
- universal speedup wording beyond reviewed evidence.

For the exact boundary, read
[Partner Acceleration Boundaries](../partner_acceleration_boundaries.md).

## More Navigation

- [Docs Index](../README.md)
- [Public Documentation Map](../public_documentation_map.md)
- [App And Example Quickstart](../app_example_quickstart.md)
- [Application Catalog](../application_catalog.md)
- [Current Architecture](../current_architecture.md)
- [IR And Lowering](../rtdl/ir_and_lowering.md)

## Tutorial Archive

Older tutorial files are preserved for audit and project history, but they are
not part of the active learner path. Start here for the current surface; use
[Tutorial Archive](../history/tutorial_archive/README.md) only when you need to
inspect archived project history.
