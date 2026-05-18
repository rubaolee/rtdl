# Database Workloads

Status: current v2.0 release workload family.

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
PYTHONPATH=src:. python examples/v2_0/features/database/rtdl_db_conjunctive_scan.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/v2_0/features/database/rtdl_db_grouped_count.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/v2_0/features/database/rtdl_db_grouped_sum.py --backend cpu_python_reference
```

Then try native and RT backends when available:

```bash
PYTHONPATH=src:. python examples/v2_0/features/database/rtdl_db_conjunctive_scan.py --backend cpu
PYTHONPATH=src:. python examples/v2_0/features/database/rtdl_db_conjunctive_scan.py --backend embree
PYTHONPATH=src:. python examples/v2_0/features/database/rtdl_db_conjunctive_scan.py --backend optix
PYTHONPATH=src:. python examples/v2_0/features/database/rtdl_db_conjunctive_scan.py --backend vulkan
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

RTDL can accelerate fixed DB-style filtering and compact grouping when the app
uses the supported columnar payload contract. It is not a SQL database, storage
engine, optimizer, or transaction system.

Use the current performance table and app support matrix for release-facing
numbers. Older PostgreSQL comparison material is kept in the report archive for
audit work.

## Current Limits

- not a DBMS
- not arbitrary SQL execution
- no joins as a first-class RTDL DB feature
- one group key for grouped kernels
- integer-compatible `grouped_sum`
- not PostgreSQL-style storage, indexing, transactions, optimizer behavior, or
  arbitrary SQL
