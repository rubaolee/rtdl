# Database Workloads

Status: active bounded `v0.7` branch line, not the last tagged mainline release.

RTDL's first database-style workload family is a bounded analytical kernel
surface over denormalized rows:

- `conjunctive_scan`
- `grouped_count`
- `grouped_sum`

Use these workloads when you want to express a small, fixed analytical kernel
that RTDL can lower to RT-style row discovery and exact refinement. Do not use
this as a general SQL or DBMS replacement.

## Run First

```bash
PYTHONPATH=src:. python examples/rtdl_db_conjunctive_scan.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/rtdl_db_grouped_count.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/rtdl_db_grouped_sum.py --backend cpu_python_reference
```

Then try native and RT backends when available:

```bash
PYTHONPATH=src:. python examples/rtdl_db_conjunctive_scan.py --backend cpu
PYTHONPATH=src:. python examples/rtdl_db_conjunctive_scan.py --backend embree
PYTHONPATH=src:. python examples/rtdl_db_conjunctive_scan.py --backend optix
PYTHONPATH=src:. python examples/rtdl_db_conjunctive_scan.py --backend vulkan
```

On Linux GPU hosts, build GPU backend libraries first:

```bash
make build-optix
make build-vulkan
```

## Prepared Dataset APIs

The repeated-query path can prepare one native dataset and then run multiple
queries against the same acceleration structure:

- `prepare_embree_db_dataset(table_rows, primary_fields=...)`
- `prepare_optix_db_dataset(table_rows, primary_fields=...)`
- `prepare_vulkan_db_dataset(table_rows, primary_fields=...)`

The prepared RT state is backend-specific:

- Embree: scene over encoded row AABBs
- OptiX: custom-primitive GAS/traversable over encoded row AABBs
- Vulkan: BLAS/TLAS over encoded row AABBs

## Current Evidence

The current canonical Linux 200k-row comparison is Goal 452. It rebases RTDL
native prepared columnar dataset timings against the best PostgreSQL index modes
tested in Goal 451:

- [Goal 452 RTDL vs best-tested PostgreSQL performance rebase](../../reports/goal452_v0_7_rtdl_vs_best_tested_postgresql_perf_rebase_2026-04-16.md)
- [Goal 450 Linux correctness and performance refresh](../../reports/goal450_v0_7_linux_correctness_and_performance_refresh_2026-04-16.md)
- [Goal 451 PostgreSQL baseline index audit](../../reports/goal451_v0_7_postgresql_baseline_index_audit_2026-04-16.md)
- [v0.7 support matrix](../../release_reports/v0_7/support_matrix.md)

The current honest performance summary is:

- query-only results against best-tested PostgreSQL are mixed
- Embree loses query-only for `conjunctive_scan` and `grouped_count`
- OptiX and Vulkan win query-only for all measured workloads
- all three RTDL backends win setup-plus-10-query total time in this measured
  Linux evidence

## Current Limits

- not a DBMS
- not arbitrary SQL execution
- no joins as a first-class RTDL DB feature
- one group key for grouped kernels
- integer-compatible `grouped_sum`
- not PostgreSQL-style storage, indexing, transactions, optimizer behavior, or
  arbitrary SQL
