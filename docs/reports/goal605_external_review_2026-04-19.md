# Goal605 External Review: Apple RT 2D Point-Neighborhood Native

Date: 2026-04-19

Verdict: **ACCEPT**

## Scope check

The goal claims native MPS-backed candidate discovery for `fixed_radius_neighbors`, `bounded_knn_rows`, and `knn_rows` on `Point2D/Point2D` inputs only. No 3D point-neighborhood coverage and no unrelated workloads are claimed.

All three claims are verified correct.

## Native primitive (`rtdl_apple_rt.mm`)

`rtdl_apple_rt_run_fixed_radius_neighbors_2d` (line 1074) is the sole new native C entry point. It:

- Builds an axis-aligned bounding box prism (8 MPS triangles, XY bounds `[sx±r, sy±r]`, z in `[-1, 1]`) for each search point.
- Shoots a pure-z ray from `(qx, qy, -1)` with direction `(0, 0, 2)` for each query, which intersects a box iff `|qx - sx| <= r` and `|qy - sy| <= r`.
- After each MPS pass, performs CPU exact Euclidean distance check (`<= radius + 1e-9`) to discard the corners of the square overestimate.
- Sorts candidates by distance then `neighbor_id` and applies `k_max`.

The box-then-exact-filter correctness argument is sound. The box is a strict superset of the Euclidean disk; no true neighbor can be missed.

## `bounded_knn_rows` and `knn_rows`

Both delegate to `fixed_radius_neighbors_2d_apple_rt` in Python (lines 815–837 of `apple_rt_runtime.py`) and then call `_rank_neighbor_rows` to add `neighbor_rank`. No separate C function is needed.

`knn_rows` uses `_combined_point2d_radius` (diagonal of the combined point bounding box + ε) as a dataset-level conservative radius, guaranteeing all points are candidates. The report explicitly labels this correctness-first with no throughput claim. That is accurate and not an overclaim.

## Contract (support matrix / predicate mode)

- `apple_rt_support_matrix()` reports `shape_dependent` / `native_shapes: ("Point2D/Point2D",)` for all three predicates. ✓
- `apple_rt_predicate_mode()` returns `native_mps_rt_2d_else_cpu_reference_compat` for all three. ✓
- `native_only=True` with 3D inputs (or unsupported predicates) still raises `NotImplementedError` with a clear message scoping the supported shapes. ✓

## 3D / unrelated workload exclusion

No 3D point-neighborhood path is added or implied. LSI, ray/triangle, and all other predicates are unmodified. The support matrix entries for those predicates are unchanged.

## Tests (`goal605_apple_rt_point_neighbor_2d_native_test.py`)

Four tests, all gated on `apple_rt_available()`:

| Test | What it covers |
|---|---|
| `test_fixed_radius_native_only_matches_cpu` | `run_apple_rt(..., native_only=True)` vs CPU reference for `fixed_radius_neighbors` |
| `test_bounded_knn_native_only_matches_cpu` | Same for `bounded_knn_rows` |
| `test_knn_native_only_matches_cpu` | Same for `knn_rows` |
| `test_direct_fixed_radius_helper_matches_cpu` | Direct call to `fixed_radius_neighbors_2d_apple_rt` vs `fixed_radius_neighbors_cpu` |

The test fixture exercises two queries with four search points at varying distances, covering within-radius, boundary, and out-of-radius cases. `_assert_rows_almost_equal` checks key sets and numeric values to 5 decimal places. This is sufficient to verify CPU parity.

## Version

`rtdl_apple_rt_get_version` returns `(0, 9, 3)`. ✓

## Honesty boundary

The report makes no throughput or performance claims. The implementation is correctly described as a correctness-first candidate filter with CPU refinement. This is consistent with what the code does.

## No issues found

All claimed capabilities are present in the code. No 3D coverage is implied. No unrelated workloads are touched. The contract metadata is accurate. Tests are meaningful and cover the public interface.
