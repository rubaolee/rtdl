# RTDL v0.6 Tag Preparation

Date: 2026-04-14
Status: release-make state prepared for `v0.6.0`

## Release tag

- `v0.6.0`

## Package contents that should be present at tagging time

- `docs/release_reports/v0_6/README.md`
- `docs/release_reports/v0_6/release_statement.md`
- `docs/release_reports/v0_6/support_matrix.md`
- `docs/release_reports/v0_6/audit_report.md`
- `docs/release_reports/v0_6/tag_preparation.md`

## Final release-facing claim

At release-making time, the repo should state:

- current released version: `v0.6.0`
- the former graph-workload development line has become the released `v0.6`
  line

## Final check before tagging

Before tagging, confirm:

- the `v0.6` release package docs are present
- the graph correctness/review gate is saved
- the current bounded graph docs and front-door language are aligned
- no unresolved blocker remains in the `v0.6` release-facing docs
