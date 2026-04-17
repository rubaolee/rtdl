# Goal 435: v0.7 OptiX Native Prepared DB Dataset

Date: 2026-04-16

## Verdict

Goal 435 is implemented and ready for external review.

The OptiX DB backend now has a native prepared dataset handle that owns copied table values, encoded primary RT axes, row metadata, row AABBs, and a built OptiX custom-primitive GAS/traversable. Repeated DB queries launch against the prepared traversable instead of rebuilding the GAS on every execution.

## Implemented Surface

- Native C ABI:
  - `rtdl_optix_db_dataset_create`
  - `rtdl_optix_db_dataset_destroy`
  - `rtdl_optix_db_dataset_conjunctive_scan`
  - `rtdl_optix_db_dataset_grouped_count`
  - `rtdl_optix_db_dataset_grouped_sum`
- Python public API:
  - `rt.prepare_optix_db_dataset(table_rows, primary_fields=...)`
  - `dataset.conjunctive_scan(predicates)`
  - `dataset.grouped_count(query)`
  - `dataset.grouped_sum(query)`
- Existing prepared kernel path:
  - `rt.prepare_optix(kernel).bind(...).run()` now uses the native prepared OptiX DB dataset for the three v0.7 DB workloads.

## Correctness Evidence

Local macOS:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal435_v0_7_optix_native_prepared_db_dataset_test -v
OK (skipped=1)
```

Linux `lestat-lx1`:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal435_v0_7_optix_native_prepared_db_dataset_test -v
Ran 4 tests in 0.737s
OK
```

The Linux tests verify:

- direct OptiX DB results match Python truth
- prepared OptiX DB results match Python truth
- repeated prepared execution is stable
- one public prepared OptiX dataset can run scan, grouped_count, and grouped_sum query shapes

## Linux PostgreSQL Performance Gate

Command:

```text
RTDL_POSTGRESQL_DSN="dbname=postgres" PYTHONPATH=src:. python3 scripts/goal435_optix_native_prepared_db_dataset_perf_gate.py --row-count 200000 --repeats 10 --dsn "dbname=postgres"
```

Raw JSON:

```text
/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal435_optix_native_prepared_db_dataset_linux_2026-04-16.json
```

| Workload | OptiX prepare once | OptiX median query | OptiX total 10 queries | PostgreSQL setup once | PostgreSQL median query | PostgreSQL total 10 queries |
|---|---:|---:|---:|---:|---:|---:|
| conjunctive_scan | 2.693911 s | 0.011617 s | 3.239599 s | 10.121371 s | 0.026345 s | 10.384042 s |
| grouped_count | 2.548569 s | 0.004479 s | 2.594221 s | 10.440232 s | 0.020238 s | 10.643651 s |
| grouped_sum | 2.414290 s | 0.010184 s | 2.516861 s | 12.867585 s | 0.035046 s | 13.218746 s |

## Interpretation

This closes the OptiX prepared dataset version of the Goal 433 contract for the current bounded DB workload family. Compared with the earlier direct OptiX DB path, repeated queries now reuse the built GAS/traversable and avoid per-query acceleration-structure rebuild.

The claim boundary remains explicit:

- This is a real OptiX RT traversal path over custom AABB primitives.
- It is not a full database system.
- PostgreSQL remains the mature database baseline.
- On this bounded synthetic gate, OptiX wins both median query latency and fresh setup plus ten-query total for the measured workloads.
- The first OptiX DB query in a process can include NVRTC/OptiX pipeline JIT cost. The repeated-query table reports medians, so the one-time JIT outlier is not treated as steady-state query latency.
- The initial Python-to-native table ingestion still uses the existing ctypes compatibility encoding path; this goal closes native OptiX dataset reuse, not final columnar ingestion.

## Follow-Up

Goal 436 should apply the same prepared-dataset ownership model to Vulkan. A later native transfer goal should replace compatibility ctypes row ingestion with a columnar or binary block input path before stronger large-table ingestion claims.
