# Goal4794 final V4 tutorial surface audit

Date: 2026-06-28

## Purpose

This is the final audit for the V4 tutorial surface. It checks whether the
current tutorials and tutorial programs are in a coherent publishable state:

1. each file belongs in the current user path,
2. each file teaches the V4 RTDL programming model correctly,
3. old process/history material is not visible in the tutorial path,
4. all tutorial commands and public gates run on Windows and local Linux.

## Summary Verdict

The V4 tutorial surface is complete pending external review.

Current tutorial path:

- `tutorials/current/README.md`
- `tutorials/current/01_first_run.md` through `tutorials/current/24_benchmark_app_bridge.md`

Old replaced tutorial pages are out of the current path and archived under:

- `tools/_archive/history/tutorial_archive/goal4788_replaced_current_pages_2026-06-28/`
- `tools/_archive/history/tutorial_archive/goal4789_replaced_current_pages_2026-06-28/`

Forbidden public-surface scan over `tutorials/current`, `examples/tutorial_programs`,
`examples/README.md`, and `docs/public_documentation_map.md` found no stale
goal/review/process/V3-current language.

## Tutorial Page Audit

| File | Should be current? | Content verdict | Historical/error leakage | Action/reflection |
| --- | --- | --- | --- | --- |
| `tutorials/current/README.md` | Yes | Correct tutorial order, 01-24, and learner outcomes. | None found. | Best current index for a learner. |
| `tutorials/current/01_first_run.md` | Yes | Explains what RTDL is before APIs. | None found. | Appropriate first conceptual page. |
| `tutorials/current/02_hello_world.md` | Yes | Restores the original simple hello-world kernel path. | None found. | Keeps first lesson simple instead of shocking users. |
| `tutorials/current/03_sorting_rows.md` | Yes | Restores sorting as values -> segment geometry -> hit rows -> rank. | None found. | Good second lesson because it teaches lowering, not a sort helper. |
| `tutorials/current/04_relations_and_operators.md` | Yes | Explains rows, fields, operators, and V4 planning boundary. | None found. | Good bridge from kernel programs to surfaces. |
| `tutorials/current/05_fixed_radius_neighbors.md` | Yes | Teaches radius-neighbor rows before V4 fixed-radius surface. | None found. | Correct NN/DBSCAN prerequisite. |
| `tutorials/current/06_nearest_witness.md` | Yes | Teaches candidate distance rows and argmin/nearest witness output. | None found. | Correct Hausdorff/contact prerequisite. |
| `tutorials/current/07_aabb_predicates.md` | Yes | Teaches AABB point/range/intersection rows. | None found. | Correct spatial-index and broadphase prerequisite. |
| `tutorials/current/08_point_in_polygon.md` | Yes | Teaches polygon containment as rows and boundary policy. | None found. | Keeps app algorithm details minimal. |
| `tutorials/current/09_line_segment_intersection_spatial_join.md` | Yes | Teaches broadphase pairs and LSI refinement rows. | None found. | Correct spatial join foundation. |
| `tutorials/current/10_ray_triangle_hits.md` | Yes | Teaches ray/triangle any-hit and closest-hit row shapes. | None found. | Correct ray-hit foundation. |
| `tutorials/current/11_grouped_continuations.md` | Yes | Teaches grouped reductions over emitted rows. | None found. | Correct continuation foundation. |
| `tutorials/current/12_component_union_from_radius.md` | Yes | Teaches fixed-radius rows into component labels. | None found. | Correct RTDBSCAN-style bridge. |
| `tutorials/current/13_bounded_witness_collection.md` | Yes | Teaches witness rows, bounded slots, and overflow validation. | None found. | Correct contact/closest-witness bridge. |
| `tutorials/current/14_aggregate_frontier_rows.md` | Yes | Relation-first aggregate frontier and weighted continuation. | None found. | Honest: does not fake a missing public `@rt.kernel` aggregate predicate. |
| `tutorials/current/15_ranked_summary_neighbors.md` | Yes | Teaches top-k/ranked summary as app-owned scoring over rows. | None found. | Correctly separates scoring from V4 planning. |
| `tutorials/current/16_contact_manifold_lowering.md` | Yes | Teaches broadphase pair rows and bounded witness rows. | None found. | Good app-lowering example without teaching a physics engine. |
| `tutorials/current/17_graph_triangle_counting_lowering.md` | Yes | Teaches graph two-hop rows to witness rows and grouped counts. | None found. | Correctly avoids a hidden triangle-counting app kernel. |
| `tutorials/current/18_robot_collision_lowering.md` | Yes | Teaches sampled pose/link rows to any-hit flags. | None found. | Clear collision contract; no full robotics claim. |
| `tutorials/current/19_raydb_table_to_ray.md` | Yes | Teaches table rows as ray payload rows and grouped aggregates. | None found. | Good bridge from data rows to RT rows. |
| `tutorials/current/20_hausdorff_composition.md` | Yes | Teaches nearest-witness rows plus directed/symmetric max reductions. | None found. | Correctly separates exact witness from threshold decision. |
| `tutorials/current/21_partner_choice_device_arrays.md` | Yes | Teaches partner choice after relation shape is known. | None found. | Correctly frames partners as execution policies. |
| `tutorials/current/22_measurement_phases.md` | Yes | Teaches setup, hot relation, continuation, validation phases. | None found. | Prevents misleading timing comparisons. |
| `tutorials/current/23_callback_planning_boundary.md` | Yes | Teaches recognized operators vs constrained predicates vs deferred action callbacks. | None found. | Keeps arbitrary callback claims out of V4.0. |
| `tutorials/current/24_benchmark_app_bridge.md` | Yes | Connects concepts to benchmark apps without becoming the first tutorial. | None found. | Correct Stage 2 doorway. |

