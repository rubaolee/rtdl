# Goal 276 Report: v0.5 Live Bounded Linux Comparison

Date: 2026-04-12
Status: implemented

## Purpose

Close the first live bounded Linux comparison loop by running cuNSearch on the
same portable 3D packages that RTDL uses and reporting parity honestly.

## What Landed

### Updated module

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/rtnn_comparison.py`

Added:

- `compare_bounded_fixed_radius_live_cunsearch(...)`

### Public surface

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/__init__.py`

Exported:

- `compare_bounded_fixed_radius_live_cunsearch(...)`

### Tests

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal276_v0_5_live_cunsearch_comparison_contract_test.py`

### Live Linux validation

Validated on `lestat-lx1` with:

- cuNSearch built from source under `/home/lestat/work/cunsearch_probe`
- a bounded synthetic 3D package pair
- live cuNSearch execution via the Goal 275 driver

Observed result:

- `parity_ok = True`
- `reference_row_count = 1`
- `external_row_count = 1`

## Verification

- local:
  - `PYTHONPATH=src:. python3 -m unittest tests.goal275_v0_5_cunsearch_live_driver_test tests.goal276_v0_5_live_cunsearch_comparison_contract_test tests.goal274_v0_5_bounded_fixed_radius_comparison_test`
  - `OK`
- Linux:
  - live bounded cuNSearch comparison returned parity on the synthetic 3D package

## Honesty Boundary

This goal does not claim:

- KITTI data is online
- RTNN paper datasets have been executed
- paper-fidelity reproduction is closed

It only closes the first live bounded Linux comparison loop on a synthetic
portable package.
