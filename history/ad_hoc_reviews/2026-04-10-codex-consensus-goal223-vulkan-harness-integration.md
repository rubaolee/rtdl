# Codex Consensus: Goal 223 Vulkan Harness Integration

Date: 2026-04-10
Reviewer: Codex
Status: accepted pending one external review artifact

## Verdict

This is the right narrow finish step for the reopened nearest-neighbor line.
The project already has live Vulkan execution for `fixed_radius_neighbors` and
`knn_rows`; the remaining harness gap was that `baseline_runner` still could not
exercise that backend. This slice closes that gap honestly.

## What it does correctly

- adds `backend="vulkan"` to `baseline_runner`
- keeps the Vulkan harness scope narrow to:
  - `fixed_radius_neighbors`
  - `knn_rows`
- compares Vulkan rows against the Python truth path
- rejects unsupported Vulkan harness requests explicitly

## Local verification seen by Codex

- `PYTHONPATH=src:. python3 -m unittest tests.goal223_vulkan_harness_integration_test tests.goal218_fixed_radius_neighbors_vulkan_test tests.goal219_knn_rows_vulkan_test`
  - `Ran 17 tests`
  - `OK (skipped=13)`
- `python3 -m compileall src/rtdsl/baseline_runner.py tests/goal223_vulkan_harness_integration_test.py`
  - `OK`

## Boundary

- this does not yet make Vulkan the harness backend for all older workloads
- that narrower scope is the correct decision for the reopened `v0.4` line
