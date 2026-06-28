# V4 Final Public File Audit - 2026-06-28

## Scope

This pass audits the files a normal user is likely to see from the repository
front door:

- `README.md`, `pyproject.toml`, `requirements.txt`, and `VERSION`;
- every file under `docs/`;
- every file under `tutorials/`;
- every file under `examples/`.

`src/`, `tests/`, `scripts/`, and `tools/` are maintainer/developer areas, so
they are covered by release gates but are not treated as learner-facing files
in this table.

## Overall Judgment

Public state is release-clean. The visible learning path is coherent:

1. start at the front page;
2. read current V4 docs;
3. run tutorial programs;
4. inspect clean `v4_app.py` benchmark entries;
5. use paper-reproduction wrappers only for paper-labeled routes.

No user-visible file in this scope required a corrective edit during this pass.
Compatibility wrapper files with older route names remain acceptable because
the clean V4 entrypoints and README files direct users to `v4_app.py`; the
wrappers preserve runnable reproduction access without becoming the learning
front door.

## Per-File Reflection

| File | Best-state judgment | Reflection |
| --- | --- | --- |
| `README.md` | Yes | Best as the front page: one V4 import, clear user paths, bounded performance wording. |
| `pyproject.toml` | Yes | Best as package metadata: V4.0.0 version and source-tree package description are current. |
| `requirements.txt` | Yes | Best as minimal dependency file; no stale release language. |
| `VERSION` | Yes | Best as single version marker for V4.0.0. |
| `docs/README.md` | Yes | Best as short current docs index; no historical maze. |
| `docs/v4_release_notes.md` | Yes | Best as public release notes with bounded claims and correct reading path. |
| `docs/current_v4_status.md` | Yes | Best after wording cleanup: user-facing status, not internal process language. |
| `docs/app_level_benchmark_summary.md` | Yes | Best as the full app-level table; no blanket speedup claim. |
| `docs/v4_engineering_summary.md` | Yes | Best as maintainer-oriented but public-safe architecture summary. |
| `docs/public_documentation_map.md` | Yes | Best as a short navigation map for current public docs. |
| `docs/learn/README.md` | Yes | Best as learning reference index. |
| `docs/learn/operator_catalog.md` | Yes | Best as operator catalog with partner scope and denominators. |
| `docs/learn/partner_choice.md` | Yes | Best as explicit partner-choice guide. |
| `docs/learn/performance_wording.md` | Yes | Best as user-facing guidance for reading ratios honestly. |
| `docs/learn/source_tree_doctor.md` | Yes | Best as checkout sanity guide. |
| `tutorials/README.md` | Yes | Best as tutorial-area pointer to current V4 path. |
| `tutorials/current/README.md` | Yes | Best as ordered learner path from RT idea to benchmark apps. |
| `tutorials/current/01_first_run.md` | Yes | Best as first conceptual entry; no old-version leakage. |
| `tutorials/current/02_hello_world.md` | Yes | Best as first runnable RTDL example. |
| `tutorials/current/03_sorting_rows.md` | Yes | Best as relation-row sorting bridge. |
| `tutorials/current/04_relations_and_operators.md` | Yes | Best as relation/operator programming model explanation. |
| `tutorials/current/05_prepare_run_continue.md` | Yes | Best as prepare/run/continue lifecycle lesson. |
| `tutorials/current/06_measure_a_program.md` | Yes | Best as measurement guide without release-defense language. |
| `tutorials/current/07_benchmark_apps.md` | Yes | Best after concept-to-surface bridge addition; teaches all 10 apps progressively. |
| `tutorials/current/08_choose_a_partner.md` | Yes | Best as partner-choice tutorial with bounded custom-logic guidance. |
| `tutorials/current/09_benchmark_harness_protocol.md` | Yes | Best as measurement protocol bridge from tutorial to harness. |
| `examples/README.md` | Yes | Best as examples map: tutorial programs, benchmark apps, paper reproduction. |
| `examples/__init__.py` | Yes | Best as package marker; harmless and current. |
| `examples/tutorial_programs/README.md` | Yes | Best as runnable tutorial-program index with advanced surface bridge. |
| `examples/tutorial_programs/__init__.py` | Yes | Best as package marker; harmless and current. |
| `examples/tutorial_programs/hello_world.py` | Yes | Best as minimal import/planner hello-world. |
| `examples/tutorial_programs/v4_frontdoor_quickstart.py` | Yes | Best as current public surface quickstart. |
| `examples/tutorial_programs/sorting_rows.py` | Yes | Best after direct-run fix; teaches row ordering and continuations. |
| `examples/tutorial_programs/operator_primitives.py` | Yes | Best as primitive/operator concept bridge. |
| `examples/tutorial_programs/partner_choices.py` | Yes | Best as explicit partner-choice runnable example. |
| `examples/tutorial_programs/fixed_radius_neighbors.py` | Yes | Best as hand-built radius-neighbor concept example. |
| `examples/tutorial_programs/nearest_neighbor.py` | Yes | Best as visible nearest-witness relation example. |
| `examples/tutorial_programs/ray_triangle_hits.py` | Yes | Best as basic ray/triangle hit relation example. |
| `examples/tutorial_programs/continuation_grouped_sum.py` | Yes | Best as continuation/reduction concept example. |
| `examples/tutorial_programs/measure_phases.py` | Yes | Best as phase measurement lesson. |
| `examples/tutorial_programs/point_in_polygon.py` | Yes | Best as PIP relation tutorial. |
| `examples/tutorial_programs/spatial_join_lsi.py` | Yes | Best as spatial join/LSI concept tutorial. |
| `examples/tutorial_programs/aggregate_frontier_rows.py` | Yes | Best as Barnes-Hut aggregate-frontier lowering tutorial. |
| `examples/tutorial_programs/component_union_from_radius.py` | Yes | Best as RTDBSCAN-style component continuation tutorial. |
| `examples/tutorial_programs/ranked_summary_neighbors.py` | Yes | Best as RTNN ranked-summary concept tutorial. |
| `examples/tutorial_programs/bounded_witness_collection.py` | Yes | Best as bounded witness/overflow tutorial. |
| `examples/tutorial_programs/contact_manifold_lowering.py` | Yes | Best as contact-manifold lowering tutorial. |
| `examples/tutorial_programs/triangle_counting_graph_lowering.py` | Yes | Best as triangle-counting graph-to-RT lowering tutorial. |
| `examples/tutorial_programs/robot_collision_lowering.py` | Yes | Best as robot collision lowering tutorial. |
| `examples/tutorial_programs/hausdorff_distance_recipe.py` | Yes | Best as Hausdorff threshold/witness composition tutorial. |
| `examples/tutorial_programs/raydb_table_to_ray.py` | Yes | Best as RayDB-style table-to-ray tutorial. |
| `examples/tutorial_programs/rayjoin_topology_intro.py` | Yes | Best as RayJoin topology tutorial. |
| `examples/tutorial_programs/aabb_spatial_index_predicates.py` | Yes | Best as AABB predicate tutorial. |
| `examples/tutorial_programs/benchmark_app_recipes.py` | Yes | Best as recipe map from tutorial concepts to all benchmark apps. |
| `examples/tutorial_programs/operator_callback_planning.py` | Yes | Best as supported/deferred callback planning demo. |
| `examples/tutorial_programs/custom_predicate_early_exit_planning.py` | Yes | Best as constrained Numba predicate example with clear boundary. |
| `examples/tutorial_programs/fixed_radius_torch_device_arrays.py` | Yes | Best after teaching-context addition; not a black-box surface call. |
| `examples/tutorial_programs/point_group_nearest_witness_torch_device_arrays.py` | Yes | Best after teaching-context addition; maps to NN/Hausdorff concepts. |
| `examples/tutorial_programs/ray_triangle_any_hit_flags_torch_device_arrays.py` | Yes | Best after teaching-context addition; maps to ray-hit concept. |
| `examples/tutorial_programs/ray_triangle_any_hit_weighted_sum_torch_device_arrays.py` | Yes | Best after teaching-context addition; maps hits to weighted continuation. |
| `examples/tutorial_programs/primitive_grouped_i64_reduction_torch_device_arrays.py` | Yes | Best after teaching-context addition; maps primitive payloads to grouped reduction. |
| `examples/tutorial_programs/closest_hit_grouped_argmin_torch_device_arrays.py` | Yes | Best after teaching-context addition; maps contact/witness concepts to surface. |
| `examples/tutorial_programs/aabb_index_all_ops_count.py` | Yes | Best after teaching-context addition; maps AABB predicates to prepared runner. |
| `examples/benchmark_apps/README.md` | Yes | Best as clean 10-app V4 entrypoint map. |
| `examples/benchmark_apps/__init__.py` | Yes | Best as package marker; harmless and current. |
| `examples/benchmark_apps/_support/__init__.py` | Yes | Best as support package marker; not a learner entry. |
| `examples/benchmark_apps/_support/_repo_bootstrap.py` | Yes | Best as helper for direct script execution from fresh clone. |
| `examples/benchmark_apps/_support/v4_public_entry.py` | Yes | Best as shared clean `v4_app.py` renderer and harness bridge. |
| `examples/benchmark_apps/_support/rtdl_language_reference.py` | Yes | Best as support implementation for benchmark apps; not the front door. |
| `examples/benchmark_apps/_support/rtdl_ann_candidate_app.py` | Yes | Best as RTNN support code retained behind V4 entrypoint. |
| `examples/benchmark_apps/_support/rtdl_barnes_hut_force_app.py` | Yes | Best as Barnes-Hut support code retained behind V4 entrypoint. |
| `examples/benchmark_apps/_support/rtdl_graph_triangle_count.py` | Yes | Best as triangle-counting support code retained behind V4 entrypoint. |
| `examples/benchmark_apps/rt_dbscan/__init__.py` | Yes | Best as app package marker. |
| `examples/benchmark_apps/rt_dbscan/v4_app.py` | Yes | Best as clean current RTDBSCAN entrypoint. |
| `examples/benchmark_apps/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py` | Yes | Acceptable as full-harness compatibility wrapper; README directs learners to `v4_app.py`. |
| `examples/benchmark_apps/rtnn/__init__.py` | Yes | Best as app package marker. |
| `examples/benchmark_apps/rtnn/v4_app.py` | Yes | Best as clean current RTNN entrypoint. |
| `examples/benchmark_apps/rtnn/rtdl_rtnn_benchmark_app.py` | Yes | Acceptable as full-harness compatibility wrapper behind `v4_app.py`. |
| `examples/benchmark_apps/triangle_counting/__init__.py` | Yes | Best as app package marker. |
| `examples/benchmark_apps/triangle_counting/v4_app.py` | Yes | Best as clean current triangle-counting entrypoint. |
| `examples/benchmark_apps/triangle_counting/rtdl_triangle_counting_benchmark_app.py` | Yes | Acceptable as full-harness compatibility wrapper behind `v4_app.py`. |
| `examples/benchmark_apps/triangle_counting/rt_graph_contract.py` | Yes | Best as app support contract used by triangle-counting route. |
| `examples/benchmark_apps/robot_collision/__init__.py` | Yes | Best as app package marker. |
| `examples/benchmark_apps/robot_collision/v4_app.py` | Yes | Best as clean current robot-collision entrypoint. |
| `examples/benchmark_apps/robot_collision/rtdl_robot_collision_benchmark_app.py` | Yes | Acceptable as full-harness compatibility wrapper behind `v4_app.py`. |
| `examples/benchmark_apps/raydb_style/__init__.py` | Yes | Best as app package marker. |
| `examples/benchmark_apps/raydb_style/v4_app.py` | Yes | Best as clean current RayDB-style entrypoint. |
| `examples/benchmark_apps/raydb_style/rtdl_raydb_style_benchmark_app.py` | Yes | Acceptable as full-harness compatibility wrapper behind `v4_app.py`. |
| `examples/benchmark_apps/librts_spatial_index/__init__.py` | Yes | Best as app package marker. |
| `examples/benchmark_apps/librts_spatial_index/v4_app.py` | Yes | Best as clean current LibRTS spatial-index entrypoint. |
| `examples/benchmark_apps/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py` | Yes | Acceptable as full-harness compatibility wrapper behind `v4_app.py`. |
| `examples/benchmark_apps/contact_manifold/__init__.py` | Yes | Best as app package marker. |
| `examples/benchmark_apps/contact_manifold/v4_app.py` | Yes | Best as clean current contact-manifold entrypoint. |
| `examples/benchmark_apps/contact_manifold/rtdl_contact_manifold_benchmark_app.py` | Yes | Acceptable as full-harness compatibility wrapper behind `v4_app.py`. |
| `examples/benchmark_apps/contact_manifold/cpp_contact_witness_baseline.cpp` | Yes | Acceptable as baseline source accompanying the benchmark app; not a learner front door. |
| `examples/benchmark_apps/spatial_rayjoin/__init__.py` | Yes | Best as app package marker. |
| `examples/benchmark_apps/spatial_rayjoin/v4_app.py` | Yes | Best as clean current Spatial RayJoin entrypoint. |
| `examples/benchmark_apps/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py` | Yes | Acceptable as named full-harness compatibility wrapper; `v4_app.py` is the current user entry. |
| `examples/benchmark_apps/barnes_hut/__init__.py` | Yes | Best as app package marker. |
| `examples/benchmark_apps/barnes_hut/v4_app.py` | Yes | Best as clean current Barnes-Hut entrypoint. |
| `examples/benchmark_apps/barnes_hut/rtdl_barnes_hut_benchmark_app.py` | Yes | Acceptable as full-harness compatibility wrapper behind `v4_app.py`. |
| `examples/benchmark_apps/hausdorff_xhd/__init__.py` | Yes | Best as app package marker. |
| `examples/benchmark_apps/hausdorff_xhd/v4_app.py` | Yes | Best as clean current Hausdorff XHD entrypoint. |
| `examples/benchmark_apps/hausdorff_xhd/rtdl_hausdorff_distance_app.py` | Yes | Best as current app support implementation for Hausdorff route. |
| `examples/benchmark_apps/hausdorff_xhd/rtdl_hausdorff_v2_function.py` | Yes | Acceptable as compatibility wrapper for the inherited threshold/witness harness; not the current learning entry. |
| `examples/benchmark_apps/hausdorff_xhd/rtdl_hausdorff_v2_language_lab.py` | Yes | Acceptable as compatibility wrapper for reproduction/harness use; `v4_app.py` remains the user entry. |
| `examples/benchmark_apps/hausdorff_xhd/rtdl_hausdorff_v2_user_benchmark.py` | Yes | Acceptable as compatibility wrapper for reproduction/harness use; `v4_app.py` remains the user entry. |
| `examples/paper_reproduction/README.md` | Yes | Best as paper-oriented path explanation, with Windows and Linux commands. |
| `examples/paper_reproduction/paper_reproduction_scope.md` | Yes | Best as boundary note separating paper-oriented wrappers from 10-app suite. |
| `examples/paper_reproduction/rt_barneshut.py` | Yes | Best after direct-run fix; explains route by default and forwards only on request. |
| `examples/paper_reproduction/rayjoin.py` | Yes | Best after direct-run fix; explains route by default and forwards only on request. |

## Automated Checks Used With This Audit

- `scripts/v4_universe_audit.py --strict-release`
- public forbidden-language scan over `README.md`, `docs/`, `tutorials/`, and
  `examples/`
- direct wrapper runs for paper-reproduction entrypoints
- public docs/package/clean checkout unit tests
- fresh Linux clone of `v4.0.0` with tutorial, benchmark-entry, paper-wrapper,
  universe, and clean-checkout probes

Final result: no corrective public edit required by the per-file reflection.
