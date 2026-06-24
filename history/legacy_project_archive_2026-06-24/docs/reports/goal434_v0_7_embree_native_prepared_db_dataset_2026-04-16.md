# Goal 434: v0.7 Embree Native Prepared DB Dataset

Date: 2026-04-16

## Verdict

Goal 434 is implemented and ready for external review.

The Embree DB backend now has a native prepared dataset handle that owns the copied table values, encoded primary RT axes, row boxes, Embree device, and committed Embree user-primitive scene. Repeated DB queries use the committed scene instead of rebuilding Embree geometry on every execution.

## Implemented Surface

- Native C ABI:
  - `rtdl_embree_db_dataset_create`
  - `rtdl_embree_db_dataset_destroy`
  - `rtdl_embree_db_dataset_conjunctive_scan`
  - `rtdl_embree_db_dataset_grouped_count`
  - `rtdl_embree_db_dataset_grouped_sum`
- Python public API:
  - `rt.prepare_embree_db_dataset(table_rows, primary_fields=...)`
  - `dataset.conjunctive_scan(predicates)`
  - `dataset.grouped_count(query)`
  - `dataset.grouped_sum(query)`
- Existing prepared kernel path:
  - `rt.prepare_embree(kernel).bind(...).run()` now uses the native prepared DB dataset for the three v0.7 DB workloads.

## Correctness Evidence

Local macOS:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal434_v0_7_embree_native_prepared_db_dataset_test -v
Ran 4 tests in 0.114s
OK
```

Linux `lestat-lx1`:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal434_v0_7_embree_native_prepared_db_dataset_test -v
Ran 4 tests in 0.182s
OK
```

The tests verify:

- direct Embree DB results match Python truth
- prepared Embree DB results match Python truth
- repeated prepared execution is stable
- one public prepared dataset can run scan, grouped_count, and grouped_sum query shapes

## Linux PostgreSQL Performance Gate

Command:

```text
RTDL_POSTGRESQL_DSN="dbname=postgres" PYTHONPATH=src:. python3 scripts/goal434_embree_native_prepared_db_dataset_perf_gate.py --row-count 200000 --repeats 10 --dsn "dbname=postgres"
```

Raw JSON:

```text
/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal434_embree_native_prepared_db_dataset_linux_2026-04-16.json
```

| Workload | Embree prepare once | Embree median query | Embree total 10 queries | PostgreSQL setup once | PostgreSQL median query | PostgreSQL total 10 queries |
|---|---:|---:|---:|---:|---:|---:|
| conjunctive_scan | 2.927411 s | 0.018753 s | 3.113833 s | 12.259940 s | 0.029153 s | 12.549844 s |
| grouped_count | 2.914072 s | 0.015879 s | 3.073149 s | 12.352186 s | 0.022302 s | 12.575946 s |
| grouped_sum | 2.774800 s | 0.035328 s | 3.127755 s | 10.601887 s | 0.038366 s | 10.986007 s |

## Interpretation

This is a real improvement over Goal 432 for Embree: the repeated query phase now reuses the native Embree scene and drops from per-query scene rebuild behavior to low query latency after one prepared dataset build.

The claim boundary remains explicit:

- This is a real Embree RT traversal path using user primitives and ray traversal over prepared row boxes.
- It is not a full database system.
- PostgreSQL query-only latency remains competitive and should still be treated as the mature database baseline.
- Embree wins the measured fresh setup plus ten-query total in this bounded synthetic gate because PostgreSQL table/index setup is much heavier.
- The initial Python-to-native table ingestion still uses the existing ctypes compatibility encoding path. Goal 434 removes per-query scene rebuild, but it does not yet replace ingestion with a final columnar/buffer-protocol transfer path.

## Follow-Up

Goals 435 and 436 should apply the same prepared-dataset ownership model to OptiX and Vulkan. A later native transfer goal should replace the compatibility ctypes row ingestion with a columnar or binary block input path before making stronger large-table performance claims.
