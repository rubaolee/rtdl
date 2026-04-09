# v0.3 Release Surface Audit And Revision

Date: 2026-04-09

## Scope

This audit reviewed the public `v0.3` release surface with four questions:

1. do user-facing file names and locations read cleanly, without leaking
   internal goal numbering or process history
2. is the `examples/` tree organized in a way a fresh user can understand
3. do the front-door docs teach enough to start successfully
4. do the live docs help users more than they confuse them

The scope for this audit was:

- root front-door docs
- tutorial and feature-home docs
- release-facing example index
- public `examples/` layout
- the public workload-reference import chain
- dependent runtime/tests/scripts that needed path updates
- historical reports only where moved-path references would otherwise break

This audit did **not** attempt to rewrite the full historical goal archive into
a user-facing set. Historical goal docs remain preserved as archive material.

## Main Decisions

### 1. Public reference naming must not leak `goal10`

The public reference module was renamed from:

- `examples/reference/rtdl_goal10_reference.py`

to:

- `examples/reference/rtdl_workload_reference.py`

This removes the main internal-goal-name leak from the public example chain.

### 2. Generated examples should not clutter the examples root

Preserved generated artifacts were moved under:

- `examples/generated/`

This keeps the `examples/` root readable for new users while still preserving
generated bundles for inspection and handoff workflows.

### 3. Front-door docs should teach the example layout explicitly

The front-door docs now explain the intended directory split:

- top-level `examples/` for first-run paths
- `examples/reference/` for readable kernels
- `examples/generated/` for preserved generated output
- `examples/visual_demo/` for RTDL-plus-Python demos
- `examples/internal/` for preserved internal history

### 4. User-facing docs should use clone-real commands and relative links

The reviewed live docs now avoid:

- machine-local absolute path links
- internal-goal file names in the public workload chain
- awkward “flagship” language in the front-door surface where “main public
  artifact” or “main release story” is clearer

## File Ledger

Each file below records the review outcome for this audit.

