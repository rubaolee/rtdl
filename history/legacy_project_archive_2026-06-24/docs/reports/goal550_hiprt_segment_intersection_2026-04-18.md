# Goal 550: HIPRT 2D Segment Intersection

Date: 2026-04-18

## Goal

Implement the first 2D geometry workload from the Goal 550 HIPRT lowering plan: `segment_intersection` over 2D `Segment2DLayout` inputs.

## Implementation Summary

- Added native HIPRT `rtdl_hiprt_run_lsi`.
- Added a custom HIPRT AABB-list geometry over build-side right segments.
- Segment AABBs are padded in X, Y, and Z by `1e-4` to avoid backend-dependent misses for exactly horizontal or vertical segments.
- Added a HIPRT custom intersection function `intersectRtdlSegment2D` that mirrors the CPU reference line-segment intersection predicate:
  - parallel or nearly parallel segments do not hit;
  - finite segment parameters must satisfy `0 <= t <= 1` and `0 <= u <= 1`;
  - intersection coordinates are emitted as `left_origin + t * left_direction`.
- Added one HIPRT kernel thread per left/probe segment.
- Added conservative worst-case row capacity `left_count * right_count`, then compacted rows on host after GPU traversal.
- Added Python `ctypes` dispatch through `segment_intersection_hiprt(...)` and `rt.run_hiprt(...)`.
- Preserved no-CPU-fallback behavior. CPU reference is used only in tests.

## Bounds

- Supported predicate: `rt.segment_intersection(exact=False)`.
- Supported layouts: `Segment2DLayout` on both sides.
- Required roles: left/probe and right/build.
- Empty left or right input returns an empty result.
- Output capacity is bounded by `left_count * right_count`; overflow is rejected before GPU work.

## Correctness Evidence

Local macOS Python-level validation:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal546_hiprt_api_parity_skeleton_test \
  tests.goal547_hiprt_correctness_matrix_test \
  tests.goal550_hiprt_segment_intersection_test

Ran 11 tests in 0.004s
OK (skipped=3)
```

Linux HIPRT validation on `lestat-lx1`:

```text
make build-hiprt HIPRT_PREFIX=$HOME/vendor/hiprt-official/hiprtSdk-2.2.0e68f54
PYTHONPATH=src:. python3 -m unittest \
  tests.goal540_hiprt_probe_test \
  tests.goal541_hiprt_ray_hitcount_test \
  tests.goal543_hiprt_dispatch_test \
  tests.goal546_hiprt_api_parity_skeleton_test \
  tests.goal547_hiprt_correctness_matrix_test \
  tests.goal548_hiprt_fixed_radius_3d_test \
  tests.goal549_hiprt_3d_knn_test \
  tests.goal550_hiprt_segment_intersection_test

Ran 27 tests in 12.560s
OK
```

Linux focused revalidation after AABB padding:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal550_hiprt_segment_intersection_test \
  tests.goal547_hiprt_correctness_matrix_test

Ran 5 tests in 6.686s
OK
```

Linux correctness matrix:

- Report: `/Users/rl2025/rtdl_python_only/docs/reports/goal550_hiprt_correctness_matrix_linux_2026-04-18.json`
- Summary: `pass=5`, `not_implemented=13`, `hiprt_unavailable=0`, `fail=0`
- HIPRT passing workloads:
  - `segment_intersection`
  - `ray_triangle_hit_count_3d`
  - `fixed_radius_neighbors_3d`
  - `bounded_knn_rows_3d`
  - `knn_rows_3d`

## Honesty Boundary

This is a real HIPRT traversal-backed path. Build segments are represented as HIPRT custom AABB primitives, and exact segment/segment refinement runs in the HIPRT custom intersection function. It is not a CPU fallback and not a performance claim. Current validation is on the Linux NVIDIA GTX 1070 HIPRT/Orochi CUDA path; AMD GPU behavior is not proven.

## Status

Codex verdict: ACCEPT.

External AI review: Claude ACCEPT in `/Users/rl2025/rtdl_python_only/docs/reports/goal550_segment_intersection_external_review_2026-04-18.md`.

Post-review advisory response: implemented X/Y/Z AABB padding and re-ran focused Linux validation plus the HIPRT matrix.

Consensus: 2-AI ACCEPT. Goal 550 segment-intersection subgoal is closed.
