# Goal 286 Report

Date: 2026-04-12
Workspace: `/Users/rl2025/worktrees/rtdl_v0_4_main_publish`

## Summary

Goal 286 turned the duplicate-point correctness boundary into an explicit preflight guard for the live cuNSearch comparison path.

## What Changed

- `src/rtdsl/rtnn_duplicate_audit.py`
  - added `CuNSearchDuplicatePointGuardResult`
  - added `assess_cunsearch_duplicate_point_guard(...)`
- `src/rtdsl/rtnn_comparison.py`
  - `compare_bounded_fixed_radius_live_cunsearch(...)` now checks the duplicate guard before execution
  - duplicate-point packages return a blocked comparison result with an explicit note
- `tests/goal286_cunsearch_duplicate_guard_test.py`
  - covers:
    - allowed nonduplicate package
    - blocked duplicate package
    - live comparison early-block behavior

## Honest Contract Change

Before Goal 286:

- duplicate-point packages could flow into the live cuNSearch comparison path
- the run could then fail strict parity in a way that looked like a generic backend mismatch

After Goal 286:

- exact cross-package duplicate points are treated as outside the current validated live cuNSearch strict-parity contract
- the live comparison path blocks early and says so explicitly

## Honest Read

This is not a backend fix. It is a contract hardening step.

What is now true:

- RTDL no longer silently treats duplicate-point packages as valid strict cuNSearch comparison inputs
- future cuNSearch benchmark reports can distinguish:
  - clean strict-parity inputs
  - duplicate-point-blocked inputs

What is still open:

- whether cuNSearch can be integrated honestly under a deduplicated comparison contract
- whether duplicate points should be normalized, filtered, or left as an explicit backend exclusion