| File | Audience | Decision | Action |
|---|---|---|---|
| `README.md` | public front door | revised | clarified example-layout story, replaced “flagship” wording with cleaner public wording, and kept the hidden-star demo as the main visual entry |
| `docs/README.md` | public docs index | revised | reordered start-here links around tutorial/examples/features and added the explicit public examples layout summary |
| `docs/quick_tutorial.md` | public tutorial | revised | added a clearer teaching progression explaining what the first three commands each teach and pointed readers to `examples/README.md` for directory orientation |
| `docs/release_facing_examples.md` | public example index | revised | kept the canonical release-facing examples, added a note about preserved generated examples under `examples/generated/`, and preserved the hidden-star demo as the main app-style example |
| `docs/current_milestone_qa.md` | live status doc | revised | removed awkward direct linking to imported Windows handoff artifact files and replaced them with cleaner source/artifact-location wording; softened “flagship” wording |
| `docs/rtdl_feature_guide.md` | public orientation guide | revised | replaced machine-local links with repo-relative links for the canonical workload-home section |
| `docs/features/README.md` | public feature index | revised | converted feature-home links and supporting links to repo-relative form |
| `docs/features/lsi/README.md` | public feature doc | revised | converted user-facing links to repo-relative form |
| `docs/features/pip/README.md` | public feature doc | revised | converted user-facing links to repo-relative form |
| `docs/features/overlay/README.md` | public feature doc | revised | converted user-facing links to repo-relative form |
| `docs/features/point_nearest_segment/README.md` | public feature doc | revised | converted links to repo-relative form and replaced “flagship live branch story” wording with “main release story” |
| `docs/features/segment_polygon_hitcount/README.md` | public feature doc | revised | converted links and commands to clone-real form; now points to the renamed public workload-reference module |
| `docs/features/segment_polygon_anyhit_rows/README.md` | public feature doc | revised | converted links and commands to clone-real form; now points to the renamed public workload-reference module |
| `docs/features/polygon_pair_overlap_area_rows/README.md` | public feature doc | revised | converted links and commands to clone-real form |
| `docs/features/polygon_set_jaccard/README.md` | public feature doc | revised | converted links to repo-relative form and fixed the generate-only command to include `PYTHONPATH=src:.` |
| `examples/README.md` | public example tree index | revised | clarified the top-level example categories and added an explicit `generated/` section; removed the smooth-camera comparison path from the “start here” list |
| `examples/reference/README.md` | public reference tree index | revised | now explicitly names `rtdl_workload_reference.py` as the primary shared workload-reference module |
| `examples/generated/README.md` | public generated-tree index | new | created a dedicated explanation for preserved generated bundles and clarified that they are not the main first-run path |
| `examples/reference/rtdl_workload_reference.py` | public reference code | renamed/revised | renamed from `rtdl_goal10_reference.py`, kept behavior intact, and added a clear module docstring |
| `examples/reference/rtdl_goal10_reference.py` | former public reference code | removed from public surface | replaced by `rtdl_workload_reference.py` to eliminate goal-number leakage from the public example tree |
| `examples/reference/rtdl_release_reference.py` | public reference facade | revised | retargeted imports to `rtdl_workload_reference.py` and simplified the docstring because the underlying file is now already public-safe |
| `examples/generated/rtdl_generated_segment_polygon_bundle/README.md` | preserved generated example | moved | relocated under `examples/generated/` to keep the examples root clean |
| `examples/generated/rtdl_generated_segment_polygon_bundle/generated_segment_polygon_hitcount_cpu_python_reference_authored_segment_polygon_minimal.py` | preserved generated example | moved | relocated under `examples/generated/` |
| `examples/generated/rtdl_generated_segment_polygon_bundle/request.json` | preserved generated example | moved | relocated under `examples/generated/` |
| `examples/generated/rtdl_generated_segment_polygon_anyhit_bundle/README.md` | preserved generated example | moved | relocated under `examples/generated/` |
| `examples/generated/rtdl_generated_segment_polygon_anyhit_bundle/generated_segment_polygon_anyhit_rows_cpu_python_reference_authored_segment_polygon_minimal.py` | preserved generated example | moved | relocated under `examples/generated/` |
| `examples/generated/rtdl_generated_segment_polygon_anyhit_bundle/request.json` | preserved generated example | moved | relocated under `examples/generated/` |
| `examples/generated/rtdl_generated_polygon_set_jaccard_bundle/README.md` | preserved generated example | moved | relocated under `examples/generated/` |
| `examples/generated/rtdl_generated_polygon_set_jaccard_bundle/generated_polygon_set_jaccard_cpu_python_reference_authored_polygon_set_jaccard_minimal.py` | preserved generated example | moved | relocated under `examples/generated/` |
| `examples/generated/rtdl_generated_polygon_set_jaccard_bundle/request.json` | preserved generated example | moved | relocated under `examples/generated/` |
| `examples/generated/rtdl_generated_segment_polygon_hitcount_cpu.py` | preserved generated example | moved | relocated under `examples/generated/` to keep the examples root focused on first-run paths |
| `Makefile` | public build surface | revised | updated the public `build` target to use the renamed `rtdl_workload_reference.py` module and `WORKLOAD_REFERENCE_KERNELS` symbol |
| `src/rtdsl/baseline_runner.py` | supporting runtime code | revised | updated imports to the renamed public workload-reference module |
| `src/rtdsl/baseline_benchmark.py` | supporting runtime code | revised | updated imports to the renamed public workload-reference module |
| `src/rtdsl/evaluation_report.py` | supporting runtime code | revised | updated imports to the renamed public workload-reference module |
| `src/rtdsl/goal112_segment_polygon_perf.py` | supporting runtime code | revised | updated imports to the renamed public workload-reference module |
| `src/rtdsl/goal114_segment_polygon_postgis.py` | supporting runtime code | revised | updated imports to the renamed public workload-reference module |
| `src/rtdsl/goal116_segment_polygon_backend_audit.py` | supporting runtime code | revised | updated imports to the renamed public workload-reference module |
| `src/rtdsl/goal118_segment_polygon_linux_large_perf.py` | supporting runtime code | revised | updated imports to the renamed public workload-reference module |
| `src/rtdsl/goal128_segment_polygon_anyhit_postgis.py` | supporting runtime code | revised | updated imports to the renamed public workload-reference module |
| `scripts/goal18_compare_result_modes.py` | supporting tool | revised | updated imports to the renamed public workload-reference module |
| `scripts/goal43_optix_validation.py` | supporting tool | revised | updated imports to the renamed public workload-reference module |
| `scripts/goal51_vulkan_validation.py` | supporting tool | revised | updated imports to the renamed public workload-reference module |
| `tests/goal10_workloads_test.py` | audit/test surface | revised | updated imports to the renamed public workload-reference module |
| `tests/goal40_native_oracle_test.py` | audit/test surface | revised | updated imports to the renamed public workload-reference module |
| `tests/goal110_baseline_runner_backend_test.py` | audit/test surface | revised | updated imports to the renamed public workload-reference module |
| `tests/goal110_segment_polygon_hitcount_semantics_test.py` | audit/test surface | revised | updated imports to the renamed public workload-reference module |
| `tests/goal110_segment_polygon_hitcount_closure_test.py` | audit/test surface | revised | updated imports to the renamed public workload-reference module |
| `tests/goal18_result_mode_test.py` | audit/test surface | revised | updated imports to the renamed public workload-reference module |
| `tests/baseline_contracts_test.py` | audit/test surface | revised | updated imports to the renamed public workload-reference module |
| `tests/baseline_integration_test.py` | audit/test surface | revised | updated imports to the renamed public workload-reference module |
| `tests/cpu_embree_parity_test.py` | audit/test surface | revised | updated imports to the renamed public workload-reference module |
| `tests/rtdsl_language_test.py` | audit/test surface | revised | updated imports and symbol names to the renamed public workload-reference module |
| `tests/rtdsl_vulkan_test.py` | audit/test surface | revised | updated imports to the renamed public workload-reference module |
| `docs/reports/RTDL_v0.3_External_Test_Report_2026-04-09.md` | historical but referenced | revised | updated the report’s cited file name to the renamed public reference module so the record does not point at a removed path |
| `docs/reports/goal111_v0_2_generate_only_mvp_2026-04-05.md` | historical report | revised | updated generated-example paths after the move to `examples/generated/` |
| `docs/reports/goal113_generate_only_maturation_2026-04-05.md` | historical report | revised | updated generated-example paths after the move to `examples/generated/` |
| `docs/reports/goal129_generate_only_second_workload_expansion_2026-04-06.md` | historical report | revised | updated generated-example paths after the move to `examples/generated/` |
| `docs/reports/goal142_jaccard_docs_and_generate_only_2026-04-06.md` | historical report | revised | updated generated-example paths after the move to `examples/generated/` |
| `docs/reports/v0_2_segment_polygon_postgis_workloads_2026-04-06.md` | historical release report | revised | updated the public reference-module path after the rename |
| `docs/reports/goal160_project_level_audit_artifacts_2026-04-07/code_audit.csv` | historical audit artifact | revised | updated moved/renamed example paths so the archived audit record still points to valid files |
| `docs/reports/goal160_project_level_audit_artifacts_2026-04-07/code_audit.md` | historical audit artifact | revised | updated moved/renamed example paths so the archived audit record still points to valid files |
| `docs/reports/goal160_project_level_audit_artifacts_2026-04-07/docs_audit.csv` | historical audit artifact | revised | updated moved/renamed doc/example paths so the archived audit record still points to valid files |
| `examples/rtdl_hello_world.py` | public first-run example | reviewed/no change | name and placement already clean; kept at the examples root |
| `examples/rtdl_hello_world_backends.py` | public first-run example | reviewed/no change | name and placement already clean; kept at the examples root |
| `examples/rtdl_segment_polygon_hitcount.py` | public workload example | reviewed/no change | name and placement already clean; kept at the examples root |
| `examples/rtdl_segment_polygon_anyhit_rows.py` | public workload example | reviewed/no change | name and placement already clean; kept at the examples root |
| `examples/rtdl_polygon_pair_overlap_area_rows.py` | public workload example | reviewed/no change | name and placement already clean; kept at the examples root |
| `examples/rtdl_polygon_set_jaccard.py` | public workload example | reviewed/no change | name and placement already clean; kept at the examples root |
| `examples/rtdl_road_hazard_screening.py` | public app-style workload example | reviewed/no change | name and placement already clean; kept at the examples root |
| `examples/visual_demo/rtdl_hidden_star_stable_ball_demo.py` | public visual demo | reviewed/no change | name and placement already match the current public story; kept as the main visual-demo source |

