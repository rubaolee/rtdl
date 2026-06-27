# Iteration 2 Implementation Report

Date: 2026-03-29
Author: Codex
Round: 2026-03-29-goal-7-embree-backend
Repo: /Users/rl2025/rtdl_python_only
Baseline Commit: 4e2be7f1aa72a42f609e6045396bef47071441e8

## Environment Bring-Up

Embree is now installed locally on this Mac:

- version: `4.4.0`
- prefix: `/opt/homebrew/opt/embree`

Verified locally:

- `brew list --versions embree`
- header path at `/opt/homebrew/opt/embree/include/embree4`
- library path at `/opt/homebrew/opt/embree/lib/libembree4.dylib`

## Implemented

### Native Embree Shim

Added a native backend shim in:

- `/Users/rl2025/rtdl_python_only/src/native/rtdl_embree.cpp`

This exposes a plain C ABI for:

- version query
- `lsi`
- `pip`
- `overlay`
- `ray_tri_hitcount`
- row-buffer cleanup

The shim uses Embree user geometry and per-workload callback logic to execute
the current RTDL workloads on top of Embree traversal.

### Python Embree Runtime

Added:

- `/Users/rl2025/rtdl_python_only/src/rtdsl/embree_runtime.py`

This layer:

1. reuses the current RTDL kernel compilation
2. reuses the current input normalization model
3. builds the native shim on demand
4. loads it through `ctypes`
5. dispatches workload execution through `rt.run_embree(...)`

### Public API

Exported:

- `rt.run_embree(...)`
- `rt.embree_version()`

Updated:

- `/Users/rl2025/rtdl_python_only/src/rtdsl/__init__.py`

### Tests

Added:

- `/Users/rl2025/rtdl_python_only/tests/rtdsl_embree_test.py`

Coverage includes:

- Embree availability/version
- `lsi` equivalence against `rt.run_cpu(...)`
- `pip` equivalence against `rt.run_cpu(...)`
- `overlay` equivalence against `rt.run_cpu(...)`
- `ray_tri_hitcount` equivalence against `rt.run_cpu(...)`

### Demos / Docs

Added:

- `/Users/rl2025/rtdl_python_only/examples/rtdl_embree_demo.py`

Updated:

- `/Users/rl2025/rtdl_python_only/Makefile`
- `/Users/rl2025/rtdl_python_only/README.md`
- `/Users/rl2025/rtdl_python_only/docs/rtdl/README.md`
- `/Users/rl2025/rtdl_python_only/docs/rtdl/programming_guide.md`
- `/Users/rl2025/rtdl_python_only/docs/rtdl/workload_cookbook.md`

## Design Boundary

The Embree backend keeps the same logical local input contract as the CPU
simulator:

- segments, points, triangles, and rays are logical records or dataclasses
- polygons use inline `vertices`

So the Embree backend is a local native runtime over the current logical RTDL
surface, not a direct execution of the lower-level polygon-ref memory layout
used by the RayJoin lowering/codegen path.

## Evidence

Local verification passed:

- `make test` -> 32 tests passed
- `make build` -> passed
- `make run-rtdsl-embree` -> passed

Observed Embree demo output:

- Embree version `(4, 4, 0)`
- materialized LSI rows
- materialized PIP rows
- materialized overlay rows
- materialized ray hit-count rows

## Summary

Goal 7 now provides the first real native backend/runtime for RTDL on this Mac.

The current workload surface can now:

- compile
- lower/codegen
- execute through Python reference semantics
- execute through Embree native runtime semantics
