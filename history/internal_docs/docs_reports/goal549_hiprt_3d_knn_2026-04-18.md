# Goal 549: HIPRT 3D KNN Rows Through Traversal

Date: 2026-04-18

## Goal

Add HIPRT support for 3D nearest-neighbor row workloads on top of the Goal 548 custom AABB traversal path.

## Implementation Summary

- Added `bounded_knn_rows_3d_hiprt(...)` in the Python HIPRT dispatch layer.
- Added `knn_rows_3d_hiprt(...)` in the Python HIPRT dispatch layer.
- `bounded_knn_rows` reuses the native HIPRT fixed-radius custom traversal with the caller-provided radius and adds 1-based `neighbor_rank`.
- `knn_rows` computes a conservative global radius from the query/search bounding box, uses the same HIPRT custom traversal to collect all candidates, and ranks the nearest `k` rows per query.
- The implementation preserves no-CPU-fallback behavior. It does not call the CPU reference path to compute results.
- The implementation is correctness-oriented. Unbounded KNN with a global radius is not expected to be performance-leading because it deliberately makes all search points eligible candidates.

## Bounds

- Supported layouts: `Point3DLayout` query points and `Point3DLayout` search points.
- Supported predicates:
  - `rt.bounded_knn_rows(radius=..., k_max=...)`
  - `rt.knn_rows(k=...)`
- Current `k` / `k_max` ceiling inherits the Goal 548 native traversal cap: `<= 64`.
- 2D KNN remains explicit `NotImplementedError`.

## Correctness Evidence

Local macOS Python-level validation:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal547_hiprt_correctness_matrix_test \
  tests.goal549_hiprt_3d_knn_test

Ran 6 tests in 0.004s
OK (skipped=4)
```

Linux HIPRT validation on `lestat-lx1`:

```text
make build-hiprt HIPRT_PREFIX=$HOME/vendor/hiprt-official/hiprtSdk-2.2.0e68f54
PYTHONPATH=src:. python3 -m unittest \
  tests.goal547_hiprt_correctness_matrix_test \
  tests.goal549_hiprt_3d_knn_test

Ran 6 tests in 7.137s
OK
```

Linux correctness matrix:

- Report: `/Users/rl2025/rtdl_python_only/docs/reports/goal549_hiprt_correctness_matrix_linux_2026-04-18.json`
- Summary: `pass=4`, `not_implemented=14`, `hiprt_unavailable=0`, `fail=0`
- HIPRT passing workloads:
  - `ray_triangle_hit_count_3d`
  - `fixed_radius_neighbors_3d`
  - `bounded_knn_rows_3d`
  - `knn_rows_3d`

## Honesty Boundary

This is a real HIPRT traversal-backed implementation because candidate discovery still runs through HIPRT custom AABB geometry and custom any-hit traversal. It is not a performance claim. For unbounded KNN, the global-radius lowering is intentionally broad so that correctness is exact; this may reduce pruning effectiveness and should be improved before any performance-forward claim.

Current validation is on the Linux NVIDIA GTX 1070 HIPRT/Orochi CUDA path. AMD GPU behavior is not proven.

## Status

Codex verdict: ACCEPT.

External AI review: Claude ACCEPT in `/Users/rl2025/rtdl_python_only/docs/reports/goal549_external_review_2026-04-18.md`.

Consensus: 2-AI ACCEPT. Goal 549 is closed.
