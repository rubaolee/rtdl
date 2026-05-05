# Goal1307: DB Compact Summary Generic Migration

Date: 2026-05-05

## Purpose

Goal1307 starts migrating `database_analytics / sales_risk_compact_summary`
from app-owned compact-summary calls to a generic v1.5 DB compact-summary
wrapper.

This is a local source migration. Pod evidence is still required before the
inventory row can be promoted to `pod_verified_generic`.

## Contract

The generic wrapper represents the materialization-free compact summary as:

```text
primitive = DB_COMPACT_SUMMARY
summary primitives = COUNT_HITS, REDUCE_INT(COUNT), REDUCE_INT(SUM)
result layout = aggregate_scan_count_and_grouped_integer_maps
```

This remains a bounded DB primitive over an application-owned denormalized
table. It is not SQL, DBMS behavior, joins, transactions, indexes as a database
feature, query planning, row output, or public speedup wording.

## Implementation

Added:

```text
run_generic_db_compact_summary_batch()
```

`PreparedSalesRiskSession.run(output_mode="compact_summary")` now calls the
generic wrapper when the prepared dataset exposes `compact_summary_batch`. The
wrapper keeps explicit primitive metadata and returns the native phase timings
without materializing grouped rows.

## Status

`database_analytics / sales_risk_compact_summary` was promoted to
`pod_verified_generic` after the OptiX pod intake. Broader DB scenarios and
row-output paths remain outside scope.

## Verification

Planned local gate:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1307_v1_5_db_compact_summary_generic_migration_test \
  tests.goal954_database_native_continuation_contract_test \
  tests.goal851_optix_db_sales_grouped_summary_fastpath_test \
  tests.goal1128_embree_db_compact_summary_contract_test
```
