# Goal4276 Top-Level Tutorial Reorganization

Status: complete local documentation reorganization.

## Purpose

The public repository now treats tutorials, docs, and examples as different
front-door concepts:

| Area | Job |
| --- | --- |
| `tutorials/` | Ordered teaching path for learners. |
| `docs/` | Reference material: concepts, APIs, architecture, primitives, IR, support boundaries, and evidence maps. |
| `examples/` | Runnable code and benchmark/reference implementations. |
| `history/` | Older release material, old tutorial pages, reviews, audit logs, and provenance. |

The goal is to prevent a learner from seeing old tutorial-era files under
`docs/tutorials/` and assuming they are current v2.10 teaching material.

## Operations

| Path | Previous status | Action | Reason |
| --- | --- | --- | --- |
| `tutorials/README.md` | did not exist | Added top-level tutorial front door | Makes tutorials first-class beside docs and examples. |
| `tutorials/current/README.md` | `docs/tutorials/current/README.md` | Moved and updated relative links | Current teaching ladder belongs under top-level tutorials. |
| `tutorials/current/01_source_tree_first_run.md` | `docs/tutorials/current/01_source_tree_first_run.md` | Moved unchanged | Current ordered tutorial step. |
| `tutorials/current/02_kernel_shape_and_backends.md` | `docs/tutorials/current/02_kernel_shape_and_backends.md` | Moved unchanged | Current ordered tutorial step. |
| `tutorials/current/03_primitives_and_discovery.md` | `docs/tutorials/current/03_primitives_and_discovery.md` | Moved and fixed docs links | Current ordered tutorial step with reference-doc links. |
| `tutorials/current/04_python_app_structure.md` | `docs/tutorials/current/04_python_app_structure.md` | Moved unchanged | Current ordered tutorial step. |
| `tutorials/current/05_partner_columns_cupy_numba.md` | `docs/tutorials/current/05_partner_columns_cupy_numba.md` | Moved and fixed partner-guide link | Current ordered tutorial step. |
| `tutorials/current/06_prepared_execution_measurement.md` | `docs/tutorials/current/06_prepared_execution_measurement.md` | Moved unchanged | Current ordered tutorial step. |
| `tutorials/current/07_benchmark_app_python_rtdl_partner.md` | `docs/tutorials/current/07_benchmark_app_python_rtdl_partner.md` | Moved and fixed benchmark/docs links | Current ordered benchmark teaching step. |
| `tutorials/current/08_spatial_join_rayjoin_reference.md` | `docs/tutorials/current/08_spatial_join_rayjoin_reference.md` | Moved and fixed benchmark links | Current Spatial RayJoin teaching reference. |
| `history/tutorial_archive/README.md` | `docs/tutorials/README.md` | Replaced with archive notice and file inventory | Avoids presenting old loose tutorial files as current teaching material. |
| `history/tutorial_archive/*.md` | `docs/tutorials/*.md` loose pages | Moved to history archive | Preserves old tutorial pages without putting them in the learner front door. |
| `README.md` | linked `docs/tutorials/README.md` | Updated to link `tutorials/` and describe `docs/` as reference docs | Makes the GitHub root page cleaner for first readers. |
| `docs/README.md` | treated `docs/tutorials/` as a docs subdir | Updated to point to top-level tutorials and removed docs/tutorials from the docs directory map | Keeps docs as reference material. |
| `docs/learn/README.md` | linked tutorial content under docs | Updated to top-level tutorial paths | Keeps the learner route current. |
| `docs/public_documentation_map.md` | mapped tutorials inside docs | Updated to the top-level tutorial track | Keeps the public map consistent. |
| `docs/quick_tutorial.md` | linked archived feature cookbook page | Updated to continue into the current tutorial track and runnable cookbook example | Removes old loose tutorial page from the normal path. |
| `docs/app_example_quickstart.md` | linked archived partner tutorial page | Updated to the current partner tutorial step | Avoids sending users to archived tutorial material. |
| `docs/release_facing_examples.md` | linked docs/tutorials | Updated to top-level tutorials | Keeps reviewer command archive link-clean. |
| `docs/features/README.md` | linked docs/tutorials | Updated to top-level tutorials | Keeps feature reference docs aligned. |
| `examples/README.md` | linked docs/tutorials | Updated to top-level tutorials | Keeps examples separate from tutorials but connected. |
| `docs/audit/process/current_milestone_qa.md` | linked docs/tutorials with stale relative path | Updated to top-level tutorials | Keeps archived process doc link valid. |
| `docs/history/version_archive_notes.md` | referenced an old v2.0 learner path and docs/tutorials link | Updated wording and link | Keeps history pointer accurate. |
| `scripts/goal4248_current_public_docs_claim_boundary_scan.py` | scanned `docs/tutorials` | Scans top-level `tutorials` | Ensures public claim-boundary checks include the new tutorial front door. |
| `tests/goal4248_current_public_docs_claim_boundary_scan_test.py` | expected docs/tutorials files | Updated to expect top-level current tutorials | Keeps claim-boundary gate current. |
| `tests/goal4271_v2_10_user_doc_cleanup_test.py` | scanned docs/examples only | Added top-level tutorials to current-doc scan and key entrypoints | Prevents tutorial docs from escaping current-doc checks. |
| `tests/goal4273_current_tutorial_ladder_test.py` | expected `docs/tutorials/current` | Updated to `tutorials/current` | Tests the new teaching location. |
| `tests/goal4274_current_doc_recheck_test.py` | did not scan top-level tutorials | Added `tutorials/**/*.md` to current public docs | Keeps link/stale-wording checks complete. |
| `tests/goal4275_spatial_rayjoin_tutorial_reference_test.py` | expected Spatial RayJoin tutorial under docs | Updated to top-level tutorial path | Keeps the new RayJoin tutorial reference covered. |

## Validation

Commands run locally:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal4273_current_tutorial_ladder_test tests.goal4275_spatial_rayjoin_tutorial_reference_test tests.goal4271_v2_10_user_doc_cleanup_test tests.goal4274_current_doc_recheck_test
$env:PYTHONPATH='src;.'; py -3 scripts/goal4248_current_public_docs_claim_boundary_scan.py
```

The full validation result is recorded by the updated current doc and
claim-boundary artifacts.

## Boundary

This is a documentation-structure cleanup. It does not change RTDL runtime
semantics, benchmark evidence, package-install status, partner support, release
status, or performance claims.
