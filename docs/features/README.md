# RTDL Feature Homes

Status: current v2.3 release feature index.

Use these pages when you want to answer practical questions:

- what the feature does;
- which example to run first;
- which engines expose it;
- what output contract it returns;
- what boundary not to overclaim.

## Choose By Workload Shape

| Workload shape | Feature home |
| --- | --- |
| engine-by-feature support states | [Engine Feature Support Contract](engine_support_matrix.md) |
| segment/segment spatial join | [LSI: Line Segment Intersection](lsi/README.md) |
| point/polygon spatial join | [PIP: Point In Polygon](pip/README.md) |
| nearest neighbors within a radius | [Fixed-Radius Neighbors](fixed_radius_neighbors/README.md) |
| top-k nearest neighbors | [KNN Rows](knn_rows/README.md) |
| segment/polygon candidate search | [Segment/Polygon Hit Count](segment_polygon_hitcount/README.md) |
| segment/polygon witness rows | [Segment/Polygon Any-Hit Rows](segment_polygon_anyhit_rows/README.md) |
| bounded overlap/Jaccard summaries | [Polygon-Pair Overlap Area Rows](polygon_pair_overlap_area_rows/README.md) and [Polygon-Set Jaccard](polygon_set_jaccard/README.md) |
| ray yes/no blocker tests | [Ray/Triangle Any Hit](ray_tri_anyhit/README.md) |
| ray hit counts | [Ray/Triangle Hit Count](ray_tri_hitcount/README.md) |
| observer-target line-of-sight rows | [Visibility Rows](visibility_rows/README.md) |
| emitted-row app reductions | [Reduce Rows](reduce_rows/README.md) |
| bounded DB-style filtering and aggregation | [Database Workloads](db_workloads/README.md) |

## Recommended Reading Order

1. [RTDL Quick Tutorial](../quick_tutorial.md)
2. [RTDL Tutorials](../tutorials/README.md)
3. [RTDL Programming Guide](../rtdl/programming_guide.md)
4. [RTDL DSL Reference](../rtdl/dsl_reference.md)
5. The feature home for the workload you plan to run.

## Boundary

Feature homes describe current APIs. They should not carry release-history
notes, old goal logs, or old benchmark claims. Older context belongs in the
archive and release-report areas.
