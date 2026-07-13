# Goal4885 Public Surface Audit After RayJoin Section 5.7 Page

Date: 2026-07-03

Status: completed local audit, pending external review.

## Objective

After adding the reader-facing RayJoin Section 5.7 bounded reproduction page,
re-audit the user-visible surface so first-time users see a clean v2.14 product
surface rather than internal work logs, experimental V3/V4 material, reviewer
process, or stale goal-specific paths.

Scope checked:

- `README.md`
- public Markdown under `docs/`
- public Markdown under `tutorials/`
- public Markdown under `examples/`
- example code strings that were exposed by the leak scan
- primitive catalog generation source, because the catalog is generated

## Fixes Made

| Area | Problem found | Action |
| --- | --- | --- |
| Root front page | `README.md` still advertised `exp-project-1/` in the repository layout table. | Removed the explicit row so the first-user path stays focused on v2.14 docs, tutorials, examples, and the optional history archive. |
| Application catalog | RTNN entry pointed at a historical `goal2348` runner. | Replaced it with the current public benchmark entry point under `examples/current/research_benchmarks/rtnn/`. |
| Prepared execution tutorial | Example opened a `history/internal_docs/docs_reports/goal3511...json` file. | Replaced it with a neutral user-owned artifact path: `artifacts/my_prepared_run_summary.json`. |
| Research benchmark index | The README sent users to `history/internal_docs/`. | Reworded it to the top-level `history/` archive only. |
| Example code metadata | GPU-RMQ, triangle-counting, and RTNN example code embedded internal evidence paths. | Replaced those strings with public docs/release package references or a general top-level history archive note. |
| RayJoin app-author guidance | It still described Section 5.7 overlay as only the old `2/8` exact subset. | Updated it to the current bounded claim: two available full-stream pairs plus two current-source representative Lakes/Parks pairs; no full hidden-input `8/8` claim. |
| RT-vs-Embree release table | Overlay performance row did not point to the new correctness page and could be misread as the whole current RayJoin status. | Added an explicit link to the bounded reproduction page while preserving the performance row's exact-subset boundary. |
| Primitive catalog | Generated discovery references still resolved to `history/internal_docs` or stale `docs/reports`/`docs/research` locations. | Updated `src/rtdsl/primitive_hierarchy.py` reference paths to public feature/boundary docs and regenerated `docs/rtdl_primitive_catalog.md`. |
| Current-doc test | A maintenance test still expected the old `docs/reports` location. | Pointed the test to the archived report and stopped treating that historical report's file count as today's dynamic count. |

## Validation

Commands run from repository root:

```powershell
rg -n "Goal\d+|goal\d+|Claude|Gemini|Antigravity|Codex|verdict|call_for_review|review debt|Phoenix|future/v4|history/internal|docs/reviews|docs/handoff|docs/rebuild|V4\.0|V3\.0|exp-project-1|docs/reports" README.md docs tutorials examples -S
```

Result: no matches.

```powershell
# Local Markdown link checker over README.md, docs/, tutorials/, examples/
```

Result: checked `89` Markdown files; all relative links exist.

```powershell
py -3 scripts\generate_rtdl_primitive_catalog.py --check
```

Result: primitive catalog up to date. The Python launcher printed the known
environment warning `Could not find platform independent libraries <prefix>`,
but the check exited successfully.

```powershell
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal4857_planar_map_point_location_public_front_door_test tests.goal4866_rayjoin_section57_output_contract_test tests.goal2102_examples_directory_organization_audit_test tests.goal4274_current_doc_recheck_test
```

Result: `Ran 17 tests ... OK`. The same Python launcher warning appeared before
test output.

```powershell
$env:PYTHONPATH='src;.'
py -3 scripts\rtdl_source_tree_doctor.py
py -3 examples\current\getting_started\rtdl_hello_world.py
```

Result: source-tree doctor core checks passed; optional native/partner warnings
were reported for unconfigured local CuPy, Numba, OptiX, and Embree paths.
Hello world printed `hello, world`.

## Per-File Audit

Legend:

- Keep: file belongs in the current user-visible surface.
- Clean: content is current, link-clean, and free of internal process leaks.
- Updated: this goal changed or regenerated the file.
- Watch: file is acceptable now but should be rechecked when related evidence changes.

