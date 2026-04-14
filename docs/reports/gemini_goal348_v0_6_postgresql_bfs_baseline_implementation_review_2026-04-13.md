# Review: RTDL v0.6 PostgreSQL BFS Baseline Implementation

**Review Date**: 2026-04-13

## Executive Summary

The RTDL v0.6 PostgreSQL BFS baseline implementation **fully aligns with the bounded plan, demonstrates coherent SQL structure for correctness, and is supported by meaningful tests.** It is clearly **ready to serve as the first PostgreSQL graph baseline** for the project. The implementation respects the explicit non-claims outlined in the planning phase, focusing strictly on its role as an external, bounded correctness baseline.

## Detailed Verdict

### 1. Does the PostgreSQL BFS baseline match the bounded plan?

**Verdict: Yes, the implementation precisely matches the bounded plan.**

The initial planning document (`gemini_goal347_v0_6_postgresql_graph_baseline_plan_review_2026-04-13.md`) clearly defined PostgreSQL's role as a *bounded external correctness and performance baseline*, emphasizing "Explicit Non-Claims" and "Bounded Scope." The implementation report (`goal348_v0_6_postgresql_bfs_baseline_implementation_2026-04-13.md`) explicitly reiterates these boundaries, stating it is "not a graph-specialized engine claim," "not a paper-equivalent system claim," and "not the primary truth path."

The Python module `src/rtdsl/external_baselines.py` implements the BFS logic using PostgreSQL's native recursive CTEs, directly fulfilling the requirement to leverage existing database capabilities for graph operations. The use of temporary edge tables (`CREATE TEMP TABLE ... ON COMMIT DROP`) further reinforces the bounded, transient nature of this baseline work, avoiding any persistent schema changes.

### 2. Is the SQL shape coherent for bounded correctness work?

**Verdict: Yes, the SQL shape is coherent, idiomatic, and robust for correctness comparisons.**

The `build_postgresql_bfs_levels_sql` function in `src/rtdsl/external_baselines.py` constructs a `WITH RECURSIVE bfs` CTE query. This is the standard and most appropriate SQL construct for breadth-first traversals in PostgreSQL. Key aspects contributing to coherence include:
*   **Recursive CTE:** Correctly implements the iterative level-by-level expansion of BFS.
*   **`MIN(level)` aggregation:** Ensures that each `vertex_id` is assigned its shortest path level (first encountered level), which is fundamental to BFS correctness.
*   **`ORDER BY level, vertex_id`:** Provides a canonical, deterministic output order essential for reliable correctness comparisons against a truth path.
*   **Temporary Tables:** The `prepare_postgresql_graph_edges_table` function correctly uses `CREATE TEMP TABLE ... ON COMMIT DROP`, making the graph representation ephemeral and self-cleaning.
*   **Indexing:** The creation of `src` and `dst` indexes on the temporary table is a good practice, ensuring reasonable performance for graph traversals even on temporary structures, which is relevant for performance baseline comparisons.

The SQL generated is clean, readable, and directly translatable to the BFS algorithm, making it well-suited for its intended purpose.

### 3. Are the tests meaningful?

**Verdict: Yes, the tests are highly meaningful and effectively validate the implementation.**

The test file `tests/goal348_postgresql_bfs_baseline_test.py` provides excellent coverage through:
*   **Targeted Unit Tests:** `test_postgresql_bfs_sql_contains_recursive_cte` directly verifies the structure of the generated SQL, confirming the presence of the `WITH RECURSIVE` clause and correct ordering, ensuring the SQL shape is as expected.
*   **Truth Path Validation:** The `test_postgresql_bfs_runner_matches_python_truth_path` is particularly strong. It utilizes a custom `_FakePostgresqlBfsConnection` and `_FakePostgresqlBfsCursor` to mock the PostgreSQL database interaction. This allows for unit testing the `run_postgresql_bfs_levels` function against `rt.bfs_levels_cpu` (the Python truth path) without needing a live database. This approach isolates the logic and validates that the PostgreSQL baseline produces identical results to the established reference implementation for a small, representative graph.
*   **Execution Verification:** The tests also assert that the expected SQL commands (`CREATE TEMP TABLE`, `WITH RECURSIVE bfs`) are indeed "executed" via the mock, confirming the control flow of the runner.

The use of fakes is a robust strategy for ensuring the correctness of the generated SQL and its interpretation without the overhead of actual database setup in a unit testing context.

### 4. Is this ready as the first PostgreSQL graph baseline?

**Verdict: Yes, this is unequivocally ready as the first PostgreSQL graph baseline.**

The implementation provides:
*   **Core BFS Functionality:** The `run_postgresql_bfs_levels` in `external_baselines.py` delivers the essential BFS algorithm using PostgreSQL.
*   **Necessary Utilities:** Connection handling (`connect_postgresql`), table preparation (`prepare_postgresql_graph_edges_table`), and SQL generation (`build_postgresql_bfs_levels_sql`) are all present and functional.
*   **Clear Boundaries:** The implementation adheres strictly to the bounded definition of a "PostgreSQL baseline" as an external correctness and performance check, avoiding any misrepresentation of PostgreSQL as a specialized graph engine.
*   **Validated Correctness:** The meaningful tests provide confidence that the implementation produces correct results against the Python truth path.
*   **Integration:** The relevant functions are correctly exposed via `src/rtdsl/__init__.py`.

This baseline provides a solid, verifiable foundation for future PostgreSQL graph baseline work and contributes to the overall `v0.6` graph strategy.
