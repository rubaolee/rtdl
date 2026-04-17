# External Review Report: Goal 452

**Date:** 2026-04-16

## Verdict
ACCEPT. Query-only results are mixed, but total setup-plus-10-query results strongly favor RTDL backends.

## Checked Evidence
This review was conducted against RTDL rebased on best-tested PostgreSQL configurations, without exhaustive PG tuning.

**Test Parameters:**
-   **Database:** PostgreSQL
-   **JSON Row Count:** 200,000
-   **Repeats:** 10
-   **DSN:** `dbname=postgres`
-   **Hash Match:** `true` for all tests

**Best PostgreSQL Modes Tested:**
-   `scan composite query+total`
-   `grouped_count composite query and no_index total`
-   `grouped_sum single_column query and covering total`

**Performance Comparison (RTDL Backend vs. PostgreSQL):**

| Mode                      | Backend | Query-Only Ratio | Total-Time Ratio |
| :------------------------ | :------ | :--------------- | :--------------- |
| `scan`                    | Embree  | 0.98x (Loses)    | 8.61x (Wins)     |
| `scan`                    | OptiX   | 1.44x (Wins)     | 5.88x (Wins)     |
| `scan`                    | Vulkan  | 1.20x (Wins)     | 6.19x (Wins)     |
| `grouped_count`           | Embree  | 0.92x (Loses)    | 9.04x (Wins)     |
| `grouped_count`           | OptiX   | 2.71x (Wins)     | 10.25x (Wins)    |
| `grouped_count`           | Vulkan  | 1.82x (Wins)     | 9.91x (Wins)     |
| `grouped_sum`             | Embree  | 1.02x (Barely Wins)| 7.84x (Wins)     |
| `grouped_sum`             | OptiX   | 3.08x (Wins)     | 9.84x (Wins)     |
| `grouped_sum`             | Vulkan  | 2.53x (Wins)     | 9.53x (Wins)     |

**Boundaries:**
-   Workloads are v0.7 synthetic database workloads.
-   No arbitrary SQL was used.
-   No general DBMS claims are made.
-   This report does not constitute release/stage/commit/tag/merge authorization.

## Findings
1.  **Query-Only Performance:** The query-only tests yielded mixed results. The Embree backend underperformed against PostgreSQL in `scan` and `grouped_count` scenarios, and showed only a marginal win (1.02x) for `grouped_sum`. OptiX and Vulkan backends demonstrated superior query-only performance across all tested modes, with wins ranging from 1.20x to 3.08x.
2.  **Total-Time Performance:** When considering the total execution time (including database setup and 10 query repetitions), all RTDL backends (Embree, OptiX, and Vulkan) showed significant performance advantages over PostgreSQL. These advantages ranged from 5.88x to an impressive 10.25x, indicating that RTDL's integrated pipeline and execution strategy provides substantial benefits beyond single-query optimizations.

## Conclusion
The review confirms that RTDL, when configured with best-tested PostgreSQL, offers a substantial performance uplift across its backends for common workloads. While single-query performance varies by backend and mode, the overall solution significantly outperforms PostgreSQL when considering the complete workflow of setup and multiple query executions. The boundaries of this evaluation are limited to synthetic workloads, excluding arbitrary SQL, and do not imply broader DBMS capabilities or release authorizations.
