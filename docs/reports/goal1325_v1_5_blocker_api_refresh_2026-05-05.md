# Goal1325: v1.5 Blocker API Refresh

Date: 2026-05-05

## Scope

Refresh the internal `v1_5_generic_migration_blockers()` helper after Goal1322
and Goal1323 so it no longer reports completed primitive migrations as current
blockers.

## Decision

The v1.5 inventory rows are now internally pod-verified generic for the
supported subpaths. Therefore these are no longer blocker statements:

- prepared pose flags needing grouped count-to-boolean reduction
- database compact summaries needing grouped integer count/sum wrappers
- polygon exact area and Jaccard scoring needing reviewed float-sum contracts

The remaining blockers are now claim and scope boundaries:

- app-level continuations named in `remaining_app_specific_work`
- whole-app speedup wording for graph, DB, polygon, ranking, clustering,
  SQL-style materialization, exact-distance rows, and force-vector reductions
- public NVIDIA wording until exact-subpath evidence receives 3-AI consensus

## Validation

Targeted local gate:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1228_v1_0_positioning_docs_test \
  tests.goal1304_v1_5_generic_migration_inventory_test

Ran 7 tests in 0.004s
OK
```
