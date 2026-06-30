# Goal 552: HIPRT 2D Point-In-Polygon

Date: 2026-04-18

## Goal

Implement `point_in_polygon` for `Point2DLayout` / `Polygon2DRef` on the HIPRT backend.

## Implementation Summary

- Added native HIPRT `rtdl_hiprt_run_pip`.
- Added HIPRT AABB-list custom primitives for build-side polygon bounding boxes.
- Added device-side polygon refs and packed vertex storage.
- Added a HIPRT custom intersection function `intersectRtdlPolygon2D` that runs inclusive point-in-polygon refinement on GPU.
- Preserved public full-matrix semantics by initializing all point/polygon output rows on GPU with `contains=0`, then using HIPRT traversal to promote containing candidates to `contains=1`.
- Added Python `ctypes` dispatch through `point_in_polygon_hiprt(...)`.
- Preserved no-CPU-fallback behavior. CPU reference is used only in tests.

## Bounds

- Supported predicate: `rt.point_in_polygon(exact=False)`.
- Supported layouts: `Point2DLayout` / `Polygon2DRef`.
- Required roles: points/probe and polygons/build.
- Supported `boundary_mode`: `inclusive`.
- Supported `result_mode`: `full_matrix`.
- Empty point input or empty polygon input returns an empty result.
- Output capacity is bounded by `point_count * polygon_count`; overflow is rejected before GPU work.

## Correctness Evidence

Local macOS Python-level validation:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal546_hiprt_api_parity_skeleton_test \
  tests.goal547_hiprt_correctness_matrix_test \
  tests.goal552_hiprt_point_in_polygon_test

Ran 11 tests in 0.006s
OK (skipped=3)
```

Linux HIPRT validation on `lestat-lx1`:

```text
make build-hiprt HIPRT_PREFIX=$HOME/vendor/hiprt-official/hiprtSdk-2.2.0e68f54
PYTHONPATH=src:. python3 -m unittest \
  tests.goal546_hiprt_api_parity_skeleton_test \
  tests.goal547_hiprt_correctness_matrix_test \
  tests.goal552_hiprt_point_in_polygon_test

Ran 11 tests in 8.296s
OK
```

Linux correctness matrix:

- Report: `/Users/rl2025/rtdl_python_only/docs/reports/goal552_hiprt_correctness_matrix_linux_2026-04-18.json`
- Summary: `pass=7`, `not_implemented=11`, `hiprt_unavailable=0`, `fail=0`
- HIPRT passing workloads:
  - `segment_intersection`
  - `point_in_polygon`
  - `ray_triangle_hit_count_2d`
  - `ray_triangle_hit_count_3d`
  - `fixed_radius_neighbors_3d`
  - `bounded_knn_rows_3d`
  - `knn_rows_3d`

## Honesty Boundary

This is a real HIPRT traversal-backed path. Build polygons are represented as HIPRT custom AABB primitives, and exact inclusive point-in-polygon refinement runs in the HIPRT custom intersection function. Full-matrix zero-row initialization is performed on GPU, not CPU. This is not a performance claim. Current validation is on the Linux NVIDIA GTX 1070 HIPRT/Orochi CUDA path; AMD GPU behavior is not proven.

## Status

Codex verdict: ACCEPT.

External AI review: Claude ACCEPT in `/Users/rl2025/rtdl_python_only/docs/reports/goal552_external_review_2026-04-18.md`.

Consensus: 2-AI ACCEPT. Goal 552 is closed.
