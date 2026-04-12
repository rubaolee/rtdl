# Goal 299 Report

Date: 2026-04-12
Workspace: `/Users/rl2025/worktrees/rtdl_v0_4_main_publish`
Primary local platform: `macOS`

## Summary

Goal 299 brings the Embree backend online for 3D `bounded_knn_rows`.

The most important result is:

- Embree can now execute 3D bounded-KNN point queries
- `run_embree(...)` matches `run_cpu_python_reference(...)` on the focused 3D
  bounded-KNN case
- prepared Embree execution also works on that same case
- raw mode exposes the expected bounded-KNN row shape including
  `neighbor_rank`
- 3D Embree `knn_rows` remains explicitly blocked for a later goal

## Technical Shape

Goal 299 does not add a second native Embree candidate-collection kernel for
bounded-KNN.

Instead, it reuses the newly closed Embree 3D fixed-radius native path and
adds the bounded ranking layer in the Python Embree runtime:

- native Embree still collects the within-radius neighbors
- Python sorts/truncates in the already-established fixed-radius order
- Python adds `neighbor_rank`

That is technically coherent because `bounded_knn_rows(radius=..., k_max=...)`
is exactly the bounded ranking of the fixed-radius neighbor set.

## Code Changes

Additive runtime changes:

- `src/rtdsl/embree_runtime.py`

New test:

- `tests/goal299_v0_5_embree_3d_bounded_knn_test.py`

## Verification

Focused Embree + 3D nearest-neighbor regression:

- `python3 -m unittest tests.goal200_fixed_radius_neighbors_embree_test tests.goal206_knn_rows_embree_test tests.goal261_v0_5_native_3d_point_contract_test tests.goal298_v0_5_embree_3d_fixed_radius_test tests.goal299_v0_5_embree_3d_bounded_knn_test tests.goal292_v0_5_native_3d_fixed_radius_oracle_test tests.goal293_v0_5_native_3d_bounded_knn_oracle_test tests.goal296_v0_5_native_3d_knn_oracle_test`
  - `Ran 28 tests`
  - `OK`

Broader review regression:

- `python3 -m unittest tests.claude_v0_5_full_review_test`
  - `Ran 112 tests`
  - `OK`

## Honest Read

What is now true:

- Embree 3D `fixed_radius_neighbors` is online
- Embree 3D `bounded_knn_rows` is online
- both are parity-clean on their focused local test cases

What is not being claimed:

- Linux Embree validation in this slice
- Windows Embree validation in this slice
- Embree 3D `knn_rows` support
- cross-platform Embree performance closure

So Goal 299 is a bounded parity bring-up, not a final performance result.
