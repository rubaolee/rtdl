# Goal4782 Tutorial Public Surface Audit

Status: `audit_complete_blocked_for_remediation`

Goal4782 audits the current public tutorial/docs/examples surface. It does not
claim the tutorial surface is release-quality. The audit result is blocked for
remediation because several files are useful but not yet at the required
teaching standard.

## Goal-Level Decision Check

1. Did I make a stupid decision?
   - Risk was high: starting edits before auditing would repeat the previous
     failure mode.
2. If yes, what actions would make it stupid?
   - Treating runnable JSON examples as teaching quality.
   - Treating planner calls as equivalent to showing RTDL lowering.
   - Hiding old benchmark harness files while they remain visible in examples.
3. Is there another path?
   - Yes: audit first, record each file, then fix one goal at a time.
4. Can I try a different path that solves the real problem?
   - Yes: Goal4782 is audit-only; implementation starts only after review.

## Scope

Included:
- top-level current docs and learn docs;
- `tutorials/current/*.md`;
- `examples/README.md`;
- `examples/tutorial_programs/*.py` and README;
- `examples/benchmark_apps/README.md` and app-visible files;
- `examples/paper_reproduction/*.py` and docs;
- newly written tutorial-goal planning docs.

Excluded:
- `src/` implementation internals;
- tests except where they define public gates;
- `tools/_archive/` history.

## Summary Findings

| Severity | Finding | Impact | Required follow-up |
| --- | --- | --- | --- |
| P0 | Tutorial quality is not uniformly proven. | We cannot claim the tutorial surface teaches RTDL end to end. | Complete Goal4783-4808. |
| P0 | `examples/tutorial_programs/sorting_rows.py` has an unreviewed working-tree edit from the current agent. | It must not be treated as accepted old work. | Goal4786 must compare against old history and decide keep/revert/rewrite. |
| P1 | Several tutorial programs are useful but too much like planner demos or JSON payload dumps. | Users may run them without learning the lowering. | Add explicit lowering narrative and output fields. |
| P1 | `examples/benchmark_apps/*/rtdl_*` legacy harness files remain next to `v4_app.py`. | Users can open old implementation files and get confused about current entrypoints. | Goal4783 must decide hide/archive or clearly label. |
| P1 | Tutorial ladder jumps from basic rows to full benchmark recipes quickly. | Learning path exists but is not yet a strict curriculum. | Goal4784 and Goal4802. |
| P2 | Advanced device-array examples are useful but rely on `teaching_context` conventions rather than a uniform tutorial template. | Review burden is higher. | Goal4804 per-file audit table. |

## Public Docs Audit

| File | Keep public? | Current verdict | Why | Follow-up goal |
| --- | --- | --- | --- | --- |
| `README.md` | Yes | Needs spot audit | Main entrypoint; not fully inspected in this goal. | Goal4785+ |
| `docs/README.md` | Yes | Conditional pass | Current-doc index role is valid. | Goal4805 |
| `docs/current_v4_status.md` | Yes | Needs wording audit | User-facing status page; must avoid internal framing. | Goal4805 |
| `docs/v4_release_notes.md` | Yes | Needs wording audit | Public release notes; must stay bounded. | Goal4805 |
| `docs/v4_engineering_summary.md` | Yes | Needs wording audit | Useful but can drift toward internal engineering. | Goal4805 |
| `docs/app_level_benchmark_summary.md` | Yes | Needs strict audit | Performance wording is sensitive. | Goal4805 |
| `docs/public_documentation_map.md` | Yes | Conditional pass | Useful public map; must stay link-clean. | Goal4805 |
| `docs/learn/README.md` | Yes | Conditional pass | Correct learning index role. | Goal4784 |
| `docs/learn/operator_catalog.md` | Yes | Conditional pass | Needed for current operator surfaces. | Goal4789 |
| `docs/learn/partner_choice.md` | Yes | Conditional pass | Needed for partner boundaries. | Goal4789 |
| `docs/learn/performance_wording.md` | Yes | Conditional pass | Needed to prevent overclaiming. | Goal4800 |
| `docs/learn/source_tree_doctor.md` | Yes | Conditional pass | Useful for user self-checks. | Goal4805 |
| `docs/engineering/tutorial_programs_auditable_goals_2026-06-28.md` | No, engineering only | Keep non-public | Internal planning/audit target, not beginner docs. | Goal4806 |
| `docs/engineering/tutorial_programs_structure_and_content_plan_2026-06-28.md` | No, engineering only | Keep non-public | Structure plan, not user tutorial. | Goal4806 |
| `docs/research/rtdl_performance_principles.md` | Maybe | Needs classification | Research-facing, not beginner-facing. | Goal4805 |
| `docs/research/rayjoin/rayjoin_exact_paper_reproduction_contract.md` | Paper docs only | Conditional pass | Contract doc, not tutorial. | Goal4803 |
| `docs/research/rayjoin/rayjoin_section57_polygon_overlay_v4_workload_status.md` | Paper docs only | Conditional pass | Workload status, not tutorial. | Goal4803 |

