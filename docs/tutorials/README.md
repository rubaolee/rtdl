# RTDL Tutorials

Start here if you want to write RTDL programs, not just read reference pages.

If you are brand new, read [Quick Tutorial](../quick_tutorial.md) first. It gets
you a working program immediately and explains the kernel shape before the
longer tutorials.

If you want to choose a runnable app or example before reading the full ladder,
use [App And Example Quickstart](../app_example_quickstart.md).

If you want the full example inventory, use [Examples Index](../../examples/README.md).
That index is intentionally more complete and more boundary-heavy than this tutorial page.

The tutorial ladder is organized around the main RTDL value proposition: write a
small workload kernel once, keep application logic in Python, and avoid
hand-maintaining separate ray-tracing backend implementations for every modern
RT stack.

The current released version is `v1.6`. The ladder below teaches the stable
Python+RTDL authoring path first, then points to older feature-family tutorials
as historical building blocks.

---

## Tutorial Ladder

| Step | Tutorial | What you learn |
| --- | --- | --- |
| 0 | [Quick Tutorial](../quick_tutorial.md) | First run, kernel anatomy, four-step pattern |
| 1 | [Hello World](hello_world.md) | Full kernel walkthrough, line-by-line |
| 2 | [Sorting Demo](sorting_demo.md) | RTDL inside a compact Python program |
| 3 | [Feature Quickstart Cookbook](feature_quickstart_cookbook.md) | One compact recipe per current public feature |
| 4 | [Segment And Polygon Workloads](segment_polygon_workloads.md) | Segment/polygon feature family and boundaries |
| 5 | [Nearest-Neighbor Workloads](nearest_neighbor_workloads.md) | Fixed-radius and KNN row workloads |
| 6 | [Graph Workloads](graph_workloads.md) | RT graph workload shapes and limits |
| 7 | [Database Workloads](db_workloads.md) | Bounded DB-style kernel examples |
| 8 | [v0.8 App Building](v0_8_app_building.md) | Historical app-building tutorial over RTDL rows plus Python orchestration |
| 9 | [RTDL Plus Python Rendering](rendering_and_visual_demos.md) | RTDL as an accelerated compute/query core inside Python demos |
| 10 | [HIPRT Example](../../examples/rtdl_hiprt_ray_triangle_hitcount.py) | See the prepared 3D path for the released v0.9 HIPRT surface |
| 11 | [Unified Apple RT Demo App](../../examples/rtdl_apple_rt_demo_app.py) | See Apple RT closest-hit and visibility-count scenarios from one demo entry point |
| 12 | [Ray/Triangle Any-Hit Example](../../examples/rtdl_ray_triangle_any_hit.py) | See the released v0.9.5 bounded any-hit row primitive |
| 13 | [Visibility Rows Example](../../examples/rtdl_visibility_rows.py) | See observer-target line-of-sight rows built on any-hit |
| 14 | [Reduce Rows Example](../../examples/rtdl_reduce_rows.py) | See deterministic Python standard-library reductions over emitted RTDL rows |

---

## Three Learning Tracks

RTDL beginners usually want one of three things:

### Track 1: Language basics

Learn the `input -> traverse -> refine -> emit` kernel shape and how Python
wraps RTDL as an engine.

- [Hello World](hello_world.md)
- [Sorting Demo](sorting_demo.md)

### Track 2: Workload tutorials

Learn the released workload families, what they emit, and when to choose each.

- [Feature Quickstart Cookbook](feature_quickstart_cookbook.md)
  - one compact recipe per current public feature
  - one runnable companion command
- [Segment And Polygon Workloads](segment_polygon_workloads.md)
  - `segment_polygon_hitcount`
  - `segment_polygon_anyhit_rows`
  - `polygon_pair_overlap_area_rows`
  - `polygon_set_jaccard`
- [Nearest-Neighbor Workloads](nearest_neighbor_workloads.md)
  - `fixed_radius_neighbors`
  - `knn_rows`
- [Graph Workloads](graph_workloads.md)
  - `bfs`
  - `triangle_count`
- [Database Workloads](db_workloads.md)
  - `conjunctive_scan`
  - `grouped_count`
  - `grouped_sum`
- v1.6 stable primitive/reduction terms and older helper names:
  - `ANY_HIT`
  - `COUNT_HITS`
  - `REDUCE_FLOAT(MIN|MAX|SUM)`
  - `REDUCE_INT(COUNT|SUM)`
  - `ray_triangle_any_hit`
  - `visibility_rows`
  - `reduce_rows`

### Track 3: Application demos

Learn how RTDL works as the accelerated compute/query core inside a larger Python
application.

- [RTDL Plus Python Rendering](rendering_and_visual_demos.md)
- [v0.8 App Building](v0_8_app_building.md)
- [HIPRT Example](../../examples/rtdl_hiprt_ray_triangle_hitcount.py)
- [Unified Apple RT Demo App](../../examples/rtdl_apple_rt_demo_app.py)
- [Ray/Triangle Any-Hit Example](../../examples/rtdl_ray_triangle_any_hit.py)
- [Visibility Rows Example](../../examples/rtdl_visibility_rows.py)
- [Reduce Rows Example](../../examples/rtdl_reduce_rows.py)

---

## After The Tutorials

Once you finish the ladder, the next useful destinations are:

- [Current Architecture](../current_architecture.md)
- [Feature Quickstart Cookbook](feature_quickstart_cookbook.md)
- [Release-Facing Examples](../release_facing_examples.md)
- [Feature Homes](../features/README.md)
- [RTDL Language Docs](../rtdl/README.md)
- [RTDL v0.4 Application Examples](../v0_4_application_examples.md)
- [HIPRT Example](../../examples/rtdl_hiprt_ray_triangle_hitcount.py)
- [Unified Apple RT Demo App](../../examples/rtdl_apple_rt_demo_app.py)
- [v0.9.6 Release Package](../release_reports/v0_9_6/README.md)
- [v0.9.5 Release Package](../release_reports/v0_9_5/README.md)

Use the tutorials first. Use the reference pages when you want exact contracts,
edge cases, and backend/status detail.
