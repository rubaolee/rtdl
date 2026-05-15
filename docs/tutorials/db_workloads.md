# RTDL Database Workloads

This tutorial covers the current v2.0-facing database-style workload shape:
bounded columnar-payload scans and grouped numeric summaries inside a Python
program.

Current bounded workload contracts:

- `conjunctive_scan`
- `grouped_count`
- `grouped_sum`

Current correctness anchors:

- Python truth path on every OS
- native oracle `run_cpu(...)` for the bounded family
- PostgreSQL on Linux as the external correctness baseline
- real RT backends for the bounded family where configured:
  - `embree`
  - `optix`
  - `vulkan`
- native prepared datasets for repeated-query execution:
  - `prepare_embree_db_dataset`
  - `prepare_optix_db_dataset`
  - `prepare_vulkan_db_dataset`
- columnar-payload transfer and partner continuation where documented

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

For a claim-sensitive NVIDIA RT-core run, use the compact OptiX summary mode:

```bash
PYTHONPATH=src:. python examples/rtdl_database_analytics_app.py --backend optix --output-mode compact_summary --require-rt-core
```

`--require-rt-core` rejects the unified DB app's full and default summary modes
because those modes can be interface/materialization dominated. The accepted
claim is the bounded compact-summary traversal path only; it is not a DBMS or a
general SQL acceleration claim.

The unified app demo shows denormalized order tables becoming matched row IDs,
grouped counts, grouped sums, and app summaries. The retired scenario-specific
compatibility files still exist for historical tests, but the unified app is
the public tutorial entry point. The old kernel-form demo showed the
corresponding
`input -> traverse -> refine -> emit` structure for the same bounded DB surface.

## 5. PostgreSQL Correctness On Linux

Historical PostgreSQL comparison tests still exist in the regression suite. If
you are doing release archaeology, use the history and report archives rather
than treating those old goal-named tests as the learner path.

```bash
PYTHONPATH=src:. python examples/rtdl_database_analytics_app.py --backend cpu_python_reference
```

For current v2.0 learning, the unified example above is the public entry point.

## 6. Current Limits

The DB-style surface is intentionally bounded. It does not include:

- multi-group-key native grouped kernels
- PostgreSQL-style storage, indexing, transactions, optimizer behavior, and
  arbitrary SQL

So the current correct claim is:

- RTDL supports bounded analytical DB-style kernels
- historical external correctness anchors live in the report archive
- the RT backend path for DB workloads is real across Embree, OptiX, and Vulkan
- native prepared dataset paths reuse Embree scenes, OptiX GAS/traversables, and
  Vulkan BLAS/TLAS state for repeated queries
- the prepared RT dataset APIs support columnar-payload ingestion on Embree,
  OptiX, and Vulkan where configured
- this is not a SQL engine, DBMS, optimizer, or broad database speedup claim