## Tutorial Markdown Audit

| File | Keep public? | Current verdict | Reason | Follow-up goal |
| --- | --- | --- | --- | --- |
| `tutorials/README.md` | Yes | Needs audit | Top tutorial entry. | Goal4784 |
| `tutorials/current/README.md` | Yes | Conditional pass | Good intent and order, but ladder needs stronger concept coverage. | Goal4784 |
| `tutorials/current/01_first_run.md` | Yes | Conditional pass | Explains RTDL pattern and RT cores at high level. | Goal4785 |
| `tutorials/current/02_hello_world.md` | Yes | Conditional pass | Planner-first lesson is appropriate. | Goal4785 |
| `tutorials/current/03_sorting_rows.md` | Yes | Blocked | Existing text is closer to row sorting than true RTDL sorting/rank lowering. | Goal4786 |
| `tutorials/current/04_relations_and_operators.md` | Yes | Conditional pass | Good relation/operator explanation; may need stronger examples. | Goal4785 |
| `tutorials/current/05_prepare_run_continue.md` | Yes | Conditional pass | Correct phase structure; advanced examples need prerequisites. | Goal4784 |
| `tutorials/current/06_measure_a_program.md` | Yes | Conditional pass | Correct measurement boundaries. | Goal4800 |
| `tutorials/current/07_benchmark_apps.md` | Yes | Needs expansion | Good bridge intent; must map all apps to prerequisite concepts precisely. | Goal4802 |
| `tutorials/current/08_choose_a_partner.md` | Yes | Conditional pass | Correct explicit partner framing. | Goal4789 |
| `tutorials/current/09_benchmark_harness_protocol.md` | Yes | Conditional pass | Useful after concepts; not a beginner lesson. | Goal4800 |

## Tutorial Program Audit

