# Goal 208 Report: v0.4 Public Example Chain

## Summary

Goal 208 makes the active nearest-neighbor line visible to normal users. `v0.4`
now has clean top-level release-facing examples for both public nearest-neighbor
workloads, and the quick tutorial/docs point to them directly.

## Implementation

- added `examples/rtdl_fixed_radius_neighbors.py`
- added `examples/rtdl_knn_rows.py`
- added a bounded test slice for the new top-level examples
- updated `examples/README.md`
- updated `docs/release_facing_examples.md`
- updated `docs/quick_tutorial.md`

## Honest Boundary

- These are correctness-first release-facing examples.
- They are not benchmark claims.
- The active `v0.4` line is still under construction and not yet released.

## Verification

- `PYTHONPATH=src:. python3 -m unittest tests.goal208_nearest_neighbor_examples_test tests.goal207_knn_rows_external_baselines_test tests.goal205_knn_rows_cpu_oracle_test`
  - `Ran 17 tests in 0.629s`
  - `OK`
- `python3 -m compileall /Users/rl2025/rtdl_python_only/examples/rtdl_fixed_radius_neighbors.py /Users/rl2025/rtdl_python_only/examples/rtdl_knn_rows.py /Users/rl2025/rtdl_python_only/tests/goal208_nearest_neighbor_examples_test.py`
  - `OK`
- direct CLI smoke:
  - `python3 examples/rtdl_fixed_radius_neighbors.py --backend cpu_python_reference`
  - `python3 examples/rtdl_knn_rows.py --backend cpu_python_reference`
