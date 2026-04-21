# RTDL Database Workloads (`v0.7.0` Release Line)

This tutorial covers the first bounded database-style workload family in RTDL's
`v0.7.0` release line.

Current bounded kernels:

- `conjunctive_scan`
- `grouped_count`
- `grouped_sum`

Current correctness anchors:

- Python truth path on every OS
- native oracle `run_cpu(...)` for the first bounded family
- PostgreSQL on Linux as the external correctness baseline
- real RT backends for the first bounded family:
  - `embree`
  - `optix`
  - `vulkan`
- native prepared DB datasets for repeated-query execution:
  - `prepare_embree_db_dataset`
  - `prepare_optix_db_dataset`
  - `prepare_vulkan_db_dataset`
- columnar prepared dataset transfer for Embree, OptiX, and Vulkan through
  `transfer="columnar"`

Important boundary:

- this is not a DBMS
- this is not SQL text execution
- this is a bounded analytical kernel family over denormalized records

## What Data Becomes What Data

| Workload | Input data | Output data |
| --- | --- | --- |
| `conjunctive_scan` | denormalized rows plus one or more predicates | matching `row_id` rows |
| `grouped_count` | denormalized rows, predicates, one group key | grouped count rows |
| `grouped_sum` | denormalized rows, predicates, one group key, one sum column | grouped sum rows |

The app does not write a DBMS or SQL executor. It provides bounded table-shaped
data and predicates; RTDL maps the search to backend traversal plus exact
refinement inside the release contract.

## 1. Conjunctive Scan

Run:

```bash
PYTHONPATH=src:. python examples/rtdl_db_conjunctive_scan.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/rtdl_db_conjunctive_scan.py --backend cpu
PYTHONPATH=src:. python examples/rtdl_db_conjunctive_scan.py --backend embree
```

On Linux GPU hosts with the backend libraries built:

```bash
PYTHONPATH=src:. python examples/rtdl_db_conjunctive_scan.py --backend optix
PYTHONPATH=src:. python examples/rtdl_db_conjunctive_scan.py --backend vulkan
```

What happens:

- a denormalized row set is the build input
- a bounded conjunction of predicates is the probe input
- RTDL emits matching `row_id` rows

## 2. Grouped Count

Run:

```bash
PYTHONPATH=src:. python examples/rtdl_db_grouped_count.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/rtdl_db_grouped_count.py --backend cpu
PYTHONPATH=src:. python examples/rtdl_db_grouped_count.py --backend embree
```

On Linux GPU hosts with the backend libraries built:

```bash
PYTHONPATH=src:. python examples/rtdl_db_grouped_count.py --backend optix
PYTHONPATH=src:. python examples/rtdl_db_grouped_count.py --backend vulkan
```

What happens:

- predicates filter the denormalized rows
- a single group key partitions the surviving rows
- RTDL emits grouped counts

## 3. Grouped Sum

Run:

```bash
PYTHONPATH=src:. python examples/rtdl_db_grouped_sum.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/rtdl_db_grouped_sum.py --backend cpu
PYTHONPATH=src:. python examples/rtdl_db_grouped_sum.py --backend embree
```

On Linux GPU hosts with the backend libraries built:

```bash
PYTHONPATH=src:. python examples/rtdl_db_grouped_sum.py --backend optix
PYTHONPATH=src:. python examples/rtdl_db_grouped_sum.py --backend vulkan
```

What happens:

- predicates filter the denormalized rows
- a single group key partitions the surviving rows
- RTDL emits grouped numeric sums

## 4. Unified DB App Demo

Run:

```bash
PYTHONPATH=src:. python examples/rtdl_database_analytics_app.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/rtdl_database_analytics_app.py --backend cpu
PYTHONPATH=src:. python examples/rtdl_database_analytics_app.py --backend embree
```

On Linux GPU hosts with the backend libraries built:

```bash
PYTHONPATH=src:. python examples/rtdl_database_analytics_app.py --backend optix
PYTHONPATH=src:. python examples/rtdl_database_analytics_app.py --backend vulkan
```

The unified app demo shows denormalized order tables becoming matched row IDs,
grouped counts, grouped sums, and app summaries. The retired scenario-specific
compatibility files still exist for historical tests, but the unified app is
the public tutorial entry point. The old kernel-form demo showed the
corresponding
`input -> traverse -> refine -> emit` structure for the same bounded DB surface.

## 5. PostgreSQL Correctness On Linux

If you are on the Linux validation host with PostgreSQL available:

```bash
RTDL_POSTGRESQL_DSN="dbname=postgres" PYTHONPATH=src:. python -m unittest \
  tests.goal420_v0_7_rt_db_conjunctive_scan_native_oracle_truth_path_test \
  tests.goal421_v0_7_rt_db_grouped_count_native_oracle_truth_path_test \
  tests.goal422_v0_7_rt_db_grouped_sum_native_oracle_truth_path_test \
  tests.goal423_v0_7_postgresql_db_correctness_test \
  tests.goal424_v0_7_postgresql_db_grouped_correctness_test -v
```

That is the current strongest bounded correctness gate for the first DB kernel
family.

## 6. Current Limits

The `v0.7.0` DB line is intentionally bounded. It does not yet include:

- multi-group-key native grouped kernels
- PostgreSQL-style storage, indexing, transactions, optimizer behavior, and
  arbitrary SQL

So the current correct claim is:

- RTDL now supports a first bounded analytical DB kernel family
- correctness is anchored against PostgreSQL on Linux
- the RT backend path for DB workloads is real across Embree, OptiX, and Vulkan
- native prepared dataset paths reuse Embree scenes, OptiX GAS/traversables, and
  Vulkan BLAS/TLAS state for repeated queries
- the prepared RT dataset APIs support columnar table ingestion on Embree,
  OptiX, and Vulkan
- the current Linux 200k-row Goal 452 comparison shows all three RT backends
  winning setup-plus-10-query total time against the best PostgreSQL modes
  tested so far, while query-only results are mixed
- Goal 492 records the final release-readiness hold before explicit `v0.7.0`
  release authorization
- `v0.7.0` is now the current tagged mainline release; claims remain bounded by
  the v0.7 release reports and support matrix