| File | Should be here? | Content correct? | Historical/error leak? | Action |
| --- | --- | --- | --- | --- |
| `README.md` | Keep | Correct v2.14 front door | No | Updated: removed explicit experimental-project row. |
| `docs/README.md` | Keep | Current docs index | No | No change. |
| `docs/app_engine_support_matrix.md` | Keep | Current support matrix | No | No change. |
| `docs/app_example_quickstart.md` | Keep | Current quickstart | No | No change. |
| `docs/application_catalog.md` | Keep | Current app catalog | No | Updated: RTNN entry now points to current public benchmark app. |
| `docs/backend_maturity.md` | Keep | Current backend guidance | No | No change. |
| `docs/capability_boundaries.md` | Keep | Current boundaries | No | No change. |
| `docs/current_architecture.md` | Keep | Current architecture | No | No change. |
| `docs/current_main_support_matrix.md` | Keep | Current support surface | No | No change. |
| `docs/partner_acceleration_boundaries.md` | Keep | Current partner boundary | No | No change. |
| `docs/performance_model.md` | Keep | Current performance framing | No | No change. |
| `docs/public_documentation_map.md` | Keep | Current navigation map | No | No change. |
| `docs/quick_tutorial.md` | Keep | Current quick intro | No | No change. |
| `docs/release_facing_examples.md` | Keep | Current examples guide | No | No change. |
| `docs/rtdl_feature_guide.md` | Keep | Current feature guide | No | No change. |
| `docs/rtdl_primitive_catalog.md` | Keep | Current generated catalog | No | Regenerated after public reference-path cleanup. |
| `docs/runtime_overhead_architecture.md` | Keep | Current overhead explanation | No | No change. |
| `docs/versioning.md` | Keep | Current versioning rule | No | No change. |
| `docs/vision.md` | Keep | Current vision | No | No change. |
| `docs/features/README.md` | Keep | Current feature index | No | No change. |
| `docs/features/db_workloads/README.md` | Keep | Current DB workload feature docs | No | No change. |
| `docs/features/engine_support_matrix.md` | Keep | Current engine support | No | No change. |
| `docs/features/fixed_radius_neighbors/README.md` | Keep | Current fixed-radius feature docs | No | No change. |
| `docs/features/knn_rows/README.md` | Keep | Current KNN-row feature docs | No | No change. |
| `docs/features/lsi/README.md` | Keep | Current LSI feature docs | No | No change. |
| `docs/features/overlay/README.md` | Keep | Current overlay feature docs | No | No change. |
| `docs/features/pip/README.md` | Keep | Current PIP feature docs | No | No change. |
| `docs/features/point_nearest_segment/README.md` | Keep | Current nearest-segment feature docs | No | No change. |
| `docs/features/polygon_pair_overlap_area_rows/README.md` | Keep | Current polygon-pair row docs | No | No change. |
| `docs/features/polygon_set_jaccard/README.md` | Keep | Current Jaccard feature docs | No | No change. |
| `docs/features/ray_tri_anyhit/README.md` | Keep | Current ray/triangle any-hit docs | No | No change. |
| `docs/features/ray_tri_hitcount/README.md` | Keep | Current ray/triangle hit-count docs | No | No change. |
| `docs/features/reduce_rows/README.md` | Keep | Current reduction docs | No | No change. |
| `docs/features/segment_polygon_anyhit_rows/README.md` | Keep | Current segment/polygon any-hit docs | No | No change. |
| `docs/features/segment_polygon_hitcount/README.md` | Keep | Current segment/polygon count docs | No | No change. |
| `docs/features/visibility_rows/README.md` | Keep | Current visibility-row docs | No | No change. |
| `docs/learn/README.md` | Keep | Current learning index | No | No change. |
| `docs/learn/benchmark_evidence_index.md` | Keep | Current benchmark evidence navigation | No | Already cleaned in Goal4884; rechecked here. |
| `docs/learn/benchmark_partner_reference_matrix.md` | Keep | Current partner matrix | No | No change. |
| `docs/learn/current_claim_boundaries.md` | Keep | Current claim boundaries | No | No change. |
| `docs/learn/partner_choice_for_custom_logic.md` | Keep | Current partner guide | No | No change. |
| `docs/learn/prepared_execution_pattern.md` | Keep | Current prepared-execution teaching | No | Updated: removed internal artifact example. |
| `docs/learn/prepared_session_reuse.md` | Keep | Current prepared-session docs | No | No change. |
| `docs/learn/primitive_discovery_workflow.md` | Keep | Current primitive discovery docs | No | No change. |
| `docs/learn/programming_surfaces.md` | Keep | Current programming-surface explanation | No | No change. |
| `docs/learn/rt_core_evidence_matrix.md` | Keep | Current evidence matrix | No | No change. |
| `docs/learn/source_tree_doctor.md` | Keep | Current setup diagnostics | No | No change. |
| `docs/learn/v2_14_app_author_implementation_strategy.md` | Keep | Current app-author guidance | No | Updated: RayJoin Section 5.7 boundary now matches bounded reproduction page. |
| `docs/release_reports/v2_14/README.md` | Keep | Current v2.14 release package index | No | Link target rechecked. |
| `docs/release_reports/v2_14/public_rt_vs_embree_comparison.md` | Keep | Current row-scoped performance evidence | No | Updated: overlay row links to bounded correctness page and keeps performance boundary narrow. |
| `docs/release_reports/v2_14/public_wording_boundaries.md` | Keep | Current wording boundary | No | No change. |
| `docs/release_reports/v2_14/rayjoin_section57_bounded_reproduction.md` | Keep | Current bounded RayJoin reproduction readout | No | Rechecked after link and leak scan. |
| `docs/rtdl/README.md` | Keep | Current RTDL language-doc index | No | No change. |
| `docs/rtdl/dsl_reference.md` | Keep | Current DSL reference | No | No change. |
| `docs/rtdl/ir_and_lowering.md` | Keep | Current IR/lowering reference | No | No change. |
| `docs/rtdl/itre_app_model.md` | Keep | Current ITRE/app-model docs | No | No change. |
| `docs/rtdl/llm_authoring_guide.md` | Keep | Current authoring guide | No | No change. |
| `docs/rtdl/programming_guide.md` | Keep | Current programming guide | No | No change. |
| `docs/rtdl/workload_cookbook.md` | Keep | Current workload cookbook | No | No change. |
| `tutorials/README.md` | Keep | Current tutorial entry | No | No change. |
| `tutorials/current/README.md` | Keep | Current tutorial track | No | No change. |
| `tutorials/current/01_source_tree_first_run.md` | Keep | Current first-run lesson | No | No change. |
| `tutorials/current/02_kernel_shape_and_backends.md` | Keep | Current kernel/backend lesson | No | No change. |
| `tutorials/current/03_primitives_and_discovery.md` | Keep | Current primitive lesson | No | No change. |
| `tutorials/current/04_python_app_structure.md` | Keep | Current app-structure lesson | No | No change. |
| `tutorials/current/05_partner_columns_cupy_numba.md` | Keep | Current partner-column lesson | No | No change. |
| `tutorials/current/06_prepared_execution_measurement.md` | Keep | Current measurement lesson | No | No change. |
| `tutorials/current/07_benchmark_app_python_rtdl_partner.md` | Keep | Current benchmark-app lesson | No | No change. |
| `tutorials/current/08_spatial_join_rayjoin_reference.md` | Keep | Current RayJoin-reference lesson | No | No change. |
| `examples/README.md` | Keep | Current examples entry | No | No change. |
| `examples/current/README.md` | Keep | Current examples catalog | No | No change. |
| `examples/current/apps/README.md` | Keep | Current app examples index | No | No change. |
| `examples/current/features/README.md` | Keep | Current feature examples index | No | No change. |
| `examples/current/getting_started/README.md` | Keep | Current getting-started examples | No | No change. |
| `examples/current/learner_apps/README.md` | Keep | Current learner-app index | No | No change. |
| `examples/current/learner_apps/gpu_rmq/README.md` | Keep | Current learner-app page | No | No change. |
| `examples/current/partners/README.md` | Keep | Current partner examples index | No | No change. |
| `examples/current/research_benchmarks/README.md` | Keep | Current benchmark examples index | No | Updated: removed direct internal-docs pointer. |
| `examples/current/research_benchmarks/barnes_hut/README.md` | Keep | Current Barnes-Hut benchmark page | No | No change. |
| `examples/current/research_benchmarks/contact_manifold/README.md` | Keep | Current contact-manifold benchmark page | No | No change. |
| `examples/current/research_benchmarks/hausdorff_xhd/README.md` | Keep | Current Hausdorff benchmark page | No | No change. |
| `examples/current/research_benchmarks/librts_spatial_index/README.md` | Keep | Current LibRTS-style benchmark page | No | No change. |
| `examples/current/research_benchmarks/raydb_style/README.md` | Keep | Current RayDB-style benchmark page | No | No change. |
| `examples/current/research_benchmarks/robot_collision/README.md` | Keep | Current robot-collision benchmark page | No | No change. |
| `examples/current/research_benchmarks/rt_dbscan/README.md` | Keep | Current RT-DBSCAN benchmark page | No | No change. |
| `examples/current/research_benchmarks/rtnn/README.md` | Keep | Current RTNN benchmark page | No | No change. |
| `examples/current/research_benchmarks/spatial_rayjoin/README.md` | Keep | Current spatial-RayJoin benchmark page | No | No change. |
| `examples/current/research_benchmarks/triangle_counting/README.md` | Keep | Current triangle-counting benchmark page | No | No change. |
| `examples/reference/README.md` | Keep | Current reference-example boundary | No | No change. |

## Example Code Metadata Audit

The public leak scan also inspected `examples/` source files. It found internal
path strings in three example modules:

- `examples/current/learner_apps/gpu_rmq/rtdl_gpu_rmq_learner_app.py`
- `examples/current/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py`
- `examples/current/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py`

Those strings were replaced with public docs/release-package references or a
general top-level history archive note. No runtime behavior was changed.

## Exit Label

`completed_public_surface_audit_after_rayjoin_page__leaks_zero__links_zero__tests_passed__pending_antigravity_review`
