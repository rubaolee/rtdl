# Goal4782 Public Surface File Inventory

Status: `inventory_for_external_review`

This inventory is a mechanical companion to
`docs/engineering/goal4782_tutorial_public_surface_audit_2026-06-28.md`.
It records every current user-visible documentation/tutorial/example file found
under `README.md`, `docs/`, `tutorials/`, and `examples/`, excluding source
internals, tests, generated caches, and `tools/_archive/`.

Legend:
- `Pass`: no Goal4782 concern found.
- `Conditional`: public role is valid, but a later goal must inspect wording,
  teaching quality, links, or execution.
- `Blocked`: known user-facing problem; must be fixed before final tutorial
  release quality can be claimed.
- `Internal`: useful project/audit record, but not a beginner/user learning
  page.

## Top-Level, Docs, Learn, Research, And Review Surface

| File | Public role | Verdict | Required action |
| --- | --- | --- | --- |
| `README.md` | Main project entry | Conditional | Goal4805 final public wording/link audit. |
| `docs/README.md` | Documentation index | Conditional | Goal4805 final link audit. |
| `docs/app_level_benchmark_summary.md` | Public benchmark summary | Conditional | Goal4800/4805 performance wording audit. |
| `docs/current_v4_status.md` | Current release status | Conditional | Goal4805 remove any internal/process leakage. |
| `docs/public_documentation_map.md` | Public documentation map | Conditional | Goal4805 link consistency. |
| `docs/v4_engineering_summary.md` | Public engineering summary | Conditional | Goal4805 keep user-facing, not internal process. |
| `docs/v4_release_notes.md` | Public release notes | Conditional | Goal4805 bounded claims audit. |
| `docs/learn/README.md` | Learning index | Conditional | Goal4784 final ladder alignment. |
| `docs/learn/operator_catalog.md` | Operator reference | Conditional | Goal4789/4805 term consistency. |
| `docs/learn/partner_choice.md` | Partner policy reference | Conditional | Goal4789 partner wording audit. |
| `docs/learn/performance_wording.md` | Performance claim guide | Conditional | Goal4800 keep bounded and user-readable. |
| `docs/learn/source_tree_doctor.md` | User self-check guide | Conditional | Goal4805 verify current paths. |
| `docs/engineering/goal4782_public_surface_file_inventory_2026-06-28.md` | Audit inventory | Internal | Keep out of beginner path. |
| `docs/engineering/goal4782_tutorial_public_surface_audit_2026-06-28.md` | Audit record | Internal | Keep out of beginner path. |
| `docs/engineering/tutorial_programs_auditable_goals_2026-06-28.md` | Tutorial repair goal plan | Internal | Keep out of beginner path. |
| `docs/engineering/tutorial_programs_structure_and_content_plan_2026-06-28.md` | Tutorial structure plan | Internal | Keep out of beginner path. |
| `docs/reviews/call_for_review_goal4782_tutorial_public_surface_audit_2026-06-28.md` | External review packet | Internal | Keep out of beginner path. |
| `docs/research/rtdl_performance_principles.md` | Research/performance principles | Conditional | Goal4805 classify as research, not beginner tutorial. |
| `docs/research/rayjoin/rayjoin_exact_paper_reproduction_contract.md` | RayJoin paper reproduction contract | Conditional | Goal4803 paper-reproduction scope audit. |
| `docs/research/rayjoin/rayjoin_section57_polygon_overlay_v4_workload_status.md` | RayJoin 5.7 workload status | Conditional | Goal4803 paper-reproduction status audit. |

## Tutorial Markdown

| File | Public role | Verdict | Required action |
| --- | --- | --- | --- |
| `tutorials/README.md` | Tutorial top entry | Conditional | Goal4784 final ladder audit. |
| `tutorials/current/README.md` | Current tutorial index | Conditional | Goal4784 prerequisite/order audit. |
| `tutorials/current/01_first_run.md` | First RTDL run | Conditional | Goal4785 concept clarity audit. |
| `tutorials/current/02_hello_world.md` | Hello-world operator request | Conditional | Goal4785 no-black-box audit. |
| `tutorials/current/03_sorting_rows.md` | Sorting/rank/top-k lesson | Blocked | Goal4786 compare history and rewrite/accept carefully. |
| `tutorials/current/04_relations_and_operators.md` | Relations/operators lesson | Conditional | Goal4785 strengthen examples if needed. |
| `tutorials/current/05_prepare_run_continue.md` | Prepare/run/continue phases | Conditional | Goal4784/4794 phase prerequisite audit. |
| `tutorials/current/06_measure_a_program.md` | Measurement boundaries | Conditional | Goal4800 make user-facing, not reviewer-facing. |
| `tutorials/current/07_benchmark_apps.md` | Benchmark app bridge | Conditional | Goal4802 map apps to prerequisites. |
| `tutorials/current/08_choose_a_partner.md` | Partner lesson | Conditional | Goal4789 partner choice audit. |
| `tutorials/current/09_benchmark_harness_protocol.md` | Benchmark harness protocol | Conditional | Goal4800 ensure advanced/post-tutorial placement. |

