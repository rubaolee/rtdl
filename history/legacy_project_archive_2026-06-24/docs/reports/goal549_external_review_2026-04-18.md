# Goal 549 External Review: HIPRT 3D KNN Rows

Date: 2026-04-18
Reviewer: Claude Sonnet 4.6 (external AI review)

## Verdict: ACCEPT

No blockers.

## Summary

Goal 549 adds `bounded_knn_rows_3d_hiprt` and `knn_rows_3d_hiprt` to the HIPRT dispatch layer by reusing the Goal 548 fixed-radius custom AABB traversal. The implementation is clean and minimal.

## What Was Reviewed

- `docs/reports/goal549_hiprt_3d_knn_2026-04-18.md` — design/implementation report
- `src/rtdsl/hiprt_runtime.py` — dispatch layer implementation
- `tests/goal549_hiprt_3d_knn_test.py` — correctness tests
- `scripts/goal547_hiprt_correctness_matrix.py` — matrix harness
- `docs/reports/goal549_hiprt_correctness_matrix_linux_2026-04-18.json` — Linux run results

## Correctness Assessment

**Linux correctness matrix**: `pass=4, fail=0, hiprt_unavailable=0`. All four implemented HIPRT workloads pass with exact CPU-reference parity:
- `ray_triangle_hit_count_3d` ✓
- `fixed_radius_neighbors_3d` ✓
- `bounded_knn_rows_3d` ✓
- `knn_rows_3d` ✓

**Test suite**: 4 tests cover both direct helper calls and `run_hiprt` dispatch for both predicates, each validated against CPU reference. Tests pass on macOS (skip=4, library unavailable) and Linux HIPRT/CUDA (0 skips, 0 failures).

## Implementation Review

**`bounded_knn_rows_3d_hiprt`**: Delegates directly to `fixed_radius_neighbors_3d_hiprt` with caller-supplied `radius`/`k_max`, then appends `neighbor_rank` via `_add_neighbor_rank`. Correct.

**`knn_rows_3d_hiprt`**: Computes a conservative global radius as the bounding-box diagonal of all combined query+search points plus 1e-6, ensuring every search point is reachable from every query point. Passes `k_max=k` to the fixed-radius path. Correct for exact-recall guarantee; the report is honest that this is not a performance-forward strategy.

**`_add_neighbor_rank`**: Iterates rows in native output order, assigning rank 1…k per `query_id` group, truncating at k. This relies on the native layer returning neighbors sorted by distance within each query group — a property inherited from Goal 548 and implicitly validated by the CPU-parity tests.

**`_validate_hiprt_kernel`**: Routes `knn_rows` and `bounded_knn_rows` through the Point3DLayout guard correctly. The dispatch in `run_hiprt` correctly extracts `k` vs `radius`/`k_max` from predicate options.

**`k_max ≤ 64` ceiling**: Inherited from Goal 548. `knn_rows_3d_hiprt` propagates `k_max=k`, so a `k > 64` call fails with a clear `ValueError`. Acceptable; the constraint is documented.

## Observations (Non-Blocking)

- **`_add_neighbor_rank` sort assumption**: The function assumes rows arrive in `query_id`-consecutive, distance-ascending order from the native layer. This is validated implicitly by the CPU-parity tests but is not explicitly guarded in Python. Not a bug given current test coverage; worth a comment if this function is ever reused outside the HIPRT path.
- **AMD GPU coverage**: Not tested. Noted in the honesty boundary.
- **Unbounded KNN global radius**: Deliberately broad for correctness; performance improvement is deferred and clearly flagged.

## Conclusion

The implementation is correct, minimal, and honest about its scope. The correctness matrix shows no regressions and two new passing workloads. ACCEPT.