## Tutorial Program Audit

| File | Should be current? | Content verdict | Historical/error leakage | Action/reflection |
| --- | --- | --- | --- | --- |
| `examples/tutorial_programs/README.md` | Yes | Correct command index, order, and advanced bridge table. | None found. | Best current program map. |
| `examples/tutorial_programs/__init__.py` | Yes | Package marker only. | None found. | Harmless and appropriate. |
| `examples/tutorial_programs/hello_world.py` | Yes | Minimal first RTDL kernel example. | None found. | Correct first runnable program. |
| `examples/tutorial_programs/sorting_rows.py` | Yes | Restored sorting-lowering example. | None found. | Correctly teaches RT transformation rather than a sort helper. |
| `examples/tutorial_programs/operator_primitives.py` | Yes | Introduces relation/operator/continuation vocabulary. | None found. | Good conceptual bridge. |
| `examples/tutorial_programs/v4_frontdoor_quickstart.py` | Yes | Shows V4 public entry after concepts. | None found. | Kept as orientation, not first lesson. |
| `examples/tutorial_programs/fixed_radius_neighbors.py` | Yes | Kernel/V4 dual mode for radius rows. | None found. | Correct kernel-first structure. |
| `examples/tutorial_programs/nearest_neighbor.py` | Yes | Kernel/V4 dual mode for nearest witness. | None found. | Correct argmin foundation. |
| `examples/tutorial_programs/ranked_summary_neighbors.py` | Yes | Relation/V4/visible modes for ranked top-k. | None found. | Correctly keeps scoring app-owned. |
| `examples/tutorial_programs/aabb_spatial_index_predicates.py` | Yes | AABB relation/V4 modes. | None found. | Correct broadphase foundation. |
| `examples/tutorial_programs/aabb_index_all_ops_count.py` | Yes | Advanced dry-run surface bridge. | None found. | Appropriate after AABB lesson. |
| `examples/tutorial_programs/point_in_polygon.py` | Yes | Kernel/V4 modes for containment rows. | None found. | Correct PIP foundation. |
| `examples/tutorial_programs/spatial_join_lsi.py` | Yes | Kernel/V4 modes for LSI/spatial join rows. | None found. | Correct spatial-join foundation. |
| `examples/tutorial_programs/rayjoin_topology_intro.py` | Yes | Topology and boundary policy support. | None found. | Useful as advanced spatial-join context. |
| `examples/tutorial_programs/ray_triangle_hits.py` | Yes | Kernel/V4 modes for ray/triangle hit rows. | None found. | Correct ray foundation. |
| `examples/tutorial_programs/continuation_grouped_sum.py` | Yes | Kernel/V4 modes for grouped reductions. | None found. | Correct continuation foundation. |
| `examples/tutorial_programs/component_union_from_radius.py` | Yes | Kernel/V4/visible modes for component union. | None found. | Correct RTDBSCAN-style bridge. |
| `examples/tutorial_programs/bounded_witness_collection.py` | Yes | Kernel/V4/visible modes for bounded witnesses. | None found. | Correct contact/nearest bridge. |
| `examples/tutorial_programs/aggregate_frontier_rows.py` | Yes | Relation/V4/visible modes for aggregate frontier. | None found. | Honest relation-first treatment. |
| `examples/tutorial_programs/contact_manifold_lowering.py` | Yes | Relation/V4/visible modes for contact manifold. | None found. | Good composition example. |
| `examples/tutorial_programs/triangle_counting_graph_lowering.py` | Yes | Relation/V4/visible modes for graph triangle counting. | None found. | Good graph-to-RT lowering example. |
| `examples/tutorial_programs/robot_collision_lowering.py` | Yes | Relation/V4/visible modes for sampled robot collision. | None found. | Clear scoped collision example. |
| `examples/tutorial_programs/raydb_table_to_ray.py` | Yes | Relation/V4/visible modes for table-to-ray payload rows. | None found. | Good database-style bridge. |
| `examples/tutorial_programs/hausdorff_distance_recipe.py` | Yes | Relation/V4/visible modes for Hausdorff composition. | None found. | Correct witness/threshold separation. |
| `examples/tutorial_programs/partner_choices.py` | Yes | Relation/V4/visible modes for explicit partner choice. | None found. | Correctly treats partners as execution policy. |
| `examples/tutorial_programs/measure_phases.py` | Yes | Relation/V4/visible modes for phase measurement. | None found. | Correct timing hygiene lesson. |
| `examples/tutorial_programs/operator_callback_planning.py` | Yes | Shows tier2, scalar-callback, and complex-callback planning outcomes. | None found. | Correct boundary example. |
| `examples/tutorial_programs/custom_predicate_early_exit_planning.py` | Yes | Shows narrow constrained predicate path and rejected action-shaped mutation. | None found. | Useful advanced boundary example; retained for catalog gate compatibility. |
| `examples/tutorial_programs/benchmark_app_recipes.py` | Yes | Maps 10 benchmark apps to operator requests, partners, and row shapes. | None found. | Correct Stage 2 bridge, not first tutorial. |
| `examples/tutorial_programs/fixed_radius_torch_device_arrays.py` | Yes | Advanced dry-run/device-array bridge for radius rows. | None found. | Appropriate after fixed-radius concept. |
| `examples/tutorial_programs/point_group_nearest_witness_torch_device_arrays.py` | Yes | Advanced bridge for nearest witness columns. | None found. | Appropriate after nearest/ranked lessons. |
| `examples/tutorial_programs/ray_triangle_any_hit_flags_torch_device_arrays.py` | Yes | Advanced bridge for ray hit flags. | None found. | Appropriate after ray hit lesson. |
| `examples/tutorial_programs/ray_triangle_any_hit_weighted_sum_torch_device_arrays.py` | Yes | Advanced bridge for weighted hit continuation. | None found. | Appropriate after ray hits and grouped continuations. |
| `examples/tutorial_programs/primitive_grouped_i64_reduction_torch_device_arrays.py` | Yes | Advanced bridge for primitive grouped reductions. | None found. | Appropriate after triangle/grouped lessons. |
| `examples/tutorial_programs/closest_hit_grouped_argmin_torch_device_arrays.py` | Yes | Advanced bridge for grouped closest witness. | None found. | Appropriate after bounded witness/contact lessons. |

