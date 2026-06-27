# Goal 437: v0.7 RT DB Repeated-Query Performance Gate

Date: 2026-04-16

## Verdict

Goal 437 is implemented and ready for external review.

The repeated-query gate consolidates the Linux evidence from the native prepared DB dataset goals:

- Goal 434: Embree prepared scene reuse
- Goal 435: OptiX prepared GAS/traversable reuse
- Goal 436: Vulkan prepared BLAS/TLAS reuse

Each backend is compared with PostgreSQL on `lestat-lx1` at 200,000 rows and 10 repeated queries per workload. PostgreSQL setup includes temp table load, per-predicate indexes, row-id index, and `ANALYZE` through `prepare_postgresql_denorm_table`.

## Reproducible Summary Artifact

Command:

```text
python3 scripts/goal437_repeated_query_db_perf_summary.py > docs/reports/goal437_repeated_query_db_perf_summary_2026-04-16.json
```

Raw summary JSON:

```text
/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal437_repeated_query_db_perf_summary_2026-04-16.json
```

Source JSON files:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal434_embree_native_prepared_db_dataset_linux_2026-04-16.json`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal435_optix_native_prepared_db_dataset_linux_2026-04-16.json`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal436_vulkan_native_prepared_db_dataset_linux_2026-04-16.json`

## Repeated-Query Performance

### Conjunctive Scan

| Engine | Prepare/setup once | Median query | Total 10 queries | PostgreSQL setup | PostgreSQL median query | PostgreSQL total | Total speedup vs PG |
|---|---:|---:|---:|---:|---:|---:|---:|
| Embree | 2.927411 s | 0.018753 s | 3.113833 s | 12.259940 s | 0.029153 s | 12.549844 s | 4.03x |
| OptiX | 2.693911 s | 0.011617 s | 3.239599 s | 10.121371 s | 0.026345 s | 10.384042 s | 3.21x |
| Vulkan | 2.764802 s | 0.013603 s | 3.217003 s | 10.145430 s | 0.026498 s | 10.409818 s | 3.24x |

### Grouped Count

| Engine | Prepare/setup once | Median query | Total 10 queries | PostgreSQL setup | PostgreSQL median query | PostgreSQL total | Total speedup vs PG |
|---|---:|---:|---:|---:|---:|---:|---:|
| Embree | 2.914072 s | 0.015879 s | 3.073149 s | 12.352186 s | 0.022302 s | 12.575946 s | 4.09x |
| OptiX | 2.548569 s | 0.004479 s | 2.594221 s | 10.440232 s | 0.020238 s | 10.643651 s | 4.10x |
| Vulkan | 2.606685 s | 0.007032 s | 2.678680 s | 10.042244 s | 0.020443 s | 10.247574 s | 3.83x |

### Grouped Sum

| Engine | Prepare/setup once | Median query | Total 10 queries | PostgreSQL setup | PostgreSQL median query | PostgreSQL total | Total speedup vs PG |
|---|---:|---:|---:|---:|---:|---:|---:|
| Embree | 2.774800 s | 0.035328 s | 3.127755 s | 10.601887 s | 0.038366 s | 10.986007 s | 3.51x |
| OptiX | 2.414290 s | 0.010184 s | 2.516861 s | 12.867585 s | 0.035046 s | 13.218746 s | 5.25x |
| Vulkan | 2.463052 s | 0.013521 s | 2.600840 s | 12.660917 s | 0.035282 s | 13.014906 s | 5.00x |

## Break-Even Read

For all measured backend/workload pairs, the RTDL prepared-dataset setup time is lower than the PostgreSQL setup/index time and the RTDL median query time is lower than the PostgreSQL median query time. Under this fresh-setup benchmark, the break-even status is therefore `wins_from_first_query` for every measured pair.

This should not be generalized to all database use cases. PostgreSQL is a full database system with durable storage, optimizer behavior, concurrent access, richer SQL, and mature indexing. This RTDL result is specifically for bounded in-memory RT-style kernels over synthetic denormalized rows.

## Correctness Boundary

The source JSON files assert row-count and row-hash equality against PostgreSQL for every measured workload:

- `conjunctive_scan`: 22,268 rows, hash `19461bddd250025c3d24a174f82e5f66046e40dded85ef27614143a08c9590c8`
- `grouped_count`: 8 rows, hash `869ed487d7eda66115bb00dceaf75df016fac2e2e0a6d75119f993d63137a77b`
- `grouped_sum`: 8 rows, hash `123b2f6fc6fa9f69e2df8da24441116549271314ef3b602482467c6ad47ed330`

## Claim Boundary

The justified v0.7 claim is:

RTDL can express three bounded database-style workload kernels and run them through native prepared RT backends that reuse acceleration structures; on the Linux 200k-row synthetic gate, Embree, OptiX, and Vulkan all beat PostgreSQL fresh setup plus 10 repeated queries for the measured cases.

The unjustified claims remain excluded:

- RTDL is not a full database system.
- This does not replace PostgreSQL.
- This does not prove arbitrary SQL acceleration.
- This does not yet prove final large-table ingestion throughput, because Python-to-native table transfer still uses the compatibility ctypes row path.
