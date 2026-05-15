# RTDL Tests

This directory is the regression and evidence gate suite. It is intentionally
large because it preserves many release and audit checks.

## Use First

| Need | Command |
| --- | --- |
| Current docs/examples organization gate | `python -m unittest tests.goal2101_frontpage_navigation_link_audit_test tests.goal2102_examples_directory_organization_audit_test` |
| Current learner-doc cleanup gate | `python -m unittest tests.goal2094_v2_learner_doc_single_version_cleanup_test tests.goal2096_v2_tutorial_directory_cleanup_test` |
| App/example catalog checks | `python -m unittest tests.goal686_app_catalog_cleanup_test tests.goal688_retired_app_surface_test` |
| Feature support contract checks | `python -m unittest tests.goal685_engine_feature_support_contract_test tests.goal687_app_engine_support_matrix_test` |

Run from the repository root with `PYTHONPATH=src:.`.

## What Lives Here

| Group | Meaning |
| --- | --- |
| `goal*.py` | Goal-specific regression gates and audit checks. |
| `fixtures/` | Small deterministic inputs for tests. |
| `golden/` | Expected IR/plans or outputs for compatibility checks. |

## Rule

Learners do not need to browse this directory file by file. Use the command
groups above, or follow the exact test command named by a report.

