# Goal 280 Report

Date: 2026-04-12
Workspace: `/Users/rl2025/worktrees/rtdl_v0_4_main_publish`
Linux host: `lestat-lx1`

## Summary

Goal 280 fixed a live cuNSearch parity failure that only appeared on real KITTI data at larger radii.

## Problem

The first real KITTI bounded comparison passed at `radius=1.0` but failed at `radius=2.0` and `radius=5.0` even though:

- row counts matched
- neighbor ids matched

The actual defect was JSON precision loss in the generated C++ driver:

- the live bridge wrote floating distances with the default stream precision
- that truncated some distances enough to exceed the repo float-comparison tolerance

## What Changed

- `src/rtdsl/rtnn_cunsearch_live.py`
  - generated driver now includes `<iomanip>`
  - generated driver now emits:
    - `std::setprecision(17)` for double builds
    - `std::setprecision(9)` for float builds
- `tests/goal275_v0_5_cunsearch_live_driver_test.py`
  - now verifies the emitted precision settings in both float and double modes

## Verification

Local:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal275_v0_5_cunsearch_live_driver_test \
  tests.goal276_v0_5_live_cunsearch_comparison_contract_test \
  tests.goal270_v0_5_kitti_bounded_acquisition_test \
  tests.goal277_v0_5_kitti_linux_ready_test

Ran 19 tests
OK
```

Linux real-data runs:

- `radius = 2.0`
  - `query_point_count = 64`
  - `search_point_count = 64`
  - `reference_row_count = 64`
  - `external_row_count = 64`
  - `parity_ok = true`
- `radius = 5.0`
  - `query_point_count = 64`
  - `search_point_count = 64`
  - `reference_row_count = 64`
  - `external_row_count = 64`
  - `parity_ok = true`

Linux artifacts:

- `/home/lestat/work/rtdl_v05_live_clean/build/goal280_kitti_live_real_r2/comparison_report.json`
- `/home/lestat/work/rtdl_v05_live_clean/build/goal280_kitti_live_real_r5/comparison_report.json`

## Result

Goal 280 is complete. The first real KITTI live comparison path is now hardened against output-precision drift in the cuNSearch bridge.
