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
- real RT backends for the first bounded family:
  - `embree`
  - `optix`
  - `vulkan`

Important boundary:

- this is not a DBMS
- this is not SQL text execution
- this is a bounded analytical kernel family over denormalized records

## 1. Conjunctive Scan

Run:

```bash
python3 examples/rtdl_db_conjunctive_scan.py --backend cpu_python_reference
python3 examples/rtdl_db_conjunctive_scan.py --backend cpu
python3 examples/rtdl_db_conjunctive_scan.py --backend embree
```

On Linux GPU hosts with the backend libraries built:

```bash
python3 examples/rtdl_db_conjunctive_scan.py --backend optix
python3 examples/rtdl_db_conjunctive_scan.py --backend vulkan
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
python3 examples/rtdl_db_grouped_count.py --backend embree
```

On Linux GPU hosts with the backend libraries built:

```bash
python3 examples/rtdl_db_grouped_count.py --backend optix
python3 examples/rtdl_db_grouped_count.py --backend vulkan
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
python3 examples/rtdl_db_grouped_sum.py --backend embree
```

On Linux GPU hosts with the backend libraries built:

```bash
python3 examples/rtdl_db_grouped_sum.py --backend optix
python3 examples/rtdl_db_grouped_sum.py --backend vulkan
```

What happens:

- predicates filter the denormalized rows
- a single group key partitions the surviving rows
- RTDL emits grouped numeric sums

## 4. App-Style DB Demo

Run:

```bash
python3 examples/rtdl_sales_risk_screening.py --backend cpu_python_reference
python3 examples/rtdl_sales_risk_screening.py --backend cpu
python3 examples/rtdl_sales_risk_screening.py --backend embree
```

On Linux GPU hosts with the backend libraries built:

```bash
python3 examples/rtdl_sales_risk_screening.py --backend optix
python3 examples/rtdl_sales_risk_screening.py --backend vulkan
```

## 5. PostgreSQL Correctness On Linux

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

## 6. What Is Still Missing

Not closed yet for the DB line:

- multi-group-key native grouped kernels
- final tag/release decision for the `v0.7` branch line

So the current correct claim is:

- RTDL now supports a first bounded analytical DB kernel family
- correctness is anchored against PostgreSQL on Linux
- the first RT backend path for DB workloads is real across Embree, OptiX, and Vulkan
- the current branch is still a bounded `v0.7` line, not the repository's last tagged mainline release