## Tutorial Programs

| File | Public role | Verdict | Required action |
| --- | --- | --- | --- |
| `examples/tutorial_programs/README.md` | Tutorial-program index | Conditional | Goal4784 update after repairs. |
| `examples/tutorial_programs/__init__.py` | Package marker | Pass | None. |
| `examples/tutorial_programs/aabb_index_all_ops_count.py` | AABB prepared runner example | Conditional | Goal4804 advanced device/surface audit. |
| `examples/tutorial_programs/aabb_spatial_index_predicates.py` | AABB predicate lesson | Conditional | Goal4790 concept audit. |
| `examples/tutorial_programs/aggregate_frontier_rows.py` | Aggregate frontier lesson | Conditional | Goal4796 no-black-box audit. |
| `examples/tutorial_programs/benchmark_app_recipes.py` | Benchmark app recipe bridge | Conditional | Goal4802 ensure bridge, not fake tutorial. |
| `examples/tutorial_programs/bounded_witness_collection.py` | Bounded witness lesson | Conditional | Goal4798 witness semantics audit. |
| `examples/tutorial_programs/closest_hit_grouped_argmin_torch_device_arrays.py` | Device-array closest-hit argmin | Conditional | Goal4804 advanced surface audit. |
| `examples/tutorial_programs/component_union_from_radius.py` | Component union lesson | Conditional | Goal4795 relation-to-union audit. |
| `examples/tutorial_programs/contact_manifold_lowering.py` | Contact lowering lesson | Conditional | Goal4798 avoid physics-app tutorial drift. |
| `examples/tutorial_programs/continuation_grouped_sum.py` | Grouped continuation lesson | Conditional | Goal4794 relation-to-continuation audit. |
| `examples/tutorial_programs/custom_predicate_early_exit_planning.py` | Custom predicate planning | Conditional | Goal4801 callback boundary audit. |
| `examples/tutorial_programs/fixed_radius_neighbors.py` | Fixed-radius neighbor lesson | Conditional | Goal4787 concept audit. |
| `examples/tutorial_programs/fixed_radius_torch_device_arrays.py` | Device-array fixed-radius lesson | Conditional | Goal4804 advanced surface audit. |
| `examples/tutorial_programs/hausdorff_distance_recipe.py` | Hausdorff composition recipe | Conditional | Goal4802 app-bridge audit. |
| `examples/tutorial_programs/hello_world.py` | First operator request | Conditional | Goal4785 no-black-box audit. |
| `examples/tutorial_programs/measure_phases.py` | Measurement phase example | Conditional | Goal4800 user-facing measurement audit. |
| `examples/tutorial_programs/nearest_neighbor.py` | Nearest witness lesson | Conditional | Goal4788 no-do-all-wrapper audit. |
| `examples/tutorial_programs/operator_callback_planning.py` | Callback boundary planning | Conditional | Goal4801 boundary audit. |
| `examples/tutorial_programs/operator_primitives.py` | Operator primitive catalog | Conditional | Goal4785 avoid catalog-only teaching. |
| `examples/tutorial_programs/partner_choices.py` | Partner choice lesson | Conditional | Goal4789 partner policy audit. |
| `examples/tutorial_programs/point_group_nearest_witness_torch_device_arrays.py` | Device-array nearest witness | Conditional | Goal4804 advanced surface audit. |
| `examples/tutorial_programs/point_in_polygon.py` | PIP lowering lesson | Conditional | Goal4791 RTDL concept audit. |
| `examples/tutorial_programs/primitive_grouped_i64_reduction_torch_device_arrays.py` | Device-array grouped i64 reduction | Conditional | Goal4804 advanced surface audit. |
| `examples/tutorial_programs/ranked_summary_neighbors.py` | Ranked summary lesson | Conditional | Goal4797 rank/top-k audit. |
| `examples/tutorial_programs/ray_triangle_any_hit_flags_torch_device_arrays.py` | Device-array any-hit flags | Conditional | Goal4804 advanced surface audit. |
| `examples/tutorial_programs/ray_triangle_any_hit_weighted_sum_torch_device_arrays.py` | Device-array weighted sum | Conditional | Goal4804 continuation split audit. |
| `examples/tutorial_programs/ray_triangle_hits.py` | Ray/triangle relation lesson | Conditional | Goal4793 relation-row audit. |
| `examples/tutorial_programs/raydb_table_to_ray.py` | Table-to-ray lowering lesson | Conditional | Goal4799 concept audit. |
| `examples/tutorial_programs/rayjoin_topology_intro.py` | RayJoin topology bridge | Conditional | Goal4803 paper-reproduction bridge audit. |
| `examples/tutorial_programs/robot_collision_lowering.py` | Robot collision lowering lesson | Conditional | Goal4799 concept audit. |
| `examples/tutorial_programs/sorting_rows.py` | Sorting/rank/top-k lesson | Blocked | Goal4786 must compare old history before accepting changes. |
| `examples/tutorial_programs/spatial_join_lsi.py` | LSI/spatial join concept lesson | Conditional | Goal4792 concept audit. |
| `examples/tutorial_programs/triangle_counting_graph_lowering.py` | Triangle-count graph lowering | Conditional | Goal4799 concept audit. |
| `examples/tutorial_programs/v4_frontdoor_quickstart.py` | V4 front-door quickstart | Conditional | Goal4785 no-catalog-dump audit. |

