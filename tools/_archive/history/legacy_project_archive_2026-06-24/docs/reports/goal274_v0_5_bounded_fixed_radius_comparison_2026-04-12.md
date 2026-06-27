# Goal 274 Report: v0.5 Bounded Fixed-Radius Comparison Harness

Date: 2026-04-12
Status: implemented

## Purpose

Add the first bounded offline comparison harness that evaluates a parsed
external fixed-radius artifact against RTDL reference rows on the same portable
3D point packages.

## What Landed

### New module

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/rtnn_comparison.py`

Added:

- `RtnnBoundedComparisonResult`
- `compare_bounded_fixed_radius_from_packages(...)`

### Public surface

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/__init__.py`

Exported:

- `RtnnBoundedComparisonResult`
- `compare_bounded_fixed_radius_from_packages(...)`

### Tests

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal274_v0_5_bounded_fixed_radius_comparison_test.py`

The focused test slice verifies:

- parity reporting when external rows match RTDL reference rows
- non-parity reporting when the external artifact differs
- honest row-count accounting for both sides of the comparison

## Verification

- `PYTHONPATH=src:. python3 -m unittest tests.goal274_v0_5_bounded_fixed_radius_comparison_test tests.goal273_v0_5_cunsearch_response_parser_test tests.goal272_v0_5_kitti_point_package_test`
- `Ran 8 tests`
- `OK`

## Honesty Boundary

This goal does not claim:

- cuNSearch execution is online
- Linux live comparison has happened
- the response artifact is a paper-fidelity result

It only closes the first bounded offline comparison path for the `v0.5` RTNN
line.
