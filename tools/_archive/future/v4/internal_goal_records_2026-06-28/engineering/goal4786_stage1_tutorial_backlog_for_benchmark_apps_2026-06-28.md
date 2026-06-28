# Goal4786: Stage 1 Tutorial Backlog For The 10 Benchmark Apps

Date: 2026-06-28

Status: planning backlog only. This file does not claim the tutorials are
finished. It defines the remaining Stage 1 tutorial topics that must exist
before Stage 2 asks a learner to read or write the 10 benchmark apps.

## Purpose

Stage 1 tutorials teach RTDL language concepts. Stage 2 benchmark apps are
exams that combine those concepts.

The tutorial surface must not teach "how to write RTDBSCAN" or "how to write
RayJoin" as app-specific recipes first. It must teach the RTDL building blocks:
input geometry, traversal, refinement, emitted rows, relations, continuations,
partners, phase measurement, and the major lowering patterns. A user should be
able to combine these blocks later when facing a benchmark app or a new
workload.

## Goal-Level Decision Check

1. Am I making the previous mistake of writing app-defense text instead of a
   language tutorial?
   - No. This backlog separates language topics from benchmark apps and treats
     benchmark apps as Stage 2 exams.
2. What action would make this decision stupid?
   - Starting with a benchmark app and hiding its logic behind a one-call
     wrapper, or ignoring old working examples before writing new material.
3. Is there a better path than inventing fresh tutorials blindly?
   - Yes. For each topic, inspect the old material first, keep the teaching
     idea if it is good, and modernize only the public V4 naming, file paths,
     and execution surfaces.
4. What path now solves the real problem?
   - Build a small concept ladder whose combined concepts cover all 10
     benchmark apps. Each topic must show the problem-to-RTDL lowering, not
     only call a finished primitive.

## Already Accepted Stage 1 Topics

| Order | Topic | Current files | Source lineage | Status |
| --- | --- | --- | --- | --- |
| 01 | First RTDL kernel / hello world | `examples/tutorial_programs/hello_world.py`, `tutorials/current/02_hello_world.md` | Restores the original user-authored hello-world idea: input geometry -> traverse -> refine -> emit -> Python output. | Completed by Goal4784. |
| 02 | Ray-hit sorting / rank from rows | `examples/tutorial_programs/sorting_rows.py`, `tutorials/current/03_sorting_rows.md` | Restores Goal97 ray-hit sorting: values -> segment geometry -> intersection hit rows -> hit counts -> stable order. | Completed by Goal4785. |

These two topics are the base of the ladder. They show that RTDL programs are
not "call a magic helper"; they lower ordinary logic into traversal rows and
continuation rows.

## Remaining Stage 1 Tutorial Topics

Each topic below must be written as a small tutorial program plus a tutorial
page or page section. Before writing the topic, inspect the listed old material
and decide whether to inherit, simplify, or replace it. A topic is not complete
until it runs on Linux with `PYTHONPATH=src:.` and its tutorial explains the
lowering.

