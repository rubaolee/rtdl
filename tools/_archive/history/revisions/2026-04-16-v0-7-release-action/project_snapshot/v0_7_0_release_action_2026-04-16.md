# RTDL v0.7.0 Release Action

Date: 2026-04-16
Author: Codex
Status: release authorized

## Authorization

The user explicitly authorized release with the instruction: `release`.

## Release Target

- Release version: `v0.7.0`
- Release branch: `codex/v0_7_rt_db`
- Tag target: `v0.7.0`
- Archive excluded from staging: `rtdsl_current.tar.gz`

## Final Local Verification

Before staging, the broad local unittest discovery was rerun:

```text
Ran 1151 tests in 99.435s
OK (skipped=105)
```

`git diff --check` was clean before staging.

## Boundary

This release action does not merge to `main`. A merge requires a separate,
explicit instruction.

The release remains bounded by the v0.7.0 release statement, support matrix,
and audit report.