## Benchmark Apps

| File | Public role | Verdict | Required action |
| --- | --- | --- | --- |
| `examples/benchmark_apps/README.md` | Benchmark app index | Conditional | Goal4783/4802 ensure clean category messaging. |
| `examples/benchmark_apps/__init__.py` | Package marker | Pass | None. |
| `examples/benchmark_apps/_support/__init__.py` | Support package marker | Pass | None. |
| `examples/benchmark_apps/_support/_repo_bootstrap.py` | Runtime support | Conditional | Goal4783 classify support vs user entry. |
| `examples/benchmark_apps/_support/rtdl_ann_candidate_app.py` | Support/legacy app component | Conditional | Goal4783 classify or archive if confusing. |
| `examples/benchmark_apps/_support/rtdl_barnes_hut_force_app.py` | Support/legacy app component | Conditional | Goal4783 classify or archive if confusing. |
| `examples/benchmark_apps/_support/rtdl_graph_triangle_count.py` | Support/legacy app component | Conditional | Goal4783 classify or archive if confusing. |
| `examples/benchmark_apps/_support/rtdl_language_reference.py` | Support reference | Conditional | Goal4783 classify or link intentionally. |
| `examples/benchmark_apps/_support/v4_public_entry.py` | Clean V4 benchmark helper | Conditional | Goal4783 keep as current support. |
| `examples/benchmark_apps/barnes_hut/__init__.py` | Package marker | Pass | None. |
| `examples/benchmark_apps/barnes_hut/v4_app.py` | Current benchmark entry | Conditional | Goal4802 run/link audit. |
| `examples/benchmark_apps/barnes_hut/rtdl_barnes_hut_benchmark_app.py` | Legacy/full harness | Blocked | Goal4783 hide/archive/label to prevent confusion. |
| `examples/benchmark_apps/contact_manifold/__init__.py` | Package marker | Pass | None. |
| `examples/benchmark_apps/contact_manifold/v4_app.py` | Current benchmark entry | Conditional | Goal4802 run/link audit. |
| `examples/benchmark_apps/contact_manifold/cpp_contact_witness_baseline.cpp` | Reference baseline | Conditional | Goal4783 label as reference-only. |
| `examples/benchmark_apps/contact_manifold/rtdl_contact_manifold_benchmark_app.py` | Legacy/full harness | Blocked | Goal4783 hide/archive/label to prevent confusion. |
| `examples/benchmark_apps/hausdorff_xhd/__init__.py` | Package marker | Pass | None. |
| `examples/benchmark_apps/hausdorff_xhd/v4_app.py` | Current benchmark entry | Conditional | Goal4802 run/link audit. |
| `examples/benchmark_apps/hausdorff_xhd/rtdl_hausdorff_distance_app.py` | Legacy/full harness | Blocked | Goal4783 hide/archive/label to prevent confusion. |
| `examples/benchmark_apps/hausdorff_xhd/rtdl_hausdorff_v2_function.py` | V2/reference helper | Blocked | Goal4783 hide/archive/label to prevent confusion. |
| `examples/benchmark_apps/hausdorff_xhd/rtdl_hausdorff_v2_language_lab.py` | V2/reference helper | Blocked | Goal4783 hide/archive/label to prevent confusion. |
| `examples/benchmark_apps/hausdorff_xhd/rtdl_hausdorff_v2_user_benchmark.py` | V2/reference helper | Blocked | Goal4783 hide/archive/label to prevent confusion. |
| `examples/benchmark_apps/librts_spatial_index/__init__.py` | Package marker | Pass | None. |
| `examples/benchmark_apps/librts_spatial_index/v4_app.py` | Current benchmark entry | Conditional | Goal4802 run/link audit. |
| `examples/benchmark_apps/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py` | Legacy/full harness | Blocked | Goal4783 hide/archive/label to prevent confusion. |
| `examples/benchmark_apps/raydb_style/__init__.py` | Package marker | Pass | None. |
| `examples/benchmark_apps/raydb_style/v4_app.py` | Current benchmark entry | Conditional | Goal4802 run/link audit. |
| `examples/benchmark_apps/raydb_style/rtdl_raydb_style_benchmark_app.py` | Legacy/full harness | Blocked | Goal4783 hide/archive/label to prevent confusion. |
| `examples/benchmark_apps/robot_collision/__init__.py` | Package marker | Pass | None. |
| `examples/benchmark_apps/robot_collision/v4_app.py` | Current benchmark entry | Conditional | Goal4802 run/link audit. |
| `examples/benchmark_apps/robot_collision/rtdl_robot_collision_benchmark_app.py` | Legacy/full harness | Blocked | Goal4783 hide/archive/label to prevent confusion. |
| `examples/benchmark_apps/rt_dbscan/__init__.py` | Package marker | Pass | None. |
| `examples/benchmark_apps/rt_dbscan/v4_app.py` | Current benchmark entry | Conditional | Goal4802 run/link audit. |
| `examples/benchmark_apps/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py` | Legacy/full harness | Blocked | Goal4783 hide/archive/label to prevent confusion. |
| `examples/benchmark_apps/rtnn/__init__.py` | Package marker | Pass | None. |
| `examples/benchmark_apps/rtnn/v4_app.py` | Current benchmark entry | Conditional | Goal4802 run/link audit. |
| `examples/benchmark_apps/rtnn/rtdl_rtnn_benchmark_app.py` | Legacy/full harness | Blocked | Goal4783 hide/archive/label to prevent confusion. |
| `examples/benchmark_apps/spatial_rayjoin/__init__.py` | Package marker | Pass | None. |
| `examples/benchmark_apps/spatial_rayjoin/v4_app.py` | Current benchmark entry | Conditional | Goal4802 run/link audit. |
| `examples/benchmark_apps/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py` | V2/reference harness | Blocked | Goal4783 hide/archive/label to prevent confusion. |
| `examples/benchmark_apps/triangle_counting/__init__.py` | Package marker | Pass | None. |
| `examples/benchmark_apps/triangle_counting/v4_app.py` | Current benchmark entry | Conditional | Goal4802 run/link audit. |
| `examples/benchmark_apps/triangle_counting/rt_graph_contract.md` | Reference contract | Conditional | Goal4783 label as reference-only. |
| `examples/benchmark_apps/triangle_counting/rtdl_triangle_counting_benchmark_app.py` | Legacy/full harness | Blocked | Goal4783 hide/archive/label to prevent confusion. |

## Paper Reproduction Apps

| File | Public role | Verdict | Required action |
| --- | --- | --- | --- |
| `examples/paper_reproduction/README.md` | Paper reproduction index | Conditional | Goal4803 confirm category boundaries. |
| `examples/paper_reproduction/paper_reproduction_scope.md` | Paper reproduction scope | Conditional | Goal4803 scope wording audit. |
| `examples/paper_reproduction/rayjoin.py` | RayJoin reproduction entry | Conditional | Goal4803 real-data/status audit. |
| `examples/paper_reproduction/rt_barneshut.py` | RT-BarnesHut reproduction entry | Conditional | Goal4803 scope/status audit. |

## Root Examples Surface

| File | Public role | Verdict | Required action |
| --- | --- | --- | --- |
| `examples/README.md` | Examples root index | Conditional | Goal4783 ensure exactly three categories. |
| `examples/__init__.py` | Package marker | Pass | None. |

## Goal4782 Result

This inventory confirms that Goal4782 should not be closed as release-quality
work. It may only close as an audit record if an external reviewer agrees that:

1. all required public-surface files are represented here;
2. blocked files are honestly identified;
3. remediation is deferred to Goal4783-4808 instead of hidden.