## Verification

Executed:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 -m unittest \
  tests.goal10_workloads_test \
  tests.goal40_native_oracle_test \
  tests.goal110_baseline_runner_backend_test \
  tests.goal110_segment_polygon_hitcount_semantics_test \
  tests.goal110_segment_polygon_hitcount_closure_test \
  tests.goal18_result_mode_test \
  tests.baseline_contracts_test \
  tests.baseline_integration_test \
  tests.cpu_embree_parity_test \
  tests.rtdsl_language_test \
  tests.rtdsl_vulkan_test

python3 -m compileall \
  examples/reference \
  examples/generated \
  examples/visual_demo \
  examples/rtdl_hello_world.py \
  examples/rtdl_hello_world_backends.py \
  examples/rtdl_segment_polygon_hitcount.py \
  examples/rtdl_segment_polygon_anyhit_rows.py \
  examples/rtdl_polygon_pair_overlap_area_rows.py \
  examples/rtdl_polygon_set_jaccard.py \
  examples/rtdl_road_hazard_screening.py

PYTHONPATH=src:. python3 -m unittest tests.goal187_v0_3_audit_test
make build
```

Results:

- targeted reference/runtime test slice:
  - `Ran 45 tests in 0.031s`
  - `OK (skipped=4)`
- `compileall` on the reviewed example trees:
  - `OK`
- `tests.goal187_v0_3_audit_test`:
  - `Ran 4 tests in 0.505s`
  - `OK`
- `make build`:
  - `OK`

## Final Audit Judgment

The public release surface is now materially cleaner than before this audit:

- no public `goal10` file name in the example chain
- no generated-bundle clutter at the `examples/` root
- front-door docs teach the example layout explicitly
- reviewed feature docs use clone-real commands and repo-relative links
- supporting code/test surfaces were kept internally consistent with the rename

Remaining honesty note:

- the repository still preserves a large historical goal/report archive, and
  those files intentionally remain archival rather than being rewritten into a
  public tutorial set