| Order | Tutorial topic | Why it is needed | Current candidate files | Old material to inspect first | Benchmark apps unlocked |
| --- | --- | --- | --- | --- | --- |
| 03 | Relation rows and operator surfaces | Users need the basic vocabulary after hello/sorting: query id, candidate id, hit fact, distance fact, payload, group id, output row. | `v4_frontdoor_quickstart.py`, `operator_primitives.py` | `tools/_archive/history/examples_legacy_2026-06-27/reference_legacy/rtdl_language_reference.py`, `tools/_archive/history/legacy_project_archive_2026-06-24/docs/rtdl/programming_guide.md`, `tools/_archive/history/legacy_project_archive_2026-06-24/docs/rtdl/dsl_reference.md` | All apps. |
| 04 | Fixed-radius neighbor relation | Many apps begin as "find candidates within radius"; users must learn radius rows before clustering or nearest-neighbor apps. | `fixed_radius_neighbors.py` | `tools/_archive/history/examples_legacy_2026-06-27/reference_legacy/rtdl_fixed_radius_neighbors_reference.py`, `tools/_archive/history/examples_legacy_2026-06-27/current_legacy/features/neighbors/rtdl_fixed_radius_neighbors.py` | RTDBSCAN, RTNN, Hausdorff XHD. |
| 05 | Nearest witness and argmin continuation | Users need nearest as rows plus an argmin/ranked continuation, not as a black-box NN call. | `nearest_neighbor.py`, `ranked_summary_neighbors.py` | `tools/_archive/history/tutorial_archive/nearest_neighbor_workloads.md`, `tools/_archive/history/examples_legacy_2026-06-27/reference_legacy/rtdl_knn_rows_reference.py`, `tools/_archive/history/examples_legacy_2026-06-27/current_legacy/features/neighbors/rtdl_knn_rows.py` | RTNN, Hausdorff XHD, Contact manifold. |
| 06 | AABB predicates and spatial index rows | Users need point/range/box predicate rows before they can read spatial-index and broadphase examples. | `aabb_spatial_index_predicates.py`, `aabb_index_all_ops_count.py` | `tools/_archive/history/examples_legacy_2026-06-27/reference_legacy/rtdl_workload_reference.py`, `tools/_archive/history/legacy_project_archive_2026-06-24/tutorials/current/12_aabb_candidate_stream.md` | LibRTS spatial index, Contact manifold, Spatial RayJoin, Robot collision. |
| 07 | Point-in-polygon as RTDL rows | Polygon containment is a spatial relation lesson, not a full GIS algorithm course. Teach the RTDL row shape and boundary policy. | `point_in_polygon.py` | `tools/_archive/history/tutorial_archive/segment_polygon_workloads.md`, generated point-in-county plan bundles under `tools/_archive/history/legacy_project_archive_2026-06-24/examples/generated/plan_bundles/` | Spatial RayJoin, RayJoin paper reproduction support. |
| 08 | Line-segment intersection and spatial join | Users need broadphase pair rows plus exact segment refinement before Spatial RayJoin and polygon overlay. | `spatial_join_lsi.py`, `rayjoin_topology_intro.py` | `tools/_archive/history/tutorial_archive/segment_polygon_workloads.md`, `tools/_archive/history/examples_legacy_2026-06-27/current_legacy/features/spatial/rtdl_segment_polygon_hitcount.py`, `rtdl_segment_polygon_anyhit_rows.py`, `rtdl_polygon_pair_overlap_area_rows.py` | Spatial RayJoin, RayJoin paper reproduction support. |
| 09 | Ray/triangle hit rows | Ray streams, triangle scenes, any-hit rows, closest-hit rows, and hit flags are the core RTDL shape for several apps. | `ray_triangle_hits.py` | `tools/_archive/history/examples_legacy_2026-06-27/reference_legacy/rtdl_ray_tri_hitcount.py`, `tools/_archive/history/examples_legacy_2026-06-27/current_legacy/features/ray_queries/rtdl_ray_triangle_any_hit.py`, `rtdl_visibility_rows.py` | Triangle counting, Robot collision, RayDB-style query, Contact manifold. |
| 10 | Grouped continuations and reductions | Users need to see how relation rows become grouped counts, sums, minima, maxima, and weighted outputs. | `continuation_grouped_sum.py` | `tools/_archive/history/examples_legacy_2026-06-27/current_legacy/features/ray_queries/rtdl_reduce_rows.py`, `tools/_archive/history/examples_legacy_2026-06-27/current_legacy/features/database/rtdl_db_grouped_count.py`, `rtdl_db_grouped_sum.py` | Triangle counting, RayDB-style query, Barnes-Hut, RTDBSCAN summaries. |
| 11 | Component union from radius rows | RTDBSCAN needs the bridge from neighbor rows to graph edges to component labels. | `component_union_from_radius.py` | `tools/_archive/history/examples_legacy_2026-06-27/current_legacy/apps/ml/rtdl_dbscan_clustering_app.py`, old RTDBSCAN benchmark docs under `tools/_archive/history/legacy_project_archive_2026-06-24/examples/current/research_benchmarks/rt_dbscan/` | RTDBSCAN. |
| 12 | Bounded witness collection | Contact and collision workloads need "collect a bounded number of witnesses per query" plus overflow handling. | `bounded_witness_collection.py` | `tools/_archive/history/legacy_project_archive_2026-06-24/tutorials/current/15_contact_manifold_broadphase_boundary.md` | Contact manifold, Robot collision. |
| 13 | Aggregate frontier and weighted vector continuation | Barnes-Hut needs aggregate/frontier rows and a grouped weighted vector continuation. | `aggregate_frontier_rows.py` | `tools/_archive/history/examples_legacy_2026-06-27/current_legacy/apps/simulation/rtdl_barnes_hut_force_app.py`, Phoenix Barnes-Hut reports in `tools/_archive/history/legacy_project_archive_2026-06-24/docs/reports/phoenix_v3_m72_*barnes_hut*` | Barnes-Hut. |
| 14 | Graph-to-RT lowering for triangle counting | Triangle counting should be taught as graph/motif rows lowered to hit/count rows, not as a special hidden app kernel. | `triangle_counting_graph_lowering.py` | `tools/_archive/history/examples_legacy_2026-06-27/current_legacy/features/graph/rtdl_graph_triangle_count.py`, old triangle benchmark docs under `tools/_archive/history/legacy_project_archive_2026-06-24/examples/current/research_benchmarks/triangle_counting/` | Triangle counting. |
| 15 | Robot collision lowering | Users need the RTDL part: poses/links/segments become collision query rows and any-hit summaries. They do not need a robotics course. | `robot_collision_lowering.py` | `tools/_archive/history/examples_legacy_2026-06-27/current_legacy/apps/robotics/rtdl_robot_collision_screening_app.py`, `tools/_archive/history/legacy_project_archive_2026-06-24/tutorials/current/14_robot_collision_flag_stream.md` | Robot collision. |
| 16 | RayDB table-to-ray and payload rows | Users need table rows becoming ray payloads, hit rows, and grouped database-style outputs. | `raydb_table_to_ray.py` | `tools/_archive/history/tutorial_archive/db_workloads.md`, `tools/_archive/history/examples_legacy_2026-06-27/current_legacy/features/database/rtdl_db_conjunctive_scan.py`, `rtdl_db_grouped_count.py`, `rtdl_db_grouped_sum.py` | RayDB-style query. |
| 17 | Hausdorff composition from nearest witnesses | Hausdorff is a composition lesson: nearest witness rows -> directed max -> symmetric distance. | `hausdorff_distance_recipe.py` | `tools/_archive/history/examples_legacy_2026-06-27/current_legacy/partners/rtdl_hausdorff_user_cpp_continuation.py`, `tools/_archive/history/tutorial_archive/nearest_neighbor_workloads.md` | Hausdorff XHD. |
| 18 | Partner choice and device-array bridge | Users choose Torch, CuPy, Numba, or RTDL native explicitly. The tutorial must teach choice and boundaries, not hide partner migration as RTDL speed. | `partner_choices.py`, `fixed_radius_torch_device_arrays.py`, `ray_triangle_any_hit_weighted_sum_torch_device_arrays.py`, `point_group_nearest_witness_torch_device_arrays.py` | `tools/_archive/history/tutorial_archive/partner_anyhit.md`, `partner_optix_column_anyhit.md`, `tools/_archive/history/examples_legacy_2026-06-27/current_legacy/partners/rtdl_partner_anyhit.py`, `rtdl_control_apps_cupy_rawkernel.py` | All apps with partner routes. |
| 19 | Measurement phases and benchmark hygiene | Users must know setup, prepare, hot traversal, continuation, validation, and materialization before reading benchmark results. | `measure_phases.py` | `tools/_archive/history/examples_legacy_2026-06-27/current_legacy/getting_started/rtdl_prepared_measurement_demo.py`, `tools/_archive/history/legacy_project_archive_2026-06-24/docs/learn/prepared_execution_pattern.md`, `prepared_session_reuse.md` | All apps. |
| 20 | Callback planning boundary | Users with complex custom logic need to know what V4 can plan, what must be decomposed into known operators, and what is explicitly deferred. | `operator_callback_planning.py`, `custom_predicate_early_exit_planning.py` | `tools/_archive/history/tutorial_archive/partner_anyhit.md`, V4 three-tier design docs, old partner/action examples | Advanced users; keeps V4.0 boundaries honest. |
| 21 | Benchmark-app bridge | Only after the concepts above, show how each benchmark app combines the smaller lessons. | `benchmark_app_recipes.py`, `tutorials/current/07_benchmark_apps.md` | Old benchmark app docs under `tools/_archive/history/legacy_project_archive_2026-06-24/examples/current/research_benchmarks/`, current `examples/benchmark_apps/*/v4_app.py` | All 10 benchmark apps. |

