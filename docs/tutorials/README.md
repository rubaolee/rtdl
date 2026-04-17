# RTDL Tutorials

Start here if you want to write RTDL programs, not just read reference pages.

If you are brand new, read [Quick Tutorial](../quick_tutorial.md) first. It gets
you a working program immediately and explains the kernel shape before the
longer tutorials.

---

## Tutorial Ladder

| Step | Tutorial | What you learn |
| --- | --- | --- |
| 0 | [Quick Tutorial](../quick_tutorial.md) | First run, kernel anatomy, four-step pattern |
| 1 | [Hello World](hello_world.md) | Full kernel walkthrough, line-by-line |
| 2 | [Sorting Demo](sorting_demo.md) | RTDL inside a compact Python program |
| 3 | [Segment And Polygon Workloads](segment_polygon_workloads.md) | Released `v0.2.0` workload families |
| 4 | [Nearest-Neighbor Workloads](nearest_neighbor_workloads.md) | Released `v0.4.0` nearest-neighbor workloads |
| 5 | [Graph Workloads](graph_workloads.md) | Released `v0.6.1` RT graph workloads |
| 6 | [Database Workloads](db_workloads.md) | Released `v0.7.0` bounded DB kernels |
| 7 | [RTDL Plus Python Rendering](rendering_and_visual_demos.md) | RTDL as an accelerated compute/query core inside Python demos |

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

### Track 3: Application demos

Learn how RTDL works as the accelerated compute/query core inside a larger Python
application.

- [RTDL Plus Python Rendering](rendering_and_visual_demos.md)

---

## After The Tutorials

Once you finish the ladder, the next useful destinations are:

- [Release-Facing Examples](../release_facing_examples.md)
- [Feature Homes](../features/README.md)
- [RTDL Language Docs](../rtdl/README.md)
- [RTDL v0.4 Application Examples](../v0_4_application_examples.md)

Use the tutorials first. Use the reference pages when you want exact contracts,
edge cases, and backend/status detail.
