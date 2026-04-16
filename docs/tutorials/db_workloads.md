# RTDL Database Workloads (`v0.7` Development Line)

This tutorial covers the first bounded database-style workload family in RTDL's
`v0.7` development line.

Current bounded kernels:

- `conjunctive_scan`
- `grouped_count`
- `grouped_sum`

Current correctness anchors:

- Python truth path on every OS
- native oracle `run_cpu(...)` for the first bounded family
- PostgreSQL on Linux as the external correctness baseline

Important boundary:

- this is not a DBMS
- this is not SQL text execution
- this is a bounded analytical kernel family over denormalized records

## 1. Conjunctive Scan

Run:

```bash
python3 examples/rtdl_db_conjunctive_scan.py --backend cpu_python_reference
python3 examples/rtdl_db_conjunctive_scan.py --backend cpu
```

What happens:

- a denormalized row set is the build input
- a bounded conjunction of predicates is the probe input
- RTDL emits matching `row_id` rows

## 2. Grouped Count

Run:

```bash
python3 examples/rtdl_db_grouped_count.py --backend cpu_python_reference
python3 examples/rtdl_db_grouped_count.py --backend cpu
```

What happens:

- predicates filter the denormalized rows
- a single group key partitions the surviving rows
- RTDL emits grouped counts

## 3. Grouped Sum

Run:

```bash
python3 examples/rtdl_db_grouped_sum.py --backend cpu_python_reference
python3 examples/rtdl_db_grouped_sum.py --backend cpu
```

What happens:

- predicates filter the denormalized rows
- a single group key partitions the surviving rows
- RTDL emits grouped numeric sums

## 4. PostgreSQL Correctness On Linux

If you are on the Linux validation host with PostgreSQL available:

```bash
RTDL_POSTGRESQL_DSN="dbname=postgres" python3 -m unittest \
  tests.goal420_v0_7_rt_db_conjunctive_scan_native_oracle_truth_path_test \
  tests.goal421_v0_7_rt_db_grouped_count_native_oracle_truth_path_test \
  tests.goal422_v0_7_rt_db_grouped_sum_native_oracle_truth_path_test \
  tests.goal423_v0_7_postgresql_db_correctness_test \
  tests.goal424_v0_7_postgresql_db_grouped_correctness_test -v
```

That is the current strongest bounded correctness gate for the first DB kernel
family.

## 5. What Is Still Missing

Not closed yet for the DB line:

- Embree / OptiX / Vulkan DB kernels
- multi-group-key native grouped kernels
- release-facing `v0.7` packaging

So the current correct claim is:

- RTDL now supports a first bounded analytical DB kernel family
- correctness is anchored against PostgreSQL on Linux
- the RT backend path for DB workloads is still future work
