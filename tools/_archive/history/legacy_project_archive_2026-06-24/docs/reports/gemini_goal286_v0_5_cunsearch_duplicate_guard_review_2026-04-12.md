## Verdict

The duplicate-point guard implemented for Goal 286 is technically coherent, the contract change is honest, and the live comparison path successfully avoids making misleading strict-parity claims when confronted with duplicate-point packages.

## Findings

1. **Technically Coherent Guard**: The duplicate detection in `src/rtdsl/rtnn_duplicate_audit.py` is efficiently implemented using a dictionary lookup keyed by strict `(x, y, z)` tuples. This achieves O(N + M) complexity instead of a naive O(N*M) Cartesian product, making it robust enough for reasonably sized point packages.
2. **Honest Contract Enforcement**: The `compare_bounded_fixed_radius_live_cunsearch` function in `src/rtdsl/rtnn_comparison.py` explicitly consults the guard before invoking the cuNSearch binary. If a cross-package duplicate is detected, execution short-circuits.
3. **Avoidance of Misleading Claims**: By short-circuiting, the system now yields an explicit blocked result with a descriptive note (e.g., `"Strict live cuNSearch comparison was blocked because the package contains exact cross-package duplicate points..."`). This prevents the test harness from proceeding, failing the row-count parity check, and masking the true cause of the discrepancy as a generic third-party engine failure.
4. **Comprehensive Test Coverage**: `tests/goal286_cunsearch_duplicate_guard_test.py` covers the necessary edge cases, proving that the guard allows clean packages, correctly identifies duplicate IDs across boundaries, and successfully aborts the `live_cunsearch` runner without attempting to launch the external process.

## Risks

* **Strict Float Equality**: The guard relies on exact floating-point equality `(query_point.x == search_point.x, etc.)`. If the point packages are generated or transformed using different parsing pipelines or precisions before this guard is hit, near-duplicates due to floating-point drift might slip past the guard. However, for "exact" duplicate prevention as stated in the requirements, this approach is completely appropriate.
* **Coarse Rejection**: The comparison path rejects the entire package if even a single duplicate pair is found. If real-world (e.g., Kitti) datasets naturally feature high rates of exact cross-package overlaps, this strict guard might drastically shrink the pool of eligible packages for live execution.

## Conclusion

The implementation correctly establishes a defensive boundary. It ensures that the system fails loudly and honestly when assumptions about strict point uniqueness are violated, rather than allowing cuNSearch to silently process excluded data and produce confusing strict-parity mismatch reports. The goal criteria are fully met.
and more transparent for future benchmarking against the cuNSearch backend.
