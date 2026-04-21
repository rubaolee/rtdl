# RTDL Feature Homes

This directory is the canonical workload-by-workload documentation surface for
the current RTDL language.

Use these feature homes when you want to answer practical questions quickly:

- what this feature does
- when to use it
- where the canonical code lives
- which example to run first
- best practices
- what to try and what not to try
- current limitations
- how each RTDL engine reports support for public selectable features

## Choose By Workload Shape

| Workload shape | Feature home |
| --- | --- |
| engine-by-feature support states | [Engine Feature Support Contract](engine_support_matrix.md) |
| segment/segment root spatial join | [LSI: Line Segment Intersection](lsi/README.md) |
| point/polygon root spatial join | [PIP: Point In Polygon](pip/README.md) |
| nearest neighbors within a radius | [Fixed-Radius Neighbors](fixed_radius_neighbors/README.md) |
| top-k nearest neighbors | [KNN Rows](knn_rows/README.md) |
| segment/polygon candidate search | [Segment/Polygon Hit Count](segment_polygon_hitcount/README.md) |
| segment/polygon row materialization | [Segment/Polygon Any-Hit Rows](segment_polygon_anyhit_rows/README.md) |
| bounded overlap/Jaccard cases | [Polygon-Pair Overlap Area Rows](polygon_pair_overlap_area_rows/README.md) and [Polygon-Set Jaccard](polygon_set_jaccard/README.md) |
| bounded ray yes/no blocker tests | [Ray/Triangle Any Hit](ray_tri_anyhit/README.md) |
| observer-target line-of-sight rows | [Visibility Rows](visibility_rows/README.md) |
| emitted-row app reductions | [Reduce Rows](reduce_rows/README.md) |
| bounded DB-style filtering and aggregation | [Database Workloads](db_workloads/README.md) |

Across these features, the intended RTDL benefit is the same: write the
workload contract once, then let RTDL handle traversal/refinement/backend
plumbing inside documented release limits.

`lsi` and `pip` are the original RTDL root workloads. Current `main` gives them
dedicated root-workload performance evidence again in
[Goal 742](../reports/goal742_lsi_pip_root_workload_refresh_2026-04-21.md):
Embree now uses native CPU ray-tracing traversal for LSI and native point-query
candidate discovery for positive-hit PIP, with automatic multithreaded dispatch
and prepared raw result modes for low-overhead app integration.

`v0.9.6` does not add a new workload family. It makes the any-hit and
visibility-count path more practical for repeated apps by adding
prepared/prepacked backend contracts for Apple RT, OptiX, HIPRT, and Vulkan.
Use those paths when the build-side triangles and probe-side ray batches are
stable and the app can consume scalar or compact yes/no outputs.

For the fastest feature-by-feature learning path, use:

- [Feature Quickstart Cookbook](../tutorials/feature_quickstart_cookbook.md)
- [rtdl_feature_quickstart_cookbook.py](../../examples/rtdl_feature_quickstart_cookbook.py)

Current feature homes:

- [Engine Feature Support Contract](engine_support_matrix.md)
- [Fixed-Radius Neighbors](fixed_radius_neighbors/README.md) (released in `v0.4.0`)
- [KNN Rows](knn_rows/README.md) (released in `v0.4.0`)
- [LSI: Line Segment Intersection](lsi/README.md)
- [PIP: Point In Polygon](pip/README.md)
- [Overlay](overlay/README.md)
- [Ray/Triangle Hit Count](ray_tri_hitcount/README.md)
- [Ray/Triangle Any Hit](ray_tri_anyhit/README.md) (released in `v0.9.5`)
- [Visibility Rows](visibility_rows/README.md) (released in `v0.9.5`)
- [Reduce Rows](reduce_rows/README.md) (released in `v0.9.5`)
- Prepared/prepacked repeated visibility/count paths (released in `v0.9.6`;
  documented in the [v0.9.6 Support Matrix](../release_reports/v0_9_6/support_matrix.md))
- [Point/Nearest Segment](point_nearest_segment/README.md)
- [Segment/Polygon Hit Count](segment_polygon_hitcount/README.md)
- [Segment/Polygon Any-Hit Rows](segment_polygon_anyhit_rows/README.md)
- [Polygon-Pair Overlap Area Rows](polygon_pair_overlap_area_rows/README.md)
- [Polygon-Set Jaccard](polygon_set_jaccard/README.md)
- [Database Workloads](db_workloads/README.md) (released bounded `v0.7.0` line)

Reading order for new users:

1. [RTDL Quick Tutorial](../quick_tutorial.md)
2. [RTDL v0.2 User Guide](../v0_2_user_guide.md)
3. this feature index
4. [Fixed-Radius Neighbors](fixed_radius_neighbors/README.md) or [KNN Rows](knn_rows/README.md) for the released nearest-neighbor line
5. the specific feature home you plan to use
6. [Database Workloads](db_workloads/README.md) if you are working on the bounded `v0.7.0` DB release
7. [RTDL Workload Cookbook](../rtdl/workload_cookbook.md)
8. [RTDL DSL Reference](../rtdl/dsl_reference.md)