## Validation

### Windows workspace

Command:

```powershell
py -m unittest tests.v4_goal4640_public_docs_cleanup_test tests.v4_frontdoor_test tests.v4_goal4643_publication_decision_test
```

Result:

```text
Ran 21 tests in 85.405s
OK
```

The Windows Python process printed the known local prefix warning on subprocess
runs, but all commands exited successfully.

### Local Linux clean-copy simulation

Host: `192.168.1.20`

The workspace was copied to `/tmp/rtdl_goal4794_final_tutorials` and run as a
clean user checkout with `PYTHONPATH=src:.`.

Representative tutorial commands:

```bash
PYTHONPATH=src:. python3 examples/tutorial_programs/hello_world.py
PYTHONPATH=src:. python3 examples/tutorial_programs/sorting_rows.py
PYTHONPATH=src:. python3 examples/tutorial_programs/fixed_radius_neighbors.py --mode both
PYTHONPATH=src:. python3 examples/tutorial_programs/ray_triangle_hits.py --mode both
PYTHONPATH=src:. python3 examples/tutorial_programs/aggregate_frontier_rows.py --mode both
PYTHONPATH=src:. python3 examples/tutorial_programs/partner_choices.py --mode both
PYTHONPATH=src:. python3 examples/tutorial_programs/measure_phases.py --mode both
PYTHONPATH=src:. python3 examples/tutorial_programs/benchmark_app_recipes.py
PYTHONPATH=src:. python3 -m unittest tests.v4_goal4640_public_docs_cleanup_test tests.v4_frontdoor_test tests.v4_goal4643_publication_decision_test
```

Result:

```text
Ran 21 tests in 32.223s
OK
```

## Final Reflection

This tutorial surface is in its best current state for V4.0 because it now has:

- a single current tutorial ladder,
- a clean separation between tutorial programs, benchmark apps, and paper reproduction apps,
- kernel/relation-first teaching before V4 wrapper calls,
- explicit partner and callback boundaries,
- no visible old tutorial path competing with the current path,
- Windows and Linux validation.

Remaining future work, if desired, should be additive polish after user reading,
not a blocker for declaring the current tutorial set complete.
