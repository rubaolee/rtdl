# Goal 260: v0.5 3D Point Surface And Reference Path

Date: 2026-04-11
Status: implemented

## Purpose

Deliver the first real code change on the `v0.5` line.

## What Landed

- `Point3D` canonical record type in the reference layer
- `Point3DLayout`
- `Points3D`
- 3D-capable Python-reference support for:
  - `fixed_radius_neighbors_cpu`
  - `knn_rows_cpu`
- runtime input coercion for 3D point records
- honest `run_cpu(...)` rejection for 3D nearest-neighbor point records while
  native CPU/oracle support is still 2D-only

## Why This Is Honest

This slice does not claim:

- 3D native CPU/oracle closure
- 3D Embree closure
- 3D OptiX closure
- 3D Vulkan closure

It claims only:

- first-class 3D point public surface
- Python-reference nearest-neighbor support

## Verification

Covered by:

- `tests/goal260_v0_5_3d_point_surface_test.py`

The test slice exercises:

- direct 3D nearest-neighbor truth-path functions
- `run_cpu_python_reference(...)` with `Points3D`
- honest `run_cpu(...)` rejection for the still-unsupported native 3D point path
