# Goal 263: v0.5 Bounded KNN Rows Surface

Date: 2026-04-11
Status: implemented

## Purpose

Turn the Goal 262 contract decision into executable non-native RTDL surface.

## What Landed

- `rt.bounded_knn_rows(radius=..., k_max=...)`
- lowering support with workload kind `bounded_knn_rows`
- Python-reference truth path:
  - `bounded_knn_rows_cpu(...)`
- package export for the new predicate and truth-path helper

## Why This Is Honest

This slice does not claim:

- native CPU/oracle support
- Embree support
- OptiX support
- Vulkan support

It claims only:

- public API
- compile/lowering support
- Python-reference execution

## Verification

Covered by:

- `tests/goal263_v0_5_bounded_knn_rows_surface_test.py`

The test slice verifies:

- API validation
- radius-bounded rank-bearing reference rows
- `run_cpu_python_reference(...)` execution
- distinct lowering plan identity
- stability of released `knn_rows(k=...)`
