# Goal 300 Report

Date: 2026-04-12
Workspace: `/Users/rl2025/worktrees/rtdl_v0_4_main_publish`
Primary local platform: `macOS`

## Summary

Goal 300 closes the remaining Embree 3D point nearest-neighbor workload:

- 3D `knn_rows`

The most important result is:

- Embree can now execute 3D KNN point queries
- `run_embree(...)` matches `run_cpu_python_reference(...)` on the focused 3D
  KNN case
- prepared Embree execution also works on that same case
- tie ordering remains deterministic by `neighbor_id`

## Code Changes

Additive changes:

- `src/native/embree/rtdl_embree_prelude.h`
- `src/native/embree/rtdl_embree_scene.cpp`
- `src/native/embree/rtdl_embree_api.cpp`
- `src/rtdsl/embree_runtime.py`

New test:

- `tests/goal300_v0_5_embree_3d_knn_test.py`

Minor current-state cleanup:

- `tests/goal298_v0_5_embree_3d_fixed_radius_test.py`

## Verification

Focused Embree + 3D nearest-neighbor regression:

- `python3 -m unittest tests.goal200_fixed_radius_neighbors_embree_test tests.goal206_knn_rows_embree_test tests.goal261_v0_5_native_3d_point_contract_test tests.goal298_v0_5_embree_3d_fixed_radius_test tests.goal299_v0_5_embree_3d_bounded_knn_test tests.goal300_v0_5_embree_3d_knn_test tests.goal292_v0_5_native_3d_fixed_radius_oracle_test tests.goal293_v0_5_native_3d_bounded_knn_oracle_test tests.goal296_v0_5_native_3d_knn_oracle_test tests.claude_v0_5_full_review_test`
  - `Ran 143 tests`
  - `OK`

## Honest Read

What is now true:

- Embree 3D `fixed_radius_neighbors` is online
- Embree 3D `bounded_knn_rows` is online
- Embree 3D `knn_rows` is online

What is not being claimed:

- Linux Embree validation in this slice
- Windows Embree validation in this slice
- cross-platform Embree performance closure

So Goal 300 closes the Embree 3D nearest-neighbor capability line, but not yet
the cross-platform performance line.
