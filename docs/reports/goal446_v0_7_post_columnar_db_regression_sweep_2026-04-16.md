# Goal 446: v0.7 Post-Columnar DB Regression Sweep

Date: 2026-04-16

## Verdict

Goal 446 is implemented and ready for external review.

This goal records a focused post-columnar regression sweep after Goals 440-445.
It does not change release or tag status.

## Linux Validation Host

Host:

```text
lestat-lx1
```

PostgreSQL readiness:

```text
/var/run/postgresql:5432 - accepting connections
```

## Command

```text
cd /home/lestat/tmp/rtdl_v0_7_db_vulkan_check
pg_isready
PYTHONPATH=src:. python3 -m py_compile \
  src/rtdsl/embree_runtime.py \
  src/rtdsl/optix_runtime.py \
  src/rtdsl/vulkan_runtime.py \
  src/rtdsl/db_perf.py
RTDL_POSTGRESQL_DSN=dbname=postgres PYTHONPATH=src:. python3 -m unittest \
  tests.goal420_v0_7_rt_db_conjunctive_scan_native_oracle_truth_path_test \
  tests.goal421_v0_7_rt_db_grouped_count_native_oracle_truth_path_test \
  tests.goal422_v0_7_rt_db_grouped_sum_native_oracle_truth_path_test \
  tests.goal423_v0_7_postgresql_db_correctness_test \
  tests.goal424_v0_7_postgresql_db_grouped_correctness_test \
  tests.goal432_v0_7_rt_db_phase_split_perf_test \
  tests.goal434_v0_7_embree_native_prepared_db_dataset_test \
  tests.goal435_v0_7_optix_native_prepared_db_dataset_test \
  tests.goal436_v0_7_vulkan_native_prepared_db_dataset_test \
  tests.goal440_v0_7_embree_columnar_prepared_db_dataset_transfer_test \
  tests.goal441_v0_7_optix_columnar_prepared_db_dataset_transfer_test \
  tests.goal442_v0_7_vulkan_columnar_prepared_db_dataset_transfer_test \
  tests.goal445_v0_7_high_level_prepared_db_columnar_default_test -v
```

Raw log:

```text
/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal446_post_columnar_db_regression_linux_2026-04-16.log
```

## Result

```text
Ran 46 tests in 1.990s
OK
```

No skips were reported on Linux for this focused suite.

## Coverage

The sweep covers:

- native/oracle DB correctness for:
  - `conjunctive_scan`
  - `grouped_count`
  - `grouped_sum`
- live PostgreSQL correctness gates for scan and grouped workloads
- phase-split performance helper unit coverage
- native prepared dataset reuse for:
  - Embree
  - OptiX
  - Vulkan
- row/columnar prepared dataset transfer parity for:
  - Embree
  - OptiX
  - Vulkan
- high-level prepared-kernel DB path uses `transfer="columnar"` for:
  - Embree
  - OptiX
  - Vulkan
- direct prepared dataset row-transfer default remains compatible

## Boundary

This is a focused DB regression sweep, not a full repository release test. It
does not change release status. It supports the v0.7 DB-columnar line after the
runtime and documentation updates.
