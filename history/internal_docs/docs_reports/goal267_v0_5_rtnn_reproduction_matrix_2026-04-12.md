# Goal 267 Report: v0.5 RTNN Reproduction Matrix

Date: 2026-04-12
Status: implemented

## Purpose

Create the first explicit RTNN reproduction matrix for `v0.5` by combining the
dataset registry and baseline registry into labeled matrix rows.

## What Landed

### New module

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/rtnn_matrix.py`

Added:

- `RtnnMatrixEntry`
- `rtnn_reproduction_matrix(...)`

### Public surface

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/__init__.py`

Exported:

- `RtnnMatrixEntry`
- `rtnn_reproduction_matrix(...)`

### Tests

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal267_v0_5_rtnn_reproduction_matrix_test.py`

The matrix tests verify:

- dataset-packaging rows do not pair with `PostGIS` or `SciPy`
- comparison-matrix rows do expose non-paper baseline rows honestly
- exact-reproduction candidates are still blocked honestly
- RTDL-extension rows remain labeled as extensions
- `bounded_knn_rows` rows do not pair with `cuNSearch`
- fixed-radius rows can still pair with `cuNSearch`

## Honesty Boundary

This goal still does not claim:

- any experiment was executed
- any adapter is online
- any exact RTNN paper reproduction exists

It only makes the first labeled matrix explicit and queryable.

## Review-Driven Correction

The first Goal 267 pass had a real coherency flaw: it defined
`nonpaper_comparison_only` but gave the matrix no artifact that could ever
produce such rows.

That is now fixed by adding:

- a dedicated `comparison_matrix` experiment target

This preserves the stricter paper-matrix boundary while still making bounded
non-paper comparison rows explicit and queryable.
