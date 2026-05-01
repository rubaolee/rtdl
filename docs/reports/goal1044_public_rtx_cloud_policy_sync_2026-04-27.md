# Goal1044 Public RTX Cloud Policy Sync

Date: 2026-04-27

## Scope

Goal1044 synchronizes release-facing v1.0 RTX app status docs with the Goal1043 repaired pod workflow.

Goal1040 and Goal1041 showed that the previous RTX evidence remains useful engineering evidence but cannot be expanded into claim-grade public speedup wording without a corrected rerun. Goal1043 fixed the local run plumbing:

- rsync-staged pods can carry `RTDL_SOURCE_COMMIT`.
- fixed-radius Group B commands no longer use `--skip-validation`.

## Changes

- Updated `scripts/goal947_v1_rtx_app_status_page.py` so generated v1.0 status pages no longer say `no readiness pod needed` for current claim-grade work.
- Regenerated `docs/v1_0_rtx_app_status.md` and `docs/reports/goal947_v1_rtx_app_status_2026-04-25.json`.
- Updated `src/rtdsl/app_support_matrix.py` maturity cloud policies to require one repaired consolidated RTX pod rerun before expanded public speedup wording.
- Updated `docs/app_engine_support_matrix.md` to match the Goal1043 cloud policy.
- Added `tests/goal1044_public_rtx_cloud_policy_sync_test.py` to prevent stale `no readiness pod needed` wording from returning to current public status docs.

## Current Policy

The app sub-paths remain `rt_core_ready` / `ready_for_rtx_claim_review`, but expanded public speedup wording now requires a repaired consolidated pod rerun with:

- source-commit traceability;
- validation-enabled fixed-radius Group B commands;
- same-semantics baseline review;
- no per-app paid-pod restart pattern.

## Boundary

This is a documentation and source-of-truth sync only. It does not run a new cloud benchmark, prove a new speedup, authorize public speedup wording, or authorize a release.
