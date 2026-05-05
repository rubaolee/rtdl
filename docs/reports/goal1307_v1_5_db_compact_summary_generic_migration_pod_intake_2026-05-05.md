# Goal1307 Pod Intake: DB Compact Summary Generic Migration

Date: 2026-05-05

## Source

Goal1307 validates `database_analytics / sales_risk_compact_summary` on the RTX
pod after routing the sales-risk compact-summary path through
`run_generic_db_compact_summary_batch()`.

Pod workspace:

```text
/workspace/rtdl_goal1292
```

The pod checkout was older than local `main`, so the Goal1307 source slice was
copied into the pod workspace before running tests.

## Evidence

Compact copied artifact:

```text
docs/reports/goal1307_v1_5_db_compact_summary_generic_migration_pod_results/compact_summary.json
```

Command shape:

```text
PYTHONPATH=src:. python3 examples/rtdl_database_analytics_app.py \
  --backend optix \
  --scenario sales_risk \
  --copies 256 \
  --output-mode compact_summary \
  --execution-mode prepared_session \
  --require-rt-core
```

Result:

| Field | Value |
| --- | --- |
| App | `database_analytics` |
| Scenario | `sales_risk` |
| Backend | `optix` |
| Copies | 256 |
| Native continuation | `optix_db_compact_summary` |
| RT-core gate | `rt_core_accelerated=true` |
| Generic primitive | `DB_COMPACT_SUMMARY` |
| Summary primitives | `COUNT_HITS`, `REDUCE_INT(COUNT)`, `REDUCE_INT(SUM)` |
| Result layout | `aggregate_scan_count_and_grouped_integer_maps` |
| Row materialization | avoided for compact summary |

Sales-risk output:

```text
risky_order_count = 1024
risky_order_count_by_region = central:256, east:256, west:512
risky_revenue_by_region = central:66560, east:79360, west:110080
highest_risk_region = west
```

## Status

`database_analytics / sales_risk_compact_summary` is now pod-verified as a
generic v1.5 compact-summary row.

This is still an exact subpath claim only. It does not claim SQL, DBMS behavior,
query planning, joins, transactions, indexes as a database feature, row-output
paths, broad database acceleration, or public NVIDIA speedup wording.

## Pod Tests

Passed on pod:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1307_v1_5_db_compact_summary_generic_migration_test \
  tests.goal954_database_native_continuation_contract_test \
  tests.goal851_optix_db_sales_grouped_summary_fastpath_test \
  tests.goal1128_embree_db_compact_summary_contract_test \
  tests.goal1304_v1_5_generic_migration_inventory_test
```

Result: 17 tests OK.
