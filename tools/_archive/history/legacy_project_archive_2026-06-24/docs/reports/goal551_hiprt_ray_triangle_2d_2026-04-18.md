# Goal 551: HIPRT 2D Ray/Triangle Hit Count

Date: 2026-04-18

## Goal

Implement `ray_triangle_hit_count` for `Ray2DLayout` / `Triangle2DLayout` on the HIPRT backend.

## Implementation Summary

- Added native HIPRT `rtdl_hiprt_run_ray_hitcount_2d`.
- Added HIPRT AABB-list custom primitives for build-side 2D triangles.
- Added a HIPRT custom intersection function `intersectRtdlTriangle2D`.
- The custom function mirrors the CPU reference shape:
  - test whether either finite ray-segment endpoint lies in the triangle;
  - otherwise test finite ray-segment intersection against all three triangle edges;
  - degenerate/parallel edge intersections follow the CPU `exact=False` behavior.
- Added Python `ctypes` dispatch through `ray_triangle_hit_count_2d_hiprt(...)`.
- Updated `rt.run_hiprt(...)` so matching `Ray2DLayout` / `Triangle2DLayout` dispatches to the new 2D HIPRT path, while matching 3D layouts continue using the existing 3D HIPRT triangle-mesh path.
- Preserved no-CPU-fallback behavior. CPU reference is used only in tests.

## Bounds

- Supported predicate: `rt.ray_triangle_hit_count(exact=False)`.
- Supported layouts: `Ray2DLayout` / `Triangle2DLayout`.
- Required roles: rays/probe and triangles/build.
- Empty ray input returns an empty result.
- Empty triangle input emits zero hit counts for each ray.

## Correctness Evidence

Local macOS Python-level validation:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal546_hiprt_api_parity_skeleton_test \
  tests.goal547_hiprt_correctness_matrix_test \
  tests.goal551_hiprt_ray_triangle_2d_test

Ran 11 tests in 0.005s
OK (skipped=3)
```

Linux HIPRT validation on `lestat-lx1`:

```text
make build-hiprt HIPRT_PREFIX=$HOME/vendor/hiprt-official/hiprtSdk-2.2.0e68f54
PYTHONPATH=src:. python3 -m unittest \
  tests.goal546_hiprt_api_parity_skeleton_test \
  tests.goal547_hiprt_correctness_matrix_test \
  tests.goal550_hiprt_segment_intersection_test \
  tests.goal551_hiprt_ray_triangle_2d_test

Ran 14 tests in 8.666s
OK
```

Linux correctness matrix:

- Report: `/Users/rl2025/rtdl_python_only/docs/reports/goal551_hiprt_correctness_matrix_linux_2026-04-18.json`
- Summary: `pass=6`, `not_implemented=12`, `hiprt_unavailable=0`, `fail=0`
- HIPRT passing workloads:
  - `segment_intersection`
  - `ray_triangle_hit_count_2d`
  - `ray_triangle_hit_count_3d`
  - `fixed_radius_neighbors_3d`
  - `bounded_knn_rows_3d`
  - `knn_rows_3d`

## Honesty Boundary

This is a real HIPRT traversal-backed path. Build triangles are represented as HIPRT custom AABB primitives, and exact 2D finite-ray/triangle refinement runs in the HIPRT custom intersection function. It is not a CPU fallback and not a performance claim. Current validation is on the Linux NVIDIA GTX 1070 HIPRT/Orochi CUDA path; AMD GPU behavior is not proven.

## Status

Codex verdict: ACCEPT.

External AI review: Claude ACCEPT in `/Users/rl2025/rtdl_python_only/docs/reports/goal551_external_review_2026-04-18.md`.

Consensus: 2-AI ACCEPT. Goal 551 is closed.
