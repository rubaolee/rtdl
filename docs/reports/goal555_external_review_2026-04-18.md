# Goal 555 External Review: HIPRT 2D Fixed-Radius and KNN

**Verdict: ACCEPT**

**Reviewer:** Claude Sonnet 4.6  
**Date:** 2026-04-18

## Summary

Goal 555 adds `fixed_radius_neighbors` and `knn_rows` (and `bounded_knn_rows`) on `Point2DLayout` using real HIPRT traversal. Implementation is consistent with the 3D path and correctness matrix shows pass=12, fail=0.

## What Was Reviewed

- `docs/reports/goal555_hiprt_2d_neighbors_2026-04-18.md`
- `src/native/rtdl_hiprt.cpp` (2D kernel and C entry points)
- `src/rtdsl/hiprt_runtime.py` (Python helpers and dispatch)
- `tests/goal555_hiprt_2d_neighbors_test.py`
- `docs/reports/goal555_hiprt_correctness_matrix_linux_2026-04-18.json`

## Findings

**Correct.** The lowering strategy is sound: search points encoded as AABBs expanded by query radius, query points as zero-length rays at z=0, custom intersection `intersectRtdlPointRadius2D` computes exact 2D Euclidean distance on-device. This matches the established 3D pattern.

**KNN reuse is appropriate.** `knn_rows_2d_hiprt` delegates to `fixed_radius_neighbors_2d_hiprt` with a conservative bounding radius from `_global_radius_for_all_2d_candidates`. The helper correctly uses only x/y (not z), and adds a 1e-6 epsilon to avoid degenerate single-point cases.

**Dispatch coverage is complete.** `hiprt_runtime.py` dispatches all three predicates (`fixed_radius_neighbors`, `knn_rows`, `bounded_knn_rows`) on `("Point2D","Point2D")` layout pairs. No CPU fallback is silently invoked.

**Tests are adequate.** Five tests cover: direct helper vs. CPU reference (both predicates), `run_hiprt` vs. CPU reference (both predicates), and empty-input edge cases. The `assert_rows_close` helper uses float-tolerant comparison (rel/abs tol 1e-6). All 5 passed on Linux HIPRT/Orochi CUDA.

**Correctness matrix.** Both new rows (`fixed_radius_neighbors_2d`, `knn_rows_2d`) show `parity=true`, row counts matching CPU reference (5 and 6 respectively).

## Blockers

None.

## Minor Notes

- Validation is on GTX 1070 (no RT cores) via HIPRT/Orochi CUDA; AMD GPU coverage remains future work, consistent with the project's honesty boundary.
- k_max <= 64 hard limit is documented and consistent with the 3D path.
