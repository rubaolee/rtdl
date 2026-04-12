# Goal 298 Report

Date: 2026-04-12
Workspace: `/Users/rl2025/worktrees/rtdl_v0_4_main_publish`
Primary local platform: `macOS`

## Summary

Goal 298 brings the Embree backend online for the first v0.5 3D point
nearest-neighbor workload:

- 3D `fixed_radius_neighbors`

The most important result is:

- Embree can now execute 3D fixed-radius point queries
- `run_embree(...)` matches `run_cpu_python_reference(...)` on the focused 3D
  test case
- prepared Embree execution also works on that same 3D fixed-radius case
- the rest of the 3D point nearest-neighbor Embree line remains honestly
  bounded:
  - 3D `bounded_knn_rows`: not online yet
  - 3D `knn_rows`: not online yet

## Code Changes

Additive 3D Embree bring-up touched:

- `src/native/embree/rtdl_embree_prelude.h`
- `src/native/embree/rtdl_embree_geometry.cpp`
- `src/native/embree/rtdl_embree_scene.cpp`
- `src/native/embree/rtdl_embree_api.cpp`
- `src/rtdsl/embree_runtime.py`

New tests:

- `tests/goal298_v0_5_embree_3d_fixed_radius_test.py`

Updated boundary test:

- `tests/goal261_v0_5_native_3d_point_contract_test.py`

## What Changed Technically

The new Embree 3D fixed-radius path adds:

- `RtdlPoint3D` to the Embree ABI
- `rtdl_embree_run_fixed_radius_neighbors_3d(...)`
- 3D point bounds in the Embree point-query scene
- 3D fixed-radius point-query collection logic
- Python `ctypes` bindings for the optional 3D fixed-radius symbol
- 3D point packing metadata in the Embree runtime

The Python runtime now supports packing `Points3D` for Embree inputs, but it
keeps the workload boundary explicit:

- 3D `fixed_radius_neighbors`: online
- 3D `knn_rows`: explicitly rejected with an honesty-boundary error

## Verification

Focused Embree regression:

- `python3 -m unittest tests.goal261_v0_5_native_3d_point_contract_test tests.goal200_fixed_radius_neighbors_embree_test tests.goal206_knn_rows_embree_test tests.goal298_v0_5_embree_3d_fixed_radius_test`
  - `Ran 20 tests`
  - `OK`

Broader v0.5 regression:

- `python3 -m unittest tests.goal292_v0_5_native_3d_fixed_radius_oracle_test tests.goal293_v0_5_native_3d_bounded_knn_oracle_test tests.goal296_v0_5_native_3d_knn_oracle_test tests.claude_v0_5_full_review_test`
  - `Ran 117 tests`
  - `OK`

## Honest Read

Goal 298 is a bounded backend bring-up slice, not a final Embree performance
closure.

What is now true:

- Embree is online for 3D `fixed_radius_neighbors`
- the path is parity-clean against the Python truth path on the tested case
- prepared execution is also working

What is not being claimed:

- Linux Embree validation in this slice
- Windows Embree validation in this slice
- 3D Embree `bounded_knn_rows` support
- 3D Embree `knn_rows` support
- cross-platform Embree performance closure

So the honest next move after this goal is:

- Goal 299: Embree 3D `bounded_knn_rows` closure

not a premature cross-platform performance claim.
