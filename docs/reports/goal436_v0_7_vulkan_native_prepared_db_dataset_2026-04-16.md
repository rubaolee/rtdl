# Goal 436: v0.7 Vulkan Native Prepared DB Dataset

Date: 2026-04-16

## Verdict

Goal 436 is implemented and ready for external review.

The Vulkan DB backend now has a native prepared dataset handle that owns copied table values, encoded primary RT axes, row metadata, row AABBs, and built Vulkan BLAS/TLAS acceleration structures. Repeated DB queries launch against the prepared TLAS instead of rebuilding acceleration structures on every execution.

## Implemented Surface

- Native C ABI:
  - `rtdl_vulkan_db_dataset_create`
  - `rtdl_vulkan_db_dataset_destroy`
  - `rtdl_vulkan_db_dataset_conjunctive_scan`
  - `rtdl_vulkan_db_dataset_grouped_count`
  - `rtdl_vulkan_db_dataset_grouped_sum`
- Python public API:
  - `rt.prepare_vulkan_db_dataset(table_rows, primary_fields=...)`
  - `dataset.conjunctive_scan(predicates)`
  - `dataset.grouped_count(query)`
  - `dataset.grouped_sum(query)`
- Existing prepared kernel path:
  - `rt.prepare_vulkan(kernel).bind(...).run()` now uses the native prepared Vulkan DB dataset for the three v0.7 DB workloads.

## Correctness Evidence

Local macOS:

```text
python3 -m py_compile src/rtdsl/vulkan_runtime.py src/rtdsl/__init__.py tests/goal436_v0_7_vulkan_native_prepared_db_dataset_test.py scripts/goal436_vulkan_native_prepared_db_dataset_perf_gate.py
OK
```

Linux `lestat-lx1`:

```text
make build-vulkan
OK
```

```text
PYTHONPATH=src:. python3 -m unittest tests.goal436_v0_7_vulkan_native_prepared_db_dataset_test -v
Ran 4 tests in 0.704s
OK
```

The Linux tests verify:

- direct Vulkan DB results match Python truth
- prepared Vulkan DB results match Python truth
- repeated prepared execution is stable
- one public prepared Vulkan dataset can run scan, grouped_count, and grouped_sum query shapes

## Linux PostgreSQL Performance Gate

Command:

```text
RTDL_POSTGRESQL_DSN="dbname=postgres" PYTHONPATH=src:. python3 scripts/goal436_vulkan_native_prepared_db_dataset_perf_gate.py --row-count 200000 --repeats 10 --dsn "dbname=postgres"
```

Raw JSON:

```text
/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal436_vulkan_native_prepared_db_dataset_linux_2026-04-16.json
```

| Workload | Vulkan prepare once | Vulkan median query | Vulkan total 10 queries | PostgreSQL setup once | PostgreSQL median query | PostgreSQL total 10 queries |
|---|---:|---:|---:|---:|---:|---:|
| conjunctive_scan | 2.764802 s | 0.013603 s | 3.217003 s | 10.145430 s | 0.026498 s | 10.409818 s |
| grouped_count | 2.606685 s | 0.007032 s | 2.678680 s | 10.042244 s | 0.020443 s | 10.247574 s |
| grouped_sum | 2.463052 s | 0.013521 s | 2.600840 s | 12.660917 s | 0.035282 s | 13.014906 s |

## Interpretation

This closes the Vulkan prepared dataset version of the Goal 433 contract for the current bounded DB workload family. Compared with the earlier direct Vulkan DB path, repeated queries now reuse the built BLAS/TLAS and avoid per-query acceleration-structure rebuild.

The claim boundary remains explicit:

- This is a real Vulkan KHR ray-tracing traversal path over custom AABB primitives.
- It is not a full database system.
- PostgreSQL remains the mature database baseline.
- On this bounded synthetic gate, Vulkan wins both median query latency and fresh setup plus ten-query total for the measured workloads.
- The first Vulkan DB query in a process can include pipeline/runtime warm-up cost. The repeated-query table reports medians, so the one-time warm-up outlier is not treated as steady-state query latency.
- The initial Python-to-native table ingestion still uses the existing ctypes compatibility encoding path; this goal closes native Vulkan dataset reuse, not final columnar ingestion.

## Follow-Up

Goal 437 should consolidate the repeated-query performance gate across Embree, OptiX, Vulkan, and PostgreSQL. A later native transfer goal should replace compatibility ctypes row ingestion with a columnar or binary block input path before stronger large-table ingestion claims.
