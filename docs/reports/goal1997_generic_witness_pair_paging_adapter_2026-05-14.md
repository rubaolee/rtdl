# Goal1997 Generic Witness-Pair Paging Adapter

Date: 2026-05-14

Status: implementation slice

## Why This Goal Exists

The row-output debt has two layers. Goal1996 added generic partner column paging,
but segment/shape witness rows still lacked a public adapter that exposes generic
native witness pairs as bounded partner-owned pages before Python row naming.

Goal1997 adds that public adapter.

## What Changed

The partner adapter now exposes:

```text
ray_primitive_witness_pair_page_optix_prepared_partner_columns(...)
```

It runs a prepared OptiX generic ray/primitive all-witness scene, slices the
emitted witness columns to the actual emitted count, and returns a bounded page
of:

```text
witness_ray_ids
witness_primitive_ids
```

The metadata explicitly records:

```text
native_engine_row_contract = generic_ray_primitive_witness_pairs
app_row_materialization = not_performed_generic_witness_page_only
```

## Boundary

This does not add polygon, segment, robot, GIS, or graph semantics to the native
engine. It exposes a generic witness-pair page. Applications may later name those
IDs as segment/polygon rows, robot edge rows, or some other app view outside the
engine.

This is not by itself a performance claim. It is an API primitive needed before
row-producing v2 apps can avoid all-row host serialization.

## Validation

Local validation passed:

```text
py -3 -m unittest tests.goal1997_generic_witness_pair_paging_adapter_test \
  tests.goal1996_partner_column_paging_primitive_test
```
