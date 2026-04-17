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

Current feature homes:

- [Fixed-Radius Neighbors](fixed_radius_neighbors/README.md) (released in `v0.4.0`)
- [KNN Rows](knn_rows/README.md) (released in `v0.4.0`)
- [LSI: Line Segment Intersection](lsi/README.md)
- [PIP: Point In Polygon](pip/README.md)
- [Overlay](overlay/README.md)
- [Ray/Triangle Hit Count](ray_tri_hitcount/README.md)
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
