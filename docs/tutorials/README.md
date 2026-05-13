# RTDL Tutorials

Start here if you want to write RTDL programs, not just read reference pages.

If you are brand new, read [Quick Tutorial](../quick_tutorial.md) first. It gets
you a working program immediately and explains the kernel shape before the
longer tutorials.

If you want to choose a runnable app or example before reading the full ladder,
use [App And Example Quickstart](../app_example_quickstart.md).

If you want the full example inventory, use [Examples Index](../../examples/README.md).
That index is more complete and more boundary-heavy than this tutorial page.

The tutorial ladder is organized around the main RTDL value proposition: write a
small workload kernel once, keep application logic in Python, and avoid
hand-maintaining separate ray-tracing backend implementations.

## Tutorial Ladder

| Step | Tutorial | What you learn |
| --- | --- | --- |
| 0 | [Quick Tutorial](../quick_tutorial.md) | First run, kernel anatomy, four-step pattern |
| 1 | [Hello World](hello_world.md) | Full kernel walkthrough, line-by-line |
| 2 | [Sorting Demo](sorting_demo.md) | RTDL inside a compact Python program |
| 3 | [Feature Quickstart Cookbook](feature_quickstart_cookbook.md) | One compact recipe per public feature |
| 4 | [Segment And Polygon Workloads](segment_polygon_workloads.md) | Segment/polygon feature family and boundaries |
| 5 | [Nearest-Neighbor Workloads](nearest_neighbor_workloads.md) | Fixed-radius and KNN row workloads |
| 6 | [Graph Workloads](graph_workloads.md) | RT graph workload shapes and limits |
| 7 | [Database Workloads](db_workloads.md) | Bounded DB-style kernel examples |
| 8 | [RTDL Plus Python Rendering](rendering_and_visual_demos.md) | RTDL as an accelerated compute/query core inside Python demos |
| 9 | [HIPRT Example](../../examples/rtdl_hiprt_ray_triangle_hitcount.py) | Prepared 3D ray/triangle path |
| 10 | [Unified Apple RT Demo App](../../examples/rtdl_apple_rt_demo_app.py) | Apple RT closest-hit and visibility-count scenarios |
| 11 | [Ray/Triangle Any-Hit Example](../../examples/rtdl_ray_triangle_any_hit.py) | Bounded any-hit row primitive |
| 12 | [Python Partner Any-Hit](partner_anyhit.md) | First v2.0 partner-owned column path with Embree as CPU RT fallback |
| 13 | [OptiX Partner Zero-Copy Any-Hit Preview](partner_optix_zero_copy_anyhit.md) | Advanced Torch/CuPy CUDA input-plus-output zero-copy slice for one OptiX primitive |
| 14 | [Visibility Rows Example](../../examples/rtdl_visibility_rows.py) | Observer-target line-of-sight rows |
| 15 | [Reduce Rows Example](../../examples/rtdl_reduce_rows.py) | Deterministic Python standard-library reductions over emitted RTDL rows |

## Three Learning Tracks

### Track 1: Language Basics

Learn the `input -> traverse -> refine -> emit` kernel shape and how Python
wraps RTDL as an engine.

- [Hello World](hello_world.md)
- [Sorting Demo](sorting_demo.md)

### Track 2: Workload Tutorials

Learn the workload families, what they emit, and when to choose each.

- [Feature Quickstart Cookbook](feature_quickstart_cookbook.md)
- [Segment And Polygon Workloads](segment_polygon_workloads.md)
- [Nearest-Neighbor Workloads](nearest_neighbor_workloads.md)
- [Graph Workloads](graph_workloads.md)
- [Database Workloads](db_workloads.md)

Current feature terms you will see:

- `ANY_HIT`
- `COUNT_HITS`
- `REDUCE_FLOAT(MIN|MAX|SUM)`
- `REDUCE_INT(COUNT|SUM)`
- `ray_triangle_any_hit`
- `visibility_rows`
- `reduce_rows`

### Track 3: Application Demos

Learn how RTDL works as the accelerated compute/query core inside a larger
Python application.

- [RTDL Plus Python Rendering](rendering_and_visual_demos.md)
- [HIPRT Example](../../examples/rtdl_hiprt_ray_triangle_hitcount.py)
- [Unified Apple RT Demo App](../../examples/rtdl_apple_rt_demo_app.py)
- [Ray/Triangle Any-Hit Example](../../examples/rtdl_ray_triangle_any_hit.py)
- [Python Partner Any-Hit](partner_anyhit.md)
- [OptiX Partner Zero-Copy Any-Hit Preview](partner_optix_zero_copy_anyhit.md)
- [Visibility Rows Example](../../examples/rtdl_visibility_rows.py)
- [Reduce Rows Example](../../examples/rtdl_reduce_rows.py)

## After The Tutorials

Once you finish the ladder, the next useful destinations are:

- [Current Architecture](../current_architecture.md)
- [Feature Quickstart Cookbook](feature_quickstart_cookbook.md)
- [Release-Facing Examples](../release_facing_examples.md)
- [Feature Homes](../features/README.md)
- [RTDL Language Docs](../rtdl/README.md)
- [Application Catalog](../application_catalog.md)
- [Capability Boundaries](../capability_boundaries.md)
- [Performance Model](../performance_model.md)

Use the tutorials first. Use the reference pages when you want exact contracts,
edge cases, backend/status detail, or benchmark evidence.
