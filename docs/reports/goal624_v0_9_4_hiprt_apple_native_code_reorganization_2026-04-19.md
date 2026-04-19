# Goal624: v0.9.4 HIPRT And Apple Native Code Reorganization

Date: 2026-04-19

Status: implemented and accepted by Gemini Flash and Claude.

## Purpose

Reorganize the two newer native backend engines so they match the existing
Embree, OptiX, and Vulkan pattern:

- a small root wrapper file under `/Users/rl2025/rtdl_python_only/src/native/`
- backend-specific implementation chunks under a backend directory

This is a maintainability-only refactor. It must not change the public C ABI,
Python runtime API, backend behavior, or release claims.

## Files Changed

Apple backend:

- `/Users/rl2025/rtdl_python_only/src/native/rtdl_apple_rt.mm`
- `/Users/rl2025/rtdl_python_only/src/native/apple_rt/rtdl_apple_rt_prelude.mm`
- `/Users/rl2025/rtdl_python_only/src/native/apple_rt/rtdl_apple_rt_api.cpp`
- `/Users/rl2025/rtdl_python_only/src/native/apple_rt/rtdl_apple_rt_metal_compute.mm`
- `/Users/rl2025/rtdl_python_only/src/native/apple_rt/rtdl_apple_rt_mps_geometry.mm`

HIPRT backend:

- `/Users/rl2025/rtdl_python_only/src/native/rtdl_hiprt.cpp`
- `/Users/rl2025/rtdl_python_only/src/native/hiprt/rtdl_hiprt_prelude.h`
- `/Users/rl2025/rtdl_python_only/src/native/hiprt/rtdl_hiprt_kernels.cpp`
- `/Users/rl2025/rtdl_python_only/src/native/hiprt/rtdl_hiprt_core.cpp`
- `/Users/rl2025/rtdl_python_only/src/native/hiprt/rtdl_hiprt_api.cpp`

Documentation:

- `/Users/rl2025/rtdl_python_only/README.md`
- `/Users/rl2025/rtdl_python_only/docs/current_architecture.md`

## New Layout

The root Apple wrapper now includes:

```text
apple_rt/rtdl_apple_rt_prelude.mm
apple_rt/rtdl_apple_rt_api.cpp
apple_rt/rtdl_apple_rt_metal_compute.mm
apple_rt/rtdl_apple_rt_mps_geometry.mm
```

The root HIPRT wrapper now includes:

```text
hiprt/rtdl_hiprt_prelude.h
hiprt/rtdl_hiprt_kernels.cpp
hiprt/rtdl_hiprt_core.cpp
hiprt/rtdl_hiprt_api.cpp
```

The build targets remain unchanged:

```text
make build-apple-rt
make build-hiprt HIPRT_PREFIX=$HOME/vendor/hiprt-official/hiprtSdk-2.2.0e68f54
```

## Validation

Local macOS Apple backend build:

```text
make build-apple-rt
```

Result: built `/Users/rl2025/rtdl_python_only/build/librtdl_apple_rt.dylib`
successfully.

Local macOS Apple focused correctness suite:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal578_apple_rt_backend_test \
  tests.goal596_apple_rt_prepared_closest_hit_test \
  tests.goal597_apple_rt_masked_hitcount_test \
  tests.goal598_apple_rt_masked_segment_intersection_test \
  tests.goal603_apple_rt_native_contract_test \
  tests.goal604_apple_rt_ray_hitcount_2d_native_test \
  tests.goal605_apple_rt_point_neighbor_2d_native_test \
  tests.goal606_apple_rt_point_neighbor_3d_native_test \
  tests.goal607_apple_rt_point_in_polygon_positive_native_test \
  tests.goal608_apple_rt_segment_polygon_native_test \
  tests.goal609_apple_rt_point_nearest_segment_native_test \
  tests.goal610_apple_rt_polygon_pair_native_test \
  tests.goal611_apple_rt_overlay_compose_native_test \
  tests.goal616_apple_rt_compute_skeleton_test \
  tests.goal617_apple_rt_db_conjunctive_scan_test \
  tests.goal618_apple_rt_db_grouped_aggregation_test \
  tests.goal619_apple_rt_graph_bfs_test \
  tests.goal620_apple_rt_graph_triangle_match_test -v
```

Result: 73 tests OK.

Linux HIPRT build after syncing the changed tree to
`lestat-lx1:/tmp/rtdl_goal624_split`:

```text
make build-hiprt HIPRT_PREFIX=$HOME/vendor/hiprt-official/hiprtSdk-2.2.0e68f54
```

Result: built `/tmp/rtdl_goal624_split/build/librtdl_hiprt.so` successfully.
The only emitted warning came from vendor Orochi `fread` return-value handling,
not from RTDL split files.

Linux HIPRT focused correctness suite:

```text
export RTDL_HIPRT_LIB=$PWD/build/librtdl_hiprt.so
export LD_LIBRARY_PATH=$HOME/vendor/hiprt-official/hiprtSdk-2.2.0e68f54/hiprt/linux64:${LD_LIBRARY_PATH:-}
PYTHONPATH=src:. python3 -m unittest <HIPRT focused tests> -v
```

Result: 73 tests OK in 59.566 s.

## Codex Review

Codex accepts this as a mechanical maintainability refactor:

- Existing root filenames remain as build targets.
- New backend directories match the established OptiX/Vulkan/Embree pattern.
- Public exported function names remain unchanged.
- Python runtime files are untouched.
- Apple and HIPRT focused build/test gates pass on the appropriate host.

## Release Boundary

This goal does not add a new workload, improve performance, or change backend
claims. It only reduces maintenance risk by removing two large monolithic
backend files.

## External Consensus

Gemini 2.5 Flash verdict:

```text
ACCEPT
```

Gemini accepted the split as a behavior-preserving maintainability refactor
because build targets remain unchanged, exported ABI remains stable, Python
runtime files are untouched, and both backend focused test suites passed.

Claude verdict:

```text
ACCEPT
```

Claude specifically checked the `#include` aggregation strategy and accepted it
because each backend still compiles as one translation unit, preserving
anonymous-namespace scoping, macro visibility, and exported `extern "C"` names.

