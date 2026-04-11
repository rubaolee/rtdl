# RTDL Tutorials

This is the tutorial front door for beginners.

Use it when your goal is not to read every reference page, but to learn how to
write and run RTDL programs in a sensible order.

## Start Here

If you are new to RTDL, use this sequence:

1. [Quick Tutorial](../quick_tutorial.md)
2. [Hello World](hello_world.md)
3. [Sorting Demo](sorting_demo.md)
4. [Segment And Polygon Workloads](segment_polygon_workloads.md)
5. [Nearest-Neighbor Workloads](nearest_neighbor_workloads.md)
6. [RTDL Plus Python Rendering](rendering_and_visual_demos.md)

If you already know you care about a specific workload family, jump directly to
the matching tutorial page below.

## How The Tutorial Set Is Organized

The tutorial ladder is intentionally split into three kinds of learning:

- language basics
- workload-focused tutorials
- RTDL-plus-Python application demos

That matters because RTDL is not only a fixed catalog of named workloads. It is
a language/runtime for geometric queries that can also sit inside user-authored
Python applications.

## Track 1: Language Basics

- [Hello World](hello_world.md)
  - the smallest RTDL program in the repo
  - teaches the `input -> traverse -> refine -> emit` shape
- [Sorting Demo](sorting_demo.md)
  - a compact “RTDL is a programmable geometric engine” example
  - teaches how Python owns the surrounding program while RTDL provides the
    geometric core

## Track 2: Workload Tutorials

- [Segment And Polygon Workloads](segment_polygon_workloads.md)
  - released `v0.2.0` workload surface
  - `segment_polygon_hitcount`
  - `segment_polygon_anyhit_rows`
  - `polygon_pair_overlap_area_rows`
  - `polygon_set_jaccard`
- [Nearest-Neighbor Workloads](nearest_neighbor_workloads.md)
  - active `v0.4` preview line
  - `fixed_radius_neighbors`
  - `knn_rows`
  - application-shaped examples built on top of those workloads

## Track 3: RTDL Plus Python Demos

- [RTDL Plus Python Rendering](rendering_and_visual_demos.md)
  - 2D/3D visual-demo entry points
  - how RTDL participates as the geometry-query core while Python owns the
    application layer

## When To Use The Reference Docs

After the tutorial ladder, the next useful pages are:

- [Release-Facing Examples](../release_facing_examples.md)
- [Feature Homes](../features/README.md)
- [RTDL Language Docs](../rtdl/README.md)
- [RTDL v0.2 User Guide](../v0_2_user_guide.md)
- [RTDL v0.4 Application Examples](../v0_4_application_examples.md)

Use the tutorial pages first. Use the reference pages when you want full
contracts, edge cases, and backend/status detail.
