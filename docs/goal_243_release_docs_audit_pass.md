# Goal 243: Release Docs Audit Pass

## Objective

Record the next system-audit pass for the public documentation tier after the
front page and tutorials.

## Scope

This pass covers the release-facing and programming-reference documentation
that sits immediately after the tutorial layer in the user-priority order:

- `docs/features/README.md`
- `docs/release_facing_examples.md`
- `docs/v0_4_application_examples.md`
- `docs/rtdl/programming_guide.md`
- `docs/rtdl/dsl_reference.md`
- `docs/rtdl/workload_cookbook.md`
- `docs/release_reports/v0_4/README.md`
- `docs/release_reports/v0_4/release_statement.md`
- `docs/release_reports/v0_4/support_matrix.md`
- `docs/release_reports/v0_4/audit_report.md`
- `docs/release_reports/v0_4/tag_preparation.md`

## Required Checks

- release state is described as `v0.4.0`, not as a pre-tag or preview state
- no maintainer-local host/path leakage remains in this public slice
- backend claims remain honest for the public example surface
- acronym expansion is acceptable on user-visible entry pages
- no broken local links are introduced by the release-state cleanup
