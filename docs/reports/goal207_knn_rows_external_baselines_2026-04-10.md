# Goal 207 Report: KNN Rows External Baselines

## Summary

Goal 207 adds the first external comparison harness for `knn_rows`. The workload can now be checked against optional SciPy and bounded PostGIS baselines without changing the RTDL-visible contract.

## Implementation

- Added SciPy `cKDTree` baseline support for `knn_rows`.
- Added bounded PostGIS nearest-order SQL/helper support for `knn_rows`.
- Extended the baseline runner to support `scipy` and `postgis` for both nearest-neighbor workloads.
- Added authored and Natural Earth-facing tests for the new baseline shape.

## Honest Boundary

- These are optional comparison helpers, not required runtime dependencies.
- This slice does not claim a benchmark win yet.

## Verification

- `PYTHONPATH=src:. python3 -m unittest tests.goal207_knn_rows_external_baselines_test tests.goal201_fixed_radius_neighbors_external_baselines_test tests.baseline_contracts_test`
  - `Ran 21 tests`
  - `OK`
- `python3 -m compileall /Users/rl2025/rtdl_python_only/src/rtdsl/external_baselines.py /Users/rl2025/rtdl_python_only/src/rtdsl/baseline_runner.py /Users/rl2025/rtdl_python_only/tests/goal207_knn_rows_external_baselines_test.py`
  - `OK`
