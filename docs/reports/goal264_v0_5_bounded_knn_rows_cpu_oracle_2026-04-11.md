# Goal 264: v0.5 Bounded KNN Rows CPU/Oracle

Date: 2026-04-11
Status: implemented

## Purpose

Add native CPU/oracle support for the new bounded-radius KNN predicate on the
existing 2D point line.

## What Landed

- native oracle ABI entrypoint:
  - `rtdl_oracle_run_bounded_knn_rows(...)`
- Python oracle runtime dispatch for `bounded_knn_rows`
- focused 2D CPU/oracle regression coverage

## Why This Is Honest

This slice closes only:

- 2D native CPU/oracle support for `bounded_knn_rows`

It does not claim:

- 3D native CPU/oracle support
- Embree support
- OptiX support
- Vulkan support

## Verification

Covered by:

- `tests/goal264_v0_5_bounded_knn_rows_cpu_oracle_test.py`

The slice verifies that `run_cpu(...)` now matches the Python reference path on
the bounded-radius KNN contract for 2D point inputs.