## Benchmark-App Prerequisite Matrix

| Benchmark app | Stage 1 topics required before Stage 2 |
| --- | --- |
| RTDBSCAN | Relation rows; fixed-radius neighbors; component union; grouped summaries; measurement phases; partner choice. |
| RTNN | Relation rows; fixed-radius neighbors; nearest witness; ranked summary; measurement phases; partner choice. |
| Triangle counting | Relation rows; ray/triangle hits; grouped continuations; graph-to-RT lowering; measurement phases. |
| Robot collision | Relation rows; AABB predicates; ray/triangle or segment hit flags; bounded witnesses; robot collision lowering; measurement phases. |
| RayDB-style query | Relation rows; ray/triangle hits; table-to-ray payloads; grouped reductions; partner choice; measurement phases. |
| LibRTS spatial index | Relation rows; AABB predicates; prepared/index operation counts; measurement phases. |
| Contact manifold | Relation rows; AABB predicates; nearest/closest witness; bounded witnesses; contact lowering; measurement phases. |
| Spatial RayJoin | Relation rows; AABB predicates; point-in-polygon; line-segment intersection; topology/boundary policy; measurement phases. |
| Barnes-Hut | Relation rows; aggregate frontier; grouped weighted vector continuation; measurement phases. |
| Hausdorff XHD | Relation rows; fixed-radius threshold checks; nearest witness; Hausdorff composition; measurement phases. |

