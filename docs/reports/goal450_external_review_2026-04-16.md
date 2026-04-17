# External Review Report: goal450_external_review_2026-04-16

## Verdict
ACCEPT

## Checked Evidence
*   **Host:** Linux (lestat-lx1)
*   **Database:** PostgreSQL 16.13
*   **RTDL Runtimes:** Embree (4,3,0), OptiX (9,0,0), Vulkan (0,1,0)
*   **Correctness Log:** /Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/linux_correctness_db_sweep_with_postgresql_2026-04-16.log
*   **Performance JSON:** /Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal450_columnar_repeated_query_perf_linux_2026-04-16.json

## Findings
*   **Correctness:** 75 tests were executed on Linux with PostgreSQL 16.13, all passing within 3.267s. The RTDL_POSTGRESQL_DSN was set to dbname=postgres.
*   **Performance:**
    *   Columnar transfer was used for repeated queries.
    *   The dataset consisted of 200,000 rows, with 10 repeated queries.
    *   All backend row_hash values matched PostgreSQL row_hash values, indicating data integrity.
    *   Significant speedups were observed compared to the PostgreSQL setup + 10 queries:
        *   **Scan:** Embree 12.53x, OptiX 8.55x, Vulkan 9.00x
        *   **Grouped Count:** Embree 10.50x, OptiX 11.90x, Vulkan 11.51x
        *   **Grouped Sum:** Embree 9.54x, OptiX 11.97x, Vulkan 11.60x
*   **Boundaries:** The tests adhered to the specified boundaries: v0.7 DB workloads only, no arbitrary SQL, no DBMS claims, and no release/stage/commit/tag/merge authorization.

## Conclusion
The evidence provided supports the bounded Linux correctness and performance refresh for v0.7 DB workloads. The RTDL system, with Embree, OptiX, and Vulkan backends, successfully passed all correctness tests and demonstrated substantial performance gains over the PostgreSQL baseline for repeated columnar queries.