| File | Concept | Current verdict | Reason | Follow-up goal |
| --- | --- | --- | --- | --- |
| `examples/tutorial_programs/README.md` | Tutorial program index | Conditional pass | Good structure; should reflect final audited ladder. | Goal4784 |
| `examples/tutorial_programs/__init__.py` | Package marker | Pass | Not a teaching file. | None |
| `hello_world.py` | First operator request | Conditional pass | Simple planner lesson is valid. | Goal4785 |
| `v4_frontdoor_quickstart.py` | Public V4 front door | Conditional pass | Shows surfaces; ensure not just catalog dumping. | Goal4785 |
| `sorting_rows.py` | Sorting/rank/top-k | Blocked | Current working tree is unreviewed; must verify old history and teach true lowering. | Goal4786 |
| `operator_primitives.py` | Operator catalog mapping | Conditional pass | Useful map, but may be too catalog-like. | Goal4785 |
| `partner_choices.py` | Partner policy | Conditional pass | Explicit partner choice is valid. | Goal4789 |
| `fixed_radius_neighbors.py` | Radius-neighbor rows | Likely pass | Shows candidate checks, neighbor rows, threshold continuation. | Goal4787 |
| `nearest_neighbor.py` | Nearest witness | Likely pass | Shows candidate rows and argmin continuation. | Goal4788 |
| `ray_triangle_hits.py` | Ray/triangle hit rows | Likely pass | Shows hit tests and relation rows. | Goal4793 |
| `continuation_grouped_sum.py` | Grouped continuation | Conditional pass | Needs ensure continuation is tied to prior relation rows. | Goal4794 |
| `measure_phases.py` | Measurement phases | Conditional pass | Good phase framing; verify public clarity. | Goal4800 |
| `point_in_polygon.py` | PIP lowering | Conditional pass | Shows candidate/exact containment; avoid teaching app algorithm too deeply. | Goal4791 |
| `spatial_join_lsi.py` | LSI/spatial join | Conditional pass | Good broadphase/refinement shape. | Goal4792 |
| `aggregate_frontier_rows.py` | Aggregate frontier | Conditional pass | Needed for Barnes-Hut; must avoid internal residency language. | Goal4796 |
| `component_union_from_radius.py` | Component union | Conditional pass | Good RTDBSCAN bridge. | Goal4795 |
| `ranked_summary_neighbors.py` | Ranked summaries | Conditional pass | Needs rank/top-k clarity. | Goal4797 |
| `bounded_witness_collection.py` | Bounded witnesses | Conditional pass | Good contact/witness bridge. | Goal4798 |
| `contact_manifold_lowering.py` | Contact lowering | Conditional pass | Must remain RTDL concept, not physics tutorial. | Goal4798 |
| `triangle_counting_graph_lowering.py` | Triangle counting lowering | Conditional pass | Must show graph-to-hit relation clearly. | Goal4799 |
| `robot_collision_lowering.py` | Collision lowering | Conditional pass | Must avoid becoming robotics tutorial. | Goal4799 |
| `hausdorff_distance_recipe.py` | Hausdorff composition | Conditional pass | Good composition candidate; verify no black box. | Goal4802 |
| `raydb_table_to_ray.py` | Table-to-ray lowering | Conditional pass | Strong RTDL concept; verify output clarity. | Goal4799 |
| `rayjoin_topology_intro.py` | Topology/boundary policy | Conditional pass | Useful bridge; RayJoin paper app remains exam, not lesson. | Goal4803 |
| `aabb_spatial_index_predicates.py` | AABB predicates | Likely pass | Shows point/range relation rows. | Goal4790 |
| `benchmark_app_recipes.py` | Benchmark bridge | Conditional pass | Good bridge; must stay explanatory, not JSON/fake tutorial. | Goal4802 |
| `operator_callback_planning.py` | Callback boundary | Conditional pass | Shows deferred complex callbacks; needs more lowering framing. | Goal4801 |
| `custom_predicate_early_exit_planning.py` | Custom predicate boundary | Conditional pass | Useful boundary example. | Goal4801 |
| `fixed_radius_torch_device_arrays.py` | Device-array fixed-radius | Conditional pass | Advanced surface; must point back to concept program. | Goal4804 |
| `point_group_nearest_witness_torch_device_arrays.py` | Device-array nearest witness | Conditional pass | Advanced surface; verify teaching context. | Goal4804 |
| `ray_triangle_any_hit_flags_torch_device_arrays.py` | Device-array hit flags | Conditional pass | Advanced surface; verify teaching context. | Goal4804 |
| `ray_triangle_any_hit_weighted_sum_torch_device_arrays.py` | Device-array weighted sum | Conditional pass | Advanced surface; verify relation + continuation split. | Goal4804 |
| `primitive_grouped_i64_reduction_torch_device_arrays.py` | Device-array grouped i64 | Conditional pass | Advanced surface; verify concept prerequisite links. | Goal4804 |
| `closest_hit_grouped_argmin_torch_device_arrays.py` | Device-array closest-hit argmin | Conditional pass | Advanced surface; verify witness semantics. | Goal4804 |
| `aabb_index_all_ops_count.py` | AABB prepared runner | Conditional pass | Advanced surface; verify no hardware surprise in dry-run. | Goal4804 |

## Benchmark Apps Audit