## Writing Rule For Each Future Topic

Before writing any remaining tutorial topic:

1. Open the current candidate tutorial program.
2. Open the listed old materials.
3. Decide what to inherit:
   - Keep old material when it shows a real RTDL lowering.
   - Modernize names, paths, and V4 public API references.
   - Remove internal goal numbers, reviewer language, release-defense wording,
     and stale version claims.
4. Ensure the lesson answers:
   - What is the user's source problem?
   - What RTDL relation rows are produced?
   - What operator or traversal produces those rows?
   - What continuation consumes them?
   - What output does the user get?
   - Which benchmark apps reuse this concept?
5. Validate the runnable program on Linux:
   - `PYTHONPATH=src:. python examples/tutorial_programs/<program>.py`
   - `PYTHONPATH=src:. python -m py_compile examples/tutorial_programs/<program>.py`
6. Do not close the topic until an external reviewer can confirm it teaches a
   concept rather than hiding logic behind a one-call wrapper.

## Non-Goals For Stage 1

- Do not teach the full algorithms for RTDBSCAN, RayJoin, Barnes-Hut, or any
  other benchmark app. Those are Stage 2 exams.
- Do not claim that the tutorial surface is complete merely because a script
  runs.
- Do not replace inherited working examples without a specific technical reason.
- Do not expose historical version debris to users; history remains in the
  archive.

## Exit Gate For Goal4786

Goal4786 is complete when this backlog is externally reviewed and accepted as a
valid Stage 1 plan. It does not authorize writing or closing the remaining
tutorial topics. The next implementation goal should take the first remaining
topic, inspect its old sources, rewrite the current tutorial if needed, run it
on Linux, and request review before closure.
