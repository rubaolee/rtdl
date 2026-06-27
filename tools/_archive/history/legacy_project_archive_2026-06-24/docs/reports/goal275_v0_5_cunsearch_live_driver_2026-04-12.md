# Goal 275 Report: v0.5 cuNSearch Live Driver

Date: 2026-04-12
Status: implemented

## Purpose

Turn the bounded cuNSearch request contract into a real live Linux execution
path.

## What Landed

### New module

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/rtnn_cunsearch_live.py`

Added:

- `CuNSearchBuildConfig`
- `resolve_cunsearch_build_config(...)`
- `run_cunsearch_fixed_radius_request_live(...)`

### Public surface

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/__init__.py`

Exported:

- `CuNSearchBuildConfig`
- `resolve_cunsearch_build_config(...)`
- `run_cunsearch_fixed_radius_request_live(...)`

### Tests

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal275_v0_5_cunsearch_live_driver_test.py`

The local slice verifies:

- honest readiness detection for the build configuration
- precision-mode detection from the cuNSearch build cache
- request-shape validation before compilation
- generated driver-source contract shape

### Live Linux validation

Validated on `lestat-lx1` against:

- `/home/lestat/work/cunsearch_probe`
- built with `cmake` + `nvcc`
- GPU: NVIDIA GeForce GTX 1070

The live driver emitted a bounded response JSON successfully.

## Verification

- local:
  - `PYTHONPATH=src:. python3 -m unittest tests.goal275_v0_5_cunsearch_live_driver_test tests.goal273_v0_5_cunsearch_response_parser_test`
  - `OK`
- Linux:
  - live fixed-radius request executed successfully against a built cuNSearch library

## Honesty Boundary

This goal does not claim:

- KITTI data is online
- a paper dataset has been executed
- full paper reproduction has happened

It only makes the first live bounded cuNSearch execution path real.