| File/group | Keep public? | Current verdict | Reason | Follow-up goal |
| --- | --- | --- | --- | --- |
| `examples/benchmark_apps/README.md` | Yes | Conditional pass | Correctly points to `v4_app.py`. | Goal4783 |
| `examples/benchmark_apps/*/v4_app.py` | Yes | Conditional pass | Clean current entrypoints. | Goal4802 |
| `examples/benchmark_apps/_support/*.py` | No direct beginner entry | Needs classification | Support code is visible under examples. | Goal4783 |
| `examples/benchmark_apps/*/rtdl_*benchmark*.py` | Not as first-contact docs | Blocked for public clarity | Legacy/full harness files sit beside clean `v4_app.py`. | Goal4783 |
| `examples/benchmark_apps/contact_manifold/cpp_contact_witness_baseline.cpp` | Reference only | Needs classification | May confuse beginners if not labeled. | Goal4783 |
| `examples/benchmark_apps/hausdorff_xhd/rtdl_hausdorff_v2_*.py` | Legacy/reference only | Blocked for public clarity | V2-labeled files remain in public example tree. | Goal4783 |
| `examples/benchmark_apps/triangle_counting/rt_graph_contract.md` | Reference only | Conditional pass | Needs clear current/reference label. | Goal4783 |

## Paper Reproduction Audit

| File | Keep public? | Current verdict | Reason | Follow-up goal |
| --- | --- | --- | --- | --- |
| `examples/paper_reproduction/README.md` | Yes | Conditional pass | Correct category separation; has current unreviewed edits. | Goal4803 |
| `examples/paper_reproduction/paper_reproduction_scope.md` | Yes | Conditional pass | Correct exam/workload framing; has current unreviewed edits. | Goal4803 |
| `examples/paper_reproduction/rt_barneshut.py` | Yes | Conditional pass | Paper workload wrapper. | Goal4803 |
| `examples/paper_reproduction/rayjoin.py` | Yes | Conditional pass | Section 5.7 wrapper/protocol exists; needs real-data run later. | Goal4803 |

## Coverage Matrix

| Required concept | Existing program | Audit result |
| --- | --- | --- |
| hello world / first request | `hello_world.py`, `v4_frontdoor_quickstart.py` | Conditional pass |
| relation rows and candidates | multiple concept programs | Conditional pass |
| sorting/rank/top-k | `sorting_rows.py`, `ranked_summary_neighbors.py` | Blocked pending Goal4786/4797 |
| nearest neighbor | `nearest_neighbor.py` | Likely pass |
| fixed-radius neighbors | `fixed_radius_neighbors.py` | Likely pass |
| PIP | `point_in_polygon.py` | Conditional pass |
| LSI/spatial join | `spatial_join_lsi.py` | Conditional pass |
| AABB predicates | `aabb_spatial_index_predicates.py` | Likely pass |
| ray/triangle hits | `ray_triangle_hits.py` | Likely pass |
| grouped reductions | `continuation_grouped_sum.py` | Conditional pass |
| component union | `component_union_from_radius.py` | Conditional pass |
| aggregate frontier | `aggregate_frontier_rows.py` | Conditional pass |
| partner choice | `partner_choices.py` | Conditional pass |
| measurement phases | `measure_phases.py` | Conditional pass |
| callback boundaries | `operator_callback_planning.py`, `custom_predicate_early_exit_planning.py` | Conditional pass |

## Required Next Goals

Do not skip directly to implementation:

1. Goal4783 must clean/clarify the three example categories and visible legacy
   benchmark files.
2. Goal4784 must finalize the learning ladder.
3. Goal4786 must handle sorting carefully by comparing old history before
   accepting any current edit.
4. Goal4804 must produce the full per-source teaching audit after individual
   fixes.
5. Goal4805 must rerun commands, snippets, and link gates.

## Non-Authorization

This audit does not authorize:
- claiming the tutorial surface is release-quality;
- closing Goal4782 without external review;
- accepting the current `sorting_rows.py` working-tree edit;
- publishing a new tutorial tag;
- hiding the benchmark-app legacy-file issue.

