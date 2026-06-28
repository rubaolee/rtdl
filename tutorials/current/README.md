# RTDL V4 Tutorial

This path teaches RTDL as a programming model. It starts from the idea of ray
tracing and ends with recipes for the 10 benchmark apps.

The path has two kinds of lessons:

- language-layer lessons, such as hello world and sorting, teach how to express
  a problem as RTDL kernel/relation rows;
- V4 runtime lessons show a current operator surface only when a measured or
  declared V4 surface exists for that relation.

Do not read "in the V4 tutorial path" as "has a V4 operator surface." A lesson
must name its V4 mapping explicitly when one exists.

## Stage Map

| Stage | Lessons | Purpose |
| --- | --- | --- |
| Foundations | 1-4 | Learn RTDL as kernel/relation programming before V4 planning. |
| Core relations | 5-10 | Write radius, nearest, AABB, PIP, LSI, and ray-hit rows. |
| Continuations | 11-14 | Turn relation rows into grouped, bounded, component, and frontier outputs. |
| App lowerings | 15-20 | Practice lowering larger app ideas into generic RTDL rows. |
| Runtime surfaces | 21-23 | Choose partners, measure phases, and understand callback boundaries. |
| Composition bridge | 24 | Map tutorial concepts to benchmark apps. |

Read the lessons in order:

1. [What RTDL Is](01_first_run.md)
2. [Hello RTDL](02_hello_world.md)
3. [Sorting Rows](03_sorting_rows.md)
4. [Relations and Operators](04_relations_and_operators.md)
5. [Fixed-Radius Neighbors](05_fixed_radius_neighbors.md)
6. [Nearest Witness](06_nearest_witness.md)
7. [AABB Predicates](07_aabb_predicates.md)
8. [Point In Polygon](08_point_in_polygon.md)
9. [Line-Segment Intersection And Spatial Join](09_line_segment_intersection_spatial_join.md)
10. [Ray/Triangle Hit Rows](10_ray_triangle_hits.md)
11. [Grouped Continuations](11_grouped_continuations.md)
12. [Component Union From Radius Rows](12_component_union_from_radius.md)
13. [Bounded Witness Collection](13_bounded_witness_collection.md)
14. [Aggregate Frontier Rows](14_aggregate_frontier_rows.md)
15. [Ranked Summary Neighbors](15_ranked_summary_neighbors.md)
16. [Contact Manifold Lowering](16_contact_manifold_lowering.md)
17. [Graph Triangle Counting Lowering](17_graph_triangle_counting_lowering.md)
18. [Robot Collision Lowering](18_robot_collision_lowering.md)
19. [RayDB Table To Ray](19_raydb_table_to_ray.md)
20. [Hausdorff Composition](20_hausdorff_composition.md)
21. [Partner Choice And Device Arrays](21_partner_choice_device_arrays.md)
22. [Measurement Phases](22_measurement_phases.md)
23. [Callback Planning Boundary](23_callback_planning_boundary.md)
24. [Benchmark App Bridge](24_benchmark_app_bridge.md)

By the end you should understand how to:

- write RTDL kernel-mode programs first, before touching V4 route planning;
- describe an RT-shaped relation such as radius-neighbor, any-hit,
  nearest-witness, AABB query, or aggregate-frontier;
- compare each tutorial program's language-layer output with its `--mode v4`
  execution-surface mapping only when that mapping exists;
- run tutorial programs for NN, radius neighbors, ray hits, PIP, spatial join,
  partner choice, primitives, and continuations;
- read concept-program output as data flow, not as a black-box API answer;
- ask the V4 planner for the current operator surface after you know the RTDL
  relation being planned;
- write fixed-radius neighbor and nearest-witness row programs;
- write AABB, point-in-polygon, and line-segment-intersection row programs;
- write ray/triangle hit-row programs;
- reduce relation rows with grouped continuations;
- continue radius-neighbor rows into component labels;
- keep bounded witness rows with overflow validation;
- describe aggregate-frontier rows and weighted vector continuations;
- rank and summarize candidate rows;
- lower contact, triangle-counting, robot-collision, RayDB, and Hausdorff
  workloads into RTDL rows and continuations;
- choose Torch, CuPy, Numba, or RTDL native explicitly in later partner lessons;
- read device-array bridge examples after the relation is clear;
- measure setup, hot relation work, continuation, validation, and materialized
  output separately;
- separate recognized V4 operators from arbitrary callback-shaped code;
- keep application meaning outside the generic operator;
- combine an RT relation with a continuation step;
- lower graph, robot, Hausdorff, RayDB, RayJoin, and Barnes-Hut app logic into
  relation rows and continuation rows in later lessons;
- run small tutorial programs before opening the full benchmark apps;
- read the benchmark app recipes before opening the full app sources;
- separate tutorial timing, hot-path timing, validation, and full benchmark
  runner timing.
