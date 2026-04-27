# Goal1045 RTX Single-Session Runbook Goal1043 Sync

Date: 2026-04-27

## Scope

Goal1045 updates the paid-pod runbook so the next v1.0 RTX app batch follows the Goal1043 claim-grade repair policy.

## Changes

- Added the `RTDL_SOURCE_COMMIT` export to `docs/rtx_cloud_single_session_runbook.md`.
- Documented the fallback order used by the runner: `RTDL_SOURCE_COMMIT`, git, then `.rtdl_source_commit`.
- Marked artifacts without source commits as engineering diagnostics only.
- Made Group B fixed-radius validation policy explicit: do not add `--skip-validation`.
- Updated `tests/goal829_rtx_cloud_single_session_runbook_test.py` so the source-commit and validation guards stay present.

## Boundary

This is a runbook/readiness update only. It does not start a cloud pod, run benchmarks, authorize a speedup claim, or authorize release.
