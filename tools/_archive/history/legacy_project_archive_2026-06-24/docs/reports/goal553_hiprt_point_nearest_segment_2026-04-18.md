# Goal 553: HIPRT 2D Point-Nearest-Segment

Date: 2026-04-18

## Goal

Implement `point_nearest_segment` for `Point2DLayout` / `Segment2DLayout` on the HIPRT backend.

## Implementation Summary

- Added native HIPRT `rtdl_hiprt_run_point_nearest_segment`.
- Added HIPRT AABB-list custom primitives over build-side segments.
- Added a HIPRT custom intersection function `intersectRtdlPointSegmentDistance2D`.
- The custom function computes exact point-to-segment distance and returns `hit.t = distance`.
- The kernel traverses all eligible segment candidates and performs top-1 nearest selection per point with CPU-reference-compatible distance and segment-id tie breaking.
- Used a conservative global radius derived from the combined point/segment bounding box so all segments are eligible. This is correctness-first and not performance-forward.
- Added Python `ctypes` dispatch through `point_nearest_segment_hiprt(...)`.
- Preserved no-CPU-fallback behavior. CPU reference is used only in tests.

## Bounds

- Supported predicate: `rt.point_nearest_segment(exact=False)`.
- Supported layouts: `Point2DLayout` / `Segment2DLayout`.
- Required roles: points/probe and segments/build.
- Empty point input or empty segment input returns an empty result.

## Correctness Evidence

Local macOS Python-level validation:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal553_hiprt_point_nearest_segment_test

Ran 3 tests in 0.000s
OK (skipped=3)
```

Linux HIPRT validation on `lestat-lx1`:

```text
make build-hiprt HIPRT_PREFIX=$HOME/vendor/hiprt-official/hiprtSdk-2.2.0e68f54
PYTHONPATH=src:. python3 -m unittest \
  tests.goal553_hiprt_point_nearest_segment_test \
  tests.goal547_hiprt_correctness_matrix_test

Ran 5 tests in 9.200s
OK
```

Linux correctness matrix:

- Report: `/Users/rl2025/rtdl_python_only/docs/reports/goal553_hiprt_correctness_matrix_linux_2026-04-18.json`
- Summary: `pass=8`, `not_implemented=10`, `hiprt_unavailable=0`, `fail=0`
- HIPRT passing workloads:
  - `segment_intersection`
  - `point_in_polygon`
  - `ray_triangle_hit_count_2d`
  - `ray_triangle_hit_count_3d`
  - `point_nearest_segment`
  - `fixed_radius_neighbors_3d`
  - `bounded_knn_rows_3d`
  - `knn_rows_3d`

## Honesty Boundary

This is a real HIPRT traversal-backed path because segment candidate discovery and distance refinement are performed through HIPRT custom AABB traversal and a HIPRT custom intersection function. It is correctness-first: the global-radius lowering deliberately makes all segments eligible, so no performance-forward claim is made. Current validation is on the Linux NVIDIA GTX 1070 HIPRT/Orochi CUDA path; AMD GPU behavior is not proven.

## Status

Codex verdict: ACCEPT.

External AI review: Claude ACCEPT in `/Users/rl2025/rtdl_python_only/docs/reports/goal553_external_review_2026-04-18.md`.

Post-review cleanup: removed a duplicate `_HIPRT_PEER_PREDICATES` entry and refreshed the goal cross-reference for `point_nearest_segment`.

Consensus: 2-AI ACCEPT. Goal 553 is closed.
