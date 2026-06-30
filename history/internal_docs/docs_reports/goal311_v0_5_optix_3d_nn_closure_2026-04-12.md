# Goal 311 Report: OptiX 3D Nearest-Neighbor Closure

Date: 2026-04-12
Status: implemented locally, Linux-validated, pending saved external review

## Purpose

Close the first honest Linux OptiX bring-up for the `v0.5` 3D point
nearest-neighbor line.

## Scope

Workloads closed in this slice:
- `fixed_radius_neighbors`
- `bounded_knn_rows`
- `knn_rows`

Platform boundary in this slice:
- Linux primary validation on `lestat-lx1`
- no Windows or macOS performance claim

## Implementation

Native OptiX changes:
- added `RtdlPoint3D` to the public OptiX prelude
- added C ABI exports:
  - `rtdl_optix_run_fixed_radius_neighbors_3d(...)`
  - `rtdl_optix_run_knn_rows_3d(...)`
- added CUDA kernels and host launchers for 3D point:
  - fixed-radius neighbors
  - KNN rows

Python runtime changes:
- 3D point packing is now accepted on the OptiX path
- prepared OptiX execution now supports:
  - `fixed_radius_neighbors`
  - `bounded_knn_rows`
  - `knn_rows`
- `bounded_knn_rows` uses the same honest strategy as Embree:
  - get fixed-radius rows from the native backend
  - assign `neighbor_rank` in Python

Correctness fix applied during Linux bring-up:
- the first 3D KNN Linux run exposed raw float32 GPU distances in the returned
  rows
- the host-side 3D KNN materialization now recomputes exact double distances
  before returning rows to Python
- this preserves parity with the Python reference path

## Verification

Local syntax and smoke:
- `python3 -m py_compile src/rtdsl/optix_runtime.py tests/goal311_v0_5_optix_3d_nn_test.py`
- passed

Local macOS tests:
- `PYTHONPATH=src:. python3 -m unittest tests.goal311_v0_5_optix_3d_nn_test`
- skipped as expected because OptiX is not built locally

Linux build:
- host: `lestat-lx1`
- OptiX SDK path:
  - `/home/lestat/vendor/optix-dev`
- command:
  - `make build-optix OPTIX_PREFIX=/home/lestat/vendor/optix-dev`
- result:
  - built `build/librtdl_optix.so`

Linux backend probe:
- `PYTHONPATH=src:. python3 -c "import rtdsl as rt; print(rt.optix_version())"`
- result:
  - `(9, 0, 0)`

Linux focused Goal 311 test:
- `PYTHONPATH=src:. python3 -m unittest tests.goal311_v0_5_optix_3d_nn_test`
- result:
  - `Ran 4 tests`
  - `OK`

Linux OptiX regression checks:
- `PYTHONPATH=src:. python3 -m unittest tests.goal216_fixed_radius_neighbors_optix_test`
  - `Ran 9 tests`
  - `OK`
- `PYTHONPATH=src:. python3 -m unittest tests.goal217_knn_rows_optix_test`
  - `Ran 5 tests`
  - `OK`

## Outcome

Goal 311 is technically complete:
- OptiX now has a real 3D point nearest-neighbor capability line on Linux
- parity is established for:
  - `fixed_radius_neighbors`
  - `bounded_knn_rows`
  - `knn_rows`

This closes the capability prerequisite for the next Linux large-scale backend
comparison across:
- native CPU/oracle
- Embree
- OptiX

## Honesty Boundary

This slice closes capability and Linux parity only.

It does not yet claim:
- Windows OptiX validation
- macOS OptiX validation
- large-scale OptiX performance superiority
- final cross-platform backend maturity
