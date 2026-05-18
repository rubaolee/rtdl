# RTDL v2.0 Tutorials

Start here if you want to write RTDL programs with the current v2.0-facing
Python+partner+RTDL surface.

RTDL is a Python eDSL. You write the surrounding Python application, describe
the traversal-heavy kernel in RTDL, and choose a backend such as the portable
CPU reference path, Embree, or OptiX. In the v2.0 track, partner frameworks such
as NumPy, PyTorch, and CuPy can own columns around supported RTDL primitives.

This page is intentionally single-version. It teaches the current v2.0 release
surface and links old tutorial history only from the final archive section.

## Start Here

| Step | Tutorial | What you learn |
| --- | --- | --- |
| 0 | [Quick Tutorial](../quick_tutorial.md) | First run, kernel anatomy, and the `input -> traverse -> refine -> emit` pattern |
| 1 | [Hello World](hello_world.md) | The smallest complete RTDL program |
| 2 | [v2.0 App Building](v2_app_building.md) | How Python, RTDL, and partner arrays divide work |
| 3 | [Python Partner Any-Hit](partner_anyhit.md) | Partner-owned columns with Embree as the CPU RT fallback |
| 4 | [OptiX Partner Column Any-Hit](partner_optix_zero_copy_anyhit.md) | The GPU partner-column shape and its claim boundary |
| 5 | [Feature Quickstart Cookbook](feature_quickstart_cookbook.md) | Which RTDL primitive shape to choose for a workload |
| 6 | [Segment And Polygon Workloads](segment_polygon_workloads.md) | Count rows, witness rows, and streaming witness summaries |
| 7 | [Nearest-Neighbor Workloads](nearest_neighbor_workloads.md) | Fixed-radius, K-closest, and Hausdorff-style composition |
| 8 | [Graph Workloads](graph_workloads.md) | Frontier/edge traversal rows and graph-summary continuation |
| 9 | [Database Workloads](db_workloads.md) | Columnar-payload scans, grouped summaries, and DB-style boundaries |
| 10 | [RTDL Plus Python Rendering](rendering_and_visual_demos.md) | RTDL as the compute/query core inside a Python visual program |

## Learning Tracks

### Language Basics

- [Quick Tutorial](../quick_tutorial.md)
- [Hello World](hello_world.md)
- [Sorting Demo](sorting_demo.md)

### Python+Partner+RTDL

- [v2.0 App Building](v2_app_building.md)
- [Python Partner Any-Hit](partner_anyhit.md)
- [OptiX Partner Column Any-Hit](partner_optix_zero_copy_anyhit.md)
- [Partner Acceleration Boundaries](../partner_acceleration_boundaries.md)

### Workload Families

- [Feature Quickstart Cookbook](feature_quickstart_cookbook.md)
- [Segment And Polygon Workloads](segment_polygon_workloads.md)
- [Nearest-Neighbor Workloads](nearest_neighbor_workloads.md)
- [Graph Workloads](graph_workloads.md)
- [Database Workloads](db_workloads.md)

## Current Claim Boundary

The v2.0 tutorial path teaches the released source-tree Python+partner+RTDL surface.
Use it from the source tree with `PYTHONPATH=src:.`.

Allowed tutorial wording:

- RTDL can run the documented Python+RTDL examples from source.
- The v2.0 release has partner-column paths for documented primitives.
- OptiX evidence exists for specific measured contracts.
- Python or partner frameworks own app continuation outside the RTDL primitive.

Not allowed:

- package-install promises;
- broad RT-core speedup claims;
- arbitrary PyTorch/CuPy acceleration claims;
- arbitrary polygon overlay, graph analytics, or database acceleration claims;
- universal speedup wording beyond reviewed evidence.

For the exact boundary, read
[Partner Acceleration Boundaries](../partner_acceleration_boundaries.md) and
[v2.0 Release Package](../release_reports/v2_0/README.md).

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
