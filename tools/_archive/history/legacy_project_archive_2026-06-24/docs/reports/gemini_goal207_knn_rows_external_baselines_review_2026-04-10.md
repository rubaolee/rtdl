# Goal 207 Review: KNN Rows External Baselines

## Verdict

The implementation for Goal 207 successfully integrates SciPy and PostGIS as external baselines for `knn_rows`, meticulously preserving the frozen `knn_rows` contract and providing robust testing.

## Findings

- **Contract Preservation**: Both SciPy and PostGIS implementations strictly adhere to the `knn_rows` contract, including per-query ordering by distance then `neighbor_id`, global grouping by `query_id`, explicit 1-based `neighbor_rank`, and emitting all available rows when `k` candidates are not met. This was verified through direct comparisons with the Python reference.
- **PostGIS Helper Bounded and Honest**: The PostGIS helper utilizes temporary tables and parameterized queries, preventing SQL injection and ensuring data isolation per run. The SQL generated correctly implements kNN using `CROSS JOIN LATERAL`, `ST_DWithin` (for spatial filtering), and `ROW_NUMBER() OVER` for ranking, ordered by `q.geom <-> s.geom` (for efficient spatial indexing) and distance/ID for tie-breaking. It is appropriately bounded by the `LIMIT %s` clause.
- **Sufficiency of Tests and Docs**:
    - **Documentation**: `goal_207_knn_rows_external_baselines.md` clearly outlines the goal, scope, non-goals, and acceptance criteria. `goal207_knn_rows_external_baselines_2026-04-10.md` summarizes the implementation and verification steps. Both appropriately state that SciPy/PostGIS are optional comparison dependencies.
    - **Tests**: `goal207_knn_rows_external_baselines_test.py` provides comprehensive unit tests, including:
        - Direct assertion of parity between SciPy and Python reference for authored and public fixture cases.
        - Verification of correct global ordering by `query_id`.
        - Detailed inspection of the generated PostGIS SQL to ensure correct spatial and ranking logic.
        - Use of mock objects (`_FakeKDTree`, `_FakePostgisConnection`) to enable testing without requiring external installations, enhancing test reliability and speed.
        - Confirmation that the `baseline_runner` correctly integrates and utilizes these new external backends.
    - The verification steps in the report (`docs/reports/goal207_knn_rows_external_baselines_2026-04-10.md`) confirm successful execution of these tests.

## Summary

Goal 207 successfully establishes external baseline comparisons for the `knn_rows` workload using SciPy's `cKDTree` and a well-defined PostGIS helper. The implementation rigorously maintains the RTDL contract. Comprehensive testing, including mocked environments and validation against a public dataset, confirms correctness and robustness. The documentation clearly defines the scope and optional nature of these baselines. This work provides valuable external validation for `knn_rows` without altering its core contract.
