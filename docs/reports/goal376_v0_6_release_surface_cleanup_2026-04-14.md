# Goal 376 Report: v0.6 release surface cleanup

Date: 2026-04-14

## Summary

This slice creates the first canonical `v0.6` release-facing package and wires
it into the repo's front-door documentation without prematurely promoting
`v0.6.0` as already released.

## What was added

- `docs/release_reports/v0_6/README.md`
- `docs/release_reports/v0_6/release_statement.md`
- `docs/release_reports/v0_6/support_matrix.md`
- `docs/release_reports/v0_6/audit_report.md`
- `docs/release_reports/v0_6/tag_preparation.md`

## What was updated

- `README.md`
- `docs/README.md`

## Why this is the right cleanup

- `v0.6` now has a bounded but real graph-workload line
- the repo previously had no canonical `v0.6` release package
- the front door can now acknowledge `v0.6` as the active release-prep line
  while honestly keeping `v0.5.0` as the current released version

## Boundary

This cleanup does not claim:

- that `v0.6.0` is already tagged
- that `v0.6` is a full graph-system release
- that the graph line has benchmark or paper-scale closure
